from datetime import date
from unittest.mock import patch

import pandas as pd

from tradingagents.portfolio.performance.benchmark_sources import load_yahoo_benchmark
from tradingagents.portfolio.performance.etf_alternatives import _fx_rate_and_date


def _data(days, prices):
    return pd.DataFrame({"Close": prices, "Dividends": [0] * len(days), "Stock Splits": [0] * len(days)},
                        index=pd.to_datetime(days))


def test_yahoo_completed_early_close_does_not_use_unfinished_or_future_rows(tmp_path):
    data = _data(["2025-11-26", "2025-11-27", "2025-11-28", "2025-12-01"], [100, 999, 103, 108])
    meta = {"symbol": "SPY", "currency": "USD", "instrumentType": "ETF", "exchangeName": "PCX"}
    with patch("tradingagents.portfolio.performance.benchmark_sources._download", return_value=(data, meta)) as fetch:
        kwargs = {"cache_dir": tmp_path}
        prior, prior_evidence = load_yahoo_benchmark("SPY", "USD", date(2025, 11, 26), date(2025, 12, 1),
                                                     as_of="2025-11-28T17:59:00+00:00", **kwargs)
        later, evidence = load_yahoo_benchmark("SPY", "USD", date(2025, 11, 26), date(2025, 12, 1),
                                                as_of="2025-11-28T18:00:00+00:00", **kwargs)
        cached, cached_evidence = load_yahoo_benchmark("SPY", "USD", date(2025, 11, 26), date(2025, 12, 1),
                                                       as_of="2025-11-28T18:45:00+00:00", **kwargs)
    assert fetch.call_count == 2
    assert cached == later and cached_evidence["input_origin"] == "cache"
    assert [row["date"] for row in prior] == ["2025-11-26"]
    assert [row["date"] for row in later] == ["2025-11-26", "2025-11-28"]
    assert evidence["historical_vintage_verified"] is False
    assert evidence["distributions"] == "embedded_in_provider_adjusted_close"
    assert evidence["series_sha256"] != prior_evidence["series_sha256"]


def test_yahoo_missing_session_and_currency_cannot_be_filled_by_adjacent_bar():
    data = _data(["2025-11-26"], [100])
    meta = {"symbol": "SPY", "currency": "USD"}
    with patch("tradingagents.portfolio.performance.benchmark_sources._download", return_value=(data, meta)):
        prices, evidence = load_yahoo_benchmark("SPY", "USD", date(2025, 11, 26), date(2025, 11, 28),
                                                 as_of="2025-11-28T18:01:00+00:00")
        wrong, wrong_evidence = load_yahoo_benchmark("SPY", "KRW", date(2025, 11, 26), date(2025, 11, 28),
                                                       as_of="2025-11-28T18:01:00+00:00")
    assert not prices and evidence["state"] == "missing_sessions"
    assert not wrong and wrong_evidence["state"] == "provider_instrument_or_currency_unverified"


def test_yahoo_fx_prior_completed_daily_mark_labels_actual_rate_date():
    data = _data(["2025-11-26", "2025-11-27", "2025-11-28"], [1400, 1410, 1499])
    meta = {"symbol": "KRW=X", "currency": "KRW", "instrumentType": "CURRENCY"}
    with patch("tradingagents.portfolio.performance.benchmark_sources._download", return_value=(data, meta)):
        rows, evidence = load_yahoo_benchmark("KRW=X", "KRW", date(2025, 11, 26), date(2025, 11, 28),
                                              as_of="2025-11-28T18:00:00+00:00", fx=True)
    assert evidence["units"] == "KRW per USD"
    assert _fx_rate_and_date("USD", {"USDKRW": rows}, date(2025, 11, 28), lookup="on_trade_date") == (1410, "2025-11-27")
    assert _fx_rate_and_date("USD", {"USDKRW": rows}, date(2025, 12, 5), lookup="on_trade_date") == (None, None)


def test_korean_supplemental_holiday_does_not_create_a_missing_bar():
    data = _data(["2026-07-16", "2026-07-20"], [100, 110])
    meta = {"symbol": "069500.KS", "currency": "KRW", "instrumentType": "ETF", "exchangeName": "KSC"}
    with patch("tradingagents.portfolio.performance.benchmark_sources._download", return_value=(data, meta)):
        rows, evidence = load_yahoo_benchmark("069500.KS", "KRW", date(2026, 7, 16), date(2026, 7, 20),
                                              as_of="2026-07-20T06:31:00+00:00")
    assert [row["date"] for row in rows] == ["2026-07-16", "2026-07-20"]
    assert evidence["state"] == "available" and evidence["missing_sessions"] == 0


def test_transient_yahoo_failure_retries_and_only_the_success_is_cached(tmp_path):
    from unittest.mock import Mock

    source = Mock()
    source.history.side_effect = [TimeoutError("timed out"), _data(["2025-11-26"], [100])]
    source.get_history_metadata.return_value = {"symbol": "SPY", "currency": "USD", "exchangeName": "PCX"}
    with (patch("yfinance.Ticker", return_value=source),
          patch("tradingagents.dataflows.stockstats_utils.time.sleep")):
        options = {"as_of": "2025-11-26T22:00:00+00:00", "cache_dir": tmp_path}
        result, evidence = load_yahoo_benchmark("SPY", "USD", date(2025, 11, 26), date(2025, 11, 26), **options)
        later, cached = load_yahoo_benchmark("SPY", "USD", date(2025, 11, 26), date(2025, 11, 26), **options)
    assert source.history.call_count == 2 and result == later
    assert evidence["input_origin"] == "fresh" and cached["input_origin"] == "cache"
