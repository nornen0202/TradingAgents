import json
from unittest.mock import Mock

import pytest
from langchain_core.messages import AIMessage
from langgraph.prebuilt import ToolNode

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph import setup as graph_setup_module
from tradingagents.graph.conditional_logic import ConditionalLogic
from tradingagents.graph.propagation import Propagator
from tradingagents.graph.setup import GraphSetup


@pytest.mark.parametrize("parallel_analysts", [False, True])
def test_compiled_graph_uses_astra_for_every_investment_decision(monkeypatch, parallel_analysts):
    """Exercise real decision/debate nodes, replacing only external evidence IO."""
    decision = json.dumps({
        "rating": "HOLD", "portfolio_stance": "NEUTRAL", "entry_action": "WAIT",
        "setup_quality": "DEVELOPING", "confidence": 0.6, "time_horizon": "medium",
        "entry_logic": "Wait for confirmation.", "exit_logic": "Exit if support fails.",
        "position_sizing": "Keep size modest.", "risk_limits": "Use a defined loss budget.",
        "catalysts": [], "invalidators": ["Support break"], "watchlist_triggers": [],
        "data_coverage": {"company_news_count": 0, "disclosures_count": 0,
                          "social_source": "unavailable", "macro_items_count": 0},
    })
    quick = Mock(model=DEFAULT_CONFIG["quick_think_llm"])
    quick.invoke.return_value = AIMessage(content="Dated evidence for discussion.")
    deep = Mock(model=DEFAULT_CONFIG["deep_think_llm"])
    deep.invoke.side_effect = lambda prompt: AIMessage(content=decision)
    memory = Mock()
    memory.get_memories.return_value = []

    def evidence_analyst(llm):
        def run(state):
            response = llm.invoke("Market evidence")
            return {"messages": [response], "market_report": response.content}
        return run

    monkeypatch.setattr(graph_setup_module, "create_market_analyst", evidence_analyst)
    setup = GraphSetup(
        quick, deep, {"market": ToolNode([])}, memory, memory, memory, memory, memory,
        ConditionalLogic(max_debate_rounds=1, max_risk_discuss_rounds=1),
    )
    graph = setup.setup_graph(["market"], parallel_analysts=parallel_analysts)
    result = graph.invoke(Propagator().create_initial_state("AAPL", "2026-10-08"))

    assert deep.model == "gpt-6-astra"
    assert deep.invoke.call_count == 3
    research_prompt, trader_messages, portfolio_prompt = [call.args[0] for call in deep.invoke.call_args_list]
    assert "As the research manager" in research_prompt
    assert "trading agent" in trader_messages[0]["content"]
    assert "As the Portfolio Manager" in portfolio_prompt
    # Each decision is accepted and passed forward with its structured contract intact.
    assert result["investment_plan"] in trader_messages[1]["content"]
    assert result["trader_investment_plan"] in portfolio_prompt
    assert json.loads(result["final_trade_decision"])["entry_action"] == "WAIT"
    assert quick.model == "gpt-6.1-sol"
    assert quick.invoke.call_count == 6  # evidence, two researchers, three risk viewpoints
