from types import SimpleNamespace

from tradingagents.scheduled.runner import _collect_called_tool_names


def test_collect_called_tool_names_from_dict_and_object_messages():
    state = {
        "messages": [
            {"tool_calls": [{"name": "get_stock_data"}, {"name": "get_indicators"}]},
            SimpleNamespace(tool_calls=[{"name": "get_intraday_snapshot"}]),
        ]
    }
    names = _collect_called_tool_names(state)
    assert names == {"get_stock_data", "get_indicators", "get_intraday_snapshot"}
