# Read-only regular-session market evidence

The local automation run-due command checks for forward-observation/policy.json inside its private state directory. A configured watchlist enables the existing market-data collection window. The policy may list up to 50 symbols with explicit venue and currency inferred from the market. Each pass sends at most four symbol requests through the existing KIS pacer. Later passes resume from the successful session records and apply the failure cooldown.

Example policy.json

    {
      "schema": "tradingagents.forward-market-observation/v1",
      "instruments": [
        {"ticker": "069500.KS", "market": "KR", "venue": "J"},
        {"ticker": "SPY", "market": "US", "venue": "AMS"}
      ]
    }

Use an independent read-only pass or inspect its coverage with the same installed Python environment.

    python -m tradingagents.execution.session_observations /private/forward-observation
    python -m tradingagents.execution.session_observations /private/forward-observation --status

For a standalone collector, --operations-state reads the existing paper strategy settings to explain operating exclusions. The command uses dedicated KIS demo credentials and fixed quotation endpoints. Positions, account orders, and broker actions are outside its access.

A verified KR opening price received within 30 seconds can supply the receipt-time bound for the exact next session. Late opening values and provisional KIS US opening values remain in the research archive. Daily close observations require the exact unadjusted exchange row and a post-close collection window. The collector uses the exchange calendar and preserves provider receipt times independently of the session clocks. The SQLite evidence retains the decoded provider response in canonical JSON and its content hash. Keep the entire folder private.

Scheduled research uses the same root for its private daily-history capture unless explicitly configured otherwise. The regular overlay reads eligible records directly from observations.sqlite. A CLI profile can supply [execution].session_observation_db. An explicitly configured legacy confirmation receipt directory continues to work. Historical adjustments and research captures retain their separate source and basis.

When the existing observer runs independently, place a forward-observation-source.json in the scheduler's private state directory with a database key containing the absolute path to its observations.sqlite. The scheduler opens this database read-only with the registered sibling policy.json. The pointer does not start an observer or route daily-history writes into that store. Legacy receipts retain their registered venue and are rechecked against the source bytes. A KIS US open is excluded from official open proof even if a legacy collector saved it as official.

Coverage uses completed exchange sessions after the watchlist registration. A missing collection stays in the denominator. The session report includes a read-only reason when the mock strategy is disabled or strategy evidence could not be assessed. The market-only observer cannot create a transaction outcome or write into the promotion ledger. Qualified forward evidence still requires the independently reconciled and monitored paper-session records.

## Private daily history for regular research

For a direct scheduled CLI run, set the existing [storage] daily_history_capture_db
in a private TOML profile. The automatic local scheduler reads the optional
daily_history_capture_db key in its existing private runtime-settings.json. Use an
absolute path outside both archive and publication directories. The immutable KR and US
full workers inherit this value, including parallel children. The existing explicit
TOML value takes precedence. This setting configures research storage only.

Back up the settings file before adding the key. Remove the key or restore the backup
to stop new captures. Previously retained rows remain append-only. Do not point the
capture at an existing account, order, observation or performance database. A storage
failure is reflected in the research evidence while the existing analysis can continue.

The private ticker evidence_ledger.json contains daily_price_history, with the original
run ID and the selected input receipts. With the configured database path, pass that ID
to DailyHistoryCapture(path, run_id) and the ledger entry's snapshot_id to
read_snapshot(snapshot_id). The read-only method verifies both the receipt identity and
exact normalized OHLCV bytes. Retried identical captures share the same record.
Reused reports keep their original run reference.

KIS and Alpaca receipts carry validated provider series terms. Alpaca's explicit USD
request records the returned price denomination contract, while native currency remains
unknown. Yahoo's fresh download records host receipt time and the explicit adjustment
request. The CSV cache can preserve selected values with no original retrieval clock or
adjustment proof. Source-only or unvalidated inputs can lack a stored snapshot. The ledger
keeps missing terms explicit and never uses retained research rows as trading evidence,
historical vintages, or replacements for older observations.
