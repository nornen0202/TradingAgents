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


def test_daily_analysis_uses_python_shell_for_all_windows_jobs():
    workflow = _workflow_text()

    assert workflow.count("        shell: python {0}") == 3


def test_daily_analysis_default_parallel_ticker_workers_is_three():
    workflow = _workflow_text()

    input_start = workflow.index("      max_parallel_tickers:")
    input_block = workflow[input_start : workflow.index("      daily_active_ticker_limit:", input_start)]
    assert 'default: "3"' in input_block


def test_daily_analysis_deploy_runs_after_final_pages_build():
    workflow = _workflow_text()

    deploy_start = workflow.index("  deploy:")
    deploy_block = workflow[deploy_start:]

    assert "      - build_pages" in deploy_block
    assert "if: ${{ always() && needs.build_pages.result == 'success' }}" in deploy_block
    assert "artifact_name: github-pages-final" in deploy_block
