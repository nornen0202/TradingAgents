from datetime import datetime, timedelta, timezone

from tradingagents.execution.overlay import evaluate_execution_state
from tradingagents.schemas import (
    ActionIfTriggered,
    BreakoutConfirmation,
    DecisionState,
    ExecutionContract,
    IntradayMarketSnapshot,
    LevelBasis,
    PrimarySetup,
    SessionVWAPPreference,
    ThesisState,
)


def _contract(**kwargs):
    base = dict(
        ticker="TSM",
        analysis_asof="2026-04-13T20:05:12+09:00",
        market_data_asof="2026-04-10T16:00:00-04:00",
        level_basis=LevelBasis.DAILY_CLOSE,
        thesis_state=ThesisState.CONSTRUCTIVE,
        primary_setup=PrimarySetup.BREAKOUT_CONFIRMATION,
        portfolio_stance="BULLISH",
        entry_action_base="WAIT",
        setup_quality="DEVELOPING",
        confidence=0.72,
        action_if_triggered=ActionIfTriggered.STARTER,
        breakout_level=100.0,
        breakout_confirmation=BreakoutConfirmation.CLOSE_ABOVE,
        min_relative_volume=1.2,
        session_vwap_preference=SessionVWAPPreference.INDIFFERENT,
    )
    base.update(kwargs)
    return ExecutionContract(**base)


def _market(*, price: float, rvol: float, age_seconds: int = 0):
    asof = datetime.now(timezone.utc) - timedelta(seconds=age_seconds)
    return IntradayMarketSnapshot(
        ticker="TSM",
        asof=asof.isoformat(),
        provider="yfinance_intraday",
        interval="5m",
        last_price=price,
        session_vwap=99.5,
        day_high=101.0,
        day_low=98.0,
        volume=1000,
        avg20_daily_volume=1000.0,
        relative_volume=rvol,
    )


def test_breakout_close_confirmation_state():
    now = datetime.now(timezone.utc)
    update = evaluate_execution_state(_contract(), _market(price=101.0, rvol=1.4), now=now, max_data_age_seconds=180)
    assert update.decision_state == DecisionState.TRIGGERED_PENDING_CLOSE


def test_intraday_breakout_actionable_now():
    now = datetime.now(timezone.utc)
    contract = _contract(breakout_confirmation=BreakoutConfirmation.INTRADAY_ABOVE)
    update = evaluate_execution_state(contract, _market(price=101.0, rvol=1.4), now=now, max_data_age_seconds=180)
    assert update.decision_state == DecisionState.ACTIONABLE_NOW


def test_stale_market_data_degraded():
    now = datetime.now(timezone.utc)
    update = evaluate_execution_state(_contract(), _market(price=101.0, rvol=1.4, age_seconds=600), now=now, max_data_age_seconds=180)
    assert update.decision_state == DecisionState.DEGRADED
