# TradingAgents KR 리포트/의사결정 보정 작업 명세서 (Codex용)

## 목적

현재 `nornen0202/TradingAgents` main 브랜치와 KR 실행 결과를 기준으로,

1. **국내 종목 배치 결과가 전부 `NO_TRADE`로 수렴하는 문제를 진단**하고,
2. **리포트 텍스트는 유지하되 최종 의사결정 캘리브레이션을 개선**하며,
3. **KR 데이터 품질/출처 투명성/텔레메트리 품질을 높이는 패치**를 구현한다.

이 작업의 목표는 **무리하게 BUY를 늘리는 것**이 아니라,
- 좋은 종목인데 “지금은 진입 대기”인 경우,
- 구조는 긍정적이지만 단기 셋업이 아직 미완성인 경우,
- 데이터가 빈약해서 관망해야 하는 경우,

이 셋을 **서로 다른 상태로 표현**하게 만드는 것이다.

---

## 이번 KR 실행에서 확인된 사실

- 2026-04-08 KR 배치는 **12개 종목 전부 성공 처리되었지만 최종 Decision은 전부 `NO_TRADE`**였다.
- 실행은 **Provider `codex` / Deep model `gpt-5.4` / Quick model `gpt-5.4-mini`** 조합으로 돌아갔다.
- `000660.KS`, `012450.KS`, `278470.KS` 등 개별 리포트는 기술/펀더멘털/리스크에 대한 서술 자체는 꽤 구체적이지만, 최종 액션은 모두 `NO_TRADE`다.
- 특히 `012450.KS`와 `278470.KS`는 리포트 본문상으로는 “조건부 진입 후보”, “소규모 시작 가능”, “조건부 no trade” 같은 뉘앙스가 있음에도 최종 출력은 단일 `NO_TRADE`로 압축된다.
- 개별 리포트 페이지에는 `LLM calls 31`, `Tool calls 0`이 반복해서 표시되는데, 실제 리포트 내용은 가격/뉴스/펀더멘털을 사용하고 있어 **계측(telemetry) 신뢰성이 낮아 보인다**.

---

## 핵심 진단

### 1) 현재 문제는 “분석 불능”보다 “결정 스키마/캘리브레이션 불량”에 가깝다

애널리스트 텍스트를 보면 종목별 차이는 분명히 있다. 그러나 최종 decision layer에서

- `좋은 종목 + 지금 진입은 애매함`
- `구조는 긍정적 + 촉매 대기`
- `완전히 불확실해서 건드리면 안 됨`

이 세 경우가 모두 `NO_TRADE`로 납작해지고 있다.

즉, **리포트 본문은 어느 정도 분별력이 있는데, 최종 decision schema가 nuance를 잃는다.**

### 2) `NO_TRADE` 허용 자체가 문제가 아니라, 너무 넓은 의미로 사용되고 있다

현재 prompt 계층은 `NO_TRADE`를 허용하는 정도가 아니라, **확신이 조금만 부족해도 `NO_TRADE`를 선택하기 쉬운 구조**로 보인다.

이건 보수성을 높이는 대신, 배치 결과를 “전부 0%”로 잠그는 부작용을 만든다.

### 3) KR 데이터는 구조상 좋아졌지만, 여전히 “직접 뉴스/직접 소셜/직접 공시”의 빈약함이 판단을 과도하게 보수화시킨다

KR 경로는 `naver/opendart/ecos`를 우선시하는 로직이 이미 있으나, 실제 종목별 리포트는

- 전용 social provider 없음
- 뉴스는 뉴스 기반 감성으로 대체
- 직접 회사 뉴스/공시 없음
- 거시/테마 기반 간접 신호 의존

이 빈도가 높다.

이 상황에서는 **보수적 모델이 전부 “확인형 대기”로 수렴하기 쉬움**.

### 4) 텔레메트리 계층이 깨져 있으면 품질 분석도 왜곡된다

리포트에 `Tool calls 0`이 반복 노출되면,
- 실제로 툴이 불리지 않았는지,
- 불렸는데 계수만 빠졌는지,
- 토큰 집계가 누락됐는지,

구분이 불가능하다.

이건 분석 정확도 이전에 **관측 가능성(observability) 문제**다.

---

## 작업 원칙

