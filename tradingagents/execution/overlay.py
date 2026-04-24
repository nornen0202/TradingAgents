from __future__ import annotations

from datetime import datetime

from tradingagents.dataflows.intraday_market import DELAYED_ANALYSIS_ONLY, STALE_INVALID_FOR_EXECUTION
from tradingagents.schemas import (
    ActionIfTriggered,
    BreakoutConfirmation,
    DecisionNow,
    DecisionState,
    ExecutionContract,
    ExecutionTimingState,
    ExecutionUpdate,
    IntradayMarketSnapshot,
    SessionVWAPPreference,
    is_event_guard_active,
)


def evaluate_execution_state(
    contract: ExecutionContract,
    market: IntradayMarketSnapshot,
    *,
    now: datetime,
    max_data_age_seconds: int,
    refresh_checkpoint: str | None = None,
) -> ExecutionUpdate:
    reason_codes: list[str] = []
    trigger_status = {
        "breakout_hit_intraday": False,
        "close_confirmation_pending": False,
        "pullback_zone_active": False,
        "invalidated": False,
        "failed_breakout": False,
        "support_hold": False,
        "support_fail": False,
    }

    staleness_seconds = int(max(0, (now - datetime.fromisoformat(market.asof)).total_seconds()))
    data_quality = str(market.execution_data_quality or "").upper()
    market_session = str(market.market_session or "").strip().lower()

    if market_session == "pre_open":
        return _build_update(
            contract,
            market,
            now,
            staleness_seconds=staleness_seconds,
            decision_state=DecisionState.WAIT,
            decision_now=DecisionNow.NONE,
            reason_codes=("pre_open_thesis_only",),
            trigger_status=trigger_status,
            data_health="OK",
            refresh_checkpoint=refresh_checkpoint,
            execution_timing_state=ExecutionTimingState.PRE_OPEN_THESIS_ONLY,
        )

    if data_quality in {DELAYED_ANALYSIS_ONLY, STALE_INVALID_FOR_EXECUTION}:
        timing_state = (
            ExecutionTimingState.STALE_TRIGGERABLE
            if contract.action_if_triggered != ActionIfTriggered.NONE
            else ExecutionTimingState.DEGRADED
        )
        return _build_update(
            contract,
            market,
            now,
            staleness_seconds=staleness_seconds,
            decision_state=DecisionState.DEGRADED,
            decision_now=DecisionNow.NONE,
            reason_codes=("delayed_or_invalid_market_data",),
            trigger_status=trigger_status,
            data_health="STALE" if data_quality == STALE_INVALID_FOR_EXECUTION else "DELAYED",
            refresh_checkpoint=refresh_checkpoint,
            execution_timing_state=timing_state,
        )

    if staleness_seconds > max_data_age_seconds:
        timing_state = (
            ExecutionTimingState.STALE_TRIGGERABLE
            if contract.action_if_triggered != ActionIfTriggered.NONE
            else ExecutionTimingState.DEGRADED
        )
        return _build_update(
            contract,
            market,
            now,
            staleness_seconds=staleness_seconds,
            decision_state=DecisionState.DEGRADED,
            decision_now=DecisionNow.NONE,
            reason_codes=("stale_market_data",),
            trigger_status=trigger_status,
            data_health="STALE",
            refresh_checkpoint=refresh_checkpoint,
            execution_timing_state=timing_state,
        )

    if is_event_guard_active(contract.event_guard, now):
        return _build_update(
            contract,
            market,
            now,
            staleness_seconds=staleness_seconds,
            decision_state=DecisionState.WAIT,
            decision_now=DecisionNow.NONE,
            reason_codes=("pre_event_guard_active",),
            trigger_status=trigger_status,
            data_health="OK",
            refresh_checkpoint=refresh_checkpoint,
            execution_timing_state=ExecutionTimingState.WAITING,
        )

    intraday_low = market.day_low if market.day_low is not None else market.last_price
    intraday_high = market.day_high if market.day_high is not None else market.last_price
    decision_state = DecisionState.WAIT
    decision_now = DecisionNow.NONE
    execution_timing_state = ExecutionTimingState.WAITING

    if contract.invalid_if_intraday_below is not None and intraday_low < contract.invalid_if_intraday_below:
        trigger_status["invalidated"] = True
        return _build_update(
            contract,
            market,
            now,
            staleness_seconds=staleness_seconds,
            decision_state=DecisionState.INVALIDATED,
            decision_now=DecisionNow.EXIT_NOW,
            reason_codes=("intraday_invalidation_breached",),
            trigger_status=trigger_status,
            data_health="OK",
            refresh_checkpoint=refresh_checkpoint,
            execution_timing_state=ExecutionTimingState.INVALIDATED,
        )

    breakout_hit = contract.breakout_level is not None and intraday_high >= contract.breakout_level
    rvol_confirmed = contract.min_relative_volume is None or ((market.relative_volume or 0.0) >= contract.min_relative_volume)
    vwap_confirmed = _vwap_check(contract.session_vwap_preference, market.last_price, market.session_vwap)
    pilot_window_open = _pilot_window_open(
        market_asof=market.asof,
        earliest_pilot_time_local=contract.earliest_pilot_time_local,
    )

    if breakout_hit:
        trigger_status["breakout_hit_intraday"] = True
        last_price_above_breakout = market.last_price >= float(contract.breakout_level or 0.0)

        if not last_price_above_breakout:
            trigger_status["failed_breakout"] = True
            decision_state = DecisionState.ARMED
            decision_now = DecisionNow.NONE
            execution_timing_state = (
                ExecutionTimingState.PILOT_BLOCKED_FAILED_BREAKOUT
                if contract.action_if_triggered == ActionIfTriggered.STARTER
                else ExecutionTimingState.FAILED_BREAKOUT
            )
            reason_codes.append("failed_breakout")
        elif contract.breakout_confirmation in {BreakoutConfirmation.CLOSE_ABOVE, BreakoutConfirmation.END_OF_DAY_ONLY}:
            trigger_status["close_confirmation_pending"] = True
            if market_session == "post_close":
                decision_state = DecisionState.WAIT
                decision_now = DecisionNow.NONE
                execution_timing_state = (
                    ExecutionTimingState.CLOSE_CONFIRMED
                    if rvol_confirmed and vwap_confirmed
                    else ExecutionTimingState.CLOSE_CONFIRM_PENDING
                )
                reason_codes.append("close_confirmed" if execution_timing_state == ExecutionTimingState.CLOSE_CONFIRMED else "close_confirmation_required")
            else:
                decision_state = DecisionState.TRIGGERED_PENDING_CLOSE
                decision_now = DecisionNow.NONE
                execution_timing_state = ExecutionTimingState.CLOSE_CONFIRM_PENDING
                reason_codes.append("close_confirmation_required")
        elif not pilot_window_open:
            decision_state = DecisionState.ARMED
            decision_now = DecisionNow.NONE
            execution_timing_state = ExecutionTimingState.CLOSE_CONFIRM_PENDING
            reason_codes.append("pilot_window_not_open")
        elif not rvol_confirmed or not vwap_confirmed:
            decision_state = DecisionState.ARMED
            decision_now = DecisionNow.NONE
            execution_timing_state = ExecutionTimingState.PILOT_BLOCKED_VOLUME
            if not rvol_confirmed:
                reason_codes.append("relative_volume_unconfirmed")
            if not vwap_confirmed:
                reason_codes.append("vwap_unconfirmed")
        else:
            decision_state = DecisionState.ACTIONABLE_NOW
            decision_now = _decision_now_from_action(contract.action_if_triggered)
            execution_timing_state = ExecutionTimingState.PILOT_READY
            reason_codes.append("pilot_ready")

    if contract.pullback_buy_zone is not None:
        if market.last_price < contract.pullback_buy_zone.low and intraday_low < contract.pullback_buy_zone.low:
            trigger_status["support_fail"] = True
            if decision_state not in {DecisionState.INVALIDATED, DecisionState.ACTIONABLE_NOW}:
                decision_state = DecisionState.ARMED
                decision_now = DecisionNow.NONE
                execution_timing_state = ExecutionTimingState.SUPPORT_FAIL
                reason_codes.append("support_zone_failed")

        in_zone = contract.pullback_buy_zone.low <= market.last_price <= contract.pullback_buy_zone.high
        if in_zone:
            trigger_status["pullback_zone_active"] = True
            trigger_status["support_hold"] = True
            if vwap_confirmed:
                decision_state = DecisionState.ACTIONABLE_NOW
                decision_now = _decision_now_from_action(contract.action_if_triggered)
                execution_timing_state = ExecutionTimingState.SUPPORT_HOLD
                reason_codes.append("pullback_zone_actionable")
            else:
                decision_state = DecisionState.ARMED
                decision_now = DecisionNow.NONE
                execution_timing_state = ExecutionTimingState.PILOT_BLOCKED_VOLUME
                reason_codes.append("vwap_unconfirmed")

    if market_session == "post_close" and execution_timing_state == ExecutionTimingState.WAITING and contract.breakout_level is not None:
        decision_state = DecisionState.WAIT
        decision_now = DecisionNow.NONE
        execution_timing_state = ExecutionTimingState.NEXT_DAY_FOLLOWTHROUGH_PENDING
        reason_codes.append("next_day_followthrough_pending")

    if not reason_codes:
        reason_codes.append("waiting_for_trigger")

    return _build_update(
        contract,
        market,
        now,
        staleness_seconds=staleness_seconds,
        decision_state=decision_state,
        decision_now=decision_now,
        reason_codes=tuple(reason_codes),
        trigger_status=trigger_status,
        data_health="OK",
        refresh_checkpoint=refresh_checkpoint,
        execution_timing_state=execution_timing_state,
    )


