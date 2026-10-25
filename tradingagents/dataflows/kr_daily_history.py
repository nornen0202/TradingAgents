"""Bounded, read-only KIS history fallback for missing Yahoo Korea daily bars."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import math
import os
import re
import time
from threading import Lock

import pandas as pd

from .api_keys import get_api_key
from .integrity import validate_daily_bars
from .vendor_exceptions import VendorInputError, VendorMalformedResponseError

SOURCE = "KIS domestic_daily_itemchartprice (KRX, adjusted prices)"
_CACHE: dict[tuple[str, str, str], tuple[float, pd.DataFrame]] = {}
_CACHE_LOCK = Lock()
_MAX_PAGES = 20
_FIELDS = {"Open": "stck_oprc", "High": "stck_hgpr", "Low": "stck_lwpr",
           "Close": "stck_clpr", "Volume": "acml_vol"}
YAHOO_ADJUSTMENT = "YFINANCE_DOWNLOAD_AUTO_ADJUST_TRUE"
_YAHOO_BASIS_AUTHORITY = object()


@dataclass(frozen=True)
class _YahooPriceBasis:
    canonical: str
    authority: object

    def __deepcopy__(self, memo):
        return self  # Immutable source-issued proof survives isolated frame copies.


def _capture_yahoo_price_basis(frame, symbol, start_date, end_date, observed_at, *, method, auto_adjust):
    """A fresh source-fetch hook may bind its explicit request, never a CSV read.

    Existing uninstrumented Yahoo/cache inputs do not issue this proof and use
    the allowed full KIS replacement. A dict/label/hash claim is not authority.
    """
    observed = datetime.fromisoformat(observed_at)
    from .kr_security_listing import _day
    start, end = _day(start_date), _day(end_date)
    if (method != "download" or auto_adjust is not True or observed.tzinfo is None
            or observed > datetime.now(timezone.utc) or start > end
            or end > observed.astimezone(timezone(timedelta(hours=9))).date()
            or re.fullmatch(r"[0-9]{6}\.(KS|KQ)", symbol) is None):
        raise ValueError("Explicit observed Yahoo auto-adjust request required")
    value = {"schema": "tradingagents.yahoo-price-request-basis/v1", "provider": "yfinance",
             "method": method, "auto_adjust": auto_adjust, "symbol": symbol,
             "requested_start": start_date, "filtered_end": end_date, "observed_at": observed_at,
             "series_sha256": hashlib.sha256(frame.to_csv(index=False).encode("utf-8")).hexdigest()}
    return _YahooPriceBasis(json.dumps(value, sort_keys=True, separators=(",", ":")), _YAHOO_BASIS_AUTHORITY)


def verified_yahoo_basis(frame, symbol, start_date, end_date, *, as_of=None):
    """Validate only the explicit download(auto_adjust=True) source-issued basis."""
    proof = frame.attrs.get("yahoo_price_basis")
    if (frame.attrs.get("adjustment") != YAHOO_ADJUSTMENT or not isinstance(proof, _YahooPriceBasis)
            or proof.authority is not _YAHOO_BASIS_AUTHORITY):
        return None
    try:
        expected = _capture_yahoo_price_basis(frame, symbol, start_date, end_date, frame.attrs["observed_at"],
                                             method="download", auto_adjust=True)
        observed = datetime.fromisoformat(frame.attrs["observed_at"])
        if proof.canonical != expected.canonical or observed > (as_of or datetime.now(timezone.utc)):
            return None
        result = json.loads(proof.canonical)
        result["basis_id"] = hashlib.sha256(proof.canonical.encode("utf-8")).hexdigest()
        return result
    except (ValueError, TypeError, KeyError):
        return None


def fallback_enabled(symbol: str) -> bool:
    return (os.getenv("TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED") == "1"
            and re.fullmatch(r"[0-9]{6}\.(KS|KQ)", symbol.upper()) is not None)


def _verify_sessions(frame, start_date, end_date, *, strict_start):
    from tradingagents.calendar_access import get_exchange_calendar
    from tradingagents.scheduled.market_calendar import is_supplemental_market_holiday

    start, end = date.fromisoformat(start_date), date.fromisoformat(end_date)
    if start > end:
        raise VendorInputError("start_date must not be later than end_date")
    begin = start if strict_start else max(start, frame.iloc[0]["Date"].date())
    try:
        # The upstream constructor needs a non-empty span even for a single
        # requested session. Padding the calendar never broadens price bounds.
        calendar = get_exchange_calendar("XKRX", start=begin - timedelta(days=1), end=end + timedelta(days=1))
        required = {stamp.date() for stamp in calendar.sessions
                    if begin <= stamp.date() <= end
                    and not is_supplemental_market_holiday(market="KR", session_date=stamp.date())}
    except Exception as exc:
        raise VendorMalformedResponseError("KR daily history session coverage cannot be verified") from exc
    observed = {stamp.date() for stamp in frame["Date"] if start <= stamp.date() <= end}
    if not required or observed != required:
        raise VendorMalformedResponseError("KR daily history has missing required sessions or non-session bars")


def _window(frame, start_date, end_date):
    window = frame.loc[(frame["Date"] >= pd.Timestamp(start_date)) & (frame["Date"] <= pd.Timestamp(end_date))].copy()
    if window.empty:
        raise VendorMalformedResponseError("Pinned KR history has no requested bars")
    return window


def _copy_frame(frame):
    copied = frame.copy()
    copied.attrs = deepcopy(frame.attrs)
    return copied


def _listing_start(frame, symbol, end_date):
    """Rebuild typed identity proof before trusting a cached/selected boundary."""
    if "listing_contract" not in frame.attrs:
        return None
    from .kr_security_listing import cutoff_for_day, validate_listing_receipt
    try:
        attrs = frame.attrs
        unknown_yahoo_clock = attrs.get("provider") == "yfinance" and "observed_at" not in attrs
        observed = None if unknown_yahoo_clock else datetime.fromisoformat(attrs["observed_at"])
        verified = datetime.fromisoformat(attrs.get("listing_verified_at", attrs.get("observed_at")))
        limit = cutoff_for_day(end_date)
        if (verified.tzinfo is None or verified > limit
                or observed is not None and (observed.tzinfo is None or observed > verified)):
            raise ValueError("Unavailable KR history observation")
        contract = validate_listing_receipt(symbol, attrs["listing_contract"],
            requested_start=attrs["requested_start"], end_date=end_date, observed_at=verified)
        price_source_verified = (
            attrs.get("source") == SOURCE and attrs.get("provider") == "kis"
            and attrs.get("adjustment") == "FID_ORG_ADJ_PRC=0"
        ) or (attrs.get("source") == "yfinance" and attrs.get("provider") == "yfinance"
              and verified_yahoo_basis(frame, symbol, attrs["requested_start"], end_date, as_of=limit) is not None)
        if (datetime.fromisoformat(contract["analysis_as_of"]) > limit
                or not price_source_verified or attrs.get("exchange") != "KRX"
                or attrs.get("requested_end") != end_date or attrs.get("complete") is not True
                or attrs.get("required_start") != contract["required_start"]
                or frame.iloc[0]["Date"].date().isoformat() != contract["required_start"]
                or type(attrs.get("session_count")) is not int or attrs["session_count"] != len(frame)
                or attrs.get("series_sha256") != hashlib.sha256(frame.to_csv(index=False).encode("utf-8")).hexdigest()):
            raise ValueError("KR listing receipt and complete series differ")
        _verify_sessions(frame, contract["required_start"], end_date, strict_start=True)
    except (ValueError, TypeError, KeyError, AttributeError, IndexError, VendorMalformedResponseError) as exc:
        raise VendorInputError("KR listing evidence conflicts with this analysis or series") from exc
    return contract["required_start"]


def selected_history(symbol: str, start_date: str, end_date: str):
    from .daily_history_selection import get_selected_daily_history

    if re.fullmatch(r"[0-9]{6}\.(KS|KQ)", symbol.upper()) is None:
        return None
    selected = get_selected_daily_history(symbol, end_date)
    if selected and selected["source"] in {SOURCE, "yfinance"}:
        frame = selected["frame"]
        if frame is None or not isinstance(frame.attrs.get("requested_start"), str) or frame.attrs["requested_start"] > start_date:
            raise VendorMalformedResponseError("Requested history exceeds the pinned KR research series")
        _listing_start(frame, symbol, end_date)
        return _window(frame, start_date, end_date)
    return None


def load_kr_daily_bars(symbol: str, start_date: str, end_date: str, *, require_end=False, require_complete=False,
                       _listing_contract=None):
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
    with _CACHE_LOCK:
        cached = _CACHE.get(key)
        frame = _copy_frame(cached[1]) if cached and time.monotonic() - cached[0] <= 300 else None
    if frame is not None and "listing_contract" in frame.attrs:
        _listing_start(frame, symbol, end_date)
        from .kr_security_listing import cutoff_for_day
        available = datetime.fromisoformat(frame.attrs["listing_contract"]["metadata_identity"]["available_at"])
        if (cutoff_for_day(end_date) - available).total_seconds() > 300:
            frame = None  # A new research must collect a new current identity binding.
    fetched = frame is None
    if fetched:
        from tradingagents.portfolio.kis import KisClient
        from .kr_security_listing import collect_listing_contract, cutoff_for_day, validate_listing_receipt

        contract = _listing_contract
        if contract is not None:
            try:
                current_cutoff = cutoff_for_day(end_date)
                contract = validate_listing_receipt(symbol, contract, requested_start=start_date,
                    end_date=end_date, observed_at=current_cutoff)
                available = datetime.fromisoformat(contract["metadata_identity"]["available_at"])
                if (current_cutoff - available).total_seconds() > 300:
                    contract = None
            except (ValueError, TypeError, KeyError) as exc:
                raise VendorInputError("Supplied KR listing receipt conflicts with this request") from exc
        if contract is None:
            contract = collect_listing_contract(symbol, requested_start=start_date, end_date=end_date)
        required_start = date.fromisoformat(contract["required_start"]) if contract else start
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
                if contract is not None and stamp < required_start:
                    raise VendorMalformedResponseError("KIS KR history predates the verified first listing")
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
            if oldest <= required_start or len(rows) < 100:
                break
            cursor = oldest - timedelta(days=1)
        else:
            raise VendorMalformedResponseError("KIS daily history exceeded its bounded page limit")
        if not records:
            raise VendorMalformedResponseError("KIS daily history has no requested bars")
        frame = pd.DataFrame([{"Date": stamp, **values} for stamp, values in sorted(records.items())])
        frame = validate_daily_bars(frame, end_date)
        frame.attrs.update(source=SOURCE, provider="kis", exchange="KRX", adjustment="FID_ORG_ADJ_PRC=0",
                           observed_at=datetime.now(timezone.utc).isoformat(), requested_start=start_date,
                           requested_end=end_date, request_count=page + 1)
        if contract is not None:
            if frame.iloc[0]["Date"].date() != required_start:
                raise VendorMalformedResponseError("KIS KR history omits the verified first regular session")
            frame.attrs.update(listing_contract=contract, required_start=required_start.isoformat())
    if require_end and frame.iloc[-1]["Date"].date() != end:
        raise VendorMalformedResponseError("KIS has no valid bar for the required completed session")
    if require_complete or "listing_contract" in frame.attrs:
        required = frame.attrs["required_start"] if "listing_contract" in frame.attrs else start_date
        _verify_sessions(frame, required, end_date, strict_start=True)
        frame.attrs.update(complete=True, session_count=len(frame),
                           series_sha256=hashlib.sha256(frame.to_csv(index=False).encode("utf-8")).hexdigest())
        _listing_start(frame, symbol, end_date)
    if fetched:
        with _CACHE_LOCK:
            if len(_CACHE) >= 128:
                _CACHE.clear()
            _CACHE[key] = (time.monotonic(), _copy_frame(frame))
    return frame


def validate_with_kr_fallback(data, symbol: str, start_date: str, end_date: str):
    """Retain Yahoo when valid/current, otherwise request an entire KIS series."""
    from .daily_history_selection import select_daily_history

    symbol = symbol.upper()
    selected = selected_history(symbol, start_date, end_date)
    if selected is not None:
        return selected
    error = None
    try:
        valid = validate_daily_bars(data, end_date)
    except VendorMalformedResponseError as exc:
        error = exc
        valid = None
    if not fallback_enabled(symbol):
        if error is not None:
            raise error
        return valid
    from .kr_security_listing import collect_listing_contract, reviewed_issue
    issue = reviewed_issue(symbol)
    needs_boundary = issue is not None and start_date < issue["first_regular_session"]
    contract = collect_listing_contract(symbol, requested_start=start_date, end_date=end_date) if needs_boundary else None
    if needs_boundary and contract is None:
        raise VendorInputError("Reviewed KR listing evidence is unavailable for this analysis")
    if valid is not None:
        try:
            if contract is not None:
                required = contract["required_start"]
                if valid.attrs.get("source") not in (None, "yfinance") or valid.attrs.get("provider") not in (None, "yfinance"):
                    raise VendorMalformedResponseError("Unselected KR price-provider claims require full replacement")
                if valid.iloc[0]["Date"].date().isoformat() != required:
                    raise VendorMalformedResponseError("Yahoo KR history omits the verified first regular session")
                try:
                    price_observed = datetime.fromisoformat(valid.attrs["observed_at"])
                    if price_observed.tzinfo is None or price_observed > datetime.now(timezone.utc):
                        raise ValueError("Unavailable price clock")
                except (ValueError, KeyError, TypeError) as exc:
                    # A cache read/identity check is not a new vendor observation.
                    # Use the already allowed entire KIS replacement, not a fabricated clock.
                    raise VendorMalformedResponseError("Yahoo KR price collection clock is unverified") from exc
                if verified_yahoo_basis(valid, symbol, start_date, end_date) is None:
                    raise VendorMalformedResponseError("Yahoo KR adjustment request basis is unverified")
            else:
                required = _listing_start(valid, symbol, end_date) or start_date
            _verify_sessions(valid, required, end_date,
                             strict_start=contract is not None or valid.attrs.get("source") == SOURCE)
        except VendorMalformedResponseError as exc:
            error, valid = exc, None
    if valid is None:
        kwargs = {"_listing_contract": contract} if contract is not None else {}
        replacement = load_kr_daily_bars(symbol, start_date, end_date, require_complete=True, **kwargs)
        if replacement is not None:
            replacement = validate_daily_bars(replacement, end_date)
            required = _listing_start(replacement, symbol, end_date) or start_date
            _verify_sessions(replacement, required, end_date, strict_start=True)
            select_daily_history(symbol, end_date, SOURCE, frame=replacement)
            pinned = selected_history(symbol, start_date, end_date)
            return pinned if pinned is not None else _window(replacement, start_date, end_date)
    if error is not None:
        raise error
    valid.attrs.update(requested_start=start_date, requested_end=end_date)
    if contract is not None:
        # KIS binds the identity only. The Yahoo price series/adjustment basis is
        # never relabelled as KIS prices and is never mixed with replacement rows.
        valid.attrs.update(listing_contract=contract, required_start=contract["required_start"],
            source="yfinance", provider="yfinance", exchange="KRX", adjustment=YAHOO_ADJUSTMENT,
            listing_verified_at=datetime.now(timezone.utc).isoformat(), complete=True,
            session_count=len(valid), series_sha256=hashlib.sha256(valid.to_csv(index=False).encode("utf-8")).hexdigest())
        _listing_start(valid, symbol, end_date)
    select_daily_history(symbol, end_date, valid.attrs.get("source") or "yfinance", frame=valid)
    pinned = selected_history(symbol, start_date, end_date)
    return pinned if pinned is not None else valid


def source_note(frame: pd.DataFrame) -> str:
    source = frame.attrs.get("source")
    if source != SOURCE and not (source == "yfinance" and "listing_contract" in frame.attrs):
        return ""
    listing = frame.attrs.get("listing_contract")
    listing_note = (f" Original request start={frame.attrs['requested_start']}; "
                    f"verified first regular session={listing['required_start']}; "
                    f"listing_contract={listing['contract_id']}." if listing else "")
    return (f"# OHLCV source: {source}; observed_at={frame.attrs.get('observed_at', 'UNVERIFIED')}; "
            f"requested_end={frame.attrs['requested_end']}. "
            f"Fetched historical bars; not a historical snapshot vintage.{listing_note}\n")
