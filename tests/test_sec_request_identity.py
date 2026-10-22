"""SEC identity must reach scheduled requests without exposing local settings."""
import json
from unittest.mock import Mock

import pytest
import requests

from tradingagents.dataflows import api_keys, sec_edgar
from tradingagents.dataflows.vendor_exceptions import VendorTransientError


@pytest.fixture
def local_settings(tmp_path, monkeypatch):
    path = tmp_path / "api_keys.json"
    for name in ("SEC_EDGAR_USER_AGENT", "SEC_USER_AGENT"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("TRADINGAGENTS_API_KEYS_PATH", str(path))
    monkeypatch.setattr(sec_edgar, "_LAST_REQUEST", 0.0)
    monkeypatch.setattr(sec_edgar, "_UNAVAILABLE_UNTIL", 0.0)
    monkeypatch.setattr(sec_edgar, "_UNAVAILABLE_STATUS", None)
    api_keys._load_documented_keys.cache_clear()
    yield path
    api_keys._load_documented_keys.cache_clear()


@pytest.mark.parametrize("setting", ["SEC_EDGAR_USER_AGENT", "SEC_USER_AGENT"])
@pytest.mark.parametrize("environment", [None, "SEC_EDGAR_USER_AGENT", "SEC_USER_AGENT"])
def test_request_uses_local_identity_with_environment_precedence(
    local_settings, monkeypatch, setting, environment,
):
    local_settings.write_text(json.dumps({setting: "Research local@example.com"}), encoding="utf-8")
    if environment:
        monkeypatch.setenv(environment, "Research env@example.com")
    response = Mock()
    response.json.return_value = {"filings": {}}
    request = Mock(return_value=response)
    monkeypatch.setattr(sec_edgar.requests, "get", request)

    assert sec_edgar._get_json("https://data.sec.gov/submissions/CIK0000320193.json") == {"filings": {}}
    assert request.call_args.kwargs["headers"]["User-Agent"] == (
        "Research env@example.com" if environment else "Research local@example.com"
    )
    assert request.call_args.kwargs["timeout"] == 25


@pytest.mark.parametrize("status", [403, 429])
def test_denial_keeps_cooldown_and_redacts_contact(local_settings, monkeypatch, status):
    identity = "Research private@example.com"
    local_settings.write_text(json.dumps({"SEC_EDGAR_USER_AGENT": identity}), encoding="utf-8")
    response = Mock(status_code=status)
    response.raise_for_status.side_effect = requests.HTTPError(identity, response=response)
    request = Mock(return_value=response)
    monkeypatch.setattr(sec_edgar.requests, "get", request)
    with pytest.raises(VendorTransientError) as first:
        sec_edgar._get_json("https://www.sec.gov/files/company_tickers.json")
    with pytest.raises(VendorTransientError) as second:
        sec_edgar._get_json("https://www.sec.gov/files/company_tickers.json")
    assert identity not in str(first.value)
    assert identity not in str(second.value)
    assert f"HTTP {status}" in str(first.value)
    assert "cooldown" in str(second.value)
    assert request.call_count == 1


def test_no_identity_preserves_existing_fallback(local_settings, monkeypatch):
    local_settings.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(api_keys, "_load_legacy_markdown_keys", lambda path: {})
    response = Mock()
    response.json.return_value = {}
    request = Mock(return_value=response)
    monkeypatch.setattr(sec_edgar.requests, "get", request)
    assert sec_edgar._get_json("https://www.sec.gov/files/company_tickers.json") == {}
    assert request.call_args.kwargs["headers"]["User-Agent"].startswith("TradingAgents research contact ")
