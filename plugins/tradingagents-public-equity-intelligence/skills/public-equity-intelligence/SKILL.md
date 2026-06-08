---
name: public-equity-intelligence
description: Use TradingAgents public-equity intelligence workflows for source-linked company research, earnings review, thesis tracking, and portfolio risk checks.
---

# Public Equity Intelligence

Use this skill when the user asks Codex to review a public stock, compare a company, prepare an earnings memo, update an investment thesis, or assess whether evidence strengthens or weakens a TradingAgents recommendation.

## Workflow

1. Inspect the latest scheduled run artifacts for the ticker.
   - Prefer `public_equity_intelligence.json`, `source_quality.json`, `evidence_ledger.json`, `earnings_event_pack.json`, and `thesis_tracker.json`.
   - Fall back to `analysis.json`, report markdown, and portfolio artifacts when the intelligence sidecars are absent.
2. Check source posture before making investment comments.
   - Report `source_quality_score`, `source_cohort`, transcript availability, estimate revision direction, and missing paid-vendor limitations.
   - Never treat unavailable FactSet, LSEG, S&P Global, Daloopa, Moody's, PitchBook, Datasite, Hebbia, Quartr, Morningstar, or Third Bridge data as negative evidence.
3. Separate company thesis from security readiness.
   - Company thesis: fundamentals, guidance, earnings quality, competitive position, credit risk, diligence context.
   - Security readiness: price setup, execution overlay, risk gate, account constraints, liquidity, event timing.
4. Use falsifiable language.
   - State what would strengthen, weaken, or invalidate the thesis.
   - Cite the artifact or provider source for important claims.

## Useful Commands

Run a scheduled analysis:

```powershell
python -m tradingagents.scheduled.runner --config config/scheduled_analysis.toml
```

Rebuild the static site from existing archived runs:

```powershell
python -m tradingagents.scheduled.runner --config config/scheduled_analysis.toml --site-only
```

Run focused tests:

```powershell
python -m pytest tests/test_institutional_intelligence.py tests/test_api_keys.py tests/test_vendor_fallback.py
```

## Vendor Imports

Optional exports can be placed under:

```text
data/institutional/<provider>/<TICKER>/<capability>.json
```

Supported provider ids include `daloopa`, `quartr`, `factset`, `lseg`, `spglobal`, `moodys`, `morningstar`, `pitchbook`, `datasite`, `hebbia`, and `third_bridge`.

The implementation must remain advisory. Vendor evidence can inform a recommendation, but it must not bypass risk gates, account constraints, execution overlays, or order approval.
