import unittest

from tests.portfolio.test_degraded_overlay_preserves_triggerability import _identity, _profile, _snapshot
from tradingagents.portfolio.account_models import PortfolioCandidate
from tradingagents.portfolio.allocation import build_recommendation
from tradingagents.portfolio.reporting import render_portfolio_report_markdown


class KoreanReportLanguageTests(unittest.TestCase):
    def test_action_table_uses_korean_fallback_for_english_rationale(self):
        snapshot = _snapshot()
        candidate = PortfolioCandidate(
            snapshot_id=snapshot.snapshot_id,
            instrument=_identity("005930.KS", "삼성전자"),
            is_held=False,
            market_value_krw=0,
            quantity=0,
            available_qty=0,
            sector="Semiconductors",
            structured_decision=None,
            data_coverage={"company_news_count": 4, "disclosures_count": 1, "social_source": "dedicated"},
            quality_flags=tuple(),
            vendor_health={"vendor_calls": {}, "fallback_count": 0},
            suggested_action_now="WATCH",
            suggested_action_if_triggered="STARTER_IF_TRIGGERED",
            trigger_conditions=("close above 75,000 KRW",),
            confidence=0.7,
            stance="BULLISH",
            entry_action="WAIT",
            setup_quality="DEVELOPING",
            rationale="This is an English rationale because the model leaked it.",
            strategy_state="add_if_triggered",
        )
        recommendation, scored = build_recommendation(
            candidates=[candidate],
            snapshot=snapshot,
            batch_metrics={"entry_action_distribution": {"WAIT": 1}, "stance_distribution": {"BULLISH": 1}},
            warnings=[],
            profile=_profile(snapshot),
            report_date="2026-04-16",
        )

        markdown = render_portfolio_report_markdown(
            snapshot=snapshot,
            recommendation=recommendation,
            candidates=scored,
        )

        action_lines = [line for line in markdown.splitlines() if "삼성전자" in line]
        self.assertTrue(action_lines)
        joined = "\n".join(action_lines)
        self.assertNotIn("English rationale", joined)
        self.assertNotIn("because", joined)
        self.assertIn("조건 충족", joined)

    def test_korean_report_has_no_english_rationale_in_investor_mode(self):
        self.test_action_table_uses_korean_fallback_for_english_rationale()


if __name__ == "__main__":
    unittest.main()
