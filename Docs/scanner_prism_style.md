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
