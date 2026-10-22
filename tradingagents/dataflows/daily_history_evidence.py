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
        from .kr_daily_history import SOURCE as KR_SOURCE

        attrs = frame.attrs
        us_metadata = source == SOURCE and attrs.get("adjustment") == "MODP=1" and attrs.get("exchange") in {"NAS", "NYS", "AMS"}
        kr_metadata = (source == KR_SOURCE and re.fullmatch(r"[0-9]{6}\.(KS|KQ)", symbol) is not None
                       and attrs.get("adjustment") == "FID_ORG_ADJ_PRC=0" and attrs.get("exchange") == "KRX")
        if (not (us_metadata or kr_metadata) or attrs.get("source") != source
                or attrs.get("provider") != "kis" or attrs.get("complete") is not True):
            raise ValueError("Unverified provider metadata")
        start = _day(attrs.get("requested_start"))
        if _day(attrs.get("requested_end")) != end or start > end:
            raise ValueError("Snapshot date bounds mismatch")
        observed = datetime.fromisoformat(str(attrs.get("observed_at")).replace("Z", "+00:00"))
        if observed.tzinfo is None or observed.utcoffset() is None or observed > now:
            raise ValueError("Unverified observation clock")
        dates = pd.to_datetime(frame["Date"], errors="raise")
        if (dates.isna().any() or dates.dt.tz is not None or dates.duplicated().any()
                or not dates.is_monotonic_increasing or (dates != dates.dt.normalize()).any()
                or dates.min().date() < start or dates.max().date() > end
                or dates.max().date() > observed.date()
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
        entry.update(status="VERIFIED_RETRIEVED_SERIES", provider="kis", exchange=attrs["exchange"],
                     adjustment=attrs["adjustment"], observed_at=observed.isoformat(), requested_start=start.isoformat(),
                     first_session=dates.min().date().isoformat(), last_session=dates.max().date().isoformat(),
                     row_count=len(frame), complete=True, series_sha256=digest)
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
