from tradingagents.agents.utils.agent_utils import (
    build_instrument_context,
    get_language_instruction,
    get_memory_matches,
)
from tradingagents.schemas import build_decision_output_instructions, ensure_structured_decision_json


def create_portfolio_manager(llm, memory):
    def portfolio_manager_node(state) -> dict:
        instrument_context = build_instrument_context(
            state["company_of_interest"],
            state.get("instrument_profile"),
        )

        history = state["risk_debate_state"]["history"]
        risk_debate_state = state["risk_debate_state"]
        market_research_report = state["market_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        sentiment_report = state["sentiment_report"]
        research_plan = state["investment_plan"]
        trader_plan = state["trader_investment_plan"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = get_memory_matches(memory, curr_situation)

        past_memory_str = ""
        for rec in past_memories:
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""As the Portfolio Manager, synthesize the risk analysts' debate and deliver the final trading decision.

{instrument_context}

Use the common decision schema and be explicit about rating (legacy), portfolio_stance, entry_action, setup_quality, confidence, time horizon, entry logic, exit logic, position sizing, risk limits, catalysts, invalidators, watchlist_triggers, data_coverage, and execution_levels.
NO_TRADE is allowed as a legacy rating, but do not collapse all outcomes into NO_TRADE.
Always distinguish: (1) directional stance, (2) immediate entry decision, (3) watchlist maintenance triggers, and (4) whether a starter could be justified when conditions are met.
For regular-session investors, split execution_levels into intraday_pilot_rule, close_confirm_rule, next_day_followthrough_rule, failed_breakout_rule, trim_rule, numeric levels[], min_relative_volume, vwap_required, earliest_pilot_time_local, funding_priority, entry_window, and trigger_quality.
Always provide machine-actionable execution_levels.levels with numeric price or range fields whenever the thesis contains a concrete trigger, support, invalidation, trim, or resistance area.
Intraday pilot means a small starter only; full-size add/entry belongs in close_confirm_rule or next_day_followthrough_rule.
If the thesis is constructive but timing is incomplete, keep stance constructive, set entry_action=WAIT, and choose HOLD or OVERWEIGHT as the legacy rating when the view remains investable.
Reserve NO_TRADE for weak, contradictory, or insufficient evidence, no favorable setup to monitor, or data quality gaps that make the view non-investable.
If the thesis is constructive and timing is confirmed today, allow BUY or OVERWEIGHT rather than defaulting to HOLD/NO_TRADE.

Context:
- Research Manager investment plan JSON: {research_plan}
- Trader execution plan JSON: {trader_plan}
- Lessons from past decisions: {past_memory_str or "No past reflections available."}

Risk Analysts Debate History:
{history}

Ground every conclusion in specific evidence from the analysts. {get_language_instruction()}
{build_decision_output_instructions("portfolio manager final decision")}"""

        response = llm.invoke(prompt)
        decision_json = ensure_structured_decision_json(response.content)

        new_risk_debate_state = {
            "judge_decision": decision_json,
            "history": risk_debate_state["history"],
            "aggressive_history": risk_debate_state["aggressive_history"],
            "conservative_history": risk_debate_state["conservative_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "Judge",
            "current_aggressive_response": risk_debate_state["current_aggressive_response"],
            "current_conservative_response": risk_debate_state["current_conservative_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
        }

        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": decision_json,
        }

    return portfolio_manager_node
