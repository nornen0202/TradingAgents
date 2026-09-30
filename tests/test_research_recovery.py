from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json

import pytest

from tradingagents.scheduled import runner
from tradingagents.scheduled.config import load_scheduled_config
from tradingagents.scheduled.research_recovery import copy_recovered_research, load_recovery_source


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


@pytest.fixture
def recovery(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        '[run]\ntickers=["AAPL","XOM"]\nmarket="US"\nrun_mode="full"\n'
        '[llm]\ncodex_fallback_on_app_server_error=false\n'
        f'[storage]\narchive_dir="{(tmp_path / "archive").as_posix()}"\nsite_dir="{(tmp_path / "site").as_posix()}"\n'
        '[execution]\nenabled=false\n', encoding="utf-8")
    config = load_scheduled_config(config_path)
    now = datetime.now(timezone.utc)
    started, finished = now - timedelta(hours=2), now - timedelta(hours=1)
    run_id = started.strftime("%Y%m%dT%H%M%S") + "_full"
    root = config.storage.archive_dir / "runs" / run_id[:4] / run_id
    date = started.date().isoformat()
    decision = {"rating": "HOLD", "portfolio_stance": "BULLISH", "entry_action": "WAIT"}
    a = {"ticker": "AAPL", "status": "success", "decision": decision,
         "analysis_date": date, "trade_date": date, "started_at": started.isoformat(),
         "finished_at": finished.isoformat(), "duration_seconds": 3600,
         "metrics": {"llm_calls": 20, "llm_fallback_calls": 0},
         "llm_usage": {"available": True, "calls": 20}, "quality_flags": []}
    state = {k: "Substantive sourced research." for k in ("market_report", "news_report", "sentiment_report", "fundamentals_report")}
    state.update(final_trade_decision=decision, company_of_interest="AAPL")
    artifacts = {"analysis_json": "tickers/AAPL/analysis.json", "final_state_json": "tickers/AAPL/final_state.json",
                 "report_markdown": "tickers/AAPL/report.md", "execution_contract_json": "tickers/AAPL/execution_contract.json"}
    write(root / artifacts["analysis_json"], a)
    write(root / artifacts["final_state_json"], state)
    write(root / artifacts["execution_contract_json"], {"ticker": "AAPL", "valid_until": finished.isoformat()})
    (root / artifacts["report_markdown"]).write_text("# Original research", encoding="utf-8")
    source = {"run_id": run_id, "status": "partial_failure", "started_at": started.isoformat(), "finished_at": finished.isoformat(),
              "settings": runner._settings_snapshot(config), "daily_thesis_trade_date": date,
              "active_universe": {"mode": "full_required_coverage", "active_count": 2,
                  "expected_holding_tickers": [], "expected_watchlist_tickers": ["AAPL", "XOM"],
                  "coverage": {"selection_complete": True, "analysis_complete": False, "complete": False}},
              "summary": {"total_tickers": 2, "successful_tickers": 1, "failed_tickers": 1},
              "tickers": [{**a, "artifacts": artifacts}, {"ticker": "XOM", "status": "failed", "error": "model timeout"}]}
    write(root / "run.json", source)
    write(root / "attempt.json", {"status": "PARTIAL_FAILURE"})
    return {"config": config, "root": root, "source": source, "now": now, "destination": tmp_path / "new-run"}


def load(fixture, **overrides):
    return load_recovery_source(**{
        "archive_dir": fixture["config"].storage.archive_dir, "source_run_id": fixture["source"]["run_id"],
        "settings": runner._settings_snapshot(fixture["config"]), "now": fixture["now"],
        "holding_tickers": [], "account_status": "disabled", **overrides})


def test_recovery_copies_original_bytes_and_times_without_recounting_calls(recovery):
    source_bytes = (recovery["root"] / "run.json").read_bytes()
    plan = load(recovery)
    summaries, receipt = copy_recovered_research(plan, run_dir=recovery["destination"])
    assert plan["retry_tickers"] == ["XOM"]
    assert plan["active_universe"]["expected_watchlist_tickers"] == ["AAPL", "XOM"]
    assert receipt["source_manifest_sha256"] == hashlib.sha256(source_bytes).hexdigest()
    assert receipt["reused_tickers"] == ["AAPL"]
    for relative in recovery["source"]["tickers"][0]["artifacts"].values():
        assert (recovery["root"] / relative).read_bytes() == (recovery["destination"] / relative).read_bytes()
    assert summaries[0]["finished_at"] == recovery["source"]["tickers"][0]["finished_at"]
    assert summaries[0]["llm_usage"]["calls"] == 0
    assert summaries[0]["source_llm_usage"]["calls"] == 20
    assert (recovery["root"] / "run.json").read_bytes() == source_bytes


@pytest.mark.parametrize("mutate", [
    lambda s: s.update(status="success"),
    lambda s: s["settings"].update(analysis_mode="smoke"),
    lambda s: s["settings"].update(run_mode="overlay_only"),
    lambda s: s["settings"].update(market="KR"),
    lambda s: s["settings"].update(deep_model="different"),
    lambda s: s["settings"].update(codex_fallback_on_app_server_error=True),
    lambda s: s["active_universe"].update(mode="holdings_first_watchlist_rotation"),
    lambda s: s["active_universe"]["coverage"].update(selection_complete=False),
    lambda s: s["active_universe"].update(expected_watchlist_tickers=["AAPL", "XOM", "MISSING"]),
    lambda s: s["active_universe"].update(missing_analysis_tickers=["XOM"]),
    lambda s: s["summary"].update(successful_tickers=2),
    lambda s: s["tickers"].append(deepcopy(s["tickers"][0])),
    lambda s: s.update(finished_at="2099-01-01T00:00:00+00:00"),
    lambda s: s.update(started_at="2000-01-01T00:00:00+00:00"),
    lambda s: s.update(started_at="2026-01-01T00:00:00"),
    lambda s: s.update(research_recovery={"source_run_id": "another"}),
])
def test_invalid_source_cohorts_fail_closed(recovery, mutate):
    mutate(recovery["source"])
    write(recovery["root"] / "run.json", recovery["source"])
    with pytest.raises(ValueError):
        load(recovery)
    assert not recovery["destination"].exists()


