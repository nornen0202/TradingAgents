import unittest
from copy import deepcopy
from unittest.mock import Mock, patch

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.config import get_config
from tradingagents.graph.trading_graph import TradingAgentsGraph


class _DummyClient:
    def __init__(self):
        self._llm = Mock()

    def get_llm(self):
        return self._llm


class GraphConfigurationTests(unittest.TestCase):
    @patch("tradingagents.graph.trading_graph.GraphSetup.setup_graph", return_value=Mock())
    @patch("tradingagents.graph.trading_graph.create_llm_client", return_value=_DummyClient())
    def test_constructing_and_preparing_graph_does_not_change_caller_settings(self, *_mocks):
        original = get_config()
        config = deepcopy(DEFAULT_CONFIG)
        config.update(output_language="Korean", analysis_as_of="2020-01-01", memory_dir=None)
        with TradingAgentsGraph(config=config, selected_analysts=["market"]) as graph:
            self.assertEqual(get_config(), original)
            graph.curr_state = {"market_report": "a previous run"}
            graph.log_states_dict = {"2020-01-01": {"market_report": "old"}}
            graph.prepare_run("AAPL", "2024-01-02")
            self.assertEqual(get_config(), original)
            self.assertIsNone(graph.curr_state)
            self.assertEqual(graph.log_states_dict, {})
            self.assertEqual(graph.bull_memory.as_of, "2024-01-02")

    @patch("tradingagents.graph.trading_graph.GraphSetup.setup_graph", return_value=Mock())
    @patch("tradingagents.graph.trading_graph.create_llm_client", return_value=_DummyClient())
    def test_mixed_providers_use_their_own_options_and_endpoints(self, create_client, *_mocks):
        config = deepcopy(DEFAULT_CONFIG)
        config.update(
            llm_provider="codex", backend_url="http://shared-codex.invalid",
            deep_think_provider="anthropic", deep_think_llm="claude-test",
            quick_think_provider="google", quick_think_llm="gemini-test",
            quick_think_backend_url="https://google-proxy.invalid",
            anthropic_effort="high", google_thinking_level="minimal",
            max_tokens=4096, memory_dir=None,
        )

        with TradingAgentsGraph(config=config, selected_analysts=["market"]):
            deep, quick, output = [call.kwargs for call in create_client.call_args_list]

        self.assertEqual(deep["provider"], "anthropic")
        self.assertIsNone(deep["base_url"])
        self.assertEqual(deep["effort"], "high")
        self.assertEqual(deep["max_tokens"], 4096)
        self.assertNotIn("model_role", deep)
        self.assertEqual(quick["provider"], "google")
        self.assertEqual(quick["base_url"], "https://google-proxy.invalid")
        self.assertEqual(quick["thinking_level"], "minimal")
        self.assertNotIn("effort", quick)
        self.assertEqual(output["provider"], "codex")
        self.assertEqual(output["model_role"], "output")
        self.assertEqual(output["base_url"], "http://shared-codex.invalid")
        self.assertNotIn("max_tokens", output)

    @patch("tradingagents.graph.trading_graph.GraphSetup.setup_graph", return_value=Mock())
    @patch("tradingagents.graph.trading_graph.create_llm_client", return_value=_DummyClient())
    def test_parallel_analysts_have_an_explicit_worker_budget(self, _client, setup):
        config = deepcopy(DEFAULT_CONFIG)
        config.update(parallel_analysts=True, analyst_max_concurrency=2, memory_dir=None)
        with TradingAgentsGraph(config=config, selected_analysts=["market", "news"]) as graph:
            self.assertEqual(graph.propagator.get_graph_args()["config"]["max_concurrency"], 2)
        self.assertTrue(setup.call_args.kwargs["parallel_analysts"])

    @patch("tradingagents.graph.trading_graph.GraphSetup.setup_graph", return_value=Mock())
    @patch("tradingagents.graph.trading_graph.create_llm_client", return_value=_DummyClient())
    def test_max_recur_limit_propagates_to_graph_args(self, *_mocks):
        config = deepcopy(DEFAULT_CONFIG)
        config["max_recur_limit"] = 321

        graph = TradingAgentsGraph(config=config, selected_analysts=["market"])

        self.assertEqual(graph.propagator.max_recur_limit, 321)
        self.assertEqual(graph.propagator.get_graph_args()["config"]["recursion_limit"], 321)

    @patch("tradingagents.graph.trading_graph.GraphSetup.setup_graph", return_value=Mock())
    @patch("tradingagents.graph.trading_graph.create_llm_client", return_value=_DummyClient())
    def test_codex_clients_use_role_specific_models_and_effort(self, create_client, *_mocks):
        config = deepcopy(DEFAULT_CONFIG)
        config["llm_provider"] = "codex"

        TradingAgentsGraph(config=config, selected_analysts=["market"])

        calls = create_client.call_args_list
        self.assertEqual([call.kwargs["model"] for call in calls], [
            "gpt-6-sol",
            "gpt-6-sol",
            "gpt-6-sol",
        ])
        self.assertEqual([call.kwargs["model_role"] for call in calls], ["deep", "quick", "output"])
        self.assertEqual(
            [call.kwargs["codex_reasoning_effort"] for call in calls],
            ["xhigh", "high", "medium"],
        )


if __name__ == "__main__":
    unittest.main()
