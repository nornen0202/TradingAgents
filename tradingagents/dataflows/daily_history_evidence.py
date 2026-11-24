"""Allowlisted provenance receipts, independent of tool text and mutable frames."""
from __future__ import annotations

from contextlib import closing
from contextvars import ContextVar
from copy import deepcopy
from datetime import date, datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sqlite3
from threading import Lock

import pandas as pd


SCHEMA = "tradingagents.daily-history-evidence/v1"
LIMITATION = "Retrieved adjusted prices are not a verified historical snapshot vintage."
_ACTIVE = ContextVar("daily_history_evidence", default=None)
_CAPTURE_APPLICATION = 0x54414843


def _day(value):
    if not isinstance(value, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
        raise ValueError("Unverified session date")
    return date.fromisoformat(value)


def _snapshot(symbol, end_date, source, frame):
    return _snapshot_with_series(symbol, end_date, source, frame)[0]


def _snapshot_identity(entry):
    doc = {k: v for k, v in entry.items() if k not in ("snapshot_id", "forward_capture")}
    return hashlib.sha256(json.dumps(doc, sort_keys=True).encode()).hexdigest()


def _series_dates_and_values(frame, end):
    dates = pd.to_datetime(frame["Date"], errors="raise")
    if (dates.isna().any() or dates.dt.tz is not None or dates.duplicated().any()
            or not dates.is_monotonic_increasing or (dates != dates.dt.normalize()).any()
            or dates.max().date() > end):
        raise ValueError("Unverified snapshot sessions")
    values = frame[["Open", "High", "Low", "Close", "Volume"]].astype(float)
    if (not all(math.isfinite(number) for number in values.to_numpy().flat)
            or (values[["Open", "High", "Low", "Close"]] <= 0).any().any()
            or (values["Volume"] < 0).any()
            or (values["High"] < values[["Open", "Low", "Close"]].max(axis=1)).any()
            or (values["Low"] > values[["Open", "High", "Close"]].min(axis=1)).any()):
        raise ValueError("Unverified snapshot prices")
    return dates


def _terms(entry, *, price_currency=None, currency_basis=None):
    entry.update(native_currency=None, price_currency=price_currency, currency_basis=currency_basis, source_event_at=None)
    missing = ["native_currency", "source_event_at"]
    missing.extend(term for term in ("price_currency", "observed_at", "exchange", "adjustment") if not entry.get(term))
    entry["unverified_fields"] = missing
    return entry


def _retain_yahoo(entry, frame, end, now):
    """Retain the admitted OHLCV input even when Yahoo cannot prove its vintage."""
    start = _day(frame.attrs["requested_start"])
    if _day(frame.attrs["requested_end"]) != end:
        raise ValueError("Snapshot date bounds mismatch")
    dates = _series_dates_and_values(frame, end)
    if dates.min().date() < start:
        raise ValueError("Snapshot starts before the requested range")
    observed_text = frame.attrs.get("research_yahoo_download_observed_at")
    observed = datetime.fromisoformat(observed_text) if observed_text else None
    if observed is not None and (observed.utcoffset() is None or observed > now or dates.max().date() > observed.date()):
        observed = None
    series = frame[["Date", "Open", "High", "Low", "Close", "Volume"]].to_csv(index=False).encode("utf-8")
    entry.update(reason="selected_yahoo_input_without_full_provider_provenance", provider="yfinance",
                 input_origin="fresh_download" if observed else
                 ("local_csv_cache" if frame.attrs.get("research_yahoo_cache_read") is True else "unverified"),
                 observed_at=observed.isoformat() if observed else None, exchange=None,
                 adjustment="yfinance.download(auto_adjust=True)" if observed else None,
                 requested_start=start.isoformat(), first_session=dates.min().date().isoformat(),
                 last_session=dates.max().date().isoformat(), row_count=len(frame),
                 series_sha256=hashlib.sha256(series).hexdigest())
    _terms(entry)
    entry["snapshot_id"] = _snapshot_identity(entry)
    return entry, series


def _snapshot_with_series(symbol, end_date, source, frame):
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
            return _terms(entry), None
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
        if source == "yfinance" and not kr_yahoo_metadata:
            return _retain_yahoo(entry, frame, end, now)
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
        dates = _series_dates_and_values(frame, end)
        if (dates.min().date() < start or observed is not None and dates.max().date() > observed.date()
                or type(attrs.get("session_count")) is not int or attrs["session_count"] != len(frame)):
            raise ValueError("Unverified snapshot sessions")
        if set(frame.columns) != {"Date", "Open", "High", "Low", "Close", "Volume"}:
            raise ValueError("Unverified snapshot columns")
        series_bytes = frame.to_csv(index=False).encode("utf-8")
        digest = hashlib.sha256(series_bytes).hexdigest()
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
            return _terms(entry), None  # Local identity verification does not create a vendor price-collection clock.
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
        explicit_price_currency = "USD" if alpaca_metadata and attrs.get("price_currency") == "USD" else None
        _terms(entry, price_currency=explicit_price_currency,
               currency_basis="explicit_provider_request" if explicit_price_currency else None)
        entry["snapshot_id"] = _snapshot_identity(entry)
        return entry, series_bytes
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError):
        # Preserve the failed verification without promoting untrusted values
        # to verified evidence, leaking provider payloads, or changing approval.
        entry["reason"] = "snapshot_metadata_or_content_unverified"
    return _terms(entry), None


