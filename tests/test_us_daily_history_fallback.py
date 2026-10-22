"""Offline contracts for complete US history and one source per research run."""

from datetime import date, datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pandas as pd
import pytest

from tradingagents.dataflows import daily_history, daily_history_selection, stockstats_utils, us_daily_history as us, y_finance
from tradingagents.dataflows.config import run_config
from tradingagents.dataflows.daily_history_selection import get_selected_daily_history
from tradingagents.dataflows.vendor_exceptions import VendorInputError, VendorMalformedResponseError
from tradingagents.portfolio.kis import KisApiError, KisClient


END = "2026-10-21"
START = "2026-10-20"
WARMUP = "2021-10-21"
REQUIRED = [date.fromisoformat(value) for value in (WARMUP, START, END)]
REAL_SESSIONS = us._sessions


def bar(day=END, **values):
    return {"xymd": str(day).replace("-", ""), "open": "100", "high": "110",
            "low": "90", "clos": "105", "tvol": "200", **values}


def payload(rows=None):
    return ({"output2": [bar(day) for day in reversed(REQUIRED)] if rows is None else rows},
            {"tr_cont": "F"})


def yahoo(*, day=END, close=float("nan")):
    return pd.DataFrame({"Open": [100], "High": [110], "Low": [90],
                         "Close": [close], "Volume": [200]},
                        index=pd.DatetimeIndex([day], name="Date"))


@pytest.fixture(autouse=True)
def isolated_run(monkeypatch, tmp_path):
    us._CACHE.clear()
    monkeypatch.setenv("TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED", "1")
    monkeypatch.setattr(us, "get_api_key", lambda _: "offline-test-value")
    monkeypatch.setattr(us, "time", SimpleNamespace(monotonic=lambda: 100.0, sleep=lambda _: None))
    monkeypatch.setattr(y_finance.yf, "Ticker", Mock(side_effect=AssertionError("unmocked Yahoo call")))
    monkeypatch.setattr(stockstats_utils.yf, "download", Mock(side_effect=AssertionError("unmocked Yahoo call")))
    monkeypatch.setattr("tradingagents.charting.capture.capture_daily_frame", Mock())
    with run_config({"data_cache_dir": str(tmp_path)}):
        yield
    us._CACHE.clear()


@pytest.fixture
def broker(monkeypatch):
    client = Mock(spec=["request_json"])
    client.request_json.return_value = payload()
    monkeypatch.setattr(KisClient, "from_api_keys", Mock(return_value=client))
    monkeypatch.setattr(us, "_sessions", Mock(return_value=REQUIRED))
    return client


def test_invalid_yahoo_replaced_by_full_source_with_five_year_warmup(broker):
    original = yahoo().reset_index()
    result = daily_history.validate_with_fallback(original, "AAPL", START, END)
    assert result["Date"].dt.strftime("%Y-%m-%d").tolist() == [START, END]
    assert result["Close"].tolist() == [105, 105]
    assert pd.isna(original.iloc[-1]["Close"])
    us._sessions.assert_any_call(date.fromisoformat(WARMUP), date.fromisoformat(END))
    selected = get_selected_daily_history("AAPL", END)
    assert selected["frame"]["Date"].min() == pd.Timestamp(WARMUP)
    assert result.attrs["source"] == us.SOURCE
    assert result.attrs["adjustment"] == "MODP=1"
    assert result.attrs["complete"] is True
    assert result.attrs["session_count"] == 3
    assert len(result.attrs["series_sha256"]) == 64
    assert "not a historical snapshot vintage" in daily_history.source_note(result)
    request = broker.request_json.call_args.kwargs
    assert request["method"] == "GET"
    assert request["path"] == "/uapi/overseas-price/v1/quotations/dailyprice"
    assert request["tr_id"] == "HHDFS76240000"
    assert request["params"] == {"AUTH": "", "EXCD": "NAS", "SYMB": "AAPL",
                                 "GUBN": "0", "BYMD": "20261021", "MODP": "1"}
    assert len(broker.method_calls) == 1
    assert broker.method_calls[0][0] == "request_json"


