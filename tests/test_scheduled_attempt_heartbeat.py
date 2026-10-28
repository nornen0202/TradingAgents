"""Windows replacement contention must not silently kill attempt heartbeats."""
from datetime import datetime, timezone
import errno
import json
import threading
from types import SimpleNamespace

import pytest

from tradingagents import atomic_io
from tradingagents.scheduled import attempts


def attempt(tmp_path):
    return attempts.RunAttempt(tmp_path, market="US", run_mode="full", started_at=datetime.now(timezone.utc))


def denied(code):
    error = PermissionError(errno.EACCES, "synthetic replacement denial")
    error.winerror = code
    return error


@pytest.mark.parametrize("code", [5, 32, 33])
def test_heartbeat_survives_transient_windows_replacement_denials(tmp_path, monkeypatch, code):
    worker = attempt(tmp_path)
    worker._write()
    previous = worker.path.read_bytes()
    original = atomic_io.os.replace
    calls, sleeps = [], []

    def replace(source, destination):
        calls.append(source)
        if len(calls) <= 2:
            assert worker.path.read_bytes() == previous
            raise denied(code)
        original(source, destination)

    ticks = iter([False, True])
    worker.stop = SimpleNamespace(wait=lambda seconds: next(ticks))
    monkeypatch.setattr(atomic_io.os, "replace", replace)
    monkeypatch.setattr(atomic_io.time, "sleep", sleeps.append)
    worker._heartbeat()
    assert len(calls) == 3 and len(set(calls)) == 1
    assert sleeps == [0.05, 0.1]
    assert json.loads(worker.path.read_text())["status"] == "RUNNING"
    assert not list(tmp_path.glob(".*.tmp"))


def test_persistent_denial_preserves_the_last_heartbeat_and_still_fails_closed(tmp_path, monkeypatch):
    worker = attempt(tmp_path)
    worker._write()
    previous = worker.path.read_bytes()
    calls = []

    def replace(*args):
        calls.append(args)
        raise denied(5)

    monkeypatch.setattr(atomic_io.os, "replace", replace)
    monkeypatch.setattr(atomic_io.time, "sleep", lambda seconds: None)
    with pytest.raises(PermissionError):
        worker._write()
    assert len(calls) == 7
    assert worker.path.read_bytes() == previous
    assert not list(tmp_path.glob(".*.tmp"))


def test_terminal_receipt_cannot_be_overwritten_by_a_slow_heartbeat(tmp_path, monkeypatch):
    worker = attempt(tmp_path)
    (tmp_path / "run.json").write_text(json.dumps({"status": "success", "summary": {"successful_tickers": 30}}))
    entered, release, finished = threading.Event(), threading.Event(), threading.Event()
    original = attempts.atomic_write_json
    errors = []

    def write(path, payload):
        # The real atomic writer serializes before its potentially slow replace.
        payload = dict(payload)
        if payload["status"] == "RUNNING":
            entered.set()
            assert release.wait(3), "Test did not release the heartbeat writer"
        original(path, payload)

    def heartbeat():
        try:
            worker._write()
        except Exception as exc:
            errors.append(exc)

    def close():
        try:
            worker.__exit__(None, None, None)
        except Exception as exc:
            errors.append(exc)
        finally:
            finished.set()

    monkeypatch.setattr(attempts, "atomic_write_json", write)
    # Simulate a heartbeat that outlives the bounded join without a 5s sleep.
    worker.thread = SimpleNamespace(join=lambda timeout: None)
    first, last = threading.Thread(target=heartbeat), threading.Thread(target=close)
    first.start()
    try:
        assert entered.wait(3)
        last.start()
        assert not finished.wait(0.05)
    finally:
        release.set()
        first.join(timeout=3)
        if last.ident is not None:
            last.join(timeout=3)
    assert not errors and finished.is_set()
    payload = json.loads(worker.path.read_text())
    assert payload["status"] == "SUCCESS" and payload["completed_tickers"] == 30
