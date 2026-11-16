import json
from unittest.mock import Mock

import pytest

from tradingagents.dataflows import alpaca_news as news
from tradingagents.dataflows.config import run_config
from tradingagents.dataflows.vendor_exceptions import VendorConfigurationError, VendorMalformedResponseError, VendorUnavailableError


@pytest.fixture
def article():
    return {"created_at": "2026-04-14T12:00:00Z", "updated_at": "2026-04-14T13:00:00Z",
            "symbols": ["AAPL"], "headline": "A dated company event", "url": "https://example.com/news",
            "source": "publisher", "summary": "Event summary"}


@pytest.fixture
def api(monkeypatch, article):
    monkeypatch.setattr(news, "get_api_key", lambda name: "fixture-secret")
    get = Mock(return_value=Mock(status_code=200, json=lambda: {"news": [article]}))
    monkeypatch.setattr(news.requests, "get", get)
    return get


def fetch():
    with run_config({"analysis_as_of": "2026-04-14T14:00:00+00:00"}):
        return json.loads(news.get_company_news_alpaca("AAPL", "2026-04-13", "2026-04-15"))


def test_dated_symbol_tagged_sample(api):
    result = fetch()
    assert result["articles"][0]["published_at"] == "2026-04-14T12:00:00+00:00"
    assert result["articles"][0]["updated_at"] == "2026-04-14T13:00:00+00:00"
    assert result["coverage"] == "bounded_sample"
    assert result["analysis_cutoff"] == "2026-04-14T14:00:00+00:00"
    assert api.call_args.kwargs["allow_redirects"] is False
    assert api.call_args.kwargs["params"]["end"] == result["analysis_cutoff"]
    assert "fixture-secret" not in json.dumps(result)


@pytest.mark.parametrize("field,value", [
    ("created_at", None), ("created_at", "nonsense"), ("created_at", "2026-04-14"),
    ("created_at", "2026-04-15T12:00:00Z"), ("created_at", "2026-04-12T12:00:00Z"),
    ("updated_at", None), ("updated_at", "bad"), ("updated_at", "2026-04-14T15:00:00Z"),
    ("updated_at", "2026-04-14T11:00:00Z"), ("symbols", ["MSFT"]),
    ("symbols", "AAPL"), ("url", ""), ("headline", None),
])
def test_excludes_invalid_future_unrelated_articles(api, article, field, value):
    article[field] = value
    with pytest.raises(VendorUnavailableError, match="no verifiable"):
        fetch()


def test_future_modification_does_not_supply_historical_article(api, article):
    article["updated_at"] = "2026-04-15T00:00:00Z"
    with run_config({"analysis_as_of": "2026-04-14"}):
        with pytest.raises(VendorUnavailableError):
            news.get_company_news_alpaca("AAPL", "2026-04-13", "2026-04-16")


def test_date_context_caps_reported_cutoff_as_well_as_article_filter(api):
    with run_config({"analysis_as_of": "2026-04-14"}):
        result = json.loads(news.get_company_news_alpaca("AAPL", "2026-04-13", "2026-04-16"))
    assert result["analysis_cutoff"] == result["end_exclusive"] == "2026-04-15T00:00:00+00:00"


def test_future_publication_is_rejected_even_with_future_request(api, article):
    article.update(created_at="2099-04-14T12:00:00Z", updated_at="2099-04-14T13:00:00Z")
    with run_config({}):
        with pytest.raises(VendorUnavailableError):
            news.get_company_news_alpaca("AAPL", "2026-04-13", "2099-04-16")


@pytest.mark.parametrize("payload", [{"news": []}, {"news": None}, {}, []])
def test_empty_or_malformed_does_not_certify_zero_news(api, payload):
    api.return_value.json = lambda: payload
    with pytest.raises((VendorUnavailableError, VendorMalformedResponseError)):
        fetch()


@pytest.mark.parametrize("status", [401, 429, 500])
def test_http_failures_do_not_leak_credentials(api, status):
    api.return_value.status_code = status
    with pytest.raises(VendorUnavailableError, match=f"HTTP {status}") as caught:
        fetch()
    assert "fixture-secret" not in str(caught.value)


def test_pagination_recovers_valid_article_after_invalid_page(api, article):
    invalid = dict(article, updated_at="2026-04-15T00:00:00Z")
    api.side_effect = [Mock(status_code=200, json=lambda: {"news": [invalid], "next_page_token": "next"}),
                       Mock(status_code=200, json=lambda: {"news": [article, article]})]
    assert len(fetch()["articles"]) == 1
    assert api.call_count == 2


def test_repeated_pagination_token_fails_closed(api, article):
    api.return_value.json = lambda: {"news": [article], "next_page_token": "same-token"}
    with pytest.raises(VendorMalformedResponseError, match="pagination"):
        fetch()
    assert api.call_count == 2


def test_bounded_sample_and_missing_credentials(api, article, monkeypatch):
    api.return_value.json = lambda: {"news": [dict(article, url=f"https://example.com/{i}") for i in range(50)],
                                   "next_page_token": "next"}
    result = fetch()
    assert len(result["articles"]) == 25 and result["truncated"] is True
    monkeypatch.setattr(news, "get_api_key", lambda name: None)
    with pytest.raises(VendorConfigurationError):
        fetch()


def test_failed_provider_can_recover_with_correlated_news_receipt(monkeypatch, api):
    from tradingagents.dataflows import interface
    interface.reset_tool_telemetry()
    monkeypatch.setitem(interface.VENDOR_METHODS["get_company_news"], "alpha_vantage",
                        Mock(side_effect=VendorUnavailableError("unavailable")))
    with run_config({"analysis_as_of": "2026-04-14", "tool_vendors": {"get_company_news": "alpha_vantage,alpaca"}}):
        result = interface.route_to_vendor("get_company_news", "AAPL", "2026-04-13", "2026-04-14")
    assert json.loads(result)["provider"] == "alpaca"
    receipt = interface.snapshot_tool_requests()[-1]
    events = interface.snapshot_tool_telemetry()
    assert receipt["status"] == "available" and len(receipt["result_sha256"]) == 64
    assert all(event["request_id"] == receipt["request_id"] for event in events)
    assert events[-1]["vendor"] == "alpaca" and events[-1]["fallback"] is False


def test_kr_does_not_use_us_news_provider():
    from tradingagents.dataflows.interface import _prioritize_market_specific_vendors
    assert "alpaca" not in _prioritize_market_specific_vendors("get_company_news", ["alpaca", "naver"], ("005930.KS",), {})
