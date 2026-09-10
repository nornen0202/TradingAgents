from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from langgraph.graph import StateGraph, START, END

from tradingagents.agents.utils.agent_states import AgentState
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph


def test_sqlite_resume_does_not_rerun_completed_nodes_and_config_isolated(tmp_path):
    calls = []
    fail = [True]
    def setup(self, selected_analysts, *, checkpointer=None):
        workflow = StateGraph(AgentState)
        def first(state):
            calls.append("first")
            return {"market_report": "grounded"}
        def second(state):
            calls.append("second")
            if fail[0]:
                fail[0] = False
                raise RuntimeError("interrupted")
            return {"news_report": "done"}
        workflow.add_node("first", first)
        workflow.add_node("second", second)
        workflow.add_edge(START, "first")
        workflow.add_edge("first", "second")
        workflow.add_edge("second", END)
        return workflow.compile(checkpointer=checkpointer)
    config = deepcopy(DEFAULT_CONFIG)
    config.update(checkpoint_enabled=True, checkpoint_dir=str(tmp_path), memory_dir=None)
    with patch("tradingagents.graph.trading_graph.create_llm_client", return_value=SimpleNamespace(get_llm=lambda: Mock())), patch("tradingagents.graph.setup.GraphSetup.setup_graph", setup):
        graph = TradingAgentsGraph(config=config, selected_analysts=["market"])
        state, args = graph.prepare_run("AAPL", "2026-03-02")
        with pytest.raises(RuntimeError, match="interrupted"):
            graph.graph.invoke(state, **args)
        graph.close()
        graph = TradingAgentsGraph(config=config, selected_analysts=["market"])
        state, args = graph.prepare_run("AAPL", "2026-03-02")
        assert state is None
        result = graph.graph.invoke(state, **args)
        assert result["market_report"] == "grounded"
        assert result["news_report"] == "done"
        assert calls == ["first", "second", "second"]
        graph.close()
        config["deep_think_llm"] = "gpt-5.5"
        graph = TradingAgentsGraph(config=config, selected_analysts=["market"])
        state, _ = graph.prepare_run("AAPL", "2026-03-02")
        assert state is not None
        graph.close()
