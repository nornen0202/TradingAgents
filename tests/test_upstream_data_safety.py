import json
from types import SimpleNamespace
from unittest.mock import Mock

import pandas as pd
import pytest

from tradingagents.dataflows import alpha_vantage_fundamentals as av
from tradingagents.dataflows import interface, sec_edgar_statements as sec, y_finance, yfinance_news as news
from tradingagents.dataflows.stockstats_utils import filter_financials_by_date
from tradingagents.dataflows.vendor_exceptions import VendorInputError, VendorTransientError


def article(title, published="2020-02-01T12:00:00Z", symbols=None):
    return {"content": {"title": title, "pubDate": published, "relatedTickers": symbols or []}}


def test_empty_quote_feed_uses_only_tagged_search_articles(monkeypatch):
    ticker = Mock()
    ticker.get_news.return_value = []
    monkeypatch.setattr(news.yf, "Ticker", lambda symbol: ticker)
    search = Mock(return_value=SimpleNamespace(news=[
        article("valid", symbols=["aapl"]),
        article("unrelated", symbols=["MSFT"]),
        article("undated", None, ["AAPL"]),
        article("future", "2020-02-02T00:00:00Z", ["AAPL"]),
    ]))
    monkeypatch.setattr(news.yf, "Search", search)
    result = news.get_company_news_yfinance("aapl", "2020-02-01", "2020-02-01")
    assert "valid" in result
    assert all(title not in result for title in ("unrelated", "undated", "future"))
    assert "sample" in result
    assert ticker.get_news.call_count == 1
    assert search.call_args.args[0] == "AAPL"


def test_empty_search_is_unavailable_and_vendor_fallback_runs(monkeypatch):
    monkeypatch.setattr(news.yf, "Ticker", lambda _: SimpleNamespace(get_news=lambda **_: []))
    monkeypatch.setattr(news.yf, "Search", lambda *_, **__: SimpleNamespace(news=[article("other", symbols=["MSFT"])]))
    result = news.get_company_news_yfinance("AAPL", "2020-02-01", "2020-02-01")
    assert "unavailable" in result and "absence of news" in result
    assert interface.should_fallback(result)
    monkeypatch.setattr(interface, "get_vendor", lambda *_: "yfinance")
    monkeypatch.setitem(interface.VENDOR_METHODS, "get_company_news", {"yfinance": news.get_company_news_yfinance, "alpha_vantage": lambda *_: "secondary news"})
    assert interface.route_to_vendor("get_company_news", "AAPL", "2020-02-01", "2020-02-01") == "secondary news"


def test_healthy_quote_feed_does_not_search(monkeypatch):
    monkeypatch.setattr(news.yf, "Ticker", lambda _: SimpleNamespace(get_news=lambda **_: [article("feed")]))
    search = Mock(side_effect=AssertionError("unnecessary search"))
    monkeypatch.setattr(news.yf, "Search", search)
    assert "feed" in news.get_company_news_yfinance("AAPL", "2020-02-01", "2020-02-01")
    search.assert_not_called()


@pytest.mark.parametrize("payload", [
    {"content": None, "title": None, "summary": None, "publisher": None, "link": None},
    {"content": {"title": None, "summary": None, "provider": {"displayName": None}, "canonicalUrl": {"url": None}}},
])
def test_nullable_news_fields_have_usable_defaults(payload):
    item = news.normalize_yfinance_article(payload)
    assert item.title == "No title" and item.source == "Unknown"
    assert item.url == item.summary == ""


def test_macro_news_filters_unknown_dates_and_utc_boundary_before_limit(monkeypatch):
    batches = iter([
        [article("unknown", None), article("future", "2020-02-02T00:00:00Z"), article("unknown2", None), article("unknown3", None)],
        [article("valid", "2020-02-01T23:59:59Z")], [], [],
    ])
    monkeypatch.setattr(news.yf, "Search", lambda **_: SimpleNamespace(news=next(batches)))
    assert [item.title for item in news.fetch_macro_news_yfinance("2020-02-01", limit=1)] == ["valid"]


def fact(value, end="2019-12-31", filed="2020-02-01", start=None, form="10-K"):
    row = {"val": value, "end": end, "filed": filed, "form": form}
    if start:
        row["start"] = start
    return row


