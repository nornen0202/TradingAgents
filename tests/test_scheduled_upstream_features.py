from tradingagents.scheduled.config import load_scheduled_config
from tradingagents.scheduled.runner import _graph_config, _settings_snapshot
from tradingagents.report_settings import public_run_settings
from tradingagents.scheduled.runner import _effective_parallel_worker_count

import pytest


def test_scheduled_tier_providers_and_parallel_limits_reach_graph(tmp_path):
    path = tmp_path / "scheduled.toml"
    path.write_text('''
[run]
tickers = ["NVDA"]
parallel_analysts = true
analyst_max_concurrency = 2
[llm]
provider = "codex"
quick_think_provider = "openai"
deep_think_provider = "anthropic"
output_think_provider = "google"
quick_think_backend_url = "https://proxy.example/v1?token=private"
quick_model = "gpt-6-luna"
deep_model = "claude-test"
output_model = "gemini-test"
''', encoding="utf-8")
    config = load_scheduled_config(path)
    graph = _graph_config(config, tmp_path / "results")
    assert graph["parallel_analysts"] is True
    assert graph["analyst_max_concurrency"] == 2
    for tier, provider in (("quick", "openai"), ("deep", "anthropic"), ("output", "google")):
        assert graph[f"{tier}_think_provider"] == provider
    assert graph["quick_think_llm"] == "gpt-6-luna"
    assert graph["deep_think_llm"] == "claude-test"
    assert graph["output_think_llm"] == "gemini-test"
    assert graph["quick_think_backend_url"].endswith("token=private")
    assert "private" not in str(public_run_settings(graph))
    assert "private" not in str(_settings_snapshot(config))


def test_scheduled_defaults_preserve_serial_codex_routing(tmp_path):
    path = tmp_path / "scheduled.toml"
    path.write_text('[run]\ntickers = ["NVDA"]\n', encoding="utf-8")
    config = load_scheduled_config(path)
    graph = _graph_config(config, tmp_path / "results")
    assert graph["parallel_analysts"] is False
    assert graph["llm_provider"] == "codex"
    assert graph["quick_think_provider"] is None
    assert _settings_snapshot(config)["quick_think_provider"] == "codex"


def test_codex_environment_models_apply_only_to_codex_roles(tmp_path, monkeypatch):
    monkeypatch.setenv("TRADINGAGENTS_CODEX_MODEL", "codex-global")
    for role in ("QUICK", "DEEP", "OUTPUT", "WRITER", "JUDGE"):
        monkeypatch.setenv(f"TRADINGAGENTS_CODEX_{role}_MODEL", f"codex-{role.lower()}")
    monkeypatch.delenv("TRADINGAGENTS_EXECUTION_LLM_SUMMARY_MODEL", raising=False)
    path = tmp_path / "scheduled.toml"
    path.write_text('''
[run]
tickers = ["NVDA"]
[llm]
provider = "google"
quick_model = "gemini-quick"
deep_think_provider = "codex"
deep_model = "configured-codex"
output_think_provider = "anthropic"
output_model = "claude-output"
writer_model = "gemini-writer"
judge_model = "gemini-judge"
[execution]
llm_summary_model = "gemini-execution"
''', encoding="utf-8")
    config = load_scheduled_config(path)
    assert config.llm.quick_model == "gemini-quick"
    assert config.llm.deep_model == "codex-deep"
    assert config.llm.output_model == "claude-output"
    assert config.llm.writer_model == "gemini-writer"
    assert config.llm.judge_model == "gemini-judge"
    assert config.execution.execution_llm_summary_model == "gemini-execution"
    monkeypatch.setenv("TRADINGAGENTS_EXECUTION_LLM_SUMMARY_MODEL", "explicit-execution")
    assert load_scheduled_config(path).execution.execution_llm_summary_model == "explicit-execution"


@pytest.mark.parametrize("role", ["quick", "deep", "output"])
def test_any_codex_tier_enforces_process_capacity_limit(tmp_path, monkeypatch, role):
    monkeypatch.setenv("TRADINGAGENTS_CODEX_MAX_PARALLEL_TICKERS_CAP", "2")
    path = tmp_path / "scheduled.toml"
    path.write_text(f'''[run]
tickers = ["NVDA"]
max_parallel_tickers = 6
[llm]
provider = "openai"
{role}_think_provider = "codex"
''', encoding="utf-8")
    workers, warning = _effective_parallel_worker_count(config=load_scheduled_config(path), ticker_count=6)
    assert workers == 2 and "cap=2" in warning


@pytest.mark.parametrize("writer_enabled,expected", [(True, 2), (False, 6)])
def test_codex_writer_keeps_cap_when_graph_tiers_are_hosted(tmp_path, monkeypatch, writer_enabled, expected):
    monkeypatch.setenv("TRADINGAGENTS_CODEX_MAX_PARALLEL_TICKERS_CAP", "2")
    path = tmp_path / "scheduled.toml"
    path.write_text(f'''[run]
tickers = ["NVDA"]
max_parallel_tickers = 6
report_polisher_enabled = {str(writer_enabled).lower()}
[llm]
provider = "codex"
quick_think_provider = "openai"
deep_think_provider = "anthropic"
output_think_provider = "google"
''', encoding="utf-8")
    workers, warning = _effective_parallel_worker_count(config=load_scheduled_config(path), ticker_count=6)
    assert workers == expected
