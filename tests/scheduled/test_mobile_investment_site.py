from __future__ import annotations

import json
from pathlib import Path

import pytest

from tradingagents.scheduled.config import SiteSettings
from tradingagents.scheduled.mobile_site import (
    MOBILE_SCHEMA,
    STRATEGY_SCHEMA,
    assert_public_payload_safe,
    assert_strategy_payload_safe,
    build_mobile_site,
    sanitize_public_decision_bundle,
    _load_latest_work_report,
    _private_market_payload,
    _public_quality,
    _strip_strategy_identifiers,
)
from tradingagents.scheduled.site import _public_ticker_summaries, build_site
from tradingagents.work.packet import _compact_public_market_bundle, sha256_json
from tradingagents.work.runtime import _report_policy


def _packet(market: str, *, public: bool) -> dict:
    public_row = {
        "ticker": "PUBLIC",
        "display_name": "Public candidate",
        "last_price": 123.45,
        "market_data_asof": "2026-07-16T09:00:00+09:00",
        "vwap_position_ko": "VWAP 위",
        "relative_volume": 1.2,
        "sync_summary_ko": "지수 동조",
        "data_status_ko": "현재 데이터",
        "quality": {
            "row_mode": "CONDITIONAL",
            "row_valid_until": "2026-07-16T09:30:00+09:00",
            "generated_in_current_run": True,
            "execution_ready": False,
            "conditional_strategy_ready": True,
        },
    }
    rows = [public_row]
    current = {
        "run_id": f"run-{market}",
        "started_at": "2026-07-16T09:00:00+09:00",
        "bundle": {
            "run_id": f"run-{market}",
            "market": market.upper(),
            "analysis_source_run_id": f"run-{market}",
            "execution_source_run_id": f"run-{market}",
            "quality": {
                "decision_ready": False,
                "conditional_strategy_ready": True,
                "total_rows": 1,
            },
            "strategy_table": rows,
            "transmission_scope": {"all_holdings_included": not public},
        },
        "universe_coverage": {
            "status": "COMPLETE",
            "complete": True,
            "source_run_id": f"run-{market}",
            "ticker_universe_mode": "config_only",
            "expected_holding_count": 0,
            "missing_holding_count": 0,
            "expected_watchlist_count": 1,
            "missing_watchlist_count": 0,
            "expected_analysis_count": 1,
            "missing_analysis_count": 0,
            "analysis_total_count": 1,
            "analysis_successful_count": 1,
            "analysis_failed_count": 0,
        },
    }
    if not public:
        held = {
            **public_row,
            "ticker": "SECRET.HOLD",
            "display_name": "Private holding",
            "is_held": True,
            "strategy_code": "REDUCE",
            "strategy_ko": "리스크 축소",
            "execution_condition_ko": "조건 충족 시 축소",
            "risk_condition_ko": "무효화 가격",
        }
        current["bundle"]["strategy_table"] = [held, public_row]
        current["bundle"]["quality"]["total_rows"] = 2
        current["universe_coverage"].update(
            {
                "expected_holding_count": 1,
                "expected_analysis_count": 2,
                "analysis_total_count": 2,
                "analysis_successful_count": 2,
            }
        )
        current["private_portfolio_overlay"] = {
            "privacy": "LOCAL_ONLY_DO_NOT_PUBLISH",
            "actions": [
                {
                    "canonical_ticker": "SECRET.HOLD",
                    "confidence": 0.73,
                    "action_now": "REDUCE_RISK",
                    "delta_krw_now": -987654321,
                    "target_weight_now": 0.12,
                    "action_if_triggered": "REDUCE_IF_TRIGGERED",
                    "trigger_conditions": ["VWAP 하향 이탈", "거래량 1.5배 이상"],
                    "risk_action": "STOP_LOSS_IF_TRIGGERED",
                    "risk_action_level": "종가 기준 손실 제한",
                    "position_metrics": {
                        "current_weight": 0.18,
                        "account_id": "RAW-ACCOUNT-123456",
                        "cano": "12345678",
                        "order_reference": "ORDER-PRIVATE-999",
                    },
                }
            ],
        }
    return {
        "surface": market,
        "event_id": f"{market}:event",
        "source_sha256": f"source-{market}",
        "workflow_contract_sha256": "f" * 64,
        "body": {
            "market": market.upper(),
            "source_health": "OK",
            "report_mode": "MIXED",
            "source": {"run_id": f"run-{market}", "status": "success"},
            "current": current,
            "guardrails": {
                "valid_until": "2026-07-16T09:30:00+09:00",
                "decision_ready": False,
            },
        },
    }


