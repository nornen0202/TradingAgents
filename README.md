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
- 선택형 PRISM 외부 신호 수집, PRISM-style 후보 스캐너, 추천 액션 성과 추적

이 프로젝트는 연구 목적입니다. 실제 투자 판단이나 자문 용도로 사용하면 안 되며, 결과는 모델, 데이터, 프롬프트, 시장 상황에 따라 크게 달라질 수 있습니다.

## PRISM 외부 신호와 운영 보강

TradingAgents는 PRISM 데이터를 외부 참고 신호로만 사용합니다. PRISM `BUY`가 있더라도 TradingAgents의 리스크 액션, 계좌 제약, 포트폴리오 배분, 실행 승인 레이어를 우회하지 않습니다.

```toml
[external.prism]
enabled = true
mode = "advisory"
local_dashboard_json_path = "C:/Projects/prism-insight/examples/dashboard/public/dashboard_data.json"
use_live_http = false
use_html_scraping = false
confidence_cap = 0.25

[scanner]
enabled = true
market = "KR"
max_candidates = 10
include_prism_candidates = true

[performance]
enabled = true
store_path = "archive/performance.sqlite"
update_outcomes_on_run = true
price_provider = "local_json"
price_history_path = "C:/TradingAgentsData/price_history.json"
benchmark_ticker = "SPY"
```

자세한 설정과 충돌 정책은 [Docs/prism_external_signals.md](Docs/prism_external_signals.md), 스캐너는 [Docs/scanner_prism_style.md](Docs/scanner_prism_style.md), 추천 성과 추적은 [Docs/action_performance_tracker.md](Docs/action_performance_tracker.md)를 참고하세요. 모든 기능은 기본 비활성화이며, 기존 scheduled report는 PRISM 없이 그대로 동작합니다. Live HTTP와 dashboard HTML embedded JSON 파싱은 각각 명시적으로 켜야 하며, outcome 업데이트도 가격 히스토리 파일 또는 opt-in provider가 있어야 계산됩니다.

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
  - `run_mode`: `full | overlay_only | selective_rerun_only`
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

- `[execution]` (장중 deterministic overlay)
  - `enabled`: `true`면 종목 리서치 후 `execution_contract.json` 생성 + 장중 overlay refresh 수행
  - `checkpoints_kst`: 예) `["23:35"]` (API 호출 절약을 위해 1회 체크포인트 권장)
  - `max_data_age_seconds`: stale data fail-closed 기준
  - `publish_badges`: 사이트 배지/상태 노출
  - `selective_rerun_enabled`: 이벤트/무효화 기반 selective rerun
  - `llm_summary_model`: execution markdown 설명 모델 (기본 `gpt-5.4-mini`)

### 장중 하이브리드 구조(Research + Deterministic Overlay + Selective Rerun)

현재 스케줄 러너는 다음 순서로 동작합니다.

1. **기존 종목 리서치 유지**: 기존 multi-agent 분석 파이프라인 실행
2. **Execution contract 생성**: 리서치 결과에서 `execution_contract.json` 생성
3. **Deterministic overlay refresh**: intraday snapshot + contract로 `execution_update.json` 갱신
4. **예외적 selective rerun**: 이벤트 신호/무효화 종목만 재분석 후 overlay 재평가

즉 “전체 종목 full rerun 반복”이 아니라, **기본은 경량 overlay**, 예외만 rerun하는 하이브리드 구조입니다.

### run_mode 운영 권장 (실무)

- `full`:
  - 종목 full research + overlay + (옵션) selective rerun 실행
  - 보통 하루 1회 기준 리포트 생성용
- `overlay_only`:
  - 최신 full run 산출물을 재사용하고 full research는 건너뜀
  - overlay만 갱신해서 최신 시세 반영
  - selective rerun은 **후보(`selective_rerun_targets`)만 생성**
- `selective_rerun_only`:
  - 운영자가 판단해 수동 트리거할 때 사용
  - 후보 종목만 selective rerun 실제 실행 후 overlay 재평가

권장 패턴:
1) 하루 1회 `full`  
2) 2시간 단위 `overlay_only`  
3) 필요 시 수동 `selective_rerun_only`

참고: 저장소에는 2시간 단위 overlay 전용 워크플로우(.github/workflows/intraday-overlay-refresh.yml)가 포함되어 있으며, `profile` 입력으로 `us/kr/all`을 선택해 미국장·한국장을 분리/동시 운영할 수 있습니다.

### checkpoints_kst 동작 방식 (중요)

`checkpoints_kst`는 백그라운드 스케줄러가 아닙니다. 프로세스가 해당 시각까지 대기했다가 자동 실행하지 않습니다.

- 러너는 **실행 시점의 KST 현재시간**을 기준으로,
- `현재시간 >= checkpoint` 인 항목 중 **가장 늦은 1개만** 그 실행에서 수행합니다.

예시:

- `checkpoints_kst = ["22:35", "22:50", "23:30"]`일 때
  - 22:40 KST에 한 번 실행 -> `22:35`만 수행
  - 22:55 KST에 한 번 실행 -> `22:50`만 수행
  - 23:35 KST에 한 번 실행 -> `23:30`만 수행
- `checkpoints_kst = ["23:35"]`일 때
  - 23:35 KST에 한 번 실행 -> `23:35`만 수행

따라서 “각 checkpoint를 실제 시각별로 따로 실행”하려면 GitHub Actions를 checkpoint 시각별로 분리 스케줄하거나, workflow_dispatch를 해당 시각에 수동 실행해야 합니다.

### GitHub Actions에서 실질 검증하는 방법

권장 검증 순서:

1. `Actions > Daily Codex Analysis > Run workflow`
   - `profile = us`
   - `tickers = TSM,NVDA` (작은 배치 권장)
   - `site_only = false`
2. 실행 후 archive의 최신 run 폴더에서 아래 파일 확인
   - 종목별:
     - `tickers/<TICKER>/execution_contract.json`
     - `tickers/<TICKER>/execution_update.json`
     - `tickers/<TICKER>/execution/checkpoints/execution_update_<checkpoint>.json`
     - `tickers/<TICKER>/execution_update.md`
   - 런 단위:
     - `execution_summary.json`, `execution_summary.md`
     - `run.json`의 `event_signals`, `selective_rerun_targets`, `selective_rerun_results`
3. 생성된 site에서 아래 UI 확인
   - `Execution As-Of`, `Decision State`, `Staleness`
   - Portfolio 페이지의 `Execution overlay` 섹션

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
