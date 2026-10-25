"""A review can share research evidence, but never two paper account journals."""
from contextlib import contextmanager
from http.server import ThreadingHTTPServer
import json
from threading import Thread
import time
from unittest.mock import Mock
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

import pytest

from tradingagents.charting import server as review_server
from tradingagents.charting.server import make_handler
from tradingagents.performance.lifecycle import append_lifecycle_event
from tradingagents.performance.replay import replay_action_history


ASOF = "2026-10-16T12:00:00Z"
KR = "000100.KS"
US = "AAPL"


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def producer(archive, name, ticker, market, **changes):
    directory = archive / "runs/2026" / name
    write(directory / "run.json", {"run_id": name, "status": "success",
        "started_at": "2026-10-16T09:00:00Z", "finished_at": "2026-10-16T10:00:00Z",
        "settings": {"market": market}, "tickers": [{"ticker": ticker, "status": "success"}], **changes})
    write(directory / "tickers" / ticker / "analysis.json", {"finished_at": "2026-10-16T10:00:00Z"})


def event(path, identity, *, ticker, at="2026-10-16T10:30:00Z", action="WAIT"):
    append_lifecycle_event(path, event_id=identity, signal_id=identity, kind="SIGNAL",
        occurred_at=at, available_at=at, ingested_at=at, payload={"ticker": ticker, "action": action})


@pytest.fixture
def archive(tmp_path):
    root = tmp_path / "archive"
    producer(root, "kr-source", KR, "kr")
    producer(root, "us-source", US, "us")
    tracker, kr, us = (root / "performance.sqlite", root / "paper/kr.sqlite", root / "paper/us.sqlite")
    for market, ticker, journal, seed_at in (
        ("KR", KR, kr, "2026-10-16T09:00:00Z"),
        ("US", US, us, "2026-10-16T09:01:00Z"),
    ):
        append_lifecycle_event(journal, event_id="paper:account_seed", signal_id="seed:" + market,
            kind="ACCOUNT_SEED", mode="paper", occurred_at=seed_at, available_at=seed_at,
            ingested_at=seed_at, payload={"cash": 123456789, "positions": {"PRIVATE_OTHER_POSITION": 17}, "currency": "KRW"})
        event(journal, "paper-signal-" + market, ticker=ticker)
        event(tracker, "tracker-signal-" + market, ticker=ticker)
    return root, tracker, {"KR": kr, "US": us}


@contextmanager
def api(root, **kwargs):
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(archive_dir=root, **kwargs))
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    base = f"http://127.0.0.1:{server.server_port}"
    def get(route, **values):
        query = {"as_of": ASOF, **values}
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            with urlopen(base + route + "?" + urlencode(query), timeout=5) as response:
                payload = json.load(response)
                if response.status != 202:
                    return payload
            query["catalog_generation"] = payload["generation"]
            if payload.get("status") == "SNAPSHOT_BUILDING":
                query["snapshot_job"] = payload["job_token"]
            time.sleep(.01)
        pytest.fail("Fixture catalog did not finish")
    try:
        yield get
    finally:
        server.shutdown()
        worker.join(timeout=5)
        server.server_close()


def test_same_currency_seed_collision_is_real_and_replay_still_rejects_it(archive):
    root, tracker, markets = archive
    with pytest.raises(ValueError, match="Conflicting lifecycle evidence across journals"):
        replay_action_history([tracker, *markets.values()], analysis_as_of=ASOF, ticker=KR)
    with api(root, db_paths=[tracker, *markets.values()]) as get:
        with pytest.raises(HTTPError) as error:
            get("/api/snapshot", ticker=KR)
        assert error.value.code == 422


@pytest.mark.parametrize("market,ticker", [("KR", KR), ("US", US)])
def test_market_scoped_snapshot_uses_only_its_account_and_common_tracker(archive, market, ticker, monkeypatch):
    root, tracker, markets = archive
    before = {path: path.read_bytes() for path in (tracker, *markets.values())}
    original = review_server.get_replay_snapshot
    received = []
    def snapshot(*args, **kwargs):
        received.append(tuple(kwargs["db_paths"]))
        return original(*args, **kwargs)
    monkeypatch.setattr(review_server, "get_replay_snapshot", snapshot)
    with api(root, db_paths=[tracker], market_journals=markets) as get:
        # Query strings cannot select a different market, account or journal.
        payload = get("/api/snapshot", ticker=ticker, market="US" if market == "KR" else "KR",
                      journal="PRIVATE_OTHER_JOURNAL")
        assert payload["ticker"] == ticker
        assert payload["read_only"] and payload["broker_orders_sent"] == 0
        assert payload["source_context"]["market"].upper() == market
        assert received == [(tracker, markets[market])]
        assert {row["event_id"] for row in payload["lifecycle"]["events"]} == {
            "tracker-signal-" + market, "paper-signal-" + market}
        assert payload["lifecycle"]["accounts"] == {}
        encoded = json.dumps(payload)
        assert "PRIVATE_OTHER_POSITION" not in encoded and "123456789" not in encoded
        assert "PRIVATE_OTHER_JOURNAL" not in encoded and str(root) not in encoded
        assert get("/api/context")["journal_sources_configured"] == 3
    assert {path: path.read_bytes() for path in before} == before


