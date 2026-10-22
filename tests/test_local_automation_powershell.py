"""Exercise the installed wrapper's native-process boundary on Windows PowerShell."""

import shutil
import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.skipif(not shutil.which("powershell.exe"), reason="Windows PowerShell required")
@pytest.mark.parametrize("no_start", [True, False])
def test_research_task_registration_preserves_existing_windows_tasks(tmp_path, no_start):
    install = Path(__file__).parents[1] / "tools/install_paper_research_task.ps1"
    for filename in ("run_local_automation.ps1", "run_powershell_hidden.vbs"):
        (tmp_path / filename).write_text("fixture")
    def quote(value):
        return "'" + str(value).replace("'", "''") + "'"
    probe = tmp_path / "register.ps1"
    probe.write_text(r'''
$ErrorActionPreference='Stop'
$global:registered=@()
$global:started=@()
function New-ScheduledTaskPrincipal { param($UserId,$LogonType,$RunLevel) return @{LogonType=$LogonType} }
function New-ScheduledTaskAction { param($Execute,$Argument) return @{Execute=$Execute;Argument=$Argument} }
function New-ScheduledTaskTrigger { param([switch]$Once,$At,$RepetitionInterval) return @{Interval=$RepetitionInterval.TotalMinutes} }
function New-ScheduledTaskSettingsSet {
    param($MultipleInstances,[switch]$StartWhenAvailable,[switch]$AllowStartIfOnBatteries,
        [switch]$DontStopIfGoingOnBatteries,[switch]$Hidden,$ExecutionTimeLimit)
    return @{Instances=$MultipleInstances;Hidden=[bool]$Hidden;Hours=$ExecutionTimeLimit.TotalHours}
}
function Register-ScheduledTask {
    param($TaskPath,$TaskName,$Action,$Trigger,$Principal,$Settings,[switch]$Force)
    $global:registered+=@{TaskPath=$TaskPath;TaskName=$TaskName;Action=$Action;Trigger=$Trigger;Settings=$Settings}
}
function Start-ScheduledTask { param($TaskPath,$TaskName) $global:started+=$TaskName }
function Disable-ScheduledTask { throw 'Existing task must be preserved' }
function Unregister-ScheduledTask { throw 'Existing task must be preserved' }
''' + f"\n& {quote(install)} -InstallRoot {quote(tmp_path)} -RepositoryRoot {quote(tmp_path / 'repo')}" + (" -NoStart" if no_start else "")
        + "\n@{registered=@($global:registered);started=@($global:started)} | ConvertTo-Json -Depth 8 -Compress\n")
    result = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-File", str(probe)],
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr
    row = json.loads(result.stdout)
    assert len(row["registered"]) == 1
    task = row["registered"][0]
    assert task["TaskName"] == "LocalAutomation-research-kis"
    assert "-Command research-kis" in task["Action"]["Argument"]
    assert task["Settings"] == {"Instances": "IgnoreNew", "Hidden": True, "Hours": 13}
    assert task["Trigger"]["Interval"] == 5
    assert row["started"] == ([] if no_start else ["LocalAutomation-research-kis"])
    marker = json.loads((tmp_path / "repo/.runtime/local-automation/research-lane-enabled.json").read_text(encoding="utf-8-sig"))
    assert marker["enabled"] is True and marker["real_orders_enabled"] is False


@pytest.mark.skipif(not shutil.which("powershell.exe"), reason="Windows PowerShell required")
@pytest.mark.parametrize("case", ["fresh", "expired", "future", "invalid", "changed", "missing_ref", "fetch_failed"])
def test_shared_source_fetch_receipt_is_bounded_and_fails_closed(tmp_path, case):
    wrapper = (Path(__file__).parents[1] / "tools/run_local_automation.ps1").read_text()
    function = wrapper.split("# Never change the user's checkout", 1)[0].split("function Resolve-LocalAutomationSourceRevision", 1)[1]
    function = "function Resolve-LocalAutomationSourceRevision" + function
    root = "'" + str(tmp_path).replace("'", "''") + "'"
    probe = tmp_path / "probe.ps1"
    probe.write_text("$ErrorActionPreference='Stop'\n" + function + f"\n$root={root}\n$case='{case}'\n" + r'''
$script:fetches=0
$script:reads=0
$script:fixtureHead='a'*40
function git {
    $global:LASTEXITCODE=0
    if ($args[0] -eq 'fetch') {
        $script:fetches++
        if ($case -eq 'fetch_failed') { $global:LASTEXITCODE=1 }
        return
    }
    $script:reads++
    if ($case -eq 'missing_ref' -and $script:reads -eq 1) { throw 'missing ref' }
    return $script:fixtureHead
}
$age=if ($case -eq 'expired') { -61 } elseif ($case -eq 'future') { 61 } else { -1 }
$revision=if ($case -eq 'changed') { 'b'*40 } else { $script:fixtureHead }
$receipt=Join-Path $root 'source-fetch.json'
if ($case -notin @('missing_ref','fetch_failed')) {
    @{revision=$revision;checked_at=[DateTimeOffset]::UtcNow.AddSeconds($age).ToString('o')} |
        ConvertTo-Json | Set-Content -LiteralPath $receipt
}
if ($case -eq 'invalid') { Set-Content -LiteralPath $receipt -Value 'broken' }
$failed=$false
try { $resolved=Resolve-LocalAutomationSourceRevision -StateRoot $root } catch { $failed=$true }
@{fetches=$script:fetches;failed=$failed;resolved=$resolved} | ConvertTo-Json -Compress
''')
    result = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-File", str(probe)],
                            capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stderr
    row = json.loads(result.stdout)
    assert row["fetches"] == (0 if case == "fresh" else 1)
    assert row["failed"] is (case == "fetch_failed")
    if case != "fetch_failed":
        assert row["resolved"] == "a" * 40


