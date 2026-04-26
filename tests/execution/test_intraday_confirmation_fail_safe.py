import unittest
from datetime import datetime, timezone

from tradingagents.execution.overlay import evaluate_execution_state
from tradingagents.schemas import (
    ActionIfTriggered,
    BreakoutConfirmation,
    DecisionState,
    ExecutionContract,
    ExecutionTimingState,
    IntradayMarketSnapshot,
    LevelBasis,
    PrimarySetup,
    SessionVWAPPreference,
    ThesisState,
)


class IntradayConfirmationFailSafeTests(unittest.TestCase):
    def _contract(self):
        return ExecutionContract(
            ticker="AAPL",
            analysis_asof="2026-04-24T09:00:00+00:00",
            market_data_asof="2026-04-24",
            level_basis=LevelBasis.DAILY_CLOSE,
            thesis_state=ThesisState.CONSTRUCTIVE,
            primary_setup=PrimarySetup.BREAKOUT_CONFIRMATION,
            portfolio_stance="BULLISH",
            entry_action_base="STARTER",
            setup_quality="COMPELLING",
            confidence=0.8,
            action_if_triggered=ActionIfTriggered.STARTER,
            breakout_level=100.0,
            breakout_confirmation=BreakoutConfirmation.INTRADAY_ABOVE,
            min_relative_volume=1.2,
            session_vwap_preference=SessionVWAPPreference.ABOVE,
        )

    def test_missing_vwap_and_rvol_block_pilot(self):
        now = datetime.now(timezone.utc)
        update = evaluate_execution_state(
            self._contract(),
            IntradayMarketSnapshot(
                ticker="AAPL",
                asof=now.isoformat(),
                provider="fixture",
                interval="5m",
                last_price=101.0,
                session_vwap=None,
                day_high=102.0,
                day_low=99.0,
                volume=1000,
                avg20_daily_volume=1000.0,
                relative_volume=None,
            ),
            now=now,
            max_data_age_seconds=180,
        )

        self.assertEqual(update.decision_state, DecisionState.ARMED)
        self.assertEqual(update.execution_timing_state, ExecutionTimingState.PILOT_BLOCKED_VOLUME)
        self.assertIn("data_missing_blocked_pilot", update.reason_codes)
        self.assertIn("relative_volume_unconfirmed", update.reason_codes)
        self.assertIn("vwap_unconfirmed", update.reason_codes)


if __name__ == "__main__":
    unittest.main()
