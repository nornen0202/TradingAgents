from __future__ import annotations

from tradingagents.portfolio.performance.etf_alternatives import EtfAlternativePortfolioResult

from .models import VirtualBenchmarkPortfolioResult, VirtualBenchmarkTransaction

EtfAlternativePortfolioResultAdapter = EtfAlternativePortfolioResult

__all__ = [
    "EtfAlternativePortfolioResultAdapter",
    "VirtualBenchmarkPortfolioResult",
    "VirtualBenchmarkTransaction",
]
