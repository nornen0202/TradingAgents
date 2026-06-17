import unittest
from unittest.mock import Mock

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from tradingagents.agents.analysts.market_analyst import create_market_analyst
from tradingagents.agents.utils.agent_utils import bind_tools_for_analyst, needs_initial_tool_call


class ToolCallPolicyTests(unittest.TestCase):
    def test_needs_initial_tool_call_until_tool_message_exists(self):
        self.assertTrue(needs_initial_tool_call([]))
        self.assertTrue(needs_initial_tool_call([HumanMessage(content="Analyze NVDA")]))
        self.assertTrue(
            needs_initial_tool_call(
                [
                    AIMessage(
                        content="I'll inspect the data first.",
                        tool_calls=[{"name": "get_stock_data", "args": {"ticker": "NVDA"}, "id": "call-1"}],
                    )
                ]
            )
        )

        tool_result = ToolMessage(content="csv ready", tool_call_id="call-1")
        self.assertFalse(needs_initial_tool_call([tool_result]))

        generic_tool = Mock()
        generic_tool.type = "tool"
        self.assertFalse(needs_initial_tool_call([generic_tool]))

    def test_bind_tools_for_analyst_requires_tool_when_supported(self):
        llm = Mock()
        tools = [object()]
        expected = object()
        llm.bind_tools.return_value = expected

        bound = bind_tools_for_analyst(llm, tools, force_tool_call=True)

        self.assertIs(bound, expected)
        llm.bind_tools.assert_called_once_with(tools, tool_choice="required")

    def test_bind_tools_for_analyst_falls_back_when_tool_choice_is_unsupported(self):
        llm = Mock()
        tools = [object()]
        llm.bind_tools.side_effect = [TypeError("unsupported"), "fallback-bound"]

        bound = bind_tools_for_analyst(llm, tools, force_tool_call=True)

        self.assertEqual(bound, "fallback-bound")
        self.assertEqual(llm.bind_tools.call_count, 2)
        self.assertEqual(llm.bind_tools.call_args_list[0].kwargs, {"tool_choice": "required"})
        self.assertEqual(llm.bind_tools.call_args_list[1].args, (tools,))

    def test_bind_tools_for_analyst_skips_requirement_when_not_forced(self):
        llm = Mock()
        tools = [object()]
        llm.bind_tools.return_value = "bound"

        bound = bind_tools_for_analyst(llm, tools, force_tool_call=False)

        self.assertEqual(bound, "bound")
        llm.bind_tools.assert_called_once_with(tools)

    def test_market_analyst_starts_with_deterministic_stock_data_tool_call(self):
        llm = Mock()
        llm.bind_tools.side_effect = AssertionError("initial market data should not invoke the LLM")
        node = create_market_analyst(llm)

        result = node(
            {
                "trade_date": "2026-06-17",
                "company_of_interest": "000660.KS",
                "instrument_profile": {"primary_symbol": "000660.KS"},
                "messages": [HumanMessage(content="Analyze 000660.KS")],
            }
        )

        message = result["messages"][0]
        self.assertEqual(result["market_report"], "")
        self.assertEqual(message.tool_calls[0]["name"], "get_stock_data")
        self.assertEqual(message.tool_calls[0]["args"]["symbol"], "000660.KS")
        self.assertEqual(message.tool_calls[0]["args"]["end_date"], "2026-06-17")
        self.assertEqual(message.tool_calls[0]["args"]["start_date"], "2025-06-12")


if __name__ == "__main__":
    unittest.main()
