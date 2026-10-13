"""Bounded, read-only KIS history fallback for missing Yahoo Korea daily bars."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import math
import os
import re
import time

import pandas as pd

from .api_keys import get_api_key
from .integrity import validate_daily_bars
from .vendor_exceptions import VendorInputError, VendorMalformedResponseError

SOURCE = "KIS domestic_daily_itemchartprice (KRX, adjusted prices)"
_CACHE: dict[tuple[str, str, str], tuple[float, pd.DataFrame]] = {}
_MAX_PAGES = 20
_FIELDS = {"Open": "stck_oprc", "High": "stck_hgpr", "Low": "stck_lwpr",
           "Close": "stck_clpr", "Volume": "acml_vol"}


def fallback_enabled(symbol: str) -> bool:
    return (os.getenv("TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED") == "1"
            and re.fullmatch(r"[0-9]{6}\.(KS|KQ)", symbol.upper()) is not None)


def load_kr_daily_bars(symbol: str, start_date: str, end_date: str, *, require_end=False):
    """Return an independently validated KIS series, or None when unavailable.

    Never splice vendors or fill a missing price. Pagination uses strictly older
    end dates and stops after 20 calls. The five-minute process cache is separate
    from Yahoo's disk cache and includes the exact requested point-in-time range.
    A known session-date check can require its exact bar via ``require_end``.
    """
    symbol = symbol.upper()
    if not fallback_enabled(symbol):
        return None
    if not get_api_key("KIS_APP_KEY") or not get_api_key("KIS_APP_SECRET"):
        return None
    start, end = date.fromisoformat(start_date), date.fromisoformat(end_date)
    if start > end:
        raise VendorInputError("start_date must not be later than end_date")
    key = (symbol, start_date, end_date)
    cached = _CACHE.get(key)
    if cached and time.monotonic() - cached[0] <= 300:
        frame = cached[1].copy()
    else:
        from tradingagents.portfolio.kis import KisClient

        client = KisClient.from_api_keys(environment="real")
        cursor = end
        records = {}
        for page in range(_MAX_PAGES):
            if page:
                time.sleep(0.25)
            payload = client.domestic_daily_itemchartprice(
                symbol[:6], start_date=start, end_date=cursor,
                market_division="J", period_division="D", adjusted_price="0",
            )
            rows = payload.get("output2") if isinstance(payload, dict) else None
            if not isinstance(rows, list):
                raise VendorMalformedResponseError("KIS daily history has no row list")
            dates = []
            for row in rows:
                if not isinstance(row, dict):
                    raise VendorMalformedResponseError("KIS daily history contains a malformed row")
                try:
                    stamp = datetime.strptime(str(row.get("stck_bsop_date", "")), "%Y%m%d").date()
                except ValueError as exc:
                    raise VendorMalformedResponseError("KIS daily history contains an invalid date") from exc
                # A future/out-of-window row cannot affect historical validation.
                if stamp > cursor or stamp < start:
                    continue
                dates.append(stamp)
                try:
                    values = {column: float(row[field]) for column, field in _FIELDS.items()}
                except (KeyError, TypeError, ValueError) as exc:
                    raise VendorMalformedResponseError("KIS daily history has incomplete OHLCV") from exc
                if (any(not math.isfinite(v) or v < 0 or (k != "Volume" and v == 0)
                        for k, v in values.items())
                        or values["High"] < max(values["Open"], values["Close"], values["Low"])
                        or values["Low"] > min(values["Open"], values["Close"])):
                    raise VendorMalformedResponseError("KIS daily history has invalid OHLCV")
                if stamp in records and records[stamp] != values:
                    raise VendorMalformedResponseError("KIS daily history has conflicting duplicate dates")
                records[stamp] = values
            if not rows:
                break
            if not dates:
                raise VendorMalformedResponseError("KIS daily history pagination made no progress")
            oldest = min(dates)
            if oldest <= start or len(rows) < 100:
                break
            cursor = oldest - timedelta(days=1)
        else:
            raise VendorMalformedResponseError("KIS daily history exceeded its bounded page limit")
        if not records:
            raise VendorMalformedResponseError("KIS daily history has no requested bars")
        frame = pd.DataFrame([{"Date": stamp, **values} for stamp, values in sorted(records.items())])
        frame = validate_daily_bars(frame, end_date)
        frame.attrs.update(source=SOURCE, observed_at=datetime.now(timezone.utc).isoformat(),
                           requested_start=start_date, requested_end=end_date)
        if len(_CACHE) >= 128:
            _CACHE.clear()
        _CACHE[key] = (time.monotonic(), frame.copy())
    if require_end and frame.iloc[-1]["Date"].date() != end:
        raise VendorMalformedResponseError("KIS has no valid bar for the required completed session")
    return frame


def validate_with_kr_fallback(data, symbol: str, start_date: str, end_date: str):
    """Retain Yahoo when valid/current, otherwise request an entire KIS series."""
    error = None
    try:
        valid = validate_daily_bars(data, end_date)
    except VendorMalformedResponseError as exc:
        error = exc
        valid = None
    if valid is None or valid.iloc[-1]["Date"] < pd.Timestamp(end_date):
        replacement = load_kr_daily_bars(symbol, start_date, end_date)
        if replacement is not None:
            # An invalid latest bar must never be replaced by an older valid bar.
            if error is not None and replacement.iloc[-1]["Date"] < pd.Timestamp(end_date):
                raise error
            if valid is None or replacement.iloc[-1]["Date"] > valid.iloc[-1]["Date"]:
                return replacement
    if error is not None:
        raise error
    return valid


def source_note(frame: pd.DataFrame) -> str:
    if frame.attrs.get("source") != SOURCE:
        return ""
    return (f"# OHLCV source: {SOURCE}; observed_at={frame.attrs['observed_at']}; "
            f"requested_end={frame.attrs['requested_end']}. "
            "Fetched historical bars; not a historical snapshot vintage.\n")
