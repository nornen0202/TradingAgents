import json
from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.graph import END, START, MessagesState, StateGraph

from tradingagents.agents.analysts.fundamentals_analyst import create_fundamentals_analyst
from tradingagents.agents.analysts.market_analyst import create_market_analyst
from tradingagents.agents.analysts.news_analyst import create_news_analyst
from tradingagents.agents.analysts.social_media_analyst import create_social_media_analyst
from tradingagents.agents.utils import core_stock_tools, institutional_data_tools
from tradingagents.graph.trading_graph import TradingAgentsGraph


class CapturingModel:
    def bind_tools(self, tools, **kwargs):
        self.tools = tools
        return RunnableLambda(self.answer)

    def answer(self, prompt):
        self.prompt = prompt.to_string()
        return AIMessage(content="Evidence-based report")


@pytest.mark.parametrize("kind,factory", [
    ("market", create_market_analyst), ("social", create_social_media_analyst),
    ("news", create_news_analyst), ("fundamentals", create_fundamentals_analyst),
])
def test_every_tool_advertised_to_analyst_is_executable(kind, factory):
    model = CapturingModel()
    factory(model)({
        "company_of_interest": "AAPL", "trade_date": "2026-09-29", "analysis_date": "2026-09-30",
        "messages": [ToolMessage(content="Collected evidence", tool_call_id="initial")],
    })
    nodes = TradingAgentsGraph.__new__(TradingAgentsGraph)._create_tool_nodes()
    assert {tool.name: tool for tool in model.tools} == nodes[kind].tools_by_name
    if kind == "market":
        assert "decision date is 2026-09-30" in model.prompt
        assert "daily prices are referenced to 2026-09-29" in model.prompt


def execute_tools(kind, calls):
    node = TradingAgentsGraph.__new__(TradingAgentsGraph)._create_tool_nodes()[kind]
    graph = StateGraph(MessagesState)
    graph.add_node("tools", node)
    graph.add_edge(START, "tools")
    graph.add_edge("tools", END)
    result = graph.compile().invoke({"messages": [AIMessage(content="", tool_calls=calls)]})
    return result["messages"][1:]


def test_intraday_tool_reaches_provider_through_graph(monkeypatch):
    monkeypatch.setattr(core_stock_tools, "fetch_intraday_market_snapshot",
                        lambda symbol, interval: SimpleNamespace(to_dict=lambda: {"symbol": symbol, "last_price": 101.25}))
    messages = execute_tools("market", [{"id": "intraday", "name": "get_intraday_snapshot", "args": {"symbol": "AAPL"}}])
    assert len(messages) == 1
    assert messages[0].status == "success"
    assert json.loads(messages[0].content)["snapshot"]["last_price"] == 101.25


def test_all_eight_institutional_tools_reach_providers_through_graph(monkeypatch):
    monkeypatch.setattr(institutional_data_tools, "render_capability_report",
                        lambda capability, ticker, curr_date: f"Evidence {ticker} {curr_date} {capability}")
    monkeypatch.setattr(institutional_data_tools, "build_public_equity_intelligence",
                        lambda **kwargs: {"earnings_event_pack": {"evidence": kwargs}})
    monkeypatch.setattr(institutional_data_tools, "build_public_equity_intelligence_artifacts", lambda **kwargs: kwargs)
    monkeypatch.setattr(institutional_data_tools, "render_intelligence_markdown", lambda payload: "Evidence " + json.dumps(payload))
    names = ["get_source_linked_financials", "get_estimates_consensus", "get_earnings_event_pack",
             "get_transcript_evidence", "get_peer_comps", "get_credit_risk_context",
             "get_diligence_context", "get_public_equity_intelligence_summary"]
    messages = execute_tools("fundamentals", [
        {"id": name, "name": name, "args": {"ticker": "GLDM", "curr_date": "2026-09-30"}} for name in names
    ])
    assert len(messages) == 8
    for message in messages:
        assert message.status == "success"
        assert "GLDM" in message.content and "2026-09-30" in message.content
        assert "not a valid tool" not in message.content
