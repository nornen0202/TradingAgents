from pathlib import Path


WORKFLOW = Path(".github/workflows/daily-codex-analysis.yml")


def _workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_daily_analysis_jobs_do_not_depend_on_windows_powershell():
    workflow = _workflow_text()

    assert "shell: python {0}" in workflow
    assert "powershell" not in workflow.lower()
    assert "pwsh" not in workflow.lower()
    assert "$LASTEXITCODE" not in workflow


def test_daily_analysis_sets_up_python_before_first_script_step():
    workflow = _workflow_text()

    for job_name in ("analyze_us:", "analyze_kr:"):
        job_start = workflow.index(f"  {job_name}")
        setup_python = workflow.index("      - name: Set up Python", job_start)
        first_python_run = workflow.index("        run: |", job_start)
        assert setup_python < first_python_run


def test_daily_analysis_uses_python_shell_for_both_windows_jobs():
    workflow = _workflow_text()

    assert workflow.count("        shell: python {0}") == 2
