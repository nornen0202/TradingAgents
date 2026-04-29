from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Mapping


def _serialize(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _serialize(item) for key, item in asdict(value).items()}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): _serialize(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_serialize(item) for item in value]
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    return value


class TriggerType(str, Enum):
    VOLUME_SURGE = "VOLUME_SURGE"
    GAP_UP_MOMENTUM = "GAP_UP_MOMENTUM"
    VALUE_TO_MARKET_CAP_INFLOW = "VALUE_TO_MARKET_CAP_INFLOW"
    DAILY_RISE_TOP = "DAILY_RISE_TOP"
    CLOSING_STRENGTH = "CLOSING_STRENGTH"
    VOLUME_SURGE_FLAT = "VOLUME_SURGE_FLAT"
    NEAR_52W_HIGH = "NEAR_52W_HIGH"
    SECTOR_LEADER = "SECTOR_LEADER"
    CONTRARIAN_VALUE_SUPPORT = "CONTRARIAN_VALUE_SUPPORT"


@dataclass(frozen=True)
class ScannerCandidate:
    ticker: str
    display_name: str | None = None
    trigger_type: str = TriggerType.VOLUME_SURGE.value
    trigger_score: float = 0.0
    agent_fit_score: float = 0.0
    final_score: float = 0.0
    stop_loss_pct: float | None = None
    risk_reward_ratio: float | None = None
    sector: str | None = None
    market: str = "KR"
    reasons: tuple[str, ...] = tuple()
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class ScannerResult:
    run_id: str
    asof: str
    market: str
    regime: str
    candidates: tuple[ScannerCandidate, ...]
    warnings: tuple[str, ...] = tuple()

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class BuyMatrix:
    profitability_gate: bool | None
    balance_sheet_gate: bool | None
    growth_gate: bool | None
    business_clarity_gate: bool | None
    momentum_signal_count: int
    macro_adjustment: float
    risk_reward_ratio: float | None
    risk_reward_floor_passed: bool | None
    sector_leadership_score: float | None
    market_regime: str | None
    effective_score: float
    min_score_required: float
    passed: bool
    fail_reasons: tuple[str, ...]
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)
