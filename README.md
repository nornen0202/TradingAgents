# TradingAgents: 멀티 에이전트 LLM 금융 트레이딩 프레임워크

영문 문서: [README.en.md](README.en.md)

## 소개

TradingAgents는 실제 트레이딩 조직의 협업 구조를 반영한 멀티 에이전트 분석 프레임워크입니다. 펀더멘털, 뉴스, 센티먼트, 시장 분석가가 각각 리포트를 만들고, 리서처와 트레이더, 리스크 관리 팀, 포트폴리오 매니저가 이를 종합해 최종 투자 판단을 만듭니다.

현재 `main` 브랜치 기준 구현에는 다음이 반영되어 있습니다.

- 다중 LLM provider 지원: `openai`, `codex`, `google`, `anthropic`, `xai`, `openrouter`, `ollama`
- 분리된 모델 역할: `quick_think_llm`, `deep_think_llm`, `output_think_llm`
- 구조화된 최종 의사결정 스키마와 품질 지표
- 비대화형 스케줄 실행과 정적 리포트 사이트 생성
- 한국어 출력용 로컬 번역 백엔드 기본값: `NLLB-200-distilled-600M + CTranslate2`
- 한국/미국 티커 스케줄 설정, `ticker_names` 오버라이드, `quality_flags`, `batch_metrics`, `warnings`

이 프로젝트는 연구 목적입니다. 실제 투자 판단이나 자문 용도로 사용하면 안 되며, 결과는 모델, 데이터, 프롬프트, 시장 상황에 따라 크게 달라질 수 있습니다.

## 빠른 시작

### 저장소 클론

```powershell
git clone https://github.com/TauricResearch/TradingAgents.git
Set-Location TradingAgents
```

### Windows PowerShell 권장 설치

```powershell
Set-Location C:\Projects\TradingAgents
py -3.13 -m venv .venv-codex
.\.venv-codex\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e . --no-cache-dir
tradingagents --help
```

한국어 스케줄 리포트를 로컬 번역기로 처리하려면 translation extras까지 설치합니다.

```powershell
python -m pip install -e ".[translation]"
```

### Docker

```powershell
Copy-Item .env.example .env
notepad .env
docker compose run --rm tradingagents
```

Ollama 프로필:

```powershell
docker compose --profile ollama run --rm tradingagents-ollama
```

## LLM 설정

기본 설정은 [default_config.py](tradingagents/default_config.py)에 있습니다.

최신 `main` 기준 기본 모델 역할은 아래와 같습니다.

- `quick_think_llm`: `gpt-5.4`
- `deep_think_llm`: `gpt-5.4`
- `output_think_llm`: `gpt-5.4`

예시:

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "codex"
config["quick_think_llm"] = "gpt-5.4"
config["deep_think_llm"] = "gpt-5.4"
config["output_think_llm"] = "gpt-5.4"

