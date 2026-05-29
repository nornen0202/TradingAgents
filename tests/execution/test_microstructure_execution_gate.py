from __future__ import annotations

from datetime import datetime, timezone

from tradingagents.execution.overlay import evaluate_execution_state
from tradingagents.schemas import (
    ActionIfTriggered,
    BreakoutConfirmation,
    DecisionState,
    ExecutionContract,
    ExecutionTimingState,
    IntradayMarketSnapshot,
    LevelBasis,
    PrimarySetup,
    ThesisState,
)


def _contract(ticker: str = "AAPL") -> ExecutionContract:
    return ExecutionContract(
        ticker=ticker,
        analysis_asof="2026-05-29T09:00:00-04:00",
        market_data_asof="2026-05-29",
        level_basis=LevelBasis.DAILY_CLOSE,
        thesis_state=ThesisState.CONSTRUCTIVE,
        primary_setup=PrimarySetup.BREAKOUT_CONFIRMATION,
        portfolio_stance="BULLISH",
        entry_action_base="WAIT",
        setup_quality="COMPELLING",
        confidence=0.8,
        action_if_triggered=ActionIfTriggered.STARTER,
        breakout_level=100.0,
        breakout_confirmation=BreakoutConfirmation.INTRADAY_ABOVE,
        min_relative_volume=1.0,
    )


def _market(**kwargs) -> IntradayMarketSnapshot:
    base = dict(
        ticker="AAPL",
        asof=datetime.now(timezone.utc).isoformat(),
        provider="kis_microstructure",
        interval="5m",
        last_price=101.0,
        session_vwap=100.0,
        day_high=102.0,
        day_low=99.0,
        volume=1000,
        avg20_daily_volume=1000.0,
        relative_volume=1.2,
        provider_realtime_capable=True,
        quote_delay_seconds=0,
        market_session="regular",
        market="US",
        spread_bps=5.0,
        orderbook_imbalance=0.2,
        execution_strength=120.0,
        halt_status={"status": "normal", "is_clear": True},
        investor_flow_status="not_applicable",
        program_flow_status="not_applicable",
        microstructure_required=True,
    )
    base.update(kwargs)
    return IntradayMarketSnapshot(**base)


def test_microstructure_required_snapshot_blocks_pilot_when_orderbook_missing():
    update = evaluate_execution_state(
        _contract(),
        _market(spread_bps=None, orderbook_imbalance=None),
        now=datetime.now(timezone.utc),
        max_data_age_seconds=180,
    )

    assert update.decision_state == DecisionState.ARMED
    assert update.execution_timing_state == ExecutionTimingState.PILOT_BLOCKED_VOLUME
    assert "microstructure_orderbook_missing" in update.reason_codes


def test_us_not_applicable_investor_and_program_flow_do_not_block_pilot():
    update = evaluate_execution_state(
        _contract(),
        _market(),
        now=datetime.now(timezone.utc),
        max_data_age_seconds=180,
    )

    assert update.decision_state == DecisionState.ACTIONABLE_NOW
    assert update.execution_timing_state == ExecutionTimingState.PILOT_READY
    assert "pilot_ready" in update.reason_codes


def test_kr_microstructure_requires_vi_and_market_alert_confirmation():
    update = evaluate_execution_state(
        _contract("005930.KS"),
        _market(
            ticker="005930.KS",
            market="KR",
            investor_flow_status="available",
            program_flow_status="available",
            vi_status={"status": "unknown", "is_clear": False},
            market_alert_status={"status": "clear", "is_clear": True},
        ),
        now=datetime.now(timezone.utc),
        max_data_age_seconds=180,
    )

    assert update.execution_timing_state == ExecutionTimingState.PILOT_BLOCKED_VOLUME
    assert "microstructure_vi_status_unconfirmed" in update.reason_codes
