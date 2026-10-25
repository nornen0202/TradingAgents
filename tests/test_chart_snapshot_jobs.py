"""Slow evidence readers never occupy HTTP workers or cross query boundaries."""
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
import json
import shutil
from pathlib import Path
import sqlite3
import stat as stat_module
import weakref
from threading import Event, Thread
from types import SimpleNamespace
import time
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

import pytest

from tradingagents.charting import server as module
from tradingagents.charting.catalog_index import ArchiveCatalogIndex
from tradingagents.charting.snapshot_jobs import SnapshotJobs, SnapshotJobError, evidence_fingerprint, journal_fingerprint, journal_identities
from tests.test_chart_catalog_index import put, ASOF


KEY = ("AAPL", ASOF, None, 1)


@pytest.mark.parametrize("kind,expected_status", [("result", 413), ("total", 429), ("builder", 422)])
def test_terminal_errors_keep_no_worker_or_delivery_tracebacks(kind, expected_status):
    jobs = SnapshotJobs(max_result_bytes=16 if kind == "result" else 1024,
                        max_total_bytes=16 if kind == "total" else 2048)
    entered, release = Event(), Event()
    original_refs = []
    class Original:
        def __init__(self):
            self.raw = bytearray(128 * 1024)
    def build(_):
        rejected_original = Original()
        original_refs.append(weakref.ref(rejected_original))
        entered.set()
        assert release.wait(5)
        if kind == "builder":
            raise SnapshotJobError(422, "Fixture input invalid")
        return ({"blob": "x" * 128, "original_bytes": len(rejected_original.raw)},
                lambda: None, lambda: bool(rejected_original.raw))
    try:
        first = jobs.request(KEY, build)[1]["job_token"]
        assert entered.wait(2)
        second = jobs.request(KEY, build)[1]["job_token"]
    finally:
        release.set()
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        with jobs._condition:
            job = jobs._receipt_job(first)
            if job.state == "ERROR":
                stored = job.error
                break
        time.sleep(.005)
    else:
        pytest.fail("Fixture error did not finish")
    assert stored.status == expected_status
    assert stored.__traceback__ is None
    assert stored.__context__ is None and stored.__cause__ is None
    release_deadline = time.monotonic() + 2
    while original_refs[0]() is not None and time.monotonic() < release_deadline:
        time.sleep(.005)
    assert original_refs[0]() is None, "Rejected financial input retained by terminal error callbacks"
    for token in (first, second):
        with pytest.raises(SnapshotJobError) as delivered:
            jobs.request(KEY, token=token)
        assert delivered.value.status == expected_status and delivered.value is not stored
        assert stored.__traceback__ is None
        assert stored.__context__ is None and stored.__cause__ is None
    assert not jobs._jobs and not jobs._receipts


def finish(jobs, key, token, *, timeout=5):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        status, payload = jobs.request(key, token=token)
        if status == 200:
            return json.loads(payload)
        time.sleep(.005)
    pytest.fail("Fixture snapshot did not finish")


def test_worker_singleflight_and_exact_token_binding():
    jobs = SnapshotJobs()
    entered, release = Event(), Event()
    calls = []
    def build(progress):
        calls.append(1)
        progress("BUILD")
        entered.set()
        assert release.wait(5)
        return {"read_only": True, "broker_orders_sent": 0}, lambda: None
    started = time.monotonic()
    status, first = jobs.request(KEY, build)
    assert status == 202 and time.monotonic() - started < .5
    assert first["as_of"] == KEY[1]
    assert entered.wait(2)
    for _ in range(10):
        status, poll = jobs.request(KEY, token=first["job_token"])
        assert status == 202 and poll["job_token"] == first["job_token"]
        assert poll["phase"] == "BUILD" and poll["elapsed_seconds"] >= 0
    for key in (("MSFT", *KEY[1:]), (KEY[0], "2026-10-16T11:00:00Z", *KEY[2:]),
                (*KEY[:2], ASOF, KEY[3]), (*KEY[:3], 2)):
        with pytest.raises(SnapshotJobError) as error:
            jobs.request(key, token=first["job_token"])
        assert error.value.status == 400
    release.set()
    assert finish(jobs, KEY, first["job_token"]) == {"read_only": True, "broker_orders_sent": 0}
    assert calls == [1]
    with pytest.raises(SnapshotJobError) as error:
        jobs.request(KEY, token=first["job_token"])
    assert error.value.status == 410


def test_initial_callers_share_one_computation_but_consume_independent_receipts():
    jobs = SnapshotJobs()
    entered, release = Event(), Event()
    builds, guards = [], []
    def build(_):
        builds.append(1)
        entered.set()
        assert release.wait(5)
        return {"whole_original": True}, lambda: None, lambda: guards.append(1) or True
    try:
        _, first = jobs.request(KEY, build)
        assert entered.wait(2)
        _, second = jobs.request(KEY, build)
        assert first["job_token"] != second["job_token"]
    finally:
        release.set()
    assert finish(jobs, KEY, first["job_token"]) == {"whole_original": True}
    assert finish(jobs, KEY, second["job_token"]) == {"whole_original": True}
    assert builds == [1] and len(guards) == 2
    for token in (first["job_token"], second["job_token"]):
        with pytest.raises(SnapshotJobError) as error:
            jobs.request(KEY, token=token)
        assert error.value.status == 410


