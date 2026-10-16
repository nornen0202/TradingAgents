# TradingAgents 통합 검토·시점 일치 검증 구현

2026-10-17 KST. 사용자 제공 ChatGPT 조사 본문과 추가 Gemini 검토를 현재 코드와 대조했다. 별도 ‘개인 투자 Workbench’ 저장소·제품은 만들지 않았다. 기존 분석·실행 판단·PRISM·SQLite 모의매매·추천 사후평가·계좌 원장을 재사용한다. 제공된 sandbox HTML 원본은 이 작업에 첨부되지 않아 그 파일 자체의 내용까지 확인한 것으로 간주하지 않는다.

## 검토 결과와 채택 범위

| 제안 | 적용 및 보완 |
|---|---|
| 기존 엔진 재사용 | 차트는 기존 실행 판단·차단 이유를 읽는다. 브라우저에 매수 가능 여부를 계산하는 규칙이 없다. |
| 장중 신선도 10분 | 정확히 600초부터 만료. 재발행·캐시 복사·보고서 생성으로 원자료 시각을 갱신하지 않는다. |
| Gemini 세션 인식 | 정규장 밖에서는 최신 정규장 종가를 거래소 달력으로 확인해 리서치 유효성을 별도로 표시한다. 계좌·장중 실행의 10분 제한을 완화하지 않는다. |
| Gemini 세 시각 | `event_time`, `ingested_at`, `evaluated_at`을 구분한다. 자료별 원래 시각명과 대응 관계를 보존한다. |
| Gemini 예시 `age <= 600` | ‘10분 미만’과 충돌하므로 `< 600`으로 수정했다. 장전·장후 15분 시세를 신규 진입 허가로 쓰지 않는다. |
| Gemini DART 폴백 | 최초 감지를 SQLite에 보존하되 실제 발표 시각으로 표시하지 않는다. 감지 이전 replay에서는 보이지 않으며, 감지 이후 보수적 신규 진입 보류에만 사용한다. |
| 차트와 replay 동시 구현 | `get_replay_snapshot(ticker, as_of_ts, ...)`가 공통 JSON을 공급한다. 가격·판단·계획·이벤트·체결·회고를 같은 시점으로 조회한다. |
| FastAPI 제안 | 기존 Python 패키지 안의 localhost 읽기전용 어댑터로 구현했다. 별도 서버 프레임워크 의존성·별도 프로젝트는 추가하지 않았다. |
| Lightweight Charts | 5.2.0 standalone 배포본 고정. npm SHA-512 검증 및 파일 SHA-256 목록, Apache LICENSE/NOTICE, 내장 fancy-canvas MIT 고지를 보존한다. SVG 정적 보고서도 제공한다. |
| P3 수급 지표 | Anchored VWAP과 Volume Profile을 결정론적으로 구현하되 봉 기반 근사라는 점과 해상도를 표시한다. Footprint·DOM을 OHLCV에서 추정하지 않는다. |

외부 제품의 요금·기능·라이선스는 개발 요구사항과 분리했다. 다음 핵심 사항은 공식 자료로 재확인했다.

