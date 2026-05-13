from __future__ import annotations

from tradingagents.portfolio.performance.etf_alternatives import (
    EtfAlternativeComparisonSummary,
    build_etf_alternative_comparison,
)


def build_etf_dca_comparison(**kwargs) -> EtfAlternativeComparisonSummary | None:
    return build_etf_alternative_comparison(**kwargs)
