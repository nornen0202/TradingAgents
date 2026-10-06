"""Retry only verified hosted-runner acquisition failures, never analysis errors."""
import json
import os
import re
import urllib.request
from datetime import datetime, timedelta, timezone


ACQUISITION_FAILURE = "The job was not acquired by Runner of type hosted even after multiple attempts"
ALLOWED_JOBS = {
    "daily-codex-analysis.yml": {"schedule_gate", "deploy"},
    "intraday-overlay-refresh.yml": {"overlay_gate", "deploy_overlay"},
    "tradingagents-mobile-notifications.yml": {"resolve", "Send remote-safe completion notification"},
}


class GitHubClient:
    def __init__(self, repository, token):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
            raise ValueError("Invalid repository")
        self.repository = repository
        self.token = token

    def request(self, path, method="GET"):
        request = urllib.request.Request(
            f"https://api.github.com/repos/{self.repository}{path}", method=method,
            headers={"Authorization": f"Bearer {self.token}",
                     "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read()
        return json.loads(data) if data else None

    def pages(self, path, key=None):
        separator = "&" if "?" in path else "?"
        result = []
        for page in range(1, 21):
            payload = self.request(f"{path}{separator}per_page=100&page={page}")
            items = payload[key] if key else payload
            result.extend(items)
            if len(items) < 100:
                return result
        raise ValueError("Incomplete GitHub pagination; refusing recovery")


def recovery_reason(client, run, now):
    """Return eligibility only after validating the current attempt and all failures."""
    if (run.get("head_repository") or {}).get("full_name") != client.repository or run.get("head_branch") != "main":
        return "untrusted_source"
    workflow_path, separator, workflow_ref = run.get("path", "").partition("@")
    allowed_refs = {"main", "refs/heads/main"}
    if re.fullmatch(r"[0-9a-f]{40}", run.get("head_sha", "")):
        allowed_refs.add(run["head_sha"])
    if separator and workflow_ref not in allowed_refs:
        return "untrusted_workflow_ref"
    workflow = workflow_path.removeprefix(".github/workflows/")
    if (not workflow_path.startswith(".github/workflows/") or workflow not in ALLOWED_JOBS
            or run.get("event") not in {"schedule", "workflow_dispatch", "workflow_run"}):
        return "unsupported_workflow"
    if run.get("status") != "completed" or run.get("conclusion") not in {"failure", "cancelled"}:
        return "not_failed"
    if not 1 <= int(run.get("run_attempt", 0)) < 3:
        return "retry_budget_exhausted"
    created = datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
    if created.tzinfo is None or not timedelta(0) <= now - created <= timedelta(hours=24):
        return "outside_recovery_window"
    jobs = client.pages(f"/actions/runs/{int(run['id'])}/attempts/{int(run['run_attempt'])}/jobs", "jobs")
    failed = [job for job in jobs if job.get("conclusion") in {"failure", "cancelled", "timed_out", "action_required", "startup_failure"}]
    if not failed:
        return "no_failed_jobs"
    for job in failed:
        if (job.get("name") not in ALLOWED_JOBS[workflow] or job.get("steps") != []
                or job.get("runner_name") or job.get("status") != "completed"):
            return "job_started_or_not_allowed"
        # check_run_url is validated and reduced to a local API path, never fetched as an arbitrary URL.
        match = re.fullmatch(
            re.escape(f"https://api.github.com/repos/{client.repository}/check-runs/") + r"([0-9]+)",
            job.get("check_run_url", ""),
        )
        if not match:
            return "missing_check_run"
        annotations = client.pages(f"/check-runs/{match[1]}/annotations")
        if not any(a.get("annotation_level") == "failure" and a.get("message", "").strip() == ACQUISITION_FAILURE
                   for a in annotations):
            return "unverified_acquisition_failure"
    return "hosted_runner_not_acquired"


def recover(client, run_id, *, now, dry_run=False):
    if not str(run_id).isdigit():
        raise ValueError("Invalid upstream run ID")
    path = f"/actions/runs/{run_id}"
    run = client.request(path)
    reason = recovery_reason(client, run, now)
    result = {"run_id": int(run_id), "run_attempt": run.get("run_attempt"), "reason": reason, "rerun_requested": False}
    if reason == "hosted_runner_not_acquired" and not dry_run:
        # Avoid acting on a stale workflow_run event after another recovery has started.
        current = client.request(path)
        if current.get("status") != "completed" or current.get("run_attempt") != run.get("run_attempt"):
            result["reason"] = "attempt_changed"
        else:
            client.request(path + "/rerun-failed-jobs", method="POST")
            result["rerun_requested"] = True
    return result


if __name__ == "__main__":
    client = GitHubClient(os.environ["GITHUB_REPOSITORY"], os.environ["GH_TOKEN"])
    result = recover(client, os.environ["UPSTREAM_RUN_ID"], now=datetime.now(timezone.utc),
                     dry_run=os.environ.get("RECOVERY_DRY_RUN", "false").lower() == "true")
    print(json.dumps(result))
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as summary:
            summary.write("Hosted runner recovery: `" + json.dumps(result) + "`\n")
