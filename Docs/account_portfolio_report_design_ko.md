# TradingAgents 계좌 운용 리포트 설계안

작성 기준:

- 저장소 기준 시점: `2026-04-10`
- 검토 기준 코드
  - `tradingagents/schemas/decision.py`
  - `tradingagents/graph/setup.py`
  - `tradingagents/agents/managers/portfolio_manager.py`
  - `tradingagents/scheduled/runner.py`
  - `tradingagents/scheduled/site.py`
  - `tradingagents/agents/utils/instrument_resolver.py`
- 참고 아키텍처 문서
  - `quant-trading-rest/docs/architecture/trading-architecture.md`
- 검토 기준 런
  - `2026-04-08 KR run`

## 1. 결론

현재 TradingAgents는 이미 다음을 잘하고 있다.

- `quick / deep / output` 모델 분리
- 종목별 analyst -> researcher -> trader -> risk debate -> portfolio manager 흐름
- 구조화된 최종 의사결정 JSON
- `quality_flags`, `batch_metrics`, `warnings`
- KR 벤더 우선순위와 fallback
- 종목별 정적 사이트 리포트

따라서 필요한 것은 "새 투자 엔진"이 아니라, **현재 티커 단위 런타임 위에 계좌 계층을 얹는 것**이다.

이 문서의 핵심 결론은 세 가지다.

1. 계좌 계층은 `LangGraph` 내부가 아니라 **그래프 밖의 후처리 파이프라인**으로 둔다.
2. 최신 `main`이 자주 내는 `BULLISH + WAIT`는 즉시 매수 신호가 아니라 **조건부 배치 후보**로 해석한다.
3. 배분 엔진은 `structured decision`만 보지 않고 `data_coverage`, `quality_flags`, `vendor_health`, `snapshot_id`를 1급 입력으로 사용한다.

## 2. 현재 main 위에 얹는 문제 정의

### 2.1 현재 main이 이미 하는 일

현재 저장소는 개별 종목에 대해 아래까지 구현되어 있다.

- 시장/심리/뉴스/펀더멘털 분석
- bull / bear 리서처 토론
- research manager 판정
- trader 실행안
- aggressive / neutral / conservative 리스크 토론
- portfolio manager 최종 JSON 판정
- `run.json`, `analysis.json`, `final_state.json`, Markdown 리포트, 정적 사이트 생성

즉, 종목별 판단 품질은 이미 충분히 높다.

### 2.2 현재 main이 하지 않는 일

아직 없는 것은 계좌 레벨의 오케스트레이션이다.

- 실제 보유 종목/현금/미체결 주문을 입력으로 받지 않는다.
- 여러 종목 신호를 비교해 계좌 전체 우선순위를 정하지 않는다.
- "오늘 얼마를 사고/팔고/유지할지"를 계좌 제약과 함께 계산하지 않는다.
- 공개 사이트는 종목별 `Decision / Portfolio stance / Entry action / Setup quality / Tool calls / Token usage / Quality flags`까지만 보여준다.

즉, 지금의 `Portfolio Manager`는 이름과 달리 **단일 종목의 최종 판정자**이지, 계좌 전체 배분기가 아니다.

## 3. 최신 main이 주는 중요한 현실: `BULLISH + WAIT`

`2026-04-08` KR 런은 12개 종목 모두 성공했고, 다수 종목이 아래 조합으로 나왔다.

- `NO_TRADE / BULLISH / WAIT`
- `HOLD / BULLISH / WAIT`

이는 우연이 아니라 현재 프롬프트 설계의 의도와 맞는다.

- `research_manager.py`
  - 증거는 긍정적이지만 셋업이 미완성이면 `portfolio_stance=BULLISH`와 `entry_action=WAIT`를 선호
- `portfolio_manager.py`
  - thesis는 건설적이지만 timing이 미완성이면 `entry_action=WAIT`
  - `NO_TRADE`는 legacy rating일 뿐이며 bullish stance와 공존 가능
- `runner.py`
  - `NO_TRADE` 집중과 `BULLISH / WAIT` 공존을 별도 경고 대상으로 취급

따라서 계좌 엔진은 이 조합을 아래처럼 해석해야 한다.

- `즉시 매수 후보`가 아니다
- `조건부 후보`다
- 리포트는 `now`와 `if_triggered`를 분리해야 한다

이 설계 원칙이 빠지면 최신 main의 출력과 계좌 리포트가 충돌한다.

