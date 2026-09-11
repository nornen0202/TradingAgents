from pathlib import Path


WORKFLOW_DIR = Path(".github/workflows")
SELF_HOSTED_WORKFLOWS = {
    "account-portfolio-report-verify.yml": 2,
    "daily-codex-analysis.yml": 3,
    "daily-prism-telegram-reports.yml": 1,
    "daily-youtube-reports.yml": 1,
    "intraday-overlay-refresh.yml": 3,
    "work-report-pages-refresh.yml": 1,
}


def test_self_hosted_pages_outputs_use_runner_temp() -> None:
    for filename, expected_paths in SELF_HOSTED_WORKFLOWS.items():
        text = (WORKFLOW_DIR / filename).read_text(encoding="utf-8")
        initialization = (
            'TRADINGAGENTS_SITE_DIR=$([System.IO.Path]::Combine($env:RUNNER_TEMP, '
        )
        assert text.count(initialization) == expected_paths, filename
        assert "TRADINGAGENTS_SITE_DIR: ${{ runner.temp }}" not in text, filename
        assert "path: site" not in text, filename


def test_workflows_that_create_nested_checkouts_clean_them() -> None:
    for filename, cleanup_name in (
        ("daily-prism-telegram-reports.yml", "Clean run-scoped PRISM files"),
        ("work-report-pages-refresh.yml", "Clean run-scoped Work report files"),
    ):
        text = (WORKFLOW_DIR / filename).read_text(encoding="utf-8")
        assert "path: source-${{ github.run_id }}" in text
        assert cleanup_name in text
        assert "if: ${{ always() }}" in text


def test_disk_recovery_jobs_do_not_download_actions_before_cleanup() -> None:
    daily = (WORKFLOW_DIR / "daily-codex-analysis.yml").read_text(encoding="utf-8")
    daily_prepare = daily.split("  prepare_analysis_runner:", 1)[1].split(
        "  analyze_us:", 1
    )[0]
    assert "uses:" not in daily_prepare

    work = (WORKFLOW_DIR / "work-report-pages-refresh.yml").read_text(encoding="utf-8")
    work_prepare = work.split("  prepare_self_hosted_runner:", 1)[1].split(
        "  build_work_report_pages:", 1
    )[0]
    assert "uses:" not in work_prepare
