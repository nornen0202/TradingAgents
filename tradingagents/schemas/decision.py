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


PriceLevelType = Literal["breakout", "support", "pullback", "invalidation", "trim", "resistance"]
PriceLevelConfirmation = Literal["intraday", "close", "two_bar", "next_day"]
FundingPriority = Literal["low", "medium", "high"]

_SOCIAL_SOURCE_ALIASES = {
    "available": SocialSource.DEDICATED.value,
}
_PRICE_LEVEL_TYPES = {"breakout", "support", "pullback", "invalidation", "trim", "resistance"}
_PRICE_LEVEL_CONFIRMATIONS = {"intraday", "close", "two_bar", "next_day"}
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "level_type": self.level_type,
            "price": self.price,
            "low": self.low,
            "high": self.high,
            "currency": self.currency,
            "confirmation": self.confirmation,
            "volume_rule": self.volume_rule,
            "source_text": self.source_text,
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
        '"levels":[{"label":"breakout above 426000","level_type":"breakout","price":426000,"confirmation":"close","volume_rule":"RVOL >= 1.2","source_text":"close above 426,000 with volume"}],'
        '"min_relative_volume":1.2,'
        '"vwap_required":true,'
        '"earliest_pilot_time_local":"10:30",'
        '"funding_priority":"low | medium | high",'
        '"entry_window":"open | mid | late",'
        '"trigger_quality":"weak | medium | strong"}}. '
        "Treat rating as the legacy medium-term investment/allocation view, not the same-day execution action. "
        "Use portfolio_stance for directional view, and entry_action for immediate action today. "
        "Do not use NO_TRADE solely because entry_action is WAIT. "
        "Always include execution_levels as investor-facing execution rules, even when the action is WAIT. "
        "Populate execution_levels.levels with machine-actionable prices or ranges whenever possible. "
        "Use intraday_pilot_rule for a small regular-session starter only, close_confirm_rule for full-size add or entry, "
        "and next_day_followthrough_rule for the next trading day support or re-breakout check. "
        "For execution_levels.levels, level_type must be one of breakout, support, pullback, invalidation, trim, resistance, "
        "and confirmation must be one of intraday, close, two_bar, next_day; put extra nuance in label or source_text. "
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
        min_relative_volume=_optional_float(raw.get("min_relative_volume")),
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
    text = str(value).replace(",", "")
    text = re.sub(r"(?<=\d)\s*[-\u2013\u2014~]\s*(?=\d)", " ", text)
    numbers: list[float] = []
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
        lowered = text.lower()
        has_explicit_range = bool(re.search(r"\d[\d,]*(?:\.\d+)?\s*[-\u2013\u2014~]\s*\d", text))
        has_range_words = any(token in lowered for token in ("zone", "range", "between", "from "))
        if not has_explicit_range and not has_range_words:
            continue
        numbers = _numbers_from_text(text)
        if len(numbers) >= 2:
            first, second = numbers[0], numbers[1]
            return (min(first, second), max(first, second))
    return (None, None)


def _has_multiple_numbers(value: Any) -> bool:
    return len(_numbers_from_text(value)) >= 2


def _normalize_text(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").strip().lower()).strip()


def _normalize_price_level_type(value: Any, raw: Mapping[str, Any]) -> PriceLevelType | None:
    text = _normalize_text(value)
    if text.replace(" ", "_") in _PRICE_LEVEL_TYPES:
        return cast(PriceLevelType, text.replace(" ", "_"))
    context = _normalize_text(
        " ".join(
            str(raw.get(field) or "")
            for field in ("label", "source_text", "level_type", "confirmation")
        )
    )
    haystack = f"{text} {context}".strip()
    if not haystack:
        return None
    if any(token in haystack for token in ("trim", "reduce", "funding source", "take profit")):
        return "trim"
    if any(token in haystack for token in ("invalid", "invalidation", "stop", "fail", "loss", "below")):
        return "invalidation"
    if any(token in haystack for token in ("pullback", "retest", "buy zone", "dip")):
        return "pullback"
    if any(token in haystack for token in ("support", "downside", "floor", "reference")):
        return "support"
    if any(token in haystack for token in ("resistance", "target", "upside", "ceiling")):
        return "resistance"
    if any(token in haystack for token in ("breakout", "trigger", "reclaim", "break above")):
        return "breakout"
    return None


def _normalize_price_level_confirmation(value: Any) -> PriceLevelConfirmation:
    text = _normalize_text(value)
    compact = text.replace(" ", "_")
    if compact in _PRICE_LEVEL_CONFIRMATIONS:
        return cast(PriceLevelConfirmation, compact)
    if not text:
        return "close"
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
    )


def ensure_structured_decision_json(payload: str | Mapping[str, Any]) -> str:
    return parse_structured_decision(payload).to_json()
