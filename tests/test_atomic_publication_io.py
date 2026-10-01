"""Synthetic local state only: never use broker credentials or live endpoints."""

import json
import multiprocessing
import os
import stat
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests

from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock
from tradingagents.portfolio.kis import KisApiError, KisClient


class _SyntheticResponse:
    status_code = 200

    def raise_for_status(self):
        pass

    def json(self):
        return {"access_token": "synthetic-shared-token", "expires_in": 86400}


class _SyntheticSession:
    def __init__(self, calls):
        self.calls = calls

    def post(self, *_args, **_kwargs):
        with self.calls.get_lock():
            self.calls.value += 1
        time.sleep(0.1)
        return _SyntheticResponse()


def _refresh_worker(cache_path, calls, start, results):
    client = KisClient(
        app_key="synthetic-key", app_secret="synthetic-secret",
        session=_SyntheticSession(calls), token_cache_path=cache_path,
        token_file_cache_enabled=True,
    )
    start.wait(10)
    results.put(client.ensure_access_token())


def _increment_worker(path, start):
    start.wait(10)
    for _ in range(10):
        with interprocess_file_lock(str(path) + ".lock", timeout=10):
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
            atomic_write_json(path, {"count": payload["count"] + 1})


def _held_lock_worker(path, ready, release):
    with interprocess_file_lock(path, timeout=5):
        ready.set()
        release.wait(10)


def _client(cache, **kwargs):
    return KisClient(
        app_key="synthetic-key", app_secret="synthetic-secret",
        session=Mock(), token_cache_path=cache, token_file_cache_enabled=True,
        **kwargs,
    )


def _cache(path, token):
    atomic_write_json(path, {
        "access_token": token,
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),
    }, mode=0o600)


def test_atomic_write_preserves_old_document_on_serialization_or_replace_failure(tmp_path):
    path = tmp_path / "manifest.json"
    atomic_write_json(path, {"old": "한글"})
    before = path.read_bytes()
    with pytest.raises(TypeError):
        atomic_write_json(path, {"bad": object()})
    assert path.read_bytes() == before
    with patch("tradingagents.atomic_io.os.replace", side_effect=OSError("synthetic failure")):
        with pytest.raises(OSError):
            atomic_write_json(path, {"new": True})
    assert path.read_bytes() == before
    assert list(tmp_path.glob(".*.tmp")) == []


def test_atomic_write_private_permissions_are_set_before_replace(tmp_path):
    path = tmp_path / "synthetic-token.json"
    original_replace = os.replace

    def inspect_replace(source, target):
        if os.name != "nt":
            assert stat.S_IMODE(Path(source).stat().st_mode) == 0o600
        original_replace(source, target)

    with patch("tradingagents.atomic_io.os.replace", side_effect=inspect_replace):
        atomic_write_json(path, {"synthetic": True}, mode=0o600)
    assert json.loads(path.read_text(encoding="utf-8")) == {"synthetic": True}


def test_multiprocess_atomic_locked_updates_have_no_lost_writes(tmp_path):
    ctx = multiprocessing.get_context("spawn")
    path = tmp_path / "manifest.json"
    atomic_write_json(path, {"count": 0})
    start = ctx.Event()
    workers = [ctx.Process(target=_increment_worker, args=(str(path), start)) for _ in range(3)]
    for worker in workers:
        worker.start()
    start.set()
    for worker in workers:
        worker.join(20)
        assert worker.exitcode == 0
    assert json.loads(path.read_text(encoding="utf-8"))["count"] == 30


def test_process_lock_is_bounded_and_reusable_after_release(tmp_path):
    ctx = multiprocessing.get_context("spawn")
    path = str(tmp_path / "state.lock")
    ready, release = ctx.Event(), ctx.Event()
    worker = ctx.Process(target=_held_lock_worker, args=(path, ready, release))
    worker.start()
    try:
        assert ready.wait(15)
        with pytest.raises(TimeoutError):
            with interprocess_file_lock(path, timeout=0.05):
                pytest.fail("A held lock must not be bypassed")
    finally:
        release.set()
        worker.join(15)
    assert worker.exitcode == 0
    with interprocess_file_lock(path, timeout=1):
        pass


def test_thread_lock_is_bounded(tmp_path):
    path = tmp_path / "state.lock"
    outcomes = []

    def attempt():
        try:
            with interprocess_file_lock(path, timeout=0.05):
                outcomes.append("unexpected-acquisition")
        except TimeoutError:
            outcomes.append("timed-out")

    with interprocess_file_lock(path):
        worker = threading.Thread(target=attempt)
        worker.start()
        worker.join(5)
    assert outcomes == ["timed-out"]