- [TradingView MCP](https://www.tradingview.com/support/solutions/43000795699-mcp-server-connect-your-ai-assistant-to-tradingview/): 개인 대화형 베타, 구독 여부와 무관한 지연 데이터, 무인 수집·자동 의사결정 투입 제한. 자동 수집원으로 추가하지 않았다.
- [TradingView 데이터 범위](https://www.tradingview.com/data-coverage/): KRX 무료 주식 시세 20분 지연. 10분 미만 실행 요건의 대체 공급원으로 사용하지 않는다.
- [Lightweight Charts 문서](https://tradingview.github.io/lightweight-charts/docs): 차트 라이브러리와 데이터 이용권은 별개이며 표시·고지 조건을 보존한다.
- [Finviz 공식 API 안내](https://finviz.com/blog/our-upgraded-api-higher-limits-clearer-data-and-more-ways-to-connect/): API·내보내기 제공은 확인되지만 이번 구현에 유료 구독이나 연동을 추가하지 않았다.
- [OpenBB V5 라이선스](https://docs.openbb.co/odp/python/faqs/license): Apache-2.0 전환과 데이터 공급자 권한의 별도 적용을 확인했다. V4 예제·AGPL 조건을 혼용하지 않았다.
- [vectorbt 라이선스](https://github.com/polakowo/vectorbt/blob/master/LICENSE.md): Commons Clause가 포함된다. 기존 백테스트 엔진을 재사용해 새 의존성을 추가하지 않았다.
- [Koyfin 공식 FAQ](https://www.koyfin.com/help/faq/can-i-get-the-data-via-api/): 고객 데이터 API 미제공 안내. 자동 연동원으로 가정하지 않았다.

REA/X 사례는 비공개 지표·유료 데이터·전략 수치 동등성을 입증하는 구현 근거로 사용하지 않았다. Finviz, Koyfin, TrendSpider, FnGuide, OpenBB, FinanceToolkit, LEAN, vectorbt, Qlib, Portfolio Performance, Ghostfolio는 비교·장래 선택지이며, 이번 우선순위 기능을 구현하기 위해 모두 설치하거나 새 엔진을 중복 도입할 이유는 없었다.

## 우선순위별 구현과 검증

| 우선순위 | 구현 | 주요 검증 |
|---|---|---|
| P0 공통 정책 | `dataflows/market_policy.py`; Work freshness/packet/runtime/pre-report/public-delivery 및 실행 overlay의 공통 제한 | 9:59 통과, 10:00 차단, 미래·결측·naive 시각 차단, 휴일·조기마감·최신 종가 리서치, 공급자 이용정책 |
| P1 이벤트 | `event_timeline.py`, SEC/DART 기존 수집 경계 캡처, 최초 감지 DB, EventGuard 확장 | 정정 버전 계보·충돌·미래 공개·누락 발표 시각, 미국 발표 전후·한국 장중 감지 쿨다운, 위험 축소 매도 우선 |
| P1 추적·replay | `performance/lifecycle.py`, `replay.py`, 추천/모의/실제 영수증/거래일지 연결 | 불변·중복 방지, 부분 체결·현금·통화·비용, 수집·확정·정산 후에만 가시성, 실제 영수증의 수량·부모 의도 일치 |
| P1 차트·근거 | `charting/*`, 기존 scheduled runner와 종목 보고서 연결, 공통 snapshot/로컬 뷰어 | 과거 시점의 미래 봉·판단·정정·사실 제거, XSS 방어, HTTP 읽기전용, 공개 재배포·개인 체결 경계 |
| P2 전략 실험 | `execution/experiments.py` 등록·동결·미래 의사결정·관측·보고 및 시간순 검증 | 동결 이후 수정 불가, 장 시작 전 타깃 고정, 공동 자본·비용·종목군·benchmark, 누락 세션 건너뛰기 금지, 모든 prefix 비교 |
| P2 스캐너 편집 | `scanner/conditions.py`, `condition_editor.py`, scheduled TOML 연동 | `all/any/not`, 허용 필드·연산·타입·깊이, NaN·unknown 전파, 날짜 없는 후보와 미래 PRISM 점수 제외 |
| P3 수급 맥락 | `charting/indicators.py` | AVWAP 수치 검산, 거래량 보존, 빈 입력·0 거래량·평탄 가격·세션·혼합 해상도·미래 봉 검증 |

주요 회귀 파일: `tests/test_market_policy_events.py`, `tests/portfolio/test_lifecycle_replay.py`, `tests/test_integrated_chart_review.py`, `tests/test_chart_review_regressions.py`, `tests/execution/test_experiments.py`, `tests/scanner/test_conditions.py`. 브라우저 검증은 `.github/scripts/investment_review_regression.py`이며 기존 모바일·전략 상호작용·보고서 읽기 회귀도 유지한다. CI에서 전체 Python 테스트, 정적 검사, 네 가지 브라우저 회귀를 수행한다.

## 데이터와 시각 계약

| 자료 | 사건 시각 | 실제 수집 | 판단·가용성 |
|---|---|---|---|
| 캔들 | `timestamp` / `event_time` | `observed_at` / `ingested_at` | `available_at`(봉 완료)와 `evaluated_at`(조회) |
| 공시 | `published_at`(확인 가능할 때만) | `observed_at`, DART `first_seen_at` | `known_at`, 스냅샷 `analysis_as_of` |
| 판단 | `execution_asof` | `ingested_at` | `evaluated_at`; 계획은 원 분석 완료 이후만 |
| 체결·회고 | `occurred_at` / `event_time` | `ingested_at` | `available_at`, `confirmed_at`, `settled_at`, replay `evaluated_at` |

수집 기록이 없는 기존 가격·체결을 임의의 과거 시각으로 채우지 않는다. 실제 체결 영수증의 수집 시각은 import 시각이며 `--as-of`로 이를 과거로 바꿀 수 없다. 미래 회고와 나중 정산된 성과는 과거 조회의 목록·합계·연결 상태에 영향을 주지 않는다. 계좌 초기 잔고·보유가 없으면 이를 0으로 만들지 않고 unknown으로 표시한다. 특정 종목으로 필터링한 조회에서는 다른 거래가 빠지므로 계좌 현금 합계를 제공하지 않는다.

일봉 캡처는 이미 분석에 사용한 `load_ohlcv` 결과를 재사용하며, 거래소 달력의 실제 세션 종료 이후 완료된 봉만 보존한다. KIS 분봉은 명시적 영업일·시각과 구간 거래량이 있는 완료 1분봉만 보존한다. 요청한 `5m` 문구를 근거로 1분 원자료를 5분봉으로 재명명하지 않는다. 일봉/분봉을 한 AVWAP·Profile 입력으로 합쳐 거래량을 중복 합산하지 않는다.

정정 공시는 `event_id`, `version_id`, `supersedes_version_id`로 연결한다. DART 날짜만 있는 접수는 `published_at=None`, `exact_event_time_known=False`, `status=detected`로 보존한다. 확인 사실 패널에는 발표·수집·확인 시각이 모두 검증된 항목만 들어가며, 그 외 자료는 미검증 수에 포함한다. SEC 시각은 공급자 값의 시간대/offset을 파싱하며 무조건 미국 동부시각으로 덮어쓰지 않는다.

## 기존 보고서에서 사용

새 분석은 종목 디렉터리에 `chart_evidence.json`, `event_timeline.json`, `investment_review.html`을 보존한다. 장중 갱신은 최신 실행 판단과 기존 일봉/새 분봉을 함께 읽어 로컬 보고서를 다시 만든다. 뷰 생성 실패는 품질 플래그로 남기며 성공한 기업 분석 자체를 실패로 바꾸지 않는다.

기존 run 폴더를 대상으로 실행한다.

```powershell
python tools/serve_investment_review.py <기존-run-폴더> --tracker-db <추천.sqlite> --tracker-db <모의계좌.sqlite>
```

브라우저에서 `http://127.0.0.1:8765`를 열면 후보·차트·근거·성과를 함께 볼 수 있다. 종목과 시간대가 포함된 ISO 기준 시각을 바꾸면 동일한 서버 스냅샷을 다시 조회한다. AVWAP 시작 시각도 지정할 수 있다. localhost GET 조회만 제공하며 자료 갱신·주문·계좌 변경 API는 없다.

정적인 시점 검토 파일은 다음과 같이 만든다.

```powershell
python tools/render_investment_review.py <run>/tickers/<ticker> --as-of 2026-10-16T10:00:00+09:00 --tracker-db <추천.sqlite>
```

같은 디렉터리의 HTML·JSON을 생성한다. 더 이른 시점에 수집한 적 없는 자료는 빈 상태로 나오는 것이 정상이다. 오래된 아카이브에 없던 과거 봉이나 수집 시각을 새로 만들어 채우지 않는다.

공개 Pages는 기존 공개 종목 경계를 유지한다. 차트 캡처 기본값은 `public_display_allowed=False`다. 이 플래그는 공개 시계열 재배포 권한을 검증한 자료에만 명시적으로 설정한다. 브라우저 localhost 화면·개인 체결·거래일지·계좌 합계를 공개 Pages로 복사하지 않는다.

## 스캐너 조건 편집

```powershell
python -m tradingagents.scanner.condition_editor create --output rules.json --rule volume_ratio gte 1.5 --rule trading_value gte 10000000000
python -m tradingagents.scanner.condition_editor validate rules.json
python -m tradingagents.scanner.condition_editor scan --condition rules.json --ohlcv dated_snapshot.json --as-of 2026-10-16T15:30:00+09:00 --market KR --output candidates.json
```

scheduled TOML의 기존 `[scanner]`에 직접 설정할 수도 있다.

```toml
[scanner]
enabled = true
condition = { all = [{ field = "volume_ratio", op = "gte", value = 1.5 }, { field = "trading_value", op = "gte", value = 10000000000 }] }
```

조건은 조사 후보를 줄이는 도구다. 실행 허가를 만들지 않는다. 날짜를 확인할 수 없는 기존 스캐너 스냅샷은 후보에서 제외되므로 공급 파일에 실제 관측 시각을 제공해야 한다.

## 전략 실험과 실제 검증의 구분

실제 체결은 로컬 증권사 영수증 JSON을 명시적으로 가져온다. 배치 전체를 먼저 검증한 뒤 한 트랜잭션으로 기록한다.

```powershell
python -m tools.import_execution_receipts --db <추적.sqlite> --input receipts.json --as-of <시간대-포함-기준시각>
```

입력은 `{ "entries": [{ "recommendation": {...}, "receipt": {...} }] }`다. 추천에는 `run_id, ticker, action, created_at`이 필요하다. 영수증에는 `status, source, intent_id, fill_id, intent_at, executed_at, confirmed_at, settled_at, side, requested_quantity, filled_quantity, fill_price, cost, currency`를 명시한다. `fill_id`는 누적 체결량이 아니라 개별 추가 체결을 식별해야 한다. 미확인 비용·의도·정산 시각을 임의로 채우지 않는다. 이 경로는 영수증 기록만 수행하고 주문을 보내지 않는다.

```powershell
python -m tradingagents.execution.experiments --registry experiments.sqlite register --input experiment.json
python -m tradingagents.execution.experiments --registry experiments.sqlite freeze --id sample-20261019
python -m tradingagents.execution.experiments --registry experiments.sqlite decision --id sample-20261019 --input next-session-decision.json
python -m tradingagents.execution.experiments --registry experiments.sqlite session --id sample-20261019 --input completed-session.json
python -m tradingagents.execution.experiments --registry experiments.sqlite report --id sample-20261019 --as-of <시간대-포함-기준시각>
```

등록 예시(운영 실험을 이 문서만으로 자동 시작하지 않는다):

```json
{
  "id": "sample-20261019",
  "hypothesis": "고정 규칙 대비 AI 보강의 비용 차감 성과와 거래 횟수를 비교한다",
  "universe": ["005930.KS"],
  "capital": 1000000,
  "currency": "KRW",
  "costs": {"fee_bps": 10, "slippage_bps": 10},
  "benchmark": "KOSPI",
  "baseline_rules": {"strategy": "existing-rule-v1", "version": "고정 버전"},
  "ai_rules": {"strategy": "existing-rule-plus-ai-v1", "prompt_version": "고정 버전"},
  "training_end": "2026-10-16T15:30:00+09:00",
  "forward_start": "2026-10-19T09:00:00+09:00",
  "forward_end": "2026-12-14T15:30:00+09:00"
}
```

동결과 실제 기록 시각은 앞으로의 실험 시작보다 앞서야 한다. 결정은 `session_id, open_at, data_as_of, dataset_version, baseline_weights, ai_weights, model_cost, validation_seconds`를 포함하고 장 시작 전에 기록한다. 완료 관측은 `session_id, close_at, available_at, opens, closes, benchmark_open, benchmark_close`를 포함한다. 종목군·자본·각 방향 수수료·슬리피지를 동일하게 적용한다. 결과는 순수익률·최대낙폭·회전율·거래 횟수·비용·검증 시간·모델 비용을 분리한다.

레지스트리는 규칙 명세와 결정의 변조·시점·비교 조건을 검사한다. 자연어 규칙의 준수 여부를 스스로 증명하거나 임의의 규칙 설명을 실행하는 엔진은 아니다. `validate_chronological_research`는 기존 next-open 백테스터를 이용한 모든 prefix 및 시간순 holdout 검증을 제공하지만 모델 학습 데이터 독립성과 역사적 공시 시각을 증명하지는 않는다. 미래 모의 실험은 별도 레지스트리에 기록해 기존 운영 모의 계좌와 자본을 섞지 않는다.

4~8주 이상의 실제 미래 관측 축적과 수익성 판단은 개발 시점에 완료할 수 없다. 테스트의 시뮬레이션 시계를 실제 미래 실적으로 제시하지 않는다. 신규 데이터 구독·실주문·실계좌 변경·자동 전략 승격은 이 작업으로 활성화하지 않았다.

## 운영·품질 경계

원자료가 비어 있거나 날짜가 없으면 차트·이벤트·스캐너는 빈 상태와 사유를 반환한다. 공급자 날짜 요청 인자만 믿거나 최신 재무 스냅샷에 임의 공시 지연을 붙이지 않는다. 새로운 LLM 클라이언트나 공급자 SDK 직접 초기화도 추가하지 않았다. 실행 판단은 정형 스키마와 기존 엔진에 남으며, 이벤트 신규 진입 제한이 결정론적인 위험 축소 매도를 막지 않는다.

마지막 검증 수치·커밋·PR은 병합 시점 결과를 기준으로 기록한다. 합성 fixture는 정상/빈/미래/누락/잘못된 시각·경계·정정·비용·리스크를 재현하며 실제 운영 성과로 간주하지 않는다.
