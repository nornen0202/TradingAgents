"""Bounded-memory, single-flight discovery for the read-only archive viewer.

Only metadata needed for selection is retained. Filesystem clocks invalidate
bytes; eligibility still uses the producer's aware timestamps on every query.
No archive, trading state, or on-disk index is written.
"""
from __future__ import annotations

from concurrent.futures import Future
import json
from pathlib import Path
from threading import Lock, Thread


def signature(path):
    stat = path.stat()
    return stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size, stat.st_ino


def project_manifest(path):
    before = signature(path)
    with path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    if signature(path) != before or not isinstance(raw, dict):
        raise ValueError("Manifest changed during discovery")
    fields = ("run_id", "status", "started_at", "finished_at", "overlay_source_run_id")
    result = {name: raw.get(name) for name in fields}
    settings = raw.get("settings")
    result["settings"] = {name: settings.get(name) for name in ("market", "run_mode")} if isinstance(settings, dict) else {}
    rows = raw.get("tickers")
    result["tickers"] = [{name: row.get(name) for name in ("ticker", "status", "quality_flags")}
                         for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []
    return before, result


class CatalogPending(Exception):
    def __init__(self, progress):
        self.progress = progress


class ArchiveCatalogIndex:
    """One scanner per server, including across different cutoff/ticker queries.

    Each new request checks for additions, deletions and changed manifests.
    A 202 response's generation token lets polling finish that same scan instead
    of starting it again. Small archives finish within the bounded initial wait.
    """

    def __init__(self, archive_dir):
        self.root = (Path(archive_dir) / "runs").resolve()
        self._lock = Lock()
        self._future = None
        self._generation = 0
        self._cache = {}
        self._visited = 0
        self._parsed = 0

    def snapshot(self, *, generation=None, wait_seconds=0.2):
        with self._lock:
            # Polling an older generation consumes the latest completed scan;
            # only a new request without a token requests another disk scan.
            if self._future is None or (self._future.done() and generation is None):
                self._generation += 1
                self._visited = self._parsed = 0
                self._future = Future()
                Thread(target=self._scan, args=(self._future,), daemon=True, name="archive-catalog").start()
            future = self._future
            token = self._generation
        try:
            return future.result(timeout=wait_seconds)
        except TimeoutError:
            if future.done():
                return future.result()
            with self._lock:
                progress = {"status": "INDEXING", "generation": token,
                            "manifests_checked": self._visited, "manifests_parsed": self._parsed}
            raise CatalogPending(progress) from None

    def _scan(self, future):
        updated = {}
        try:
            for path in self.root.glob("*/*/run.json"):
                # Revalidate boundaries even for cache hits. Do not open an
                # archive symlink/junction that was replaced after the last scan.
                if not path.resolve().is_relative_to(self.root):
                    continue
                try:
                    stamp = signature(path)
                    cached = self._cache.get(path)
                    if cached is None or cached[0] != stamp:
                        cached = project_manifest(path)
                        with self._lock:
                            self._parsed += 1
                    updated[path] = cached
                except (OSError, ValueError, TypeError):
                    # Never reuse the previous valid value after a bad rewrite.
                    pass
                with self._lock:
                    self._visited += 1
            self._cache = updated
            future.set_result(tuple((path, item[1]) for path, item in updated.items()))
        except Exception as error:
            future.set_exception(error)
