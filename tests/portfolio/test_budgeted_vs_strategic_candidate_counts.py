import unittest

from tests.portfolio.test_degraded_overlay_preserves_triggerability import _identity, _profile, _snapshot
from tradingagents.portfolio.account_models import PortfolioCandidate
from tradingagents.portfolio.allocation import build_recommendation


class BudgetedVsStrategicCandidateCountTests(unittest.TestCase):
    def test_cash_constraint_keeps_strategic_count_while_budgeted_count_is_zero(self):
        snapshot = _snapshot()
        candidates = [
            PortfolioCandidate(
                snapshot_id=snapshot.snapshot_id,
                instrument=_identity("000660.KS", "SK하이닉스"),
                is_held=False,
                market_value_krw=0,
                quantity=0,
                available_qty=0,
                sector="Semiconductors",
                structured_decision=None,
                data_coverage={"company_news_count": 5, "disclosures_count": 1, "social_source": "dedicated"},
                quality_flags=tuple(),
                vendor_health={"vendor_calls": {}, "fallback_count": 0},
                suggested_action_now="WATCH",
                suggested_action_if_triggered="STARTER_IF_TRIGGERED",
                trigger_conditions=("종가 215,500원 상회",),
                confidence=0.72,
                stance="BULLISH",
                entry_action="WAIT",
                setup_quality="DEVELOPING",
                rationale="조건 확인 전까지는 대기합니다.",
                strategy_state="add_if_triggered",
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
                data_coverage={"company_news_count": 4, "disclosures_count": 1, "social_source": "dedicated"},
                quality_flags=tuple(),
                vendor_health={"vendor_calls": {}, "fallback_count": 0},
                suggested_action_now="WATCH",
                suggested_action_if_triggered="STARTER_IF_TRIGGERED",
                trigger_conditions=("거래량 증가와 종가 돌파",),
                confidence=0.75,
                stance="BULLISH",
                entry_action="WAIT",
                setup_quality="COMPELLING",
                rationale="조건 확인 전까지는 대기합니다.",
                strategy_state="add_if_triggered",
            ),
        ]

        recommendation, _ = build_recommendation(
            candidates=candidates,
            snapshot=snapshot,
            batch_metrics={"entry_action_distribution": {"WAIT": 2}, "stance_distribution": {"BULLISH": 2}},
            warnings=[],
            profile=_profile(snapshot),
            report_date="2026-04-16",
        )

        self.assertEqual(recommendation.candidate_counts["strategic_trigger_candidates_count"], 2)
        self.assertEqual(recommendation.candidate_counts["budgeted_trigger_candidates_count"], 0)
        self.assertTrue(all(action.action_if_triggered == "STARTER_IF_TRIGGERED" for action in recommendation.actions))


if __name__ == "__main__":
    unittest.main()