@pytest.mark.parametrize("market", [None, "", "OTHER", "US"])
def test_unknown_or_wrong_source_market_is_rejected_before_journal_access(archive, monkeypatch, market):
    root, tracker, markets = archive
    producer(root, "kr-source", KR, market)
    read = Mock(side_effect=AssertionError("Unverified market opened a journal"))
    monkeypatch.setattr(review_server, "get_replay_snapshot", read)
    with api(root, db_paths=[tracker], market_journals=markets) as get:
        with pytest.raises(HTTPError) as error:
            get("/api/snapshot", ticker=KR)
        assert error.value.code == 422
        assert error.value.read().decode() == "Archive journal market scope unverified"
    read.assert_not_called()


def test_missing_market_mapping_never_falls_back_to_another_account(archive, monkeypatch):
    root, tracker, markets = archive
    read = Mock(side_effect=AssertionError("Wrong account fallback"))
    monkeypatch.setattr(review_server, "get_replay_snapshot", read)
    with api(root, db_paths=[tracker], market_journals={"US": markets["US"]}) as get:
        with pytest.raises(HTTPError) as error:
            get("/api/snapshot", ticker=KR)
        assert error.value.code == 422
    read.assert_not_called()


@pytest.mark.parametrize("mapping", [{}, {"kr": "kr.sqlite"}, {"EU": "eu.sqlite"},
                                     {"KR": "same.sqlite", "US": "same.sqlite"}])
def test_invalid_or_shared_account_mappings_are_not_accepted(tmp_path, mapping):
    with pytest.raises(ValueError):
        make_handler(archive_dir=tmp_path, market_journals=mapping)


def test_explicit_single_account_legacy_configuration_keeps_working(archive):
    root, tracker, markets = archive
    # Legacy caller already chooses one account. No implicit market required.
    producer(root, "kr-source", KR, None)
    with api(root, db_paths=[tracker, markets["KR"]]) as get:
        payload = get("/api/snapshot", ticker=KR)
    assert payload["ticker"] == KR
    assert len(payload["lifecycle"]["events"]) == 2


def test_future_source_and_lifecycle_cannot_change_a_past_market_projection(archive):
    root, tracker, markets = archive
    with api(root, db_paths=[tracker], market_journals=markets) as get:
        before = get("/api/snapshot", ticker=KR)
        event(markets["KR"], "future-kr", ticker=KR, at="2026-10-17T10:30:00Z", action="BUY")
        producer(root, "future-wrong-market", KR, "US", started_at="2026-10-17T09:00:00Z",
                 finished_at="2026-10-17T10:00:00Z")
        after = get("/api/snapshot", ticker=KR)
        assert after == before
        assert after["source_context"]["run_id"] == "kr-source"


@pytest.mark.parametrize("as_of", ["bad", "2026-10-16T12:00:00", "2099-01-01T00:00:00Z"])
def test_unknown_naive_and_future_request_cutoff_is_rejected(archive, as_of):
    root, tracker, markets = archive
    with api(root, db_paths=[tracker], market_journals=markets) as get:
        with pytest.raises(HTTPError) as error:
            get("/api/snapshot", ticker=KR, as_of=as_of)
        assert error.value.code == 400


def test_cli_keeps_single_account_option_and_adds_explicit_market_journals(archive, monkeypatch):
    root, tracker, markets = archive
    serve = Mock()
    monkeypatch.setattr(review_server, "serve", serve)
    assert review_server.main(["--archive-dir", str(root), "--journal", str(tracker),
        "--paper-journal-kr", str(markets["KR"]), "--paper-journal-us", str(markets["US"])]) == 0
    assert serve.call_args.kwargs["db_paths"] == [tracker]
    assert serve.call_args.kwargs["market_journals"] == markets
    serve.reset_mock()
    assert review_server.main(["--archive-dir", str(root), "--journal", str(markets["KR"])]) == 0
    assert serve.call_args.kwargs["db_paths"] == [markets["KR"]]
    assert serve.call_args.kwargs["market_journals"] is None


def test_installed_review_lane_uses_tracker_plus_exact_market_binding(tmp_path, monkeypatch):
    from tradingagents import local_automation
    import sys
    serve = Mock()
    monkeypatch.setattr(review_server, "serve", serve)
    monkeypatch.setattr(local_automation, "prepare_environment", lambda: None)
    root, state, runtime = (tmp_path / name for name in ("archive", "state", "work"))
    monkeypatch.setattr(sys, "argv", ["local_automation", "review", "--archive-dir", str(root),
                                    "--state-dir", str(state), "--runtime-dir", str(runtime)])
    assert local_automation.main() == 0
    assert serve.call_args.kwargs["db_paths"] == [root.resolve() / "performance.sqlite"]
    assert serve.call_args.kwargs["market_journals"] == {
        "KR": root.resolve() / "paper/kr.sqlite", "US": root.resolve() / "paper/us.sqlite"}
    assert serve.call_args.kwargs["strategy_ledger_dir"] == state.resolve() / "kis-strategy"


@pytest.mark.parametrize("bad_schema", [False, True])
def test_replay_reader_releases_database_handles_without_gc(tmp_path, bad_schema):
    import sqlite3
    from tradingagents.performance.lifecycle import initialize_lifecycle
    path = tmp_path / "one-account.sqlite"
    db = sqlite3.connect(path)
    if bad_schema:
        db.execute("CREATE TABLE lifecycle_events(event_id TEXT)")
    else:
        initialize_lifecycle(db)
    db.commit()
    db.close()
    if bad_schema:
        with pytest.raises(sqlite3.DatabaseError):
            replay_action_history(path, analysis_as_of=ASOF, ticker=KR)
    else:
        replay_action_history(path, analysis_as_of=ASOF, ticker=KR)
    # A reader context manager alone does not close SQLite on Windows.
    path.rename(tmp_path / "released-account.sqlite")
