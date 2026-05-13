from __future__ import annotations

from datetime import date

from tradingagents.portfolio.benchmarks.price_provider import normalize_price_bars


def test_price_provider_normalizes_adjusted_close_fixture():
    bars = normalize_price_bars(
        [{"date": "2026-04-13", "adjusted_close": 123.4}],
        ticker="069500.KS",
        currency="KRW",
        provider="fixture",
    )

    assert len(bars) == 1
    assert bars[0].date == date(2026, 4, 13)
    assert bars[0].close == 123.4
    assert bars[0].adjusted_close == 123.4
    assert bars[0].provider == "fixture"
