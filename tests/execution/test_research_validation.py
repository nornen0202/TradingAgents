import numpy as np
import pandas as pd

from tradingagents.execution.research_backtest import targets
from tradingagents.execution.research_validation import (
    prefix_invariance,
    warmup_invariance,
)


def prices():
    return pd.DataFrame(
        {"A": 100 + np.sin(np.arange(600) / 30) * 10 + np.arange(600) / 10},
        index=pd.bdate_range("2023-01-02", periods=600),
    )


def test_fixed_trend_passes_but_future_mean_fails():
    data = prices()
    assert prefix_invariance(data, lambda x: targets(x, "trend_200"))["passed"]
    assert all(
        x["passed"] for x in warmup_invariance(data, lambda x: targets(x, "trend_200"))
    )
    assert not prefix_invariance(data, lambda x: (x > x.mean()).astype(float))["passed"]


def test_warmup_detects_recursive_history_dependency():
    result = warmup_invariance(prices(), lambda x: x.cumsum() / 1000000)
    assert all(not row["passed"] for row in result)
