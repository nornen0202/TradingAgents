from collections import Counter
from threading import Barrier, Lock
from unittest.mock import Mock

import pytest
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.errors import GraphRecursionError
from langgraph.prebuilt import ToolNode

from tradingagents.dataflows.config import get_config, run_config
from tradingagents.graph import setup as graph_setup_module
from tradingagents.graph.conditional_logic import ConditionalLogic
from tradingagents.graph.setup import GraphSetup, _analyst_subgraph


def _setup(monkeypatch, analysts, tools, researcher):
    for kind, analyst in analysts.items():
        factory = {"market": "create_market_analyst", "news": "create_news_analyst"}[kind]
        monkeypatch.setattr(graph_setup_module, factory, lambda *args, node=analyst: node)
    monkeypatch.setattr(graph_setup_module, "create_bull_researcher", lambda *args: researcher)
    for factory in (
        "create_bear_researcher", "create_research_manager", "create_trader",
        "create_aggressive_debator", "create_conservative_debator", "create_neutral_debator",
    ):
        monkeypatch.setattr(graph_setup_module, factory, lambda *args: lambda state: {})
    monkeypatch.setattr(graph_setup_module, "create_portfolio_manager", lambda *args: lambda state: {"final_trade_decision": "HOLD"})
    return GraphSetup(Mock(), Mock(), tools, None, None, None, None, None, ConditionalLogic(0, 0))


def _initial_state():
    return {
        "messages": [("human", "AAPL")], "company_of_interest": "AAPL",
        "trade_date": "2024-01-01", "market_report": "", "news_report": "",
        "investment_debate_state": {"count": 0}, "risk_debate_state": {"count": 0},
    }


def test_parallel_branches_isolate_tool_messages_and_wait_for_all_reports(monkeypatch):
    barrier = Barrier(2)
    lock = Lock()
    active = 0
    peak = 0
    seen_cutoffs = []
    research_inputs = []

    @tool
    def evidence(source: str) -> str:
        """Return branch-specific test evidence."""
        nonlocal active, peak
        with lock:
            active += 1
            peak = max(peak, active)
        barrier.wait(timeout=10)
        seen_cutoffs.append(get_config()["analysis_as_of"])
        with lock:
            active -= 1
        return source + " evidence"

    def analyst(kind):
        def run(state):
            messages = state["messages"]
            if isinstance(messages[-1], ToolMessage):
                assert messages[-1].content == kind + " evidence"
                assert len(messages) == 3
                return {"messages": [AIMessage(content=kind)], kind + "_report": kind + " report"}
            assert len(messages) == 1
            return {"messages": [AIMessage(content="", tool_calls=[
                {"name": "evidence", "args": {"source": kind}, "id": kind},
            ])]}
        return run

    def researcher(state):
        research_inputs.append((state["market_report"], state["news_report"]))
        assert len(state["messages"]) == 1
        return {}

    setup = _setup(monkeypatch, {kind: analyst(kind) for kind in ("market", "news")},
                   {kind: ToolNode([evidence]) for kind in ("market", "news")}, researcher)
    graph = setup.setup_graph(["market", "news"], parallel_analysts=True)
    with run_config({"analysis_as_of": "2024-01-01"}):
        result = graph.invoke(_initial_state(), {"max_concurrency": 2})
    assert result["final_trade_decision"] == "HOLD"
    assert research_inputs == [("market report", "news report")]
    assert seen_cutoffs == ["2024-01-01", "2024-01-01"]
    assert peak == 2


def test_parallel_checkpoint_resumes_failed_branch_without_repeating_completed_one(monkeypatch):
    calls = Counter()

    def market(state):
        calls["market"] += 1
        return {"messages": [AIMessage(content="market")], "market_report": "saved"}

    def news(state):
        calls["news"] += 1
        if calls["news"] == 1:
            raise RuntimeError("interrupted source")
        return {"messages": [AIMessage(content="news")], "news_report": "resumed"}

    def research(state):
        calls["research"] += 1
        assert state["market_report"] == "saved" and state["news_report"] == "resumed"
        return {}

    setup = _setup(monkeypatch, {"market": market, "news": news},
                   {kind: ToolNode([]) for kind in ("market", "news")}, research)
    graph = setup.setup_graph(["market", "news"], checkpointer=InMemorySaver(), parallel_analysts=True)
    config = {"configurable": {"thread_id": "parallel-resume"}, "max_concurrency": 2}
    with pytest.raises(RuntimeError, match="interrupted source"):
        graph.invoke(_initial_state(), config)
    assert calls["research"] == 0
    result = graph.invoke(None, config)
    assert result["final_trade_decision"] == "HOLD"
    assert calls == {"market": 1, "news": 2, "research": 1}


def test_sequential_default_keeps_prior_report_context(monkeypatch):
    seen = []

    def market(state):
        seen.append("market")
        return {"messages": [AIMessage(content="market")], "market_report": "prior evidence"}

    def news(state):
        seen.append("news")
        assert state["market_report"] == "prior evidence"
        assert len(state["messages"]) == 1
        return {"messages": [AIMessage(content="news")], "news_report": "new evidence"}

    setup = _setup(monkeypatch, {"market": market, "news": news},
                   {kind: ToolNode([]) for kind in ("market", "news")}, lambda state: {})
    result = setup.setup_graph(["market", "news"]).invoke(_initial_state())
    assert result["final_trade_decision"] == "HOLD"
    assert seen == ["market", "news"]


@pytest.mark.parametrize("selected", [[], ["market", "market"], ["unknown"]])
def test_invalid_analyst_selection_fails_before_building_nodes(selected):
    setup = GraphSetup(Mock(), Mock(), {}, None, None, None, None, None, ConditionalLogic())
    with pytest.raises(ValueError):
        setup.setup_graph(selected, parallel_analysts=True)


def test_parallel_tool_loop_respects_recursion_budget():
    @tool
    def repeat() -> str:
        """A tool for testing an analyst that never finishes."""
        return "evidence"

    def looping(state):
        return {"messages": [AIMessage(content="", tool_calls=[
            {"name": "repeat", "args": {}, "id": str(len(state["messages"]))},
        ])]}

    graph = _analyst_subgraph("market", looping, ToolNode([repeat]))
    with pytest.raises(GraphRecursionError):
        graph.invoke(_initial_state(), {"recursion_limit": 6})
