# Action Performance Tracker

The performance tracker records recommendations, not only executed trades. This avoids selection bias and lets later reviews compare TradingAgents-only, PRISM-confirmed, PRISM-conflicted, scanner-discovered, and skipped candidates.

## Config

```toml
[performance]
enabled = true
store_path = "archive/performance.sqlite"
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

Outcome updates can be run with deterministic fixture price histories in tests. Production price backfills should be wired to the preferred market data provider before enabling automated outcome refreshes.