## 4. 설계 원칙

### 4.1 현재 티커 런타임을 재사용한다

새 계층은 기존 티커 분석을 대체하지 않는다.

- 기존 종목 분석 런타임은 그대로 둔다
- 계좌 계층은 그 결과를 소비하는 후처리 서비스다

### 4.2 계좌 정보는 LangGraph 안으로 넣지 않는다

`AgentState`와 analyst/researcher/trader/risk debate 프롬프트에 계좌 전체 정보를 넣지 않는다.

이유:

- 프롬프트가 불필요하게 무거워진다
- 민감한 계좌 정보가 모든 에이전트로 퍼진다
- 티커 단위 재사용성이 떨어진다

### 4.3 즉시 액션과 조건부 액션을 분리한다

모든 종목을 단일 `delta_krw`로 압축하지 않는다.

- `action_now`
- `delta_krw_now`
- `action_if_triggered`
- `delta_krw_if_triggered`
- `trigger_conditions`

를 분리한다.

### 4.4 데이터 헬스를 1급 입력으로 취급한다

계좌 리포트는 아래 정보를 반드시 함께 본다.

- `data_coverage`
- `quality_flags`
- `tool_telemetry.vendor_calls`
- `tool_telemetry.fallback_count`
- `batch_metrics.decision_distribution`
- `batch_metrics.stance_distribution`
- `batch_metrics.entry_action_distribution`
- `batch_metrics.avg_confidence`
- `batch_metrics.company_news_zero_ratio`
- `warnings`

### 4.5 브로커 세부는 상위 계층으로 새지 않게 한다

`quant-trading-rest`의 아키텍처 문서가 잘 짚듯이:

- 상위 계층은 브로커별 API 차이를 몰라야 한다
- 브로커 세션/응답 형식/에러는 `Broker Gateway`가 흡수해야 한다
- 설정, 판단, 실행, 상태를 분리해야 한다

### 4.6 런 단위 불변 스냅샷을 사용한다

한 번의 계좌 리포트 런에서는 아래가 고정되어야 한다.

- 계좌 현금
- 보유 종목
- 평균단가
- 주문 가능 수량
- 미체결 주문
- 사용자 제약 설정
- 분석 대상 종목군

중간 변경은 다음 런에서만 반영한다.

### 4.7 계좌 리포트는 기본적으로 비공개 산출물이다

공개 GitHub Pages에는 올리지 않는다.

- 공개: 종목별 분석 사이트
- 비공개: 계좌 스냅샷, 계좌 운용 리포트, 주문안

## 5. 목표 아키텍처

권장 파이프라인:

```text
1. Portfolio Config Service
2. Broker Gateway
3. Instrument Identity Service
4. Account Snapshot Service
5. Existing TradingAgents Ticker Runtime
6. Candidate Builder
7. Gate Engine
8. Allocation Engine
9. Recommendation State Store
10. Report Renderer
11. Optional Execution Planner
```

이 구조는 `quant-trading-rest`의 `Config / Gateway / Runtime / State` 경계를 TradingAgents 문맥에 맞게 재해석한 것이다.

## 6. 컴포넌트 역할

### 6.1 Portfolio Config Service

역할:

- 계좌 운용 프로필 로딩
- 감시종목, 현금 버퍼, 최대 회전율, 최대 섹터 비중 등 정책 검증
- 실행 모드 결정

입력 후보:

- `config/portfolio_profiles.toml`
- `config/account_targets.toml`

### 6.2 Broker Gateway

역할:

- 증권사 인증
- 계좌 목록 조회
- 현금/주문가능금액/미체결 주문/보유종목 조회
- 브로커별 응답 차이 정규화

MVP 우선순위:

1. `kis.py`
2. `csv_import.py`
3. `manual_snapshot.py`
4. `kiwoom.py`
5. `ls_sec.py`
6. `openbanking.py`는 후순위

### 6.3 Instrument Identity Service

역할:

- 브로커 심볼을 분석 런타임용 canonical ticker로 정규화
- `resolve_instrument()` 재사용
- `yahoo_symbol`, `krx_code`, `dart_corp_code`, `display_name` 보정

이 계층은 Broker Gateway와 기존 TradingAgents 런타임 사이에 반드시 있어야 한다.

### 6.4 Account Snapshot Service

역할:

- 브로커 raw 응답을 공통 `AccountSnapshot`으로 변환
- snapshot freeze
- raw / normalized 동시 저장

