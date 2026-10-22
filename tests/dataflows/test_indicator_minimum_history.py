"""Offline minimum-observation contracts; these do not assert IIR convergence."""

from unittest.mock import Mock

import exchange_calendars as xcals
import numpy as np
import pandas as pd
import pytest
import stockstats
from stockstats import wrap

from tradingagents.dataflows import interface, stockstats_utils as stats, y_finance
from tradingagents.dataflows.config import run_config
from tradingagents.dataflows.research_evidence import REQUIRED_METHODS, SCHEMA, assess_tool_evidence, evidence_review_reason
from tradingagents.dataflows.vendor_exceptions import InsufficientIndicatorHistoryError, VendorInputError
from tradingagents.scheduled.market_calendar import is_supplemental_market_holiday


DAY = "2026-10-21"
MINIMUMS = {
    "close_50_sma": 50, "close_200_sma": 200, "close_10_ema": 10,
    "macd": 26, "macds": 34, "macdh": 34, "rsi": 15,
    "boll": 20, "boll_ub": 20, "boll_lb": 20, "atr": 15,
    "vwma": 14, "mfi": 15,
}
SESSIONS = xcals.get_calendar("XNYS").sessions_in_range("2023-01-01", DAY)


def history(count, *, market="US"):
    sessions = SESSIONS if market == "US" else xcals.get_calendar("XKRX").sessions_in_range("2023-01-01", DAY)
    sessions = sessions[[not is_supplemental_market_holiday(market=market, session_date=value.date()) for value in sessions]]
    sessions = sessions[-count:] if count else sessions[:0]
    steps = np.arange(count, dtype=float)
    close = 100.0 + steps / 10 + np.sin(steps)
    return pd.DataFrame({"Date": sessions.tz_localize(None), "Open": close,
                         "High": close + 2, "Low": close - 2, "Close": close,
                         "Volume": 1000 + steps})


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.delenv("TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED", raising=False)
    monkeypatch.setattr(stats.yf, "download", Mock(side_effect=AssertionError("network forbidden")))
    monkeypatch.setattr(y_finance.yf, "Ticker", Mock(side_effect=AssertionError("network forbidden")))
    interface.reset_tool_telemetry()
    yield
    interface.reset_tool_telemetry()


def supply(monkeypatch, frame):
    monkeypatch.setattr(stats, "load_ohlcv", lambda *_: frame.copy(deep=True))
    monkeypatch.setattr(y_finance, "load_ohlcv", lambda *_: frame.copy(deep=True))


def assess_with_other_required_methods_available():
    outcomes = interface.snapshot_tool_requests()
    events = interface.snapshot_tool_telemetry()
    started, finished = outcomes[0]["started_at"], outcomes[-1]["completed_at"]
    for index, method in enumerate(sorted(REQUIRED_METHODS - {"get_indicators"}), start=1):
        identity = f"{index:032x}"
        outcomes.append({"request_id": identity, "method": method, "status": "available",
                         "result_sha256": "a" * 64, "started_at": started, "completed_at": finished})
        events.append({"request_id": identity, "method": method, "status": "success", "fallback": False})
    return assess_tool_evidence({"request_schema": SCHEMA, "request_outcomes": outcomes, "events": events},
                                started_at=started, finished_at=finished)


@pytest.mark.parametrize("indicator,minimum", MINIMUMS.items())
@pytest.mark.parametrize("delta", [-1, 0, 1])
def test_actual_period_boundaries_all_three_paths(monkeypatch, indicator, minimum, delta):
    frame = history(minimum + delta)
    supply(monkeypatch, frame)
    assert stats.indicator_minimum_observations(indicator) == minimum
    if delta < 0:
        with pytest.raises(InsufficientIndicatorHistoryError, match="Insufficient history"):
            stats.StockstatsUtils.get_stock_stats("AAPL", indicator, DAY)
        with pytest.raises(InsufficientIndicatorHistoryError):
            y_finance._get_stock_stats_bulk("AAPL", indicator, DAY)
        with pytest.raises(InsufficientIndicatorHistoryError):
            y_finance.get_stock_stats_indicators_window("AAPL", indicator, DAY, 0)
    else:
        expected = float(wrap(frame.copy())[indicator].iloc[-1])
        assert stats.StockstatsUtils.get_stock_stats("AAPL", indicator, DAY) == expected
        assert float(y_finance._get_stock_stats_bulk("AAPL", indicator, DAY)[DAY]) == expected
        assert f"{DAY}: {expected}" in y_finance.get_stock_stats_indicators_window("AAPL", indicator, DAY, 0)


