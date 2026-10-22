from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
import shutil

import pytest

from tradingagents.atomic_io import atomic_write_json
from tradingagents.scheduled import runner
from tradingagents.scheduled import research_refresh as refresh
from tradingagents.scheduled.config import load_scheduled_config
from tradingagents.schemas import parse_structured_decision

NOW = datetime.now(timezone.utc) - timedelta(hours=1)


def encoded_decision(**changes):
    data = {"rating": "HOLD", "portfolio_stance": "NEUTRAL", "entry_action": "WAIT",
            "conditional_entry_action": "NONE", "risk_action": "HOLD", "confidence": .6,
            "time_horizon": "medium", "entry_logic": "Wait for verified entry conditions.",
            "exit_logic": "Follow a verified risk exit.", "position_sizing": "One demo share within original limits.",
            "risk_limits": "Keep the existing risk limits.", "catalysts": [], "invalidators": []}
    data.update(changes)
    # Production _select_public_decision returns this JSON text, not a mapping.
    result = json.dumps(data)
    parse_structured_decision(result)
    return result


def cohort(root, identity="20261022T120000-full", *, mode="full", parent=None, start=None,
           tickers=("AAPL", "AMD", "MSFT")):
    start = start or NOW - timedelta(hours=2)
    directory = root / "runs/2026" / identity
    rows = []
    for ticker in tickers:
        base = directory / "tickers" / ticker
        analysis = {"ticker": ticker, "status": "success", "trade_date": "2026-10-21", "analysis_date": "2026-10-22",
                    "started_at": start.isoformat(), "finished_at": (start + timedelta(minutes=1)).isoformat(),
                    "decision": encoded_decision(),
                    "tool_telemetry": {"fallback_count": 8}}
        atomic_write_json(base / "analysis.json", analysis)
        atomic_write_json(base / "execution_contract.json", {"ticker": ticker, "analysis_asof": analysis["finished_at"],
            "action_if_triggered": "NONE", "portfolio_stance": "NEUTRAL", "entry_action_base": "WAIT",
            "setup_quality": "DEVELOPING", "confidence": .5, "reason_codes": []})
        rows.append({"ticker": ticker, "status": "success", "decision": analysis["decision"],
                     "artifacts": {"analysis_json": f"tickers/{ticker}/analysis.json",
                                   "execution_contract_json": f"tickers/{ticker}/execution_contract.json"}})
    result = {"run_id": identity, "label": "local-scheduler-us-full", "status": "success",
              "started_at": start.isoformat(), "finished_at": (start + timedelta(minutes=2)).isoformat(),
              "settings": {"market": "US", "run_mode": mode}, "tickers": rows,
              "summary": {"configured_ticker_count": len(tickers), "failed_tickers": 0}}
    if parent:
        result["overlay_source_run_id"] = parent
    atomic_write_json(directory / "run.json", result)
    return directory, result


def revision(root, source, *, target="AAPL", identity="20261022T141000-revision"):
    plan = refresh.make_plan(root, source, [target], now=NOW, reasons=["scheduled_thesis_refresh"])
    parent_dir = refresh.manifest_path(root, source["run_id"]).parent
    directory = root / "runs/2026" / identity
    shutil.copytree(parent_dir / "tickers", directory / "tickers")
    current = deepcopy(source)
    current.update(run_id=identity, started_at=NOW.isoformat(), finished_at=(NOW + timedelta(minutes=10)).isoformat(),
                   settings={"market": "US", "run_mode": "selective_rerun_only"}, overlay_source_run_id=source["run_id"])
    base = directory / "tickers" / target
    analysis = json.loads((base / "analysis.json").read_text())
    analysis.update(started_at=NOW.isoformat(), finished_at=(NOW + timedelta(minutes=8)).isoformat())
    atomic_write_json(base / "analysis.json", analysis)
    contract = json.loads((base / "execution_contract.json").read_text())
    contract["analysis_asof"] = analysis["finished_at"]
    atomic_write_json(base / "execution_contract.json", contract)
    current["research_refresh"] = refresh.revision_receipt(root, directory, current, plan)
    atomic_write_json(directory / "run.json", current)
    return directory, current


