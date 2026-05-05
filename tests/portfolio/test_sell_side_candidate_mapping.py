import json
import unittest

from tradingagents.portfolio.account_models import AccountConstraints, AccountSnapshot, Position
from tradingagents.portfolio.candidates import _build_single_candidate


class SellSideCandidateMappingTests(unittest.TestCase):
    def _position(self, *, avg_cost=70000, market_price=70000, unrealized_pnl=0):
        return Position(
            broker_symbol="005930",
            canonical_ticker="005930.KS",
            display_name="Samsung Electronics",
            sector="Technology",
            quantity=10,
            available_qty=10,
            avg_cost_krw=avg_cost,
            market_price_krw=market_price,
            market_value_krw=int(market_price * 10),
            unrealized_pnl_krw=unrealized_pnl,
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

    def test_stop_loss_level_above_current_price_required_for_now(self):
        candidate, _ = _build_single_candidate(
            snapshot=self._snapshot(),
            canonical_ticker="005930.KS",
            position=self._position(),
            analysis={
                "decision": self._decision(
                    risk_action="STOP_LOSS",
                    risk_action_reason_codes=["INVALIDATION_BROKEN"],
                    risk_action_level={
                        "label": "stop",
                        "level_type": "STOP_LOSS",
                        "price": 65000,
                        "confirmation": "intraday",
                    },
                ),
                "tool_telemetry": {},
                "execution_update": {
                    "decision_state": "WAIT",
                    "last_price": 70000,
                    "trigger_status": {},
                    "source": {"market_session": "regular"},
                },
            },
        )

        self.assertEqual(candidate.suggested_action_now, "HOLD")
        self.assertEqual(candidate.suggested_action_if_triggered, "STOP_LOSS_IF_TRIGGERED")

    def test_close_confirmation_stop_loss_does_not_fire_intraday(self):
        candidate, _ = _build_single_candidate(
            snapshot=self._snapshot(),
            canonical_ticker="005930.KS",
            position=self._position(),
            analysis={
                "decision": self._decision(
                    risk_action="STOP_LOSS",
                    risk_action_reason_codes=["INVALIDATION_BROKEN"],
                    risk_action_level={
                        "label": "close below stop",
                        "level_type": "STOP_LOSS",
                        "price": 65000,
                        "confirmation": "close",
                    },
                ),
                "tool_telemetry": {},
                "execution_update": {
                    "decision_state": "WAIT",
                    "last_price": 64000,
                    "trigger_status": {},
                    "source": {"market_session": "regular"},
                },
            },
        )

        self.assertEqual(candidate.suggested_action_now, "HOLD")
        self.assertEqual(candidate.suggested_action_if_triggered, "STOP_LOSS_IF_TRIGGERED")

    def test_reason_code_alone_does_not_create_stop_loss_now(self):
        candidate, _ = _build_single_candidate(
            snapshot=self._snapshot(),
            canonical_ticker="005930.KS",
            position=self._position(),
            analysis={
                "decision": self._decision(
                    risk_action="STOP_LOSS",
                    risk_action_reason_codes=["INVALIDATION_BROKEN"],
                ),
                "tool_telemetry": {},
            },
        )

        self.assertEqual(candidate.suggested_action_now, "HOLD")
        self.assertEqual(candidate.suggested_action_if_triggered, "STOP_LOSS_IF_TRIGGERED")

    def test_profit_level_reduce_risk_is_labeled_take_profit_without_damage(self):
        position = self._position(avg_cost=70000, market_price=84000, unrealized_pnl=140000)
        candidate, _ = _build_single_candidate(
            snapshot=AccountSnapshot(
                **{
                    **self._snapshot().__dict__,
                    "positions": (position,),
                }
            ),
            canonical_ticker="005930.KS",
            position=position,
            analysis={
                "decision": self._decision(
                    risk_action="REDUCE_RISK",
                    risk_action_reason_codes=["EXTENDED_MOVE"],
                    risk_action_level={
                        "label": "extension resistance",
                        "level_type": "TAKE_PROFIT",
                        "price": 85000,
                        "confirmation": "intraday",
                    },
                ),
                "tool_telemetry": {},
                "execution_update": {
                    "decision_state": "WAIT",
                    "last_price": 84000,
                    "trigger_status": {},
                    "source": {"market_session": "regular"},
                },
            },
        )

        self.assertEqual(candidate.risk_action, "REDUCE_RISK")
        self.assertEqual(candidate.portfolio_relative_action, "REDUCE_RISK")
        self.assertEqual(candidate.sell_intent, "TAKE_PROFIT")
        self.assertEqual(candidate.sell_side_category, "profit")
        self.assertEqual(candidate.thesis_after_sell, "MAINTAIN")
        self.assertAlmostEqual(candidate.position_metrics["unrealized_return_pct"], 20.0)

    def test_damage_code_keeps_profit_level_reduce_risk_as_reduce_risk(self):
        position = self._position(avg_cost=70000, market_price=84000, unrealized_pnl=140000)
        candidate, _ = _build_single_candidate(
            snapshot=AccountSnapshot(
                **{
                    **self._snapshot().__dict__,
                    "positions": (position,),
                }
            ),
            canonical_ticker="005930.KS",
            position=position,
            analysis={
                "decision": self._decision(
                    risk_action="REDUCE_RISK",
                    risk_action_reason_codes=["SUPPORT_BROKEN"],
                    risk_action_level={
                        "label": "failed extension",
                        "level_type": "TAKE_PROFIT",
                        "price": 85000,
                        "confirmation": "intraday",
                    },
                ),
                "tool_telemetry": {},
            },
        )

        self.assertEqual(candidate.sell_intent, "REDUCE_RISK")
        self.assertEqual(candidate.thesis_after_sell, "WEAKENED")


if __name__ == "__main__":
    unittest.main()
