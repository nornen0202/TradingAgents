from __future__ import annotations

from datetime import datetime

from tradingagents.schemas import (
    ActionIfTriggered,
    BreakoutConfirmation,
    DecisionNow,
    DecisionState,
    ExecutionContract,
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
    }

    staleness_seconds = int(max(0, (now - datetime.fromisoformat(market.asof)).total_seconds()))
    if staleness_seconds > max_data_age_seconds:
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
        )

    if contract.invalid_if_intraday_below is not None and market.last_price < contract.invalid_if_intraday_below:
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
        )

    decision_state = DecisionState.WAIT
    decision_now = DecisionNow.NONE

    if contract.breakout_level is not None and market.last_price >= contract.breakout_level:
        trigger_status["breakout_hit_intraday"] = True
        rvol_ok = contract.min_relative_volume is None or ((market.relative_volume or 0.0) >= contract.min_relative_volume)
        if rvol_ok:
            if contract.breakout_confirmation == BreakoutConfirmation.CLOSE_ABOVE:
                decision_state = DecisionState.TRIGGERED_PENDING_CLOSE
                trigger_status["close_confirmation_pending"] = True
                reason_codes.append("close_confirmation_required")
            else:
                decision_state = DecisionState.ACTIONABLE_NOW
                decision_now = _decision_now_from_action(contract.action_if_triggered)
                reason_codes.append("breakout_confirmed")
        else:
            decision_state = DecisionState.ARMED
            reason_codes.append("relative_volume_unconfirmed")

    if contract.pullback_buy_zone is not None:
        in_zone = contract.pullback_buy_zone.low <= market.last_price <= contract.pullback_buy_zone.high
        if in_zone:
            trigger_status["pullback_zone_active"] = True
            if _vwap_check(contract.session_vwap_preference, market.last_price, market.session_vwap):
                decision_state = DecisionState.ACTIONABLE_NOW
                decision_now = _decision_now_from_action(contract.action_if_triggered)
                reason_codes.append("pullback_zone_actionable")
            else:
                decision_state = DecisionState.ARMED
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
) -> ExecutionUpdate:
    return ExecutionUpdate(
        ticker=contract.ticker,
        analysis_asof=contract.analysis_asof,
        execution_asof=now.isoformat(),
        market_data_asof=market.asof,
        source={"provider": market.provider, "interval": market.interval},
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
    )
