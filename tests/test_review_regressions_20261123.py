from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import date, datetime, timedelta, timezone
import json
import sqlite3
from threading import Event
from types import SimpleNamespace
from unittest.mock import Mock

import pandas as pd
import pytest

from tradingagents.dataflows import interface, intraday_market, naver_news
from tradingagents.dataflows.config import run_config
from tradingagents.dataflows.intraday import kis_quotes, providers as intraday_providers
from tradingagents.dataflows.vendor_exceptions import VendorInputError, VendorUnavailableError
from tradingagents.performance import action_outcomes
from tradingagents.scheduled import runner
from tradingagents.scheduled.config import load_scheduled_config
from tradingagents.schemas import IntradayMarketSnapshot
from tradingagents.work import handoff, site


NOW = datetime(2026, 10, 2, 13, 30, tzinfo=timezone.utc)


@pytest.mark.parametrize("seconds,allowed", [(1, True), (9, False)])
def test_live_intraday_uses_receipt_clock_and_rejects_future_quote(monkeypatch, seconds, allowed):
    received = [False]

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return (NOW + timedelta(seconds=2 if received[0] else 0)).astimezone(tz)

    def fetch(*args, **kwargs):
        received[0] = True
        return IntradayMarketSnapshot(
            ticker="AAPL", asof=(NOW + timedelta(seconds=seconds)).isoformat(), provider="fixture",
            interval="5m", last_price=100, session_vwap=None, day_high=100, day_low=100,
            volume=10, avg20_daily_volume=None, relative_volume=None,
        )

    monkeypatch.setattr("datetime.datetime", Clock)
    monkeypatch.setattr(intraday_providers, "datetime", Clock)
    monkeypatch.setattr(intraday_market, "get_intraday_provider", lambda _: SimpleNamespace(fetch=fetch))
    with run_config({"analysis_as_of": NOW.date().isoformat()}):
        if allowed:
            assert intraday_market.fetch_intraday_market_snapshot("AAPL", provider="fixture").last_price == 100
        else:
            with pytest.raises(VendorUnavailableError, match="exceeds analysis_as_of"):
                intraday_market.fetch_intraday_market_snapshot("AAPL", provider="fixture")


@pytest.mark.parametrize("fields", [{}, {"stck_bsop_date": "20261002", "stck_cntg_hour": "996000"}])
def test_kis_quote_requires_original_trade_clock(monkeypatch, fields):
    client = Mock()
    client.request_json.return_value = ({"output": {"stck_prpr": "100", **fields}}, {})
    monkeypatch.setattr(kis_quotes.KisClient, "from_api_keys", lambda **_: client)
    with run_config({}), pytest.raises(VendorUnavailableError, match="verifiable trade date or time"):
        kis_quotes.KISQuoteProvider().fetch("005930.KS")


def test_dated_kis_quote_preserves_delay_and_closed_session(monkeypatch):
    closed = datetime.fromisoformat("2026-10-03T10:00:00+09:00")

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return closed.astimezone(tz)

    monkeypatch.setattr(kis_quotes, "datetime", Clock)
    client = Mock()
    client.request_json.return_value = ({"output": {
        "stck_prpr": "100", "stck_bsop_date": "20261002", "stck_cntg_hour": "153000",
    }}, {})
    monkeypatch.setattr(kis_quotes.KisClient, "from_api_keys", lambda **_: client)
    with run_config({}):
        quote = kis_quotes.KISQuoteProvider().fetch("005930.KS")
    assert quote.asof == "2026-10-02T15:30:00+09:00"
    assert quote.quote_delay_seconds == 66_600
    assert quote.market_session == "closed"
    assert intraday_market.classify_execution_market_data(quote) == "STALE_INVALID_FOR_EXECUTION"


