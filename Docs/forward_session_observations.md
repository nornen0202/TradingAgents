# Read-only regular-session market evidence

The local automation run-due command checks for forward-observation/policy.json inside its private state directory. A configured watchlist enables the existing market-data collection window. The policy may list up to four symbols with explicit venue and currency inferred from the market.

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

An opening price received within 30 seconds can supply the receipt-time bound for the exact next session. A late quote remains in the research archive as a late open. Daily close observations require the exact unadjusted exchange row and a post-close collection window. The collector uses the exchange calendar and preserves provider receipt times independently of the session clocks. The SQLite evidence retains the decoded provider response in canonical JSON and its content hash. Keep the entire folder private.

Scheduled research uses the same root for its private daily-history capture unless explicitly configured otherwise. An eligible regular-session observation can be consumed by the execution overlay. Historical adjustments and research captures retain their separate source and basis.

Coverage uses completed exchange sessions after the watchlist registration. A missing collection stays in the denominator. The session report includes a read-only reason when the mock strategy is disabled or strategy evidence could not be assessed. The market-only observer cannot create a transaction outcome or write into the promotion ledger. Qualified forward evidence still requires the independently reconciled and monitored paper-session records.