def test_one_observation_cannot_be_sma200(monkeypatch):
    frame = history(1)
    assert float(wrap(frame.copy())["close_200_sma"].iloc[-1]) == frame["Close"].iloc[-1]
    supply(monkeypatch, frame)
    with pytest.raises(InsufficientIndicatorHistoryError, match="requires 200.*found 1"):
        y_finance.get_stockstats_indicator("AAPL", "close_200_sma", DAY)


@pytest.mark.parametrize("indicator,minimum", MINIMUMS.items())
def test_earliest_immature_requested_date_is_not_hidden(monkeypatch, indicator, minimum):
    frame = history(minimum + 4)
    supply(monkeypatch, frame)
    bulk = y_finance._get_stock_stats_bulk("AAPL", indicator, DAY)
    first = frame["Date"].iloc[0].strftime("%Y-%m-%d")
    assert bulk[first].startswith("N/A: Insufficient")
    first_valid = frame["Date"].iloc[minimum - 1]
    assert not bulk[first_valid.strftime("%Y-%m-%d")].startswith("N/A")
    safe_lookback = (pd.Timestamp(DAY) - first_valid).days
    assert f"{DAY}:" in y_finance.get_stock_stats_indicators_window("AAPL", indicator, DAY, safe_lookback)
    unsafe_lookback = (pd.Timestamp(DAY) - frame["Date"].iloc[minimum - 2]).days
    per_day = Mock(side_effect=AssertionError("must not use a separate daily fallback"))
    monkeypatch.setattr(y_finance, "get_stockstats_indicator", per_day)
    with pytest.raises(InsufficientIndicatorHistoryError, match="requested date"):
        y_finance.get_stock_stats_indicators_window("AAPL", indicator, DAY, unsafe_lookback)
    per_day.assert_not_called()


@pytest.mark.parametrize("indicator", MINIMUMS)
def test_sufficient_history_preserves_existing_values_and_input(monkeypatch, indicator):
    frame = history(700)
    original = frame.copy(deep=True)
    supply(monkeypatch, frame)
    expected = wrap(frame.copy())[indicator]
    bulk = y_finance._get_stock_stats_bulk("AAPL", indicator, DAY)
    for row in range(600, len(frame)):
        key = frame["Date"].iloc[row].strftime("%Y-%m-%d")
        assert float(bulk[key]) == float(expected.iloc[row])
    pd.testing.assert_frame_equal(frame, original)


@pytest.mark.parametrize("extra_date", ["2026-10-22", None, "bad-date", "2026-02-30"])
def test_unknown_or_future_date_cannot_satisfy_observation_count(monkeypatch, extra_date):
    frame = history(199)
    extra = {"Date": extra_date, "Open": 1, "High": 2, "Low": 1, "Close": 1, "Volume": 1}
    frame["Date"] = frame["Date"].astype(object)
    frame = pd.concat([frame, pd.DataFrame([extra])], ignore_index=True)
    supply(monkeypatch, frame)
    with pytest.raises(InsufficientIndicatorHistoryError, match="found 199"):
        y_finance._get_stock_stats_bulk("AAPL", "close_200_sma", DAY)


def test_future_malformed_values_cannot_change_past_calculation(monkeypatch):
    frame = history(220)
    supply(monkeypatch, frame)
    baseline = y_finance._get_stock_stats_bulk("AAPL", "rsi", DAY)
    future = {"Date": pd.Timestamp("2026-10-22"), "Open": None, "High": None,
              "Low": None, "Close": float("inf"), "Volume": None}
    supply(monkeypatch, pd.concat([frame, pd.DataFrame([future])], ignore_index=True))
    assert y_finance._get_stock_stats_bulk("AAPL", "rsi", DAY) == baseline


@pytest.mark.parametrize("frame", [history(0), pd.DataFrame({"Close": [100]})])
def test_empty_or_undated_history_fails(monkeypatch, frame):
    supply(monkeypatch, frame)
    with pytest.raises(InsufficientIndicatorHistoryError):
        y_finance.get_stockstats_indicator("AAPL", "close_200_sma", DAY)


def test_duplicate_dates_do_not_count_as_new_observations(monkeypatch):
    frame = history(199)
    supply(monkeypatch, pd.concat([frame, frame.tail(1)], ignore_index=True))
    with pytest.raises(InsufficientIndicatorHistoryError, match="found 199"):
        y_finance._get_stock_stats_bulk("AAPL", "close_200_sma", DAY)


@pytest.mark.parametrize("symbol,market", [("AAPL", "US"), ("005930.KS", "KR")])
def test_middle_missing_session_is_not_a_holiday_or_complete_window(monkeypatch, symbol, market):
    frame = history(240, market=market).drop(index=230)
    supply(monkeypatch, frame)
    with pytest.raises(InsufficientIndicatorHistoryError, match="missing trading sessions"):
        y_finance.get_stock_stats_indicators_window(symbol, "close_200_sma", DAY, 30)


