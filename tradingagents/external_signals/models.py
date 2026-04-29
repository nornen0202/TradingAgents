from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping


def _serialize(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _serialize(item) for key, item in asdict(value).items()}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, Mapping):
        return {str(key): _serialize(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_serialize(item) for item in value]
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    return value


class ExternalSignalSource(str, Enum):
    PRISM_DASHBOARD = "prism_dashboard"
    PRISM_LOCAL_JSON = "prism_local_json"
    PRISM_SQLITE = "prism_sqlite"
    MANUAL_JSON = "manual_json"


class ExternalSignalAction(str, Enum):
    BUY = "BUY"
    ADD = "ADD"
    HOLD = "HOLD"
    WATCH = "WATCH"
    TRIM_TO_FUND = "TRIM_TO_FUND"
    REDUCE_RISK = "REDUCE_RISK"
    TAKE_PROFIT = "TAKE_PROFIT"
    STOP_LOSS = "STOP_LOSS"
    EXIT = "EXIT"
    NO_ENTRY = "NO_ENTRY"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ExternalSignal:
    source: ExternalSignalSource
    ticker: str
    display_name: str | None
    market: str | None
    action: ExternalSignalAction
    confidence: float | None
    trigger_type: str | None
    score: float | None
    stop_loss_price: float | None
    target_price: float | None
    current_price: float | None
    reason: str | None
    tags: tuple[str, ...]
    asof: str
    raw: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class ExternalSignalIngestion:
    source: ExternalSignalSource | None
    status: str
    asof: str
    signals: tuple[ExternalSignal, ...]
    warnings: tuple[str, ...] = tuple()
    attempted_sources: tuple[str, ...] = tuple()
    selected_source: str | None = None

    @property
    def signals_count(self) -> int:
        return len(self.signals)

    def status_dict(self) -> dict[str, Any]:
        return {
            "source": self.source.value if self.source else None,
            "status": self.status,
            "asof": self.asof,
            "signals_count": self.signals_count,
            "warnings": list(self.warnings),
            "attempted_sources": list(self.attempted_sources),
            "selected_source": self.selected_source,
        }

    def signals_dict(self) -> dict[str, Any]:
        return {
            "source": self.source.value if self.source else None,
            "status": self.status,
            "asof": self.asof,
            "signals": [signal.to_dict() for signal in self.signals],
        }


class ReconciliationAgreement(str, Enum):
    CONSENSUS = "CONSENSUS"
    PARTIAL_AGREEMENT = "PARTIAL_AGREEMENT"
    TRADINGAGENTS_ONLY = "TRADINGAGENTS_ONLY"
    EXTERNAL_ONLY = "EXTERNAL_ONLY"
    HARD_CONFLICT = "HARD_CONFLICT"
    NO_OVERLAP = "NO_OVERLAP"
    EXTERNAL_UNAVAILABLE = "EXTERNAL_UNAVAILABLE"


@dataclass(frozen=True)
class ExternalReconciliationEntry:
    ticker: str
    display_name: str | None
    tradingagents_action: str | None
    tradingagents_risk_action: str | None
    prism_action: str | None
    prism_confidence: float | None
    agreement: ReconciliationAgreement
    recommendation: str
    reason: str
    execution_blocked: bool = False
    confidence_modifier: float = 0.0
    risk_gate_bypass_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)
