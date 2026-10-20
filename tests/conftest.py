"""Deterministic contention for tests that exercise the real publication lock."""

import errno
import os
from types import SimpleNamespace

import pytest

from tradingagents import atomic_io


@pytest.fixture
def publication_contention(monkeypatch):
    def install(*, release_after=45, on_release=lambda: None):
        clock = SimpleNamespace(elapsed=0.0, released=False)

        def sleep(seconds):
            clock.elapsed += seconds

        # Replace this module's clock, not the process-wide time module.
        monkeypatch.setattr(atomic_io, "time", SimpleNamespace(
            monotonic=lambda: clock.elapsed, sleep=sleep))

        def contend():
            if clock.elapsed < release_after:
                raise OSError(errno.EACCES, "synthetic publisher still owns the lane")
            if not clock.released:
                on_release()
                clock.released = True

        if os.name == "nt":
            import msvcrt
            original = msvcrt.locking

            def locking(fd, mode, length):
                if mode == msvcrt.LK_NBLCK:
                    contend()
                return original(fd, mode, length)

            monkeypatch.setattr(msvcrt, "locking", locking)
        else:
            import fcntl
            original = fcntl.flock

            def flock(fd, mode):
                if mode & fcntl.LOCK_NB:
                    contend()
                return original(fd, mode)

            monkeypatch.setattr(fcntl, "flock", flock)
        return clock

    return install
