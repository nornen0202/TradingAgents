"""Scheduled overlays wait for research without spending worker attempts."""
from datetime import datetime, timedelta
import hashlib
import json
from types import SimpleNamespace

import pytest

from tradingagents import local_automation as local
from tradingagents.scheduled import runner
from tests.test_scheduled_run_mode import _write_full_overlay_baseline


AT = datetime.fromisoformat("2026-10-28T23:45:00+09:00")


@pytest.fixture
def admission(tmp_path, monkeypatch):
    from tradingagents import local_advisory_recovery
    from tradingagents.notifications import local as notifications

    item = SimpleNamespace(name="intraday-overlay-us-1028-2340",
        workflow_file="intraday-overlay-refresh.yml", inputs={"profile": "us"},
        window_start_kst=AT - timedelta(minutes=5), max_failed_attempts=4)
    monkeypatch.setattr(local, "script", lambda _: SimpleNamespace(due_targets=lambda *a, **kw: [item]))
    monkeypatch.setattr(local, "local_target_window_start", lambda *a, **kw: item.window_start_kst)
    monkeypatch.setattr(runner, "_iter_run_manifests_desc", lambda *a, **kw: [])
    monkeypatch.setattr(local_advisory_recovery, "recover_due", lambda *a, **kw: [])
    monkeypatch.setattr(local.subprocess, "run", lambda *a, **kw: pytest.fail("Unready overlay admitted"))
    monkeypatch.setattr(local, "preflight", lambda *a: pytest.fail("Overlay started model preflight"))
    monkeypatch.setattr(notifications, "queue_failure", lambda *a, **kw: pytest.fail("Dependency wait notified as failure"))
    return tmp_path / "archive", tmp_path / "state", item


def baseline(archive, **updates):
    manifest = _write_full_overlay_baseline(archive, tickers=["AAPL"],
        started_at=(AT - timedelta(hours=6)).isoformat(),
        run_id="20261028T175000_local-scheduler-us-full")
    manifest.update(updates)
    save_baseline(archive, manifest)
    return manifest


def save_baseline(archive, manifest):
    for path in (archive / "latest-run.json", archive / "runs/2026" / manifest["run_id"] / "run.json"):
        path.write_text(json.dumps(manifest), encoding="utf-8")


@pytest.mark.parametrize("case", [
    "empty", "stale", "too_many_sessions", "future", "missing_date", "invalid_date",
    "other_market", "failed", "running", "partial", "incomplete_coverage", "overlay_only",
])
@pytest.mark.parametrize("dry_run", [False, True])
def test_unready_baseline_waits_without_attempts_or_archive_writes(admission, case, dry_run):
    archive, state, item = admission
    if case != "empty":
        manifest = baseline(archive)
        if case in {"stale", "too_many_sessions", "future", "missing_date", "invalid_date"}:
            manifest["started_at"] = {
                "stale": (AT - timedelta(days=7)).isoformat(),
                "too_many_sessions": (AT - timedelta(days=2)).isoformat(),
                "future": (AT + timedelta(hours=1)).isoformat(),
                "missing_date": None, "invalid_date": "not-a-date",
            }[case]
        elif case == "other_market":
            manifest["settings"]["market"] = "KR"
        elif case in {"failed", "running", "partial"}:
            manifest["status"] = {"failed": "failed", "running": "running", "partial": "partial_failure"}[case]
        elif case == "incomplete_coverage":
            manifest["active_universe"] = {"coverage": {"complete": False}}
        elif case == "overlay_only":
            manifest["settings"]["run_mode"] = "overlay_only"
        save_baseline(archive, manifest)
    before = {p: p.read_bytes() for p in archive.rglob("*") if p.is_file()}
    for now in (AT, AT + timedelta(minutes=1)):
        assert local.run_due(archive, state, now=now, dry_run=dry_run) == [
            {"target": item.name, "status": "WAITING_RESEARCH_BASELINE"}]
    assert not state.exists()
    assert {p: p.read_bytes() for p in archive.rglob("*") if p.is_file()} == before


def test_unreadable_baseline_fails_closed_without_leaking_error_or_spending_attempt(admission):
    archive, state, item = admission
    archive.mkdir()
    (archive / "latest-run.json").write_text("private-invalid-manifest", encoding="utf-8")
    assert local.run_due(archive, state, now=AT) == [
        {"target": item.name, "status": "OVERLAY_BASELINE_UNVERIFIED", "error_type": "JSONDecodeError"}]
    assert not state.exists()


def test_kr_overlay_waits_for_same_market_research(admission):
    archive, state, item = admission
    item.inputs["profile"] = "kr"
    manifest = baseline(archive)
    assert local.run_due(archive, state, now=AT)[0]["status"] == "WAITING_RESEARCH_BASELINE"
    manifest["settings"]["market"] = "KR"
    save_baseline(archive, manifest)
    assert local.run_due(archive, state, now=AT, dry_run=True) == [{"target": item.name, "status": "DUE"}]
    assert not state.exists()


def test_new_completed_research_resumes_same_slot_without_resetting_history(admission, monkeypatch):
    archive, state, item = admission
    key = hashlib.sha256(f"{item.name}:{item.window_start_kst.isoformat()}".encode()).hexdigest()
    receipt_path = state / "attempts" / f"{key}.json"
    receipt_path.parent.mkdir(parents=True)
    receipt_path.write_text(json.dumps({"attempts": 1, "started_at": (AT - timedelta(hours=2)).isoformat(),
        "exit_code": 1}), encoding="utf-8")
    original = receipt_path.read_bytes()
    baseline(archive, status="running")
    assert local.run_due(archive, state, now=AT)[0]["status"] == "WAITING_RESEARCH_BASELINE"
    assert receipt_path.read_bytes() == original
    baseline(archive, status="success")
    assert local.run_due(archive, state, now=AT, dry_run=True) == [{"target": item.name, "status": "DUE"}]
    assert receipt_path.read_bytes() == original
    calls = []
    monkeypatch.setattr(local, "require_storage_headroom", lambda *a: None)
    monkeypatch.setattr(local.subprocess, "run", lambda args, **kw: calls.append(args) or SimpleNamespace(returncode=0))
    assert local.run_due(archive, state, now=AT) == [{"target": item.name, "status": "DUE"}]
    assert len(calls) == 1
    assert calls[0][calls[0].index("--run-mode") + 1] == "overlay_only"
    assert "--strict" in calls[0] and "--resume-from-run" not in calls[0]
    assert json.loads(receipt_path.read_text())["attempts"] == 2
    assert list((state / "attempts").iterdir()) == [receipt_path]


@pytest.mark.parametrize("attempts,minutes_ago", [(4, 120), (1, 5)])
def test_existing_budget_and_cooldown_still_precede_baseline_admission(admission, monkeypatch, attempts, minutes_ago):
    archive, state, item = admission
    key = hashlib.sha256(f"{item.name}:{item.window_start_kst.isoformat()}".encode()).hexdigest()
    path = state / "attempts" / f"{key}.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"attempts": attempts,
        "started_at": (AT - timedelta(minutes=minutes_ago)).isoformat(), "exit_code": 1}), encoding="utf-8")
    original = path.read_bytes()
    monkeypatch.setattr(runner, "_resolve_latest_full_overlay_baseline_manifest",
        lambda *a, **kw: pytest.fail("Budget bypassed for baseline check"))
    assert local.run_due(archive, state, now=AT) == [
        {"target": item.name, "status": "RETRY_BUDGET_OR_COOLDOWN"}]
    assert path.read_bytes() == original
