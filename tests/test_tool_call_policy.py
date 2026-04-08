import unittest

from langchain_core.messages import HumanMessage, ToolMessage

from tradingagents.agents.utils.agent_utils import bind_tools_for_analyst, needs_initial_tool_call


class _FakeBound:
    def __init__(self, kwargs):
        self.kwargs = kwargs


class _FakeLLM:
    def __init__(self):
        self.last_kwargs = None

    def bind_tools(self, tools, **kwargs):
        self.last_kwargs = kwargs
        return _FakeBound(kwargs)


class _FakeLLMNoToolChoice:
    def bind_tools(self, tools, **kwargs):
        if "tool_choice" in kwargs:
            raise TypeError("unsupported")
        return _FakeBound(kwargs)


class ToolCallPolicyTests(unittest.TestCase):
    def test_needs_initial_tool_call_true_without_tool_messages(self):
        self.assertTrue(needs_initial_tool_call([HumanMessage(content="start")]))

    def test_needs_initial_tool_call_false_after_tool_message(self):
        messages = [HumanMessage(content="start"), ToolMessage(content="ok", tool_call_id="id-1")]
        self.assertFalse(needs_initial_tool_call(messages))

    def test_bind_tools_for_analyst_requires_tool_when_supported(self):
        llm = _FakeLLM()
        bind_tools_for_analyst(llm, tools=[], force_tool_call=True)
        self.assertEqual(llm.last_kwargs.get("tool_choice"), "required")

    def test_bind_tools_for_analyst_falls_back_when_tool_choice_unsupported(self):
        llm = _FakeLLMNoToolChoice()
        bound = bind_tools_for_analyst(llm, tools=[], force_tool_call=True)
        self.assertEqual(bound.kwargs, {})


if __name__ == "__main__":
    unittest.main()