def test_shared_computation_cannot_bypass_global_receipt_limit_or_cancel_another_reader():
    jobs = SnapshotJobs()
    entered, release = Event(), Event()
    calls = []
    def build(_):
        calls.append(1)
        entered.set()
        assert release.wait(5)
        return {"whole_original": True}, lambda: None
    try:
        receipts = [jobs.request(KEY, build)[1]]
        assert entered.wait(2)
        receipts.extend(jobs.request(KEY, build)[1] for _ in range(3))
        assert len({r["job_token"] for r in receipts}) == 4
        assert len(jobs._jobs) == 1 and len(jobs._receipts) == 4
        with pytest.raises(SnapshotJobError) as error:
            jobs.request(KEY, build)
        assert error.value.status == 429
        jobs.cancel(KEY, receipts[0]["job_token"])
        assert len(jobs._jobs) == 1 and len(jobs._receipts) == 3
    finally:
        release.set()
    for receipt in receipts[1:]:
        assert finish(jobs, KEY, receipt["job_token"]) == {"whole_original": True}
    assert calls == [1] and not jobs._jobs and not jobs._receipts


def test_verification_is_one_transition_and_slow_verify_does_not_rebuild():
    jobs = SnapshotJobs()
    verifying, release = Event(), Event()
    builds, verifies = [], []
    def verify():
        verifies.append(1)
        verifying.set()
        assert release.wait(5)
    def build(progress):
        builds.append(1)
        return {"value": 1}, verify
    _, pending = jobs.request(KEY, build)
    token = pending["job_token"]
    deadline = time.monotonic() + 2
    while not verifying.is_set():
        status, progress = jobs.request(KEY, token=token)
        assert status == 202
        assert time.monotonic() < deadline
        time.sleep(.005)
    for _ in range(10):
        assert jobs.request(KEY, token=token)[1]["phase"] == "VERIFY"
    release.set()
    assert finish(jobs, KEY, token) == {"value": 1}
    assert builds == verifies == [1]


def test_delivery_guard_reenters_only_async_verification_and_has_a_finite_retry_budget():
    for eventually_valid in (True, False):
        jobs = SnapshotJobs()
        valid, verifies = [False], []
        def verify():
            verifies.append(1)
            if eventually_valid and len(verifies) == 2:
                valid[0] = True
        _, pending = jobs.request(KEY, lambda _: ({"whole_original": True}, verify, lambda: valid[0]))
        if eventually_valid:
            assert finish(jobs, KEY, pending["job_token"]) == {"whole_original": True}
            assert len(verifies) == 2
        else:
            with pytest.raises(SnapshotJobError) as error:
                finish(jobs, KEY, pending["job_token"])
            assert error.value.status == 422 and len(verifies) == 3
        assert not jobs._jobs


def test_only_ctime_and_shm_derived_metadata_are_excluded_from_journal_financial_stamps(tmp_path, monkeypatch):
    journal = tmp_path / "paper.sqlite"
    wal, shm = Path(str(journal) + "-wal"), Path(str(journal) + "-shm")
    for path in (journal, wal, shm):
        path.write_bytes(b"fixture")
    before = journal_fingerprint((journal,))
    original = Path.stat
    change = ["ctime_and_shm"]
    def changed(path, *args, **kwargs):
        raw = original(path, *args, **kwargs)
        fields = {name: getattr(raw, name) for name in dir(raw) if name.startswith("st_")}
        fields["st_ctime_ns"] += 1000
        if path == shm:
            for field in ("st_mtime_ns", "st_size", "st_ino"):
                fields[field] += 1000
        elif path == journal and change[0] == "financial_mtime":
            fields["st_mtime_ns"] += 1000
        elif path == wal and change[0] == "financial_size":
            fields["st_size"] += 1
        elif path == journal and change[0] == "main_identity":
            fields["st_ino"] += 1
        return SimpleNamespace(**fields)
    monkeypatch.setattr(Path, "stat", changed)
    assert journal_fingerprint((journal,)) == before
    for field in ("financial_mtime", "financial_size", "main_identity"):
        change[0] = field
        after = journal_fingerprint((journal,))
        assert after != before
        if field == "main_identity":
            assert journal_identities(after) != journal_identities(before)


def test_active_and_queued_jobs_are_bounded_and_cancellation_discards_late_result():
    jobs = SnapshotJobs(max_jobs=2)
    entered, release = Event(), Event()
    calls = []
    def slow(progress):
        calls.append("active")
        entered.set()
        assert release.wait(5)
        return {"private": "must never be delivered"}, lambda: None
    _, first = jobs.request(KEY, slow)
    assert entered.wait(2)
    other = ("MSFT", *KEY[1:])
    _, second = jobs.request(other, lambda _: pytest.fail("Cancelled queued build ran"))
    with pytest.raises(SnapshotJobError) as error:
        jobs.request(("GOOG", *KEY[1:]), slow)
    assert error.value.status == 429 and len(jobs._jobs) == 2
    jobs.cancel(other, second["job_token"])
    jobs.cancel(KEY, first["job_token"])
    with pytest.raises(SnapshotJobError) as error:
        jobs.request(KEY, token=first["job_token"])
    assert error.value.status == 410
    release.set()
    deadline = time.monotonic() + 2
    while jobs._jobs:
        assert time.monotonic() < deadline
        time.sleep(.005)
    assert calls == ["active"]


@pytest.mark.parametrize("kind,status", [("oversize", 413), ("exception", 422)])
def test_failure_does_not_reuse_or_truncate_a_previous_good_result(kind, status):
    jobs = SnapshotJobs(max_result_bytes=64)
    def build(_):
        if kind == "exception":
            raise ValueError("PRIVATE_ACCOUNT/PATH/SOURCE")
        return {"whole_evidence": "x" * 100}, lambda: None
    _, progress = jobs.request(KEY, build)
    with pytest.raises(SnapshotJobError) as error:
        finish(jobs, KEY, progress["job_token"])
    assert error.value.status == status
    assert "PRIVATE" not in error.value.message
    assert not jobs._jobs


