from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum
from json import JSONDecodeError
from typing import Any, Literal, Mapping, cast


class StructuredDecisionValidationError(ValueError):
    """Raised when a decision payload does not match the required schema."""


class DecisionRating(str, Enum):
    BUY = "BUY"
    OVERWEIGHT = "OVERWEIGHT"
    HOLD = "HOLD"
    UNDERWEIGHT = "UNDERWEIGHT"
    SELL = "SELL"
    NO_TRADE = "NO_TRADE"


class PortfolioStance(str, Enum):
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    BULLISH = "BULLISH"


class EntryAction(str, Enum):
    NONE = "NONE"
    WAIT = "WAIT"
    STARTER = "STARTER"
    ADD = "ADD"
    EXIT = "EXIT"


class RiskAction(str, Enum):
    NONE = "NONE"
    HOLD = "HOLD"
    TRIM_TO_FUND = "TRIM_TO_FUND"
    REDUCE_RISK = "REDUCE_RISK"
    TAKE_PROFIT = "TAKE_PROFIT"
    STOP_LOSS = "STOP_LOSS"
    EXIT = "EXIT"


class SetupQuality(str, Enum):
    WEAK = "WEAK"
    DEVELOPING = "DEVELOPING"
    COMPELLING = "COMPELLING"


class TimeHorizon(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class EntryWindow(str, Enum):
    OPEN = "open"
    MID = "mid"
    LATE = "late"


class TriggerQuality(str, Enum):
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"


class SocialSource(str, Enum):
    DEDICATED = "dedicated"
    NEWS_DERIVED = "news_derived"
    UNAVAILABLE = "unavailable"


class PriceLevelType(str, Enum):
    BREAKOUT = "BREAKOUT"
    SUPPORT = "SUPPORT"
    PULLBACK = "PULLBACK"
    INVALIDATION = "INVALIDATION"
    TRIM = "TRIM"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"
    RESISTANCE = "RESISTANCE"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.value == other.upper().replace(" ", "_")
        return super().__eq__(other)

    __hash__ = str.__hash__


PriceLevelConfirmation = Literal["intraday", "close", "two_bar", "next_day", "volume_confirmed"]
FundingPriority = Literal["low", "medium", "high"]

_SOCIAL_SOURCE_ALIASES = {
    "available": SocialSource.DEDICATED.value,
}
_PRICE_LEVEL_TYPES = {level.value for level in PriceLevelType}
_PRICE_LEVEL_TYPE_ALIASES = {
    "breakout": PriceLevelType.BREAKOUT,
    "support": PriceLevelType.SUPPORT,
    "pullback": PriceLevelType.PULLBACK,
    "invalidation": PriceLevelType.INVALIDATION,
    "trim": PriceLevelType.TRIM,
    "stop_loss": PriceLevelType.STOP_LOSS,
    "stop": PriceLevelType.STOP_LOSS,
    "take_profit": PriceLevelType.TAKE_PROFIT,
    "profit": PriceLevelType.TAKE_PROFIT,
    "resistance": PriceLevelType.RESISTANCE,
}
_PRICE_LEVEL_CONFIRMATIONS = {"intraday", "close", "two_bar", "next_day", "volume_confirmed"}
_NUMBER_PATTERN = re.compile(r"[-+]?\d*\.?\d+")


@dataclass(frozen=True)
class DataCoverage:
    company_news_count: int
    disclosures_count: int
    social_source: SocialSource
    macro_items_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "company_news_count": self.company_news_count,
            "disclosures_count": self.disclosures_count,
            "social_source": self.social_source.value,
            "macro_items_count": self.macro_items_count,
        }


@dataclass(frozen=True)
class PriceLevel:
    label: str
    level_type: PriceLevelType
    price: float | None = None
    low: float | None = None
    high: float | None = None
    currency: str | None = None
    confirmation: PriceLevelConfirmation = "close"
    volume_rule: str = ""
    source_text: str = ""
    reason_code: str = ""
    level_type_source: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "level_type": self.level_type_source or _price_level_type_value(self.level_type),
            "price": self.price,
            "low": self.low,
            "high": self.high,
            "currency": self.currency,
            "confirmation": self.confirmation,
            "volume_rule": self.volume_rule,
            "source_text": self.source_text,
            "reason_code": self.reason_code,
        }


