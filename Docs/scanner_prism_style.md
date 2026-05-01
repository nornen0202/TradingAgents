# PRISM-Style Scanner

The scanner is an optional universe selector. It discovers candidates from local OHLCV snapshots and can include PRISM advisory signals, but it never places orders.

## Config

```toml
[scanner]
enabled = true
market = "KR"
local_ohlcv_path = "tests/fixtures/scanner/kr_ohlcv_snapshot.json"
max_candidates = 10
max_new_tickers_per_run = 5
include_prism_candidates = true
prism_candidate_market_filter = "same_market" # same_market | all | disabled
```

When disabled, scheduled runs use the configured tickers and portfolio profile exactly as before.

## Trigger Types

- `VOLUME_SURGE`
- `GAP_UP_MOMENTUM`
- `VALUE_TO_MARKET_CAP_INFLOW`
- `DAILY_RISE_TOP`
- `CLOSING_STRENGTH`
- `VOLUME_SURGE_FLAT`
- `NEAR_52W_HIGH`
- `SECTOR_LEADER`
- `CONTRARIAN_VALUE_SUPPORT`

Default KR filters remove low-liquidity names, small market caps, and daily movers above 20%.

Scanner output is saved to:

```text
scanner/scanner_candidates.json
```

The scheduled analysis universe is:

```text
configured/account tickers + scanner top N + PRISM candidate top N
```

deduped and capped by `max_new_tickers_per_run`.

By default, PRISM candidates are imported only when their inferred market matches `[scanner].market` and the scheduled run market. This prevents a US run from importing KR dashboard tickers such as `000660.KS`. If PRISM external data is mostly cross-market, scanner warnings use this form:

```text
PRISM 후보 226개 중 현재 시장 US와 일치하지 않아 226개 제외
```

Scanner artifacts include source counters:

```text
scanner_discovered
prism_imported_same_market
prism_excluded_cross_market
```

Use `prism_candidate_market_filter = "all"` only for explicit cross-market research workflows. Use `"disabled"` to keep PRISM data in the portfolio comparison layer while disabling scanner-side PRISM candidate import.
