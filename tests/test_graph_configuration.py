import unittest
from copy import deepcopy
from unittest.mock import Mock, patch

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph


class _DummyClient:
    def __init__(self):
        self._llm = Mock()

    def get_llm(self):
        return self._llm


class GraphConfigurationTests(unittest.TestCase):
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
            "gpt-5.6-sol",
            "gpt-5.6-terra",
            "gpt-5.6-luna",
        ])
        self.assertEqual([call.kwargs["model_role"] for call in calls], ["deep", "quick", "output"])
        self.assertEqual(
            [call.kwargs["codex_reasoning_effort"] for call in calls],
            ["medium", "low", "low"],
        )


if __name__ == "__main__":
    unittest.main()
