import json
import traceback
from unittest.mock import Mock, patch

import pytest
import requests

from tradingagents.dataflows.alpha_vantage_common import (
    AlphaVantageRateLimitError,
    _filter_csv_by_date_range,
    _make_api_request,
)
from tradingagents.dataflows.vendor_exceptions import (
    VendorConfigurationError,
    VendorMalformedResponseError,
    VendorTransientError,
)


@pytest.mark.parametrize("payload, exception", [
    ({"Information": "API key SECRET: 25 requests per day"}, AlphaVantageRateLimitError),
    ({"Note": "Call frequency exceeded SECRET"}, AlphaVantageRateLimitError),
    ({"Information": "Invalid API key SECRET"}, VendorConfigurationError),
    ({"Information": "Service maintenance SECRET"}, VendorTransientError),
    ({"Error Message": "Invalid request apikey=SECRET"}, VendorTransientError),
    (["SECRET"], VendorMalformedResponseError),
])
def test_rejected_payload_is_not_data_and_does_not_expose_key(payload, exception):
    response = Mock(text=json.dumps(payload))
    with patch("tradingagents.dataflows.alpha_vantage_common.get_api_key", return_value="SECRET"), patch(
        "tradingagents.dataflows.alpha_vantage_common.requests.get", return_value=response
    ), pytest.raises(exception) as caught:
        _make_api_request("NEWS_SENTIMENT", {"symbol": "AAPL"})
    assert "SECRET" not in str(caught.value)


def test_http_error_does_not_expose_key_in_traceback():
    with patch("tradingagents.dataflows.alpha_vantage_common.get_api_key", return_value="SECRET"), patch(
        "tradingagents.dataflows.alpha_vantage_common.requests.get",
        side_effect=requests.HTTPError("403 https://example.test/?apikey=SECRET"),
    ), pytest.raises(VendorTransientError) as caught:
        _make_api_request("OVERVIEW", {"symbol": "AAPL"})
    assert "SECRET" not in "".join(traceback.format_exception(caught.value))


@pytest.mark.parametrize("payload", ['{"Name":"Apple"}', "timestamp,close\n2026-01-01,100\n"])
def test_valid_vendor_payload_is_preserved(payload):
    params = {"symbol": "AAPL"}
    with patch("tradingagents.dataflows.alpha_vantage_common.get_api_key", return_value="SECRET"), patch(
        "tradingagents.dataflows.alpha_vantage_common.requests.get", return_value=Mock(text=payload)
    ):
        assert _make_api_request("OVERVIEW", params) == payload
    assert params == {"symbol": "AAPL"}


def test_bad_price_dates_fail_closed_instead_of_leaking_full_series():
    with pytest.raises(VendorMalformedResponseError):
        _filter_csv_by_date_range("timestamp,close\nbroken,100\n2030-01-01,200\n", "2026-01-01", "2026-01-31")


def test_valid_price_series_excludes_future_rows():
    result = _filter_csv_by_date_range("timestamp,close\n2026-01-01,100\n2030-01-01,200\n", "2026-01-01", "2026-01-31")
    assert "2026-01-01" in result
    assert "2030-01-01" not in result