def test_completed_revision_is_found_when_a_later_quote_wins_pointer(tmp_path):
    _, full = cohort(tmp_path)
    _, new = revision(tmp_path, full)
    _, quote = cohort(tmp_path, "20261022T141500-overlay", mode="overlay_only", parent=full["run_id"],
                      start=NOW + timedelta(minutes=5))
    for row in quote["tickers"]:
        row["artifacts"]["microstructure_snapshot_json"] = "microstructure.json"
        row["artifacts"]["microstructure_report_md"] = "microstructure.md"
    atomic_write_json(tmp_path / "latest-run.json", quote)
    selected = runner._resolve_latest_overlay_source_manifest(tmp_path, market="US", tickers=["AAPL", "AMD", "MSFT"])
    assert selected == new
    assert selected["research_refresh"]["carried_forward_tickers"] == ["AMD", "MSFT"]
    # A quote descending from the already adopted revision retains its identity.
    quote["overlay_source_run_id"] = new["run_id"]
    atomic_write_json(tmp_path / "latest-run.json", quote)
    assert runner._resolve_latest_overlay_source_manifest(tmp_path, market="US", tickers=["AAPL"]) == quote


@pytest.mark.parametrize("change", ["carried", "new", "contract", "receipt", "missing", "future", "market", "failed", "parent"])
def test_missing_corrupt_mismatched_or_unfinished_revision_is_not_adopted(tmp_path, change):
    _, full = cohort(tmp_path)
    directory, new = revision(tmp_path, full)
    if change in {"carried", "new", "contract"}:
        ticker = "AMD" if change == "carried" else "AAPL"
        filename = "execution_contract.json" if change == "contract" else "analysis.json"
        path = directory / "tickers" / ticker / filename
        data = json.loads(path.read_text())
        data["unexpected"] = True
        atomic_write_json(path, data)
    if change == "receipt":
        new["research_refresh"]["completed_targets"] = ["AMD"]
    if change == "missing":
        (directory / "tickers/AAPL/analysis.json").unlink()
    if change == "future":
        new["finished_at"] = (NOW + timedelta(days=1)).isoformat()
    if change == "market":
        new["settings"]["market"] = "KR"
    if change == "failed":
        new["status"] = "partial_failure"
    if change == "parent":
        new["research_refresh"]["plan"]["parent_run_id"] = "../escape"
    atomic_write_json(directory / "run.json", new)
    assert not refresh.verified_revision(tmp_path, new, market="US", now=NOW + timedelta(hours=1))
    assert refresh.prefer_completed_revision(tmp_path, full, market="US", tickers=["AAPL"], now=NOW + timedelta(hours=1)) == full


def test_new_full_baseline_supersedes_old_revision_even_if_old_revision_finishes_late(tmp_path):
    _, full = cohort(tmp_path)
    _, new = revision(tmp_path, full)
    _, replacement = cohort(tmp_path, "20261022T141600-full", start=NOW + timedelta(minutes=6))
    atomic_write_json(tmp_path / "latest-run.json", new)
    assert runner._resolve_latest_overlay_source_manifest(tmp_path, market="US", tickers=["AAPL"]) == replacement


@pytest.mark.parametrize("descendant", [False, True])
def test_latest_pointer_or_derived_quote_does_not_legitimize_damaged_research(tmp_path, descendant):
    _, full = cohort(tmp_path)
    directory, new = revision(tmp_path, full)
    (directory / "tickers/AAPL/analysis.json").write_text("damaged")
    latest = new
    if descendant:
        _, latest = cohort(tmp_path, "20261022T141500-quote", mode="overlay_only", parent=new["run_id"],
                           start=NOW + timedelta(minutes=5))
        for row in latest["tickers"]:
            row["artifacts"]["microstructure_snapshot_json"] = "microstructure.json"
    atomic_write_json(tmp_path / "latest-run.json", latest)
    assert runner._resolve_latest_overlay_source_manifest(tmp_path, market="US", tickers=["AAPL"]) == full