def test_active_source_new_holdings_and_path_escape_are_rejected(recovery):
    with pytest.raises(ValueError, match="New account holdings"):
        load(recovery, holding_tickers=["MSFT"])
    with pytest.raises(ValueError, match="run ID"):
        load(recovery, source_run_id="../other")
    write(recovery["root"] / "attempt.json", {"status": "RUNNING"})
    with pytest.raises(ValueError, match="still active"):
        load(recovery)


@pytest.mark.parametrize("file,mutate", [
    ("analysis.json", lambda a: a.update(ticker="MSFT")),
    ("analysis.json", lambda a: a["metrics"].update(llm_fallback_calls=1)),
    ("analysis.json", lambda a: a.update(decision={"rating": "BUY"})),
    ("analysis.json", lambda a: a.update(trade_date="2000-01-01")),
    ("analysis.json", lambda a: a.update(finished_at="2099-01-01T00:00:00+00:00")),
    ("final_state.json", lambda a: a.update(company_of_interest="MSFT")),
    ("final_state.json", lambda a: a.update(final_trade_decision={"rating": "BUY"})),
    ("final_state.json", lambda a: a.update(fundamentals_report="")),
    ("final_state.json", lambda a: a.update(fundamentals_report="TRADINGAGENTS_CODEX_FALLBACK_RESPONSE")),
    ("execution_contract.json", lambda a: a.update(ticker="MSFT")),
])
def test_incomplete_or_inconsistent_research_is_never_reused(recovery, file, mutate):
    plan = load(recovery)
    path = recovery["root"] / "tickers/AAPL" / file
    value = json.loads(path.read_text(encoding="utf-8"))
    mutate(value)
    write(path, value)
    with pytest.raises(ValueError):
        copy_recovered_research(plan, run_dir=recovery["destination"])
    assert not recovery["destination"].exists()


def test_missing_artifact_and_escape_fail_without_partial_writes(recovery):
    plan = load(recovery)
    plan["successful_rows"][0]["artifacts"]["report_markdown"] = "../outside.md"
    with pytest.raises(ValueError, match="artifact path"):
        copy_recovered_research(plan, run_dir=recovery["destination"])
    assert not recovery["destination"].exists()


def test_recovery_cannot_overwrite_original_or_copy_changed_manifest(recovery):
    plan = load(recovery)
    with pytest.raises(ValueError, match="overwrite"):
        copy_recovered_research(plan, run_dir=recovery["root"])
    source = deepcopy(recovery["source"])
    source["status"] = "failed"
    write(recovery["root"] / "run.json", source)
    with pytest.raises(ValueError, match="source changed"):
        copy_recovered_research(plan, run_dir=recovery["destination"])


def test_recovery_requires_loaded_current_account(recovery):
    recovery["source"]["settings"]["ticker_universe_mode"] = "config_plus_account"
    write(recovery["root"] / "run.json", recovery["source"])
    settings = runner._settings_snapshot(recovery["config"])
    settings["ticker_universe_mode"] = "config_plus_account"
    with pytest.raises(ValueError, match="current loaded account"):
        load(recovery, settings=settings, account_status="failed")


@pytest.mark.parametrize("args", [["--site-only"], ["--tickers", "XOM"], ["--trade-date", "2026-09-29"]])
def test_cli_rejects_partial_scope_overrides_before_loading_config(args):
    with pytest.raises(SystemExit):
        runner.main(["--resume-from-run", "20260930T193547_full", *args])


@pytest.mark.parametrize("retry_status", ["success", "failed"])
def test_runner_retries_only_failed_ticker_and_recomputes_full_coverage(recovery, monkeypatch, retry_status):
    retried = []
    def analyze(**kwargs):
        retried.append(kwargs["ticker"])
        assert kwargs["trade_date_override"] == recovery["source"]["daily_thesis_trade_date"]
        return {"ticker": kwargs["ticker"], "status": retry_status, "decision": {}, "artifacts": {}}
    monkeypatch.setattr(runner, "_run_single_ticker", analyze)
    monkeypatch.setattr(runner, "_augment_run_tickers_with_scanner", lambda **_: pytest.fail("Must not reselect frozen cohort"))
    monkeypatch.setattr(runner, "collect_event_signals", lambda **_: {})
    monkeypatch.setattr(runner, "build_live_context_delta", lambda **_: {})
    monkeypatch.setattr(runner, "build_and_write_decision_bundle", lambda **_: {})
    manifest = runner.execute_scheduled_run(recovery["config"], skip_site_build=True,
        run_label="recovery-test", resume_from_run=recovery["source"]["run_id"])
    assert retried == ["XOM"]
    assert [r["ticker"] for r in manifest["tickers"]] == ["AAPL", "XOM"]
    assert manifest["status"] == ("success" if retry_status == "success" else "partial_failure")
    assert manifest["active_universe"]["coverage"]["complete"] is (retry_status == "success")
    assert runner._strict_required_coverage_failed(manifest) is (retry_status != "success")
    assert manifest["research_recovery"]["reused_tickers"] == ["AAPL"]
    assert manifest["llm_usage"]["calls"] == 0  # no provider calls in this fixture
