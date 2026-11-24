# Isolated paper control recovery

The control ledger binds signed status, positions, halt, and flatten requests to one isolated paper scope and a fenced writer. A flatten request preserves a single, stable set of sell intent identifiers. A transport must revalidate fresh native quotes, current sellable shares, the order journal, and broker capabilities before sending those intents. The controls carry no live order authority.

## Local rehearsal

1. Freeze and record the paper account scope, software revision, risk policy, calendar, cost model, authorization roles, operator, and independently configured standby. Use distinct writer identities. Make an online database backup and run an integrity check on a restored copy.
2. Rehearse with an isolated ledger and fixture broker. Verify an expired, mismatched, or duplicate signed request and a writer from the former epoch cannot create another order.
3. Simulate a transport disconnect after acknowledgement and after each partial execution. Keep periodic reports independent of account snapshots and broker retry state. Reconnect and reconcile authenticated account cash, positions, open orders, and every uncertain submission before admitting new risk.
4. Apply the halt, cancel pending paper orders, and reconcile cancellation. Recover flatten intent identities from the replacement writer. Treat a replay as the same set of intents. Verify flat positions and the settlement receipt before closing the incident.
5. Keep both systems halted if the snapshot is incomplete, the broker scope cannot be verified, or writer fencing cannot be demonstrated.

An expired, provably unsubmitted order can retain its intent ID under a new signed request and current quotes. A verified terminal partial fill requires a separate intent for the reconciled remaining shares. Open or uncertain orders must be reconciled before any request for a remainder.

## Offline domestic KIS replay

`tradingagents paper-replay init --workspace <new-directory>` initializes a dedicated local workspace. Put the fixture producer archive in its `archive/runs` tree using the regular run, decision bundle, proposal, and execution contract formats. Each action input is JSON with schema `tradingagents.isolated-kis-replay/v1` and an explicit offset-aware `as_of`. Fixtures can be invoked from the scheduler entry point with `python -m tradingagents.local_automation strategy-kis --isolated-replay <workspace> --replay-action <action> --fixture-input <fixture>`.

The `tick` input supplies the domestic ticker universe, KIS quote and index observations, and responses keyed by VTS transaction code. The local preview returns a one-use approval callback for the exact terms. A separate `callback` invocation accepts an authenticated Telegram-format update from the fixture actor, bot, and chat. Its secret is generated in the local workspace marker. Leave that marker and any callback payload in the local workspace. A second tick refreshes the quote and checks the decision expiry before the guarded KIS broker reaches its offline transport.

Use `inspect-orders` for a read-only daily-order requery after an unknown response. The result gives the row count and preserves the unknown journal state. The `settlement` action attaches source bytes and reviewed execution details to reconciled fills. The replay requires this evidence before increasing exposure after a filled sale, alongside the broker's current cash-only capacity. `promotion-start`, `promotion-record`, and `promotion-status` exercise a frozen fixture policy and the observed settlement session. Promotion remains blocked by the fixture evidence scope. `tests/execution/test_isolated_replay.py` supplies complete payload examples.

## Remote prerequisites

Remote failover needs one shared transactional writer authority with monotonic fencing, independent heartbeats, and deterministic account binding. Use infrastructure and a broker adapter that enforce the fence at the write boundary. The local SQLite lease supports same-journal rehearsal and cannot enforce a fence across separate database copies or independently connected brokers. Copy databases only as backup or under a documented cutover with the prior writer fenced out. Keep the standby disabled until those controls are verified.

If the restored paper environment cannot reconcile all orders or match the recorded scope, keep it isolated. Roll back to the recorded software and risk-policy revision on a verified copy. Do not clear command nonces or resubmit unknown intents. A new scope or a change to any live transport requires independent review and authorization.
