import os
import requests
import pandas as pd
import json
from datetime import datetime
from io import StringIO

from .api_keys import get_api_key as get_documented_api_key
from .config import get_config
from .vendor_exceptions import VendorConfigurationError, VendorTransientError, VendorMalformedResponseError

API_BASE_URL = "https://www.alphavantage.co/query"

def get_api_key() -> str:
    """Retrieve the API key for Alpha Vantage from environment variables."""
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY") or get_documented_api_key("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise VendorConfigurationError("ALPHA_VANTAGE_API_KEY is not configured.")
    return api_key

def format_datetime_for_api(date_input) -> str:
    """Convert various date formats to YYYYMMDDTHHMM format required by Alpha Vantage API."""
    if isinstance(date_input, str):
        # If already in correct format, return as-is
        if len(date_input) == 13 and 'T' in date_input:
            return date_input
        # Try to parse common date formats
        try:
            dt = datetime.strptime(date_input, "%Y-%m-%d")
            return dt.strftime("%Y%m%dT0000")
        except ValueError:
            try:
                dt = datetime.strptime(date_input, "%Y-%m-%d %H:%M")
                return dt.strftime("%Y%m%dT%H%M")
            except ValueError:
                raise ValueError(f"Unsupported date format: {date_input}")
    elif isinstance(date_input, datetime):
        return date_input.strftime("%Y%m%dT%H%M")
    else:
        raise ValueError(f"Date must be string or datetime object, got {type(date_input)}")

class AlphaVantageRateLimitError(VendorTransientError):
    """Exception raised when Alpha Vantage API rate limit is exceeded."""
    pass

def _make_api_request(function_name: str, params: dict) -> dict | str:
    """Helper function to make API requests and handle responses.
    
    Raises:
        AlphaVantageRateLimitError: When API rate limit is exceeded
    """
    # Create a copy of params to avoid modifying the original
    api_params = params.copy()
    api_params.update({
        "function": function_name,
        "apikey": get_api_key(),
        "source": "trading_agents",
    })
    
    # Handle entitlement parameter if present in params or global variable
    current_entitlement = globals().get('_current_entitlement')
    entitlement = api_params.get("entitlement") or current_entitlement
    
    if entitlement:
        api_params["entitlement"] = entitlement
    elif "entitlement" in api_params:
        # Remove entitlement if it's None or empty
        api_params.pop("entitlement", None)
    
    try:
        response = requests.get(
            API_BASE_URL,
            params=api_params,
            timeout=float(get_config().get("vendor_timeout", 15)),
        )
        response.raise_for_status()
    except requests.RequestException:
        # Request exceptions can contain the full URL, including the API key.
        raise VendorTransientError("Alpha Vantage request failed (network or HTTP error).") from None

    response_text = response.text
    
    # Error responses are JSON even when CSV data was requested. Never pass an
    # API rejection to an analyst as if it were financial evidence.
    try:
        response_json = json.loads(response_text)
    except json.JSONDecodeError:
        return response_text

    if not isinstance(response_json, dict):
        raise VendorMalformedResponseError("Alpha Vantage returned an unexpected JSON payload.")
    notice = response_json.get("Information") or response_json.get("Note")
    if notice:
        low = str(notice).lower()
        if any(marker in low for marker in ("rate limit", "requests per day", "call frequency", "premium")):
            raise AlphaVantageRateLimitError("Alpha Vantage rate limit or subscription limit exceeded.")
        if "api key" in low or "apikey" in low:
            raise VendorConfigurationError("Alpha Vantage API key is invalid or missing.")
        raise VendorTransientError("Alpha Vantage returned a service notice instead of data.")
    if "Error Message" in response_json:
        raise VendorTransientError("Alpha Vantage rejected the request.")

    return response_text



def _filter_csv_by_date_range(csv_data: str, start_date: str, end_date: str) -> str:
    """
    Filter CSV data to include only rows within the specified date range.

    Args:
        csv_data: CSV string from Alpha Vantage API
        start_date: Start date in yyyy-mm-dd format
        end_date: End date in yyyy-mm-dd format

    Returns:
        Filtered CSV string
    """
    if not csv_data or csv_data.strip() == "":
        return csv_data

    try:
        # Parse CSV data
        df = pd.read_csv(StringIO(csv_data))

        # Assume the first column is the date column (timestamp)
        date_col = df.columns[0]
        df[date_col] = pd.to_datetime(df[date_col])

        # Filter by date range
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)

        filtered_df = df[(df[date_col] >= start_dt) & (df[date_col] <= end_dt)]

        # Convert back to CSV string
        return filtered_df.to_csv(index=False)

    except Exception:
        # Returning the original full series here would leak future prices.
        raise VendorMalformedResponseError("Alpha Vantage price dates could not be filtered safely.") from None
