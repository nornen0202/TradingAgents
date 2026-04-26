import json
import unittest

from tradingagents.schemas import PriceLevelType, RiskAction, parse_structured_decision


class SellSideRiskActionSchemaTests(unittest.TestCase):
    def _base_payload(self, **overrides):
        payload = {
            "rating": "HOLD",
            "portfolio_stance": "BULLISH",
            "entry_action": "WAIT",
            "setup_quality": "DEVELOPING",
            "confidence": 0.7,
            "time_horizon": "short",
            "entry_logic": "Wait for a cleaner entry.",
            "exit_logic": "Trim if support fails.",
            "position_sizing": "Starter only.",
            "risk_limits": "Respect support.",
            "catalysts": [],
            "invalidators": ["Close below 95 invalidates support."],
            "watchlist_triggers": [],
            "data_coverage": {
                "company_news_count": 1,
                "disclosures_count": 0,
                "social_source": "dedicated",
                "macro_items_count": 1,
            },
        }
        payload.update(overrides)
        return payload

    def test_old_artifact_defaults_risk_action_none(self):
        parsed = parse_structured_decision(json.dumps(self._base_payload(), ensure_ascii=False))

        self.assertEqual(parsed.risk_action, RiskAction.NONE)
        self.assertIn("risk_action", parsed.to_dict())

    def test_legacy_sell_exit_falls_back_to_exit_risk_action(self):
        parsed = parse_structured_decision(
            json.dumps(
                self._base_payload(
                    rating="SELL",
                    portfolio_stance="BEARISH",
                    entry_action="EXIT",
                    setup_quality="WEAK",
                ),
                ensure_ascii=False,
            )
        )

        self.assertEqual(parsed.risk_action, RiskAction.EXIT)
        self.assertIn("LEGACY_SELL_EXIT", parsed.risk_action_reason_codes)

    def test_risk_action_level_accepts_lowercase_legacy_level_type(self):
        parsed = parse_structured_decision(
            json.dumps(
                self._base_payload(
                    risk_action="STOP_LOSS",
                    risk_action_reason="Stop-loss level broke.",
                    risk_action_reason_codes=["INVALIDATION_BROKEN"],
                    risk_action_level={
                        "label": "stop below 95",
                        "level_type": "STOP_LOSS",
                        "price": "95.0",
                        "confirmation": "close",
                    },
                ),
                ensure_ascii=False,
            )
        )

        self.assertEqual(parsed.risk_action, RiskAction.STOP_LOSS)
        self.assertIsNotNone(parsed.risk_action_level)
        self.assertEqual(parsed.risk_action_level.level_type, PriceLevelType.STOP_LOSS)
        self.assertEqual(parsed.to_dict()["risk_action_level"]["level_type"], "STOP_LOSS")


if __name__ == "__main__":
    unittest.main()
