import unittest

from tradingagents.scheduled.runner import _compute_batch_warnings


class SellSideAuditWarningTests(unittest.TestCase):
    def test_support_fail_with_zero_reduce_risk_warns(self):
        warnings = _compute_batch_warnings(
            {
                "decision_distribution": {"HOLD": 10},
                "stance_distribution": {"BULLISH": 10},
                "entry_action_distribution": {"WAIT": 10},
                "sell_side_distribution": {"REDUCE_RISK": 0},
                "support_fail_count": 1,
                "numeric_trigger_text_empty_levels_ratio": 0.0,
            }
        )

        self.assertIn("sell_side_missed_support_fail", warnings)
        self.assertIn("bullish_wait_concentration", warnings)

    def test_numeric_level_extraction_warning_is_nonfatal(self):
        warnings = _compute_batch_warnings(
            {
                "decision_distribution": {"HOLD": 10},
                "stance_distribution": {"NEUTRAL": 10},
                "entry_action_distribution": {"WAIT": 10},
                "sell_side_distribution": {"REDUCE_RISK": 0},
                "support_fail_count": 0,
                "numeric_trigger_text_empty_levels_ratio": 0.5,
            }
        )

        self.assertIn("execution_level_extraction_warning", warnings)


if __name__ == "__main__":
    unittest.main()
