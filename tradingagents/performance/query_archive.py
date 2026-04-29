from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

from .action_outcomes import initialize_action_tracker


def query_archive(
    *,
    db_path: Path,
    query: str | None = None,
    ticker: str | None = None,
    action: str | None = None,
) -> list[dict[str, Any]]:
    initialize_action_tracker(db_path)
    clauses: list[str] = []
    params: list[Any] = []
    if ticker:
        clauses.append("ticker = ?")
        params.append(ticker.upper())
    if action:
        clauses.append("action = ?")
        params.append(action.upper())
    if query:
        clauses.append("(ticker LIKE ? OR action LIKE ? OR COALESCE(skip_reason, '') LIKE ? OR COALESCE(prism_agreement, '') LIKE ?)")
        token = f"%{query}%"
        params.extend([token, token, token, token])
    sql = "SELECT * FROM action_recommendations"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY created_at DESC LIMIT 50"
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute(sql, params)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Query TradingAgents recommendation archive.")
    parser.add_argument("--db", default="archive/performance.sqlite", help="Path to performance SQLite DB.")
    parser.add_argument("--query", help="Free-text query over ticker/action/skip reason/PRISM agreement.")
    parser.add_argument("--ticker", help="Ticker filter, e.g. 278470.KS.")
    parser.add_argument("--action", help="Action filter, e.g. REDUCE_RISK.")
    args = parser.parse_args(argv)
    rows = query_archive(db_path=Path(args.db), query=args.query, ticker=args.ticker, action=args.action)
    print(json.dumps({"rows": rows}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
