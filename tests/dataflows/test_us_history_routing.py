from unittest.mock import Mock

import pandas as pd
import pytest

from tradingagents.dataflows import interface
from tradingagents.dataflows.config import run_config
from tradingagents.dataflows.daily_history_selection import get_selected_daily_history, select_daily_history
from tradingagents.dataflows.us_daily_history import SOURCE
from tradingagents.dataflows.vendor_exceptions import VendorInputError, VendorMalformedResponseError


DAY = "2026-10-21"
METHODS = ("get_stock_data", "get_indicators")


def call(method, *, symbol="AAPL", keywords=False):
    if method == "get_stock_data":
        args = (symbol, "2026-10-01", DAY)
        kwargs = dict(symbol=symbol, start_date="2026-10-01", end_date=DAY)
    else:
        args = (symbol, "close_200_sma", DAY, 10)
        kwargs = dict(symbol=symbol, indicator="close_200_sma", curr_date=DAY, look_back_days=10)
    return interface.route_to_vendor(method, **kwargs) if keywords else interface.route_to_vendor(method, *args)


@pytest.fixture
def vendors(monkeypatch):
    monkeypatch.setenv("TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED", "1")
    result = {}
    for method in METHODS:
        result[method] = {"yfinance": Mock(return_value="verified Yahoo result"),
                          "alpha_vantage": Mock(return_value="verified Alpha Vantage result")}
        monkeypatch.setitem(interface.VENDOR_METHODS, method, result[method])
    interface.reset_tool_telemetry()
    yield result
    interface.reset_tool_telemetry()


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("error", [VendorMalformedResponseError("Daily history source changed"),
                                   RuntimeError("US history recovery unavailable")])
def test_default_us_wrapper_failure_cannot_fall_through_to_alpha(vendors, method, error):
    vendors[method]["yfinance"].side_effect = error
    with run_config({"tool_vendors": {method: "yfinance"}}):
        with pytest.raises(RuntimeError, match="No available vendor"):
            call(method)
    vendors[method]["alpha_vantage"].assert_not_called()
    assert interface.snapshot_tool_requests()[-1]["status"] == "error"


@pytest.mark.parametrize("method", METHODS)
def test_real_source_conflict_is_not_hidden_by_outer_vendor_fallback(vendors, method):
    def conflict(*args, **kwargs):
        select_daily_history("AAPL", DAY, SOURCE, pd.DataFrame({"Close": [105]}))
    vendors[method]["yfinance"].side_effect = conflict
    with run_config({"tool_vendors": {method: "yfinance"}}):
        select_daily_history("AAPL", DAY, "yfinance")
        with pytest.raises(RuntimeError, match="source changed"):
            call(method)
        assert get_selected_daily_history("AAPL", DAY)["source"] == "yfinance"
    vendors[method]["alpha_vantage"].assert_not_called()


@pytest.mark.parametrize("method", METHODS)
def test_empty_us_wrapper_result_cannot_fall_through_to_alpha(vendors, method):
    vendors[method]["yfinance"].return_value = "No data found"
    with run_config({"tool_vendors": {method: "yfinance,alpha_vantage"}}):
        assert call(method) == "No data found"
        assert get_selected_daily_history("AAPL", DAY) is None
    vendors[method]["alpha_vantage"].assert_not_called()
    assert interface.snapshot_tool_requests()[-1]["status"] == "unavailable"


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("source", ["yfinance", SOURCE])
def test_existing_yahoo_or_kis_pin_overrides_later_alpha_preference(vendors, method, source):
    with run_config({"tool_vendors": {method: "alpha_vantage"}}):
        original = pd.DataFrame({"Close": [105]}) if source == SOURCE else None
        select_daily_history("AAPL", DAY, source, original)
        assert call(method, keywords=True) == "verified Yahoo result"
        pinned = get_selected_daily_history("AAPL", DAY)
        assert pinned["source"] == source
        if source == SOURCE:
            assert pinned["frame"].iloc[0]["Close"] == 105
    vendors[method]["yfinance"].assert_called_once()
    vendors[method]["alpha_vantage"].assert_not_called()


@pytest.mark.parametrize("method", METHODS)
def test_explicit_alpha_success_pins_source_and_blocks_other_tool_switch(vendors, method):
    other = next(item for item in METHODS if item != method)
    with run_config({"tool_vendors": {method: "alpha_vantage", other: "yfinance"}}):
        assert call(method) == "verified Alpha Vantage result"
        assert get_selected_daily_history("AAPL", DAY)["source"] == "alpha_vantage"
        with pytest.raises(VendorInputError, match="source changed"):
            call(other)
    vendors[other]["yfinance"].assert_not_called()
    vendors[other]["alpha_vantage"].assert_not_called()


