from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_prism_telegram_workflow_keeps_pages_permission_off_self_hosted_build_job() -> None:
    workflow = (ROOT / ".github" / "workflows" / "daily-prism-telegram-reports.yml").read_text(encoding="utf-8")

    preflight_job = workflow.split("  prepare_self_hosted_runner:", 1)[1].split(
        "  build_prism_telegram_pages:", 1
    )[0]
    build_job = workflow.split("  build_prism_telegram_pages:", 1)[1].split("  deploy:", 1)[0]
    deploy_job = workflow.split("  deploy:", 1)[1]

    assert "Clear stale runner diagnostic logs" in preflight_job
    assert "_diag\\pages" in preflight_job
    assert "_diag\\blocks" in preflight_job
    assert "permissions:\n      contents: read" in build_job
    assert "needs: prepare_self_hosted_runner" in build_job
    assert "pages: write" not in build_job
    assert "id-token: write" not in build_job
    assert "path: source-${{ github.run_id }}" in build_job
    assert "TRADINGAGENTS_SITE_DIR: ${{ github.workspace }}\\site-${{ github.run_id }}" in build_job
    assert "working-directory: ${{ env.TRADINGAGENTS_REPO_DIR }}" in build_job
    assert "Prepare runner diagnostics" not in build_job

    assert "permissions:\n      pages: write\n      id-token: write" in deploy_job


def test_daily_codex_pages_job_preserves_prism_telegram_archive_location() -> None:
    workflow = (ROOT / ".github" / "workflows" / "daily-codex-analysis.yml").read_text(encoding="utf-8")
    build_pages = workflow.split("  build_pages:", 1)[1].split("  deploy:", 1)[0]

    assert "TRADINGAGENTS_PRISM_TELEGRAM_ARCHIVE_DIR: ${{ vars.TRADINGAGENTS_PRISM_TELEGRAM_ARCHIVE_DIR }}" in build_pages