def test_result_memory_and_terminal_retention_are_bounded():
    now = [10.]
    jobs = SnapshotJobs(max_total_bytes=32, max_result_bytes=32, retention_seconds=5, clock=lambda: now[0])
    _, first = jobs.request(KEY, lambda _: ({"text": "x" * 10}, lambda: None))
    deadline = time.monotonic() + 2
    while jobs._receipt_job(first["job_token"]).state != "READY":
        assert time.monotonic() < deadline
        time.sleep(.005)
    second_key = ("MSFT", *KEY[1:])
    _, second = jobs.request(second_key, lambda _: ({"text": "y" * 10}, lambda: None))
    with pytest.raises(SnapshotJobError) as error:
        finish(jobs, second_key, second["job_token"])
    assert error.value.status == 429
    now[0] = 16.
    with pytest.raises(SnapshotJobError) as error:
        jobs.request(KEY, token=first["job_token"])
    assert error.value.status == 410


def test_new_query_reclaims_uncollected_terminal_results_and_ready_cancel_is_immediate():
    jobs = SnapshotJobs(max_jobs=1)
    _, first = jobs.request(KEY, lambda _: ({"original": True}, lambda: None))
    deadline = time.monotonic() + 2
    while jobs._receipt_job(first["job_token"]).state != "READY":
        assert time.monotonic() < deadline
        time.sleep(.005)
    _, second = jobs.request(KEY, lambda _: ({"fresh": True}, lambda: None))
    assert first["job_token"] != second["job_token"]
    with pytest.raises(SnapshotJobError) as error:
        jobs.request(KEY, token=first["job_token"])
    assert error.value.status == 410
    while jobs._receipt_job(second["job_token"]).state != "READY":
        assert time.monotonic() < deadline
        time.sleep(.005)
    jobs.cancel(KEY, second["job_token"])
    assert not jobs._jobs


@pytest.mark.parametrize("change", ["source", "addition", "deletion", "manifest", "journal", "wal", "shm", "journal_sidecar", "boundary"])
def test_ready_result_is_revalidated_before_single_delivery(tmp_path, monkeypatch, change):
    root = tmp_path / "archive"
    directory = root / "runs/2026/source/tickers/AAPL"
    directory.mkdir(parents=True)
    evidence = directory / "chart_evidence.json"
    evidence.write_text('{"old":"whole original"}')
    manifest = directory.parent.parent / "run.json"
    manifest.write_text("{}")
    journal = tmp_path / "account.sqlite"
    journal.write_bytes(b"original journal")
    def fingerprint():
        return evidence_fingerprint(directory, root=root, manifest=manifest, journals=(journal,))
    before = fingerprint()
    jobs = SnapshotJobs()
    def build(_):
        def verify():
            if fingerprint() != before:
                raise ValueError("Changed")
        return {"whole_original": True}, verify
    _, progress = jobs.request(KEY, build)
    deadline = time.monotonic() + 2
    while jobs._receipt_job(progress["job_token"]).state != "READY":
        assert time.monotonic() < deadline
        time.sleep(.005)
    if change == "source":
        evidence.write_text('{"new":"changed data"}')
    elif change == "addition":
        (directory / "new_checkpoint.json").write_text("{}")
    elif change == "deletion":
        evidence.unlink()
    elif change == "manifest":
        manifest.write_text('{"changed":true}')
    elif change == "journal":
        journal.write_bytes(b"changed journal")
    elif change in {"wal", "shm", "journal_sidecar"}:
        Path(str(journal) + ("-journal" if change == "journal_sidecar" else "-" + change)).write_bytes(b"new sidecar")
    else:
        original = Path.resolve
        monkeypatch.setattr(Path, "resolve", lambda path, *a, **kw: tmp_path / "outside" if path == directory else original(path, *a, **kw))
    with pytest.raises(SnapshotJobError) as error:
        finish(jobs, KEY, progress["job_token"])
    assert error.value.status == 422 and not jobs._jobs


@contextmanager
def api(archive, **kwargs):
    server = ThreadingHTTPServer(("127.0.0.1", 0), module.make_handler(archive_dir=archive, **kwargs))
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    def request(route, **query):
        defaults = {} if query.pop("_omit_as_of", False) else {"as_of": ASOF}
        with urlopen(f"http://127.0.0.1:{server.server_port}" + route + "?" + urlencode({**defaults, **query}), timeout=3) as response:
            return response.status, json.load(response), response.headers
    try:
        yield request
    finally:
        server.shutdown()
        worker.join(5)
        server.server_close()


def http_finish(request, pending, *, ticker="AAPL", generation=None, **query):
    values = {"ticker": ticker, "snapshot_job": pending["job_token"],
              "catalog_generation": generation if generation is not None else pending["generation"], **query}
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        status, payload, headers = request("/api/snapshot", **values)
        if status == 200:
            return payload, headers
        assert payload["job_token"] == pending["job_token"]
        time.sleep(.005)
    pytest.fail("Fixture HTTP snapshot did not finish")


