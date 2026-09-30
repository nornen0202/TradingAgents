import unittest

from cli.utils import normalize_ticker_symbol
from tradingagents.agents.utils.agent_utils import build_instrument_context
from tradingagents.agents.utils.instrument_resolver import resolve_instrument


class TickerSymbolHandlingTests(unittest.TestCase):
    def test_normalize_ticker_symbol_preserves_exchange_suffix(self):
        self.assertEqual(normalize_ticker_symbol(" cnc.to "), "CNC.TO")

    def test_build_instrument_context_mentions_exact_symbol(self):
        context = build_instrument_context("7203.T")
        self.assertIn("7203.T", context)
        self.assertIn("exchange suffix", context)

    def test_us_adr_profile_does_not_claim_usd_financial_statements(self):
        profile = resolve_instrument("TSM")
        self.assertEqual(profile.currency, "USD")
        context = build_instrument_context("TSM", profile)
        self.assertIn("trading currency USD", context)
        self.assertNotIn("reporting currency USD", context)
        self.assertIn("financial-statement currency", context)
        self.assertIn("ADR-to-ordinary-share ratios", context)


if __name__ == "__main__":
    unittest.main()
