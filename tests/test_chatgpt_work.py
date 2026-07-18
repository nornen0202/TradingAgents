from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tradingagents.work import packet as work_packet
from tradingagents.work.handoff import WORK_HANDOFF_SCHEMA, dispatch_pages_handoff
from tradingagents.work.packet import WORK_REPORT_SCHEMA, WORK_SCHEMA, build_surface_packet
from tradingagents.work.runtime import WorkRuntime, WorkRuntimeError, validate_packet
from tradingagents.work.site import _fit_packet_budget, build_work_site


def _write_market_run(
    archive: Path,
    *,
    run_id: str,
    market: str,
    started_at: str,
    row_mode: str = "BLOCKED_STALE",
) -> Path:
    run_dir = archive / "runs" / "2026" / run_id
    run_dir.mkdir(parents=True)
    ready = row_mode == "IMMEDIATE"
    conditional = row_mode in {"IMMEDIATE", "CONDITIONAL"}
    manifest = {
        "run_id": run_id,
        "started_at": started_at,
        "settings": {"market": market.upper(), "run_mode": "overlay_only"},
        "decision_bundle": {
            "decision_ready": ready,
            "conditional_strategy_ready": conditional,
            "artifacts": {"decision_bundle_v2_json": "decision_bundle_v2.json"},
        },
    }
    bundle = {
        "artifact_type": "decision_bundle",
        "version": 2,
        "run_id": run_id,
        "market": market.upper(),
        "generated_at": started_at,
        "quality": {
            "decision_ready": ready,
            "conditional_strategy_ready": conditional,
            "report_mode": "READY" if ready else "CONDITIONAL" if conditional else "OUTAGE",
            "fresh_row_ratio": 1.0 if ready else 0.0,
            "conditional_row_ratio": 1.0 if conditional else 0.0,
        },
        "summary": {"ticker_count": 1},
        "strategy_table": [
            {
                "ticker": "005930.KS" if market.lower() == "kr" else "NVDA",
                "is_held": True,
                "strategy_code": "HOLD" if conditional else "DATA_CHECK",
                "strategy_ko": "보유 유지" if conditional else "데이터 확인 전 대기",
                "market_data_asof": started_at,
                "last_price": 100,
                "session_vwap": 99,
                "relative_volume": 1.1,
                "data_status_ko": "테스트",
                "quality": {
                    "row_mode": row_mode,
                    "execution_ready": ready,
                    "conditional_strategy_ready": conditional,
                    "generated_in_current_run": row_mode != "BLOCKED_STALE",
                    "current_execution_promotion": "POSSIBLE" if ready else "BLOCKED" if row_mode == "BLOCKED_STALE" else "RECHECK_REQUIRED",
                },
            }
        ],
        "benchmark_context": {},
    }
    (run_dir / "run.json").write_text(json.dumps(manifest), encoding="utf-8")
    (run_dir / "decision_bundle_v2.json").write_text(json.dumps(bundle), encoding="utf-8")
    return run_dir


