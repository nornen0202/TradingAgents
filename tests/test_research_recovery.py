from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
from unittest.mock import Mock
from zoneinfo import ZoneInfo

import pytest

from tradingagents.scheduled import runner
from tradingagents.execution import delivery
from tradingagents.scheduled.config import load_scheduled_config
from tradingagents.scheduled.research_recovery import copy_recovered_research, load_recovery_source, recovery_preflight_models


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
    date = started.astimezone(ZoneInfo("America/New_York")).date().isoformat()
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


def preflight_models(fixture, **overrides):
    return recovery_preflight_models(**{
        "archive_dir": fixture["config"].storage.archive_dir,
        "source_run_id": fixture["source"]["run_id"], "now": fixture["now"],
        "quick_model": "gpt-6.1-sol", "deep_model": "gpt-6.1-sol", "output_model": "gpt-6.1-sol",
        **overrides})


def set_source_models(fixture):
    fixture["source"]["settings"].update(provider="codex", **{
        f"{role}_model": "gpt-6-sol" for role in ("quick", "deep", "output", "writer", "judge")})
    write(fixture["root"] / "run.json", fixture["source"])


def test_recovery_preflight_preserves_cohort_after_default_model_migration(recovery):
    set_source_models(recovery)
    source_bytes = (recovery["root"] / "run.json").read_bytes()
    settings = deepcopy(recovery["source"]["settings"])
    for role in ("quick", "deep", "output", "writer", "judge"):
        settings[f"{role}_model"] = "gpt-6.1-sol"
    with pytest.raises(ValueError, match="configuration changed: quick_model"):
        load(recovery, settings=settings)
    quick, deep, output = preflight_models(recovery)
    assert (quick, deep, output) == ("gpt-6-sol",) * 3
    settings.update(quick_model=quick, deep_model=deep, output_model=output,
                    writer_model=output, judge_model=deep)
    plan = load(recovery, settings=settings)
    assert plan["retry_tickers"] == ["XOM"]
    assert [r["ticker"] for r in plan["successful_rows"]] == ["AAPL"]
    settings["max_debate_rounds"] += 1
    with pytest.raises(ValueError, match="configuration changed: max_debate_rounds"):
        load(recovery, settings=settings)
    assert (recovery["root"] / "run.json").read_bytes() == source_bytes


def test_ordinary_preflight_keeps_new_defaults_without_reading_archive(recovery):
    assert preflight_models(recovery, source_run_id="") == ("gpt-6.1-sol",) * 3


@pytest.mark.parametrize("mutate", [
    lambda s: s.update(status="success"),
    lambda s: s.update(research_recovery={"source_run_id": "another"}),
    lambda s: s.update(started_at="2000-01-01T00:00:00+00:00"),
    lambda s: s.update(finished_at="2099-01-01T00:00:00+00:00"),
    lambda s: s["settings"].update(provider="openai"),
    lambda s: s["settings"].update(analysis_mode="smoke"),
    lambda s: s["settings"].update(run_mode="overlay_only"),
    lambda s: s["settings"].update(codex_fallback_on_app_server_error=True),
    lambda s: s["settings"].pop("quick_model"),
    lambda s: s["settings"].update(quick_model="bad\nmodel"),
    lambda s: s["settings"].update(writer_model="different"),
    lambda s: s["settings"].update(judge_model="different"),
])
def test_recovery_preflight_rejects_unsafe_source_before_model_selection(recovery, mutate):
    set_source_models(recovery)
    mutate(recovery["source"])
    write(recovery["root"] / "run.json", recovery["source"])
    with pytest.raises(ValueError):
        preflight_models(recovery)


def test_recovery_preflight_rejects_active_source_and_path_escape(recovery):
    set_source_models(recovery)
    with pytest.raises(ValueError, match="run ID"):
        preflight_models(recovery, source_run_id="../other")
    write(recovery["root"] / "attempt.json", {"status": "RUNNING"})
    with pytest.raises(ValueError, match="still active"):
        preflight_models(recovery)


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


def failed_holding_source(fixture):
    active = fixture["source"]["active_universe"]
    active.update(expected_holding_tickers=["XOM"], expected_watchlist_tickers=["AAPL"],
                  selected_tickers=["AAPL", "XOM"], holding_tickers=[], missing_holding_tickers=["XOM"],
                  account_snapshot_status="loaded", fresh_snapshot_drift={"status": "VERIFIED"})
    active["coverage"].update(selection_complete=False, fresh_snapshot_complete=True)
    selection = {key: deepcopy(active[key]) for key in (
        "mode", "active_count", "expected_holding_tickers", "expected_watchlist_tickers", "selected_tickers")}
    selection.update(coverage={"complete": True}, missing_holding_tickers=[], missing_watchlist_tickers=[])
    write(fixture["root"] / "run.json", fixture["source"])
    write(fixture["root"] / "universe_selection.json", selection)
    return selection


def test_failed_holding_recovery_uses_bound_original_selection_without_mutating_source(recovery):
    failed_holding_source(recovery)
    before = {name: (recovery["root"] / name).read_bytes() for name in ("run.json", "universe_selection.json")}
    plan = load(recovery, holding_tickers=["XOM"], account_status="loaded")
    summaries, receipt = copy_recovered_research(plan, run_dir=recovery["destination"])
    assert plan["retry_tickers"] == ["XOM"]
    assert [row["ticker"] for row in summaries] == ["AAPL"]
    assert plan["active_universe"]["coverage"]["selection_complete"] is True
    assert plan["active_universe"]["coverage"]["analysis_complete"] is False
    assert receipt["source_selection_sha256"] == hashlib.sha256(before["universe_selection.json"]).hexdigest()
    assert all((recovery["root"] / name).read_bytes() == data for name, data in before.items())


