from __future__ import annotations

from tradingagents.portfolio.performance.etf_alternatives import _normalize_price_rows


def normalize_price_rows(raw):
    rows, _basis = _normalize_price_rows(raw)
    return rows