def test_healthy_yahoo_remains_primary_without_broker_call(broker):
    result = us.validate_with_us_fallback(yahoo(close=104).reset_index(), "AAPL", START, END)
    assert result.iloc[-1]["Close"] == 104
    assert get_selected_daily_history("AAPL", END)["source"] == "yfinance"
    assert not us.source_note(result)
    broker.request_json.assert_not_called()


@pytest.mark.parametrize("data", [pd.DataFrame(), yahoo(day=START, close=104).reset_index()])
def test_empty_or_stale_yahoo_requires_exact_latest_broker_session(broker, data):
    result = us.validate_with_us_fallback(data, "AAPL", START, END)
    assert result.iloc[-1]["Date"] == pd.Timestamp(END)
    assert result.attrs["source"] == us.SOURCE


@pytest.mark.parametrize("field,value", [
    ("clos", ""), ("clos", "NaN"), ("clos", "inf"), ("clos", "0"),
    ("open", "0"), ("high", "99"), ("low", "106"), ("tvol", "-1"),
    ("tvol", "NaN"), ("tvol", None),
])
def test_malformed_older_broker_bar_fails_even_when_latest_is_good(broker, field, value):
    broker.request_json.return_value = payload([bar(), bar(START), bar(WARMUP, **{field: value})])
    with pytest.raises(VendorMalformedResponseError, match="OHLCV"):
        us.load_us_daily_bars("AAPL", START, END)
    assert not us._CACHE


@pytest.mark.parametrize("rows", [
    None, [None], [{"clos": "105"}], [bar("2026-10-xx")],
    [bar("20260230")], [bar("2026-10-21T00:00:00-04:00")],
])
def test_missing_or_invalid_date_and_payload_fail_closed(broker, rows):
    broker.request_json.return_value = ({"output2": rows}, {})
    with pytest.raises(VendorMalformedResponseError):
        us.load_us_daily_bars("AAPL", START, END)
    assert not us._CACHE


def test_missing_ohlcv_field_is_not_synthesized(broker):
    broken = bar(WARMUP)
    del broken["tvol"]
    broker.request_json.return_value = payload([bar(), bar(START), broken])
    with pytest.raises(VendorMalformedResponseError, match="incomplete OHLCV"):
        us.load_us_daily_bars("AAPL", START, END)
    assert not us._CACHE


def test_future_bad_row_is_excluded_before_value_and_pagination_checks(broker):
    broker.request_json.return_value = payload([bar("2026-10-22", clos="bad"), *payload()[0]["output2"]])
    result = us.load_us_daily_bars("AAPL", START, END)
    assert result["Date"].max() == pd.Timestamp(END)
    assert len(result) == 3


@pytest.mark.parametrize("rows", [
    [bar(START), bar(WARMUP)],
    [bar(), bar(WARMUP)],
    [bar(), bar(START), bar("2021-10-23"), bar(WARMUP)],
])
def test_latest_missing_calendar_hole_and_non_session_bar_are_rejected(broker, rows):
    broker.request_json.return_value = payload(rows)
    with pytest.raises(VendorMalformedResponseError, match="required sessions"):
        us.load_us_daily_bars("AAPL", START, END)
    assert not us._CACHE


def test_ipo_short_history_cannot_replace_full_warmup(broker):
    broker.request_json.side_effect = [payload([bar(), bar(START)]), payload([])]
    with pytest.raises(VendorMalformedResponseError, match="ended before the required range"):
        us.load_us_daily_bars("AAPL", START, END)
    assert not us._CACHE


def test_identical_duplicates_deduplicate_but_conflicting_duplicates_fail(broker):
    broker.request_json.return_value = payload([bar(), *payload()[0]["output2"]])
    assert len(us.load_us_daily_bars("AAPL", START, END)) == 3
    us._CACHE.clear()
    broker.request_json.return_value = payload([bar(clos="104"), *payload()[0]["output2"]])
    with pytest.raises(VendorMalformedResponseError, match="conflicting duplicate"):
        us.load_us_daily_bars("AAPL", START, END)
    assert not us._CACHE


def test_cursor_moves_before_oldest_date_and_repeated_page_fails(broker):
    first = payload([bar(), bar(START)])
    broker.request_json.side_effect = [first, payload([bar(WARMUP)])]
    result = us.load_us_daily_bars("AAPL", START, END)
    assert len(result) == 3
    assert broker.request_json.call_args_list[1].kwargs["params"]["BYMD"] == "20261019"
    us._CACHE.clear()
    broker.request_json.reset_mock()
    broker.request_json.side_effect = [first, first]
    with pytest.raises(VendorMalformedResponseError, match="no progress"):
        us.load_us_daily_bars("AAPL", START, END)
    assert broker.request_json.call_count == 2