def _write_universe_contract(
    run_dir: Path,
    *,
    expected_holdings: list[str],
    missing_holdings: list[str],
    expected_watchlist: list[str],
    missing_watchlist: list[str],
    failed_tickers: list[str],
) -> None:
    manifest_path = run_dir / "run.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    selected = [
        ticker
        for ticker in dict.fromkeys([*expected_holdings, *expected_watchlist])
        if ticker not in {*missing_holdings, *missing_watchlist}
    ]
    failed = set(failed_tickers)
    selection_complete = not missing_holdings and not missing_watchlist
    analysis_complete = not (failed & set(selected))
    manifest["active_universe"] = {
        "ticker_universe_mode": "config_plus_account",
        "account_snapshot_status": "loaded",
        "account_holding_count": len(expected_holdings),
        "expected_holding_tickers": expected_holdings,
        "missing_holding_tickers": missing_holdings,
        "expected_watchlist_tickers": expected_watchlist,
        "missing_watchlist_tickers": missing_watchlist,
        "missing_analysis_tickers": [],
        "coverage": {
            "complete": selection_complete and analysis_complete,
            "selection_complete": selection_complete,
            "analysis_complete": analysis_complete,
            "analysis_expected_count": len(selected),
            "analysis_successful_count": len(selected) - len(failed & set(selected)),
            "analysis_failed_count": len(failed & set(selected)),
            "analysis_missing_count": 0,
            "holding_expected_count": len(expected_holdings),
            "holding_selected_count": len(expected_holdings) - len(missing_holdings),
            "holding_missing_count": len(missing_holdings),
            "watchlist_expected_count": len(expected_watchlist),
            "watchlist_selected_count": len(expected_watchlist) - len(missing_watchlist),
            "watchlist_missing_count": len(missing_watchlist),
        },
    }
    manifest["tickers"] = [
        {"ticker": ticker, "status": "failed" if ticker in failed else "success"}
        for ticker in selected
    ]
    manifest["summary"] = {
        "total_tickers": len(selected),
        "successful_tickers": len(selected) - len(failed & set(selected)),
        "failed_tickers": len(failed & set(selected)),
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")


def _write_youtube_market_evidence(
    archive: Path,
    *,
    video_id: str,
    ticker: str,
    published_at: str = "2026-07-14T13:30:00+00:00",
) -> None:
    run_dir = archive / "runs" / "2026" / "youtube-market-evidence"
    video_dir = run_dir / "videos" / video_id
    video_dir.mkdir(parents=True)
    (run_dir / "youtube_run.json").write_text(
        json.dumps(
            {
                "run_id": "youtube-market-evidence",
                "started_at": "2026-07-14T13:45:00+00:00",
                "finished_at": "2026-07-14T13:50:00+00:00",
                "status": "success",
                "videos": [
                    {
                        "video_id": video_id,
                        "published_at": published_at,
                        "public_summary_path": f"videos/{video_id}/public_summary.json",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (video_dir / "public_summary.json").write_text(
        json.dumps(
            {
                "video_id": video_id,
                "title": f"Evidence for {ticker}",
                "published_at": published_at,
                "entities": [{"ticker": ticker, "status": "verified"}],
            }
        ),
        encoding="utf-8",
    )


def _structured_report(prepared: dict, *, ticker_override: list[str] | None = None) -> dict:
    packet = json.loads(Path(prepared["packet_path"]).read_text(encoding="utf-8"))
    packet_rows = packet.get("body", {}).get("current", {}).get("bundle", {}).get("strategy_table", [])
    supporting_context = packet.get("body", {}).get("supporting_context", {})
    tickers = ticker_override if ticker_override is not None else [row["ticker"] for row in packet_rows]
    by_ticker = {str(row.get("ticker")): row for row in packet_rows}
    strategies = []
    for index, ticker in enumerate(tickers, start=1):
        row = by_ticker.get(ticker, {})
        thesis = row.get("thesis") if isinstance(row.get("thesis"), dict) else {}
        execution = row.get("execution") if isinstance(row.get("execution"), dict) else {}
        stance = thesis.get("stance") or "RESEARCH"
        entry_conditions = thesis.get("entry_conditions") or []
        invalidation_conditions = thesis.get("invalidation_conditions") or []
        if stance in {"BUY", "HOLD", "REDUCE", "SELL", "AVOID"}:
            entry_conditions = entry_conditions or [
                "종가가 세션 VWAP를 상회하고 거래량 증가가 확인될 때"
            ]
            invalidation_conditions = invalidation_conditions or [
                "종가가 세션 VWAP를 하회하거나 위험 한도를 초과할 때"
            ]
        strategy = {
                "ticker": ticker,
                "display_name": row.get("display_name"),
                "rank": index,
                "portfolio_role": "holding" if row.get("is_held") else "watchlist",
                "thesis": {
                    "stance": stance,
                    "horizon": "daily",
                    "confidence": thesis.get("confidence") if isinstance(thesis.get("confidence"), (int, float)) else 0.5,
                    "rationale": thesis.get("rationale") or ["test thesis"],
                    "entry_conditions": entry_conditions,
                    "invalidation_conditions": invalidation_conditions,
                    "invalidation_action": "기존 비중을 절반 축소하고 다음 정규장에서 재평가",
                    "position_sizing": "existing risk limits",
                    "research_priority": "MEDIUM",
                },
                "execution": {
                    "readiness": execution.get("readiness") or "NEEDS_LIVE_RECHECK",
                    "as_of": execution.get("as_of"),
                    "valid_until": execution.get("valid_until"),
                    "action_now": execution.get("action_now"),
                    "action_if_triggered": execution.get("action_if_triggered"),
                    "required_rechecks": execution.get("required_rechecks") or [],
                    "blockers": execution.get("blockers") or [],
                },
                "source_contributions": [
                    {
                        "source": "tradingagents",
                        "direction": "MAINTAIN",
                        "reason": "prepared packet",
                        "execution_gate_override": False,
                    }
                ],
            }
        if stance == "RESEARCH" and (not entry_conditions or not invalidation_conditions):
            strategy["thesis"]["data_needed_reason"] = (
                "실시간 가격과 거래량 데이터가 없어 실행 조건을 확정할 수 없음"
            )
        strategies.append(strategy)
    healthy_matches: dict[str, list[tuple[str, str]]] = {}
    for source in ("youtube", "prism"):
        source_context = supporting_context.get(source, {})
        if str(source_context.get("source_health") or "").upper() != "OK":
            continue
        for event in source_context.get("events") or []:
            event_key = str(event.get("event_key") or "")
            for matched_ticker in (event.get("relevance") or {}).get("matched_tickers") or []:
                identity = str(matched_ticker).upper().removesuffix(".KS").removesuffix(".KQ")
                healthy_matches.setdefault(identity, []).append((source, event_key))
    for strategy in strategies:
        identity = str(strategy["ticker"]).upper().removesuffix(".KS").removesuffix(".KQ")
        matches = healthy_matches.get(identity) or []
        if matches:
            source, event_key = matches[0]
            strategy["source_contributions"].append(
                {
                    "source": source,
                    "event_key": event_key,
                    "affected_field": "confidence",
                    "direction": "MAINTAIN",
                    "reason": "matched external evidence reviewed",
                    "execution_gate_override": False,
                }
            )
        elif healthy_matches:
            strategy["no_relevant_evidence_reason"] = (
                "No transmitted healthy external event matched this ticker."
            )
    return {
        "binding": {
            "surface": prepared["surface"],
            "event_id": prepared["event_id"],
            "source_sha256": prepared["source_sha256"],
        },
        "title": "테스트 통합 투자 전략",
        "generated_at": "2026-07-14T14:06:00+00:00",
        "as_of": "2026-07-14T14:05:00+00:00",
        "source_health": packet.get("body", {}).get("source_health"),
        "report_mode": packet.get("body", {}).get("report_mode"),
        "summary": "분석 시점 전략과 실행 준비도를 분리한다.",
        "top_actions": [],
        "strategies": strategies,
        "coverage_receipt": packet.get("body", {}).get("current", {}).get("universe_coverage", {}),
        "model_receipt": packet.get("body", {}).get("model_provenance", {}),
        "source_summary": {
            "policy": "balanced_external",
            "external_evidence_receipt": supporting_context.get("receipt_contract"),
        },
        "next_checkpoint": "다음 시장 데이터 갱신 시점",
    }


def _publish_market(runtime: WorkRuntime, prepared: dict, *, archive: Path) -> dict:
    packet = json.loads(Path(prepared["packet_path"]).read_text(encoding="utf-8"))
    rows = packet.get("body", {}).get("current", {}).get("bundle", {}).get("strategy_table", [])
    market_asof = datetime.fromisoformat(str(rows[0]["market_data_asof"]).replace("Z", "+00:00"))
    return runtime.publish(
        prepared["surface"],
        prepared["event_id"],
        prepared["source_sha256"],
        report_markdown="# 테스트 전략\n\n분석 시점 thesis를 유지하고 주문 전 실시간 데이터를 확인합니다.",
        structured_report=_structured_report(prepared),
        archive_dir=archive,
        now=market_asof + timedelta(minutes=6),
    )


def test_non_ready_latest_market_run_still_builds_work_event(tmp_path: Path):
    archive = tmp_path / "archive"
    _write_market_run(
        archive,
        run_id="latest-outage-kr",
        market="kr",
        started_at="2026-07-14T13:56:00+09:00",
    )

    packet = build_surface_packet(
        "kr",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 14, 0, tzinfo=timezone.utc),
        public=False,
    )

    assert packet["schema"] == WORK_SCHEMA
    assert packet["body"]["current"]["run_id"] == "latest-outage-kr"
    assert packet["body"]["report_mode"] == "OUTAGE"
    assert packet["body"]["current"]["bundle"]["strategy_table"][0]["quality"]["row_mode"] == "BLOCKED_STALE"


def test_prompt_revision_changes_work_event_id(monkeypatch):
    body = {"kind": "youtube", "source_health": "OK", "execution_eligible": False, "events": []}
    hashes = {
        "prompt_sha256": "1" * 64,
        "skill_sha256": "2" * 64,
        "task_manifest_sha256": "3" * 64,
    }
    monkeypatch.setattr(work_packet, "workflow_contract_hashes", lambda _surface: hashes)
    first = work_packet._seal_packet("youtube", body=body)
    hashes = {**hashes, "prompt_sha256": "4" * 64}
    monkeypatch.setattr(work_packet, "workflow_contract_hashes", lambda _surface: hashes)
    second = work_packet._seal_packet("youtube", body=body)

    assert first["source_sha256"] == second["source_sha256"]
    assert first["prompt_sha256"] != second["prompt_sha256"]
    assert first["event_id"] != second["event_id"]
    # A packet prepared under the prior embedded contract remains verifiable
    # after the live prompt/skill/task files rotate.
    validate_packet(first)


def test_market_packet_distinguishes_runtime_observed_analysis_from_configured_work_model(
    tmp_path: Path,
):
    archive = tmp_path / "archive"
    run_dir = _write_market_run(
        archive,
        run_id="model-receipt-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="IMMEDIATE",
    )
    manifest_path = run_dir / "run.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["settings"].update(
        {
            "provider": "codex",
            "quick_model": "gpt-5.6-terra",
            "deep_model": "gpt-5.6-sol",
            "output_model": "gpt-5.6-luna",
            "codex_deep_reasoning_effort": "medium",
        }
    )
    manifest["llm_usage"] = {
        "available": True,
        "calls": 9,
        "by_model": {
            "gpt-5.6-sol": {
                "calls": 4,
                "input_tokens": 1200,
                "output_tokens": 300,
                "total_tokens": 1500,
            }
        },
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    packet = build_surface_packet(
        "us",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc),
        public=False,
    )
    provenance = packet["body"]["model_provenance"]

    assert provenance["market_analysis"]["verification_status"] == "RUNTIME_USAGE_OBSERVED"
    assert provenance["market_analysis"]["observed_calls"] == 9
    assert "gpt-5.6-sol" in provenance["market_analysis"]["observed_models"]
    assert provenance["work_synthesis"]["requested_model"] == "gpt-5.6-sol"
    assert provenance["work_synthesis"]["verification_status"] == "CONFIGURED_NOT_RUNTIME_VERIFIED"
    assert provenance["work_synthesis"]["observed_model"] is None


def test_packet_integrity_rejects_body_tampering_without_reseal():
    packet = work_packet._seal_packet(
        "youtube",
        body={
            "kind": "youtube",
            "source_health": "OK",
            "execution_eligible": False,
            "events": [],
        },
    )
    packet["body"]["events"].append({"event_key": "tampered"})

    with pytest.raises(WorkRuntimeError, match="source SHA-256 does not match its body"):
        validate_packet(packet)


def test_missing_manifest_status_is_unverified_not_ok(tmp_path: Path):
    archive = tmp_path / "archive"
    _write_market_run(
        archive,
        run_id="status-unknown-kr",
        market="kr",
        started_at="2026-07-14T10:00:00+09:00",
        row_mode="IMMEDIATE",
    )

    packet = build_surface_packet(
        "kr",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 1, 5, tzinfo=timezone.utc),
        public=False,
    )

    assert packet["body"]["source_health"] == "UNVERIFIED"
    assert packet["body"]["guardrails"]["decision_ready"] is True
    assert packet["body"]["guardrails"]["report_mode"] == "READY"


def test_compact_market_packet_keeps_all_required_watchlist_and_limits_only_discovery():
    watchlist = [f"WATCH{i}" for i in range(8)]
    discovery = [f"SCAN{i}" for i in range(12)]
    rows = [
        {"ticker": "HELD", "is_held": True, "quality": {}},
        *({"ticker": ticker, "is_held": False, "quality": {}} for ticker in watchlist),
        *({"ticker": ticker, "is_held": False, "quality": {}} for ticker in discovery),
    ]

    compact = work_packet.compact_decision_bundle(
        {"strategy_table": rows, "benchmark_context": {}},
        required_watchlist_tickers=watchlist,
    )

    transmitted = [row["ticker"] for row in compact["strategy_table"]]
    scope = compact["transmission_scope"]
    assert transmitted == ["HELD", *watchlist, *discovery[:10]]
    assert scope["all_holdings_included"] is True
    assert scope["all_required_watchlist_included"] is True
    assert scope["required_watchlist_ticker_count"] == len(watchlist)
    assert scope["transmitted_required_watchlist_count"] == len(watchlist)
    assert scope["scanner_candidate_limit"] == 10
    assert scope["omitted_nonheld_ticker_count"] == 2


def test_public_market_packet_omits_portfolio_membership(tmp_path: Path):
    archive = tmp_path / "archive"
    _write_market_run(
        archive,
        run_id="private-held-kr",
        market="kr",
        started_at="2026-07-14T10:00:00+09:00",
        row_mode="IMMEDIATE",
    )

    packet = build_surface_packet(
        "kr",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 1, 5, tzinfo=timezone.utc),
        public=True,
    )

    bundle = packet["body"]["current"]["bundle"]
    assert bundle["strategy_table"] == []
    assert bundle["transmission_scope"]["portfolio_membership_omitted"] is True
    serialized = json.dumps(packet, ensure_ascii=False)
    assert "is_held" not in serialized
    assert "held_ticker_count" not in serialized


def test_public_market_packet_keeps_allowlisted_research_row_without_membership(tmp_path: Path):
    archive = tmp_path / "archive"
    run_dir = _write_market_run(
        archive,
        run_id="allowlisted-held-kr",
        market="kr",
        started_at="2026-07-14T10:00:00+09:00",
        row_mode="IMMEDIATE",
    )
    _write_universe_contract(
        run_dir,
        expected_holdings=["005930.KS"],
        missing_holdings=[],
        expected_watchlist=["005930"],
        missing_watchlist=[],
        failed_tickers=[],
    )

    packet = build_surface_packet(
        "kr",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 1, 5, tzinfo=timezone.utc),
        public=True,
    )

    rows = packet["body"]["current"]["bundle"]["strategy_table"]
    serialized = json.dumps(packet, ensure_ascii=False)
    assert [row["ticker"] for row in rows] == ["005930.KS"]
    assert "is_held" not in serialized
    assert "strategy_ko" not in serialized
    assert "action_now" not in serialized
    assert "action_if_triggered" not in serialized


def test_public_market_packet_fails_closed_without_public_universe_contract(tmp_path: Path):
    archive = tmp_path / "archive"
    _write_market_run(
        archive,
        run_id="legacy-unknown-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="IMMEDIATE",
    )

    packet = build_surface_packet(
        "us",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc),
        public=True,
    )

    assert packet["body"]["current"]["bundle"]["strategy_table"] == []


def test_private_market_packet_reports_complete_required_universe(tmp_path: Path):
    archive = tmp_path / "archive"
    run_dir = _write_market_run(
        archive,
        run_id="complete-required-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="IMMEDIATE",
    )
    _write_universe_contract(
        run_dir,
        expected_holdings=["NVDA"],
        missing_holdings=[],
        expected_watchlist=["AAPL", "MSFT"],
        missing_watchlist=[],
        failed_tickers=[],
    )

    packet = build_surface_packet(
        "us",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc),
        public=False,
    )

    coverage = packet["body"]["current"]["universe_coverage"]
    assert coverage == {
        "status": "COMPLETE",
        "complete": True,
        "source_run_id": "complete-required-us",
        "ticker_universe_mode": "config_plus_account",
        "account_snapshot_status": "loaded",
        "expected_holding_count": 1,
        "missing_holding_count": 0,
        "expected_watchlist_count": 2,
        "missing_watchlist_count": 0,
        "expected_analysis_count": 3,
        "missing_analysis_count": 0,
        "analysis_total_count": 3,
        "analysis_successful_count": 3,
        "analysis_failed_count": 0,
        "missing_holding_tickers": [],
        "missing_watchlist_tickers": [],
        "missing_analysis_tickers": [],
        "failed_tickers": [],
    }