class DailyHistoryCapture:
    """Retain the exact verified series and its acquisition receipt locally."""

    def __init__(self, path: Path, run_id: str):
        self.path = Path(path)
        self.run_id = run_id

    def append(self, entry, series):
        now = datetime.now(timezone.utc)
        observed = datetime.fromisoformat(entry["observed_at"]) if entry.get("observed_at") else None
        if (hashlib.sha256(series).hexdigest() != entry["series_sha256"]
                or _snapshot_identity(entry) != entry["snapshot_id"]
                or observed is not None and (observed.utcoffset() is None or observed > now)):
            raise ValueError("Series and acquisition clock must match the receipt")
        encoded = json.dumps({k: v for k, v in entry.items() if k != "forward_capture"}, sort_keys=True, ensure_ascii=False)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass
        else:
            os.close(fd)
        db = sqlite3.connect(self.path, timeout=5)
        try:
            with db:
                db.execute("BEGIN IMMEDIATE")
                application = db.execute("PRAGMA application_id").fetchone()[0]
                if application != _CAPTURE_APPLICATION:
                    if application or db.execute("SELECT 1 FROM sqlite_master LIMIT 1").fetchone():
                        raise ValueError("Capture database must use a dedicated file")
                    db.execute(f"PRAGMA application_id = {_CAPTURE_APPLICATION}")
                db.execute("""CREATE TABLE IF NOT EXISTS daily_history_captures(
                    run_id TEXT NOT NULL, snapshot_id TEXT NOT NULL, captured_at TEXT NOT NULL,
                    receipt TEXT NOT NULL, series BLOB NOT NULL, PRIMARY KEY(run_id, snapshot_id)
                )""")
                db.execute("""CREATE TRIGGER IF NOT EXISTS daily_history_no_update
                    BEFORE UPDATE ON daily_history_captures BEGIN SELECT RAISE(ABORT, 'Capture is append-only'); END""")
                db.execute("""CREATE TRIGGER IF NOT EXISTS daily_history_no_delete
                    BEFORE DELETE ON daily_history_captures BEGIN SELECT RAISE(ABORT, 'Capture is append-only'); END""")
                prior = db.execute("SELECT receipt, series FROM daily_history_captures WHERE run_id=? AND snapshot_id=?",
                                   (self.run_id, entry["snapshot_id"])).fetchone()
                if prior is None:
                    db.execute("INSERT INTO daily_history_captures VALUES (?,?,?,?,?)",
                               (self.run_id, entry["snapshot_id"], now.isoformat(), encoded, series))
                elif prior != (encoded, series):
                    raise ValueError("Existing capture differs from the verified snapshot")
        finally:
            db.close()


    def read_snapshot(self, snapshot_id):
        """Return one run-owned receipt and its exact retained research bytes."""
        if not isinstance(snapshot_id, str) or not re.fullmatch(r"[0-9a-f]{64}", snapshot_id):
            raise ValueError("Invalid snapshot ID")
        with closing(sqlite3.connect(self.path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
            if db.execute("PRAGMA application_id").fetchone()[0] != _CAPTURE_APPLICATION:
                raise ValueError("Not a daily history capture database")
            row = db.execute("SELECT receipt, series FROM daily_history_captures WHERE run_id=? AND snapshot_id=?",
                             (self.run_id, snapshot_id)).fetchone()
        if row is None:
            return None
        receipt, series = json.loads(row[0]), row[1]
        if (receipt["snapshot_id"] != snapshot_id or _snapshot_identity(receipt) != snapshot_id
                or hashlib.sha256(series).hexdigest() != receipt["series_sha256"]):
            raise ValueError("Stored snapshot does not match its receipt")
        return receipt, series

class DailyHistoryEvidenceRecorder:
    """One ticker's receipts shared by copied child contexts, retained on error."""

    def __init__(self, ticker, *, capture=None):
        self.ticker = ticker
        self._capture = capture
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
            prior = self._entries.get(key)
            if prior is not None and prior.get("forward_capture") != "WRITE_FAILED":
                return
            entry, series = _snapshot_with_series(symbol, end_date, source, frame)
            if prior is not None and entry.get("snapshot_id") != prior["snapshot_id"]:
                return
            if self._capture is not None and series is not None:
                try:
                    self._capture.append(entry, series)
                    entry["forward_capture"] = "STORED"
                except (OSError, sqlite3.Error, ValueError):
                    entry["forward_capture"] = "WRITE_FAILED"
            self._entries[key] = entry

    def ledger_reference(self, run_id):
        receipt = self.receipt()
        return {**receipt, "run_id": run_id, "scope": "RESEARCH_ONLY"}

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
