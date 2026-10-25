"""Existing scheduled artifacts stay usable through overlays and a persistent UI."""
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
from threading import Thread
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pytest

from tradingagents.charting.operations import archive_catalog, paper_health, kis_demo_health
from tradingagents.charting.server import make_handler
from tradingagents.execution.experiments import ExperimentRegistry


ASOF = "2026-10-16T12:00:00Z"


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def run(archive, name, *, started="2026-10-16T09:00:00Z", finished="2026-10-16T10:00:00Z", ticker="AAPL"):
    root = archive / "runs" / "2026" / name
    write(root / "run.json", {"run_id": name, "status": "success", "started_at": started,
          "finished_at": finished, "tickers": [{"ticker": ticker, "status": "success"}]})
    directory = root / "tickers" / ticker
    write(directory / "analysis.json", {"finished_at": finished})
    write(directory / "chart_evidence.json", {"ticker": ticker, "bars": []})
    return directory


def health_fixture():
    return {"schema": "tradingagents.paper-runtime/v1", "mode": "LOCAL_PAPER_ONLY", "enabled": True,
        "broker_orders_sent": 0, "real_orders_enabled": False, "checked_at": "2026-10-16T11:59:00Z",
        "markets": {"kr": {"status": "MARKET_CLOSED", "checked_at": "2026-10-16T11:59:00Z",
            "last_quote_at": "2026-10-16T06:29:00Z", "last_fill_at": None,
            "ledger_path": "C:/SECRET/ACCOUNT-123.sqlite", "cash": 123456789,
            "source_run_id": "known-run", "source_revision": "abc123",
            "order_counts": {"PENDING": 1, "FILLED": 0, "REJECTED": 2, "CANCELLED": 0},
            "blockers": ["MARKET_CLOSED", "private path C:/SECRET/ACCOUNT"]}}}


def kis_read_fixture(market="KR", **changes):
    return {"mode": "KIS_DEMO", "market": market, "status": "READ_CONNECTION_VERIFIED", "checked_at": "2026-10-16T11:59:00Z",
            "orders_submitted": 0, "live_orders_enabled": False, "real_account_access": False,
            "paper_order_connection_verified": False, "account": "PRIVATE-ACCOUNT", "app_key": "SECRET-KEY",
            "app_secret": "SECRET-CREDENTIAL", "holdings": [{"ticker": "PRIVATE", "qty": 123}],
            "path": "C:/PRIVATE/settings", **changes}


def test_archive_selection_is_dynamic_per_ticker_and_point_in_time(tmp_path):
    original = run(tmp_path, "original")
    run(tmp_path, "kr", ticker="005930")
    # A slow earlier invocation completing later cannot displace newer input.
    run(tmp_path, "slow", started="2026-10-16T08:00:00Z", finished="2026-10-16T11:00:00Z")
    run(tmp_path, "future", started="2026-10-16T13:00:00Z", finished="2026-10-16T14:00:00Z")
    assert archive_catalog(tmp_path, analysis_as_of=ASOF)["AAPL"]["ticker_dir"] == original
    assert set(archive_catalog(tmp_path, analysis_as_of=ASOF)) == {"AAPL", "005930"}
    assert archive_catalog(tmp_path, analysis_as_of="2026-10-16T09:30:00Z") == {}
    latest = run(tmp_path, "next", started="2026-10-16T10:30:00Z", finished="2026-10-16T11:30:00Z")
    assert archive_catalog(tmp_path, analysis_as_of=ASOF)["AAPL"]["ticker_dir"] == latest
    assert archive_catalog(tmp_path, analysis_as_of="2026-10-16T10:01:00Z")["AAPL"]["ticker_dir"] == original


