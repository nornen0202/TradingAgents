from concurrent.futures import ThreadPoolExecutor
import json
from threading import Barrier
from types import SimpleNamespace

import pytest

from tradingagents.dataflows.config import get_config, run_config, run_config_context
from tradingagents.graph.trading_graph import TradingAgentsGraph


def test_run_scope_restores_nested_settings_after_failure_and_does_not_alias():
    original = get_config()
    with run_config({"output_language": "Korean", "data_vendors": {"news_data": "naver"}}):
        assert get_config()["data_vendors"]["core_stock_apis"] == "yfinance"
        copy = get_config()
        copy["data_vendors"]["news_data"] = "corrupted"
        assert get_config()["data_vendors"]["news_data"] == "naver"
        with pytest.raises(RuntimeError):
            with run_config({"output_language": "English"}):
                assert get_config()["output_language"] == "English"
                assert get_config()["data_vendors"]["news_data"] != "naver"
                raise RuntimeError("interrupted")
        assert get_config()["output_language"] == "Korean"
    assert get_config() == original


def test_concurrent_run_scopes_keep_cutoffs_and_vendors_separate():
    barrier = Barrier(2)

    def read(settings):
        with run_config(settings):
            barrier.wait(timeout=5)
            return get_config()

    settings = [
        {"analysis_as_of": "2024-01-01", "data_vendors": {"news_data": "naver"}},
        {"analysis_as_of": "2025-01-01", "data_vendors": {"news_data": "yfinance"}},
    ]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(read, settings))
    for requested, actual in zip(settings, results):
        assert actual["analysis_as_of"] == requested["analysis_as_of"]
        assert actual["data_vendors"]["news_data"] == requested["data_vendors"]["news_data"]


def test_stream_yields_and_early_close_do_not_leak_configuration():
    original = get_config()
    seen_on_close = []

    def stream(*args, **kwargs):
        try:
            yield get_config()["analysis_as_of"]
            yield get_config()["analysis_as_of"]
        finally:
            seen_on_close.append(get_config()["analysis_as_of"])

    first, second = [object.__new__(TradingAgentsGraph) for _ in range(2)]
    for graph, cutoff in ((first, "2024-01-01"), (second, "2025-01-01")):
        graph.graph = SimpleNamespace(stream=stream)
        graph._prepared_run_config = {"analysis_as_of": cutoff}
    first_stream, second_stream = first.stream_run({}), second.stream_run({})
    assert next(first_stream) == "2024-01-01"
    assert get_config() == original
    assert next(second_stream) == "2025-01-01"
    assert next(first_stream) == "2024-01-01"
    assert get_config() == original
    first_stream.close()
    second_stream.close()
    assert seen_on_close == ["2024-01-01", "2025-01-01"]
    assert get_config() == original


def test_private_run_context_copies_nested_inputs():
    settings = {"data_vendors": {"news_data": "naver"}}
    context = run_config_context(settings)
    settings["data_vendors"]["news_data"] = "yfinance"
    assert context.run(get_config)["data_vendors"]["news_data"] == "naver"


def test_invoke_run_restores_caller_settings_after_failed_invocation():
    original = get_config()

    def invoke(*args, **kwargs):
        assert get_config()["analysis_as_of"] == "2024-01-01"
        assert get_config()["output_language"] == "Korean"
        raise RuntimeError("failed source")

    graph = object.__new__(TradingAgentsGraph)
    graph._prepared_run_config = {"analysis_as_of": "2024-01-01", "output_language": "Korean"}
    graph.graph = SimpleNamespace(invoke=invoke)
    with pytest.raises(RuntimeError, match="failed source"):
        graph.invoke_run({})
    assert get_config() == original


def test_state_log_records_reproducible_settings_without_paths_or_credentials(tmp_path):
    graph = object.__new__(TradingAgentsGraph)
    graph.config = {
        "results_dir": str(tmp_path), "llm_provider": "codex", "deep_think_provider": "google",
        "quick_think_llm": "gpt-6-sol", "deep_think_llm": "gemini-test",
        "backend_url": "https://user:password@private.invalid", "api_key": "secret-token",
        "codex_workspace_dir": "C:/private/workspace", "parallel_analysts": True,
    }
    graph.ticker = "AAPL"
    graph.selected_analysts = ["market", "news"]
    graph.log_states_dict = {}
    state = {
        "company_of_interest": "AAPL", "trade_date": "2024-01-01",
        "market_report": "market", "sentiment_report": "", "news_report": "news", "fundamentals_report": "",
        "investment_debate_state": dict.fromkeys(["bull_history", "bear_history", "history", "current_response", "judge_decision"], ""),
        "risk_debate_state": dict.fromkeys(["aggressive_history", "conservative_history", "neutral_history", "history", "judge_decision"], ""),
        "trader_investment_plan": "hold", "investment_plan": "hold", "final_trade_decision": "HOLD",
    }
    graph._log_state("2024-01-01", state)
    saved = json.loads((tmp_path / "AAPL/TradingAgentsStrategy_logs/full_states_log_2024-01-01.json").read_text())
    settings = saved["run_settings"]
    assert settings["deep_think_provider"] == "google"
    assert settings["quick_think_provider"] == "codex"
    assert settings["analysts"] == ["market", "news"]
    serialized = json.dumps(settings)
    for private in ("secret-token", "private.invalid", "C:/private", str(tmp_path)):
        assert private not in serialized
