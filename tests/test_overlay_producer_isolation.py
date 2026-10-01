from __future__ import annotations

import ast
from pathlib import Path
import subprocess

import pytest
import yaml


WORKFLOW_PATH = Path(".github/workflows/intraday-overlay-refresh.yml")


def producer(market):
    return yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))["jobs"][f"overlay_refresh_{market}"]


def step(job, name):
    return next(item for item in job["steps"] if item.get("name") == name)


@pytest.mark.parametrize("market", ["us", "kr"])
def test_dedicated_runner_requires_explicit_opt_in_and_overlay_only(market):
    job = producer(market)
    assert job["runs-on"] == (
        "${{ fromJSON(((inputs.run_mode || 'overlay_only') == 'overlay_only' "
        "&& vars.TRADINGAGENTS_OVERLAY_RUNNER_LABELS) || '[\"self-hosted\", \"Windows\"]') }}"
    )
    assert "TRADINGAGENTS_PAGES_RUNNER_LABELS" not in job["runs-on"]
    assert job["concurrency"] == {"group": f"tradingagents-overlay-producer-{market}", "cancel-in-progress": False}


@pytest.mark.parametrize("market", ["us", "kr"])
def test_each_producer_has_run_attempt_scoped_paths_and_virtualenv(market):
    job = producer(market)
    checkout = step(job, "Check out repository")
    assert checkout["with"]["path"] == f"overlay-{market}-${{{{ github.run_id }}}}-${{{{ github.run_attempt }}}}"
    assert checkout["with"]["persist-credentials"] is False
    assert checkout["with"]["clean"] is False
    assert job["env"]["TRADINGAGENTS_OVERLAY_RUN_LABEL"] == f"github-actions-overlay-{market}-${{{{ github.run_id }}}}-${{{{ github.run_attempt }}}}"
    init = step(job, f"Initialize overlay-{market} run-scoped temporary path")["run"]
    assert f"tradingagents-site-$env:GITHUB_RUN_ID-$env:GITHUB_RUN_ATTEMPT-overlay-{market}" in init
    assert f"tradingagents-venv-$env:GITHUB_RUN_ID-$env:GITHUB_RUN_ATTEMPT-overlay-{market}" in init
    guard = step(job, "Wait for safe Windows resource headroom")
    install = step(job, "Install TradingAgents in run-scoped virtual environment")
    assert job["steps"].index(guard) < job["steps"].index(install)
    assert "windows_resource_guard.py" in guard["run"]
    for name in (guard["name"], install["name"], "Run overlay refresh mode", f"Validate {market.upper()} decision bundle quality"):
        assert step(job, name)["working-directory"] == "${{ env.TRADINGAGENTS_REPO_DIR }}"


@pytest.mark.parametrize("market", ["us", "kr"])
def test_install_only_uses_venv_pip(monkeypatch, tmp_path, market):
    venv = tmp_path / "venv"
    monkeypatch.setenv("TRADINGAGENTS_OVERLAY_VENV_DIR", str(venv))
    calls = []
    monkeypatch.setattr(subprocess, "check_call", lambda args: calls.append(args))
    exec(step(producer(market), "Install TradingAgents in run-scoped virtual environment")["run"], {})
    assert calls[0][1:3] == ["-m", "venv"]
    assert calls[1] == [str(venv / "Scripts" / "python.exe"), "-m", "pip", "install", "-e", ".[translation]"]
    assert len(calls) == 2


@pytest.mark.parametrize("market", ["us", "kr"])
def test_dispatch_inputs_are_data_not_python_source(monkeypatch, tmp_path, market):
    job = producer(market)
    assert job["env"]["REQUESTED_TICKERS"] == "${{ inputs.tickers }}"
    for item in job["steps"]:
        script = item.get("run", "")
        assert "${{ inputs." not in script
        assert "${{ github.event.inputs." not in script
        if "python" in item.get("shell", job["defaults"]["run"]["shell"]):
            ast.parse(script)
    repo, archive = tmp_path / "repo", tmp_path / "archive"
    (repo / "config").mkdir(parents=True)
    archive.mkdir()
    filename = "scheduled_analysis.toml" if market == "us" else "scheduled_analysis_korea.toml"
    (repo / "config" / filename).write_text("", encoding="utf-8")
    monkeypatch.chdir(repo)
    for key, value in {
        "TRADINGAGENTS_REPO_DIR": str(repo), "TRADINGAGENTS_ARCHIVE_DIR": str(archive),
        "TRADINGAGENTS_SITE_DIR": str(tmp_path / "site"), "TRADINGAGENTS_OVERLAY_VENV_DIR": str(tmp_path / "venv"),
        "REQUESTED_RUN_MODE": "overlay_only", "REQUESTED_TICKERS": 'AAPL"; raise SystemExit("injected"); #',
        "TRADINGAGENTS_OVERLAY_RUN_LABEL": f"github-actions-overlay-{market}-123-2",
    }.items():
        monkeypatch.setenv(key, value)
    calls = []
    monkeypatch.setattr(subprocess, "check_call", lambda args: calls.append(args))
    exec(step(job, "Run overlay refresh mode")["run"], {})
    assert calls[0][-2:] == ["--tickers", 'AAPL"; raise SystemExit("injected"); #']
    assert calls[0][0] == str(tmp_path / "venv" / "Scripts" / "python.exe")
    assert calls[0][calls[0].index("--label") + 1] == f"github-actions-overlay-{market}-123-2"


