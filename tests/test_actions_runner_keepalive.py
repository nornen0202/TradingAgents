from pathlib import Path


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