def test_http_same_catalog_cohort_builds_once_while_health_remains_available(tmp_path, monkeypatch):
    put(tmp_path)
    entered, release = Event(), Event()
    calls, scans = [], []
    original_scan = ArchiveCatalogIndex._scan
    def scan(self, *args):
        scans.append(1)
        return original_scan(self, *args)
    def slow(ticker, at, *, phase_hook, **kwargs):
        phase_hook("BUILD")
        calls.append((ticker, at))
        entered.set()
        assert release.wait(5)
        return {"ticker": ticker, "read_only": True, "broker_orders_sent": 0}
    monkeypatch.setattr(ArchiveCatalogIndex, "_scan", scan)
    monkeypatch.setattr(module, "get_replay_snapshot", slow)
    with api(tmp_path) as request:
        status, tickers, headers = request("/api/tickers")
        assert status == 200 and tickers == ["AAPL"]
        generation = int(headers["X-Archive-Catalog-Generation"])
        started = time.monotonic()
        status, pending, headers = request("/api/snapshot", ticker="AAPL", catalog_generation=generation)
        assert status == 202 and time.monotonic() - started < .5
        assert pending["generation"] == generation == int(headers["X-Archive-Catalog-Generation"])
        assert datetime.fromisoformat(pending["as_of"]) == datetime.fromisoformat(ASOF.replace("Z", "+00:00"))
        assert entered.wait(2)
        with pytest.raises(HTTPError) as wrong_cutoff:
            request("/api/snapshot", ticker="AAPL", catalog_generation=generation,
                    snapshot_job=pending["job_token"], as_of="2026-10-16T11:59:00Z")
        assert wrong_cutoff.value.code == 400
        assert request("/api/kis-strategy-health")[1]["real_orders_enabled"] is False
        assert len(scans) == len(calls) == 1
        # More than the retained two generations may complete in another tab.
        # The in-flight opaque job still binds its own original cohort.
        for _ in range(3):
            _, _, other_headers = request("/api/tickers")
            assert int(other_headers["X-Archive-Catalog-Generation"]) > generation
        for _ in range(3):
            status, same, _ = request("/api/snapshot", ticker="AAPL", catalog_generation=generation, snapshot_job=pending["job_token"])
            assert status == 202 and same["phase"] == "BUILD"
        release.set()
        payload, final_headers = http_finish(request, pending)
        assert payload["read_only"] is True and payload["source_context"]["run_id"] == "first"
        assert int(final_headers["X-Archive-Catalog-Generation"]) == generation
        assert len(scans) == 4 and len(calls) == 1
        with pytest.raises(HTTPError) as error:
            http_finish(request, pending)
        assert error.value.code == 410


def test_queued_job_keeps_its_admitted_catalog_lease_after_other_tab_refreshes(tmp_path, monkeypatch):
    put(tmp_path)
    entered, release = Event(), Event()
    calls = []
    first_anchor = "2026-10-16T09:00:00Z"
    def builder(ticker, at, *, anchor, **kwargs):
        calls.append(anchor)
        if anchor == first_anchor:
            entered.set()
            assert release.wait(5)
        return {"ticker": ticker, "anchor": anchor, "read_only": True, "broker_orders_sent": 0}
    monkeypatch.setattr(module, "get_replay_snapshot", builder)
    with api(tmp_path) as request:
        _, _, headers = request("/api/tickers")
        generation = int(headers["X-Archive-Catalog-Generation"])
        _, first, _ = request("/api/snapshot", ticker="AAPL", anchor=first_anchor, catalog_generation=generation)
        assert entered.wait(2)
        _, queued, _ = request("/api/snapshot", ticker="AAPL", catalog_generation=generation)
        assert queued["phase"] == "QUEUED"
        for _ in range(3):
            assert request("/api/tickers")[0] == 200
        release.set()
        one, _ = http_finish(request, first, anchor=first_anchor)
        two, second_headers = http_finish(request, queued)
        assert one["anchor"] == first_anchor and two["anchor"] is None
        assert int(second_headers["X-Archive-Catalog-Generation"]) == generation
        assert calls == [first_anchor, None]


@pytest.mark.parametrize("change", ["future_append", "visible_append", "visible_update", "visible_delete", "seed_update", "file_replace",
                                    "during_visible_append", "during_seed_update", "during_future_append", "during_continuous_future_append"])
