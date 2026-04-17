import json
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from tradingagents.scheduled.config import load_scheduled_config
from tradingagents.scheduled.runner import (
    _build_analysis_quality_flags,
    _build_close_plan_artifact,
    _build_daily_thesis_artifact,
    _build_intraday_execution_artifact,
    _completed_daily_trade_date_for_kr,
    _compute_batch_metrics,
    _compute_batch_warnings,
)


def test_no_mixed_daily_cohort_for_kr_intraday_runs():
    now = datetime(2026, 4, 17, 14, 0, tzinfo=ZoneInfo("Asia/Seoul"))
    thesis_date = _completed_daily_trade_date_for_kr(now).isoformat()

    metrics = _compute_batch_metrics(
        [
            {"status": "success", "trade_date": thesis_date, "decision": "HOLD"},
            {"status": "success", "trade_date": thesis_date, "decision": "HOLD"},
            {"status": "success", "trade_date": thesis_date, "decision": "HOLD"},
        ]
    )

    assert thesis_date == "2026-04-16"
    assert not any("mixed_daily_cohort" in warning for warning in _compute_batch_warnings(metrics))


def test_same_day_market_requires_intraday_tool_or_quality_flag():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "scheduled.toml"
        config_path.write_text(
            """
[run]
tickers = ["005930.KS"]
market = "KR"
analysts = ["market"]

[storage]
archive_dir = "./archive"
site_dir = "./site"
""",
            encoding="utf-8",
        )
        config = load_scheduled_config(config_path)

    flags = _build_analysis_quality_flags(
        config=config,
        trade_date="2026-04-17",
        analysis_date="2026-04-17",
        called_tools={"get_stock_data", "get_indicators"},
        effective_tool_calls=2,
        tokens_available=True,
    )

    assert "intraday_snapshot_missing_same_day" in flags


def test_daily_thesis_intraday_execution_close_plan_artifacts_are_split():
    decision = {
        "rating": "HOLD",
        "portfolio_stance": "BULLISH",
        "entry_action": "WAIT",
        "setup_quality": "DEVELOPING",
        "confidence": 0.7,
        "time_horizon": "short",
        "entry_logic": "조건 확인 전까지 대기",
        "exit_logic": "무효화 가격 이탈 시 축소",
        "position_sizing": "소액 starter 후 확인",
        "risk_limits": "버퍼 준수",
        "catalysts": ["breakout above 100 with rvol 1.2"],
        "invalidators": ["close below 95"],
        "watchlist_triggers": ["above vwap preferred"],
        "data_coverage": {"company_news_count": 1, "disclosures_count": 1, "social_source": "dedicated", "macro_items_count": 1},
        "execution_levels": {
            "intraday_pilot_rule": "10:30 이후 trigger 상회 + VWAP 위",
            "close_confirm_rule": "종가 trigger 상회",
            "next_day_followthrough_rule": "다음날 첫 30분 trigger 재이탈 없음",
            "failed_breakout_rule": "trigger 아래 재이탈 시 신규 금지",
            "trim_rule": "95 이탈 시 축소",
            "funding_priority": "high",
            "entry_window": "mid",
            "trigger_quality": "strong",
        },
    }
    analysis = {
        "ticker": "005930.KS",
        "ticker_name": "삼성전자",
        "trade_date": "2026-04-16",
        "analysis_date": "2026-04-17",
        "finished_at": "2026-04-17T10:05:00+09:00",
        "decision": json.dumps(decision, ensure_ascii=False),
    }
    contract = {
        "portfolio_stance": "BULLISH",
        "entry_action_base": "WAIT",
        "setup_quality": "DEVELOPING",
        "confidence": 0.7,
        "action_if_triggered": "STARTER",
        "execution_levels": decision["execution_levels"],
    }
    update = {
        "execution_asof": "2026-04-17T14:35:00+09:00",
        "market_data_asof": "2026-04-17T14:35:00+09:00",
        "decision_state": "TRIGGERED_PENDING_CLOSE",
        "decision_now": "NONE",
        "execution_timing_state": "LATE_SESSION_CONFIRM",
    }

    thesis = _build_daily_thesis_artifact(analysis_payload=analysis, contract_payload=contract)
    intraday = _build_intraday_execution_artifact(
        analysis_payload=analysis,
        contract_payload=contract,
        execution_update_payload=update,
    )
    close_plan = _build_close_plan_artifact(
        analysis_payload=analysis,
        contract_payload=contract,
        execution_update_payload=update,
    )

    assert thesis["artifact_type"] == "daily_thesis"
    assert intraday["artifact_type"] == "intraday_execution"
    assert close_plan["artifact_type"] == "close_plan"
    assert thesis["same_day_partial_bar_used_as_daily_thesis"] is False
    assert intraday["daily_thesis_trade_date"] == "2026-04-16"
    assert close_plan["next_day_followthrough_rule"] == "다음날 첫 30분 trigger 재이탈 없음"

