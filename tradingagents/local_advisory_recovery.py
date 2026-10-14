"""Bounded advisory dispatch from an idle local production tick.

The caller owns run-due.lock. Remote collectors retain their independent native
workspaces; their lifetime must not hold up a later market overlay checkpoint.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
from types import SimpleNamespace
import urllib.error
from zoneinfo import ZoneInfo

from tradingagents.atomic_io import atomic_write_json
from tradingagents.notifications.advisory import SPECS, canonical

REPOSITORY = "nornen0202/TradingAgents"
WORKFLOWS = {spec[0]: surface for surface, spec in SPECS.items()}


class RecoveryDiagnostic(Exception):
    """A fixed, credential-free reason code, never a remote exception body."""


def diagnostic(exc):
    reason = "API_OR_EVIDENCE_ERROR"
    if isinstance(exc, RecoveryDiagnostic):
        reason = str(exc)
    elif isinstance(exc, urllib.error.HTTPError):
        reason = f"API_HTTP_{int(exc.code)}"
    elif isinstance(exc, (urllib.error.URLError, TimeoutError)):
        reason = "API_UNAVAILABLE"
    return {"status": "ADVISORY_DIAGNOSTIC_REQUIRED", "error_type": type(exc).__name__,
            "reason_code": reason}


def timestamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("Advisory timestamp must include a timezone")
    return result


def read(path, default=None, *, reason="RECEIPT_INVALID"):
    # Corrupt evidence must stop admission, never silently reset a retry budget.
    try:
        if not path.exists():
            return default
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("Expected an object")
        return value
    except (OSError, ValueError) as exc:
        raise RecoveryDiagnostic(reason) from exc


def create_client(watchdog):
    try:
        token = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True, timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError) as exc:
        raise RecoveryDiagnostic("AUTH_UNAVAILABLE") from exc
    if not token:
        raise RecoveryDiagnostic("AUTH_UNAVAILABLE")
    class Client(watchdog.GitHubActionsClient):
        def list_active_runs(self):
            runs = {}
            # A rerun retains the original creation date. Never restrict live
            # ownership to the current day's history query.
            for status in ("queued", "in_progress", "waiting", "pending", "requested"):
                payload = self._request("GET", f"/actions/runs?branch=main&status={status}&per_page=100")
                page = payload.get("workflow_runs", [])
                if len(page) >= 100 or payload.get("total_count", 0) > len(page):
                    raise RecoveryDiagnostic("ACTIVE_HISTORY_TRUNCATED")
                runs.update({int(run["id"]): run for run in page})
            return list(runs.values())

    return Client(repository=REPOSITORY, token=token, ref="main")


def candidate_paths(archive, surface, start, finish):
    """Canonical runner IDs encode their start second in KST."""
    root = Path(os.getenv(SPECS[surface][4]) or archive / SPECS[surface][5])
    prefix = "youtube_" if surface == "youtube" else "prism_telegram_"
    for path in (root / "runs").glob(f"*/*/{SPECS[surface][3]}"):
        if not path.parent.name.startswith(prefix):
            continue
        try:
            began = datetime.strptime(path.parent.name[len(prefix):], "%Y%m%d_%H%M%S").replace(tzinfo=ZoneInfo("Asia/Seoul"))
        except ValueError:
            continue
        if start.replace(microsecond=0) <= began <= finish:
            yield path


def has_unbound_completion(archive, target, now):
    """Old-created reruns can produce new canonical work outside API history."""
    from tradingagents.local_automation import ROOT
    from tradingagents.youtube.config import load_youtube_config
    from tradingagents.prism_telegram.config import load_prism_telegram_config

    surface = WORKFLOWS[target.workflow_file]
    expected = (set(load_youtube_config(ROOT / "config/youtube_daily.toml").channel.urls) if surface == "youtube"
                else load_prism_telegram_config(ROOT / "config/prism_telegram_daily.toml").source.channel)
    for path in candidate_paths(archive, surface, target.window_start_kst, now):
        manifest = read(path, reason="CANONICAL_INVALID")
        if manifest.get("status") != "success":
            continue
        actual = manifest.get("channel_urls") if surface == "youtube" else (manifest.get("source") or {}).get("channel")
        if actual is None:
            raise RecoveryDiagnostic("CANONICAL_SCOPE_UNVERIFIED")
        if (set(actual) if surface == "youtube" else actual) != expected:
            continue
        try:
            verified, _ = canonical(archive, surface, manifest["run_id"])
        except Exception as exc:
            raise RecoveryDiagnostic("CANONICAL_INCOMPLETE") from exc
        if (manifest == verified and target.window_start_kst <= timestamp(verified["started_at"])
                <= timestamp(verified["finished_at"]) <= now):
            return True
    return False


class LocalCoverageClient:
    """Keep watchdog failure/active guards, but require real advisory production."""

    def __init__(self, client, archive):
        self.client, self.archive = client, archive
        self.jobs = {}
        self.target_window = None

    def list_jobs(self, run_id):
        if run_id not in self.jobs:
            jobs = self.client.list_jobs(run_id)
            if len(jobs) >= 100:
                raise RecoveryDiagnostic("JOBS_TRUNCATED")
            self.jobs[run_id] = jobs
        return self.jobs[run_id]

    def raw_runs(self, workflow, since):
        runs = self.client.list_runs(workflow, created_since_utc=since)
        if len(runs) >= 50:
            raise RecoveryDiagnostic("HISTORY_TRUNCATED")
        return runs

    def list_runs(self, workflow_file, *, created_since_utc):
        runs = self.raw_runs(workflow_file, created_since_utc)
        surface = WORKFLOWS.get(workflow_file)
        if not surface:
            return runs
        runs = sorted(runs, key=lambda run: timestamp(run["created_at"]), reverse=True)
        retained = []
        for run in runs:
            if any(f"[request_scope={scope}]" in str(run.get("display_title", ""))
                   for scope in ("custom_sources", "custom_tickers")):
                # Preserve the watchdog's explicit scope exclusion before
                # trying to bind a custom run to the default canonical source.
                retained.append(run)
                continue
            if run.get("status") == "completed":
                if self.target_window and timestamp(run["created_at"]) < self.target_window:
                    continue
                jobs = self.list_jobs(int(run["id"]))
                build = [job for job in jobs if job.get("name") == SPECS[surface][1]]
                steps = [step for job in build for step in job.get("steps", [])
                         if step.get("name") == SPECS[surface][2]]
                if any(step.get("conclusion") == "success" for step in steps):
                    # Once collection succeeded, missing publication/canonical
                    # evidence needs diagnosis, not another complete collection.
                    self.verify_production(surface, run, jobs, steps)
                    # This complete in-window producer is the watchdog's
                    # success boundary; superseded older evidence cannot undo
                    # it or reset newer failure accounting differently.
                    retained.append(run)
                    break
                elif run.get("conclusion") == "success":
                    # Runtime-gate green and publish=false are not new coverage,
                    # and must neither consume nor reset failure budgets.
                    continue
            retained.append(run)
        return retained

    def verify_production(self, surface, run, jobs, steps):
        if (len(steps) != 1 or run.get("head_branch") != "main"
                or (run.get("head_repository") or {}).get("full_name") != REPOSITORY
                or str(run.get("path", "")).split("@", 1)[0] != f".github/workflows/{SPECS[surface][0]}"):
            raise RecoveryDiagnostic("PRODUCER_IDENTITY_UNVERIFIED")
        step = steps[0]
        start, finish = timestamp(step["started_at"]), timestamp(step["completed_at"])
        matches = []
        # The two canonical runners name their runs in KST. Select only the
        # actual collection's seconds before opening data; an unrelated old
        # damaged manifest must not block today's independent collectors.
        for path in candidate_paths(self.archive, surface, start, finish):
            manifest = read(path, reason="CANONICAL_INVALID")
            began = timestamp(manifest["started_at"])
            if start <= began <= finish and began <= timestamp(manifest["finished_at"]) <= finish:
                try:
                    verified, _ = canonical(self.archive, surface, manifest["run_id"])
                except Exception as exc:
                    raise RecoveryDiagnostic("CANONICAL_INCOMPLETE") from exc
                if verified != manifest:
                    raise RecoveryDiagnostic("CANONICAL_CHANGED_DURING_READ")
                matches.append(verified)
        if len(matches) != 1:
            raise RecoveryDiagnostic("CANONICAL_MISSING_OR_AMBIGUOUS")
        # Delivery is independent. A failed stamp/deploy after an actual
        # completed collection must not launch research again.
        builds = [job for job in jobs if job.get("name") == SPECS[surface][1]]
        stamps = [step for job in builds for step in job.get("steps", [])
                  if step.get("name") == "Stamp rollback-resistant Pages snapshot" and step.get("conclusion") == "success"]
        if len(builds) != 1 or builds[0].get("conclusion") != "success" or len(stamps) != 1:
            raise RecoveryDiagnostic("COLLECTION_COMPLETE_PUBLICATION_INCOMPLETE")

    def failure_diagnostic_signature(self, run_id):
        return self.client.failure_diagnostic_signature(run_id)


def validate_admission(admission):
    try:
        if (admission["schema"] != "tradingagents.local-advisory-admission/v1"
                or admission["workflow"] not in WORKFLOWS
                or admission["target"] != WORKFLOWS[admission["workflow"]] + "-daily"
                or admission["status"] not in {"DISPATCH_REQUESTED", "DISPATCH_ACCEPTED", "DISPATCH_UNRESOLVED", "ACTIVE", "TERMINAL"}
                or not isinstance(admission["prior_run_ids"], list)
                or any(type(run_id) is not int or run_id <= 0 for run_id in admission["prior_run_ids"])
                or admission["inputs"]["recovery_source"] != "local_watchdog"):
            raise ValueError("Invalid admission")
        timestamp(admission["requested_at"])
        timestamp(admission["window_start"])
        if admission["status"] in {"ACTIVE", "TERMINAL"}:
            if type(admission["run_id"]) is not int or admission["run_id"] <= 0 or type(admission["run_attempt"]) is not int or admission["run_attempt"] <= 0:
                raise ValueError("Invalid admitted run")
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise RecoveryDiagnostic("ADMISSION_INVALID") from exc


def resolve_admission(client, admission):
    """Do not retry an accepted/unknown request merely because a timer expired."""
    validate_admission(admission)
    if admission["status"] == "TERMINAL":
        return admission
    workflow = admission["workflow"]
    if workflow not in WORKFLOWS:
        raise RecoveryDiagnostic("ADMISSION_INVALID")
    since = timestamp(admission["requested_at"]) - timedelta(seconds=5)
    runs = client.raw_runs(workflow, since)
    matches = [run for run in runs if int(run["id"]) not in admission["prior_run_ids"]
               and run.get("head_branch") == "main"
               and (run.get("head_repository") or {}).get("full_name") == REPOSITORY
               and run.get("event") == "workflow_dispatch"
               and "[recovery_source=local_watchdog]" in str(run.get("display_title", ""))
               and timestamp(run["created_at"]) >= since]
    if len(matches) != 1:
        return {**admission, "status": "DISPATCH_UNRESOLVED"}
    run = matches[0]
    return {**admission, "run_id": int(run["id"]), "run_attempt": int(run.get("run_attempt") or 1),
            "status": "TERMINAL" if run.get("status") == "completed" else "ACTIVE"}


def recover_due(archive, state, *, watchdog, targets, now, dry_run=False, client_factory=None):
    """Return credential-free diagnostics; errors never become core failures."""
    targets = [target for target in targets if target.workflow_file in WORKFLOWS]
    if not targets:
        return []
    # YouTube can spend three hours collecting. Reserve one further hour for
    # setup and PRISM's 45-minute collector before its 17:00 admission cutoff.
    prism_deadline = now.replace(hour=17, minute=0, second=0, microsecond=0)
    if now + timedelta(hours=4) >= prism_deadline:
        targets.sort(key=lambda target: target.workflow_file != SPECS["prism"][0])
    decisions = []
    root = state / "advisory-recovery"
    admission_path = root / "admission.json"
    try:
        client = LocalCoverageClient((client_factory or create_client)(watchdog), archive)
        admission = read(admission_path)
        if admission is not None:
            resolved = resolve_admission(client, admission)
            if not dry_run and resolved != admission:
                atomic_write_json(admission_path, resolved)
            if resolved["status"] != "TERMINAL":
                return [{"target": resolved["target"], "status": "ADVISORY_" + resolved["status"],
                         "run_id": resolved.get("run_id")}]
        # Queued native collectors may not have jobs yet. Protect both advisory
        # surfaces before dispatch, beyond the watchdog's named-job blockers.
        active = [int(run["id"]) for run in client.client.list_active_runs()
                  if run.get("status") != "completed" and run.get("head_branch") == "main"
                  and (run.get("head_repository") or {}).get("full_name") == REPOSITORY
                  and str(run.get("path", "")).split("@", 1)[0].split("/")[-1] in WORKFLOWS]
        if active:
            return [{"status": "ADVISORY_ACTIVE", "run_ids": active}]
        for original in targets:
            target = replace(original, job_names=original.work_job_names)
            workflow = target.workflow_file
            key = hashlib.sha256(f"{target.name}:{target.window_start_kst.isoformat()}".encode()).hexdigest()
            receipt_path = root / "attempts" / f"{key}.json"
            try:
                receipt = read(receipt_path, {"attempts": []})
                attempts = receipt.get("attempts")
                if not isinstance(attempts, list):
                    raise RecoveryDiagnostic("RECEIPT_INVALID")
                for attempt in attempts:
                    validate_admission(attempt)
                    if attempt["target"] != target.name or attempt["window_start"] != target.window_start_kst.isoformat():
                        raise RecoveryDiagnostic("RECEIPT_INVALID")
            except Exception as exc:
                decisions.append({"target": target.name, **diagnostic(exc)})
                continue
            # Ownership/dependency queries inspect raw jobs, never another
            # collector's canonical quality. A damaged YT packet must not
            # prevent independent PRISM recovery after YT has terminated.
            raw = SimpleNamespace(list_runs=lambda workflow_file, *, created_since_utc:
                                  client.raw_runs(workflow_file, created_since_utc), list_jobs=client.list_jobs)
            try:
                clear, reason = watchdog.blockers_are_clear(client=raw, target=target)
                if clear:
                    ready, reason = watchdog.dependencies_are_satisfied(client=raw, target=target)
                else:
                    ready = False
                if clear and ready:
                    client.target_window = target.failure_window_start_kst or target.window_start_kst
                    covered, reason = watchdog.target_is_covered(client=client, target=target)
                    if not covered and has_unbound_completion(archive, target, now):
                        raise RecoveryDiagnostic("CANONICAL_COMPLETE_PRODUCER_UNRESOLVED")
                else:
                    covered = False
            except Exception as exc:
                decisions.append({"target": target.name, **diagnostic(exc)})
                continue
            if not clear or not ready or covered:
                decisions.append({"target": target.name, "status": "ADVISORY_COVERED_OR_HELD", "reason": reason})
                continue
            if (len(attempts) >= target.max_failed_attempts or
                    attempts and now - timestamp(attempts[-1]["requested_at"]) < timedelta(minutes=60)):
                decisions.append({"target": target.name, "status": "ADVISORY_RETRY_BUDGET_OR_COOLDOWN"})
                continue
            if dry_run:
                decisions.append({"target": target.name, "status": "ADVISORY_DUE"})
                break
            before = client.raw_runs(workflow, target.window_start_kst.astimezone(timezone.utc) - timedelta(days=1))
            if any(run.get("status") != "completed" for run in before):
                decisions.append({"target": target.name, "status": "ADVISORY_ACTIVE"})
                break
            inputs = {**target.inputs, "recovery_source": "local_watchdog"}
            admission = {"schema": "tradingagents.local-advisory-admission/v1", "target": target.name,
                         "workflow": workflow, "window_start": target.window_start_kst.isoformat(),
                         "requested_at": now.isoformat(), "status": "DISPATCH_REQUESTED",
                         "prior_run_ids": [int(run["id"]) for run in before], "inputs": inputs}
            # Both durable guards precede the network mutation. Crash/timeout
            # leaves an unresolved admission, never an automatic blind retry.
            atomic_write_json(admission_path, admission)
            atomic_write_json(receipt_path, {"target": target.name, "attempts": [*attempts, admission]})
            try:
                client.client.dispatch(workflow, inputs)
            except Exception as exc:
                atomic_write_json(admission_path, {**admission, "status": "DISPATCH_UNRESOLVED",
                                                   "error_type": type(exc).__name__})
                decisions.append({"target": target.name, "status": "ADVISORY_DISPATCH_UNRESOLVED",
                                  "error_type": type(exc).__name__})
            else:
                atomic_write_json(admission_path, {**admission, "status": "DISPATCH_ACCEPTED"})
                decisions.append({"target": target.name, "status": "ADVISORY_DISPATCH_ACCEPTED"})
            break
    except Exception as exc:
        # Never serialize HTTP bodies, command stderr, tokens or private data.
        decisions.append(diagnostic(exc))
    return decisions
