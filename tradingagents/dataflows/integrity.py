"""Shared point-in-time and path guards for data supplied to investment agents."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import math
import re
from zoneinfo import ZoneInfo

import pandas as pd

from .vendor_exceptions import VendorInputError, VendorMalformedResponseError


def safe_symbol(symbol: str) -> str:
    symbol = str(symbol).strip().upper()
    if not re.fullmatch(r"[A-Z0-9^][A-Z0-9.^=_-]{0,63}", symbol) or ".." in symbol:
        raise VendorInputError("Invalid ticker: use an exchange-qualified symbol, not a path.")
    return symbol


def is_historical(as_of: str | date | datetime | None, *, market_timezone: str = "UTC") -> bool:
    """An exact past instant or completed market day requires historical evidence."""
    if not as_of:
        return False
    raw = str(as_of).strip()
    return bool(raw) and parse_analysis_cutoff(as_of, market_timezone) < datetime.now(timezone.utc)


def requires_historical_snapshot(ticker: str, requested: str | date | datetime | None) -> bool:
    from tradingagents.agents.utils.instrument_resolver import resolve_instrument
    from .config import get_config

    config = get_config()
    if config.get("point_in_time_strict"):
        return True
    scoped = config.get("analysis_as_of")
    if not requested and not scoped:
        return False
    zone = resolve_instrument(ticker).timezone
    return is_historical(requested, market_timezone=zone) or is_historical(scoped, market_timezone=zone)


def parse_analysis_cutoff(requested: date | datetime | str, market_timezone: str) -> datetime:
    """Resolve a date to the end of its market day or preserve an exact instant."""
    raw = str(requested).strip()
    stamp = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if len(raw) == 10:
        return stamp.replace(tzinfo=ZoneInfo(market_timezone)) + timedelta(days=1) - timedelta(microseconds=1)
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ValueError("Analysis cutoff requires a timezone")
    return stamp


def utc_window(start: str, end: str) -> tuple[datetime, datetime]:
    """Inclusive calendar dates represented by a UTC half-open interval."""
    lower = datetime.strptime(start, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    upper = datetime.strptime(end, "%Y-%m-%d").replace(tzinfo=timezone.utc) + timedelta(days=1)
    if lower >= upper:
        raise VendorInputError("start_date must not be later than end_date")
    return lower, upper


def session_date(value):
    """Preserve exchange-local daily labels, including mixed DST offsets."""
    try:
        stamp = pd.Timestamp(value)
        if pd.isna(stamp):
            return pd.NaT
        return stamp.tz_localize(None).normalize() if stamp.tzinfo else stamp.normalize()
    except (TypeError, ValueError):
        return pd.NaT


def validate_daily_bars(data: pd.DataFrame, as_of: str) -> pd.DataFrame:
    """Cut off future rows before validation; never invent a price or volume."""
    frame = data.copy()
    if "Date" not in frame or "Close" not in frame:
        raise VendorMalformedResponseError("OHLCV must include Date and Close")
    frame["Date"] = pd.to_datetime(frame["Date"].map(session_date))
    frame = frame.loc[frame["Date"].notna() & (frame["Date"] <= pd.Timestamp(as_of))]
    frame = frame.sort_values("Date").drop_duplicates("Date", keep="last")
    for column in ("Open", "High", "Low", "Close", "Volume"):
        if column in frame:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if frame.empty:
        raise VendorMalformedResponseError("No data found in the requested OHLCV window")
    if not frame.empty:
        latest = frame.iloc[-1]
        close = latest["Close"]
        if pd.isna(close) or close <= 0 or close == float("inf"):
            raise VendorMalformedResponseError("Latest requested OHLCV bar has no valid close; do not use an older price")
        for column in ("Open", "High", "Low", "Volume"):
            if column in latest and (
                not math.isfinite(latest[column])
                or latest[column] < 0
                or (column != "Volume" and latest[column] == 0)
            ):
                raise VendorMalformedResponseError(f"Latest OHLCV bar has invalid {column}")
        if "High" in latest and "Low" in latest and latest["High"] < latest["Low"]:
            raise VendorMalformedResponseError("OHLCV high is below low")
        for column in ("Open", "Close"):
            if column in latest and (
                ("High" in latest and latest[column] > latest["High"])
                or ("Low" in latest and latest[column] < latest["Low"])
            ):
                raise VendorMalformedResponseError(f"Latest OHLCV {column} is outside the daily range")
        if (pd.Timestamp(as_of) - latest["Date"]).days > 7:
            raise VendorMalformedResponseError("Stale OHLCV: last available bar is over seven calendar days before the requested date")
    return frame.reset_index(drop=True)
