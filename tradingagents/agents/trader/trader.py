import functools

from tradingagents.agents.utils.agent_utils import build_instrument_context, get_memory_matches
from tradingagents.agents.utils.decision_retry import invoke_structured_decision_with_retry
from tradingagents.schemas import build_decision_output_instructions


def create_trader(llm, memory):
    def trader_node(state, name):
        company_name = state["company_of_interest"]
        instrument_context = build_instrument_context(company_name, state.get("instrument_profile"))
        investment_plan = state["investment_plan"]
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = get_memory_matches(memory, curr_situation)

        past_memory_str = ""
        if past_memories:
            for rec in past_memories:
                past_memory_str += rec["recommendation"] + "\n\n"
        else:
            past_memory_str = "No past memories found."

        context = {
            "role": "user",
            "content": (
                f"Based on a comprehensive analysis by a team of analysts, here is an investment plan tailored for {company_name}. "
                f"{instrument_context} This plan incorporates insights from market trends, macro context, sentiment, news, and fundamentals. "
                f"Use this plan as a foundation for your execution decision.\n\nProposed Investment Plan JSON: {investment_plan}\n\n"
                f"Technical market report (price/volume source): {market_research_report}\n\n"
                f"Fundamentals and valuation: {fundamentals_report}\n\n"
                f"News and event risks: {news_report}\n\n"
                f"Sentiment and coverage limits: {sentiment_report}\n\n"
                f"Analysis as-of date: {state.get('trade_date', 'unknown')}. "
                "Anchor all entry, stop and target prices to dated evidence in these reports. "
                "Do not manufacture missing prices, upcoming earnings dates, or a calibrated win probability. "
                "Compare the opportunity with a diversified regional ETF and holding cash, including fees, spread and slippage. "
                "If price evidence is missing or contradictory, keep entry_action=WAIT and say what must be verified."
            ),
        }

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a trading agent analyzing market data to make execution-ready investment decisions. "
                    "Translate the research manager's view into a concrete trade recommendation with entry logic, exit logic, position sizing, risk limits, catalysts, and invalidators. "
                    "Keep entry_action and risk_action separate: entry_action is the buy-side/new-entry decision, while risk_action captures held-position trimming, profit-taking, stop-loss, or exit risk. "
                    "Do not use TRIM_TO_FUND for thesis damage, support breaks, failed breakouts, or stop-loss events; use REDUCE_RISK, STOP_LOSS, TAKE_PROFIT, or EXIT with reason codes and numeric levels when applicable. "
                    "When the thesis is constructive but the setup is not actionable yet, keep entry_action=WAIT and provide explicit triggers instead of flattening the legacy rating to NO_TRADE. "
                    "Use NO_TRADE only when there is no favorable setup to monitor, the risk/reward is clearly unfavorable, or the evidence quality is too weak for an investable view. "
                    "When setup quality is compelling and timing is confirmed, allow BUY or OVERWEIGHT rather than defaulting to NO_TRADE or HOLD. "
                    "Confidence describes strength of evidence, not the probability of profit. Position sizing must respect a defined loss budget, existing concentration and cash. "
                    f"Apply lessons from similar situations: {past_memory_str} "
                    f"{build_decision_output_instructions('trader execution plan')}"
                ),
            },
            context,
        ]

        result, decision_json = invoke_structured_decision_with_retry(
            llm,
            messages,
            context="trader execution plan",
        )

        return {
            "messages": [result],
            "trader_investment_plan": decision_json,
            "sender": name,
        }

    return functools.partial(trader_node, name="Trader")