@pytest.mark.parametrize("cutoff", ["2026-10-02T00:30:00+09:00", datetime.fromisoformat("2026-10-02T00:30:00+09:00")])
def test_news_tool_uses_exchange_day_and_exact_clock_on_fallback(monkeypatch, cutoff):
    monkeypatch.setattr(naver_news, "_get_headers", dict)
    response = Mock()
    response.json.return_value = {"items": [
        {"title": "on time", "pubDate": "Fri, 02 Oct 2026 00:15:00 +0900"},
        {"title": "future", "pubDate": "Fri, 02 Oct 2026 00:45:00 +0900"},
        {"title": "undated"},
        {"title": "invalid", "pubDate": "never"},
        {"title": "unverified timezone", "pubDate": "Fri, 02 Oct 2026 00:25:00 -0000"},
        None,
    ]}
    monkeypatch.setattr(naver_news.requests, "get", Mock(return_value=response))
    providers = {"primary": Mock(return_value="No news found"), "naver": naver_news.get_company_news_naver}
    monkeypatch.setitem(interface.VENDOR_METHODS, "get_company_news", providers)
    monkeypatch.setattr(interface, "_prioritize_market_specific_vendors", lambda _method, chain, *_: chain)
    with run_config({"analysis_as_of": cutoff, "tool_vendors": {"get_company_news": "primary,naver"}}):
        report = interface.route_to_vendor("get_company_news", "005930.KS", "2026-10-02", "2026-10-02")
        assert "on time" in report
        assert all(title not in report for title in ("future", "undated", "invalid", "unverified timezone"))
        with pytest.raises(VendorInputError, match="exceeds"):
            interface.route_to_vendor("get_company_news", "005930.KS", "2026-10-02", "2026-10-03")
    providers["primary"].assert_called_once()


def _config(tmp_path):
    path = tmp_path / "scheduled.toml"
    path.write_text('[run]\ntickers=["AAPL"]\ntimezone="UTC"\nmarket="US"\n'
                    '[storage]\narchive_dir="./archive"\nsite_dir="./site"\n', encoding="utf-8")
    return load_scheduled_config(path)


@pytest.mark.parametrize("bad_close", [None, float("inf"), 0])
def test_scheduled_strict_trade_date_waits_for_valid_completed_price(monkeypatch, tmp_path, bad_close):
    monkeypatch.setattr(runner, "datetime", Mock(now=Mock(return_value=NOW)))
    monkeypatch.setattr(runner, "_expected_completed_daily_trade_date", Mock(return_value=date(2026, 10, 1)))
    rows = pd.DataFrame({"Close": [100, bad_close, 999, 999]},
                        index=pd.to_datetime(["2026-09-30", "2026-10-01", None, "2026-10-02"]))
    monkeypatch.setattr(runner, "_fetch_recent_trade_date_history", Mock(return_value=rows))
    with pytest.raises(RuntimeError, match="Refusing stale"):
        runner.resolve_trade_date("AAPL", _config(tmp_path))


def test_same_second_scheduled_runs_own_separate_directories(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "datetime", Mock(now=Mock(return_value=NOW)))
    monkeypatch.setattr(runner, "_execute_run_body", lambda _config, **kw: kw["run_dir"])
    config = _config(tmp_path)
    with ThreadPoolExecutor(max_workers=2) as pool:
        directories = list(pool.map(lambda _: runner.execute_scheduled_run(config), range(2)))
    assert directories[0] != directories[1]
    assert all(directory.is_dir() for directory in directories)