def test_only_future_rows_cannot_advance_pagination(broker):
    broker.request_json.return_value = payload([bar("2026-10-22", clos="bad")])
    with pytest.raises(VendorMalformedResponseError, match="no progress"):
        us.load_us_daily_bars("AAPL", START, END)
    assert not us._CACHE


def test_twenty_page_budget_is_enforced_without_admitting_partial_history(broker):
    broker.request_json.side_effect = lambda **kw: payload([bar(kw["params"]["BYMD"])])
    with pytest.raises(VendorMalformedResponseError, match="bounded page limit"):
        us.load_us_daily_bars("AAPL", START, END)
    assert broker.request_json.call_count == 20
    assert all(call.kwargs["method"] == "GET" for call in broker.request_json.call_args_list)
    assert not us._CACHE


def test_elapsed_time_budget_stops_before_next_request(broker, monkeypatch):
    clock = iter([0.0, 120.0])
    monkeypatch.setattr(us.time, "monotonic", lambda: next(clock))
    with pytest.raises(VendorMalformedResponseError, match="time limit"):
        us.load_us_daily_bars("AAPL", START, END)
    broker.request_json.assert_not_called()


def test_nyse_lookup_and_share_class_mapping_are_explicit(broker):
    broker.request_json.side_effect = [payload([]), payload()]
    result = us.load_us_daily_bars("BRK-B", START, END)
    assert result.attrs["exchange"] == "NYS"
    assert [call.kwargs["params"]["EXCD"] for call in broker.request_json.call_args_list] == ["NAS", "NYS"]
    assert {call.kwargs["params"]["SYMB"] for call in broker.request_json.call_args_list} == {"BRK/B"}


def test_empty_markets_stop_after_three_venues(broker):
    broker.request_json.return_value = payload([])
    with pytest.raises(VendorMalformedResponseError, match="required range"):
        us.load_us_daily_bars("AAPL", START, END)
    assert [call.kwargs["params"]["EXCD"] for call in broker.request_json.call_args_list] == ["NAS", "NYS", "AMS"]


def test_later_page_error_propagates_without_switching_market_or_caching(broker):
    broker.request_json.side_effect = [payload([bar(), bar(START)]), KisApiError("offline failure")]
    with pytest.raises(KisApiError, match="offline failure"):
        us.load_us_daily_bars("AAPL", START, END)
    assert broker.request_json.call_count == 2
    assert {call.kwargs["params"]["EXCD"] for call in broker.request_json.call_args_list} == {"NAS"}
    assert not us._CACHE


@pytest.mark.parametrize("symbol", ["005930.KS", "^GSPC", "BRK-A", "../AAPL", "AAPL/USD", ""])
def test_ineligible_symbol_never_requests_broker(broker, symbol):
    assert us.load_us_daily_bars(symbol, START, END) is None
    broker.request_json.assert_not_called()


def test_no_optin_or_credentials_never_requests_broker(broker, monkeypatch):
    monkeypatch.delenv("TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED")
    assert us.load_us_daily_bars("AAPL", START, END) is None
    monkeypatch.setenv("TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED", "1")
    monkeypatch.setattr(us, "get_api_key", lambda _: None)
    assert us.load_us_daily_bars("AAPL", START, END) is None
    broker.request_json.assert_not_called()


@pytest.mark.parametrize("start,end", [("bad", END), (START, "2026-02-30"), (END, START)])
def test_invalid_requested_dates_never_request_broker(broker, start, end):
    with pytest.raises(VendorInputError):
        us.load_us_daily_bars("AAPL", start, end)
    broker.request_json.assert_not_called()


