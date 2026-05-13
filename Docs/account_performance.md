# Account Performance vs Index/ETF

The scheduled portfolio report can publish an account performance section that compares account NAV against market indexes or ETFs. The section is designed for investor reading first and auditability second: the default view shows only trustworthy comparison windows, while raw period calculations and provider warnings remain in diagnostics and downloadable JSON.

## Return Methods

- `broker_performance`: when Korea Investment broker-reported period performance is available, the investor report treats it as the primary account-performance source. The internal TradingAgents snapshot return remains a secondary diagnostic calculation.
- `simple_nav_return`: `(end_nav - start_nav) / start_nav`. This is easy to audit, but it is only a clean performance return when there were no material external cashflows during the window.
- `twr_return`: time-weighted return adjusted for classified external capital flows. TradingAgents uses dated account snapshots and classified deposit/withdrawal events to remove the effect of capital moving into or out of the account.
- `mwr_return`: reserved for money-weighted IRR when dated external cashflows are complete enough. When it cannot be computed, `mwr_unavailable_reason` explains why.
- `primary_return`: the return shown in the investor headline. It is TWR when classified external capital flows are present and computable. If there are no external capital flows and reconciliation is clean, the report labels the result as `TWR-equivalent` simple NAV. If cashflow classification is incomplete, simple NAV is shown only as a cashflow-unadjusted reference value.

If ledger rows suggest cash movement but cannot be classified, the report sets `return_method_warning = "cashflow_adjustment_unavailable"` and labels the headline as cashflow-unadjusted simple NAV. TWR and MWR unavailable states are explicit in JSON and in the investor notes.

If broker performance reports deposits or withdrawals while the internal ledger does not classify external capital flows, TradingAgents no longer labels the snapshot return as TWR-equivalent. It marks the snapshot return as cashflow-unadjusted and emits `account_performance_broker_external_flows_not_in_snapshot_ledger`.

## Broker-Reported Performance

For KIS domestic profiles, the engine can read the broker period-profit summary through the existing KIS period profit APIs or through a private JSON/CSV baseline configured with:

```toml
[portfolio_performance]
broker_return_baseline_path = ""
broker_period_start = ""
broker_period_end = ""
prefer_broker_reported_performance = true
show_snapshot_performance_when_unreconciled = false
```

Normalized artifacts are written alongside the account performance artifacts:

- `broker_performance_raw.json`
- `broker_performance_normalized.json`
- `broker_performance_comparison.json`

The comparison artifact checks broker ending assets against the TradingAgents account value, compares broker return with the internal simple NAV return, records period/scope alignment, and reports `OK`, `WARNING`, or `FAILED`.

The broker app-style formulas are:

- `investment_pnl_krw = end_asset_krw - start_asset_krw - deposit_amount_krw + withdrawal_amount_krw`
- `balance_return_pct = investment_pnl_krw / (start_asset_krw + deposit_amount_krw - withdrawal_amount_krw) * 100`
- `total_deposit_return_pct = investment_pnl_krw / (start_asset_krw + deposit_amount_krw) * 100`

## Period Coverage

Each period includes `period_coverage`:

- `requested_start_date`: requested window start, such as YTD or 1Y.
- `actual_start_date`: first usable account snapshot used for the calculation.
- `coverage_ratio`: actual days divided by requested days when calculable.
- `is_summary_eligible`: false when coverage is below the configured threshold, defaults to `0.8`, or when the row duplicates another actual window.
- `same_actual_window_as`: set when several requested periods collapse to the same snapshot window.

When account history starts late, the investor table does not show duplicated 1M/3M/6M/YTD/1Y rows as independent performance. It uses `ALL_AVAILABLE` / `사용 가능 전체 기간` as the headline window and keeps raw period rows under diagnostics.

`min_coverage_ratio` defaults to `0.8`. Setting it to `0.0` intentionally disables the coverage gate; values below `0.0` or above `1.0` are clamped.

