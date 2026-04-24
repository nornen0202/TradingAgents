from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from tradingagents.schemas import (
    ActionIfTriggered,
    BreakoutConfirmation,
    EventGuard,
    ExecutionContract,
    LevelBasis,
    PriceLevel,
    PrimarySetup,
    PullbackBuyZone,
    SessionVWAPPreference,
    ThesisState,
    parse_structured_decision,
)


def build_execution_contract(*, ticker: str, analysis_payload: dict[str, Any]) -> ExecutionContract:
    decision_payload = analysis_payload.get("decision")
    analysis_asof = str(analysis_payload.get("finished_at") or analysis_payload.get("started_at") or datetime.now().isoformat())
    market_data_asof = str(analysis_payload.get("trade_date") or analysis_payload.get("analysis_date") or analysis_asof)

    if isinstance(decision_payload, str) and decision_payload.strip().startswith("{"):
        try:
            decision = parse_structured_decision(decision_payload)
            execution_levels = decision.execution_levels
            structured_levels = execution_levels.levels

            breakout_structured = _find_level(structured_levels, "breakout", "resistance")
            pullback_structured = _find_level(structured_levels, "pullback", "support")
            invalid_close_structured = _find_invalidation_level(structured_levels, confirmation="close")
            invalid_intraday_structured = _find_invalidation_level(structured_levels, confirmation="intraday")

            used_regex_fallback = False
            breakout_level = _price_from_level(breakout_structured)
            if breakout_level is None:
                breakout_level = _extract_level((*decision.watchlist_triggers, *decision.catalysts), ("breakout", "above"))
                used_regex_fallback = used_regex_fallback or breakout_level is not None

            pullback_low, pullback_high = _zone_from_level(pullback_structured)
            if pullback_low is None or pullback_high is None:
                fallback_low, fallback_high = _extract_zone(
                    (*decision.watchlist_triggers, *decision.catalysts),
                    keywords=("pullback", "buy zone", "retest"),
                )
                if fallback_low is not None and fallback_high is not None:
                    pullback_low, pullback_high = fallback_low, fallback_high
                    used_regex_fallback = True

            invalid_close = _price_from_level(invalid_close_structured)
            if invalid_close is None:
                invalid_close = _extract_level(decision.invalidators, ("close", "below"))
                used_regex_fallback = used_regex_fallback or invalid_close is not None

            invalid_intraday = _price_from_level(invalid_intraday_structured)
            if invalid_intraday is None:
                invalid_intraday = _extract_level(decision.invalidators, ("intraday", "below"))
                used_regex_fallback = used_regex_fallback or invalid_intraday is not None

            event_guard = _extract_event_guard((*decision.watchlist_triggers, *decision.catalysts, *decision.invalidators))
            vwap_pref = (
                SessionVWAPPreference.ABOVE
                if execution_levels.vwap_required
                else _extract_vwap_preference((*decision.watchlist_triggers, *decision.catalysts))
            )
            min_rvol = execution_levels.min_relative_volume
            if min_rvol is None:
                min_rvol = _extract_relative_volume(
                    (
                        *decision.watchlist_triggers,
                        *decision.catalysts,
                        *(level.volume_rule for level in structured_levels if level.volume_rule),
                    )
                )
                used_regex_fallback = used_regex_fallback or min_rvol is not None

            breakout_confirmation = _breakout_confirmation(
                breakout_structured,
                (*decision.watchlist_triggers, *decision.catalysts),
            )
            reason_codes = list(_normalize_reason_codes(decision.watchlist_triggers, prefix="trigger"))
            notes = list(_normalize_reason_codes(decision.catalysts, prefix="catalyst"))
            if used_regex_fallback:
                reason_codes.append("execution_level_regex_fallback")

            actionable_defined = _has_machine_actionable_level(
                structured_levels=structured_levels,
                breakout_level=breakout_level,
                pullback_low=pullback_low,
                pullback_high=pullback_high,
                invalid_close=invalid_close,
                invalid_intraday=invalid_intraday,
            )
            action_if_triggered = _action_if_triggered(decision.entry_action.value)
            if (
                (
                    action_if_triggered != ActionIfTriggered.NONE
                    or (
                        str(decision.portfolio_stance.value).upper() == "BULLISH"
                        and str(decision.entry_action.value).upper() == "WAIT"
                    )
                )
                and not actionable_defined
            ):
                reason_codes.append("no_machine_actionable_level")

            return ExecutionContract(
                ticker=ticker,
                analysis_asof=analysis_asof,
                market_data_asof=market_data_asof,
                level_basis=LevelBasis.DAILY_CLOSE,
                thesis_state=_thesis_from_stance(decision.portfolio_stance.value),
                primary_setup=_setup_from_entry_action(decision.entry_action.value),
                portfolio_stance=decision.portfolio_stance.value,
                entry_action_base=decision.entry_action.value,
                setup_quality=decision.setup_quality.value,
                confidence=decision.confidence,
                action_if_triggered=action_if_triggered,
                starter_fraction_of_target=(0.25 if decision.entry_action.value == "STARTER" else None),
                breakout_level=breakout_level,
                breakout_confirmation=breakout_confirmation,
                pullback_buy_zone=(
                    None
                    if pullback_low is None or pullback_high is None
                    else PullbackBuyZone(low=pullback_low, high=pullback_high)
                ),
                invalid_if_close_below=invalid_close,
                invalid_if_intraday_below=invalid_intraday,
                min_relative_volume=min_rvol,
                session_vwap_preference=vwap_pref,
                event_guard=event_guard,
                reason_codes=tuple(dict.fromkeys(reason_codes)),
                notes=tuple(dict.fromkeys(notes)),
                structured_levels=structured_levels,
                vwap_required=execution_levels.vwap_required,
                earliest_pilot_time_local=execution_levels.earliest_pilot_time_local,
                intraday_pilot_rule=execution_levels.intraday_pilot_rule or _default_intraday_pilot_rule(
                    breakout_level=breakout_level,
                    min_relative_volume=min_rvol,
                    earliest_pilot_time_local=execution_levels.earliest_pilot_time_local,
                    vwap_required=execution_levels.vwap_required,
                ),
                close_confirm_rule=execution_levels.close_confirm_rule or _default_close_confirm_rule(
                    breakout_level=breakout_level,
                    min_relative_volume=min_rvol,
                ),
                next_day_followthrough_rule=(
                    execution_levels.next_day_followthrough_rule
                    or _default_next_day_followthrough_rule(breakout_level=breakout_level)
                ),
                failed_breakout_rule=execution_levels.failed_breakout_rule or _default_failed_breakout_rule(
                    breakout_level=breakout_level,
                ),
                trim_rule=execution_levels.trim_rule or _default_trim_rule(
                    invalid_close=invalid_close,
                    invalid_intraday=invalid_intraday,
                ),
                funding_priority=execution_levels.funding_priority,
                entry_window=execution_levels.entry_window.value,
                trigger_quality=execution_levels.trigger_quality.value,
            )
        except Exception:
            pass

    return ExecutionContract(
        ticker=ticker,
        analysis_asof=analysis_asof,
        market_data_asof=market_data_asof,
        level_basis=LevelBasis.DAILY_CLOSE,
        thesis_state=ThesisState.NEUTRAL,
        primary_setup=PrimarySetup.WATCH_ONLY,
        portfolio_stance="NEUTRAL",
        entry_action_base="WAIT",
        setup_quality="DEVELOPING",
        confidence=0.4,
        action_if_triggered=ActionIfTriggered.NONE,
        reason_codes=("fallback_contract",),
        notes=("Structured decision unavailable; fail-closed watch mode.",),
        vwap_required=False,
        earliest_pilot_time_local="10:30",
        intraday_pilot_rule="Allow only a small pilot after confirmation; otherwise keep the idea on watch.",
        close_confirm_rule="Recheck the trigger and volume at the close before upgrading the setup.",
        next_day_followthrough_rule="Next session, keep the trigger during the first 30-60 minutes before adding.",
        failed_breakout_rule="If the breakout fails, block new buying and reassess risk.",
        trim_rule="Trim if the invalidation level or failed breakout confirms.",
        funding_priority="low",
        entry_window="mid",
        trigger_quality="weak",
    )