def test_private_market_packet_reports_missing_and_failed_required_universe(tmp_path: Path):
    archive = tmp_path / "archive"
    run_dir = _write_market_run(
        archive,
        run_id="incomplete-required-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    _write_universe_contract(
        run_dir,
        expected_holdings=["NVDA", "SGOV"],
        missing_holdings=["SGOV"],
        expected_watchlist=["AAPL", "MSFT"],
        missing_watchlist=["AAPL"],
        failed_tickers=["MSFT"],
    )

    packet = build_surface_packet(
        "us",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc),
        public=False,
    )

    coverage = packet["body"]["current"]["universe_coverage"]
    assert coverage["status"] == "INCOMPLETE"
    assert coverage["complete"] is False
    assert coverage["missing_holding_tickers"] == ["SGOV"]
    assert coverage["missing_watchlist_tickers"] == ["AAPL"]
    assert coverage["failed_tickers"] == ["MSFT"]
    assert coverage["analysis_failed_count"] == 1


def test_market_universe_coverage_rejects_partial_overlay_summary(tmp_path: Path):
    archive = tmp_path / "archive"
    run_dir = _write_market_run(
        archive,
        run_id="partial-overlay-us",
        market="us",
        started_at="2026-07-15T22:10:00+09:00",
        row_mode="IMMEDIATE",
    )
    _write_universe_contract(
        run_dir,
        expected_holdings=["NVDA"],
        missing_holdings=[],
        expected_watchlist=["AAPL", "MSFT"],
        missing_watchlist=[],
        failed_tickers=[],
    )
    manifest_path = run_dir / "run.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["tickers"] = manifest["tickers"][:2]
    manifest["summary"] = {
        "total_tickers": 2,
        "successful_tickers": 2,
        "failed_tickers": 0,
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    packet = build_surface_packet(
        "us",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 15, 13, 15, tzinfo=timezone.utc),
        public=False,
    )

    coverage = packet["body"]["current"]["universe_coverage"]
    assert coverage["status"] == "INCOMPLETE"
    assert coverage["complete"] is False
    assert coverage["expected_analysis_count"] == 3
    assert coverage["analysis_total_count"] == 2


def test_public_market_universe_coverage_omits_private_ticker_names(tmp_path: Path):
    archive = tmp_path / "archive"
    run_dir = _write_market_run(
        archive,
        run_id="public-incomplete-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    _write_universe_contract(
        run_dir,
        expected_holdings=["NVDA", "SGOV"],
        missing_holdings=["SGOV"],
        expected_watchlist=["AAPL", "MSFT"],
        missing_watchlist=["AAPL"],
        failed_tickers=["MSFT"],
    )
    manifest_path = run_dir / "run.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["active_universe"]["fresh_snapshot_drift"] = {
        "status": "VERIFIED",
        "added_holding_tickers": ["WORK.DRIFT.ADDED.PRIVATE"],
        "removed_holding_tickers": ["WORK.DRIFT.REMOVED.PRIVATE"],
    }
    manifest["portfolio"] = {
        "status": "success",
        "private_coverage_snapshot": {
            "holding_set_complete": True,
            "canonical_holding_tickers": ["WORK.SNAPSHOT.HOLD.PRIVATE"],
        },
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    packet = build_surface_packet(
        "us",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc),
        public=True,
    )

    coverage = packet["body"]["current"]["universe_coverage"]
    assert coverage["status"] == "INCOMPLETE"
    assert coverage["portfolio_coverage_details_omitted"] is True
    assert "account_snapshot_status" not in coverage
    assert "expected_holding_count" not in coverage
    assert "analysis_total_count" not in coverage
    assert "analysis_successful_count" not in coverage
    assert "analysis_failed_count" not in coverage
    assert "expected_analysis_count" not in coverage
    assert "missing_analysis_count" not in coverage
    serialized = json.dumps(coverage, ensure_ascii=False)
    serialized_packet = json.dumps(packet, ensure_ascii=False)
    assert "SGOV" not in serialized
    assert "AAPL" not in serialized
    assert "MSFT" not in serialized
    assert "missing_holding_tickers" not in serialized
    assert "missing_watchlist_tickers" not in serialized
    assert "missing_analysis_tickers" not in serialized
    assert "failed_tickers" not in serialized
    assert "WORK.DRIFT.ADDED.PRIVATE" not in serialized_packet
    assert "WORK.DRIFT.REMOVED.PRIVATE" not in serialized_packet
    assert "WORK.SNAPSHOT.HOLD.PRIVATE" not in serialized_packet
    assert "private_coverage_snapshot" not in serialized_packet
    assert "fresh_snapshot_drift" not in serialized_packet


def test_work_packet_expires_rows_independently(tmp_path: Path):
    archive = tmp_path / "archive"
    run_dir = _write_market_run(
        archive,
        run_id="heterogeneous-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="IMMEDIATE",
    )
    bundle_path = run_dir / "decision_bundle_v2.json"
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    fresh = json.loads(json.dumps(bundle["strategy_table"][0]))
    fresh["ticker"] = "MSFT"
    fresh["market_data_asof"] = "2026-07-14T10:35:00-04:00"
    bundle["strategy_table"].append(fresh)
    expired_conditional = json.loads(json.dumps(bundle["strategy_table"][0]))
    expired_conditional["ticker"] = "AAPL"
    expired_conditional["quality"].update(
        {
            "row_mode": "CONDITIONAL",
            "execution_ready": False,
            "conditional_strategy_ready": True,
            "current_execution_promotion": "RECHECK_REQUIRED",
        }
    )
    bundle["strategy_table"].append(expired_conditional)
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")

    packet = build_surface_packet(
        "us",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 14, 40, tzinfo=timezone.utc),
        public=False,
    )
    rows = {row["ticker"]: row for row in packet["body"]["current"]["bundle"]["strategy_table"]}

    assert rows["NVDA"]["quality"]["row_mode"] == "BLOCKED_STALE"
    assert rows["NVDA"]["quality"]["source_row_mode"] == "IMMEDIATE"
    assert rows["MSFT"]["quality"]["row_mode"] == "IMMEDIATE"
    assert rows["AAPL"]["quality"]["row_mode"] == "BLOCKED_STALE"
    assert rows["AAPL"]["quality"]["source_row_mode"] == "CONDITIONAL"
    assert rows["AAPL"]["quality"]["conditional_strategy_ready"] is False
    assert rows["AAPL"]["thesis"]["stance"] == "HOLD"
    assert rows["AAPL"]["thesis"]["label_ko"] == "보유 유지"
    assert rows["AAPL"]["execution"]["readiness"] == "NEEDS_LIVE_RECHECK"
    assert rows["AAPL"]["execution"]["source_readiness"] == "WAIT_FOR_TRIGGER"
    assert packet["body"]["guardrails"]["valid_until"] == "2026-07-14T11:05:00-04:00"


def test_runtime_prepare_resume_ack_and_noop(tmp_path: Path):
    archive = tmp_path / "archive"
    _write_market_run(
        archive,
        run_id="runtime-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    runtime = WorkRuntime(tmp_path / "runtime")
    kwargs = {
        "archive_dir": archive,
        "youtube_archive_dir": tmp_path / "youtube",
        "prism_archive_dir": tmp_path / "prism",
        "now": datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc),
    }

    first = runtime.prepare("us", **kwargs)
    resumed = runtime.prepare("us", **kwargs)
    try:
        runtime.acknowledge("us", first["event_id"])
    except WorkRuntimeError as exc:
        assert "publish the final Work report first" in str(exc)
    else:
        raise AssertionError("market acknowledgement must require a published report")
    published = _publish_market(runtime, first, archive=archive)
    ack = runtime.acknowledge("us", first["event_id"], now=datetime(2026, 7, 14, 14, 6, tzinfo=timezone.utc))
    noop = runtime.prepare("us", **kwargs)

    assert first["result"] == "NEW"
    assert resumed["result"] == "RESUME"
    assert published["status"] == "PUBLISHED"
    assert published["schema"] == WORK_REPORT_SCHEMA
    assert ack["status"] == "rendered"
    assert ack["report_sha256"] == published["report_sha256"]
    assert noop["result"] == "NOOP"
    assert Path(first["packet_path"]).is_file()
    assert runtime.ledger_path.read_text(encoding="utf-8").count("\n") == 5
    ledger = [
        json.loads(line)
        for line in runtime.ledger_path.read_text(encoding="utf-8").splitlines()
    ]
    acknowledged = next(item for item in ledger if item.get("event") == "acknowledged")
    assert acknowledged["source_sha256"] == first["source_sha256"]


