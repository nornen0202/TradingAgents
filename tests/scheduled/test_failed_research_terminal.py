import json
from dataclasses import replace
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from tradingagents.execution import delivery
from tradingagents.scheduled import runner
from tradingagents.scheduled.config import load_scheduled_config


def config_for(tmp_path, *, mode="full", parallel=False, execution=False):
    path = tmp_path / "config.toml"
    path.write_text(
        '[run]\ntickers=["AAPL", "MSFT"]\nmarket="US"\n'
        f'run_mode="{mode}"\nparallel_ticker_execution={str(parallel).lower()}\nmax_parallel_tickers=2\n'
        f'[storage]\narchive_dir="{(tmp_path / "archive").as_posix()}"\n'
        f'site_dir="{(tmp_path / "site").as_posix()}"\n'
        '[portfolio]\nenabled=true\n[performance]\nenabled=true\n'
        f'[execution]\nenabled={str(execution).lower()}\n',
        encoding="utf-8",
    )
    return load_scheduled_config(path)


@pytest.mark.parametrize("parallel", [False, True])
def test_all_failed_full_research_finishes_without_downstream_calls(tmp_path, monkeypatch, parallel):
    config = config_for(tmp_path, parallel=parallel, execution=True)
    tickers = [f"TICKER{i}" for i in range(30)]
    config = replace(config, run=replace(config.run, tickers=tickers))
    archive = config.storage.archive_dir
    original = archive / "runs/2025/original/tickers/AAPL/analysis.json"
    original.parent.mkdir(parents=True)
    original.write_bytes(b'{"decision":"WAIT","original_approval":"preserve"}')
    ledger = archive / "paper/ledger.json"
    ledger.parent.mkdir(parents=True)
    ledger.write_bytes(b'{"attempts":1,"max_attempts":4,"orders":[]}')
    before = {path: path.read_bytes() for path in (original, ledger)}
    monkeypatch.setattr(runner, "_resolve_run_trade_date", lambda **_: "2026-10-21")

    def workers(**kwargs):
        rows = []
        for ticker in kwargs["run_tickers"]:
            error_path = kwargs["run_dir"] / "tickers" / ticker / "error.json"
            error_path.parent.mkdir(parents=True)
            error_path.write_text(json.dumps({"status": "failed", "ticker": ticker,
                                              "error": "Required daily price unavailable"}))
            rows.append({"ticker": ticker, "status": "failed", "decision": None,
                         "error": "Required daily price unavailable", "metrics": {},
                         "artifacts": {"error_json": f"tickers/{ticker}/error.json"}})
        return (rows, {}, {}, []) if parallel else rows

    worker = Mock(side_effect=workers)
    monkeypatch.setattr(runner, "_run_parallel_tickers" if parallel else "_run_sequential_tickers", worker)
    forbidden = Mock(side_effect=AssertionError("No downstream work after all ticker research failed"))
    for name in ("collect_event_news", "collect_event_signals", "_run_execution_overlay_passes",
                 "run_portfolio_pipeline", "build_and_write_decision_bundle", "build_live_context_delta",
                 "_run_performance_tracking", "build_site"):
        monkeypatch.setattr(runner, name, forbidden)
    monkeypatch.setattr(delivery, "handoff_completed_run", forbidden)

    manifest = runner.execute_scheduled_run(config, run_label="all-failed")

    worker.assert_called_once()
    forbidden.assert_not_called()
    assert manifest["status"] == "failed"
    assert manifest["summary"]["successful_tickers"] == 0
    assert manifest["summary"]["failed_tickers"] == 30
    assert len(manifest["quality_gate"]["failed_tickers"]) == 30
    assert manifest["terminal_failure"]["reason"] == "no_successful_ticker_research"
    assert manifest["terminal_failure"]["successful_tickers"] == 0
    assert "requested_new_research_count" not in manifest["terminal_failure"]
    assert manifest["run_quality"]["run_quality_score"] == 0
    for stage in ("portfolio", "execution", "decision_bundle", "performance"):
        assert manifest[stage] == {"status": "skipped", "reason": "no_successful_ticker_research"}
    run_dir = next((archive / "runs").glob(f'*/{manifest["run_id"]}'))
    assert json.loads((run_dir / "run.json").read_text()) == manifest
    attempt = json.loads((run_dir / "attempt.json").read_text())
    assert attempt["status"] == "FAILED"
    assert attempt["completed_tickers"] == 0
    assert datetime.fromisoformat(attempt["finished_at"]) >= datetime.fromisoformat(manifest["finished_at"])
    assert len(list(run_dir.glob("tickers/*/error.json"))) == 30
    assert not list(run_dir.glob("**/portfolio_candidates.json"))
    assert not list(run_dir.glob("**/analysis.json"))
    assert {path: path.read_bytes() for path in before} == before


