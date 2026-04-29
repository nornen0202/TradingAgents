# PRISM External Signals

TradingAgents treats PRISM data as advisory external evidence. PRISM can confirm, challenge, or enrich a TradingAgents view, but it cannot bypass TradingAgents risk gates, account constraints, portfolio allocation, or execution approval.

## Sources

Configured source priority:

1. `PRISM_DASHBOARD_JSON_PATH` or `[external.prism].local_dashboard_json_path`
2. `PRISM_SQLITE_DB_PATH` or `[external.prism].local_sqlite_db_path`
3. `PRISM_DASHBOARD_JSON_URL` when `use_live_http = true`
4. `PRISM_DASHBOARD_BASE_URL` candidate JSON endpoints when `use_live_http = true`
5. graceful empty result

Live HTTP is disabled by default. Tests do not call live dashboards unless a test explicitly opts in.

## Example

```toml
[external.prism]
enabled = true
mode = "advisory"
local_dashboard_json_path = "C:/Projects/prism-insight/examples/dashboard/public/dashboard_data.json"
use_live_http = false
confidence_cap = 0.25
```

Environment overrides:

```text
PRISM_EXTERNAL_ENABLED
PRISM_DASHBOARD_JSON_PATH
PRISM_SQLITE_DB_PATH
PRISM_DASHBOARD_JSON_URL
PRISM_DASHBOARD_BASE_URL
PRISM_USE_LIVE_HTTP
PRISM_TIMEOUT_SECONDS
PRISM_MAX_PAYLOAD_BYTES
```

## Conflict Rules

- PRISM `BUY` plus TradingAgents `REDUCE_RISK`, `STOP_LOSS`, or `EXIT` creates a hard conflict and review requirement.
- PRISM `SELL` or `STOP_LOSS` plus TradingAgents `ADD_NOW` or `STARTER_NOW` blocks immediate buy and requires review.
- PRISM buy-side confirmation can improve ranking, capped by `confidence_cap`.
- PRISM watch-only signals can raise watchlist priority but do not create an automatic buy.

Artifacts are written under each run:

```text
external_signals/prism_signals.json
external_signals/prism_ingestion_status.json
external_signals/prism_reconciliation.json
```

The investor report shows agreement and conflict sections without exposing raw PRISM payload internals.
