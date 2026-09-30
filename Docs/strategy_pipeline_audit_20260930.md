# KR·US 투자 전략 파이프라인 감사 — 2026-09-30

## 판정

**분석·보고서 생성·배포는 실제로 수행되고 있다. 그러나 US의 ‘26개 전부 보유·관찰’을 정상적인 최신 종합 투자 판단이라고 해석해서는 안 된다.** 가장 직접적인 원인은 Work가 받은 **BUY 20/HOLD 6 입력을 원분석의 legacy rating으로 덮어써 HOLD 26으로 발행한 것**이다. 원분석 갱신 실패, 시세 유효성에 따라 달라지는 전략 변환, 과거 Work 보고서의 우선 적용, 화면 집계 오류도 겹쳐 있다. KR의 매수·축소 표시 역시 현재 주문 지시를 의미하지 않는다.

이번 작업은 사용자가 요청한 **문제 발굴·검증 감사**다. 아래 수정안은 아직 적용하지 않았다. 매수/매도 비율을 인위적으로 늘리거나, 만료된 자료의 실행 제한을 풀거나, 실패한 생산 작업을 새로 실행하지 않았다.

## 기준 자료와 범위

- 코드: `96b7af76208b1123b74c25fdfaa1811e9031baf5`, `nornen0202/TradingAgents`의 main.
- 공개 화면: [KR](https://nornen0202.github.io/TradingAgents/mobile/strategy.html?market=kr), [US](https://nornen0202.github.io/TradingAgents/mobile/strategy.html?market=us). 실제 브라우저와 JSON을 함께 확인했다.
- 고정해서 비교한 공개 데이터: `mobile/strategy.json`, 생성 시각 **2026-09-30 14:04:21 KST**. SHA-256과 정량 증거는 [감사 증거 JSON](strategy_pipeline_audit_20260930_evidence.json)에 기록했다. 이후 자동 배포로 live URL의 내용은 달라질 수 있다.
- 배포 표식: `pages-snapshot.json`, `Intraday Overlay Refresh`, run `36671015819`, 2026-09-30 14:04:24 KST, 위 코드 SHA와 일치.
- 로컬 정본: 최신 완료 full run KR·US 각 30종목, 최신 overlay, 최근 Work 보고서 시장별 6개씩 총 12개, 실패한 US run의 부분 산출물, 관련 GitHub Actions job·annotation·알림 기록.
- 정적 검토: 데이터 공급자 → 종목 분석·토론·구조화 결정 → 포트폴리오/위험 → decision bundle → Work packet·publish → 모바일 변환·렌더링 → Pages 배포·복구·알림.
- 검증: 관련 기존 테스트 **239 passed**. 실제 자료를 이용한 별도 최소 재현과 DOM 집계도 수행했다. 모든 기업 공시·뉴스·시세의 사실을 외부 원문으로 재검증하거나 투자 성과를 검증한 감사는 아니다.

## 같은 ‘HOLD’가 다른 화면이 되는 과정

| 단계 | KR | US |
|---|---|---|
| 마지막 완료 full run | `20260930T081017_github-actions-kr` | `20260929T020356_github-actions-us` |
| 원분석 거래일 | 2026-09-29 | 2026-09-25 |
| 30종목 원모델 rating | HOLD 30 | HOLD 30 |
| 방향 / 당일 진입 | BULLISH 28, NEUTRAL 2 / WAIT 30 | BULLISH 28, NEUTRAL 2 / WAIT 30 |
| 원결정의 조건부 진입 | STARTER 20, NONE 10 | STARTER 26, NONE 4 |
| 공개 카드 수 | 27 | 26 |
| 최신 공개 bundle 전략 | BUY_ON_CONFIRMATION 18, REDUCE 1, HOLD 5, WAIT_CLOSE 1, WAIT 2 | DATA_CHECK 26 |
| 공개 계좌 행동 | 현재 HOLD/WATCH만 존재 | 현재 HOLD/WATCH만 존재 |
| 공개 조건부 행동 | 추가 6, 신규 12, 축소 4, 관찰 2, NONE 3 | 추가 8, 신규 12, NONE 6 |
| 최신 Work가 실제 받은 immutable 입력 thesis | BUY 18, HOLD 8, REDUCE 1 | **BUY 20, HOLD 6** |
| 최신 Work thesis | BUY 18, HOLD 8, REDUCE 1 | HOLD 26 |
| 브라우저 전략 요약 | 매수 17 / 보유 9 / 축소 1 | 매수 0 / 보유 26 / 축소 0 |
| 브라우저 실제 카드 방향 | 매수 18 / 보유 8 / 축소 1 | 보유 26 |

30종목 생산과 27/26개 전송의 차이는 보유·필수 관심종목을 모두 포함한 뒤 탐색 후보를 최대 10개로 제한하는 정책 때문이다. 이를 분석 누락으로 계산하지 않았다. 보유종목과 필수 관심목록은 서로 겹치므로 두 기대 건수를 단순 합산해서도 안 된다.

`rating=HOLD` 자체가 오류라는 증거는 없다. 원결정은 상승 관점, 즉시 행동, 조건부 매수, 하방 위험을 별도로 보유한다. 문제는 다음 전달 과정에서 이 축들을 하나의 보유 등급으로 합치는 것이다.

1. 정규장 overlay에서 `BUY_ON_CONFIRMATION → thesis.BUY`로 전달된다. US 9/30 01:52 KST overlay는 생산 30종목 중 BUY_ON_CONFIRMATION 23개를 갖고 있었다. 최신 Work에 전달된 26종목은 BUY 20/HOLD 6이며 source hash도 발행 보고서와 일치한다.
2. 그런데 최신 US 작성 스크립트 `.runtime/chatgpt-work/drafts/us/build-1addd9e5.py:193`은 `stance = original["rating"]`으로 다시 설정한다. 원본 등급이 모두 HOLD여서 20개 BUY가 HOLD로 바뀐다. 이전 overlay 관점은 `overlay_stance_at_quote_time` 내부에 남지만 모바일 방향은 이 필드를 쓰지 않는다.
3. publish 검증은 BUY→RESEARCH만 막고 BUY→HOLD의 변경 근거를 요구하지 않는다. 최근 US 6개 중 4개가 입력 BUY 20/HOLD 6에서 출력 HOLD 26으로 바뀌었다. 나머지 2개는 입력부터 HOLD 26이었다.
4. 별도로 장외/오래된 자료에서는 `decision_bundle._strategy_code()`가 먼저 DATA_CHECK를 반환하고, `packet._attach_analysis_theses()`가 rating만 stance로 복원한다. 감사 시점 US의 현재 데이터는 이 경로도 거친다. 따라서 작성 스크립트 하나만 고쳐도 전체 문제가 사라지지는 않는다.
5. 모바일 `analysisDirection()`은 과거 Work stance도 현재 행과 조건부 행동보다 우선한다. 요약 `marketOverview()`는 또 다른 규칙으로 action_now를 읽는다. 현재 주문 없음의 HOLD/WATCH가 조건부 전략 집계까지 지배한다.

**정규장과 휴장 차이만으로 설명되지 않는다.** 9월 29일 01:23 KST US Work 보고서는 실행 상태가 WAIT_FOR_TRIGGER 18개, NEEDS_LIVE_RECHECK 8개였음에도 thesis는 26개 모두 HOLD였다. 반대로 감사 시각의 미국장은 닫혀 있었으므로 현재 실행 제한 자체는 적절하다.

## 우선 수정할 결함

### F01 · P1 · Work의 무근거 HOLD 덮어쓰기와 만료 시 전략 의미 손실

- **확인:** 위 immutable 입력→출력 대조에서 BUY 20개가 HOLD로 치환된다. 최신 작성 스크립트는 `rationale`도 원결정의 `entry_logic`을 복사한다. 외부 영상의 조사 순위 조정은 있지만, 20개 방향 변경을 뒷받침하는 새 판단 근거는 별도로 검증되지 않는다. 이는 ‘모델이 최신 근거를 종합해 26개 모두 보유로 판단했다’는 해석과 다르다.
- 별도 최소 재현에서도 동일한 조건부 추가매수 입력에 `conditional_ready=True`면 `BUY_ON_CONFIRMATION`, False면 `DATA_CHECK`가 된다. 이후 복원은 rating만 취한다.
- **위치:** 로컬 최신 작성 스크립트 `build-1addd9e5.py:193`, `tradingagents/work/runtime.py:1358`, `tradingagents/scheduled/decision_bundle.py:430`, `tradingagents/work/packet.py:254`, `tradingagents/work/packet.py:485`, `tradingagents/scheduled/mobile_site.py:1817`. 로컬 실행별 스크립트는 저장소 밖 운영 산출물이므로 저장소 코드만 검토하면 직접 원인을 놓친다.
- **수정:** 원분석 등급, 방향 관점, 조건부 매수 계획, 위험 대응, 현재 실행 준비도를 명시적으로 분리한다. 작성기가 legacy rating으로 덮어쓰지 않게 하고, Work의 방향 변경에는 이전/이후 방향·새 근거·변경 이유를 요구한다. 정당한 새 증거에 따른 BUY→HOLD는 허용하되 만료만을 이유로 일괄 변경하지 않는다. TTL은 실행 준비도만 낮춘다. `OVERWEIGHT`, `UNDERWEIGHT`, `NO_TRADE`도 유효한 원결정 enum인데 복원 허용 집합에서 빠져 있으므로 명시적 매핑이 필요하다. BULLISH나 STARTER를 곧바로 현재 BUY 승인으로 바꾸면 안 된다.
- **완료 조건:** 같은 결정의 시세를 fresh→stale→fresh로 바꿔도 분석 방향·조건부 계획·위험 계획은 동일하고, 현재 실행 상태만 변한다. BUY 20개 입력을 이유 없이 HOLD 26으로 발행하는 재현을 publish가 거부한다. HOLD와 ‘조건부 매수 검토’의 공존을 화면이 설명한다.

### F02 · P1 · US 전체 분석 중단 후 복구 공백과 상태 은폐

- **확인:** [run 36587824683](https://github.com/nornen0202/TradingAgents/actions/runs/36587824683)의 analyze_us가 실패했다. GitHub annotation은 **self-hosted runner lost communication**이다. CPU·메모리·네트워크 중 실제 원인은 해당 기록만으로 확정할 수 없다.
- 실제 분석은 9/30 00:11 KST에 시작했다. `20260930T001148_github-actions-us`에는 9/28 기준 `analysis.json`과 `final_state.json`이 각각 **21개** 남았지만 `run.json`이 없다. 완료된 최신 분석으로 채택될 수 없으며, 이전 9/25 기준 full run이 계속 쓰인다.
- 후속 [36594217937](https://github.com/nornen0202/TradingAgents/actions/runs/36594217937), [36595559090](https://github.com/nornen0202/TradingAgents/actions/runs/36595559090)는 success지만 실제 분석·배포가 skipped다. 앞선 분석이 당시 진행 중이어서 중복 방지된 것으로, 재시도 성공이 아니다.
- `.github/scripts/scheduled_actions_watchdog.py:748`의 US full 복구 창은 KST 17:50~22:45다. 이번 분석은 지연되어 그 창 이후에 시작·실패했으며, 감사 시점까지 새 완료 full run은 없다.
- 최신 overlay의 `status=success`, 분석 성공 30/30 표시는 이전 원분석의 coverage다. 최신 full attempt 실패를 보여주지 않는다.
- **수정:** `latest_attempt`와 `latest_completed_analysis`를 별도로 공개하고 세션별 full 완료 기한을 추적한다. 지연 시작·연결 단절 뒤에도 제한된 재시도/재개를 허용한다. 시작 manifest와 심박·종료 상태를 먼저 영속화하고 부분 종목 결과는 동일 cohort·입력 버전 검증 후에만 재사용한다. 불완전한 21개를 기존 9개와 무조건 합치면 안 된다.
- **완료 조건:** 늦게 시작한 run이 복구 창 뒤에 실패하는 재현에서도 장애가 표시되고 복구 또는 명시적인 최종 실패 상태가 남는다. 건너뜀 success가 분석 성공으로 집계되지 않는다.

### F03 · P1 · 과거 참고 보고서가 현재 카드의 방향·순위·분류를 덮어씀

- **확인:** 공개 KR·US 모두 `reference_report`, `lineage.status=PAST_REFERENCE`, `current_action_cards_enriched=false`다. 그런데 `workStrategy()`는 integrated와 reference를 구분하지 않고 현재 카드에 적용한다. `analysisDirection()`, `rowPriority()`, 카드의 조건·신뢰도·분류가 그 결과를 사용한다. 실행 객체를 제거하는 방어는 있지만 분석·정렬·분류의 출처 격리는 되지 않는다.
- KR은 보고서의 `088350.KS` 대신 현재 전송에 `062040.KS`가 들어오면서 전체 보고서가 coverage mismatch가 됐다. 전체 분석 universe 변화가 아니라 탐색 top-10 전송 집합 변화도 이런 결과를 만들 수 있다.
- US는 같은 full 원분석을 잇는 overlay 체인이지만 `report_source_run_id=...015245...`, 현재 직접 부모는 `...050100...`이어서 lineage mismatch다. freshness는 full 조상을 추적하는 반면 보고서 결합은 직접 run ID 집합만 비교한다.
- **위치:** `mobile_site.py:767`, `mobile_site.py:1634`, `mobile_site.py:1810`, `mobile_site.py:1930`, `.github/scripts/verify_work_pages_handoff.py:115`.
- **수정:** full analysis ID·결정 해시·계약·종목별 일치로 재사용 범위를 증명한다. 증명되지 않은 참고 보고서는 별도 영역에 두고 현재 카드의 전략과 순위를 덮어쓰지 않게 한다. 같은 원분석의 정상 overlay 갱신은 정당한 재사용으로 판정한다.
- **완료 조건:** 다른 full run, 잘못된 계약, 전송 후보 교체, overlay 두 단계 이상을 각각 테스트한다. JSON의 enriched=false와 실제 DOM 동작이 일치해야 한다.

### F04 · P1 · 익절 가격 조건의 방향이 뒤집히고 손실 포지션에도 익절 명칭 유지

- **확인:** 대덕전자 원결정은 TAKE_PROFIT 130,300원 **도달** 조건이고 실행 엔진도 upside에서 `가격 >= 기준`을 평가한다. 그러나 `_risk_condition()`은 모든 가격에 ‘이탈 시’를 붙여 공개 카드에 **‘130,300 이탈 시 이익실현성 축소’**를 출력한다. Work도 이 잘못된 조건을 전달받아 재해석한다.
- 이 공개 행의 평가손익률은 음수인데 TAKE_PROFIT이 유지된다. `_take_profit_lacks_evidence()`는 수익 여부 외에 계획/가격/이유 중 하나만 존재해도 익절 근거를 인정한다. 손실 중 위험 축소가 필요할 수는 있지만, 그것을 이익 실현으로 부르면 안 된다.
- **위치:** `decision_bundle.py:584`, `execution/overlay.py:416`, `portfolio/candidates.py:1157`.
- **수정:** 방향(upside/downside), 비교 연산자, 확인 방식(장중/종가)을 구조화해 엔진과 문구가 같은 조건에서 생성되게 한다. 손익·원가·통화 기준과 매도 목적을 대조하고 필요하면 위험 축소로 재분류한다.
- **완료 조건:** 익절선 위/아래, 손절선 위/아래, 종가 미확정, 손실 포지션 사례에서 평가식·문구·Work 조건이 일치한다. 이 수정은 현재 매도 실행을 승인하는 작업과 분리한다.

### F05 · P2 · 분포 요약과 실제 카드가 다른 판단 규칙을 사용

- **확인:** 동일한 KR DOM에서 요약은 BUY 17/HOLD 9/REDUCE 1, 카드 `data-direction`은 buy 18/hold 8/reduce 1이었다. 현재 Work에 없는 새 후보도 카드에는 조건부 매수로 나오지만 요약은 WATCH로 세어질 수 있다.
- `marketOverview()`는 stance와 action_now를 정규식으로 합치고, 카드의 `analysisDirection()`은 현재 전략·조건부 행동을 추가로 사용한다. AVOID 전용 집계도 없다.
- **위치:** `mobile_site.py:2015`.
- **수정/완료 조건:** 표준 전략 분류 함수를 카드·요약·필터에 공통 적용하고, 요약 합계와 카드 방향별 수가 항상 같아야 한다. ‘현재 주문’과 ‘조건부 검토’ 집계를 분리한다.

### F06 · P2 · 관심종목과 신규 후보의 정본 분류가 Work에서 바뀜

- **확인:** KR 공개 정본은 보유 13/관심 4/신규 10이다. 브라우저는 보유 13/관심 13/신규 1이다. Work가 기존 신규 후보 9개를 `portfolio_role=watchlist`로 적었고, JS가 `row.universe_role`보다 이 값을 우선한다. US의 discovery 10개 분류는 정상이다.
- **위치:** `mobile_site.py:1936`, Work 구조화 보고서 검증.
- **수정/완료 조건:** 보유·관심·탐색 membership은 producer 정본에서 복사하고 publish 시 대조한다. 모델은 조사 순위를 변경할 수 있지만 membership을 임의 변경하지 않는다. 정본·필터 건수 일치 회귀 테스트가 필요하다.

### F07 · P1 · 개인정보 정제가 정상 출처 URL과 기계용 enum을 훼손

- **확인:** 실제 KR 보고서 출처 `https://www.youtube.com/watch?v=3kObJjjyJNI`가 모바일에서는 `http[로컬 경로 제외]`가 된다. Windows 경로 정규식이 `https://`의 `s:/`부터 경로로 인식한다.
- 재귀 번역은 구조화 값까지 `HOLD→보유`, `NEEDS_LIVE_RECHECK→주문 전 실시간 재확인`, `affected_field=confidence→신뢰도`로 바꾼다. 일부 JS는 한국어를 이해하지만 다른 집계는 영문 enum만 검사한다.
- **위치:** `mobile_site.py:170`, `mobile_site.py:419`, `mobile_site.py:929`.
- **수정:** URL 파싱·문맥에 맞는 경로 경계로 개인정보 제거를 제한한다. enum은 그대로 두고 별도 화면 label만 번역한다.
- **완료 조건:** HTTPS·쿼리·한글 URL을 보존하면서 Windows/UNC/개인 경로와 토큰은 계속 제거해야 한다. 공개 JSON enum round-trip과 실제 출처 링크 열기를 검증한다.

### F08 · P2 · 원모델 실행 영수증이 full run 대신 overlay를 읽음

- **확인:** 최신 US Work의 market_analysis 영수증은 이전 overlay를 읽어 CONFIGURED_ONLY, observed_calls=0이다. 실제 full run에는 gpt-6-sol **1,510회** 호출의 usage 기록이 있다. KR 영수증의 27회도 full run의 1,450회와 다르다.
- **위치:** `packet.py:395`; `freshness_receipt.analysis_run_id`와 다른 계보 해석을 사용한다.
- **수정/완료 조건:** 종목 원분석, overlay 처리, Work 종합의 영수증을 분리하고 검증된 full 조상을 참조한다. Work 자체는 여전히 CONFIGURED_NOT_RUNTIME_VERIFIED로 표시해야 하며, 요청 모델을 실제 관측 모델이라고 바꾸지 않는다.

### F09 · P2 · US 공시·거시 자료의 빈 구간이 완료 coverage에 가려짐

- **확인:** 최신 US full의 30종목 모두 disclosures_count=0, macro 도구 fallback 60회, 사회관계망 fallback 30회다. 표본 telemetry에서 FRED_API_KEY 미설정이 명시됐고 workflow에는 FRED 키 전달 경로가 없다. 공시 도구 vendor는 OpenDART만 등록되어 있다. 전용 사회관계망 대신 뉴스 기반 감성을 썼다는 표기는 원문에 존재한다.
- KR은 공시 0건 종목이 1/30이다. US 자료 구조의 상대적 공백이 있으며, ‘30/30 성공’은 필요한 근거가 모두 확보됐다는 뜻이 아니다.
- **장중 실행 자료도 KR과 다르다.** US 01:52/03:11 KST overlay의 conditional_row_ratio는 1.0이지만 fresh_row_ratio는 0이다. 표본 MPWR은 DELAYED_ANALYSIS_ONLY, LULD/Reg SHO/news halt 미제공, 주문장·체결강도 제한을 기록한다. 원천 이름에도 `alpaca.delayed_sip.latest_quote`가 있다. 이는 조건부 분석은 가능하되 즉시 실행은 승인할 수 없는 상태이며, 단순히 시장이 닫혀 있기 때문만은 아니다.
- **위치:** `dataflows/interface.py:139`, `.github/workflows/daily-codex-analysis.yml`, 원분석 `tool_telemetry`, `data_coverage`.
- **수정/완료 조건:** US 기업 공시의 1차 출처 수집 경로와 FRED 구성 진단을 마련한다. 기대하지 않는 ETF 공시와 기업 공시, 자료 미지원·미수집·실제 0건을 구분한다. 공급자별 coverage·누락 근거가 최종 보고서까지 전달돼야 한다. US 시세 entitlement·실시간/지연 feed·시장 상태 지원 범위를 명시하고, 미지원 상태를 정상으로 가정해 실행 제한을 풀지 않는다. 공시 부족을 이유로 모든 종목을 억지로 매수/매도로 변경해서는 안 된다.

### F10 · P2 · 가격 기준일·뉴스 기준일·재무 조회일의 혼합을 최종 제목이 충분히 설명하지 못함

- **확인:** US AMD 상태는 trade_date=9/25, analysis_date=9/29다. 시장 보고서는 9/25 종가, 뉴스는 9/29 기준으로 9/28 사건을 포함한다. 재무 원문은 9/29 조회자료의 9/25 당시 이용 가능 여부가 미확인이라고 적었다. 결정에서는 9/28 뉴스 제외를 언급하기도 한다.
- 최신 의사결정에 전 거래일 종가와 최신 뉴스를 함께 사용하는 것은 가능하다. 그러나 그 결과를 일괄 ‘9/25 당시 분석’ 또는 point-in-time 검증 완료라고 부를 수 없다. `filter_financials_by_date()`는 기본적으로 회계기간 종료일을 필터링하며 공시 당시 버전을 증명하지 않는다. 기본 `point_in_time_strict=False`다.
- **수정/완료 조건:** 가격 기준일과 판단 기준시각을 분리하고 각 근거에 publication/retrieval 시각을 남긴다. 실시간 종합에서는 최신 사건을 일관되게 반영하고, 과거 재현에서는 공시 당시 사용 가능성이 증명된 자료만 사용한다. 과거 자료에 미래 정보가 섞였다는 투자 성과 주장은 이번 감사에서 하지 않는다.

### F11 · P2 · Work 발행 시점의 입력 만료가 반복됨

- **확인:** 최근 KR 6개 보고서는 모두 전 행 NEEDS_LIVE_RECHECK. US 6개 중 5개도 전 행 동일하며, 1개만 WAIT_FOR_TRIGGER 18개가 있다. 최신 KR은 시세 관측→발행 **50.8분**, US는 **90.0분**이다. 장전/장외 보고서도 표본에 포함돼 있으므로 이 비율 전체를 장중 장애율로 해석하면 안 된다.
- 실행 차단은 올바르지만, 사용자는 새 보고서에서 현재 실행 판단을 얻기 어렵다. 게시 시각이 입력 시각을 갱신하지 않는다는 기존 경고는 유지해야 한다.
- **수정/완료 조건:** full 완료/overlay 준비 이벤트에 Work를 맞추고, 오래 걸리는 종합과 짧은 시세 확인을 분리한다. 최종 발행 전에 최신 실행 상태를 별도 검증해 결합하되 과거 thesis의 작성시각·출처를 보존한다. 유효시간을 단순 연장하는 해결은 금지한다.

### F12 · P2 · 배포 검증과 회귀 테스트가 의미 오류를 잡지 못함

- **확인:** report schema·immutable hash·Pages identity 검증은 통과한다. `pages_snapshot._validate_strategy_payload()`는 파일 존재, schema, markets 객체, 식별자 안전성을 검사하지만 분포·조건 방향·분류·정본 재사용 의미는 검사하지 않는다. handoff 검증은 enriched=false 플래그와 execution 제거를 확인하지만 브라우저가 reference thesis를 쓰는지는 확인하지 않는다.
- 관련 239개 테스트가 통과하면서 F01~F08의 재현 결과가 남는다. 테스트 통과를 분석 품질이나 최신 full 완료의 증명으로 삼을 수 없다.
- **수정/완료 조건:** 의미 불변식 테스트를 추가한다. 분포와 카드 일치, 과거 보고서가 현재 결정을 덮어쓰지 않음, enum/URL 보존, 가격 조건의 연산자 일치, stale 전후 thesis 보존, producer membership 보존, 실패 attempt 노출이 포함돼야 한다. ‘BUY가 몇 개 이상’ 같은 결과 할당제는 쓰지 않는다.

## 정상 작동을 확인한 부분

1. **원분석은 실제 실행됐다.** 완료된 KR·US full에 각각 30종목 결과, analyst/토론/최종결정/작성 산출물 및 모델 usage가 존재한다. HOLD를 단순한 빈 응답이나 provider fallback으로 단정할 근거는 없다. batch에는 WAIT 30/30·BULLISH 28/30 편중 경고도 이미 기록된다.
2. **정본 보고서가 생성·보존·배포됐다.** 최신 KR `5a9ba3ce…`, US `33243145…` report hash를 검증했고, 로컬 latest와 content-addressed event가 일치한다. 공개 `work/v1/{market}/report/latest.json`도 로컬 정본과 바이트 단위로 일치했다. [KR handoff](https://github.com/nornen0202/TradingAgents/actions/runs/36670394521), [US handoff](https://github.com/nornen0202/TradingAgents/actions/runs/36611311874)의 실제 build·deploy job이 성공했다.
3. **출력 범위는 의도된 제한이다.** 최신 producer의 보유·필수 관심 누락은 0이다. 30개 생산과 27/26개 카드의 차이는 탐색 후보 상한이다. F06의 표시 분류 오류와 구분해야 한다.
4. **만료 자료로 즉시 주문을 승인하지 않았다.** 최신 Work의 모든 execution은 NEEDS_LIVE_RECHECK다. 참고용 보고서에서 실행 객체를 제거하는 방어도 있다. 다만 F03처럼 thesis/순위 경로는 별도로 보완해야 한다.
5. **외부 근거 전달은 존재한다.** 최신 Work receipt의 KR은 YouTube 12/검토창 75, PRISM 10/10; US는 YouTube 12/44, PRISM 9/9다. US YouTube 기여는 조사 우선순위 1건·순위 7건으로 남아 있다. PRISM이 보고서에 전달됐다는 사실과 종목별 최종 판단에 기여했다는 사실은 다르며, 모든 종목에 기여를 강제할 이유는 없다.
6. **실패 알림도 작동했다.** [notification run 36600828763](https://github.com/nornen0202/TradingAgents/actions/runs/36600828763)의 로그에서 upstream_run_id=36587824683, should_notify=true, reason=upstream_failed, status=SENT를 확인했다. 이는 전송 기록이며 사용자의 실제 수신·열람을 증명하지 않는다. 알림이 없었던 장애라고 단정하지 않았다.

## 수정 순서와 승인 가능한 완료 기준

| 순서 | 범위 | 완료 기준 |
|---|---|---|
| 1 | F02 운영 복구·가시성 | 실패한 최신 full과 이전 완료 full이 구분되고, 세션 마감 기준의 재시도/실패 상태가 증명됨 |
| 2 | F01·F03 전략 의미·계보 | stale 전후 의미 보존, 같은 full 조상 검증, 과거 보고서 영향 범위가 데이터와 DOM에서 일치 |
| 3 | F04·F07 조건·출처 정확성 | 위험 조건 연산자와 문구 일치, 손익 기반 명칭, URL·enum 무손실, 개인정보 제거 유지 |
| 4 | F05·F06·F08 화면·추적성 | 카드/요약/분류 일치, 원모델/overlay/Work 영수증 분리 |
| 5 | F09·F10·F11 근거·시각·운영 | 공급자 공백 표시, source별 시각 계약, Work/시세 갱신 연계 |
| 전 단계 | F12 | 새 의미 회귀 검증을 거친 다음 fork PR→merge→새 배포 산출물/실제 UI 재검증 |

실행 제한은 유지한다. 먼저 원래의 조건부 전략을 정확히 전달하고, 새 분석이 실제로 완료됐는지 보여주는 것이 목표다. 본 감사만으로 특정 종목을 지금 매수·매도해야 한다거나 전략의 수익성이 검증됐다고 결론내리지 않는다.

## 재현·검증 명령

```powershell
.venv/Scripts/python.exe -m tools.audit_work_freshness --archive-dir C:/TradingAgentsData/archive --output .runtime/strategy-audit-20260930/freshness.json
.venv/Scripts/python.exe -m pytest -q tests/test_chatgpt_work.py tests/scheduled/test_mobile_investment_site.py tests/test_work_pages_handoff.py tests/scheduled/test_decision_bundle.py tests/test_scheduled_workflow_gate.py tests/test_scheduled_actions_watchdog.py tests/test_structured_decision.py tests/test_portfolio_pipeline.py tests/test_pages_snapshot.py tests/scheduled/test_trade_date_freshness_guard.py tests/execution/test_account_strategy_research.py
gh run view 36587824683 --repo nornen0202/TradingAgents --json jobs,conclusion,startedAt,updatedAt
gh api repos/nornen0202/TradingAgents/check-runs/109473045505/annotations
```

테스트 결과: **239 passed, 19.00s**. 기존 `.pytest_cache` 쓰기 권한 경고 1건이 있었으며 테스트 실패는 없었다. freshness 명령의 외부 원천 상태는 archive/env 구성에 의존한다. 로컬 셸에 PRISM 경로 환경변수가 없어 생기는 MISSING을 운영 PRISM 장애로 간주하지 않았고, 실제 발행 보고서의 receipt를 사용했다.

감사 증거 JSON은 공개 snapshot의 해시·집계와 실행 식별자만 보존한다. 원시 계좌 파일·계좌 식별자·인증정보·비공개 원문 로그는 저장소에 추가하지 않았다.

## 후속 수정 — 2026-09-30

감사 이후 사용자가 수정·테스트·검증까지 요청하여 다음 보완을 구현했다. 위 감사 표는 수정 전의 고정 관측값이다.

| 항목 | 구현과 검증 |
|---|---|
| F01 | packet의 원등급·관점·즉시 진입·조건부 계획·위험 계획을 보존한다. fresh/stale/fresh에서도 같은 논지를 유지하며 Work의 방향 변경은 전달된 외부 근거와 연결한 변경 영수증이 필요하다. |
| F02 | 전체 실행 시작 전 `attempt.json`을 저장하고 30초 심박·종료 상태를 기록한다. 심박 만료는 INTERRUPTED로 노출한다. 완료 분석과 최신 시도를 분리하고 US 복구 창을 다음 날 08:00 KST까지 확장한다. |
| F03·F11 | 다단계 overlay의 full 조상과 종목별 결정 해시를 대조한다. 같은 분석의 Work 논지와 새 overlay 실행 상태를 별도 결합하고, 검증되지 않은 참고 보고서는 현재 카드를 바꾸지 못한다. TTL은 연장하지 않는다. |
| F04 | 공통 위험 조건 함수로 상방 `>=` / 하방 `<=`와 장중·종가 확인 문구를 맞춘다. 손실 포지션의 익절 표기는 위험 축소로 바꾸되 가격 조건 방향은 유지한다. |
| F05·F06 | 카드와 요약에 같은 분류 함수를 사용한다. 보유/관심/신규 분류는 producer에서 복사하며 publish에서 membership 변경을 거부한다. |
| F07 | HTTPS 출처와 구조화 enum을 보존하고 개인정보·자격증명·로컬 경로 정제는 유지한다. |
| F08 | full 분석과 overlay의 모델 사용량 영수증을 분리한다. Work 모델은 계속 CONFIGURED_NOT_RUNTIME_VERIFIED로 표기한다. |
| F09 | SEC EDGAR 공시 인덱스 경로, FRED 키 전달·탐색, 수집 상태를 추가한다. 공시 본문을 읽은 것으로 과장하지 않으며 종목 미매핑·조회 0건·부분 구간·수집 실패를 구별한다. |
| F10 | 재무·최종 판단 프롬프트에서 판단일과 일봉 가격 기준일을 분리하고 화면에도 각각 표시한다. 회계기간 종료일을 공시 당시 이용 가능성의 증명으로 사용하지 않는다. |
| F12 | 의미 불변식, 원등급 HOLD 덮어쓰기 거부, 다단계 계보·모델 사용량, 위험 조건, 손실 포지션, URL/enum, 장애 기록, 실제 DOM 분포·분류 회귀 검증을 추가한다. Pages stamp에도 의미 검증을 적용한다. |

운영 외부 조건: 2026-09-30 수정 검증 시 로컬 및 GitHub에 FRED 키가 없었고 SEC 공식 endpoint는 HTTP 403을 반환했다. 코드 연결과 명시적 실패 표시는 구현했지만 이 관측을 실제 공시·FRED 수집 성공으로 해석하면 안 된다. 공급자 제한을 근거 없이 해제하거나 주문 가능 상태를 승격하지 않는다. 예약 Work의 KR·US 문구도 v12 정본·변경 근거 계약에 맞추되 시간표와 모델 설정은 유지했다.