def test_cache_reuses_warmup_and_isolated_values_but_keys_symbol_and_end(broker, monkeypatch):
    one = us.load_us_daily_bars("AAPL", START, END)
    one.loc[0, "Close"] = 1
    one.attrs["source"] = "mutated"
    two = us.load_us_daily_bars("AAPL", WARMUP, END)
    assert two.loc[0, "Close"] == 105
    assert two.attrs["source"] == us.SOURCE
    assert broker.request_json.call_count == 1
    us.load_us_daily_bars("MSFT", START, END)
    assert broker.request_json.call_count == 2
    required = [date(2021, 10, 20), date(2026, 10, 20)]
    monkeypatch.setattr(us, "_sessions", Mock(return_value=required))
    broker.request_json.return_value = payload([bar(day) for day in reversed(required)])
    us.load_us_daily_bars("AAPL", START, START)
    assert broker.request_json.call_count == 3
    assert ("AAPL", "2021-10-20", START) in us._CACHE


def test_cache_expiry_rechecks_provider_and_does_not_replace_good_cache_on_failure(broker, monkeypatch):
    us.load_us_daily_bars("AAPL", START, END)
    monkeypatch.setattr(us.time, "monotonic", lambda: 401.0)
    broker.request_json.side_effect = RuntimeError("offline unavailable")
    with pytest.raises(RuntimeError, match="offline unavailable"):
        us.load_us_daily_bars("AAPL", START, END)
    assert broker.request_json.call_count == 2
    assert us._CACHE[("AAPL", WARMUP, END)][0] == 100


def test_yahoo_then_broker_source_change_is_rejected_with_original_selection(broker):
    us.validate_with_us_fallback(yahoo(close=104).reset_index(), "AAPL", START, END)
    with pytest.raises(VendorMalformedResponseError, match="source changed"):
        us.validate_with_us_fallback(yahoo().reset_index(), "AAPL", START, END)
    assert get_selected_daily_history("AAPL", END)["source"] == "yfinance"


def test_concurrent_first_broker_snapshot_wins_over_later_fetch(broker, monkeypatch):
    first = us.load_us_daily_bars("AAPL", START, END)
    second = first.copy()
    second["Close"] = 106
    monkeypatch.setattr(us, "load_us_daily_bars", Mock(return_value=second))
    original_select = daily_history_selection.select_daily_history

    def competing_selection(symbol, end_date, source, frame=None):
        original_select(symbol, end_date, source, frame=first)
        original_select(symbol, end_date, source, frame=frame)

    monkeypatch.setattr(daily_history_selection, "select_daily_history", competing_selection)
    result = us.validate_with_us_fallback(yahoo().reset_index(), "AAPL", START, END)
    assert result["Close"].tolist() == [105, 105]
    assert get_selected_daily_history("AAPL", END)["frame"]["Close"].tolist() == [105] * 3


@pytest.mark.parametrize("failure", [
    VendorMalformedResponseError("offline incomplete history"),
    VendorInputError("offline invalid requested date"),
    RuntimeError("offline provider failed"),
])
def test_bulk_failure_does_not_become_per_day_empty_success(broker, monkeypatch, failure):
    monkeypatch.setattr(y_finance, "_get_stock_stats_bulk", Mock(side_effect=failure))
    per_day = Mock(return_value="")
    monkeypatch.setattr(y_finance, "get_stockstats_indicator", per_day)
    with pytest.raises(type(failure), match="offline"):
        y_finance.get_stock_stats_indicators_window("AAPL", "close_200_sma", END, 10)
    per_day.assert_not_called()
    broker.request_json.assert_not_called()


@pytest.mark.parametrize("failure", [
    VendorMalformedResponseError("offline source changed"),
    VendorInputError("offline invalid date"),
    RuntimeError("offline provider failed"),
])
def test_single_indicator_failure_never_becomes_empty_success(broker, monkeypatch, failure):
    monkeypatch.setattr(stockstats_utils.StockstatsUtils, "get_stock_stats", Mock(side_effect=failure))
    with pytest.raises(type(failure), match="offline"):
        y_finance.get_stockstats_indicator("AAPL", "close_200_sma", END)
    broker.request_json.assert_not_called()


def test_stale_yahoo_with_missing_broker_credentials_still_fails_closed(broker, monkeypatch):
    monkeypatch.setattr(us, "get_api_key", lambda _: None)
    with pytest.raises(VendorMalformedResponseError, match="required completed US session"):
        us.validate_with_us_fallback(yahoo(day=START, close=104).reset_index(), "AAPL", START, END)
    broker.request_json.assert_not_called()
    assert get_selected_daily_history("AAPL", END) is None


