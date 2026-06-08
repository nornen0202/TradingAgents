from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from tradingagents.agents.utils.agent_utils import (
    bind_tools_for_analyst,
    build_instrument_context,
    get_balance_sheet,
    get_cashflow,
    get_credit_risk_context,
    get_diligence_context,
    get_earnings_event_pack,
    get_estimates_consensus,
    get_fundamentals,
    get_income_statement,
    get_insider_transactions,
    get_language_instruction,
    needs_initial_tool_call,
    get_peer_comps,
    get_public_equity_intelligence_summary,
    get_source_linked_financials,
    get_transcript_evidence,
)


def create_fundamentals_analyst(llm):
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        instrument_context = build_instrument_context(
            state["company_of_interest"],
            state.get("instrument_profile"),
        )

        tools = [
            get_fundamentals,
            get_balance_sheet,
            get_cashflow,
            get_income_statement,
            get_insider_transactions,
            get_source_linked_financials,
            get_estimates_consensus,
            get_earnings_event_pack,
            get_transcript_evidence,
            get_peer_comps,
            get_credit_risk_context,
            get_diligence_context,
            get_public_equity_intelligence_summary,
        ]

        system_message = (
            "You are a fundamentals analyst focused on medium-term business quality and event risk. "
            "Center the report on recent disclosures, earnings quality, guidance changes, capital structure, cash flow, margins, insider transactions, and any notable balance-sheet shifts. "
            "Use `get_fundamentals(ticker, curr_date)` for the overview, `get_balance_sheet`, `get_cashflow`, and `get_income_statement` for statement detail, and `get_insider_transactions(ticker)` for insider activity. "
            "Use the institutional tools to strengthen reliability: `get_source_linked_financials`, `get_earnings_event_pack`, `get_estimates_consensus`, `get_transcript_evidence`, `get_peer_comps`, `get_credit_risk_context`, `get_diligence_context`, and `get_public_equity_intelligence_summary`. "
            "Tag important numbers and claims with the provider or source type that supports them. Explicitly state when transcript, consensus, credit, or diligence data is unavailable instead of inferring it. "
            "Separate company-thesis evidence from security-thesis readiness, and call out whether new evidence strengthens, weakens, or leaves the thesis unchanged. "
            "Do not frame this as only a past-week exercise; emphasize the latest reported fundamentals and the most recent event-driven changes that matter for traders."
            " End with a Markdown table summarizing the main fundamental strengths, weaknesses, watch items, source status, and missing-data limitations."
            + get_language_instruction()
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK; another assistant with different tools"
                    " will help where you left off. Execute what you can to make progress."
                    " Return the completed fundamentals report directly once you have enough evidence."
                    " You have access to the following tools: {tool_names}.\n{system_message}"
                    " For your reference, the current date is {current_date}. {instrument_context}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(instrument_context=instrument_context)

        chain = prompt | bind_tools_for_analyst(
            llm,
            tools,
            force_tool_call=needs_initial_tool_call(state["messages"]),
        )
        result = chain.invoke(state["messages"])

        report = ""
        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node