@dataclass(frozen=True)
class ExecutionLevels:
    intraday_pilot_rule: str = ""
    close_confirm_rule: str = ""
    next_day_followthrough_rule: str = ""
    failed_breakout_rule: str = ""
    trim_rule: str = ""
    levels: tuple[PriceLevel, ...] = tuple()
    min_relative_volume: float | None = None
    vwap_required: bool = False
    earliest_pilot_time_local: str = "10:30"
    funding_priority: FundingPriority = "medium"
    entry_window: EntryWindow = EntryWindow.MID
    trigger_quality: TriggerQuality = TriggerQuality.MEDIUM

    def to_dict(self) -> dict[str, Any]:
        return {
            "intraday_pilot_rule": self.intraday_pilot_rule,
            "close_confirm_rule": self.close_confirm_rule,
            "next_day_followthrough_rule": self.next_day_followthrough_rule,
            "failed_breakout_rule": self.failed_breakout_rule,
            "trim_rule": self.trim_rule,
            "levels": [level.to_dict() for level in self.levels],
            "min_relative_volume": self.min_relative_volume,
            "vwap_required": self.vwap_required,
            "earliest_pilot_time_local": self.earliest_pilot_time_local,
            "funding_priority": self.funding_priority,
            "entry_window": self.entry_window.value,
            "trigger_quality": self.trigger_quality.value,
        }


@dataclass(frozen=True)
class StructuredDecision:
    rating: DecisionRating
    portfolio_stance: PortfolioStance
    entry_action: EntryAction
    setup_quality: SetupQuality
    confidence: float
    time_horizon: TimeHorizon
    entry_logic: str
    exit_logic: str
    position_sizing: str
    risk_limits: str
    catalysts: tuple[str, ...]
    invalidators: tuple[str, ...]
    watchlist_triggers: tuple[str, ...]
    data_coverage: DataCoverage
    execution_levels: ExecutionLevels = ExecutionLevels()
    risk_action: RiskAction = RiskAction.NONE
    risk_action_reason: str = ""
    risk_action_reason_codes: tuple[str, ...] = tuple()
    risk_action_confidence: float | None = None
    risk_action_level: PriceLevel | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "rating": self.rating.value,
            "portfolio_stance": self.portfolio_stance.value,
            "entry_action": self.entry_action.value,
            "setup_quality": self.setup_quality.value,
            "confidence": self.confidence,
            "time_horizon": self.time_horizon.value,
            "entry_logic": self.entry_logic,
            "exit_logic": self.exit_logic,
            "position_sizing": self.position_sizing,
            "risk_limits": self.risk_limits,
            "catalysts": list(self.catalysts),
            "invalidators": list(self.invalidators),
            "watchlist_triggers": list(self.watchlist_triggers),
            "data_coverage": self.data_coverage.to_dict(),
            "execution_levels": self.execution_levels.to_dict(),
            "risk_action": self.risk_action.value,
            "risk_action_reason": self.risk_action_reason,
            "risk_action_reason_codes": list(self.risk_action_reason_codes),
            "risk_action_confidence": self.risk_action_confidence,
            "risk_action_level": self.risk_action_level.to_dict() if self.risk_action_level else None,
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


