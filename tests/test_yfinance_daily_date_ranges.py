from __future__ import annotations

import unittest
from unittest.mock import patch

import pandas as pd

from tradingagents.dataflows.y_finance import get_YFin_data_online


class _TickerStub:
    def __init__(self, captured: dict[str, str]):
        self._captured = captured

    def history(self, *, start, end):
        self._captured["start"] = start
        self._captured["end"] = end
        return pd.DataFrame(
            {
                "Open": [10.0, 20.0],
                "High": [11.0, 21.0],
                "Low": [9.0, 19.0],
                "Close": [10.5, 20.5],
                "Volume": [1000, 2000],
            },
            index=pd.DatetimeIndex(["2026-06-26", "2026-06-27"], tz="UTC"),
        )


class YFinanceDailyDateRangeTests(unittest.TestCase):
    def test_yfinance_stock_data_treats_tool_end_date_as_inclusive(self):
        captured: dict[str, str] = {}

        with patch("tradingagents.dataflows.y_finance.yf.Ticker", lambda _symbol: _TickerStub(captured)):
            result = get_YFin_data_online("AAPL", "2026-06-01", "2026-06-26")

        self.assertEqual(captured["start"], "2026-06-01")
        self.assertEqual(captured["end"], "2026-06-27")
        self.assertIn("2026-06-26", result)
        self.assertNotIn("2026-06-27", result)
