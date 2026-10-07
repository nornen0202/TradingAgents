"""Release a verified unstarted Pages lease without bypassing approval rules."""
from datetime import datetime, timedelta, timezone
import json
import os
import time
from urllib.error import HTTPError


GROUP = "tradingagents-pages-deploy"
ALLOWED = {
    "daily-codex-analysis.yml": ("deploy", ("build_pages",)),
    "intraday-overlay-refresh.yml": ("deploy_overlay", ("publish_overlay_site",)),
    "work-report-pages-refresh.yml": ("deploy", ("build_work_report_pages",)),
    "daily-youtube-reports.yml": ("deploy", ("build_youtube_pages",)),
    "daily-prism-telegram-reports.yml": ("deploy", ("build_prism_telegram_pages",)),
    "account-portfolio-report-verify.yml": ("deploy", ("verify_kr", "verify_us")),
}


def inspect(client, now):
    try:
        group = client.request(f"/actions/concurrency_groups/{GROUP}")
    except HTTPError as exc:
        if exc.code == 404:
            return None, "no_active_lease"
        raise
    members = group.get("group_members", [])
    holders = [m for m in members if m.get("status") == "in_progress"]
    if len(holders) != 1 or not holders[0].get("job_id"):
        return None, "no_unique_job_lease"
    holder = holders[0]
    run_id, job_id = int(holder["run_id"]), int(holder["job_id"])
    run = client.request(f"/actions/runs/{run_id}")
    path, _, ref = run.get("path", "").partition("@")
    workflow = path.removeprefix(".github/workflows/")
    if (not path.startswith(".github/workflows/") or workflow not in ALLOWED
            or ref not in {"", "main", "refs/heads/main", run.get("head_sha")}
            or (run.get("head_repository") or {}).get("full_name") != client.repository
            or run.get("head_branch") != "main"
            or run.get("event") not in {"schedule", "workflow_dispatch"}
            or run.get("status") == "completed"
            or not 1 <= int(run.get("run_attempt", 0)) <= 3):
        return None, "untrusted_or_ineligible_run"
    job = client.request(f"/actions/jobs/{job_id}")
    deploy, build = ALLOWED[workflow]
    if (job.get("name") != deploy or job.get("status") != "waiting"
            or job.get("steps") != [] or job.get("runner_name") or job.get("runner_id")):
        return None, "deployment_started_or_not_waiting"
    try:
        started = datetime.fromisoformat(job["started_at"].replace("Z", "+00:00"))
        created = datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
        if (started.tzinfo is None or created.tzinfo is None or started < created
                or not timedelta(minutes=45) <= now - started <= timedelta(hours=24)):
            return None, "outside_stall_window"
    except (KeyError, ValueError, TypeError):
        return None, "invalid_clock"
    # Failed-job reruns may retain successful upstream jobs from older attempts.
    # Fold oldest to newest so a later failure never gets masked by old success.
    latest_jobs = {}
    for attempt in range(1, int(run["run_attempt"]) + 1):
        for previous in client.pages(f"/actions/runs/{run_id}/attempts/{attempt}/jobs", "jobs"):
            latest_jobs[previous.get("name")] = previous
    jobs = list(latest_jobs.values())
    if (not any(j.get("name") in build and j.get("conclusion") == "success" for j in jobs)
            or latest_jobs.get(deploy, {}).get("id") != job_id
            or any(j.get("id") != job_id and (
                j.get("status") != "completed" or j.get("conclusion") not in {"success", "skipped"}
            ) for j in jobs)):
        return None, "upstream_not_successful"
    pending = client.request(f"/actions/runs/{run_id}/pending_deployments")
    if (len(pending) != 1 or pending[0].get("environment", {}).get("name") != "github-pages"
            or pending[0].get("reviewers") != [] or pending[0].get("wait_timer") != 0):
        return None, "approval_or_timer_required"
    environment = client.request("/environments/github-pages")
    # Never release a lease that is intentionally waiting for a human, timer,
    # or custom protection app. Branch restrictions themselves remain intact.
    rules = environment.get("protection_rules")
    if not isinstance(rules, list) or any(rule.get("type") != "branch_policy" for rule in rules):
        return None, "environment_protection_required"
    return {"run_id": run_id, "job_id": job_id, "attempt": run["run_attempt"],
            "started_at": job["started_at"],
            "has_successor": any(m.get("status") == "pending" for m in members)}, "stalled_unstarted_pages"


def recover(client, *, now, dry_run=False, sleep=time.sleep):
    candidate, reason = inspect(client, now)
    result = {"reason": reason, "cancel_requested": False, "rerun_requested": False}
    if not candidate:
        return result
    result.update(candidate)
    if dry_run:
        return result
    # Re-read the lease, attempt, job, and approval rules immediately before
    # mutation. Do not cancel a job that acquired a runner in the meantime.
    current, reason = inspect(client, now)
    if current != candidate:
        result["reason"] = "lease_changed"
        return result
    path = f"/actions/runs/{candidate['run_id']}"
    client.request(path + "/force-cancel", method="POST")
    result["cancel_requested"] = True
    if candidate["has_successor"] or candidate["attempt"] >= 3:
        return result
    # Retain successful analysis/build jobs if no newer snapshot is queued.
    # Retry only failed jobs, with the existing rollback and lineage guards.
    for _ in range(5):
        cancelled = client.request(path)
        if cancelled.get("run_attempt") != candidate["attempt"]:
            result["reason"] = "attempt_changed"
            return result
        if cancelled.get("status") == "completed":
            if cancelled.get("conclusion") == "cancelled":
                client.request(path + "/rerun-failed-jobs", method="POST")
                result["rerun_requested"] = True
            return result
        sleep(2)
    result["reason"] = "cancellation_pending"
    return result


if __name__ == "__main__":
    from recover_hosted_runner import GitHubClient

    client = GitHubClient(os.environ["GITHUB_REPOSITORY"], os.environ["GH_TOKEN"])
    print(json.dumps(recover(client, now=datetime.now(timezone.utc),
                             dry_run=os.environ.get("RECOVERY_DRY_RUN", "false").lower() == "true")))