def _thesis_from_stance(stance: str) -> ThesisState:
    mapping = {
        "BULLISH": ThesisState.CONSTRUCTIVE,
        "NEUTRAL": ThesisState.NEUTRAL,
        "BEARISH": ThesisState.FRAGILE,
    }
    return mapping.get(str(stance).upper(), ThesisState.NEUTRAL)


def _setup_from_entry_action(entry_action: str) -> PrimarySetup:
    normalized = str(entry_action).upper()
    if normalized in {"ADD", "STARTER"}:
        return PrimarySetup.BREAKOUT_CONFIRMATION
    if normalized == "WAIT":
        return PrimarySetup.WATCH_ONLY
    if normalized == "EXIT":
        return PrimarySetup.RANGE_RECLAIM
    return PrimarySetup.WATCH_ONLY


def _action_if_triggered(entry_action: str) -> ActionIfTriggered:
    normalized = str(entry_action).upper()
    mapping = {
        "STARTER": ActionIfTriggered.STARTER,
        "ADD": ActionIfTriggered.ADD,
        "EXIT": ActionIfTriggered.EXIT,
    }
    return mapping.get(normalized, ActionIfTriggered.NONE)


def _normalize_reason_codes(values: tuple[str, ...], *, prefix: str) -> list[str]:
    normalized: list[str] = []
    for value in values:
        code = value.strip().lower().replace(" ", "_")
        if not code:
            continue
        normalized.append(f"{prefix}:{code[:60]}")
    return normalized


