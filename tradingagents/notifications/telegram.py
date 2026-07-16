from __future__ import annotations

import hashlib
import io
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Iterator, Sequence


LEDGER_SCHEMA = "tradingagents.telegram-notification-ledger/v1"
MAX_TELEGRAM_TEXT_CHARS = 3_500
DEFAULT_FAILURE_INCIDENT_COOLDOWN_MINUTES = 360
_CURRENT_FRESHNESS = {"LIVE_CHECKPOINT", "CURRENT_SESSION", "CURRENT_RUN_FRESH", "FRESH"}
_MAX_ACTION_DATA_AGE = timedelta(minutes=30)
_MAX_CLOCK_SKEW = timedelta(minutes=5)


class NotificationError(RuntimeError):
    """A safe-to-display notification failure without secret-bearing details."""


@dataclass(frozen=True)
class WorkflowSpec:
    terminal_jobs: tuple[str, ...]
    run_labels: tuple[str, ...] = ()


WORKFLOW_SPECS: dict[str, WorkflowSpec] = {
    "Daily Codex Analysis": WorkflowSpec(
        terminal_jobs=("deploy",),
        run_labels=("github-actions-us", "github-actions-kr"),
    ),
    "Intraday Overlay Refresh": WorkflowSpec(
        terminal_jobs=("deploy_overlay",),
        run_labels=("github-actions-overlay-us", "github-actions-overlay-kr"),
    ),
    "Account Portfolio Report Verify": WorkflowSpec(
        terminal_jobs=("deploy",),
        run_labels=("github-actions-portfolio-us", "github-actions-portfolio-kr"),
    ),
    "Daily YouTube Verified Reports": WorkflowSpec(terminal_jobs=("deploy",)),
    "Daily PRISM Telegram Reports": WorkflowSpec(terminal_jobs=("deploy",)),
}