@pytest.mark.skipif(not shutil.which("powershell.exe"), reason="Windows PowerShell required")
@pytest.mark.parametrize("exit_code", [0, 7])
def test_stderr_does_not_interrupt_worker_but_exit_failure_is_preserved(tmp_path, exit_code):
    wrapper = (Path(__file__).parents[1] / "tools/run_local_automation.ps1").read_text()
    boundary = wrapper.split("    if ($DryRun)", 1)[1].split("    # End worker process boundary.", 1)[0]
    boundary = "if ($DryRun)" + boundary
    worker = tmp_path / "worker.py"
    marker = tmp_path / "completed.txt"
    worker.write_text(
        "import sys, time\nfrom pathlib import Path\n"
        "print('recoverable warning', file=sys.stderr, flush=True)\n"
        "time.sleep(0.3)\n"
        f"Path({str(marker)!r}).write_text('completed')\n"
        f"sys.exit({exit_code})\n"
    )
    def quote(value):
        return "'" + str(value).replace("'", "''") + "'"
    probe = tmp_path / "probe.ps1"
    probe.write_text(
        "$ErrorActionPreference = 'Stop'\n"
        f"$pythonPath = {quote(sys.executable)}\n"
        f"$arguments = @({quote(worker)})\n"
        f"$logPath = {quote(tmp_path / 'worker.log')}\n"
        "$Command = 'run-due'\n$DryRun = $false\n"
        "try {\n" + boundary + "\nWrite-Output 'WRAPPER_OK'\n} catch {\n"
        "Write-Output ('WRAPPER_ERROR:' + $_.Exception.Message)\n}\n"
        "Write-Output ('PREFERENCE:' + $ErrorActionPreference)\n"
        "Write-Output ('PYTHON_INVOKED:' + $pythonInvoked)\n"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-File", str(probe)],
        capture_output=True, text=True, timeout=20,
    )
    assert marker.read_text() == "completed"
    assert "recoverable warning" in (tmp_path / "worker.log").read_text(encoding="utf-16")
    assert "PREFERENCE:Stop" in result.stdout
    assert "PYTHON_INVOKED:True" in result.stdout
    if exit_code:
        assert "WRAPPER_ERROR:Local run-due failed." in result.stdout
        assert "WRAPPER_OK" not in result.stdout
    else:
        assert "WRAPPER_OK" in result.stdout


@pytest.mark.skipif(not shutil.which("powershell.exe"), reason="Windows PowerShell required")
@pytest.mark.parametrize("failure", ["bad_executable", "log_is_directory"])
def test_native_launch_failure_is_distinct_from_python_failure(tmp_path, failure):
    wrapper = (Path(__file__).parents[1] / "tools/run_local_automation.ps1").read_text()
    boundary = "if ($DryRun)" + wrapper.split("    if ($DryRun)", 1)[1].split("    # End worker process boundary.", 1)[0]
    executable = Path(sys.executable)
    log = tmp_path / "worker.log"
    if failure == "bad_executable":
        executable = tmp_path / "broken.exe"
        executable.write_text("not an executable")
    else:
        log.mkdir()
    def quote(value):
        return "'" + str(value).replace("'", "''") + "'"
    probe = tmp_path / "probe.ps1"
    probe.write_text("$ErrorActionPreference='Stop'\n"
                     f"$pythonPath={quote(executable)}\n$logPath={quote(log)}\n"
                     "$arguments=@('-c','pass')\n$Command='run-due'\n$DryRun=$false\n"
                     "try {\n" + boundary + "\n} catch {Write-Output 'LAUNCH_ERROR'}\n"
                     "Write-Output ('PYTHON_INVOKED:' + $pythonInvoked)\n")
    result = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-File", str(probe)],
                            capture_output=True, text=True, timeout=20)
    assert "LAUNCH_ERROR" in result.stdout
    assert "PYTHON_INVOKED:False" in result.stdout
