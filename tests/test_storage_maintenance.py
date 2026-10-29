from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ET

import pytest


PWSH = shutil.which("pwsh") or shutil.which("pwsh.exe")
SCRIPT = Path(__file__).parents[1] / "tools" / "maintain_project_storage.ps1"


@pytest.mark.skipif(os.name != 'nt' or PWSH is None, reason='Windows PowerShell required')
def test_maintenance_refuses_nested_junction_without_touching_external_data(tmp_path):
    outside = _directory(tmp_path / 'external')
    stale = _directory(tmp_path / 'runner' / '_work' / 'TradingAgents' / 'TradingAgents' / 'site-123')
    result = subprocess.run(
        [PWSH, '-NoProfile', '-NonInteractive', '-Command',
         'New-Item -ItemType Junction -Path $env:TEST_LINK -Target $env:TEST_TARGET | Out-Null'],
        env={**os.environ, 'TEST_LINK': str(stale / 'linked'), 'TEST_TARGET': str(outside)},
        capture_output=True, text=True, encoding="utf-8", timeout=30,
    )
    assert result.returncode == 0, result.stderr
    result = _run_maintenance(tmp_path, apply=True)
    assert result.returncode != 0
    assert 'reparse point' in result.stderr
    assert (outside / 'payload.txt').read_text() == 'generated'


def _directory(path: Path, *, modified: datetime | None = None) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    (path / "payload.txt").write_text("generated", encoding="utf-8")
    if modified is not None:
        timestamp = modified.timestamp()
        os.utime(path / "payload.txt", (timestamp, timestamp))
        os.utime(path, (timestamp, timestamp))
    return path


def _maintenance_invocation(tmp_path: Path, *, apply: bool, extended_policy=None):
    # These fixtures model an idle temporary runner, regardless of unrelated
    # production Runner.Worker processes on the machine running the tests.
    wrapper = tmp_path / "maintenance-test-wrapper.ps1"
    wrapper.write_text(
        "function Get-Process { [CmdletBinding()] param([string[]] $Name)\n"
        "  if ($Name -contains 'Runner.Worker') { return @() }\n"
        "  Microsoft.PowerShell.Management\\Get-Process -Name $Name -ErrorAction SilentlyContinue\n"
        "}\n& $env:TEST_MAINTENANCE_SCRIPT @args\nexit $LASTEXITCODE\n",
        encoding="utf-8",
    )
    # A real host maintenance owner must neither block these temporary fixtures
    # nor be disturbed by them. Only the test copy receives a distinct mutex.
    isolated = tmp_path / "maintenance-scripts"
    isolated.mkdir(exist_ok=True)
    test_script = isolated / SCRIPT.name
    test_script.write_text(
        SCRIPT.read_text(encoding="utf-8").replace(
            "Local\\TradingAgentsStorageMaintenance",
            "Local\\TradingAgentsStorageTest-" + uuid.uuid4().hex,
        ), encoding="utf-8",
    )
    for helper in ("maintain_codex_storage.py", "maintain_codex_storage_policy.py"):
        shutil.copyfile(SCRIPT.parent / helper, isolated / helper)
    command = [
        PWSH,
        "-NoLogo",
        "-NoProfile",
        "-File",
        str(wrapper),
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
    if extended_policy is not None:
        command += ["-ExtendedPolicyPath", str(extended_policy)]
    return command, {**os.environ, "TEST_MAINTENANCE_SCRIPT": str(test_script)}


def _run_maintenance(tmp_path: Path, *, apply: bool, extended_policy=None) -> subprocess.CompletedProcess[str]:
    command, environment = _maintenance_invocation(tmp_path, apply=apply, extended_policy=extended_policy)
    return subprocess.run(command, check=False, capture_output=True, text=True, encoding="utf-8",
                          env=environment, timeout=60)


@pytest.mark.skipif(os.name != "nt" or PWSH is None, reason="Windows PowerShell required")
@pytest.mark.parametrize("helper_exit", [0, 7])
def test_helper_progress_is_persisted_before_exit_and_failure_propagates(tmp_path, helper_exit):
    (tmp_path / "runner").mkdir()
    config = tmp_path / "policy.json"
    config.write_text(json.dumps({"enabled": True, "python_executable": sys.executable,
                                  "preserve_canonical_archive": True}), encoding="utf-8")
    command, environment = _maintenance_invocation(tmp_path, apply=True, extended_policy=config)
    release = tmp_path / "release-helper"
    (tmp_path / "maintenance-scripts" / "maintain_codex_storage_policy.py").write_text(
        "import os, sys, time\nfrom pathlib import Path\n"
        "if '--preflight-only' in sys.argv:\n print('preflight-ready', flush=True); sys.exit(0)\n"
        "print('verified-copy-progress', flush=True)\n"
        "deadline = time.monotonic() + 40\n"
        "while not Path(os.environ['TEST_RELEASE']).exists():\n"
        " if time.monotonic() > deadline: sys.exit(99)\n time.sleep(0.05)\n"
        "print('helper-finished', flush=True)\n"
        "sys.exit(int(os.environ['TEST_HELPER_EXIT']))\n", encoding="utf-8",
    )
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, encoding="utf-8", env={**environment,
                               "TEST_RELEASE": str(release), "TEST_HELPER_EXIT": str(helper_exit)})
    log = tmp_path / "maintenance.log"
    try:
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if log.exists() and "CODEX_STORAGE verified-copy-progress" in log.read_text(encoding="utf-8-sig"):
                break
            if process.poll() is not None:
                pytest.fail("Helper exited before its externally released completion")
            time.sleep(0.05)
        assert process.poll() is None
        assert "CODEX_STORAGE verified-copy-progress" in log.read_text(encoding="utf-8-sig")
    finally:
        release.touch()
        stdout, stderr = process.communicate(timeout=30)
    assert "SUMMARY" in stdout
    assert "helper-finished" in log.read_text(encoding="utf-8-sig")
    if helper_exit:
        assert process.returncode != 0
        assert "returned 7" in stderr
    else:
        assert process.returncode == 0, stderr