def test_paper_health_is_safe_and_does_not_advance_quote_or_fill_clocks(tmp_path):
    path = tmp_path / "status.json"
    write(path, health_fixture())
    status = paper_health(path, analysis_as_of=ASOF)
    assert status["status"] == "AVAILABLE" and not status["stale"]
    assert status["markets"]["kr"]["last_quote_at"] == "2026-10-16T06:29:00+00:00"
    assert status["markets"]["kr"]["last_fill_at"] is None
    assert status["markets"]["kr"]["blockers"] == ["MARKET_CLOSED"]
    assert "SECRET" not in json.dumps(status) and "123456789" not in json.dumps(status)
    assert paper_health(path, analysis_as_of="2026-10-16T11:58:00Z")["status"] == "UNAVAILABLE"
    assert paper_health(path, analysis_as_of="2026-10-16T12:11:00Z")["stale"]
    raw = health_fixture()
    raw["real_orders_enabled"] = True
    write(path, raw)
    assert paper_health(path, analysis_as_of=ASOF)["status"] == "UNAVAILABLE"


def test_persistent_server_sees_new_runs_and_pure_research_apis_without_writes(tmp_path):
    archive = tmp_path / "archive"
    run(archive, "original")
    status_path = tmp_path / "paper.json"
    write(status_path, health_fixture())
    write(archive / "paper/kis-readiness.json", kis_read_fixture())
    write(archive / "paper/kis-us-readiness.json", kis_read_fixture("US"))
    absent_registry = tmp_path / "not-created.sqlite"
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(archive_dir=archive,
              experiment_registry=absent_registry, paper_status_path=status_path))
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    base = f"http://127.0.0.1:{server.server_port}"
    def get(route, **query):
        import time
        values = {"as_of": ASOF, **query}
        for _ in range(100):
            with urlopen(base + route + "?" + urlencode(values)) as response:
                payload = json.load(response)
                if response.status != 202:
                    return payload
            values["catalog_generation"] = payload["generation"]
            if payload.get("status") == "SNAPSHOT_BUILDING":
                values["snapshot_job"] = payload["job_token"]
            time.sleep(.01)
        pytest.fail("Fixture archive response did not finish")
    try:
        context = get("/api/context")
        assert context["tickers"]["AAPL"]["run_id"] == "original"
        snapshot = get("/api/snapshot", ticker="AAPL")
        assert snapshot["source_context"]["run_id"] == "original"
        run(archive, "new", started="2026-10-16T10:30:00Z", finished="2026-10-16T11:30:00Z")
        assert get("/api/snapshot", ticker="AAPL")["source_context"]["run_id"] == "new"
        assert get("/api/snapshot", ticker="AAPL", as_of="2026-10-16T10:01:00Z")["source_context"]["run_id"] == "original"
        compiled = get("/api/condition-draft", text="거래대금 100억원 이상 그리고 전일 대비 거래량 1.5배 이상 그리고 거래정지 제외", market="KR")
        assert compiled["status"] == "compiled" and compiled["condition"]
        assert get("/api/condition-draft", text="거래량이 많은 종목", market="KR")["condition"] is None
        assert get("/api/experiment-cards")["cards"] == []
        assert not absent_registry.exists()
        assert get("/api/paper-health")["markets"]["kr"]["status"] == "MARKET_CLOSED"
        assert "SECRET" not in json.dumps(get("/api/paper-health"))
        kis = get("/api/kis-demo-health", path="C:/PRIVATE/settings")
        assert kis["markets"]["KR"]["status"] == "READ_CONNECTION_VERIFIED"
        assert kis["markets"]["US"]["status"] == "READ_CONNECTION_VERIFIED"
        assert "SECRET" not in json.dumps(kis) and "PRIVATE" not in json.dumps(kis)
        for route in ("/api/condition-draft", "/api/experiment-cards", "/api/kis-demo-health"):
            with pytest.raises(HTTPError) as error:
                urlopen(Request(base + route, method="POST", data=b"{}"))
            assert error.value.code == 501
    finally:
        server.shutdown()
        worker.join(timeout=5)
        server.server_close()


