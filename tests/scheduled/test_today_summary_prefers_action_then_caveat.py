import json

from tradingagents.scheduled.site import _ticker_investor_summary


def test_today_summary_prefers_action_then_caveat():
    decision = json.dumps(
        {
            "rating": "NO_TRADE",
            "portfolio_stance": "BULLISH",
            "entry_action": "WAIT",
            "setup_quality": "DEVELOPING",
            "confidence": 0.7,
            "watchlist_triggers": ["종가 266.43 상회"],
            "catalysts": [],
            "invalidators": [],
            "data_coverage": {"company_news_count": 1, "disclosures_count": 0, "social_source": "dedicated", "macro_items_count": 0},
        },
        ensure_ascii=False,
    )
    summary = _ticker_investor_summary(
        {
            "ticker": "NVDA",
            "decision": decision,
            "quality_flags": ["stale_market_data"],
            "execution_update": {"decision_state": "WAIT", "review_required": True},
        },
        {},
        language="Korean",
    )

    assert "조건 확인" in summary["today_action"]
    assert "stale/degraded" in summary["today_action"]
    assert summary["today_action"].endswith("사람 검토 필요.")
