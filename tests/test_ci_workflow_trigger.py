from pathlib import Path
import os
import shutil
import subprocess

import pytest
import yaml


def test_ci_does_not_run_twice_for_pull_request_branches() -> None:
    workflow = yaml.safe_load(Path(".github/workflows/ci.yml").read_text(encoding="utf-8"))
    triggers = workflow[True]

    assert "pull_request" in triggers
    assert triggers["push"]["branches"] == ["main"]


def test_browser_validation_has_its_own_budget_and_required_gate():
    jobs = yaml.safe_load(Path(".github/workflows/ci.yml").read_text(encoding="utf-8"))["jobs"]
    assert jobs["unit"]["timeout-minutes"] == 60
    assert jobs["browser"]["timeout-minutes"] == 15
    assert "needs" not in jobs["browser"]
    commands = {step.get("run", "") for step in jobs["browser"]["steps"]}
    for script in ("mobile_layout_regression.py", "strategy_interaction_regression.py",
                   "report_reading_regression.py", "investment_review_regression.py"):
        assert f"python .github/scripts/{script}" in commands
    assert set(jobs["test"]["needs"]) == {"unit", "browser"}
    assert jobs["test"]["if"] == "${{ always() }}"


@pytest.mark.skipif(shutil.which("pwsh") is None, reason="PowerShell required")
@pytest.mark.parametrize("unit,browser", [("success", "success"), ("failure", "success"),
    ("cancelled", "success"), ("skipped", "success"), ("success", "failure"),
    ("success", "cancelled"), ("success", "skipped"), ("", "success")])
def test_required_ci_gate_rejects_every_non_success(tmp_path, unit, browser):
    job = yaml.safe_load(Path(".github/workflows/ci.yml").read_text(encoding="utf-8"))["jobs"]["test"]
    script = tmp_path / "gate.ps1"
    script.write_text(job["steps"][0]["run"], encoding="utf-8")
    result = subprocess.run([shutil.which("pwsh"), "-NoProfile", "-NonInteractive", "-File", str(script)],
                            env={**os.environ, "UNIT_RESULT": unit, "BROWSER_RESULT": browser},
                            capture_output=True, timeout=20)
    assert (result.returncode == 0) is (unit == browser == "success")
