from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).parents[1]


def test_runner_keepalive_uses_service_then_current_user_fallback() -> None:
    script = (ROOT / "tools" / "ensure_actions_runner.ps1").read_text(
        encoding="utf-8"
    )

    assert "Runner.Listener.exe" in script
    assert "Start-Service" in script
    assert "Start-Process" in script
    assert "TradingAgentsActionsRunnerKeepAlive" in script
    assert "-WindowStyle Hidden" in script


def test_runner_keepalive_installer_is_recurring_and_least_privilege() -> None:
    script = (ROOT / "tools" / "install_actions_runner_keepalive.ps1").read_text(
        encoding="utf-8"
    )

    assert "<LogonTrigger>" in script
    assert "<Interval>$interval</Interval>" in script
    assert "<RunLevel>LeastPrivilege</RunLevel>" in script
    assert "Register-ScheduledTask" in script
    assert "Copy-Item" in script


@pytest.mark.parametrize("status", ["Running", "StartPending"])
def test_invisible_service_listener_never_launches_a_duplicate(status):
    pwsh = shutil.which("pwsh")
    if not pwsh:
        pytest.skip("PowerShell runtime unavailable")
    source = str(ROOT / "tools" / "ensure_actions_runner.ps1").replace("'", "''")
    code = f"""
    function Test-Path {{ param($LiteralPath,$PathType) return $true }}
    function Get-CimInstance {{ param($Filter) return [pscustomobject]@{{ExecutablePath=$null}} }}
    function Get-Content {{ param($LiteralPath,[switch]$Raw) return 'test-service' }}
    function Get-Service {{ param($Name) return [pscustomobject]@{{Status=[ServiceProcess.ServiceControllerStatus]::{status}} }}
    function Start-Service {{ throw 'Unexpected service start' }}
    function Start-Process {{ throw 'Duplicate runner launched' }}
    & '{source}' -RunnerRoot C:\\actions-runner
    """
    result = subprocess.run([pwsh, "-NoProfile", "-Command", code], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert ("HEALTHY runner service is active" if status == "Running"
            else "DEFERRED runner service owns startup") in result.stdout
