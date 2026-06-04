from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo


KST = ZoneInfo("Asia/Seoul")
UTC = timezone.utc


@dataclass(frozen=True)
class ScheduleTarget:
    profile: str
    window_start_time: time
    target_jobs: tuple[str, ...]


class GitHubActionsGateClient:
    def __init__(self, *, repository: str, token: str, branch: str = "main") -> None:
        self.repository = repository
        self.token = token
        self.branch = branch

    def _request(self, method: str, path: str) -> Any:
        url = f"https://api.github.com/repos/{self.repository}{path}"
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            method=method,
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    def list_runs(self, workflow_file: str, *, created_since_utc: datetime) -> list[dict[str, Any]]:
        query = urllib.parse.urlencode(
            {
                "branch": self.branch,
                "created": f">={created_since_utc.isoformat().replace('+00:00', 'Z')}",
                "per_page": "100",
            }
        )
        payload = self._request("GET", f"/actions/workflows/{workflow_file}/runs?{query}")
        return list(payload.get("workflow_runs", []))

    def list_jobs(self, run_id: int) -> list[dict[str, Any]]:
        payload = self._request("GET", f"/actions/runs/{run_id}/jobs?per_page=100")
        return list(payload.get("jobs", []))


def _parse_time(raw: str) -> time:
    hour, minute = raw.split(":", 1)
    return time(int(hour), int(minute))


def load_schedule_targets(raw_json: str) -> dict[str, ScheduleTarget]:
    payload = json.loads(raw_json)
    targets: dict[str, ScheduleTarget] = {}
    for schedule, raw_target in payload.items():
        targets[schedule] = ScheduleTarget(
            profile=str(raw_target.get("profile", "")),
            window_start_time=_parse_time(str(raw_target["window_start"])),
            target_jobs=tuple(str(item) for item in raw_target.get("target_jobs", ())),
        )
    return targets


def _window_start(now_kst: datetime, window_start_time: time) -> datetime:
    window_start_kst = now_kst.replace(
        hour=window_start_time.hour,
        minute=window_start_time.minute,
        second=0,
        microsecond=0,
    )
    if now_kst.time() < window_start_time:
        window_start_kst -= timedelta(days=1)
    return window_start_kst


def job_covers_target(job: dict[str, Any], target_job_names: set[str]) -> bool:
    if job.get("name") not in target_job_names:
        return False
    status = str(job.get("status") or "").lower()
    conclusion = str(job.get("conclusion") or "").lower()
    if status != "completed":
        return True
    return conclusion == "success"


def _run_covers_target(
    *,
    client: Any,
    run: dict[str, Any],
    current_run_id: int,
    target_job_names: set[str],
) -> tuple[bool, str]:
    run_id = int(run.get("id", 0))
    if run_id == current_run_id:
        return False, ""

    status = str(run.get("status") or "").lower()
    conclusion = str(run.get("conclusion") or "").lower()
    if status == "completed" and conclusion != "success":
        return False, ""

    jobs = client.list_jobs(run_id)
    for job in jobs:
        if job_covers_target(job, target_job_names):
            job_name = job.get("name")
            job_status = job.get("status")
            job_conclusion = job.get("conclusion")
            event = run.get("event", "unknown")
            return True, f"Prior {event} run {run_id} covers {job_name}: {job_status}/{job_conclusion}."

    return False, ""


def decide_schedule_gate(
    *,
    event_name: str,
    schedule: str,
    requested_profile: str,
    manual_default_profile: str,
    workflow_file: str,
    current_run_id: int,
    client: Any,
    targets: dict[str, ScheduleTarget],
    now_kst: datetime,
) -> tuple[str, bool, str]:
    if event_name != "schedule":
        profile = requested_profile.strip() or manual_default_profile
        return profile, True, f"Manual dispatch runs profile={profile}."

    target = targets.get(schedule)
    if target is None:
        return "", False, f"Unrecognized scheduled cron: {schedule}"

    window_start_kst = _window_start(now_kst, target.window_start_time)
    window_start_utc = window_start_kst.astimezone(UTC)
    target_job_names = set(target.target_jobs)

    try:
        runs = client.list_runs(workflow_file, created_since_utc=window_start_utc)
        for run in runs:
            covered, reason = _run_covers_target(
                client=client,
                run=run,
                current_run_id=current_run_id,
                target_job_names=target_job_names,
            )
            if covered:
                return (
                    target.profile,
                    False,
                    f"Skipping duplicate {target.profile.upper() or workflow_file} scheduled run; {reason}",
                )
    except Exception as exc:
        print(f"::warning::Could not inspect prior workflow runs/jobs; running to preserve coverage: {exc}")
        return target.profile, True, "Schedule gate API lookup failed; running to preserve daily coverage."

    return (
        target.profile,
        True,
        f"No successful or active {target.profile.upper() or workflow_file} target job since {window_start_kst.isoformat()}; running now.",
    )


def write_outputs(*, profile: str, should_run: bool, reason: str) -> None:
    safe_reason = reason.replace("\n", " ")
    output_path = os.environ["GITHUB_OUTPUT"]
    with open(output_path, "a", encoding="utf-8") as handle:
        if profile:
            handle.write(f"profile={profile}\n")
        handle.write(f"should_run={'true' if should_run else 'false'}\n")
        handle.write(f"reason={safe_reason}\n")
    print(reason)


def main() -> int:
    client = GitHubActionsGateClient(
        repository=os.environ["GH_REPOSITORY"],
        token=os.environ["GH_TOKEN"],
        branch=os.environ.get("GATE_BRANCH", "main"),
    )
    profile, should_run, reason = decide_schedule_gate(
        event_name=os.environ.get("GH_EVENT_NAME", ""),
        schedule=os.environ.get("EVENT_SCHEDULE", "").strip(),
        requested_profile=os.environ.get("REQUESTED_PROFILE", ""),
        manual_default_profile=os.environ.get("MANUAL_DEFAULT_PROFILE", ""),
        workflow_file=os.environ["WORKFLOW_FILE"],
        current_run_id=int(os.environ["GH_RUN_ID"]),
        client=client,
        targets=load_schedule_targets(os.environ["SCHEDULE_GATE_TARGETS_JSON"]),
        now_kst=datetime.now(KST),
    )
    write_outputs(profile=profile, should_run=should_run, reason=reason)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
