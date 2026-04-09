<p align="center">
  <img src="assets/TauricResearch.png" style="width: 60%; height: auto;">
</p>

# TradingAgents: Multi-Agent LLM Financial Trading Framework

Korean documentation: [README.md](README.md)

## Overview

TradingAgents is a multi-agent market analysis framework that mirrors the workflow of a real trading desk. Fundamental, news, sentiment, and market analysts produce specialized reports, then researchers, the trader, the risk team, and the portfolio manager synthesize them into a final decision.

As of the current `main` branch, the repository includes:

- multi-provider support for `openai`, `codex`, `google`, `anthropic`, `xai`, `openrouter`, and `ollama`
- split model roles for `quick_think_llm`, `deep_think_llm`, and `output_think_llm`
- structured final decision parsing and quality signals
- non-interactive scheduled analysis plus a static report site
- a default local Korean localization path using `NLLB-200-distilled-600M + CTranslate2`
- scheduled config support for `ticker_names`, `quality_flags`, `batch_metrics`, and `warnings`

This project is for research purposes. It is not financial advice, and outputs can vary materially depending on models, prompts, data quality, and market conditions.

## Quick Start

### Clone the repository

```bash
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
```

### Recommended Windows PowerShell setup

```powershell
Set-Location C:\Projects\TradingAgents
py -3.13 -m venv .venv-codex
.\.venv-codex\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e . --no-cache-dir
tradingagents --help
```

To enable the default local translation backend for scheduled Korean reports:

```powershell
python -m pip install -e ".[translation]"
```

### Docker

```bash
cp .env.example .env
docker compose run --rm tradingagents
```

For local models with Ollama:

```bash
docker compose --profile ollama run --rm tradingagents-ollama
```

## LLM Configuration

The base config lives in [tradingagents/default_config.py](tradingagents/default_config.py).

Current default model roles on `main` are:

- `quick_think_llm`: `gpt-5.4-mini`
- `deep_think_llm`: `gpt-5.4`
- `output_think_llm`: `gpt-5.2`

Example:

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "codex"
config["quick_think_llm"] = "gpt-5.4-mini"
config["deep_think_llm"] = "gpt-5.4"
config["output_think_llm"] = "gpt-5.2"

graph = TradingAgentsGraph(debug=True, config=config)
final_state, decision = graph.propagate("NVDA", "2026-01-15")
print(decision)
```

When `llm_provider = "codex"`, these extra knobs are available:

- `codex_binary`
- `codex_reasoning_effort`
- `codex_summary`
- `codex_personality`
- `codex_workspace_dir`
- `codex_request_timeout`
- `codex_max_retries`
- `codex_cleanup_threads`

## API Key Setup

TradingAgents resolves credentials in this order:

1. environment variables
2. `.env` values loaded by the CLI
3. documentation fallback from [Docs/list_api_keys.md](Docs/list_api_keys.md) for selected vendors

### 1. Environment variables or `.env`

This is the recommended path for most users.

```bash
export OPENAI_API_KEY=...
export GOOGLE_API_KEY=...
export ANTHROPIC_API_KEY=...
export XAI_API_KEY=...
export OPENROUTER_API_KEY=...
export ALPHA_VANTAGE_API_KEY=...
export NAVER_CLIENT_ID=...
export NAVER_CLIENT_SECRET=...
export OPENDART_API_KEY=...
export ECOS_API_KEY=...
export KRX_API_KEY=...
```

If you prefer `.env`, place it at the repo root. The CLI loads it automatically:

```dotenv
OPENAI_API_KEY=
GOOGLE_API_KEY=
ANTHROPIC_API_KEY=
XAI_API_KEY=
OPENROUTER_API_KEY=
ALPHA_VANTAGE_API_KEY=
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
OPENDART_API_KEY=
ECOS_API_KEY=
KRX_API_KEY=
```

### 2. `Docs/list_api_keys.md` fallback

Based on [tradingagents/dataflows/api_keys.py](tradingagents/dataflows/api_keys.py), the project can also read these values from [Docs/list_api_keys.md](Docs/list_api_keys.md):

- `ALPHA_VANTAGE_API_KEY`
- `NAVER_CLIENT_ID`
- `NAVER_CLIENT_SECRET`
- `OPENDART_API_KEY`

Expected format:

```md
Alpha Vantage: your-alpha-vantage-key

Naver:
- Client ID: your-client-id
- Client Secret: your-client-secret