def test_broker_price_pins_indicator_and_csv_paths_even_when_yahoo_recovers(broker, monkeypatch, tmp_path):
    ticker = Mock()
    ticker.history.return_value = yahoo()
    monkeypatch.setattr(y_finance.yf, "Ticker", Mock(return_value=ticker))
    csv = y_finance.get_YFin_data_online("AAPL", START, END)
    assert "OHLCV source: KIS overseas_dailyprice" in csv
    assert ticker.history.call_args.kwargs["end"] == "2026-10-22"
    ticker.history.return_value = yahoo(close=109)
    download = Mock(return_value=yahoo(close=109))
    monkeypatch.setattr(stockstats_utils.yf, "download", download)
    indicator = y_finance.get_stock_stats_indicators_window("AAPL", "close_10_ema", END, 0)
    again = y_finance.get_YFin_data_online("AAPL", START, END)
    assert "OHLCV source: KIS overseas_dailyprice" in indicator
    assert f"{END}: 105.0" in indicator
    assert "105.0" in again
    assert ticker.history.call_count == 1
    download.assert_not_called()
    assert broker.request_json.call_count == 1
    assert not list(tmp_path.glob("*.csv"))


def test_existing_bad_yahoo_disk_cache_stays_unchanged_after_broker_recovery(broker, tmp_path):
    today = pd.Timestamp.today()
    end = (today + pd.DateOffset(days=1)).strftime("%Y-%m-%d")
    path = tmp_path / f"AAPL-YFin-data-{WARMUP}-{end}.csv"
    yahoo().reset_index().to_csv(path, index=False)
    before = path.read_bytes()
    result = stockstats_utils.load_ohlcv("AAPL", END)
    assert result.attrs["source"] == us.SOURCE
    assert path.read_bytes() == before
    stockstats_utils.yf.download.assert_not_called()


def test_selected_snapshot_isolation_and_run_config_reset(broker):
    with run_config({}):
        us.validate_with_us_fallback(yahoo().reset_index(), "AAPL", START, END)
        one = get_selected_daily_history("AAPL", END)
        one["frame"].loc[0, "Close"] = 1
        assert get_selected_daily_history("AAPL", END)["frame"].loc[0, "Close"] == 105
    assert get_selected_daily_history("AAPL", END) is None
    with run_config({}):
        us.validate_with_us_fallback(yahoo(close=104).reset_index(), "AAPL", START, END)
        assert get_selected_daily_history("AAPL", END)["source"] == "yfinance"


def test_pinned_snapshot_cannot_supply_unrequested_earlier_history(broker):
    us.validate_with_us_fallback(yahoo().reset_index(), "AAPL", START, END)
    with pytest.raises(VendorMalformedResponseError, match="exceeds the pinned"):
        us.selected_history("AAPL", "2020-10-21", END)


def test_real_xnys_calendar_five_year_history_uses_bounded_mock_pages(broker, monkeypatch):
    import exchange_calendars as xcals

    class FixedClock(datetime):
        @classmethod
        def now(cls, tz=None):
            value = cls(2026, 10, 22, 12, tzinfo=timezone.utc)
            return value.astimezone(tz) if tz else value.replace(tzinfo=None)

    # Use the real calendar function while every broker transport stays mocked.
    monkeypatch.setattr(us, "_sessions", REAL_SESSIONS)
    monkeypatch.setattr(us, "datetime", FixedClock)
    calendar = xcals.get_calendar("XNYS")
    expected = [stamp.date() for stamp in calendar.sessions_in_range(WARMUP, END)]

    def request(**kwargs):
        cursor = datetime.strptime(kwargs["params"]["BYMD"], "%Y%m%d").date()
        rows = [bar(day) for day in reversed(expected) if day <= cursor][:100]
        return payload(rows)

    broker.request_json.side_effect = request
    result = us.load_us_daily_bars("AAPL", START, END)
    assert result["Date"].dt.date.tolist() == expected
    assert date(2025, 12, 25) not in expected
    assert 1000 < len(result) < 1400
    assert broker.request_json.call_count == (len(expected) + 99) // 100 <= 20
    assert result.attrs["session_count"] == len(expected)