@pytest.mark.parametrize("mutate", [
    lambda s: s["coverage"].update(complete=False),
    lambda s: s.update(selected_tickers=["AAPL"]),
    lambda s: s.update(expected_holding_tickers=[]),
    lambda s: s.update(expected_watchlist_tickers=["AAPL", "OTHER"]),
    lambda s: s.update(active_count=3),
    lambda s: s.update(missing_holding_tickers=["XOM"]),
])
def test_failed_holding_recovery_rejects_unproven_selection(recovery, mutate):
    selection = failed_holding_source(recovery)
    mutate(selection)
    write(recovery["root"] / "universe_selection.json", selection)
    with pytest.raises(ValueError):
        load(recovery, holding_tickers=["XOM"], account_status="loaded")
    assert not recovery["destination"].exists()


@pytest.mark.parametrize("mutate", [
    lambda a: a.update(missing_holding_tickers=["AAPL"]),
    lambda a: a.update(account_snapshot_status="unavailable"),
    lambda a: a.update(fresh_snapshot_drift={"status": "FAILED"}),
    lambda a: a["coverage"].update(fresh_snapshot_complete=False),
])
def test_failed_holding_recovery_rejects_unverified_fresh_snapshot_or_false_gap(recovery, mutate):
    failed_holding_source(recovery)
    mutate(recovery["source"]["active_universe"])
    write(recovery["root"] / "run.json", recovery["source"])
    with pytest.raises(ValueError):
        load(recovery, holding_tickers=["XOM"], account_status="loaded")