def test_public_bundle_excludes_held_rows_and_portfolio_actions() -> None:
    bundle = {
        "run_id": "run-us",
        "market": "US",
        "quality": {"decision_ready": True, "quality_label_ko": "장중 판단 가능"},
        "strategy_table": [
            {
                "ticker": "SECRET.HOLD",
                "is_held": True,
                "strategy_ko": "보유 유지",
                "action_now": "HOLD",
                "last_price": 10,
            },
            {
                "ticker": "PUBLIC",
                "is_held": False,
                "strategy_ko": "분할매수",
                "execution_condition_ko": "매수 조건",
                "last_price": 20,
                "quality": {"row_mode": "CONDITIONAL"},
            },
        ],
    }

    public = sanitize_public_decision_bundle(bundle)
    serialized = json.dumps(public, ensure_ascii=False)

    assert [row["ticker"] for row in public["strategy_table"]] == ["PUBLIC"]
    assert "SECRET.HOLD" not in serialized
    assert "is_held" not in serialized
    assert "strategy_ko" not in serialized
    assert "execution_condition_ko" not in serialized
    assert_public_payload_safe(public)


def test_public_safety_check_fails_closed_on_nested_private_key() -> None:
    with pytest.raises(ValueError, match="Forbidden private key"):
        assert_public_payload_safe({"markets": {"kr": {"rows": [{"is_held": True}]}}})


def test_legacy_manifest_without_public_universe_provenance_fails_closed() -> None:
    manifest = {
        "tickers": [
            {"ticker": "PUBLIC-UNKNOWN", "status": "success"},
            {"ticker": "POSSIBLE-HOLDING", "status": "success"},
        ]
    }

    assert _public_ticker_summaries(manifest) == []


def test_public_bundle_keeps_allowed_watchlist_ticker_without_revealing_held_flag() -> None:
    bundle = {
        "strategy_table": [
            {"ticker": "005930.KS", "is_held": True, "last_price": 70000, "strategy_ko": "보유 유지"},
            {"ticker": "SECRET.HOLD", "is_held": True, "last_price": 1},
        ]
    }

    public = sanitize_public_decision_bundle(bundle, allowed_tickers=["005930"])
    serialized = json.dumps(public, ensure_ascii=False)

    assert [row["ticker"] for row in public["strategy_table"]] == ["005930.KS"]
    assert "is_held" not in serialized
    assert "strategy_ko" not in serialized
    assert "SECRET.HOLD" not in serialized


def test_public_mobile_sanitizer_does_not_truncate_safe_watchlist_rows() -> None:
    tickers = [f"PUBLIC{i}" for i in range(8)]
    bundle = {
        "strategy_table": [
            {"ticker": ticker, "is_held": False, "last_price": index + 1}
            for index, ticker in enumerate(tickers)
        ]
    }

    public = sanitize_public_decision_bundle(bundle, allowed_tickers=tickers)

    assert [row["ticker"] for row in public["strategy_table"]] == tickers

    packet_bundle = _compact_public_market_bundle(bundle, allowed_tickers=tickers)
    assert [row["ticker"] for row in packet_bundle["strategy_table"]] == tickers


def test_strategy_safety_check_rejects_nested_raw_account_identifier() -> None:
    with pytest.raises(ValueError, match="Forbidden account identifier"):
        assert_strategy_payload_safe(
            {"markets": {"kr": {"rows": [{"position_metrics": {"account_id": "123-456"}}]}}}
        )


@pytest.mark.parametrize(
    "sensitive_text",
    (
        "CANO 12345678",
        "ODNO=87654321",
        "ACNT_PRDT_CD: 01",
        "order reference ORDER-1234",
        "client id CLIENT-1234",
        "access token alphabetic-secret",
        "token: alphabetic-secret",
        "api_key=alphabetic-secret",
        r"C:\Users\investor\private\receipt.json",
        r"C:\TradingAgentsData\automation-logs\private.log",
    ),
)
def test_strategy_safety_scans_and_redacts_sensitive_string_values(sensitive_text: str) -> None:
    with pytest.raises(ValueError, match="Forbidden identifier value"):
        assert_strategy_payload_safe({"rationale": sensitive_text})
    sanitized = _strip_strategy_identifiers({"rationale": sensitive_text})
    serialized = json.dumps(sanitized, ensure_ascii=False)
    assert sensitive_text not in serialized
    assert_strategy_payload_safe(sanitized)


def test_strategy_string_scanner_avoids_general_account_status_false_positive() -> None:
    payload = {"rationale": "account id unavailable"}
    assert _strip_strategy_identifiers(payload) == payload
    assert_strategy_payload_safe(payload)


@pytest.mark.parametrize(
    "identifier_key",
    (
        "order_id",
        "order_no",
        "order_number",
        "order_reference",
        "odno",
        "cano",
        "acnt_prdt_cd",
        "custtype",
        "client_id",
    ),
)
def test_strategy_safety_check_rejects_raw_order_and_kis_identifiers(identifier_key: str) -> None:
    with pytest.raises(ValueError, match="Forbidden account identifier"):
        assert_strategy_payload_safe(
            {"markets": {"kr": {"integrated_report": {identifier_key: "RAW-PRIVATE-1234"}}}}
        )


