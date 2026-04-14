from __future__ import annotations

from datetime import datetime
from typing import Any

from tradingagents.schemas import (
    ActionIfTriggered,
    BreakoutConfirmation,
    EventGuard,
    ExecutionContract,
    LevelBasis,
    PrimarySetup,
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
                breakout_confirmation=BreakoutConfirmation.CLOSE_ABOVE,
                min_relative_volume=1.0,
                session_vwap_preference=SessionVWAPPreference.INDIFFERENT,
                event_guard=EventGuard(),
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