### 6.5 Existing TradingAgents Ticker Runtime

역할:

- 기존 종목 분석 실행
- `final_trade_decision`, `analysis.json`, `final_state.json` 생산

이 계층은 수정 최소화가 원칙이다.

### 6.6 Candidate Builder

역할:

- `StructuredDecision`와 `analysis.json`을 포트폴리오 후보로 변환
- legacy `rating`을 계좌 액션 문맥으로 번역
- `watchlist_triggers`, `catalysts`, `invalidators`를 `trigger_conditions` 후보로 정리
- `now`와 `triggered` 후보를 분리

### 6.7 Gate Engine

역할:

- 계좌 차원의 가드레일 적용
- 위험/데이터/현금 제약을 먼저 걸러냄

예:

- 최소 현금 버퍼
- 최대 단일 종목 비중
- 최대 섹터 비중
- 최대 일일 회전율
- 최소 주문 금액
- 최대 주문 건수
- 데이터 품질 하한

### 6.8 Allocation Engine

역할:

- 후보 점수화
- `now` 금액 배정
- `triggered` 금액 배정
- 보유 종목 / 비보유 종목 액션 변환

### 6.9 Recommendation State Store

역할:

- 입력, 중간 결과, 최종 결과를 저장
- 회귀 테스트와 사후 분석을 가능하게 함

### 6.10 Report Renderer

역할:

- 계좌 운용 JSON을 사람이 읽는 Markdown / HTML로 변환
- 데이터 헬스와 소스 헬스를 함께 표시

### 6.11 Optional Execution Planner

역할:

- 주문안을 생성하되 기본은 `read_only`
- `confirm_required` 모드에서만 주문 payload 생성
- `auto_execute`는 최후 단계

## 7. 핵심 스키마

### 7.1 InstrumentIdentity

```json
{
  "broker_symbol": "005930",
  "canonical_ticker": "005930.KS",
  "yahoo_symbol": "005930.KS",
  "krx_code": "005930",
  "dart_corp_code": null,
  "display_name": "삼성전자",
  "exchange": "KRX",
  "country": "KR",
  "currency": "KRW"
}
```

### 7.2 AccountSnapshot

```json
{
  "snapshot_id": "20260410T073000_kis_12345678-01",
  "as_of": "2026-04-10T07:30:00+09:00",
  "broker": "kis",
  "account_id": "12345678-01",
  "currency": "KRW",
  "settled_cash_krw": 3000000,
  "available_cash_krw": 2850000,
  "buying_power_krw": 2800000,
  "pending_orders": [
    {
      "broker_order_id": "A0001",
      "broker_symbol": "005930",
      "side": "buy",
      "qty": 5,
      "remaining_qty": 5,
      "status": "open"
    }
  ],
  "positions": [
    {
      "broker_symbol": "005930",
      "canonical_ticker": "005930.KS",
      "display_name": "삼성전자",
      "sector": "Semiconductors",
      "quantity": 14,
      "available_qty": 14,
      "avg_cost_krw": 71200,
      "market_price_krw": 73400,
      "market_value_krw": 1027600,
      "unrealized_pnl_krw": 30800
    }
  ],
  "constraints": {
    "min_cash_buffer_krw": 1000000,
    "min_trade_krw": 100000,
    "max_single_name_weight": 0.35,
    "max_sector_weight": 0.50,
    "max_daily_turnover_ratio": 0.30,
    "max_order_count_per_day": 5,
    "respect_existing_weights_softly": true
  }
}
```

### 7.3 PortfolioCandidate

```json
{
  "snapshot_id": "20260410T073000_kis_12345678-01",
  "canonical_ticker": "000660.KS",
  "display_name": "SK하이닉스",
  "is_held": true,
  "structured_decision": {
    "rating": "NO_TRADE",
    "portfolio_stance": "BULLISH",
    "entry_action": "WAIT",
    "setup_quality": "DEVELOPING",
    "confidence": 0.66
  },
  "trigger_signals": [
    "watchlist_triggers: breakout confirmation",
    "catalyst: earnings revision stabilization"
  ],
  "data_coverage": {
    "company_news_count": 8,
    "disclosures_count": 1,
    "social_source": "dedicated",
    "macro_items_count": 4
  },
  "quality_flags": ["token_usage_unavailable"],
  "vendor_health": {
    "vendor_calls": {
      "naver": 3,
      "opendart": 1,
      "yfinance": 2
    },
    "fallback_count": 1
  }
}
```

