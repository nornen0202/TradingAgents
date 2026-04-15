from tradingagents.scheduled.site import _today_summary


def test_today_label_uses_execution_state_priority():
    actionable = {
        "ticker": "AAPL",
        "decision": '{"rating":"HOLD","portfolio_stance":"BULLISH","entry_action":"WAIT","setup_quality":"DEVELOPING","confidence":0.6,"time_horizon":"medium","entry_logic":"x","exit_logic":"x","position_sizing":"x","risk_limits":"x","catalysts":[],"invalidators":[],"watchlist_triggers":[],"data_coverage":{"company_news_count":1,"disclosures_count":0,"social_source":"news_derived","macro_items_count":0}}',
        "execution_update": {"decision_state": "ACTIONABLE_NOW"},
    }
    triggered = {
        "ticker": "MSFT",
        "decision": actionable["decision"],
        "execution_update": {"decision_state": "TRIGGERED_PENDING_CLOSE"},
    }
    assert _today_summary(actionable, language="Korean") == "오늘 바로 검토"
    assert _today_summary(triggered, language="Korean") == "종가 확인 필요"
