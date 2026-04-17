import json
from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor
from tradingagents.dataflows.intraday_market import fetch_intraday_market_snapshot


@tool
def get_stock_data(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve stock price data (OHLCV) for a given ticker symbol.
    Uses the configured core_stock_apis vendor.
    Args:
        symbol (str): Ticker symbol of the company, e.g. AAPL, TSM
        start_date (str): Start date in yyyy-mm-dd format
        end_date (str): End date in yyyy-mm-dd format
    Returns:
        str: A formatted dataframe containing the stock price data for the specified ticker symbol in the specified date range.
    """
    return route_to_vendor("get_stock_data", symbol, start_date, end_date)


@tool
def get_intraday_snapshot(
    symbol: Annotated[str, "ticker symbol of the company"],
    interval: Annotated[str, "Intraday interval such as 1m, 2m, 5m, 15m, 30m, 60m"] = "5m",
) -> str:
    """
    Retrieve intraday snapshot (last price, day range, intraday volume, relative volume) for execution-aware timing checks.
    Returns JSON text for easier downstream parsing by LLM agents.
    """
    try:
        snapshot = fetch_intraday_market_snapshot(symbol, interval=interval)
    except Exception as exc:
        return json.dumps(
            {
                "ok": False,
                "symbol": symbol,
                "interval": interval,
                "tool": "get_intraday_snapshot",
                "error_type": exc.__class__.__name__,
                "error": str(exc),
            },
            ensure_ascii=False,
        )
    return json.dumps(
        {
            "ok": True,
            "symbol": symbol,
            "interval": interval,
            "snapshot": snapshot.to_dict(),
        },
        ensure_ascii=False,
    )
