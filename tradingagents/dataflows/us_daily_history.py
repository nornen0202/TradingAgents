"""Independent, bounded KIS US daily history for recovering invalid Yahoo bars.

Prices and indicators use one complete MODP=1 series. No row is spliced into
Yahoo, and a fresh retrieval is not evidence of a historical snapshot vintage.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import hashlib
import math
import os
import re
import time
from threading import RLock

import pandas as pd

from .api_keys import get_api_key
from .integrity import validate_daily_bars
from .intraday.us_symbols import kis_symbol
from .vendor_exceptions import VendorInputError, VendorMalformedResponseError

SOURCE = "KIS overseas_dailyprice (US, MODP=1 adjusted prices)"
_MAX_PAGES = 20
_MAX_SECONDS = 120
_CACHE: dict[tuple[str, str, str], tuple[float, pd.DataFrame]] = {}
_CACHE_LOCK = RLock()
_FIELDS = {"Open": "open", "High": "high", "Low": "low", "Close": "clos", "Volume": "tvol"}


def fallback_enabled(symbol: str) -> bool:
    return (os.getenv("TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED") == "1"
            and re.fullmatch(r"[A-Z]{1,10}(?:-B)?", symbol.upper()) is not None
            and ("-" not in symbol or symbol.upper() == "BRK-B"))


def _sessions(start: date, end: date) -> list[date]:
    try:
        from tradingagents.calendar_access import get_exchange_calendar
        calendar = get_exchange_calendar("XNYS")
        sessions = [stamp.date() for stamp in calendar.sessions_in_range(start.isoformat(), end.isoformat())]
        if not sessions or calendar.session_close(sessions[-1].isoformat()).to_pydatetime() > datetime.now(timezone.utc):
            raise ValueError("No completed requested session")
        return sessions
    except Exception as exc:
        raise VendorMalformedResponseError("US completed-session calendar is unavailable for the requested range") from exc


def _window(frame: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    result = frame.loc[(frame["Date"] >= pd.Timestamp(start_date)) & (frame["Date"] <= pd.Timestamp(end_date))].copy()
    if result.empty:
        raise VendorMalformedResponseError("KIS has no requested US daily bars")
    return result.reset_index(drop=True)


def load_us_daily_bars(symbol: str, start_date: str, end_date: str):
    """Return a separate canonical series including the five-year warmup.

    Every expected US session must be present, including the latest completed
    session. Unknown dates, malformed bars, holes, conflicting duplicates, page
    repetition and exhausted bounds fail closed. Newly listed/limited histories
    cannot silently stand in for the requested warmup interval.
    """
    symbol = symbol.upper()
    if not fallback_enabled(symbol) or not get_api_key("KIS_APP_KEY") or not get_api_key("KIS_APP_SECRET"):
        return None
    try:
        start, end = date.fromisoformat(start_date), date.fromisoformat(end_date)
    except ValueError as exc:
        raise VendorInputError("US daily history requires ISO calendar dates") from exc
    if start > end:
        raise VendorInputError("start_date must not be later than end_date")
    # Fetch once for both the price report and all indicator warmups.
    start = min(start, (pd.Timestamp(end) - pd.DateOffset(years=5)).date())
    required = _sessions(start, end)
    key = (symbol, start.isoformat(), end_date)
    with _CACHE_LOCK:
        cached = _CACHE.get(key)
        if cached and time.monotonic() - cached[0] <= 300:
            return cached[1].copy()

    from tradingagents.portfolio.kis import KisApiError, KisClient

    client = KisClient.from_api_keys(environment="real")  # allowlisted GET market data only
    cursor, records, exchange = end, {}, None
    started = time.monotonic()
    calls = 0
    for page in range(_MAX_PAGES):
        if time.monotonic() - started >= _MAX_SECONDS:
            raise VendorMalformedResponseError("KIS US daily history exceeded its time limit")
        payload = None
        # Probe only known US venues; never guess a market from the ticker text.
        for candidate in (exchange,) if exchange else ("NAS", "NYS", "AMS"):
            if calls:
                time.sleep(0.25)
            calls += 1
            try:
                payload, _headers = client.request_json(
                    method="GET", path="/uapi/overseas-price/v1/quotations/dailyprice", tr_id="HHDFS76240000",
                    params={"AUTH": "", "EXCD": candidate, "SYMB": kis_symbol(symbol),
                            "GUBN": "0", "BYMD": cursor.strftime("%Y%m%d"), "MODP": "1"},
                )
            except KisApiError:
                if exchange:
                    raise
                continue
            rows = payload.get("output2") if isinstance(payload, dict) else None
            if not isinstance(rows, list):
                raise VendorMalformedResponseError("KIS US daily history has no row list")
            if rows:
                exchange = candidate
                break
        rows = payload.get("output2") if isinstance(payload, dict) else None
        if time.monotonic() - started >= _MAX_SECONDS:
            raise VendorMalformedResponseError("KIS US daily history exceeded its time limit")
        if not exchange or not rows:
            raise VendorMalformedResponseError("KIS US daily history ended before the required range")
        page_dates = []
        for row in rows:
            if not isinstance(row, dict):
                raise VendorMalformedResponseError("KIS US daily history contains a malformed row")
            value = str(row.get("xymd", ""))
            try:
                if re.fullmatch(r"[0-9]{8}", value) is None:
                    raise ValueError("Date must have eight digits")
                stamp = datetime.strptime(value, "%Y%m%d").date()
            except ValueError as exc:
                raise VendorMalformedResponseError("KIS US daily history contains an invalid date") from exc
            # Future/out-of-window rows cannot affect values or pagination.
            if stamp > cursor:
                continue
            page_dates.append(stamp)
            if stamp < start:
                continue
            try:
                values = {name: float(row[field]) for name, field in _FIELDS.items()}
            except (KeyError, TypeError, ValueError) as exc:
                raise VendorMalformedResponseError("KIS US daily history has incomplete OHLCV") from exc
            if (any(not math.isfinite(v) or v < 0 or (k != "Volume" and v == 0) for k, v in values.items())
                    or values["High"] < max(values["Open"], values["Close"], values["Low"])
                    or values["Low"] > min(values["Open"], values["Close"])):
                raise VendorMalformedResponseError("KIS US daily history has invalid OHLCV")
            if stamp in records and records[stamp] != values:
                raise VendorMalformedResponseError("KIS US daily history has conflicting duplicate dates")
            records[stamp] = values
        if not page_dates:
            raise VendorMalformedResponseError("KIS US daily history pagination made no progress")
        oldest = min(page_dates)
        if oldest <= required[0]:
            break
        cursor = oldest - timedelta(days=1)
    else:
        raise VendorMalformedResponseError("KIS US daily history exceeded its bounded page limit")
    if set(records) != set(required):
        raise VendorMalformedResponseError("KIS US daily history is missing required sessions or contains non-session bars")
    frame = validate_daily_bars(pd.DataFrame([{"Date": stamp, **values} for stamp, values in sorted(records.items())]), end_date)
    frame.attrs.update(source=SOURCE, provider="kis", exchange=exchange, adjustment="MODP=1",
                       observed_at=datetime.now(timezone.utc).isoformat(), requested_start=start.isoformat(),
                       requested_end=end_date, complete=True, session_count=len(required), request_count=calls,
                       series_sha256=hashlib.sha256(frame.to_csv(index=False).encode("utf-8")).hexdigest())
    with _CACHE_LOCK:
        if len(_CACHE) >= 128:
            _CACHE.clear()
        _CACHE[key] = (time.monotonic(), frame.copy())
    return frame


def selected_history(symbol: str, start_date: str, end_date: str):
    from .daily_history_selection import get_selected_daily_history

    selected = get_selected_daily_history(symbol, end_date)
    if selected and selected["source"] == SOURCE:
        frame = selected["frame"]
        if frame is None or frame.attrs["requested_start"] > start_date:
            raise VendorMalformedResponseError("Requested history exceeds the pinned research series")
        return _window(frame, start_date, end_date)
    return None


def validate_with_us_fallback(data, symbol: str, start_date: str, end_date: str):
    from .daily_history_selection import select_daily_history

    selected = selected_history(symbol, start_date, end_date)
    if selected is not None:
        return selected
    error, valid = None, None
    try:
        valid = validate_daily_bars(data, end_date)
    except VendorMalformedResponseError as exc:
        error = exc
    if valid is not None and fallback_enabled(symbol):
        # A recent final bar cannot hide a missing session inside the observed
        # series. Preserve the existing leading-history contract; the first
        # observed bar is not evidence of a listing date.
        begin = max(date.fromisoformat(start_date), valid.iloc[0]["Date"].date())
        last = valid.iloc[-1]["Date"].date()
        required = set(_sessions(begin, last)) if begin <= last else set()
        observed = {stamp.date() for stamp in valid["Date"] if stamp.date() >= begin}
        if required - observed:
            error = VendorMalformedResponseError("Yahoo US daily history is missing an interior completed session")
            valid = None
    stale_required_session = (valid is not None and fallback_enabled(symbol)
        and valid.iloc[-1]["Date"] < pd.Timestamp(_sessions(date.fromisoformat(start_date), date.fromisoformat(end_date))[-1]))
    if fallback_enabled(symbol) and (valid is None or stale_required_session):
        replacement = load_us_daily_bars(symbol, start_date, end_date)
        if replacement is not None:
            select_daily_history(symbol, end_date, SOURCE, frame=replacement)
            # A parallel tool may have selected first; return that exact frame.
            pinned = selected_history(symbol, start_date, end_date)
            return pinned if pinned is not None else _window(replacement, start_date, end_date)
    if error is not None:
        raise error
    if stale_required_session:
        raise VendorMalformedResponseError("No provider supplied the required completed US session")
    select_daily_history(symbol, end_date, "yfinance")
    return valid


def source_note(frame: pd.DataFrame) -> str:
    if frame.attrs.get("source") != SOURCE:
        return ""
    return (f"# OHLCV source: {SOURCE}; exchange={frame.attrs['exchange']}; "
            f"observed_at={frame.attrs['observed_at']}; requested_end={frame.attrs['requested_end']}; "
            f"series_sha256={frame.attrs['series_sha256']}; complete=true. "
            "Single provider adjustment basis for price and indicators; not a historical snapshot vintage.\n")
