# Decision Bundle v2

`decision_bundle_v2.json`은 TradingAgents 리서치와 장중 실행 데이터를 ChatGPT 및
GitHub Pages에 전달하는 단일 투자 판단 계약입니다. 내부 기계 코드는 유지하지만,
사용자 화면과 ChatGPT 답변에는 직관적인 한국어 전략명을 우선 표시합니다.

## 핵심 산출물

- `execution/decision_bundle_v2.json`: 종목별 현재가, 기준시각, VWAP, RVOL,
  거래량·거래대금, 스프레드, 섹터·지수 동조, 진입 조건과 무효화 조건
- `execution/strategy_table_ko.md`: 보유 종목 전체와 우선 신규 후보를 행동 순서로
  정렬한 한국어 투자 전략표
- `execution/decision_bundle_status.json`: 준비도, 신선도 비율, 파일 SHA-256
- `portfolio/prism_current_signals.json`: 시장과 시각을 검증한 최근 PRISM 신호만
  남긴 현재 신호 집합

## 준비도 기준

`quality.decision_ready=true`는 현재 실행 컨텍스트이면서 데이터가 신선하고,
실행 가능 종목 비율이 80% 이상일 때만 설정됩니다. 이전 세션 자료, 백필 자료,
핵심 시세 필드가 빠진 자료는 리서치에는 사용할 수 있지만 즉시 매수·매도 판단으로
승격할 수 없습니다.

추가로 모든 보유 종목 행이 실행 가능해야 합니다. 신규 후보가 많아 80%를 넘더라도
stale 보유 행이 하나라도 있으면 portfolio-wide `decision_ready`는 false입니다.
일부 행만 유효하면 `quality.report_mode=MIXED`로 게시하며, 행별 `row_mode`는
`IMMEDIATE`, `CONDITIONAL`, `BLOCKED_STALE`, `MISSING` 중 하나입니다.

`IMMEDIATE`는 `current_execution_promotion=POSSIBLE`이고 provider 상태 재확인
blocker가 없을 때만 허용됩니다. stale BUY/SELL/REDUCE 의도는 즉시 행동으로
표시하지 않습니다.

`quality.conditional_strategy_ready=true`는 현재 세션의 현재가·VWAP·상대 거래량과
기준시각은 충족하지만 일부 호가·수급·시장 상태가 지연 또는 제한된 경우입니다.
이 계층은 실제 값을 이용한 보유·축소·종가 확인·조건부 매수 전략을 제공하지만,
즉시 주문 승격은 금지하고 주문 전 실시간 호가와 거래 상태 재확인을 요구합니다.

## 안정 URL

- `/latest/us/status.json`, `/latest/kr/status.json`: 가장 최근 run의 준비도
- `/latest/{market}/decision_bundle.json`: 마지막으로 준비도 검증을 통과한 bundle
- `/latest/{market}/strategy_table_ko.md`: 해당 bundle의 한국어 전략표
- `/latest/{market}/source.json`: 안정 URL이 가리키는 원본 run

새 run이 실패하거나 준비되지 않았더라도 마지막 정상 bundle의 안정 URL은 유지됩니다.
최신 상태와 마지막 정상 투자 판단을 혼동하지 않도록 `status.json`과 `source.json`을
함께 확인해야 합니다.

## ChatGPT 전송

`.github/scripts/build_chatgpt_context_pack.py`가 시장별 프롬프트와 bundle을 하나의
payload로 결합합니다. 산출된 `TRANSMISSION_KEY`를 자동화 상태에 기록해 같은 run과
내용을 중복 전송하지 않습니다. 준비되지 않은 main은 연구 전용, 준비되지 않은
overlay는 데이터 장애 모드로 전송합니다.

현재 key는 source hash뿐 아니라 prompt SHA-256과 contract version을 포함합니다.
일부 행만 실행/조건부인 overlay는 전체 장애로 숨기지 않고 `MIXED`로 전송합니다.

ChatGPT 사용자용 분류는 다음 한국어 표현을 사용합니다.

- 지금 분할매수 검토
- 조건 확인 후 분할매수 검토
- 보유 유지
- 비중 축소 검토
- 매도·청산 검토
- 조건 충족 전 대기
- 신규 매수 회피
- 데이터 확인 전 대기
- 종가 확인 후 판단

YouTube는 당일 Context Pack을 우선하며, 결측 시 직전 KST 날짜 자료 하나만 오래된
보조 맥락으로 허용합니다. 전일 자료는 테마·위험·검증 우선순위에는 쓸 수 있지만
현재 실행 판단을 상향하는 근거로 사용할 수 없습니다.
