import json
from datetime import datetime, timezone

import pytest
from langchain_core.messages import AIMessage, RemoveMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.prebuilt import ToolNode

from tradingagents.scheduled.research_observation import ResearchObservationRecorder
from tradingagents.scheduled.decision_bundle import build_decision_bundle
from tradingagents.work.freshness import source_freshness_receipt
from tradingagents.work.packet import compact_decision_bundle, _market_universe_coverage


QUOTE = {"ticker": "ABBV", "asof": "2026-10-02T10:05:00-04:00", "last_price": 200.0,
         "session_vwap": 199.0, "relative_volume": 1.2, "provider": "yfinance",
         "market_session": "regular", "execution_data_quality": "DELAYED_ANALYSIS_ONLY"}


def record(snapshot=None, **payload):
    recorder = ResearchObservationRecorder("ABBV")
    recorder.on_tool_start({"name": "get_intraday_snapshot"}, "", run_id="a")
    recorder.on_tool_end(json.dumps({"ok": True, "symbol": "ABBV", "snapshot": snapshot or QUOTE, **payload}), run_id="a")
    return recorder.receipt()


def test_observation_survives_graph_message_cleanup_and_is_detached():
    @tool
    def get_intraday_snapshot(symbol: str) -> str:
        """Return the host quote."""
        return json.dumps({"ok": True, "symbol": symbol, "snapshot": QUOTE})

    recorder = ResearchObservationRecorder("ABBV")
    graph = StateGraph(MessagesState)
    graph.add_node("tools", ToolNode([get_intraday_snapshot]))
    graph.add_node("clear", lambda state: {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)]})
    graph.add_edge(START, "tools")
    graph.add_edge("tools", "clear")
    graph.add_edge("clear", END)
    state = graph.compile().invoke({"messages": [AIMessage(content="", tool_calls=[
        {"id": "q", "name": "get_intraday_snapshot", "args": {"symbol": "ABBV"}}
    ])]}, config={"callbacks": [recorder]})
    assert state["messages"] == []
    receipt = recorder.receipt()
    assert receipt["market_data_asof"] == QUOTE["asof"]
    receipt["last_price"] = 0
    assert recorder.receipt()["last_price"] == 200


@pytest.mark.parametrize("change", [
    {"asof": "2026-10-02"}, {"asof": "2099-10-02T10:00:00+00:00"},
    {"ticker": "AAPL"}, {"last_price": float("nan")}, {"last_price": 0}, {"last_price": True},
])
def test_invalid_quotes_never_supply_a_market_clock(change):
    receipt = record({**QUOTE, **change})
    assert receipt["status"] == "INVALID"
    assert "market_data_asof" not in receipt


def test_provider_failure_and_unrelated_tools_cannot_supply_a_clock():
    assert record(ok=False, error="private provider payload")["status"] == "UNAVAILABLE"
    recorder = ResearchObservationRecorder("ABBV")
    recorder.on_tool_start({"name": "other_tool"}, "", run_id="x")
    recorder.on_tool_end(json.dumps(QUOTE), run_id="x")
    assert recorder.receipt()["status"] == "NOT_COLLECTED"
    recorder.on_tool_start({"name": "get_intraday_snapshot"}, "", run_id="x")
    recorder.on_tool_error(RuntimeError("private"), run_id="x")
    assert recorder.receipt()["status"] == "UNAVAILABLE"
    assert "private" not in json.dumps(recorder.receipt())


def bundle_for(summary, context=None):
    return build_decision_bundle(run_id="research", market="US", generated_at="2026-10-02T14:10:00+00:00",
                                analysis_source_run_id="research", ticker_summaries=[summary],
                                execution_context=context, benchmark_loader=lambda _: {})


def test_failed_research_retains_quote_and_diagnostic_without_execution_promotion():
    summary = {"ticker": "ABBV", "status": "failed", "research_market_observation": record(),
               "failure_diagnostics": {"failure_category": "STRUCTURED_OUTPUT_ERROR",
                   "exception_class": "CodexStructuredOutputError", "retryability": "UNKNOWN",
                   "error": "private response"}}
    bundle = bundle_for(summary)
    row = bundle["strategy_table"][0]
    assert row["market_data_asof"] == QUOTE["asof"]
    assert row["last_price"] == 200
    assert row["market_data_basis"] == "RESEARCH_OBSERVATION"
    assert row["quality"]["execution_ready"] is False
    assert row["quality"]["conditional_strategy_ready"] is False
    assert bundle["quality"]["decision_ready"] is False
    assert "private" not in json.dumps(bundle)
    compact = compact_decision_bundle(bundle)["strategy_table"][0]
    assert compact["market_data_basis"] == "RESEARCH_OBSERVATION"
    assert compact["failure_diagnostics"]["failure_category"] == "STRUCTURED_OUTPUT_ERROR"
    receipt = source_freshness_receipt({}, bundle, now=datetime(2026, 10, 5, tzinfo=timezone.utc),
                                       analysis_manifest={}, public=False)
    assert receipt["market_data_status"] == "STALE"
    assert receipt["market_data_observed_count"] == receipt["market_data_research_observation_count"] == 1
    coverage = _market_universe_coverage({"tickers": [summary]}, public=False)
    assert coverage["analysis_failures"][0]["failure_category"] == "STRUCTURED_OUTPUT_ERROR"
    assert "analysis_failures" not in _market_universe_coverage({"tickers": [summary]}, public=True)


def test_overlay_clock_and_failed_overlay_are_never_backfilled_from_research():
    summary = {"ticker": "ABBV", "status": "success", "research_market_observation": record()}
    for clock in (None, "2026-10-02T15:00:00+00:00"):
        bundle = bundle_for(summary, {"tickers": [{"ticker": "ABBV", "market_data_asof": clock}]})
        row = bundle["strategy_table"][0]
        assert row["market_data_asof"] == clock
        assert row["market_data_basis"] == "EXECUTION_CONTEXT"
        assert row["last_price"] is None


def test_legacy_archive_cannot_invent_clock_from_report_or_daily_date():
    bundle = bundle_for({"ticker": "ABBV", "status": "success", "trade_date": "2026-10-01",
                         "finished_at": "2026-10-02T15:00:00+00:00"})
    assert bundle["strategy_table"][0]["market_data_asof"] is None
