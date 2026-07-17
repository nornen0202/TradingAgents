from __future__ import annotations

import hashlib
import io
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import zipfile
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
    max_failed_attempts: int = 2
    failure_window_start_kst: datetime | None = None
    work_job_names: tuple[str, ...] = ()


class GitHubActionsClient:
    def __init__(self, *, repository: str, token: str, ref: str = "main") -> None:
        self.repository = repository
        self.token = token
        self.ref = ref
        self._diagnostic_cache: dict[int, str] = {}

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

    def failure_diagnostic_signature(self, run_id: int) -> str:
        run_id = int(run_id)
        if run_id in self._diagnostic_cache:
            return self._diagnostic_cache[run_id]
        try:
            request = urllib.request.Request(
                f"https://api.github.com/repos/{self.repository}/actions/runs/{run_id}/logs",
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {self.token}",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read(32_000_001)
            signature = "" if len(raw) > 32_000_000 else _log_archive_diagnostic_signature(raw)
        except (OSError, urllib.error.URLError, zipfile.BadZipFile):
            signature = ""
        self._diagnostic_cache[run_id] = signature
        return signature


def target_is_covered(
    *,
    client: GitHubActionsClient,
    target: WatchdogTarget,
) -> tuple[bool, str]:
    since_utc = target.window_start_kst.astimezone(UTC)
    failure_since_utc = (
        target.failure_window_start_kst or target.window_start_kst
    ).astimezone(UTC)
    query_since_utc = min(since_utc, failure_since_utc)
    target_job_names = set(target.job_names)
    runs = client.list_runs(target.workflow_file, created_since_utc=query_since_utc)
    if not runs:
        return False, f"No runs since {target.window_start_kst.isoformat()}."
    runs = sorted(
        runs,
        key=lambda run: _workflow_run_created_at(run) or datetime.min.replace(tzinfo=UTC),
        reverse=True,
    )

    failure_attempts: dict[str, list[int]] = {}
    latest_failure_fingerprint: str | None = None
    for run in runs:
        run_id = int(run.get("id", 0))
        status = str(run.get("status") or "").lower()
        created_at = _workflow_run_created_at(run)
        in_target_window = created_at is None or created_at >= since_utc
        in_failure_window = created_at is None or created_at >= failure_since_utc
        jobs = client.list_jobs(run_id)
        if not _run_applies_to_target(run=run, jobs=jobs, target=target):
            continue
        active_matches: list[str] = []
        successful_matches: set[str] = set()
        failed_matches: list[str] = []
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
            elif job_conclusion not in {"", "skipped", "neutral"}:
                failed_steps = [
                    step
                    for step in (job.get("steps") or [])
                    if str(step.get("conclusion") or "").lower()
                    not in {"", "success", "skipped", "neutral"}
                ]
                if failed_steps:
                    for step in failed_steps:
                        step_name = str(step.get("name") or "unknown")
                        step_conclusion = str(step.get("conclusion") or "").lower()
                        failed_matches.append(
                            f"{job_name}/{step_name}:{step_conclusion}"
                        )
                else:
                    failed_matches.append(f"{job_name}:{job_conclusion}")
        if in_target_window and active_matches:
            return True, f"Run {run_id} has active target job(s): {', '.join(active_matches)}."
        if in_target_window and status != "completed":
            return True, f"Run {run_id} is active before all target jobs are available."
        if in_target_window and target_job_names <= successful_matches:
            covered = ", ".join(sorted(successful_matches))
            return True, f"Run {run_id} covers target job set: {covered}."
        no_work = _completed_success_no_work(run=run, jobs=jobs, target=target)
        if in_target_window and no_work:
            return True, f"Run {run_id} completed successfully with an explicit no-work target result."
        if in_failure_window and (target_job_names <= successful_matches or no_work):
            # A completed target job clears older failure history.  Only the
            # consecutive incident after the latest recovery consumes budget.
            break

        if (
            status == "completed"
            and in_failure_window
            and _run_recovery_source(run) != "manual"
        ):
            if not failed_matches:
                failed_matches = _workflow_failure_fallback(run=run, jobs=jobs)
            if not failed_matches:
                failed_matches = _missing_required_job_failures(
                    required_job_names=target_job_names,
                    jobs=jobs,
                )
            if not failed_matches:
                continue
            head_sha = str(run.get("head_sha") or "unknown").strip().lower()
            fingerprint_context = _run_fingerprint_context(run=run, target=target)
            diagnostic_signature = _client_failure_diagnostic_signature(client, run_id)
            diagnostic_context = (
                f"diagnostic={diagnostic_signature}"
                if diagnostic_signature
                # Recovery retry accounting must remain bounded even when the
                # GitHub log archive is temporarily unavailable.  Telegram's
                # user-facing alert fingerprint intentionally fails open with
                # a run nonce; this watchdog instead groups the conservative
                # stage/SHA/profile fallback so automation cannot loop forever.
                else "diagnostic=unavailable"
            )
            fingerprint = (
                f"{head_sha}|{fingerprint_context}|{diagnostic_context}|"
                f"{'|'.join(sorted(set(failed_matches)))}"
            )
            if (
                latest_failure_fingerprint is not None
                and fingerprint != latest_failure_fingerprint
            ):
                break
            failure_attempts.setdefault(fingerprint, []).append(run_id)
            if latest_failure_fingerprint is None:
                latest_failure_fingerprint = fingerprint

    matching_failures = failure_attempts.get(latest_failure_fingerprint or "", [])
    if target.max_failed_attempts > 0 and len(matching_failures) >= target.max_failed_attempts:
        attempts = ", ".join(
            str(run_id) for run_id in matching_failures[: target.max_failed_attempts]
        )
        return True, (
            f"Retry budget exhausted after {target.max_failed_attempts} identical target-job "
            f"failure(s) in the cooldown window: {attempts}."
        )

    return False, f"No successful target jobs since {target.window_start_kst.isoformat()}."


def _run_applies_to_target(
    *,
    run: dict[str, Any],
    jobs: list[dict[str, Any]],
    target: WatchdogTarget,
) -> bool:
    requested_profile = str(target.inputs.get("profile") or "").strip().lower()
    marked_profile = _run_marker(run, "profile", {"kr", "us", "all"})
    if requested_profile in {"kr", "us"} and marked_profile:
        if marked_profile not in {requested_profile, "all"}:
            return False

    marked_run_mode = _run_marker(
        run,
        "run_mode",
        {"overlay_only", "selective_rerun_only", "full", "smoke", "site_only"},
    )
    requested_run_mode = str(target.inputs.get("run_mode") or "").strip().lower()
    if marked_run_mode and requested_run_mode and marked_run_mode != requested_run_mode:
        return False

    request_scope = _run_marker(
        run,
        "request_scope",
        {"default_universe", "custom_tickers", "custom_sources"},
    )
    if request_scope in {"custom_tickers", "custom_sources"}:
        return False

    if requested_profile not in {"kr", "us"} or marked_profile:
        return True

    # Backward-compatible fallback for runs created before profile markers.
    # A non-skipped target-profile job is sufficient; a run that clearly did
    # work only for the opposite profile must not cover this target.
    target_suffix = f"_{requested_profile}"
    target_profile_jobs = [
        job for job in jobs if str(job.get("name") or "").lower().endswith(target_suffix)
    ]
    if any(
        str(job.get("status") or "").lower() != "completed"
        or str(job.get("conclusion") or "").lower() not in {"", "skipped", "neutral"}
        for job in target_profile_jobs
    ):
        return True
    opposite_suffix = "_us" if requested_profile == "kr" else "_kr"
    if any(
        str(job.get("name") or "").lower().endswith(opposite_suffix)
        and (
            str(job.get("status") or "").lower() != "completed"
            or str(job.get("conclusion") or "").lower()
            not in {"", "skipped", "neutral"}
        )
        for job in jobs
    ):
        return False
    # If the target-profile job exists but was skipped, retain the run so the
    # explicit completed-success/no-work contract can evaluate it below.  With
    # neither profile visible, stay conservative and treat an active legacy run
    # as applicable to avoid dispatching a duplicate.
    return True


def _completed_success_no_work(
    *,
    run: dict[str, Any],
    jobs: list[dict[str, Any]],
    target: WatchdogTarget,
) -> bool:
    if (
        str(run.get("status") or "").lower() != "completed"
        or str(run.get("conclusion") or "").lower() != "success"
    ):
        return False
    work_names = set(target.work_job_names or target.job_names[:1])
    work_jobs = [job for job in jobs if str(job.get("name") or "") in work_names]
    return bool(work_jobs) and all(
        str(job.get("status") or "").lower() == "completed"
        and str(job.get("conclusion") or "").lower() in {"skipped", "neutral"}
        for job in work_jobs
    )


def _workflow_failure_fallback(
    *,
    run: dict[str, Any],
    jobs: list[dict[str, Any]],
) -> list[str]:
    failed: list[str] = []
    for job in jobs:
        job_name = str(job.get("name") or "unknown")
        conclusion = str(job.get("conclusion") or "").lower()
        if conclusion in {"", "success", "skipped", "neutral"}:
            continue
        failed_steps = [
            step
            for step in (job.get("steps") or [])
            if str(step.get("conclusion") or "").lower()
            not in {"", "success", "skipped", "neutral"}
        ]
        if failed_steps:
            failed.extend(
                f"{job_name}/{str(step.get('name') or 'unknown')}:{str(step.get('conclusion') or '').lower()}"
                for step in failed_steps
            )
        else:
            failed.append(f"{job_name}:{conclusion}")
    if failed:
        return failed
    conclusion = str(run.get("conclusion") or "").lower()
    return [f"workflow:{conclusion}"] if conclusion not in {"", "success", "skipped", "neutral"} else []


def _missing_required_job_failures(
    *,
    required_job_names: set[str],
    jobs: list[dict[str, Any]],
) -> list[str]:
    """Return synthetic failures for an incomplete end-to-end success path.

    A workflow-level ``success`` is insufficient when a required publish or
    deploy job never ran.  Explicit no-work runs are handled before this helper.
    """

    conclusions = {
        str(job.get("name") or ""): str(job.get("conclusion") or "").lower()
        for job in jobs
        if str(job.get("name") or "") in required_job_names
    }
    return [
        f"missing_or_skipped_required_job:{job_name}"
        for job_name in sorted(required_job_names)
        if conclusions.get(job_name, "") in {"", "skipped", "neutral"}
    ]


def _run_fingerprint_context(*, run: dict[str, Any], target: WatchdogTarget) -> str:
    profile = _run_marker(run, "profile", {"kr", "us", "all"}) or str(
        target.inputs.get("profile") or "none"
    ).lower()
    run_mode = _run_marker(
        run,
        "run_mode",
        {"overlay_only", "selective_rerun_only", "full", "smoke", "site_only"},
    ) or str(target.inputs.get("run_mode") or "default").lower()
    request_scope = _run_marker(
        run,
        "request_scope",
        {"default_universe", "custom_tickers", "custom_sources"},
    ) or "default_universe"
    return f"profile={profile}|run_mode={run_mode}|request_scope={request_scope}"


def _run_recovery_source(run: dict[str, Any]) -> str:
    marked = _run_marker(
        run,
        "recovery_source",
        {"native", "manual", "cloud_watchdog", "local_watchdog"},
    )
    if marked:
        return marked
    event = str(run.get("event") or "").lower()
    if event == "schedule":
        return "native"
    if event == "workflow_dispatch":
        return "manual"
    return "unknown"


def _run_marker(run: dict[str, Any], key: str, allowed: set[str]) -> str:
    title = str(run.get("display_title") or run.get("displayTitle") or "")
    match = re.search(
        rf"\[{re.escape(key)}=([a-z0-9_-]+)\]",
        title,
        flags=re.IGNORECASE,
    )
    value = match.group(1).lower() if match else ""
    return value if value in allowed else ""


_DIAGNOSTIC_ERROR_PATTERN = re.compile(
    r"(?:\bOVERLAY_[A-Z0-9_]+\b|##\[error\]|\b(?:error|exception|traceback|failed)\b)",
    flags=re.IGNORECASE,
)
_ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def _sanitize_diagnostic_line(line: str) -> str:
    value = _ANSI_PATTERN.sub("", line).strip().lower()
    value = re.sub(r"^\d{4}-\d{2}-\d{2}t\d{2}:\d{2}:\d{2}(?:\.\d+)?z\s+", "", value)
    value = re.sub(r"https?://\S+", "<url>", value)
    value = re.sub(r"(?:[a-z]:)?[/\\][^\s:]+(?:[/\\][^\s:]+)+", "<path>", value)
    value = re.sub(r"\b[0-9a-f]{12,}\b", "<hex>", value)
    value = re.sub(r"\s+", " ", value)
    return value[:1000]


def _log_text_diagnostic_signature(text: str) -> str:
    diagnostic_lines: list[str] = []
    for raw_line in text.splitlines():
        if not _DIAGNOSTIC_ERROR_PATTERN.search(raw_line):
            continue
        sanitized = _sanitize_diagnostic_line(raw_line)
        if sanitized and sanitized not in diagnostic_lines:
            diagnostic_lines.append(sanitized)
        if len(diagnostic_lines) >= 8:
            break
    if not diagnostic_lines:
        return ""
    payload = "\n".join(diagnostic_lines).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _log_archive_diagnostic_signature(raw: bytes) -> str:
    lines: list[str] = []
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        for name in sorted(archive.namelist()):
            if name.endswith("/"):
                continue
            content = archive.read(name).decode("utf-8", errors="replace")
            for raw_line in content.splitlines():
                if _DIAGNOSTIC_ERROR_PATTERN.search(raw_line):
                    lines.append(raw_line)
            if len(lines) >= 64:
                break
    return _log_text_diagnostic_signature("\n".join(lines))


def _client_failure_diagnostic_signature(client: Any, run_id: int) -> str:
    provider = getattr(client, "failure_diagnostic_signature", None)
    if not callable(provider):
        return ""
    try:
        signature = str(provider(run_id) or "").strip().lower()
    except (OSError, RuntimeError, ValueError):
        return ""
    return signature if re.fullmatch(r"[0-9a-f]{64}", signature) else ""


def _workflow_run_created_at(run: dict[str, Any]) -> datetime | None:
    raw = str(run.get("created_at") or run.get("createdAt") or "").strip()
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


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
    return utc_now.weekday() < 5 and _time_between(utc_now.time(), time(13, 35), time(18, 30))


def _latest_overlay_checkpoint(profile: str, now_kst: datetime) -> datetime | None:
    candidates: list[datetime] = []
    if profile == "kr":
        checkpoint_times = (time(10, 5), time(12, 0), time(13, 20))
        day_offsets = (0,)
    elif profile == "us":
        checkpoint_times = (time(0, 40), time(2, 10), time(22, 40))
        day_offsets = (-1, 0)
    else:
        raise ValueError(f"Unsupported overlay checkpoint profile: {profile}")
    for day_offset in day_offsets:
        checkpoint_date = (now_kst + timedelta(days=day_offset)).date()
        for checkpoint_time in checkpoint_times:
            candidate = datetime.combine(checkpoint_date, checkpoint_time, tzinfo=KST)
            if candidate <= now_kst:
                candidates.append(candidate)
    return max(candidates) if candidates else None


def _daily_codex_dependency(profile: str, now_kst: datetime) -> WatchdogDependency:
    if profile == "kr":
        job_names = ("analyze_kr", "build_pages")
    elif profile == "us":
        job_names = ("analyze_us", "build_pages")
    else:
        raise ValueError(f"Unsupported Daily Codex dependency profile: {profile}")

    return WatchdogDependency(
        name=f"daily-codex-{profile}",
        workflow_file="daily-codex-analysis.yml",
        job_names=job_names,
        window_start_kst=now_kst - timedelta(hours=24),
    )


def _daily_codex_active_blocker(profile: str, now_kst: datetime) -> WatchdogBlocker:
    if profile == "kr":
        window_start = datetime.combine(now_kst.date(), time(4, 30), tzinfo=KST)
        job_names = ("analyze_kr", "build_pages")
    elif profile == "us":
        window_start = datetime.combine(now_kst.date(), time(17, 45), tzinfo=KST)
        if now_kst.time() < time(17, 45):
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
        window_start = datetime.combine(now_kst.date(), time(9, 30), tzinfo=KST)
        job_names = ("overlay_gate", "overlay_refresh_kr", "publish_overlay_site", "deploy_overlay")
    elif profile == "us":
        window_start = datetime.combine(now_kst.date(), time(22, 30), tzinfo=KST)
        if now_kst.time() < time(22, 30):
            window_start -= timedelta(days=1)
        job_names = ("overlay_gate", "overlay_refresh_us", "publish_overlay_site", "deploy_overlay")
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
        job_names=("build_youtube_pages", "deploy", "youtube_coverage"),
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
                job_names=("build_youtube_pages", "deploy", "youtube_coverage"),
                work_job_names=("build_youtube_pages",),
                window_start_kst=youtube_window,
                inputs={
                    "lookback_hours": "24",
                    "publish": "true",
                    "recovery_source": "cloud_watchdog",
                },
                blockers=(
                    _daily_codex_active_blocker("us", now_kst),
                    _intraday_overlay_active_blocker("us", now_kst),
                ),
            )
        )

    if kst_weekday < 5:
        codex_us_window = datetime.combine(kst_date, time(17, 45), tzinfo=KST)
        if _time_between(kst_time, time(17, 50), time(22, 45)):
            targets.append(
                WatchdogTarget(
                    name="daily-codex-us",
                    workflow_file="daily-codex-analysis.yml",
                    job_names=("analyze_us", "build_pages", "deploy"),
                    work_job_names=("analyze_us",),
                    window_start_kst=codex_us_window,
                    inputs={"profile": "us", "recovery_source": "cloud_watchdog"},
                    blockers=(_intraday_overlay_active_blocker("kr", now_kst),),
                )
            )

        codex_kr_window = datetime.combine(kst_date, time(4, 30), tzinfo=KST)
        if _time_between(kst_time, time(4, 45), time(10, 15)):
            targets.append(
                WatchdogTarget(
                    name="daily-codex-kr",
                    workflow_file="daily-codex-analysis.yml",
                    job_names=("analyze_kr", "build_pages", "deploy"),
                    work_job_names=("analyze_kr",),
                    window_start_kst=codex_kr_window,
                    inputs={"profile": "kr", "recovery_source": "cloud_watchdog"},
                    blockers=(_intraday_overlay_active_blocker("us", now_kst),),
                )
            )

        if _time_between(kst_time, time(10, 0), time(13, 40)):
            kr_checkpoint = _latest_overlay_checkpoint("kr", now_kst)
            if kr_checkpoint is None:
                return targets
            targets.append(
                WatchdogTarget(
                    name=f"intraday-overlay-kr-{kr_checkpoint.strftime('%H%M')}",
                    workflow_file="intraday-overlay-refresh.yml",
                    job_names=(
                        "overlay_gate",
                        "overlay_refresh_kr",
                        "publish_overlay_site",
                        "deploy_overlay",
                    ),
                    work_job_names=("overlay_refresh_kr",),
                    window_start_kst=kr_checkpoint,
                    inputs={
                        "profile": "kr",
                        "run_mode": "overlay_only",
                        "recovery_source": "cloud_watchdog",
                    },
                    dependencies=(_daily_codex_dependency("kr", now_kst),),
                    failure_window_start_kst=_intraday_overlay_active_blocker(
                        "kr", now_kst
                    ).window_start_kst,
                )
            )

    if us_intraday_overlay_due:
        us_checkpoint = _latest_overlay_checkpoint("us", now_kst)
        if us_checkpoint is None:
            return targets
        targets.append(
            WatchdogTarget(
                name=f"intraday-overlay-us-{us_checkpoint.strftime('%m%d-%H%M')}",
                workflow_file="intraday-overlay-refresh.yml",
                job_names=(
                    "overlay_gate",
                    "overlay_refresh_us",
                    "publish_overlay_site",
                    "deploy_overlay",
                ),
                work_job_names=("overlay_refresh_us",),
                window_start_kst=us_checkpoint,
                inputs={
                    "profile": "us",
                    "run_mode": "overlay_only",
                    "recovery_source": "cloud_watchdog",
                },
                dependencies=(_daily_codex_dependency("us", now_kst),),
                failure_window_start_kst=_intraday_overlay_active_blocker(
                    "us", now_kst
                ).window_start_kst,
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
            state = "suppressed" if reason.startswith("Retry budget exhausted") else "covered"
            messages.append(f"{target.name}: {state}; {reason}")
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