def test_ready_http_snapshot_distinguishes_future_append_from_changed_visible_journal(tmp_path, monkeypatch, change):
    from tests.test_market_journal_review import producer
    from tradingagents.performance.lifecycle import append_lifecycle_event
    from tradingagents.performance import replay as replay_module
    root = tmp_path / "archive"
    producer(root, "source", "AAPL", "US")
    journal = root / "paper/us.sqlite"
    journal.parent.mkdir(parents=True)
    def record(identity, at="2026-10-16T10:30:00Z", *, seed=False):
        with closing(sqlite3.connect(journal)) as db:
            append_lifecycle_event(db, event_id=identity, signal_id=identity, kind="ACCOUNT_SEED" if seed else "SIGNAL",
                mode="paper" if seed else "recommendation", occurred_at=at, available_at=at, ingested_at=at,
                payload={"cash": 100, "positions": {}, "currency": "USD"} if seed else {"ticker": "AAPL", "action": "WAIT"})
            db.commit()
    record("seed", "2026-10-16T09:00:00Z", seed=True)
    record("original")
    jobs = SnapshotJobs()
    monkeypatch.setattr(module, "SnapshotJobs", lambda: jobs)
    original_reader, reads = replay_module.replay_action_history, []
    def counted_reader(*args, **kwargs):
        reads.append(1)
        result = original_reader(*args, **kwargs)
        if (len(reads) == 2 or change == "during_continuous_future_append" and len(reads) == 3) and change.startswith("during_"):
            # The verifier has already read its snapshot. A write before the
            # after-stamp must not promote an unexamined new DB generation.
            if change == "during_seed_update":
                with closing(sqlite3.connect(journal)) as db:
                    db.execute("DROP TRIGGER lifecycle_no_update")
                    db.execute("UPDATE lifecycle_events SET payload_json=? WHERE event_id='seed'",
                               (json.dumps({"cash": 999, "positions": {}, "currency": "USD"}),))
                    db.commit()
            else:
                record("concurrent" + str(len(reads)), at="2026-10-17T11:00:00Z" if change in {"during_future_append", "during_continuous_future_append"} else "2026-10-16T11:30:00Z")
        return result
    monkeypatch.setattr(replay_module, "replay_action_history", counted_reader)
    before = journal.read_bytes()
    with api(root, market_journals={"US": journal}) as request:
        status, pending, _ = request("/api/snapshot", ticker="AAPL")
        assert status == 202
        deadline = time.monotonic() + 5
        while jobs._receipt_job(pending["job_token"]).state != "READY":
            assert time.monotonic() < deadline
            time.sleep(.005)
        # The normal reader already completed. Only delivery validation remains.
        if change in {"future_append", "visible_append"} or change.startswith("during_"):
            record("new", at="2026-10-17T10:30:00Z" if change != "visible_append" else "2026-10-16T11:00:00Z")
        elif change == "file_replace":
            replacement = journal.with_name("replacement.sqlite")
            replacement.write_bytes(before)
            replacement.replace(journal)
        else:
            with closing(sqlite3.connect(journal)) as db:
                if change == "visible_delete":
                    db.execute("DROP TRIGGER lifecycle_no_delete")  # Fixture corruption only.
                    db.execute("DELETE FROM lifecycle_events WHERE event_id='original'")
                else:
                    db.execute("DROP TRIGGER lifecycle_no_update")
                    payload = {"cash": 999, "positions": {}, "currency": "USD"} if change == "seed_update" else {"ticker": "AAPL", "action": "BUY"}
                    db.execute("UPDATE lifecycle_events SET payload_json=? WHERE event_id=?", (json.dumps(payload), "seed" if change == "seed_update" else "original"))
                db.commit()
        if change in {"future_append", "during_future_append"}:
            payload, _ = http_finish(request, pending)
            assert {e["event_id"] for e in payload["lifecycle"]["events"]} == {"original"}
            assert payload["lifecycle"]["accounts"] == {}
            assert payload["read_only"] is True and payload["broker_orders_sent"] == 0
            assert "999" not in json.dumps(payload)
        else:
            with pytest.raises(HTTPError) as error:
                http_finish(request, pending)
            assert error.value.code == 422
        assert len(reads) == (1 if change == "file_replace" else 3 if change.startswith("during_") else 2)


def test_future_wal_append_keeps_same_cutoff_snapshot_without_modifying_wal_or_main_db(tmp_path, monkeypatch):
    from tests.test_market_journal_review import producer
    from tradingagents.performance.lifecycle import append_lifecycle_event
    root = tmp_path / "archive"
    producer(root, "source", "AAPL", "US")
    journal = root / "paper/us.sqlite"
    journal.parent.mkdir(parents=True)
    jobs = SnapshotJobs()
    monkeypatch.setattr(module, "SnapshotJobs", lambda: jobs)
    with closing(sqlite3.connect(journal)) as writer:
        assert writer.execute("PRAGMA journal_mode=WAL").fetchone()[0] == "wal"
        def record(identity, at):
            append_lifecycle_event(writer, event_id=identity, signal_id=identity, kind="SIGNAL",
                occurred_at=at, available_at=at, ingested_at=at, payload={"ticker": "AAPL", "action": "WAIT"})
            writer.commit()
        record("original", "2026-10-16T10:30:00Z")
        wal = Path(str(journal) + "-wal")
        with api(root, market_journals={"US": journal}) as request:
            _, pending, _ = request("/api/snapshot", ticker="AAPL")
            deadline = time.monotonic() + 5
            while jobs._receipt_job(pending["job_token"]).state != "READY":
                assert time.monotonic() < deadline
                time.sleep(.005)
            original_main, original_wal, identity = journal.read_bytes(), wal.read_bytes(), journal.stat().st_ino
            record("future", "2026-10-17T10:30:00Z")
            changed_wal = wal.read_bytes()
            assert changed_wal != original_wal and journal.read_bytes() == original_main
            payload, _ = http_finish(request, pending)
            assert {e["event_id"] for e in payload["lifecycle"]["events"]} == {"original"}
            assert wal.read_bytes() == changed_wal and journal.read_bytes() == original_main
            assert journal.stat().st_ino == identity


def test_readonly_wal_clone_can_create_shm_without_invalidating_unchanged_financial_evidence(tmp_path):
    from tests.test_market_journal_review import producer
    from tradingagents.performance.lifecycle import append_lifecycle_event
    root = tmp_path / "archive"
    producer(root, "source", "AAPL", "US")
    source = tmp_path / "idle-writer.sqlite"
    journal = root / "paper/us.sqlite"
    journal.parent.mkdir(parents=True)
    with closing(sqlite3.connect(source)) as writer:
        assert writer.execute("PRAGMA journal_mode=WAL").fetchone()[0] == "wal"
        append_lifecycle_event(writer, event_id="known", signal_id="known", kind="SIGNAL",
            occurred_at="2026-10-16T10:30:00Z", available_at="2026-10-16T10:30:00Z", ingested_at="2026-10-16T10:30:00Z",
            payload={"ticker": "AAPL", "action": "WAIT"})
        writer.commit()
        shutil.copyfile(source, journal)
        shutil.copyfile(Path(str(source) + "-wal"), Path(str(journal) + "-wal"))
        assert not Path(str(journal) + "-shm").exists()
        before = {path: path.read_bytes() for path in (journal, Path(str(journal) + "-wal"))}
        with api(root, market_journals={"US": journal}) as request:
            _, pending, _ = request("/api/snapshot", ticker="AAPL")
            payload, _ = http_finish(request, pending)
            assert {event["event_id"] for event in payload["lifecycle"]["events"]} == {"known"}
            assert {path: path.read_bytes() for path in before} == before


