"""Bound analyst data collection while preserving a usable final report."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from tradingagents.agents.utils.agent_utils import get_language_instruction


def completed_tool_rounds(messages):
    """Count request batches with results, rather than individual tool calls."""
    answered = {
        message.tool_call_id
        for message in messages
        if isinstance(message, ToolMessage)
    }
    return sum(
        bool(calls := getattr(message, "tool_calls", None))
        and all(call.get("id") in answered for call in calls)
        for message in messages
    )


def _text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block if isinstance(block, str) else str(block.get("text", ""))
            for block in content
            if isinstance(block, (str, dict))
        )
    return ""


def bounded_analyst(analyst, *, kind, report_key, llm, max_tool_rounds):
    """Use one tool-free completion when this analyst exhausts its budget.

    Messages are reset between sequential analysts and private in parallel
    subgraphs, so the budget belongs to one analyst and survives checkpoints.
    """
    if (
        isinstance(max_tool_rounds, bool)
        or not isinstance(max_tool_rounds, int)
        or max_tool_rounds < 1
    ):
        raise ValueError("max_tool_rounds must be a positive integer")

    def run(state, config):
        messages = state.get("messages", [])
        if completed_tool_rounds(messages) < max_tool_rounds:
            return analyst(state)

        result = llm.invoke(
            [
                SystemMessage(
                    content=f"You are the {kind} analyst. Write the completed report "
                    "using only the evidence already collected. Tools are unavailable. "
                    "Explicitly disclose missing data and uncertainty; do not invent evidence."
                    + get_language_instruction()
                ),
                *messages,
                HumanMessage(
                    content=f"The data collection limit ({max_tool_rounds} tool rounds) "
                    f"has been reached for {state['company_of_interest']} as of "
                    f"{state.get('analysis_date') or state['trade_date']}. "
                    "Return your final report now without requesting more tools. "
                    "State that collection was limited and ground conclusions in available results."
                ),
            ],
            config=config,
        )
        report = _text(result.content).strip()
        if report:
            report += (
                "\n\nData availability: collection stopped at the configured limit; "
                "this report may be incomplete."
            )
        else:
            # Some provider wrappers can still return tool requests even without
            # bound tools. Never execute those or silently pass an empty report.
            evidence = [
                f"{message.name or 'Tool'}: {_text(message.content)[:2000]}"
                for message in messages
                if isinstance(message, ToolMessage)
            ]
            report = (
                f"Data collection stopped after {max_tool_rounds} tool rounds. "
                "No final analyst synthesis was returned; the available tool evidence "
                "below is incomplete and does not establish an investment recommendation.\n\n"
                + "\n\n".join(evidence)
            )
        # A new message deliberately drops any provider-returned tool_calls so
        # routers terminate and never leave unanswered tool requests in state.
        return {"messages": [AIMessage(content=report)], report_key: report}

    return run
