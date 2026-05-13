from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Literal


class CashflowType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    DIVIDEND = "DIVIDEND"
    INTEREST = "INTEREST"
    FEE = "FEE"
    TAX = "TAX"
    FX_CONVERSION_IN = "FX_CONVERSION_IN"
    FX_CONVERSION_OUT = "FX_CONVERSION_OUT"
    UNKNOWN_EXTERNAL = "UNKNOWN_EXTERNAL"


class CashflowSource(str, Enum):
    KIS_LEDGER = "kis_ledger"
    KIS_PERIOD_SUMMARY = "kis_period_summary"
    MANUAL_CSV = "manual_csv"
    MANUAL_JSON = "manual_json"
    SNAPSHOT_INFERRED = "snapshot_inferred"


@dataclass(frozen=True)
class DatedCashflow:
    event_id: str
    event_date: date
    event_time: datetime | None
    type: CashflowType
    amount_krw: float
    currency: str = "KRW"
    amount_original: float | None = None
    fx_rate: float | None = None
    source: CashflowSource = CashflowSource.MANUAL_JSON
    description: str | None = None
    confidence: Literal["high", "medium", "low"] = "high"
    raw: dict[str, Any] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class BenchmarkInstrument:
    benchmark_id: str
    display_name: str
    ticker: str
    market: Literal["KR", "US"]
    currency: str
    asset_class: str = "ETF"
    price_provider: str = "auto"
    fallback_tickers: tuple[str, ...] = ()
    notes: str | None = None


@dataclass(frozen=True)
class BenchmarkPortfolioDefinition:
    benchmark_id: str
    display_name: str
    description: str
    instruments: tuple[BenchmarkInstrument, ...]
    weights: dict[str, float]
    rebalance_policy: Literal["cashflow_only", "monthly", "quarterly", "none"] = "cashflow_only"


@dataclass(frozen=True)
class BenchmarkPriceBar:
    ticker: str
    date: date
    open: float | None
    high: float | None
    low: float | None
    close: float
    adjusted_close: float | None
    currency: str
    provider: str
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class VirtualBenchmarkTransaction:
    event_date: date
    benchmark_id: str
    ticker: str
    side: Literal["BUY", "SELL"]
    amount_krw: float
    price: float
    shares: float
    source_cashflow_id: str
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class VirtualBenchmarkPortfolioResult:
    benchmark_id: str
    display_name: str
    period_start: date
    period_end: date
    final_value_krw: float
    invested_principal_krw: float
    net_external_cashflow_krw: float
    pnl_krw: float
    return_on_contributions_pct: float | None
    mwr_irr_pct: float | None
    twr_pct: float | None
    max_drawdown_pct: float | None
    volatility_pct: float | None
    transactions: list[VirtualBenchmarkTransaction] = field(default_factory=list)
    equity_curve: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class EtfAlternativeComparison:
    actual_source: Literal["broker_reported", "snapshot_reconciled", "unavailable"]
    period_start: date
    period_end: date
    actual_final_value_krw: float | None
    actual_return_pct: float | None
    actual_pnl_krw: float | None
    benchmarks: list[VirtualBenchmarkPortfolioResult]
    best_benchmark_id: str | None
    blended_benchmark_id: str | None
    actual_vs_benchmark: dict[str, dict[str, Any]]
    recommendation: dict[str, Any]
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CoreSatelliteRecommendation:
    recommended_core_etf_weight: float
    recommended_individual_stock_weight: float
    confidence: str
    reasons: list[str] = field(default_factory=list)
    rules_triggered: list[str] = field(default_factory=list)
    next_review_date: date | None = None
