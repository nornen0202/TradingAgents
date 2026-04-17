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
            execution_levels = decision.execution_levels
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
                intraday_pilot_rule=execution_levels.intraday_pilot_rule or _default_intraday_pilot_rule(
                    breakout_level=breakout_level,
                    min_relative_volume=min_rvol,
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
        intraday_pilot_rule="장중 신규 진입은 보류하고, 구조적 thesis가 복구될 때까지 관찰합니다.",
        close_confirm_rule="종가 기준 구조적 조건을 다시 확인한 뒤 실행 여부를 판단합니다.",
        next_day_followthrough_rule="다음 거래일 첫 30~60분 동안 핵심 가격대를 회복하는지 확인합니다.",
        failed_breakout_rule="장중 돌파 실패가 확인되면 신규 매수를 금지합니다.",
        trim_rule="보유 중이면 무효화 가격 이탈 또는 리스크 확대 시 축소를 검토합니다.",
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


def _default_intraday_pilot_rule(
    *,
    breakout_level: float | None,
    min_relative_volume: float | None,
) -> str:
    level = _format_level(breakout_level) if breakout_level is not None else "trigger"
    rvol = f" + adjusted RVOL {min_relative_volume:g}배 이상" if min_relative_volume else " + adjusted RVOL 확인"
    return f"10:30 KST 이후 {level} 상회 + VWAP 위{rvol} + 오전 실패 돌파가 아닐 때 30만~60만원 starter만 허용"


def _default_close_confirm_rule(
    *,
    breakout_level: float | None,
    min_relative_volume: float | None,
) -> str:
    level = _format_level(breakout_level) if breakout_level is not None else "핵심 trigger"
    rvol = f"와 RVOL {min_relative_volume:g}배 이상" if min_relative_volume else "와 거래량 확인"
    return f"종가가 {level} 위에서 유지되고 {rvol}가 동반될 때 본격 진입 또는 증액을 검토"


def _default_next_day_followthrough_rule(*, breakout_level: float | None) -> str:
    level = _format_level(breakout_level) if breakout_level is not None else "핵심 trigger"
    return f"다음 거래일 첫 30~60분 동안 {level} 재이탈이 없고 재돌파가 유지될 때 추가 검토"


def _default_failed_breakout_rule(*, breakout_level: float | None) -> str:
    level = _format_level(breakout_level) if breakout_level is not None else "trigger"
    return f"장중 {level} 돌파 후 VWAP 또는 {level} 아래로 재이탈하면 당일 신규 매수 금지"


def _default_trim_rule(*, invalid_close: float | None, invalid_intraday: float | None) -> str:
    invalid = invalid_intraday if invalid_intraday is not None else invalid_close
    if invalid is None:
        return "핵심 지지 이탈 또는 thesis 훼손 뉴스가 확인되면 먼저 축소 후보로 분류"
    return f"{_format_level(invalid)} 이탈이 확인되면 보유분 축소 또는 청산 검토"


def _format_level(value: float | None) -> str:
    if value is None:
        return "trigger"
    if float(value).is_integer():
        return f"{int(value):,}"
    return f"{float(value):,.2f}"