1. **`NO_TRADE`를 제거하지 말 것.**
   - `NO_TRADE`는 유지한다.
   - 다만 의미를 좁혀서 “현재 액션을 취할 근거가 부족한 경우”에 한정한다.

2. **억지로 BUY/HOLD를 늘리지 말 것.**
   - 단지 분포를 예쁘게 만들려고 결론을 강제로 바꾸지 않는다.

3. **최종 decision은 계속 deterministic parsing을 유지할 것.**
   - 현재처럼 `parse_structured_decision()` 기반 deterministic parse는 유지한다.
   - LLM으로 마지막 문자열을 다시 추출하는 방식으로 되돌리지 않는다.

4. **KR 데이터 빈약성은 결과 스키마와 confidence에 반영할 것.**
   - 직접 회사 뉴스/공시가 없으면 confidence를 깎고, provenance를 표시한다.

5. **리포트는 “스탠스”와 “즉시 액션”을 분리해 보여줄 것.**
   - 지금의 가장 큰 병목은 이 둘이 한 필드에 섞여 있다는 점이다.

---

## P0. 최우선 패치 — Decision schema 재설계

### 목표
`NO_TRADE`를 줄이는 것이 아니라, **“긍정적이지만 대기”와 “완전 회피”를 구분**하게 만든다.

### 수정 대상
- `tradingagents.schemas` 모듈 (결정 스키마/출력 지시문/검증/파서 정의부)
- `tradingagents/agents/managers/research_manager.py`
- `tradingagents/agents/managers/portfolio_manager.py`
- `tradingagents/graph/signal_processing.py`
- 최종 HTML 리포트/인덱스 렌더러 (파일 탐색 후 수정)

### 요구사항
현재 공통 decision schema를 확장해서 최소 아래 필드를 추가하라.

```json
{
  "rating": "NO_TRADE | UNDERWEIGHT | HOLD | OVERWEIGHT | BUY",
  "portfolio_stance": "BEARISH | NEUTRAL | BULLISH",
  "entry_action": "NONE | WAIT | STARTER | ADD | EXIT",
  "setup_quality": "WEAK | DEVELOPING | COMPELLING",
  "confidence": 0.0,
  "time_horizon": "short | medium | long",
  "entry_logic": "...",
  "exit_logic": "...",
  "position_sizing": "...",
  "risk_limits": "...",
  "catalysts": ["..."],
  "invalidators": ["..."],
  "watchlist_triggers": ["..."],
  "data_coverage": {
    "company_news_count": 0,
    "disclosures_count": 0,
    "social_source": "dedicated | news_derived | unavailable",
    "macro_items_count": 0
  }
}
```

### 중요한 설계 규칙
- `rating`은 **레거시 호환용**으로 남기되, 더 이상 “즉시 액션”을 단독으로 대표하지 않게 한다.
- `portfolio_stance`는 **종목에 대한 방향성 평가**다.
- `entry_action`은 **오늘 당장 무엇을 할지**다.
- 즉,
  - 좋은 종목이지만 진입 타이밍이 애매하면:
    - `portfolio_stance = BULLISH`
    - `entry_action = WAIT`
    - `rating`은 레거시 규칙에 따라 `NO_TRADE` 또는 `HOLD`로 매핑 가능
  - 진짜로 피해야 하는 종목이면:
    - `portfolio_stance = BEARISH or NEUTRAL`
    - `entry_action = NONE`

### prompt 수정 지침
#### Research Manager
현재 prompt의 “evidence가 약하거나 conflicted면 NO_TRADE” 톤을 완화하라.

바꿔야 할 방향:
- `NO_TRADE`는 허용하되,
- **증거가 긍정적이지만 entry timing만 미완성인 경우에는**
  - `portfolio_stance`는 긍정으로 유지하고,
  - `entry_action=WAIT` 또는 `STARTER` 후보를 제시하게 하라.

#### Portfolio Manager
현재 prompt는 사실상 “자본 배정에 완전히 compelling하지 않으면 NO_TRADE”로 기운다.

바꿔야 할 방향:
- 최종 판단 시 반드시 다음을 구분하도록 강제하라.
  1. 종목 방향성 평가
  2. 즉시 신규 진입 여부
  3. 감시 목록 유지 여부
  4. 조건 충족 시 starter 가능 여부

