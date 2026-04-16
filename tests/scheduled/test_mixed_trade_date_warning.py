import unittest

from tradingagents.scheduled.runner import _compute_batch_metrics, _compute_batch_warnings


class MixedTradeDateWarningTests(unittest.TestCase):
    def test_mixed_trade_date_run_gets_warning(self):
        metrics = _compute_batch_metrics(
            [
                {"status": "success", "trade_date": "2026-04-15", "decision": "HOLD"},
                {"status": "success", "trade_date": "2026-04-16", "decision": "HOLD"},
            ]
        )

        warnings = _compute_batch_warnings(metrics)

        self.assertTrue(any("mixed_daily_cohort" in warning for warning in warnings))
        self.assertTrue(any("2026-04-15" in warning and "2026-04-16" in warning for warning in warnings))


if __name__ == "__main__":
    unittest.main()
