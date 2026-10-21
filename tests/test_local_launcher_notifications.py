"""Exercise the installed entrypoint contract with Windows PowerShell 5.1.

All external programs are local test executables; no GitHub or Telegram calls.
"""
import hashlib
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
HIDDEN_LAUNCHER = ROOT / "tools/run_powershell_hidden.vbs"
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
    assert calls[:2] == ["git rev-parse fork/main", "git fetch fork main --quiet"]
    assert calls[2].startswith("gh workflow run ")


def test_concurrent_launchers_share_new_main_revision_without_fetch_race(sandbox):
    tmp_path, env = sandbox
    # Use real local Git repositories and a harmless worker; no remote service,
    # account configuration, publication, or notification is contacted.
    env["PATH"] = os.environ["PATH"]
    remote, writer = tmp_path / "remote.git", tmp_path / "writer"
    repo = Path(env["TA_TEST_REPO"])
    def git(*args, cwd=None):
        result = subprocess.run(["git", *map(str, args)], cwd=cwd, env=env,
                                capture_output=True, text=True, timeout=15)
        assert result.returncode == 0, result.stderr
        return result.stdout.strip()
    git("init", "--bare", remote)
    git("init", "-b", "main", writer)
    git("config", "user.name", "Isolated Fixture", cwd=writer)
    git("config", "user.email", "fixture@example.invalid", cwd=writer)
    (writer / "tracked.txt").write_text("base")
    git("add", ".", cwd=writer)
    git("commit", "-qm", "base", cwd=writer)
    git("remote", "add", "fork", remote, cwd=writer)
    git("push", "-q", "fork", "main", cwd=writer)
    git("clone", "-q", "-b", "main", "--origin", "fork", remote, repo)
    python = repo / ".venv/Scripts/python.exe"
    python.parent.mkdir(parents=True)
    results = tmp_path / "worker-results"
    results.mkdir()
    env["TA_TEST_RESULTS"] = str(results)
    env["TA_TEST_EXE"] = str(python)
    env["TA_TEST_SOURCE"] = r'''
using System;
using System.IO;
class Worker {
    static int Main(string[] args) {
        File.WriteAllText(Path.Combine(Environment.GetEnvironmentVariable("TA_TEST_RESULTS"), args[3]),
                          Environment.GetEnvironmentVariable("TRADINGAGENTS_SOURCE_SHA"));
        return 0;
    }
}
'''
    compiled = ps("Add-Type -TypeDefinition $env:TA_TEST_SOURCE -OutputAssembly $env:TA_TEST_EXE -OutputType ConsoleApplication", env)
    assert compiled.returncode == 0, compiled.stderr
    for iteration in range(3):
        # Each iteration represents the next cache period. Workers within the
        # period deliberately share a single fetch under the repository mutex.
        receipt = repo / ".runtime/local-automation/source-fetch.json"
        if receipt.exists():
            saved = json.loads(receipt.read_text(encoding="utf-8-sig"))
            saved["checked_at"] = "2020-01-01T00:00:00Z"
            receipt.write_text(json.dumps(saved))
        (writer / "tracked.txt").write_text(str(iteration))
        git("commit", "-qam", f"new main {iteration}", cwd=writer)
        git("push", "-q", "fork", "main", cwd=writer)
        expected = git("rev-parse", "HEAD", cwd=writer)
        workers = [subprocess.Popen(
            [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(WRAPPER),
             "-Command", command, "-RepositoryRoot", str(repo), "-DryRun"],
            env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for command in ("run-due", "publish")]
        for worker in workers:
            _, stderr = worker.communicate(timeout=30)
            assert worker.returncode == 0, stderr
        assert all((results / command).read_text() == expected for command in ("run-due", "publish"))
        assert (repo / f".runtime/local-automation/source/{expected}/tracked.txt").read_text() == str(iteration)
    assert not (repo / ".runtime/local-automation/notifications").exists()


def test_source_fetch_lock_wait_is_bounded_and_does_not_start_git(sandbox):
    tmp_path, env = sandbox
    repo = Path(env["TA_TEST_REPO"])
    python = repo / ".venv/Scripts/python.exe"
    python.parent.mkdir(parents=True)
    python.write_text("never executed")
    repository_key = hashlib.sha256(str(repo.resolve()).rstrip("\\/").upper().encode()).hexdigest()
    env["TA_TEST_MUTEX"] = "Local\\TradingAgentsSourceFetch-" + repository_key
    env["TA_TEST_READY"] = str(tmp_path / "mutex-ready")
    holder = subprocess.Popen(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-Command",
         "$m=[Threading.Mutex]::new($false,$env:TA_TEST_MUTEX); "
         "$null=$m.WaitOne(); try { [IO.File]::WriteAllText($env:TA_TEST_READY,'ready'); "
         "$null=[Console]::ReadLine() } finally {$m.ReleaseMutex(); $m.Dispose()}"],
        env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        deadline = time.monotonic() + 10
        while not Path(env["TA_TEST_READY"]).exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        assert Path(env["TA_TEST_READY"]).exists(), "fixture mutex holder failed to start"
        # Keep the production 60-second bound but shorten only this wait in the
        # isolated fixture so the regression does not block for a full minute.
        script = WRAPPER.read_text()
        assert "$fetchMutex.WaitOne(60000)" in script
        bounded = tmp_path / WRAPPER.name
        bounded.write_text(script.replace("$fetchMutex.WaitOne(60000)", "$fetchMutex.WaitOne(200)"))
        shutil.copyfile(HELPER, tmp_path / HELPER.name)
        env["TA_TEST_WRAPPER"] = str(bounded)
        started = time.monotonic()
        result = ps("& $env:TA_TEST_WRAPPER -Command publish -RepositoryRoot $env:TA_TEST_REPO -DryRun", env)
        assert result.returncode != 0
        assert "Source refresh is still active" in result.stderr
        assert time.monotonic() - started < 10
        assert not (tmp_path / "calls.txt").exists()
    finally:
        holder.communicate("\n", timeout=10)


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
    for source in [HIDDEN_LAUNCHER, HELPER, WRAPPER]:
        assert (install / source.name).read_bytes() == source.read_bytes()
    assert not (Path(env['TA_TEST_REPO']) / '.runtime').exists()
    assert not (tmp_path / 'calls.txt').exists()
    assert not list(install.glob('*.tmp'))


def test_hidden_launcher_hides_console_preserves_arguments_and_exit(tmp_path):
    script = tmp_path / 'console probe 한글.ps1'
    result_path = tmp_path / 'result.json'
    script.write_text(r'''
param([string]$RepositoryRoot, [string]$ArchiveRoot)
Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class ConsoleProbe { [DllImport("kernel32.dll")] public static extern IntPtr GetConsoleWindow(); [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h); }'
$h = [ConsoleProbe]::GetConsoleWindow()
@{visible=[ConsoleProbe]::IsWindowVisible($h);repo=$RepositoryRoot;archive=$ArchiveRoot} | ConvertTo-Json | Set-Content -LiteralPath $env:TA_HIDDEN_RESULT -Encoding UTF8
exit 7
''', encoding='utf-8-sig')
    repo = str(tmp_path / 'repository with spaces 한글')
    archive = str(tmp_path / 'archive with spaces')
    result = subprocess.run(
        [str(Path(os.environ['SystemRoot']) / 'System32/wscript.exe'), '//B', '//Nologo',
         str(HIDDEN_LAUNCHER), str(script), '-RepositoryRoot', repo, '-ArchiveRoot', archive],
        env={**os.environ, 'TA_HIDDEN_RESULT': str(result_path)}, timeout=20,
    )
    assert result.returncode == 7
    observed = json.loads(result_path.read_text(encoding='utf-8-sig'))
    assert observed == {'visible': False, 'repo': repo, 'archive': archive}


@pytest.mark.parametrize('interval', [5, 15, 30])
def test_installer_registers_gui_launcher_without_changing_worker_arguments(tmp_path, interval):
    install = tmp_path / 'maintenance with spaces'
    repo = tmp_path / 'repo with spaces'
    archive = tmp_path / 'archive with spaces'
    receipt = tmp_path / 'actions.jsonl'
    env = {**os.environ, 'TA_INSTALLER': str(ROOT / 'tools/install_local_automation.ps1'),
           'TA_INSTALL': str(install), 'TA_REPO': str(repo), 'TA_ARCHIVE': str(archive),
           'TA_ACTIONS': str(receipt), 'TA_INTERVAL': str(interval)}
    result = ps(r'''
$ErrorActionPreference = 'Stop'
# Import before installing mocks: module autoload exports functions with these
# names and would otherwise replace the mocks when a constructor is first used.
Import-Module ScheduledTasks, Microsoft.PowerShell.Management, Microsoft.PowerShell.Utility
$PSModuleAutoLoadingPreference = 'None'
function global:Get-ScheduledTask { param($TaskPath, $ErrorAction) @() }
function global:Register-ScheduledTask {
    param($TaskPath, $TaskName, $Action, $Trigger, $Principal, $Settings, [switch]$Force)
    $triggers=@($Trigger | ForEach-Object { @{type=$_.CimClass.CimClassName;at=$_.StartBoundary;interval=$_.Repetition.Interval;delay=$_.Delay;days=$_.DaysOfWeek} })
    @{name=$TaskName;execute=$Action.Execute;arguments=$Action.Arguments;multiple=[string]$Settings.MultipleInstances;limit=$Settings.ExecutionTimeLimit;triggers=$triggers} | ConvertTo-Json -Depth 6 -Compress | Add-Content -LiteralPath $env:TA_ACTIONS -Encoding UTF8
}
$options=@{}
if($env:TA_INTERVAL -ne '5'){$options.PollIntervalMinutes=[int]$env:TA_INTERVAL}
& $env:TA_INSTALLER -RepositoryRoot $env:TA_REPO -ArchiveRoot $env:TA_ARCHIVE -InstallRoot $env:TA_INSTALL -NoStart @options
''', env)
    assert result.returncode == 0, result.stderr
    actions = [json.loads(line) for line in receipt.read_text(encoding='utf-8-sig').splitlines()]
    assert len(actions) == 2
    for action, command in zip(actions, ['run-due', 'publish']):
        assert Path(action['execute']).name.lower() == 'wscript.exe'
        assert action['arguments'] == (
            f'//B //Nologo "{install / HIDDEN_LAUNCHER.name}" "{install / WRAPPER.name}" '
            f'-Command {command} -RepositoryRoot "{repo}" -ArchiveRoot "{archive}"')
        assert action['name'] == f'LocalAutomation-{command}'
        assert action['multiple'] == 'IgnoreNew'
        assert action['limit'] == 'PT13H'
        timer, logon, *critical = action['triggers']
        assert timer['type'] == 'MSFT_TaskTimeTrigger'
        assert timer['interval'] == f'PT{interval if command == "publish" else 1}M'
        tick = datetime.fromisoformat(timer['at'])
        assert tick.minute % (interval if command == 'publish' else 1) == (2 if command == 'publish' else 0)
        assert tick.second == 0
        assert logon['type'] == 'MSFT_TaskLogonTrigger'
        assert logon['delay'] == ('PT2M' if command == 'publish' else 'PT30S')
        if command == 'run-due':
            boundary, = critical
            at = datetime.fromisoformat(boundary['at']).astimezone()
            assert (at.hour, at.minute) == (17, 50)
            assert boundary['type'] == 'MSFT_TaskWeeklyTrigger' and boundary['days'] == 62
        else:
            assert not critical


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
