"""Exercise the installed entrypoint contract with Windows PowerShell 5.1.

All external programs are local test executables; no GitHub or Telegram calls.
"""
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from tradingagents.atomic_io import interprocess_file_lock
from tradingagents.notifications import local

POWERSHELL = shutil.which("powershell.exe")
pytestmark = pytest.mark.skipif(os.name != "nt" or not POWERSHELL, reason="Windows PowerShell 5.1 contract")
ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "tools/local_automation_launcher_notifications.ps1"
WRAPPER = ROOT / "tools/run_local_automation.ps1"
OBSERVED = "2026-10-12T08:00:00+00:00"


def ps(script, env):
    return subprocess.run([POWERSHELL, "-NoProfile", "-NonInteractive", "-Command", script],
                          env=env, capture_output=True, text=True, timeout=45)


class Sandbox(tuple):
    def __repr__(self):
        return "<isolated launcher fixture; environment redacted>"


@pytest.fixture
def sandbox(tmp_path):
    # Compile a tiny native gh/git stand-in because ProcessStartInfo intentionally
    # does not launch a shell or accept a command-string wrapper in production.
    fake = tmp_path / "bin"
    fake.mkdir()
    source = r'''
using System;
using System.IO;
class FakeNative {
    static int Main(string[] args) {
        var program = Path.GetFileNameWithoutExtension(Environment.GetCommandLineArgs()[0]);
        File.AppendAllText(Environment.GetEnvironmentVariable("TA_TEST_CALLS"), program + " " + String.Join(" ", args) + "\n");
        Console.Error.WriteLine("private-fixture-diagnostic-must-not-enter-outbox");
        System.Threading.Thread.Sleep(Int32.Parse(Environment.GetEnvironmentVariable("TA_TEST_SLEEP_MS") ?? "0"));
        return Int32.Parse(Environment.GetEnvironmentVariable("TA_TEST_NATIVE_EXIT") ?? "0");
    }
}
'''
    env = {**os.environ, "PATH": str(fake) + os.pathsep + os.environ["PATH"],
           "TA_TEST_CALLS": str(tmp_path / "calls.txt"), "TA_TEST_NATIVE_EXIT": "0",
           "TA_TEST_SOURCE": source, "TA_TEST_EXE": str(fake / "gh.exe"),
           "TA_TEST_STATE": str(tmp_path / "state"), "TA_TEST_HELPER": str(HELPER),
           "TA_TEST_WRAPPER": str(WRAPPER), "TA_TEST_REPO": str(tmp_path / "repo")}
    result = ps("Add-Type -TypeDefinition $env:TA_TEST_SOURCE -OutputAssembly $env:TA_TEST_EXE -OutputType ConsoleApplication", env)
    assert result.returncode == 0, result.stderr
    shutil.copyfile(fake / "gh.exe", fake / "git.exe")
    return Sandbox((tmp_path, env))


def launch(env, *, observed=OBSERVED):
    return ps("$ErrorActionPreference='Stop'; . $env:TA_TEST_HELPER; "
              "Send-LocalAutomationLauncherFailure -StateRoot $env:TA_TEST_STATE "
              f"-ErrorType LocalRuntimeUnavailable -ObservedAt '{observed}'", env)


def read_event(tmp_path):
    path, = (tmp_path / "state/notifications/events").glob("*.json")
    event = local.read(path)
    assert local.event_id(event) == path.stem
    return event, path.stem


def test_powershell_outbox_hash_first_time_and_one_bootstrap(sandbox):
    tmp_path, env = sandbox
    for observed in [OBSERVED, "2026-10-12T09:00:00+00:00"]:
        result = launch(env, observed=observed)
        assert result.returncode == 0, result.stderr
    event, key = read_event(tmp_path)
    assert local.timestamp(event["finished_at"]) == local.timestamp(OBSERVED)
    assert event["source_key"] == "launcher:2026-10-12"
    receipt = local.read(tmp_path / "state/notifications/dispatches" / f"{key}.json")
    assert receipt["status"] == "DISPATCH_ACCEPTED" and receipt["attempts"] == 1
    calls = (tmp_path / "calls.txt").read_text().splitlines()
    assert len(calls) == 1 and f"local_event_id={key}" in calls[0]
    assert "private-fixture" not in json.dumps([event, receipt])
    # The fallback failure notifier works with stdlib only, without the venv's
    # installed project dependencies and without loading Telegram credentials.
    result = subprocess.run([sys.executable, "-S", "-m", "tradingagents.notifications", "notify-local",
                             "--local-event-id", key, "--archive-dir", str(tmp_path),
                             "--state-dir", str(tmp_path / "state"), "--dry-run"],
                            capture_output=True, text=True, cwd=ROOT, timeout=10)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "DRY_RUN"


