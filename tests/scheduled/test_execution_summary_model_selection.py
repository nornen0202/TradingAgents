from pathlib import Path
from types import SimpleNamespace
from dataclasses import replace
import re

import pytest

from tradingagents.scheduled.config import load_scheduled_config
from tradingagents.scheduled.runner import _execution_summary_model_for_update


class _State:
    def __init__(self, value: str):
        self.value = value


def _config(tmp_path: Path, *, execution_model: str = ""):
    config_path = tmp_path / "scheduled.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["AAPL"]

[execution]
llm_summary_model = "{execution_model}"

[storage]
archive_dir = "{(tmp_path / 'archive').as_posix()}"
site_dir = "{(tmp_path / 'site').as_posix()}"
""",
        encoding="utf-8",
    )
    return load_scheduled_config(config_path)


def _update(*, state: str, now: str = "NONE", if_triggered: str = "WAIT", data_health: str = "OK"):
    return SimpleNamespace(
        decision_state=_State(state),
        decision_now=_State(now),
        decision_if_triggered=_State(if_triggered),
        data_health=data_health,
        execution_timing_state=_State("WAITING"),
        reason_codes=(),
    )


def test_execution_summary_model_selection_is_deterministic_for_plain_wait(tmp_path: Path):
    config = _config(tmp_path)

    assert _execution_summary_model_for_update(config=config, update=_update(state="WAIT")) is None


def test_execution_summary_model_selection_uses_quick_for_actionable_updates(tmp_path: Path):
    config = _config(tmp_path)

    model = _execution_summary_model_for_update(
        config=config,
        update=_update(state="ACTIONABLE_NOW", now="STARTER_NOW"),
    )

    assert model == "gpt-6.1-sol"


def test_execution_summary_model_selection_uses_deep_for_degraded_or_stale_updates(tmp_path: Path):
    config = _config(tmp_path)

    model = _execution_summary_model_for_update(
        config=config,
        update=_update(state="DEGRADED", data_health="STALE"),
    )

    assert model == "gpt-6.1-sol"


def test_execution_summary_model_selection_honors_explicit_override(tmp_path: Path):
    config = _config(tmp_path, execution_model="gpt-5.4")

    model = _execution_summary_model_for_update(config=config, update=_update(state="WAIT"))

    assert model == "gpt-5.4"


@pytest.mark.parametrize("state,action,health", [
    ("ACTIONABLE_NOW", "STARTER_NOW", "OK"),
    ("DEGRADED", "WAIT", "STALE"),
    ("INVALIDATED", "SELL", "OK"),
    ("WAIT", "NONE", "OK"),
])
def test_overlay_fast_path_does_not_escalate_optional_prose(tmp_path, state, action, health):
    config = _config(tmp_path)
    config = replace(config, run=replace(config.run, run_mode="overlay_only"))
    update = _update(state=state, now=action, data_health=health)
    assert _execution_summary_model_for_update(config=config, update=update) is None


def test_overlay_preserves_explicit_summary_model_opt_in(tmp_path):
    config = _config(tmp_path, execution_model="gpt-5.4")
    config = replace(config, run=replace(config.run, run_mode="overlay_only"))
    assert _execution_summary_model_for_update(
        config=config, update=_update(state="DEGRADED", data_health="STALE"),
    ) == "gpt-5.4"


@pytest.mark.parametrize("workflow_name,job_count", [
    ("daily-codex-analysis.yml", 2),
    ("daily-youtube-reports.yml", 1),
])
def test_workflow_exact_role_models_preserve_optional_summary_policy(tmp_path, monkeypatch, workflow_name, job_count):
    workflow = (Path(".github/workflows") / workflow_name).read_text(encoding="utf-8")
    # Simulate an older runner-wide override, then the actual job environment.
    for variable in ("TRADINGAGENTS_CODEX_MODEL", "TRADINGAGENTS_EXECUTION_LLM_SUMMARY_MODEL"):
        monkeypatch.setenv(variable, "gpt-6-sol")
        values = re.findall(rf'^\s+{variable}: "([^"]*)"$', workflow, flags=re.MULTILINE)
        assert values == [""] * job_count
        monkeypatch.setenv(variable, values[0])
    # Daily jobs export these role values; YouTube's base site uses TOML defaults.
    for role in ("DEEP", "QUICK", "OUTPUT", "WRITER", "JUDGE"):
        if workflow_name == "daily-codex-analysis.yml":
            monkeypatch.setenv(f"TRADINGAGENTS_CODEX_{role}_MODEL", "gpt-6.1-sol")
        else:
            monkeypatch.delenv(f"TRADINGAGENTS_CODEX_{role}_MODEL", raising=False)

    config = _config(tmp_path)
    assert config.execution.execution_llm_summary_model is None
    assert _execution_summary_model_for_update(config=config, update=_update(state="WAIT")) is None
    for update in (
        _update(state="ACTIONABLE_NOW", now="STARTER_NOW"),
        _update(state="DEGRADED", data_health="STALE"),
    ):
        assert _execution_summary_model_for_update(config=config, update=update) == "gpt-6.1-sol"
        overlay = replace(config, run=replace(config.run, run_mode="overlay_only"))
        assert _execution_summary_model_for_update(config=overlay, update=update) is None
