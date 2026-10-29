"""Immutable evidence linking recommendations, order intents and observed fills.

This journal shares the existing SQLite stores. It never sends orders. Timestamps
separate event occurrence, observation, confirmation and settlement.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
import re
from pathlib import Path
import sqlite3
from typing import Any, Mapping


KINDS = {"SIGNAL", "INTENT", "FILL", "CANCEL", "OUTCOME", "RETROSPECTIVE", "RETROSPECTIVE_ALLOCATION", "ACCOUNT_SEED"}
MODES = {"recommendation", "paper", "demo", "actual"}


def timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or "T" not in value:
        raise ValueError("Explicit timezone-aware timestamp required")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("Invalid lifecycle timestamp") from None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Timezone-aware timestamp required")
    return parsed.astimezone(timezone.utc)


def stable_signal_id(run_id: str, ticker: str, action: str, source: str = "TradingAgents") -> str:
    if any(not isinstance(value, str) for value in (run_id, ticker, action, source)):
        raise ValueError("Signal identity fields must be nonempty strings")
    values = [str(v).strip() for v in (run_id, ticker, action, source)]
    if not all(values):
        raise ValueError("Signal requires run, ticker, action and source")
    values[1] = values[1].upper()
    return "signal:" + hashlib.sha256(json.dumps(values, ensure_ascii=False).encode()).hexdigest()


def initialize_lifecycle(conn: sqlite3.Connection) -> None:
    conn.execute("""CREATE TABLE IF NOT EXISTS lifecycle_events(
        event_id TEXT PRIMARY KEY, signal_id TEXT NOT NULL, intent_id TEXT,
        kind TEXT NOT NULL, mode TEXT NOT NULL, occurred_at TEXT NOT NULL,
        available_at TEXT NOT NULL, confirmed_at TEXT, settled_at TEXT,
        payload_json TEXT NOT NULL, ingested_at TEXT)""")
    columns = {row[1] for row in conn.execute("PRAGMA table_info(lifecycle_events)")}
    if "ingested_at" not in columns:
        conn.execute("ALTER TABLE lifecycle_events ADD COLUMN ingested_at TEXT")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lifecycle_signal ON lifecycle_events(signal_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lifecycle_kind ON lifecycle_events(kind)")
    conn.execute("""CREATE INDEX IF NOT EXISTS idx_lifecycle_ticker ON lifecycle_events(
        CASE WHEN json_valid(payload_json) THEN upper(json_extract(payload_json, '$.ticker')) END)""")
    conn.execute("""CREATE TRIGGER IF NOT EXISTS lifecycle_no_update BEFORE UPDATE ON lifecycle_events
        BEGIN SELECT RAISE(ABORT, 'Lifecycle evidence is immutable'); END""")
    conn.execute("""CREATE TRIGGER IF NOT EXISTS lifecycle_no_delete BEFORE DELETE ON lifecycle_events
        BEGIN SELECT RAISE(ABORT, 'Lifecycle evidence is immutable'); END""")


def _number(value: Any, *, positive: bool = False) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and (value > 0 if positive else value >= 0))


def validate_event(event: Mapping[str, Any]) -> None:
    if event.get("kind") not in KINDS or event.get("mode") not in MODES:
        raise ValueError("Unsupported lifecycle kind or execution mode")
    if not event.get("event_id") or not event.get("signal_id"):
        raise ValueError("Stable event and signal IDs required")
    occurred, available = timestamp(event["occurred_at"]), timestamp(event["available_at"])
    ingested = timestamp(event.get("ingested_at"))
    if ingested < occurred:
        raise ValueError("Ingestion cannot precede occurrence")
    if occurred > available:
        raise ValueError("Evidence cannot be available before it occurs")
    for clock in ("confirmed_at", "settled_at"):
        if event.get(clock) is not None and timestamp(event[clock]) < occurred:
            raise ValueError("Confirmation/settlement cannot precede event")
    kind, payload = event["kind"], event["payload"]
    if not isinstance(payload, Mapping):
        raise ValueError("Lifecycle payload must be an object")
    if kind in {"FILL", "OUTCOME", "RETROSPECTIVE", "RETROSPECTIVE_ALLOCATION"}:
        timestamp(event.get("confirmed_at"))
    if kind in {"FILL", "RETROSPECTIVE", "RETROSPECTIVE_ALLOCATION"}:
        timestamp(event.get("settled_at"))
    if kind in {"INTENT", "FILL", "CANCEL"} and not event.get("intent_id"):
        raise ValueError("Order evidence requires intent ID")
    if kind == "FILL":
        if (payload.get("side") not in {"BUY", "SELL"} or not payload.get("ticker")
                or not _number(payload.get("quantity"), positive=True)
                or not _number(payload.get("price"), positive=True)
                or not _number(payload.get("cost"))):
            raise ValueError("Fill requires positive quantity/price, side, ticker and explicit nonnegative costs")
        if event["mode"] == "recommendation":
            raise ValueError("A recommendation is not a fill")
        currency = payload.get("currency")
        if not isinstance(currency, str) or len(currency) != 3 or not currency.isascii() or not currency.isalpha() or not currency.isupper():
            raise ValueError("Explicit three-letter fill currency required")
    if kind == "ACCOUNT_SEED":
        if (not _number(payload.get("cash")) or not isinstance(payload.get("positions", {}), Mapping)
                or any(not _number(quantity) for quantity in payload.get("positions", {}).values())):
            raise ValueError("Account seed requires finite cash and nonnegative quantities")
    if kind == "RETROSPECTIVE_ALLOCATION":
        if (event["mode"] == "recommendation" or payload.get("schema") != "tradingagents.fifo-allocation/v1"
                or payload.get("algorithm") != "FIFO_INCREMENTAL_FILL_COSTS/v1"
                or not isinstance(payload.get("ticker"), str) or not payload["ticker"]
                or not isinstance(payload.get("exit_fill_id"), str) or not payload["exit_fill_id"]
                or not re.fullmatch(r"[A-Z]{3}", str(payload.get("currency", "")))
                or not re.fullmatch(r"[0-9a-f]{64}", str(payload.get("content_hash", "")))
                or "previous_revision_id" not in payload
                or (payload["previous_revision_id"] is not None and
                    (not isinstance(payload["previous_revision_id"], str) or not payload["previous_revision_id"]))):
            raise ValueError("Explicit allocation revision identity required")
        for key in ("review_ids", "input_event_ids"):
            values = payload.get(key)
            if (not isinstance(values, list) or any(not isinstance(value, str) or not value for value in values)
                    or len(values) != len(set(values))):
                raise ValueError("Unique allocation evidence references required")
        if (payload["exit_fill_id"] not in payload["input_event_ids"]
                or timestamp(payload.get("input_as_of")) > available
                or max(timestamp(event[k]) for k in ("occurred_at", "confirmed_at", "settled_at")) > available
                or available > ingested):
            raise ValueError("Allocation revision cannot precede its outcome evidence")
    json.dumps(dict(payload), allow_nan=False)


def append_lifecycle_event(
    db: Path | str | sqlite3.Connection, *, event_id: str, signal_id: str,
    kind: str, occurred_at: str, available_at: str, payload: Mapping[str, Any],
    intent_id: str | None = None, mode: str = "recommendation",
    confirmed_at: str | None = None, settled_at: str | None = None,
    ingested_at: str | None = None,
) -> bool:
    """Identical retries are no-ops; conflicting IDs fail closed.

    An existing connection participates in its transaction without committing.
    A path opens a local transaction and never a broker connection.
    """
    event = dict(event_id=event_id, signal_id=signal_id, intent_id=intent_id, kind=kind,
                 mode=mode, occurred_at=occurred_at, available_at=available_at,
                 confirmed_at=confirmed_at, settled_at=settled_at,
                 ingested_at=ingested_at if ingested_at is not None else datetime.now(timezone.utc).isoformat(), payload=dict(payload))
    validate_event(event)
    encoded = json.dumps(event.pop("payload"), sort_keys=True, ensure_ascii=False, allow_nan=False)
    values = (*event.values(), encoded)
    if not isinstance(db, sqlite3.Connection):
        path = Path(db)
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as conn:
            return _append(conn, values)
    return _append(db, values)


def _append(conn: sqlite3.Connection, values: tuple) -> bool:
    initialize_lifecycle(conn)
    columns = "event_id,signal_id,intent_id,kind,mode,occurred_at,available_at,confirmed_at,settled_at,ingested_at,payload_json"
    previous = conn.execute(f"SELECT {columns} FROM lifecycle_events WHERE event_id=?", (values[0],)).fetchone()
    if previous:
        # A retry observes the same receipt later; preserve the first ingestion
        # time without allowing it to be rewritten or backdated.
        if tuple(previous)[:9] + tuple(previous)[10:] != values[:9] + values[10:]:
            raise ValueError("Lifecycle event ID reused with different evidence")
        return False
    if values[3] == "FILL":
        payload = json.loads(values[10])
        intent = conn.execute("SELECT signal_id,mode,payload_json,occurred_at FROM lifecycle_events WHERE kind='INTENT' AND intent_id=? AND mode=?", (values[2], values[4])).fetchone()
        if intent is None or intent[0] != values[1]:
            raise ValueError("Fill requires a matching immutable order intent")
        intent_payload = json.loads(intent[2])
        if (intent_payload.get("side") != payload["side"] or intent_payload.get("ticker") != payload["ticker"]
                or not _number(intent_payload.get("quantity"), positive=True)):
            raise ValueError("Fill does not match order terms")
        if timestamp(values[5]) < timestamp(intent[3]):
            raise ValueError("Fill cannot precede order intent")
        prior = conn.execute("SELECT payload_json FROM lifecycle_events WHERE kind='FILL' AND intent_id=? AND mode=?", (values[2], values[4])).fetchall()
        filled = sum(json.loads(row[0])["quantity"] for row in prior)
        if filled + payload["quantity"] > intent_payload["quantity"] + 1e-9:
            raise ValueError("Incremental fills exceed requested quantity")
    conn.execute(f"INSERT INTO lifecycle_events({columns}) VALUES (?,?,?,?,?,?,?,?,?,?,?)", values)
    return True
