import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from types import ModuleType

import pytest

from tradingagents import local_automation as local


def invoke(tmp_path, monkeypatch, *, dry_run=False):
    monkeypatch.setattr(local, "prepare_environment", lambda: None)
    monkeypatch.setattr(sys, "argv", ["local", "validate-kis", "--archive-dir", str(tmp_path / "archive"),
        "--state-dir", str(tmp_path / "state"), "--runtime-dir", str(tmp_path / "runtime"),
        *(["--dry-run"] if dry_run else [])])
    return local.main()


@pytest.mark.parametrize("dry_run", [False, True])
def test_strategy_lane_paths_dry_run_and_private_log_projection(tmp_path, monkeypatch, capsys, dry_run):
    from tradingagents.execution import demo_runtime
    calls = []
    def tick(*args):
        calls.append(args)
        return {"mode": "KIS_DEMO_STRATEGY", "checked_at": "2026-10-18T01:00:00Z", "markets": {
            "KR": {"status": "WAITING_VALIDATION", "orders": ["PRIVATE_ORDER"], "performance": "PRIVATE_AMOUNT"}}}
    monkeypatch.setattr(demo_runtime, "tick", tick)
    monkeypatch.setattr(local, "prepare_environment", lambda: None)
    monkeypatch.setattr(sys, "argv", ["local", "strategy-kis", "--archive-dir", str(tmp_path / "archive"),
        "--state-dir", str(tmp_path / "state"), "--runtime-dir", str(tmp_path / "runtime"), *(["--dry-run"] if dry_run else [])])
    assert local.main() == 0
    assert "PRIVATE" not in capsys.readouterr().out
    assert len(calls) == (0 if dry_run else 1)
    if calls:
        assert calls[0] == ((tmp_path / "archive").resolve(), (tmp_path / "state/kis-strategy").resolve(), (tmp_path / "state/kis-validation").resolve())


@pytest.mark.parametrize("config", [None, "invalid", {}, [],
    {"mode": "KIS_DEMO_SESSION_VALIDATION", "enabled": True, "real_orders_enabled": True},
    {"mode": "KIS_DEMO_SESSION_VALIDATION", "enabled": 1, "real_orders_enabled": False},
    {"mode": "KIS_DEMO_SESSION_VALIDATION", "enabled": False, "real_orders_enabled": False},
    {"mode": "real", "enabled": True, "real_orders_enabled": False}])
def test_validation_lane_requires_complete_explicit_demo_enable(tmp_path, monkeypatch, capsys, config):
    state = tmp_path / "state/kis-validation"
    state.mkdir(parents=True)
    if config is not None:
        (state / "enabled.json").write_text(config if isinstance(config, str) else json.dumps(config))
    forbidden = ModuleType("tradingagents.execution.demo_validation")
    forbidden.run_campaign = lambda *args, **kwargs: pytest.fail("disabled lane invoked validation")
    monkeypatch.setitem(sys.modules, "tradingagents.execution.demo_validation", forbidden)
    assert invoke(tmp_path, monkeypatch) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "DISABLED"


def test_enabled_validation_lane_uses_persistent_paths_and_halt_recovery(tmp_path, monkeypatch):
    state = tmp_path / "state/kis-validation"
    state.mkdir(parents=True)
    (state / "enabled.json").write_text(json.dumps({"mode": "KIS_DEMO_SESSION_VALIDATION", "enabled": True,
        "real_orders_enabled": False}), encoding="utf-8-sig")
    (state / "HALT").touch()  # runner must still reconcile/cancel previously admitted orders
    calls = []
    fake = ModuleType("tradingagents.execution.demo_validation")
    fake.run_campaign = lambda *args, **kwargs: calls.append((args, kwargs)) or {}
    monkeypatch.setitem(sys.modules, "tradingagents.execution.demo_validation", fake)
    assert invoke(tmp_path, monkeypatch) == 0
    assert calls == [(((tmp_path / "archive").resolve(), state.resolve()), {"run": True})]
    calls.clear()
    assert invoke(tmp_path, monkeypatch, dry_run=True) == 0
    assert calls == []


@pytest.mark.skipif(not shutil.which("powershell.exe"), reason="Windows task installer")
@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("strategy", [False, True])
def test_validation_installer_only_registers_explicit_demo_lane(tmp_path, enabled, strategy):
    root = Path(__file__).resolve().parents[1]
    receipt = tmp_path / "tasks.jsonl"
    env = {**os.environ, "TA_INSTALLER": str(root / ("tools/install_kis_strategy.ps1" if strategy else "tools/install_kis_session_validation.ps1")),
        "TA_SWITCH": "EnableDemoStrategy" if strategy else "EnableDemoValidation",
        "TA_REPO": str(tmp_path / "repository with spaces"), "TA_ARCHIVE": str(tmp_path / "archive"),
        "TA_INSTALL": str(tmp_path / "maintenance"), "TA_RECEIPT": str(receipt), "TA_ENABLE": str(enabled)}
    script = r'''
Import-Module ScheduledTasks, Microsoft.PowerShell.Management, Microsoft.PowerShell.Utility
$PSModuleAutoLoadingPreference='None'
$ErrorActionPreference='Stop'
function global:Register-ScheduledTask {
 param($TaskPath,$TaskName,$Action,$Trigger,$Principal,$Settings,[switch]$Force)
 @{name=$TaskName;path=$TaskPath;exe=$Action.Execute;arguments=$Action.Arguments;limit=$Settings.ExecutionTimeLimit;multiple=[string]$Settings.MultipleInstances;period=$Trigger[0].Repetition.Interval} |
 ConvertTo-Json -Compress | Add-Content -LiteralPath $env:TA_RECEIPT -Encoding utf8
}
$opt = @{}; $opt[$env:TA_SWITCH] = ($env:TA_ENABLE -eq 'True')
& $env:TA_INSTALLER -RepositoryRoot $env:TA_REPO -ArchiveRoot $env:TA_ARCHIVE -InstallRoot $env:TA_INSTALL @opt -NoStart
'''
    result = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
        env=env, capture_output=True, text=True, timeout=30)
    if not enabled:
        assert result.returncode != 0
        assert not receipt.exists()
        assert not Path(env["TA_REPO"]).exists()
        return
    assert result.returncode == 0, result.stderr
    tasks = [json.loads(line) for line in receipt.read_text(encoding="utf-8-sig").splitlines()]
    assert len(tasks) == 1
    task = tasks[0]
    assert task["name"] == ("LocalAutomation-strategy-kis" if strategy else "LocalAutomation-validate-kis")
    assert task["path"] == "\\TradingAgents\\"
    assert task["exe"].lower().endswith("wscript.exe")
    assert "run_powershell_hidden.vbs" in task["arguments"]
    assert ("-Command strategy-kis" if strategy else "-Command validate-kis") in task["arguments"]
    assert task["period"] == "PT1M"
    assert task["limit"] == "PT10M"
    assert task["multiple"] == "IgnoreNew"
    config = json.loads((Path(env["TA_REPO"]) / (".runtime/local-automation/kis-strategy/enabled.json" if strategy else ".runtime/local-automation/kis-validation/enabled.json")).read_text(encoding="utf-8-sig"))
    assert config["mode"] == ("KIS_DEMO_STRATEGY" if strategy else "KIS_DEMO_SESSION_VALIDATION")
    assert config["enabled"] is True
    assert config["real_orders_enabled"] is False
