# Local Translation Backend

TradingAgents scheduled configs now default to a local report-localization path:

- Backend: `nllb_ct2`
- Model alias: `nllb-200-distilled-600m`
- Runtime: CTranslate2
- Fallback: LLM fallback stays enabled unless you turn it off

## What changed

- Only the 12 fields that are rendered in `complete_report.md` are localized
- Debate transcripts and intermediate response fields are no longer rewritten
- Korean-looking content is skipped so we do not retranslate text that is already localized

## Runner setup

1. Install translation extras:
   `pip install ".[translation]"`
2. Convert or place a CTranslate2 model on the runner.
3. Point the workflow at the local model directory with repository variables:

```text
TRADINGAGENTS_TRANSLATION_MODEL_PATH=C:\models\nllb-200-distilled-600m-ct2
TRADINGAGENTS_TRANSLATION_TOKENIZER_PATH=C:\models\nllb-200-distilled-600m
TRADINGAGENTS_TRANSLATION_DEVICE=auto
TRADINGAGENTS_ALLOW_LARGE_TRANSLATION_MODEL=0
```

## MADLAD option

`madlad_ct2` is available as an opt-in backend for users who want to test a larger document-oriented model:

```toml
[translation]
backend = "madlad_ct2"
model = "madlad-400-3b"
allow_large_model = true
```

Use it only after checking runner RAM/VRAM and runtime headroom. The code intentionally blocks this backend unless `allow_large_model` is enabled.
