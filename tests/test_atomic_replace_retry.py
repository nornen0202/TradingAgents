"""Synthetic archive files; never relax permissions or retry a whole producer."""

import ctypes
import errno
import json
import os
import threading
from pathlib import Path

import pytest

from tradingagents import atomic_io


def windows_error(code):
    error = PermissionError(errno.EACCES, "synthetic Windows replacement denial")
    error.winerror = code
    return error


@pytest.mark.parametrize("code", [5, 32, 33])
def test_transient_windows_denial_retries_same_complete_temporary_file(monkeypatch, tmp_path, code):
    path = tmp_path / "latest-run.json"
    atomic_io.atomic_write_json(path, {"old": True})
    before = path.read_bytes()
    replace = os.replace
    sources, sleeps = [], []

    def briefly_denied(source, destination):
        sources.append(source)
        assert json.loads(Path(source).read_text(encoding="utf-8")) == {"new": "한글"}
        assert path.read_bytes() == before
        if len(sources) <= 2:
            raise windows_error(code)
        replace(source, destination)

    monkeypatch.setattr(atomic_io.os, "replace", briefly_denied)
    monkeypatch.setattr(atomic_io.time, "sleep", sleeps.append)
    atomic_io.atomic_write_json(path, {"new": "한글"})
    assert len(sources) == 3 and len(set(sources)) == 1
    assert sleeps == [0.05, 0.1]
    assert json.loads(path.read_text(encoding="utf-8")) == {"new": "한글"}
    assert not list(tmp_path.glob(".*.tmp"))


@pytest.mark.parametrize("code", [5, 32, 33])
def test_persistent_windows_denial_is_bounded_and_preserves_old_file(monkeypatch, tmp_path, code):
    path = tmp_path / "latest-run.json"
    atomic_io.atomic_write_json(path, {"old": True})
    before = path.read_bytes()
    calls, sleeps = [], []
    error = windows_error(code)

    def denied(*args):
        calls.append(args)
        raise error

    monkeypatch.setattr(atomic_io.os, "replace", denied)
    monkeypatch.setattr(atomic_io.time, "sleep", sleeps.append)
    with pytest.raises(PermissionError) as caught:
        atomic_io.atomic_write_json(path, {"new": True})
    assert caught.value is error
    assert len(calls) == 7
    assert sleeps == [0.05, 0.1, 0.2, 0.4, 0.8, 1.0]
    assert path.read_bytes() == before
    assert not list(tmp_path.glob(".*.tmp"))


@pytest.mark.parametrize("error", [
    PermissionError(errno.EACCES, "POSIX access denial"),
    OSError(errno.ENOSPC, "full disk"),
    windows_error(87),
])
def test_other_replacement_failures_are_not_retried(monkeypatch, tmp_path, error):
    path = tmp_path / "latest-run.json"
    atomic_io.atomic_write_json(path, {"old": True})
    before = path.read_bytes()
    calls, sleeps = [], []

    def failed(*args):
        calls.append(args)
        raise error

    monkeypatch.setattr(atomic_io.os, "replace", failed)
    monkeypatch.setattr(atomic_io.time, "sleep", sleeps.append)
    with pytest.raises(OSError) as caught:
        atomic_io.atomic_write_json(path, {"new": True})
    assert caught.value is error
    assert len(calls) == 1 and not sleeps
    assert path.read_bytes() == before
    assert not list(tmp_path.glob(".*.tmp"))


def test_permission_failure_before_replacement_is_not_retried(monkeypatch, tmp_path):
    path = tmp_path / "latest-run.json"
    atomic_io.atomic_write_json(path, {"old": True})
    before = path.read_bytes()
    replaces, sleeps = [], []

    def denied(*_args):
        raise windows_error(5)

    monkeypatch.setattr(atomic_io.os, "fsync", denied)
    monkeypatch.setattr(atomic_io.os, "replace", lambda *args: replaces.append(args))
    monkeypatch.setattr(atomic_io.time, "sleep", sleeps.append)
    with pytest.raises(PermissionError):
        atomic_io.atomic_write_json(path, {"new": True})
    assert not replaces and not sleeps
    assert path.read_bytes() == before
    assert not list(tmp_path.glob(".*.tmp"))


@pytest.mark.skipif(os.name != "nt", reason="Windows reader handle sharing semantics")
def test_windows_reader_releasing_handle_allows_atomic_replacement(tmp_path):
    from ctypes import wintypes

    path = tmp_path / "latest-run.json"
    atomic_io.atomic_write_json(path, {"old": True})
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                  ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    # A normal reader may share reads/writes while preventing deletion/rename.
    handle = kernel.CreateFileW(str(path), 0x80000000, 0x1 | 0x2, None, 3, 0x80, None)
    assert handle != wintypes.HANDLE(-1).value
    release = threading.Event()

    def close_reader():
        release.wait(0.15)
        kernel.CloseHandle(handle)

    reader = threading.Thread(target=close_reader)
    reader.start()
    try:
        atomic_io.atomic_write_json(path, {"new": True})
    finally:
        release.set()
        reader.join(5)
    assert not reader.is_alive()
    assert json.loads(path.read_text(encoding="utf-8")) == {"new": True}
    assert not list(tmp_path.glob(".*.tmp"))