def inspect_workflow_run(
    run: dict[str, Any],
    jobs: Sequence[dict[str, Any]],
    *,
    repository: str,
    failure_diagnostics: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Validate a workflow_run payload and decide whether it represents real work."""

    workflow_name = str(run.get("name") or "")
    spec = WORKFLOW_SPECS.get(workflow_name)
    if spec is None:
        raise NotificationError(f"Unsupported upstream workflow: {workflow_name or '(missing)'}")

    head_repository = run.get("head_repository") if isinstance(run.get("head_repository"), dict) else {}
    head_repository_name = str(head_repository.get("full_name") or "")
    head_branch = str(run.get("head_branch") or "")
    if head_repository_name != repository or head_branch != "main":
        raise NotificationError("Refusing notification for an untrusted repository or branch.")
    upstream_run_id = int(run.get("id") or 0)
    head_sha = str(run.get("head_sha") or "").lower()
    if upstream_run_id <= 0:
        raise NotificationError("Upstream workflow provenance is incomplete.")

    conclusion = str(run.get("conclusion") or "").lower()
    if conclusion not in {
        "success",
        "failure",
        "cancelled",
        "timed_out",
        "action_required",
        "neutral",
        "startup_failure",
        "stale",
        "skipped",
    }:
        raise NotificationError(f"Unsupported upstream conclusion: {conclusion or '(missing)'}")
    if conclusion == "success" and not re.fullmatch(r"[0-9a-f]{40}", head_sha):
        raise NotificationError("Successful upstream workflow provenance is incomplete.")

    terminal_names = set(spec.terminal_jobs)
    terminal_jobs = [job for job in jobs if str(job.get("name") or "") in terminal_names]
    successful_terminal_jobs = [
        str(job.get("name") or "")
        for job in terminal_jobs
        if str(job.get("conclusion") or "").lower() == "success"
    ]
    attempted_terminal_jobs = [
        str(job.get("name") or "")
        for job in terminal_jobs
        if str(job.get("conclusion") or "").lower() not in {"", "skipped"}
    ]
    terminal_deploy_superseded = _terminal_deploy_was_superseded(terminal_jobs)
    attempted_job_names = [
        str(job.get("name") or "")
        for job in jobs
        if str(job.get("name") or "").strip()
        and str(job.get("conclusion") or "").lower() not in {"", "skipped"}
    ]
    successful_job_names = {
        str(job.get("name") or "")
        for job in jobs
        if str(job.get("conclusion") or "").lower() == "success"
    }
    surfaces: list[str] = []
    if successful_job_names & {"analyze_kr", "overlay_refresh_kr", "verify_kr"}:
        surfaces.append("kr")
    if successful_job_names & {"analyze_us", "overlay_refresh_us", "verify_us"}:
        surfaces.append("us")
    if workflow_name == "Daily YouTube Verified Reports" and successful_terminal_jobs:
        surfaces.append("youtube")
    if workflow_name == "Daily PRISM Telegram Reports" and successful_terminal_jobs:
        surfaces.append("prism")

    # Backup schedule probes deliberately finish successfully with all work jobs
    # skipped. Do not turn those probes into false completion notifications.
    # ``startup_failure`` and ``stale`` are real GitHub Actions completion
    # conclusions.  They commonly have no jobs to inspect, but still need a
    # phone alert.  A wholly skipped workflow is the opposite: it represents a
    # scheduler/no-work outcome and must not create a false failure alert.
    display_title = str(run.get("display_title") or "")
    recovery_source = _workflow_recovery_source(
        event=str(run.get("event") or ""),
        display_title=display_title,
    )
    failure_context = _workflow_failure_context(
        workflow_name=workflow_name,
        conclusion=conclusion,
        head_sha=head_sha,
        event=str(run.get("event") or ""),
        display_title=display_title,
        recovery_source=recovery_source,
        jobs=jobs,
        upstream_run_id=upstream_run_id,
        failure_diagnostics=failure_diagnostics or {},
    )
    failure_fingerprint = (
        hashlib.sha256(
            json.dumps(
                failure_context,
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        if conclusion != "success"
        else ""
    )
    if conclusion == "skipped":
        should_notify = False
        reason = "no_work_workflow_skipped"
    elif conclusion in {"cancelled", "neutral"} and not attempted_job_names:
        should_notify = False
        reason = "no_work_unattempted"
    elif conclusion != "success":
        should_notify = True
        reason = "upstream_failed"
    elif successful_terminal_jobs and terminal_deploy_superseded:
        should_notify = False
        reason = "no_work_superseded"
    elif successful_terminal_jobs:
        should_notify = True
        reason = "terminal_job_succeeded"
    else:
        should_notify = False
        reason = "no_work_gate_skip"
    return {
        "workflow_name": workflow_name,
        "repository": repository,
        "upstream_run_id": upstream_run_id,
        "upstream_run_attempt": int(run.get("run_attempt") or 1),
        "head_sha": head_sha,
        "conclusion": conclusion,
        "should_notify": should_notify,
        "reason": reason,
        "html_url": str(run.get("html_url") or ""),
        "event": str(run.get("event") or ""),
        "created_at": str(run.get("created_at") or ""),
        "updated_at": str(run.get("updated_at") or ""),
        "successful_terminal_jobs": successful_terminal_jobs,
        "attempted_terminal_jobs": attempted_terminal_jobs,
        "terminal_deploy_superseded": terminal_deploy_superseded,
        "attempted_job_names": attempted_job_names,
        "run_labels": list(spec.run_labels),
        "surfaces": surfaces,
        "display_title": display_title,
        "recovery_source": recovery_source,
        "failure_context": failure_context,
        "failure_fingerprint": failure_fingerprint,
    }


def _workflow_recovery_source(*, event: str, display_title: str) -> str:
    match = re.search(
        r"\[recovery_source=(native|manual|cloud_watchdog|local_watchdog)\]",
        str(display_title or ""),
        flags=re.IGNORECASE,
    )
    if match:
        return match.group(1).lower()
    return "native" if str(event or "").lower() == "schedule" else "manual"


def _workflow_failure_context(
    *,
    workflow_name: str,
    conclusion: str,
    head_sha: str,
    event: str,
    display_title: str,
    recovery_source: str,
    jobs: Sequence[dict[str, Any]],
    upstream_run_id: int,
    failure_diagnostics: dict[str, str],
) -> dict[str, Any]:
    failed_stages: list[str] = []
    for job in jobs:
        job_name = _fingerprint_token(job.get("name") or "unknown_job")
        job_conclusion = str(job.get("conclusion") or "").strip().lower()
        if job_conclusion in {"", "success", "skipped", "neutral"}:
            continue
        failed_steps = [
            step
            for step in (job.get("steps") or [])
            if str(step.get("conclusion") or "").strip().lower()
            not in {"", "success", "skipped", "neutral"}
        ]
        if failed_steps:
            for step in failed_steps:
                failed_stages.append(
                    f"{job_name}/{_fingerprint_token(step.get('name') or 'unknown_step')}:"
                    f"{str(step.get('conclusion') or '').strip().lower()}"
                )
        else:
            failed_stages.append(f"{job_name}:{job_conclusion}")
    if not failed_stages:
        failed_stages.append(f"workflow:{str(conclusion or 'unknown').lower()}")

    profile = _workflow_marker(display_title, "profile", {"kr", "us", "all"})
    if not profile:
        job_names = {str(job.get("name") or "").lower() for job in jobs}
        has_kr = any(name.endswith("_kr") for name in job_names)
        has_us = any(name.endswith("_us") for name in job_names)
        profile = "all" if has_kr and has_us else "kr" if has_kr else "us" if has_us else "unknown"
    run_mode = _workflow_marker(
        display_title,
        "run_mode",
        {"overlay_only", "selective_rerun_only", "full", "smoke", "site_only"},
    )
    if not run_mode:
        run_mode = "overlay_only" if workflow_name == "Intraday Overlay Refresh" else "default"
    request_scope = _workflow_marker(
        display_title,
        "request_scope",
        {"default_universe", "custom_tickers", "custom_sources"},
    ) or "default_universe"
    origin_class = "manual" if recovery_source == "manual" else "automated"
    diagnostic_signatures = sorted(
        {
            str(value).lower()
            for value in failure_diagnostics.values()
            if re.fullmatch(r"[0-9a-f]{64}", str(value).lower())
        }
    )
    context = {
        "schema": "tradingagents.notification-failure-context/v1",
        "workflow": workflow_name,
        "conclusion": str(conclusion or "").lower(),
        "head_sha": str(head_sha or "unknown").lower(),
        "profile": profile,
        "run_mode": run_mode,
        "request_scope": request_scope,
        "origin_class": origin_class,
        "event_class": "manual" if str(event or "").lower() == "workflow_dispatch" and origin_class == "manual" else "automated",
        "failed_stages": sorted(set(failed_stages)),
        "diagnostic_signatures": diagnostic_signatures,
        "diagnostic_mode": "stable_log_signature" if diagnostic_signatures else "run_scoped_fallback",
    }
    if not diagnostic_signatures:
        # Without a stable diagnostic signature, treating two failures as the
        # same root cause could hide a new actionable incident in the same
        # broad workflow step.  Fail open to one alert per run instead.
        context["run_nonce"] = int(upstream_run_id)
    return context


def _workflow_marker(display_title: str, key: str, allowed: set[str]) -> str:
    match = re.search(
        rf"\[{re.escape(key)}=([a-z0-9_-]+)\]",
        str(display_title or ""),
        flags=re.IGNORECASE,
    )
    value = match.group(1).lower() if match else ""
    return value if value in allowed else ""


def _fingerprint_token(value: Any) -> str:
    normalized = re.sub(r"\s+", " ", str(value or "")).strip().lower()
    return re.sub(r"[^a-z0-9_.:/ -]+", "?", normalized)[:160] or "unknown"


def _terminal_deploy_was_superseded(terminal_jobs: Sequence[dict[str, Any]]) -> bool:
    deploy_steps = [
        step
        for job in terminal_jobs
        if str(job.get("conclusion") or "").lower() == "success"
        for step in (job.get("steps") or [])
        if re.search(r"\bdeploy\b", str(step.get("name") or ""), flags=re.IGNORECASE)
    ]
    return bool(deploy_steps) and all(
        str(step.get("conclusion") or "").lower() in {"skipped", "neutral"}
        for step in deploy_steps
    )


class GitHubActionsClient:
    def __init__(self, *, repository: str, token: str, timeout_seconds: float = 20.0) -> None:
        if not repository or not token:
            raise NotificationError("GitHub repository and token are required.")
        self.repository = repository
        self.token = token
        self.timeout_seconds = timeout_seconds

    def inspect_run(self, run_id: int) -> dict[str, Any]:
        run = self._get(f"/actions/runs/{int(run_id)}")
        jobs: list[dict[str, Any]] = []
        page = 1
        while True:
            payload = self._get(f"/actions/runs/{int(run_id)}/jobs?per_page=100&page={page}")
            batch = list(payload.get("jobs") or [])
            jobs.extend(item for item in batch if isinstance(item, dict))
            if len(batch) < 100:
                break
            page += 1
        diagnostics = (
            self._failure_diagnostics(run_id=int(run_id))
            if str(run.get("conclusion") or "").lower() != "success"
            else {}
        )
        return inspect_workflow_run(
            run,
            jobs,
            repository=self.repository,
            failure_diagnostics=diagnostics,
        )

    def _failure_diagnostics(self, *, run_id: int) -> dict[str, str]:
        try:
            raw = self._get_bytes(f"/actions/runs/{int(run_id)}/logs", max_bytes=32_000_000)
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                diagnostics: dict[str, str] = {}
                for name in sorted(archive.namelist()):
                    if name.endswith("/"):
                        continue
                    try:
                        text = archive.read(name).decode("utf-8", errors="replace")
                    except (KeyError, OSError):
                        continue
                    signature = _diagnostic_signature(text)
                    if signature:
                        diagnostics[name[:160]] = signature
                return diagnostics
        except (NotificationError, OSError, zipfile.BadZipFile):
            # The incident fingerprint deliberately becomes run-scoped when
            # logs are unavailable, so a possibly new root cause is alerted.
            return {}

    def _get(self, path: str) -> dict[str, Any]:
        request = urllib.request.Request(
            f"https://api.github.com/repos/{self.repository}{path}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "TradingAgents-notifier",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            status = getattr(exc, "code", None)
            suffix = f" HTTP {status}" if status else ""
            raise NotificationError(f"GitHub Actions metadata request failed.{suffix}") from None
        if not isinstance(payload, dict):
            raise NotificationError("GitHub Actions metadata response was not an object.")
        return payload

    def _get_bytes(self, path: str, *, max_bytes: int) -> bytes:
        request = urllib.request.Request(
            f"https://api.github.com/repos/{self.repository}{path}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "TradingAgents-notifier",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                payload = response.read(max_bytes + 1)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
            raise NotificationError("GitHub Actions log request failed.") from None
        if len(payload) > max_bytes:
            raise NotificationError("GitHub Actions log archive exceeded the safe size limit.")
        return payload


class TelegramBotClient:
    def __init__(
        self,
        *,
        bot_token: str,
        chat_id: str,
        timeout_seconds: float = 20.0,
        max_attempts: int = 4,
        sleep: Callable[[float], None] = time.sleep,
        opener: Callable[..., Any] = urllib.request.urlopen,
    ) -> None:
        if not bot_token or not chat_id:
            raise NotificationError(
                "TELEGRAM_BOT_TOKEN and TELEGRAM_NOTIFICATION_CHAT_ID are required."
            )
        normalized_chat_id = str(chat_id).strip()
        try:
            numeric_chat_id = int(normalized_chat_id)
        except ValueError:
            raise NotificationError(
                "TELEGRAM_NOTIFICATION_CHAT_ID must be a positive numeric private-chat ID."
            ) from None
        # Telegram private user chats use positive numeric IDs; groups and
        # channels use negative IDs (or channel usernames).  The notification
        # can contain holdings and personal strategy links, so fail closed
        # instead of permitting a group/channel destination.
        if numeric_chat_id <= 0 or normalized_chat_id != str(numeric_chat_id):
            raise NotificationError(
                "TELEGRAM_NOTIFICATION_CHAT_ID must identify a private user chat."
            )
        self._api_base = f"https://api.telegram.org/bot{bot_token}"
        self._endpoint = f"{self._api_base}/sendMessage"
        self.chat_id = normalized_chat_id
        self.timeout_seconds = max(1.0, float(timeout_seconds))
        self.max_attempts = max(1, int(max_attempts))
        self._sleep = sleep
        self._opener = opener

    def ensure_private_chat(self) -> None:
        """Verify a Telegram getChat receipt before sending sensitive content."""

        encoded = json.dumps({"chat_id": self.chat_id}).encode("utf-8")
        for attempt in range(1, self.max_attempts + 1):
            try:
                request = urllib.request.Request(
                    f"{self._api_base}/getChat",
                    data=encoded,
                    method="POST",
                    headers={"Content-Type": "application/json", "User-Agent": "TradingAgents-notifier"},
                )
                with self._opener(request, timeout=self.timeout_seconds) as response:
                    status = int(getattr(response, "status", 200))
                    raw = response.read()
            except urllib.error.HTTPError as exc:
                status = int(exc.code)
                try:
                    raw = exc.read(16_384)
                finally:
                    exc.close()
            except (urllib.error.URLError, TimeoutError, OSError):
                if attempt >= self.max_attempts:
                    raise NotificationError(
                        "Telegram private-chat verification failed after retryable network errors."
                    ) from None
                self._sleep(min(2 ** (attempt - 1), 8))
                continue
            except ValueError:
                raise NotificationError("Telegram private-chat verification request is invalid.") from None

            response_payload = _json_object_or_empty(raw)
            if status == 200 and response_payload.get("ok") is True:
                result = (
                    response_payload.get("result")
                    if isinstance(response_payload.get("result"), dict)
                    else {}
                )
                try:
                    receipt_chat_id = int(result.get("id"))
                except (TypeError, ValueError):
                    raise NotificationError(
                        "Telegram getChat response did not contain a valid chat receipt."
                    ) from None
                if receipt_chat_id != int(self.chat_id):
                    raise NotificationError(
                        "Telegram getChat receipt did not match the configured destination."
                    )
                if str(result.get("type") or "").lower() != "private":
                    raise NotificationError(
                        "Refusing to send sensitive notification to a non-private Telegram chat."
                    )
                return

            retry_after = _telegram_retry_after(response_payload)
            retryable = status == 429 or 500 <= status <= 599
            if retryable and attempt < self.max_attempts:
                delay = retry_after if retry_after is not None else min(2 ** (attempt - 1), 8)
                self._sleep(max(0.0, min(float(delay), 60.0)))
                continue
            raise NotificationError(f"Telegram private-chat verification failed (HTTP {status}).")

        raise NotificationError("Telegram private-chat verification exhausted all attempts.")

    def send_message(
        self,
        text: str,
        *,
        buttons: Sequence[Sequence[dict[str, str]]] | None = None,
    ) -> int:
        if not text or len(text) > 4_096:
            raise NotificationError("Telegram message text is empty or exceeds 4096 characters.")
        payload: dict[str, Any] = {
            "chat_id": self.chat_id,
            "text": text,
            "disable_web_page_preview": True,
            "protect_content": True,
        }
        if buttons:
            payload["reply_markup"] = {"inline_keyboard": [list(row) for row in buttons]}
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        for attempt in range(1, self.max_attempts + 1):
            try:
                request = urllib.request.Request(
                    self._endpoint,
                    data=encoded,
                    method="POST",
                    headers={"Content-Type": "application/json", "User-Agent": "TradingAgents-notifier"},
                )
                with self._opener(request, timeout=self.timeout_seconds) as response:
                    status = int(getattr(response, "status", 200))
                    raw = response.read()
            except urllib.error.HTTPError as exc:
                status = int(exc.code)
                try:
                    raw = exc.read(16_384)
                finally:
                    exc.close()
            except (urllib.error.URLError, TimeoutError, OSError):
                if attempt >= self.max_attempts:
                    raise NotificationError("Telegram delivery failed after retryable network errors.") from None
                self._sleep(min(2 ** (attempt - 1), 8))
                continue
            except ValueError:
                raise NotificationError("Telegram delivery request is invalid.") from None

            response_payload = _json_object_or_empty(raw)
            if status == 200 and response_payload.get("ok") is True:
                result = response_payload.get("result") if isinstance(response_payload.get("result"), dict) else {}
                message_id = result.get("message_id")
                if isinstance(message_id, int):
                    return message_id
                raise NotificationError("Telegram accepted the request without a message receipt.")

            retry_after = _telegram_retry_after(response_payload)
            retryable = status == 429 or 500 <= status <= 599
            if retryable and attempt < self.max_attempts:
                delay = retry_after if retry_after is not None else min(2 ** (attempt - 1), 8)
                self._sleep(max(0.0, min(float(delay), 60.0)))
                continue
            raise NotificationError(f"Telegram rejected the notification (HTTP {status}).")

        raise NotificationError("Telegram delivery exhausted all attempts.")


class AtomicNotificationLedger:
    """Durable resumable delivery state; message bodies and secret URLs are never stored."""

    def __init__(
        self,
        path: Path,
        *,
        lock_timeout_seconds: float = 30.0,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.path = Path(path)
        self.lock_path = self.path.with_suffix(self.path.suffix + ".lock")
        self.lock_timeout_seconds = lock_timeout_seconds
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def deliver(
        self,
        *,
        event_key: str,
        chunks: Sequence[str],
        buttons: Sequence[Sequence[dict[str, str]]] | None,
        sender: Callable[[str, Sequence[Sequence[dict[str, str]]] | None], int],
        receipt_metadata: dict[str, Any],
        incident_key: str | None = None,
        incident_cooldown_seconds: float = 0.0,
    ) -> dict[str, Any]:
        if not event_key or not chunks:
            raise NotificationError("Notification event key and chunks are required.")
        digest = _content_digest(chunks, buttons)
        with _exclusive_lock(self.lock_path, timeout_seconds=self.lock_timeout_seconds):
            ledger = self._load()
            entries = ledger.setdefault("entries", {})
            incidents = ledger.setdefault("incidents", {})
            current = entries.get(event_key)
            if isinstance(current, dict):
                if current.get("content_sha256") != digest:
                    raise NotificationError("Notification event key collision with different content.")
                if current.get("status") == "delivered":
                    return {
                        "status": "NOOP",
                        "reason": "EVENT_ALREADY_DELIVERED",
                        "event_key": event_key,
                        "message_ids": list(current.get("message_ids") or []),
                    }
            else:
                normalized_incident_key = str(incident_key or "").strip()
                if normalized_incident_key and incident_cooldown_seconds > 0:
                    prior_incident = incidents.get(normalized_incident_key)
                    if isinstance(prior_incident, dict):
                        incident_at = _try_datetime(
                            str(
                                prior_incident.get("last_delivered_at")
                                or prior_incident.get("first_seen_at")
                                or ""
                            )
                        )
                        now = _normalized_utc(self._clock())
                        if (
                            incident_at is not None
                            and now - incident_at < timedelta(seconds=incident_cooldown_seconds)
                        ):
                            prior_incident.update(
                                {
                                    "last_seen_at": now.isoformat(),
                                    "last_event_key": event_key,
                                    "suppressed_count": int(
                                        prior_incident.get("suppressed_count") or 0
                                    )
                                    + 1,
                                }
                            )
                            self._write(ledger)
                            return {
                                "status": "NOOP",
                                "reason": "INCIDENT_COOLDOWN",
                                "event_key": event_key,
                                "incident_key": normalized_incident_key,
                                "message_ids": [],
                            }
                now_text = _normalized_utc(self._clock()).isoformat()
                current = {
                    "status": "pending",
                    "content_sha256": digest,
                    "chunk_count": len(chunks),
                    "sent_chunks": 0,
                    "message_ids": [],
                    "created_at": now_text,
                    **_safe_receipt_metadata(receipt_metadata),
                }
                entries[event_key] = current
                if normalized_incident_key:
                    previous_incident = incidents.get(normalized_incident_key)
                    previous_suppressed_count = (
                        int(previous_incident.get("suppressed_count") or 0)
                        if isinstance(previous_incident, dict)
                        else 0
                    )
                    incidents[normalized_incident_key] = {
                        "status": "pending",
                        "event_key": event_key,
                        "first_seen_at": now_text,
                        "last_seen_at": now_text,
                        "suppressed_count": previous_suppressed_count,
                    }
                self._write(ledger)

            sent_chunks = int(current.get("sent_chunks") or 0)
            if sent_chunks < 0 or sent_chunks > len(chunks):
                raise NotificationError("Notification ledger contains an invalid chunk cursor.")
            message_ids = list(current.get("message_ids") or [])
            for index in range(sent_chunks, len(chunks)):
                message_id = sender(chunks[index], buttons if index == 0 else None)
                message_ids.append(int(message_id))
                current.update(
                    {
                        "status": "pending",
                        "sent_chunks": index + 1,
                        "message_ids": message_ids,
                        "updated_at": _normalized_utc(self._clock()).isoformat(),
                    }
                )
                self._write(ledger)

            delivered_at = _normalized_utc(self._clock()).isoformat()
            current.update({"status": "delivered", "delivered_at": delivered_at})
            normalized_incident_key = str(incident_key or "").strip()
            if normalized_incident_key:
                incident = incidents.setdefault(normalized_incident_key, {})
                incident.update(
                    {
                        "status": "delivered",
                        "event_key": event_key,
                        "last_event_key": event_key,
                        "last_delivered_at": delivered_at,
                        "last_seen_at": delivered_at,
                        "suppressed_count": int(incident.get("suppressed_count") or 0),
                    }
                )
            self._write(ledger)
            return {
                "status": "SENT",
                "event_key": event_key,
                "incident_key": normalized_incident_key or None,
                "message_ids": message_ids,
            }

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"schema": LEDGER_SCHEMA, "entries": {}, "incidents": {}}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            raise NotificationError("Notification ledger is unreadable; refusing a possible duplicate.") from None
        if not isinstance(payload, dict) or payload.get("schema") != LEDGER_SCHEMA:
            raise NotificationError("Notification ledger schema is invalid.")
        if not isinstance(payload.get("entries"), dict):
            raise NotificationError("Notification ledger entries are invalid.")
        if payload.get("incidents") is not None and not isinstance(payload.get("incidents"), dict):
            raise NotificationError("Notification ledger incidents are invalid.")
        payload.setdefault("incidents", {})
        return payload

    def _write(self, ledger: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        raw = (json.dumps(ledger, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
        temp_path = self.path.with_name(f".{self.path.name}.{os.getpid()}.tmp")
        try:
            with temp_path.open("wb") as handle:
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, self.path)
        finally:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass


def chunk_text(text: str, limit: int = MAX_TELEGRAM_TEXT_CHARS) -> list[str]:
    if limit < 32:
        raise ValueError("Chunk limit must be at least 32 characters.")
    normalized = str(text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        return []
    chunks: list[str] = []
    current = ""
    for line in normalized.split("\n"):
        pieces = [line[index : index + limit] for index in range(0, len(line), limit)] or [""]
        for piece in pieces:
            candidate = piece if not current else f"{current}\n{piece}"
            if len(candidate) <= limit:
                current = candidate
            else:
                chunks.append(current.rstrip())
                current = piece
    if current.strip():
        chunks.append(current.rstrip())
    if not chunks or any(len(chunk) > limit for chunk in chunks):
        raise AssertionError("Telegram chunking invariant failed.")
    return chunks


def notification_event_key(*, repository: str, upstream_run_id: int, conclusion: str, chat_id: str) -> str:
    chat_hash = hashlib.sha256(str(chat_id).encode("utf-8")).hexdigest()[:16]
    material = f"telegram-notification/v1\0{repository}\0{int(upstream_run_id)}\0{conclusion}\0{chat_hash}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:40]


def notification_incident_key(*, repository: str, failure_fingerprint: str, chat_id: str) -> str:
    fingerprint = str(failure_fingerprint or "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", fingerprint):
        return ""
    chat_hash = hashlib.sha256(str(chat_id).encode("utf-8")).hexdigest()[:16]
    material = f"telegram-failure-incident/v1\0{repository}\0{fingerprint}\0{chat_hash}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:40]


def find_market_runs(
    *,
    archive_dir: Path,
    labels: Sequence[str],
    created_at: str,
    updated_at: str,
    upstream_run_id: int,
    repository: str,
    workflow_name: str,
    head_sha: str,
) -> list[dict[str, Any]]:
    if not labels:
        return []
    start = _parse_datetime(created_at) - timedelta(minutes=10)
    end = _parse_datetime(updated_at) + timedelta(minutes=10)
    manifests: list[tuple[datetime, dict[str, Any], Path]] = []
    runs_root = Path(archive_dir) / "runs"
    if not runs_root.is_dir():
        return []
    for year_dir in runs_root.iterdir():
        if not year_dir.is_dir():
            continue
        for run_dir in year_dir.iterdir():
            if not run_dir.is_dir():
                continue
            manifest_path = run_dir / "run.json"
            if not manifest_path.is_file():
                continue
            try:
                payload = json.loads(manifest_path.read_text(encoding="utf-8"))
                finished = _parse_datetime(str(payload.get("finished_at") or payload.get("started_at") or ""))
            except (OSError, json.JSONDecodeError, ValueError):
                continue
            if str(payload.get("run_id") or "") != run_dir.name:
                continue
            github_actions = (
                payload.get("github_actions")
                if isinstance(payload.get("github_actions"), dict)
                else {}
            )
            if (
                _exact_int(github_actions.get("run_id")) != int(upstream_run_id)
                or str(github_actions.get("repository") or "") != repository
                or str(github_actions.get("workflow") or "") != workflow_name
                or str(github_actions.get("sha") or "").lower() != str(head_sha or "").lower()
            ):
                continue
            if str(payload.get("label") or "") not in labels or not (start <= finished <= end):
                continue
            manifests.append((finished, payload, run_dir))

    latest_by_market: dict[str, tuple[datetime, dict[str, Any], Path]] = {}
    for item in manifests:
        market = str(((item[1].get("settings") or {}).get("market") or item[1].get("market") or "")).upper()
        if market not in {"KR", "US"}:
            continue
        if market not in latest_by_market or item[0] > latest_by_market[market][0]:
            latest_by_market[market] = item

    results: list[dict[str, Any]] = []
    for market in ("KR", "US"):
        item = latest_by_market.get(market)
        if item is None:
            continue
        _, manifest, run_dir = item
        bundle = _load_json_object(run_dir / "decision_bundle_v2.json")
        results.append(
            {
                "market": market,
                "run_id": str(manifest.get("run_id") or run_dir.name),
                "label": str(manifest.get("label") or ""),
                "status": str(manifest.get("status") or ""),
                "started_at": str(manifest.get("started_at") or ""),
                "finished_at": str(manifest.get("finished_at") or ""),
                "summary": manifest.get("summary") if isinstance(manifest.get("summary"), dict) else {},
                "active_universe": (
                    manifest.get("active_universe")
                    if isinstance(manifest.get("active_universe"), dict)
                    else {}
                ),
                "manifest_tickers": [
                    value for value in (manifest.get("tickers") or []) if isinstance(value, dict)
                ],
                "github_actions": github_actions,
                "bundle": bundle,
            }
        )
    return results


def compose_notification(
    context: dict[str, Any],
    *,
    archive_dir: Path,
    public_base_url: str,
    cards_only: bool = False,
) -> tuple[list[str], list[list[dict[str, str]]], dict[str, Any]]:
    workflow_name = str(context["workflow_name"])
    conclusion = str(context["conclusion"])
    run_id = int(context["upstream_run_id"])
    actions_url = str(context.get("html_url") or "")
    base = public_base_url.rstrip("/")
    completed = _format_kst(str(context.get("updated_at") or ""))

    if conclusion != "success":
        if cards_only:
            return [], [], {"markets": [], "run_ids": [], "surfaces": []}
        failure_fingerprint = str(context.get("failure_fingerprint") or "").lower()
        text = "\n".join(
            [
                f"🚨 TradingAgents 자동화 {conclusion.upper()}",
                f"워크플로: {workflow_name}",
                f"완료 시각: {completed}",
                f"GitHub 실행 ID: {run_id}",
                f"장애 식별자: {failure_fingerprint[:12] or '확인 불가'}",
                "분석 또는 배포가 완료되지 않았습니다. 기존 투자 전략을 최신 결과로 간주하지 마세요.",
            ]
        )
        buttons = [[{"text": "실패 로그 확인", "url": actions_url}]] if _is_https_url(actions_url) else []
        return chunk_text(text), buttons, {
            "markets": [],
            "run_ids": [],
            "surfaces": [],
            "failure_fingerprint": failure_fingerprint,
        }

    market_runs = find_market_runs(
        archive_dir=archive_dir,
        labels=list(context.get("run_labels") or []),
        created_at=str(context.get("created_at") or ""),
        updated_at=str(context.get("updated_at") or ""),
        upstream_run_id=int(context.get("upstream_run_id") or 0),
        repository=str(context.get("repository") or ""),
        workflow_name=workflow_name,
        head_sha=str(context.get("head_sha") or ""),
    )
    surfaces = [str(value).lower() for value in (context.get("surfaces") or [])]
    expected_markets = {surface.upper() for surface in surfaces if surface in {"kr", "us"}}
    if expected_markets:
        market_runs = [item for item in market_runs if str(item.get("market") or "").upper() in expected_markets]
    lines = (
        ["TradingAgents 개인 종목 액션 카드"]
        if cards_only
        else [
            "✅ TradingAgents 분석·배포 완료",
            f"워크플로: {workflow_name}",
            f"완료 시각: {completed}",
            f"GitHub 실행 ID: {run_id}",
        ]
    )
    if not market_runs:
        if cards_only:
            return [], [], {"markets": [], "run_ids": [], "surfaces": surfaces}
        lines.extend(
            [
                "시장 archive와 직접 연결된 신규 run은 없습니다.",
                "사이트 재배포·YouTube·PRISM 작업이면 아래 공개 페이지에서 최신 결과를 확인하세요.",
            ]
        )
    if market_runs:
        for item in market_runs:
            lines.extend(
                _market_action_card_lines(
                    item,
                    workflow_created_at=str(context.get("created_at") or ""),
                    workflow_updated_at=str(context.get("updated_at") or ""),
                )
            )
    lines.append("모든 전략은 참고용이며, 주문 전 가격·시각·데이터 상태를 다시 확인하세요.")

    buttons: list[list[dict[str, str]]] = []
    for item in ([] if cards_only else market_runs):
        market = str(item["market"]).lower()
        run_public_url = f"{base}/runs/{urllib.parse.quote(str(item['run_id']))}/index.html"
        mobile_url = f"{base}/mobile/?market={urllib.parse.quote(market)}"
        row = [
            {"text": f"{market.upper()} 공개 리포트", "url": run_public_url},
            {"text": f"{market.upper()} 모바일", "url": mobile_url},
        ]
        buttons.append(row)
        private_url = (
            f"{base}/mobile/private.html"
            f"?market={urllib.parse.quote(market)}"
            f"&run={urllib.parse.quote(str(item['run_id']), safe='')}"
        )
        buttons.append([{"text": f"{market.upper()} 투자 전략", "url": private_url}])
    if not cards_only:
        represented = {str(item["market"]).lower() for item in market_runs}
        for surface in surfaces:
            if surface in represented:
                continue
            public_url, mobile_url = _surface_urls(base, surface)
            buttons.append(
                [
                    {"text": f"{surface.upper()} 공개 리포트", "url": public_url},
                    {"text": f"{surface.upper()} 모바일", "url": mobile_url},
                ]
            )
            if surface in {"kr", "us"}:
                private_url = (
                    f"{base}/mobile/private.html"
                    f"?market={urllib.parse.quote(surface)}"
                )
                buttons.append([{"text": f"{surface.upper()} 투자 전략", "url": private_url}])
    if not cards_only and not market_runs and not surfaces and base:
        buttons.append([{"text": "TradingAgents 리포트", "url": f"{base}/"}])
    if not cards_only and _is_https_url(actions_url):
        buttons.append([{"text": "GitHub 실행 로그", "url": actions_url}])

    text = "\n".join(lines)
    metadata = {
        "markets": [item["market"] for item in market_runs],
        "run_ids": [item["run_id"] for item in market_runs],
        "surfaces": surfaces,
    }
    return chunk_text(text), buttons, metadata


def _surface_urls(base: str, surface: str) -> tuple[str, str]:
    key = str(surface).lower()
    if key == "youtube":
        return f"{base}/youtube/", f"{base}/youtube/"
    if key == "prism":
        return f"{base}/prism-telegram/", f"{base}/prism-telegram/"
    return f"{base}/", f"{base}/mobile/?market={urllib.parse.quote(key)}"


def _market_action_card_lines(
    item: dict[str, Any],
    *,
    workflow_created_at: str,
    workflow_updated_at: str,
) -> list[str]:
    market = str(item.get("market") or "")
    run_id = str(item.get("run_id") or "")
    bundle = item.get("bundle") if isinstance(item.get("bundle"), dict) else {}
    quality = bundle.get("quality") if isinstance(bundle.get("quality"), dict) else {}
    summary = bundle.get("summary") if isinstance(bundle.get("summary"), dict) else {}
    rows = [row for row in (bundle.get("strategy_table") or []) if isinstance(row, dict)]
    actionable, blockers = _market_actionability_contract(
        item,
        workflow_created_at=workflow_created_at,
        workflow_updated_at=workflow_updated_at,
    )
    if not actionable:
        return [
            "",
            f"[{market}] 실행 차단·재확인 필요",
            f"분석 run: {run_id or '-'}",
            "커버리지·manifest·의사결정·신선도 계약을 모두 확인하지 못해 종목별 액션을 전송하지 않았습니다.",
            f"차단 코드: {', '.join(blockers[:6]) or 'UNVERIFIED'}",
        ]
    status = (
        "즉시 실행 검토 가능"
        if quality.get("decision_ready") is True
        else "조건부 검토"
        if quality.get("conditional_strategy_ready") is True
        else "실행 차단·재확인 필요"
    )
    lines = [
        "",
        f"[{market}] {status}",
        f"분석 run: {run_id}",
        f"종목 {len(rows)}개 · 즉시 액션 {int(summary.get('immediate_action_count') or 0)}개",
    ]
    reference_time = _try_datetime(workflow_updated_at)
    for row in sorted(rows, key=lambda value: int(value.get("table_priority") or 9999)):
        ticker = _single_line(row.get("ticker") or "-")
        if reference_time is None or not _row_is_fresh_immediate(row, reference_time=reference_time):
            lines.append(f"• {ticker} · 차단 · 데이터 재확인 필요 (종목 액션 생략)")
            continue
        held = "보유" if row.get("is_held") is True else "관심"
        row_quality = row.get("quality") if isinstance(row.get("quality"), dict) else {}
        readiness = (
            "즉시"
            if row_quality.get("execution_ready") is True
            else "조건부"
            if row_quality.get("conditional_strategy_ready") is True
            else "차단"
        )
        strategy = _single_line(row.get("strategy_ko") or row.get("strategy_code") or "확인 필요")
        price = _format_price(row.get("last_price"))
        data_status = _single_line(row.get("data_status_ko") or "데이터 상태 확인")
        condition = _truncate(_single_line(row.get("execution_condition_ko") or ""), 180)
        risk = _truncate(_single_line(row.get("risk_condition_ko") or ""), 140)
        line = f"• {ticker} · {held}/{readiness} · {strategy} · {price} · {data_status}"
        if condition:
            line += f" | 조건: {condition}"
        if risk:
            line += f" | 위험: {risk}"
        lines.append(_truncate(line, 520))
    return lines


def _market_actionability_contract(
    item: dict[str, Any],
    *,
    workflow_created_at: str,
    workflow_updated_at: str,
) -> tuple[bool, list[str]]:
    """Validate the exact source receipt before emitting ticker action text."""

    blockers: list[str] = []
    run_id = str(item.get("run_id") or "")
    market = str(item.get("market") or "").upper()
    status = str(item.get("status") or "").lower()
    summary = item.get("summary") if isinstance(item.get("summary"), dict) else {}
    active = item.get("active_universe") if isinstance(item.get("active_universe"), dict) else {}
    coverage = active.get("coverage") if isinstance(active.get("coverage"), dict) else {}
    manifest_tickers = [value for value in (item.get("manifest_tickers") or []) if isinstance(value, dict)]
    bundle = item.get("bundle") if isinstance(item.get("bundle"), dict) else {}
    quality = bundle.get("quality") if isinstance(bundle.get("quality"), dict) else {}
    rows = [value for value in (bundle.get("strategy_table") or []) if isinstance(value, dict)]

    if not run_id or status != "success":
        blockers.append("MANIFEST_NOT_SUCCESS")
    if str(bundle.get("run_id") or "") != run_id or str(bundle.get("market") or "").upper() != market:
        blockers.append("RUN_PROVENANCE_MISMATCH")
    if not str(bundle.get("analysis_source_run_id") or "") or not str(bundle.get("execution_source_run_id") or ""):
        blockers.append("SOURCE_PROVENANCE_MISSING")
    if quality.get("decision_ready") is not True:
        blockers.append("DECISION_NOT_READY")

    expected = _exact_int(coverage.get("analysis_expected_count"))
    successful = _exact_int(coverage.get("analysis_successful_count"))
    summary_total = _exact_int(summary.get("total_tickers"))
    summary_successful = _exact_int(summary.get("successful_tickers"))
    summary_failed = _exact_int(summary.get("failed_tickers"))
    if (
        coverage.get("complete") is not True
        or coverage.get("selection_complete") is not True
        or coverage.get("analysis_complete") is not True
        or expected is None
        or expected <= 0
        or successful != expected
    ):
        blockers.append("UNIVERSE_INCOMPLETE")
    for key in (
        "holding_missing_count",
        "watchlist_missing_count",
        "analysis_failed_count",
        "analysis_missing_count",
        "analysis_unexpected_count",
        "analysis_duplicate_count",
    ):
        if _exact_int(coverage.get(key)) != 0:
            blockers.append("UNIVERSE_COUNTS_UNVERIFIED")
            break
    if any(
        active.get(key)
        for key in (
            "missing_holding_tickers",
            "missing_watchlist_tickers",
            "missing_analysis_tickers",
            "failed_analysis_tickers",
            "unexpected_analysis_tickers",
            "duplicate_analysis_tickers",
        )
    ):
        blockers.append("UNIVERSE_GAPS_PRESENT")

    universe_mode = str(active.get("ticker_universe_mode") or "").lower()
    fresh_snapshot_drift = (
        active.get("fresh_snapshot_drift")
        if isinstance(active.get("fresh_snapshot_drift"), dict)
        else {}
    )
    if universe_mode in {"config_plus_account", "account_only"} and (
        str(active.get("account_snapshot_status") or "").lower() != "loaded"
        or coverage.get("fresh_snapshot_complete") is not True
        or str(fresh_snapshot_drift.get("status") or "").upper() != "VERIFIED"
    ):
        blockers.append("ACCOUNT_SNAPSHOT_UNVERIFIED")

    ticker_identities = [
        _ticker_identity(value.get("ticker"))
        for value in manifest_tickers
        if str(value.get("ticker") or "").strip()
    ]
    if (
        expected is None
        or summary_total != expected
        or summary_successful != expected
        or summary_failed != 0
        or len(manifest_tickers) != expected
        or len(ticker_identities) != expected
        or len(set(ticker_identities)) != expected
        or any(str(value.get("status") or "").lower() != "success" for value in manifest_tickers)
    ):
        blockers.append("MANIFEST_COUNTS_MISMATCH")
    bundle_total = _exact_int(quality.get("total_rows"))
    if expected is None or len(rows) != expected or bundle_total != expected:
        blockers.append("BUNDLE_COUNTS_MISMATCH")

    created = _try_datetime(workflow_created_at)
    updated = _try_datetime(workflow_updated_at)
    started = _try_datetime(str(item.get("started_at") or ""))
    finished = _try_datetime(str(item.get("finished_at") or ""))
    generated = _try_datetime(str(bundle.get("generated_at") or ""))
    if not all((created, updated, started, finished, generated)):
        blockers.append("PROVENANCE_TIME_MISSING")
    elif not (
        created - timedelta(minutes=10) <= started <= updated + timedelta(minutes=10)
        and started <= finished <= updated + timedelta(minutes=10)
        and created - timedelta(minutes=10) <= generated <= updated + timedelta(minutes=10)
    ):
        blockers.append("PROVENANCE_TIME_MISMATCH")

    if updated is None:
        blockers.append("FRESHNESS_REFERENCE_MISSING")
    else:
        fresh_rows = [row for row in rows if _row_is_fresh_immediate(row, reference_time=updated)]
        stale_held_rows = [
            row
            for row in rows
            if row.get("is_held") is True and not _row_is_fresh_immediate(row, reference_time=updated)
        ]
        if not fresh_rows or stale_held_rows:
            blockers.append("ROW_NOT_FRESH_IMMEDIATE")

    return not blockers, list(dict.fromkeys(blockers))


def _exact_int(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _ticker_identity(value: Any) -> str:
    ticker = str(value or "").strip().upper()
    for suffix in (".KS", ".KQ"):
        if ticker.endswith(suffix):
            return ticker[: -len(suffix)]
    return ticker


def _row_is_fresh_immediate(row: dict[str, Any], *, reference_time: datetime) -> bool:
    quality = row.get("quality") if isinstance(row.get("quality"), dict) else {}
    asof = _try_datetime(str(row.get("market_data_asof") or ""))
    age = reference_time - asof if asof is not None else None
    return bool(
        quality.get("generated_in_current_run") is True
        and quality.get("execution_ready") is True
        and str(quality.get("row_mode") or "").upper() == "IMMEDIATE"
        and str(quality.get("freshness_class") or "").upper() in _CURRENT_FRESHNESS
        and age is not None
        and age >= -_MAX_CLOCK_SKEW
        and age <= _MAX_ACTION_DATA_AGE
    )


def _try_datetime(value: str) -> datetime | None:
    try:
        return _parse_datetime(value)
    except ValueError:
        return None


def _content_digest(
    chunks: Sequence[str],
    buttons: Sequence[Sequence[dict[str, str]]] | None,
) -> str:
    payload = {"chunks": list(chunks), "buttons": [list(row) for row in (buttons or [])]}
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _diagnostic_signature(log_text: str) -> str:
    candidates: list[str] = []
    pattern = re.compile(
        r"(?:OVERLAY_[A-Z0-9_]+|##\[error\]|(?:runtime|value|type|key|connection|timeout)?error\s*:|exception\s*:)",
        flags=re.IGNORECASE,
    )
    for raw_line in str(log_text or "").splitlines():
        line = re.sub(r"\x1b\[[0-9;]*m", "", raw_line).strip()
        line = re.sub(r"^\d{4}-\d{2}-\d{2}T\S+Z\s+", "", line)
        if not pattern.search(line):
            continue
        # Only the digest is persisted.  Normalization removes volatile URLs,
        # paths and long tokens while preserving stable error codes/messages.
        line = re.sub(r"https?://\S+", "<url>", line)
        line = re.sub(r"[A-Za-z]:\\[^\s]+", "<path>", line)
        line = re.sub(r"\b[0-9a-f]{32,}\b", "<hex>", line, flags=re.IGNORECASE)
        line = re.sub(r"\s+", " ", line).strip()[:500]
        if line:
            candidates.append(line)
        if len(candidates) >= 3:
            break
    if not candidates:
        return ""
    return hashlib.sha256("\n".join(candidates).encode("utf-8")).hexdigest()


def _safe_receipt_metadata(value: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "repository",
        "upstream_run_id",
        "workflow_name",
        "conclusion",
        "markets",
        "run_ids",
        "surfaces",
    }
    return {key: value.get(key) for key in allowed if value.get(key) is not None}


def _load_json_object(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _json_object_or_empty(raw: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _telegram_retry_after(payload: dict[str, Any]) -> float | None:
    parameters = payload.get("parameters") if isinstance(payload.get("parameters"), dict) else {}
    value = parameters.get("retry_after")
    return float(value) if isinstance(value, (int, float)) else None


def _parse_datetime(value: str) -> datetime:
    normalized = str(value or "").strip().replace("Z", "+00:00")
    if not normalized:
        raise ValueError("Missing datetime")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _format_kst(value: str) -> str:
    try:
        from zoneinfo import ZoneInfo

        return _parse_datetime(value).astimezone(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M KST")
    except (ValueError, KeyError):
        return value or "확인 불가"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalized_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _format_price(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"현재가 {value:,.4f}".rstrip("0").rstrip(".")
    return "현재가 확인 필요"


def _single_line(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _truncate(value: str, limit: int) -> str:
    return value if len(value) <= limit else value[: max(1, limit - 1)].rstrip() + "…"


def _is_https_url(value: str) -> bool:
    parsed = urllib.parse.urlparse(str(value or ""))
    return parsed.scheme == "https" and bool(parsed.netloc)


@contextmanager
def _exclusive_lock(path: Path, *, timeout_seconds: float, stale_seconds: float = 300.0) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + max(0.1, timeout_seconds)
    while True:
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(descriptor, f"{os.getpid()}\n{_utc_now()}\n".encode("utf-8"))
            os.close(descriptor)
            break
        except FileExistsError:
            try:
                age = time.time() - path.stat().st_mtime
                if age > stale_seconds:
                    path.unlink()
                    continue
            except FileNotFoundError:
                continue
            if time.monotonic() >= deadline:
                raise NotificationError("Timed out waiting for the notification ledger lock.") from None
            time.sleep(0.1)
    try:
        yield
    finally:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
