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
            contract = cached[1].attrs.get("listing_contract")
            if contract is not None:
                from .security_listing import cutoff_for_day, validate_listing_receipt
                current_cutoff = cutoff_for_day(end_date)
                try:
                    validate_listing_receipt(symbol, contract, requested_start=start.isoformat(),
                                             end_date=end_date, observed_at=current_cutoff)
                except (ValueError, TypeError, KeyError) as exc:
                    raise VendorInputError("Cached listing evidence conflicts with this analysis cutoff") from exc
                available = datetime.fromisoformat(contract["metadata_identity"]["available_at"])
                if (current_cutoff - available).total_seconds() <= 300:
                    return cached[1].copy()
            else:
                return cached[1].copy()

    from tradingagents.portfolio.kis import KisApiError, KisClient

    started = time.monotonic()
    client = KisClient.from_api_keys(environment="real")  # allowlisted GET market data only
    from .security_listing import collect_listing_contract
    contract = collect_listing_contract(symbol, client, requested_start=start.isoformat(), end_date=end_date)
    required_start = date.fromisoformat(contract["required_start"]) if contract else start
    if contract:
        required = _sessions(required_start, end)
        if not required or required[0] != required_start:
            raise VendorMalformedResponseError("Reviewed first regular listing is not a completed requested session")
    cursor, records, exchange = end, {}, contract["reviewed_event"]["exchange"] if contract else None
    excluded_pre_regular_dates = set()
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
            if stamp < required_start:
                if contract and stamp >= start:
                    excluded_pre_regular_dates.add(stamp.isoformat())
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
    if contract:
        frame.attrs.update(listing_contract=contract, required_start=required_start.isoformat(),
                           excluded_before_verified_regular_listing=sorted(excluded_pre_regular_dates))
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
        if "listing_contract" in frame.attrs:
            from .security_listing import cutoff_for_day, validate_listing_receipt
            try:
                observed = datetime.fromisoformat(frame.attrs["observed_at"])
                validate_listing_receipt(symbol, frame.attrs["listing_contract"],
                                         requested_start=frame.attrs["requested_start"], end_date=end_date,
                                         observed_at=min(observed, cutoff_for_day(end_date)))
            except (ValueError, TypeError, KeyError) as exc:
                raise VendorInputError("Pinned listing evidence conflicts with this analysis cutoff") from exc
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
        try:
            values = valid[["Open", "High", "Low", "Close", "Volume"]].astype(float)
            complete_values = (
                all(math.isfinite(value) for value in values.to_numpy().flat)
                and (values[["Open", "High", "Low", "Close"]] > 0).all().all()
                and (values["Volume"] >= 0).all()
                and (values["High"] >= values[["Open", "Low", "Close"]].max(axis=1)).all()
                and (values["Low"] <= values[["Open", "High", "Close"]].min(axis=1)).all()
            )
        except (KeyError, TypeError, ValueError, OverflowError):
            complete_values = False
        if not complete_values:
            error = VendorMalformedResponseError("Yahoo US daily history has invalid or incomplete OHLCV")
            valid = None
    if valid is not None and fallback_enabled(symbol):
        # A recent final bar cannot hide a missing session inside the observed
        # series. Preserve the existing leading-history contract; the first
        # observed bar is not evidence of a listing date.
        begin = valid.iloc[0]["Date"].date()
        last = valid.iloc[-1]["Date"].date()
        try:
            required = set(_sessions(begin, last)) if begin <= last else set()
            observed = {stamp.date() for stamp in valid["Date"]}
            if observed != required:
                raise VendorMalformedResponseError("Yahoo US daily history has missing or non-session bars")
        except VendorMalformedResponseError as exc:
            error = exc
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
    listing = frame.attrs.get("listing_contract")
    listing_note = (f" Original request start={frame.attrs['requested_start']}; "
                    f"verified first regular session={listing['required_start']}; "
                    f"listing_contract={listing['contract_id']}." if listing else "")
    return (f"# OHLCV source: {SOURCE}; exchange={frame.attrs['exchange']}; "
            f"observed_at={frame.attrs['observed_at']}; requested_end={frame.attrs['requested_end']}; "
            f"series_sha256={frame.attrs['series_sha256']}; complete=true. "
            f"Single provider adjustment basis for price and indicators; not a historical snapshot vintage.{listing_note}\n")
