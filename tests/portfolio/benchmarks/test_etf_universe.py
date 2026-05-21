from __future__ import annotations

try:
    import pytest
except ModuleNotFoundError:  # pragma: no cover - CI unittest import compatibility.
    from tests.pytest_compat import pytest

from tradingagents.portfolio.benchmarks.etf_universe import (
    default_instrument_models,
    default_portfolio_definitions,
    normalize_weights,
)


def test_default_universe_contains_required_single_etf_benchmarks():
    instruments = {item.benchmark_id: item for item in default_instrument_models()}
    portfolios = {item.benchmark_id: item for item in default_portfolio_definitions()}

    assert instruments["KOSPI200"].ticker == "069500.KS"
    assert instruments["KOSDAQ150"].ticker == "229200.KS"
    assert instruments["SP500_KRW"].ticker == "360750.KS"
    assert instruments["NASDAQ100_KRW"].ticker == "133690.KS"
    assert {"KOSPI200_100", "KOSDAQ150_100", "SP500_100", "NASDAQ100_100", "BLENDED"} <= set(portfolios)


def test_blended_weights_are_normalized():
    weights = normalize_weights({"kospi200": 7, "sp500_krw": 3})

    assert weights == pytest.approx({"KOSPI200": 0.7, "SP500_KRW": 0.3})