def _find_level(levels: tuple[PriceLevel, ...], *level_types: str) -> PriceLevel | None:
    allowed = {str(level_type).strip().lower() for level_type in level_types}
    for level in levels:
        if level.level_type in allowed:
            return level
    return None


def _find_invalidation_level(levels: tuple[PriceLevel, ...], *, confirmation: str) -> PriceLevel | None:
    for level in levels:
        if level.level_type not in {"invalidation", "trim"}:
            continue
        if str(level.confirmation).strip().lower() == confirmation:
            return level
    return None


def _price_from_level(level: PriceLevel | None) -> float | None:
    if level is None:
        return None
    if level.price is not None:
        return float(level.price)
    if level.low is not None and level.high is not None:
        return float(min(level.low, level.high))
    if level.low is not None:
        return float(level.low)
    if level.high is not None:
        return float(level.high)
    return None


def _zone_from_level(level: PriceLevel | None) -> tuple[float | None, float | None]:
    if level is None:
        return (None, None)
    if level.low is not None and level.high is not None:
        return (float(min(level.low, level.high)), float(max(level.low, level.high)))
    if level.price is not None:
        value = float(level.price)
        return (value, value)
    if level.low is not None:
        value = float(level.low)
        return (value, value)
    if level.high is not None:
        value = float(level.high)
        return (value, value)
    return (None, None)


def _has_machine_actionable_level(
    *,
    structured_levels: tuple[PriceLevel, ...],
    breakout_level: float | None,
    pullback_low: float | None,
    pullback_high: float | None,
    invalid_close: float | None,
    invalid_intraday: float | None,
) -> bool:
    if structured_levels:
        for level in structured_levels:
            if level.price is not None or level.low is not None or level.high is not None:
                return True
    return any(value is not None for value in (breakout_level, pullback_low, pullback_high, invalid_close, invalid_intraday))


def _extract_level(lines: tuple[str, ...], keywords: tuple[str, ...]) -> float | None:
    for line in lines:
        lowered = line.lower()
        if not all(keyword in lowered for keyword in keywords):
            continue
        match = re.search(r"(-?\d+(?:\.\d+)?)", line)
        if match:
            return float(match.group(1))
    return None


def _extract_zone(lines: tuple[str, ...], *, keywords: tuple[str, ...]) -> tuple[float | None, float | None]:
    for line in lines:
        lowered = line.lower()
        if not any(keyword in lowered for keyword in keywords):
            continue
        numbers = re.findall(r"(-?\d+(?:\.\d+)?)", line)
        if len(numbers) >= 2:
            first = float(numbers[0])
            second = float(numbers[1])
            return (min(first, second), max(first, second))
    return (None, None)


def _extract_event_guard(lines: tuple[str, ...]) -> EventGuard:
    joined = " ".join(lines).lower()
    earnings_date = None
    date_match = re.search(r"(20\d{2}-\d{2}-\d{2})", joined)
    if date_match and "earnings" in joined:
        earnings_date = date_match.group(1)
    block_days = 0
    if "before earnings" in joined or "pre-earnings" in joined:
        block_days = 1
    return EventGuard(
        earnings_date=earnings_date,
        block_new_position_within_days=block_days,
        allow_add_only_after_event=("add only after earnings" in joined),
        requires_post_event_rerun=("earnings" in joined or "guidance" in joined),
    )