def _vwap_check(pref: SessionVWAPPreference, price: float, vwap: float | None) -> bool:
    if pref == SessionVWAPPreference.INDIFFERENT or vwap is None:
        return True
    if pref == SessionVWAPPreference.ABOVE:
        return price >= vwap
    return price <= vwap


def _decision_now_from_action(action: ActionIfTriggered) -> DecisionNow:
    mapping = {
        ActionIfTriggered.NONE: DecisionNow.NONE,
        ActionIfTriggered.STARTER: DecisionNow.STARTER_NOW,
        ActionIfTriggered.ADD: DecisionNow.ADD_NOW,
        ActionIfTriggered.REDUCE: DecisionNow.REDUCE_NOW,
        ActionIfTriggered.EXIT: DecisionNow.EXIT_NOW,
    }
    return mapping[action]


def _pilot_window_open(*, market_asof: str, earliest_pilot_time_local: str | None) -> bool:
    if not earliest_pilot_time_local:
        return True
    try:
        parsed = datetime.fromisoformat(str(market_asof))
        hour_text, minute_text = str(earliest_pilot_time_local).split(":", 1)
        return (parsed.hour, parsed.minute) >= (int(hour_text), int(minute_text))
    except Exception:
        return True


def _build_update(
    contract: ExecutionContract,
    market: IntradayMarketSnapshot,
    now: datetime,
    *,
    staleness_seconds: int,
    decision_state: DecisionState,
    decision_now: DecisionNow,
    reason_codes: tuple[str, ...],
    trigger_status: dict[str, bool],
    data_health: str,
    refresh_checkpoint: str | None,
    execution_timing_state: ExecutionTimingState = ExecutionTimingState.WAITING,
) -> ExecutionUpdate:
    return ExecutionUpdate(
        ticker=contract.ticker,
        analysis_asof=contract.analysis_asof,
        execution_asof=now.isoformat(),
        market_data_asof=market.asof,
        source={
            "provider": market.provider,
            "interval": market.interval,
            "bar_timestamp": market.bar_timestamp or market.asof,
            "provider_timestamp": market.provider_timestamp or market.asof,
            "quote_delay_seconds": market.quote_delay_seconds,
            "provider_realtime_capable": market.provider_realtime_capable,
            "market_session": market.market_session,
            "execution_data_quality": market.execution_data_quality,
        },
        last_price=market.last_price,
        session_vwap=market.session_vwap,
        day_high=market.day_high,
        day_low=market.day_low,
        intraday_volume=market.volume,
        avg20_daily_volume=market.avg20_daily_volume,
        relative_volume=market.relative_volume,
        price_state="INTRADAY",
        volume_state=(
            "CONFIRMED"
            if (market.relative_volume or 0.0) >= (contract.min_relative_volume or 0.0)
            else "UNCONFIRMED"
        ),
        event_state="GUARDED" if "pre_event_guard_active" in reason_codes else "OPEN",
        decision_state=decision_state,
        decision_now=decision_now,
        decision_if_triggered=contract.action_if_triggered,
        trigger_status=trigger_status,
        changed_fields=(
            "execution_asof",
            "last_price",
            "session_vwap",
            "relative_volume",
        ),
        reason_codes=reason_codes,
        staleness_seconds=staleness_seconds,
        data_health=data_health,
        refresh_checkpoint=refresh_checkpoint,
        execution_timing_state=execution_timing_state,
    )
