"""Currency metadata uses the existing Yahoo snapshot, never another request."""
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pandas as pd
import pytest

from tradingagents.dataflows import integrity, interface, y_finance
from tradingagents.dataflows.vendor_exceptions import VendorInputError


DAY = "2026-10-26"
QUOTE = "Vendor-reported Trading Currency (info.currency): "
FINANCIAL = "Vendor-reported Financial Reporting Currency (info.financialCurrency): "


@pytest.fixture(autouse=True)
def fixed_clock(monkeypatch):
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            value = datetime(2026, 10, 26, 12, tzinfo=timezone.utc)
            return value.astimezone(tz) if tz is not None else value.replace(tzinfo=None)

    monkeypatch.setattr(integrity, "datetime", Clock)
    monkeypatch.setattr(y_finance, "datetime", Clock)
    interface.reset_tool_telemetry()
    yield
    interface.reset_tool_telemetry()


def overview(monkeypatch, metadata, *, ticker="000660.KS"):
    info = {"longName": "Fixture company", "marketCap": 1234567890123,
            "totalRevenue": 987654321098, "trailingEps": 123.456789, **metadata}
    resolver = Mock(return_value=(ticker, info, []))
    monkeypatch.setattr(y_finance, "_resolve_info_with_symbol_fallback", resolver)
    monkeypatch.setattr(y_finance.yf, "Ticker", Mock(side_effect=AssertionError("extra provider request")))
    result = y_finance.get_fundamentals(ticker, curr_date=DAY)
    resolver.assert_called_once_with(ticker)
    y_finance.yf.Ticker.assert_not_called()
    return result


@pytest.mark.parametrize("quote,financial", [("KRW", "KRW"), ("USD", "TWD"), ("GBP", "USD"), ("ZZZ", "YYY")])
def test_separate_vendor_tokens_preserve_numbers_and_do_not_claim_verified_iso(monkeypatch, quote, financial):
    result = overview(monkeypatch, {"currency": quote, "financialCurrency": financial})
    assert QUOTE + quote in result and FINANCIAL + financial in result
    assert "Market Cap: 1234567890123" in result
    assert "Revenue (TTM): 987654321098" in result and "EPS (TTM): 123.456789" in result
    assert "Current vendor snapshot; not verified point-in-time." in result
    assert "vendor tokens only: code format does not verify ISO registration" in result
    assert "financial-statement units, per-share or ADR basis, or filing/publication times" in result


@pytest.mark.parametrize("metadata,quote,financial", [
    ({"currency": "USD"}, "USD", "UNVERIFIED_MISSING"),
    ({"financialCurrency": "KRW"}, "UNVERIFIED_MISSING", "KRW"),
    ({}, "UNVERIFIED_MISSING", "UNVERIFIED_MISSING"),
    ({"currency": None, "financialCurrency": " \t"}, "UNVERIFIED_MISSING", "UNVERIFIED_MISSING"),
])
def test_missing_side_is_not_inferred_from_other_side_or_korean_ticker(monkeypatch, metadata, quote, financial):
    result = overview(monkeypatch, metadata)
    assert QUOTE + quote in result and FINANCIAL + financial in result


@pytest.mark.parametrize("value,expected", [
    ("GBp", "UNVERIFIED_NONSTANDARD_VENDOR_TOKEN"),
    ("usd", "UNVERIFIED_NONSTANDARD_VENDOR_TOKEN"),
    ("uSd", "UNVERIFIED_NONSTANDARD_VENDOR_TOKEN"),
    (True, "UNVERIFIED_MALFORMED"), (123, "UNVERIFIED_MALFORMED"),
    (["PRIVATE_TOKEN"], "UNVERIFIED_MALFORMED"),
    ({"PRIVATE_TOKEN": "secret"}, "UNVERIFIED_MALFORMED"),
    ("USD\nPRIVATE_TOKEN", "UNVERIFIED_MALFORMED"),
    ("U$D", "UNVERIFIED_MALFORMED"), ("ＵＳＤ", "UNVERIFIED_MALFORMED"),
    (" USD ", "UNVERIFIED_MALFORMED"),
])
def test_malformed_or_nonstandard_tokens_are_not_echoed_or_uppercased(monkeypatch, value, expected):
    result = overview(monkeypatch, {"currency": value, "financialCurrency": value})
    assert QUOTE + expected in result and FINANCIAL + expected in result
    assert "PRIVATE_TOKEN" not in result
    assert QUOTE + "GBP" not in result and FINANCIAL + "GBP" not in result