def test_changed_selection_after_preflight_cannot_write_reused_artifacts(recovery):
    failed_holding_source(recovery)
    plan = load(recovery, holding_tickers=["XOM"], account_status="loaded")
    (recovery["root"] / "universe_selection.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="selection changed"):
        copy_recovered_research(plan, run_dir=recovery["destination"])
    assert not recovery["destination"].exists()


@pytest.mark.parametrize("mutate", [
    lambda s: s.update(status="success"),
    lambda s: s["settings"].update(analysis_mode="smoke"),
    lambda s: s["settings"].update(run_mode="overlay_only"),
    lambda s: s["settings"].update(market="KR"),
    lambda s: s["settings"].update(deep_model="different"),
    lambda s: s["settings"].update(codex_max_retries=2),
    lambda s: s["settings"].pop("codex_max_retries"),
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


def test_settings_snapshot_records_retry_budget(recovery):
    assert runner._settings_snapshot(recovery["config"])["codex_max_retries"] == 1


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
    downstream = Mock(return_value={})
    for name in ("collect_event_signals", "collect_event_news", "build_live_context_delta", "build_and_write_decision_bundle"):
        monkeypatch.setattr(runner, name, downstream)
    manifest = runner.execute_scheduled_run(recovery["config"], skip_site_build=True,
        run_label="recovery-test", resume_from_run=recovery["source"]["run_id"])
    assert retried == ["XOM"]
    assert [r["ticker"] for r in manifest["tickers"]] == ["AAPL", "XOM"]
    assert manifest["status"] == ("success" if retry_status == "success" else "partial_failure")
    assert manifest["active_universe"]["coverage"]["complete"] is (retry_status == "success")
    assert runner._strict_required_coverage_failed(manifest) is (retry_status != "success")
    assert manifest["research_recovery"]["reused_tickers"] == ["AAPL"]
    assert manifest["llm_usage"]["calls"] == 0  # no provider calls in this fixture
    if retry_status == "success":
        assert downstream.call_count == 4
        assert "terminal_failure" not in manifest
    else:
        downstream.assert_not_called()
        assert manifest["terminal_failure"]["reason"] == "no_new_successful_recovery_research"


def _offline_successful_worker(fixture, ticker, run_dir):
    """Write a fresh research cohort member without a model or provider."""
    original = fixture["source"]["tickers"][0]
    row = deepcopy(original)
    clock = datetime.now(timezone.utc)
    row.update(ticker=ticker, started_at=clock.isoformat(), finished_at=clock.isoformat(),
               analysis_date=clock.astimezone(ZoneInfo("America/New_York")).date().isoformat(),
               duration_seconds=0, metrics={"llm_calls": 0}, llm_usage={"available": False, "calls": 0})
    row["artifacts"] = {key: path.replace("AAPL", ticker) for key, path in original["artifacts"].items()}
    row["artifacts"]["investment_review_html"] = f"tickers/{ticker}/investment_review.html"
    for key, relative in row["artifacts"].items():
        path = run_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if key == "investment_review_html":
            path.write_text("<html>Fresh worker view</html>", encoding="utf-8")
        elif key == "report_markdown":
            path.write_bytes((fixture["root"] / original["artifacts"][key]).read_bytes())
        else:
            payload = json.loads((fixture["root"] / original["artifacts"][key]).read_text(encoding="utf-8"))
            if key == "analysis_json":
                payload.update({k: row[k] for k in ("ticker", "started_at", "finished_at", "analysis_date",
                                                  "duration_seconds", "metrics", "llm_usage")})
            elif key == "final_state_json":
                payload["company_of_interest"] = ticker
            elif key == "execution_contract_json":
                payload["ticker"] = ticker
            write(path, payload)
    return row


@pytest.mark.parametrize("original_html", [False, True])
@pytest.mark.parametrize("execution_enabled", [False, True])
@pytest.mark.parametrize("remaining_failure", [False, True])
def test_recovery_postprocessing_preserves_original_artifacts_for_next_resume(
    recovery, monkeypatch, original_html, execution_enabled, remaining_failure,
):
    from tradingagents.charting import report, snapshot

    config = recovery["config"]
    config = replace(config, run=replace(config.run, tickers=["AAPL", "XOM", "MSFT"]),
                     execution=replace(config.execution, execution_refresh_enabled=execution_enabled))
    recovery["config"] = config
    source = recovery["source"]
    source["settings"] = runner._settings_snapshot(config)
    source["tickers"].append({"ticker": "MSFT", "status": "failed"})
    source["active_universe"].update(active_count=3, expected_watchlist_tickers=["AAPL", "XOM", "MSFT"])
    source["summary"].update(total_tickers=3, failed_tickers=2)
    if original_html:
        relative = "tickers/AAPL/investment_review.html"
        source["tickers"][0]["artifacts"]["investment_review_html"] = relative
        (recovery["root"] / relative).write_bytes(b"<html>Original dated view, immutable</html>")
    write(recovery["root"] / "run.json", source)
    before = {p.relative_to(recovery["root"]).as_posix(): p.read_bytes()
              for p in recovery["root"].rglob("*") if p.is_file()}
    analyzed, rendered, overlaid, bundled = [], [], [], []

    def analyze(**kwargs):
        ticker = kwargs["ticker"]
        analyzed.append(ticker)
        if ticker == "MSFT" and remaining_failure:
            return {"ticker": ticker, "status": "failed", "error": "fixture only", "artifacts": {}}
        return _offline_successful_worker(recovery, ticker, kwargs["run_dir"])

    def fetch(**kwargs):
        # Exercise the real overlay failure writer without a provider request.
        for row in kwargs["ticker_summaries"]:
            if row.get("status") != "success":
                continue
            overlaid.append(row["ticker"])
        return {}

    monkeypatch.setattr(runner, "_run_single_ticker", analyze)
    monkeypatch.setattr(runner, "_augment_run_tickers_with_scanner", lambda **_: pytest.fail("Frozen cohort changed"))
    for name in ("collect_event_signals", "collect_event_news", "build_live_context_delta"):
        monkeypatch.setattr(runner, name, lambda **_: {})
    monkeypatch.setattr(runner, "build_and_write_decision_bundle",
                        lambda **kw: bundled.append([row["ticker"] for row in kw["manifest"]["tickers"]]) or {})
    monkeypatch.setattr(runner, "_select_due_checkpoints", lambda **_: (["09:35"], "REGULAR"))
    monkeypatch.setattr(runner, "market_session_state", lambda **_: {"is_open": True, "phase": "regular"})
    monkeypatch.setattr(runner, "_fetch_overlay_market_snapshots", fetch)
    monkeypatch.setattr(snapshot, "get_replay_snapshot", lambda ticker, *a, **kw: rendered.append(ticker) or {"ticker": ticker})
    monkeypatch.setattr(report, "render_review", lambda value: f"<html>Postprocessed {value['ticker']}</html>")
    manifest = runner.execute_scheduled_run(config, skip_site_build=True, run_label="preserve-reused-view",
                                            resume_from_run=source["run_id"])
    directory = config.storage.archive_dir / "runs" / manifest["run_id"][:4] / manifest["run_id"]
    fresh = ["XOM"] if remaining_failure else ["XOM", "MSFT"]
    assert analyzed == ["XOM", "MSFT"]
    assert rendered == (fresh + fresh if execution_enabled else fresh)
    assert overlaid == (fresh if execution_enabled else [])
    assert bundled == [["AAPL", "XOM", "MSFT"]]
    assert manifest["status"] == ("partial_failure" if remaining_failure else "success")
    assert manifest["summary"]["successful_tickers"] == 1 + len(fresh)
    assert manifest["active_universe"]["coverage"]["complete"] is (not remaining_failure)
    reused = manifest["tickers"][0]
    assert reused["artifacts"] == source["tickers"][0]["artifacts"]
    assert reused["execution_update"] is None
    for relative in reused["artifacts"].values():
        assert (directory / relative).read_bytes() == before[relative]
    for ticker in fresh:
        assert (directory / f"tickers/{ticker}/investment_review.html").read_text() == f"<html>Postprocessed {ticker}</html>"
    assert before == {p.relative_to(recovery["root"]).as_posix(): p.read_bytes()
                      for p in recovery["root"].rglob("*") if p.is_file()}
    if remaining_failure:
        plan = load(recovery, source_run_id=manifest["run_id"], now=datetime.now(timezone.utc))
        assert plan["retry_tickers"] == ["MSFT"]
        assert plan["research_owners"]["AAPL"]["run_id"] == source["run_id"]
        assert plan["research_owners"]["XOM"]["run_id"] == manifest["run_id"]
    # The next ordinary overlay creates derived rows with their own artifact
    # namespace. It still visits the entire successful cohort, including AAPL.
    child_before = {p.relative_to(directory).as_posix(): p.read_bytes() for p in directory.rglob("*") if p.is_file()}
    overlay_dir = directory.with_name(directory.name + "-overlay")
    overlay_config = replace(config, run=replace(config.run, run_mode="overlay_only"),
        execution=replace(config.execution, execution_lightweight_refresh=True))
    # A completed child is discovered through the ordinary strict resolver.
    # Partial cases exercise explicit-source copying only, not promotion of a
    # partial run into a valid full-research baseline.
    rows, baseline = runner._bootstrap_overlay_inputs_from_latest_run(config=overlay_config, run_dir=overlay_dir,
        tickers=["AAPL", *fresh], source_manifest=manifest if remaining_failure else None)
    assert baseline == manifest["run_id"]
    assert all("research_reuse" not in row for row in rows)
    overlaid.clear()
    updates = runner._run_execution_overlay_passes(config=overlay_config, run_dir=overlay_dir,
        ticker_summaries=rows, checkpoints=["09:36"], analysis_source_run_id=baseline)
    assert overlaid == ["AAPL", *fresh]
    assert all(ticker in updates for ticker in ["AAPL", *fresh])
    assert child_before == {p.relative_to(directory).as_posix(): p.read_bytes() for p in directory.rglob("*") if p.is_file()}
    if remaining_failure:
        assert load(recovery, source_run_id=manifest["run_id"], now=datetime.now(timezone.utc))["retry_tickers"] == ["MSFT"]
        if original_html:
            (directory / reused["artifacts"]["investment_review_html"]).write_bytes(b"changed after publication")
            with pytest.raises(ValueError, match="reused research changed"):
                load(recovery, source_run_id=manifest["run_id"], now=datetime.now(timezone.utc))


def test_all_reused_overlay_returns_no_new_evidence_without_fetch_or_render(recovery, monkeypatch):
    plan = load(recovery)
    summaries, _ = copy_recovered_research(plan, run_dir=recovery["destination"])
    original = {p: p.read_bytes() for p in recovery["destination"].rglob("*") if p.is_file()}
    monkeypatch.setattr(runner, "_fetch_overlay_market_snapshots", lambda **_: pytest.fail("No new rows to refresh"))
    updates = runner._run_execution_overlay_passes(config=recovery["config"], run_dir=recovery["destination"],
        ticker_summaries=summaries, checkpoints=["09:35"])
    assert updates == {}
    assert summaries[0]["execution_update"] is None
    assert original == {p: p.read_bytes() for p in recovery["destination"].rglob("*") if p.is_file()}


def test_entirely_new_research_still_renders_each_successful_review(recovery, monkeypatch):
    from tradingagents.charting import report, snapshot

    rendered = []
    monkeypatch.setattr(runner, "_resolve_run_trade_date", lambda **_: recovery["source"]["daily_thesis_trade_date"])
    monkeypatch.setattr(runner, "_run_single_ticker",
                        lambda **kw: _offline_successful_worker(recovery, kw["ticker"], kw["run_dir"]))
    for name in ("collect_event_signals", "collect_event_news", "build_live_context_delta", "build_and_write_decision_bundle"):
        monkeypatch.setattr(runner, name, lambda **_: {})
    monkeypatch.setattr(snapshot, "get_replay_snapshot", lambda ticker, *a, **kw: rendered.append(ticker) or {})
    monkeypatch.setattr(report, "render_review", lambda _: "<html>Fresh completed view</html>")
    manifest = runner.execute_scheduled_run(recovery["config"], skip_site_build=True, run_label="new-research-views")
    assert manifest["status"] == "success"
    assert "research_recovery" not in manifest
    assert rendered == ["AAPL", "XOM"]
    assert all("investment_review_html" in row["artifacts"] for row in manifest["tickers"])


@pytest.mark.parametrize("parallel", [False, True])
@pytest.mark.parametrize("retry_status", ["failed", "skipped"])
def test_empty_failed_only_retry_preserves_22_original_successes_and_8_failures_without_postprocessing(recovery, monkeypatch, parallel, retry_status):
    source, root = recovery["source"], recovery["root"]
    template = deepcopy(source["tickers"][0])
    reused = ["AAPL", *[f"KEEP{i:02}" for i in range(1, 22)]]
    retried = ["XOM", *[f"FAIL{i:02}" for i in range(1, 8)]]
    tickers = reused + retried
    config = recovery["config"]
    config = replace(config,
        run=replace(config.run, tickers=tickers, parallel_ticker_execution=parallel, max_parallel_tickers=2),
        execution=replace(config.execution, execution_refresh_enabled=True),
        portfolio=replace(config.portfolio, enabled=True), performance=replace(config.performance, enabled=True))
    recovery["config"] = config
    rows = []
    for ticker in reused:
        row = deepcopy(template)
        row["ticker"] = ticker
        row["artifacts"] = {key: value.replace("AAPL", ticker) for key, value in template["artifacts"].items()}
        for key, relative in row["artifacts"].items():
            data = (root / template["artifacts"][key]).read_text(encoding="utf-8").replace("AAPL", ticker)
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(data, encoding="utf-8")
        rows.append(row)
    rows += [{"ticker": ticker, "status": "failed", "error": "prior failure"} for ticker in retried]
    source.update(settings=runner._settings_snapshot(config), tickers=rows,
                  summary={"total_tickers": 30, "successful_tickers": 22, "failed_tickers": 8})
    source["active_universe"].update(active_count=30, selected_tickers=tickers, expected_watchlist_tickers=tickers)
    write(root / "run.json", source)
    originals = {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}

    def workers(**kwargs):
        assert kwargs["run_tickers"] == retried
        assert kwargs["trade_date_override"] == source["daily_thesis_trade_date"]
        failures = []
        for ticker in kwargs["run_tickers"]:
            relative = f"tickers/{ticker}/error.json"
            if retry_status == "failed":
                write(kwargs["run_dir"] / relative, {"ticker": ticker, "status": retry_status, "error": "fixture timeout"})
            calls = 2 if retry_status == "failed" else 0
            failures.append({"ticker": ticker, "status": retry_status, "decision": None,
                             "error": "fixture timeout" if retry_status == "failed" else "runtime_budget",
                             "metrics": {"llm_calls": calls}, "llm_usage": {"available": True, "calls": calls},
                             "artifacts": {"error_json": relative} if retry_status == "failed" else {}})
        return (failures, {}, {}, []) if parallel else failures

    worker = Mock(side_effect=workers)
    monkeypatch.setattr(runner, "_run_parallel_tickers" if parallel else "_run_sequential_tickers", worker)
    forbidden = Mock(side_effect=AssertionError("Failed-only recovery must not start downstream work without new success"))
    for name in ("collect_event_news", "collect_event_signals", "_run_execution_overlay_passes",
                 "run_portfolio_pipeline", "build_and_write_decision_bundle", "build_live_context_delta",
                 "_run_performance_tracking", "build_site", "_augment_run_tickers_with_scanner"):
        monkeypatch.setattr(runner, name, forbidden)
    monkeypatch.setattr(delivery, "handoff_completed_run", forbidden)
    manifest = runner.execute_scheduled_run(config, run_label="empty-recovery", resume_from_run=source["run_id"])

    worker.assert_called_once()
    forbidden.assert_not_called()
    assert manifest["status"] == "partial_failure"
    assert manifest["summary"]["successful_tickers"] == 22 and manifest["summary"]["failed_tickers"] == 8
    assert manifest["summary"]["total_tickers"] == 30
    assert manifest["summary"]["skipped_tickers"] == (8 if retry_status == "skipped" else 0)
    assert [r["ticker"] for r in manifest["tickers"]] == tickers
    assert manifest["terminal_failure"] == {
        "schema": "tradingagents.research-terminal-failure/v1", "stage": "ticker_research",
        "reason": "no_new_successful_recovery_research", "successful_tickers": 22, "failed_tickers": 8,
        "requested_new_research_count": 8, "newly_successful_tickers": 0, "reused_research_count": 22}
    assert manifest["research_recovery"]["source_run_id"] == source["run_id"]
    assert manifest["research_recovery"]["reused_tickers"] == reused
    assert manifest["research_recovery"]["retry_tickers"] == retried
    assert manifest["daily_thesis_trade_date"] == source["daily_thesis_trade_date"]
    assert manifest["active_universe"]["coverage"]["complete"] is False
    assert manifest["active_universe"]["coverage"]["analysis_complete"] is False
    assert runner._strict_required_coverage_failed(manifest)
    assert manifest["llm_usage"]["calls"] == (16 if retry_status == "failed" else 0)  # Never recount 440 reused calls.
    for stage in ("portfolio", "execution", "decision_bundle", "performance"):
        assert manifest[stage] == {"status": "skipped", "reason": "no_new_successful_recovery_research"}
    run_dir = config.storage.archive_dir / "runs" / manifest["run_id"][:4] / manifest["run_id"]
    assert json.loads((run_dir / "run.json").read_text()) == manifest
    attempt = json.loads((run_dir / "attempt.json").read_text())
    assert attempt["status"] == "PARTIAL_FAILURE" and attempt["completed_tickers"] == 22
    assert len(list(run_dir.glob("tickers/*/error.json"))) == (8 if retry_status == "failed" else 0)
    for original, copied in zip(rows[:22], manifest["tickers"][:22]):
        assert copied["started_at"] == original["started_at"] and copied["finished_at"] == original["finished_at"]
        assert copied["source_llm_usage"]["calls"] == 20 and copied["llm_usage"]["calls"] == 0
        for relative in original["artifacts"].values():
            assert (run_dir / relative).read_bytes() == (root / relative).read_bytes()
    assert originals == {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}
    assert not list(run_dir.glob("**/portfolio_candidates.json"))
    assert not (run_dir / "decision_bundle_v2.json").exists()
    # This terminal run remains valid input for the next original-budget retry.
    next_plan = load(recovery, source_run_id=manifest["run_id"], now=datetime.now(timezone.utc))
    assert next_plan["retry_tickers"] == retried
    assert len(next_plan["successful_rows"]) == 22


def append_partial_recovery(fixture, *, parent_id=None, succeed=None, offset=40):
    """Publish an offline failed-only child using the real copy contract."""
    parent_id = parent_id or fixture["source"]["run_id"]
    plan = load(fixture, source_run_id=parent_id)
    start = fixture["now"] - timedelta(minutes=offset)
    finish = start + timedelta(minutes=5)
    identity = start.strftime("%Y%m%dT%H%M%S") + "_resume"
    directory = fixture["config"].storage.archive_dir / "runs" / identity[:4] / identity
    reused, receipt = copy_recovered_research(plan, run_dir=directory)
    rows = {r["ticker"]: r for r in reused}
    for ticker in plan["retry_tickers"]:
        if ticker != succeed:
            rows[ticker] = {"ticker": ticker, "status": "failed"}
            continue
        original = fixture["source"]["tickers"][0]
        row = deepcopy(original)
        row.update(ticker=ticker, started_at=start.isoformat(), finished_at=finish.isoformat(),
                   analysis_date=start.astimezone(ZoneInfo("America/New_York")).date().isoformat(),
                   metrics={"llm_calls": 7, "llm_fallback_calls": 0}, llm_usage={"available": True, "calls": 7},
                   duration_seconds=300)
        row["artifacts"] = {key: relative.replace("AAPL", ticker) for key, relative in original["artifacts"].items()}
        for key, relative in row["artifacts"].items():
            old = fixture["root"] / original["artifacts"][key]
            if key == "report_markdown":
                target = directory / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(old.read_bytes())
                continue
            value = json.loads(old.read_text(encoding="utf-8"))
            if key == "analysis_json":
                value.update({k: row[k] for k in ("ticker", "started_at", "finished_at", "analysis_date", "metrics", "llm_usage", "duration_seconds")})
            elif key == "final_state_json":
                value["company_of_interest"] = ticker
            elif key == "execution_contract_json":
                value["ticker"] = ticker
            write(directory / relative, value)
        rows[ticker] = row
    manifest = deepcopy(plan["source"])
    manifest.update(run_id=identity, started_at=start.isoformat(), finished_at=finish.isoformat(),
                    status="partial_failure", tickers=[rows[t] for t in plan["tickers"]],
                    active_universe=deepcopy(plan["active_universe"]), research_recovery=receipt)
    manifest["active_universe"]["coverage"].update(complete=False, analysis_complete=False)
    successes = sum(r["status"] == "success" for r in rows.values())
    manifest["summary"].update(total_tickers=len(rows), successful_tickers=successes, failed_tickers=len(rows)-successes)
    write(directory / "run.json", manifest)
    write(directory / "attempt.json", {"run_id": identity, "status": "PARTIAL_FAILURE", "market": "US", "run_mode": "full",
                                       "started_at": start.isoformat(), "finished_at": finish.isoformat()})
    return manifest, directory


@pytest.fixture
def recovery_chain(recovery):
    config = recovery["config"]
    recovery["config"] = replace(config, run=replace(config.run, tickers=["AAPL", "XOM", "MSFT"]))
    source = recovery["source"]
    source["settings"] = runner._settings_snapshot(recovery["config"])
    source["tickers"].append({"ticker": "MSFT", "status": "failed"})
    source["active_universe"].update(active_count=3, expected_watchlist_tickers=["AAPL", "XOM", "MSFT"])
    source["summary"].update(total_tickers=3, failed_tickers=2)
    write(recovery["root"] / "run.json", source)
    child, directory = append_partial_recovery(recovery, succeed="XOM")
    return recovery, child, directory


def test_nested_recovery_reuses_every_success_with_original_clocks_usage_and_bytes(recovery_chain):
    fixture, child, directory = recovery_chain
    original = {str(p): p.read_bytes() for root in (fixture["root"], directory) for p in root.rglob("*") if p.is_file()}
    plan = load(fixture, source_run_id=child["run_id"])
    assert plan["retry_tickers"] == ["MSFT"]
    assert plan["research_owners"]["AAPL"]["run_id"] == fixture["source"]["run_id"]
    assert plan["research_owners"]["XOM"]["run_id"] == child["run_id"]
    summaries, receipt = copy_recovered_research(plan, run_dir=fixture["destination"])
    assert receipt["reused_tickers"] == ["AAPL", "XOM"]
    assert [r["source_llm_usage"]["calls"] for r in summaries] == [20, 7]
    assert [r["source_metrics"]["llm_calls"] for r in summaries] == [20, 7]
    assert [r["source_duration_seconds"] for r in summaries] == [3600, 300]
    assert all(r["metrics"]["llm_calls"] == 0 for r in summaries)
    assert summaries[0]["finished_at"] == fixture["source"]["tickers"][0]["finished_at"]
    for row in summaries:
        for relative in row["artifacts"].values():
            assert (fixture["destination"] / relative).read_bytes() == (directory / relative).read_bytes()
    assert all(Path(p).read_bytes() == data for p, data in original.items())
    next_child, _ = append_partial_recovery(fixture, parent_id=child["run_id"], offset=20)
    next_plan = load(fixture, source_run_id=next_child["run_id"])
    again, _ = copy_recovered_research(next_plan, run_dir=fixture["destination"].with_name("third-copy"))
    assert next_plan["retry_tickers"] == ["MSFT"]
    assert [r["source_llm_usage"]["calls"] for r in again] == [20, 7]


@pytest.mark.parametrize("case", [
    "missing_parent", "missing_receipt", "malformed_receipt", "missing_hash", "wrong_hash", "parent_changed",
    "parent_artifact_changed", "child_artifact_changed", "borrowed_ticker", "reuse_membership", "fake_usage",
    "future_child", "missing_clock", "bad_clock", "naive_clock", "overlap", "old_root", "changed_settings",
    "changed_selection", "changed_price_date", "future_attempt", "wrong_attempt_identity", "cycle", "recursive_cycle",
])
def test_nested_recovery_rejects_unverifiable_lineage_before_copy(recovery_chain, case):
    fixture, child, directory = recovery_chain
    parent = deepcopy(fixture["source"])
    if case == "missing_parent":
        (fixture["root"] / "run.json").unlink()
    elif case == "missing_receipt":
        child.pop("research_recovery")
    elif case == "malformed_receipt":
        child["research_recovery"] = []
    elif case == "missing_hash":
        child["research_recovery"].pop("source_manifest_sha256")
    elif case == "wrong_hash":
        child["research_recovery"]["source_manifest_sha256"] = "0" * 64
    elif case == "parent_changed":
        parent["label"] = "changed"
        write(fixture["root"] / "run.json", parent)
    elif case in {"parent_artifact_changed", "child_artifact_changed"}:
        root = fixture["root"] if case == "parent_artifact_changed" else directory
        path = root / "tickers/AAPL/report.md"
        path.write_bytes(path.read_bytes() + b" ")
    elif case == "borrowed_ticker":
        child["tickers"][1]["research_reuse"] = deepcopy(child["tickers"][0]["research_reuse"])
    elif case == "reuse_membership":
        child["research_recovery"]["reused_tickers"].append("XOM")
    elif case == "fake_usage":
        child["tickers"][0]["source_llm_usage"] = {"calls": 0}
    elif case == "future_child":
        child["finished_at"] = (fixture["now"] + timedelta(seconds=1)).isoformat()
    elif case == "missing_clock":
        child.pop("finished_at")
    elif case == "bad_clock":
        child["finished_at"] = "2026-02-30T00:00:00+00:00"
    elif case == "naive_clock":
        child["finished_at"] = fixture["now"].replace(tzinfo=None).isoformat()
    elif case == "overlap":
        child["started_at"] = parent["started_at"]
        write(directory / "attempt.json", {"status": "PARTIAL_FAILURE"})
    elif case == "old_root":
        parent["started_at"] = (fixture["now"] - timedelta(hours=25)).isoformat()
        write(fixture["root"] / "run.json", parent)
        child["research_recovery"]["source_manifest_sha256"] = hashlib.sha256((fixture["root"] / "run.json").read_bytes()).hexdigest()
    elif case == "changed_settings":
        child["settings"]["max_debate_rounds"] += 1
    elif case == "changed_selection":
        child["active_universe"]["expected_watchlist_tickers"] = ["AAPL", "MSFT"]
    elif case == "changed_price_date":
        child["daily_thesis_trade_date"] = "2000-01-01"
    elif case == "future_attempt":
        attempt = json.loads((directory / "attempt.json").read_text())
        attempt["finished_at"] = (fixture["now"] + timedelta(seconds=1)).isoformat()
        write(directory / "attempt.json", attempt)
    elif case == "wrong_attempt_identity":
        write(directory / "attempt.json", {"status": "PARTIAL_FAILURE", "run_id": parent["run_id"]})
    elif case == "cycle":
        child["research_recovery"]["source_run_id"] = child["run_id"]
    elif case == "recursive_cycle":
        parent["research_recovery"] = deepcopy(child["research_recovery"])
        parent["research_recovery"]["source_run_id"] = child["run_id"]
        write(fixture["root"] / "run.json", parent)
    write(directory / "run.json", child)
    with pytest.raises(ValueError):
        load(fixture, source_run_id=child["run_id"])
    assert not fixture["destination"].exists()


@pytest.mark.parametrize("ancestor_file", ["run.json", "attempt.json", "tickers/AAPL/report.md"])
def test_nested_recovery_rechecks_ancestors_before_any_copy(recovery_chain, ancestor_file):
    fixture, child, _ = recovery_chain
    plan = load(fixture, source_run_id=child["run_id"])
    path = fixture["root"] / ancestor_file
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError):
        copy_recovered_research(plan, run_dir=fixture["destination"])
    assert not fixture["destination"].exists()


def test_nested_recovery_bounds_lineage_depth(recovery_chain, monkeypatch):
    from tradingagents.scheduled import research_recovery
    fixture, child, _ = recovery_chain
    monkeypatch.setattr(research_recovery, "MAX_RECOVERY_LINEAGE", 1)
    with pytest.raises(ValueError, match="too deep"):
        load(fixture, source_run_id=child["run_id"])


@pytest.mark.parametrize("nested", [False, True])
def test_nested_recovery_cannot_write_into_any_original_ancestor(recovery_chain, nested):
    fixture, child, _ = recovery_chain
    plan = load(fixture, source_run_id=child["run_id"])
    before = {p: p.read_bytes() for p in fixture["root"].rglob("*") if p.is_file()}
    destination = fixture["root"] / "new-copy" if nested else fixture["root"]
    with pytest.raises(ValueError, match="overwrite"):
        copy_recovered_research(plan, run_dir=destination)
    assert all(p.read_bytes() == data for p, data in before.items())
    assert set(before) == {p for p in fixture["root"].rglob("*") if p.is_file()}


def test_original_explicit_frozen_selection_must_match_terminal_order(recovery):
    recovery["source"]["active_universe"]["selected_tickers"] = ["XOM", "AAPL"]
    write(recovery["root"] / "run.json", recovery["source"])
    with pytest.raises(ValueError, match="frozen selection"):
        load(recovery)


@pytest.mark.parametrize("when", ["load", "copy"])
def test_nested_recovery_binds_original_failed_holding_selection(recovery, when):
    failed_holding_source(recovery)
    child, directory = append_partial_recovery(recovery)
    if when == "copy":
        plan = load(recovery, source_run_id=child["run_id"])
    path = recovery["root"] / "universe_selection.json"
    path.write_bytes(path.read_bytes() + b" ")  # Same semantic JSON, changed committed proof.
    with pytest.raises(ValueError, match="selection"):
        if when == "load":
            load(recovery, source_run_id=child["run_id"])
        else:
            copy_recovered_research(plan, run_dir=recovery["destination"])
    assert not recovery["destination"].exists()


@pytest.mark.parametrize("field,value", [
    ("trade_date", "2099-01-01"), ("trade_date", "2026-02-30"), ("trade_date", None),
    ("analysis_date", "2099-01-01"), ("analysis_date", "2026-02-30"), ("analysis_date", None),
])
def test_reused_dates_must_be_real_and_belong_to_original_market_day(recovery, field, value):
    source = recovery["source"]
    row = source["tickers"][0]
    path = recovery["root"] / row["artifacts"]["analysis_json"]
    analysis = json.loads(path.read_text())
    row[field] = analysis[field] = value
    if field == "trade_date":
        source["daily_thesis_trade_date"] = value
    write(path, analysis)
    write(recovery["root"] / "run.json", source)
    with pytest.raises(ValueError):
        plan = load(recovery)
        copy_recovered_research(plan, run_dir=recovery["destination"])
    assert not recovery["destination"].exists()


def test_nested_us_recovery_after_kst_midnight_keeps_original_us_analysis_day(recovery):
    source = recovery["source"]
    recovery["now"] = datetime.fromisoformat("2026-10-23T02:00:00+09:00")
    source.update(started_at="2026-10-22T23:50:00+09:00", finished_at="2026-10-23T00:30:00+09:00",
                  daily_thesis_trade_date="2026-10-22")
    row = source["tickers"][0]
    row.update(started_at="2026-10-23T00:05:00+09:00", finished_at="2026-10-23T00:20:00+09:00",
               analysis_date="2026-10-22", trade_date="2026-10-22")
    path = recovery["root"] / row["artifacts"]["analysis_json"]
    analysis = json.loads(path.read_text())
    analysis.update({key: row[key] for key in ("started_at", "finished_at", "analysis_date", "trade_date")})
    write(path, analysis)
    write(recovery["root"] / "run.json", source)
    child, _ = append_partial_recovery(recovery)
    plan = load(recovery, source_run_id=child["run_id"])
    summaries, _ = copy_recovered_research(plan, run_dir=recovery["destination"])
    assert summaries[0]["analysis_date"] == "2026-10-22"
    assert summaries[0]["started_at"].startswith("2026-10-23")
    assert (recovery["destination"] / row["artifacts"]["analysis_json"]).read_bytes() == path.read_bytes()


def test_nested_recovery_runner_only_invokes_remaining_failed_ticker(recovery_chain, monkeypatch):
    fixture, child, _ = recovery_chain
    calls = []
    monkeypatch.setattr(runner, "_run_single_ticker", lambda **kw: calls.append(kw["ticker"]) or {
        "ticker": kw["ticker"], "status": "failed", "artifacts": {}})
    monkeypatch.setattr(runner, "_augment_run_tickers_with_scanner", lambda **_: pytest.fail("Frozen cohort must not be reselected"))
    forbidden = Mock(side_effect=AssertionError("Nested retry produced no new successful research"))
    for name in ("collect_event_signals", "collect_event_news", "build_live_context_delta", "build_and_write_decision_bundle"):
        monkeypatch.setattr(runner, name, forbidden)
    manifest = runner.execute_scheduled_run(fixture["config"], skip_site_build=True,
        run_label="nested-recovery-test", resume_from_run=child["run_id"])
    assert calls == ["MSFT"]
    assert manifest["status"] == "partial_failure"
    assert manifest["research_recovery"]["reused_tickers"] == ["AAPL", "XOM"]
    assert manifest["parallel_ticker_execution"]["requested_new_research_count"] == 1
    assert runner._strict_required_coverage_failed(manifest)
    assert manifest["terminal_failure"]["reason"] == "no_new_successful_recovery_research"
    forbidden.assert_not_called()


@pytest.fixture
def finalization(recovery, tmp_path, monkeypatch):
    source = recovery["source"]
    root = recovery["root"]
    (root / "run.json").unlink()
    write(root / "attempt.json", {"run_id": source["run_id"], "status": "FAILED", "market": "US",
                                   "run_mode": "full", "started_at": source["started_at"],
                                   "finished_at": source["finished_at"], "error_type": "OSError"})
    selection = deepcopy(source["active_universe"])
    selection.update(selected_tickers=["AAPL", "XOM"])
    selection["coverage"]["complete"] = True
    write(root / "universe_selection.json", selection)
    rows = []
    for ticker in ("AAPL", "XOM"):
        row = deepcopy(source["tickers"][0])
        row["ticker"] = ticker
        row["artifacts"] = {k: value.replace("AAPL", ticker) for k, value in row["artifacts"].items()}
        for key, relative in row["artifacts"].items():
            original = root / source["tickers"][0]["artifacts"][key]
            data = original.read_text(encoding="utf-8").replace("AAPL", ticker)
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(data, encoding="utf-8")
        analysis_path = root / row["artifacts"]["analysis_json"]
        analysis = json.loads(analysis_path.read_text())
        analysis.update(provider="codex", models={f"{role}_model": source["settings"][f"{role}_model"]
                                                for role in ("quick", "deep", "output")})
        write(analysis_path, analysis)
        write(root / "worker-summaries" / f"{ticker}.json", row)
        rows.append(row)
    sha = "1" * 40
    snapshot = tmp_path / sha
    source_config = snapshot / "config" / "original.toml"
    source_config.parent.mkdir(parents=True)
    original_config = (tmp_path / "config.toml").read_bytes()
    source_config.write_bytes(original_config)
    (snapshot / ".source-ready").write_text(sha)
    monkeypatch.setattr("subprocess.check_output", lambda *args, **kwargs: original_config)
    return {**recovery, "source_config": source_config, "rows": rows}


def finalization_plan(fixture, **overrides):
    from tradingagents.scheduled.research_recovery import load_finalization_source
    return load_finalization_source(**{
        "archive_dir": fixture["config"].storage.archive_dir, "source_run_id": fixture["source"]["run_id"],
        "settings": runner._settings_snapshot(fixture["config"]), "now": fixture["now"],
        "holding_tickers": [], "account_status": "disabled", "source_config_path": fixture["source_config"],
        **overrides})


def test_completed_research_finalization_runs_no_graph_and_preserves_source(finalization, monkeypatch):
    root = finalization["root"]
    original = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    monkeypatch.setattr(runner, "_run_single_ticker", lambda **_: pytest.fail("Completed research must not rerun"))
    monkeypatch.setattr(runner, "_augment_run_tickers_with_scanner", lambda **_: pytest.fail("Frozen selection must not rerun"))
    monkeypatch.setattr("tradingagents.charting.snapshot.get_replay_snapshot",
                        lambda *a, **kw: pytest.fail("Copied finalization reviews must not query a new replay snapshot"))
    downstream = Mock(return_value={})
    for name in ("collect_event_signals", "collect_event_news", "build_live_context_delta", "build_and_write_decision_bundle"):
        monkeypatch.setattr(runner, name, downstream)
    manifest = runner.execute_scheduled_run(finalization["config"], skip_site_build=True,
        run_label="finalization-test", finalize_from_run=finalization["source"]["run_id"],
        finalization_source_config=finalization["source_config"])
    assert manifest["status"] == "success"
    assert manifest["summary"]["successful_tickers"] == 2
    assert manifest["active_universe"]["coverage"]["complete"] is True
    assert manifest["research_recovery"]["finalization_only"] is True
    assert manifest["research_recovery"]["retry_tickers"] == []
    assert [row["artifacts"] for row in manifest["tickers"]] == [row["artifacts"] for row in finalization["rows"]]
    assert manifest["parallel_ticker_execution"]["requested_new_research_count"] == 0
    assert manifest["llm_usage"]["calls"] == 0
    assert downstream.call_count == 4
    assert "terminal_failure" not in manifest
    assert original == {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    assert not (root / "run.json").exists()


@pytest.mark.parametrize("change", ["active", "missing_worker", "failed_worker", "wrong_model", "bad_config", "new_holding"])
def test_finalization_refuses_unverified_or_incomplete_source(finalization, change):
    root = finalization["root"]
    overrides = {}
    if change == "active":
        attempt = json.loads((root / "attempt.json").read_text())
        attempt["status"] = "RUNNING"
        write(root / "attempt.json", attempt)
    elif change == "missing_worker":
        (root / "worker-summaries/XOM.json").unlink()
    elif change == "failed_worker":
        row = deepcopy(finalization["rows"][1])
        row["status"] = "failed"
        write(root / "worker-summaries/XOM.json", row)
    elif change == "wrong_model":
        path = root / "tickers/XOM/analysis.json"
        analysis = json.loads(path.read_text())
        analysis["models"]["deep_model"] = "different"
        write(path, analysis)
    elif change == "bad_config":
        finalization["source_config"].write_text('model="tampered"')
    else:
        overrides["holding_tickers"] = ["NEW"]
    with pytest.raises(ValueError):
        finalization_plan(finalization, **overrides)
    assert not finalization["destination"].exists()


def test_finalization_rechecks_hashes_before_copying(finalization):
    plan = finalization_plan(finalization)
    path = finalization["root"] / "tickers/XOM/report.md"
    path.write_text("changed")
    with pytest.raises(ValueError, match="source changed"):
        copy_recovered_research(plan, run_dir=finalization["destination"])
    assert not finalization["destination"].exists()
