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

    assert workflow.count("        shell: python {0}") == 4


def test_daily_analysis_default_parallel_ticker_workers_is_four():
    workflow = _workflow_text()

    input_start = workflow.index("      max_parallel_tickers:")
    input_block = workflow[input_start : workflow.index("      daily_active_ticker_limit:", input_start)]
    assert 'default: "4"' in input_block


def test_daily_analysis_default_ticker_timeout_is_sixty_minutes():
    workflow = _workflow_text()

    input_start = workflow.index("      per_ticker_timeout_minutes:")
    input_block = workflow[input_start : workflow.index("\n\npermissions:", input_start)]
    assert 'default: "60"' in input_block


def test_daily_analysis_job_timeout_bounds_scheduled_runs():
    workflow = _workflow_text()

    assert workflow.count("    timeout-minutes: 720") == 2
    assert "        timeout-minutes: 240" not in workflow


def test_daily_analysis_jobs_skip_inline_site_build_execution_refresh_and_fail_on_partial_runs():
    workflow = _workflow_text()

    assert workflow.count('"--skip-site-build",') == 2
    assert workflow.count('"--disable-execution-refresh",') == 2
    assert workflow.count('"--strict",') == 2


def test_daily_analysis_uploads_diagnostics_even_on_failure():
    workflow = _workflow_text()

    assert "Collect US analysis diagnostics" in workflow
    assert "Upload US analysis diagnostics" in workflow
    assert "Collect KR analysis diagnostics" in workflow
    assert "Upload KR analysis diagnostics" in workflow


def test_daily_analysis_schedule_gate_requires_pages_build_for_daily_coverage():
    workflow = _workflow_text()

    assert '"target_jobs": ["analyze_us", "build_pages"]' in workflow
    assert '"target_jobs": ["analyze_kr", "build_pages"]' in workflow


def test_daily_analysis_self_hosted_jobs_serialize_workspace_checkout():
    workflow = _workflow_text()

    for job_name in ("analyze_us", "analyze_kr", "prepare_pages_runner", "build_pages"):
        job_start = workflow.index(f"  {job_name}:")
        job_block = workflow[job_start : job_start + 1200]
        assert "concurrency:" in job_block
        assert "group: daily-codex-analysis-self-hosted-${{ github.ref }}" in job_block
        assert "cancel-in-progress: false" in job_block


def test_daily_analysis_cleans_pages_diagnostics_before_self_hosted_checkout():
    workflow = _workflow_text()

    for job_name in ("analyze_us", "analyze_kr"):
        job_start = workflow.index(f"  {job_name}:")
        checkout = workflow.index("      - name: Check out repository", job_start)
        job_before_checkout = workflow[job_start:checkout]
        assert '"_diag" / "pages"' in job_before_checkout
        assert "*.log" in job_before_checkout


def test_daily_pages_build_uses_runner_diagnostics_preflight():
    workflow = _workflow_text()

    preflight = workflow.split("  prepare_pages_runner:", 1)[1].split("  build_pages:", 1)[0]
    build_pages = workflow.split("  build_pages:", 1)[1].split("  deploy:", 1)[0]

    assert "Clear stale runner diagnostic logs" in preflight
    assert '"_diag" / "pages"' in preflight
    assert '"_diag" / "blocks"' in preflight
    assert "contents: read" in preflight
    assert "needs.prepare_pages_runner.result == 'success'" in build_pages
    assert "      - prepare_pages_runner" in build_pages
    assert "permissions:\n      contents: read" in build_pages
    assert "pages: write" not in build_pages
    assert "id-token: write" not in build_pages
    assert "Prepare GitHub Pages diagnostics" not in build_pages


def test_daily_analysis_configures_pages_only_in_final_build_job():
    workflow = _workflow_text()

    assert workflow.count("      - name: Configure GitHub Pages") == 1
    build_pages_start = workflow.index("  build_pages:")
    configure_pages = workflow.index("      - name: Configure GitHub Pages")
    assert configure_pages > build_pages_start


def test_daily_analysis_deploy_runs_after_final_pages_build():
    workflow = _workflow_text()

    deploy_start = workflow.index("  deploy:")
    deploy_block = workflow[deploy_start:]

    assert "      - build_pages" in deploy_block
    assert "if: ${{ always() && needs.build_pages.result == 'success' }}" in deploy_block
    assert "artifact_name: github-pages-final" in deploy_block
    assert "permissions:\n      pages: write\n      id-token: write" in deploy_block