@pytest.mark.parametrize("changes", [{"checked_at": None}, {"checked_at": "bad"}, {"checked_at": "2026-10-16"},
    {"checked_at": "2026-10-17T11:00:00Z"}, {"mode": "real"}, {"market": "US"}, {"orders_submitted": True},
    {"orders_submitted": 1}, {"live_orders_enabled": True}, {"real_account_access": True},
    {"paper_order_connection_verified": True}, {"status": "PRIVATE_SECRET"}])
def test_kis_read_health_rejects_future_untimed_or_unsafe_receipts(tmp_path, changes):
    before = kis_demo_health(tmp_path, analysis_as_of=ASOF)
    write(tmp_path / "paper/kis-readiness.json", kis_read_fixture(**changes))
    assert kis_demo_health(tmp_path, analysis_as_of=ASOF) == before


def test_kis_health_whitelist_distinguishes_read_connection_and_unverified_orders(tmp_path):
    write(tmp_path / "paper/kis-readiness.json", kis_read_fixture())
    write(tmp_path / "paper/kis-us-readiness.json", kis_read_fixture("US", status="CONNECTION_UNVERIFIED"))
    result = kis_demo_health(tmp_path, analysis_as_of=ASOF)
    assert result["markets"]["KR"]["status"] == "READ_CONNECTION_VERIFIED"
    assert result["markets"]["US"]["status"] == "CONNECTION_UNVERIFIED"
    for view in result["markets"].values():
        assert set(view) == {"status", "checked_at", "market", "mode", "orders_submitted", "live_orders_enabled", "paper_order_connection_verified"}
        assert view["orders_submitted"] == 0 and view["paper_order_connection_verified"] is False
    assert "SECRET" not in json.dumps(result) and "PRIVATE" not in json.dumps(result)
    with pytest.raises(ValueError, match="timezone"):
        kis_demo_health(tmp_path, analysis_as_of="2026-10-16")


def test_experiment_cards_api_reads_frozen_registry_and_filters_future(tmp_path):
    directory = run(tmp_path, "run")
    registry_path = tmp_path / "experiments.sqlite"
    def now():
        return datetime(2026, 10, 16, 9, tzinfo=timezone.utc)
    registry = ExperimentRegistry(registry_path, clock=now)
    spec = {"id": "paired", "hypothesis": "동일 비용의 규칙 비교", "universe": ["AAPL"], "capital": 10000,
        "currency": "USD", "benchmark": "SPY", "costs": {"fee_bps": 1, "slippage_bps": 2},
        "baseline_rules": {"strategy": "fixed"}, "ai_rules": {"strategy": "candidate"},
        "training_end": "2026-10-15T20:00:00Z", "forward_start": "2026-10-19T13:30:00Z",
        "forward_end": "2026-12-01T21:00:00Z"}
    registry.register(spec)
    registry.freeze("paired")
    registry.close()
    before = registry_path.read_bytes()
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(directory.parents[1], experiment_registry=registry_path))
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        result = json.load(urlopen(f"http://127.0.0.1:{server.server_port}/api/experiment-cards?as_of={ASOF}"))
        assert result["cards"][0]["id"] == "paired"
        assert result["cards"][0]["status"] == "awaiting_forward_start"
        assert registry_path.read_bytes() == before
    finally:
        server.shutdown()
        worker.join(timeout=5)
        server.server_close()