## Same-Cashflow Benchmark

The same-cashflow benchmark simulates buying or selling benchmark shares only for external capital flows:

- Included as capital flows: deposits and withdrawals.
- Not included as capital flows: internal stock BUY/SELL trades.
- Classified but not injected into benchmark capital: dividends, interest, fees, taxes, and FX conversion details.
- Unknown ledger rows are not applied to same-cashflow benchmark simulation.

This keeps internal rebalancing from being mistaken for investor contributions or withdrawals.

## Same-Deposit-Date ETF DCA Benchmark

When dated deposit/withdrawal cashflows and ETF price data are available, TradingAgents also builds virtual ETF portfolios for the same account period. The primary comparison is broker-reported account performance versus a virtual account that buys benchmark ETFs on the same cashflow dates.

Artifacts:

- `etf_dca_comparison.json`
- `etf_dca_benchmark_results.json`
- `etf_dca_benchmark_transactions.json`
- `etf_dca_equity_curves.json`
- `etf_dca_policy_recommendation.json`
- `etf_alternative_portfolios_public.json`
- `cashflows_audit.json`

If KIS only provides aggregate deposits and withdrawals, exact DCA comparison is marked unavailable with `etf_alternative_cashflow_dates_required`. TradingAgents does not turn aggregate deposits into fake single-date cashflows.

The DCA benchmark formulas mirror the broker app-style return:

- `benchmark_pnl_krw = benchmark_end_value_krw - seed_asset_krw - deposit_amount_krw + withdrawal_amount_krw`
- `benchmark_balance_return_pct = benchmark_pnl_krw / (seed_asset_krw + deposit_amount_krw - withdrawal_amount_krw) * 100`

The default ETF universe and manual cashflow CSV format are documented in [etf_dca_benchmark.md](etf_dca_benchmark.md).
The public comparison payload includes `exact_dated_cashflows_available`, `actual_vs_benchmark`, `best_benchmark_id`, `blended_benchmark_id`, and redacted cashflow markers. Exact dated cashflow amounts remain private.

## Reconciliation

The report emits a reconciliation block:

```json
{
  "start_nav_krw": 0,
  "end_nav_krw": 0,
  "simple_nav_pnl_krw": 0,
  "sum_position_contribution_krw": 0,
  "external_cashflow_net_krw": null,
  "fees_taxes_krw": 0,
  "unexplained_difference_krw": 0,
  "unexplained_difference_pct_of_nav": 0.0,
  "reconciliation_status": "OK"
}
```

Reconciliation uses NAV movement, summed realized/unrealized contribution rows, known external cashflows, and fees/taxes. Materiality thresholds are:

- `OK`: unexplained difference up to 2% of ending NAV.
- `WARNING`: above 2% and up to 5%.
- `FAILED`: above 5%; above 20% is marked critical.

If reconciliation fails, `summary.performance_confidence` becomes `low`, `hide_excess_headline` is true, and the investor view demotes benchmark excess values to "manual reconciliation required" instead of presenting them as a headline.

KR contribution rows are aggregated by canonical ticker. For example, realized PnL from a KIS ledger row such as `000660` is merged into a held Yahoo-style position such as `000660.KS` when the account positions identify the same six-digit code. Unresolved bare codes remain separate and add a diagnostic warning.

## Provider Fallback

`data_quality.benchmark_provider_status` records preferred and used price providers by benchmark. The investor view shows actual provider status per benchmark, for example `KOSPI/KOSDAQ = KIS` or `SPY/QQQ = KIS failed, yfinance fallback`. The global configured provider is diagnostic context only, and raw provider URLs/errors remain in diagnostics for audit.

## Chart Consistency

The chart uses the same return method and actual window as the summary. Chart metadata includes `final_return`, `peak_return`, `max_drawdown`, and `consistency_status`. The investor view labels peak return as "period high" so intermediate chart highs are not confused with the final headline return.
