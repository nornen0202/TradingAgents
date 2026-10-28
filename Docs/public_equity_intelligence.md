# Public Equity Intelligence

TradingAgents now supports a public-equity intelligence layer inspired by the OpenAI Financial Markets/Public Equity Investing workflow.

The default path is free/public-data first. Paid institutional vendors are optional and do not block a run when credentials or licenses are missing.

## What It Adds

- Source-linked evidence ledger for each ticker run.
- Earnings event pack artifact for actuals, guidance, consensus delta, transcript highlights, and catalysts.
- Thesis tracker artifact separating company-thesis evidence from security-thesis readiness.
- Provider catalog covering Yahoo Finance, Alpha Vantage, OpenDART, Naver, ECOS, KRX, SEC EDGAR, KIS, Massive/Polygon, Alpaca, Daloopa, Quartr, FactSet, LSEG, S&P Global, Moody's, Morningstar, PitchBook, Datasite, Hebbia, and Third Bridge.
- Portfolio/report metadata for source quality, source cohort, transcript availability, estimate revision direction, and thesis status.
- Action-performance cohorts so later results can compare `public_only` against `public_plus_institutional_imports`.

## Data Import Layout

Put optional vendor exports under:

```text
data/institutional/<provider>/<TICKER>/<capability>.json
data/institutional/<provider>/<TICKER>.json
data/institutional/<TICKER>/<provider>_<capability>.json
```

Examples:

```text
data/institutional/daloopa/NVDA/financials.json
data/institutional/quartr/NVDA/transcript.json
data/institutional/factset/NVDA/estimates.json
data/institutional/moodys/NVDA/credit.json
```

Useful JSON keys are:

- `source_refs` or `sources`
- `evidence_ledger`, `evidence`, or `items`
- `earnings_event_pack` or `earnings`
- `estimate_revision_direction`

Missing paid data is reported as a limitation, not treated as a failure.

### Point-in-time import contract

Every imported snapshot must include the actual publication time of that version
and the time it was observed, with explicit timezone offsets:

```json
{
  "timestamp_envelope": {
    "published_at": "2026-06-08T10:00:00Z",
    "observed_at": "2026-06-08T11:00:00Z"
  },
  "estimate_revision_direction": "neutral"
}
```

The analysis date is mandatory. The execution context's `analysis_as_of` can
only narrow it. Date-only cutoffs use the security's market timezone (Seoul for
Korean symbols, New York otherwise), capped at the current instant. Imports with
missing, invalid, naive, reversed, or future availability clocks are excluded
from tool responses, evidence, coverage, and source-quality calculations.
Declared nested publication, observation, amendment, and as-of dates must also
fall within the cutoff; an invalid nested clock rejects the snapshot.

A financial period end, filesystem timestamp, or assumed reporting delay cannot
establish publication. Revised exports need the actual publication clock of the
revision. A future `scheduled_at` may describe an event announced before the
cutoff; it does not establish that the event has occurred. Older undated imports
remain on disk but cannot influence historical analysis until their provenance
is supplied.

## Runtime Artifacts

Each successful scheduled ticker run can emit:

- `public_equity_intelligence.json`
- `source_quality.json`
- `evidence_ledger.json`
- `earnings_event_pack.json`
- `thesis_tracker.json`
- `public_equity_intelligence.md`

The static ticker page shows the compact source/evidence state and exposes the full artifacts as downloads.

## Safety Policy

Institutional data can increase confidence only through reviewable evidence. It must not bypass risk gates, account constraints, execution overlays, or explicit order approval.
