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
class WatchdogDependency:
    name: str
    workflow_file: str
    job_names: tuple[str, ...]
    window_start_kst: datetime


@dataclass(frozen=True)
class WatchdogBlocker:
    name: str
    workflow_file: str
    job_names: tuple[str, ...]
    window_start_kst: datetime


@dataclass(frozen=True)
class WatchdogTarget:
    name: str
    workflow_file: str
    job_names: tuple[str, ...]
    window_start_kst: datetime
    inputs: dict[str, str]
    dependencies: tuple[WatchdogDependency, ...] = ()
    blockers: tuple[WatchdogBlocker, ...] = ()


class GitHubActionsClient:
    def __init__(self, *, repository: str, token: str, ref: str = "main") -> None:
        self.repository = repository
        self.token = token
        self.ref = ref

    def _request(self, method: str, path: str, *, payload: dict[str, Any] | None = None) -> Any:
        url = f"https://api.github.com/repos/{self.repository}{path}"
        data = None
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
            if not body:
                return None
            return json.loads(body.decode("utf-8"))

    def list_runs(self, workflow_file: str, *, created_since_utc: datetime) -> list[dict[str, Any]]:
        query = urllib.parse.urlencode(
            {
                "branch": self.ref,
                "created": f">={created_since_utc.isoformat().replace('+00:00', 'Z')}",
                "per_page": "50",
            }
        )
        payload = self._request("GET", f"/actions/workflows/{workflow_file}/runs?{query}")
        return list(payload.get("workflow_runs", []))

    def list_jobs(self, run_id: int) -> list[dict[str, Any]]:
        payload = self._request("GET", f"/actions/runs/{run_id}/jobs?per_page=100")
        return list(payload.get("jobs", []))

    def dispatch(self, workflow_file: str, inputs: dict[str, str]) -> None:
        self._request(
            "POST",
            f"/actions/workflows/{workflow_file}/dispatches",
            payload={"ref": self.ref, "inputs": inputs},
        )


def target_is_covered(
    *,
    client: GitHubActionsClient,
    target: WatchdogTarget,
) -> tuple[bool, str]:
    since_utc = target.window_start_kst.astimezone(UTC)
    target_job_names = set(target.job_names)
    runs = client.list_runs(target.workflow_file, created_since_utc=since_utc)
    if not runs:
        return False, f"No runs since {target.window_start_kst.isoformat()}."

    for run in runs:
        run_id = int(run.get("id", 0))
        status = str(run.get("status") or "").lower()
        conclusion = str(run.get("conclusion") or "").lower()
        if status == "completed" and conclusion != "success":
            continue

        jobs = client.list_jobs(run_id)
        active_matches: list[str] = []
        successful_matches: set[str] = set()
        for job in jobs:
            job_name = str(job.get("name") or "")
            if job_name not in target_job_names:
                continue
            job_status = str(job.get("status") or "").lower()
            job_conclusion = str(job.get("conclusion") or "").lower()
            if job_status != "completed":
                active_matches.append(f"{job_name}: {job_status}/{job_conclusion}")
            elif job_conclusion == "success":
                successful_matches.add(job_name)
        if active_matches:
            return True, f"Run {run_id} has active target job(s): {', '.join(active_matches)}."
        if status != "completed" and successful_matches:
            covered = ", ".join(sorted(successful_matches))
            missing = ", ".join(sorted(target_job_names - successful_matches))
            return True, f"Run {run_id} is still active after target job(s) succeeded: {covered}; waiting for {missing}."
        if target_job_names <= successful_matches:
            covered = ", ".join(sorted(successful_matches))
            return True, f"Run {run_id} covers target job set: {covered}."

    return False, f"No successful target jobs since {target.window_start_kst.isoformat()}."


def dependency_is_satisfied(
    *,
    client: GitHubActionsClient,
    dependency: WatchdogDependency,
) -> tuple[bool, str]:
    runs = client.list_runs(
        dependency.workflow_file,
        created_since_utc=dependency.window_start_kst.astimezone(UTC),
    )
    if not runs:
        return False, f"No dependency runs since {dependency.window_start_kst.isoformat()}."

    active: list[int] = []
    required_jobs = set(dependency.job_names)
    for run in runs:
        run_id = int(run.get("id", 0))
        status = str(run.get("status") or "").lower()
        conclusion = str(run.get("conclusion") or "").lower()
        if status != "completed":
            active.append(run_id)
            continue
        if conclusion != "success":
            continue

        successful_jobs = {
            str(job.get("name"))
            for job in client.list_jobs(run_id)
            if str(job.get("status") or "").lower() == "completed"
            and str(job.get("conclusion") or "").lower() == "success"
        }
        if required_jobs <= successful_jobs:
            return True, f"Dependency {dependency.name} satisfied by run {run_id}."

    if active:
        return False, f"Dependency {dependency.name} still active in run(s): {', '.join(str(item) for item in active)}."
    return False, f"Dependency {dependency.name} has no completed successful target jobs since {dependency.window_start_kst.isoformat()}."


