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


def test_delayed_analysis_cannot_create_pilot_ready():
    contract = ExecutionContract(
        ticker="TSM",
        analysis_asof="2026-04-24T08:00:00+09:00",
        market_data_asof="2026-04-23",
        level_basis=LevelBasis.DAILY_CLOSE,
        thesis_state=ThesisState.CONSTRUCTIVE,
        primary_setup=PrimarySetup.BREAKOUT_CONFIRMATION,
        portfolio_stance="BULLISH",
        entry_action_base="WAIT",
        setup_quality="DEVELOPING",
        confidence=0.8,
        action_if_triggered=ActionIfTriggered.STARTER,
        breakout_level=100.0,
        breakout_confirmation=BreakoutConfirmation.INTRADAY_ABOVE,
        min_relative_volume=1.0,
    )
    market = IntradayMarketSnapshot(
        ticker="TSM",
        asof="2026-04-24T10:30:00+09:00",
        provider="yfinance_intraday",
        interval="5m",
        last_price=101.0,
        session_vwap=99.0,
        day_high=101.5,
        day_low=98.0,
        volume=1000,
        avg20_daily_volume=1000.0,
        relative_volume=1.5,
        provider_realtime_capable=False,
        market_session="regular",
        execution_data_quality="DELAYED_ANALYSIS_ONLY",
    )

    update = evaluate_execution_state(
        contract,
        market,
        now=datetime.now(timezone.utc),
        max_data_age_seconds=180,
    )

    assert update.decision_state == DecisionState.DEGRADED
    assert update.execution_timing_state == ExecutionTimingState.STALE_TRIGGERABLE
