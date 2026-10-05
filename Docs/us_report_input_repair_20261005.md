# US report input repair — 2026-10-05

## Verified incident

The local Work report published on 2026-10-05 used production run
`20261002T230721_github-actions-us`: 30 selected symbols, 29 successful analyses,
and one failed analysis (ABBV). Every strategy row lacked a market observation
timestamp and price. The daily reference date was 2026-10-01. Report publication
did not refresh those inputs.

Two independent defects explain the symptoms:

1. The full-research workflow deliberately passes `--disable-execution-refresh`.
   Research agents nevertheless call `get_intraday_snapshot`. The tool result
   lived only in graph messages, which are cleared after each analyst. Neither
   the saved final state nor the strategy bundle retained that structured quote.
   The bundle obtained quotes exclusively from execution context, absent in this
   production run. The resulting missing timestamp was correctly reported as
   missing; report rendering was not the original loss point.
2. ABBV failed during sentiment analysis because two model responses contained
   serialization/control markers. Validation correctly rejected them with
   `CodexStructuredOutputError`. This was a model-output failure, not proof of a
   market-data outage. The Work packet exposed the failed symbol but omitted the
   existing safe diagnostic classification.

## Changes

- A per-ticker callback preserves an allowlisted host quote receipt through graph
  message cleanup. Successful and failed ticker artifacts and manifest summaries
  retain it. Receipt collection time stays separate from the provider quote time.
- The collector rejects wrong symbols, missing/naive/future quote clocks, and
  non-finite, non-positive or boolean prices. Provider failures remain explicit.
- When no execution context exists, strategy rows show the saved quote with
  `market_data_basis=RESEARCH_OBSERVATION`. This path cannot grant execution or
  conditional readiness. Existing execution context, including failed or partial
  context, always takes precedence and is never patched with an older quote.
- Local freshness receipts include observed/missing row counts. Work packets
  carry allowlisted analysis failure diagnostics. Public coverage metadata still
  omits private universe counts and failed holding membership.
- The US report prompt distinguishes research quotes, missing data and model
  output failures. Its contract is now `market-work-v13-us`.
- Response instructions prohibit control tokens and self-correction commentary.
  Repair instructions follow the transcript. The US configuration allows two
  retries (three total attempts), retaining strict validation and the same model.
  Rejected output is never stripped into an accepted report or replayed as evidence.

## Validation and historical limits

Regression tests cover actual graph message cleanup, success/failure archive
serialization, bundle/Work projection, invalid quotes, overlay precedence,
execution blocking, diagnostic privacy and recovery on the third model attempt.

The original archive and content-addressed Work report must remain unchanged.
Their missing quote clocks cannot be reconstructed from report prose, a daily
reference date, publication time or a newly fetched quote. Failed-only cohort
recovery rejects sources older than 24 hours; this October 2 source is outside
that window on October 5. A new complete production cohort is necessary to
replace the incomplete report. An isolated ABBV verification must not be
represented as completion of the original 30-symbol cohort.
