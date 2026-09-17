"""Shared point-in-time and path guards for data supplied to investment agents."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import math
import re

import pandas as pd

from .vendor_exceptions import VendorInputError, VendorMalformedResponseError


def safe_symbol(symbol: str) -> str:
    symbol = str(symbol).strip().upper()
    if not re.fullmatch(r"[A-Z0-9^][A-Z0-9.^=_-]{0,63}", symbol) or ".." in symbol:
        raise VendorInputError("Invalid ticker: use an exchange-qualified symbol, not a path.")
    return symbol


def is_historical(as_of: str | None) -> bool:
    """Current snapshots cannot stand in for a prior day's information set."""
    return bool(as_of and date.fromisoformat(as_of) < datetime.now(timezone.utc).date())


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
            if column in latest and (not math.isfinite(latest[column]) or latest[column] < 0):
                raise VendorMalformedResponseError(f"Latest OHLCV bar has invalid {column}")
        if "High" in latest and "Low" in latest and latest["High"] < latest["Low"]:
            raise VendorMalformedResponseError("OHLCV high is below low")
        if (pd.Timestamp(as_of) - latest["Date"]).days > 7:
            raise VendorMalformedResponseError("Stale OHLCV: last available bar is over seven calendar days before the requested date")
    return frame.reset_index(drop=True)