def test_same_run_retry_records_one_recommendation_and_signal(tmp_path, monkeypatch):
    run_dir = tmp_path / "run"
    scanner = run_dir / "scanner"
    scanner.mkdir(parents=True)
    (run_dir / "run.json").write_text(json.dumps({"run_id": "fixture", "finished_at": NOW.isoformat()}))
    (scanner / "scanner_candidates.json").write_text(json.dumps({"candidates": [{"ticker": "AAPL"}]}))
    db = tmp_path / "performance.sqlite"
    action_outcomes.initialize_action_tracker(db)
    read_first, allow_insert = Event(), Event()
    exists = action_outcomes._recommendation_exists

    def pause_first_read(conn, row):
        result = exists(conn, row)
        if not read_first.is_set():
            read_first.set()
            assert allow_insert.wait(2)
        return result

    monkeypatch.setattr(action_outcomes, "_recommendation_exists", pause_first_read)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(action_outcomes.record_run_recommendations, run_dir, db, recorded_at=NOW.isoformat())
        if not read_first.wait(5):
            first.result(timeout=1)
            pytest.fail("The recommendation did not reach the deduplication check")
        second = pool.submit(action_outcomes.record_run_recommendations, run_dir, db, recorded_at=NOW.isoformat())
        try:
            with pytest.raises(TimeoutError):
                second.result(timeout=0.3)
        finally:
            allow_insert.set()
        assert sorted([first.result(), second.result()]) == [0, 1]
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM action_recommendations").fetchone() == (1,)
        assert conn.execute("SELECT COUNT(*) FROM lifecycle_events WHERE kind='SIGNAL'").fetchone() == (1,)


def test_late_old_outcome_refresh_preserves_newest_materialized_metrics(tmp_path):
    db = tmp_path / "performance.sqlite"
    action_outcomes.initialize_action_tracker(db)
    with sqlite3.connect(db) as conn:
        conn.execute("INSERT INTO action_recommendations (run_id,ticker,action,created_at) VALUES (?,?,?,?)",
                     ("fixture", "AAPL", "BUY", NOW.isoformat()))
    history = {"AAPL": [["2026-10-02", 100], ["2026-10-05", 110], ["2026-10-06", 120]]}
    ingestion = "2026-10-07T00:00:00Z"
    for cutoff in ("2026-10-06", "2026-10-02", "2026-10-06"):
        action_outcomes.update_action_outcomes(db, cutoff, price_history=history, recorded_at=ingestion,
                                               recommendation_ids=[1])
        with sqlite3.connect(db) as conn:
            assert conn.execute("SELECT return_1d,updated_at FROM action_outcomes").fetchall() == [(0.1, "2026-10-06")]
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM lifecycle_events WHERE kind='OUTCOME'").fetchone() == (2,)


def test_pages_build_uses_only_validated_report_snapshot(tmp_path, monkeypatch):
    folder = tmp_path / "archive" / "work-reports" / "kr"
    (folder / "events").mkdir(parents=True)
    digest = "a" * 64
    report = {"schema": site.WORK_REPORT_SCHEMA, "surface": "kr", "published_at": NOW.isoformat(),
              "report_sha256": digest, "event_id": "kr:event", "report_markdown": "# Fixture"}
    data = json.dumps(report).encode()
    latest = folder / "latest.json"
    latest.write_bytes(data)
    (folder / "events" / f"{digest}.json").write_bytes(data)
    monkeypatch.setattr(site, "validate_work_report", lambda _: None)

    def replace_after_validation(**kwargs):
        latest.write_bytes(b'{"unvalidated":"racing writer"}')
        return {"reports": []}

    monkeypatch.setattr(site, "publish_report_history", replace_after_validation)
    site._publish_latest_report(root=tmp_path / "site", archive_dir=tmp_path / "archive", surface="kr", url_prefix="/work/v1")
    assert (tmp_path / "site" / "kr" / "report" / "latest.json").read_bytes() == data


def test_pages_dispatch_rejects_contents_different_from_acknowledgement(tmp_path, monkeypatch):
    digest = "a" * 64
    report_file = tmp_path / "report.json"
    report_file.write_text("{}")
    runtime = SimpleNamespace(root=tmp_path, status=lambda _: {"state": {
        "last_acked_event_id": "kr:event", "last_acked_report_sha256": digest, "last_acked_report_path": str(report_file),
    }})
    monkeypatch.setattr(handoff.shutil, "which", lambda _: "gh")
    dispatch = Mock(return_value=SimpleNamespace(returncode=0))
    with pytest.raises(handoff.WorkRuntimeError, match="missing required keys"):
        handoff.dispatch_pages_handoff(runtime, surface="kr", event_id="kr:event", report_sha256=digest,
                                       repository="example/fixture", runner=dispatch)
    dispatch.assert_not_called()