def test_private_action_matches_kr_broker_and_canonical_ticker_aliases() -> None:
    packet = _packet("kr", public=False)
    packet["body"]["current"]["bundle"]["strategy_table"][0]["ticker"] = "005930.KS"
    packet["body"]["current"]["private_portfolio_overlay"]["actions"][0]["canonical_ticker"] = "005930"

    market = _private_market_payload(packet)

    assert market["rows"][0]["portfolio_action"]["action_now"] == "REDUCE_RISK"


def _write_valid_work_report(
    archive: Path,
    *,
    market: str,
    event_id: str,
    source_sha256: str,
    source_run_id: str,
    tickers: list[str],
) -> dict:
    strategies = []
    for index, ticker in enumerate(tickers, start=1):
        strategies.append(
            {
                "ticker": ticker,
                "display_name": "Private holding" if index == 1 else "Public candidate",
                "rank": index,
                "portfolio_role": "HOLDING" if index == 1 else "WATCHLIST",
                "thesis": {
                    "stance": "REDUCE" if index == 1 else "RESEARCH",
                    "confidence": 0.73,
                    "rationale": "리스크 대비 비중과 진입 조건을 점검",
                    "entry_conditions": ["VWAP 하향 이탈"],
                    "invalidation_conditions": ["종가가 무효화 가격 하회"],
                    "invalidation_action": (
                        "보유 비중을 절반 축소하고 다음 정규장에서 재평가"
                        if index == 1
                        else "신규 주문을 보류하고 실시간 가격·거래량 확인 후 재분석"
                    ),
                    "horizon": "다음 정규장 마감까지",
                    "position_sizing": "기존 위험 한도 내",
                },
                "execution": {
                    "readiness": "NEEDS_LIVE_RECHECK",
                    "required_rechecks": ["실시간 가격 재확인"],
                },
                "source_contributions": [
                    {
                        "source": "youtube",
                        "summary": "강세 근거",
                        "execution_gate_override": False,
                    }
                ],
            }
        )
    structured = {
        "binding": {
            "surface": market,
            "event_id": event_id,
            "source_sha256": source_sha256,
        },
        "title": f"{market.upper()} 통합 투자 전략",
        "generated_at": "2026-07-16T09:05:00+09:00",
        "as_of": "2026-07-16T09:05:00+09:00",
        "summary": "분석 시점 전략을 유지하고 주문 전에 가격을 재확인",
        "top_actions": [
            {"ticker": ticker, "readiness": "NEEDS_LIVE_RECHECK"}
            for ticker in tickers
        ],
        "strategies": strategies,
        "coverage_receipt": {"status": "COMPLETE", "source_run_id": source_run_id},
        "source_summary": {"youtube": "반영", "prism": "반영", market: "핵심"},
        "next_checkpoint": "다음 시장 데이터 갱신 시점",
    }
    material = {
        "schema": "tradingagents.work-report/v1",
        "surface": market,
        "event_id": event_id,
        "source_sha256": source_sha256,
        "prompt_contract_version": "mobile-test-v1",
        "workflow_contract_sha256": "f" * 64,
        "policy": _report_policy(),
        "report_markdown": "# 통합 전략\n\n분석 논리는 유지하되 주문 전 실시간 재확인이 필요합니다.",
        "structured_report": structured,
    }
    report_sha256 = sha256_json(material)
    report = {
        **material,
        "report_id": f"{market}:{report_sha256[:32]}",
        "report_sha256": report_sha256,
        "published_at": "2026-07-16T09:05:00+09:00",
    }
    report_dir = archive / "work-reports" / market
    event_path = report_dir / "events" / f"{report_sha256}.json"
    event_path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    event_path.write_text(serialized, encoding="utf-8")
    (report_dir / "latest.json").write_text(serialized, encoding="utf-8")
    return report


