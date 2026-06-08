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
