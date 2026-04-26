import unittest

from tradingagents.portfolio.account_models import (
    AccountConstraints,
    AccountSnapshot,
    InstrumentIdentity,
    PortfolioCandidate,
    PortfolioProfile,
    Position,
)
from tradingagents.portfolio.allocation import build_recommendation


class TrimToFundVsReduceRiskTests(unittest.TestCase):
    def _identity(self, ticker):
        return InstrumentIdentity(
            broker_symbol=ticker.split(".")[0],
            canonical_ticker=ticker,
            yahoo_symbol=ticker,
            krx_code=None,
            dart_corp_code=None,
            display_name=ticker,
            exchange="KRX",
            country="KR",
            currency="KRW",
        )

    def _position(self, ticker):
        return Position(
            broker_symbol=ticker.split(".")[0],
            canonical_ticker=ticker,
            display_name=ticker,
            sector="Tech",
            quantity=10,
            available_qty=10,
            avg_cost_krw=100000,
            market_price_krw=100000,
            market_value_krw=1000000,
            unrealized_pnl_krw=0,
        )

    def _snapshot(self):
        constraints = AccountConstraints(min_cash_buffer_krw=1000000, min_trade_krw=100000)
        positions = (self._position("005930.KS"), self._position("000660.KS"))
        return AccountSnapshot(
            snapshot_id="snap",
            as_of="2026-04-24T10:30:00+09:00",
            broker="manual",
            account_id="test",
            currency="KRW",
            settled_cash_krw=100000,
            available_cash_krw=100000,
            buying_power_krw=100000,
            total_equity_krw=2100000,
            constraints=constraints,
            positions=positions,
        )

    def _profile(self, snapshot):
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
            trigger_budget_krw=500000,
            constraints=snapshot.constraints,
        )

    def _candidate(self, ticker, relative_action, risk_action, category):
        return PortfolioCandidate(
            snapshot_id="snap",
            instrument=self._identity(ticker),
            is_held=True,
            market_value_krw=1000000,
            quantity=10,
            available_qty=10,
            sector="Tech",
            structured_decision=None,
            data_coverage={"company_news_count": 1, "disclosures_count": 0, "social_source": "dedicated"},
            quality_flags=tuple(),
            vendor_health={"vendor_calls": {}, "fallback_count": 0},
            suggested_action_now="HOLD",
            suggested_action_if_triggered="NONE",
            trigger_conditions=tuple(),
            confidence=0.7,
            stance="BULLISH",
            entry_action="WAIT",
            setup_quality="DEVELOPING",
            rationale="test",
            portfolio_relative_action=relative_action,
            relative_action_reason_codes=("OPPORTUNITY_COST",) if relative_action == "TRIM_TO_FUND" else ("SUPPORT_BROKEN",),
            risk_action=risk_action,
            risk_action_reason_codes=("SUPPORT_BROKEN",) if risk_action == "REDUCE_RISK" else tuple(),
            sell_side_category=category,
        )

    def test_counts_keep_trim_to_fund_and_reduce_risk_separate(self):
        snapshot = self._snapshot()
        recommendation, _ = build_recommendation(
            candidates=[
                self._candidate("005930.KS", "TRIM_TO_FUND", "TRIM_TO_FUND", "funding"),
                self._candidate("000660.KS", "REDUCE_RISK", "REDUCE_RISK", "risk"),
            ],
            snapshot=snapshot,
            batch_metrics={"entry_action_distribution": {"WAIT": 2}, "stance_distribution": {"BULLISH": 2}},
            warnings=[],
            profile=self._profile(snapshot),
            report_date="2026-04-24",
        )

        self.assertEqual(recommendation.candidate_counts["trim_to_fund_count"], 1)
        self.assertEqual(recommendation.candidate_counts["reduce_risk_count"], 1)
        self.assertEqual(recommendation.candidate_counts["take_profit_count"], 0)


if __name__ == "__main__":
    unittest.main()