graph = TradingAgentsGraph(debug=True, config=config)
final_state, decision = graph.propagate("NVDA", "2026-01-15")
print(decision)
```

`codex` provider에서는 아래 설정도 추가로 지원합니다.

- `codex_binary`
- `codex_reasoning_effort`
- `codex_summary`
- `codex_personality`
- `codex_workspace_dir`
- `codex_request_timeout`
- `codex_max_retries`
- `codex_cleanup_threads`

## API 키 설정 방법

TradingAgents는 API 키를 다음 순서로 찾습니다.

1. 환경 변수
2. CLI가 자동 로드하는 `.env`
3. 로컬 [config/api_keys.json](config/api_keys.json) fallback
4. 구버전 호환용 `Docs/list_api_keys.md` fallback

### 1. 환경 변수 또는 `.env`

일반적으로는 이 방식이 가장 권장됩니다.

```powershell
$env:OPENAI_API_KEY = "..."
$env:GOOGLE_API_KEY = "..."
$env:ANTHROPIC_API_KEY = "..."
$env:XAI_API_KEY = "..."
$env:OPENROUTER_API_KEY = "..."
$env:ALPHA_VANTAGE_API_KEY = "..."
$env:NAVER_CLIENT_ID = "..."
$env:NAVER_CLIENT_SECRET = "..."
$env:OPENDART_API_KEY = "..."
$env:ECOS_API_KEY = "..."
$env:KRX_API_KEY = "..."
```

`.env`를 쓸 때는 저장소 루트에 아래처럼 넣으면 CLI가 자동으로 읽습니다.

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

### 2. `config/api_keys.json` fallback

[api_keys.py](tradingagents/dataflows/api_keys.py) 기준으로 아래 값은 로컬 [config/api_keys.json](config/api_keys.json) 파일에서도 읽습니다. 시작할 때는 [config/api_keys.example.json](config/api_keys.example.json)을 복사해서 쓰면 됩니다.

- `ALPHA_VANTAGE_API_KEY`
- `NAVER_CLIENT_ID`
- `NAVER_CLIENT_SECRET`
- `OPENDART_API_KEY`

예시는 아래 형식입니다.

```json
{
  "ALPHA_VANTAGE_API_KEY": "your-alpha-vantage-key",
  "NAVER_CLIENT_ID": "your-client-id",
  "NAVER_CLIENT_SECRET": "your-client-secret",
  "OPENDART_API_KEY": "your-opendart-key"
}
```

기본 위치가 아니라면 `TRADINGAGENTS_API_KEYS_PATH`로 경로를 지정할 수 있습니다.

### 3. 레거시 `Docs/list_api_keys.md` fallback

이전 클론은 기존 Markdown 형식도 계속 읽을 수 있지만, 새 설정은 `config/api_keys.json`을 권장합니다.

### 4. 지원하는 환경 변수 alias

최신 구현은 일부 alias 이름도 허용합니다.

- Alpha Vantage: `ALPHA_VANTAGE_API_KEY`, `ALPHA_VANTAGE_KEY`
- Naver Client ID: `NAVER_CLIENT_ID`, `NAVER_API_CLIENT_ID`
- Naver Client Secret: `NAVER_CLIENT_SECRET`, `NAVER_API_CLIENT_SECRET`
- OpenDart: `OPENDART_API_KEY`, `OPEN_DART_API_KEY`, `OPENDART_KEY`

주의:

- placeholder 값이나 `REDACTED`, `TODO`, `CHANGEME` 같은 값은 무시됩니다.
- 이 저장소의 GitHub Actions는 이미 workflow secrets를 통해 vendor 키를 주입하므로, 커밋된 `config/api_keys.json`이 없어도 실행에 의존하지 않습니다.
- 공유 환경에서는 API 키를 Git에 올리기보다 Secrets 또는 runner 환경 변수로 넣는 편이 안전합니다.

## Codex provider

`codex` provider는 OpenAI API 키 대신 Codex CLI 로그인이 필요합니다.

```powershell
where.exe codex
codex --version
codex login
```

또는:

```powershell
codex login --device-auth
```

권장 `~/.codex/config.toml` 예시:

```toml
approval_policy = "never"
sandbox_mode = "read-only"
web_search = "disabled"
personality = "none"
cli_auth_credentials_store = "file"
```

참고:

- TradingAgents는 `codex app-server`와 stdio로 직접 통신합니다.
- Codex dynamic tools는 사용하지 않습니다.
- 각 호출은 새로운 ephemeral Codex thread로 실행됩니다.
- 기본 작업 디렉터리는 `~/.codex/tradingagents-workspace`입니다.

Windows에서 자동 탐지를 덮어쓰려면:

```powershell
$env:CODEX_BINARY = "C:\full\path\to\codex.exe"
```

## 스케줄 분석과 정적 리포트 사이트

비대화형 실행은 [scheduled_analysis.toml](config/scheduled_analysis.toml) 계열 설정으로 동작합니다.

최신 `main` 기준 주요 필드:

- `[run]`
  - `tickers`
  - `analysts`
  - `output_language`
  - `trade_date_mode`
  - `timezone`
  - `max_debate_rounds`
  - `max_risk_discuss_rounds`
  - `continue_on_ticker_error`
  - `report_polisher_enabled`: 기본 `true`. `output_model`로 투자자용 요약을 한 번 더 정제하고, 실패 시 템플릿 요약으로 대체합니다.
- `[llm]`
  - `provider`
  - `quick_model`
  - `deep_model`
  - `output_model`
- `[portfolio]`
  - `enabled`
  - `semantic_judge_enabled`
  - `action_judge_enabled`
  - `report_polisher_enabled`: 기본 `true`. 계좌/워치리스트 리포트 상단에 투자자용 요약을 추가합니다.
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
  - 티커 표시 이름 오버라이드

실행 예시:

```powershell
.\.venv-codex\Scripts\Activate.ps1
python -m tradingagents.scheduled --config config/scheduled_analysis.toml
```

또는:

```powershell
tradingagents-scheduled --config config/scheduled_analysis.toml
```

생성 결과에는 `run.json`, 티커별 `analysis.json`, `final_state.json`, markdown 리포트, `quality_flags`, `batch_metrics`, `warnings`가 포함됩니다.

## 로컬 번역 백엔드

최신 `main` 기준 스케줄 리포트의 기본 로컬 번역 경로는 `nllb_ct2`입니다.

- 기본 추천: `translation.backend = "nllb_ct2"`
- 기본 모델: `translation.model = "nllb-200-distilled-600m"`
- 대형 대안: `translation.backend = "madlad_ct2"`, `translation.model = "madlad-400-3b"`
- `madlad_ct2`는 `allow_large_model = true`가 아니면 막혀 있습니다.
- 이미 한국어처럼 보이는 텍스트는 skip합니다.
- 실제 리포트에 렌더링되는 12개 필드만 번역합니다.

GitHub Actions self-hosted runner에서 로컬 번역을 쓰려면 repository variables 예시는 다음과 같습니다.

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

대안:

```powershell
python -m cli.main
```

## 기여

버그 수정, 문서 개선, 기능 제안 등 모든 형태의 기여를 환영합니다.

## 인용

논문/인용 정보는 [README.en.md](README.en.md)의 Citation 섹션을 참고해 주세요.
