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
        processor = SignalProcessor(None)

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

    def test_invalid_schema_raises_validation_error(self):
        payload = '{"confidence": 0.5, "time_horizon": "short"}'
        with self.assertRaises(StructuredDecisionValidationError):
            parse_structured_decision(payload)


if __name__ == "__main__":
    unittest.main()
