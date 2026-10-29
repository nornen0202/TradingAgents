# PRISM 델타 · 세 종목 미진입과 가상 운용 자료 구분
작성 2026-10-21 09:10:18 KST · 수집 완료 2026-10-21 09:02:27 KST · source health **OK**

## 먼저 볼 변화
1. 수집 21개 메시지·22개 추출 신호가 모두 새 delta다. 24시간 packet은 21/21로 잘리지 않았고 source health는 OK다. 이는 투자 사실의 완전 검증이나 계좌 확인을 뜻하지 않는다.
2. TW·SLS·MRNA의 관심 알림 뒤에 세 종목 모두 NO_ENTRY가 기록됐다. 높은 점수보다 후속 미진입 사유를 우선해 연구상 즉시 관심도를 낮춘다.
3. BTC 데모 7건, 주식 가상 포트폴리오 1건, 가상 운용의 관심 알림 1건을 실제 계좌 거래와 분리한다. 일부 원래 simulation flag가 false라도 본문에 명시된 가상 성격을 보존한다.
4. SNDX·PRLD는 SLS PDF의 비교기업 문맥이다. 독립 추천으로 늘리지 않으며 PDF 본문·차트가 전송되지 않은 한계를 명시한다.
5. 모든 영향은 연구 전용이다. 과거 장중 시세·다중 종목 가격·불명확한 MRNA target 값을 현재 주문·목표·손절로 재사용하지 않는다.

## 범위·시각·자료의 성격
원래 24시간 범위 21건, 전송 21건, 생략 0건, 신규 21건·수정 0건·동일 자료 제외 0건이다. 추출 신호는 총 22개다. 모든 메시지 시각과 신호 시각이 수집 완료 이후가 아니며 현재 24시간 범위 안에 있다. 범위 COMPLETE는 전달된 메시지 범위에만 적용한다. 기업 공시·첨부 전체·실시간 시장·계좌가 모두 검증됐다는 뜻이 아니다.
BTC 데모 7건은 동일 시나리오의 진입·보호 변경·부분 청산·종료다. 원래 simulation_only=false를 숨기거나 고치지 않고, 본문의 데모 문구에 근거해 가상 암호자산으로 별도 분류했다. 부분 청산 가격 손익과 최종 비용 반영 순손익은 중복 합산하지 않는다.
주식 가상 포트폴리오 1건(16403)은 simulation_only=true다. 관심 알림 16390은 flag가 false지만 본문에 가상 포트폴리오 운용이라고 명시돼 있다. 둘 다 실제 사용자 보유·체결의 증거가 아니다. 나머지 미진입·차트·PDF·기업 설명도 실제 주문을 입증하지 않는 연구 자료다.

## 실제 주식 연구에 반영할 충돌
TW·SLS·MRNA의 03:36 KST 관심 알림은 WATCH였지만 03:51 KST 후속 메시지는 NO_ENTRY다. TW는 손익비, SLS는 하락 추세·점수, MRNA는 수익성·성장성 조건을 충족하지 못했다는 원문 판단이다. 이를 후속 시장 종합의 연구 우선순위와 즉시 관심도 하향에 반영한다. 현재 시장 thesis나 주문을 바꾸는 것은 아니다.
원문의 0.99·0.61 등 점수는 해당 봇의 점수이며 독립 사실검증 신뢰도가 아니다. 같은 채널의 본문·PDF·차트 세 건을 세 개의 독립 확인으로 세지 않는다. 원문의 미국 시장 강세 분류도 현재 시장 상태로 승격하지 않는다.

