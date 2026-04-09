import unittest
from unittest.mock import Mock

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

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


if __name__ == "__main__":
    unittest.main()
