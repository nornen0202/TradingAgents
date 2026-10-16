"""Import explicit local broker execution evidence without broker connectivity.

Input is {recommendation: {...}, receipt: {...}}, or {entries: [that, ...]}.
--as-of filters source evidence; ingestion is stamped at the actual import time.
Use ``python -m tools.import_execution_receipts --help`` from the repository.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Any, Mapping

from tradingagents.performance.action_outcomes import record_execution_receipt, record_recommendation_evidence
from tradingagents.performance.lifecycle import stable_signal_id, timestamp


def _entries(payload: Any, *, as_of: str) -> list[tuple[dict, dict]]:
    cutoff = timestamp(as_of)
    raw_entries = payload.get("entries") if isinstance(payload, Mapping) and "entries" in payload else [payload]
    if not isinstance(raw_entries, list) or not raw_entries:
        raise ValueError("Input must contain at least one recommendation/receipt entry")
    result = []
    for index, entry in enumerate(raw_entries):
        if not isinstance(entry, Mapping) or not isinstance(entry.get("recommendation"), Mapping) or not isinstance(entry.get("receipt"), Mapping):
            raise ValueError(f"Entry {index} requires recommendation and receipt objects")
        row, receipt = dict(entry["recommendation"]), dict(entry["receipt"])
        for key in ("run_id", "ticker", "action"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError(f"Entry {index}: recommendation requires {key}")
        row["ticker"] = row["ticker"].strip().upper()
        clocks = [row.get("created_at")]
        clocks.extend(receipt.get(key) for key in ("intent_at", "executed_at", "confirmed_at", "settled_at"))
        clocks.extend(receipt[key] for key in ("available_at", "intent_available_at", "observed_at", "received_at", "ingested_at", "evaluated_at") if key in receipt)
        if any(timestamp(value) > cutoff for value in clocks):
            raise ValueError(f"Entry {index}: future execution evidence is not allowed by --as-of")
        result.append((row, receipt))
    return result


def _write_batch(conn: sqlite3.Connection, entries: list[tuple[dict, dict]], *, ingested_at: str) -> int:
    inserted = 0
    for row, receipt in entries:
        # Preserve optional evidence already stored with the recommendation.
        # An import may provide a compact identity plus its execution receipt.
        if conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='lifecycle_events'").fetchone():
            signal_id = stable_signal_id(row["run_id"], row["ticker"], row["action"], row.get("source") or "TradingAgents")
            previous = conn.execute("SELECT payload_json FROM lifecycle_events WHERE event_id=?", (signal_id,)).fetchone()
            if previous:
                row = {**json.loads(previous[0]), **row}
        record_recommendation_evidence(conn, row, ingested_at=ingested_at)
        inserted += int(record_execution_receipt(conn, row=row, receipt=receipt, recorded_at=ingested_at, strict=True))
    return inserted


def import_receipts(db_path: Path, payload: Any, *, as_of: str) -> dict[str, Any]:
    """Validate the whole batch in memory before opening the destination file."""
    entries = _entries(payload, as_of=as_of)
    ingested_at = datetime.now(timezone.utc).isoformat()
    if timestamp(as_of) > timestamp(ingested_at):
        raise ValueError("--as-of cannot be later than the actual import time")
    with sqlite3.connect(":memory:") as preflight:
        _write_batch(preflight, entries, ingested_at=ingested_at)
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path, isolation_level=None, timeout=20) as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            inserted = _write_batch(conn, entries, ingested_at=ingested_at)
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
    return {"status": "imported", "entries": len(entries), "inserted_fills": inserted,
            "duplicate_fills": len(entries) - inserted, "analysis_as_of": as_of,
            "ingested_at": ingested_at, "broker_orders_sent": 0}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--as-of", required=True, help="Timezone-aware source evidence cutoff")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8-sig"))
        result = import_receipts(args.db, payload, as_of=args.as_of)
    except (ValueError, KeyError, TypeError, sqlite3.DatabaseError) as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
