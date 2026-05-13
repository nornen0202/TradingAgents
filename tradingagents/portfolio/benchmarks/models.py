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