def fixture_facts(monkeypatch, facts):
    monkeypatch.setattr(sec, "_ticker_map", lambda _: {"AAPL": "0000320193", "BRK-B": "0001067983"})
    monkeypatch.setattr(sec, "_company_facts", lambda *_: facts)


def test_sec_uses_latest_revision_known_by_analysis_date(monkeypatch):
    fixture_facts(monkeypatch, {"Assets": {"units": {"USD": [
        fact(1_000_000), fact(2_000_000, filed="2020-04-01"),
        fact(9_000_000, end="2020-03-31", filed="2020-05-01", form="10-Q"),
    ]}}})
    before = sec.get_balance_sheet("AAPL", "annual", "2020-03-01")
    after = sec.get_balance_sheet("AAPL", "annual", "2020-05-01")
    assert "Total Assets (USD millions),1.000" in before
    assert "2020-04-01" not in before
    assert "Total Assets (USD millions),2.000" in after
    assert "2020-03-31" not in after  # a 10-Q is not a fiscal year


def test_sec_ytd_cashflow_and_productive_asset_capex_are_labeled(monkeypatch):
    fixture_facts(monkeypatch, {
        "NetCashProvidedByUsedInOperatingActivities": {"units": {"USD": [fact(6_000_000, "2020-06-30", "2020-08-01", "2020-01-01", "10-Q")]}},
        "PaymentsToAcquireProductiveAssets": {"units": {"USD": [fact(2_000_000, "2020-06-30", "2020-08-01", "2020-04-01", "10-Q")]}},
    })
    result = sec.get_cashflow("AAPL", curr_date="2020-09-01")
    assert "2020-06-30 (6 months YTD)" in result
    assert "Operating Cash Flow (USD millions),,6.000" in result
    assert "Capital Expenditure (USD millions),2.000," in result


def test_sec_does_not_sum_tags_or_scale_eps_as_millions(monkeypatch):
    quarterly = fact(3_000_000, "2020-03-31", "2020-05-01", "2020-01-01", "10-Q")
    fixture_facts(monkeypatch, {
        "Revenues": {"units": {"USD": [quarterly]}},
        "SalesRevenueNet": {"units": {"USD": [{**quarterly, "val": 4_000_000}]}},
        "EarningsPerShareDiluted": {"units": {"USD/shares": [{**quarterly, "val": 1.25}]}},
    })
    report = sec.get_income_statement("AAPL", curr_date="2020-06-01")
    assert "Revenue (USD millions),3.000" in report
    assert "Diluted EPS (USD/shares),1.2500" in report


def test_sec_rejects_unknown_future_and_malformed_filing_dates(monkeypatch):
    fixture_facts(monkeypatch, {"Assets": {"units": {"USD": [
        fact(1, filed=""), fact(2, filed=None), fact(3, filed="future"),
        fact(4, filed="2021-01-01"), fact(float("nan")),
    ]}}})
    with pytest.raises(VendorTransientError, match="no annual"):
        sec.get_balance_sheet("AAPL", "annual", "2020-03-01")


def test_sec_limits_periods_and_preserves_foreign_currency(monkeypatch):
    fixture_facts(monkeypatch, {"Assets": {"units": {"EUR": [
        fact(1_000_000, f"{year}-12-31", f"{year + 1}-02-01") for year in range(2000, 2020)
    ]}}})
    report = sec.get_balance_sheet("BRK.B", "annual", "2020-03-01")
    assert "2015-12-31" not in report and "2016-12-31" in report
    assert "Total Assets (EUR millions),1.000,1.000,1.000,1.000" in report


def test_sec_prefers_shortest_reported_span_for_each_period(monkeypatch):
    fixture_facts(monkeypatch, {"Revenues": {"units": {"USD": [
        fact(3_000_000, "2020-06-30", "2020-08-01", "2020-04-01", "10-Q"),
        fact(6_000_000, "2020-06-30", "2020-08-01", "2020-01-01", "10-Q"),
    ]}}})
    report = sec.get_income_statement("AAPL", curr_date="2020-09-01")
    assert "Revenue (USD millions),3.000" in report
    assert "6 months" not in report