### 7.4 PortfolioAction

계좌 액션은 반드시 `즉시`와 `조건부`를 분리한다.

```json
{
  "canonical_ticker": "000660.KS",
  "display_name": "SK하이닉스",
  "priority": 1,
  "confidence": 0.66,
  "action_now": "HOLD",
  "delta_krw_now": 0,
  "target_weight_now": 0.29,
  "action_if_triggered": "ADD_IF_TRIGGERED",
  "delta_krw_if_triggered": 300000,
  "target_weight_if_triggered": 0.33,
  "trigger_conditions": [
    "중기 추세 회복 확인",
    "품질 플래그 악화 없음"
  ],
  "rationale": "방향성은 긍정적이지만 즉시 증액 근거보다 조건부 추가 근거가 더 강함",
  "data_health": {
    "coverage_score": 0.84,
    "fallback_count": 1,
    "quality_flags": ["token_usage_unavailable"]
  }
}
```

### 7.5 PortfolioRecommendation

```json
{
  "snapshot_id": "20260410T073000_kis_12345678-01",
  "report_date": "2026-04-10",
  "account_value_krw": 7000000,
  "recommended_cash_after_now_krw": 2500000,
  "recommended_cash_after_triggered_krw": 2000000,
  "market_regime": "constructive_but_selective",
  "actions": [],
  "portfolio_risks": [
    "반도체 편중",
    "구성적이지만 즉시 실행 가능한 후보가 적음"
  ],
  "data_health_summary": {
    "decision_distribution": {
      "NO_TRADE": 4,
      "HOLD": 8
    },
    "stance_distribution": {
      "BULLISH": 10,
      "NEUTRAL": 2
    },
    "entry_action_distribution": {
      "WAIT": 12
    },
    "avg_confidence": 0.63,
    "company_news_zero_ratio": 0.0,
    "warning_flags": [
      "token_usage_unavailable",
      "constructive_signals_concentrated_in_wait"
    ]
  }
}
```

## 8. Candidate Builder 설계

### 8.1 입력

Candidate Builder는 단순히 `final_trade_decision`만 읽지 않는다.

입력:

- `final_trade_decision`
- `analysis.json`
- `instrument_profile`
- `AccountSnapshot`

### 8.2 계좌 액션 번역 규칙

계좌 리포트에서는 `NO_TRADE`를 그대로 노출하지 않는다.

번역 원칙:

- 보유 종목 + `BULLISH + WAIT`
  - `action_now = HOLD`
  - `action_if_triggered = ADD_IF_TRIGGERED`
- 비보유 종목 + `BULLISH + WAIT`
  - `action_now = WATCH`
  - `action_if_triggered = STARTER_IF_TRIGGERED`
- 보유 종목 + `BEARISH + EXIT`
  - `action_now = REDUCE_NOW` 또는 `EXIT_NOW`
- 비보유 종목 + `BEARISH`
  - `action_now = WATCH`
  - `action_if_triggered = NONE`
- 보유 종목 + `NEUTRAL + WAIT`
  - `action_now = HOLD`
  - `action_if_triggered = NONE`

즉, 계좌 액션 레이어의 enum은 아래처럼 읽기 쉬운 형태가 좋다.

- `HOLD`
- `WATCH`
- `WATCH_TRIGGER`
- `STARTER_NOW`
- `ADD_NOW`
- `TRIM_NOW`
- `REDUCE_NOW`
- `EXIT_NOW`
- `STARTER_IF_TRIGGERED`
- `ADD_IF_TRIGGERED`
- `REDUCE_IF_TRIGGERED`
- `EXIT_IF_TRIGGERED`

## 9. Gate Engine 설계

Gate Engine은 Allocation Engine보다 먼저 돈다.

### 9.1 Account Gates

- 최소 현금 버퍼
- 최대 일일 회전율
- 최대 주문 건수
- 최소 주문 금액

### 9.2 Concentration Gates

- 최대 단일 종목 비중
- 최대 섹터 비중
- 동일 테마 중복 노출 제한

### 9.3 Data Gates

- `no_tool_calls_detected`가 있으면 신규 진입 금지
- `company_news_count = 0`이면 점수 감점 또는 즉시 액션 금지
- `fallback_count`가 과도하면 조건부 후보로만 남김
- `token_usage_unavailable`는 경고 플래그지만 단독으로 금지 사유는 아님

