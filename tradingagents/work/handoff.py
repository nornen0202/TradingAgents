from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Sequence

from .runtime import WorkRuntime, WorkRuntimeError


WORK_HANDOFF_SCHEMA = "tradingagents.work-pages-handoff/v1"
_MARKET_SURFACES = {"kr", "us"}
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_REPOSITORY_RE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")


def dispatch_pages_handoff(
    runtime: WorkRuntime,
    *,
    surface: str,
    event_id: str,
    report_sha256: str,
    repository: str,
    ref: str = "main",
    workflow: str = "work-report-pages-refresh.yml",
    force: bool = False,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    """Dispatch an exact, acknowledged market Work report to the Pages refresh workflow."""

    key = str(surface or "").strip().lower()
    event = str(event_id or "").strip()
    report_sha = str(report_sha256 or "").strip().lower()
    repo = str(repository or "").strip()
    branch = str(ref or "").strip()
    workflow_file = str(workflow or "").strip()
    if key not in _MARKET_SURFACES:
        raise WorkRuntimeError("Pages handoff is supported only for acknowledged KR/US market reports")
    if not event.startswith(f"{key}:"):
        raise WorkRuntimeError("Pages handoff event does not match the requested market surface")
    if not _SHA256_RE.fullmatch(report_sha):
        raise WorkRuntimeError("Pages handoff requires a lowercase 64-character report SHA-256")
    if not _REPOSITORY_RE.fullmatch(repo):
        raise WorkRuntimeError("Pages handoff repository must use the owner/repository form")
    if not branch or any(character.isspace() for character in branch):
        raise WorkRuntimeError("Pages handoff ref is invalid")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+\.ya?ml", workflow_file):
        raise WorkRuntimeError("Pages handoff workflow filename is invalid")

    status = runtime.status(key)
    state = status.get("state") if isinstance(status.get("state"), dict) else {}
    if str(state.get("last_acked_event_id") or "") != event:
        raise WorkRuntimeError("Pages handoff event is not the latest canonical acknowledged event")
    if str(state.get("last_acked_report_sha256") or "").lower() != report_sha:
        raise WorkRuntimeError("Pages handoff report is not the latest canonical acknowledged report")
    report_path = Path(str(state.get("last_acked_report_path") or ""))
    if not report_path.is_file():
        raise WorkRuntimeError("Pages handoff acknowledged report file is unavailable")

    receipt_path = runtime.root / "handoffs" / key / f"{report_sha}.json"
    if receipt_path.is_file() and not force:
        try:
            previous = json.loads(receipt_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise WorkRuntimeError(f"Invalid Pages handoff receipt: {receipt_path}: {exc}") from exc
        if not isinstance(previous, dict) or previous.get("schema") != WORK_HANDOFF_SCHEMA:
            raise WorkRuntimeError(f"Unsupported Pages handoff receipt: {receipt_path}")
        return {**previous, "status": "ALREADY_DISPATCHED"}

    gh = shutil.which("gh")
    if not gh:
        raise WorkRuntimeError("GitHub CLI is unavailable; Pages handoff was not dispatched")
    command: Sequence[str] = (
        gh,
        "workflow",
        "run",
        workflow_file,
        "--repo",
        repo,
        "--ref",
        branch,
        "-f",
        f"surface={key}",
        "-f",
        f"event_id={event}",
        "-f",
        f"report_sha256={report_sha}",
    )
    try:
        completed = runner(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=45,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise WorkRuntimeError(f"GitHub Pages handoff dispatch failed: {exc}") from exc
    if int(completed.returncode) != 0:
        detail = " ".join(str(completed.stderr or completed.stdout or "").split())[:500]
        raise WorkRuntimeError(
            f"GitHub Pages handoff dispatch failed with exit {completed.returncode}: {detail or 'no diagnostic'}"
        )

    receipt = {
        "schema": WORK_HANDOFF_SCHEMA,
        "surface": key,
        "event_id": event,
        "report_sha256": report_sha,
        "repository": repo,
        "ref": branch,
        "workflow": workflow_file,
        "status": "DISPATCH_ACCEPTED",
        "dispatched_at": datetime.now().astimezone().isoformat(),
        "external_delivery_verified": False,
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = receipt_path.with_suffix(".tmp")
    temporary.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(receipt_path)
    return receipt