@pytest.mark.parametrize("symbol,market", [("AAPL", "US"), ("005930.KS", "KR")])
def test_real_holidays_do_not_require_fabricated_bars(monkeypatch, symbol, market):
    frame = history(300, market=market)
    supply(monkeypatch, frame)
    assert f"{DAY}:" in y_finance.get_stock_stats_indicators_window(symbol, "close_200_sma", DAY, 30)


def test_historical_calendar_uses_requested_bounds_not_default_cache(monkeypatch):
    # Build a separate instance without broadening xcals' cached default.
    calendar_type = type(xcals.get_calendar("XNYS"))
    historical_calendar = calendar_type(start="1999-01-01", end="2000-12-31")
    frame = history(220)
    frame["Date"] = historical_calendar.sessions[-220:].tz_localize(None)
    day = frame["Date"].iloc[-1].strftime("%Y-%m-%d")
    supply(monkeypatch, frame)
    expected = float(wrap(frame.copy())["close_200_sma"].iloc[-1])
    assert stats.StockstatsUtils.get_stock_stats("AAPL", "close_200_sma", day) == expected
    assert float(y_finance._get_stock_stats_bulk("AAPL", "close_200_sma", day)[day]) == expected


def test_weekend_observation_cannot_inflate_history(monkeypatch):
    frame = history(220)
    extra = frame.tail(1).copy()
    extra["Date"] = pd.Timestamp("2026-10-18")
    supply(monkeypatch, pd.concat([frame, extra], ignore_index=True))
    with pytest.raises(InsufficientIndicatorHistoryError, match="non-session bars"):
        y_finance._get_stock_stats_bulk("AAPL", "close_200_sma", DAY)


def test_missing_latest_trading_bar_does_not_become_nontrading_day(monkeypatch):
    supply(monkeypatch, history(220).iloc[:-1])
    with pytest.raises(InsufficientIndicatorHistoryError, match="missing trading sessions"):
        y_finance.get_stockstats_indicator("AAPL", "close_200_sma", DAY)


def test_no_observed_weekend_window_is_not_a_successful_indicator(monkeypatch):
    supply(monkeypatch, history(220))
    with pytest.raises(InsufficientIndicatorHistoryError, match="No observed"):
        y_finance.get_stock_stats_indicators_window("AAPL", "close_200_sma", "2026-10-18", 0)
    with pytest.raises(InsufficientIndicatorHistoryError, match="No observed"):
        y_finance.get_stockstats_indicator("AAPL", "close_200_sma", "2026-10-18")
    result = y_finance.get_stock_stats_indicators_window("AAPL", "close_200_sma", "2026-10-18", 7)
    assert "2026-10-18: N/A: No observed daily bar" in result
    assert "2026-10-16:" in result


def test_undefined_volume_indicator_is_not_success(monkeypatch):
    frame = history(30)
    frame["Volume"] = 0
    supply(monkeypatch, frame)
    assert y_finance._get_stock_stats_bulk("AAPL", "vwma", DAY)[DAY].startswith("N/A")
    with pytest.raises(InsufficientIndicatorHistoryError):
        y_finance.get_stockstats_indicator("AAPL", "vwma", DAY)
    with pytest.raises(InsufficientIndicatorHistoryError):
        y_finance.get_stock_stats_indicators_window("AAPL", "vwma", DAY, 0)


@pytest.mark.parametrize("invalid", [None, float("nan"), float("inf"), 0.0])
def test_invalid_middle_price_is_not_a_valid_observation(monkeypatch, invalid):
    frame = history(210)
    frame.loc[100, "Close"] = invalid
    supply(monkeypatch, frame)
    with pytest.raises(InsufficientIndicatorHistoryError, match="invalid Close"):
        y_finance._get_stock_stats_bulk("AAPL", "close_200_sma", DAY)


def test_long_lookback_does_not_claim_complete_indicator_history(monkeypatch):
    supply(monkeypatch, history(700))
    with pytest.raises(InsufficientIndicatorHistoryError, match="requested date"):
        y_finance.get_stock_stats_indicators_window("AAPL", "close_200_sma", DAY, 2000)


@pytest.mark.parametrize("lookback", [-1, True, 1.5, "30", 10**20])
def test_invalid_lookback_is_rejected_without_loading(monkeypatch, lookback):
    load = Mock(side_effect=AssertionError("invalid request must not fetch"))
    monkeypatch.setattr(y_finance, "load_ohlcv", load)
    with pytest.raises(VendorInputError):
        y_finance.get_stock_stats_indicators_window("AAPL", "close_200_sma", DAY, lookback)
    load.assert_not_called()