def test_present_time_maintenance_preserves_original_analysis_and_earlier_replay(tmp_path):
    import pandas as pd
    from tradingagents.charting.capture import capture_daily_frame
    from tradingagents.charting.maintenance import refresh_existing_review
    from tradingagents.charting.report import build_review

    directory = run(tmp_path, "original")
    original = (directory / "analysis.json").read_bytes()
    before = build_review(directory, analysis_as_of=ASOF)
    context_before = archive_catalog(tmp_path, analysis_as_of=ASOF)["AAPL"]["public_context"]
    def loader(symbol, curr_date):
        assert symbol == "AAPL" and curr_date >= "2026-10-16"
        frame = pd.DataFrame([{"Date": "2026-10-15", "Open": 100, "High": 110, "Low": 90, "Close": 105, "Volume": 1000}])
        capture_daily_frame(symbol, frame, curr_date=curr_date)
        return frame
    first = refresh_existing_review(directory, loader=loader)
    second = refresh_existing_review(directory, loader=loader)
    assert first["bar_count"] == 1 and not first["backdated"]
    assert second["broker_orders_sent"] == 0
    assert (directory / "analysis.json").read_bytes() == original
    assert build_review(directory, analysis_as_of=ASOF) == before
    assert archive_catalog(tmp_path, analysis_as_of=ASOF)["AAPL"]["public_context"] == context_before
    current = build_review(directory, analysis_as_of=second["captured_at"])
    assert len(current["series"][0]["bars"]) == 1
    assert current["series"][0]["bars"][0]["observed_at"] > ASOF
    assert len(list((directory / "execution/checkpoints").glob("chart_evidence_*.json"))) == 2
    assert (directory / "investment_review.html").is_file()


@pytest.mark.parametrize("day", ["2099-01-01", "bad", None])
def test_maintenance_rejects_undated_future_and_empty_capture_without_archive_changes(tmp_path, day):
    import pandas as pd
    from tradingagents.charting.capture import capture_daily_frame
    from tradingagents.charting.maintenance import refresh_existing_review
    directory = run(tmp_path, "original")
    before = (directory / "chart_evidence.json").read_bytes()
    def loader(symbol, curr_date):
        frame = pd.DataFrame([] if day is None else [{"Date": day, "Open": 100, "High": 110, "Low": 90, "Close": 105, "Volume": 1000}])
        capture_daily_frame(symbol, frame, curr_date=curr_date)
    with pytest.raises(ValueError, match="No completed"):
        refresh_existing_review(directory, loader=loader)
    assert (directory / "chart_evidence.json").read_bytes() == before
    assert not list((directory / "execution/checkpoints").glob("chart_evidence_*.json"))
    receipt = json.loads((directory / "chart_capture_status.json").read_text())
    assert receipt["status"] == "UNAVAILABLE" and receipt["error_type"] == "ValueError"


def test_overlay_bootstrap_preserves_chart_event_and_evidence_artifacts(tmp_path, monkeypatch):
    from tradingagents.scheduled import runner
    from tradingagents.scheduled.config import load_scheduled_config
    archive = tmp_path / "archive"
    source_dir = run(archive, "source")
    source_root = source_dir.parents[1]
    manifest = json.loads((source_root / "run.json").read_text())
    artifact_names = {"chart_evidence_json": "chart_evidence.json", "event_timeline_json": "event_timeline.json",
        "evidence_ledger_json": "evidence_ledger.json", "source_quality_json": "source_quality.json",
        "earnings_event_pack_json": "earnings_event_pack.json"}
    artifacts = {"analysis_json": "tickers/AAPL/analysis.json"}
    for key, filename in artifact_names.items():
        if not (source_dir / filename).exists():
            write(source_dir / filename, {"ticker": "AAPL", "original_clock": ASOF})
        artifacts[key] = "tickers/AAPL/" + filename
    manifest["tickers"][0]["artifacts"] = artifacts
    write(source_dir / "execution_contract.json", {"ticker": "AAPL", "ingested_at": ASOF})
    artifacts["execution_contract_json"] = "tickers/AAPL/execution_contract.json"
    monkeypatch.setattr(runner, "_resolve_latest_overlay_source_manifest", lambda *args, **kwargs: manifest)
    monkeypatch.setattr(runner, "_copy_latest_microstructure_artifacts", lambda **kwargs: {})
    config_path = tmp_path / "config.toml"
    config_path.write_text('[run]\ntickers=["AAPL"]\n[storage]\narchive_dir="'+archive.as_posix()+'"\n', encoding="utf-8")
    config = load_scheduled_config(config_path)
    destination = archive / "runs/2026/overlay"
    summaries, source = runner._bootstrap_overlay_inputs_from_latest_run(config=config, run_dir=destination, tickers=["AAPL"])
    assert source == "source"
    for key, filename in artifact_names.items():
        assert summaries[0]["artifacts"][key] == "tickers/AAPL/" + filename
        assert (destination / "tickers/AAPL" / filename).read_bytes() == (source_dir / filename).read_bytes()


