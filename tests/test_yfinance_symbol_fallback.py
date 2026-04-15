import unittest
from unittest.mock import patch

from tradingagents.dataflows.stockstats_utils import yf_retry
from tradingagents.dataflows.y_finance import _build_yfinance_symbol_candidates, get_fundamentals


class YFinanceSymbolFallbackTests(unittest.TestCase):
    def test_build_candidates_for_kr_symbol_with_wrong_suffix(self):
        self.assertEqual(
            _build_yfinance_symbol_candidates("058470.KS"),
            ["058470.KS", "058470", "058470.KQ"],
        )

    def test_get_fundamentals_tries_alternate_symbol_when_primary_fails(self):
        class _TickerStub:
            def __init__(self, symbol: str):
                self.symbol = symbol

            @property
            def info(self):
                if self.symbol == "058470.KQ":
                    return {"longName": "Sample KR Co"}
                raise RuntimeError("No fundamentals data found for symbol")

        with patch("tradingagents.dataflows.y_finance.yf.Ticker", side_effect=lambda s: _TickerStub(s)):
            result = get_fundamentals("058470.KS")

        self.assertIn("# Company Fundamentals for 058470.KQ", result)
        self.assertIn("Name: Sample KR Co", result)

    def test_yf_retry_retries_none_chart_payload_type_error(self):
        attempts = []

        def flaky_call():
            attempts.append(1)
            if len(attempts) == 1:
                raise TypeError("'NoneType' object is not subscriptable")
            return "ok"

        self.assertEqual(yf_retry(flaky_call, max_retries=1, base_delay=0), "ok")
        self.assertEqual(len(attempts), 2)


if __name__ == "__main__":
    unittest.main()
