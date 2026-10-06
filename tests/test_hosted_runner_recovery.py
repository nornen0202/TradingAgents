from copy import deepcopy
from datetime import datetime, timezone
import importlib.util
from pathlib import Path

import pytest
import yaml


spec = importlib.util.spec_from_file_location("hosted_recovery", ".github/scripts/recover_hosted_runner.py")
recovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recovery)
NOW = datetime(2026, 10, 6, 7, tzinfo=timezone.utc)


class Client:
    repository = "owner/repo"

    def __init__(self):
        self.run = {"id": 123, "head_repository": {"full_name": self.repository}, "head_branch": "main",
                    "path": ".github/workflows/daily-codex-analysis.yml", "event": "schedule",
                    "status": "completed", "conclusion": "failure", "run_attempt": 1,
                    "created_at": "2026-10-05T18:33:25Z"}
        self.jobs = [{"name": "deploy", "conclusion": "cancelled", "status": "completed", "steps": [],
                      "runner_name": "", "check_run_url": "https://api.github.com/repos/owner/repo/check-runs/456"}]
        self.annotations = [{"annotation_level": "failure", "message": recovery.ACQUISITION_FAILURE}]
        self.posts = []
        self.changed = False
        self.reads = 0

    def request(self, path, method="GET"):
        if method == "POST":
            self.posts.append(path)
            return None
        self.reads += 1
        result = deepcopy(self.run)
        if self.changed and self.reads > 1:
            result["run_attempt"] += 1
        return result

    def pages(self, path, key=None):
        return self.jobs if key == "jobs" else self.annotations


@pytest.mark.parametrize("workflow,job", [(w, j) for w, jobs in recovery.ALLOWED_JOBS.items() for j in jobs])
def test_retries_only_failed_jobs_and_preserves_successful_analysis(workflow, job):
    client = Client()
    client.run["path"] = ".github/workflows/" + workflow
    client.jobs[0]["name"] = job
    client.jobs.append({"name": "analyze_us", "conclusion": "success", "steps": [{"name": "analysis"}]})
    assert recovery.recover(client, 123, now=NOW)["rerun_requested"]
    assert client.posts == ["/actions/runs/123/rerun-failed-jobs"]


@pytest.mark.parametrize("mutate", [
    lambda c: c.run.update(head_branch="feature"),
    lambda c: c.run.update(head_repository={"full_name": "other/fork"}),
    lambda c: c.run.update(path=".github/workflows/unknown.yml"),
    lambda c: c.run.update(event="pull_request"),
    lambda c: c.run.update(status="in_progress"),
    lambda c: c.run.update(conclusion="success"),
    lambda c: c.run.update(run_attempt=3),
    lambda c: c.run.update(created_at="2026-10-04T18:33:25Z"),
    lambda c: c.run.update(created_at="2026-10-07T18:33:25Z"),
    lambda c: c.jobs[0].update(steps=[{"name": "started"}]),
    lambda c: c.jobs[0].pop("steps"),
    lambda c: c.jobs[0].update(runner_name="runner"),
    lambda c: c.jobs[0].update(name="analyze_kr"),
    lambda c: c.jobs[0].update(check_run_url="https://example.com/check-runs/456"),
    lambda c: c.annotations[0].update(message="The operation was canceled."),
    lambda c: c.annotations[0].update(annotation_level="notice"),
    lambda c: c.jobs.clear(),
    lambda c: c.jobs.append({"name": "analyze_kr", "conclusion": "failure", "steps": [{"name": "analysis"}]}),
])
def test_unsafe_or_unproven_retries_are_rejected(mutate):
    client = Client()
    mutate(client)
    assert not recovery.recover(client, 123, now=NOW)["rerun_requested"]
    assert client.posts == []


def test_dry_run_and_concurrent_recovery_do_not_post():
    client = Client()
    result = recovery.recover(client, 123, now=NOW, dry_run=True)
    assert result["reason"] == "hosted_runner_not_acquired"
    assert not result["rerun_requested"]
    client.changed = True
    client.reads = 0
    assert recovery.recover(client, 123, now=NOW)["reason"] == "attempt_changed"
    assert client.posts == []


@pytest.mark.parametrize("suffix", ["", "@main", "@refs/heads/main", "@" + "a" * 40])
def test_documented_workflow_ref_suffix_is_normalized(suffix):
    client = Client()
    client.run["head_sha"] = "a" * 40
    client.run["path"] += suffix
    assert recovery.recover(client, 123, now=NOW)["rerun_requested"]


@pytest.mark.parametrize("path", [
    ".github/workflows/daily-codex-analysis.yml@feature",
    ".github/workflows/daily-codex-analysis.yml@",
    ".github/workflows/daily-codex-analysis.yml@main@feature",
    ".github/workflows/daily-codex-analysis.yml@" + "b" * 40,
    "daily-codex-analysis.yml",
])
def test_untrusted_workflow_refs_and_paths_are_rejected(path):
    client = Client()
    client.run.update(path=path, head_sha="a" * 40)
    assert not recovery.recover(client, 123, now=NOW)["rerun_requested"]
    assert client.posts == []


def test_pagination_does_not_drop_later_failures():
    client = recovery.GitHubClient("owner/repo", "unused")
    calls = []
    def request(path):
        calls.append(path)
        return {"jobs": [1] * 100 if path.endswith("&page=1") else [2]}
    client.request = request
    assert len(client.pages("/jobs?filter=latest", "jobs")) == 101
    assert calls[-1].endswith("&per_page=100&page=2")


def test_workflow_uses_trusted_main_and_separate_hosted_pool():
    workflow = yaml.safe_load(Path(".github/workflows/hosted-runner-recovery.yml").read_text())
    assert workflow["permissions"] == {"actions": "write", "checks": "read", "contents": "read"}
    job = workflow["jobs"]["recover"]
    assert job["runs-on"] == "windows-latest"
    assert job["steps"][0]["with"] == {"ref": "main", "persist-credentials": False}
    assert "Hosted Runner Recovery" not in workflow[True]["workflow_run"]["workflows"]