@pytest.mark.skipif(os.name != "nt" or PWSH is None, reason="Windows PowerShell required")
def test_installer_keeps_scheduler_owner_until_guarded_maintenance_finishes(tmp_path):
    captured = tmp_path / "registered-task.xml"
    wrapper = tmp_path / "install-wrapper.ps1"
    wrapper.write_text(
        "function Register-ScheduledTask { param($TaskPath, $TaskName, $Xml, [switch]$Force)\n"
        " [IO.File]::WriteAllText($env:TEST_CAPTURE_XML, $Xml)\n}\n"
        "& $env:TEST_INSTALL_SCRIPT -InstallRoot $env:TEST_INSTALL_ROOT\n", encoding="utf-8",
    )
    result = subprocess.run([PWSH, "-NoProfile", "-NonInteractive", "-File", str(wrapper)],
                            capture_output=True, text=True, encoding="utf-8", timeout=30,
                            env={**os.environ, "TEST_CAPTURE_XML": str(captured),
                                 "TEST_INSTALL_SCRIPT": str(SCRIPT.with_name("install_storage_maintenance.ps1")),
                                 "TEST_INSTALL_ROOT": str(tmp_path / "installed")})
    assert result.returncode == 0, result.stderr
    root = ET.fromstring(captured.read_text(encoding="utf-8"))
    ns = {"t": "http://schemas.microsoft.com/windows/2004/02/mit/task"}
    assert root.findtext("t:Settings/t:ExecutionTimeLimit", namespaces=ns) == "PT0S"
    assert root.findtext("t:Settings/t:MultipleInstancesPolicy", namespaces=ns) == "IgnoreNew"
    assert root.findtext("t:Principals/t:Principal/t:RunLevel", namespaces=ns) == "LeastPrivilege"
    assert root.findtext("t:Triggers/t:CalendarTrigger/t:ScheduleByDay/t:DaysInterval", namespaces=ns) == "1"


@pytest.mark.skipif(os.name != "nt" or PWSH is None, reason="Windows PowerShell required")
def test_referenced_canonical_history_is_preserved_while_other_retention_runs(tmp_path):
    old = datetime.now() - timedelta(days=40)
    stamp = old.strftime("%Y%m%d")
    main = _directory(tmp_path / "data" / "archive" / "runs" / str(old.year) / f"{stamp}T010101_old")
    youtube = _directory(tmp_path / "data" / "archive" / "youtube-archive" / "runs" / str(old.year) / f"youtube_{stamp}_010101")
    prism = _directory(tmp_path / "data" / "prism-telegram-archive" / "runs" / str(old.year) / f"prism_telegram_{stamp}_010101")
    config = tmp_path / "policy.json"
    config.write_text(json.dumps({"enabled": False, "python_executable": sys.executable,
                                  "preserve_canonical_archive": True}), encoding="utf-8")
    (tmp_path / "runner").mkdir()
    diagnostic = tmp_path / "runner" / "_diag" / "Worker_old.log"
    diagnostic.parent.mkdir()
    diagnostic.write_text("old diagnostic")
    os.utime(diagnostic, (old.timestamp(), old.timestamp()))
    result = _run_maintenance(tmp_path, apply=True, extended_policy=config)
    assert result.returncode == 0, result.stderr
    assert (main / "payload.txt").read_text() == "generated"
    assert (youtube / "payload.txt").read_text() == "generated"
    assert (prism / "payload.txt").read_text() == "generated"
    assert not diagnostic.exists()
    assert "PRESERVED root=" in result.stdout


@pytest.mark.skipif(os.name != "nt" or PWSH is None, reason="Windows PowerShell required")
def test_invalid_policy_preserves_old_history_before_any_cleanup(tmp_path):
    old = datetime.now() - timedelta(days=40)
    main = _directory(tmp_path / "data" / "archive" / "runs" / str(old.year) / f"{old:%Y%m%d}T010101_old")
    config = tmp_path / "invalid-policy.json"
    config.write_text("{malformed")
    result = _run_maintenance(tmp_path, apply=True, extended_policy=config)
    assert result.returncode != 0
    assert (main / "payload.txt").read_text() == "generated"


@pytest.mark.skipif(os.name != "nt" or PWSH is None, reason="Windows PowerShell required")
def test_relocation_mismatch_blocks_wrapper_cleanup_before_mutation(tmp_path):
    old = datetime.now() - timedelta(days=40)
    main = _directory(tmp_path / "data" / "archive" / "runs" / str(old.year) / f"{old:%Y%m%d}T010101_old")
    source = _directory(tmp_path / "recreated-source")
    destination = _directory(tmp_path / "offloaded")
    diagnostic = tmp_path / "runner" / "_diag" / "Worker_old.log"
    diagnostic.parent.mkdir(parents=True)
    diagnostic.write_text("old diagnostic")
    os.utime(diagnostic, (old.timestamp(), old.timestamp()))
    config = tmp_path / "policy.json"
    config.write_text(json.dumps({"enabled": True, "python_executable": sys.executable,
                                  "relocations": [{"id": "saved", "source": str(source), "destination": str(destination)}]}))
    result = _run_maintenance(tmp_path, apply=True, extended_policy=config)
    assert result.returncode != 0
    assert "cleanup was not started" in result.stderr
    assert (main / "payload.txt").read_text() == "generated"
    assert diagnostic.read_text() == "old diagnostic"
    assert (source / "payload.txt").exists() and (destination / "payload.txt").exists()


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
