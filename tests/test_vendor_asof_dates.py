from unittest.mock import Mock, patch

import pytest

from tradingagents.dataflows.config import run_config
from tradingagents.dataflows.interface import route_to_vendor
from tradingagents.dataflows.vendor_exceptions import VendorInputError


@pytest.mark.parametrize("method,args", [
    ("get_stock_data", ("AAPL", "2026-4-1", "2026-4-5")),
    ("get_company_news", ("AAPL", "2026-04-01", "2026-4-5")),
    ("get_indicators", ("AAPL", "rsi", "2026-4-5", 10)),
    ("get_indicators", ("AAPL", "rsi", "2026-04-05T12:00:00", 10)),
    ("get_indicators", ("AAPL", "rsi", "2026-04-05", 10)),
])
def test_noncanonical_or_future_date_never_reaches_vendor(method, args):
    vendor = Mock(return_value="FUTURE DATA")
    with (
        run_config({"analysis_as_of": "2026-04-01", "point_in_time_strict": False}),
        patch.dict("tradingagents.dataflows.interface.VENDOR_METHODS", {method: {"yfinance": vendor}}),
    ):
        with pytest.raises(VendorInputError):
            route_to_vendor(method, *args)
    vendor.assert_not_called()


def test_indicator_keyword_date_has_the_same_guard():
    with run_config({"analysis_as_of": "2026-04-01"}):
        with pytest.raises(VendorInputError):
            route_to_vendor("get_indicators", symbol="AAPL", indicator="rsi", curr_date="2026-4-5", look_back_days=10)