def dependencies_are_satisfied(
    *,
    client: GitHubActionsClient,
    target: WatchdogTarget,
) -> tuple[bool, str]:
    for dependency in target.dependencies:
        satisfied, reason = dependency_is_satisfied(client=client, dependency=dependency)
        if not satisfied:
            return False, reason
    return True, "All dependencies satisfied."


def blocker_is_active(
    *,
    client: GitHubActionsClient,
    blocker: WatchdogBlocker,
) -> tuple[bool, str]:
    runs = client.list_runs(
        blocker.workflow_file,
        created_since_utc=blocker.window_start_kst.astimezone(UTC),
    )
    target_job_names = set(blocker.job_names)
    for run in runs:
        run_id = int(run.get("id", 0))
        status = str(run.get("status") or "").lower()
        if status == "completed":
            continue
        for job in client.list_jobs(run_id):
            job_name = str(job.get("name") or "")
            job_status = str(job.get("status") or "").lower()
            if job_name in target_job_names and job_status != "completed":
                return True, f"Active blocker {blocker.name} run {run_id} has {job_name}: {job_status}."
    return False, "No active blocker runs."


def blockers_are_clear(
    *,
    client: GitHubActionsClient,
    target: WatchdogTarget,
) -> tuple[bool, str]:
    for blocker in target.blockers:
        active, reason = blocker_is_active(client=client, blocker=blocker)
        if active:
            return False, reason
    return True, "No active blockers."


def _time_between(value: time, start: time, end: time) -> bool:
    return start <= value < end


def _youtube_window_start(now_kst: datetime) -> datetime:
    window = now_kst.replace(hour=5, minute=0, second=0, microsecond=0)
    if now_kst.time() < time(5, 0):
        window -= timedelta(days=1)
    return window


def _youtube_watchdog_due(now_kst: datetime, youtube_window: datetime) -> bool:
    # Recovery starts after the direct post-US-overlay YouTube probes and stays
    # open through the morning so a delayed US overlay can still finish first.
    return youtube_window + timedelta(hours=1, minutes=50) <= now_kst < youtube_window + timedelta(hours=10)


def _us_intraday_overlay_due(now_kst: datetime) -> bool:
    utc_now = now_kst.astimezone(UTC)
    return utc_now.weekday() < 5 and _time_between(utc_now.time(), time(14, 20), time(21, 20))


def _daily_codex_dependency(profile: str, now_kst: datetime) -> WatchdogDependency:
    if profile == "kr":
        window_start = datetime.combine(now_kst.date(), time(6, 0), tzinfo=KST)
        job_names = ("analyze_kr", "build_pages")
    elif profile == "us":
        window_start = datetime.combine(now_kst.date(), time(16, 0), tzinfo=KST)
        if now_kst.time() < time(16, 0):
            window_start -= timedelta(days=1)
        job_names = ("analyze_us", "build_pages")
    else:
        raise ValueError(f"Unsupported Daily Codex dependency profile: {profile}")

    return WatchdogDependency(
        name=f"daily-codex-{profile}",
        workflow_file="daily-codex-analysis.yml",
        job_names=job_names,
        window_start_kst=window_start,
    )


def _daily_codex_active_blocker(profile: str, now_kst: datetime) -> WatchdogBlocker:
    if profile == "kr":
        window_start = datetime.combine(now_kst.date(), time(6, 0), tzinfo=KST)
        job_names = ("analyze_kr", "build_pages")
    elif profile == "us":
        window_start = datetime.combine(now_kst.date(), time(16, 0), tzinfo=KST)
        if now_kst.time() < time(16, 0):
            window_start -= timedelta(days=1)
        job_names = ("analyze_us", "build_pages")
    else:
        raise ValueError(f"Unsupported Daily Codex blocker profile: {profile}")

    return WatchdogBlocker(
        name=f"daily-codex-{profile}-pages",
        workflow_file="daily-codex-analysis.yml",
        job_names=job_names,
        window_start_kst=window_start,
    )


def _intraday_overlay_active_blocker(profile: str, now_kst: datetime) -> WatchdogBlocker:
    if profile == "kr":
        window_start = datetime.combine(now_kst.date(), time(9, 0), tzinfo=KST)
        job_names = ("overlay_refresh_kr", "publish_overlay_site", "deploy_overlay")
    elif profile == "us":
        window_start = datetime.combine(now_kst.date(), time(23, 0), tzinfo=KST)
        if now_kst.time() < time(23, 0):
            window_start -= timedelta(days=1)
        job_names = ("overlay_refresh_us", "publish_overlay_site", "deploy_overlay")
    else:
        raise ValueError(f"Unsupported Intraday Overlay blocker profile: {profile}")

    return WatchdogBlocker(
        name=f"intraday-overlay-{profile}-publish",
        workflow_file="intraday-overlay-refresh.yml",
        job_names=job_names,
        window_start_kst=window_start,
    )