def test_failed_bootstrap_uses_existing_cumulative_retry_budget(sandbox):
    tmp_path, env = sandbox
    env["TA_TEST_NATIVE_EXIT"] = "1"
    assert launch(env).returncode == 0
    assert launch(env).returncode == 0
    _, key = read_event(tmp_path)
    state = tmp_path / "state"
    receipt = state / "notifications/dispatches" / f"{key}.json"
    assert local.read(receipt)["status"] == "DISPATCH_FAILED"
    assert len((tmp_path / "calls.txt").read_text().splitlines()) == 1
    calls = []
    def runner(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(returncode=1, stdout="[]")
    now = datetime.fromisoformat(OBSERVED)
    for minutes in (16, 32, 48):
        local.reconcile(state, now=now + timedelta(minutes=minutes), runner=runner)
    assert sum(c[1] == "workflow" for c in calls) == 2
    assert local.read(receipt)["attempts"] == 3


def test_python_dispatch_lock_retains_event_without_competing_dispatch(sandbox):
    tmp_path, env = sandbox
    lock = tmp_path / "state/notifications/dispatch.lock"
    with interprocess_file_lock(lock, timeout=0):
        result = launch(env)
        assert result.returncode == 0, result.stderr
        read_event(tmp_path)
        assert not (tmp_path / "calls.txt").exists()
    assert launch(env).returncode == 0
    assert len((tmp_path / "calls.txt").read_text().splitlines()) == 1


def test_real_wrapper_captures_missing_python_without_fetching(sandbox):
    tmp_path, env = sandbox
    result = ps("& $env:TA_TEST_WRAPPER -Command run-due -RepositoryRoot $env:TA_TEST_REPO", env)
    assert result.returncode != 0
    state = Path(env["TA_TEST_REPO"]) / ".runtime/local-automation"
    event_path, = (state / "notifications/events").glob("*.json")
    event = local.read(event_path)
    assert event["stage"] == "launcher" and event["error_type"] == "LocalRuntimeUnavailable"
    assert local.event_id(event) == event_path.stem
    assert (tmp_path / "calls.txt").read_text().startswith("gh workflow run ")


def test_wrapper_dry_run_does_not_queue_or_dispatch(sandbox):
    tmp_path, env = sandbox
    result = ps("& $env:TA_TEST_WRAPPER -Command publish -RepositoryRoot $env:TA_TEST_REPO -DryRun", env)
    assert result.returncode != 0
    assert not (Path(env["TA_TEST_REPO"]) / ".runtime").exists()
    assert not (tmp_path / "calls.txt").exists()


def test_real_wrapper_captures_fetch_failure_before_python(sandbox):
    tmp_path, env = sandbox
    repo = Path(env["TA_TEST_REPO"])
    python = repo / ".venv/Scripts/python.exe"
    python.parent.mkdir(parents=True)
    python.write_text("never executed")
    env["TA_TEST_NATIVE_EXIT"] = "1"
    result = ps("& $env:TA_TEST_WRAPPER -Command publish -RepositoryRoot $env:TA_TEST_REPO", env)
    assert result.returncode != 0
    path, = (repo / ".runtime/local-automation/notifications/events").glob("*.json")
    assert local.read(path)["error_type"] == "SourceFetchFailed"
    calls = (tmp_path / "calls.txt").read_text().splitlines()
    assert calls[0] == "git fetch fork main --quiet" and calls[1].startswith("gh workflow run ")


def test_atomic_script_update_does_not_touch_schedule_or_runtime(sandbox):
    tmp_path, env = sandbox
    install = tmp_path / 'maintenance'
    install.mkdir()
    (install / WRAPPER.name).write_text('old script')
    env['TA_TEST_INSTALL'] = str(install)
    env['TA_TEST_INSTALLER'] = str(ROOT / 'tools/install_local_automation.ps1')
    result = ps('& $env:TA_TEST_INSTALLER -RepositoryRoot $env:TA_TEST_REPO '
                '-InstallRoot $env:TA_TEST_INSTALL -UpdateScriptsOnly', env)
    assert result.returncode == 0, result.stderr
    for source in [HELPER, WRAPPER]:
        assert (install / source.name).read_bytes() == source.read_bytes()
    assert not (Path(env['TA_TEST_REPO']) / '.runtime').exists()
    assert not (tmp_path / 'calls.txt').exists()
    assert not list(install.glob('*.tmp'))


@pytest.mark.parametrize('runtime', ['missing', 'invalid', 'failed', 'timeout', 'usable'])
def test_workflow_runtime_probe_falls_back_on_launch_error_or_timeout(sandbox, runtime):
    tmp_path, env = sandbox
    workflow = yaml.safe_load((ROOT / '.github/workflows/tradingagents-mobile-notifications.yml').read_text())
    step = next(step for step in workflow['jobs']['notify_local']['steps'] if step.get('id') == 'local_python')
    executable = tmp_path / 'missing.exe'
    if runtime == 'invalid':
        executable.write_text('not an executable')
    elif runtime in {'failed', 'timeout'}:
        executable = tmp_path / 'bin/gh.exe'
        env['TA_TEST_NATIVE_EXIT'] = '1' if runtime == 'failed' else '0'
        if runtime == 'timeout':
            env['TA_TEST_SLEEP_MS'] = '30000'
    elif runtime == 'usable':
        executable = Path(sys.executable)
    env['TA_TEST_PYTHON'] = str(executable)
    output = tmp_path / 'github-output.txt'
    env['GITHUB_OUTPUT'] = str(output)
    script = step['run'].replace("'C:/Projects/TradingAgents/.venv/Scripts/python.exe'", '$env:TA_TEST_PYTHON')
    started = time.monotonic()
    # A previous native command's success must never mark an unstarted probe usable.
    result = ps('$ErrorActionPreference="Stop"; $global:LASTEXITCODE=0; ' + script, env)
    assert result.returncode == 0, result.stderr
    assert output.read_text(encoding='utf-16').strip() == f"unavailable={str(runtime != 'usable').lower()}"
    assert 'private-fixture' not in result.stdout + result.stderr
    if runtime == 'timeout':
        assert time.monotonic() - started < 25
