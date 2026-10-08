from copy import deepcopy
from datetime import datetime, timezone
import importlib.util

import pytest
import yaml


spec = importlib.util.spec_from_file_location("followups", ".github/scripts/recover_missing_followups.py")
recovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recovery)
NOW = datetime(2026, 10, 8, 1, tzinfo=timezone.utc)
WORKFLOW = "intraday-overlay-refresh.yml"


def run(workflow=WORKFLOW, **changes):
    value = {"id": 100, "path": f".github/workflows/{workflow}",
             "head_repository": {"full_name": "owner/repo"}, "head_branch": "main",
             "actor": {"login": "github-actions[bot]"}, "event": "workflow_dispatch",
             "display_title": "Overlay [recovery_source=cloud_watchdog]",
             "status": "completed", "conclusion": "success", "run_attempt": 1,
             "created_at": "2026-10-08T00:00:00Z", "updated_at": "2026-10-08T00:20:00Z"}
    return value | changes


def followup(workflow, **changes):
    return run(workflow, id=200, display_title="Followup [upstream=100] [attempt=1] [dry_run=false]",
               **changes)


class Client:
    repository = "owner/repo"

    def __init__(self):
        self.upstream = run()
        self.histories = {w: [] for w in (*recovery.PRODUCERS, *recovery.FOLLOWUPS)}
        self.histories[WORKFLOW] = [self.upstream]
        self.jobs = [{"name": "overlay_refresh_us", "conclusion": "success"},
                     {"name": "deploy_overlay", "conclusion": "success"}]
        self.posts = []
        self.appear = None
        self.reads = {}
        self.fail_history = None
        self.changed = None

    def pages(self, path, key):
        if "/jobs" in path:
            return deepcopy(self.jobs)
        workflow = path.split("/workflows/")[1].split("/")[0]
        if workflow == self.fail_history:
            raise ValueError("Incomplete GitHub pagination")
        self.reads[workflow] = self.reads.get(workflow, 0) + 1
        if workflow == self.appear and self.reads[workflow] > 1:
            return [followup(workflow, status="in_progress")]
        return deepcopy(self.histories[workflow])

    def request(self, path, method="GET", payload=None):
        if method == "POST":
            self.posts.append((path, payload))
            workflow = path.split("/workflows/")[1].split("/")[0]
            self.histories[workflow].append(followup(workflow, status="queued"))
        else:
            return deepcopy(self.changed or self.upstream)


def test_missing_followups_dispatched_once_without_repeating_producer():
    client = Client()
    first = recovery.recover(client, now=NOW)
    assert all(r["dispatch_requested"] for r in first)
    assert {p[0] for p in client.posts} == {
        f"/actions/workflows/{w}/dispatches" for w in recovery.FOLLOWUPS}
    assert client.posts[0][1] == {"ref": "main", "inputs": {
        "upstream_run_id": "100", "upstream_run_attempt": "1", "dry_run": "false"}}
    assert all(r["reason"] == "active_followup" for r in recovery.recover(client, now=NOW))
    assert len(client.posts) == 2


@pytest.mark.parametrize("conclusion,expected", [("success", 2), ("failure", 1), ("skipped", 0)])
def test_prism_recovery_notifies_real_collection_and_mirrors_only_deployed_output(conclusion, expected):
    workflow = "daily-prism-telegram-reports.yml"
    client = Client()
    client.upstream = run(workflow, display_title="PRISM [recovery_source=cloud_watchdog]",
        conclusion="failure" if conclusion == "failure" else "success")
    client.histories[WORKFLOW] = []
    client.histories[workflow] = [client.upstream]
    client.jobs = [{"name": "build_prism_telegram_pages", "conclusion": conclusion},
        {"name": "deploy", "conclusion": "success" if conclusion == "success" else "skipped"}]
    result = recovery.recover(client, now=NOW)
    assert len(result) == len(client.posts) == expected
    assert all(r["dispatch_requested"] for r in result)
    if expected:
        assert all(r["reason"] == "active_followup" for r in recovery.recover(client, now=NOW))
        assert len(client.posts) == expected