@pytest.mark.parametrize("method", METHODS)
def test_pinned_alpha_failure_cannot_switch_to_yahoo(vendors, method):
    with run_config({"tool_vendors": {method: "alpha_vantage"}}):
        assert call(method) == "verified Alpha Vantage result"
        vendors[method]["alpha_vantage"].side_effect = RuntimeError("provider outage")
        with pytest.raises(VendorInputError, match="source changed"):
            call(method)
    vendors[method]["yfinance"].assert_not_called()


@pytest.mark.parametrize("method", METHODS)
def test_unselected_explicit_alpha_failure_retains_existing_recovery(vendors, method):
    vendors[method]["alpha_vantage"].side_effect = RuntimeError("provider outage")
    def recovery(*args, **kwargs):
        select_daily_history("AAPL", DAY, SOURCE, pd.DataFrame({"Close": [105]}))
        return "verified full KIS history"
    vendors[method]["yfinance"].side_effect = recovery
    with run_config({"tool_vendors": {method: "alpha_vantage"}}):
        assert call(method) == "verified full KIS history"
        assert get_selected_daily_history("AAPL", DAY)["source"] == SOURCE


@pytest.mark.parametrize("method", METHODS)
def test_inflight_alpha_cannot_return_after_another_tool_selected_kis(vendors, method):
    def concurrent_selection(*args, **kwargs):
        select_daily_history("AAPL", DAY, SOURCE, pd.DataFrame({"Close": [105]}))
        return "incompatible Alpha Vantage result"
    vendors[method]["alpha_vantage"].side_effect = concurrent_selection
    with run_config({"tool_vendors": {method: "alpha_vantage"}}):
        with pytest.raises(VendorInputError, match="source changed"):
            call(method)
        assert get_selected_daily_history("AAPL", DAY)["source"] == SOURCE
    vendors[method]["yfinance"].assert_not_called()


@pytest.mark.parametrize("method", METHODS)
def test_concurrent_pin_at_alpha_commit_cannot_trigger_outer_fallback(vendors, monkeypatch, method):
    def raced_selection(symbol, end_date, source, frame=None):
        select_daily_history(symbol, end_date, SOURCE, pd.DataFrame({"Close": [105]}))
        select_daily_history(symbol, end_date, source, frame)
    monkeypatch.setattr(interface, "select_daily_history", raced_selection)
    with run_config({"tool_vendors": {method: "alpha_vantage"}}):
        with pytest.raises(VendorInputError, match="source changed"):
            call(method)
        assert get_selected_daily_history("AAPL", DAY)["source"] == SOURCE
    vendors[method]["yfinance"].assert_not_called()


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("symbol,optin", [("005930.KS", True), ("AAPL", False)])
def test_kr_and_us_optout_keep_existing_vendor_fallback(vendors, monkeypatch, method, symbol, optin):
    if not optin:
        monkeypatch.delenv("TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED")
    vendors[method]["yfinance"].side_effect = RuntimeError("provider outage")
    with run_config({"tool_vendors": {method: "yfinance"}}):
        assert call(method, symbol=symbol) == "verified Alpha Vantage result"
        assert get_selected_daily_history(symbol, DAY) is None
    vendors[method]["alpha_vantage"].assert_called_once()


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("keywords", [False, True])
@pytest.mark.parametrize("symbol", [" AAPL ", "aapl", "\tAaPl\n", " brk-b "])
@pytest.mark.parametrize("pinned", [False, True])
def test_equivalent_symbol_spelling_cannot_bypass_us_source_guard(
    vendors, method, keywords, symbol, pinned,
):
    canonical = symbol.strip().upper()
    vendors[method]["yfinance"].side_effect = VendorMalformedResponseError("pinned recovery failed")
    with run_config({"tool_vendors": {method: "yfinance,alpha_vantage"}}):
        if pinned:
            select_daily_history(canonical, DAY, SOURCE, pd.DataFrame({"Close": [105]}))
        with pytest.raises(RuntimeError, match="No available vendor"):
            call(method, symbol=symbol, keywords=keywords)
        selected = get_selected_daily_history(canonical, DAY)
        assert selected["source"] == SOURCE if pinned else selected is None
    vendors[method]["yfinance"].assert_called_once()
    vendors[method]["alpha_vantage"].assert_not_called()
    assert interface.snapshot_tool_requests()[-1]["status"] == "error"


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("keywords", [False, True])
def test_explicit_alpha_with_equivalent_symbol_keeps_canonical_source_pin(vendors, method, keywords):
    with run_config({"tool_vendors": {method: "alpha_vantage"}}):
        assert call(method, symbol=" aApL ", keywords=keywords) == "verified Alpha Vantage result"
        assert get_selected_daily_history("AAPL", DAY)["source"] == "alpha_vantage"
        assert call(method, symbol="AAPL", keywords=not keywords) == "verified Alpha Vantage result"
    assert vendors[method]["alpha_vantage"].call_count == 2
    vendors[method]["yfinance"].assert_not_called()
