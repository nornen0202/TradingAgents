from __future__ import annotations

import re
from typing import Any, Iterable

from tradingagents.portfolio.instrument_identity import resolve_identity

from .models import ExternalSignalAction


_BUY_WORDS = {"BUY", "BUY_NOW", "ENTER", "ENTRY", "LONG", "매수", "진입"}
_ADD_WORDS = {"ADD", "ADD_NOW", "ACCUMULATE", "증액", "추가매수", "추가 매수"}
_HOLD_WORDS = {"HOLD", "KEEP", "보유", "유지"}
_WATCH_WORDS = {"WATCH", "WAIT", "MONITOR", "관찰", "관망", "대기"}
_TRIM_WORDS = {"TRIM_TO_FUND", "TRIM", "FUNDING_TRIM", "자금마련", "자금 마련"}
_REDUCE_WORDS = {"REDUCE", "REDUCE_RISK", "DE_RISK", "DERISK", "축소", "위험축소", "위험 축소"}
_TAKE_PROFIT_WORDS = {"TAKE_PROFIT", "PROFIT_TAKING", "PROFIT", "익절", "이익실현", "이익 실현"}
_STOP_WORDS = {"STOP_LOSS", "STOP", "CUT_LOSS", "손절"}
_EXIT_WORDS = {"EXIT", "SELL", "CLOSE", "LIQUIDATE", "매도", "청산"}
_NO_ENTRY_WORDS = {"NO_ENTRY", "NO_TRADE", "AVOID", "SKIP", "보류", "회피", "진입없음", "진입 없음"}


def canonicalize_ticker(value: Any, *, display_name: str | None = None, market: str | None = None) -> str | None:
    text = str(value or "").strip()
    name = str(display_name or "").strip() or None
    if not text and not name:
        return None

    for candidate in (text, name):
        if not candidate:
            continue
        try:
            return resolve_identity(candidate, name).canonical_ticker
        except Exception:
            continue

    normalized = text.upper()
    if re.fullmatch(r"\d{6}", normalized):
        suffix = ".KS" if str(market or "").strip().upper() != "KQ" else ".KQ"
        return f"{normalized}{suffix}"
    if normalized:
        return normalized
    return None


def normalize_external_action(value: Any, *, section: str | None = None) -> ExternalSignalAction:
    raw = str(value or "").strip()
    section_text = str(section or "").strip()
    candidates = [raw, raw.upper().replace("-", "_").replace(" ", "_"), section_text, section_text.upper()]
    words = {candidate for candidate in candidates if candidate}
    compact_words = {candidate.replace("_", "").replace(" ", "") for candidate in words}

    if words & _BUY_WORDS or compact_words & {item.replace("_", "").replace(" ", "") for item in _BUY_WORDS}:
        return ExternalSignalAction.BUY
    if words & _ADD_WORDS or compact_words & {item.replace("_", "").replace(" ", "") for item in _ADD_WORDS}:
        return ExternalSignalAction.ADD
    if words & _TRIM_WORDS or compact_words & {item.replace("_", "").replace(" ", "") for item in _TRIM_WORDS}:
        return ExternalSignalAction.TRIM_TO_FUND
    if words & _REDUCE_WORDS or compact_words & {item.replace("_", "").replace(" ", "") for item in _REDUCE_WORDS}:
        return ExternalSignalAction.REDUCE_RISK
    if words & _TAKE_PROFIT_WORDS or compact_words & {item.replace("_", "").replace(" ", "") for item in _TAKE_PROFIT_WORDS}:
        return ExternalSignalAction.TAKE_PROFIT
    if words & _STOP_WORDS or compact_words & {item.replace("_", "").replace(" ", "") for item in _STOP_WORDS}:
        return ExternalSignalAction.STOP_LOSS
    if words & _EXIT_WORDS or compact_words & {item.replace("_", "").replace(" ", "") for item in _EXIT_WORDS}:
        return ExternalSignalAction.EXIT
    if words & _NO_ENTRY_WORDS or compact_words & {item.replace("_", "").replace(" ", "") for item in _NO_ENTRY_WORDS}:
        return ExternalSignalAction.NO_ENTRY
    if words & _HOLD_WORDS or compact_words & {item.replace("_", "").replace(" ", "") for item in _HOLD_WORDS}:
        return ExternalSignalAction.HOLD
    if words & _WATCH_WORDS or compact_words & {item.replace("_", "").replace(" ", "") for item in _WATCH_WORDS}:
        return ExternalSignalAction.WATCH

    section_lower = section_text.lower()
    if "holding" in section_lower:
        return ExternalSignalAction.HOLD
    if "watch" in section_lower or "missed" in section_lower or "opportun" in section_lower:
        return ExternalSignalAction.WATCH
    if "avoided" in section_lower or "loss" in section_lower:
        return ExternalSignalAction.REDUCE_RISK
    return ExternalSignalAction.UNKNOWN


def first_non_empty(mapping: dict[str, Any], keys: Iterable[str]) -> Any:
    for key in keys:
        if key in mapping and mapping[key] not in (None, ""):
            return mapping[key]
    lower_map = {str(key).lower(): value for key, value in mapping.items()}
    for key in keys:
        value = lower_map.get(str(key).lower())
        if value not in (None, ""):
            return value
    return None


def coerce_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "").replace("%", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def coerce_confidence(value: Any) -> float | None:
    number = coerce_float(value)
    if number is None:
        return None
    if number > 1.0 and number <= 100.0:
        number = number / 100.0
    return max(0.0, min(1.0, number))


def coerce_score(value: Any) -> float | None:
    number = coerce_float(value)
    if number is None:
        return None
    if number > 1.0 and number <= 100.0:
        number = number / 100.0
    return number
