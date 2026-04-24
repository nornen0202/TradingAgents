import json

from tradingagents.execution.contract_builder import build_execution_contract


def test_korean_trigger_text_does_not_break_contract():
    decision = {
        "rating": "HOLD",
        "portfolio_stance": "BULLISH",
        "entry_action": "WAIT",
        "setup_quality": "DEVELOPING",
        "confidence": 0.68,
        "time_horizon": "short",
        "entry_logic": "장중 소형 starter만 허용",
        "exit_logic": "무효화 이탈 시 축소",
        "position_sizing": "pilot only",
        "risk_limits": "1R",
        "catalysts": ["조건 확인 전 추격 금지"],
        "invalidators": ["종가 기준 이탈 시 재평가"],
        "watchlist_triggers": ["거래량 확인", "VWAP 회복"],
        "data_coverage": {
            "company_news_count": 1,
            "disclosures_count": 0,
            "social_source": "dedicated",
            "macro_items_count": 1,
        },
        "execution_levels": {
            "intraday_pilot_rule": "10:30 이후 pilot",
            "close_confirm_rule": "종가 확인 후 add",
            "next_day_followthrough_rule": "다음날 초반 유지 확인",
            "failed_breakout_rule": "실패 돌파 시 신규 금지",
            "trim_rule": "지지 이탈 시 축소",
            "levels": [
                {"label": "돌파", "level_type": "breakout", "price": 426000, "confirmation": "intraday"},
                {"label": "지지", "level_type": "support", "low": 418000, "high": 420000, "confirmation": "close"},
                {"label": "무효화", "level_type": "invalidation", "price": 414000, "confirmation": "close"},
            ],
            "min_relative_volume": 1.0,
            "vwap_required": True,
            "earliest_pilot_time_local": "10:30",
            "funding_priority": "medium",
            "entry_window": "mid",
            "trigger_quality": "medium",
        },
    }

    payload = {
        "decision": json.dumps(decision, ensure_ascii=False),
        "finished_at": "2026-04-24T10:00:00+09:00",
        "trade_date": "2026-04-23",
    }

    contract = build_execution_contract(ticker="278470.KS", analysis_payload=payload)

    assert contract.breakout_level == 426000
    assert contract.pullback_buy_zone is not None
    assert contract.pullback_buy_zone.low == 418000
    assert contract.invalid_if_close_below == 414000
    assert contract.structured_levels[0].label == "돌파"
