import json
import unittest

from tradingagents.scheduled.site import _ticker_investor_summary


def _decision(trigger: str) -> str:
    return json.dumps(
        {
            "rating": "NO_TRADE",
            "portfolio_stance": "BULLISH",
            "entry_action": "WAIT",
            "setup_quality": "DEVELOPING",
            "confidence": 0.7,
            "time_horizon": "medium",
            "entry_logic": "조건 확인",
            "exit_logic": "지지선 이탈",
            "position_sizing": "분할 접근",
            "risk_limits": "손절 기준 준수",
            "catalysts": [],
            "invalidators": ["지지선 이탈"],
            "watchlist_triggers": [trigger],
            "data_coverage": {
                "company_news_count": 3,
                "disclosures_count": 1,
                "social_source": "dedicated",
                "macro_items_count": 1,
            },
        },
        ensure_ascii=False,
    )


class StaleOverlayTodaySummaryTests(unittest.TestCase):
    def test_stale_overlay_keeps_ticker_specific_today_text(self):
        samsung = _ticker_investor_summary(
            {
                "ticker": "005930.KS",
                "ticker_name": "삼성전자",
                "status": "success",
                "analysis_date": "2026-04-16",
                "trade_date": "2026-04-15",
                "finished_at": "2026-04-16T12:34:00+09:00",
                "quality_flags": ["stale_market_data"],
                "decision": _decision("종가 75,000원 상회"),
            },
            {},
        )
        lgcns = _ticker_investor_summary(
            {
                "ticker": "064400.KS",
                "ticker_name": "LG CNS",
                "status": "success",
                "analysis_date": "2026-04-16",
                "trade_date": "2026-04-15",
                "finished_at": "2026-04-16T12:34:00+09:00",
                "quality_flags": ["stale_market_data"],
                "decision": _decision("종가 1,559,000원 돌파"),
            },
            {},
        )

        self.assertNotEqual(samsung["today_action"], lgcns["today_action"])
        self.assertIn("75,000원", samsung["today_action"])
        self.assertIn("1,559,000원", lgcns["today_action"])

    def test_formal_execution_timing_state_drives_investor_wording(self):
        base_summary = {
            "ticker": "005930.KS",
            "ticker_name": "삼성전자",
            "status": "success",
            "analysis_date": "2026-04-16",
            "trade_date": "2026-04-15",
            "finished_at": "2026-04-16T12:34:00+09:00",
            "decision": _decision("종가 75,000원 상회"),
        }

        live_breakout = _ticker_investor_summary(
            {
                **base_summary,
                "execution_update": {
                    "decision_state": "ACTIONABLE_NOW",
                    "execution_timing_state": "LIVE_BREAKOUT",
                },
            },
            {},
            language="Korean",
        )
        close_confirm = _ticker_investor_summary(
            {
                **base_summary,
                "execution_update": {
                    "decision_state": "TRIGGERED_PENDING_CLOSE",
                    "execution_timing_state": "CLOSE_CONFIRM",
                },
            },
            {},
            language="Korean",
        )

        self.assertIn("장중 기준 돌파 구간 진입", live_breakout["today_action"])
        self.assertIn("종가 확인 후 추가 검토", live_breakout["close_action"])
        self.assertIn("종가 확인 대기", close_confirm["today_action"])
        self.assertIn("유지 시 실행 검토", close_confirm["close_action"])


if __name__ == "__main__":
    unittest.main()