def _extract_vwap_preference(lines: tuple[str, ...]) -> SessionVWAPPreference:
    joined = " ".join(lines).lower()
    if "above vwap" in joined or "vwap above" in joined:
        return SessionVWAPPreference.ABOVE
    if "below vwap" in joined:
        return SessionVWAPPreference.BELOW
    return SessionVWAPPreference.INDIFFERENT


def _extract_relative_volume(lines: tuple[str, ...]) -> float | None:
    for line in lines:
        lowered = line.lower()
        if "relative volume" not in lowered and "rvol" not in lowered and "volume_rule" not in lowered:
            continue
        match = re.search(r"(?:rvol|relative volume)[^0-9-]*(-?\d+(?:\.\d+)?)", lowered)
        if match:
            return max(0.1, float(match.group(1)))
        numbers = re.findall(r"(-?\d+(?:\.\d+)?)", line)
        if numbers:
            return max(0.1, float(numbers[-1]))
    return None


def _breakout_confirmation(level: PriceLevel | None, lines: tuple[str, ...]) -> BreakoutConfirmation:
    if level is not None:
        mapping = {
            "intraday": BreakoutConfirmation.INTRADAY_ABOVE,
            "close": BreakoutConfirmation.CLOSE_ABOVE,
            "two_bar": BreakoutConfirmation.TWO_BAR_HOLD,
            "next_day": BreakoutConfirmation.END_OF_DAY_ONLY,
        }
        return mapping.get(level.confirmation, BreakoutConfirmation.CLOSE_ABOVE)
    return _breakout_confirmation_from_text(lines)


def _breakout_confirmation_from_text(lines: tuple[str, ...]) -> BreakoutConfirmation:
    joined = " ".join(lines).lower()
    if "intraday above" in joined:
        return BreakoutConfirmation.INTRADAY_ABOVE
    if "two bar hold" in joined or "2 bar hold" in joined:
        return BreakoutConfirmation.TWO_BAR_HOLD
    if "end of day" in joined or "eod only" in joined:
        return BreakoutConfirmation.END_OF_DAY_ONLY
    return BreakoutConfirmation.CLOSE_ABOVE


def _default_intraday_pilot_rule(
    *,
    breakout_level: float | None,
    min_relative_volume: float | None,
    earliest_pilot_time_local: str | None,
    vwap_required: bool,
) -> str:
    level = _format_level(breakout_level) if breakout_level is not None else "the trigger"
    time_gate = earliest_pilot_time_local or "10:30"
    vwap_text = " with price above VWAP" if vwap_required else ""
    rvol_text = f" and RVOL >= {min_relative_volume:g}" if min_relative_volume else " and volume confirmation"
    return f"After {time_gate} local, allow only a small pilot if price clears {level}{vwap_text}{rvol_text}."


def _default_close_confirm_rule(
    *,
    breakout_level: float | None,
    min_relative_volume: float | None,
) -> str:
    level = _format_level(breakout_level) if breakout_level is not None else "the trigger"
    rvol_text = f" with RVOL >= {min_relative_volume:g}" if min_relative_volume else " with volume confirmation"
    return f"Require a close above {level}{rvol_text} before a full add."


def _default_next_day_followthrough_rule(*, breakout_level: float | None) -> str:
    level = _format_level(breakout_level) if breakout_level is not None else "the trigger"
    return f"Next session, keep {level} during the first 30-60 minutes before adding."


def _default_failed_breakout_rule(*, breakout_level: float | None) -> str:
    level = _format_level(breakout_level) if breakout_level is not None else "the trigger"
    return f"If price loses {level} after breakout, block new buying and reassess funding sources."


def _default_trim_rule(*, invalid_close: float | None, invalid_intraday: float | None) -> str:
    invalid = invalid_intraday if invalid_intraday is not None else invalid_close
    if invalid is None:
        return "Trim if the thesis invalidates or a failed breakout confirms."
    return f"Trim if price loses {_format_level(invalid)} on the relevant confirmation basis."


def _format_level(value: float | None) -> str:
    if value is None:
        return "the trigger"
    if float(value).is_integer():
        return f"{int(value):,}"
    return f"{float(value):,.2f}"
