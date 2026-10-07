import json
from copy import deepcopy
from datetime import date

from .alpha_vantage_common import _make_api_request
from .config import get_config
from .integrity import is_historical
from .vendor_exceptions import VendorMalformedResponseError


def _filter_reports_by_date(result, curr_date: str):
    """Bound fiscal periods and require verified publication dates for past runs."""
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
    strict = get_config().get("point_in_time_strict", False) or is_historical(curr_date)

    def available(report):
        if not isinstance(report, dict):
            return False
        try:
            fiscal = date.fromisoformat(report["fiscalDateEnding"])
            publication = report.get("reportedDate") or report.get("filingDate")
            if strict and not publication:
                return False
            filed = date.fromisoformat(publication) if publication else fiscal
            return fiscal.isoformat() <= curr_date and filed.isoformat() <= curr_date
        except (KeyError, TypeError, ValueError):
            return False

    for key in ("annualReports", "quarterlyReports"):
        if key in result:
            if not isinstance(result[key], list):
                raise VendorMalformedResponseError(f"Financial statement {key} must be a list")
            result[key] = [
                r for r in result[key]
                if available(r)
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
        curr_date (str): Analysis date, yyyy-mm-dd; historical overviews are withheld.

    Returns:
        str: Company overview data including financial ratios and key metrics
    """
    params = {
        "symbol": ticker,
    }

    if is_historical(curr_date):
        return "No fundamentals data: Alpha Vantage OVERVIEW is a current snapshot, not a historical vintage."
    return _make_api_request("OVERVIEW", params)


def _get_statement(function: str, ticker: str, curr_date: str | None):
    result = _filter_reports_by_date(_make_api_request(function, {"symbol": ticker}), curr_date)
    payload = json.loads(result) if isinstance(result, str) else result
    if isinstance(payload, dict) and not any(payload.get(key) for key in ("annualReports", "quarterlyReports")):
        return "No fundamentals data found: Alpha Vantage has no financial reports eligible for the requested publication date."
    return result


def get_balance_sheet(ticker: str, freq: str = "quarterly", curr_date: str = None):
    """Retrieve balance sheet data for a given ticker symbol using Alpha Vantage."""
    return _get_statement("BALANCE_SHEET", ticker, curr_date)


def get_cashflow(ticker: str, freq: str = "quarterly", curr_date: str = None):
    """Retrieve cash flow statement data for a given ticker symbol using Alpha Vantage."""
    return _get_statement("CASH_FLOW", ticker, curr_date)


def get_income_statement(ticker: str, freq: str = "quarterly", curr_date: str = None):
    """Retrieve income statement data for a given ticker symbol using Alpha Vantage."""
    return _get_statement("INCOME_STATEMENT", ticker, curr_date)

