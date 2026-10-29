from langchain_core.tools import tool
from typing import Annotated
import json
from tradingagents.dataflows.interface import route_to_vendor
from tradingagents.dataflows.vendor_exceptions import InsufficientIndicatorHistoryError

@tool
def get_indicators(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[str, "The current trading date you are trading on, YYYY-mm-dd"],
    look_back_days: Annotated[int, "how many days to look back"] = 30,
) -> str:
    """
    Retrieve a single technical indicator for a given ticker symbol.
    Uses the configured technical_indicators vendor.
    Args:
        symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
        indicator (str): A single technical indicator name, e.g. 'rsi', 'macd'. Call this tool once per indicator.
        curr_date (str): The current trading date you are trading on, YYYY-mm-dd
        look_back_days (int): How many days to look back, default is 30
    Returns:
        str: A formatted dataframe containing the technical indicators for the specified ticker symbol and indicator.
    """
    # LLMs sometimes pass multiple indicators as a comma-separated string;
    # split and process each individually.
    indicators = [i.strip().lower() for i in indicator.split(",") if i.strip()]
    results = []
    for ind in indicators:
        try:
            results.append(route_to_vendor("get_indicators", symbol, ind, curr_date, look_back_days))
        except InsufficientIndicatorHistoryError:
            # The vendor request retains its error evidence and execution gate.
            # Let the analyst explain an unavailable indicator, without making
            # up warm-up bars or discarding the rest of the company's research.
            results.append(json.dumps({
                "status": "UNAVAILABLE", "reason": "INSUFFICIENT_OR_UNVERIFIED_INDICATOR_HISTORY",
                "symbol": symbol, "indicator": ind, "as_of": curr_date,
                "look_back_days": look_back_days, "value": None, "execution_authorized": False,
                "instruction": "State this limitation. Do not infer, fill, or substitute an indicator value.",
            }, ensure_ascii=True))
        except ValueError as e:
            results.append(str(e))
    return "\n\n".join(results)