def test_overlay_preserves_attached_now_vintages_missing_from_original_manifest(tmp_path):
    from tradingagents.scheduled.runner import _copy_integrated_review_sources
    source = run(tmp_path, "original")
    write(source / "execution/checkpoints/chart_evidence_later.json", {"ticker": "AAPL", "observed_at": "2026-10-16T13:00:00Z", "bars": []})
    write(source / "chart_capture_status.json", {"schema": "tradingagents.chart-capture-status/v1", "ticker": "AAPL",
        "status": "UNAVAILABLE", "checked_at": "2026-10-16T14:00:00Z", "observed_at": "2026-10-16T14:00:00Z", "error_type": "VendorMalformedResponseError"})
    target_root = tmp_path / "runs/2026/overlay"
    target = target_root / "tickers/AAPL"
    copied = _copy_integrated_review_sources(source_ticker_dir=source, target_ticker_dir=target,
        source_run_dir=source.parents[1], run_dir=target_root, existing_artifacts={})
    assert copied["chart_evidence_json"] == "tickers/AAPL/chart_evidence.json"
    assert copied["chart_capture_status_json"] == "tickers/AAPL/chart_capture_status.json"
    assert (target / "chart_capture_status.json").read_bytes() == (source / "chart_capture_status.json").read_bytes()
    assert (target / "execution/checkpoints/chart_evidence_later.json").read_bytes() == (source / "execution/checkpoints/chart_evidence_later.json").read_bytes()


def test_integrated_refresh_handles_tuple_quality_flags_and_reads_journals(tmp_path, monkeypatch):
    from tradingagents.scheduled import runner
    from tradingagents.charting import snapshot
    directory = run(tmp_path, "run")
    summary = {"quality_flags": ("overlay_only_mode",)}
    seen = []
    def unavailable(*args, **kwargs):
        seen.extend(kwargs["db_paths"])
        raise ValueError("invalid local input")
    monkeypatch.setattr(snapshot, "get_replay_snapshot", unavailable)
    runner._refresh_integrated_review(directory, summary, run_dir=directory.parents[1], db_paths=[Path("journal.sqlite")])
    assert summary["quality_flags"] == ["overlay_only_mode", "integrated_review_unavailable"]
    assert seen == [Path("journal.sqlite")]


