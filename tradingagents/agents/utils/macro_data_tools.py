"""Optional macro evidence with the vintage pinned to the analysis date."""

from langchain_core.tools import tool
from tradingagents.dataflows.interface import route_to_vendor
from tradingagents.dataflows.config import get_config


@tool
def get_macro_data(indicator: str, curr_date: str, look_back_days: int = 365) -> str:
    """Read FRED macro observations known at curr_date (e.g. cpi, yield_curve, unemployment)."""
    if not 1 <= look_back_days <= 3650:
        return "No macro data: look_back_days must be between 1 and 3650."
    cutoff = get_config().get("analysis_as_of")
    if cutoff and get_config().get("point_in_time_strict"):
        curr_date = min(curr_date, cutoff)
    try:
        return route_to_vendor("get_macro_indicators", indicator, curr_date, look_back_days)
    except Exception:
        # Provider errors can contain a URL with API credentials; never echo it.
        return "No macro data: FRED unavailable or unconfigured. Do not infer missing observations."
