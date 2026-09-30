from datetime import datetime, timedelta, timezone
from dataclasses import replace

import pytest

from tradingagents.execution.overlay import evaluate_execution_state
from tradingagents.schemas import (
    ActionIfTriggered,
    BreakoutConfirmation,
    DecisionState,
    ExecutionContract,
    ExecutionTimingState,
    IntradayMarketSnapshot,
    LevelBasis,
    PriceLevel,
    PriceLevelType,
    PrimarySetup,
    ThesisState,
)


def _contract(**kwargs):
    base = dict(
        ticker="005930.KS",
        analysis_asof="2026-04-16T18:00:00+09:00",
        market_data_asof="2026-04-16",
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


def _market(*, last_price: float, day_high: float, day_low: float, age_seconds: int = 0, asof=None, market_session="regular"):
    asof = asof or (datetime.now(timezone.utc) - timedelta(seconds=age_seconds))
    return IntradayMarketSnapshot(
        ticker="005930.KS",
        asof=asof.isoformat(),
        provider="kis_quote",
        interval="5m",
        last_price=last_price,
        session_vwap=99.5,
        day_high=day_high,
        day_low=day_low,
        volume=1000,
        avg20_daily_volume=1000.0,
        relative_volume=1.2,
        market_session=market_session,
    )


def test_stale_overlay_preserves_triggerable_candidates():
    update = evaluate_execution_state(
        _contract(),
        _market(last_price=101.0, day_high=101.5, day_low=98.0, age_seconds=600),
        now=datetime.now(timezone.utc),
        max_data_age_seconds=180,
    )

    assert update.decision_state == DecisionState.DEGRADED
    assert update.execution_timing_state == ExecutionTimingState.STALE_TRIGGERABLE
    assert update.decision_if_triggered == ActionIfTriggered.STARTER


def test_failed_breakout_state_is_distinct_from_live_breakout():
    update = evaluate_execution_state(
        _contract(),
        _market(last_price=99.0, day_high=101.5, day_low=98.0),
        now=datetime.now(timezone.utc),
        max_data_age_seconds=180,
    )

    assert update.execution_timing_state == ExecutionTimingState.PILOT_BLOCKED_FAILED_BREAKOUT
    assert update.trigger_status["failed_breakout"] is True


def test_late_session_confirm_state_uses_checkpoint_context():
    now = datetime(2026, 4, 17, 14, 35, tzinfo=timezone.utc)
    update = evaluate_execution_state(
        _contract(breakout_confirmation=BreakoutConfirmation.CLOSE_ABOVE),
        _market(last_price=101.0, day_high=101.5, day_low=98.0, asof=now),
        now=now,
        max_data_age_seconds=180,
        refresh_checkpoint="14:35",
    )

    assert update.decision_state == DecisionState.TRIGGERED_PENDING_CLOSE
    assert update.execution_timing_state == ExecutionTimingState.CLOSE_CONFIRM_PENDING


def test_risk_action_level_uses_current_price_not_day_low_for_stop_now():
    update = evaluate_execution_state(
        _contract(
            action_if_triggered=ActionIfTriggered.NONE,
            breakout_level=None,
            risk_action="STOP_LOSS",
            risk_action_level=PriceLevel(
                label="intraday stop",
                level_type=PriceLevelType.STOP_LOSS,
                price=95.0,
                confirmation="intraday",
            ),
        ),
        _market(last_price=100.0, day_high=101.0, day_low=90.0),
        now=datetime.now(timezone.utc),
        max_data_age_seconds=180,
    )

    assert update.decision_state == DecisionState.WAIT
    assert update.decision_now.value == "NONE"


def test_close_confirmation_risk_action_waits_for_close_intraday():
    update = evaluate_execution_state(
        _contract(
            action_if_triggered=ActionIfTriggered.NONE,
            breakout_level=None,
            risk_action="STOP_LOSS",
            risk_action_level=PriceLevel(
                label="close stop",
                level_type=PriceLevelType.STOP_LOSS,
                price=95.0,
                confirmation="close",
            ),
        ),
        _market(last_price=94.0, day_high=101.0, day_low=93.0, market_session="regular"),
        now=datetime.now(timezone.utc),
        max_data_age_seconds=180,
    )

    assert update.decision_state == DecisionState.TRIGGERED_PENDING_CLOSE
    assert update.decision_now.value == "NONE"
    assert update.execution_timing_state == ExecutionTimingState.CLOSE_CONFIRM_PENDING


@pytest.mark.parametrize("session", ["regular", "post_close"])
@pytest.mark.parametrize("rvol", [None, 0.5, 5.0])
def test_volume_risk_plan_requires_its_actual_confirmation(session, rvol):
    from tradingagents.portfolio.candidates import _risk_action_level_triggered_now
    from tradingagents.execution.risk_trigger import risk_condition_text

    # Based on the AMZN plan observed in the live audit: volume expansion AND
    # a regular-session close below support. Even high current RVOL alone is
    # insufficient to establish that historical close-and-volume condition.
    level = PriceLevel(
        label="보유 위험 감축선", level_type=PriceLevelType.SUPPORT,
        price=244.24, confirmation="volume_confirmed",
        volume_rule="거래량 증가를 동반한 정규장 종가 이탈",
    )
    now = datetime.now(timezone.utc)
    market = replace(
        _market(last_price=244.0, day_high=247.0, day_low=243.0,
                market_session=session, asof=now), relative_volume=rvol,
    )
    contract = _contract(action_if_triggered=ActionIfTriggered.NONE,
                         breakout_level=None, risk_action="REDUCE_RISK",
                         risk_action_level=level)
    update = evaluate_execution_state(contract, market, now=now, max_data_age_seconds=180)
    assert update.decision_now.value == "NONE"
    assert update.trigger_status["risk_action_triggered"] is False
    assert "risk_action_confirmation_required" in update.reason_codes
    assert not _risk_action_level_triggered_now(
        risk_action="REDUCE_RISK", risk_action_level=level.to_dict(),
        execution_update=update.to_dict(), current_price=market.last_price,
    )
    text = risk_condition_text("REDUCE_RISK", level.to_dict(), "위험 축소")
    assert "거래량 조건 확인 후" in text
    assert level.volume_rule in text
    assert "장중 확인 시" not in text


def test_explicit_intraday_risk_plan_still_acts_on_current_price():
    from tradingagents.portfolio.candidates import _risk_action_level_triggered_now

    level = PriceLevel(label="intraday stop", level_type=PriceLevelType.STOP_LOSS,
                       price=95.0, confirmation="intraday")
    now = datetime.now(timezone.utc)
    update = evaluate_execution_state(
        _contract(action_if_triggered=ActionIfTriggered.NONE, breakout_level=None,
                  risk_action="STOP_LOSS", risk_action_level=level),
        _market(last_price=94.0, day_high=101.0, day_low=93.0, asof=now),
        now=now, max_data_age_seconds=180,
    )
    assert update.decision_now.value == "EXIT_NOW"
    assert _risk_action_level_triggered_now(
        risk_action="STOP_LOSS", risk_action_level=level.to_dict(),
        execution_update=update.to_dict(), current_price=94.0,
    )
