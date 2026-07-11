from __future__ import annotations

import json
from pathlib import Path

from tradingagents.scheduled.decision_bundle import (
    build_decision_bundle,
    render_strategy_table_markdown,
    select_investor_strategy_rows,
)
from tradingagents.scheduled.site import _publish_latest_decision_bundles


def _live_context(
    *,
    generated: bool = True,
    freshness: str = "LIVE_CHECKPOINT",
    eligibility: str | None = None,
) -> dict:
    return {
        "artifact_type": "chatgpt_execution_context",
        "market": "US",
        "checkpoint": "12:00",
        "checkpoint_timezone": "America/New_York",
        "tickers": [
            {
                "ticker": "NVDA",
                "market_data_asof": "2026-07-10T12:00:00-04:00",
                "decision_state": "ACTIONABLE_NOW",
                "decision_now": "STARTER_NOW",
                "decision_if_triggered": "STARTER",
                "execution_timing_state": "PILOT_READY",
                "reason_codes": ["PRICE_ABOVE_TRIGGER", "VWAP_OK", "VOLUME_OK"],
                "last_price": 205.0,
                "session_vwap": 202.0,
                "relative_volume": 1.4,
                "intraday_volume": 20_000_000,
                "avg20_daily_volume": 30_000_000,
                "trading_value": 4_100_000_000,
                "price_change_pct": 1.8,
                "spread_bps": 1.2,
                "generated_in_current_run": generated,
                "freshness_class": freshness,
                "execution_eligibility": eligibility
                or ("LIVE_EXECUTION_READY" if generated else "HISTORICAL_REFERENCE_ONLY"),
                "microstructure_source_run_id": "overlay-us-live",
                "asof_execution_gate": {
                    "core_fields_present": True,
                    "missing_core_fields": [],
                },
            }
        ],
    }


def test_builds_korean_action_first_strategy_table():
    bundle = build_decision_bundle(
        run_id="overlay-us-live",
        market="US",
        generated_at="2026-07-10T12:01:00-04:00",
        analysis_source_run_id="daily-us",
        ticker_summaries=[{"ticker": "NVDA", "ticker_name": "NVIDIA", "status": "success"}],
        execution_context=_live_context(),
        portfolio_candidates=[
            {
                "canonical_ticker": "NVDA",
                "display_name": "NVIDIA",
                "is_held": True,
                "sector": "Semiconductors",
                "trigger_conditions": ["거래량을 동반해 돌파 가격 위에서 유지"],
            }
        ],
        portfolio_actions=[
            {
                "canonical_ticker": "NVDA",
                "priority": 1,
                "action_now": "STARTER_NOW",
                "action_if_triggered": "STARTER",
                "risk_action": "REDUCE_RISK",
            }
        ],
        benchmark_loader=lambda _symbols: {
            "SOXX": {"asof": "2026-07-10T12:00:00-04:00", "change_pct": 0.9},
            "SPY": {"asof": "2026-07-10T12:00:00-04:00", "change_pct": 0.3},
        },
    )

    row = bundle["strategy_table"][0]
    assert bundle["quality"]["decision_ready"] is True
    assert bundle["quality"]["conditional_strategy_ready"] is True
    assert row["strategy_code"] == "BUY_NOW"
    assert row["strategy_ko"] == "지금 분할매수 검토"
    assert row["vwap_position_ko"].startswith("VWAP 위")
    assert row["sector_sync"]["status_ko"] == "동반 상승"
    assert row["index_sync"]["status_ko"] == "동반 상승"
    assert "매수 기준가 상회" in row["reason_codes_ko"]
    assert row["risk_condition_ko"] == "리스크 축소"
    markdown = render_strategy_table_markdown(bundle)
    assert "# 종목별 투자 전략표" in markdown
    assert "지금 분할매수 검토" in markdown


def test_stale_context_is_never_promoted_to_actionable_strategy():
    bundle = build_decision_bundle(
        run_id="overlay-us-stale",
        market="US",
        generated_at="2026-07-10T12:01:00-04:00",
        analysis_source_run_id="daily-us",
        ticker_summaries=[{"ticker": "NVDA", "status": "success"}],
        execution_context=_live_context(generated=False, freshness="PRIOR_SESSION_BACKFILL"),
        portfolio_candidates=[{"canonical_ticker": "NVDA", "is_held": True}],
        portfolio_actions=[{"canonical_ticker": "NVDA", "action_now": "STARTER_NOW"}],
        benchmark_loader=lambda _symbols: {},
    )

    assert bundle["quality"]["decision_ready"] is False
    assert bundle["strategy_table"][0]["strategy_code"] == "DATA_CHECK"
    assert "과거 데이터" in bundle["strategy_table"][0]["data_status_ko"]


