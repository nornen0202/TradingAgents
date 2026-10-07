from pathlib import Path
from textwrap import dedent
from types import SimpleNamespace

import pytest

from tradingagents.llm_clients import codex_preflight


def _preflight_scripts(path):
    text = Path(path).read_text(encoding="utf-8")
    chunks = text.split("      - name: Verify Codex login and model availability\n")[1:]
    return [dedent(chunk.split("      - name:", 1)[0].split("        run: |\n", 1)[1]) for chunk in chunks]


SCRIPTS = [
    *_preflight_scripts(".github/workflows/daily-codex-analysis.yml"),
    *_preflight_scripts(".github/workflows/daily-youtube-reports.yml"),
]


@pytest.mark.parametrize("script", SCRIPTS, ids=["us", "kr", "youtube"])
@pytest.mark.parametrize("resolved,fallback", [("gpt-6-sol", True), ("gpt-6-sol", False), ("gpt-6.1-sol", True)])
def test_workflow_rejects_model_substitution_before_export(tmp_path, monkeypatch, script, resolved, fallback):
    env_file = tmp_path / "github-env"
    monkeypatch.setenv("GITHUB_ENV", str(env_file))
    monkeypatch.setenv("GITHUB_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("TRADINGAGENTS_CODEX_WORKSPACE_DIR", str(tmp_path))
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)
    monkeypatch.setenv("TRADINGAGENTS_CODEX_PREFLIGHT_ALLOW_MODEL_FALLBACK", "0")
    calls = []

    def preflight(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(requested_model=kwargs["model"], resolved_model=resolved, fallback_used=fallback)

    monkeypatch.setattr(codex_preflight, "run_codex_preflight", preflight)
    with pytest.raises(SystemExit, match="model fallback is disabled"):
        exec(compile(script, "workflow-preflight", "exec"), {})
    assert len(calls) == 3
    assert all(call["model"] == "gpt-6.1-sol" and not call["fallback_models"] for call in calls)
    assert not env_file.exists()


@pytest.mark.parametrize("script", SCRIPTS, ids=["us", "kr", "youtube"])
def test_workflow_exports_exact_target_for_each_active_role(tmp_path, monkeypatch, script):
    env_file = tmp_path / "github-env"
    monkeypatch.setenv("GITHUB_ENV", str(env_file))
    monkeypatch.setenv("GITHUB_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("TRADINGAGENTS_CODEX_WORKSPACE_DIR", str(tmp_path))
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)
    monkeypatch.setenv("TRADINGAGENTS_CODEX_PREFLIGHT_ALLOW_MODEL_FALLBACK", "0")
    monkeypatch.setattr(codex_preflight, "run_codex_preflight", lambda **kwargs: SimpleNamespace(
        requested_model=kwargs["model"], resolved_model="gpt-6.1-sol", fallback_used=False,
        account="test-account", models=["gpt-6.1-sol"],
    ))
    exec(compile(script, "workflow-preflight", "exec"), {})
    exported = env_file.read_text(encoding="utf-8").splitlines()
    models = [line for line in exported if "_MODEL=" in line]
    assert len(models) in (4, 5)
    assert all(line.endswith("=gpt-6.1-sol") for line in models)
    assert "TRADINGAGENTS_CODEX_PREFLIGHT_OK=1" in exported
