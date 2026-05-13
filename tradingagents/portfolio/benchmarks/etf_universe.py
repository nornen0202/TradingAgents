from __future__ import annotations

from tradingagents.portfolio.performance.etf_alternatives import _DEFAULT_INSTRUMENTS, _DEFAULT_PORTFOLIOS


def default_instruments() -> dict[str, dict[str, str]]:
    return {key: dict(value) for key, value in _DEFAULT_INSTRUMENTS.items()}


def default_portfolios() -> dict[str, dict[str, float]]:
    return {key: dict(value) for key, value in _DEFAULT_PORTFOLIOS.items()}
