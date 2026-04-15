from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from json import JSONDecodeError
from typing import Any, Mapping


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


class SocialSource(str, Enum):
    DEDICATED = "dedicated"
    NEWS_DERIVED = "news_derived"
    UNAVAILABLE = "unavailable"


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
        '"data_coverage":{"company_news_count":0,"disclosures_count":0,"social_source":"dedicated | news_derived | unavailable","macro_items_count":0}}. '
        "Treat rating as the legacy medium-term investment/allocation view, not the same-day execution action. "
        "Use portfolio_stance for directional view, and entry_action for immediate action today. "
        "Do not use NO_TRADE solely because entry_action is WAIT. "
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
    try:
        social_source = SocialSource(str(raw_coverage.get("social_source", "unavailable")).strip().lower())
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
    )


def ensure_structured_decision_json(payload: str | Mapping[str, Any]) -> str:
    return parse_structured_decision(payload).to_json()
