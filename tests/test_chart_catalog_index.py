"""Large-archive discovery stays bounded, dynamic, and point-in-time safe."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
import json
from threading import Event, Thread
import time
from urllib.request import urlopen

import pytest

from tradingagents.charting import catalog_index as module
from tradingagents.charting.catalog_index import ArchiveCatalogIndex, CatalogPending
from tradingagents.charting.operations import archive_catalog
from tradingagents.charting.server import make_handler


ASOF = "2026-10-16T12:00:00Z"


def put(root, name="first", **changes):
    directory = root / "runs" / "2026" / name
    ticker = directory / "tickers" / "AAPL"
    ticker.mkdir(parents=True, exist_ok=True)
    raw = {"run_id": name, "status": "success", "started_at": "2026-10-16T09:00:00Z",
           "finished_at": "2026-10-16T10:00:00Z", "settings": {"market": "US"},
           "tickers": [{"ticker": "AAPL", "status": "success", "large_graph": "x" * 10000}],
           "large_unused_state": "y" * 10000, **changes}
    path = directory / "run.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    return path


def select(index, **kwargs):
    return archive_catalog(index.root.parent, analysis_as_of=kwargs.pop("as_of", ASOF),
                           manifest_entries=index.snapshot(wait_seconds=5), names_only=True, **kwargs)


def test_projection_retains_no_graph_and_unchanged_manifests_are_not_reparsed(tmp_path, monkeypatch):
    path = put(tmp_path)
    index = ArchiveCatalogIndex(tmp_path)
    first = index.snapshot(wait_seconds=5)
    assert len(json.dumps(first[0][1])) < 400
    monkeypatch.setattr(module, "project_manifest", lambda path: pytest.fail("Unchanged bytes reparsed"))
    assert index.snapshot(wait_seconds=5) == first
    path.unlink()
    assert index.snapshot(wait_seconds=5) == ()


@pytest.mark.parametrize("changes", [
    {"finished_at": "2026-10-17T10:00:00Z"}, {"finished_at": None},
    {"finished_at": "bad"}, {"finished_at": "2026-10-16T10:00:00"},
    {"started_at": "2026-10-16T11:00:00Z"}, {"status": "running"}, {"run_id": "wrong"}])
def test_rewrite_invalidates_old_valid_projection(tmp_path, changes):
    put(tmp_path)
    index = ArchiveCatalogIndex(tmp_path)
    assert set(select(index)) == {"AAPL"}
    put(tmp_path, **changes)
    assert select(index) == {}


def test_rewrites_additions_and_reversed_cutoffs_do_not_leak_future(tmp_path):
    put(tmp_path)
    index = ArchiveCatalogIndex(tmp_path)
    assert "first" in str(select(index)["AAPL"]["ticker_dir"])
    put(tmp_path, "second", started_at="2026-10-16T10:30:00Z", finished_at="2026-10-16T11:00:00Z")
    assert "second" in str(select(index)["AAPL"]["ticker_dir"])
    assert "first" in str(select(index, as_of="2026-10-16T10:10:00Z")["AAPL"]["ticker_dir"])
    (tmp_path / "runs/2026/second/run.json").write_text("{")
    assert "first" in str(select(index)["AAPL"]["ticker_dir"])


def test_names_do_not_read_analysis_or_coverage(tmp_path, monkeypatch):
    put(tmp_path)
    from tradingagents.charting import operations
    monkeypatch.setattr(operations, "_json", lambda path: pytest.fail("Names opened analysis"))
    monkeypatch.setattr(operations, "known_artifacts", lambda *a: pytest.fail("Names opened coverage"))
    assert set(select(ArchiveCatalogIndex(tmp_path))) == {"AAPL"}


def test_simultaneous_queries_and_polling_share_one_scan(tmp_path, monkeypatch):
    put(tmp_path)
    entered, release = Event(), Event()
    original = module.project_manifest
    calls = []
    def slow(path):
        calls.append(path)
        entered.set()
        assert release.wait(5)
        return original(path)
    monkeypatch.setattr(module, "project_manifest", slow)
    index = ArchiveCatalogIndex(tmp_path)
    def request():
        with pytest.raises(CatalogPending) as pending:
            index.snapshot(wait_seconds=0.01)
        return pending.value.progress
    try:
        with ThreadPoolExecutor(max_workers=8) as pool:
            progress = list(pool.map(lambda _: request(), range(8)))
        assert entered.is_set() and len(calls) == 1
        assert {p["generation"] for p in progress} == {1}
    finally:
        release.set()
    assert index.snapshot(generation=1, wait_seconds=5)
    assert index.snapshot(generation=1, wait_seconds=5)
    assert len(calls) == 1


def test_slow_catalog_returns_progress_without_blocking_operational_health(tmp_path, monkeypatch):
    put(tmp_path)
    original = module.project_manifest
    release = Event()
    def slow(path):
        assert release.wait(5)
        return original(path)
    monkeypatch.setattr(module, "project_manifest", slow)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(archive_dir=tmp_path))
    Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        started = time.monotonic()
        with urlopen(base + "/api/tickers") as response:
            assert response.status == 202
            progress = json.load(response)
        assert time.monotonic() - started < 2
        assert json.load(urlopen(base + "/api/kis-strategy-health"))["real_orders_enabled"] is False
        release.set()
        deadline = time.monotonic() + 5
        while True:
            with urlopen(base + f"/api/tickers?catalog_generation={progress['generation']}") as response:
                data = json.load(response)
                if response.status == 200:
                    assert data == ["AAPL"]
                    break
            assert time.monotonic() < deadline
    finally:
        release.set()
        server.shutdown()
        server.server_close()


def test_changed_during_read_does_not_enter_index(tmp_path, monkeypatch):
    path = put(tmp_path)
    real = module.signature
    stamps = iter([real(path), (0, 0, 0, 0)])
    monkeypatch.setattr(module, "signature", lambda _: next(stamps))
    with pytest.raises(ValueError, match="changed"):
        module.project_manifest(path)


def test_another_tab_poll_does_not_restart_completed_generation(tmp_path):
    put(tmp_path)
    index = ArchiveCatalogIndex(tmp_path)
    index.snapshot(wait_seconds=5)
    first_generation = index._generation
    index.snapshot(wait_seconds=5)  # Another tab's fresh request completes gen2.
    assert index._generation == first_generation + 1
    assert index.snapshot(generation=first_generation, wait_seconds=0)
    assert index._generation == first_generation + 1


@pytest.mark.parametrize("ticker", ["..", "../../escape", "C:/escape", "foo\\bar"])
def test_invalid_ticker_paths_are_excluded(tmp_path, ticker):
    put(tmp_path, tickers=[{"ticker": ticker, "status": "success"}])
    assert select(ArchiveCatalogIndex(tmp_path)) == {}


def test_cutoff_requires_aware_timestamp(tmp_path):
    with pytest.raises(ValueError):
        archive_catalog(tmp_path, analysis_as_of=datetime.now())
    assert archive_catalog(tmp_path, analysis_as_of=datetime.now(timezone.utc)) == {}


@pytest.mark.parametrize("error", [BrokenPipeError, ConnectionResetError, ConnectionAbortedError])
def test_cancelled_client_does_not_trigger_a_second_reply(tmp_path, error):
    handler_type = make_handler(archive_dir=tmp_path)
    handler = object.__new__(handler_type)
    statuses = []
    handler.send_response = lambda code: statuses.append(code)
    handler.send_header = lambda *a: None
    def disconnected():
        raise error("Client cancelled")
    handler.end_headers = disconnected
    handler.reply(200, "data", "text/plain")
    assert statuses == [200]
