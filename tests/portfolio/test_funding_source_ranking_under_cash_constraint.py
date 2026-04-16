import unittest

from tests.portfolio.test_degraded_overlay_preserves_triggerability import _identity, _profile
from tradingagents.portfolio.account_models import AccountConstraints, AccountSnapshot, PortfolioCandidate, Position
from tradingagents.portfolio.allocation import build_recommendation


class FundingSourceRankingTests(unittest.TestCase):
    def test_cash_constrained_account_gets_trim_and_add_if_funded_candidates(self):
        constraints = AccountConstraints(min_cash_buffer_krw=2_500_000, min_trade_krw=100_000)
        snapshot = AccountSnapshot(
            snapshot_id="snap",
            as_of="2026-04-16T09:16:00+09:00",
            broker="manual",
            account_id="test",
            currency="KRW",
            settled_cash_krw=1_000_000,
            available_cash_krw=1_000_000,
            buying_power_krw=1_000_000,
            positions=(
                Position(
                    broker_symbol="010950",
                    canonical_ticker="010950.KS",
                    display_name="S-Oil",
                    sector="Energy",
                    quantity=20,
                    available_qty=20,
                    avg_cost_krw=70_000,
                    market_price_krw=65_000,
                    market_value_krw=1_300_000,
                    unrealized_pnl_krw=-100_000,
                ),
            ),
            constraints=constraints,
        )
        candidates = [
            PortfolioCandidate(
                snapshot_id=snapshot.snapshot_id,
                instrument=_identity("010950.KS", "S-Oil"),
                is_held=True,
                market_value_krw=1_300_000,
                quantity=20,
                available_qty=20,
                sector="Energy",
                structured_decision=None,
                data_coverage={"company_news_count": 0, "disclosures_count": 0, "social_source": "unavailable"},
                quality_flags=tuple(),
                vendor_health={"vendor_calls": {}, "fallback_count": 0},
                suggested_action_now="HOLD",
                suggested_action_if_triggered="NONE",
                trigger_conditions=tuple(),
                confidence=0.45,
                stance="NEUTRAL",
                entry_action="WAIT",
                setup_quality="WEAK",
                rationale="유지하되 우선순위는 낮습니다.",
                strategy_state="hold_or_watch",
            ),
            PortfolioCandidate(
                snapshot_id=snapshot.snapshot_id,
                instrument=_identity("034020.KS", "두산에너빌리티"),
                is_held=False,
                market_value_krw=0,
                quantity=0,
                available_qty=0,
                sector="Industrials",
                structured_decision=None,
                data_coverage={"company_news_count": 5, "disclosures_count": 1, "social_source": "dedicated"},
                quality_flags=tuple(),
                vendor_health={"vendor_calls": {}, "fallback_count": 0},
                suggested_action_now="WATCH",
                suggested_action_if_triggered="STARTER_IF_TRIGGERED",
                trigger_conditions=("종가 돌파와 거래량 확인",),
                confidence=0.8,
                stance="BULLISH",
                entry_action="WAIT",
                setup_quality="COMPELLING",
                rationale="조건 충족 전까지는 대기합니다.",
                strategy_state="add_if_triggered",
            ),
        ]

        recommendation, _ = build_recommendation(
            candidates=candidates,
            snapshot=snapshot,
            batch_metrics={"entry_action_distribution": {"WAIT": 2}, "stance_distribution": {"BULLISH": 1, "NEUTRAL": 1}},
            warnings=[],
            profile=_profile(snapshot),
            report_date="2026-04-16",
        )

        self.assertGreaterEqual(len(recommendation.funding_plan["top_add_if_funded"]), 1)
        self.assertGreaterEqual(len(recommendation.funding_plan["top_trim_if_funding_needed"]), 1)
        self.assertEqual(
            recommendation.funding_plan["top_trim_if_funding_needed"][0]["canonical_ticker"],
            "010950.KS",
        )
        switch_orders = recommendation.scenario_plan["switch"]["orders_if_triggered"]
        aggressive_orders = recommendation.scenario_plan["aggressive"]["orders_if_triggered"]
        self.assertTrue(any(order["side"] == "sell" for order in switch_orders))
        self.assertTrue(any(order["side"] == "buy" for order in switch_orders))
        self.assertTrue(any(order["side"] == "buy" for order in aggressive_orders))
        self.assertGreater(recommendation.scenario_plan["switch"]["gross_sell_krw"], 0)
        self.assertGreater(recommendation.scenario_plan["switch"]["gross_buy_krw"], 0)
        self.assertGreater(recommendation.scenario_plan["aggressive"]["gross_buy_krw"], 0)


if __name__ == "__main__":
    unittest.main()