### 9.4 Snapshot / Batch Gates

- 하나의 리포트 런에서는 모든 후보의 `snapshot_id`가 동일해야 한다
- `entry_action_distribution.WAIT` 비중이 높고 `stance_distribution.BULLISH`도 높으면 신규 즉시 매수 한도를 자동 축소한다
- `decision_distribution.NO_TRADE` 집중은 단독으로 bearish로 해석하지 않고 `portfolio_stance`, `entry_action`과 함께 본다
- `warnings`에 데이터 결손 또는 벤더 이상 징후가 많으면 `triggered` 예산만 유지하고 `now` 예산을 줄인다

## 10. Allocation Engine 설계

### 10.1 핵심 원칙

배분 엔진은 종목별 `conviction`과 `immediacy`를 분리해서 다룬다.

```text
conviction = f(portfolio_stance, setup_quality, confidence)
immediacy = g(entry_action)
coverage = h(data_coverage, quality_flags, vendor_health)

score_now = conviction * immediacy * coverage
            - turnover_penalty
            - concentration_penalty

score_triggered = conviction * coverage
                  - concentration_penalty
```

### 10.2 immediacy 해석

권장 기본값:

- `ADD`: 높음
- `STARTER`: 중간 이상
- `WAIT`: 매우 낮음
- `NONE`: 0
- `EXIT`: 축소/청산 점수로 별도 처리

이렇게 하면 `BULLISH + WAIT`는:

- `score_now`는 낮고
- `score_triggered`는 높게

남는다.

### 10.3 coverage 해석

coverage는 아래를 함께 본다.

- `data_coverage.company_news_count`
- `data_coverage.disclosures_count`
- `data_coverage.social_source`
- `quality_flags`
- `tool_telemetry.vendor_calls`
- `tool_telemetry.fallback_count`
- `batch_metrics.entry_action_distribution`
- `batch_metrics.stance_distribution`
- `batch_metrics.avg_confidence`
- `warnings`

예시 패널티:

- `company_news_count = 0`
  - 감점
- `disclosures_count = 0`
  - KR 대형주면 소폭 감점
- `social_source = news_derived`
  - dedicated보다 감점
- `fallback_count >= 2`
  - 감점
- `no_tool_calls_detected`
  - 신규 매수 금지
- `WAIT` 집중 + `BULLISH` 집중
  - `investable_cash_now` 축소
  - `trigger_budget_krw` 확대

### 10.4 batch-aware allocation 해석

배분 엔진은 개별 종목 점수만 보지 않고, 이번 배치 전체가 어떤 성격인지도 함께 본다.

- `entry_action_distribution.WAIT / total`이 높으면
  - 시장은 우호적일 수 있어도 즉시 체결 타이밍은 부족하다고 해석
- `stance_distribution.BULLISH / total`이 높고 `decision_distribution.NO_TRADE / total`도 높으면
  - 약세장이 아니라 "구성적이지만 타이밍이 덜 열린 배치"로 해석
- `company_news_zero_ratio`가 높으면
  - 신규 진입 금액을 보수적으로 줄임

### 10.5 now / triggered 금액 배정

```text
investable_cash_now = available_cash_krw - min_cash_buffer_krw
positive_now = sum(max(score_now_i, 0))
positive_triggered = sum(max(score_triggered_i, 0))

delta_now_i =
  investable_cash_now * max(score_now_i, 0) / positive_now

delta_if_triggered_i =
  trigger_budget_krw * max(score_triggered_i, 0) / positive_triggered
```

이후 아래 제약을 적용한다.

- `min_trade_krw`
- `max_single_name_weight`
- `max_sector_weight`
- `max_order_count_per_day`
- `available_qty`

### 10.6 기존 비중을 너무 따지지 않는 방법

기존 비중은 하드 고정이 아니라 소프트 패널티로만 사용한다.

- 기존 보유라는 이유로 유지 강제 금지
- 하루 만에 완전 뒤집기 방지
- `turnover_penalty`로 급변만 억제

## 11. 리포트 형식

### 11.1 상단 요약

- 총 계좌 평가금액
- 현금 비중
- 오늘 바로 실행할 액션 수
- 조건 충족 시 실행 후보 수
- 시장 레짐

### 11.2 종목별 액션 테이블

