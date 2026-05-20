from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class BrokerBenchmarkReturn:
    benchmark: str
    benchmark_return_pct: float | None
    excess_return_pct: float | None
    comparison_basis: str = "broker_period_return"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BrokerPerformanceSummary:
    broker: str
    account_scope: str
    period_start: str
    period_end: str
    investment_pnl_krw: int | None = None
    balance_return_pct: float | None = None
    average_balance_return_pct: float | None = None
    net_asset_return_pct: float | None = None
    total_deposit_return_pct: float | None = None
    investment_principal_krw: int | None = None
    start_asset_krw: int | None = None
    end_asset_krw: int | None = None
    deposit_amount_krw: int | None = None
    withdrawal_amount_krw: int | None = None
    realized_trade_pnl_krw: int | None = None
    realized_trade_return_pct: float | None = None
    trade_fees_krw: int | None = None
    trade_taxes_krw: int | None = None
    dividend_krw: int | None = None
    interest_krw: int | None = None
    fees_krw: int | None = None
    taxes_krw: int | None = None
    benchmark_returns: list[BrokerBenchmarkReturn] = field(default_factory=list)
    benchmark_excess_returns: dict[str, float | None] = field(default_factory=dict)
    raw_summary: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["benchmark_returns"] = [item.to_dict() for item in self.benchmark_returns]
        return payload

    @property
    def external_capital_flow_count(self) -> int:
        count = 0
        if self.deposit_amount_krw and self.deposit_amount_krw > 0:
            count += 1
        if self.withdrawal_amount_krw and self.withdrawal_amount_krw > 0:
            count += 1
        return count

    @property
    def external_cashflow_net_krw(self) -> int:
        return int(self.deposit_amount_krw or 0) - int(self.withdrawal_amount_krw or 0)


@dataclass(frozen=True)
class BrokerPerformanceComparison:
    broker_end_asset_krw: int | None
    tradingagents_account_value_krw: int | None
    end_asset_delta_krw: int | None
    end_asset_delta_pct: float | None
    broker_balance_return_pct: float | None
    tradingagents_simple_nav_return_pct: float | None
    return_delta_pct: float | None
    period_match_status: str
    scope_match_status: str
    comparison_status: str
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