### 리포트/UI 수정
- 개별 종목 페이지 상단에 다음을 모두 노출:
  - `Decision` (legacy)
  - `Portfolio stance`
  - `Entry action`
  - `Setup quality`
- 배치 인덱스 페이지에는 `Decision`만 보여주지 말고 최소
  - `Decision`
  - `Stance`
  - `Entry action`
  를 같이 보여라.

### 기대 효과
예를 들어 `012450.KS`, `278470.KS` 같은 종목은
- 지금 당장 신규 매수는 안 하더라도,
- “좋은 종목 / 구조는 긍정 / 조건부 대기”라는 상태가 결과에 드러나게 된다.

---

## P1. 텔레메트리 복구 — Codex/Tool usage 계측 정상화

### 목표
리포트 페이지의 `LLM calls`, `Tool calls`, `tokens`가 실제 실행을 반영하게 한다.

### 수정 대상
- Codex LLM wrapper/adapter 구현부 (현재 Codex provider 구현 파일 탐색 후 수정)
- stats callback 구현부 (현재 callback handler 구현 파일 탐색 후 수정)
- 스케줄 러너/리포트 생성기 (통계값 기록부)
- `tradingagents/graph/trading_graph.py`

### 이유
현재 그래프는 callback을 LLM constructor에 전달하도록 되어 있는데, 결과 리포트에는 `Tool calls 0`이 반복된다. 이는 실제 툴 미사용이 아니라 **계측 누락 가능성**이 높다.

### 요구사항
1. **LLM call / token usage / tool call을 모두 일관되게 집계**하라.
2. 모델별 통계를 분리하라.
   - deep model calls
   - quick model calls
3. 툴 통계도 분리하라.
   - tool name
   - vendor used
   - success/fallback 여부
4. HTML 리포트에 아래 정보를 추가하라.
   - 총 tool calls
   - vendor별 호출 수
   - fallback 발생 횟수
5. 통계가 수집되지 못하면 `0` 대신 `unknown` 또는 `unavailable`로 표시하라.
   - 잘못된 0은 분석을 왜곡한다.

### acceptance
- 가격/뉴스/펀더멘털이 실제로 들어간 종목 리포트에서 `Tool calls`가 무조건 0으로 찍히지 않아야 한다.
- vendor fallback이 있었다면 최종 보고서 메타데이터에 남아야 한다.

---

## P1. KR data provenance/coverage 강화

### 목표
KR 리포트가 **무슨 데이터가 없어서 보수적으로 결론 났는지**를 명확히 드러내게 한다.

### 수정 대상
- `tradingagents/dataflows/interface.py`
- `tradingagents/dataflows/naver_news.py`
- `resolve_instrument`를 제공하는 instrument resolver 모듈 (파일 탐색 후 수정)
- `tradingagents/agents/analysts/social_media_analyst.py`
- 뉴스/공시/소셜 관련 agent utils 및 report rendering

### 요구사항
1. **vendor provenance를 state에 보존**하라.
   - 어떤 툴이 어느 vendor로 응답했는지
   - fallback이 있었는지
2. **coverage metadata를 같이 저장**하라.
   - company news count
   - disclosures count
   - social evidence count
   - macro items count
3. `naver_news`에서 KR 종목 검색 시 사용하는 `profile.display_name` 의존성을 개선하라.
   - 기본은 현재처럼 company display name 사용
   - 추가로 alias fallback을 넣는다:
     - 한글 회사명
     - 영문 회사명
     - 숫자 종목코드
     - Yahoo symbol
     - 흔한 약칭
   - 다중 질의를 날린 뒤 dedupe하는 방식을 허용한다.
4. 직접 회사 뉴스/공시가 0건이면, 보고서와 decision schema의 `data_coverage`에 반드시 반영하라.
5. 리포트에 “사회심리”가 실제 social data인지 news-derived sentiment인지 구분해서 표시하라.

### social agent 처리 방침
현재 social analyst는 `get_social_sentiment`와 `get_company_news`를 같이 쓰고, prompt도 “전용 social provider가 없으면 news-derived sentiment임을 명시하라”는 방향이다. 따라서 아래 둘 중 하나를 택하라.

#### 옵션 A
이름을 유지하되, 리포트 섹션명을 다음처럼 바꾼다.
- `소셜/공적서사 애널리스트`
- `Public Narrative & Sentiment Analyst`

