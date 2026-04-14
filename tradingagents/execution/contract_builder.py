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
            breakout_level = _extract_level((*decision.watchlist_triggers, *decision.catalysts), ("breakout", "above"))
            pullback_low, pullback_high = _extract_zone(
                (*decision.watchlist_triggers, *decision.catalysts),
                keywords=("pullback", "buy zone", "retest"),
            )
            invalid_close = _extract_level(decision.invalidators, ("close", "below"))
            invalid_intraday = _extract_level(decision.invalidators, ("intraday", "below"))
            event_guard = _extract_event_guard((*decision.watchlist_triggers, *decision.catalysts, *decision.invalidators))
            vwap_pref = _extract_vwap_preference((*decision.watchlist_triggers, *decision.catalysts))
            min_rvol = _extract_relative_volume((*decision.watchlist_triggers, *decision.catalysts))
            reason_codes = tuple(_normalize_reason_codes(decision.watchlist_triggers, prefix="trigger"))
            notes = tuple(_normalize_reason_codes(decision.catalysts, prefix="catalyst"))
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
                action_if_triggered=_action_if_triggered(decision.entry_action.value),
                starter_fraction_of_target=(0.25 if decision.entry_action.value == "STARTER" else None),
                breakout_level=breakout_level,
                breakout_confirmation=_breakout_confirmation_from_text((*decision.watchlist_triggers, *decision.catalysts)),
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
                reason_codes=reason_codes,
                notes=notes,
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
    if "above vwap" in joined:
        return SessionVWAPPreference.ABOVE
    if "below vwap" in joined:
        return SessionVWAPPreference.BELOW
    return SessionVWAPPreference.INDIFFERENT


def _extract_relative_volume(lines: tuple[str, ...]) -> float | None:
    for line in lines:
        lowered = line.lower()
        if "relative volume" not in lowered and "rvol" not in lowered:
            continue
        match = re.search(r"(?:rvol|relative volume)\s*[:>=]?\s*(-?\d+(?:\.\d+)?)", lowered)
        if not match:
            numbers = re.findall(r"(-?\d+(?:\.\d+)?)", line)
            if numbers:
                match_value = numbers[-1]
                return max(0.1, float(match_value))
        if match:
            return max(0.1, float(match.group(1)))
    return 1.0


def _breakout_confirmation_from_text(lines: tuple[str, ...]) -> BreakoutConfirmation:
    joined = " ".join(lines).lower()
    if "intraday above" in joined:
        return BreakoutConfirmation.INTRADAY_ABOVE
    if "two bar hold" in joined or "2 bar hold" in joined:
        return BreakoutConfirmation.TWO_BAR_HOLD
    if "end of day" in joined or "eod only" in joined:
        return BreakoutConfirmation.END_OF_DAY_ONLY
    return BreakoutConfirmation.CLOSE_ABOVE
