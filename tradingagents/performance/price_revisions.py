"""Append-only price attestations for already recorded recommendations."""

from __future__ import annotations

import argparse
from contextlib import closing
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3

from .lifecycle import timestamp
from .price_evidence import PriceReference, native_reference


def initialize_price_revisions(connection):
    connection.execute("""
        CREATE TABLE IF NOT EXISTS action_price_revisions(
            revision_id TEXT PRIMARY KEY, recommendation_id INTEGER NOT NULL,
            parent_id TEXT, recorded_at TEXT NOT NULL,
            reference_json TEXT, source_digest TEXT NOT NULL,
            UNIQUE(recommendation_id, recorded_at)
        )
    """)
    for operation in ("UPDATE", "DELETE"):
        connection.execute(f"""
            CREATE TRIGGER IF NOT EXISTS action_price_revisions_no_{operation.lower()}
            BEFORE {operation} ON action_price_revisions
            BEGIN SELECT RAISE(ABORT, 'Price revision is append-only'); END
        """)


def latest_revision_sql(recommendation_id, cutoff):
    """Shared, correlated point-in-time revision selection in reporting queries."""
    return f"""SELECT q.revision_id FROM main.action_price_revisions q
               WHERE q.recommendation_id = {recommendation_id} AND q.recorded_at <= {cutoff}
               ORDER BY q.recorded_at DESC LIMIT 1"""


def append_price_revision(path: Path, attestation, *, clock=None, apply=False):
    """Preview or append a recommendation-bound reference correction or exclusion.

    The source digest binds the reviewed capture without storing source artifacts
    in the database. The caller is responsible for independent source review.
    An explicit null reference excludes the recommendation from verified scores.
    """
    from .action_outcomes import initialize_action_tracker
    if not path.is_file():
        raise ValueError("An existing reviewed recommendation database is required")
    keys = {"recommendation_id", "run_id", "ticker", "decided_at", "parent_id", "reference", "source_digest"}
    if (not isinstance(attestation, dict) or set(attestation) != keys
            or type(attestation["recommendation_id"]) is not int or attestation["recommendation_id"] < 1
            or not isinstance(attestation["source_digest"], str)
            or not re.fullmatch(r"[a-f0-9]{64}", attestation["source_digest"])):
        raise ValueError("A complete recommendation identity and source content digest are required")
    price = PriceReference.read(attestation["reference"])
    if attestation["reference"] is not None and price is None:
        raise ValueError("Invalid explicit price reference")
    observed_clock = clock() if clock else datetime.now(timezone.utc)
    now = timestamp(observed_clock.isoformat() if isinstance(observed_clock, datetime) else observed_clock)
    decided = timestamp(attestation["decided_at"])
    if decided > now or (price is not None and timestamp(price.observed_at) > decided):
        raise ValueError("Price attestation cannot rely on a future observation")
    payload = dict(attestation, decided_at=decided.isoformat(), reference=asdict(price) if price else None)
    revision_id = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if apply:
        initialize_action_tracker(path)
    connection_path = path.resolve() if apply else path.resolve().as_uri() + "?mode=ro"
    with sqlite3.connect(connection_path, uri=not apply, timeout=30) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("BEGIN IMMEDIATE" if apply else "BEGIN")
        rec = connection.execute("SELECT * FROM action_recommendations WHERE id=?",
                                 (attestation["recommendation_id"],)).fetchone()
        if (rec is None or rec["run_id"] != attestation["run_id"] or rec["ticker"] != attestation["ticker"]
                or timestamp(rec["created_at"]) != decided):
            raise ValueError("Attestation does not match an immutable recommendation")
        if price is not None:
            market = str(rec["market"] or "").strip().upper() if "market" in rec.keys() else None
            admitted, reason = native_reference(payload["reference"], market, rec["created_at"])
            if admitted is None:
                raise ValueError(f"Attested reference could not be verified: {reason}")
        exists = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='action_price_revisions'"
        ).fetchone()
        response = {"recommendation_id": rec["id"], "revision_id": revision_id,
                    "parent_id": attestation["parent_id"], "exclusion": price is None}
        if exists:
            duplicate = connection.execute("SELECT 1 FROM action_price_revisions WHERE revision_id=?", (revision_id,)).fetchone()
            if duplicate:
                return response | {"state": "ALREADY_RECORDED"}
            current = connection.execute(
                "SELECT revision_id,recorded_at FROM action_price_revisions WHERE recommendation_id=? ORDER BY recorded_at DESC LIMIT 1",
                (rec["id"],)
            ).fetchone()
        else:
            current = None
        if (current["revision_id"] if current else None) != attestation["parent_id"]:
            raise ValueError("Price revision parent is stale")
        if current is not None and timestamp(current["recorded_at"]) >= now:
            raise ValueError("Append-only price attestation clock did not advance")
        if apply:
            connection.execute("INSERT INTO action_price_revisions VALUES (?,?,?,?,?,?)",
                               (revision_id, rec["id"], attestation["parent_id"], now.isoformat(),
                                json.dumps(asdict(price), sort_keys=True) if price else None,
                                attestation["source_digest"]))
        return response | {"state": "APPENDED" if apply else "PREVIEW"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path)
    parser.add_argument("attestation", type=Path)
    parser.add_argument("proof", type=Path)
    parser.add_argument("--revised-copy", type=Path)
    args = parser.parse_args(argv)
    attestation = json.loads(args.attestation.read_text(encoding="utf-8-sig"))
    with args.proof.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    if not isinstance(attestation, dict) or attestation.get("source_digest") != digest:
        raise ValueError("Price attestation source digest disagrees with the reviewed evidence")
    preview = append_price_revision(args.database, attestation)
    if args.revised_copy is None:
        print(json.dumps(preview, sort_keys=True))
        return 0
    # Reserve a new file. The reviewed source is always opened read-only.
    with args.revised_copy.open("xb"):
        pass
    uri = args.database.resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as source, closing(sqlite3.connect(args.revised_copy)) as clone:
        source.backup(clone)
        if clone.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
            raise ValueError("Revised copy does not pass SQLite integrity validation")
    result = append_price_revision(args.revised_copy, attestation, apply=True)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