| 식별자 | 연구 액션 | 후속 확인 |
|---|---|---|
| BKH | MAINTAIN | 가상 포트폴리오에서 언급된 종목이다. 실제 보유·HOLD 권고로 해석하지 않고 시장 종합에서 시뮬레이터 참고로만 유지한다. |
| BP | MAINTAIN | 가상 포트폴리오에서 언급된 종목이다. 실제 보유·HOLD 권고로 해석하지 않고 시장 종합에서 시뮬레이터 참고로만 유지한다. |
| FRSH | MAINTAIN | 가상 포트폴리오에서 언급된 종목이다. 실제 보유·HOLD 권고로 해석하지 않고 시장 종합에서 시뮬레이터 참고로만 유지한다. |
| HALO | MAINTAIN | 가상 포트폴리오에서 언급된 종목이다. 실제 보유·HOLD 권고로 해석하지 않고 시장 종합에서 시뮬레이터 참고로만 유지한다. |
| LLY | MAINTAIN | 가상 포트폴리오에서 언급된 종목이다. 실제 보유·HOLD 권고로 해석하지 않고 시장 종합에서 시뮬레이터 참고로만 유지한다. |
| MRNA | DOWNGRADE_WATCH | 후속 NO_ENTRY의 수익성·성장성 gate 미달을 우선한다. 기대되는 파이프라인이 실적·현금 개선으로 이어지는지 검증하며 원문 가격 역할도 재확인한다. |
| PRLD | REQUIRES_PRIMARY_VERIFICATION | SLS PDF의 비교기업 언급이다. SLS 가격·목표를 배정하지 않고 독립 연구 근거가 확보될 때까지 식별 참고로 둔다. |
| SLS | DOWNGRADE_WATCH | 후속 NO_ENTRY의 추세·점수 미달을 보존한다. 임상 기대와 주가 급등을 분리하고 최신 임상 발표·현금 소진·희석 및 추세를 먼저 검증한다. |
| SNDX | REQUIRES_PRIMARY_VERIFICATION | SLS PDF의 비교기업 언급이다. 독립 종목 신호·매수 후보로 올리지 않으며 원문 역할과 기업 공시를 확인한다. |
| TW | DOWNGRADE_WATCH | 선행 관심 신호보다 뒤의 NO_ENTRY(손익비 미달)를 우선한다. 즉시 관심도는 낮추고 실적의 현금 전환·인수 실행 위험·시장 조건 검증을 연구 우선 과제로 올린다. |

## 가격·첨부·종목 매핑 한계
- 10월 20일 미국 장중 관측 가격은 확정 종가·현재 시세가 아니다. 미국 장 종료 후 작성된 이 보고서에서 새 실행 가격으로 사용하지 않는다.
- BP·HALO·LLY의 다중 종목 가격은 mention block 경고가 있다. 독립 원문 대조와 최신 시세 확인 없이 목표·손절로 옮기지 않는다.
- MRNA 설명의 추출 target_price는 preview의 과거 관측가와 역할이 불명확하다. 숫자를 수정해 정상처럼 만들지 않고 가격 역할·기간 검증 전 사용을 배제한다.
- SLS PDF의 SNDX·PRLD는 비교기업 문맥이다. 명시된 ticker를 보존하되 추천 개수로 부풀리거나 SLS 가격을 연결하지 않는다.
- PDF 본문은 packet에서 빈 preview·NO_ARCHIVED_TEXT다. 차트는 안내문만 전달됐다. 따라서 전체 PDF·이미지의 수치와 도형을 직접 검증했다고 표현하지 않는다.

## 21개 신규 메시지 검토

