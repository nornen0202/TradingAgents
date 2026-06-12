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
OVERLAY_TARGET_JOBS = {
    "us": ("overlay_refresh_us", "publish_overlay_site", "deploy_overlay"),
    "kr": ("overlay_refresh_kr", "publish_overlay_site", "deploy_overlay"),
}
DEFAULT_MAX_SCHEDULE_DELAY_MINUTES = 90


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


def _cron_field_values(raw: str, *, minimum: int, maximum: int) -> tuple[int, ...]:
    raw = raw.strip()
    if raw == "*":
        return tuple(range(minimum, maximum + 1))
    values: set[int] = set()
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            start = int(start_text)
            end = int(end_text)
            values.update(range(max(minimum, start), min(maximum, end) + 1))
        else:
            value = int(part)
            if minimum <= value <= maximum:
                values.add(value)
    return tuple(sorted(values))


def _last_scheduled_fire_utc(schedule: str, now_utc: datetime) -> datetime | None:
    fields = schedule.split()
    if len(fields) < 2:
        return None
    minutes = _cron_field_values(fields[0], minimum=0, maximum=59)
    hours = _cron_field_values(fields[1], minimum=0, maximum=23)
    if not minutes or not hours:
        return None
    cron_weekdays: set[int] | None = None
    if len(fields) >= 5 and fields[4].strip() != "*":
        cron_weekdays = {value % 7 for value in _cron_field_values(fields[4], minimum=0, maximum=7)}
        if not cron_weekdays:
            return None

    candidates: list[datetime] = []
    for day_offset in range(0, -8, -1):
        base_date = (now_utc + timedelta(days=day_offset)).date()
        candidate_weekday = (base_date.weekday() + 1) % 7
        if cron_weekdays is not None and candidate_weekday not in cron_weekdays:
            continue
        for hour in hours:
            for minute in minutes:
                candidate = datetime.combine(base_date, time(hour, minute), tzinfo=UTC)
                if candidate <= now_utc:
                    candidates.append(candidate)
    return max(candidates) if candidates else None


def _schedule_fresh_enough(
    *,
    schedule: str,
    now_kst: datetime,
    max_delay_minutes: int,
) -> tuple[bool, str]:
    expected_utc = _last_scheduled_fire_utc(schedule, now_kst.astimezone(UTC))
    if expected_utc is None:
        return True, "No concrete scheduled fire time could be derived."
    delay_seconds = (now_kst.astimezone(UTC) - expected_utc).total_seconds()
    delay_minutes = int(delay_seconds // 60)
    if delay_minutes > max_delay_minutes:
        return (
            False,
            "Scheduled event is stale: "
            f"expected {expected_utc.astimezone(KST).isoformat()} KST, "
            f"delay {delay_minutes}m exceeds {max_delay_minutes}m.",
        )
    return True, f"Scheduled event delay {delay_minutes}m is within {max_delay_minutes}m."


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


def overlay_window_start_kst(profile: str, now_kst: datetime) -> datetime:
    if profile == "kr":
        start = time(9, 0)
    elif profile == "us":
        start = time(23, 0)
    else:
        raise ValueError(f"Unsupported profile: {profile}")
    window_start = now_kst.replace(hour=start.hour, minute=start.minute, second=0, microsecond=0)
    if now_kst.time() < start:
        window_start -= timedelta(days=1)
    return window_start


def active_overlay_for_profile(
    *,
    client: Any,
    profile: str,
    now_kst: datetime,
    current_run_id: int,
) -> tuple[bool, str]:
    target_jobs = set(OVERLAY_TARGET_JOBS[profile])
    runs = client.list_runs(
        "intraday-overlay-refresh.yml",
        created_since_utc=overlay_window_start_kst(profile, now_kst).astimezone(UTC),
    )
    for run in runs:
        run_id = int(run.get("id", 0))
        if run_id == current_run_id:
            continue
        status = str(run.get("status") or "").lower()
        if status == "completed":
            continue
        for job in client.list_jobs(run_id):
            job_name = str(job.get("name") or "")
            job_status = str(job.get("status") or "").lower()
            if job_name in target_jobs and job_status != "completed":
                return True, f"Active {profile.upper()} overlay run {run_id} has {job_name}: {job_status}."
    return False, "No active same-profile overlay run."


def decide_intraday_gate(
    *,
    event_name: str,
    schedule: str,
    requested_profile: str,
    client: Any,
    now_kst: datetime,
    current_run_id: int = 0,
    max_schedule_delay_minutes: int = DEFAULT_MAX_SCHEDULE_DELAY_MINUTES,
) -> tuple[dict[str, bool], list[str]]:
    decisions = {"us": False, "kr": False}
    messages: list[str] = []

    for profile in requested_profiles(event_name=event_name, schedule=schedule, requested_profile=requested_profile):
        if event_name == "schedule":
            fresh, freshness_reason = _schedule_fresh_enough(
                schedule=schedule,
                now_kst=now_kst,
                max_delay_minutes=max_schedule_delay_minutes,
            )
            if not fresh:
                messages.append(f"intraday-overlay-{profile}: held; {freshness_reason}")
                continue
        try:
            active, active_reason = active_overlay_for_profile(
                client=client,
                profile=profile,
                now_kst=now_kst,
                current_run_id=current_run_id,
            )
        except Exception as exc:
            active = False
            active_reason = f"Could not inspect active same-profile overlays: {exc}"
        if active:
            messages.append(f"intraday-overlay-{profile}: held; {active_reason}")
            continue

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
        current_run_id=int(os.environ.get("GH_RUN_ID") or 0),
        max_schedule_delay_minutes=int(
            os.environ.get("INTRADAY_OVERLAY_MAX_SCHEDULE_DELAY_MINUTES")
            or DEFAULT_MAX_SCHEDULE_DELAY_MINUTES
        ),
    )
    write_outputs(decisions, messages)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
