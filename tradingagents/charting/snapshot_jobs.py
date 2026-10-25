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
    delivery_valid: object = None
    completed: float | None = None
    error: SnapshotJobError | None = None


class SnapshotJobs:
    """One worker, four total jobs and four caller receipts; no executor queue.

    A completed job is verified before delivery. A cheap tracked-path check at
    the actual poll can re-enter asynchronous verification at most twice if
    evidence changed meanwhile. A delivery consumes its token even if the
    client subsequently disconnects; a lost response needs a fresh query.
    """
    def __init__(self, *, max_jobs=4, max_result_bytes=8 * 1024 * 1024,
                 max_total_bytes=16 * 1024 * 1024, retention_seconds=120, clock=monotonic):
        self.max_jobs, self.max_result_bytes, self.max_total_bytes = max_jobs, max_result_bytes, max_total_bytes
        self.retention_seconds, self.clock = retention_seconds, clock
        self._condition = Condition()
        self._jobs, self._queue = {}, deque()
        self._receipts, self._delivery_invalidations = {}, {}
        self._worker = None

    def _receipt_job(self, token):
        return self._jobs.get(self._receipts.get(token))

    def _drop_receipt(self, token):
        identity = self._receipts.pop(token, None)
        self._delivery_invalidations.pop(token, None)
        if identity is None or identity in self._receipts.values():
            return
        job = self._jobs.get(identity)
        if job is not None and job.state in {"RUNNING", "VERIFYING"}:
            # No remaining reader owns the work. Do not stop the Python reader;
            # discard its late result, retaining its bounded worker slot.
            job.state, job.payload, job.completed = "CANCELLED", None, self.clock()
        else:
            self._jobs.pop(identity, None)

    def _drop_job(self, identity):
        for token, owner in list(self._receipts.items()):
            if owner == identity:
                self._receipts.pop(token)
                self._delivery_invalidations.pop(token, None)
        self._jobs.pop(identity, None)

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
                self._drop_job(token)

    def request(self, key, build=None, *, token=None):
        with self._condition:
            now = self.clock()
            self._purge(now)
            if token is None:
                job = next((j for j in self._jobs.values() if j.key == key and j.state in {"QUEUED", "RUNNING", "VERIFYING"}), None)
                # Receipts are globally bounded, not four per shared job. Old
                # terminal readers may be evicted; active callers are retained.
                terminal = sorted((r for r, owner in self._receipts.items()
                                   if self._jobs[owner].state in {"READY", "DELIVERY_READY", "ERROR"}),
                                  key=lambda r: self._receipt_job(r).completed)
                def full():
                    return len(self._receipts) >= self.max_jobs or job is None and len(self._jobs) >= self.max_jobs
                while full() and terminal:
                    self._drop_receipt(terminal.pop(0))
                if full():
                    raise SnapshotJobError(429, "Archive snapshot capacity reached; retry a fresh query later")
                if job is None:
                    job = _Job(secrets.token_urlsafe(24), key, build, now, now)
                    self._jobs[job.token] = job
                    self._enqueue(job.token)
                token = secrets.token_urlsafe(24)
                self._receipts[token] = job.token
                self._delivery_invalidations[token] = 0
            else:
                job = self._receipt_job(token)
                if job is None:
                    raise SnapshotJobError(410, "Archive snapshot token expired or unknown; start a fresh query")
                if job.key != key:
                    raise SnapshotJobError(400, "Archive snapshot token does not match this query")
            if job.state == "ERROR":
                self._drop_receipt(token)
                # Raising the stored object would attach this caller's frame
                # while another receipt still retains the terminal job.
                raise SnapshotJobError(job.error.status, job.error.message) from None
            if job.state == "READY":
                job.state, job.phase, job.phase_started = "VERIFYING", "VERIFY", now
                self._enqueue(job.token, verify=True)
            if job.state == "DELIVERY_READY":
                try:
                    valid = job.delivery_valid is None or job.delivery_valid()
                except (OSError, ValueError, TypeError, RuntimeError):
                    valid = False
                if valid:
                    self._drop_receipt(token)
                    return 200, job.payload
                if self._delivery_invalidations[token] >= 2:
                    self._drop_receipt(token)
                    raise SnapshotJobError(422, "Archive evidence changed repeatedly before delivery; start a fresh query")
                self._delivery_invalidations[token] += 1
                job.state, job.phase, job.phase_started = "VERIFYING", "VERIFY", now
                self._enqueue(job.token, verify=True)
            if job.state == "CANCELLED":
                raise SnapshotJobError(410, "Archive snapshot was cancelled; start a fresh query")
            return 202, {"status": "SNAPSHOT_BUILDING", "job_token": token, "generation": key[3],
                         "as_of": key[1],
                         "phase": job.phase, "elapsed_seconds": max(0, now - job.created),
                         "phase_elapsed_seconds": max(0, now - job.phase_started)}

    def cancel(self, key, token):
        with self._condition:
            job = self._receipt_job(token)
            if job is None:
                raise SnapshotJobError(410, "Archive snapshot token expired or unknown; start a fresh query")
            if job.key != key:
                raise SnapshotJobError(400, "Archive snapshot token does not match this query")
            self._drop_receipt(token)

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
                    self._drop_job(token)
                    continue
                if not checking:
                    job.state = "RUNNING"
            try:
                if checking:
                    job.verify()
                    encoded = job.payload
                else:
                    payload, verify, *guards = job.build(lambda phase: self._progress(job, phase))
                    if len(guards) > 1:
                        raise ValueError("Unexpected snapshot delivery guard")
                    job.delivery_valid = guards[0] if guards else None
                    self._progress(job, "SERIALIZE")
                    encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
                    payload = None  # Do not retain a decoded duplicate while idle.
                    if len(encoded) > self.max_result_bytes:
                        raise SnapshotJobError(413, "Archive snapshot exceeds response size limit; evidence was not truncated")
                    job.verify = verify
                with self._condition:
                    if job.state == "CANCELLED" or token not in self._jobs:
                        self._drop_job(token)
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
                        self._drop_job(token)
                        continue
                    # Keep status/message only, never a worker traceback that
                    # retains rejected buffers, builders or financial inputs.
                    job.error = (SnapshotJobError(error.status, error.message) if isinstance(error, SnapshotJobError)
                                 else SnapshotJobError(422, "Archive input invalid, changed or unavailable"))
                    job.payload, job.build, job.verify, job.delivery_valid = None, None, None, None
                    encoded = payload = verify = None
                    guards = ()
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