### 1. stock_ai_agent:16410 · CRYPTO_DEMO
[원메시지](https://t.me/stock_ai_agent/16410) · 10-21 05:57:26 KST · 원래 simulation_only=false
BTC 데모 종료·정산 알림이다. 부분 청산과 최종 정산을 중복 합산하지 않는다. 실제 사용자 계좌의 손익이나 주문 완료로 간주하지 않는다.

### 2. stock_ai_agent:16409 · CRYPTO_DEMO
[원메시지](https://t.me/stock_ai_agent/16409) · 10-21 05:56:27 KST · 원래 simulation_only=false
BTC 데모 보호 변경이며 남은 수량을 다루는 알림이다. 원래 simulation_only=false여도 본문에 데모라고 명시돼 가상 암호자산 자료로 분류한다.

### 3. stock_ai_agent:16408 · CRYPTO_DEMO
[원메시지](https://t.me/stock_ai_agent/16408) · 10-21 05:51:28 KST · 원래 simulation_only=false
앞선 BTC 데모 보호 변경의 후속 상태다. 새 주식 종목 신호나 독립 수익 사례로 세지 않는다.

### 4. stock_ai_agent:16407 · CRYPTO_DEMO
[원메시지](https://t.me/stock_ai_agent/16407) · 10-21 05:50:28 KST · 원래 simulation_only=false
BTC 데모의 부분 청산이다. 수수료·펀딩 전 가격 손익과 정산 후 순손익을 구분하며 실제 수익으로 합산하지 않는다.

### 5. stock_ai_agent:16406 · CRYPTO_DEMO
[원메시지](https://t.me/stock_ai_agent/16406) · 10-21 05:38:28 KST · 원래 simulation_only=false
BTC 데모의 다른 부분 청산이다. 같은 시나리오의 분할 관측이며 투자 성과의 독립 표본이 아니다.

### 6. stock_ai_agent:16405 · CRYPTO_DEMO
[원메시지](https://t.me/stock_ai_agent/16405) · 10-21 05:31:28 KST · 원래 simulation_only=false
BTC 데모 보호 가격·레버리지·가상 자산 상태다. 주식의 목표·손절·크기로 전이하지 않는다.

### 7. stock_ai_agent:16404 · CRYPTO_DEMO
[원메시지](https://t.me/stock_ai_agent/16404) · 10-21 04:47:27 KST · 원래 simulation_only=false
BTC 데모 첫 진입이며 이후 부분 청산·종료와 같은 가상 시나리오다. 실제 계좌 매수의 증거가 아니다.

### 8. stock_ai_agent:16403 · VIRTUAL_PORTFOLIO
[원메시지](https://t.me/stock_ai_agent/16403) · 10-21 03:51:42 KST · 원래 simulation_only=true
FRSH·BKH·BP·HALO·LLY의 가상 포트폴리오 관측이다. simulation_only=true를 유지하고 HOLD를 사용자 보유 판단으로 바꾸지 않는다. 다중 종목의 목표·손절은 재사용하지 않는다.

### 9. stock_ai_agent:16402 · EQUITY_NO_ENTRY
[원메시지](https://t.me/stock_ai_agent/16402) · 10-21 03:51:40 KST · 원래 simulation_only=false
TW의 앞선 관심 신호 뒤에 손익비 하한 미달로 미진입이 기록됐다. 연구 후보의 즉시 관심도를 낮추며 실적·인수·가격 조건을 새 공식 자료로 검증할 우선순위를 올린다.

### 10. stock_ai_agent:16401 · EQUITY_NO_ENTRY
[원메시지](https://t.me/stock_ai_agent/16401) · 10-21 03:51:37 KST · 원래 simulation_only=false
SLS는 앞선 높은 점수의 관심 신호 뒤에 하락 추세·점수 부족으로 미진입이 기록됐다. 임상 기대를 진입 허가로 해석하지 않고 최신 임상·현금·추세 확인을 요구한다.

### 11. stock_ai_agent:16400 · EQUITY_NO_ENTRY
[원메시지](https://t.me/stock_ai_agent/16400) · 10-21 03:51:33 KST · 원래 simulation_only=false
MRNA는 앞선 관심 신호 뒤에 수익성·성장성 gate 미달로 미진입이 기록됐다. 상승률·점수보다 원문 gate 미달을 우선해 연구상 관심도를 낮춘다.

### 12. stock_ai_agent:16399 · CHART_REFERENCE
[원메시지](https://t.me/stock_ai_agent/16399) · 10-21 03:44:45 KST · 원래 simulation_only=false
TW 차트 주석 안내만 전달됐다. 이미지의 베이스·피벗·상대강도를 직접 검증한 것이 아니므로 돌파 확인이나 가격 조건을 새로 생성하지 않는다.

### 13. stock_ai_agent:16398 · CHART_REFERENCE
[원메시지](https://t.me/stock_ai_agent/16398) · 10-21 03:44:33 KST · 원래 simulation_only=false
SLS 차트 참고 메시지이며 실제 임상 공시나 매수 신호가 아니다. 뒤따르는 미진입 판단과 함께 본다.

### 14. stock_ai_agent:16397 · CHART_REFERENCE
[원메시지](https://t.me/stock_ai_agent/16397) · 10-21 03:44:20 KST · 원래 simulation_only=false
MRNA 차트 참고 자료다. 차트 존재만으로 수익성·성장성 미달을 해소하지 않는다.

### 15. stock_ai_agent:16396 · PDF_REFERENCE
[원메시지](https://t.me/stock_ai_agent/16396) · 10-21 03:44:06 KST · 원래 simulation_only=false
TW PDF에서 추출된 WATCH 식별자만 전달됐고 packet 본문은 비어 있다. 전체 PDF를 읽거나 핵심 숫자를 검증했다고 표현하지 않는다.

### 16. stock_ai_agent:16395 · PDF_REFERENCE
[원메시지](https://t.me/stock_ai_agent/16395) · 10-21 03:44:01 KST · 원래 simulation_only=false
SLS PDF의 SNDX·PRLD는 표시명에 비교기업 문맥이 포함돼 있다. 세 종목을 독립 추천으로 승격하지 않으며 SLS의 가격·목표를 비교기업에 배정하지 않는다.

### 17. stock_ai_agent:16394 · PDF_REFERENCE
[원메시지](https://t.me/stock_ai_agent/16394) · 10-21 03:43:55 KST · 원래 simulation_only=false
MRNA PDF의 WATCH와 식별자만으로 사업 실적·임상·목표가가 검증되지 않는다. 본문 미전송 한계를 보존한다.

### 18. stock_ai_agent:16393 · EQUITY_COMMENTARY
[원메시지](https://t.me/stock_ai_agent/16393) · 10-21 03:43:48 KST · 원래 simulation_only=false
TW 전자거래 사업과 과거 장중 가격·거래량에 대한 설명이다. 확정 종가나 기관 순매수 증거로 쓰지 않으며 후속 미진입과 구분한다.

### 19. stock_ai_agent:16392 · EQUITY_COMMENTARY
[원메시지](https://t.me/stock_ai_agent/16392) · 10-21 03:43:43 KST · 원래 simulation_only=false
SLS 임상 단계와 과거 장중 상승 설명이다. 당시 관측 가격을 현재 시세로 사용하지 않고 임상·현금·희석 위험을 공식 자료로 확인한다.

### 20. stock_ai_agent:16391 · EQUITY_COMMENTARY
[원메시지](https://t.me/stock_ai_agent/16391) · 10-21 03:43:39 KST · 원래 simulation_only=false
MRNA 모멘텀과 사업 회복 설명이다. packet target_price가 preview의 과거 관측가보다 낮아 가격 역할·기간·원문 매핑이 확인될 때까지 목표값 사용을 배제한다.

### 21. stock_ai_agent:16390 · VIRTUAL_SIGNAL_ALERT
[원메시지](https://t.me/stock_ai_agent/16390) · 10-21 03:36:22 KST · 원래 simulation_only=false
본문은 가상 포트폴리오 운용 공개라고 명시한다. MRNA·SLS·TW의 WATCH와 높은 점수는 독립 검증 신뢰도나 현재 매수 허가가 아니다. 후속 세 종목 미진입을 함께 전달한다.

## 다음 확인
다음 범위 확인 기준은 2026-10-22 03:36:22 KST다. 이는 24시간 자료 범위의 만료 확인 시각이며 매매 유효기간이 아니다.
- TW·SLS·MRNA 최신 공식 공시와 현금·실적/임상 확인
- 차트와 PDF 본문을 별도 전달받기 전 수치 검증 완료로 처리하지 않기
- SNDX·PRLD 비교기업 역할과 MRNA 가격 역할 확인
- 다음 미국 세션에서 최신 시세·계좌·기존 gate 재검증

KR에는 이번 packet의 검증된 종목 신호가 없다. US에는 세 종목 미진입·첨부 누락·가상 운용 구분을 전달한다. 신선한 시세·계좌·기존 위험 gate가 없으므로 모든 행은 RESEARCH_ONLY다. 외부 알림과 공개 페이지 전달은 로컬 publish·ACK 뒤 별도로 확인해야 한다.

COVERAGE_RECEIPT {"event_id":"prism:56061743d60a18c1b21c1ab33b5efa8d","status":"COMPLETE","window_events":21,"transmitted_events":21,"truncated":false,"new_events":21,"revised_events":0}

MOBILE_HANDOFF {"owner":"external_github_notification_pipeline","status":"PENDING_EXTERNAL_VERIFICATION","work_sent_notification":false}