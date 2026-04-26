import json
import unittest

from tradingagents.portfolio.account_models import AccountConstraints, AccountSnapshot, Position
from tradingagents.portfolio.candidates import _build_single_candidate


class SellSideCandidateMappingTests(unittest.TestCase):
    def _position(self):
        return Position(
            broker_symbol="005930",
            canonical_ticker="005930.KS",
            display_name="Samsung Electronics",
            sector="Technology",
            quantity=10,
            available_qty=10,
            avg_cost_krw=70000,
            market_price_krw=70000,
            market_value_krw=700000,
            unrealized_pnl_krw=0,
        )

    def _snapshot(self):
        return AccountSnapshot(
            snapshot_id="snap",
            as_of="2026-04-24T10:30:00+09:00",
            broker="manual",
            account_id="test",
            currency="KRW",
            settled_cash_krw=1000000,
            available_cash_krw=1000000,
            buying_power_krw=1000000,
            total_equity_krw=1700000,
            constraints=AccountConstraints(min_cash_buffer_krw=100000),
            positions=(self._position(),),
        )

    def _decision(self, **overrides):
        payload = {
            "rating": "HOLD",
            "portfolio_stance": "BULLISH",
            "entry_action": "WAIT",
            "risk_action": "NONE",
            "setup_quality": "DEVELOPING",
            "confidence": 0.7,
            "time_horizon": "short",
            "entry_logic": "Wait.",
            "exit_logic": "Respect support.",
            "position_sizing": "Starter.",
            "risk_limits": "Support below 65000.",
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
        payload.update(overrides)
        return json.dumps(payload, ensure_ascii=False)

    def test_support_fail_on_held_position_maps_to_reduce_now(self):
        candidate, warnings = _build_single_candidate(
            snapshot=self._snapshot(),
            canonical_ticker="005930.KS",
            position=self._position(),
            analysis={
                "decision": self._decision(),
                "tool_telemetry": {},
                "execution_update": {
                    "decision_state": "ARMED",
                    "execution_timing_state": "SUPPORT_FAIL",
                    "trigger_status": {"support_fail": True},
                    "source": {"execution_data_quality": "REALTIME_EXECUTION_READY"},
                },
            },
        )

        self.assertEqual(warnings, [])
        self.assertEqual(candidate.suggested_action_now, "REDUCE_NOW")
        self.assertEqual(candidate.portfolio_relative_action, "REDUCE_RISK")
        self.assertEqual(candidate.risk_action, "REDUCE_RISK")
        self.assertEqual(candidate.sell_side_category, "risk")

    def test_non_held_stop_loss_becomes_avoid_not_sell_action(self):
        candidate, _ = _build_single_candidate(
            snapshot=self._snapshot(),
            canonical_ticker="AAPL",
            position=None,
            analysis={
                "decision": self._decision(
                    risk_action="STOP_LOSS",
                    risk_action_reason_codes=["INVALIDATION_BROKEN"],
                ),
                "tool_telemetry": {},
            },
        )

        self.assertEqual(candidate.suggested_action_now, "WATCH")
        self.assertEqual(candidate.portfolio_relative_action, "AVOID")
        self.assertEqual(candidate.risk_action, "STOP_LOSS")


if __name__ == "__main__":
    unittest.main()