def build_decision_output_instructions(context: str) -> str:
    return (
        f"Return only one valid JSON object for the {context}. "
        "Do not wrap it in markdown fences. "
        "The schema is: "
        '{"rating":"NO_TRADE | UNDERWEIGHT | HOLD | OVERWEIGHT | BUY | SELL",'
        '"portfolio_stance":"BEARISH | NEUTRAL | BULLISH",'
        '"entry_action":"NONE | WAIT | STARTER | ADD | EXIT",'
        '"risk_action":"NONE | HOLD | TRIM_TO_FUND | REDUCE_RISK | TAKE_PROFIT | STOP_LOSS | EXIT",'
        '"risk_action_reason":"...",'
        '"risk_action_reason_codes":["..."],'
        '"risk_action_confidence":0.0,'
        '"risk_action_level":{"label":"support fail","level_type":"SUPPORT","price":420000,"confirmation":"close","source_text":"close below support","reason_code":"SUPPORT_BROKEN"},'
        '"setup_quality":"WEAK | DEVELOPING | COMPELLING",'
        '"confidence":0.0,'
        '"time_horizon":"short | medium | long",'
        '"entry_logic":"...",'
        '"exit_logic":"...",'
        '"position_sizing":"...",'
        '"risk_limits":"...",'
        '"catalysts":["..."],'
        '"invalidators":["..."],'
        '"watchlist_triggers":["..."],'
        '"data_coverage":{"company_news_count":0,"disclosures_count":0,"social_source":"dedicated | news_derived | unavailable","macro_items_count":0},'
        '"execution_levels":{'
        '"intraday_pilot_rule":"After 10:30 local, allow only a small pilot if trigger, VWAP, and volume conditions are met",'
        '"close_confirm_rule":"Require a close above the trigger before a full add",'
        '"next_day_followthrough_rule":"Next day, keep the trigger during the first 30-60 minutes before adding",'
        '"failed_breakout_rule":"If price loses the trigger or VWAP after breakout, block new buying",'
        '"trim_rule":"Trim if invalidation or failed breakout confirms",'
        '"levels":[{"label":"breakout above 426000","level_type":"BREAKOUT","price":426000,"confirmation":"close","volume_rule":"RVOL >= 1.2","source_text":"close above 426,000 with volume","reason_code":"BREAKOUT_TRIGGER"}],'
        '"min_relative_volume":1.2,'
        '"vwap_required":true,'
        '"earliest_pilot_time_local":"10:30",'
        '"funding_priority":"low | medium | high",'
        '"entry_window":"open | mid | late",'
        '"trigger_quality":"weak | medium | strong"}}. '
        "Treat rating as the legacy medium-term investment/allocation view, not the same-day execution action. "
        "Use portfolio_stance for directional view, and entry_action for immediate action today. "
        "Evaluate both buy-side entry and sell-side/downside risk. "
        "For held positions, explicitly decide whether risk_action should be HOLD, TRIM_TO_FUND, REDUCE_RISK, TAKE_PROFIT, STOP_LOSS, or EXIT. "
        "Use TRIM_TO_FUND only for funding or rotation when the thesis is not invalidated; use REDUCE_RISK, STOP_LOSS, or EXIT for support breaks, invalidation, failed breakout, thesis damage, weak earnings/guidance, regime headwinds, or deteriorated reward/risk. "
        "Use TAKE_PROFIT when the thesis remains valid but an extended move or fading momentum argues for partial de-risking. "
        "Always include risk_action_reason_codes and risk_action_level when a numeric sell-side level exists. "
        "Do not use NO_TRADE solely because entry_action is WAIT. "
        "Always include execution_levels as investor-facing execution rules, even when the action is WAIT. "
        "Populate execution_levels.levels with machine-actionable prices or ranges whenever possible. "
        "Use intraday_pilot_rule for a small regular-session starter only, close_confirm_rule for full-size add or entry, "
        "and next_day_followthrough_rule for the next trading day support or re-breakout check. "
        "For execution_levels.levels, level_type must be one of BREAKOUT, SUPPORT, PULLBACK, INVALIDATION, TRIM, STOP_LOSS, TAKE_PROFIT, RESISTANCE, "
        "and confirmation must be one of intraday, close, two_bar, next_day, volume_confirmed; put extra nuance in label or source_text. "
        "For constructive but unconfirmed setups, prefer HOLD or OVERWEIGHT with portfolio_stance=BULLISH and entry_action=WAIT when the evidence supports watchlist or held exposure. "
        "Reserve NO_TRADE for weak, contradictory, or insufficient theses, no favorable setup to monitor, or data quality gaps that make the view non-investable. "
        "Use BUY or OVERWEIGHT when the thesis is strong and the entry setup is actionable today; do not default to NO_TRADE just because it is available. "
        "Use uppercase enum fields, confidence between 0 and 1 inclusive, and concise but specific strings."
    )


