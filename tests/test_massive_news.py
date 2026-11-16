from datetime import datetime, timezone
import json
from unittest.mock import Mock

import pytest

from tradingagents.dataflows import massive_news as news
from tradingagents.dataflows.config import run_config
from tradingagents.dataflows.vendor_exceptions import VendorUnavailableError, VendorMalformedResponseError


class Clock(datetime):
    @classmethod
    def now(cls, tz=None):
        return datetime(2026, 4, 14, 14, tzinfo=timezone.utc)


@pytest.fixture
def article(monkeypatch):
    row = {"published_utc": "2026-04-14T12:00:00Z", "tickers": ["BRK.B"],
           "title": "Company event", "article_url": "https://example.com/news",
           "publisher": {"name": "Publisher"}, "description": "Summary"}
    monkeypatch.setattr(news, "datetime", Clock)
    monkeypatch.setattr(news, "get_api_key", lambda name: "fixture-secret")
    monkeypatch.setattr(news.requests, "get", Mock(return_value=Mock(status_code=200, json=lambda: {"results": [row]})))
    return row


def fetch():
    with run_config({"analysis_as_of": "2026-04-14"}):
        return json.loads(news.get_company_news_massive("BRK-B", "2026-04-07", "2026-04-14"))


def test_class_share_mapping_and_current_version_provenance(article):
    result = fetch()
    assert result["ticker"] == "BRK-B" and result["articles"][0]["symbols"] == ["BRK.B"]
    assert result["article_version"] == "current_snapshot_only"
    assert result["retrieved_at"] == "2026-04-14T14:00:00+00:00"
    assert news.requests.get.call_args.kwargs["params"]["ticker"] == "BRK.B"
    assert news.requests.get.call_args.kwargs["allow_redirects"] is False


@pytest.mark.parametrize("field,value", [
    ("published_utc", None), ("published_utc", "bad"), ("published_utc", "2026-04-14"),
    ("published_utc", "2026-04-14T15:00:00Z"), ("published_utc", "2026-04-06T12:00:00Z"),
    ("tickers", ["BRK.A"]), ("tickers", "BRK.B"), ("publisher", None), ("title", ""),
])
def test_rejects_unverifiable_future_or_other_share_class(article, field, value):
    article[field] = value
    with pytest.raises(VendorUnavailableError):
        fetch()


@pytest.mark.parametrize("context,end", [("2026-04-13", "2026-04-14"), ("2026-04-14", "2026-04-13"),
                                         ("2026-04-14T13:59:59Z", "2026-04-14")])
def test_cannot_backdate_current_article_revision(article, context, end):
    with run_config({"analysis_as_of": context}):
        with pytest.raises(VendorUnavailableError):
            news.get_company_news_massive("BRK-B", "2026-04-07", end)
    news.requests.get.assert_not_called()


@pytest.mark.parametrize("payload", [{"results": []}, {}, [], {"results": None}])
def test_empty_malformed_response_never_certifies_news_free_window(article, payload):
    news.requests.get.return_value.json = lambda: payload
    with pytest.raises((VendorUnavailableError, VendorMalformedResponseError)):
        fetch()


@pytest.mark.parametrize("status", [401, 429, 500])
def test_http_failures_do_not_leak_credentials(article, status):
    news.requests.get.return_value.status_code = status
    with pytest.raises(VendorUnavailableError, match=f"HTTP {status}") as caught:
        fetch()
    assert "fixture-secret" not in str(caught.value)


def test_untrusted_pagination_url_never_receives_credentials(article):
    news.requests.get.return_value.json = lambda: {"results": [article], "next_url": "https://attacker.invalid/"}
    assert fetch()["truncated"] is True
    news.requests.get.assert_called_once()


def test_news_routing_recovers_class_shares(article, monkeypatch):
    from tradingagents.dataflows import interface
    interface.reset_tool_telemetry()
    monkeypatch.setitem(interface.VENDOR_METHODS["get_company_news"], "alpaca",
                        Mock(side_effect=VendorUnavailableError("empty")))
    with run_config({"analysis_as_of": "2026-04-14"}):
        result = interface.route_to_vendor("get_company_news", "BRK-B", "2026-04-07", "2026-04-14")
    assert json.loads(result)["provider"] == "massive"
    assert interface.snapshot_tool_requests()[-1]["status"] == "available"
    assert interface.snapshot_tool_telemetry()[-1]["vendor"] == "massive"
