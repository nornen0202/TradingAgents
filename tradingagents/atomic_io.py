"""Small local-filesystem primitives for shared producer state.

Atomic replacement prevents partial documents; the separate advisory lock protects
read/modify/write or token-refresh transactions. All cooperating writers must use
the same lock path. These helpers do not provide a distributed/network-FS lock.
"""

from __future__ import annotations

import errno
import json
import os
import uuid
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


_THREAD_LOCKS: dict[str, threading.Lock] = {}
_THREAD_LOCKS_GUARD = threading.Lock()
_WINDOWS_REPLACE_RETRY_DELAYS = (0.05, 0.1, 0.2, 0.4, 0.8, 1.0)


def _temporary_sibling(destination: Path) -> tuple[int, Path]:
    # tempfile.mkstemp retries PermissionError on Windows when os.access says
    # writable. ACL/sandbox denial can therefore spin for TMP_MAX attempts.
    # Retry actual name collisions only, with a finite bound; never alter ACLs.
    flags = os.O_RDWR | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    for _ in range(16):
        temporary = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.tmp")
        try:
            return os.open(temporary, flags, 0o600), temporary
        except FileExistsError:
            continue
    raise FileExistsError("Unable to allocate a unique atomic-write sibling")


def atomic_write_json(
    path: str | Path,
    payload: Any,
    *,
    mode: int | None = None,
    indent: int | None = 2,
) -> None:
    """Publish complete UTF-8 JSON using a unique temporary sibling and replace.

The old file is retained if serialization, writing, or replacement fails. Local
producer state can include account/error data, so every replacement is owner-only
even if the previous file had broader permissions. Windows ACLs remain OS-managed.
Windows reader handles can briefly prevent replacement. Retry only that operation
for native access/sharing/lock denials, for at most 2.55 seconds of backoff; a
persistent denial still fails without deleting or changing the destination.
"""
    if mode not in (None, 0o600):
        raise ValueError("Shared producer JSON must use owner-only permissions.")
    content = (json.dumps(payload, ensure_ascii=False, indent=indent) + "\n").encode("utf-8")
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = _temporary_sibling(destination)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o600)
        for attempt in range(len(_WINDOWS_REPLACE_RETRY_DELAYS) + 1):
            try:
                os.replace(temporary, destination)
                break
            except OSError as exc:
                if (getattr(exc, "winerror", None) not in {5, 32, 33}
                        or attempt == len(_WINDOWS_REPLACE_RETRY_DELAYS)):
                    raise
                time.sleep(_WINDOWS_REPLACE_RETRY_DELAYS[attempt])
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def interprocess_file_lock(path: str | Path, *, timeout: float = 30.0) -> Iterator[None]:
    """Acquire a bounded process/thread lock, released automatically on exit.

The lock file is deliberately never deleted (unlinking would split lock identity).
Only local cooperating processes are supported. Coordination errors fail closed;
there is no unlocked fallback. The OS releases the lock if a process dies.
"""
    if timeout < 0:
        raise ValueError("Lock timeout must be non-negative.")
    lock_path = Path(path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    key = os.path.normcase(str(lock_path.resolve()))
    with _THREAD_LOCKS_GUARD:
        thread_lock = _THREAD_LOCKS.setdefault(key, threading.Lock())
    deadline = time.monotonic() + timeout
    if not thread_lock.acquire(timeout=timeout):
        raise TimeoutError("Shared state lock acquisition timed out.")
    fd: int | None = None
    acquired = False
    try:
        fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
        # Both OS locks support an empty file (Windows permits ranges past EOF).
        # Never initialize byte zero before acquiring: a peer can already hold
        # that range, making an otherwise valid contender fail with EACCES.
        while True:
            try:
                if os.name == "nt":
                    import msvcrt

                    os.lseek(fd, 0, os.SEEK_SET)
                    msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
                break
            except OSError as exc:
                if exc.errno not in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}:
                    raise
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("Shared state lock acquisition timed out.") from exc
                time.sleep(min(0.05, remaining))
        yield
    finally:
        try:
            if fd is not None:
                try:
                    if acquired:
                        if os.name == "nt":
                            import msvcrt

                            os.lseek(fd, 0, os.SEEK_SET)
                            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
                        else:
                            import fcntl

                            fcntl.flock(fd, fcntl.LOCK_UN)
                finally:
                    os.close(fd)
        finally:
            thread_lock.release()