@pytest.mark.parametrize("symbol,market,optin", [("AAPL", "US", False), ("AAPL", "US", True), ("005930.KS", "KR", True)])
def test_upper_vendor_and_agent_tool_cannot_hide_insufficient_history(monkeypatch, symbol, market, optin):
    from tradingagents.agents.utils.technical_indicators_tools import get_indicators
    if optin:
        monkeypatch.setenv("TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED", "1")
    supply(monkeypatch, history(199, market=market))
    alternative = Mock(return_value="success-shaped unverified indicator")
    monkeypatch.setitem(interface.VENDOR_METHODS, "get_indicators", {
        "yfinance": y_finance.get_stock_stats_indicators_window, "alpha_vantage": alternative,
    })
    with run_config({"tool_vendors": {"get_indicators": "yfinance,alpha_vantage"}}):
        with pytest.raises(InsufficientIndicatorHistoryError):
            get_indicators.invoke({"symbol": symbol, "indicator": "close_200_sma", "curr_date": DAY, "look_back_days": 0})
    alternative.assert_not_called()
    assert interface.snapshot_tool_requests()[-1]["status"] == "error"
    events = interface.snapshot_tool_telemetry()
    assert len(events) == 1
    assert events[0]["status"] == "error"
    assert events[0]["fallback"] is False
    evidence = assess_with_other_required_methods_available()
    assert evidence["status"] == "REQUIRED_EVIDENCE_MISSING"
    assert evidence["missing_required_methods"] == ["get_indicators"]
    assert evidence_review_reason({"request_evidence": evidence}) == "required_research_evidence_missing"


@pytest.mark.parametrize("lookback,expected", [(0, "REQUIRED_EVIDENCE_MISSING"), (7, "COMPLETE")])
def test_weekend_window_evidence_depends_on_actual_observed_values(monkeypatch, lookback, expected):
    from tradingagents.agents.utils.technical_indicators_tools import get_indicators
    supply(monkeypatch, history(220))
    alternative = Mock(return_value="must not repair a zero-observation window")
    monkeypatch.setitem(interface.VENDOR_METHODS, "get_indicators", {
        "yfinance": y_finance.get_stock_stats_indicators_window, "alpha_vantage": alternative,
    })
    with run_config({"tool_vendors": {"get_indicators": "yfinance,alpha_vantage"}}):
        args = {"symbol": "AAPL", "indicator": "close_200_sma", "curr_date": "2026-10-18", "look_back_days": lookback}
        if lookback == 0:
            with pytest.raises(InsufficientIndicatorHistoryError, match="No observed"):
                get_indicators.invoke(args)
            assert interface.snapshot_tool_requests()[-1]["status"] == "error"
            assert interface.snapshot_tool_requests()[-1]["result_sha256"] is None
        else:
            result = get_indicators.invoke(args)
            assert "2026-10-18: N/A: No observed daily bar" in result
            assert interface.snapshot_tool_requests()[-1]["status"] == "available"
    alternative.assert_not_called()
    evidence = assess_with_other_required_methods_available()
    assert evidence["status"] == expected
    assert evidence_review_reason({"request_evidence": evidence}) == ("required_research_evidence_missing" if lookback == 0 else None)


def test_period_override_is_checked_without_changing_calculation(monkeypatch):
    old = stockstats.set_dft_window("rsi", 21)
    try:
        assert stats.indicator_minimum_observations("rsi") == 22
        supply(monkeypatch, history(21))
        with pytest.raises(InsufficientIndicatorHistoryError, match="requires 22"):
            y_finance._get_stock_stats_bulk("AAPL", "rsi", DAY)
        frame = history(100)
        supply(monkeypatch, frame)
        assert float(y_finance._get_stock_stats_bulk("AAPL", "rsi", DAY)[DAY]) == float(wrap(frame.copy())["rsi"].iloc[-1])
    finally:
        stockstats.set_dft_window("rsi", old)


def test_rsi_counterexample_keeps_full_history_instead_of_truncating(monkeypatch):
    frame = history(700)
    close = np.r_[np.linspace(100.0, 200.0, 445), np.full(255, 200.0)]
    for column in ("Open", "Close"):
        frame[column] = close
    frame["High"], frame["Low"] = close + 1, close - 1
    supply(monkeypatch, frame)
    assert float(y_finance._get_stock_stats_bulk("AAPL", "rsi", DAY)[DAY]) == 100.0
    assert float(wrap(frame.tail(255).copy())["rsi"].iloc[-1]) == 50.0
