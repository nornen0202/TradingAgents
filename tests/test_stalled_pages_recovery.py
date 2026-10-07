from copy import deepcopy
from datetime import datetime, timezone
import importlib.util

import pytest
import yaml


spec = importlib.util.spec_from_file_location("stalled_pages", ".github/scripts/recover_stalled_pages.py")
recovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recovery)
NOW = datetime(2026, 10, 7, 5, tzinfo=timezone.utc)


class Client:
    repository = "owner/repo"

    def __init__(self, successor=True):
        self.group = {"group_members": [{"run_id": 123, "job_id": 456, "status": "in_progress"}]}
        if successor:
            self.group["group_members"].append({"run_id": 124, "job_id": 457, "status": "pending"})
        self.run = {"id": 123, "head_repository": {"full_name": self.repository}, "head_branch": "main",
                    "path": ".github/workflows/intraday-overlay-refresh.yml", "event": "workflow_dispatch",
                    "status": "waiting", "run_attempt": 1, "created_at": "2026-10-06T15:10:05Z"}
        self.job = {"id": 456, "name": "deploy_overlay", "status": "waiting", "steps": [],
                    "runner_id": None, "runner_name": None, "started_at": "2026-10-06T15:16:15Z"}
        self.jobs = [{"id": 455, "name": "publish_overlay_site", "status": "completed", "conclusion": "success"}, self.job]
        self.pending = [{"environment": {"name": "github-pages"}, "reviewers": [], "wait_timer": 0}]
        self.environment = {"protection_rules": [{"type": "branch_policy"}]}
        self.posts = []
        self.group_reads = 0
        self.change = False

    def request(self, path, method="GET"):
        if method == "POST":
            self.posts.append(path)
            if path.endswith("/force-cancel"):
                self.run.update(status="completed", conclusion="cancelled")
            return None
        if "/concurrency_groups/" in path:
            self.group_reads += 1
            if self.change and self.group_reads > 1:
                self.job.update(status="in_progress", runner_name="runner")
            return deepcopy(self.group)
        if "/pending_deployments" in path:
            return deepcopy(self.pending)
        if "/environments/" in path:
            return deepcopy(self.environment)
        return deepcopy(self.job if "/jobs/" in path else self.run)

    def pages(self, path, key=None):
        return deepcopy(self.jobs)


def test_releases_real_incident_and_preserves_newer_pending_snapshot():
    client = Client()
    result = recovery.recover(client, now=NOW)
    assert result["cancel_requested"] and not result["rerun_requested"]
    assert client.posts == ["/actions/runs/123/force-cancel"]


def test_without_successor_retries_only_failed_jobs_after_cancellation():
    client = Client(successor=False)
    assert recovery.recover(client, now=NOW)["rerun_requested"]
    assert client.posts == ["/actions/runs/123/force-cancel", "/actions/runs/123/rerun-failed-jobs"]


@pytest.mark.parametrize("mutate", [
    lambda c: c.run.update(head_branch="feature"),
    lambda c: c.run.update(head_repository={"full_name": "other/repo"}),
    lambda c: c.run.update(path=".github/workflows/unknown.yml"),
    lambda c: c.run.update(path=c.run["path"] + "@other"),
    lambda c: c.run.update(event="pull_request"),
    lambda c: c.run.update(run_attempt=4),
    lambda c: c.run.update(status="completed"),
    lambda c: c.job.update(status="in_progress"),
    lambda c: c.job.update(status="queued"),
    lambda c: c.job.update(steps=[{"name": "started"}]),
    lambda c: c.job.pop("steps"),
    lambda c: c.job.update(runner_id=1),
    lambda c: c.job.update(runner_name="runner"),
    lambda c: c.job.update(started_at="2026-10-07T04:30:00Z"),
    lambda c: c.job.update(started_at="2026-10-07T06:00:00Z"),
    lambda c: c.job.update(started_at="2026-10-05T20:00:00Z"),
    lambda c: c.job.update(started_at="invalid"),
    lambda c: c.jobs[0].update(conclusion="failure"),
    lambda c: c.jobs.append({"id": 454, "status": "in_progress"}),
    lambda c: c.pending[0].update(reviewers=[{"reviewer": {"login": "human"}}]),
    lambda c: c.pending[0].update(wait_timer=60),
    lambda c: c.pending.clear(),
    lambda c: c.environment.update(protection_rules=[{"type": "required_reviewers"}]),
    lambda c: c.environment.update(protection_rules=[{"type": "custom_deployment_protection_rule"}]),
])
def test_never_cancels_untrusted_started_protected_or_recent_jobs(mutate):
    client = Client()
    mutate(client)
    assert not recovery.recover(client, now=NOW)["cancel_requested"]
    assert not client.posts


def test_rechecks_lease_before_mutation_and_supports_dry_run():
    client = Client()
    client.change = True
    assert recovery.recover(client, now=NOW)["reason"] == "lease_changed"
    assert not client.posts
    client = Client()
    assert recovery.recover(client, now=NOW, dry_run=True)["reason"] == "stalled_unstarted_pages"
    assert not client.posts


def test_last_attempt_releases_lease_without_an_unbounded_retry():
    client = Client(successor=False)
    client.run["run_attempt"] = 3
    result = recovery.recover(client, now=NOW)
    assert result["cancel_requested"] and not result["rerun_requested"]


def test_watchdog_and_pages_queue_are_wired():
    from pathlib import Path
    workflows = Path(".github/workflows")
    watchdog = yaml.safe_load((workflows / "scheduled-actions-watchdog.yml").read_text())
    assert any("recover_stalled_pages.py" in step.get("run", "")
               for step in watchdog["jobs"]["dispatch_missing_scheduled_actions"]["steps"])
    for path in workflows.glob("*.yml"):
        workflow = yaml.safe_load(path.read_text())
        for job in workflow.get("jobs", {}).values():
            concurrency = job.get("concurrency", {})
            if concurrency.get("group") == recovery.GROUP:
                assert concurrency["queue"] == "max"
                assert concurrency["cancel-in-progress"] is False
