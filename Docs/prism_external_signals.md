# PRISM External Signals

TradingAgents treats PRISM data as advisory external evidence. PRISM can confirm, challenge, or enrich a TradingAgents view, but it cannot bypass TradingAgents risk gates, account constraints, portfolio allocation, or execution approval.

## Sources

Configured source priority:

1. `PRISM_DASHBOARD_JSON_PATH` or `[external.prism].local_dashboard_json_path`
2. `PRISM_SQLITE_DB_PATH` or `[external.prism].local_sqlite_db_path`
3. `PRISM_DASHBOARD_JSON_URL` when `use_live_http = true`
4. `PRISM_DASHBOARD_BASE_URL` candidate JSON endpoints when `use_live_http = true`
5. dashboard HTML embedded JSON only when both `use_live_http = true` and `use_html_scraping = true`
6. graceful empty result

Live HTTP is disabled by default. HTML scraping is also disabled by default and is implemented only as an opt-in fallback for dashboard pages that embed JSON in script tags. Tests do not call live dashboards unless `RUN_LIVE_PRISM_TESTS=1`.

## Example

```toml
[external.prism]
enabled = true
mode = "advisory"
local_dashboard_json_path = "C:/Projects/prism-insight/examples/dashboard/public/dashboard_data.json"
use_live_http = false
use_html_scraping = false
confidence_cap = 0.25
```

Live dashboard JSON can be enabled explicitly:

```toml
[external.prism]
enabled = true
mode = "advisory"
dashboard_json_url = "https://analysis.stocksimulation.kr/dashboard_data.json"
use_live_http = true
use_html_scraping = false
```

HTML fallback remains a separate opt-in:

```toml
[external.prism]
enabled = true
dashboard_base_url = "https://analysis.stocksimulation.kr"
use_live_http = true
use_html_scraping = true
```

Environment overrides:

```text
PRISM_EXTERNAL_ENABLED
PRISM_DASHBOARD_JSON_PATH
PRISM_SQLITE_DB_PATH
PRISM_DASHBOARD_JSON_URL
PRISM_DASHBOARD_BASE_URL
PRISM_USE_LIVE_HTTP
PRISM_USE_HTML_SCRAPING
PRISM_TIMEOUT_SECONDS
PRISM_MAX_PAYLOAD_BYTES
```

The live adapter enforces request timeout, content-type checks, max payload bytes, JSON validation, warnings, and graceful fallback. HTML parsing only extracts JSON payloads from script tags and does not place orders or interact with browser controls.

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
