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

US_SCHEDULES = {"0 14-20 * * 1-5", "50 19,20 * * 1-5"}
KR_SCHEDULES = {"35 0-5 * * 1-5", "20 6 * * 1-5", "50 0-5 * * 1-5", "25 6 * * 1-5"}
DAILY_TARGET_JOBS = {"us": ("analyze_us", "build_pages"), "kr": ("analyze_kr", "build_pages")}


@dataclass(frozen=True)
class DailyDependency:
    profile: str
    workflow_file: str
    target_job_names: tuple[str, ...]
    window_start_kst: datetime


class GitHubActionsClient:
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


def requested_profiles(*, event_name: str, schedule: str, requested_profile: str) -> tuple[str, ...]:
    if event_name == "schedule":
        if schedule in US_SCHEDULES:
            return ("us",)
        if schedule in KR_SCHEDULES:
            return ("kr",)
        return ()

    profile = (requested_profile or "all").strip().lower()
    if profile == "all":
        return ("us", "kr")
    if profile in {"us", "kr"}:
        return (profile,)
    return ()


def daily_window_start_kst(profile: str, now_kst: datetime) -> datetime:
    if profile == "kr":
        start = time(6, 0)
    elif profile == "us":
        start = time(16, 0)
    else:
        raise ValueError(f"Unsupported profile: {profile}")

    window_start = now_kst.replace(hour=start.hour, minute=start.minute, second=0, microsecond=0)
    if now_kst.time() < start:
        window_start -= timedelta(days=1)
    return window_start


def daily_dependency(profile: str, now_kst: datetime) -> DailyDependency:
    return DailyDependency(
        profile=profile,
        workflow_file="daily-codex-analysis.yml",
        target_job_names=DAILY_TARGET_JOBS[profile],
        window_start_kst=daily_window_start_kst(profile, now_kst),
    )


def _run_has_successful_target_jobs(*, client: Any, run_id: int, target_job_names: tuple[str, ...]) -> bool:
    required = set(target_job_names)
    successful: set[str] = set()
    for job in client.list_jobs(run_id):
        name = str(job.get("name") or "")
        if name not in required:
            continue
        status = str(job.get("status") or "").lower()
        conclusion = str(job.get("conclusion") or "").lower()
        if status == "completed" and conclusion == "success":
            successful.add(name)
    return required <= successful


def _run_created_at(run: dict[str, Any]) -> datetime:
    raw = str(run.get("created_at") or run.get("createdAt") or "")
    if not raw:
        return datetime.min.replace(tzinfo=UTC)
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return datetime.min.replace(tzinfo=UTC)


def daily_dependency_satisfied(*, client: Any, dependency: DailyDependency) -> tuple[bool, str]:
    runs = client.list_runs(
        dependency.workflow_file,
        created_since_utc=dependency.window_start_kst.astimezone(UTC),
    )
    if not runs:
        return False, f"No Daily Codex {dependency.profile.upper()} run since {dependency.window_start_kst.isoformat()}."

    active: list[int] = []
    for run in sorted(runs, key=_run_created_at, reverse=True):
        run_id = int(run.get("id", 0))
        status = str(run.get("status") or "").lower()
        conclusion = str(run.get("conclusion") or "").lower()

        if status != "completed":
            active.append(run_id)
            continue
        if conclusion != "success":
            continue
        if _run_has_successful_target_jobs(
            client=client,
            run_id=run_id,
            target_job_names=dependency.target_job_names,
        ):
            if active:
                return (
                    False,
                    f"Newer Daily Codex {dependency.profile.upper()} run(s) still active: {', '.join(str(item) for item in active)}.",
                )
            return (
                True,
                f"Daily Codex {dependency.profile.upper()} run {run_id} completed successfully after {dependency.window_start_kst.isoformat()}.",
            )

    if active:
        return False, f"Daily Codex {dependency.profile.upper()} run(s) still active: {', '.join(str(item) for item in active)}."
    return False, f"No completed successful Daily Codex {dependency.profile.upper()} target job since {dependency.window_start_kst.isoformat()}."


def decide_intraday_gate(
    *,
    event_name: str,
    schedule: str,
    requested_profile: str,
    client: Any,
    now_kst: datetime,
) -> tuple[dict[str, bool], list[str]]:
    decisions = {"us": False, "kr": False}
    messages: list[str] = []

    for profile in requested_profiles(event_name=event_name, schedule=schedule, requested_profile=requested_profile):
        dependency = daily_dependency(profile, now_kst)
        try:
            satisfied, reason = daily_dependency_satisfied(client=client, dependency=dependency)
        except Exception as exc:
            satisfied = False
            reason = f"Could not verify Daily Codex {profile.upper()} dependency; holding overlay to preserve ordering: {exc}"
        decisions[profile] = satisfied
        messages.append(f"intraday-overlay-{profile}: {'allowed' if satisfied else 'held'}; {reason}")

    if not messages:
        messages.append("No intraday overlay profile selected for this event.")

    return decisions, messages


def write_outputs(decisions: dict[str, bool], messages: list[str]) -> None:
    output_path = os.environ["GITHUB_OUTPUT"]
    reason = " ".join(message.replace("\n", " ") for message in messages)
    with open(output_path, "a", encoding="utf-8") as handle:
        handle.write(f"run_us={'true' if decisions.get('us') else 'false'}\n")
        handle.write(f"run_kr={'true' if decisions.get('kr') else 'false'}\n")
        handle.write(f"reason={reason}\n")
    for message in messages:
        print(message)


def _now_kst_from_env() -> datetime:
    raw = os.environ.get("GATE_NOW_KST", "").strip()
    if raw:
        parsed = datetime.fromisoformat(raw)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=KST)
        return parsed.astimezone(KST)
    return datetime.now(KST)


def main() -> int:
    client = GitHubActionsClient(
        repository=os.environ["GH_REPOSITORY"],
        token=os.environ["GH_TOKEN"],
        branch=os.environ.get("GATE_BRANCH", "main"),
    )
    decisions, messages = decide_intraday_gate(
        event_name=os.environ.get("GH_EVENT_NAME", ""),
        schedule=os.environ.get("EVENT_SCHEDULE", "").strip(),
        requested_profile=os.environ.get("REQUESTED_PROFILE", ""),
        client=client,
        now_kst=_now_kst_from_env(),
    )
    write_outputs(decisions, messages)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