def test_historical_vendor_selection_and_korean_exclusion(monkeypatch):
    chain = ["yfinance", "alpha_vantage", "sec_edgar"]
    assert interface._prioritize_market_specific_vendors("get_balance_sheet", chain, ("AAPL", "annual", "2020-03-01"), {})[0] == "sec_edgar"
    assert "sec_edgar" not in interface._prioritize_market_specific_vendors("get_balance_sheet", chain, ("005930.KS", "annual", "2020-03-01"), {})


def test_historical_statements_are_safe_without_strict_flag(monkeypatch):
    monkeypatch.setattr(av, "get_config", lambda: {"point_in_time_strict": False})
    payload = {"annualReports": [
        {"fiscalDateEnding": "2019-12-31"},
        {"fiscalDateEnding": "2019-12-31", "reportedDate": "2020-02-01"},
        {"fiscalDateEnding": "2019-12-31", "reportedDate": "malformed"},
    ]}
    assert len(av._filter_reports_by_date(payload, "2020-03-01")["annualReports"]) == 1
    frame = pd.DataFrame({pd.Timestamp("2019-12-31"): [100]})
    assert filter_financials_by_date(frame, "2020-03-01").empty
    for function in (y_finance.get_balance_sheet, y_finance.get_cashflow, y_finance.get_income_statement):
        assert "unavailable" in function("AAPL", curr_date="2020-03-01")


def test_no_eligible_alpha_reports_trigger_fallback(monkeypatch):
    monkeypatch.setattr(av, "_make_api_request", lambda *_: json.dumps({"annualReports": [{"fiscalDateEnding": "2019-12-31"}]}))
    result = av.get_balance_sheet("AAPL", curr_date="2020-03-01")
    assert interface.should_fallback(result)


def test_run_date_is_inherited_by_omitted_statement_date(monkeypatch):
    monkeypatch.setattr(interface, "get_config", lambda: {"analysis_as_of": "2020-03-01", "point_in_time_strict": False})
    monkeypatch.setattr(interface, "get_vendor", lambda *_: "sec_edgar")
    vendor = Mock(return_value="statement")
    monkeypatch.setitem(interface.VENDOR_METHODS, "get_balance_sheet", {"sec_edgar": vendor})
    assert interface.route_to_vendor("get_balance_sheet", "AAPL") == "statement"
    vendor.assert_called_once_with("AAPL", curr_date="2020-03-01")


def test_historical_insider_sample_is_withheld_without_strict_flag(monkeypatch):
    monkeypatch.setattr(interface, "get_config", lambda: {"analysis_as_of": "2020-03-01", "point_in_time_strict": False})
    assert "publication timestamps are not verified" in interface.route_to_vendor("get_insider_transactions", "AAPL")


def test_flat_search_articles_are_dated_in_utc(monkeypatch):
    monkeypatch.setattr(news.yf, "Ticker", lambda _: SimpleNamespace(get_news=lambda **_: []))
    monkeypatch.setattr(news.yf, "Search", lambda *_, **__: SimpleNamespace(news=[
        {"title": "Flat article", "relatedTickers": ["AAPL"], "providerPublishTime": 1580558399},
    ]))
    assert "Flat article" in news.get_company_news_yfinance("AAPL", "2020-02-01", "2020-02-01")


def test_past_overviews_are_withheld_without_vendor_requests(monkeypatch):
    yahoo = Mock(side_effect=AssertionError("live snapshot must not be read"))
    alpha = Mock(side_effect=AssertionError("live snapshot must not be read"))
    monkeypatch.setattr(y_finance, "_resolve_info_with_symbol_fallback", yahoo)
    monkeypatch.setattr(av, "_make_api_request", alpha)
    assert "current snapshot" in y_finance.get_fundamentals("AAPL", "2020-03-01")
    assert "current snapshot" in av.get_fundamentals("AAPL", "2020-03-01")
    yahoo.assert_not_called()
    alpha.assert_not_called()


def test_run_cutoff_rejects_future_statement_dates_without_strict_flag(monkeypatch):
    monkeypatch.setattr(interface, "get_config", lambda: {"analysis_as_of": "2020-03-01", "point_in_time_strict": False})
    with pytest.raises(VendorInputError, match="as-of"):
        interface.route_to_vendor("get_balance_sheet", "AAPL", "annual", "2020-03-02")
    with pytest.raises(VendorInputError, match="YYYY-MM-DD"):
        interface.route_to_vendor("get_balance_sheet", "AAPL", "annual", "invalid")