| 종목 | 현재 평가금액 | 액션 now | 금액 now | 액션 if triggered | 금액 if triggered | 우선순위 | 근거 |
|---|---:|---|---:|---|---:|---:|---|
| 삼성전자 | 1,000,000 | HOLD | 0 | STARTER_IF_TRIGGERED | 200,000 | 2 | 방향성은 긍정적이나 즉시 진입 근거는 약함 |
| SK하이닉스 | 2,000,000 | HOLD | 0 | ADD_IF_TRIGGERED | 300,000 | 1 | BULLISH + WAIT, 조건부 추가 후보 |
| 에이피알 | 1,000,000 | HOLD | 0 | WATCH_TRIGGER | 0 | 3 | 변동성 확인 전 추가 자제 |

### 11.3 Data Health / Source Health

각 종목 옆에 최소한 아래 정보를 보여준다.

- `company_news_count`
- `disclosures_count`
- `social_source`
- `quality_flags`
- `vendor_calls`
- `fallback_count`

리포트 상단의 배치 건강도 요약에는 아래도 포함한다.

- `decision_distribution`
- `stance_distribution`
- `entry_action_distribution`
- `avg_confidence`
- `company_news_zero_ratio`
- `warnings`

이 섹션은 "이 제안을 얼마나 믿을 수 있는가"를 판단하는 데 필수다.

### 11.4 실행 구분

- `오늘 바로 실행`
- `조건 충족 시 실행`

### 11.5 공개 / 비공개 분리

- 공개 리포트
  - 기존 종목 사이트
- 비공개 리포트
  - 계좌 스냅샷
  - 계좌 액션 리포트
  - 주문안

## 12. 사용자 예시 계좌

입력 예시:

- 삼성전자 100만원
- SK하이닉스 200만원
- 에이피알 100만원
- 예수금 300만원

총 계좌는 700만원이다.

최신 KR 런의 현실을 반영하면, 이 계좌의 이상적 출력은 아래처럼 `now`와 `triggered`가 분리되어야 한다.

- 삼성전자
  - `action_now = HOLD`
  - `delta_krw_now = 0`
  - `action_if_triggered = STARTER_IF_TRIGGERED`
  - `delta_krw_if_triggered = 0 ~ 200,000`
- SK하이닉스
  - `action_now = HOLD`
  - `delta_krw_now = 0`
  - `action_if_triggered = ADD_IF_TRIGGERED`
  - `delta_krw_if_triggered = 300,000`
- 에이피알
  - `action_now = HOLD`
  - `delta_krw_now = 0`
  - `action_if_triggered = WATCH_TRIGGER`
  - `delta_krw_if_triggered = 0`
- 현금
  - `recommended_cash_after_now_krw >= 2,500,000`

중요한 점:

- `SK하이닉스 +300,000 KRW`를 즉시 실행안으로 쓰면 최신 main과 충돌한다
- 현재 구조에서 더 맞는 표현은 `HOLD now / ADD_IF_TRIGGERED +300,000 KRW`다

## 13. 파일 매핑

### 13.1 새 모듈

- `tradingagents/portfolio/account_models.py`
- `tradingagents/portfolio/instrument_identity.py`
- `tradingagents/portfolio/candidates.py`
- `tradingagents/portfolio/gates.py`
- `tradingagents/portfolio/allocation.py`
- `tradingagents/portfolio/state_store.py`
- `tradingagents/portfolio/reporting.py`
- `tradingagents/portfolio/csv_import.py`
- `tradingagents/portfolio/manual_snapshot.py`

### 13.2 유지 / 최소 수정 대상

- `tradingagents/graph/setup.py`
- `tradingagents/agents/*`

MVP에서는 계좌 상태를 `AgentState`에 넣지 않는다.
`tradingagents/agents/utils/agent_states.py` 수정은 후순위로 미루는 편이 맞다.

### 13.3 스케줄 실행 통합

- `tradingagents/scheduled/config.py`
  - `portfolio_profiles.toml` 로딩
- `tradingagents/scheduled/runner.py`
  - 기존 ticker run 이후 계좌 레이어 후처리
  - `portfolio_report.json`, `portfolio_candidates.json`, `decision_audit.json` 저장
- `tradingagents/scheduled/site.py`
  - 공개 사이트는 계속 ticker 중심
  - private account report는 별도 renderer 또는 artifact로 처리

### 13.4 평가

새 파일 권장:

- `tradingagents/eval/portfolio_walk_forward.py`

기존 `walk_forward.py`는 바로 덮어쓰지 않는다.

