from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any


def _serialize(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _serialize(item) for key, item in asdict(value).items()}
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, dict):
        return {str(key): _serialize(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_serialize(item) for item in value]
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    return value


@dataclass(frozen=True)
class InstrumentIdentity:
    broker_symbol: str
    canonical_ticker: str
    yahoo_symbol: str
    krx_code: str | None
    dart_corp_code: str | None
    display_name: str
    exchange: str
    country: str
    currency: str

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class PendingOrder:
    broker_order_id: str
    broker_symbol: str
    canonical_ticker: str | None
    side: str
    qty: float
    remaining_qty: float
    status: str

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class Position:
    broker_symbol: str
    canonical_ticker: str
    display_name: str
    sector: str | None
    quantity: float
    available_qty: float
    avg_cost_krw: int
    market_price_krw: int
    market_value_krw: int
    unrealized_pnl_krw: int

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class AccountConstraints:
    min_cash_buffer_krw: int = 0
    min_trade_krw: int = 100_000
    max_single_name_weight: float = 0.35
    max_sector_weight: float = 0.50
    max_daily_turnover_ratio: float = 0.30
    max_order_count_per_day: int = 5
    respect_existing_weights_softly: bool = True

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class AccountSnapshot:
    snapshot_id: str
    as_of: str
    broker: str
    account_id: str
    currency: str
    settled_cash_krw: int
    available_cash_krw: int
    buying_power_krw: int
    total_equity_krw: int | None = None
    snapshot_health: str = "VALID"
    cash_diagnostics: dict[str, Any] = field(default_factory=dict)
    pending_orders: tuple[PendingOrder, ...] = tuple()
    positions: tuple[Position, ...] = tuple()
    constraints: AccountConstraints = field(default_factory=AccountConstraints)
    warnings: tuple[str, ...] = tuple()

    @property
    def account_value_krw(self) -> int:
        if self.total_equity_krw is not None and int(self.total_equity_krw) > 0:
            return int(self.total_equity_krw)
        return int(max(self.available_cash_krw, 0) + sum(position.market_value_krw for position in self.positions))

    def find_position(self, canonical_ticker: str) -> Position | None:
        for position in self.positions:
            if position.canonical_ticker == canonical_ticker:
                return position
        return None

    def to_dict(self) -> dict[str, Any]:
        payload = _serialize(self)
        payload["account_value_krw"] = self.account_value_krw
        return payload


@dataclass(frozen=True)
class PortfolioProfile:
    name: str
    enabled: bool
    broker: str
    broker_environment: str
    read_only: bool
    account_no: str | None
    product_code: str | None
    manual_snapshot_path: Path | None
    csv_positions_path: Path | None
    private_output_dirname: str
    watch_tickers: tuple[str, ...]
    trigger_budget_krw: int
    constraints: AccountConstraints
    continue_on_error: bool = True
    market_scope: str = "kr"

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class PortfolioCandidate:
    snapshot_id: str
    instrument: InstrumentIdentity
    is_held: bool
    market_value_krw: int
    quantity: float
    available_qty: float
    sector: str | None
    structured_decision: dict[str, Any] | None
    data_coverage: dict[str, Any]
    quality_flags: tuple[str, ...]
    vendor_health: dict[str, Any]
    suggested_action_now: str
    suggested_action_if_triggered: str
    trigger_conditions: tuple[str, ...]
    confidence: float
    stance: str
    entry_action: str
    setup_quality: str
    rationale: str
    trigger_profile: dict[str, Any] = field(default_factory=dict)
    decision_source: str = "RULE_ONLY"
    thesis_strength: float = 0.0
    timing_readiness: float = 0.0
    reason_codes: tuple[str, ...] = tuple()
    review_required: bool = False
    score_now: float = 0.0
    score_triggered: float = 0.0
    gate_reasons: tuple[str, ...] = tuple()
    data_health: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = _serialize(self)
        payload["broker_symbol"] = self.instrument.broker_symbol
        payload["canonical_ticker"] = self.instrument.canonical_ticker
        payload["display_name"] = self.instrument.display_name
        return payload


@dataclass(frozen=True)
class PortfolioAction:
    canonical_ticker: str
    display_name: str
    priority: int
    confidence: float
    action_now: str
    delta_krw_now: int
    target_weight_now: float
    action_if_triggered: str
    delta_krw_if_triggered: int
    target_weight_if_triggered: float
    trigger_conditions: tuple[str, ...]
    rationale: str
    data_health: dict[str, Any]
    decision_source: str = "RULE_ONLY"
    timing_readiness: float = 0.0
    reason_codes: tuple[str, ...] = tuple()
    review_required: bool = False
    trigger_type: str | None = None
    gate_reasons: tuple[str, ...] = tuple()
    sector: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class PortfolioRecommendation:
    snapshot_id: str
    report_date: str
    account_value_krw: int
    recommended_cash_after_now_krw: int
    recommended_cash_after_triggered_krw: int
    market_regime: str
    actions: tuple[PortfolioAction, ...]
    portfolio_risks: tuple[str, ...]
    data_health_summary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)
