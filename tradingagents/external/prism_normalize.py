from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from typing import Any, Iterable

from .prism_models import PrismSignalAction


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


def infer_market_from_ticker(value: Any) -> str | None:
    symbol = str(value or "").strip().upper()
    if not symbol:
        return None
    if symbol.endswith((".KS", ".KQ")):
        return "KR"
    if re.fullmatch(r"\d{6}", symbol):
        return "KR"
    if re.fullmatch(r"[A-Z][A-Z0-9.-]{0,9}", symbol):
        return "US"
    return None


def canonicalize_ticker(value: Any, *, display_name: str | None = None, market: str | None = None) -> str | None:
    text = str(value or "").strip()
    name = str(display_name or "").strip() or None
    if not text and not name:
        return None

    for candidate in (text, name):
        if not candidate:
            continue
        try:
            from tradingagents.portfolio.instrument_identity import resolve_identity

            return resolve_identity(candidate, name).canonical_ticker
        except Exception:
            continue

    normalized = text.upper()
    if re.fullmatch(r"\d{6}", normalized):
        suffix = ".KQ" if str(market or "").strip().upper() == "KQ" else ".KS"
        return f"{normalized}{suffix}"
    return normalized or None


def normalize_market(value: Any, *, ticker: str | None = None) -> str:
    inferred = infer_market_from_ticker(ticker)
    if inferred:
        return inferred
    text = str(value or "").strip().upper()
    if text in {"KR", "KOREA", "KRX", "KQ", "KS"}:
        return "KR"
    if text in {"US", "USA", "NASDAQ", "NYSE", "AMEX"}:
        return "US"
    return "UNKNOWN"


def normalize_market_with_warnings(
    value: Any,
    *,
    ticker: str | None = None,
    default_market: str | None = None,
) -> tuple[str, list[str]]:
    warnings: list[str] = []
    inferred = infer_market_from_ticker(ticker)
    explicit = _market_from_text(value)
    default = _market_from_text(default_market)
    if inferred:
        if explicit and explicit != inferred:
            warnings.append("market_conflict_overridden")
        elif default and default != inferred:
            warnings.append("market_inferred_from_ticker")
        return inferred, warnings
    if explicit:
        return explicit, warnings
    if default:
        return default, warnings
    return "UNKNOWN", warnings


def _market_from_text(value: Any) -> str | None:
    text = str(value or "").strip().upper()
    if text in {"KR", "KOREA", "KRX", "KQ", "KS"}:
        return "KR"
    if text in {"US", "USA", "NASDAQ", "NYSE", "AMEX"}:
        return "US"
    return None


def normalize_action(value: Any, *, section: str | None = None) -> PrismSignalAction:
    raw = str(value or "").strip()
    section_text = str(section or "").strip()
    candidates = [raw, raw.upper().replace("-", "_").replace(" ", "_"), section_text, section_text.upper()]
    words = {candidate for candidate in candidates if candidate}
    compact_words = {candidate.replace("_", "").replace(" ", "") for candidate in words}

    def _matches(values: set[str]) -> bool:
        compact_values = {item.replace("_", "").replace(" ", "") for item in values}
        return bool(words & values or compact_words & compact_values)

    if _matches(_BUY_WORDS):
        return PrismSignalAction.BUY
    if _matches(_ADD_WORDS):
        return PrismSignalAction.ADD
    if _matches(_TRIM_WORDS):
        return PrismSignalAction.TRIM_TO_FUND
    if _matches(_REDUCE_WORDS):
        return PrismSignalAction.REDUCE_RISK
    if _matches(_TAKE_PROFIT_WORDS):
        return PrismSignalAction.TAKE_PROFIT
    if _matches(_STOP_WORDS):
        return PrismSignalAction.STOP_LOSS
    if _matches(_EXIT_WORDS):
        return PrismSignalAction.SELL if "SELL" in words or "매도" in words else PrismSignalAction.EXIT
    if _matches(_NO_ENTRY_WORDS):
        return PrismSignalAction.NO_ENTRY
    if _matches(_HOLD_WORDS):
        return PrismSignalAction.HOLD
    if _matches(_WATCH_WORDS):
        return PrismSignalAction.WATCH

    section_lower = section_text.lower()
    if "sell" in section_lower:
        return PrismSignalAction.SELL
    if "holding" in section_lower or "portfolio" in section_lower:
        return PrismSignalAction.HOLD
    if "watch" in section_lower or "missed" in section_lower or "opportun" in section_lower:
        return PrismSignalAction.WATCH
    if "avoided" in section_lower or "loss" in section_lower:
        return PrismSignalAction.REDUCE_RISK
    return PrismSignalAction.UNKNOWN


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


def optional_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def coerce_float(value: Any) -> float | None:
    if value in (None, "") or isinstance(value, bool):
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


def coerce_int(value: Any) -> int | None:
    number = coerce_float(value)
    return None if number is None else int(number)


def coerce_unit_interval(value: Any) -> float | None:
    number = coerce_float(value)
    if number is None:
        return None
    if 1.0 < number <= 100.0:
        number = number / 100.0
    return max(0.0, min(1.0, number))


def parse_datetime(value: Any) -> datetime | None:
    text = optional_text(value)
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def json_safe(value: Any) -> Any:
    try:
        json.dumps(value, ensure_ascii=False)
        return value
    except TypeError:
        if isinstance(value, dict):
            return {str(key): json_safe(item) for key, item in value.items()}
        if isinstance(value, list):
            return [json_safe(item) for item in value]
        if isinstance(value, tuple):
            return [json_safe(item) for item in value]
        return str(value)


def payload_hash(payload: Any) -> str:
    encoded = json.dumps(json_safe(payload), sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
