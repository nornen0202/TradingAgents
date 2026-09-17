from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd
import pytest

from tradingagents.eval import walk_forward as wf


def test_next_open_entry_and_full_holding_window_required():
    frame = pd.DataFrame({"Open": [10, 100, 110], "Close": [11, 105, 120]},
                         index=pd.to_datetime(["2026-03-02", "2026-03-03", "2026-03-04"]))
    with patch.object(wf.yf, "Ticker", return_value=SimpleNamespace(history=lambda **kwargs: frame)):
        assert wf._fetch_forward_return("AAPL", "2026-03-02", 2) == pytest.approx(0.2)
        assert wf._fetch_forward_return("AAPL", "2026-03-02", 3) is None


def test_initial_loss_is_in_drawdown():
    assert wf._compute_max_drawdown([-0.1, 0.02]) == pytest.approx(-0.1)


def test_malformed_entry_price_is_excluded():
    frame = pd.DataFrame({"Open": ["unavailable"], "Close": [105]}, index=pd.to_datetime(["2026-03-03"]))
    with patch.object(wf.yf, "Ticker", return_value=SimpleNamespace(history=lambda **kwargs: frame)):
        assert wf._fetch_forward_return("AAPL", "2026-03-02", 1) is None


class FakeGraph:
    def __init__(self, **kwargs):
        self.config = kwargs["config"]
        self.reflections = []
        self.calls = []
        self.closed = False

    def propagate(self, symbol, trade_date):
        self.calls.append((trade_date, len(self.reflections)))
        return {"company_of_interest": symbol, "trade_date": trade_date, "instrument_profile": {"country": "US"}}, "BUY"

    def reflect_and_remember(self, outcome, *, state, outcome_known_at):
        self.reflections.append((state["trade_date"], outcome_known_at, outcome))

    def close(self):
        self.closed = True


def window(symbol, date, holding):
    return {"return": 0.10, "entry_date": "2026-03-03" if date == "2026-03-02" else "2026-03-04",
            "exit_date": "2026-03-06", "entry_price": 100, "exit_price": 110}


def test_future_outcome_not_taught_early_and_overlap_not_compounded():
    graph = FakeGraph(config={})
    with patch.object(wf, "TradingAgentsGraph", return_value=graph), patch.object(wf, "_fetch_forward_window", side_effect=window):
        result = wf.run_walk_forward_evaluation(["AAPL", "MSFT"], ["2026-03-03", "2026-03-02"], enable_reflection=True)
    assert graph.calls == [("2026-03-02", 0), ("2026-03-02", 0), ("2026-03-03", 0), ("2026-03-03", 0)]
    assert result["metrics"]["max_drawdown"] is None
    assert result["metrics"]["overlapping_cohorts"]
    assert result["records"][0]["strategy_return"] == pytest.approx(0.098)
    assert result["records"][1]["exposure_change"] == 1
    assert graph.closed


def test_reflection_released_only_after_exit_date():
    graph = FakeGraph(config={})
    with patch.object(wf, "TradingAgentsGraph", return_value=graph), patch.object(wf, "_fetch_forward_window", side_effect=window):
        wf.run_walk_forward_evaluation(["AAPL"], ["2026-03-02", "2026-03-09"], enable_reflection=True)
    assert graph.calls == [("2026-03-02", 0), ("2026-03-09", 1)]
    assert graph.reflections[0][:2] == ("2026-03-02", "2026-03-06")


def test_sell_does_not_assume_short_sale_and_kr_benchmark_is_local():
    assert wf.RATING_TO_EXPOSURE["SELL"] == 0
    assert wf._regional_benchmark("005930.KS") == "069500.KS"


def test_incomplete_outcomes_are_reported_not_silently_counted():
    graph = FakeGraph(config={})
    with patch.object(wf, "TradingAgentsGraph", return_value=graph), patch.object(wf, "_fetch_forward_window", return_value=None):
        result = wf.run_walk_forward_evaluation(["AAPL"], ["2026-03-02"])
    assert result["records"] == []
    assert result["excluded"][0]["reason"] == "incomplete_or_invalid_forward_window"
    assert result["assumptions"]["point_in_time_strict"] is True


def test_unvalidated_decision_is_not_counted_as_successful_abstention():
    graph = FakeGraph(config={})
    with patch.object(wf, "TradingAgentsGraph", return_value=graph), patch.object(graph, "propagate", return_value=({"company_of_interest": "AAPL"}, "REVIEW")), patch.object(wf, "_fetch_forward_window") as fetch:
        result = wf.run_walk_forward_evaluation(["AAPL"], ["2026-03-02"])
    assert result["records"] == []
    assert result["excluded"][0]["reason"] == "decision_unvalidated"
    fetch.assert_not_called()
