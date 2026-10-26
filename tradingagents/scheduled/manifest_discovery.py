"""Discard unchanged overlay manifests before loading full-research candidates.

The index is only a negative discovery cache. Every returned full manifest is
read from disk again and still needs the caller's date/coverage/quality checks.
It never caches a selected source, decision, quote, or approval.
"""
from __future__ import annotations

import json
from pathlib import Path

from tradingagents.atomic_io import atomic_write_json


SCHEMA = "tradingagents.run-mode-discovery/v1"


def _signature(path: Path) -> list[int]:
    stat = path.stat()
    return [stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size, stat.st_ino]


def _load_index(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("schema") == SCHEMA and isinstance(payload.get("entries"), dict):
            return payload["entries"]
    except (OSError, ValueError, AttributeError):
        pass
    return {}


def full_manifests_desc(archive_dir: Path, *, modes=None, write_index: bool = True) -> list[tuple[dict, Path]]:
    """Discover original manifests; read-only callers can suppress cache writes."""
    modes = {"full"} if modes is None else set(modes)
    runs_dir = archive_dir / "runs"
    if not runs_dir.exists():
        return []
    index_path = archive_dir / ".run-mode-discovery.json"
    previous = _load_index(index_path)
    current, selected = {}, []
    for year in sorted((p for p in runs_dir.iterdir() if p.is_dir()), reverse=True):
        for directory in sorted((p for p in year.iterdir() if p.is_dir()), reverse=True):
            path = directory / "run.json"
            try:
                signature = _signature(path)
            except FileNotFoundError:
                continue
            key = path.relative_to(runs_dir).as_posix()
            cached = previous.get(key)
            if (isinstance(cached, dict) and cached.get("signature") == signature
                    and isinstance(cached.get("mode"), str)
                    and cached.get("mode") in {"overlay_only", "portfolio_only", "selective_rerun_only"}
                    and cached["mode"] not in modes):
                current[key] = cached
                continue
            # Do not cache parsed objects: callers may mutate their own copy.
            # A malformed changed file fails just as an uncached archive scan.
            manifest = json.loads(path.read_text(encoding="utf-8"))
            mode = str((manifest.get("settings") or {}).get("run_mode") or "full").strip().lower()
            try:
                unchanged = signature == _signature(path)
            except FileNotFoundError:
                unchanged = False
            if unchanged:
                current[key] = {"signature": signature, "mode": mode}
            if mode in modes:
                selected.append((manifest, directory))
    if write_index and current != previous:
        try:
            # Concurrent discovery may replace this optional index; each next
            # reader enumerates and re-stats every original file regardless.
            atomic_write_json(index_path, {"schema": SCHEMA, "entries": current})
        except OSError:
            pass  # Read-only archives retain the exact uncached selection.
    return selected
