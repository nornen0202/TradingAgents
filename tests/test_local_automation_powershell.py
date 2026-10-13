"""Exercise the installed wrapper's native-process boundary on Windows PowerShell."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest


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
