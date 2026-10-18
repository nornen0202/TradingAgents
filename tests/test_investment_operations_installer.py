import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest


@pytest.mark.skipif(not shutil.which("powershell.exe"), reason="Windows task installer")
def test_installer_registers_only_paper_and_private_review_with_hidden_launchers(tmp_path):
    root = Path(__file__).resolve().parents[1]
    receipt = tmp_path / "tasks.jsonl"
    env = {**os.environ, "TA_INSTALLER": str(root / "tools/install_investment_operations.ps1"),
           "TA_REPO": str(tmp_path / "repository with spaces"), "TA_ARCHIVE": str(tmp_path / "archive"),
           "TA_INSTALL": str(tmp_path / "maintenance"), "TA_RECEIPT": str(receipt)}
    script = r'''
Import-Module ScheduledTasks, Microsoft.PowerShell.Management, Microsoft.PowerShell.Utility
$PSModuleAutoLoadingPreference='None'
$ErrorActionPreference='Stop'
function global:Register-ScheduledTask {
 param($TaskPath,$TaskName,$Action,$Trigger,$Principal,$Settings,[switch]$Force)
 @{name=$TaskName;path=$TaskPath;exe=$Action.Execute;arguments=$Action.Arguments;limit=$Settings.ExecutionTimeLimit;multiple=[string]$Settings.MultipleInstances;period=$Trigger[0].Repetition.Interval} |
 ConvertTo-Json -Compress | Add-Content -LiteralPath $env:TA_RECEIPT -Encoding utf8
}
& $env:TA_INSTALLER -RepositoryRoot $env:TA_REPO -ArchiveRoot $env:TA_ARCHIVE -InstallRoot $env:TA_INSTALL -NoStart
'''
    result = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
                            env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    tasks = [json.loads(line) for line in receipt.read_text(encoding="utf-8-sig").splitlines()]
    assert [t["name"] for t in tasks] == ["LocalAutomation-paper", "LocalAutomation-review"]
    assert [t["period"] for t in tasks] == ["PT1M", "PT15M"]
    assert tasks[0]["limit"] == "PT10M"
    assert tasks[1]["limit"] == "PT0S"
    for task in tasks:
        assert task["exe"].lower().endswith("wscript.exe")
        assert "run_powershell_hidden.vbs" in task["arguments"]
        assert task["multiple"] == "IgnoreNew"
        assert task["path"] == "\\TradingAgents\\"
    enabled = json.loads((Path(env["TA_REPO"]) / ".runtime/local-automation/paper/enabled.json").read_text(encoding="utf-8-sig"))
    assert enabled["mode"] == "LOCAL_PAPER_ONLY"
    assert enabled["real_orders_enabled"] is False
