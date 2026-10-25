"""Bounded, in-memory jobs for one explicit read-only archive snapshot.

This is a response transport, not a price/account cache. A completed token is
delivered once; a fresh request rebuilds and revalidates its source evidence.
Filesystem signatures invalidate bytes and never establish evidence clocks.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import json
from pathlib import Path
import secrets
from threading import Condition, Thread
from time import monotonic


PHASES = frozenset({"QUEUED", "INDEX", "SELECTION_COVERAGE", "REPLAY", "BUILD", "SERIALIZE", "VERIFY"})


class SnapshotJobError(Exception):
    def __init__(self, status, message):
        self.status, self.message = status, message
        super().__init__(message)


@dataclass
class _Job:
    token: str
    key: tuple
    build: object
    created: float
    phase_started: float
    state: str = "QUEUED"
    phase: str = "QUEUED"
    payload: bytes | None = None
    verify: object = None
    completed: float | None = None
    error: SnapshotJobError | None = None


class SnapshotJobs:
    """One worker, four total jobs and bounded results; no executor work queue.

    READY -> VERIFYING -> DELIVERY_READY is a single transition. A delivery
    consumes its token even if the client subsequently disconnects. The client
    must start a fresh query after a lost response, not replay cached authority.
    """
    def __init__(self, *, max_jobs=4, max_result_bytes=8 * 1024 * 1024,
                 max_total_bytes=16 * 1024 * 1024, retention_seconds=120, clock=monotonic):
        self.max_jobs, self.max_result_bytes, self.max_total_bytes = max_jobs, max_result_bytes, max_total_bytes
        self.retention_seconds, self.clock = retention_seconds, clock
        self._condition = Condition()
        self._jobs, self._queue = {}, deque()
        self._worker = None

    def _enqueue(self, token, verify=False):
        self._queue.append((token, verify))
        if self._worker is None:
            self._worker = Thread(target=self._run, daemon=True, name="archive-snapshot")
            self._worker.start()
        self._condition.notify()

    def _purge(self, now):
        for token, job in list(self._jobs.items()):
            if (job.state in {"READY", "DELIVERY_READY", "ERROR"} and job.completed is not None
                    and now - job.completed >= self.retention_seconds):
                del self._jobs[token]

    def request(self, key, build=None, *, token=None):
        with self._condition:
            now = self.clock()
            self._purge(now)
            if token is None:
                job = next((j for j in self._jobs.values() if j.key == key and j.state in {"QUEUED", "RUNNING", "VERIFYING"}), None)
                if job is None:
                    # Aborted clients may never collect a completed response.
                    # Reclaim only terminal jobs, never running/queued evidence.
                    terminal = sorted((j for j in self._jobs.values() if j.state in {"READY", "DELIVERY_READY", "ERROR"}),
                                      key=lambda j: j.completed)
                    while len(self._jobs) >= self.max_jobs and terminal:
                        del self._jobs[terminal.pop(0).token]
                    if len(self._jobs) >= self.max_jobs:
                        raise SnapshotJobError(429, "Archive snapshot capacity reached; retry a fresh query later")
                    job = _Job(secrets.token_urlsafe(24), key, build, now, now)
                    self._jobs[job.token] = job
                    self._enqueue(job.token)
            else:
                job = self._jobs.get(token)
                if job is None:
                    raise SnapshotJobError(410, "Archive snapshot token expired or unknown; start a fresh query")
                if job.key != key:
                    raise SnapshotJobError(400, "Archive snapshot token does not match this query")
            if job.state == "ERROR":
                del self._jobs[job.token]
                raise job.error
            if job.state == "READY":
                job.state, job.phase, job.phase_started = "VERIFYING", "VERIFY", now
                self._enqueue(job.token, verify=True)
            if job.state == "DELIVERY_READY":
                del self._jobs[job.token]
                return 200, job.payload
            if job.state == "CANCELLED":
                raise SnapshotJobError(410, "Archive snapshot was cancelled; start a fresh query")
            return 202, {"status": "SNAPSHOT_BUILDING", "job_token": job.token, "generation": key[3],
                         "as_of": key[1],
                         "phase": job.phase, "elapsed_seconds": max(0, now - job.created),
                         "phase_elapsed_seconds": max(0, now - job.phase_started)}

    def cancel(self, key, token):
        with self._condition:
            job = self._jobs.get(token)
            if job is None:
                raise SnapshotJobError(410, "Archive snapshot token expired or unknown; start a fresh query")
            if job.key != key:
                raise SnapshotJobError(400, "Archive snapshot token does not match this query")
            if job.state in {"READY", "DELIVERY_READY", "ERROR", "QUEUED"}:
                del self._jobs[token]
                return
            job.state, job.payload, job.completed = "CANCELLED", None, self.clock()

    def _progress(self, job, phase):
        if phase not in PHASES:
            raise ValueError("Unknown snapshot phase")
        with self._condition:
            if job.state != "CANCELLED":
                job.phase, job.phase_started = phase, self.clock()

    def _run(self):
        while True:
            with self._condition:
                if not self._queue:
                    self._condition.wait(1)
                    if not self._queue:
                        self._worker = None
                        return
                token, checking = self._queue.popleft()
                job = self._jobs.get(token)
                if job is None:
                    continue
                if job.state == "CANCELLED":
                    del self._jobs[token]
                    continue
                if not checking:
                    job.state = "RUNNING"
            try:
                if checking:
                    job.verify()
                    encoded = job.payload
                else:
                    payload, verify = job.build(lambda phase: self._progress(job, phase))
                    self._progress(job, "SERIALIZE")
                    encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
                    payload = None  # Do not retain a decoded duplicate while idle.
                    if len(encoded) > self.max_result_bytes:
                        raise SnapshotJobError(413, "Archive snapshot exceeds response size limit; evidence was not truncated")
                    job.verify = verify
                with self._condition:
                    if job.state == "CANCELLED" or token not in self._jobs:
                        self._jobs.pop(token, None)
                        continue
                    total = sum(len(j.payload) for j in self._jobs.values() if j is not job and j.payload is not None)
                    if total + len(encoded) > self.max_total_bytes:
                        raise SnapshotJobError(429, "Archive snapshot response memory limit reached; retry a fresh query later")
                    job.payload, job.build = encoded, None
                    job.state = "DELIVERY_READY" if checking else "READY"
                    job.completed = self.clock()
            except Exception as error:
                with self._condition:
                    if job.state == "CANCELLED" or token not in self._jobs:
                        self._jobs.pop(token, None)
                        continue
                    job.error = error if isinstance(error, SnapshotJobError) else SnapshotJobError(422, "Archive input invalid, changed or unavailable")
                    job.payload, job.build, job.verify = None, None, None
                    job.state, job.completed = "ERROR", self.clock()


def evidence_fingerprint(directory, *, root, manifest=None, journals=(), alias=None):
    """Bounded to this selected ticker's files and configured journals only.

    No file contents or producer clocks are changed. Missing journal sidecars
    are part of the fingerprint, so a newly-created WAL cannot be overlooked.
    """
    root, directory = Path(root), Path(directory)
    resolved_root = root.resolve()
    if alias is not None and Path(alias).resolve() != resolved_root:
        raise ValueError("Archive alias boundary changed")
    if directory.resolve() != directory or not directory.is_relative_to(resolved_root) or not directory.is_dir():
        raise ValueError("Selected archive boundary changed")
    paths = [directory]
    for path in directory.rglob("*"):
        paths.append(path)
        if len(paths) > 10000:
            raise ValueError("Selected archive evidence file limit exceeded")
    if manifest is not None:
        paths.append(Path(manifest))
    rows = []
    for path in sorted(paths):
        resolved = path.resolve()
        if resolved != path or not resolved.is_relative_to(resolved_root):
            raise ValueError("Archive evidence boundary changed")
        stat = path.stat()
        rows.append((str(path), stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size, stat.st_ino, stat.st_dev, stat.st_mode))
    return tuple(rows) + journal_fingerprint(journals)


def journal_fingerprint(journals):
    """Metadata invalidation only; the caller must compare cutoff-visible proof.

    A normal future append may change every SQLite byte without changing a past
    view. This signature is not itself a requirement that journals stay frozen.
    """
    rows = []
    for configured in journals:
        path = Path(configured)
        fixed = path.resolve()
        for suffix in ("", "-wal", "-shm", "-journal"):
            item = Path(str(path) + suffix)
            if item.resolve() != Path(str(fixed) + suffix):
                raise ValueError("Configured journal boundary changed")
            if item.exists():
                stat = item.stat()
                rows.append((str(item), stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size, stat.st_ino, stat.st_dev, stat.st_mode))
            else:
                rows.append((str(item), None))
    return tuple(rows)


def journal_identities(stamps):
    # Four rows per configured main DB: file, WAL, SHM and rollback journal.
    return tuple((row[0], row[4:6] if len(row) > 2 else None) for row in stamps[::4])


