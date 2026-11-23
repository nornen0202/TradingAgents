"""Read-only currency diagnostics for an isolated performance ledger copy."""

import argparse
import json
from pathlib import Path
import sqlite3


def audit_snapshot(db_path: Path) -> dict:
    with sqlite3.connect(db_path.resolve(strict=True).as_uri() + "?mode=ro", uri=True) as conn:
        conn.execute("BEGIN")
        columns = {row[1] for row in conn.execute("PRAGMA table_info(action_recommendations)")}
        if not {"market", "recommended_price"} <= columns:
            raise ValueError("Unsupported recommendation schema")
        metrics = conn.execute("""
            SELECT CASE WHEN upper(r.market) IN ('US', 'KR') THEN upper(r.market)
                        WHEN coalesce(trim(r.market), '') = '' THEN 'UNKNOWN'
                        ELSE 'OTHER' END AS market_bucket,
                   COUNT(DISTINCT r.id),
                   COUNT(DISTINCT CASE WHEN r.recommended_price IS NOT NULL THEN r.id END),
                   COUNT(DISTINCT CASE WHEN r.recommended_price IS NOT NULL
                                      AND o.return_5d BETWEEN -1 AND -0.99 THEN r.id END)
            FROM action_recommendations r
            LEFT JOIN action_outcomes o ON o.recommendation_id = r.id
            GROUP BY market_bucket
        """).fetchall()
        labels = ("recommendations", "priced_recommendations", "extreme_legacy_return_candidates")
        return {
            "measurement_scope": "aggregate_screening_only",
            "markets": {
                market: dict(zip(labels, counts))
                for market, *counts in metrics
            },
            "explicit_reference_column_exists": "price_reference_json" in columns,
            "candidate_count_proves_currency_mismatch": False,
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(audit_snapshot(args.snapshot), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
