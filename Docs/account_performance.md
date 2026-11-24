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

KIS `inquire-period-trade-profit` fields such as `tot_rlzt_pfls` and `tot_pftrt` are normalized as realized trade diagnostics:

- `realized_trade_pnl_krw`
- `realized_trade_return_pct`
- `trade_fees_krw`
- `trade_taxes_krw`

They are not promoted into `balance_return_pct`, because the endpoint is a period trade-profit view rather than whole-account NAV performance.

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

For KIS domestic stock accounts, TradingAgents automatically queries the official account endpoints that are available in the project integration: order fills, period profit, period trade profit, and period account-rights rows. Period-rights rows can add dated dividend/rights cash events to reconciliation. The current official domestic-stock samples do not expose a general dated external deposit/withdrawal ledger for ordinary stock accounts, so exact DCA comparison is still marked unavailable with `etf_alternative_cashflow_dates_required` when only aggregate cashflow information is available. TradingAgents does not turn aggregate deposits into fake single-date cashflows. CSV/JSON cashflow files remain an optional fallback when the broker does not provide a dated API source.

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

Period rows keep raw calculated returns in JSON for audit, but public display uses `display_eligible=false` and `trust_state=unreconciled_reference` so the default investor page can hide untrusted snapshot returns and leave them only in diagnostics.

KR contribution rows are aggregated by canonical ticker. For example, realized PnL from a KIS ledger row such as `000660` is merged into a held Yahoo-style position such as `000660.KS` when the account positions identify the same six-digit code. Unresolved bare codes remain separate and add a diagnostic warning.

## Provider Fallback

`data_quality.benchmark_provider_status` records preferred and used price providers by benchmark. The investor view shows actual provider status per benchmark, for example `KOSPI/KOSDAQ = KIS` or `SPY/QQQ = KIS failed, yfinance fallback`. The global configured provider is diagnostic context only, and raw provider URLs/errors remain in diagnostics for audit.

## Chart Consistency

The chart uses the same return method and actual window as the summary. Chart metadata includes `final_return`, `peak_return`, `max_drawdown`, and `consistency_status`. The investor view labels peak return as "period high" so intermediate chart highs are not confused with the final headline return.

## 추천 가격의 단위와 기존 데이터

정규 writer는 시간·원천·조정 기준이 있는 원통화 가격을 `recommended_price`와 `price_reference_json`에 저장합니다. KRW 환산 단가와 총 평가액은 각각 `display_unit_price_krw`와 `valuation_amount_krw`로 분리됩니다. 근거가 없는 가격, 통화가 맞지 않는 가격과 판단 이후 취득된 가격은 새 추천의 성과 기준가를 비워 두고 이유를 남깁니다. KIS 장중 분봉은 완료된 봉의 응답을 근거로 사용합니다. [KIS 해외 분봉 예제](https://github.com/koreainvestment/open-trading-api/tree/main/examples_llm/overseas_stock/inquire_time_itemchartprice)

기존 행과 수익률은 보존합니다. 정상 보고서는 활성 검증 결과만 집계하고 가격 미확정·제외 건수를 보여 줍니다. 범위가 `-100% ~ -99%`인 행을 골라내는 것은 점검이며 통화 오염 확정에는 당시 출처와 단위 증거가 필요합니다. 아래 읽기 전용 명령은 전체, 최근 40,000개 결과와 최근 40,000개 추천을 구분합니다. SQLite 온라인 백업 API로 일관된 사본을 만든 뒤 실행합니다.

```console
python -m tradingagents.performance.evidence_audit /private/performance-snapshot.sqlite
```

정정에 사용할 명시 근거를 검토한 뒤 `python -m tradingagents.performance.price_revisions`로 미리 봅니다. 검증 사본에는 `--revised-copy`를 사용합니다. 실제 실행기의 스키마 확장은 첫 writer에서 트랜잭션으로 진행되며 가격 정정은 별도의 append-only 영수증입니다. 원본 DB 승인 시에는 유휴 상태에서 백업·복원 검증을 먼저 하고 이후 발생한 쓰기를 보존합니다. 오래된 DB 백업 전체를 덮어쓰면 백업 이후 결과가 사라질 수 있으므로 일반적인 표시 원복에는 후속 정정이나 기존 읽기 모드를 사용합니다.