def journal_fingerprint(journals, *, validate_paths=True):
    """Metadata invalidation only; the caller must compare cutoff-visible proof.

    A normal future append may change every SQLite byte without changing a past
    view. ctime does not establish content mutation. SHM is a reader-generated
    SQLite index, so its mutable times/size/identity are not financial evidence;
    its existence, type and reparse attributes still invalidate the reader.
    """
    rows = []
    for configured in journals:
        path = Path(configured)
        # sqlite3 opens the resolved main DB in the replay reader. Its WAL/SHM
        # belong to that DB filename, not to a differently named file alias.
        fixed = path.resolve() if validate_paths else path
        for suffix in ("", "-wal", "-shm", "-journal"):
            item = Path(str(fixed) + suffix)
            if validate_paths and item.resolve() != item:
                raise ValueError("Configured journal boundary changed")
            try:
                local = item.lstat()
            except FileNotFoundError:
                rows.append((str(item), None))
            else:
                if suffix == "-shm":
                    rows.append((str(item), None, None, None, None, None, local.st_mode,
                                 getattr(local, "st_file_attributes", None), getattr(local, "st_reparse_tag", None)))
                else:
                    stat = item.stat()
                    rows.append((str(item), stat.st_mtime_ns, None, stat.st_size, stat.st_ino, stat.st_dev, stat.st_mode,
                                 local.st_ino, local.st_dev, local.st_mode,
                                 getattr(local, "st_file_attributes", None), getattr(local, "st_reparse_tag", None)))
    return tuple(rows)


def journal_identities(stamps):
    # Four rows per configured main DB: file, WAL, SHM and rollback journal.
    return tuple((row[0], row[4:6] if len(row) > 2 else None) for row in stamps[::4])


def tracked_source_metadata(stamps):
    """Re-stat already known paths only: no rglob, resolve, JSON or content I/O."""
    rows = []
    for old in stamps:
        path = Path(old[0])
        stat = path.lstat()
        rows.append((str(path), stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size, stat.st_ino, stat.st_dev, stat.st_mode))
    return tuple(rows)


def boundary_identities(paths):
    rows = []
    for configured in paths:
        path = Path(configured)
        stat = path.stat()
        rows.append((str(path), stat.st_ino, stat.st_dev, stat.st_mode,
                     getattr(stat, "st_file_attributes", None), getattr(stat, "st_reparse_tag", None)))
    return tuple(rows)