OpenDart: your-opendart-key
```

### 3. Supported environment variable aliases

The latest implementation also accepts these aliases:

- Alpha Vantage: `ALPHA_VANTAGE_API_KEY`, `ALPHA_VANTAGE_KEY`
- Naver client ID: `NAVER_CLIENT_ID`, `NAVER_API_CLIENT_ID`
- Naver client secret: `NAVER_CLIENT_SECRET`, `NAVER_API_CLIENT_SECRET`
- OpenDart: `OPENDART_API_KEY`, `OPEN_DART_API_KEY`, `OPENDART_KEY`

Notes:

- placeholder values such as `REDACTED`, `TODO`, and `CHANGEME` are ignored
- for GitHub Actions or shared environments, prefer repository secrets or runner environment variables over committing keys into docs

## Codex Provider

The `codex` provider does not require an OpenAI API key. It requires a valid Codex CLI login:

```bash
codex login
```

or:

```bash
codex login --device-auth
```

Recommended `~/.codex/config.toml`:

```toml
approval_policy = "never"
sandbox_mode = "read-only"
web_search = "disabled"
personality = "none"
cli_auth_credentials_store = "file"
```

Notes:

- TradingAgents talks to `codex app-server` over stdio
- it keeps LangGraph `ToolNode` execution inside the project
- it does not use Codex dynamic tools
- each model invocation runs in a fresh ephemeral Codex thread
- the default workspace is `~/.codex/tradingagents-workspace`

On Windows, you can override binary discovery explicitly:

```powershell
$env:CODEX_BINARY = "C:\full\path\to\codex.exe"
```

## Scheduled Analysis and Static Reports

Non-interactive runs use the TOML configs under `config/`, such as [config/scheduled_analysis.toml](config/scheduled_analysis.toml).

Important current fields include:

- `[run]`
  - `tickers`
  - `analysts`
  - `output_language`
  - `trade_date_mode`
  - `timezone`
  - `max_debate_rounds`
  - `max_risk_discuss_rounds`
  - `continue_on_ticker_error`
- `[llm]`
  - `provider`
  - `quick_model`
  - `deep_model`
  - `output_model`
- `[translation]`
  - `backend`
  - `model`
  - `model_path`
  - `tokenizer_path`
  - `device`
  - `allow_llm_fallback`
  - `allow_large_model`
- `[storage]`
  - `archive_dir`
  - `site_dir`
- `[ticker_names]`
  - optional display-name overrides for tickers

Run it with:

```powershell
.\.venv-codex\Scripts\Activate.ps1
python -m tradingagents.scheduled --config config/scheduled_analysis.toml
```

or:

```powershell
tradingagents-scheduled --config config/scheduled_analysis.toml
```

Artifacts include `run.json`, per-ticker `analysis.json`, `final_state.json`, markdown reports, `quality_flags`, `batch_metrics`, and top-level `warnings`.

## Local Translation Backend

The current default scheduled localization path is `nllb_ct2`.

- recommended default: `translation.backend = "nllb_ct2"`
- default model: `translation.model = "nllb-200-distilled-600m"`
- optional larger path: `translation.backend = "madlad_ct2"` with `translation.model = "madlad-400-3b"`
- `madlad_ct2` is blocked unless `allow_large_model = true`
- content that already looks Korean is skipped
- only the 12 report-facing fields are localized

Example GitHub Actions repository variables for a self-hosted runner:

```text
TRADINGAGENTS_TRANSLATION_MODEL_PATH=C:\models\nllb-200-distilled-600m-ct2
TRADINGAGENTS_TRANSLATION_TOKENIZER_PATH=C:\models\nllb-200-distilled-600m
TRADINGAGENTS_TRANSLATION_DEVICE=auto
TRADINGAGENTS_ALLOW_LARGE_TRANSLATION_MODEL=0
```

## CLI

```powershell
Set-Location C:\Projects\TradingAgents
.\.venv-codex\Scripts\Activate.ps1
tradingagents
```

Alternative:

```powershell
python -m cli.main
```

## Contributing

Contributions are welcome, whether you are fixing bugs, improving docs, or proposing new capabilities.

## Citation

If TradingAgents is helpful in your work, please cite:

```bibtex
@misc{xiao2025tradingagentsmultiagentsllmfinancial,
      title={TradingAgents: Multi-Agents LLM Financial Trading Framework},
      author={Yijia Xiao and Edward Sun and Di Luo and Wei Wang},
      year={2025},
      eprint={2412.20138},
      archivePrefix={arXiv},
      primaryClass={q-fin.TR},
      url={https://arxiv.org/abs/2412.20138},
}
```
