from __future__ import annotations

from datetime import date
from typing import Any

from tradingagents.portfolio.performance.etf_alternatives import _normalize_price_rows

from .models import BenchmarkPriceBar


def normalize_price_rows(raw):
    rows, _basis = _normalize_price_rows(raw)
    return rows


def normalize_price_bars(
    raw: Any,
    *,
    ticker: str,
    currency: str = "KRW",
    provider: str = "local_fixture",
) -> list[BenchmarkPriceBar]:
    rows, basis = _normalize_price_rows(raw)
    bars: list[BenchmarkPriceBar] = []
    for row in rows:
        try:
            parsed = date.fromisoformat(str(row.get("date")))
            close = float(row.get("close"))
        except (TypeError, ValueError):
            continue
        bars.append(
            BenchmarkPriceBar(
                ticker=ticker,
                date=parsed,
                open=None,
                high=None,
                low=None,
                close=close,
                adjusted_close=close if basis == "adjusted_close" else None,
                currency=currency,
                provider=provider,
            )
        )
    return bars