## 14. 산출물

최소 산출물:

- `account_snapshot.json`
- `portfolio_candidates.json`
- `portfolio_report.json`
- `proposed_orders.json`
- `decision_audit.json`

권장 추가 산출물:

- `portfolio_report.md`
- `broker_raw/balance.json`
- `broker_raw/positions.json`
- `broker_raw/buying_power.json`

## 15. 브로커 전략

### 15.1 MVP 우선순위

1. `KIS adapter`
2. `CSV import fallback`
3. `manual snapshot fallback`
4. `Kiwoom adapter`
5. `LS adapter`

이 순서가 현실적인 이유:

- 공식 API 온보딩이 부담스러운 사용자도 많다
- 계좌 리포트 MVP의 본질은 주문이 아니라 읽기 전용 분석이다
- 따라서 `KIS + CSV/manual_snapshot + read_only report`가 가장 실무적이다

### 15.2 유지할 원칙

- 공식 API 우선
- 스크래핑 비권장
- 자동주문은 후순위

## 16. 테스트와 감사 추적

### 16.1 테스트 전략

`quant-trading-rest`의 record/replay 전략을 채택한다.

권장 테스트:

- `test_broker_kis_normalization.py`
- `test_portfolio_snapshot_freeze.py`
- `test_portfolio_candidate_builder.py`
- `test_portfolio_gates.py`
- `test_portfolio_allocation.py`
- `test_portfolio_report_rendering.py`

### 16.2 Fixture 전략

- 실제 브로커 응답 일부를 비식별화해 JSON fixture 저장
- Fake adapter가 재생
- 동일 입력에서 동일 `portfolio_report.json`이 생성되는지 검증

### 16.3 감사 로그

`decision_audit.json`에는 아래를 남긴다.

- `snapshot_id`
- 계좌 총액
- `decision_distribution`
- `stance_distribution`
- `entry_action_distribution`
- 후보 종목별 원점수
- coverage penalty 근거
- gate 통과 여부
- 배정 전/후 금액
- 최종 액션 사유 코드

## 17. GitHub Actions self-hosted + 한국투자증권 배포안

### 17.1 권장 운영 구조

- 공개 종목 리포트 잡
  - 기존 `site/` 생성
- 비공개 계좌 리포트 잡
  - `self-hosted, Windows, tradingagents-kr, kis`
  - 별도 environment 사용

### 17.2 비밀값

- `KIS_APP_KEY`
- `KIS_APP_SECRET`
- `KIS_ACCOUNT_NO`
- `KIS_PRODUCT_CODE`

토큰은 매 실행마다 발급하고 저장하지 않는다.

### 17.3 공개 / 비공개 산출물

- 공개
  - 기존 ticker site
- 비공개
  - `account_snapshot.json`
  - `portfolio_report.json`
  - `proposed_orders.json`
  - raw broker responses

### 17.4 추천 경로

- private archive
  - runner 외부 고정 디렉터리
- GitHub Pages
  - 공개 종목 site만 업로드

## 18. 단계별 구현

### Phase 1. Read-only MVP

- `portfolio_profiles.toml`
- `KIS adapter`
- `CSV/manual_snapshot fallback`
- `Account Snapshot Service`
- `Candidate Builder`
- `Gate Engine`
- `Allocation Engine`
- `private portfolio_report.md / json`

### Phase 2. Runner / artifact integration

- self-hosted KR account job
- private archive
- masked artifact

### Phase 3. Optional execution planner

- `proposed_orders.json`
- `confirm_required` 모드

### Phase 4. Portfolio evaluation

- `portfolio_walk_forward.py`
- 계좌 수준 백테스트

## 19. 최종 권고

이 설계안의 최종 형태는 아래 문장으로 요약된다.

1. 기존 TradingAgents 티커 런타임은 그대로 둔다.
2. 계좌 계층은 LangGraph 밖의 후처리 서비스로 둔다.
3. `BULLISH + WAIT`는 즉시 주문이 아니라 조건부 배치 후보로 해석한다.
4. `data_coverage`, `quality_flags`, `vendor_health`, `snapshot_id`를 1급 입력으로 사용한다.
5. MVP는 `KIS + CSV/manual snapshot + read_only account report`로 시작한다.

이렇게 가면 이 문서는 단순 아이디어 메모가 아니라, **현재 main 위에 계좌 운영 계층을 안전하게 얹는 구현 설계 문서**가 된다.
