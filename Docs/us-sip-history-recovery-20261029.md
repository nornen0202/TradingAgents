# Complete SIP history recovery

CVX, BRK-B and PM failed because Yahoo's final close was invalid and KIS returned malformed historical OHLCV. The existing Alpaca connection provides a complete alternative when the request ends at the latest completed regular-session close. A broad recent end had returned HTTP403; the official historical-data contract permits delayed SIP queries. No subscription or permission changes are required.

The opt-in fallback follows Yahoo and KIS failures and retrieves one complete SIP series with adjustment=all. It binds symbol mapping to the analysis date, enforces the full five-year expected-session set and OHLCV rules, excludes future/out-of-window rows, fails on unknown dates/conflicting duplicates, and bounds time/pagination. Prices and indicators pin the same immutable selected series and evidence receipt; it never patches individual KIS/Yahoo rows. Metadata explicitly does not claim a historical snapshot vintage.

Local automation enables the fallback only when the existing Alpaca credentials are configured. HTTP errors do not trigger unbounded retries or feed/subscription changes. A recent session inside the historical delay fails closed.

Read-only live validation for the 2026-10-28 cutoff returned1,255 complete valid sessions for each of CVX, BRK.B and PM. Offline tests cover valid, empty, missing, future, unknown/malformed dates, invalid OHLCV, duplicate conflicts, pagination, denied requests, provenance and source pinning.

Official references:
- https://docs.alpaca.markets/us/reference/stockbars
- https://docs.alpaca.markets/us/docs/market-data-faq
