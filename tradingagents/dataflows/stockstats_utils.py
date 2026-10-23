import time
import logging
import math
import re
from datetime import datetime

import pandas as pd
import yfinance as yf
from yfinance.exceptions import YFRateLimitError
from stockstats import dft_windows, wrap
from typing import Annotated
import os
from .config import get_config
from .integrity import safe_symbol, session_date, is_historical
from .daily_history import fallback_enabled, selected_history, validate_with_fallback
from .vendor_exceptions import InsufficientIndicatorHistoryError, VendorInputError

logger = logging.getLogger(__name__)


def _indicator_session_date(value):
    try:
        return session_date(value)
    except (AttributeError, OverflowError):
        return pd.NaT


def indicator_minimum_observations(indicator: str) -> int:
    """Nominal input requirements, not EMA/SMMA convergence guarantees.

    Read stockstats' actual default periods, including explicit overrides.
    Difference/true-range indicators require an observed preceding price;
    MACD signal/histogram require a full signal period of mature MACD inputs.
    """
    fixed = {"close_50_sma": 50, "close_200_sma": 200, "close_10_ema": 10}
    if indicator in fixed:
        return fixed[indicator]
    family = {"macds": "macd", "macdh": "macd", "boll_ub": "boll", "boll_lb": "boll"}.get(indicator, indicator)
    if family not in {"macd", "boll", "rsi", "atr", "vwma", "mfi"}:
        raise VendorInputError(f"Unsupported stockstats indicator: {indicator}")
    try:
        periods = [int(value) for value in dft_windows(family).split(",")]
        if len(periods) != (3 if family == "macd" else 1) or any(value <= 0 for value in periods):
            raise ValueError("Invalid period configuration")
    except (AttributeError, TypeError, ValueError) as exc:
        raise InsufficientIndicatorHistoryError("Stockstats indicator periods cannot be verified") from exc
    if family == "macd":
        return max(periods[:2]) + (periods[2] - 1 if indicator != "macd" else 0)
    return periods[0] + (1 if family in {"rsi", "atr", "mfi"} else 0)


def _verify_indicator_sessions(frame: pd.DataFrame, symbol: str, cutoff: pd.Timestamp) -> None:
    """Never label a missing KR/US trading bar as a weekend or holiday."""
    symbol = safe_symbol(symbol)
    market = "KR" if re.fullmatch(r"[0-9]{6}\.(KS|KQ)", symbol) else "US" if re.fullmatch(r"[A-Z]{1,10}(?:-B)?", symbol) else None
    if market is None:
        return  # No invented exchange calendar for other instrument classes.
    try:
        from tradingagents.calendar_access import get_exchange_calendar
        from tradingagents.scheduled.market_calendar import default_calendar_name, is_supplemental_market_holiday
        calendar = get_exchange_calendar(default_calendar_name(market), start=frame["Date"].iloc[0], end=cutoff)
        # A weekend cutoff can be later than this calendar's last session.
        sessions = pd.DatetimeIndex(calendar.sessions).tz_localize(None)
        sessions = sessions[(sessions >= frame["Date"].iloc[0]) & (sessions <= cutoff)]
        expected = {stamp.date() for stamp in sessions
                    if not is_supplemental_market_holiday(market=market, session_date=stamp.date())}
    except Exception as exc:
        raise InsufficientIndicatorHistoryError("Indicator session coverage cannot be verified") from exc
    observed = set(frame["Date"].dt.date)
    if observed != expected:
        raise InsufficientIndicatorHistoryError("Indicator history has missing trading sessions or non-session bars")