def test_mobile_build_writes_plaintext_action_strategy_without_raw_account_ids(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_packet(market: str, **kwargs) -> dict:
        return _packet(market, public=bool(kwargs.get("public")))

    monkeypatch.setattr("tradingagents.scheduled.mobile_site.build_surface_packet", fake_packet)
    archive = tmp_path / "archive"
    _write_valid_work_report(
        archive,
        market="kr",
        event_id="kr:event",
        source_sha256="source-kr",
        source_run_id="run-kr",
        tickers=["SECRET.HOLD", "PUBLIC"],
    )
    mobile = tmp_path / "site" / "mobile"
    mobile.mkdir(parents=True)
    (mobile / "private.enc.json").write_text("legacy", encoding="utf-8")
    (mobile / "private.json").write_text("legacy", encoding="utf-8")

    status = build_mobile_site(site_dir=tmp_path / "site", archive_dir=archive)
    mobile = tmp_path / "site" / "mobile"
    public_payload = json.loads((mobile / "public.json").read_text(encoding="utf-8"))
    strategy_payload = json.loads((mobile / "strategy.json").read_text(encoding="utf-8"))
    serialized_strategy = json.dumps(strategy_payload, ensure_ascii=False)

    assert status["private_dashboard"]["enabled"] is True
    assert status["private_dashboard"]["storage"] == "PLAINTEXT_ACTION_DATA"
    assert status["strategy_payload_url"] == "mobile/strategy.json"
    assert public_payload["schema"] == MOBILE_SCHEMA
    assert "SECRET.HOLD" not in json.dumps(public_payload, ensure_ascii=False)
    assert strategy_payload["schema"] == STRATEGY_SCHEMA
    assert strategy_payload["markets"]["kr"]["rows"][0]["ticker"] == "SECRET.HOLD"
    assert strategy_payload["markets"]["kr"]["rows"][0]["universe_role"] == "HOLDING"
    action = strategy_payload["markets"]["kr"]["rows"][0]["portfolio_action"]
    assert action["delta_krw_now"] == -987654321
    assert action["trigger_conditions"] == ["VWAP 하향 이탈", "거래량 1.5배 이상"]
    assert "account_id" not in action["position_metrics"]
    assert "cano" not in action["position_metrics"]
    assert "order_reference" not in action["position_metrics"]
    assert strategy_payload["markets"]["kr"]["portfolio_action_count"] == 1
    assert strategy_payload["markets"]["kr"]["manifest_status"] == "success"
    assert strategy_payload["markets"]["kr"]["decision_ready"] is False
    assert strategy_payload["markets"]["kr"]["universe_coverage"]["expected_analysis_count"] == 2
    assert strategy_payload["markets"]["kr"]["provenance"] == {
        "surface_run_id": "run-kr",
        "manifest_run_id": "run-kr",
        "universe_source_run_id": "run-kr",
        "decision_bundle_run_id": "run-kr",
        "analysis_source_run_id": "run-kr",
        "execution_source_run_id": "run-kr",
    }
    report = strategy_payload["markets"]["kr"]["integrated_report"]
    assert report["structured_report"]["strategies"][0]["thesis"]["stance"] == "REDUCE"
    assert report["structured_report"]["strategies"][0]["thesis"]["invalidation_action"] == (
        "보유 비중을 절반 축소하고 다음 정규장에서 재평가"
    )
    assert report["lineage"]["status"] == "CURRENT_PACKET"
    assert "source_sha256" not in serialized_strategy
    assert "report_sha256" not in serialized_strategy
    assert "RAW-ACCOUNT" not in serialized_strategy
    assert "BLOCKED_STALE" not in serialized_strategy
    assert "현재 조건부 실행 가능: 없음" not in serialized_strategy
    assert "주문 전 실시간 재확인" in report["report_markdown"]
    assert _load_latest_work_report(archive, "kr")["report_id"].startswith("kr:")
    assert_strategy_payload_safe(strategy_payload)

    assert not (mobile / "private.enc.json").exists()
    assert not (mobile / "private.json").exists()
    assert b"viewport-fit=cover" in (mobile / "index.html").read_bytes()
    assert b"data-valid-until" in (mobile / "index.html").read_bytes()
    mobile_css = (mobile / "mobile.css").read_text(encoding="utf-8")
    assert "env(safe-area-inset-top)" in mobile_css
    assert "overflow-wrap: anywhere" in mobile_css
    assert "main { width: 100%; max-width: 760px; min-width: 0;" in mobile_css
    assert "grid-template-columns: repeat(2, minmax(0, 1fr))" in mobile_css
    assert ".cards { display: grid; grid-template-columns: minmax(0, 1fr);" in mobile_css
    assert ".market-panel, #private-root { min-width: 0; max-width: 100%; }" in mobile_css
    private_js = (mobile / "private.js").read_text(encoding="utf-8")
    private_html = (mobile / "private.html").read_text(encoding="utf-8")
    assert "리스크 축소" in private_js
    assert "currency: 'KRW'" in private_js
    assert "style: 'percent'" in private_js
    assert "fetch('strategy.json'" in private_js
    assert "crypto.subtle" not in private_js
    assert "AES-GCM" not in private_js
    assert "private.enc.json" not in private_js
    assert "분석 시점 결론" in private_js
    assert "확인할 진입·축소 조건" in private_js
    assert "조건 충족 후 행동" in private_js
    assert "무효화·손실 제한 조건" in private_js
    assert "무효화 시 행동" in private_js
    assert "humanPlan(thesis.invalidation_action || workExecution.risk_action)" in private_js
    assert "row.execution_condition_ko" in private_js
    assert "action.trigger_conditions" in private_js
    assert "const analysisAction = (hasWork ? workConclusion : baseConclusion)" in private_js
    assert "const entryCondition = (hasWork ? workEntryConditions : baseEntryConditions)" in private_js
    assert "distinctConditions(...values).slice(0, 3)" in private_js
    assert "기본 분석·전체 조건 보기" in private_js
    assert "별도 단계 실행 계획 없음" not in private_js
    assert "CUSTOM: '세부 실행 계획 확인'" in private_js
    assert "sizingText(action.delta_krw_if_triggered, action.target_weight_if_triggered)" in private_js
    assert "text.split(/\\s+(?:\\/|\\||·)\\s+|\\n+/)" in private_js
    assert "const baseConclusion = action.action_now ? actionLabel(action.action_now)" in private_js
    assert "조건 정보 없음" in private_js
    assert "행동 계획 정보 없음" in private_js
    assert "slice(0, Math.min(3, ranked.length))" in private_js
    assert "topActions.slice(0, 3)" in private_js
    assert "(strategy.thesis || {}).stance" in private_js
    assert "strategy.rank ?? row.portfolio_priority" in private_js
    assert "현재 실행 가능: 없음" not in private_js
    assert "BLOCKED_STALE" not in private_js
    assert "AES" not in private_html
    assert "복호화" not in private_html
    assert "guardrails.expired_at_build" in private_js
    assert "!Number.isFinite(marketValid)" in private_js
    assert "!Number.isFinite(valid)" in private_js
    assert "sourceHealth !== 'OK'" in private_js
    assert "coverage.status === 'COMPLETE'" in private_js
    assert "accountReady" in private_js
    assert "quality.decision_ready === true" in private_js
    assert "boundRunIds.every((value) => value === runId)" in private_js
    for readiness, investor_code in {
        "READY_NOW": "READY",
        "WAIT_FOR_TRIGGER": "CONDITIONAL",
        "NEEDS_LIVE_RECHECK": "RECHECK",
        "MARKET_CLOSED": "RECHECK",
        "DATA_OUTAGE": "RECHECK",
        "RESEARCH_ONLY": "RESEARCH",
    }.items():
        assert f"{readiness}: {{code: '{investor_code}'" in private_js
    assert "readinessSeverity(workGate.code) >= readinessSeverity(base.code)" in private_js
    assert "알 수 없는 Work 준비 상태" in private_js
    assert "function marketHealth(item, rows)" in private_js
    assert "className: 'missing', label: '전략 행 없음'" in private_js
    assert "className: 'degraded', label: expired ? '데이터 만료 · 재확인'" in private_js
    assert "health health-neutral" in private_js
    assert "health health-${esc(health.className)}" in private_js
    assert '<meta name="robots" content="noindex,nofollow,noarchive">' in private_html
    assert "requestedRun" in private_js


def test_expired_machine_state_is_normalized_out_of_every_mobile_artifact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def expired_packet(market: str, **kwargs) -> dict:
        packet = _packet(market, public=bool(kwargs.get("public")))
        rows = packet["body"]["current"]["bundle"]["strategy_table"]
        for row in rows:
            row["quality"] = {
                **(row.get("quality") or {}),
                "row_mode": "BLOCKED_STALE",
                "expired_at_build": True,
                "row_valid_until": "2026-07-16T08:30:00+09:00",
            }
        if not kwargs.get("public"):
            packet["body"]["current"]["private_portfolio_overlay"]["actions"][0][
                "execution_feasibility_now"
            ] = "blocked_stale_or_degraded_data"
        return packet

    monkeypatch.setattr(
        "tradingagents.scheduled.mobile_site.build_surface_packet",
        expired_packet,
    )
    mobile = tmp_path / "site" / "mobile"
    build_mobile_site(site_dir=tmp_path / "site", archive_dir=tmp_path / "archive")

    artifacts = [path for path in mobile.rglob("*") if path.is_file()]
    assert artifacts
    assert all(b"blocked_stale" not in path.read_bytes().lower() for path in artifacts)
    public = json.loads((mobile / "public.json").read_text(encoding="utf-8"))
    strategy = json.loads((mobile / "strategy.json").read_text(encoding="utf-8"))
    public_quality = public["markets"]["kr"]["rows"][0]["quality"]
    assert "row_mode" not in public_quality
    assert public_quality["investor_state"] == "RECHECK"
    assert public_quality["investor_label"] == "주문 전 재확인"
    assert strategy["markets"]["kr"]["rows"][0]["quality"]["investor_state"] == "RECHECK"
    assert (
        strategy["markets"]["kr"]["rows"][0]["portfolio_action"][
            "execution_feasibility_now"
        ]
        == "RECHECK_REQUIRED_or_degraded_data"
    )


def test_validated_work_conclusion_is_authoritative_over_conflicting_base_action(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def conflicting_packet(market: str, **kwargs) -> dict:
        packet = _packet(market, public=bool(kwargs.get("public")))
        if not kwargs.get("public"):
            held = packet["body"]["current"]["bundle"]["strategy_table"][0]
            held["strategy_code"] = "BUY"
            held["strategy_ko"] = "분할매수"
            packet["body"]["current"]["private_portfolio_overlay"]["actions"][0][
                "action_now"
            ] = "BUY_NOW"
        return packet

    monkeypatch.setattr(
        "tradingagents.scheduled.mobile_site.build_surface_packet",
        conflicting_packet,
    )
    archive = tmp_path / "archive"
    _write_valid_work_report(
        archive,
        market="kr",
        event_id="kr:event",
        source_sha256="source-kr",
        source_run_id="run-kr",
        tickers=["SECRET.HOLD", "PUBLIC"],
    )
    build_mobile_site(site_dir=tmp_path / "site", archive_dir=archive)
    mobile = tmp_path / "site" / "mobile"
    strategy = json.loads((mobile / "strategy.json").read_text(encoding="utf-8"))
    market = strategy["markets"]["kr"]
    assert market["rows"][0]["portfolio_action"]["action_now"] == "BUY_NOW"
    assert market["integrated_report"]["structured_report"]["strategies"][0]["thesis"][
        "stance"
    ] == "REDUCE"
    private_js = (mobile / "private.js").read_text(encoding="utf-8")
    assert "const analysisAction = (hasWork ? workConclusion : baseConclusion)" in private_js
    assert "const entryCondition = (hasWork ? workEntryConditions : baseEntryConditions)" in private_js
    assert "기본 분석 결론" in private_js


def test_mobile_quality_exposes_investor_state_instead_of_machine_state() -> None:
    quality = _public_quality({"row_mode": "BLOCKED_STALE", "expired_at_build": True})
    assert "row_mode" not in quality
    assert quality["investor_state"] == "RECHECK"
    assert quality["investor_label"] == "주문 전 재확인"


def test_mobile_work_report_requires_matching_content_addressed_event(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    report = _write_valid_work_report(
        archive,
        market="kr",
        event_id="kr:event",
        source_sha256="source-kr",
        source_run_id="run-kr",
        tickers=["SECRET.HOLD", "PUBLIC"],
    )
    event_path = (
        archive
        / "work-reports"
        / "kr"
        / "events"
        / f"{report['report_sha256']}.json"
    )
    event_path.unlink()

    assert _load_latest_work_report(
        archive,
        "kr",
        current_packet=_packet("kr", public=False),
    ) == {}


def test_mobile_separates_unrelated_work_report_as_past_reference(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "tradingagents.scheduled.mobile_site.build_surface_packet",
        lambda market, **kwargs: _packet(market, public=bool(kwargs.get("public"))),
    )
    archive = tmp_path / "archive"
    _write_valid_work_report(
        archive,
        market="kr",
        event_id="kr:previous-event",
        source_sha256="previous-source",
        source_run_id="previous-run",
        tickers=["SECRET.HOLD", "PUBLIC"],
    )

    build_mobile_site(site_dir=tmp_path / "site", archive_dir=archive)
    strategy = json.loads(
        (tmp_path / "site" / "mobile" / "strategy.json").read_text(encoding="utf-8")
    )
    market = strategy["markets"]["kr"]

    assert "integrated_report" not in market
    assert market["reference_report"]["lineage"]["status"] == "PAST_REFERENCE"
    assert market["reference_report"]["lineage"]["current_action_cards_enriched"] is False
    private_js = (tmp_path / "site" / "mobile" / "private.js").read_text(encoding="utf-8")
    assert "현재 카드 순위·실행 판단에는 반영하지 않았습니다" in private_js
    assert "item.integrated_report || {}" in private_js


def test_mobile_accepts_report_bound_to_current_analysis_source_lineage(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    _write_valid_work_report(
        archive,
        market="kr",
        event_id="kr:prior-overlay-event",
        source_sha256="prior-overlay-source",
        source_run_id="run-kr",
        tickers=["SECRET.HOLD", "PUBLIC"],
    )

    report = _load_latest_work_report(
        archive,
        "kr",
        current_packet=_packet("kr", public=False),
    )

    assert report["lineage"]["status"] == "CURRENT_ANALYSIS_LINEAGE"
    assert report["lineage"]["ticker_coverage_matches"] is True
    assert report["analysis_only"] is True
    assert "주문 전 실시간 재확인" in report["report_markdown"]
    assert report["structured_report"]["top_actions"]
    assert all(
        "execution" not in strategy
        for strategy in report["structured_report"]["strategies"]
    )
    assert report["structured_report"]["strategies"][0]["thesis"]["stance"] == "REDUCE"


def test_mobile_does_not_enrich_current_cards_across_workflow_contract_change(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    _write_valid_work_report(
        archive,
        market="kr",
        event_id="kr:event",
        source_sha256="source-kr",
        source_run_id="run-kr",
        tickers=["SECRET.HOLD", "PUBLIC"],
    )
    packet = _packet("kr", public=False)
    packet["workflow_contract_sha256"] = "e" * 64

    report = _load_latest_work_report(archive, "kr", current_packet=packet)

    assert report["lineage"]["status"] == "PAST_REFERENCE"
    assert report["lineage"]["reason"] == "workflow_contract_mismatch"
    assert report["lineage"]["current_action_cards_enriched"] is False


def test_mobile_build_needs_no_key_when_private_actions_exist(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "tradingagents.scheduled.mobile_site.build_surface_packet",
        lambda market, **kwargs: _packet(market, public=bool(kwargs.get("public"))),
    )
    status = build_mobile_site(site_dir=tmp_path / "site", archive_dir=tmp_path / "archive")

    assert status["private_dashboard"]["enabled"] is True
    assert (tmp_path / "site" / "mobile" / "strategy.json").exists()
    assert not (tmp_path / "site" / "mobile" / "private.enc.json").exists()


def test_mobile_research_only_build_still_publishes_strategy_view(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def research_packet(market: str, **kwargs) -> dict:
        packet = _packet(market, public=bool(kwargs.get("public")))
        packet["body"]["current"].pop("private_portfolio_overlay", None)
        for row in packet["body"]["current"]["bundle"]["strategy_table"]:
            row.pop("is_held", None)
        return packet

    monkeypatch.setattr("tradingagents.scheduled.mobile_site.build_surface_packet", research_packet)
    status = build_mobile_site(site_dir=tmp_path / "site", archive_dir=tmp_path / "archive")

    assert status["private_dashboard"]["enabled"] is True
    assert (tmp_path / "site" / "mobile" / "strategy.json").exists()
    assert not (tmp_path / "site" / "mobile" / "private.enc.json").exists()


def test_full_site_never_copies_raw_private_or_execution_artifacts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    archive = tmp_path / "archive"
    site = tmp_path / "site"
    run_id = "20260716T090000_privacy-us"
    run_dir = archive / "runs" / "2026" / run_id
    ticker_report = run_dir / "tickers" / "AAPL" / "report" / "complete_report.md"
    private_dir = run_dir / "portfolio-private"
    execution_dir = run_dir / "execution"
    ticker_report.parent.mkdir(parents=True)
    private_dir.mkdir(parents=True)
    execution_dir.mkdir(parents=True)
    ticker_report.write_text("# Public AAPL research\n", encoding="utf-8")
    secret_marker = "PRIVATE-ACCOUNT-987654321"
    (private_dir / "status.json").write_text(json.dumps({"status": "success", "profile": "private"}), encoding="utf-8")
    (private_dir / "portfolio_report.json").write_text(json.dumps({"action_now": secret_marker}), encoding="utf-8")
    (private_dir / "portfolio_report.md").write_text(secret_marker, encoding="utf-8")
    (private_dir / "summary_card.svg").write_text(f"<svg><text>{secret_marker}</text></svg>", encoding="utf-8")
    (execution_dir / "chatgpt_execution_context.json").write_text(json.dumps({"private": secret_marker}), encoding="utf-8")
    decision_bundle = {
        "run_id": run_id,
        "market": "US",
        "quality": {"decision_ready": True},
        "strategy_table": [
            {"ticker": "SECRET.HOLD", "is_held": True, "strategy_ko": "보유 유지"},
            {"ticker": "AAPL", "is_held": True, "last_price": 10, "quality": {"row_mode": "CONDITIONAL"}},
        ],
    }
    (run_dir / "decision_bundle_v2.json").write_text(json.dumps(decision_bundle), encoding="utf-8")
    manifest = {
        "version": 1,
        "run_id": run_id,
        "status": "success",
        "started_at": "2026-07-16T09:00:00+09:00",
        "summary": {"total_tickers": 1, "successful_tickers": 1, "failed_tickers": 0},
        "settings": {"output_language": "Korean", "market": "US", "run_mode": "full"},
        "active_universe": {
            "expected_watchlist_tickers": ["AAPL"],
            "scanner_candidates": [],
            "expected_holding_tickers": ["SECRET.HOLD"],
            "missing_holding_tickers": ["FRESH.NEW.PRIVATE"],
            "missing_analysis_tickers": ["ANALYSIS.MISSING.PRIVATE"],
            "fresh_snapshot_drift": {
                "status": "VERIFIED",
                "added_holding_tickers": ["DRIFT.ADDED.PRIVATE"],
                "removed_holding_tickers": ["DRIFT.REMOVED.PRIVATE"],
            },
        },
        "portfolio": {
            "status": "success",
            "profile": "private",
            "private_coverage_snapshot": {
                "holding_set_complete": True,
                "canonical_holding_tickers": ["SNAPSHOT.HOLD.PRIVATE"],
            },
            "artifacts": {
                "portfolio_report_json": "portfolio-private/portfolio_report.json",
                "portfolio_report_md": "portfolio-private/portfolio_report.md",
                "summary_card_svg": "portfolio-private/summary_card.svg",
            },
        },
        "execution": {
            "artifacts": {"chatgpt_execution_context_json": "execution/chatgpt_execution_context.json"},
            "overlay_phase": {"selected_checkpoints": []},
            "notes": ["RAW-EXECUTION-NOTE-SECRET.HOLD"],
        },
        "warnings": ["RAW-WARNING-PRIVATE-TICKER-SECRET.HOLD"],
        "decision_bundle": {
            "decision_ready": True,
            "artifacts": {"decision_bundle_v2_json": "decision_bundle_v2.json"},
        },
        "tickers": [
            {
                "ticker": "AAPL",
                "status": "success",
                "analysis_date": "2026-07-16",
                "trade_date": "2026-07-16",
                "decision": {"action": "HOLD", "confidence": 0.5},
                "error": "PRIVATE-ERROR-C:/Users/JY/account-SECRET.HOLD",
                "is_held": True,
                "portfolio_action": {
                    "action_now": "REDUCE_NOW",
                    "rationale": "PUBLIC-TICKER-PRIVATE-ACTION-MARKER",
                    "delta_krw_now": -123456789,
                },
                "action_lift_audit": {
                    "lift_status": "ACTION_LIFT_FAILURE",
                    "next_valid_action": "PUBLIC-TICKER-PRIVATE-LIFT-MARKER",
                },
                "artifacts": {"report_markdown": "tickers/AAPL/report/complete_report.md"},
            },
            {
                "ticker": "SECRET.HOLD",
                "status": "success",
                "analysis_date": "2026-07-16",
                "trade_date": "2026-07-16",
                "decision": {"action": "HOLD", "confidence": 0.5},
                "artifacts": {},
            },
        ],
    }
    (run_dir / "run.json").write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr("tradingagents.work.site.build_work_site", lambda **_kwargs: {})

    build_site(archive, site, SiteSettings(title="TA", subtitle="Daily"))

    relative_files = {path.relative_to(site).as_posix() for path in site.rglob("*") if path.is_file()}
    forbidden_names = {
        "portfolio_report.json",
        "portfolio_report.md",
        "summary_card.svg",
        "strategy_table_ko.md",
        "decision_bundle_v2.json",
        "chatgpt_execution_context.json",
    }
    assert not {Path(name).name for name in relative_files} & forbidden_names
    all_bytes = b"\n".join(path.read_bytes() for path in site.rglob("*") if path.is_file())
    assert secret_marker.encode() not in all_bytes
    assert b"PUBLIC-TICKER-PRIVATE-ACTION-MARKER" not in all_bytes
    assert b"PUBLIC-TICKER-PRIVATE-LIFT-MARKER" not in all_bytes
    assert b"123456789" not in all_bytes
    assert b"RAW-WARNING-PRIVATE-TICKER" not in all_bytes
    assert b"RAW-EXECUTION-NOTE" not in all_bytes
    assert b"PRIVATE-ERROR-C:/Users/JY" not in all_bytes
    public_surface_bytes = b"\n".join(
        path.read_bytes()
        for path in site.rglob("*")
        if path.is_file() and path != site / "mobile" / "strategy.json"
    )
    assert b"SECRET.HOLD" not in public_surface_bytes
    for private_ticker_marker in (
        b"FRESH.NEW.PRIVATE",
        b"ANALYSIS.MISSING.PRIVATE",
        b"DRIFT.ADDED.PRIVATE",
        b"DRIFT.REMOVED.PRIVATE",
        b"SNAPSHOT.HOLD.PRIVATE",
    ):
        assert private_ticker_marker not in all_bytes
    assert not (site / "runs" / run_id / "SECRET.HOLD.html").exists()
    assert not (site / "downloads").exists()
    assert "계좌번호와 고객 식별정보는 제외" in (
        site / "runs" / run_id / "portfolio.html"
    ).read_text(encoding="utf-8")
    sanitized_latest = json.loads((site / "latest" / "us" / "decision_bundle.json").read_text(encoding="utf-8"))
    assert [row["ticker"] for row in sanitized_latest["strategy_table"]] == ["AAPL"]
    assert "is_held" not in json.dumps(sanitized_latest)
    feed = json.loads((site / "feed.json").read_text(encoding="utf-8"))
    serialized_feed = json.dumps(feed, ensure_ascii=False)
    assert feed["runs"][0]["ticker_count"] == 1
    assert feed["runs"][0]["summary"]["total_tickers"] == 1
    assert "portfolio" not in feed["runs"][0]
    assert "FRESH.NEW.PRIVATE" not in serialized_feed
    assert "SNAPSHOT.HOLD.PRIVATE" not in serialized_feed
