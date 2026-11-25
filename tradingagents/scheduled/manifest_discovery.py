"""Discard unchanged overlay manifests before loading full-research candidates.

The index is only a negative discovery cache. Every returned full manifest is
read from disk again and still needs the caller's date/coverage/quality checks.
It never caches a selected source, decision, quote, or approval.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from itertools import islice
import json
import os
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


def _directories_desc(root):
    try:
        with os.scandir(root) as entries:
            return sorted((Path(entry.path) for entry in entries if entry.is_dir()), reverse=True)
    except (FileNotFoundError, NotADirectoryError):
        return []


def full_manifests_desc(archive_dir: Path, *, modes=None, write_index: bool = True) -> list[tuple[dict, Path]]:
    """Discover original manifests; read-only callers can suppress cache writes."""
    modes = {"full"} if modes is None else set(modes)
    runs_dir = archive_dir / "runs"
    if not runs_dir.exists():
        return []
    physical_runs = runs_dir.resolve()
    index_path = archive_dir / ".run-mode-discovery.json"
    previous = _load_index(index_path)
    current, selected = {}, []
    def inspect(directory):
        path = directory / "run.json"
        relative = path.relative_to(physical_runs)
        key = relative.as_posix()
        try:
            signature = _signature(path)
        except FileNotFoundError:
            return key, None, None
        cached = previous.get(key)
        if (isinstance(cached, dict) and cached.get("signature") == signature
                and isinstance(cached.get("mode"), str)
                and cached["mode"] in {"overlay_only", "portfolio_only", "selective_rerun_only"}
                and cached["mode"] not in modes):
            return key, cached, None
        # A malformed changed file fails just as an uncached archive scan.
        manifest = json.loads(path.read_text(encoding="utf-8"))
        mode = str((manifest.get("settings") or {}).get("run_mode") or "full").strip().lower()
        try:
            unchanged = signature == _signature(path)
        except FileNotFoundError:
            unchanged = False
        entry = {"signature": signature, "mode": mode} if unchanged else None
        return key, entry, (manifest, runs_dir / relative.parent) if mode in modes else None

    directories = (directory for year in _directories_desc(physical_runs) for directory in _directories_desc(year))
    workers = 8 if os.name == "nt" else 1
    # Bound Windows metadata I/O and preserve canonical result and error order.
    with ThreadPoolExecutor(max_workers=workers) as pool:
        while batch := list(islice(directories, workers * 2)):
            for key, entry, candidate in pool.map(inspect, batch):
                if entry is not None:
                    current[key] = entry
                if candidate is not None:
                    selected.append(candidate)
    if write_index and current != previous:
        try:
            # Concurrent discovery may replace this optional index; each next
            # reader enumerates and re-stats every original file regardless.
            atomic_write_json(index_path, {"schema": SCHEMA, "entries": current})
        except OSError:
            pass  # Read-only archives retain the exact uncached selection.
    return selected
