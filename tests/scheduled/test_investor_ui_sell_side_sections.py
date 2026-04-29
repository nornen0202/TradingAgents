import json
import unittest

from tradingagents.portfolio.account_models import (
    AccountConstraints,
    AccountSnapshot,
    InstrumentIdentity,
    PortfolioAction,
    PortfolioRecommendation,
)
from tradingagents.portfolio.reporting import render_portfolio_report_markdown
from tradingagents.scheduled.site import _run_category, _ticker_investor_summary


class InvestorUiSellSideSectionsTests(unittest.TestCase):
    def _action(self, ticker, relative_action, *, action_now="HOLD", action_if_triggered="NONE"):
        return PortfolioAction(
            canonical_ticker=ticker,
            display_name=ticker,
            priority=1,
            confidence=0.7,
            action_now=action_now,
            delta_krw_now=0,
            target_weight_now=0.1,
            action_if_triggered=action_if_triggered,
            delta_krw_if_triggered=0,
            target_weight_if_triggered=0.1,
            trigger_conditions=tuple(),
            rationale="test",
            data_health={},
            portfolio_relative_action=relative_action,
            risk_action=relative_action if relative_action in {"REDUCE_RISK", "TAKE_PROFIT", "STOP_LOSS", "EXIT"} else "NONE",
            sell_side_category="risk" if relative_action == "REDUCE_RISK" else "none",
        )

    def test_report_contains_investor_sell_side_sections_and_korean_labels(self):
        snapshot = AccountSnapshot(
            snapshot_id="snap",
            as_of="2026-04-24T10:30:00+09:00",
            broker="manual",
            account_id="test",
            currency="KRW",
            settled_cash_krw=1000000,
            available_cash_krw=1000000,
            buying_power_krw=1000000,
            total_equity_krw=1000000,
            constraints=AccountConstraints(min_cash_buffer_krw=100000),
        )
        recommendation = PortfolioRecommendation(
            snapshot_id="snap",
            report_date="2026-04-24",
            account_value_krw=1000000,
            recommended_cash_after_now_krw=1000000,
            recommended_cash_after_triggered_krw=1000000,
            market_regime="mixed",
            actions=(
                self._action("005930.KS", "TRIM_TO_FUND"),
                self._action("000660.KS", "REDUCE_RISK"),
                self._action("AAPL", "TAKE_PROFIT"),
                self._action("MSFT", "STOP_LOSS"),
            ),
            portfolio_risks=tuple(),
            data_health_summary={},
            candidate_counts={
                "trim_to_fund_count": 1,
                "reduce_risk_count": 1,
                "take_profit_count": 1,
                "stop_loss_count": 1,
                "exit_count": 0,
            },
        )

        markdown = render_portfolio_report_markdown(snapshot=snapshot, recommendation=recommendation, candidates=[])

        self.assertIn("오늘 살 후보", markdown)
        self.assertIn("위험 때문에 줄일 후보", markdown)
        self.assertIn("이익실현 후보", markdown)
        self.assertIn("손절/청산 후보", markdown)
        self.assertIn("강한 후보 매수를 위한 일부 축소", markdown)
        self.assertIn("리스크 축소", markdown)
        self.assertIn("## 오늘 할 일: 방향별 후보", markdown)
        self.assertIn("### 오늘 즉시 매도/축소 후보", markdown)
        self.assertIn("### 조건부 매수 후보", markdown)
        self.assertIn("현재 매수가능금액", markdown)
        self.assertIn("매도 정산 후 예상 현금", markdown)
        self.assertNotIn("전략상 우선순위", markdown)
        self.assertNotIn("| Scenario | Intent | Plan |", markdown)

    def test_run_category_labels_post_close_as_review(self):
        manifest = {
            "market_session_phase": "post_close",
            "execution": {"execution_data_quality": "REALTIME_EXECUTION_READY"},
            "started_at": "2026-04-24T16:30:00+09:00",
            "settings": {"market": "KR"},
        }

        self.assertEqual(_run_category(manifest), "POST_CLOSE_REVIEW")

    def test_ticker_card_prefers_account_execution_view_over_research_view(self):
        decision = {
            "rating": "OVERWEIGHT",
            "portfolio_stance": "BULLISH",
            "entry_action": "WAIT",
            "setup_quality": "DEVELOPING",
            "confidence": 0.7,
            "time_horizon": "short",
            "entry_logic": "Wait.",
            "exit_logic": "Stop if support fails.",
            "position_sizing": "Hold.",
            "risk_limits": "Close below 64300.",
            "catalysts": [],
            "invalidators": [],
            "watchlist_triggers": [],
            "data_coverage": {
                "company_news_count": 1,
                "disclosures_count": 0,
                "social_source": "dedicated",
                "macro_items_count": 1,
            },
        }
        ticker_summary = {
            "ticker": "064350.KS",
            "status": "success",
            "decision": json.dumps(decision, ensure_ascii=False),
            "portfolio_action": {
                "action_now": "STOP_LOSS_NOW",
                "action_if_triggered": "NONE",
                "portfolio_relative_action": "STOP_LOSS",
                "risk_action": "STOP_LOSS",
                "risk_action_level": {"price": 64300, "confirmation": "close"},
                "rationale": "손절 조건 확인",
            },
        }

        summary = _ticker_investor_summary(ticker_summary, {"settings": {"output_language": "Korean"}}, language="Korean")

        self.assertEqual(summary["investment_view"], "손절/청산 검토")
        self.assertEqual(summary["research_view"], "비중 확대")
        self.assertIn("손절", summary["today_action"])


if __name__ == "__main__":
    unittest.main()
