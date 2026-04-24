from types import SimpleNamespace
from unittest.mock import patch

from tradingagents.scheduled.runner import _resolve_run_trade_date


def test_mixed_daily_cohort_guard():
    config = SimpleNamespace(run=SimpleNamespace())

    with patch("tradingagents.scheduled.runner.resolve_trade_date", return_value="2026-04-23") as mocked:
        trade_date = _resolve_run_trade_date(config=config, tickers=["005930.KS", "000660.KS"])

    assert trade_date == "2026-04-23"
    mocked.assert_called_once_with("005930.KS", config)
