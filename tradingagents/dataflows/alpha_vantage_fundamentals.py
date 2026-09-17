from .alpha_vantage_common import _make_api_request
import json
from copy import deepcopy
from .config import get_config
from .integrity import is_historical
from .vendor_exceptions import VendorMalformedResponseError


def _filter_reports_by_date(result, curr_date: str):
    """Filter annualReports/quarterlyReports to exclude entries after curr_date.

    Prevents look-ahead bias by removing fiscal periods that end after
    the simulation's current date.
    """
    if not curr_date:
        return result
    was_text = isinstance(result, str)
    if was_text:
        try:
            result = json.loads(result)
        except (ValueError, TypeError) as exc:
            raise VendorMalformedResponseError("Invalid financial statement JSON") from exc
    if not isinstance(result, dict):
        raise VendorMalformedResponseError("Financial statement must be an object")
    result = deepcopy(result)
    strict = get_config().get("point_in_time_strict", False)
    for key in ("annualReports", "quarterlyReports"):
        if key in result:
            result[key] = [
                r for r in result[key]
                if isinstance(r, dict)
                and r.get("fiscalDateEnding")
                and r["fiscalDateEnding"] <= curr_date
                and (r.get("reportedDate") or r.get("filingDate") or ("9999-12-31" if strict else r["fiscalDateEnding"])) <= curr_date
            ]
    result["_data_quality"] = (
        "Publication-date filtered. Historical revisions are not guaranteed point-in-time."
        if strict else "Fiscal-period filtered; publication dates/revisions may be unavailable. Not verified point-in-time."
    )
    return json.dumps(result, ensure_ascii=False) if was_text else result


def get_fundamentals(ticker: str, curr_date: str = None) -> str:
    """
    Retrieve comprehensive fundamental data for a given ticker symbol using Alpha Vantage.

    Args:
        ticker (str): Ticker symbol of the company
        curr_date (str): Current date you are trading at, yyyy-mm-dd (not used for Alpha Vantage)

    Returns:
        str: Company overview data including financial ratios and key metrics
    """
    params = {
        "symbol": ticker,
    }

    if get_config().get("point_in_time_strict", False) and is_historical(curr_date):
        return "No fundamentals data: Alpha Vantage OVERVIEW is a current snapshot, not a historical vintage."
    return _make_api_request("OVERVIEW", params)


def get_balance_sheet(ticker: str, freq: str = "quarterly", curr_date: str = None):
    """Retrieve balance sheet data for a given ticker symbol using Alpha Vantage."""
    result = _make_api_request("BALANCE_SHEET", {"symbol": ticker})
    return _filter_reports_by_date(result, curr_date)


def get_cashflow(ticker: str, freq: str = "quarterly", curr_date: str = None):
    """Retrieve cash flow statement data for a given ticker symbol using Alpha Vantage."""
    result = _make_api_request("CASH_FLOW", {"symbol": ticker})
    return _filter_reports_by_date(result, curr_date)


def get_income_statement(ticker: str, freq: str = "quarterly", curr_date: str = None):
    """Retrieve income statement data for a given ticker symbol using Alpha Vantage."""
    result = _make_api_request("INCOME_STATEMENT", {"symbol": ticker})
    return _filter_reports_by_date(result, curr_date)

