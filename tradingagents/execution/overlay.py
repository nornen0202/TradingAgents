from __future__ import annotations

from datetime import datetime

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
        reason_codes.append("pre_event_guard_active")
        return _build_update(
            contract,
            market,
            now,
            staleness_seconds=staleness_seconds,
            decision_state=DecisionState.WAIT,
            decision_now=DecisionNow.NONE,
            reason_codes=tuple(reason_codes),
            trigger_status=trigger_status,
            data_health="OK",
            refresh_checkpoint=refresh_checkpoint,
            execution_timing_state=ExecutionTimingState.WAITING,
        )

    intraday_low = market.day_low if market.day_low is not None else market.last_price
    intraday_high = market.day_high if market.day_high is not None else market.last_price

    if contract.invalid_if_intraday_below is not None and intraday_low < contract.invalid_if_intraday_below:
        trigger_status["invalidated"] = True
        reason_codes.append("intraday_invalidation_breached")
        return _build_update(
            contract,
            market,
            now,
            staleness_seconds=staleness_seconds,
            decision_state=DecisionState.INVALIDATED,
            decision_now=DecisionNow.EXIT_NOW,
            reason_codes=tuple(reason_codes),
            trigger_status=trigger_status,
            data_health="OK",
            refresh_checkpoint=refresh_checkpoint,
            execution_timing_state=ExecutionTimingState.INVALIDATED,
        )

    decision_state = DecisionState.WAIT
    decision_now = DecisionNow.NONE
    execution_timing_state = ExecutionTimingState.WAITING

    if contract.breakout_level is not None and intraday_high >= contract.breakout_level:
        trigger_status["breakout_hit_intraday"] = True
        rvol_ok = contract.min_relative_volume is None or ((market.relative_volume or 0.0) >= contract.min_relative_volume)
        if rvol_ok:
            if contract.breakout_confirmation == BreakoutConfirmation.CLOSE_ABOVE:
                decision_state = DecisionState.TRIGGERED_PENDING_CLOSE
                execution_timing_state = (
                    ExecutionTimingState.LATE_SESSION_CONFIRM
                    if _is_late_session(now, refresh_checkpoint=refresh_checkpoint)
                    else ExecutionTimingState.CLOSE_CONFIRM
                )
                trigger_status["close_confirmation_pending"] = True
                reason_codes.append("close_confirmation_required")
            else:
                if market.last_price >= contract.breakout_level:
                    decision_state = DecisionState.ACTIONABLE_NOW
                    decision_now = _decision_now_from_action(contract.action_if_triggered)
                    execution_timing_state = ExecutionTimingState.LIVE_BREAKOUT
                    reason_codes.append("breakout_confirmed")
                else:
                    decision_state = DecisionState.ARMED
                    execution_timing_state = ExecutionTimingState.FAILED_BREAKOUT
                    trigger_status["failed_breakout"] = True
                    reason_codes.append("failed_breakout")
        else:
            decision_state = DecisionState.ARMED
            execution_timing_state = ExecutionTimingState.LIVE_BREAKOUT
            reason_codes.append("relative_volume_unconfirmed")

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
            if _vwap_check(contract.session_vwap_preference, market.last_price, market.session_vwap):
                decision_state = DecisionState.ACTIONABLE_NOW
                decision_now = _decision_now_from_action(contract.action_if_triggered)
                execution_timing_state = ExecutionTimingState.SUPPORT_HOLD
                reason_codes.append("pullback_zone_actionable")
            else:
                decision_state = DecisionState.ARMED
                execution_timing_state = ExecutionTimingState.SUPPORT_HOLD
                reason_codes.append("vwap_filter_not_met")

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


def _is_late_session(now: datetime, *, refresh_checkpoint: str | None) -> bool:
    if not refresh_checkpoint:
        return False
    checkpoint = str(refresh_checkpoint).strip().lower()
    if "late" in checkpoint or "close" in checkpoint:
        return True
    if not checkpoint.startswith(("14:", "15:")):
        return False
    local = now
    if now.tzinfo is not None:
        try:
            from zoneinfo import ZoneInfo

            local = now.astimezone(ZoneInfo("Asia/Seoul"))
        except Exception:
            local = now
    return (local.hour, local.minute) >= (14, 30)


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
        volume_state="CONFIRMED" if (market.relative_volume or 0.0) >= (contract.min_relative_volume or 0.0) else "UNCONFIRMED",
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
