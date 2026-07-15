from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from tradingagents.work import packet as work_packet
from tradingagents.work.packet import WORK_SCHEMA, build_surface_packet
from tradingagents.work.runtime import WorkRuntime, WorkRuntimeError
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
    discovery = [f"SCAN{i}" for i in range(8)]
    rows = [
        {"ticker": "HELD", "is_held": True, "quality": {}},
        *({"ticker": ticker, "is_held": False, "quality": {}} for ticker in watchlist),
        *({"ticker": ticker, "is_held": False, "quality": {}} for ticker in discovery),
    ]

    compact = work_packet.compact_decision_bundle(
        {"strategy_table": rows, "benchmark_context": {}},
        required_watchlist_tickers=watchlist,
        max_new_candidates=5,
    )

    transmitted = [row["ticker"] for row in compact["strategy_table"]]
    scope = compact["transmission_scope"]
    assert transmitted == ["HELD", *watchlist, *discovery[:5]]
    assert scope["all_holdings_included"] is True
    assert scope["all_required_watchlist_included"] is True
    assert scope["required_watchlist_ticker_count"] == len(watchlist)
    assert scope["transmitted_required_watchlist_count"] == len(watchlist)
    assert scope["scanner_candidate_limit"] == 5
    assert scope["omitted_nonheld_ticker_count"] == 3


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
    ack = runtime.acknowledge("us", first["event_id"], now=datetime(2026, 7, 14, 14, 6, tzinfo=timezone.utc))
    noop = runtime.prepare("us", **kwargs)

    assert first["result"] == "NEW"
    assert resumed["result"] == "RESUME"
    assert ack["status"] == "rendered"
    assert noop["result"] == "NOOP"
    assert Path(first["packet_path"]).is_file()
    assert runtime.ledger_path.read_text(encoding="utf-8").count("\n") == 4


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
    runtime.state_path.write_text("{broken", encoding="utf-8")

    try:
        runtime.status()
    except WorkRuntimeError as exc:
        assert "Invalid canonical Work state" in str(exc)
    else:
        raise AssertionError("corrupt canonical Work state must fail closed")

    recovered = runtime.recover("kr", prepared["event_id"], packet["source_sha256"], state_revision=7)
    assert recovered["status"] == "recovered_visible_receipt"
    assert recovered["state_revision"] == 7
    assert runtime.status("kr")["state"]["last_acked_event_id"] == prepared["event_id"]


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
        assert "MOBILE_HANDOFF" in text
        assert "전송·게시 완료를 주장" in text
        assert "WORK_RECEIPT" in text
        assert "비신뢰" in text


def test_all_work_prompts_fail_closed_on_stale_data_and_do_not_claim_mobile_delivery():
    for surface in ("kr", "us", "youtube", "prism"):
        text = work_packet.prompt_text(surface)
        assert "COVERAGE_RECEIPT" in text
        assert "MOBILE_HANDOFF" in text
        assert "PENDING_EXTERNAL_VERIFICATION" in text
        assert "복호화 키를 출력하지 않는다" in text
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
    assert boundary["task_must_not_claim_external_delivery"] is True
    assert {task["surface"] for task in manifest["tasks"]} == {"kr", "us", "youtube", "prism"}
    assert all("Chrome" in task["prompt"] or "ChatGPT web" in task["prompt"] for task in manifest["tasks"])
    assert all("COVERAGE_RECEIPT" in task["prompt"] for task in manifest["tasks"])
    assert all("MOBILE_HANDOFF" in task["prompt"] for task in manifest["tasks"])
    assert all("never claim Telegram or Pages delivery completed" in task["prompt"] for task in manifest["tasks"])
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
    assert (
        "Never print, log, persist in Pages, or place `MOBILE_DASHBOARD_KEY` "
        "in a query string or server-visible request"
    ) in skill
    assert "Telegram private link's URL fragment" in skill
    assert "https://help.openai.com/en/articles/20001275/" in operations
    assert (
        "https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt"
        in operations
    )
    assert "Scheduled Tasks는 공식적으로 Pro 모델을 지원하지 않는다" in operations
    assert "https://learn.chatgpt.com/docs/remote-connections" in operations
    assert "AES-256-GCM" in operations
    assert "#key=..." in operations
    assert "외부 GitHub workflow가 임의의 개인 ChatGPT 대화에 결과를 주입" in operations
