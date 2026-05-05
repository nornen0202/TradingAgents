import unittest

from tradingagents.graph.signal_processing import SignalProcessor
from tradingagents.schemas import StructuredDecisionValidationError, parse_structured_decision


class StructuredDecisionTests(unittest.TestCase):
    def test_valid_schema_parses_deterministically(self):
        payload = """
        {
          "rating": "BUY",
          "confidence": 0.78,
          "time_horizon": "medium",
          "entry_logic": "Buy on pullbacks above support.",
          "exit_logic": "Exit on a break below support.",
          "position_sizing": "Half position.",
          "risk_limits": "Risk 1% of capital.",
          "catalysts": ["Earnings beat"],
          "invalidators": ["Guidance cut"]
        }
        """
        decision = parse_structured_decision(payload)
        processor = SignalProcessor()

        self.assertEqual(decision.rating.value, "BUY")
        self.assertEqual(decision.portfolio_stance.value, "BULLISH")
        self.assertEqual(processor.process_signal(payload), "BUY")

    def test_legacy_schema_defaults_new_fields(self):
        payload = """
        {
          "rating": "NO_TRADE",
          "confidence": 0.52,
          "time_horizon": "short",
          "entry_logic": "Wait for setup.",
          "exit_logic": "N/A",
          "position_sizing": "0%",
          "risk_limits": "No new risk.",
          "catalysts": ["Breakout confirmation"],
          "invalidators": ["Support loss"]
        }
        """
        decision = parse_structured_decision(payload)
        self.assertEqual(decision.entry_action.value, "NONE")
        self.assertEqual(decision.data_coverage.social_source.value, "unavailable")
        self.assertEqual(decision.risk_action.value, "NONE")
        self.assertIn("risk_action", decision.to_dict())
        self.assertFalse(decision.profit_taking_plan.enabled)

    def test_profit_taking_plan_parses_and_falls_back_from_level(self):
        payload = """
        {
          "rating": "HOLD",
          "portfolio_stance": "BULLISH",
          "entry_action": "WAIT",
          "risk_action": "TAKE_PROFIT",
          "risk_action_reason_codes": ["EXTENDED_MOVE"],
          "risk_action_level": {
            "label": "extension zone",
            "level_type": "TAKE_PROFIT",
            "price": 131100,
            "confirmation": "intraday",
            "reason_code": "PROFIT_TAKING"
          },
          "profit_taking_plan": {
            "enabled": true,
            "stage_1_fraction": 20,
            "stage_2_price": 135000,
            "stage_2_fraction": 0.30,
            "trailing_stop_price": 121700,
            "keep_core_fraction": 0.45,
            "reentry_condition": "VWAP retest holds",
            "reason_codes": ["RSI_OVERBOUGHT"]
          },
          "setup_quality": "DEVELOPING",
          "confidence": 0.70,
          "time_horizon": "short",
          "entry_logic": "Wait.",
          "exit_logic": "Take staged profit near extension.",
          "position_sizing": "Hold core.",
          "risk_limits": "Use trailing stop.",
          "catalysts": [],
          "invalidators": [],
          "watchlist_triggers": [],
          "data_coverage": {"company_news_count":1,"disclosures_count":0,"social_source":"dedicated","macro_items_count":1}
        }
        """
        decision = parse_structured_decision(payload)

        self.assertTrue(decision.profit_taking_plan.enabled)
        self.assertEqual(decision.profit_taking_plan.stage_1_price, 131100.0)
        self.assertEqual(decision.profit_taking_plan.stage_1_fraction, 0.20)
        self.assertIn("RSI_OVERBOUGHT", decision.profit_taking_plan.reason_codes)

    def test_legacy_underweight_with_risk_text_infers_reduce_risk(self):
        payload = """
        {
          "rating": "UNDERWEIGHT",
          "portfolio_stance": "BEARISH",
          "entry_action": "WAIT",
          "setup_quality": "WEAK",
          "confidence": 0.58,
          "time_horizon": "short",
          "entry_logic": "No fresh entry.",
          "exit_logic": "Reduce if support breaks.",
          "position_sizing": "Lower exposure.",
          "risk_limits": "Close below 95 invalidates the setup.",
          "catalysts": [],
          "invalidators": ["Support broken below 95"],
          "watchlist_triggers": [],
          "data_coverage": {"company_news_count":1,"disclosures_count":0,"social_source":"dedicated","macro_items_count":1}
        }
        """
        decision = parse_structured_decision(payload)
        self.assertEqual(decision.risk_action.value, "REDUCE_RISK")

    def test_risk_action_level_does_not_parse_date_as_range(self):
        payload = """
        {
          "rating": "HOLD",
          "portfolio_stance": "BULLISH",
          "entry_action": "WAIT",
          "risk_action": "TAKE_PROFIT",
          "risk_action_reason_codes": ["PROFIT_TAKING"],
          "risk_action_level": {
            "label": "52-week high trim",
            "level_type": "TAKE_PROFIT",
            "price": 130300,
            "confirmation": "intraday",
            "source_text": "2026-04-27 고점 및 52주 고점 130300 접근 시 일부 이익실현"
          },
          "setup_quality": "DEVELOPING",
          "confidence": 0.70,
          "time_horizon": "short",
          "entry_logic": "Wait.",
          "exit_logic": "Take profit near resistance.",
          "position_sizing": "Hold.",
          "risk_limits": "Use levels.",
          "catalysts": [],
          "invalidators": [],
          "watchlist_triggers": [],
          "data_coverage": {"company_news_count":1,"disclosures_count":0,"social_source":"dedicated","macro_items_count":1}
        }
        """
        decision = parse_structured_decision(payload)

        self.assertEqual(decision.risk_action_level.price, 130300.0)
        self.assertIsNone(decision.risk_action_level.low)
        self.assertIsNone(decision.risk_action_level.high)

    def test_invalid_schema_raises_validation_error(self):
        payload = '{"confidence": 0.5, "time_horizon": "short"}'
        with self.assertRaises(StructuredDecisionValidationError):
            parse_structured_decision(payload)


if __name__ == "__main__":
    unittest.main()
