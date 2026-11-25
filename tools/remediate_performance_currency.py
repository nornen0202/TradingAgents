"""Audit and remediate legacy KRW-polluted US rows in performance.sqlite."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sqlite3
from typing import Any


def remediate_performance_currency(
    db_path: Path,
    *,
    apply: bool = False,
    backup_path: Path | None = None,
) -> dict[str, Any]:
    db_path = Path(db_path)
    if not db_path.is_file():
        raise FileNotFoundError(f"Database not found: {db_path}")

    with sqlite3.connect(db_path, timeout=60) as conn:
        conn.row_factory = sqlite3.Row
        corrupted = list(
            conn.execute(
                """
                SELECT o.rowid AS outcome_rowid,
                       o.recommendation_id,
                       r.ticker,
                       r.market,
                       r.recommended_price,
                       o.return_1d,
                       o.return_5d,
                       o.return_20d,
                       o.outcome_label
                FROM action_outcomes o
                JOIN action_recommendations r ON r.id = o.recommendation_id
                WHERE COALESCE(o.outcome_label, '') != 'invalidated_currency_mismatch'
                  AND (
                    COALESCE(UPPER(TRIM(r.market)), '') = 'US'
                    OR (
                      COALESCE(TRIM(r.market), '') = ''
                      AND r.ticker NOT LIKE '%.KS'
                      AND r.ticker NOT LIKE '%.KQ'
                      AND r.ticker GLOB '[A-Za-z]*'
                    )
                  )
                  AND r.recommended_price >= 10000
                  AND (
                    COALESCE(o.return_1d, 0.0) <= -0.95
                    OR COALESCE(o.return_5d, 0.0) <= -0.95
                    OR COALESCE(o.return_20d, 0.0) <= -0.95
                  )
                """
            )
        )
        recommendation_ids = sorted({int(row["recommendation_id"]) for row in corrupted})
        outcome_rowids = sorted({int(row["outcome_rowid"]) for row in corrupted})
        by_ticker: dict[str, int] = {}
        for row in corrupted:
            ticker = str(row["ticker"] or "UNKNOWN").upper()
            by_ticker[ticker] = by_ticker.get(ticker, 0) + 1

    receipt: dict[str, Any] = {
        "db_path": str(db_path),
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "mode": "apply" if apply else "dry_run",
        "corrupted_outcome_rows": len(outcome_rowids),
        "corrupted_recommendation_ids": len(recommendation_ids),
        "by_ticker": dict(sorted(by_ticker.items())),
        "backup_path": str(backup_path) if backup_path else None,
        "remediated_outcome_rows": 0,
        "cleared_recommended_prices": 0,
    }
    if not apply or not outcome_rowids:
        return receipt

    if backup_path is not None:
        backup_path = Path(backup_path)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(db_path, timeout=60) as src, sqlite3.connect(backup_path, timeout=60) as dst:
            src.backup(dst)
        if not backup_path.is_file() or backup_path.stat().st_size == 0:
            shutil.copy2(db_path, backup_path)

    with sqlite3.connect(db_path, timeout=60) as conn:
        conn.execute("BEGIN IMMEDIATE")
        chunk_size = 500
        updated_outcomes = 0
        for index in range(0, len(outcome_rowids), chunk_size):
            batch = outcome_rowids[index : index + chunk_size]
            placeholders = ",".join("?" for _ in batch)
            cur = conn.execute(
                f"""
                UPDATE action_outcomes
                SET outcome_label = 'invalidated_currency_mismatch',
                    return_1d = NULL,
                    return_3d = NULL,
                    return_5d = NULL,
                    return_10d = NULL,
                    return_20d = NULL,
                    return_60d = NULL,
                    benchmark_excess_5d = NULL,
                    benchmark_excess_20d = NULL,
                    benchmark_excess_60d = NULL,
                    max_drawdown_20d = NULL,
                    max_favorable_excursion_20d = NULL,
                    avoided_drawdown_20d = NULL,
                    missed_upside_20d = NULL
                WHERE rowid IN ({placeholders})
                """,
                batch,
            )
            updated_outcomes += int(cur.rowcount or 0)

        cleared_recs = 0
        for index in range(0, len(recommendation_ids), chunk_size):
            batch = recommendation_ids[index : index + chunk_size]
            placeholders = ",".join("?" for _ in batch)
            cur = conn.execute(
                f"""
                UPDATE action_recommendations
                SET recommended_price = NULL
                WHERE id IN ({placeholders})
                  AND price_reference_json IS NULL
                """,
                batch,
            )
            cleared_recs += int(cur.rowcount or 0)
        conn.commit()

    receipt["remediated_outcome_rows"] = updated_outcomes
    receipt["cleared_recommended_prices"] = cleared_recs
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, required=True, help="Path to performance.sqlite")
    parser.add_argument("--backup", type=Path, default=None, help="Backup path before --apply")
    parser.add_argument("--apply", action="store_true", help="Apply remediation in-place")
    args = parser.parse_args()
    result = remediate_performance_currency(args.db, apply=args.apply, backup_path=args.backup)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