@pytest.mark.parametrize("link", ["mock", "native", "junction"])
def test_configured_file_journal_alias_uses_the_bound_target_sqlite_sidecars(tmp_path, monkeypatch, link):
    from tests.test_market_journal_review import producer
    from tradingagents.performance.lifecycle import append_lifecycle_event
    root = tmp_path / "archive"
    producer(root, "source", "AAPL", "US")
    target_dir = tmp_path / "bound"
    target_dir.mkdir()
    target, alias = target_dir / "target.sqlite", tmp_path / "alias.sqlite"
    with closing(sqlite3.connect(target)) as writer:
        assert writer.execute("PRAGMA journal_mode=WAL").fetchone()[0] == "wal"
        append_lifecycle_event(writer, event_id="known", signal_id="known", kind="SIGNAL",
            occurred_at="2026-10-16T10:30:00Z", available_at="2026-10-16T10:30:00Z", ingested_at="2026-10-16T10:30:00Z",
            payload={"ticker": "AAPL", "action": "WAIT"})
        writer.commit()
        if link == "junction":
            import sys
            if sys.platform != "win32":
                pytest.skip("Windows directory junction fixture")
            import _winapi
            alias_dir = tmp_path / "journal-alias"
            try:
                _winapi.CreateJunction(str(target_dir), str(alias_dir))
            except OSError as error:
                pytest.skip(f"Temporary junction unavailable: {error.winerror}")
            alias = alias_dir / target.name
            assert alias.resolve() == target
        elif link == "native":
            try:
                alias.symlink_to(target)
            except OSError as error:
                pytest.skip(f"Native file symlink unavailable: {error.winerror if hasattr(error, 'winerror') else error.errno}")
        else:
            alias.write_bytes(b"mock alias placeholder")
            original = Path.resolve
            monkeypatch.setattr(Path, "resolve", lambda p, *a, **kw: target if p == alias else original(p, *a, **kw))
        originals = {p: p.read_bytes() for p in (target, Path(str(target) + "-wal"))}
        with api(root, market_journals={"US": alias}) as request:
            _, pending, _ = request("/api/snapshot", ticker="AAPL")
            payload, _ = http_finish(request, pending)
            assert {event["event_id"] for event in payload["lifecycle"]["events"]} == {"known"}
            assert {p: p.read_bytes() for p in originals} == originals


@pytest.mark.parametrize("change", ["alias_retarget", "alias_cycle", "wal_escape", "future_append"])
def test_bound_alias_checks_retarget_and_sidecar_scope_without_rejecting_future_append(tmp_path, monkeypatch, change):
    from tests.test_market_journal_review import producer
    from tradingagents.performance.lifecycle import append_lifecycle_event
    root = tmp_path / "archive"
    producer(root, "source", "AAPL", "US")
    target, alias, outside = tmp_path / "bound.sqlite", tmp_path / "alias.sqlite", tmp_path / "do-not-open.sqlite"
    alias.write_bytes(b"mock configured alias")
    outside.write_bytes(b"must not be opened")
    wal = Path(str(target) + "-wal")
    changed = [False]
    original_resolve, original_lstat = Path.resolve, Path.lstat
    def resolve(path, *args, **kwargs):
        if path == alias:
            if changed[0] and change == "alias_cycle":
                raise RuntimeError("Mock alias symlink cycle")
            return outside if changed[0] and change == "alias_retarget" else target
        if path == wal and changed[0] and change == "wal_escape":
            return outside
        return original_resolve(path, *args, **kwargs)
    def lstat(path, *args, **kwargs):
        raw = original_lstat(path, *args, **kwargs)
        if path != wal or not changed[0] or change != "wal_escape":
            return raw
        fields = {name: getattr(raw, name) for name in dir(raw) if name.startswith("st_")}
        fields["st_mode"] = stat_module.S_IFLNK
        return SimpleNamespace(**fields)
    monkeypatch.setattr(Path, "resolve", resolve)
    monkeypatch.setattr(Path, "lstat", lstat)
    jobs = SnapshotJobs()
    monkeypatch.setattr(module, "SnapshotJobs", lambda: jobs)
    original_builder, received = module.get_replay_snapshot, []
    def observed(*args, **kwargs):
        received.append(kwargs["db_paths"])
        return original_builder(*args, **kwargs)
    monkeypatch.setattr(module, "get_replay_snapshot", observed)
    with closing(sqlite3.connect(target)) as writer:
        writer.execute("PRAGMA journal_mode=WAL")
        def record(identity, at):
            append_lifecycle_event(writer, event_id=identity, signal_id=identity, kind="SIGNAL", occurred_at=at,
                available_at=at, ingested_at=at, payload={"ticker": "AAPL", "action": "WAIT"})
            writer.commit()
        record("original", "2026-10-16T10:30:00Z")
        with api(root, market_journals={"US": alias}) as request:
            _, pending, _ = request("/api/snapshot", ticker="AAPL")
            token = pending["job_token"]
            deadline = time.monotonic() + 10
            while jobs._receipt_job(token).state != "READY":
                assert time.monotonic() < deadline
                time.sleep(.005)
            request("/api/snapshot", ticker="AAPL", catalog_generation=pending["generation"], snapshot_job=token)
            while jobs._receipt_job(token).state != "DELIVERY_READY":
                assert time.monotonic() < deadline
                time.sleep(.005)
            changed[0] = True
            if change == "future_append":
                record("future", "2026-10-17T10:30:00Z")
            assert request("/api/snapshot", ticker="AAPL", catalog_generation=pending["generation"], snapshot_job=token)[0] == 202
            if change == "future_append":
                payload, _ = http_finish(request, pending)
                assert {e["event_id"] for e in payload["lifecycle"]["events"]} == {"original"}
            else:
                with pytest.raises(HTTPError) as error:
                    http_finish(request, pending)
                assert error.value.code == 422
            assert received == [(target,)]


