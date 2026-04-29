from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

from .action_outcomes import initialize_action_tracker, record_run_recommendations


ARCHIVE_SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS archived_run_artifacts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      run_id TEXT NOT NULL,
      artifact_type TEXT NOT NULL,
      ticker TEXT,
      payload_json TEXT NOT NULL,
      created_at TEXT NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_archived_run_artifacts_run ON archived_run_artifacts(run_id)",
    "CREATE INDEX IF NOT EXISTS idx_archived_run_artifacts_ticker ON archived_run_artifacts(ticker)",
)


def initialize_archive_store(db_path: Path) -> None:
    initialize_action_tracker(db_path)
    with sqlite3.connect(db_path) as conn:
        for statement in ARCHIVE_SCHEMA:
            conn.execute(statement)
        conn.commit()


def archive_run(run_dir: Path, db_path: Path) -> None:
    initialize_archive_store(db_path)
    record_run_recommendations(run_dir, db_path)
    manifest = _load_json(Path(run_dir) / "run.json")
    run_id = str(manifest.get("run_id") or Path(run_dir).name)
    created_at = datetime.now().astimezone().isoformat()
    artifacts = [
        ("runs", None, manifest),
        ("performance_summaries", None, (manifest.get("performance") or {})),
        ("scanner_candidates", None, _load_json(Path(run_dir) / "scanner" / "scanner_candidates.json")),
        ("external_prism_signals", None, _load_json(Path(run_dir) / "external_signals" / "prism_signals.json")),
        ("closed_trade_reviews", None, _load_json(Path(run_dir) / "closed_trade_review.json")),
    ]
    portfolio_candidates = _load_json(Path(run_dir) / "portfolio-private" / "portfolio_candidates.json")
    for item in portfolio_candidates.get("candidates") or []:
        if isinstance(item, Mapping):
            artifacts.append(("portfolio_candidates", str(item.get("canonical_ticker") or ""), dict(item)))
    with sqlite3.connect(db_path) as conn:
        for artifact_type, ticker, payload in artifacts:
            if not payload:
                continue
            conn.execute(
                """
                INSERT INTO archived_run_artifacts (run_id, artifact_type, ticker, payload_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (run_id, artifact_type, ticker, json.dumps(payload, ensure_ascii=False), created_at),
            )
        conn.commit()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}
    return {}
