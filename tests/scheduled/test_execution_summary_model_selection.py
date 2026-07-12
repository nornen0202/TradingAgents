from pathlib import Path
from types import SimpleNamespace

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

    assert model == "gpt-5.6-terra"


def test_execution_summary_model_selection_uses_deep_for_degraded_or_stale_updates(tmp_path: Path):
    config = _config(tmp_path)

    model = _execution_summary_model_for_update(
        config=config,
        update=_update(state="DEGRADED", data_health="STALE"),
    )

    assert model == "gpt-5.6-sol"


def test_execution_summary_model_selection_honors_explicit_override(tmp_path: Path):
    config = _config(tmp_path, execution_model="gpt-5.4")

    model = _execution_summary_model_for_update(config=config, update=_update(state="WAIT"))

    assert model == "gpt-5.4"
