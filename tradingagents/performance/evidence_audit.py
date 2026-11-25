"""Read-only diagnostics for a SQLite performance snapshot; emits aggregate evidence only."""

import argparse
from collections import Counter
from contextlib import closing
import json
from pathlib import Path
import sqlite3

from .price_evidence import PriceReference, native_reference


def _market(value):
    normalized = str(value or "").strip().upper()
    return normalized if normalized in {"US", "KR"} else ("OTHER" if normalized else "UNKNOWN")


def _classification(price, raw, market, decided_at, suspected):
    try:
        payload = json.loads(raw) if raw else None
    except (TypeError, ValueError):
        payload = None
    reference, state = native_reference(payload, market, decided_at)
    if reference and price == reference.price:
        return "native_unit_supported"
    if reference:
        return "recovery_reference_available"
    explicit = PriceReference.read(payload)
    if explicit and state == "currency_mismatch" and explicit.price == price:
        return "explicit_currency_mismatch"
    return "suspected_only" if suspected else "unverified"


def audit_snapshot(db_path: Path) -> dict:
    with closing(sqlite3.connect(db_path.resolve(strict=True).as_uri() + "?mode=ro", uri=True)) as conn:
        conn.execute("PRAGMA mmap_size=536870912")
        conn.execute("BEGIN")
        columns = {row[1] for row in conn.execute("PRAGMA table_info(action_recommendations)")}
        if not {"market", "recommended_price", "created_at"} <= columns:
            raise ValueError("Unsupported recommendation schema")
        has_reference = "price_reference_json" in columns
        reference_sql = "r.price_reference_json" if has_reference else "NULL"
        candidates = {row[0] for row in conn.execute(
            "SELECT recommendation_id FROM action_outcomes WHERE return_5d BETWEEN -1 AND -0.99"
        )}
        totals, classes, recent_outcomes, recent_recommendations = {}, Counter(), Counter(), Counter()
        for market_raw, decided_at, price, raw, recommendation_id in conn.execute(f"""
            SELECT r.market, r.created_at, r.recommended_price, {reference_sql}, r.id
            FROM action_recommendations r ORDER BY r.id DESC
        """):
            market = _market(market_raw)
            tally = totals.setdefault(market, Counter())
            tally["recommendations"] += 1
            priced = price is not None
            suspicious = isinstance(price, (int, float)) and price > 0 and recommendation_id in candidates
            tally["priced_recommendations"] += priced
            tally["extreme_legacy_return_candidates"] += suspicious
            if priced or raw:
                classes[_classification(price, raw, market, decided_at, suspicious)] += 1
            if recent_recommendations["rows"] < 40_000:
                recent_recommendations["rows"] += 1
                if suspicious:
                    recent_recommendations[f"candidates_{market}"] += 1

        recent_by_timestamp = Counter()
        for order, sample in (("rowid DESC", recent_outcomes), ("updated_at DESC, rowid DESC", recent_by_timestamp)):
            for market, price, ret in conn.execute(f"""
                SELECT r.market, r.recommended_price, recent.return_5d
                FROM (SELECT recommendation_id, return_5d FROM action_outcomes ORDER BY {order} LIMIT 40000) recent
                LEFT JOIN action_recommendations r ON r.id=recent.recommendation_id
            """):
                sample["rows"] += 1
                sample["rows_with_5d_return"] += ret is not None
                if isinstance(price, (int, float)) and price > 0 and ret is not None and -1 <= ret <= -.99:
                    sample[f"candidates_{_market(market)}"] += 1
        return {
            "measurement_scope": "aggregate_screening_only",
            "markets": {market: dict(counts) for market, counts in totals.items()},
            "evidence_classifications_for_priced_or_referenced_rows": dict(classes),
            "recent_40000_by_outcome_insertion": dict(recent_outcomes),
            "recent_40000_by_outcome_timestamp": dict(recent_by_timestamp),
            "recent_40000_by_recommendation_id": dict(recent_recommendations),
            "explicit_reference_column_exists": has_reference,
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
