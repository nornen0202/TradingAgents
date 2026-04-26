import unittest

from tradingagents.live.sell_side_delta import build_sell_side_delta_candidates, render_risk_action_delta_markdown


class LiveDowngradeTests(unittest.TestCase):
    def test_support_fail_creates_reduce_risk_delta(self):
        artifact = {
            "ticker_deltas": [
                {
                    "ticker": "005930.KS",
                    "base_action": "HOLD",
                    "live_action": "SUPPORT_FAIL",
                    "execution_timing_state": "SUPPORT_FAIL",
                    "live_price": 210000,
                    "relative_volume": 1.4,
                    "contract_evidence": {"support_level": 215500},
                }
            ]
        }

        candidates = build_sell_side_delta_candidates(
            live_context_delta=artifact,
            held_tickers={"005930.KS"},
        )

        self.assertEqual(candidates[0]["new_risk_action"], "REDUCE_RISK")
        self.assertEqual(candidates[0]["delta_type"], "SUPPORT_FAIL")
        self.assertEqual(candidates[0]["evidence"]["support_level"], 215500)
        self.assertIn("005930.KS", render_risk_action_delta_markdown(candidates))

    def test_negative_news_creates_report_only_reduce_risk_delta(self):
        artifact = {
            "ticker_deltas": [
                {
                    "ticker": "AAPL",
                    "base_action": "HOLD",
                    "live_action": "WAIT",
                    "news_delta": ["earnings_estimate_downgraded"],
                }
            ]
        }

        candidates = build_sell_side_delta_candidates(live_context_delta=artifact, held_tickers={"AAPL"})

        self.assertEqual(candidates[0]["new_risk_action"], "REDUCE_RISK")
        self.assertEqual(candidates[0]["delta_type"], "NEGATIVE_EARNINGS_GUIDANCE")


if __name__ == "__main__":
    unittest.main()