def test_acknowledged_market_report_dispatches_exact_idempotent_pages_handoff(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    archive = tmp_path / "archive"
    _write_market_run(
        archive,
        run_id="handoff-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    runtime = WorkRuntime(tmp_path / "runtime")
    prepared = runtime.prepare(
        "us",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc),
    )
    published = _publish_market(runtime, prepared, archive=archive)
    runtime.acknowledge("us", prepared["event_id"])
    monkeypatch.setattr("tradingagents.work.handoff.shutil.which", lambda _name: "gh")
    calls = []

    def fake_runner(command, **kwargs):
        calls.append((list(command), kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    dispatched = dispatch_pages_handoff(
        runtime,
        surface="us",
        event_id=prepared["event_id"],
        report_sha256=published["report_sha256"],
        repository="nornen0202/TradingAgents",
        runner=fake_runner,
    )
    repeated = dispatch_pages_handoff(
        runtime,
        surface="us",
        event_id=prepared["event_id"],
        report_sha256=published["report_sha256"],
        repository="nornen0202/TradingAgents",
        runner=fake_runner,
    )

    assert dispatched["schema"] == WORK_HANDOFF_SCHEMA
    assert dispatched["status"] == "DISPATCH_ACCEPTED"
    assert dispatched["external_delivery_verified"] is False
    assert repeated["status"] == "ALREADY_DISPATCHED"
    assert len(calls) == 1
    command = calls[0][0]
    assert command[:4] == ["gh", "workflow", "run", "work-report-pages-refresh.yml"]
    assert f"event_id={prepared['event_id']}" in command
    assert f"report_sha256={published['report_sha256']}" in command


def test_pages_handoff_rejects_report_that_is_not_latest_acknowledgement(tmp_path: Path):
    runtime = WorkRuntime(tmp_path / "runtime")

    with pytest.raises(WorkRuntimeError, match="latest canonical acknowledged event"):
        dispatch_pages_handoff(
            runtime,
            surface="kr",
            event_id="kr:" + "1" * 32,
            report_sha256="2" * 64,
            repository="nornen0202/TradingAgents",
        )


def test_market_publish_is_content_addressed_and_packet_bound(tmp_path: Path):
    archive = tmp_path / "archive"
    _write_market_run(
        archive,
        run_id="publish-bound-kr",
        market="kr",
        started_at="2026-07-14T10:00:00+09:00",
        row_mode="CONDITIONAL",
    )
    runtime = WorkRuntime(tmp_path / "runtime")
    prepared = runtime.prepare(
        "kr",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 1, 5, tzinfo=timezone.utc),
    )
    draft = _structured_report(prepared, ticker_override=["005930"])

    with pytest.raises(WorkRuntimeError, match="source SHA-256"):
        runtime.publish(
            "kr",
            prepared["event_id"],
            "0" * 64,
            report_markdown="# 전략\n\n테스트",
            structured_report=draft,
            archive_dir=archive,
        )
    bad_binding = json.loads(json.dumps(draft))
    bad_binding["binding"]["event_id"] = "kr:wrong"
    with pytest.raises(WorkRuntimeError, match="binding"):
        runtime.publish(
            "kr",
            prepared["event_id"],
            prepared["source_sha256"],
            report_markdown="# 전략\n\n테스트",
            structured_report=bad_binding,
            archive_dir=archive,
        )

    published = runtime.publish(
        "kr",
        prepared["event_id"],
        prepared["source_sha256"],
        report_markdown="# 전략\n\n분석 시점 thesis와 실행 준비도를 분리합니다.",
        structured_report=draft,
        archive_dir=archive,
        now=datetime(2026, 7, 14, 1, 6, tzinfo=timezone.utc),
    )
    report_path = Path(published["report_path"])
    latest_path = archive / "work-reports" / "kr" / "latest.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert report_path.name == f"{published['report_sha256']}.json"
    assert latest_path.read_bytes() == report_path.read_bytes()
    assert report["structured_report"]["strategies"][0]["ticker"] == "005930"
    assert report["policy"]["external_evidence_profile"] == "balanced_external"
    assert report["policy"]["external_evidence_may_bypass_execution_gate"] is False


def test_market_publish_rejects_missing_unknown_and_duplicate_packet_tickers(tmp_path: Path):
    archive = tmp_path / "archive"
    run_dir = _write_market_run(
        archive,
        run_id="publish-coverage-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    bundle_path = run_dir / "decision_bundle_v2.json"
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    second = json.loads(json.dumps(bundle["strategy_table"][0]))
    second["ticker"] = "AAPL"
    second["is_held"] = False
    bundle["strategy_table"].append(second)
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    runtime = WorkRuntime(tmp_path / "runtime")
    prepared = runtime.prepare(
        "us",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc),
    )

    missing = _structured_report(prepared, ticker_override=["NVDA"])
    missing["coverage_receipt"] = {"status": "COMPLETE", "all_rendered": True}
    with pytest.raises(WorkRuntimeError, match="omits prepared packet tickers: AAPL"):
        runtime.publish(
            "us",
            prepared["event_id"],
            prepared["source_sha256"],
            report_markdown="# 전략\n\n누락 테스트",
            structured_report=missing,
            archive_dir=archive,
        )

    unknown = _structured_report(prepared, ticker_override=["NVDA", "AAPL", "TSLA"])
    with pytest.raises(WorkRuntimeError, match="unknown tickers: TSLA"):
        runtime.publish(
            "us",
            prepared["event_id"],
            prepared["source_sha256"],
            report_markdown="# 전략\n\nunknown 테스트",
            structured_report=unknown,
            archive_dir=archive,
        )

    duplicate = _structured_report(prepared, ticker_override=["NVDA", "AAPL", "AAPL"])
    with pytest.raises(WorkRuntimeError, match="repeats canonical tickers: AAPL"):
        runtime.publish(
            "us",
            prepared["event_id"],
            prepared["source_sha256"],
            report_markdown="# 전략\n\n중복 테스트",
            structured_report=duplicate,
            archive_dir=archive,
        )


def test_market_publish_rejects_unbound_coverage_receipt(tmp_path: Path):
    archive = tmp_path / "archive"
    run_dir = _write_market_run(
        archive,
        run_id="publish-receipt-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    _write_universe_contract(
        run_dir,
        expected_holdings=["NVDA", "AAPL"],
        missing_holdings=["AAPL"],
        expected_watchlist=[],
        missing_watchlist=[],
        failed_tickers=[],
    )
    runtime = WorkRuntime(tmp_path / "runtime")
    prepared = runtime.prepare(
        "us",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc),
    )
    draft = _structured_report(prepared)
    assert draft["coverage_receipt"]["status"] == "INCOMPLETE"
    draft["coverage_receipt"] = {
        "status": "COMPLETE",
        "complete": True,
        "missing_holding_count": 0,
    }

    with pytest.raises(WorkRuntimeError, match="coverage_receipt does not exactly match"):
        runtime.publish(
            "us",
            prepared["event_id"],
            prepared["source_sha256"],
            report_markdown="# 전략\n\n허위 coverage 테스트",
            structured_report=draft,
            archive_dir=archive,
            now=datetime(2026, 7, 14, 14, 6, tzinfo=timezone.utc),
        )


def test_market_publish_rejects_tampered_model_receipt(tmp_path: Path):
    archive = tmp_path / "archive"
    _write_market_run(
        archive,
        run_id="publish-model-receipt-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    runtime = WorkRuntime(tmp_path / "runtime")
    prepared = runtime.prepare(
        "us",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc),
    )
    draft = _structured_report(prepared)
    draft["model_receipt"]["work_synthesis"]["verification_status"] = "RUNTIME_VERIFIED"

    with pytest.raises(WorkRuntimeError, match="model_receipt does not exactly match"):
        runtime.publish(
            "us",
            prepared["event_id"],
            prepared["source_sha256"],
            report_markdown="# 전략\n\n모델 영수증 변조 테스트",
            structured_report=draft,
            archive_dir=archive,
        )


def test_market_publish_binds_healthy_external_evidence_and_requires_explicit_no_match(
    tmp_path: Path,
):
    archive = tmp_path / "archive"
    youtube = tmp_path / "youtube"
    run_dir = _write_market_run(
        archive,
        run_id="publish-external-evidence-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    bundle_path = run_dir / "decision_bundle_v2.json"
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    aapl = json.loads(json.dumps(bundle["strategy_table"][0]))
    aapl["ticker"] = "AAPL"
    aapl["is_held"] = False
    bundle["strategy_table"].append(aapl)
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    _write_youtube_market_evidence(youtube, video_id="nvda-evidence", ticker="NVDA")

    runtime = WorkRuntime(tmp_path / "runtime")
    prepared = runtime.prepare(
        "us",
        archive_dir=archive,
        youtube_archive_dir=youtube,
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc),
    )
    packet = json.loads(Path(prepared["packet_path"]).read_text(encoding="utf-8"))
    contract = packet["body"]["supporting_context"]["receipt_contract"]
    assert contract["sources"]["youtube"]["event_keys"] == ["nvda-evidence"]

    empty_summary = _structured_report(prepared)
    empty_summary["source_summary"] = {}
    with pytest.raises(WorkRuntimeError, match="external-evidence receipt does not exactly match"):
        runtime.publish(
            "us",
            prepared["event_id"],
            prepared["source_sha256"],
            report_markdown="# 전략\n\n외부 근거 요약 누락 테스트",
            structured_report=empty_summary,
            archive_dir=archive,
            now=datetime(2026, 7, 14, 14, 6, tzinfo=timezone.utc),
        )

    tampered_receipt = _structured_report(prepared)
    tampered_receipt["source_summary"]["external_evidence_receipt"]["sources"]["youtube"][
        "event_keys"
    ] = []
    with pytest.raises(WorkRuntimeError, match="external-evidence receipt does not exactly match"):
        runtime.publish(
            "us",
            prepared["event_id"],
            prepared["source_sha256"],
            report_markdown="# 전략\n\n외부 근거 receipt 변조 테스트",
            structured_report=tampered_receipt,
            archive_dir=archive,
            now=datetime(2026, 7, 14, 14, 6, tzinfo=timezone.utc),
        )

    empty_contributions = _structured_report(prepared)
    nvda = next(item for item in empty_contributions["strategies"] if item["ticker"] == "NVDA")
    nvda["source_contributions"] = []
    with pytest.raises(WorkRuntimeError, match="omits a matched healthy external-evidence contribution"):
        runtime.publish(
            "us",
            prepared["event_id"],
            prepared["source_sha256"],
            report_markdown="# 전략\n\n외부 근거 기여 누락 테스트",
            structured_report=empty_contributions,
            archive_dir=archive,
            now=datetime(2026, 7, 14, 14, 6, tzinfo=timezone.utc),
        )

    missing_field = _structured_report(prepared)
    nvda = next(item for item in missing_field["strategies"] if item["ticker"] == "NVDA")
    external = next(item for item in nvda["source_contributions"] if item["source"] == "youtube")
    external.pop("affected_field")
    with pytest.raises(WorkRuntimeError, match="requires event_key and affected_field"):
        runtime.publish(
            "us",
            prepared["event_id"],
            prepared["source_sha256"],
            report_markdown="# 전략\n\n외부 근거 영향 필드 누락 테스트",
            structured_report=missing_field,
            archive_dir=archive,
            now=datetime(2026, 7, 14, 14, 6, tzinfo=timezone.utc),
        )

    missing_no_match_reason = _structured_report(prepared)
    aapl_strategy = next(
        item for item in missing_no_match_reason["strategies"] if item["ticker"] == "AAPL"
    )
    aapl_strategy.pop("no_relevant_evidence_reason")
    with pytest.raises(WorkRuntimeError, match="AAPL requires no_relevant_evidence_reason"):
        runtime.publish(
            "us",
            prepared["event_id"],
            prepared["source_sha256"],
            report_markdown="# 전략\n\n외부 근거 비관련 사유 누락 테스트",
            structured_report=missing_no_match_reason,
            archive_dir=archive,
            now=datetime(2026, 7, 14, 14, 6, tzinfo=timezone.utc),
        )

    published = runtime.publish(
        "us",
        prepared["event_id"],
        prepared["source_sha256"],
        report_markdown="# 전략\n\n외부 근거의 영향과 비관련 사유를 명시한 정상 보고서입니다.",
        structured_report=_structured_report(prepared),
        archive_dir=archive,
        now=datetime(2026, 7, 14, 14, 6, tzinfo=timezone.utc),
    )
    assert published["status"] == "PUBLISHED"


def test_market_report_schema_rejects_nonconcrete_strategy_fields(tmp_path: Path):
    archive = tmp_path / "archive"
    run_dir = _write_market_run(
        archive,
        run_id="publish-schema-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    bundle_path = run_dir / "decision_bundle_v2.json"
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    aapl = json.loads(json.dumps(bundle["strategy_table"][0]))
    aapl["ticker"] = "AAPL"
    aapl["is_held"] = False
    bundle["strategy_table"].append(aapl)
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    runtime = WorkRuntime(tmp_path / "runtime")
    prepared = runtime.prepare(
        "us",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc),
    )

    cases = [
        (
            lambda report: report["strategies"][0]["thesis"].update({"entry_conditions": []}),
            "requires nonempty entry_conditions",
        ),
        (
            lambda report: report["strategies"][0]["thesis"].update(
                {"invalidation_conditions": ["조건 충족 시"]}
            ),
            "must be concrete and non-placeholder",
        ),
        (
            lambda report: report["strategies"][1].update(
                {"rank": report["strategies"][0]["rank"]}
            ),
            "rank must be unique",
        ),
        (
            lambda report: report["strategies"][0].update({"portfolio_role": "other"}),
            "invalid portfolio_role",
        ),
        (
            lambda report: report["strategies"][0]["thesis"].update({"confidence": 1.1}),
            "confidence must be numeric from 0 to 1",
        ),
        (
            lambda report: report["strategies"][0]["thesis"].update({"horizon": "TBD"}),
            "actionable thesis requires horizon",
        ),
        (
            lambda report: report["strategies"][0]["thesis"].update(
                {"invalidation_action": "없음"}
            ),
            "thesis requires invalidation_action",
        ),
        (
            lambda report: report["strategies"][0]["execution"].update(
                {"action_if_triggered": None}
            ),
            "WAIT_FOR_TRIGGER requires action_if_triggered",
        ),
    ]
    for mutate, message in cases:
        draft = _structured_report(prepared)
        mutate(draft)
        with pytest.raises(WorkRuntimeError, match=message):
            runtime.publish(
                "us",
                prepared["event_id"],
                prepared["source_sha256"],
                report_markdown="# 전략\n\n구조화 스키마 거부 테스트",
                structured_report=draft,
                archive_dir=archive,
                now=datetime(2026, 7, 14, 14, 6, tzinfo=timezone.utc),
            )


def test_market_top_actions_bind_exact_strategy_readiness_and_action(tmp_path: Path):
    archive = tmp_path / "archive"
    _write_market_run(
        archive,
        run_id="publish-top-action-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    runtime = WorkRuntime(tmp_path / "runtime")
    prepared = runtime.prepare(
        "us",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc),
    )
    draft = _structured_report(prepared)
    execution = draft["strategies"][0]["execution"]

    unknown = json.loads(json.dumps(draft))
    unknown["top_actions"] = [
        {"ticker": "TSLA", "readiness": execution["readiness"], "action": execution["action_if_triggered"]}
    ]
    with pytest.raises(WorkRuntimeError, match="references unknown strategy ticker: TSLA"):
        runtime.publish(
            "us", prepared["event_id"], prepared["source_sha256"],
            report_markdown="# 전략\n\nunknown top action", structured_report=unknown,
            archive_dir=archive, now=datetime(2026, 7, 14, 14, 6, tzinfo=timezone.utc),
        )

    mismatch = json.loads(json.dumps(draft))
    mismatch["top_actions"] = [
        {"ticker": "NVDA", "readiness": "READY_NOW", "action": execution["action_if_triggered"]}
    ]
    with pytest.raises(WorkRuntimeError, match="readiness does not match its strategy"):
        runtime.publish(
            "us", prepared["event_id"], prepared["source_sha256"],
            report_markdown="# 전략\n\nreadiness mismatch", structured_report=mismatch,
            archive_dir=archive, now=datetime(2026, 7, 14, 14, 6, tzinfo=timezone.utc),
        )

    draft["top_actions"] = [
        {"ticker": "NVDA", "readiness": execution["readiness"], "action": execution["action_if_triggered"]}
    ]
    published = runtime.publish(
        "us", prepared["event_id"], prepared["source_sha256"],
        report_markdown="# 전략\n\n전략과 일치하는 top action", structured_report=draft,
        archive_dir=archive, now=datetime(2026, 7, 14, 14, 6, tzinfo=timezone.utc),
    )
    assert published["status"] == "PUBLISHED"


@pytest.mark.parametrize(
    "blocked_markdown",
    [
        "# 전략\n\n**지금 실행 가능** ： **없음**",
        "# 전략\n\n현재   조건부 실행 가능: ( None )",
        "# 전략\n\n조건부 재확인 - NONE",
        "# 전략\n\n조건부 재확인： n / a",
        "# 전략\n\n`BLOCKED _ STALE`",
    ],
)
def test_market_markdown_empty_state_filter_normalizes_formatting_variants(
    tmp_path: Path,
    blocked_markdown: str,
):
    archive = tmp_path / "archive"
    _write_market_run(
        archive,
        run_id="publish-markdown-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    runtime = WorkRuntime(tmp_path / "runtime")
    prepared = runtime.prepare(
        "us", archive_dir=archive, youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc),
    )
    with pytest.raises(WorkRuntimeError, match="blocked empty-state or raw status code"):
        runtime.publish(
            "us", prepared["event_id"], prepared["source_sha256"],
            report_markdown=blocked_markdown, structured_report=_structured_report(prepared),
            archive_dir=archive, now=datetime(2026, 7, 14, 14, 6, tzinfo=timezone.utc),
        )


def test_market_publish_rejects_execution_gate_promotion_and_expired_validity(tmp_path: Path):
    archive = tmp_path / "archive"
    _write_market_run(
        archive,
        run_id="publish-gate-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    runtime = WorkRuntime(tmp_path / "runtime")
    prepared = runtime.prepare(
        "us",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc),
    )

    promoted = _structured_report(prepared)
    promoted["strategies"][0]["execution"].update(
        {
            "readiness": "READY_NOW",
            "action_now": "BUY",
            "action_if_triggered": None,
        }
    )
    with pytest.raises(WorkRuntimeError, match="promotes packet execution to READY_NOW"):
        runtime.publish(
            "us",
            prepared["event_id"],
            prepared["source_sha256"],
            report_markdown="# 전략\n\n승격 테스트",
            structured_report=promoted,
            archive_dir=archive,
            now=datetime(2026, 7, 14, 14, 6, tzinfo=timezone.utc),
        )

    extended = _structured_report(prepared)
    original_valid_until = datetime.fromisoformat(
        extended["strategies"][0]["execution"]["valid_until"]
    )
    extended["strategies"][0]["execution"]["valid_until"] = (
        original_valid_until + timedelta(hours=1)
    ).isoformat()
    with pytest.raises(WorkRuntimeError, match="extends the packet execution validity"):
        runtime.publish(
            "us",
            prepared["event_id"],
            prepared["source_sha256"],
            report_markdown="# 전략\n\n유효시간 연장 테스트",
            structured_report=extended,
            archive_dir=archive,
            now=datetime(2026, 7, 14, 14, 6, tzinfo=timezone.utc),
        )

    expired = _structured_report(prepared)
    with pytest.raises(WorkRuntimeError, match="packet execution validity that has expired"):
        runtime.publish(
            "us",
            prepared["event_id"],
            prepared["source_sha256"],
            report_markdown="# 전략\n\npublish 시점 만료 테스트",
            structured_report=expired,
            archive_dir=archive,
            now=datetime(2026, 7, 14, 15, 0, tzinfo=timezone.utc),
        )


def test_market_publish_preserves_packet_blockers_and_required_rechecks(tmp_path: Path):
    archive = tmp_path / "archive"
    run_dir = _write_market_run(
        archive,
        run_id="publish-blockers-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    bundle_path = run_dir / "decision_bundle_v2.json"
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    bundle["strategy_table"][0]["quality"]["provider_blockers"] = ["provider_down"]
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    runtime = WorkRuntime(tmp_path / "runtime")
    prepared = runtime.prepare(
        "us",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 15, 0, tzinfo=timezone.utc),
    )

    missing_blockers = _structured_report(prepared)
    missing_blockers["strategies"][0]["execution"]["blockers"] = []
    with pytest.raises(WorkRuntimeError, match="omits packet execution blockers"):
        runtime.publish(
            "us",
            prepared["event_id"],
            prepared["source_sha256"],
            report_markdown="# 전략\n\nblocker 누락 테스트",
            structured_report=missing_blockers,
            archive_dir=archive,
            now=datetime(2026, 7, 14, 15, 1, tzinfo=timezone.utc),
        )

    missing_rechecks = _structured_report(prepared)
    missing_rechecks["strategies"][0]["execution"]["required_rechecks"] = []
    with pytest.raises(WorkRuntimeError, match="omits packet execution required_rechecks"):
        runtime.publish(
            "us",
            prepared["event_id"],
            prepared["source_sha256"],
            report_markdown="# 전략\n\nrecheck 누락 테스트",
            structured_report=missing_rechecks,
            archive_dir=archive,
            now=datetime(2026, 7, 14, 15, 1, tzinfo=timezone.utc),
        )


def test_market_publish_rejects_kis_order_and_identity_fields(tmp_path: Path):
    archive = tmp_path / "archive"
    _write_market_run(
        archive,
        run_id="publish-private-fields-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    runtime = WorkRuntime(tmp_path / "runtime")
    prepared = runtime.prepare(
        "us",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc),
    )
    forbidden_keys = (
        "order_id",
        "order_no",
        "order_number",
        "order_reference",
        "orderId",
        "odno",
        "cano",
        "acnt_prdt_cd",
        "custtype",
        "client_id",
        "customer_id",
        "broker_account_id",
        "access_token",
        "refresh_token",
        "token",
    )
    for forbidden_key in forbidden_keys:
        draft = _structured_report(prepared)
        draft["source_summary"][forbidden_key] = "sensitive-value"
        with pytest.raises(WorkRuntimeError, match=f"forbidden key: {forbidden_key}"):
            runtime.publish(
                "us",
                prepared["event_id"],
                prepared["source_sha256"],
                report_markdown="# 전략\n\n민감 필드 테스트",
                structured_report=draft,
                archive_dir=archive,
                now=datetime(2026, 7, 14, 14, 6, tzinfo=timezone.utc),
            )

    for sensitive_value in (
        "계좌번호: 1234-5678",
        "계좌번호 1234-5678",
        "CANO=12345678",
        "CANO 12345678",
        "access token abcdefgh",
        r"C:\Users\investor\private\receipt.json",
    ):
        draft = _structured_report(prepared)
        draft["source_summary"]["note"] = sensitive_value
        with pytest.raises(WorkRuntimeError, match="blocked secret, identifier, or local path"):
            runtime.publish(
                "us",
                prepared["event_id"],
                prepared["source_sha256"],
                report_markdown="# 전략\n\n민감 값 테스트",
                structured_report=draft,
                archive_dir=archive,
                now=datetime(2026, 7, 14, 14, 6, tzinfo=timezone.utc),
            )

    with pytest.raises(WorkRuntimeError, match="blocked secret, identifier, or local path"):
        runtime.publish(
            "us",
            prepared["event_id"],
            prepared["source_sha256"],
            report_markdown="# 전략\n\n주문 참조: ODNO=12345678",
            structured_report=_structured_report(prepared),
            archive_dir=archive,
            now=datetime(2026, 7, 14, 14, 6, tzinfo=timezone.utc),
        )

    safe = runtime.publish(
        "us",
        prepared["event_id"],
        prepared["source_sha256"],
        report_markdown="# 전략\n\naccount id unavailable; identifier is intentionally omitted.",
        structured_report=_structured_report(prepared),
        archive_dir=archive,
        now=datetime(2026, 7, 14, 14, 6, tzinfo=timezone.utc),
    )
    assert safe["status"] == "PUBLISHED"


def test_market_publish_revalidates_immutable_outbox_packet(tmp_path: Path):
    archive = tmp_path / "archive"
    _write_market_run(
        archive,
        run_id="publish-tamper-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    runtime = WorkRuntime(tmp_path / "runtime")
    prepared = runtime.prepare(
        "us",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc),
    )
    packet_path = Path(prepared["packet_path"])
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    packet["body"]["current"]["bundle"]["strategy_table"][0]["ticker"] = "ATTACK"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(WorkRuntimeError, match="source SHA-256 does not match its body"):
        runtime.publish(
            "us",
            prepared["event_id"],
            prepared["source_sha256"],
            report_markdown="# 전략\n\n변조 테스트",
            structured_report=_structured_report(prepared),
            archive_dir=archive,
            now=datetime(2026, 7, 14, 14, 6, tzinfo=timezone.utc),
        )


def test_runtime_deduplicates_and_revises_youtube_events(tmp_path: Path):
    archive = tmp_path / "archive"
    youtube = tmp_path / "youtube"
    run_dir = youtube / "runs" / "2026" / "youtube-run"
    video_dir = run_dir / "videos" / "video-1"
    video_dir.mkdir(parents=True)
    manifest = {
        "run_id": "youtube-run",
        "started_at": "2026-07-14T07:00:00+09:00",
        "videos": [
            {
                "video_id": "video-1",
                "title": "테스트",
                "published_at": "2026-07-14T06:30:00+09:00",
                "public_summary_path": "videos/video-1/public_summary.json",
            }
        ],
    }
    (run_dir / "youtube_run.json").write_text(json.dumps(manifest), encoding="utf-8")
    summary_path = video_dir / "public_summary.json"
    summary_path.write_text(
        json.dumps({"video_id": "video-1", "title": "V1", "published_at": "2026-07-14T06:30:00+09:00"}),
        encoding="utf-8",
    )
    runtime = WorkRuntime(tmp_path / "runtime")
    kwargs = {
        "archive_dir": archive,
        "youtube_archive_dir": youtube,
        "prism_archive_dir": tmp_path / "prism",
        "now": datetime(2026, 7, 14, 7, 5, tzinfo=timezone.utc),
    }

    first = runtime.prepare("youtube", **kwargs)
    first_packet = json.loads(Path(first["packet_path"]).read_text(encoding="utf-8"))
    runtime.acknowledge("youtube", first["event_id"])
    second = runtime.prepare("youtube", **kwargs)
    summary_path.write_text(
        json.dumps({"video_id": "video-1", "title": "V2", "published_at": "2026-07-14T06:30:00+09:00"}),
        encoding="utf-8",
    )
    revision = runtime.prepare("youtube", **kwargs)
    revision_packet = json.loads(Path(revision["packet_path"]).read_text(encoding="utf-8"))

    assert first_packet["body"]["delta"]["new_events"] == 1
    assert second["result"] == "NOOP"
    assert revision["result"] == "NEW"
    assert revision_packet["body"]["delta"]["revised_events"] == 1


def test_advisory_contract_revision_is_not_suppressed_as_noop(tmp_path: Path, monkeypatch):
    archive = tmp_path / "archive"
    youtube = tmp_path / "youtube"
    run_dir = youtube / "runs" / "2026" / "youtube-contract"
    video_dir = run_dir / "videos" / "video-1"
    video_dir.mkdir(parents=True)
    (run_dir / "youtube_run.json").write_text(
        json.dumps(
            {
                "run_id": "youtube-contract",
                "started_at": "2026-07-14T07:00:00+09:00",
                "status": "success",
                "videos": [
                    {
                        "video_id": "video-1",
                        "published_at": "2026-07-14T06:30:00+09:00",
                        "public_summary_path": "videos/video-1/public_summary.json",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (video_dir / "public_summary.json").write_text(
        json.dumps({"video_id": "video-1", "title": "V1", "published_at": "2026-07-14T06:30:00+09:00"}),
        encoding="utf-8",
    )
    runtime = WorkRuntime(tmp_path / "runtime")
    kwargs = {
        "archive_dir": archive,
        "youtube_archive_dir": youtube,
        "prism_archive_dir": tmp_path / "prism",
        "now": datetime(2026, 7, 14, 7, 5, tzinfo=timezone.utc),
    }
    first = runtime.prepare("youtube", **kwargs)
    runtime.acknowledge("youtube", first["event_id"])
    original = work_packet.workflow_contract_hashes("youtube")
    monkeypatch.setattr(
        work_packet,
        "workflow_contract_hashes",
        lambda _surface: {**original, "skill_sha256": "f" * 64},
    )

    revised = runtime.prepare("youtube", **kwargs)
    revised_packet = json.loads(Path(revised["packet_path"]).read_text(encoding="utf-8"))

    assert revised["result"] == "NEW"
    assert revised_packet["body"]["delta"]["delivered_event_keys"] == ["video-1"]


def test_advisory_manifest_rotation_does_not_regress(tmp_path: Path):
    youtube = tmp_path / "youtube"
    for index in range(41):
        run_dir = youtube / "runs" / "2026" / f"run-{index:02d}"
        video_dir = run_dir / "videos" / f"video-{index:02d}"
        video_dir.mkdir(parents=True)
        published = f"2026-07-14T{index % 20:02d}:00:00+09:00"
        (run_dir / "youtube_run.json").write_text(
            json.dumps(
                {
                    "run_id": f"run-{index:02d}",
                    "started_at": published,
                    "status": "success",
                    "videos": [
                        {
                            "video_id": f"video-{index:02d}",
                            "published_at": published,
                            "public_summary_path": f"videos/video-{index:02d}/public_summary.json",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (video_dir / "public_summary.json").write_text(
            json.dumps({"video_id": f"video-{index:02d}", "published_at": published}),
            encoding="utf-8",
        )
    runtime = WorkRuntime(tmp_path / "runtime")
    kwargs = {
        "archive_dir": tmp_path / "archive",
        "youtube_archive_dir": youtube,
        "prism_archive_dir": tmp_path / "prism",
        "now": datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc),
    }
    first = runtime.prepare("youtube", **kwargs)
    runtime.acknowledge("youtube", first["event_id"])
    empty = youtube / "runs" / "2026" / "run-99"
    empty.mkdir(parents=True)
    (empty / "youtube_run.json").write_text(
        json.dumps({"run_id": "run-99", "started_at": "2026-07-14T22:00:00+09:00", "status": "success", "videos": []}),
        encoding="utf-8",
    )

    result = runtime.prepare("youtube", **kwargs)

    assert result["result"] != "SOURCE_REGRESSION"


def test_market_archive_rollback_is_source_regression(tmp_path: Path):
    archive = tmp_path / "archive"
    older = _write_market_run(
        archive,
        run_id="older-us",
        market="us",
        started_at="2026-07-14T09:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    latest = _write_market_run(
        archive,
        run_id="latest-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    runtime = WorkRuntime(tmp_path / "runtime")
    kwargs = {
        "archive_dir": archive,
        "youtube_archive_dir": tmp_path / "youtube",
        "prism_archive_dir": tmp_path / "prism",
        "now": datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc),
    }
    first = runtime.prepare("us", **kwargs)
    _publish_market(runtime, first, archive=archive)
    runtime.acknowledge("us", first["event_id"])
    shutil.rmtree(latest)

    result = runtime.prepare("us", **kwargs)

    assert older.exists()
    assert result["result"] == "SOURCE_REGRESSION"


def test_invalid_state_fails_closed_and_visible_receipt_can_recover(tmp_path: Path):
    archive = tmp_path / "archive"
    _write_market_run(
        archive,
        run_id="recover-kr",
        market="kr",
        started_at="2026-07-14T10:00:00+09:00",
        row_mode="CONDITIONAL",
    )
    runtime = WorkRuntime(tmp_path / "runtime")
    prepared = runtime.prepare(
        "kr",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 1, 5, tzinfo=timezone.utc),
    )
    packet = json.loads(Path(prepared["packet_path"]).read_text(encoding="utf-8"))
    published = _publish_market(runtime, prepared, archive=archive)
    acknowledged = runtime.acknowledge("kr", prepared["event_id"])
    runtime.state_path.write_text("{broken", encoding="utf-8")

    try:
        runtime.status()
    except WorkRuntimeError as exc:
        assert "Invalid canonical Work state" in str(exc)
    else:
        raise AssertionError("corrupt canonical Work state must fail closed")

    recovered = runtime.recover(
        "kr",
        prepared["event_id"],
        packet["source_sha256"],
        report_sha256=published["report_sha256"],
        state_revision=acknowledged["state_revision"],
        archive_dir=archive,
    )
    assert recovered["status"] == "recovered_visible_receipt"
    assert recovered["state_revision"] == acknowledged["state_revision"]
    state = runtime.status("kr")["state"]
    assert state["last_acked_event_id"] == prepared["event_id"]
    assert state["last_acked_report_sha256"] == published["report_sha256"]


def test_market_recovery_rejects_valid_state_and_unacknowledged_report(tmp_path: Path):
    archive = tmp_path / "archive"
    _write_market_run(
        archive,
        run_id="recover-unacked-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    runtime = WorkRuntime(tmp_path / "runtime")
    prepared = runtime.prepare(
        "us",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc),
    )
    packet = json.loads(Path(prepared["packet_path"]).read_text(encoding="utf-8"))
    published = _publish_market(runtime, prepared, archive=archive)

    with pytest.raises(WorkRuntimeError, match="cannot replace existing canonical state"):
        runtime.recover(
            "us",
            prepared["event_id"],
            packet["source_sha256"],
            report_sha256=published["report_sha256"],
            state_revision=1,
            archive_dir=archive,
        )

    runtime.state_path.unlink()
    with pytest.raises(WorkRuntimeError, match="not backed by the canonical acknowledgement ledger"):
        runtime.recover(
            "us",
            prepared["event_id"],
            packet["source_sha256"],
            report_sha256=published["report_sha256"],
            state_revision=1,
            archive_dir=archive,
        )


def test_market_recovery_rejects_stale_report_replay_after_state_loss(tmp_path: Path):
    archive = tmp_path / "archive"
    _write_market_run(
        archive,
        run_id="recover-old-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    runtime = WorkRuntime(tmp_path / "runtime")
    first = runtime.prepare(
        "us",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc),
    )
    first_packet = json.loads(Path(first["packet_path"]).read_text(encoding="utf-8"))
    first_report = _publish_market(runtime, first, archive=archive)
    first_ack = runtime.acknowledge("us", first["event_id"])

    _write_market_run(
        archive,
        run_id="recover-new-us",
        market="us",
        started_at="2026-07-14T11:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    second = runtime.prepare(
        "us",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 15, 5, tzinfo=timezone.utc),
    )
    _publish_market(runtime, second, archive=archive)
    runtime.acknowledge("us", second["event_id"])
    runtime.state_path.write_text("{broken", encoding="utf-8")

    with pytest.raises(WorkRuntimeError, match="Recovery report is stale"):
        runtime.recover(
            "us",
            first["event_id"],
            first_packet["source_sha256"],
            report_sha256=first_report["report_sha256"],
            state_revision=first_ack["state_revision"],
            archive_dir=archive,
        )


def test_multi_surface_recovery_preserves_prior_recovered_surface(tmp_path: Path):
    archive = tmp_path / "archive"
    _write_market_run(
        archive,
        run_id="recover-multi-kr",
        market="kr",
        started_at="2026-07-14T10:00:00+09:00",
        row_mode="CONDITIONAL",
    )
    _write_market_run(
        archive,
        run_id="recover-multi-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    runtime = WorkRuntime(tmp_path / "runtime")
    receipts = {}
    for surface, prepared_at in (
        ("kr", datetime(2026, 7, 14, 1, 5, tzinfo=timezone.utc)),
        ("us", datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc)),
    ):
        prepared = runtime.prepare(
            surface,
            archive_dir=archive,
            youtube_archive_dir=tmp_path / "youtube",
            prism_archive_dir=tmp_path / "prism",
            now=prepared_at,
        )
        packet = json.loads(Path(prepared["packet_path"]).read_text(encoding="utf-8"))
        report = _publish_market(runtime, prepared, archive=archive)
        ack = runtime.acknowledge(surface, prepared["event_id"])
        receipts[surface] = (prepared, packet, report, ack)

    runtime.state_path.write_text("{broken", encoding="utf-8")
    for surface in ("us", "kr"):
        prepared, packet, report, ack = receipts[surface]
        runtime.recover(
            surface,
            prepared["event_id"],
            packet["source_sha256"],
            report_sha256=report["report_sha256"],
            state_revision=ack["state_revision"],
            archive_dir=archive,
        )

    recovered_state = runtime.status()
    assert set(recovered_state["surfaces"]) == {"kr", "us"}
    assert recovered_state["revision"] == max(
        receipts["kr"][3]["state_revision"],
        receipts["us"][3]["state_revision"],
    )
    assert recovered_state["surfaces"]["kr"]["last_acked_report_sha256"] == receipts["kr"][2][
        "report_sha256"
    ]
    assert recovered_state["surfaces"]["us"]["last_acked_report_sha256"] == receipts["us"][2][
        "report_sha256"
    ]


def test_advisory_source_health_detects_stale_producer(tmp_path: Path):
    youtube = tmp_path / "youtube"
    run_dir = youtube / "runs" / "2026" / "stale-run"
    video_dir = run_dir / "videos" / "old-video"
    video_dir.mkdir(parents=True)
    (run_dir / "youtube_run.json").write_text(
        json.dumps(
            {
                "run_id": "stale-run",
                "started_at": "2026-07-10T06:00:00+09:00",
                "finished_at": "2026-07-10T06:10:00+09:00",
                "status": "success",
                "videos": [
                    {
                        "video_id": "old-video",
                        "published_at": "2026-07-10T05:00:00+09:00",
                        "public_summary_path": "videos/old-video/public_summary.json",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (video_dir / "public_summary.json").write_text(
        json.dumps({"video_id": "old-video", "published_at": "2026-07-10T05:00:00+09:00"}),
        encoding="utf-8",
    )

    packet = build_surface_packet(
        "youtube",
        archive_dir=tmp_path / "archive",
        youtube_archive_dir=youtube,
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 7, 0, tzinfo=timezone.utc),
    )

    assert packet["body"]["source_health"] == "STALE"
    assert packet["body"]["source"]["run_id"] == "stale-run"
    assert packet["body"]["source"]["stale_after_hours"] == 36


def test_youtube_packet_preserves_evidence_ids_for_claim_mapping(tmp_path: Path):
    run_dir = tmp_path / "run"
    summary_dir = run_dir / "videos" / "video-1"
    summary_dir.mkdir(parents=True)
    (summary_dir / "public_summary.json").write_text(
        json.dumps(
            {
                "video_id": "video-1",
                "published_at": "2026-07-14T06:30:00+09:00",
                "entities": [{"ticker": "NVDA", "name": "NVIDIA", "status": "verified"}],
                "claims": [{"claim_id": "C1", "supporting_evidence_ids": ["E1"]}],
                "evidence": [
                    {
                        "evidence_id": "E1",
                        "claim_id": "C1",
                        "title": "Official filing",
                        "source_url": "https://example.test/filing",
                        "source_tier": "official",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    event = work_packet._youtube_event(
        {
            "video_id": "video-1",
            "published_at": "2026-07-14T06:30:00+09:00",
            "public_summary_path": "videos/video-1/public_summary.json",
        },
        run_dir,
    )

    assert event["summary"]["claims"][0]["supporting_evidence_ids"] == ["E1"]
    assert event["summary"]["evidence"][0]["evidence_id"] == "E1"
    assert event["relevance"]["tickers"] == ["NVDA"]
    assert event["relevance"]["markets"] == ["US"]


def test_external_context_ranks_ticker_relevance_and_declares_balanced_policy():
    events = [
        {
            "event_key": "general",
            "occurred_at": "2026-07-14T11:00:00+09:00",
            "relevance": {"tickers": [], "markets": ["US"]},
        },
        {
            "event_key": "nvda",
            "occurred_at": "2026-07-14T10:00:00+09:00",
            "relevance": {"tickers": ["NVDA"], "markets": ["US"]},
        },
    ]

    ranked = work_packet._rank_support_events(events, market="us", tickers=["NVDA"])
    policy = work_packet._balanced_external_policy()

    assert ranked[0]["event_key"] == "nvda"
    assert ranked[0]["relevance"]["matched_tickers"] == ["NVDA"]
    assert ranked[0]["relevance"]["score"] > ranked[1]["relevance"]["score"]
    assert policy["profile"] == "balanced_external"
    assert "confidence" in policy["material_thesis_effects"]
    assert policy["may_bypass_market_or_portfolio_execution_gate"] is False


@pytest.mark.parametrize(("source", "cap"), [("youtube", 12), ("prism", 20)])
def test_supporting_context_cap_uses_fair_ticker_quota_and_recomputes_receipt(
    monkeypatch,
    tmp_path: Path,
    source: str,
    cap: int,
):
    busy_events = [
        {
            "event_key": f"busy-{index}",
            "content_sha256": f"{index + 1:064x}",
            "occurred_at": (
                datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)
                + timedelta(minutes=index)
            ).isoformat(),
            "relevance": {"tickers": ["BUSY"], "markets": ["US"]},
            "summary": {},
        }
        for index in range(cap + 3)
    ]
    held_event = {
        "event_key": "held-only-event",
        "content_sha256": "f" * 64,
        "occurred_at": "2026-07-14T11:00:00+00:00",
        "relevance": {"tickers": ["HELD"], "markets": ["US"]},
        "summary": {},
    }
    events = [*busy_events, held_event]
    target_body = {
        "source_health": "OK",
        "coverage": {
            "total_unique_events": len(events),
            "window_events": len(events),
            "transmitted_events": len(events),
            "truncated": False,
        },
        "events": events,
    }
    empty_body = {
        "source_health": "MISSING",
        "coverage": {
            "total_unique_events": 0,
            "window_events": 0,
            "transmitted_events": 0,
            "truncated": False,
        },
        "events": [],
    }
    monkeypatch.setattr(
        work_packet,
        "_youtube_body",
        lambda _archive, *, now: target_body if source == "youtube" else empty_body,
    )
    monkeypatch.setattr(
        work_packet,
        "_prism_body",
        lambda _archive, *, now: target_body if source == "prism" else empty_body,
    )

    context = work_packet._supporting_context(
        {"youtube": tmp_path / "youtube", "prism": tmp_path / "prism"},
        now=datetime(2026, 7, 14, 14, 0, tzinfo=timezone.utc),
        market="us",
        tickers=["HELD", "BUSY"],
    )
    selected = context[source]["events"]
    selected_keys = [event["event_key"] for event in selected]
    coverage = context[source]["coverage"]
    receipt = context["receipt_contract"]["sources"][source]

    assert len(selected) == cap
    assert "held-only-event" in selected_keys
    assert coverage["transmitted_events"] == cap
    assert coverage["truncated"] is True
    assert coverage["omitted_events"] == len(events) - cap
    assert coverage["omitted_due_to_context_cap"] == len(events) - cap
    assert coverage["oldest_occurred_at"] == held_event["occurred_at"]
    assert receipt["event_keys"] == selected_keys
    assert receipt["coverage"] == coverage


def test_public_packet_budget_drops_oldest_events_deterministically():
    body = {
        "kind": "prism",
        "source_health": "OK",
        "execution_eligible": False,
        "coverage": {
            "total_unique_events": 100,
            "window_events": 100,
            "transmitted_events": 100,
            "truncated": False,
        },
        "events": [
            {
                "event_key": f"event-{index}",
                "content_sha256": f"{index:064x}"[-64:],
                "summary": {"preview": "x" * 2_000},
            }
            for index in range(100)
        ],
    }
    packet = work_packet.seal_packet("prism", body=body)

    fitted = _fit_packet_budget(packet, max_chars=20_000)

    assert len(json.dumps(fitted, ensure_ascii=False, indent=2)) <= 20_000
    assert fitted["body"]["coverage"]["truncated"] is True
    assert fitted["body"]["coverage"]["omitted_due_to_packet_budget"] > 0
    assert fitted["body"]["events"][0]["event_key"] == "event-0"


def test_work_site_status_points_to_hash_verified_packet(tmp_path: Path):
    archive = tmp_path / "archive"
    _write_market_run(
        archive,
        run_id="site-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="IMMEDIATE",
    )
    site = tmp_path / "site"

    index = build_work_site(
        site_dir=site,
        archive_dir=archive,
        public_base_url="https://example.test/TradingAgents",
    )

    status = json.loads((site / "work" / "v1" / "us" / "status.json").read_text(encoding="utf-8"))
    latest_bytes = (site / "work" / "v1" / "us" / "latest.json").read_bytes()
    assert status["packet_sha256"] == hashlib.sha256(latest_bytes).hexdigest()
    assert status["latest_url"] == "https://example.test/TradingAgents/work/v1/us/latest.json"
    assert index["streams"]["us"]["event_id"] == status["event_id"]
    published_prompt = site / "work" / "v1" / "prompts" / "market_us.md"
    assert published_prompt.is_file()
    assert status["prompt_sha256"] == hashlib.sha256(published_prompt.read_bytes()).hexdigest()


def test_work_site_exposes_validated_content_addressed_integrated_report(tmp_path: Path):
    archive = tmp_path / "archive"
    _write_market_run(
        archive,
        run_id="site-report-us",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    runtime = WorkRuntime(tmp_path / "runtime")
    prepared = runtime.prepare(
        "us",
        archive_dir=archive,
        youtube_archive_dir=tmp_path / "youtube",
        prism_archive_dir=tmp_path / "prism",
        now=datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc),
    )
    published = _publish_market(runtime, prepared, archive=archive)
    site = tmp_path / "site"

    build_work_site(
        site_dir=site,
        archive_dir=archive,
        public_base_url="https://example.test/TradingAgents",
    )

    status = json.loads((site / "work" / "v1" / "us" / "status.json").read_text(encoding="utf-8"))
    report_status = status["integrated_report"]
    latest = site / "work" / "v1" / "us" / "report" / "latest.json"
    event = site / "work" / "v1" / "us" / "report" / "events" / f"{published['report_sha256']}.json"
    assert report_status["report_sha256"] == published["report_sha256"]
    assert report_status["latest_url"].endswith("/work/v1/us/report/latest.json")
    assert latest.read_bytes() == event.read_bytes()


def test_work_site_preserves_prior_content_addressed_events(tmp_path: Path):
    archive = tmp_path / "archive"
    site = tmp_path / "site"
    _write_market_run(
        archive,
        run_id="site-event-1",
        market="us",
        started_at="2026-07-14T10:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    first = build_work_site(site_dir=site, archive_dir=archive)
    first_name = Path(first["streams"]["us"]["event_url"]).name
    _write_market_run(
        archive,
        run_id="site-event-2",
        market="us",
        started_at="2026-07-14T11:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    second = build_work_site(site_dir=site, archive_dir=archive)
    second_name = Path(second["streams"]["us"]["event_url"]).name

    assert first_name != second_name
    assert (site / "work" / "v1" / "us" / "events" / first_name).is_file()
    assert (site / "work" / "v1" / "us" / "events" / second_name).is_file()
    assert (archive / "work-public" / "v1" / "us" / "events" / first_name).is_file()


def test_work_site_purges_legacy_public_market_event_with_private_actions(tmp_path: Path):
    archive = tmp_path / "archive"
    site = tmp_path / "site"
    _write_market_run(
        archive,
        run_id="safe-current-us",
        market="us",
        started_at="2026-07-14T11:00:00-04:00",
        row_mode="CONDITIONAL",
    )
    legacy = work_packet.seal_packet(
        "us",
        body={
            "kind": "market",
            "market": "US",
            "current": {
                "private_portfolio_overlay": {
                    "privacy": "LOCAL_ONLY_DO_NOT_PUBLISH",
                    "actions": [{"canonical_ticker": "SECRET", "action_now": "SELL"}],
                }
            },
        },
    )
    legacy_name = "legacy-private.json"
    legacy_path = archive / "work-public" / "v1" / "us" / "events" / legacy_name
    legacy_path.parent.mkdir(parents=True, exist_ok=True)
    legacy_path.write_text(json.dumps(legacy, ensure_ascii=False), encoding="utf-8")

    build_work_site(site_dir=site, archive_dir=archive)

    assert not legacy_path.exists()
    assert not (site / "work" / "v1" / "us" / "events" / legacy_name).exists()
    assert "SECRET" not in (site / "work" / "v1" / "us" / "latest.json").read_text(encoding="utf-8")


def test_market_prompts_require_row_gate_and_receipt():
    for surface in ("kr", "us"):
        text = work_packet.prompt_text(surface)
        assert "row_mode=IMMEDIATE" in text
        assert "전역 report mode" in text
        assert "current.universe_coverage" in text
        assert "COMPLETE|INCOMPLETE|UNVERIFIED" in text
        assert "COVERAGE_RECEIPT" in text
        assert "response_scanner_limit" in text
        assert '"response_scanner_limit":10' in text
        assert "MOBILE_HANDOFF" in text
        assert "전송·게시 완료를 주장" in text
        assert "WORK_RECEIPT" in text
        assert "비신뢰" in text
        assert "balanced_external" in text
        assert "thesis" in text
        assert "execution.readiness" in text
        assert "current.universe_coverage` 객체를 그대로 복사" in text
        assert "required rechecks를 모두 보존" in text
        assert "최대 3개" in text
        assert "publish --surface" in text
        assert "빈 카테고리" in text
        assert "raw `BLOCKED_STALE`" in text


def test_all_work_prompts_fail_closed_on_stale_data_and_do_not_claim_mobile_delivery():
    for surface in ("kr", "us", "youtube", "prism"):
        text = work_packet.prompt_text(surface)
        assert "COVERAGE_RECEIPT" in text
        assert "MOBILE_HANDOFF" in text
        assert "PENDING_EXTERNAL_VERIFICATION" in text
        assert "계좌 식별자" in text or "전송·게시 완료를 주장" in text
        assert "STALE" in text


def test_scheduled_work_task_manifest_uses_gpt56_local_mode_and_unique_surfaces():
    manifest = json.loads(Path("config/chatgpt_work_tasks.json").read_text(encoding="utf-8"))

    assert manifest["execution_mode"] == "local"
    assert manifest["model"] == "gpt-5.6-sol"
    assert manifest["reasoning_effort"] == "xhigh"
    boundary = manifest["capability_boundary"]
    assert boundary["local_archives_require_local_host"] is True
    assert boundary["chatgpt_web_direct_local_file_access"] is False
    assert boundary["mobile_delivery_owner"] == "external_github_notification_pipeline"
    assert "plaintext_strategy_pages" in boundary["mobile_channels"]
    assert "aes_gcm_private_mobile_pages" not in boundary["mobile_channels"]
    assert boundary["task_must_not_claim_external_delivery"] is True
    assert boundary["market_report_pages_handoff_workflow"] == "work-report-pages-refresh.yml"
    assert {task["surface"] for task in manifest["tasks"]} == {"kr", "us", "youtube", "prism"}
    assert all("Chrome" in task["prompt"] or "ChatGPT web" in task["prompt"] for task in manifest["tasks"])
    assert all("COVERAGE_RECEIPT" in task["prompt"] for task in manifest["tasks"])
    assert all("MOBILE_HANDOFF" in task["prompt"] for task in manifest["tasks"])
    assert all("claim Telegram or Pages delivery completed" in task["prompt"] for task in manifest["tasks"])
    assert all("balanced_external" in task["prompt"] for task in manifest["tasks"])
    assert all("publish" in task["prompt"] for task in manifest["tasks"])
    market_tasks = [task for task in manifest["tasks"] if task["surface"] in {"kr", "us"}]
    assert all("tradingagents.work handoff" in task["prompt"] for task in market_tasks)
    youtube = next(task for task in manifest["tasks"] if task["surface"] == "youtube")
    prism = next(task for task in manifest["tasks"] if task["surface"] == "prism")
    assert "BYMINUTE=30" in youtube["rrule"]
    assert "BYMINUTE=35" in prism["rrule"]


def test_work_skill_and_operations_doc_state_local_and_mobile_delivery_boundaries():
    skill = Path(".agents/skills/tradingagents-daily-investment-work/SKILL.md").read_text(
        encoding="utf-8"
    )
    operations = Path("Docs/chatgpt_work_migration_ko.md").read_text(encoding="utf-8")

    assert "ChatGPT web Scheduled tasks" in skill
    assert "cannot directly read this computer's folder" in skill
    assert "current.universe_coverage" in skill
    assert "Never claim external delivery without its receipt" in skill
    assert "Strategy Pages are plaintext by user choice" in skill
    assert "account identifiers, credentials" in skill
    assert "prepare → write Markdown and structured JSON → publish → acknowledge → KR/US Pages handoff" in skill
    assert "python -m tradingagents.work handoff" in skill
    assert "work-reports/<surface>/latest.json" in skill
    assert "--report-sha256 <report_sha256>" in skill
    assert "canonical acknowledgement ledger" in skill
    assert "https://help.openai.com/en/articles/20001275/" in operations
    assert (
        "https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt"
        in operations
    )
    assert "Scheduled Tasks는 공식적으로 Pro 모델을 지원하지 않는다" in operations
    assert "https://learn.chatgpt.com/docs/remote-connections" in operations
    assert "Plaintext 전략 Pages" in operations
    assert "tradingagents.work-report/v1" in operations
    assert "외부 GitHub workflow가 임의의 개인 ChatGPT 대화에 결과를 주입" in operations