#### 옵션 B
이름은 유지하되, 헤더에 source type을 강제 표시한다.
- `Source type: dedicated social`
- `Source type: news-derived sentiment`

### acceptance
- `012450.KS` 같이 직접 뉴스/공시가 없을 때, final decision JSON과 HTML에 그 사실이 명시돼야 한다.
- social report가 news-derived인 경우, 절대 실제 소셜 게시물을 본 것처럼 쓰지 않아야 한다.

---

## P1. Batch sanity check 추가

### 목표
“이번처럼 12개 전부 `NO_TRADE`” 같은 배치 회귀를 CI/사이트 생성 단계에서 자동 감지한다.

### 수정 대상
- KR 배치 실행 스크립트
- 결과 집계/사이트 생성 스크립트
- GitHub Actions workflow 또는 배치 스케줄러

### 요구사항
1. 배치 종료 후 다음 지표를 자동 계산하라.
   - `decision_distribution`
   - `stance_distribution`
   - `entry_action_distribution`
   - 평균 confidence
   - direct company news 0건 비율
2. 아래 조건이면 warning을 남겨라.
   - 종목 수 >= 10
   - `Decision == NO_TRADE` 비율 >= 80%
3. 아래 조건이면 stronger warning을 남겨라.
   - `NO_TRADE` 비율 >= 80%
   - 그런데 `portfolio_stance == BULLISH` 또는 `entry_action == WAIT` 비율이 높음
   - 즉 “좋은 종목인데 전부 legacy decision만 `NO_TRADE`”인 상태
4. 경고는
   - 콘솔 로그
   - 결과 JSON
   - 사이트 index 상단 banner
   모두에 남겨라.

---

## P2. KR 종목 식별/검색 품질 개선

### 목표
한국 종목 뉴스/공시 recall을 올린다.

### 수정 대상
- instrument resolver 모듈
- KR vendor adapter들 (`naver`, `opendart`, 필요시 `ecos`)
- 관련 tests

### 요구사항
1. 종목 식별을 다음 체계로 표준화하라.
   - `input_symbol`
   - `normalized_symbol`
   - `country`
   - `display_name_kr`
   - `display_name_en`
   - `krx_code`
   - `yahoo_symbol`
   - `dart_corp_code`
   - `aliases[]`
2. 뉴스 검색은 `aliases[]` 기반으로 recall을 높여라.
3. OpenDART 연동은 가능한 경우 corp code 기반으로 안정화하라.
4. 리포트 상단에 사람이 읽기 좋은 회사명을 표시하라.
   - 숫자 코드만 덩그러니 보이지 않게

### acceptance
- `005930.KS`, `000660.KS`, `012450.KS` 같은 KR 종목이 각각 올바른 회사명/alias 세트를 갖는다.
- Naver search query가 숫자 코드 단독에만 의존하지 않는다.

---

## P2. KR run configuration audit

### 목표
현재 main의 기본 vendor/fallback 로직은 괜찮지만, **KR 배치가 어떤 설정으로 실제 실행됐는지 더 명시적/재현 가능**하게 만든다.

### 수정 대상
- KR schedule/workflow/config 파일 (탐색 후 수정)
- `default_config.py`
- batch runner

### 요구사항
1. KR 배치용 설정을 명시적으로 분리하라.
   - 예: `configs/kr_daily.yaml` 같은 형태
2. 최소 아래 항목이 명시적으로 보이게 하라.
   - `market_country=KR`
   - timezone
   - deep/quick model
   - vendor priority
   - debate rounds
   - risk discuss rounds
3. KR 설정에서 vendor priority를 명시하라.
   - `get_company_news`: `naver,...`
   - `get_disclosures`: `opendart`
   - `get_macro_news`: `ecos,...`
   - `get_social_sentiment`: `naver,...`
4. 기본 2/2 토론 라운드보다 낮게 내려간 override가 있는지 점검하라.
   - 비용 때문에 낮춘 경우, 왜 낮췄는지 주석/문서화
   - 배치가 지나치게 `NO_TRADE`로 수렴하면 KR 배치에서는 최소 2/2를 권장

### 참고
main 기본 설정은 `max_debate_rounds=2`, `max_risk_discuss_rounds=2`, `enable_no_trade=True`다. 따라서 KR 배치가 다르게 실행됐다면, 그 override를 반드시 추적 가능하게 만들어야 한다.

