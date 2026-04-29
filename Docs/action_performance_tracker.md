# Action Performance Tracker

The performance tracker records recommendations, not only executed trades. This avoids selection bias and lets later reviews compare TradingAgents-only, PRISM-confirmed, PRISM-conflicted, scanner-discovered, and skipped candidates.

## Config

```toml
[performance]
enabled = true
store_path = "archive/performance.sqlite"
update_outcomes_on_run = true
price_provider = "local_json" # none / local_json / yfinance
price_history_path = "C:/TradingAgentsData/price_history.json"
benchmark_ticker = "SPY"
outcome_horizons = [1, 3, 5, 10, 20, 60]
price_lookback_days = 120
```

Tracked actions include:

```text
ADD_NOW
ADD_IF_TRIGGERED
STARTER_NOW
STARTER_IF_TRIGGERED
HOLD
WAIT
TRIM_TO_FUND
REDUCE_RISK
TAKE_PROFIT
STOP_LOSS
EXIT
scanner_candidate_skipped
prism_candidate_skipped
```

## CLI

```powershell
python -m tradingagents.performance.query_archive --db archive/performance.sqlite --ticker 278470.KS
python -m tradingagents.performance.query_archive --db archive/performance.sqlite --action REDUCE_RISK
python -m tradingagents.performance.query_archive --db archive/performance.sqlite --query "STOP_LOSS"
```

## Outcome Updates

Outcome updates are disabled unless `update_outcomes_on_run = true`. Even then, the runner needs either a local price history file or an explicit provider.

Local JSON accepts this shape:

```json
{
  "000660.KS": [
    {"date": "2026-04-01", "close": 100},
    {"date": "2026-04-02", "close": 101}
  ],
  "SPY": [
    {"date": "2026-04-01", "close": 500},
    {"date": "2026-04-02", "close": 501}
  ]
}
```

If `benchmark_ticker` is present in the file, it is stored as the benchmark return series and used for `benchmark_return_5d`.

`price_provider = "yfinance"` can fetch missing recommendation tickers, but it is opt-in and provider/network failures are reported as warnings. Tests use deterministic local fixture prices and do not require network access.

The generated static portfolio page now includes a `추천 성과 추적` section when performance tracking is enabled. It shows recorded recommendations, updated outcomes, provider status, action-level average returns, and PRISM agreement/conflict buckets.
