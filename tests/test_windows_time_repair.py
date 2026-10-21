"""Exercise the administrative workflow with only mocked Windows services/NTP."""
from pathlib import Path
import shutil
import subprocess

import pytest


@pytest.mark.parametrize("failed_resync", [False, True])
@pytest.mark.parametrize("unsynchronized", [False, True])
def test_bounded_step_restores_threshold_and_checks_real_offset(tmp_path, failed_resync, unsynchronized):
    shell = shutil.which("powershell")
    if not shell:
        pytest.skip("Windows PowerShell required")
    source = Path("tools/repair_windows_time.ps1").read_text(encoding="utf-8")
    # The test replaces every privileged operation; production retains #Requires.
    source = source.replace("#Requires -RunAsAdministrator", "# Mocked administration")
    target = tmp_path / "repair.ps1"
    target.write_text(source, encoding="utf-8")
    bootstrap = tmp_path / "test.ps1"
    bootstrap.write_text(r'''
$global:phase = 1
$global:stepped = $false
$global:resynced = $false
function Get-CimInstance { [pscustomobject]@{ PartOfDomain = $false } }
function Set-Service { }
function Start-Service { }
function Restart-Service { }
function Start-Sleep { }
function Get-ItemProperty { [pscustomobject]@{ MaxAllowedPhaseOffset = $global:phase } }
function Set-ItemProperty {
    param($LiteralPath, $Name, $Value)
    if ($Name -eq 'MaxAllowedPhaseOffset') {
        $global:phase = $Value
        if ($Value -eq 0) { $global:stepped = $true }
    }
}
function w32tm {
    $global:LASTEXITCODE = 0
    if ($args -contains '/resync') {
        $global:resynced = $true
        if (FAIL_RESYNC) { $global:LASTEXITCODE = 1 }
    }
    if ($args -contains '/stripchart') {
        $offset = if ($global:resynced) { '+00.0200000s' } else { '+00.8000000s' }
        1..5 | ForEach-Object { "12:00:00, $offset" }
    }
    if ($args -contains '/status') { 'Leap Indicator: LEAP_VALUE(status)' }
}
$failed = $false
try { & $args[0] -StepClock } catch { $failed = $true }
if ($global:phase -ne 1 -or -not $global:stepped -or -not $global:resynced) { exit 10 }
if ($failed -ne (EXPECT_FAILURE)) { exit 11 }
'''.replace("FAIL_RESYNC", "$true" if failed_resync else "$false")
        .replace("LEAP_VALUE", "3" if unsynchronized else "0")
        .replace("EXPECT_FAILURE", "$true" if failed_resync or unsynchronized else "$false"), encoding="utf-8")
    result = subprocess.run([shell, "-NoProfile", "-File", str(bootstrap), str(target)],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
