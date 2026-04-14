from datetime import datetime, timedelta, timezone

from tradingagents.execution.overlay import evaluate_execution_state
from tradingagents.portfolio.candidates import _apply_execution_overlay_actions
from tradingagents.scheduled.runner import _build_execution_summary, _select_due_checkpoints
from tradingagents.schemas import (
    ActionIfTriggered,
    BreakoutConfirmation,
    DecisionState,
    EventGuard,
    ExecutionContract,
    IntradayMarketSnapshot,
    LevelBasis,
    PrimarySetup,
    ThesisState,
    is_event_guard_active,
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
        breakout_confirmation=BreakoutConfirmation.INTRADAY_ABOVE,
        min_relative_volume=1.0,
    )
    base.update(kwargs)
    return ExecutionContract(**base)


def _market(*, last_price: float, day_high: float, day_low: float):
    return IntradayMarketSnapshot(
        ticker="TSM",
        asof=datetime.now(timezone.utc).isoformat(),
        provider="yfinance_intraday",
        interval="5m",
        last_price=last_price,
        session_vwap=99.5,
        day_high=day_high,
        day_low=day_low,
        volume=1000,
        avg20_daily_volume=1000.0,
        relative_volume=1.2,
    )


def test_event_guard_expires_after_event_day():
    now = datetime(2026, 4, 14, tzinfo=timezone.utc)
    guard = EventGuard(earnings_date="2026-04-13", block_new_position_within_days=1)
    assert is_event_guard_active(guard, now) is False


def test_breakout_hit_by_day_high_marks_actionable():
    now = datetime.now(timezone.utc)
    update = evaluate_execution_state(
        _contract(),
        _market(last_price=99.5, day_high=101.0, day_low=98.0),
        now=now,
        max_data_age_seconds=180,
    )
    assert update.decision_state in {DecisionState.ACTIONABLE_NOW, DecisionState.ARMED}


def test_build_execution_summary_handles_empty_updates():
    summary = _build_execution_summary(run_id="run", ticker_updates={"_latest_checkpoint": {"value": "22:35"}}, checkpoint="22:35")
    assert summary["market_regime"] == "degraded"


def test_due_checkpoint_selection_uses_current_time():
    now_kst = datetime(2026, 4, 14, 22, 52)
    selected = _select_due_checkpoints(now_kst=now_kst, checkpoints=["22:35", "22:50", "23:30"])
    assert selected == ["22:50"]


def test_candidate_mapping_invalidated_state():
    now, trig = _apply_execution_overlay_actions(
        action_now="HOLD",
        action_if_triggered="ADD_IF_TRIGGERED",
        execution_update={"decision_state": "INVALIDATED", "decision_now": "EXIT_NOW"},
        is_held=True,
    )
    assert now == "REDUCE_NOW"
    assert trig == "EXIT_IF_TRIGGERED"
