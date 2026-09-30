from types import SimpleNamespace

from tradingagents.scheduled.runner import _collect_called_tool_names
from cli.stats_handler import StatsCallbackHandler
from langchain_core.messages import AIMessage, RemoveMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.prebuilt import ToolNode


def test_collect_called_tool_names_from_dict_and_object_messages():
    state = {
        "messages": [
            {"tool_calls": [{"name": "get_stock_data"}, {"name": "get_indicators"}]},
            SimpleNamespace(tool_calls=[{"name": "get_intraday_snapshot"}]),
        ]
    }
    names = _collect_called_tool_names(state)
    assert names == {"get_stock_data", "get_indicators", "get_intraday_snapshot"}


def test_executed_tool_names_survive_analyst_message_cleanup():
    @tool
    def get_intraday_snapshot(symbol: str) -> str:
        """Return a deliberately unavailable snapshot to distinguish call from source success."""
        return '{"ok":false,"error":"provider unavailable"}'

    stats = StatsCallbackHandler()
    graph = StateGraph(MessagesState)
    graph.add_node("tools", ToolNode([get_intraday_snapshot]))
    graph.add_node("clear", lambda state: {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)]})
    graph.add_edge(START, "tools")
    graph.add_edge("tools", "clear")
    graph.add_edge("clear", END)
    final_state = graph.compile().invoke({"messages": [AIMessage(content="", tool_calls=[
        {"id": "snapshot", "name": "get_intraday_snapshot", "args": {"symbol": "AAPL"}}
    ])]}, config={"callbacks": [stats]})
    assert final_state["messages"] == []
    assert stats.get_stats()["tool_call_counts"] == {"get_intraday_snapshot": 1}
    assert _collect_called_tool_names(final_state, metrics=stats.get_stats()) == {"get_intraday_snapshot"}
    # A reader cannot accidentally mutate the handler's durable counts.
    stats.get_stats()["tool_call_counts"]["invented"] = 3
    assert "invented" not in stats.get_stats()["tool_call_counts"]