def calculate_stockstats_indicator(data: pd.DataFrame, symbol: str, indicator: str, curr_date: str) -> pd.DataFrame:
    """Keep the full calculation history; mask only immature output rows."""
    required = indicator_minimum_observations(indicator)
    try:
        cutoff = pd.Timestamp(datetime.strptime(curr_date, "%Y-%m-%d"))
    except (TypeError, ValueError) as exc:
        raise VendorInputError("Indicator date must be YYYY-MM-DD") from exc
    if "Date" not in data:
        raise InsufficientIndicatorHistoryError("Indicator history has no verifiable dates")
    frame = data.copy()
    frame["Date"] = pd.to_datetime(frame["Date"].map(_indicator_session_date))
    # Unknown/future dates cannot contribute to observations or calculations.
    frame = frame.loc[frame["Date"].notna() & (frame["Date"] <= cutoff)]
    frame = frame.sort_values("Date").drop_duplicates("Date", keep="last").reset_index(drop=True)
    if len(frame) < required:
        raise InsufficientIndicatorHistoryError(
            f"Insufficient history for {indicator}: requires {required} observed daily bars; found {len(frame)}"
        )
    columns = ["Close"]
    if indicator in {"atr", "vwma", "mfi"}:
        columns += ["High", "Low"]
    if indicator in {"vwma", "mfi"}:
        columns += ["Volume"]
    for column in columns:
        if column not in frame:
            raise InsufficientIndicatorHistoryError(f"Indicator history is missing {column}")
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
        if not frame[column].map(lambda value: pd.notna(value) and math.isfinite(value) and (value >= 0 if column == "Volume" else value > 0)).all():
            raise InsufficientIndicatorHistoryError(f"Indicator history has invalid {column} observations")
    _verify_indicator_sessions(frame, symbol, cutoff)
    calculated = wrap(frame.copy())
    values = calculated[indicator].copy()
    values.iloc[:required - 1] = float("nan")
    result = frame[["Date"]].copy()
    result[indicator] = values.to_numpy()
    result.attrs["indicator_minimum_observations"] = required
    return result


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


def load_ohlcv(symbol: str, curr_date: str, *, requested_start: str | None = None) -> pd.DataFrame:
    """Fetch OHLCV data with caching, filtered to prevent look-ahead bias.

    Downloads at least five years before the requested date, or an explicitly
    earlier price-report start, and caches per symbol/window. Active-date caches
    expire after five minutes; historical rows
    are cut off before validation and indicator calculation.
    """
    config = get_config()
    symbol = safe_symbol(symbol)
    curr_date_dt = pd.to_datetime(curr_date)

    # Include enough warm-up history even for an older evaluation date.
    today_date = pd.Timestamp.today()
    start_date = min(today_date, curr_date_dt) - pd.DateOffset(years=5)
    if requested_start is not None:
        try:
            requested = pd.Timestamp(datetime.strptime(requested_start, "%Y-%m-%d"))
        except (TypeError, ValueError) as exc:
            raise VendorInputError("Requested history start must be YYYY-MM-DD") from exc
        if requested > curr_date_dt:
            raise VendorInputError("Requested history start exceeds the price end date")
        start_date = min(start_date, requested)
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
    pinned = selected_history(symbol, start_str, curr_date)
    if pinned is not None:
        data = pinned
    elif use_cache:
        data = pd.read_csv(data_file, on_bad_lines="skip", float_precision="round_trip")
    else:
        try:
            data = yf_retry(lambda: yf.download(
                symbol,
                start=start_str,
                end=end_str,
                multi_level_index=False,
                progress=False,
                auto_adjust=True,
            ))
        except Exception:
            if not fallback_enabled(symbol):
                raise
            data = pd.DataFrame()
        data = data.reset_index()
    validated = validate_with_fallback(data, symbol, start_str, curr_date)
    # Validate before admitting a new Yahoo cache. A KIS replacement must never
    # poison a Yahoo-labelled file or mix vendor adjustment bases.
    if pinned is None and not use_cache and not validated.attrs.get("source"):
        data.to_csv(data_file, index=False)

    # Reuse this exact validated input for the private chart, without refetching.
    from tradingagents.charting.capture import capture_daily_frame
    try:
        capture_daily_frame(symbol, validated, curr_date=curr_date)
    except (ValueError, TypeError, KeyError, OverflowError) as exc:
        logger.warning("Chart capture unavailable: %s", type(exc).__name__)
    return validated


def filter_financials_by_date(data: pd.DataFrame, curr_date: str) -> pd.DataFrame:
    """Drop financial statement columns (fiscal period timestamps) after curr_date.

    yfinance financial statements use fiscal period end dates as columns.
    Columns after curr_date represent future data and are removed to
    prevent look-ahead bias.
    """
    if not curr_date or data.empty:
        return data
    if is_historical(curr_date):
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
        df = calculate_stockstats_indicator(data, symbol, indicator, curr_date)
        df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
        curr_date_str = pd.to_datetime(curr_date).strftime("%Y-%m-%d")

        matching_rows = df[df["Date"].str.startswith(curr_date_str)]

        if not matching_rows.empty:
            indicator_value = matching_rows[indicator].values[0]
            if pd.isna(indicator_value) or not math.isfinite(indicator_value):
                raise InsufficientIndicatorHistoryError(f"Insufficient or undefined {indicator} history on {curr_date}")
            return indicator_value
        else:
            raise InsufficientIndicatorHistoryError(f"No observed {indicator} value for requested date {curr_date}")
