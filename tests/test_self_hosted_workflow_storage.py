import ast
from pathlib import Path

import yaml

import os
import shutil
import subprocess
import stat

import pytest


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


def test_python_workflow_steps_import_os_before_using_os_environ() -> None:
    for workflow_path in WORKFLOW_DIR.glob("*.yml"):
        workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
        for job_name, job in (workflow.get("jobs") or {}).items():
            default_shell = (
                ((job.get("defaults") or {}).get("run") or {}).get("shell", "")
            )
            for step in job.get("steps") or []:
                script = step.get("run")
                shell = step.get("shell", default_shell)
                if (
                    not isinstance(script, str)
                    or "python" not in shell
                    or "os.environ" not in script
                ):
                    continue
                tree = ast.parse(script)
                imports_os = any(
                    isinstance(node, ast.Import)
                    and any(alias.name == "os" for alias in node.names)
                    for node in ast.walk(tree)
                ) or any(
                    isinstance(node, ast.ImportFrom) and node.module == "os"
                    for node in ast.walk(tree)
                )
                assert imports_os, (
                    f"{workflow_path.name}:{job_name}:{step.get('name')} uses "
                    "os.environ without importing os"
                )


@pytest.mark.parametrize('filename,job_name', [
    ('work-report-pages-refresh.yml', 'prepare_self_hosted_runner'),
    ('daily-codex-analysis.yml', 'prepare_analysis_runner'),
])
def test_preflight_is_bounded_and_preserves_unrelated_files(tmp_path, filename, job_name):
    workflow = yaml.safe_load((WORKFLOW_DIR / filename).read_text(encoding='utf-8'))
    job = workflow['jobs'][job_name]
    assert job['timeout-minutes'] <= 10
    assert '-NoProfile -NonInteractive' in job['defaults']['run']['shell']
    step = job['steps'][0]
    assert step['timeout-minutes'] <= 5
    if os.name != 'nt' or not shutil.which('pwsh'):
        pytest.skip('Windows PowerShell required for cleanup execution')
    workspace = tmp_path / 'workspace'
    workspace.mkdir()
    stale = workspace / 'source-123'
    stale.mkdir()
    (stale / 'output.txt').write_text('stale')
    notes = workspace / 'user-notes'
    notes.mkdir()
    (notes / 'keep.txt').write_text('keep')
    script = tmp_path / 'preflight.ps1'
    # Isolate free-space checks from the CI host's current disk utilization.
    script.write_text('function Get-PSDrive { param($Name) @{Free=20GB} }\n' + step['run'])
    result = subprocess.run(['pwsh', '-NoProfile', '-NonInteractive', '-File', str(script)],
                            env={**os.environ, 'GITHUB_WORKSPACE': str(workspace)},
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert not stale.exists()
    assert (notes / 'keep.txt').read_text() == 'keep'
    assert 'Removing stale runner output:' in result.stdout


def test_work_report_inputs_are_passed_as_data():
    workflow = yaml.safe_load((WORKFLOW_DIR / 'work-report-pages-refresh.yml').read_text(encoding='utf-8'))
    job = workflow['jobs']['build_work_report_pages']
    assert job['env']['WORK_EVENT_ID'] == '${{ inputs.event_id }}'
    for step in job['steps']:
        script = step.get('run', '')
        assert '${{ inputs.' not in script


@pytest.mark.parametrize('filename,job_name', [
    ('work-report-pages-refresh.yml', 'build_work_report_pages'),
    ('daily-prism-telegram-reports.yml', 'build_prism_telegram_pages'),
])
@pytest.mark.parametrize('unsafe_target', [False, True])
def test_final_cleanup_handles_readonly_git_files_and_checks_boundaries(tmp_path, filename, job_name, unsafe_target):
    if os.name != 'nt' or not shutil.which('pwsh'):
        pytest.skip('Windows PowerShell required for cleanup execution')
    workflow = yaml.safe_load((WORKFLOW_DIR / filename).read_text(encoding='utf-8'))
    cleanup = next(step for step in workflow['jobs'][job_name]['steps']
                   if step.get('name', '').startswith('Clean run-scoped'))
    assert cleanup['timeout-minutes'] <= 5
    assert '-NoProfile -NonInteractive' in cleanup['shell']
    workspace, runner_temp = tmp_path / 'workspace', tmp_path / 'temp'
    source, site = workspace / 'source-123', runner_temp / 'site-123'
    pack = source / '.git' / 'objects' / 'pack' / 'example.idx'
    pack.parent.mkdir(parents=True)
    pack.write_text('read-only Git index')
    pack.chmod(stat.S_IREAD)
    site.mkdir(parents=True)
    (site / 'index.html').write_text('generated site')
    keep = workspace / 'keep.txt'
    keep.write_text('unrelated data')
    script = tmp_path / 'cleanup.ps1'
    script.write_text(cleanup['run'])
    result = subprocess.run(
        ['pwsh', '-NoProfile', '-NonInteractive', '-File', str(script)],
        env={**os.environ, 'GITHUB_WORKSPACE': str(workspace), 'RUNNER_TEMP': str(runner_temp),
             'TRADINGAGENTS_REPO_DIR': str(workspace if unsafe_target else source),
             'TRADINGAGENTS_SITE_DIR': str(site)},
        capture_output=True, text=True, encoding='utf-8', timeout=30,
    )
    assert not site.exists(), result.stderr
    assert keep.read_text() == 'unrelated data'
    if unsafe_target:
        assert result.returncode != 0
        assert 'unsafe run-scoped path' in result.stderr
        assert pack.exists()
        pack.chmod(stat.S_IWRITE)
    else:
        assert result.returncode == 0, result.stderr
        assert not source.exists()
