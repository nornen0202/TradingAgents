"""Reconcile completed watchdog producers whose workflow_run followups were lost."""
from datetime import datetime, timedelta, timezone
import json
import os
from urllib.parse import urlencode


PRODUCERS = {
    "daily-codex-analysis.yml": {"analyze_kr", "analyze_us"},
    "intraday-overlay-refresh.yml": {"overlay_refresh_kr", "overlay_refresh_us"},
    "daily-youtube-reports.yml": {"build_youtube_pages"},
}
FOLLOWUPS = ("tradingagents-mobile-notifications.yml", "publish-ai-context.yml")
# Earlier incidents were already delivered manually, before provenance run names
# existed. Never replay those historical sends during rollout.
NOT_BEFORE = datetime(2026, 10, 7, 15, 59, tzinfo=timezone.utc)


def timestamp(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo is not None else None
    except (AttributeError, TypeError, ValueError):
        return None


def trusted(run, workflow, repository):
    path, _, ref = str(run.get("path", "")).partition("@")
    return (path == f".github/workflows/{workflow}"
            and ref in {"", "main", "refs/heads/main", run.get("head_sha")}
            and (run.get("head_repository") or {}).get("full_name") == repository
            and run.get("head_branch") == "main")


def history(client, workflow, since):
    query = urlencode({"branch": "main", "created": ">=" + since.isoformat()})
    return client.pages(f"/actions/workflows/{workflow}/runs?{query}", "workflow_runs")


def eligible(run, workflow, repository, now):
    created, finished = timestamp(run.get("created_at")), timestamp(run.get("updated_at"))
    return (trusted(run, workflow, repository)
            and run.get("event") == "workflow_dispatch"
            and (run.get("actor") or {}).get("login") == "github-actions[bot]"
            and "[recovery_source=cloud_watchdog]" in run.get("display_title", "")
            and run.get("status") == "completed"
            and run.get("conclusion") in {"success", "failure", "cancelled", "timed_out"}
            and isinstance(run.get("run_attempt"), int) and 1 <= run["run_attempt"] <= 3
            and created is not None and max(NOT_BEFORE, now - timedelta(hours=24)) <= created <= now
            and finished is not None and created <= finished <= now - timedelta(minutes=3))


def followup_reason(runs, upstream, workflow, repository, now):
    marker = f"[upstream={upstream['id']}]"
    attempts = [r for r in runs if trusted(r, workflow, repository)
                and r.get("event") in {"workflow_run", "workflow_dispatch"}
                and marker in r.get("display_title", "")
                and "[dry_run=true]" not in r.get("display_title", "")]
    current = [r for r in attempts
               if f"[attempt={upstream['run_attempt']}]" in r.get("display_title", "")]
    # Any active attempt owns this upstream, including a previous producer attempt.
    if any(r.get("status") != "completed" for r in attempts):
        return "active_followup"
    if any(r.get("conclusion") == "success" for r in current):
        return "followup_completed"
    if sum(max(int(r.get("run_attempt", 1)), 1) for r in attempts) >= 3:
        return "retry_budget_exhausted"
    if any(timestamp(r.get("updated_at")) is None
           or now - timestamp(r["updated_at"]) < timedelta(minutes=15) for r in attempts):
        return "retry_cooldown"
    return "missing_followup"


def recover(client, *, now, dry_run=False):
    since = max(NOT_BEFORE, now - timedelta(hours=24))
    # Complete every paginated read before issuing any dispatch. Incomplete
    # history is an error, never evidence that a send is missing.
    histories = {w: history(client, w, since) for w in (*PRODUCERS, *FOLLOWUPS)}
    results = []
    for workflow in PRODUCERS:
        for upstream in histories[workflow]:
            if not eligible(upstream, workflow, client.repository, now):
                continue
            jobs = client.pages(f"/actions/runs/{int(upstream['id'])}/jobs", "jobs")
            if not any(j.get("name") in PRODUCERS[workflow]
                       and j.get("conclusion") != "skipped" for j in jobs):
                continue
            for followup in FOLLOWUPS:
                if followup == "publish-ai-context.yml" and not any(
                    j.get("name") in {"deploy", "deploy_overlay"}
                    and j.get("conclusion") == "success" for j in jobs
                ):
                    continue
                reason = followup_reason(histories[followup], upstream, followup, client.repository, now)
                result = {"upstream_run_id": upstream["id"], "upstream_run_attempt": upstream["run_attempt"],
                          "workflow": followup, "reason": reason, "dispatch_requested": False}
                results.append(result)
                if reason != "missing_followup" or dry_run:
                    continue
                # A delayed native followup or a producer rerun may have appeared.
                fresh = client.request(f"/actions/runs/{int(upstream['id'])}")
                if not eligible(fresh, workflow, client.repository, now) or fresh["run_attempt"] != upstream["run_attempt"]:
                    result["reason"] = "upstream_changed"
                    continue
                reason = followup_reason(history(client, followup, since), fresh, followup, client.repository, now)
                result["reason"] = reason
                if reason != "missing_followup":
                    continue
                inputs = {"upstream_run_id": str(upstream["id"]),
                          "upstream_run_attempt": str(upstream["run_attempt"])}
                if followup == FOLLOWUPS[0]:
                    inputs["dry_run"] = "false"
                client.request(f"/actions/workflows/{followup}/dispatches", method="POST",
                               payload={"ref": "main", "inputs": inputs})
                result["dispatch_requested"] = True
    return results


if __name__ == "__main__":
    from recover_hosted_runner import GitHubClient

    client = GitHubClient(os.environ["GITHUB_REPOSITORY"], os.environ["GH_TOKEN"])
    print(json.dumps(recover(client, now=datetime.now(timezone.utc),
                             dry_run=os.environ.get("RECOVERY_DRY_RUN", "false").lower() == "true")))