@pytest.mark.parametrize("change", ["source", "visible_append", "future_append"])
def test_second_caller_revalidates_its_receipt_after_first_caller_consumed_shared_payload(tmp_path, monkeypatch, change):
    from tests.test_market_journal_review import producer
    from tradingagents.performance.lifecycle import append_lifecycle_event
    root = tmp_path / "archive"
    producer(root, "source", "AAPL", "US")
    journal = root / "paper/us.sqlite"
    journal.parent.mkdir(parents=True)
    def record(identity, at):
        with closing(sqlite3.connect(journal)) as db:
            append_lifecycle_event(db, event_id=identity, signal_id=identity, kind="SIGNAL", occurred_at=at,
                available_at=at, ingested_at=at, payload={"ticker": "AAPL", "action": "WAIT"})
            db.commit()
    record("original", "2026-10-16T10:30:00Z")
    jobs, entered, release = SnapshotJobs(), Event(), Event()
    monkeypatch.setattr(module, "SnapshotJobs", lambda: jobs)
    original_builder, builds = module.get_replay_snapshot, []
    def held(*args, **kwargs):
        result = original_builder(*args, **kwargs)
        builds.append(1)
        entered.set()
        assert release.wait(5)
        return result
    monkeypatch.setattr(module, "get_replay_snapshot", held)
    with api(root, market_journals={"US": journal}) as request:
        try:
            _, first, _ = request("/api/snapshot", ticker="AAPL")
            assert entered.wait(3)
            _, second, _ = request("/api/snapshot", ticker="AAPL", catalog_generation=first["generation"])
            assert first["job_token"] != second["job_token"]
            assert len(jobs._jobs) == 1 and len(jobs._receipts) == 2
        finally:
            release.set()
        first_payload, _ = http_finish(request, first)
        assert {e["event_id"] for e in first_payload["lifecycle"]["events"]} == {"original"}
        shared_bytes = jobs._receipt_job(second["job_token"]).payload
        assert len(jobs._jobs) == 1 and sum(len(j.payload) for j in jobs._jobs.values()) == len(shared_bytes)
        if change == "source":
            (root / "runs/2026/source/tickers/AAPL/analysis.json").write_text('{"changed":true}')
        else:
            record("new", "2026-10-17T10:30:00Z" if change == "future_append" else "2026-10-16T11:00:00Z")
        assert request("/api/snapshot", ticker="AAPL", catalog_generation=second["generation"], snapshot_job=second["job_token"])[0] == 202
        if change == "future_append":
            payload, _ = http_finish(request, second)
            assert payload == first_payload
        else:
            with pytest.raises(HTTPError) as error:
                http_finish(request, second)
            assert error.value.code == 422
        assert builds == [1] and not jobs._jobs and not jobs._receipts


@pytest.mark.parametrize("change", ["source", "visible_append", "future_append"])
def test_delivery_ready_result_is_invalidated_again_before_actual_200(tmp_path, monkeypatch, change):
    from tests.test_market_journal_review import producer
    from tradingagents.performance.lifecycle import append_lifecycle_event
    root = tmp_path / "archive"
    producer(root, "source", "AAPL", "US")
    journal = root / "paper/us.sqlite"
    journal.parent.mkdir(parents=True)
    def record(identity, at):
        with closing(sqlite3.connect(journal)) as db:
            append_lifecycle_event(db, event_id=identity, signal_id=identity, kind="SIGNAL",
                occurred_at=at, available_at=at, ingested_at=at, payload={"ticker": "AAPL", "action": "WAIT"})
            db.commit()
    record("original", "2026-10-16T10:30:00Z")
    jobs = SnapshotJobs()
    monkeypatch.setattr(module, "SnapshotJobs", lambda: jobs)
    with api(root, market_journals={"US": journal}) as request:
        _, pending, _ = request("/api/snapshot", ticker="AAPL")
        token = pending["job_token"]
        deadline = time.monotonic() + 10
        while jobs._receipt_job(token).state != "READY":
            assert time.monotonic() < deadline
            time.sleep(.005)
        assert request("/api/snapshot", ticker="AAPL", catalog_generation=pending["generation"], snapshot_job=token)[0] == 202
        while jobs._receipt_job(token).state != "DELIVERY_READY":
            assert time.monotonic() < deadline
            time.sleep(.005)
        if change == "source":
            (root / "runs/2026/source/tickers/AAPL/analysis.json").write_text('{"changed":true}')
        else:
            record("new", "2026-10-17T10:30:00Z" if change == "future_append" else "2026-10-16T11:00:00Z")
        # This request must never do the expensive validation synchronously or
        # deliver a previously-ready payload before seeing the new evidence.
        status, again, _ = request("/api/snapshot", ticker="AAPL", catalog_generation=pending["generation"], snapshot_job=token)
        assert status == 202 and again["phase"] == "VERIFY"
        if change == "future_append":
            payload, _ = http_finish(request, pending)
            assert {event["event_id"] for event in payload["lifecycle"]["events"]} == {"original"}
        else:
            with pytest.raises(HTTPError) as error:
                http_finish(request, pending)
            assert error.value.code == 422


