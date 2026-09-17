from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import subprocess

import pytest


PWSH = shutil.which("pwsh") or shutil.which("pwsh.exe")
SCRIPT = Path(__file__).parents[1] / "tools" / "maintain_project_storage.ps1"


def _directory(path: Path, *, modified: datetime | None = None) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    (path / "payload.txt").write_text("generated", encoding="utf-8")
    if modified is not None:
        timestamp = modified.timestamp()
        os.utime(path / "payload.txt", (timestamp, timestamp))
        os.utime(path, (timestamp, timestamp))
    return path


def _run_maintenance(tmp_path: Path, *, apply: bool) -> subprocess.CompletedProcess[str]:
    command = [
        PWSH,
        "-NoLogo",
        "-NoProfile",
        "-File",
        str(SCRIPT),
        "-DataRoot",
        str(tmp_path / "data"),
        "-RunnerRoot",
        str(tmp_path / "runner"),
        "-RepositoryRoot",
        str(tmp_path / "repository"),
        "-RetentionDays",
        "14",
        "-RunnerDiagnosticRetentionDays",
        "14",
        "-RunnerUpdateRetentionDays",
        "7",
        "-RunnerArtifactMinimumAgeHours",
        "0",
        "-RepositoryArtifactRetentionDays",
        "14",
        "-CodexAttachmentRetentionDays",
        "14",
        "-LogPath",
        str(tmp_path / "maintenance.log"),
    ]
    if apply:
        command.append("-Apply")
    return subprocess.run(command, check=False, capture_output=True, text=True)


@pytest.mark.skipif(os.name != "nt" or PWSH is None, reason="Windows PowerShell 7 is required")
def test_storage_maintenance_dry_run_and_guarded_cleanup(tmp_path: Path) -> None:
    now = datetime.now()
    old = now - timedelta(days=30)
    recent = now - timedelta(days=2)
    old_stamp = old.strftime("%Y%m%d")
    recent_stamp = recent.strftime("%Y%m%d")

    data_root = tmp_path / "data"
    old_main = _directory(data_root / "archive" / "runs" / old.strftime("%Y") / f"{old_stamp}T010101_test")
    latest_main = _directory(data_root / "archive" / "runs" / recent.strftime("%Y") / f"{recent_stamp}T010101_test")
    old_youtube = _directory(data_root / "archive" / "youtube-archive" / "runs" / old.strftime("%Y") / f"youtube_{old_stamp}_010101")
    old_prism = _directory(data_root / "prism-telegram-archive" / "runs" / old.strftime("%Y") / f"prism_telegram_{old_stamp}_010101")
    latest_manifest = data_root / "archive" / "latest-run.json"
    latest_manifest.parent.mkdir(parents=True, exist_ok=True)
    latest_manifest.write_text(json.dumps({"run_id": latest_main.name}), encoding="utf-8")

    runner_root = tmp_path / "runner"
    workspace = runner_root / "_work" / "TradingAgents" / "TradingAgents"
    runner_site = _directory(workspace / "site-123", modified=old)
    unknown_workspace = _directory(workspace / "user-notes", modified=old)
    old_diagnostic = runner_root / "_diag" / "Worker_old.log"
    old_diagnostic.parent.mkdir(parents=True, exist_ok=True)
    old_diagnostic.write_text("old", encoding="utf-8")
    os.utime(old_diagnostic, (old.timestamp(), old.timestamp()))
    update_staging = _directory(runner_root / "_work" / "_update", modified=old)
    old_bin_backup = _directory(runner_root / "bin.1.0.0", modified=old)
    old_externals_backup = _directory(runner_root / "externals.1.0.0", modified=old)
    current_bin_backup = _directory(runner_root / "bin.2.0.0", modified=recent)
    current_externals_backup = _directory(runner_root / "externals.2.0.0", modified=recent)
    old_installer = runner_root / "actions-runner-win-x64-1.0.0.zip"
    old_installer.write_text("old", encoding="utf-8")
    os.utime(old_installer, (old.timestamp(), old.timestamp()))

    repository_root = tmp_path / "repository"
    local_site = _directory(repository_root / "site", modified=old)
    generated_runtime = _directory(repository_root / ".runtime" / "public-account-verify-old", modified=old)
    preserved_runtime = _directory(repository_root / ".runtime" / "chatgpt-work", modified=old)
    old_attachment = _directory(repository_root / ".codex-remote-attachments" / "run-123", modified=old)
    recent_attachment = _directory(repository_root / ".codex-remote-attachments" / "run-456", modified=recent)

    dry_run = _run_maintenance(tmp_path, apply=False)
    assert dry_run.returncode == 0, dry_run.stderr
    for path in (old_main, old_youtube, old_prism, runner_site, local_site, generated_runtime, old_attachment, update_staging, old_bin_backup, old_externals_backup, old_installer):
        assert path.exists()

    result = _run_maintenance(tmp_path, apply=True)
    assert result.returncode == 0, result.stderr
    for path in (old_main, old_youtube, old_prism, runner_site, local_site, generated_runtime, old_attachment, update_staging, old_bin_backup, old_externals_backup, old_installer):
        assert not path.exists()
    for path in (latest_main, unknown_workspace, preserved_runtime, recent_attachment, current_bin_backup, current_externals_backup):
        assert path.exists()
    assert not old_diagnostic.exists()
    assert (tmp_path / "maintenance.log").is_file()
