from collections import Counter
from unittest.mock import Mock

import pytest
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode

from tradingagents.graph import setup as graph_setup_module
from tradingagents.graph.analyst_safety import bounded_analyst, completed_tool_rounds
from tradingagents.graph.conditional_logic import ConditionalLogic
from tradingagents.graph.setup import GraphSetup


def _initial_state():
    return {
        "messages": [("human", "AAPL")], "company_of_interest": "AAPL",
        "trade_date": "2024-01-01", "market_report": "", "news_report": "",
        "investment_debate_state": {"count": 0}, "risk_debate_state": {"count": 0},
    }


def _setup(monkeypatch, analysts, tools, llm, researcher=lambda state: {}):
    for kind, analyst in analysts.items():
        monkeypatch.setattr(graph_setup_module, f"create_{kind}_analyst", lambda *args, node=analyst: node)
    monkeypatch.setattr(graph_setup_module, "create_bull_researcher", lambda *args: researcher)
    for factory in (
        "create_bear_researcher", "create_research_manager", "create_trader",
        "create_aggressive_debator", "create_conservative_debator", "create_neutral_debator",
    ):
        monkeypatch.setattr(graph_setup_module, factory, lambda *args: lambda state: {})
    monkeypatch.setattr(graph_setup_module, "create_portfolio_manager", lambda *args: lambda state: {"final_trade_decision": "HOLD"})
    return GraphSetup(llm, Mock(), tools, None, None, None, None, None, ConditionalLogic(0, 0), max_tool_rounds=2)


@pytest.mark.parametrize("parallel", [False, True])
def test_empty_data_loops_finalize_with_private_per_analyst_budgets(monkeypatch, parallel):
    calls = Counter()

    @tool
    def missing(source: str) -> str:
        """Simulate a vendor without data for the requested instrument."""
        calls[source] += 1
        return f"{source}: no data available"

    def analyst(kind):
        def run(state):
            return {"messages": [AIMessage(content="", tool_calls=[{
                "name": "missing", "args": {"source": kind},
                "id": f"{kind}-{len(state['messages'])}",
            }])]}
        return run

    def finalize(messages, config):
        kind = "market" if "market analyst" in messages[0].content else "news"
        evidence = [m.content for m in messages if isinstance(m, ToolMessage)]
        assert evidence == [f"{kind}: no data available"] * 2
        assert "without requesting more tools" in messages[-1].content
        return AIMessage(content=f"{kind}: insufficient data; collection limit reached")

    research_calls = []

    def researcher(state):
        research_calls.append(state)
        assert state["market_report"].startswith("market: insufficient data")
        assert state["news_report"].startswith("news: insufficient data")
        return {}

    llm = Mock()
    llm.invoke.side_effect = finalize
    setup = _setup(monkeypatch, {k: analyst(k) for k in ("market", "news")},
                   {k: ToolNode([missing]) for k in ("market", "news")}, llm, researcher)
    result = setup.setup_graph(["market", "news"], parallel_analysts=parallel).invoke(_initial_state())
    assert result["final_trade_decision"] == "HOLD"
    assert calls == {"market": 2, "news": 2}
    assert llm.invoke.call_count == 2
    assert llm.bind_tools.call_count == 0
    assert len(research_calls) == 1


def test_tool_batch_counts_as_one_round_and_unanswered_requests_do_not_count():
    request = AIMessage(content="", tool_calls=[
        {"name": "one", "args": {}, "id": "a"},
        {"name": "two", "args": {}, "id": "b"},
    ])
    assert completed_tool_rounds([request]) == 0
    assert completed_tool_rounds([request, ToolMessage(content="no data", tool_call_id="a")]) == 0
    assert completed_tool_rounds([request, ToolMessage(content="no data", tool_call_id="a"),
                                  ToolMessage(content="error", tool_call_id="b")]) == 1


def test_finalization_discards_provider_tool_requests_and_retains_evidence():
    llm = Mock()
    llm.invoke.return_value = AIMessage(content="", tool_calls=[{"name": "again", "args": {}, "id": "discard"}])
    analyst = Mock()
    node = bounded_analyst(analyst, kind="market", report_key="market_report", llm=llm, max_tool_rounds=1)
    state = _initial_state()
    state["messages"] = [AIMessage(content="", tool_calls=[{"name": "price", "args": {}, "id": "done"}]),
                         ToolMessage(content="price source unavailable", tool_call_id="done", name="price")]
    result = node(state, {})
    assert "price source unavailable" in result["market_report"]
    assert "does not establish an investment recommendation" in result["market_report"]
    assert result["messages"][-1].tool_calls == []
    analyst.assert_not_called()


@pytest.mark.parametrize("parallel", [False, True])
def test_completed_round_budget_survives_checkpoint_resume(monkeypatch, parallel):
    calls = Counter()

    @tool
    def evidence() -> str:
        """Return no data to exercise the bounded loop."""
        calls["tool"] += 1
        return "no data"

    def analyst(state):
        calls["analyst"] += 1
        if completed_tool_rounds(state["messages"]) == 1 and calls["analyst"] == 2:
            raise RuntimeError("interrupted analyst")
        return {"messages": [AIMessage(content="", tool_calls=[{
            "name": "evidence", "args": {}, "id": str(len(state["messages"])),
        }])]}

    llm = Mock()
    llm.invoke.return_value = AIMessage(content="Incomplete evidence; limit reached")
    setup = _setup(monkeypatch, {"market": analyst}, {"market": ToolNode([evidence])}, llm)
    graph = setup.setup_graph(["market"], checkpointer=InMemorySaver(), parallel_analysts=parallel)
    config = {"configurable": {"thread_id": "bounded-resume"}}
    with pytest.raises(RuntimeError, match="interrupted analyst"):
        graph.invoke(_initial_state(), config)
    result = graph.invoke(None, config)
    assert result["market_report"].startswith("Incomplete evidence; limit reached")
    assert "collection stopped at the configured limit" in result["market_report"]
    assert calls["tool"] == 2
    assert llm.invoke.call_count == 1


@pytest.mark.parametrize("limit", [0, -1, 1.5, "2", True, None])
def test_invalid_tool_round_limit_is_rejected(limit):
    with pytest.raises(ValueError, match="max_tool_rounds"):
        GraphSetup(Mock(), Mock(), {}, None, None, None, None, None, ConditionalLogic(), max_tool_rounds=limit)
