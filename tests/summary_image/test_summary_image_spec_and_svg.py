import unittest

from tradingagents.portfolio.account_models import (
    AccountConstraints,
    AccountSnapshot,
    InstrumentIdentity,
    PortfolioAction,
    PortfolioCandidate,
    PortfolioRecommendation,
)
from tradingagents.summary_image.render_svg import render_summary_svg
from tradingagents.summary_image.spec import build_portfolio_summary_image_spec


def _snapshot() -> AccountSnapshot:
    return AccountSnapshot(
        snapshot_id="snap",
        as_of="2026-04-26T23:40:00+09:00",
        broker="manual",
        account_id="acct",
        currency="KRW",
        settled_cash_krw=1_000_000,
        available_cash_krw=676_302,
        buying_power_krw=676_302,
        total_equity_krw=25_502_998,
        constraints=AccountConstraints(min_cash_buffer_krw=2_500_000),
    )


def _action(
    ticker: str,
    *,
    priority: int,
    action_now: str = "HOLD",
    action_if_triggered: str = "ADD_IF_TRIGGERED",
    relative_action: str = "WATCH",
    conditions: tuple[str, ...] = ("close above 100",),
) -> PortfolioAction:
    return PortfolioAction(
        canonical_ticker=ticker,
        display_name=ticker,
        priority=priority,
        confidence=0.8,
        action_now=action_now,
        delta_krw_now=0,
        target_weight_now=0.1,
        action_if_triggered=action_if_triggered,
        delta_krw_if_triggered=300_000,
        target_weight_if_triggered=0.12,
        trigger_conditions=conditions,
        rationale="test rationale",
        data_health={},
        portfolio_relative_action=relative_action,
        risk_action=relative_action if relative_action in {"REDUCE_RISK", "STOP_LOSS"} else "NONE",
    )


def _recommendation() -> PortfolioRecommendation:
    actions = (
        _action("TSM", priority=1, action_if_triggered="ADD_IF_TRIGGERED", conditions=("400 breakout",)),
        _action("GEV", priority=2, relative_action="TRIM_TO_FUND", conditions=("1181 support",)),
        _action("NVDA", priority=3, relative_action="REDUCE_RISK", conditions=("support failed",)),
    )
    return PortfolioRecommendation(
        snapshot_id="snap",
        report_date="2026-04-26",
        account_value_krw=25_502_998,
        recommended_cash_after_now_krw=676_302,
        recommended_cash_after_triggered_krw=376_302,
        market_regime="bullish",
        actions=actions,
        portfolio_risks=("추격 매수 위험", "지지선 확인 필요"),
        data_health_summary={"sell_side_distribution": {"TRIM_TO_FUND": 1, "REDUCE_RISK": 1}},
        candidate_counts={
            "immediate_budgeted_count": 0,
            "pilot_ready_count": 0,
            "close_confirm_count": 1,
            "trim_to_fund_count": 1,
            "reduce_risk_count": 1,
            "take_profit_count": 0,
            "stop_loss_count": 0,
            "exit_count": 0,
        },
    )


def _candidate(ticker: str, *, held: bool) -> PortfolioCandidate:
    instrument = InstrumentIdentity(
        broker_symbol=ticker,
        canonical_ticker=ticker,
        yahoo_symbol=ticker,
        krx_code=None,
        dart_corp_code=None,
        display_name=ticker,
        exchange="NASDAQ",
        country="US",
        currency="USD",
    )
    return PortfolioCandidate(
        snapshot_id="snap",
        instrument=instrument,
        is_held=held,
        market_value_krw=100_000 if held else 0,
        quantity=1 if held else 0,
        available_qty=1 if held else 0,
        sector=None,
        structured_decision=None,
        data_coverage={},
        quality_flags=tuple(),
        vendor_health={},
        suggested_action_now="HOLD",
        suggested_action_if_triggered="ADD_IF_TRIGGERED",
        trigger_conditions=("close above 100",),
        confidence=0.8,
        stance="BULLISH",
        entry_action="WAIT",
        setup_quality="WATCH",
        rationale="test",
    )


class SummaryImageSpecAndSvgTests(unittest.TestCase):
    def test_spec_contains_exact_counts_and_account_values(self):
        spec = build_portfolio_summary_image_spec(
            snapshot=_snapshot(),
            recommendation=_recommendation(),
            candidates=[_candidate("TSM", held=True), _candidate("GEV", held=False)],
            manifest={
                "run_id": "20260426T013659_github-actions-us",
                "status": "partial_failure",
                "started_at": "2026-04-26T01:36:59+00:00",
                "summary": {"total_tickers": 23, "successful_tickers": 21, "failed_tickers": 2},
                "settings": {"market": "US", "output_language": "Korean"},
                "tickers": [{"ticker": "TSM"}],
            },
            live_sell_side_delta=[],
            report_writer_payload={},
            redact_account_values=False,
        )

        self.assertEqual(spec["title"], "TradingAgents US 계좌 운용 리포트 요약")
        self.assertEqual(spec["account"]["account_value"], "25,502,998 KRW")
        self.assertEqual(spec["counts"]["trim_to_fund"], 1)
        self.assertEqual(spec["counts"]["reduce_risk"], 1)
        self.assertIn("TSM", [item["ticker"] for item in spec["top_priority"]])

    def test_svg_renderer_preserves_summary_text_for_web_display(self):
        spec = build_portfolio_summary_image_spec(
            snapshot=_snapshot(),
            recommendation=_recommendation(),
            candidates=[],
            manifest={
                "run_id": "20260426T013659_github-actions-us",
                "status": "success",
                "started_at": "2026-04-26T01:36:59+00:00",
                "summary": {"total_tickers": 23, "successful_tickers": 23, "failed_tickers": 0},
                "settings": {"market": "US"},
            },
            live_sell_side_delta=[],
            report_writer_payload={},
            redact_account_values=True,
        )
        svg = render_summary_svg(spec)

        self.assertIn("<svg", svg)
        self.assertIn("TradingAgents US", svg)
        self.assertIn("비공개", svg)
        self.assertIn("리포트 기준", svg)
        self.assertNotIn("25,502,998 KRW", svg)


if __name__ == "__main__":
    unittest.main()