def test_concurrent_token_refresh_issues_once_across_processes(tmp_path):
    ctx = multiprocessing.get_context("spawn")
    cache = str(tmp_path / "synthetic-token.json")
    calls, start, results = ctx.Value("i", 0), ctx.Event(), ctx.Queue()
    workers = [ctx.Process(target=_refresh_worker, args=(cache, calls, start, results)) for _ in range(3)]
    for worker in workers:
        worker.start()
    start.set()
    for worker in workers:
        worker.join(20)
        assert worker.exitcode == 0
    assert calls.value == 1
    assert [results.get(timeout=2) for _ in workers] == ["synthetic-shared-token"] * 3
    assert json.loads(Path(cache).read_text(encoding="utf-8"))["access_token"] == "synthetic-shared-token"


def test_same_client_threads_share_one_refresh_when_disk_cache_disabled(tmp_path):
    client = _client(tmp_path / "unused-synthetic-token.json")
    client._token_file_cache_enabled = False
    outcomes = []

    def issue(*_args, **_kwargs):
        time.sleep(0.05)
        return _SyntheticResponse()

    client.session.post.side_effect = issue
    workers = [threading.Thread(target=lambda: outcomes.append(client.ensure_access_token())) for _ in range(3)]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(5)
    assert outcomes == ["synthetic-shared-token"] * 3
    client.session.post.assert_called_once()


def test_auth_retry_reuses_peer_replacement_not_rejected_token(tmp_path):
    path = tmp_path / "synthetic-token.json"
    _cache(path, "synthetic-rejected")
    client = _client(path)
    assert client.ensure_access_token() == "synthetic-rejected"
    client.invalidate_access_token()
    _cache(path, "synthetic-peer-replacement")
    assert client.issue_access_token(force=True) == "synthetic-peer-replacement"
    client.session.post.assert_not_called()


def test_auth_retry_does_not_reuse_rejected_disk_token(tmp_path):
    path = tmp_path / "synthetic-token.json"
    _cache(path, "synthetic-rejected")
    client = _client(path)
    client.session.post.return_value = _SyntheticResponse()
    client.ensure_access_token()
    client.invalidate_access_token()
    assert client.issue_access_token(force=True) == "synthetic-shared-token"
    client.session.post.assert_called_once()


def test_nonforced_issue_does_not_reuse_invalidated_disk_token(tmp_path):
    path = tmp_path / "synthetic-token.json"
    _cache(path, "synthetic-rejected")
    client = _client(path)
    client.session.post.return_value = _SyntheticResponse()
    client.ensure_access_token()
    client.invalidate_access_token()
    assert client.issue_access_token(force=False) == "synthetic-shared-token"
    client.session.post.assert_called_once()


def test_token_coordination_failure_never_issues_unlocked(tmp_path):
    client = _client(tmp_path / "synthetic-token.json")
    with patch("tradingagents.portfolio.kis.interprocess_file_lock", side_effect=TimeoutError("synthetic")):
        with pytest.raises(KisApiError, match="coordination failed"):
            client.ensure_access_token()
    client.session.post.assert_not_called()


def test_token_persistence_failure_does_not_return_uncached_token(tmp_path):
    client = _client(tmp_path / "synthetic-token.json")
    client.session.post.return_value = _SyntheticResponse()
    with patch("tradingagents.portfolio.kis.atomic_write_json", side_effect=PermissionError("synthetic")):
        with pytest.raises(KisApiError, match="persisted safely"):
            client.ensure_access_token()
    assert client._access_token is None
    assert client._token_expires_at is None


def test_token_http_failure_is_not_mislabeled_as_coordination_failure(tmp_path):
    client = _client(tmp_path / "synthetic-token.json")
    client.session.post.side_effect = requests.ConnectionError("synthetic transport failure")
    with pytest.raises(requests.ConnectionError):
        client.ensure_access_token()


def test_failed_auth_refresh_never_resurrects_rejected_disk_token(tmp_path):
    path = tmp_path / "synthetic-token.json"
    _cache(path, "synthetic-rejected")
    client = _client(path)
    client.ensure_access_token()
    client.invalidate_access_token()
    client.session.post.side_effect = requests.ConnectionError("synthetic transport failure")
    for _ in range(2):
        with pytest.raises(requests.ConnectionError):
            client.ensure_access_token()
        assert client._access_token is None
    assert client.session.post.call_count == 2