def test_delayed_current_session_data_produces_conditional_strategy_not_data_check():
    context = _live_context(
        freshness="DELAYED_CHECKPOINT",
        eligibility="DELAYED_ANALYSIS_ONLY",
    )
    context["tickers"][0]["decision_state"] = "DEGRADED"
    context["tickers"][0]["decision_now"] = "STARTER_NOW"
    bundle = build_decision_bundle(
        run_id="overlay-us-conditional",
        market="US",
        generated_at="2026-07-10T12:01:00-04:00",
        analysis_source_run_id="daily-us",
        ticker_summaries=[{"ticker": "NVDA", "status": "success"}],
        execution_context=context,
        portfolio_candidates=[{"canonical_ticker": "NVDA", "is_held": False}],
        portfolio_actions=[{"canonical_ticker": "NVDA", "action_now": "STARTER_NOW"}],
        benchmark_loader=lambda _symbols: {},
    )

    row = bundle["strategy_table"][0]
    assert bundle["quality"]["decision_ready"] is False
    assert bundle["quality"]["conditional_strategy_ready"] is True
    assert bundle["quality"]["conditional_row_ratio"] == 1.0
    assert row["strategy_ko"] == "조건 확인 후 분할매수 검토"
    assert row["quality"]["execution_ready"] is False
    assert row["quality"]["conditional_strategy_ready"] is True
    assert row["data_status_ko"] == "현재 세션 조건부 데이터, 주문 전 호가·상태 재확인"


def test_latest_pointer_ignores_newer_non_ready_run(tmp_path: Path):
    ready_dir = tmp_path / "ready"
    stale_dir = tmp_path / "stale"
    site_dir = tmp_path / "site"
    ready_dir.mkdir()
    stale_dir.mkdir()
    for name in ("decision_bundle_v2.json", "strategy_table_ko.md", "decision_bundle_status.json"):
        (ready_dir / name).write_text("{}" if name.endswith(".json") else "# 전략표", encoding="utf-8")
    manifests = [
        {
            "run_id": "newer-stale-us",
            "started_at": "2026-07-10T13:00:00+09:00",
            "settings": {"market": "US"},
            "_run_dir": str(stale_dir),
            "decision_bundle": {"decision_ready": False, "quality_label_ko": "확인 필요", "fresh_row_ratio": 0.0},
        },
        {
            "run_id": "older-ready-us",
            "started_at": "2026-07-10T12:00:00+09:00",
            "settings": {"market": "US"},
            "_run_dir": str(ready_dir),
            "decision_bundle": {
                "decision_ready": True,
                "quality_label_ko": "장중 투자 판단 가능",
                "fresh_row_ratio": 1.0,
                "artifacts": {
                    "decision_bundle_v2_json": "decision_bundle_v2.json",
                    "strategy_table_ko_md": "strategy_table_ko.md",
                    "decision_bundle_status_json": "decision_bundle_status.json",
                },
            },
        },
    ]

    _publish_latest_decision_bundles(site_dir=site_dir, manifests=manifests)

    status = json.loads((site_dir / "latest" / "us" / "status.json").read_text(encoding="utf-8"))
    source = json.loads((site_dir / "latest" / "us" / "source.json").read_text(encoding="utf-8"))
    assert status["latest_run_id"] == "newer-stale-us"
    assert status["decision_ready"] is False
    assert source["decision_ready_run_id"] == "older-ready-us"
    assert (site_dir / "latest" / "us" / "decision_bundle.json").exists()


def test_investor_table_keeps_all_holdings_and_limits_new_candidates():
    rows = [
        {"ticker": "HELD2", "is_held": True, "table_priority": 4},
        *[
            {"ticker": f"NEW{index}", "is_held": False, "table_priority": index}
            for index in range(1, 8)
        ],
        {"ticker": "HELD1", "is_held": True, "table_priority": 3},
    ]

    selected = select_investor_strategy_rows(rows)

    assert [row["ticker"] for row in selected] == [
        "HELD2",
        "HELD1",
        "NEW1",
        "NEW2",
        "NEW3",
        "NEW4",
        "NEW5",
    ]
    assert [row["display_priority"] for row in selected] == list(range(1, 8))


def test_candidate_invalidation_condition_is_shown_in_korean_strategy_table():
    bundle = build_decision_bundle(
        run_id="overlay-us-risk",
        market="US",
        generated_at="2026-07-10T12:01:00-04:00",
        analysis_source_run_id="daily-us",
        ticker_summaries=[{"ticker": "NVDA", "status": "success"}],
        execution_context=_live_context(),
        portfolio_candidates=[
            {
                "canonical_ticker": "NVDA",
                "is_held": True,
                "invalidation_conditions": ["199달러 종가 하회"],
            }
        ],
        portfolio_actions=[{"canonical_ticker": "NVDA", "action_now": "STARTER_NOW"}],
        benchmark_loader=lambda _symbols: {},
    )

    assert bundle["strategy_table"][0]["risk_condition_ko"] == "199달러 종가 하회"


def test_hold_action_does_not_create_contradictory_risk_wording():
    bundle = build_decision_bundle(
        run_id="overlay-us-risk-hold",
        market="US",
        generated_at="2026-07-10T12:01:00-04:00",
        analysis_source_run_id="daily-us",
        ticker_summaries=[{"ticker": "NVDA", "status": "success"}],
        execution_context=_live_context(),
        portfolio_candidates=[{"canonical_ticker": "NVDA", "is_held": True}],
        portfolio_actions=[
            {
                "canonical_ticker": "NVDA",
                "action_now": "HOLD",
                "risk_action": "HOLD",
                "risk_action_level": {"price": 199},
            }
        ],
        benchmark_loader=lambda _symbols: {},
    )

    assert bundle["strategy_table"][0]["risk_condition_ko"] == "199 이탈 시 전략 재평가"
