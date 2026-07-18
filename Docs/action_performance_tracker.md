# Action Performance Tracker

The performance tracker records recommendations, not only executed trades. This avoids selection bias and lets later reviews compare TradingAgents-only, PRISM-confirmed, PRISM-conflicted, PRISM-uncovered-current-market, scanner-discovered, and skipped candidates. Its forward returns are counterfactual recommendation-price paths, not account returns or proof that an order was filled.

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
TAKE_PROFIT_NOW
TAKE_PROFIT_IF_TRIGGERED
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

Scheduled runs now separate recommendation recording from outcome updates. When tracking is enabled, recommendations are written first. If outcome updates are disabled or price history is unavailable, the run status is `recorded_pending_outcomes` instead of `failed`, and `failure_reason` / `unavailable_reason` explain any remaining issue.

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

If performance tracking records recommendations but cannot update outcomes because no price provider/history is available, the report says:

```text
성과 추적: 기록은 저장됐지만 아직 성과 계산은 수행되지 않았습니다.
```

The generated static portfolio page includes `추천 사후평가 (실제 체결 성과 아님)` when performance tracking is enabled. It shows recommendation rows separately from matured 5-day samples, distinct analysis runs, linked closed trades, action-level average returns, profit-taking performance, PRISM agreement/conflict buckets, and action-level source buckets:

```text
TradingAgents-only
PRISM-confirmed
PRISM-conflicted
PRISM-uncovered-current-market
Scanner-discovered
```

Profit-taking recommendations also store additive calibration fields when present:

```text
sell_intent
sell_trigger_status
sell_size_plan
unrealized_return_pct
profit_protection_score
profit_plan_json
```

Outcome updates compute `avoided_drawdown_20d`, `missed_upside_20d`, and `benchmark_excess_5d` so `TAKE_PROFIT` can be reviewed separately from generic risk reduction.

`delta_krw_now > 0` is only a proposed allocation. It never sets `was_executed=1`. Execution is recognized only when a structured `execution_receipt` has a broker/KIS source, a filled or partially-filled status, and positive filled quantity. Historical rows that used proposed allocation as an execution proxy remain visible only as `legacy_unverified_execution_rows`; they are excluded from actual-trade claims. Until a broker fill and a closed `trade_journal` row are linked, `data_quality.feedback_loop_status=COUNTERFACTUAL_ONLY` and `actual_trade_effectiveness_available=false`.

## Action Lift Calibration

Portfolio action rows can carry Action Lift metadata:

```text
lift_status
opportunity_cost_score
opportunity_capture_score
pilot_allowed
full_size_allowed
```

Calibration denominators intentionally use only TradingAgents portfolio action rows with lift metadata. Scanner-only and PRISM-only skipped discovery rows are excluded from `actionable_not_ordered_rate`, `missed_upside_5d`, `missed_upside_20d`, and `prism_conflict_winner_rate` so skipped discovery candidates do not dilute account action lift failures.

Skipped discovery rows remain tracked separately:

```text
scanner_candidate_skipped_count
prism_candidate_skipped_count
```

The calibration summary includes:

```text
action_lift_denominator_count
actionable_not_ordered_count
actionable_not_ordered_rate
missed_upside_5d
missed_upside_20d
prism_conflict_winner_rate
scanner_candidate_skipped_count
prism_candidate_skipped_count
```