def test_symbol_fallback_keeps_one_successful_info_read_and_exact_reported_currency(monkeypatch):
    accesses = []

    class Ticker:
        def __init__(self, symbol):
            self.symbol = symbol

        @property
        def info(self):
            accesses.append(self.symbol)
            return {"longName": "Fixture KQ", "currency": "USD", "financialCurrency": "KRW"} if self.symbol == "058470.KQ" else {}

    monkeypatch.setattr(y_finance.yf, "Ticker", Ticker)
    monkeypatch.setattr(y_finance, "yf_retry", lambda callback: callback())
    result = y_finance.get_fundamentals("058470.KS", curr_date=DAY)
    assert accesses == ["058470.KS", "058470", "058470.KQ"]
    assert "# Company Fundamentals for 058470.KQ" in result
    assert QUOTE + "USD" in result and FINANCIAL + "KRW" in result


def test_empty_info_remains_unavailable_without_fabricated_metadata(monkeypatch):
    resolver = Mock(return_value=(None, None, ["AAPL: empty info"]))
    monkeypatch.setattr(y_finance, "_resolve_info_with_symbol_fallback", resolver)
    result = y_finance.get_fundamentals("AAPL", curr_date=DAY)
    assert result.startswith("No fundamentals data found")
    assert QUOTE not in result and FINANCIAL not in result


@pytest.mark.parametrize("value", ["2026-10-25", "2020-03-01"])
def test_historical_leaf_never_reads_current_currency_metadata(monkeypatch, value):
    resolver = Mock(side_effect=AssertionError("historical snapshot lookup"))
    monkeypatch.setattr(y_finance, "_resolve_info_with_symbol_fallback", resolver)
    result = y_finance.get_fundamentals("AAPL", curr_date=value)
    assert "current snapshot, not a historical vintage" in result
    assert QUOTE not in result and FINANCIAL not in result
    resolver.assert_not_called()


def route(monkeypatch):
    resolver = Mock(return_value=("AAPL", {"longName": "Fixture", "currency": "USD", "financialCurrency": "TWD"}, []))
    monkeypatch.setattr(y_finance, "_resolve_info_with_symbol_fallback", resolver)
    monkeypatch.setattr(interface, "get_config", lambda: {"analysis_as_of": DAY, "point_in_time_strict": False})
    monkeypatch.setattr(interface, "get_vendor", lambda *_: "yfinance")
    monkeypatch.setitem(interface.VENDOR_METHODS, "get_fundamentals", {"yfinance": y_finance.get_fundamentals})
    return resolver


@pytest.mark.parametrize("value", ["2026-10-27", "invalid", "2026-02-30", "20261026", "2026-1-01"])
def test_router_rejects_future_or_invalid_dates_before_provider(monkeypatch, value):
    resolver = route(monkeypatch)
    with pytest.raises(VendorInputError):
        interface.route_to_vendor("get_fundamentals", "AAPL", curr_date=value)
    resolver.assert_not_called()


@pytest.mark.parametrize("mode", ["omitted", "none", "empty", "positional_none"])
def test_router_inherits_omitted_cutoff_without_new_currency_lookup(monkeypatch, mode):
    resolver = route(monkeypatch)
    if mode == "positional_none":
        result = interface.route_to_vendor("get_fundamentals", "AAPL", None)
    else:
        kwargs = {} if mode == "omitted" else {"curr_date": None if mode == "none" else ""}
        result = interface.route_to_vendor("get_fundamentals", "AAPL", **kwargs)
    assert QUOTE + "USD" in result and FINANCIAL + "TWD" in result
    resolver.assert_called_once_with("AAPL")


@pytest.mark.parametrize("function,property_name", [
    (y_finance.get_balance_sheet, "quarterly_balance_sheet"),
    (y_finance.get_cashflow, "quarterly_cashflow"),
    (y_finance.get_income_statement, "quarterly_income_stmt"),
])
def test_statement_getters_do_not_fetch_info_for_currency(monkeypatch, function, property_name):
    ticker = SimpleNamespace(**{property_name: pd.DataFrame({pd.Timestamp(DAY): [100]}, index=["Fixture"] )})
    monkeypatch.setattr(y_finance.yf, "Ticker", Mock(return_value=ticker))
    monkeypatch.setattr(y_finance, "_resolve_info_with_symbol_fallback", Mock(side_effect=AssertionError("statement info lookup")))
    monkeypatch.setattr(y_finance, "filter_financials_by_date", lambda data, _: data)
    result = function("AAPL", curr_date=DAY)
    assert "Fixture,100" in result
    y_finance._resolve_info_with_symbol_fallback.assert_not_called()
    assert QUOTE not in result and FINANCIAL not in result
