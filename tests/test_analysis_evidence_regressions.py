from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from cli.stats_handler import StatsCallbackHandler
from tradingagents.agents.utils.agent_states import AgentState
from tradingagents.agents.utils import institutional_data_tools as institutional_tools
from tradingagents.dataflows import institutional
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.llm_clients.codex_schema import normalize_tools_for_codex
from tradingagents.schemas.decision import _parse_price_level


@pytest.mark.parametrize("context", [
    "2026-09-29의 333.99는 당일 실시간 기준이 아니다.",
    "2026/09/29의 10일 이동평균 333.99", "2026.09.29자 333.99",
    "9월29일의 10:30이후 VWAP 333.99", "2026-09-29 closing reference 333.99",
])
def test_dates_with_korean_particles_are_not_price_ranges(context):
    level = _parse_price_level({"level_type": "RESISTANCE", "price": 333.99, "source_text": context})
    assert level.price == 333.99
    assert level.low is None and level.high is None


@pytest.mark.parametrize("context", ["2026-09-29의 10:30이후", "2026년9월29일의 10시30분 이후", "2026-09-29T10:30:00-04:00 기준", "52-week high and 50-day moving average, support"])
def test_real_price_range_survives_neighboring_date_and_clock(context):
    level = _parse_price_level({"level_type": "SUPPORT", "source_text": context + " 320~325 구간"})
    assert (level.low, level.high) == (320, 325)


@pytest.mark.parametrize("fraction", ["25~50%", "25–50%", "25%–50%", "25 to 50 percent", "25~50퍼센트", "12.5~25.5%"])
def test_sale_fraction_is_not_an_inferred_price_range(fraction):
    level = _parse_price_level({
        "level_type": "SUPPORT", "price": 94.72,
        "source_text": f"정규장 종가가 $94.72 아래로 내려가면 보유분의 {fraction}를 위험 축소 목적으로 매도",
    })
    assert level.price == 94.72
    assert level.low is None and level.high is None
    genuine_range = _parse_price_level({
        "level_type": "SUPPORT",
        "source_text": f"Reduce {fraction} in the 92.47~94.72 price zone",
    })
    assert (genuine_range.low, genuine_range.high) == (92.47, 94.72)


def test_constructor_callbacks_reach_real_tool_execution(tmp_path):
    @tool
    def sample_price(symbol: str) -> str:
        """Return a test quote."""
        return "101.25"

    def setup(self, selected_analysts, *, checkpointer=None):
        graph = StateGraph(AgentState)
        graph.add_node("ask", lambda state: {"messages": [AIMessage(content="", tool_calls=[
            {"id": "quote", "name": "sample_price", "args": {"symbol": "AAPL"}}
        ])]})
        graph.add_node("tools", ToolNode([sample_price]))
        graph.add_edge(START, "ask"); graph.add_edge("ask", "tools"); graph.add_edge("tools", END)
        return graph.compile()

    config = deepcopy(DEFAULT_CONFIG)
    config.update(checkpoint_enabled=False, results_dir=str(tmp_path), memory_dir=None)
    stats = StatsCallbackHandler()
    with patch("tradingagents.graph.trading_graph.create_llm_client", return_value=SimpleNamespace(get_llm=lambda: Mock())), patch("tradingagents.graph.setup.GraphSetup.setup_graph", setup):
        graph = TradingAgentsGraph(config=config, selected_analysts=["market"], callbacks=[stats])
        state, args = graph.prepare_run("AAPL", "2026-09-29", analysis_date="2026-09-30")
        graph.graph.invoke(state, **args)
        assert stats.get_stats()["tool_call_counts"] == {"sample_price": 1}
        _, overridden = graph.prepare_run("AAPL", "2026-09-29", callbacks=[])
        assert "callbacks" not in overridden["config"]
        graph.close()


def test_summary_uses_injected_current_context_without_exposing_state_to_model(monkeypatch):
    seen = {}
    monkeypatch.setattr(institutional_tools, "snapshot_tool_telemetry", lambda: [{"vendor": "test", "method": "get_stock_data", "status": "success"}])
    def capture(**kwargs):
        seen.update(kwargs)
        return {"summary": {"source_quality_score": 0.1}}
    monkeypatch.setattr(institutional_tools, "build_public_equity_intelligence_artifacts", capture)
    schema = normalize_tools_for_codex([institutional_tools.get_public_equity_intelligence_summary])[0]
    assert "state" not in schema["function"]["parameters"]["properties"]
    graph = StateGraph(AgentState)
    graph.add_node("tools", ToolNode([institutional_tools.get_public_equity_intelligence_summary]))
    graph.add_edge(START, "tools"); graph.add_edge("tools", END)
    result = graph.compile().invoke({"company_of_interest": "AAPL", "news_report": "Collected report", "messages": [AIMessage(content="", tool_calls=[
        {"id": "summary", "name": "get_public_equity_intelligence_summary", "args": {"ticker": "AAPL", "curr_date": "2026-09-30"}}
    ])]})
    assert result["messages"][-1].status == "success"
    assert seen["final_state"]["news_report"] == "Collected report"
    assert seen["tool_events"][0]["status"] == "success"
    assert "not a final investment decision" in result["messages"][-1].content
    institutional_tools.get_public_equity_intelligence_summary.invoke({"ticker": "MSFT", "curr_date": "2026-09-30", "state": {"company_of_interest": "AAPL"}})
    assert seen["final_state"] == {} and seen["tool_events"] == []


def test_failed_and_repeated_provider_calls_do_not_inflate_quality(monkeypatch):
    monkeypatch.setattr(institutional, "_load_all_imported_payloads", lambda ticker: [])
    success = {"vendor": "yfinance", "method": "get_stock_data", "status": "success"}
    failure = {"vendor": "fred", "method": "get_macro_indicators", "status": "fallback"}
    def score(events):
        return institutional.build_public_equity_intelligence(ticker="AAPL", curr_date="2026-09-30", tool_events=events)["source_quality_score"]
    assert score([failure] * 30) == score([]) == 0
    assert score([success]) == score([success] * 30 + [failure] * 30)
    assert score([success, {**success, "method": "get_fundamentals"}]) > score([success])
