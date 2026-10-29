"""A completed repair needs canonical lineage, not a privileged label."""
from copy import deepcopy
from datetime import timedelta
from types import SimpleNamespace
import json
import pytest

from tests.test_research_recovery import recovery, append_partial_recovery, write
from tradingagents.scheduled.research_recovery import verified_completed_recovery
from tradingagents.scheduled import runner
from tradingagents import local_automation as local
from tradingagents.notifications.local import _local_market_producer


@pytest.fixture
def completed_recovery(recovery):
    recovery["source"]["label"] = "local-scheduler-us-full"
    write(recovery["root"] / "run.json", recovery["source"])
    child, directory = append_partial_recovery(recovery, succeed="XOM")
    child.update(label="manual-us-failed-recovery", status="success")
    child["active_universe"]["coverage"].update(complete=True, analysis_complete=True)
    write(directory / "run.json", child)
    attempt = json.loads((directory / "attempt.json").read_text())
    attempt["status"] = "SUCCESS"
    write(directory / "attempt.json", attempt)
    return recovery, child, directory


def test_completed_repair_admits_without_modifying_sources_or_refreshing_clocks(completed_recovery):
    fixture, child, directory = completed_recovery
    archive, now = fixture["config"].storage.archive_dir, fixture["now"]
    before = {p: p.read_bytes() for p in archive.rglob("*") if p.is_file()}
    assert verified_completed_recovery(archive, child, now=now)
    assert _local_market_producer(child, archive, now=now)
    assert not _local_market_producer(child)
    assert not runner._manifest_is_complete_overlay_baseline(child, market="US", requested_tickers=None, required_holding_tickers=None)
    selected = runner._resolve_latest_full_overlay_baseline_manifest(archive, market="US", now=now, write_discovery_index=False)
    assert selected["run_id"] == child["run_id"]
    assert runner._manifest_age_seconds(child, now=now, market="US") == 7200
    target = SimpleNamespace(workflow_file="daily-codex-analysis.yml", inputs={"profile":"us"},
                             window_start_kst=now - timedelta(hours=3))
    assert local.completed_target(local._scheduler_manifest_view(child), target, now=now, archive=archive)
    assert not local.completed_target(local._scheduler_manifest_view(child), target, now=now - timedelta(hours=1), archive=archive)
    assert {p: p.read_bytes() for p in archive.rglob("*") if p.is_file()} == before
    # A receipt valid at completion cannot renew research age after four days.
    assert runner._resolve_latest_full_overlay_baseline_manifest(archive, market="US", now=now+timedelta(days=5), write_discovery_index=False) is None


@pytest.mark.parametrize("case", ["no_receipt", "source_hash", "source_label", "changed_reused_file", "changed_new_file",
    "partial", "active", "future", "naive", "missing_date", "future_date", "selection", "model", "cohort", "noncanonical"])
def test_invalid_recovery_never_enters_production(completed_recovery, case):
    fixture, child, directory = completed_recovery
    if case == "no_receipt": child.pop("research_recovery")
    elif case == "source_hash": child["research_recovery"]["source_manifest_sha256"] = "0" * 64
    elif case == "source_label":
        parent = fixture["source"]
        parent["label"] = "smoke-us-test"
        write(fixture["root"] / "run.json", parent)
    elif case == "changed_reused_file":
        (directory / child["tickers"][0]["artifacts"]["report_markdown"]).write_text("tampered")
    elif case == "changed_new_file":
        path = directory / child["tickers"][1]["artifacts"]["analysis_json"]
        value = json.loads(path.read_text()); value["ticker"] = "OTHER"; write(path, value)
    elif case == "partial": child["status"] = "partial_failure"
    elif case == "active": write(directory / "attempt.json", {"status":"RUNNING"})
    elif case == "future": child["finished_at"] = (fixture["now"]+timedelta(days=1)).isoformat()
    elif case == "naive": child["started_at"] = "2026-10-29T12:00:00"
    elif case in {"missing_date", "future_date"}: child["tickers"][1]["analysis_date"] = None if case == "missing_date" else "2099-01-01"
    elif case == "selection": child["active_universe"]["coverage"]["complete"] = False
    elif case == "model": child["settings"]["quick_model"] = "different"
    elif case == "cohort": child["tickers"].pop()
    if case != "noncanonical": write(directory / "run.json", child)
    else: child = deepcopy(child); child["finished_at"] = fixture["now"].isoformat()
    assert not verified_completed_recovery(fixture["config"].storage.archive_dir, child, now=fixture["now"])
