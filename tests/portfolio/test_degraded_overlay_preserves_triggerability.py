import unittest

from tradingagents.portfolio.account_models import (
    AccountConstraints,
    AccountSnapshot,
    InstrumentIdentity,
    PortfolioCandidate,
    PortfolioProfile,
)
from tradingagents.portfolio.allocation import build_recommendation


def _identity(ticker: str, name: str) -> InstrumentIdentity:
    return InstrumentIdentity(
        broker_symbol=ticker.split(".")[0],
        canonical_ticker=ticker,
        yahoo_symbol=ticker,
        krx_code=ticker.split(".")[0],
        dart_corp_code=None,
        display_name=name,
        exchange="KRX",
        country="KR",
        currency="KRW",
    )


def _snapshot() -> AccountSnapshot:
    constraints = AccountConstraints(min_cash_buffer_krw=2_500_000, min_trade_krw=100_000)
    return AccountSnapshot(
        snapshot_id="snap",
        as_of="2026-04-16T09:16:00+09:00",
        broker="manual",
        account_id="test",
        currency="KRW",
        settled_cash_krw=1_000_000,
        available_cash_krw=1_000_000,
        buying_power_krw=1_000_000,
        constraints=constraints,
    )


def _profile(snapshot: AccountSnapshot) -> PortfolioProfile:
    return PortfolioProfile(
        name="test",
        enabled=True,
        broker="manual",
        broker_environment="real",
        read_only=True,
        account_no=None,
        product_code=None,
        manual_snapshot_path=None,
        csv_positions_path=None,
        private_output_dirname="private",
        watch_tickers=tuple(),
        trigger_budget_krw=500_000,
        constraints=snapshot.constraints,
    )


class DegradedOverlayTriggerabilityTests(unittest.TestCase):
    def test_degraded_overlay_keeps_strategy_trigger(self):
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
            data_coverage={"company_news_count": 3, "disclosures_count": 1, "social_source": "dedicated"},
            quality_flags=("stale_market_data",),
            vendor_health={"vendor_calls": {}, "fallback_count": 0},
            suggested_action_now="WATCH",
            suggested_action_if_triggered="STARTER_IF_TRIGGERED",
            trigger_conditions=("종가 75,000원 상회",),
            confidence=0.7,
            stance="BULLISH",
            entry_action="WAIT",
            setup_quality="DEVELOPING",
            rationale="조건 확인 전까지는 대기합니다.",
            data_health={"quality_flags": ["stale_market_data"]},
            strategy_state="add_if_triggered",
            execution_feasibility_now="blocked_stale_or_degraded_data",
            stale_but_triggerable=True,
        )

        recommendation, _ = build_recommendation(
            candidates=[candidate],
            snapshot=snapshot,
            batch_metrics={"entry_action_distribution": {"WAIT": 1}, "stance_distribution": {"BULLISH": 1}},
            warnings=[],
            profile=_profile(snapshot),
            report_date="2026-04-16",
        )

        action = recommendation.actions[0]
        self.assertEqual(action.action_if_triggered, "STARTER_IF_TRIGGERED")
        self.assertEqual(action.delta_krw_if_triggered, 0)
        self.assertTrue(action.stale_but_triggerable)
        self.assertEqual(recommendation.candidate_counts["strategic_trigger_candidates_count"], 1)
        self.assertEqual(recommendation.candidate_counts["budgeted_trigger_candidates_count"], 0)


if __name__ == "__main__":
    unittest.main()