def test_scheduled_event_capture_survives_institutional_failure_and_persists_render_flags(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from tradingagents.scheduled import runner
    from tradingagents.scheduled.config import load_scheduled_config
    from tradingagents.dataflows import event_timeline
    from tradingagents.charting import report
    config_path = tmp_path / "config.toml"
    config_path.write_text('[run]\ntickers=["AAPL"]\n', encoding="utf-8")
    config = load_scheduled_config(config_path)
    graph = SimpleNamespace(propagate=lambda *args, **kwargs: ({}, "HOLD"), close=lambda: None)
    monkeypatch.setattr(runner, "TradingAgentsGraph", lambda *args, **kwargs: graph)
    monkeypatch.setattr(runner, "StatsCallbackHandler", lambda: SimpleNamespace(get_stats=lambda: {"llm_calls": 0, "tool_calls": 0}))
    monkeypatch.setattr(runner, "polish_ticker_report", lambda state, **kwargs: (state, {}))
    def save(state, ticker, report_dir, **kwargs):
        report_dir.mkdir(parents=True, exist_ok=True)
        output = report_dir / "report.md"
        output.write_text("fixture")
        return output
    monkeypatch.setattr(runner, "save_report_bundle", save)
    def unavailable(**kwargs):
        raise ValueError("optional component unavailable")
    monkeypatch.setattr(runner, "build_public_equity_intelligence_artifacts", unavailable)
    monkeypatch.setattr(runner, "build_execution_contract", unavailable)
    monkeypatch.setattr(event_timeline, "snapshot_event_records", lambda **kwargs: [{"ticker": "AAPL", "event_id": "one",
        "version_id": "original", "title": "Captured filing", "published_at": "2026-10-15T10:00:00Z",
        "known_at": "2026-10-15T10:00:00Z", "observed_at": "2026-10-15T10:01:00Z"}])
    monkeypatch.setattr(report, "render_review", lambda *args, **kwargs: (_ for _ in ()).throw(ValueError("render unavailable")))
    result = runner._run_single_ticker(config=config, ticker="AAPL", run_dir=tmp_path / "run",
                                      engine_results_dir=tmp_path / "engine", trade_date_override="2026-10-15")
    assert result["status"] == "success"
    directory = tmp_path / "run/tickers/AAPL"
    assert json.loads((directory / "event_timeline.json").read_text())["events"][0]["title"] == "Captured filing"
    analysis = json.loads((directory / "analysis.json").read_text())
    assert "integrated_review_unavailable" in analysis["quality_flags"]
    assert "chart_bars_unavailable" in analysis["quality_flags"]
    assert analysis["chart_capture"]["completed_bar_count"] == 0


def test_future_evidence_does_not_change_prior_exclusion_count(tmp_path):
    from tradingagents.charting.report import build_review
    directory = run(tmp_path, "original")
    known = {"claim": "known", "kind": "fact", "published_at": "2026-10-16T09:00:00Z",
             "known_at": "2026-10-16T09:00:00Z", "observed_at": "2026-10-16T09:01:00Z"}
    write(directory / "evidence_ledger.json", [known])
    early = build_review(directory, analysis_as_of=ASOF)
    future = {**known, "claim": "UNAVAILABLE_FUTURE", "observed_at": "2026-10-16T13:00:00Z"}
    write(directory / "evidence_ledger.json", [known, future])
    assert build_review(directory, analysis_as_of=ASOF) == early


def test_failed_provider_capture_is_persisted_safely_and_absent_from_earlier_context(tmp_path):
    from tradingagents.charting.maintenance import refresh_existing_review
    directory = run(tmp_path, "original")
    before = archive_catalog(tmp_path, analysis_as_of=ASOF)["AAPL"]["public_context"]
    def failure(*args):
        raise RuntimeError("PRIVATE token=my-secret URL must not appear")
    with pytest.raises(RuntimeError):
        refresh_existing_review(directory, loader=failure)
    receipt = json.loads((directory / "chart_capture_status.json").read_text())
    assert receipt["status"] == "UNAVAILABLE" and receipt["error_type"] == "RuntimeError"
    assert "PRIVATE" not in json.dumps(receipt) and "secret" not in json.dumps(receipt)
    assert archive_catalog(tmp_path, analysis_as_of=ASOF)["AAPL"]["public_context"] == before
    present = archive_catalog(tmp_path, analysis_as_of=datetime.now(timezone.utc))["AAPL"]["public_context"]
    assert present["chart_capture_status"]["status"] == "UNAVAILABLE"
    assert present["chart_capture_status"]["error_type"] == "RuntimeError"
    assert not present["chart_capture_available"]


def test_legacy_verdict_and_plan_can_be_observed_now_without_backdating_or_refreshing(tmp_path):
    from tradingagents.charting.maintenance import reobserve_existing_evidence
    from tradingagents.charting.snapshot import get_replay_snapshot
    directory = run(tmp_path, "original")
    update = {"ticker": "AAPL", "execution_asof": "2026-10-16T10:00:00Z", "market_data_asof": "2026-10-16T09:59:00Z",
              "decision_state": "WAIT", "reason_codes": ["ORIGINAL_VOLUME_BLOCK"], "valid_until": "2026-10-16T10:05:00Z"}
    contract = {"ticker": "AAPL", "breakout_level": 111, "entry_valid_until": "2026-10-16T11:00:00Z"}
    write(directory / "execution_update.json", update)
    write(directory / "execution_contract.json", contract)
    original_update = (directory / "execution_update.json").read_bytes()
    original_contract = (directory / "execution_contract.json").read_bytes()
    before = get_replay_snapshot("AAPL", ASOF, ticker_dir=directory)
    assert before["execution_verdict"] is None and before["plan"] == {}
    result = reobserve_existing_evidence(directory)
    assert set(result["reobserved"]) == {"execution_update", "execution_contract"}
    assert result["provider_requests"] == 0 and result["broker_orders_sent"] == 0
    assert (directory / "execution_update.json").read_bytes() == original_update
    assert (directory / "execution_contract.json").read_bytes() == original_contract
    assert get_replay_snapshot("AAPL", ASOF, ticker_dir=directory) == before
    current = get_replay_snapshot("AAPL", datetime.now(timezone.utc), ticker_dir=directory)
    assert current["execution_verdict"] == "WAIT"
    assert current["block_reasons"] == ["ORIGINAL_VOLUME_BLOCK"]
    assert current["execution"]["execution_asof"] == update["execution_asof"]
    assert current["execution"]["market_data_asof"] == update["market_data_asof"]
    assert current["execution"]["valid_until"] == update["valid_until"]
    assert current["execution"]["provenance"] == "reobserved_archive"
    assert current["freshness_status"] == "STALE"
    assert current["plan"]["breakout_level"] == 111
    repeated = reobserve_existing_evidence(directory)
    assert repeated["reobserved"] == [] and len(repeated["skipped"]) == 2
    assert len(list((directory / "execution/checkpoints").glob("*_reobserved_*.json"))) == 2


@pytest.mark.parametrize("stamp", [None, "bad", "2026-10-16", "2099-01-01T10:00:00Z"])
def test_legacy_reobservation_requires_valid_original_execution_clock(tmp_path, stamp):
    from tradingagents.charting.maintenance import reobserve_existing_evidence
    from tradingagents.charting.snapshot import get_replay_snapshot
    directory = run(tmp_path, "original")
    write(directory / "execution_update.json", {"ticker": "AAPL", "execution_asof": stamp, "decision_state": "BUY_NOW"})
    result = reobserve_existing_evidence(directory)
    assert "execution_update" not in result["reobserved"]
    assert get_replay_snapshot("AAPL", datetime.now(timezone.utc), ticker_dir=directory)["execution_verdict"] is None


def test_reobserved_older_decision_does_not_displace_a_newer_valid_decision(tmp_path):
    from tradingagents.charting.maintenance import reobserve_existing_evidence
    from tradingagents.charting.snapshot import get_replay_snapshot
    directory = run(tmp_path, "original")
    write(directory / "execution_update.json", {"ticker": "AAPL", "execution_asof": "2026-10-16T10:00:00Z", "decision_state": "OLD"})
    write(directory / "execution/checkpoints/execution_update_newer.json", {"ticker": "AAPL", "execution_asof": "2026-10-16T11:00:00Z",
        "ingested_at": "2026-10-16T11:00:01Z", "decision_state": "NEWER"})
    reobserve_existing_evidence(directory)
    assert get_replay_snapshot("AAPL", datetime.now(timezone.utc), ticker_dir=directory)["execution_verdict"] == "NEWER"
