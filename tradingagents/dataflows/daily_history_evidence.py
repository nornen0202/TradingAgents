"""Allowlisted provenance receipts, independent of tool text and mutable frames."""
from __future__ import annotations

from contextvars import ContextVar
from copy import deepcopy
from datetime import date, datetime, timezone
import hashlib
import json
import math
import re
from threading import Lock

import pandas as pd


SCHEMA = "tradingagents.daily-history-evidence/v1"
LIMITATION = "Retrieved adjusted prices are not a verified historical snapshot vintage."
_ACTIVE = ContextVar("daily_history_evidence", default=None)


def _day(value):
    if not isinstance(value, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
        raise ValueError("Unverified session date")
    return date.fromisoformat(value)


def _snapshot(symbol, end_date, source, frame):
    # Source-only routes cannot invent an observation clock or snapshot hash.
    entry = {"symbol": symbol, "source": source, "requested_end": end_date,
             "status": "UNVERIFIED", "historical_vintage_verified": False,
             "limitations": [LIMITATION]}
    try:
        end = _day(end_date)
        now = datetime.now(timezone.utc)
        if end > now.date():
            raise ValueError("Future requested date")
        if frame is None:
            entry["reason"] = "selected_source_without_snapshot"
            return entry
        if not isinstance(frame, pd.DataFrame) or frame.empty:
            raise ValueError("Missing snapshot rows")
        from .us_daily_history import SOURCE
        from .alpaca_daily_history import SOURCE as ALPACA_SOURCE
        from .kr_daily_history import SOURCE as KR_SOURCE
        from .kr_daily_history import verified_yahoo_basis

        attrs = frame.attrs
        us_metadata = source == SOURCE and attrs.get("adjustment") == "MODP=1" and attrs.get("exchange") in {"NAS", "NYS", "AMS"}
        alpaca_metadata = (source == ALPACA_SOURCE and attrs.get("adjustment") == "all"
                           and attrs.get("exchange") == "US_SIP" and attrs.get("feed") == "sip"
                           and attrs.get("symbol_asof") == end_date)
        kr_metadata = (source == KR_SOURCE and re.fullmatch(r"[0-9]{6}\.(KS|KQ)", symbol) is not None
                       and attrs.get("adjustment") == "FID_ORG_ADJ_PRC=0" and attrs.get("exchange") == "KRX")
        kr_yahoo_metadata = (source == "yfinance" and attrs.get("provider") == "yfinance"
                             and re.fullmatch(r"[0-9]{6}\.(KS|KQ)", symbol) is not None
                             and attrs.get("exchange") == "KRX"
                             and verified_yahoo_basis(frame, symbol, attrs.get("requested_start"), end_date, as_of=now) is not None
                             and isinstance(attrs.get("listing_contract"), dict)
                             and attrs["listing_contract"].get("schema") == "tradingagents.verified-kr-first-regular-listing/v1")
        if (not (us_metadata or alpaca_metadata or kr_metadata or kr_yahoo_metadata) or attrs.get("source") != source
                or attrs.get("provider") != ("yfinance" if kr_yahoo_metadata else "alpaca" if alpaca_metadata else "kis")
                or attrs.get("complete") is not True):
            raise ValueError("Unverified provider metadata")
        start = _day(attrs.get("requested_start"))
        if _day(attrs.get("requested_end")) != end or start > end:
            raise ValueError("Snapshot date bounds mismatch")
        unknown_yahoo_clock = kr_yahoo_metadata and "observed_at" not in attrs
        observed = None if unknown_yahoo_clock else datetime.fromisoformat(str(attrs.get("observed_at")).replace("Z", "+00:00"))
        if observed is not None and (observed.tzinfo is None or observed.utcoffset() is None or observed > now):
            raise ValueError("Unverified observation clock")
        dates = pd.to_datetime(frame["Date"], errors="raise")
        if (dates.isna().any() or dates.dt.tz is not None or dates.duplicated().any()
                or not dates.is_monotonic_increasing or (dates != dates.dt.normalize()).any()
                or dates.min().date() < start or dates.max().date() > end
                or observed is not None and dates.max().date() > observed.date()
                or type(attrs.get("session_count")) is not int or attrs["session_count"] != len(frame)):
            raise ValueError("Unverified snapshot sessions")
        values = frame[["Open", "High", "Low", "Close", "Volume"]].astype(float)
        if (not all(math.isfinite(number) for number in values.to_numpy().flat)
                or (values[["Open", "High", "Low", "Close"]] <= 0).any().any()
                or (values["Volume"] < 0).any()
                or (values["High"] < values[["Open", "Low", "Close"]].max(axis=1)).any()
                or (values["Low"] > values[["Open", "High", "Close"]].min(axis=1)).any()):
            raise ValueError("Unverified snapshot prices")
        digest = hashlib.sha256(frame.to_csv(index=False).encode("utf-8")).hexdigest()
        if attrs.get("series_sha256") != digest:
            raise ValueError("Snapshot content hash mismatch")
        if alpaca_metadata:
            from .us_daily_history import _sessions
            from tradingagents.calendar_access import get_exchange_calendar
            required = _sessions(start, end)
            close = get_exchange_calendar("XNYS").session_close(required[-1].isoformat()).to_pydatetime()
            request_end = datetime.fromisoformat(attrs.get("request_end", ""))
            if set(dates.dt.date) != set(required) or request_end != close or observed < close:
                raise ValueError("SIP series coverage or completed-session cutoff mismatch")
        listing = None
        if "listing_contract" in attrs:
            if us_metadata:
                from .security_listing import cutoff_for_day, validate_listing_receipt
            elif kr_metadata or kr_yahoo_metadata:
                from .kr_security_listing import cutoff_for_day, validate_listing_receipt
            else:
                raise ValueError("Listing contract requires a verified market source.")
            if datetime.fromisoformat(attrs["listing_contract"]["analysis_as_of"]) > cutoff_for_day(end_date):
                raise ValueError("Listing receipt exceeds this analysis cutoff.")
            verified = observed
            if kr_metadata or kr_yahoo_metadata:
                verified = datetime.fromisoformat(attrs.get("listing_verified_at", attrs.get("observed_at")))
                if (verified.tzinfo is None or verified > now
                        or observed is not None and observed > verified):
                    raise ValueError("KR identity verification clock is unavailable")
            listing = validate_listing_receipt(symbol, attrs["listing_contract"], requested_start=start.isoformat(),
                                               end_date=end_date, observed_at=verified)
            if (attrs.get("required_start") != listing["required_start"]
                    or dates.min().date().isoformat() != listing["required_start"]
                    or attrs.get("exchange") != listing["reviewed_event"]["exchange"]):
                raise ValueError("Listing contract and snapshot bounds differ.")
        if unknown_yahoo_clock:
            entry.update(reason="price_observation_clock_unverified", provider="yfinance", identity_provider="KIS",
                         identity_verified_at=verified.isoformat(), listing_contract=listing)
            return entry  # Local identity verification does not create a vendor price-collection clock.
        entry.update(status="VERIFIED_RETRIEVED_SERIES", provider=attrs["provider"], exchange=attrs["exchange"],
                     adjustment=attrs["adjustment"], observed_at=observed.isoformat(), requested_start=start.isoformat(),
                     first_session=dates.min().date().isoformat(), last_session=dates.max().date().isoformat(),
                     row_count=len(frame), complete=True, series_sha256=digest)
        if listing is not None:
            entry["listing_contract"] = listing
            if kr_yahoo_metadata:
                entry["price_request_basis"] = verified_yahoo_basis(frame, symbol, start.isoformat(), end_date, as_of=now)
            if kr_metadata or kr_yahoo_metadata:
                entry["identity_provider"] = "KIS"
                entry["identity_verified_at"] = verified.isoformat()
        entry["snapshot_id"] = hashlib.sha256(json.dumps(entry, sort_keys=True).encode()).hexdigest()
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError):
        # Preserve the failed verification without promoting untrusted values
        # to verified evidence, leaking provider payloads, or changing approval.
        entry["reason"] = "snapshot_metadata_or_content_unverified"
    return entry


class DailyHistoryEvidenceRecorder:
    """One ticker's receipts shared by copied child contexts, retained on error."""

    def __init__(self, ticker):
        self.ticker = ticker
        self._entries = {}
        self._lock = Lock()

    def activate(self):
        return _ACTIVE.set(self)

    @staticmethod
    def reset(token):
        _ACTIVE.reset(token)

    def add(self, symbol, end_date, source, frame):
        if symbol != self.ticker:
            return
        with self._lock:
            key = (symbol, end_date, source)
            if key not in self._entries:
                self._entries[key] = _snapshot(symbol, end_date, source, frame)

    def receipt(self):
        with self._lock:
            entries = deepcopy(list(self._entries.values()))
        return {"schema": SCHEMA, "ticker": self.ticker,
                "status": "COLLECTED" if entries else "NOT_COLLECTED", "entries": entries,
                "historical_vintage_verified": False, "limitations": [LIMITATION]}


def record_selected_history(symbol, end_date, source, frame):
    recorder = _ACTIVE.get()
    if recorder is not None:
        recorder.add(symbol, end_date, source, frame)
