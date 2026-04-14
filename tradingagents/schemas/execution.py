from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any


class ExecutionValidationError(ValueError):
    """Raised when execution payload validation fails."""


class LevelBasis(str, Enum):
    DAILY_CLOSE = "daily_close"
    INTRADAY_SNAPSHOT = "intraday_snapshot"
    EVENT_POST_EARNINGS = "event_post_earnings"


class ThesisState(str, Enum):
    CONSTRUCTIVE = "constructive"
    NEUTRAL = "neutral"
    FRAGILE = "fragile"
    INVALID = "invalid"


class PrimarySetup(str, Enum):
    BREAKOUT_CONFIRMATION = "breakout_confirmation"
    PULLBACK_BUY = "pullback_buy"
    RANGE_RECLAIM = "range_reclaim"
    WATCH_ONLY = "watch_only"
    EVENT_POST_EARNINGS = "event_post_earnings"


class ActionIfTriggered(str, Enum):
    NONE = "NONE"
    STARTER = "STARTER"
    ADD = "ADD"
    REDUCE = "REDUCE"
    EXIT = "EXIT"


class BreakoutConfirmation(str, Enum):
    CLOSE_ABOVE = "close_above"
    INTRADAY_ABOVE = "intraday_above"
    TWO_BAR_HOLD = "two_bar_hold"
    END_OF_DAY_ONLY = "end_of_day_only"


class SessionVWAPPreference(str, Enum):
    ABOVE = "above"
    BELOW = "below"
    INDIFFERENT = "indifferent"


class DecisionState(str, Enum):
    WAIT = "WAIT"
    ARMED = "ARMED"
    TRIGGERED_PENDING_CLOSE = "TRIGGERED_PENDING_CLOSE"
    ACTIONABLE_NOW = "ACTIONABLE_NOW"
    INVALIDATED = "INVALIDATED"
    DEGRADED = "DEGRADED"


class DecisionNow(str, Enum):
    NONE = "NONE"
    STARTER_NOW = "STARTER_NOW"
    ADD_NOW = "ADD_NOW"
    REDUCE_NOW = "REDUCE_NOW"
    EXIT_NOW = "EXIT_NOW"


@dataclass(frozen=True)
class PullbackBuyZone:
    low: float
    high: float

    def to_dict(self) -> dict[str, Any]:
        return {"low": self.low, "high": self.high}


@dataclass(frozen=True)
class EventGuard:
    earnings_date: str | None = None
    block_new_position_within_days: int = 0
    allow_add_only_after_event: bool = False
    requires_post_event_rerun: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "earnings_date": self.earnings_date,
            "block_new_position_within_days": self.block_new_position_within_days,
            "allow_add_only_after_event": self.allow_add_only_after_event,
            "requires_post_event_rerun": self.requires_post_event_rerun,
        }


@dataclass(frozen=True)
class ExecutionContract:
    ticker: str
    analysis_asof: str
    market_data_asof: str
    level_basis: LevelBasis
    thesis_state: ThesisState
    primary_setup: PrimarySetup
    portfolio_stance: str
    entry_action_base: str
    setup_quality: str
    confidence: float
    action_if_triggered: ActionIfTriggered
    starter_fraction_of_target: float | None = None
    breakout_level: float | None = None
    breakout_confirmation: BreakoutConfirmation | None = None
    pullback_buy_zone: PullbackBuyZone | None = None
    invalid_if_close_below: float | None = None
    invalid_if_intraday_below: float | None = None
    min_relative_volume: float | None = None
    session_vwap_preference: SessionVWAPPreference = SessionVWAPPreference.INDIFFERENT
    event_guard: EventGuard | None = None
    reason_codes: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "ticker": self.ticker,
            "analysis_asof": self.analysis_asof,
            "market_data_asof": self.market_data_asof,
            "level_basis": self.level_basis.value,
            "thesis_state": self.thesis_state.value,
            "primary_setup": self.primary_setup.value,
            "portfolio_stance": self.portfolio_stance,
            "entry_action_base": self.entry_action_base,
            "setup_quality": self.setup_quality,
            "confidence": self.confidence,
            "action_if_triggered": self.action_if_triggered.value,
            "starter_fraction_of_target": self.starter_fraction_of_target,
            "breakout_level": self.breakout_level,
            "breakout_confirmation": self.breakout_confirmation.value if self.breakout_confirmation else None,
            "pullback_buy_zone": self.pullback_buy_zone.to_dict() if self.pullback_buy_zone else None,
            "invalid_if_close_below": self.invalid_if_close_below,
            "invalid_if_intraday_below": self.invalid_if_intraday_below,
            "min_relative_volume": self.min_relative_volume,
            "session_vwap_preference": self.session_vwap_preference.value,
            "event_guard": self.event_guard.to_dict() if self.event_guard else None,
            "reason_codes": list(self.reason_codes),
            "notes": list(self.notes),
        }
        return payload

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


@dataclass(frozen=True)
class IntradayMarketSnapshot:
    ticker: str
    asof: str
    provider: str
    interval: str
    last_price: float
    session_vwap: float | None
    day_high: float
    day_low: float
    volume: int
    avg20_daily_volume: float | None
    relative_volume: float | None


@dataclass(frozen=True)
class ExecutionUpdate:
    ticker: str
    analysis_asof: str
    execution_asof: str
    market_data_asof: str
    source: dict[str, Any]
    last_price: float | None
    session_vwap: float | None
    day_high: float | None
    day_low: float | None
    intraday_volume: int | None
    avg20_daily_volume: float | None
    relative_volume: float | None
    price_state: str
    volume_state: str
    event_state: str
    decision_state: DecisionState
    decision_now: DecisionNow
    decision_if_triggered: ActionIfTriggered
    trigger_status: dict[str, Any]
    changed_fields: tuple[str, ...]
    reason_codes: tuple[str, ...]
    staleness_seconds: int | None
    data_health: str
    refresh_checkpoint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ticker": self.ticker,
            "analysis_asof": self.analysis_asof,
            "execution_asof": self.execution_asof,
            "market_data_asof": self.market_data_asof,
            "source": self.source,
            "last_price": self.last_price,
            "session_vwap": self.session_vwap,
            "day_high": self.day_high,
            "day_low": self.day_low,
            "intraday_volume": self.intraday_volume,
            "avg20_daily_volume": self.avg20_daily_volume,
            "relative_volume": self.relative_volume,
            "price_state": self.price_state,
            "volume_state": self.volume_state,
            "event_state": self.event_state,
            "decision_state": self.decision_state.value,
            "decision_now": self.decision_now.value,
            "decision_if_triggered": self.decision_if_triggered.value,
            "trigger_status": self.trigger_status,
            "changed_fields": list(self.changed_fields),
            "reason_codes": list(self.reason_codes),
            "staleness_seconds": self.staleness_seconds,
            "data_health": self.data_health,
            "refresh_checkpoint": self.refresh_checkpoint,
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


def is_event_guard_active(event_guard: EventGuard | None, now: datetime) -> bool:
    if event_guard is None:
        return False
    if not event_guard.earnings_date:
        return False
    try:
        event_day = date.fromisoformat(event_guard.earnings_date)
    except ValueError:
        return False
    now_day = now.date()
    delta = (event_day - now_day).days
    return 0 <= delta <= int(event_guard.block_new_position_within_days)
