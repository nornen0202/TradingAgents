import json
import unittest

from tradingagents.execution.contract_builder import build_execution_contract


class NumericExecutionLevelTests(unittest.TestCase):
    def _payload(self, execution_levels):
        decision = {
            "rating": "HOLD",
            "portfolio_stance": "BULLISH",
            "entry_action": "WAIT",
            "setup_quality": "DEVELOPING",
            "confidence": 0.7,
            "time_horizon": "short",
            "entry_logic": "Wait for trigger.",
            "exit_logic": "Trim if support breaks.",
            "position_sizing": "Starter only.",
            "risk_limits": "Use invalidation levels.",
            "catalysts": [],
            "invalidators": [],
            "watchlist_triggers": [],
            "data_coverage": {
                "company_news_count": 1,
                "disclosures_count": 0,
                "social_source": "dedicated",
                "macro_items_count": 1,
            },
            "execution_levels": execution_levels,
        }
        return {
            "decision": json.dumps(decision, ensure_ascii=False),
            "finished_at": "2026-04-24T10:00:00+09:00",
            "trade_date": "2026-04-24",
        }

    def test_numeric_trim_rule_creates_trim_level(self):
        contract = build_execution_contract(
            ticker="AAPL",
            analysis_payload=self._payload({"trim_rule": "Trim if price loses 172.50 on close."}),
        )

        levels = contract.to_dict()["execution_levels"]["levels"]
        self.assertTrue(any(level["level_type"] == "TRIM" and level["price"] == 172.5 for level in levels))

    def test_failed_breakout_rule_creates_reference_and_invalidation_levels(self):
        contract = build_execution_contract(
            ticker="005930.KS",
            analysis_payload=self._payload(
                {"failed_breakout_rule": "If price loses 426,000 after breakout, block new buying and reduce risk."}
            ),
        )

        levels = contract.to_dict()["execution_levels"]["levels"]
        self.assertTrue(any(level["level_type"] == "BREAKOUT" and level["price"] == 426000.0 for level in levels))
        self.assertTrue(any(level["level_type"] == "INVALIDATION" and level["price"] == 426000.0 for level in levels))

    def test_korean_support_range_creates_support_zone(self):
        decision = self._payload({})
        raw = json.loads(decision["decision"])
        raw["watchlist_triggers"] = ["\uc9c0\uc9c0 \uad6c\uac04 21\ub9cc5,500\uc6d0~22\ub9cc\uc6d0 \uc774\ud0c8 \uc2dc \ucd95\uc18c \uac80\ud1a0"]
        decision["decision"] = json.dumps(raw, ensure_ascii=False)

        contract = build_execution_contract(ticker="005930.KS", analysis_payload=decision)
        levels = contract.to_dict()["execution_levels"]["levels"]

        self.assertTrue(any(level["level_type"] == "SUPPORT" and level["low"] == 215500.0 for level in levels))

    def test_date_and_52_week_text_does_not_create_date_range(self):
        contract = build_execution_contract(
            ticker="034020.KS",
            analysis_payload=self._payload(
                {"trim_rule": "2026-04-27 고점 및 52주 고점 130300 접근 시 일부 이익실현 검토"}
            ),
        )

        levels = contract.to_dict()["execution_levels"]["levels"]
        self.assertTrue(any(level["level_type"] == "TRIM" and level["price"] == 130300.0 for level in levels))
        self.assertFalse(any(level.get("low") == 4.0 and level.get("high") == 2026.0 for level in levels))

    def test_market_metrics_are_not_extracted_as_price_levels(self):
        decision = self._payload({})
        raw = json.loads(decision["decision"])
        raw["watchlist_triggers"] = ["RVOL 1.2", "RSI 73.08", "거래량 1,153,302주"]
        decision["decision"] = json.dumps(raw, ensure_ascii=False)

        contract = build_execution_contract(ticker="005930.KS", analysis_payload=decision)
        levels = contract.to_dict()["execution_levels"]["levels"]
        numeric_values = {
            value
            for level in levels
            for value in (level.get("price"), level.get("low"), level.get("high"))
            if value is not None
        }

        self.assertFalse({1.2, 73.08, 1153302.0} & numeric_values)


if __name__ == "__main__":
    unittest.main()
