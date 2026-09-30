"""Durable attempt state; incomplete attempts never become analysis cohorts."""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path


class RunAttempt:
    def __init__(self, run_dir: Path, *, market: str, run_mode: str, started_at: datetime):
        self.path = run_dir / "attempt.json"
        self.state = {"schema": "tradingagents.analysis-attempt/v1", "run_id": run_dir.name,
                      "market": market.upper(), "run_mode": run_mode,
                      "started_at": started_at.isoformat(), "status": "RUNNING"}
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self._heartbeat, daemon=True)

    def _write(self):
        self.state["heartbeat_at"] = datetime.now(timezone.utc).isoformat()
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.state, indent=2), encoding="utf-8")
        os.replace(temporary, self.path)

    def _heartbeat(self):
        while not self.stop.wait(30):
            self._write()

    def __enter__(self):
        self._write()
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.stop.set()
        self.thread.join(timeout=5)
        manifest = _read(self.path.parent / "run.json")
        self.state["status"] = "FAILED" if exc_type else str(manifest.get("status") or "FAILED").upper()
        self.state["finished_at"] = datetime.now(timezone.utc).isoformat()
        self.state["completed_tickers"] = (manifest.get("summary") or {}).get("successful_tickers", 0)
        self.state["error_type"] = exc_type.__name__ if exc_type else None
        self._write()


def _read(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def latest_full_attempt(archive: Path, market: str, *, now: datetime) -> dict:
    candidates = []
    for path in (archive / "runs").glob("*/*/attempt.json"):
        item = _read(path)
        if item.get("market", "").lower() != market.lower() or item.get("run_mode") != "full":
            continue
        completed = _read(path.with_name("run.json"))
        if item.get("status") == "RUNNING" and completed.get("finished_at"):
            item.update(status=str(completed.get("status") or "UNVERIFIED").upper(), finished_at=completed["finished_at"])
        candidates.append(item)
    # Completed legacy runs predate attempt.json. They remain valid baselines.
    for path in (archive / "runs").glob("*/*/run.json"):
        item = _read(path)
        settings = item.get("settings") or {}
        if path.with_name("attempt.json").exists() or str(settings.get("market", "")).lower() != market.lower() or settings.get("run_mode", "full") != "full":
            continue
        candidates.append({"run_id": item.get("run_id"), "started_at": item.get("started_at"),
                           "finished_at": item.get("finished_at"), "status": str(item.get("status") or "UNVERIFIED").upper()})
    if not candidates:
        return {}
    item = max(candidates, key=lambda row: str(row.get("started_at") or ""))
    if item.get("status") == "RUNNING":
        try:
            heartbeat = datetime.fromisoformat(item["heartbeat_at"])
            if heartbeat.tzinfo is None or heartbeat > now or now - heartbeat > timedelta(minutes=5):
                item["status"] = "INTERRUPTED"
        except (KeyError, TypeError, ValueError):
            item["status"] = "UNVERIFIED"
    return item