@pytest.mark.parametrize("targets", [[], ["AAPL"] * 2, ["AAPL", "AMD", "MSFT"], ["OTHER"]])
def test_request_does_not_expand_cohort_or_research_budget(tmp_path, targets):
    _, full = cohort(tmp_path)
    with pytest.raises(ValueError):
        refresh.make_plan(tmp_path, full, targets, now=NOW, reasons=["refresh"])


def test_changed_original_after_request_cannot_be_reinterpreted_as_recovery(tmp_path):
    directory, full = cohort(tmp_path)
    plan = refresh.make_plan(tmp_path, full, ["AAPL"], now=NOW, reasons=["refresh"])
    path = directory / "tickers/AMD/analysis.json"
    data = json.loads(path.read_text())
    decision = json.loads(data["decision"])
    decision["entry_action"] = "STARTER"
    data["decision"] = json.dumps(decision)
    atomic_write_json(path, data)
    with pytest.raises(ValueError, match="pinned source"):
        refresh.load_plan_source(tmp_path, plan, now=NOW)


def test_research_runner_replaces_selected_thesis_and_preserves_unchanged_bytes(tmp_path, monkeypatch):
    monkeypatch.setenv("TRADINGAGENTS_SOURCE_SHA", "a" * 40)
    directory, full = cohort(tmp_path)
    now = datetime.now(timezone.utc)
    plan = refresh.make_plan(tmp_path, full, ["AAPL"], now=now, reasons=["refresh"])
    config_path = tmp_path / "config.toml"
    config_path.write_text(f'''[run]
tickers = ["OTHER"]
market = "US"
run_mode = "selective_rerun_only"
[storage]
archive_dir = "{tmp_path.as_posix()}"
site_dir = "{(tmp_path / 'site').as_posix()}"
[execution]
enabled = false
[portfolio]
enabled = false
''')
    called = []
    def research(**kwargs):
        ticker = kwargs["ticker"]
        called.append(ticker)
        row = deepcopy(full["tickers"][0])
        base = kwargs["run_dir"] / "tickers" / ticker
        data = json.loads((directory / "tickers" / ticker / "analysis.json").read_text())
        data.update(started_at=datetime.now(timezone.utc).isoformat(), finished_at=datetime.now(timezone.utc).isoformat())
        atomic_write_json(base / "analysis.json", data)
        contract = json.loads((directory / "tickers" / ticker / "execution_contract.json").read_text())
        contract["analysis_asof"] = data["finished_at"]
        atomic_write_json(base / "execution_contract.json", contract)
        return row
    monkeypatch.setattr(runner, "_run_single_ticker", research)
    def forbidden(*a, **k):
        raise AssertionError("No universe discovery, price/order worker, portfolio model or duplicate news collection")
    for name in ("_resolve_run_ticker_universe", "collect_event_news", "_run_execution_overlay_passes",
                 "run_portfolio_pipeline", "_copy_latest_microstructure_artifacts"):
        monkeypatch.setattr(runner, name, forbidden)
    config = load_scheduled_config(config_path)
    result = runner.execute_scheduled_run(config, run_label="local-thesis-refresh-us", skip_site_build=True,
        defer_execution_handoff=True, research_refresh_plan=plan)
    assert result["status"] == "success"
    assert called == ["AAPL"]
    assert result["summary"]["total_tickers"] == 3
    assert result["research_refresh"]["carried_forward_tickers"] == ["AMD", "MSFT"]
    assert result["source_revision"] == result["research_refresh"]["source_revision"] == "a" * 40
    assert refresh.verified_revision(tmp_path, result, market="US", now=datetime.now(timezone.utc))
    target = refresh.manifest_path(tmp_path, result["run_id"]).parent
    for ticker in ("AMD", "MSFT"):
        assert (target / "tickers" / ticker / "analysis.json").read_bytes() == (directory / "tickers" / ticker / "analysis.json").read_bytes()
    assert parse_structured_decision(json.loads((target / "tickers/AAPL/analysis.json").read_text())["decision"]).entry_action.value == "WAIT"
