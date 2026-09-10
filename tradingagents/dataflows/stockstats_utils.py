import time
import logging

import pandas as pd
import yfinance as yf
from yfinance.exceptions import YFRateLimitError
from stockstats import wrap
from typing import Annotated
import os
from .config import get_config
from .integrity import safe_symbol, session_date, validate_daily_bars, is_historical

logger = logging.getLogger(__name__)


def yf_retry(func, max_retries=3, base_delay=2.0):
    """Execute a yfinance call with exponential backoff on transient vendor errors."""
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as exc:
            if not is_retryable_yfinance_error(exc) or attempt >= max_retries:
                raise
            delay = base_delay * (2 ** attempt)
            logger.warning(
                "Yahoo Finance transient error, retrying in %.0fs (attempt %s/%s): %s",
                delay,
                attempt + 1,
                max_retries,
                _summarize_yfinance_error(exc),
            )
            time.sleep(delay)


def is_retryable_yfinance_error(exc: Exception) -> bool:
    if isinstance(exc, YFRateLimitError):
        return True
    text = f"{exc.__class__.__module__}.{exc.__class__.__name__}: {exc}".lower()
    retry_markers = (
        "timeout",
        "timed out",
        "operation timed out",
        "curl: (28)",
        "failed to perform",
        "rate limit",
        "too many requests",
        "invalid crumb",
        "unauthorized",
        "temporarily unavailable",
        "connection aborted",
        "connection reset",
        "remote end closed connection",
        "'nonetype' object is not subscriptable",
    )
    return any(marker in text for marker in retry_markers)


def _summarize_yfinance_error(exc: Exception) -> str:
    text = str(exc).strip() or exc.__class__.__name__
    return text[:240]


def _clean_dataframe(data: pd.DataFrame) -> pd.DataFrame:
    """Normalize dates and numeric columns without manufacturing missing prices."""
    data = data.copy()
    data["Date"] = pd.to_datetime(data["Date"].map(session_date))
    data = data.dropna(subset=["Date"])

    price_cols = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in data.columns]
    data[price_cols] = data[price_cols].apply(pd.to_numeric, errors="coerce")
    # Do not backfill from future prices, fabricate volume, or hide a bad latest bar.

    return data


def load_ohlcv(symbol: str, curr_date: str) -> pd.DataFrame:
    """Fetch OHLCV data with caching, filtered to prevent look-ahead bias.

    Downloads at least five years before the requested date and caches per
    symbol. Active-date caches expire after five minutes; historical rows
    are cut off before validation and indicator calculation.
    """
    config = get_config()
    symbol = safe_symbol(symbol)
    curr_date_dt = pd.to_datetime(curr_date)

    # Include enough warm-up history even for an older evaluation date.
    today_date = pd.Timestamp.today()
    start_date = min(today_date, curr_date_dt) - pd.DateOffset(years=5)
    start_str = start_date.strftime("%Y-%m-%d")
    # yfinance's ``end`` is exclusive. Use tomorrow as the download boundary so
    # a completed same-day bar is not silently omitted after the market close.
    end_str = (today_date + pd.DateOffset(days=1)).strftime("%Y-%m-%d")

    os.makedirs(config["data_cache_dir"], exist_ok=True)
    data_file = os.path.join(
        config["data_cache_dir"],
        f"{symbol}-YFin-data-{start_str}-{end_str}.csv",
    )

    # Refresh a morning snapshot after the close, but share recent downloads
    # between indicators to avoid repeated network calls for the same analysis.
    use_cache = os.path.exists(data_file) and (
        curr_date_dt < today_date.normalize() - pd.Timedelta(days=1)
        or time.time() - os.path.getmtime(data_file) <= 300
    )
    if use_cache:
        data = pd.read_csv(data_file, on_bad_lines="skip")
    else:
        data = yf_retry(lambda: yf.download(
            symbol,
            start=start_str,
            end=end_str,
            multi_level_index=False,
            progress=False,
            auto_adjust=True,
        ))
        data = data.reset_index()
        data.to_csv(data_file, index=False)

    data = validate_daily_bars(data, curr_date)

    return data


def filter_financials_by_date(data: pd.DataFrame, curr_date: str) -> pd.DataFrame:
    """Drop financial statement columns (fiscal period timestamps) after curr_date.

    yfinance financial statements use fiscal period end dates as columns.
    Columns after curr_date represent future data and are removed to
    prevent look-ahead bias.
    """
    if not curr_date or data.empty:
        return data
    if get_config().get("point_in_time_strict", False) and is_historical(curr_date):
        # Yahoo exposes fiscal period ends, not historical filing vintages.
        return data.iloc[:, :0]
    cutoff = pd.Timestamp(curr_date)
    mask = pd.to_datetime(data.columns, errors="coerce") <= cutoff
    return data.loc[:, mask]


class StockstatsUtils:
    @staticmethod
    def get_stock_stats(
        symbol: Annotated[str, "ticker symbol for the company"],
        indicator: Annotated[
            str, "quantitative indicators based off of the stock data for the company"
        ],
        curr_date: Annotated[
            str, "curr date for retrieving stock price data, YYYY-mm-dd"
        ],
    ):
        data = load_ohlcv(symbol, curr_date)
        df = wrap(data)
        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
        curr_date_str = pd.to_datetime(curr_date).strftime("%Y-%m-%d")

        df[indicator]  # trigger stockstats to calculate the indicator
        matching_rows = df[df["Date"].str.startswith(curr_date_str)]

        if not matching_rows.empty:
            indicator_value = matching_rows[indicator].values[0]
            return indicator_value
        else:
            return "N/A: Not a trading day (weekend or holiday)"
