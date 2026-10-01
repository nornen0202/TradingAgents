"""Small local-filesystem primitives for shared producer state.

Atomic replacement prevents partial documents; the separate advisory lock protects
read/modify/write or token-refresh transactions. All cooperating writers must use
the same lock path. These helpers do not provide a distributed/network-FS lock.
"""

from __future__ import annotations

import errno
import json
import os
import stat
import tempfile
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


_THREAD_LOCKS: dict[str, threading.Lock] = {}
_THREAD_LOCKS_GUARD = threading.Lock()


def atomic_write_json(
    path: str | Path,
    payload: Any,
    *,
    mode: int | None = None,
    indent: int | None = 2,
) -> None:
    """Publish complete UTF-8 JSON using a unique temporary sibling and replace.

The old file is retained if serialization, writing, or replacement fails. Explicit
``mode=0o600`` is required for secrets; otherwise an existing mode is preserved,
or 0644 is used for a new public document. Windows ACLs remain OS-managed.
"""
    content = (json.dumps(payload, ensure_ascii=False, indent=indent) + "\n").encode("utf-8")
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if mode is None:
        try:
            mode = stat.S_IMODE(destination.stat().st_mode)
        except FileNotFoundError:
            mode = 0o644
    fd, temporary_name = tempfile.mkstemp(prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, destination)
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
        # msvcrt locks a byte range, including for a newly created lock file.
        if os.fstat(fd).st_size == 0:
            os.write(fd, b"\0")
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
