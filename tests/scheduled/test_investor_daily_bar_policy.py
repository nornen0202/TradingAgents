from dataclasses import replace
from datetime import date
from unittest.mock import patch

import pandas as pd
import pytest

from tests.scheduled.test_trade_date_freshness_guard import _config, _FixedDatetime
from tradingagents.scheduled.runner import resolve_trade_date


def available(market="US"):
    config = _config(market, wait_minutes=150)
    return replace(config, run=replace(config.run, daily_bar_policy="available"))


@pytest.mark.parametrize("market,ticker", [("US", "AAPL"), ("KR", "005930.KS")])
@pytest.mark.parametrize("observed", ["2026-06-26", "2026-06-29"])
def test_delayed_actual_daily_bar_does_not_wait_or_relabel(market, ticker, observed, capsys):
    history = pd.DataFrame({"Close": [100, 102]}, index=pd.to_datetime(["2026-06-25", observed]))
    with patch("tradingagents.scheduled.runner.datetime", _FixedDatetime), patch(
        "tradingagents.scheduled.runner._expected_completed_daily_trade_date", return_value=date(2026, 6, 29)
    ), patch("tradingagents.scheduled.runner._fetch_recent_trade_date_history", return_value=history), patch(
        "tradingagents.scheduled.runner.sleep", side_effect=AssertionError("must not wait")
    ):
        assert resolve_trade_date(ticker, available(market)) == observed
    if observed == "2026-06-26":
        assert observed in capsys.readouterr().out


@pytest.mark.parametrize("bad", ["2026-07-01", "2026-06-30", "bad", None, "2026-05-01"])
def test_future_incomplete_invalid_missing_and_outside_window_dates_are_excluded(bad):
    history = pd.DataFrame({"Close": [99, 777]}, index=["2026-06-26", bad])
    with patch("tradingagents.scheduled.runner.datetime", _FixedDatetime), patch(
        "tradingagents.scheduled.runner._expected_completed_daily_trade_date", return_value=date(2026, 6, 29)
    ), patch("tradingagents.scheduled.runner._fetch_recent_trade_date_history", return_value=history):
        assert resolve_trade_date("AAPL", available()) == "2026-06-26"


@pytest.mark.parametrize("history", [pd.DataFrame(), pd.DataFrame({"Close": [float("nan"), float("inf"), -1, 0]}, index=["2026-06-29"] * 4), pd.DataFrame({"Close": [100]}, index=["invalid"])])
def test_no_usable_bar_does_not_invent_date(history):
    with patch("tradingagents.scheduled.runner.datetime", _FixedDatetime), patch(
        "tradingagents.scheduled.runner._expected_completed_daily_trade_date", return_value=date(2026, 6, 29)
    ), patch("tradingagents.scheduled.runner._fetch_recent_trade_date_history", return_value=history):
        with pytest.raises(RuntimeError, match="No valid dated"):
            resolve_trade_date("AAPL", available())


def test_vendor_failure_does_not_synthesize_a_calendar_date():
    with patch("tradingagents.scheduled.runner._fetch_recent_trade_date_history", side_effect=TimeoutError()):
        with pytest.raises(RuntimeError, match="No observed daily bar"):
            resolve_trade_date("AAPL", available())


def test_calendar_unavailable_uses_observed_previous_date_not_incomplete_today():
    history = pd.DataFrame({"Close": [100, 105]}, index=["2026-06-29", "2026-06-30"])
    with patch("tradingagents.scheduled.runner.datetime", _FixedDatetime), patch(
        "tradingagents.scheduled.runner._expected_completed_daily_trade_date", return_value=None
    ), patch("tradingagents.scheduled.runner._fetch_recent_trade_date_history", return_value=history):
        assert resolve_trade_date("005930.KS", available("KR")) == "2026-06-29"


def test_execution_overlay_keeps_strict_daily_date_policy():
    from tests.scheduled.test_trade_date_freshness_guard import _FakeHistory
    config = available()
    config = replace(config, run=replace(config.run, run_mode="overlay_only", latest_market_data_wait_minutes=0))
    with patch("tradingagents.scheduled.runner.datetime", _FixedDatetime), patch(
        "tradingagents.scheduled.runner._expected_completed_daily_trade_date", return_value=date(2026, 6, 29)
    ), patch("tradingagents.scheduled.runner._fetch_recent_trade_date_history", return_value=_FakeHistory(date(2026, 6, 26))):
        with pytest.raises(RuntimeError, match="Refusing stale"):
            resolve_trade_date("AAPL", config)
