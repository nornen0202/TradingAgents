from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from .prism_dashboard import parse_dashboard_payload
from .prism_models import PrismIngestionResult, PrismSourceKind


PRISM_SQLITE_TABLES = (
    "stock_holdings",
    "trading_history",
    "watchlist_history",
    "holding_decisions",
    "trading_journal",
    "trading_principles",
    "trading_intuitions",
    "analysis_performance_tracker",
    "market_condition",
    "trigger_performance",
    "missed_opportunities",
    "avoided_losses",
)


def load_prism_sqlite(path: str | Path, *, market: str | None = None) -> PrismIngestionResult:
    ingested_at = datetime.now().astimezone()
    db_path = Path(path).expanduser()
    if not db_path.exists():
        return PrismIngestionResult(
            enabled=True,
            ok=False,
            source_kind=PrismSourceKind.SQLITE,
            source=db_path.as_posix(),
            ingested_at=ingested_at,
            warnings=[f"sqlite_missing:{db_path}"],
        )

    payload: dict[str, Any] = {}
    warnings: list[str] = []
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            tables = {
                str(row["name"])
                for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                if row["name"]
            }
            for table in PRISM_SQLITE_TABLES:
                if table not in tables:
                    warnings.append(f"sqlite_table_missing:{table}")
                    continue
                payload[table] = [dict(row) for row in conn.execute(f'SELECT * FROM "{table}"')]
    except Exception as exc:
        return PrismIngestionResult(
            enabled=True,
            ok=False,
            source_kind=PrismSourceKind.SQLITE,
            source=db_path.as_posix(),
            ingested_at=ingested_at,
            warnings=[f"sqlite_read_failed:{db_path}:{exc}"],
        )

    result = parse_dashboard_payload(
        payload,
        source_kind=PrismSourceKind.SQLITE,
        source=db_path.as_posix(),
        market=market,
        ingested_at=ingested_at,
    )
    return PrismIngestionResult(
        **{
            **result.__dict__,
            "warnings": [*warnings, *result.warnings],
        }
    )