@pytest.mark.parametrize("market", ["us", "kr"])
@pytest.mark.parametrize("matching_runs", [0, 1, 2])
def test_quality_check_uses_only_this_job_run_not_global_latest(monkeypatch, tmp_path, market, matching_runs):
    job = producer(market)
    validation = step(job, f"Validate {market.upper()} decision bundle quality")
    assert '"--latest"' not in validation["run"]
    archive = tmp_path / "archive"
    year = archive / "runs" / "2026"
    year.mkdir(parents=True)
    (year / "20261002T130000_github-actions-overlay-other-456-1").mkdir()
    (archive / "latest-run.json").write_text('{"run_id":"unrelated-newer-run"}', encoding="utf-8")
    label = f"github-actions-overlay-{market}-123-2"
    for index in range(matching_runs):
        (year / f"20261002T13000{index}_{label}").mkdir()
    monkeypatch.setenv("TRADINGAGENTS_ARCHIVE_DIR", str(archive))
    monkeypatch.setenv("TRADINGAGENTS_OVERLAY_VENV_DIR", str(tmp_path / "venv"))
    monkeypatch.setenv("TRADINGAGENTS_OVERLAY_RUN_LABEL", label)
    calls = []
    monkeypatch.setattr(subprocess, "check_call", lambda args: calls.append(args))
    if matching_runs == 1:
        exec(validation["run"], {})
        assert calls[0][-2:] == ["--run-dir", str(year / f"20261002T130000_{label}")]
    else:
        with pytest.raises(SystemExit, match="exactly one"):
            exec(validation["run"], {})
        assert calls == []


@pytest.mark.parametrize("market", ["us", "kr"])
@pytest.mark.parametrize("unsafe", [False, True])
def test_checkout_cleanup_is_exact_and_preserves_other_jobs(monkeypatch, tmp_path, market, unsafe):
    job = producer(market)
    cleanup = step(job, f"Clean run-scoped overlay-{market} files")
    assert cleanup["if"] == "${{ always() }}"
    workspace = tmp_path / "workspace"
    own = workspace / f"overlay-{market}-123-2"
    other = workspace / "unrelated-checkout"
    runner_temp = tmp_path / "runner-temp"
    venv = runner_temp / f"tradingagents-venv-123-2-overlay-{market}"
    site = runner_temp / f"tradingagents-site-123-2-overlay-{market}"
    other_venv = runner_temp / f"tradingagents-venv-456-1-overlay-{market}"
    own.mkdir(parents=True)
    other.mkdir()
    for folder in (venv, site, other_venv):
        folder.mkdir(parents=True)
    (own / "generated.txt").write_text("task-local", encoding="utf-8")
    (other / "keep.txt").write_text("keep", encoding="utf-8")
    monkeypatch.setenv("GITHUB_WORKSPACE", str(workspace))
    monkeypatch.setenv("GITHUB_RUN_ID", "123")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "2")
    monkeypatch.setenv("TRADINGAGENTS_REPO_DIR", str(workspace if unsafe else own))
    monkeypatch.setenv("RUNNER_TEMP", str(runner_temp))
    monkeypatch.setenv("TRADINGAGENTS_OVERLAY_VENV_DIR", str(venv))
    monkeypatch.setenv("TRADINGAGENTS_SITE_DIR", str(site))
    if unsafe:
        with pytest.raises(SystemExit, match="unsafe"):
            exec(cleanup["run"], {})
        assert own.exists()
        assert venv.exists()
        assert site.exists()
    else:
        exec(cleanup["run"], {})
        assert not own.exists()
        assert not venv.exists()
        assert not site.exists()
    assert (other / "keep.txt").read_text(encoding="utf-8") == "keep"
    assert other_venv.exists()


@pytest.mark.parametrize("market", ["us", "kr"])
def test_cleanup_rejects_unknown_temp_path_before_deleting_anything(monkeypatch, tmp_path, market):
    cleanup = step(producer(market), f"Clean run-scoped overlay-{market} files")
    workspace, runner_temp = tmp_path / "workspace", tmp_path / "runner-temp"
    own = workspace / f"overlay-{market}-123-2"
    own.mkdir(parents=True)
    runner_temp.mkdir()
    for key, value in {
        "GITHUB_WORKSPACE": str(workspace), "RUNNER_TEMP": str(runner_temp),
        "GITHUB_RUN_ID": "123", "GITHUB_RUN_ATTEMPT": "2",
        "TRADINGAGENTS_REPO_DIR": str(own), "TRADINGAGENTS_OVERLAY_VENV_DIR": str(runner_temp),
        "TRADINGAGENTS_SITE_DIR": "",
    }.items():
        monkeypatch.setenv(key, value)
    with pytest.raises(SystemExit, match="unsafe"):
        exec(cleanup["run"], {})
    assert own.exists()
    assert runner_temp.exists()


def test_publish_runner_was_not_moved_to_dedicated_producer():
    workflow = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
    assert workflow["jobs"]["publish_overlay_site"]["runs-on"] == ["self-hosted", "Windows"]