def _extract_json_object(payload: str | Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(payload, Mapping):
        return payload

    if not isinstance(payload, str) or not payload.strip():
        raise StructuredDecisionValidationError("Decision payload must be a non-empty JSON string or mapping.")

    text = payload.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3 and lines[0].startswith("```") and lines[-1].startswith("```"):
            text = "\n".join(lines[1:-1]).strip()

    try:
        parsed = json.loads(text)
        if isinstance(parsed, Mapping):
            return parsed
    except JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            parsed, _ = decoder.raw_decode(text[index:])
        except JSONDecodeError:
            continue
        if isinstance(parsed, Mapping):
            return parsed

    raise StructuredDecisionValidationError("Could not locate a valid JSON object in the decision payload.")


def _require_string(data: Mapping[str, Any], field_name: str) -> str:
    value = data.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise StructuredDecisionValidationError(f"Field '{field_name}' must be a non-empty string.")
    return value.strip()


def _require_string_list(data: Mapping[str, Any], field_name: str) -> tuple[str, ...]:
    value = data.get(field_name)
    if not isinstance(value, list):
        raise StructuredDecisionValidationError(f"Field '{field_name}' must be a list of strings.")

    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise StructuredDecisionValidationError(
                f"Field '{field_name}' must contain only non-empty strings."
            )
        normalized.append(item.strip())
    return tuple(normalized)


def _optional_string_list(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return tuple()
    normalized: list[str] = []
    for item in value:
        text = str(item or "").strip()
        if text:
            normalized.append(text)
    return tuple(normalized)


def _optional_string(value: Any) -> str:
    return str(value or "").strip()


def _optional_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    numbers = _numbers_from_text(value)
    return numbers[0] if numbers else None


def _optional_metric_float(value: Any) -> float | None:
    if value in (None, "") or isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    text = str(value)
    text = re.sub(r"\b20\d{2}[-./]\d{1,2}[-./]\d{1,2}\b", " ", text)
    text = re.sub(r"\b\d{1,2}:\d{2}\b", " ", text)
    for match in _NUMBER_PATTERN.finditer(text):
        token = match.group(0)
        if token in {"+", "-", ".", "+.", "-."}:
            continue
        try:
            return float(token)
        except ValueError:
            continue
    return None


def _optional_bool(value: Any, *, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False
    if any(token in text for token in ("required", "require", "above vwap", "vwap ok", "must")):
        return True
    if any(token in text for token in ("not required", "optional", "ignore", "indifferent")):
        return False
    return default


def _parse_price_level(raw: Mapping[str, Any]) -> PriceLevel:
    level_type = _normalize_price_level_type(raw.get("level_type"), raw)
    if level_type is None:
        raise StructuredDecisionValidationError(f"Unsupported execution level_type: {raw.get('level_type')!r}.")

    confirmation = _normalize_price_level_confirmation(raw.get("confirmation"))

    label = _optional_string(raw.get("label")) or _optional_string(raw.get("source_text")) or level_type
    low = _optional_float(raw.get("low"))
    high = _optional_float(raw.get("high"))
    price = _optional_float(raw.get("price"))
    if low is None or high is None:
        range_low, range_high = _range_from_values(
            raw.get("price"),
            raw.get("low"),
            raw.get("high"),
        )
        if range_low is None or range_high is None:
            range_low, range_high = _range_from_context(
                raw.get("label"),
                raw.get("source_text"),
            )
        if range_low is not None and range_high is not None:
            low = range_low if low is None else low
            high = range_high if high is None else high
            if _has_multiple_numbers(raw.get("price")):
                price = None
    if low is not None and high is not None and low > high:
        low, high = high, low
    if _range_is_incompatible_with_price(price=price, low=low, high=high):
        low = None
        high = None

    return PriceLevel(
        label=label,
        level_type=level_type,
        price=price,
        low=low,
        high=high,
        currency=_optional_string(raw.get("currency")) or None,
        confirmation=confirmation,
        volume_rule=_optional_string(raw.get("volume_rule")),
        source_text=_optional_string(raw.get("source_text")),
        reason_code=_optional_string(raw.get("reason_code")),
        level_type_source=_optional_string(raw.get("level_type")),
    )


def _parse_execution_levels(data: Mapping[str, Any]) -> ExecutionLevels:
    raw = data.get("execution_levels")
    if not isinstance(raw, Mapping):
        return ExecutionLevels()

    entry_window = _normalize_entry_window(raw.get("entry_window"))
    trigger_quality = _normalize_trigger_quality(raw.get("trigger_quality"))

    funding_priority = _normalize_funding_priority(raw.get("funding_priority"))

    level_items: list[PriceLevel] = []
    raw_levels = raw.get("levels")
    if isinstance(raw_levels, list):
        for item in raw_levels:
            if not isinstance(item, Mapping):
                continue
            try:
                level_items.append(_parse_price_level(item))
            except StructuredDecisionValidationError:
                continue

    return ExecutionLevels(
        intraday_pilot_rule=_optional_string(raw.get("intraday_pilot_rule")),
        close_confirm_rule=_optional_string(raw.get("close_confirm_rule")),
        next_day_followthrough_rule=_optional_string(raw.get("next_day_followthrough_rule")),
        failed_breakout_rule=_optional_string(raw.get("failed_breakout_rule")),
        trim_rule=_optional_string(raw.get("trim_rule")),
        levels=tuple(level_items),
        min_relative_volume=_optional_metric_float(raw.get("min_relative_volume")),
        vwap_required=_optional_bool(raw.get("vwap_required"), default=False),
        earliest_pilot_time_local=_optional_string(raw.get("earliest_pilot_time_local")) or "10:30",
        funding_priority=funding_priority,
        entry_window=entry_window,
        trigger_quality=trigger_quality,
    )


def _numbers_from_text(value: Any) -> list[float]:
    if value in (None, "") or isinstance(value, bool):
        return []
    if isinstance(value, int | float):
        return [float(value)]
    text = _strip_non_price_numeric_context(str(value))
    korean_values: list[float] = []
    consumed_spans: list[tuple[int, int]] = []
    for match in re.finditer(r"(\d+(?:\.\d+)?)\s*만\s*([\d,]+)(?=원|\s|~|-|$)", text):
        major = float(match.group(1)) * 10000
        minor = float(str(match.group(2) or 0).replace(",", ""))
        korean_values.append(major + minor)
        consumed_spans.append(match.span())
    text_for_manse = text
    for start, end in reversed(consumed_spans):
        text_for_manse = text_for_manse[:start] + " " * (end - start) + text_for_manse[end:]
    for match in re.finditer(r"(\d+(?:\.\d+)?)\s*만", text_for_manse):
        korean_values.append(float(match.group(1)) * 10000)
    text = re.sub(r"\d+(?:\.\d+)?\s*만\s*[\d,]*", " ", text)
    text = re.sub(r"\b\d{1,2}:\d{2}\b", " ", text)
    text = text.replace(",", "")
    text = re.sub(r"(?<=\d)\s*[-\u2013\u2014~]\s*(?=\d)", " ", text)
    numbers: list[float] = list(korean_values)
    for match in _NUMBER_PATTERN.finditer(text):
        token = match.group(0)
        if token in {"+", "-", ".", "+.", "-."}:
            continue
        try:
            numbers.append(float(token))
        except ValueError:
            continue
    return numbers


def _range_from_values(*values: Any) -> tuple[float | None, float | None]:
    for value in values:
        numbers = _numbers_from_text(value)
        if len(numbers) >= 2:
            first, second = numbers[0], numbers[1]
            return (min(first, second), max(first, second))
    return (None, None)


def _range_from_context(*values: Any) -> tuple[float | None, float | None]:
    for value in values:
        text = str(value or "")
        sanitized = _strip_non_price_numeric_context(text)
        lowered = text.lower()
        has_explicit_range = bool(re.search(r"\d[\d,]*(?:\.\d+)?\s*[-\u2013\u2014~]\s*\d", sanitized))
        has_range_words = any(token in lowered for token in ("zone", "range", "between", "from ", "구간", "~"))
        if not has_explicit_range and not has_range_words:
            continue
        numbers = _numbers_from_text(text)
        if len(numbers) >= 2:
            first, second = numbers[0], numbers[1]
            return (min(first, second), max(first, second))
    return (None, None)


def _has_multiple_numbers(value: Any) -> bool:
    return len(_numbers_from_text(value)) >= 2


def _strip_non_price_numeric_context(text: str) -> str:
    cleaned = str(text or "")
    cleaned = re.sub(r"\b20\d{2}[-./]\d{1,2}[-./]\d{1,2}\b", " ", cleaned)
    cleaned = re.sub(r"\b\d{1,2}\s*월\s*\d{1,2}\s*일\b", " ", cleaned)
    cleaned = re.sub(r"\b\d{1,2}:\d{2}\b", " ", cleaned)
    cleaned = re.sub(r"[-+]?\d+(?:\.\d+)?\s*%", " ", cleaned)
    cleaned = re.sub(
        r"\b(?:rvol|rsi)\s*(?:>=|<=|>|<|=|:)?\s*[-+]?\d+(?:\.\d+)?\b",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"\b\d+(?:\.\d+)?\s*(?:ema|sma|ma)(?=\s|[,.);:]|$)",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"\b\d+(?:\.\d+)?\s*(?:일|day|days|week|weeks|주)(?=\s|[,.);:]|$)",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"\d[\d,]*(?:\.\d+)?\s*(?:주|shares?|shares)(?=\s|[,.);:]|$)",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned


def _range_is_incompatible_with_price(
    *,
    price: float | None,
    low: float | None,
    high: float | None,
) -> bool:
    if price is None or low is None or high is None:
        return False
    largest_range_value = max(abs(float(low)), abs(float(high)))
    if largest_range_value == 0:
        return True
    return float(price) >= 10_000 and largest_range_value < float(price) * 0.2


def _normalize_text(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").strip().lower()).strip()


def _price_level_type_value(value: Any) -> str:
    if isinstance(value, PriceLevelType):
        return value.value
    text = str(value or "").strip()
    if not text:
        return ""
    normalized = text.upper().replace(" ", "_")
    alias = _PRICE_LEVEL_TYPE_ALIASES.get(normalized.lower())
    return text if alias else normalized


def _normalize_price_level_type(value: Any, raw: Mapping[str, Any]) -> PriceLevelType | None:
    text = _normalize_text(value)
    compact = text.replace(" ", "_")
    alias = _PRICE_LEVEL_TYPE_ALIASES.get(compact)
    if alias is not None:
        return alias
    upper = compact.upper()
    if upper in _PRICE_LEVEL_TYPES:
        return PriceLevelType(upper)
    context = _normalize_text(
        " ".join(
            str(raw.get(field) or "")
            for field in ("label", "source_text", "level_type", "confirmation")
        )
    )
    haystack = f"{text} {context}".strip()
    if not haystack:
        return None
    if any(token in haystack for token in ("take profit", "profit target", "take-profit")):
        return PriceLevelType.TAKE_PROFIT
    if any(token in haystack for token in ("stop loss", "stop-loss", "stop out", "loss control")):
        return PriceLevelType.STOP_LOSS
    if any(token in haystack for token in ("trim", "reduce", "funding source")):
        return PriceLevelType.TRIM
    if any(token in haystack for token in ("invalid", "invalidation", "fail", "loss", "below")):
        return PriceLevelType.INVALIDATION
    if any(token in haystack for token in ("pullback", "retest", "buy zone", "dip")):
        return PriceLevelType.PULLBACK
    if any(token in haystack for token in ("support", "downside", "floor", "reference")):
        return PriceLevelType.SUPPORT
    if any(token in haystack for token in ("resistance", "target", "upside", "ceiling")):
        return PriceLevelType.RESISTANCE
    if any(token in haystack for token in ("breakout", "trigger", "reclaim", "break above")):
        return PriceLevelType.BREAKOUT
    return None


def _normalize_price_level_confirmation(value: Any) -> PriceLevelConfirmation:
    text = _normalize_text(value)
    compact = text.replace(" ", "_")
    if compact in _PRICE_LEVEL_CONFIRMATIONS:
        return cast(PriceLevelConfirmation, compact)
    if not text:
        return "close"
    if any(token in text for token in ("volume confirmed", "volume confirmation", "rvol confirmed", "volume_confirmed")):
        return "volume_confirmed"
    if ("two" in text and "bar" in text) or "2 bar" in text or "two_bar" in compact:
        return "two_bar"
    if any(token in text for token in ("next day", "follow through", "followthrough", "next session")):
        return "next_day"
    if any(token in text for token in ("close", "daily", "eod", "end of day", "strong close")):
        return "close"
    if any(token in text for token in ("intraday", "touch", "hold", "reclaim", "stall", "test", "vwap")):
        return "intraday"
    return "close"


def _normalize_funding_priority(value: Any) -> FundingPriority:
    text = _normalize_text(value)
    if "high" in text:
        return "high"
    if "low" in text:
        return "low"
    return "medium"


def _normalize_entry_window(value: Any) -> EntryWindow:
    text = _normalize_text(value)
    if "open" in text:
        return EntryWindow.OPEN
    if "late" in text or "close" in text:
        return EntryWindow.LATE
    return EntryWindow.MID


def _normalize_trigger_quality(value: Any) -> TriggerQuality:
    text = _normalize_text(value)
    if "strong" in text or "high" in text:
        return TriggerQuality.STRONG
    if "weak" in text or "low" in text:
        return TriggerQuality.WEAK
    return TriggerQuality.MEDIUM


def _infer_stance_action_from_rating(rating: DecisionRating) -> tuple[PortfolioStance, EntryAction, SetupQuality]:
    if rating in {DecisionRating.BUY, DecisionRating.OVERWEIGHT}:
        return PortfolioStance.BULLISH, EntryAction.ADD, SetupQuality.COMPELLING
    if rating == DecisionRating.HOLD:
        return PortfolioStance.NEUTRAL, EntryAction.WAIT, SetupQuality.DEVELOPING
    if rating in {DecisionRating.UNDERWEIGHT, DecisionRating.SELL}:
        return PortfolioStance.BEARISH, EntryAction.EXIT, SetupQuality.WEAK
    return PortfolioStance.NEUTRAL, EntryAction.NONE, SetupQuality.DEVELOPING


def _infer_risk_action_from_legacy(
    *,
    rating: DecisionRating,
    portfolio_stance: PortfolioStance,
    entry_action: EntryAction,
    setup_quality: SetupQuality,
    data: Mapping[str, Any],
) -> tuple[RiskAction, tuple[str, ...], str]:
    text_blob = " ".join(
        str(data.get(field) or "")
        for field in (
            "risk_action_reason",
            "exit_logic",
            "risk_limits",
            "invalidators",
            "watchlist_triggers",
            "catalysts",
        )
    ).lower()
    has_true_risk_condition = any(
        token in text_blob
        for token in (
            "support",
            "invalidation",
            "invalidat",
            "stop",
            "loss",
            "failed breakout",
            "breakout fail",
            "guidance",
            "earnings miss",
            "thesis",
            "below",
            "breach",
            "broken",
        )
    )
    portfolio_relative = str(data.get("portfolio_relative_action") or "").strip().upper()
    if portfolio_relative == RiskAction.TRIM_TO_FUND.value and not has_true_risk_condition:
        return RiskAction.NONE, tuple(), ""
    if rating == DecisionRating.SELL and entry_action == EntryAction.EXIT:
        return RiskAction.EXIT, ("LEGACY_SELL_EXIT",), "Legacy SELL rating with EXIT entry action."
    if (
        rating == DecisionRating.UNDERWEIGHT
        or portfolio_stance == PortfolioStance.BEARISH
        or setup_quality == SetupQuality.WEAK
    ) and has_true_risk_condition:
        return RiskAction.REDUCE_RISK, ("LEGACY_WEAK_RISK_SETUP",), "Legacy weak/bearish setup with downside-risk evidence."
    return RiskAction.NONE, tuple(), ""


def _parse_risk_action(
    *,
    data: Mapping[str, Any],
    rating: DecisionRating,
    portfolio_stance: PortfolioStance,
    entry_action: EntryAction,
    setup_quality: SetupQuality,
) -> tuple[RiskAction, str, tuple[str, ...], float | None, PriceLevel | None]:
    fallback_action, fallback_codes, fallback_reason = _infer_risk_action_from_legacy(
        rating=rating,
        portfolio_stance=portfolio_stance,
        entry_action=entry_action,
        setup_quality=setup_quality,
        data=data,
    )
    raw_action = str(data.get("risk_action") or "").strip().upper()
    if not raw_action:
        risk_action = fallback_action
    else:
        try:
            risk_action = RiskAction(raw_action)
        except ValueError as exc:
            raise StructuredDecisionValidationError(f"Unsupported risk action: {data.get('risk_action')!r}.") from exc

    reason = _optional_string(data.get("risk_action_reason")) or fallback_reason
    reason_codes = _optional_string_list(data.get("risk_action_reason_codes")) or fallback_codes
    confidence = _optional_float(data.get("risk_action_confidence"))
    if confidence is not None and not 0.0 <= confidence <= 1.0:
        raise StructuredDecisionValidationError("Field 'risk_action_confidence' must be between 0 and 1 inclusive.")

    risk_level = None
    raw_level = data.get("risk_action_level")
    if isinstance(raw_level, Mapping):
        try:
            risk_level = _parse_price_level(raw_level)
        except StructuredDecisionValidationError:
            risk_level = None
    if risk_level is None and risk_action in {RiskAction.REDUCE_RISK, RiskAction.STOP_LOSS, RiskAction.EXIT}:
        for level in _parse_execution_levels(data).levels:
            normalized = _price_level_type_value(level.level_type)
            if normalized in {
                PriceLevelType.SUPPORT.value,
                PriceLevelType.INVALIDATION.value,
                PriceLevelType.STOP_LOSS.value,
                PriceLevelType.TRIM.value,
            }:
                risk_level = level
                break
    return risk_action, reason, tuple(dict.fromkeys(reason_codes)), confidence, risk_level


def parse_structured_decision(payload: str | Mapping[str, Any]) -> StructuredDecision:
    data = _extract_json_object(payload)
    missing_fields = {
        "rating",
        "confidence",
        "time_horizon",
        "entry_logic",
        "exit_logic",
        "position_sizing",
        "risk_limits",
        "catalysts",
        "invalidators",
    } - set(data.keys())
    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise StructuredDecisionValidationError(f"Decision payload is missing required fields: {missing}.")

    try:
        rating = DecisionRating(str(data["rating"]).strip().upper())
    except ValueError as exc:
        raise StructuredDecisionValidationError(f"Unsupported rating: {data.get('rating')!r}.") from exc

    try:
        confidence = float(data["confidence"])
    except (TypeError, ValueError) as exc:
        raise StructuredDecisionValidationError("Field 'confidence' must be numeric.") from exc
    if not 0.0 <= confidence <= 1.0:
        raise StructuredDecisionValidationError("Field 'confidence' must be between 0 and 1 inclusive.")

    try:
        time_horizon = TimeHorizon(str(data["time_horizon"]).strip().lower())
    except ValueError as exc:
        raise StructuredDecisionValidationError(
            f"Unsupported time horizon: {data.get('time_horizon')!r}."
        ) from exc

    inferred_stance, inferred_entry, inferred_setup = _infer_stance_action_from_rating(rating)

    try:
        portfolio_stance = PortfolioStance(str(data.get("portfolio_stance", inferred_stance.value)).strip().upper())
    except ValueError as exc:
        raise StructuredDecisionValidationError(
            f"Unsupported portfolio stance: {data.get('portfolio_stance')!r}."
        ) from exc

    try:
        entry_action = EntryAction(str(data.get("entry_action", inferred_entry.value)).strip().upper())
    except ValueError as exc:
        raise StructuredDecisionValidationError(
            f"Unsupported entry action: {data.get('entry_action')!r}."
        ) from exc

    try:
        setup_quality = SetupQuality(str(data.get("setup_quality", inferred_setup.value)).strip().upper())
    except ValueError as exc:
        raise StructuredDecisionValidationError(
            f"Unsupported setup quality: {data.get('setup_quality')!r}."
        ) from exc

    risk_action, risk_action_reason, risk_action_reason_codes, risk_action_confidence, risk_action_level = _parse_risk_action(
        data=data,
        rating=rating,
        portfolio_stance=portfolio_stance,
        entry_action=entry_action,
        setup_quality=setup_quality,
    )

    raw_coverage = data.get("data_coverage") if isinstance(data.get("data_coverage"), Mapping) else {}
    social_source_raw = str(raw_coverage.get("social_source", "unavailable")).strip().lower()
    social_source_raw = _SOCIAL_SOURCE_ALIASES.get(social_source_raw, social_source_raw)
    try:
        social_source = SocialSource(social_source_raw)
    except ValueError as exc:
        raise StructuredDecisionValidationError(
            f"Unsupported social source: {raw_coverage.get('social_source')!r}."
        ) from exc

    return StructuredDecision(
        rating=rating,
        portfolio_stance=portfolio_stance,
        entry_action=entry_action,
        setup_quality=setup_quality,
        confidence=confidence,
        time_horizon=time_horizon,
        entry_logic=_require_string(data, "entry_logic"),
        exit_logic=_require_string(data, "exit_logic"),
        position_sizing=_require_string(data, "position_sizing"),
        risk_limits=_require_string(data, "risk_limits"),
        catalysts=_require_string_list(data, "catalysts"),
        invalidators=_require_string_list(data, "invalidators"),
        watchlist_triggers=_require_string_list(data, "watchlist_triggers") if "watchlist_triggers" in data else tuple(),
        data_coverage=DataCoverage(
            company_news_count=max(0, int(raw_coverage.get("company_news_count", 0) or 0)),
            disclosures_count=max(0, int(raw_coverage.get("disclosures_count", 0) or 0)),
            social_source=social_source,
            macro_items_count=max(0, int(raw_coverage.get("macro_items_count", 0) or 0)),
        ),
        execution_levels=_parse_execution_levels(data),
        risk_action=risk_action,
        risk_action_reason=risk_action_reason,
        risk_action_reason_codes=risk_action_reason_codes,
        risk_action_confidence=risk_action_confidence,
        risk_action_level=risk_action_level,
    )


def ensure_structured_decision_json(payload: str | Mapping[str, Any]) -> str:
    return parse_structured_decision(payload).to_json()