def _youtube_active_blocker(now_kst: datetime) -> WatchdogBlocker:
    return WatchdogBlocker(
        name="daily-youtube-publish",
        workflow_file="daily-youtube-reports.yml",
        job_names=("build_youtube_pages", "deploy"),
        window_start_kst=_youtube_window_start(now_kst),
    )


def due_targets(now_kst: datetime) -> list[WatchdogTarget]:
    targets: list[WatchdogTarget] = []
    kst_date = now_kst.date()
    kst_time = now_kst.time()
    kst_weekday = now_kst.weekday()

    youtube_window = _youtube_window_start(now_kst)
    us_intraday_overlay_due = _us_intraday_overlay_due(now_kst)
    if _youtube_watchdog_due(now_kst, youtube_window) and not us_intraday_overlay_due:
        targets.append(
            WatchdogTarget(
                name="youtube-daily",
                workflow_file="daily-youtube-reports.yml",
                job_names=("build_youtube_pages",),
                window_start_kst=youtube_window,
                inputs={"lookback_hours": "24", "publish": "true"},
                blockers=(
                    _daily_codex_active_blocker("us", now_kst),
                    _intraday_overlay_active_blocker("us", now_kst),
                ),
            )
        )

    if kst_weekday < 5:
        codex_us_window = datetime.combine(kst_date, time(16, 0), tzinfo=KST)
        if _time_between(kst_time, time(17, 45), time(23, 15)):
            targets.append(
                WatchdogTarget(
                    name="daily-codex-us",
                    workflow_file="daily-codex-analysis.yml",
                    job_names=("analyze_us", "build_pages"),
                    window_start_kst=codex_us_window,
                    inputs={"profile": "us"},
                    blockers=(_intraday_overlay_active_blocker("kr", now_kst),),
                )
            )

        codex_kr_window = datetime.combine(kst_date, time(6, 0), tzinfo=KST)
        if _time_between(kst_time, time(7, 45), time(15, 45)):
            targets.append(
                WatchdogTarget(
                    name="daily-codex-kr",
                    workflow_file="daily-codex-analysis.yml",
                    job_names=("analyze_kr", "build_pages"),
                    window_start_kst=codex_kr_window,
                    inputs={"profile": "kr"},
                    blockers=(
                        _intraday_overlay_active_blocker("us", now_kst),
                        _youtube_active_blocker(now_kst),
                    ),
                )
            )

        if _time_between(kst_time, time(9, 50), time(15, 45)):
            targets.append(
                WatchdogTarget(
                    name="intraday-overlay-kr",
                    workflow_file="intraday-overlay-refresh.yml",
                    job_names=("overlay_refresh_kr",),
                    window_start_kst=now_kst - timedelta(minutes=75),
                    inputs={"profile": "kr", "run_mode": "overlay_only"},
                    dependencies=(_daily_codex_dependency("kr", now_kst),),
                )
            )

    if us_intraday_overlay_due:
        targets.append(
            WatchdogTarget(
                name="intraday-overlay-us",
                workflow_file="intraday-overlay-refresh.yml",
                job_names=("overlay_refresh_us",),
                window_start_kst=now_kst - timedelta(minutes=75),
                inputs={"profile": "us", "run_mode": "overlay_only"},
                dependencies=(_daily_codex_dependency("us", now_kst),),
            )
        )

    return targets


def run_watchdog(*, client: GitHubActionsClient, now_kst: datetime, dry_run: bool = False) -> list[str]:
    messages: list[str] = []
    for target in due_targets(now_kst):
        blockers_clear, blocker_reason = blockers_are_clear(client=client, target=target)
        if not blockers_clear:
            messages.append(f"{target.name}: waiting; {blocker_reason}")
            continue

        dependencies_satisfied, dependency_reason = dependencies_are_satisfied(client=client, target=target)
        if not dependencies_satisfied:
            messages.append(f"{target.name}: waiting; {dependency_reason}")
            continue

        covered, reason = target_is_covered(client=client, target=target)
        if covered:
            messages.append(f"{target.name}: covered; {reason}")
            continue
        if dry_run:
            messages.append(f"{target.name}: would dispatch; {reason}")
            continue
        client.dispatch(target.workflow_file, target.inputs)
        messages.append(f"{target.name}: dispatched {target.workflow_file}; {reason}")
    if not messages:
        messages.append(f"No watchdog targets due at {now_kst.isoformat()}.")
    return messages


def _now_kst_from_env() -> datetime:
    raw = os.environ.get("WATCHDOG_NOW_KST", "").strip()
    if raw:
        parsed = datetime.fromisoformat(raw)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=KST)
        return parsed.astimezone(KST)
    return datetime.now(KST)


def main() -> int:
    repository = os.environ["GH_REPOSITORY"]
    token = os.environ["GH_TOKEN"]
    ref = os.environ.get("GH_REF", "main")
    dry_run = os.environ.get("WATCHDOG_DRY_RUN", "").strip().lower() in {"1", "true", "yes"}
    client = GitHubActionsClient(repository=repository, token=token, ref=ref)
    for message in run_watchdog(client=client, now_kst=_now_kst_from_env(), dry_run=dry_run):
        print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