@pytest.mark.parametrize("changes", [
    {"head_branch": "feature"}, {"head_repository": {"full_name": "evil/repo"}},
    {"path": f".github/workflows/{WORKFLOW}@other"}, {"event": "pull_request"},
    {"actor": {"login": "human"}}, {"display_title": "Overlay [recovery_source=native]"},
    {"status": "in_progress"}, {"conclusion": None}, {"run_attempt": 4},
    {"created_at": "2026-10-07T15:58:00Z"}, {"created_at": "2026-10-09T00:00:00Z"},
    {"updated_at": "2026-10-08T00:59:00Z"}, {"updated_at": "2026-10-07T23:00:00Z"},
    {"updated_at": "bad"}, {"updated_at": "2026-10-08T00:20:00"},
])
def test_untrusted_running_old_and_invalid_clock_never_dispatch(changes):
    client = Client()
    client.upstream.update(changes)
    assert recovery.recover(client, now=NOW) == []
    assert not client.posts


def test_gate_only_skips_and_failed_deploy_not_mirrored():
    client = Client()
    client.jobs[0]["conclusion"] = "skipped"
    assert recovery.recover(client, now=NOW) == []
    client.jobs[0]["conclusion"] = "failure"
    client.jobs[1]["conclusion"] = "skipped"
    client.upstream["conclusion"] = "failure"
    result = recovery.recover(client, now=NOW)
    assert len(result) == 1 and result[0]["workflow"] == recovery.FOLLOWUPS[0]


@pytest.mark.parametrize("changes,reason", [
    ({}, "followup_completed"),
    ({"status": "queued"}, "active_followup"),
    ({"conclusion": "failure", "run_attempt": 3}, "retry_budget_exhausted"),
    ({"conclusion": "failure", "updated_at": "2026-10-08T00:50:00Z"}, "retry_cooldown"),
    ({"conclusion": "failure", "updated_at": "bad"}, "retry_cooldown"),
    ({"conclusion": "failure"}, "missing_followup"),
])
def test_success_active_cooldown_and_native_rerun_budget(changes, reason):
    client = Client()
    for w in recovery.FOLLOWUPS:
        client.histories[w] = [followup(w, **changes)]
    result = recovery.recover(client, now=NOW)
    assert all(r["reason"] == reason for r in result)
    assert bool(client.posts) == (reason == "missing_followup")


def test_budget_accumulates_across_followup_runs_and_producer_attempts():
    client = Client()
    client.upstream["run_attempt"] = 2
    for w in recovery.FOLLOWUPS:
        client.histories[w] = [followup(w) | {"id": n} for n in range(3)]
    assert all(r["reason"] == "retry_budget_exhausted" for r in recovery.recover(client, now=NOW))
    assert not client.posts


def test_dry_run_and_unrelated_ids_do_not_cover_real_delivery():
    client = Client()
    for w in recovery.FOLLOWUPS:
        client.histories[w] = [followup(w) | {"display_title": title} for title in (
            "[upstream=100] [attempt=1] [dry_run=true]", "[upstream=1000] [attempt=1]",
            "[upstream=100] [attempt=2]")]
    assert all(r["dispatch_requested"] for r in recovery.recover(client, now=NOW))


def test_preview_no_mutation_and_incomplete_history_fails_before_dispatch():
    client = Client()
    assert len(recovery.recover(client, now=NOW, dry_run=True)) == 2
    assert not client.posts
    client.fail_history = recovery.FOLLOWUPS[-1]
    with pytest.raises(ValueError, match="Incomplete"):
        recovery.recover(client, now=NOW)
    assert not client.posts


def test_recheck_respects_late_native_followup_and_upstream_rerun():
    client = Client()
    client.appear = recovery.FOLLOWUPS[0]
    result = recovery.recover(client, now=NOW)
    assert result[0]["reason"] == "active_followup" and len(client.posts) == 1
    client = Client()
    client.changed = run(status="in_progress", run_attempt=2)
    assert all(r["reason"] == "upstream_changed" for r in recovery.recover(client, now=NOW))
    assert not client.posts


def test_workflow_provenance_and_serialized_watchdog_wiring():
    from pathlib import Path
    for workflow in recovery.FOLLOWUPS:
        value = yaml.safe_load(Path(".github/workflows", workflow).read_text())
        assert "[upstream=" in value["run-name"] and "[attempt=" in value["run-name"]
        triggers = value.get("on", value.get(True))
        assert "upstream_run_attempt" in triggers["workflow_dispatch"]["inputs"]
    value = yaml.safe_load(Path(".github/workflows/scheduled-actions-watchdog.yml").read_text())
    assert value["concurrency"] == {"group": "scheduled-actions-watchdog", "cancel-in-progress": False}
    steps = value["jobs"]["dispatch_missing_scheduled_actions"]["steps"]
    step = next(s for s in steps if "recover_missing_followups.py" in s.get("run", ""))
    assert "cancelled()" in step["if"] and "RECOVERY_DRY_RUN" in step["env"]
