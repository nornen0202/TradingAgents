from tradingagents.presentation import present_action_summary, present_primary_condition
from tradingagents.schemas import build_decision_output_instructions


def test_wait_summary_carries_primary_trigger():
    payload = """
    {
      "rating": "HOLD",
      "portfolio_stance": "BULLISH",
      "entry_action": "WAIT",
      "setup_quality": "DEVELOPING",
      "confidence": 0.66,
      "time_horizon": "medium",
      "entry_logic": "Wait for breakout confirmation.",
      "exit_logic": "Exit below support.",
      "position_sizing": "Starter only after confirmation.",
      "risk_limits": "Risk 1R.",
      "catalysts": ["earnings revision"],
      "invalidators": ["support loss"],
      "watchlist_triggers": ["close above 100 with volume"],
      "data_coverage": {
        "company_news_count": 3,
        "disclosures_count": 1,
        "social_source": "dedicated",
        "macro_items_count": 2
      }
    }
    """

    assert present_primary_condition(payload, language="English") == "close above 100 with volume"
    assert (
        present_action_summary(payload, language="English")
        == "Wait for confirmation: close above 100 with volume"
    )


def test_decision_instructions_do_not_flatten_wait_to_no_trade():
    instructions = build_decision_output_instructions("test decision")

    assert "Do not use NO_TRADE solely because entry_action is WAIT" in instructions
    assert "Reserve NO_TRADE" in instructions
