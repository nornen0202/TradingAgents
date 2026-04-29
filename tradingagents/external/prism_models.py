from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Literal, Mapping


def serialize_prism_value(value: Any) -> Any:
    if is_dataclass(value):
        return {key: serialize_prism_value(item) for key, item in asdict(value).items()}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, Mapping):
        return {str(key): serialize_prism_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [serialize_prism_value(item) for item in value]
    if isinstance(value, list):
        return [serialize_prism_value(item) for item in value]
    return value


class PrismSignalAction(str, Enum):
    BUY = "BUY"
    ADD = "ADD"
    NO_ENTRY = "NO_ENTRY"
    HOLD = "HOLD"
    WATCH = "WATCH"
    SELL = "SELL"
    TRIM_TO_FUND = "TRIM_TO_FUND"
    REDUCE_RISK = "REDUCE_RISK"
    TAKE_PROFIT = "TAKE_PROFIT"
    STOP_LOSS = "STOP_LOSS"
    EXIT = "EXIT"
    UNKNOWN = "UNKNOWN"


class PrismSourceKind(str, Enum):
    DASHBOARD_LIVE = "dashboard_live"
    DASHBOARD_JSON = "dashboard_json"
    SQLITE = "sqlite"
    CSV = "csv"
    MANUAL_JSON = "manual_json"
    PRISM_API = "prism_api"


@dataclass(frozen=True)
class PrismExternalSignal:
    canonical_ticker: str
    display_name: str | None = None
    market: Literal["KR", "US", "UNKNOWN"] = "UNKNOWN"
    source_kind: PrismSourceKind = PrismSourceKind.MANUAL_JSON
    source_path_or_url: str | None = None
    source_asof: datetime | None = None
    ingested_at: datetime = field(default_factory=lambda: datetime.now().astimezone())

    signal_action: PrismSignalAction = PrismSignalAction.UNKNOWN
    trigger_type: str | None = None
    trigger_score: float | None = None
    composite_score: float | None = None
    agent_fit_score: float | None = None
    risk_reward_ratio: float | None = None
    stop_loss_price: float | None = None
    target_price: float | None = None
    confidence: float | None = None
    rationale: str | None = None
    tags: tuple[str, ...] = tuple()

    current_price: float | None = None
    avg_cost: float | None = None
    quantity: float | None = None
    position_value: float | None = None
    pnl_pct: float | None = None

    realized_return_pct: float | None = None
    holding_days: int | None = None
    win_rate_30d_by_trigger: float | None = None
    avg_30d_return_by_trigger: float | None = None

    raw: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return serialize_prism_value(self)


@dataclass(frozen=True)
class PrismIngestionResult:
    enabled: bool
    ok: bool
    source_kind: PrismSourceKind | None = None
    source: str | None = None
    ingested_at: datetime = field(default_factory=lambda: datetime.now().astimezone())
    signals: list[PrismExternalSignal] = field(default_factory=list)
    portfolio_snapshot: dict[str, Any] | None = None
    performance_summary: dict[str, Any] | None = None
    journal_lessons: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    raw_payload_hash: str | None = None

    @property
    def signals_count(self) -> int:
        return len(self.signals)

    def to_dict(self) -> dict[str, Any]:
        return serialize_prism_value(self)

    def status_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "ok": self.ok,
            "source_kind": self.source_kind.value if self.source_kind else None,
            "source": self.source,
            "ingested_at": self.ingested_at.isoformat(),
            "signals_count": self.signals_count,
            "warnings": list(self.warnings),
            "raw_payload_hash": self.raw_payload_hash,
        }

    def signals_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "ok": self.ok,
            "source_kind": self.source_kind.value if self.source_kind else None,
            "source": self.source,
            "ingested_at": self.ingested_at.isoformat(),
            "raw_payload_hash": self.raw_payload_hash,
            "signals": [signal.to_dict() for signal in self.signals],
        }