@pytest.mark.parametrize("when", ["before_build", "after_ready"])
def test_derived_shm_reparse_escape_is_rejected_before_read_and_before_delivery(tmp_path, monkeypatch, when):
    from tests.test_market_journal_review import producer
    root = tmp_path / "archive"
    producer(root, "source", "AAPL", "US")
    journal = root / "paper/us.sqlite"
    journal.parent.mkdir(parents=True)
    with closing(sqlite3.connect(journal)):
        pass
    shm = Path(str(journal) + "-shm")
    shm.write_bytes(b"derived fixture index")
    escaped = [when == "before_build"]
    original_resolve, original_lstat = Path.resolve, Path.lstat
    def resolve(path, *args, **kwargs):
        return tmp_path / "outside" if path == shm and escaped[0] else original_resolve(path, *args, **kwargs)
    def lstat(path, *args, **kwargs):
        raw = original_lstat(path, *args, **kwargs)
        if path != shm or not escaped[0]:
            return raw
        fields = {name: getattr(raw, name) for name in dir(raw) if name.startswith("st_")}
        fields["st_mode"] = stat_module.S_IFLNK
        fields["st_file_attributes"] = 0x400
        fields["st_reparse_tag"] = 0xA000000C
        return SimpleNamespace(**fields)
    monkeypatch.setattr(Path, "resolve", resolve)
    monkeypatch.setattr(Path, "lstat", lstat)
    jobs = SnapshotJobs()
    monkeypatch.setattr(module, "SnapshotJobs", lambda: jobs)
    with api(root, market_journals={"US": journal}) as request:
        _, pending, _ = request("/api/snapshot", ticker="AAPL")
        if when == "after_ready":
            token = pending["job_token"]
            deadline = time.monotonic() + 10
            while jobs._receipt_job(token).state != "READY":
                assert time.monotonic() < deadline
                time.sleep(.005)
            request("/api/snapshot", ticker="AAPL", catalog_generation=pending["generation"], snapshot_job=token)
            while jobs._receipt_job(token).state != "DELIVERY_READY":
                assert time.monotonic() < deadline
                time.sleep(.005)
            escaped[0] = True
        with pytest.raises(HTTPError) as error:
            http_finish(request, pending)
        assert error.value.code == 422


@pytest.mark.parametrize("query", [{"ticker": ".."}, {"ticker": "AAPL", "as_of": "bad"},
    {"ticker": "AAPL", "as_of": "2099-01-01T00:00:00Z"}, {"ticker": "AAPL", "anchor": "bad"},
    {"ticker": "AAPL", "anchor": "2026-10-17T00:00:00Z"}, {"ticker": "AAPL", "snapshot_job": "../secret", "catalog_generation": 1},
    {"ticker": "AAPL", "snapshot_cancel": "1"}, {"ticker": "AAPL", "_omit_as_of": True}])
def test_http_invalid_future_or_forged_queries_do_not_build(tmp_path, monkeypatch, query):
    put(tmp_path)
    jobs = SnapshotJobs()
    monkeypatch.setattr(module, "SnapshotJobs", lambda: jobs)
    monkeypatch.setattr(module, "get_replay_snapshot", lambda *a, **kw: pytest.fail("Invalid query built"))
    with api(tmp_path) as request:
        with pytest.raises(HTTPError) as error:
            request("/api/snapshot", **query)
        assert error.value.code == 400
        assert not jobs._jobs


def test_completed_catalog_generation_is_bounded_and_not_cross_returned(tmp_path):
    put(tmp_path)
    index = ArchiveCatalogIndex(tmp_path)
    first, original = index.snapshot_with_generation(wait_seconds=5)
    put(tmp_path, "second", started_at="2026-10-16T10:30:00Z", finished_at="2026-10-16T11:00:00Z")
    second, changed = index.snapshot_with_generation(wait_seconds=5)
    assert first != second and original != changed
    assert index.snapshot_with_generation(generation=first) == (first, original)
    index.snapshot_with_generation(wait_seconds=5)
    with pytest.raises(ValueError, match="stale"):
        index.snapshot_with_generation(generation=first)
    assert len(index._completed) == 2


def test_optional_phase_hook_does_not_change_snapshot_contract(tmp_path):
    from tests.test_integrated_chart_review import ticker_archive
    from tradingagents.charting.snapshot import get_replay_snapshot
    ticker_archive(tmp_path)
    directory = tmp_path / "tickers/TEST"
    phases = []
    before = {p: p.read_bytes() for p in directory.rglob("*") if p.is_file()}
    cutoff = datetime(2026, 10, 16, 12, tzinfo=timezone.utc)
    original = get_replay_snapshot("TEST", cutoff, ticker_dir=directory)
    observed = get_replay_snapshot("TEST", cutoff, ticker_dir=directory, phase_hook=phases.append)
    assert observed == original and phases == ["REPLAY", "BUILD"]
    assert {p: p.read_bytes() for p in before} == before