---

## P2. 모델 구성 관련 원칙

### 현재 상태
- main 기본값은 deep=`gpt-5.4`, quick=`gpt-5.4-mini`
- 이번 KR 실행도 같은 조합으로 돌았다.

### 지침
이 패치의 1차 목표는 **모델 교체가 아니라 의사결정 구조 보정**이다.

즉,
- 이번 패치에서는 deep/quick 조합을 그대로 유지해도 된다.
- 먼저 schema/data/telemetry를 고친 뒤,
- 그 다음에 필요하면 모델 비용 최적화를 다시 논의한다.

---

## P3. 리포트 해석력 개선

### 목표
사용자가 “왜 `NO_TRADE`인지” 뿐 아니라, “이 종목을 아예 싫어하는지 / 그냥 대기인지”를 즉시 알 수 있게 한다.

### 수정 대상
- HTML report renderer
- Markdown report builder
- index page builder

### 요구사항
개별 종목 리포트 상단 요약 카드에 다음을 추가하라.

- `Legacy decision`
- `Portfolio stance`
- `Immediate action`
- `Setup quality`
- `Confidence`
- `Primary blockers`
- `Watchlist triggers`
- `Data coverage summary`
- `Evidence source summary` (company news / macro / disclosures / social-derived)

### 예시
```text
Legacy decision: NO_TRADE
Portfolio stance: BULLISH
Immediate action: WAIT
Setup quality: DEVELOPING
Primary blockers: no company-specific catalyst, short-term momentum unconfirmed
Watchlist triggers: reclaim 10EMA, MACD cross, new filing/news
Data coverage: company news 0, disclosures 0, social=news-derived, macro=3
```

이렇게 되면 `NO_TRADE` 하나만 보고 오해하는 일이 줄어든다.

---

## 구현 시 주의사항

1. **결과 분포를 억지로 바꾸기 위해 프롬프트만 과도하게 bullish하게 바꾸지 말 것.**
2. **deterministic parse는 유지할 것.**
3. **리포트/사이트가 schema 확장 후에도 backward-compatible 하게 동작할 것.**
4. **과거 결과 파일이 새 renderer에서 깨지지 않도록 migration 또는 fallback을 넣을 것.**
5. **테스트를 반드시 추가할 것.**

---

## 권장 테스트

### 단위 테스트
- schema validation / parser test
- legacy decision ↔ stance/action mapping test
- vendor provenance serialization test
- social source labeling test
- KR alias resolution test

### 통합 테스트
- `012450.KS` 유사 케이스:
  - 직접 뉴스/공시 0
  - 기술구조 강세
  - 기대 결과: `portfolio_stance=BULLISH or NEUTRAL-BULLISH`, `entry_action=WAIT`, legacy `NO_TRADE` 가능
- `278470.KS` 유사 케이스:
  - 장기 펀더멘털 강함
  - 단기 모멘텀 미완성
  - 기대 결과: 조건부 대기 + 트리거 표시
- `058470.KS` 유사 케이스:
  - 좋은 재무지만 촉매 부재
  - 기대 결과: `WAIT` 또는 `NONE`, blocker 명시

### 배치 테스트
- 10개 이상 KR 종목 샘플 배치에서
  - decision distribution 생성
  - stance/action distribution 생성
  - sanity warning 작동 확인
  - telemetry non-zero/unknown 표시 확인

---

## 최종 산출물

Codex는 아래 결과물을 제출해야 한다.

1. 수정된 코드
2. 변경 파일 목록과 변경 이유
3. 새 decision schema 설명
4. telemetry 변경 설명
5. KR data provenance/coverage 변경 설명
6. 테스트 결과
7. 샘플 KR 종목 2~3개에 대한 전/후 비교 요약
   - 특히 `NO_TRADE`가 그대로라도, 이제는 **왜 대기인지/왜 회피인지 구분**되는지 보여줄 것

---

## 한 줄 요약

이 작업은 **`NO_TRADE`를 없애는 작업이 아니라, `NO_TRADE`가 너무 많은 의미를 떠안고 있는 구조를 분해하는 작업**이다. 리포트 본문의 분별력은 어느 정도 살아 있으므로, 핵심은 **decision schema, telemetry, KR provenance, report UI**를 고쳐서 그 분별력이 최종 결과에도 드러나게 만드는 것이다.