@pytest.mark.parametrize("mode,statuses,expected", [
    ("full", ["failed", "success"], "partial_failure"),
    ("full", ["success", "success"], "success"),
    ("portfolio_only", [], "success"),
])
def test_successful_research_and_account_only_keep_portfolio_path(tmp_path, monkeypatch, mode, statuses, expected):
    config = config_for(tmp_path, mode=mode)
    rows = [{"ticker": ticker, "status": status, "metrics": {}, "artifacts": {}}
            for ticker, status in zip(config.run.tickers, statuses)]
    monkeypatch.setattr(runner, "_resolve_run_trade_date", lambda **_: "2026-10-21")
    monkeypatch.setattr(runner, "_run_sequential_tickers", lambda **_: rows)
    for name in ("collect_event_news", "collect_event_signals", "build_live_context_delta"):
        monkeypatch.setattr(runner, name, lambda **_: {})
    portfolio = Mock(return_value={"status": "success"})
    monkeypatch.setattr(runner, "run_portfolio_pipeline", portfolio)
    bundle = Mock(return_value={"status": "success"})
    monkeypatch.setattr(runner, "build_and_write_decision_bundle", bundle)
    performance = Mock(return_value={"status": "success"})
    monkeypatch.setattr(runner, "_run_performance_tracking", performance)
    handoff = Mock()
    monkeypatch.setattr(delivery, "handoff_completed_run", handoff)

    manifest = runner.execute_scheduled_run(config, run_label="usable-research", skip_site_build=True)

    assert manifest["status"] == expected
    assert "terminal_failure" not in manifest
    portfolio.assert_called_once()
    bundle.assert_called_once()
    handoff.assert_called_once()
    assert performance.call_count == (1 if mode == "full" else 0)
    assert manifest["summary"]["successful_tickers"] == statuses.count("success")
    attempt_path = next(config.storage.archive_dir.glob("runs/*/*/attempt.json"))
    assert json.loads(attempt_path.read_text())["status"] == expected.upper()


def test_failed_worker_preserves_safe_partial_tool_evidence(tmp_path, monkeypatch):
    config = config_for(tmp_path)
    request = {"request_id": "request-1", "method": "get_stock_data", "status": "failed",
               "started_at": "2026-10-22T09:00:00+00:00", "completed_at": "2026-10-22T09:00:01+00:00",
               "result_sha256": None, "raw_prompt": "secret-prompt", "api_key": "secret-key"}
    events = [{"request_id": "request-1", "method": "get_stock_data", "vendor": vendor,
               "status": "fallback", "fallback": True, "note": "secret-provider-note"}
              for vendor in ("yfinance", "alpha_vantage")]
    monkeypatch.setattr(runner, "snapshot_tool_telemetry", lambda: events)
    monkeypatch.setattr(runner, "snapshot_tool_requests", lambda: [request])
    graph = SimpleNamespace(propagate=Mock(side_effect=RuntimeError("Required daily price unavailable")),
                            close=Mock())
    monkeypatch.setattr(runner, "TradingAgentsGraph", lambda *a, **k: graph)
    result = runner._run_single_ticker(config=config, ticker="AAPL", run_dir=tmp_path / "run",
                                      engine_results_dir=tmp_path / "engine", trade_date_override="2026-10-21")

    assert result["status"] == "failed"
    error = json.loads((tmp_path / "run/tickers/AAPL/error.json").read_text())
    telemetry = error["tool_telemetry"]
    assert result["tool_telemetry"] == telemetry
    assert telemetry["vendor_calls"] == {"yfinance": 1, "alpha_vantage": 1}
    assert telemetry["total_tool_calls"] == telemetry["fallback_count"] == 2
    assert telemetry["called_tools"] == ["get_stock_data"]
    assert telemetry["request_outcomes"][0]["status"] == "failed"
    assert telemetry["request_outcomes"][0]["started_at"] == request["started_at"]
    assert "secret" not in json.dumps(telemetry)
    assert "note" not in telemetry["events"][0]
    assert result["decision"] is None
    assert not (tmp_path / "run/tickers/AAPL/analysis.json").exists()
    graph.close.assert_called_once()
