# KR microstructure execution remediation

검토일: 2026-06-27 KST

## 확인된 문제

1. 공개 `chatgpt_execution_context.json`에는 KIS 기반 `last_price`, `session_vwap`, `relative_volume`가 이미 존재했지만, ChatGPT 답변은 무료 웹 시세 재확인 과정에서 이를 “확인 불가”처럼 취급했다.
2. KIS REST 응답의 `mrkt_warn_cls_code = "00"`은 정상 코드인데 기존 정규화가 이를 flagged로 해석해 `market_alert_status`를 차단 사유로 만들었다.
3. KIS 체결 테이프의 `tday_rltv`는 체결강도 성격의 필드인데 기존 추출 후보에 없어 `execution_strength`가 비어 있었다.
4. 코드가 내보내던 `CURRENT_RUN_FRESH` / `LIVE_EXECUTION_OK` 값은 프롬프트의 `LIVE_CHECKPOINT` / `LIVE_EXECUTION_READY` 표현과 달라 LLM이 실행 가능 계열을 보수적으로 오해할 수 있었다.
5. 최신 daily run이 장전 또는 비-checkpoint run이면 fresh microstructure가 없고, 직전 overlay 산출물이 백필되면서 현재 주문과 as-of 판단이 섞여 보였다.

## 적용한 보완

- KIS `mrkt_warn_cls_code`의 정상 코드(`0`, `00`, `000`, `N`)를 clear로 해석한다.
- KIS 체결 테이프의 `tday_rltv`를 `execution_strength` 후보로 사용한다.
- future publication metadata를 프롬프트 친화적인 `LIVE_CHECKPOINT`, `CURRENT_SESSION`, `LIVE_EXECUTION_READY`, `ASOF_EXECUTION_READY`로 정렬한다.
- ChatGPT context에 `asof_execution_gate`를 추가해 core field 존재 여부와 as-of 실행 가능 여부를 기계적으로 표시한다.
- KR 프롬프트는 KIS/TradingAgents microstructure JSON을 as-of 실행표의 1순위 원천으로 쓰고, 무료 웹 시세는 현재 재확인용으로 분리하도록 보강했다.

## 최소비용 데이터 전략

| 선택지 | 월 비용 | 해결 범위 | 한계 | 판단 |
|---|---:|---|---|---|
| KIS Open API REST + WebSocket | 0원 | 국내 현재가, 분봉, 호가, 체결, 프로그램/투자자 수급, 실시간 체결/호가 스트림 | 증권 계정/키 필요, rate limit 및 필드 해석 관리 필요 | 최우선. 현재 코드 경로를 유지하며 WebSocket 보강 |
| KRX Data Marketplace Open API | 0원 또는 승인 기반 | 공식 일별/통계 검증, 종목/ETF 마스터, 지수·일별매매 | execution-grade 실시간 microstructure에는 부적합 | 보조 검증 |
| 금융위/공공데이터포털 KRX 연계 | 0원 | 일별 종가/거래량 백필 | 갱신주기상 실시간 아님 | 백필 전용 |
| Koscom/KRX 시세분배 계약 | 개별 문의 | 공식 실시간/지연 시세 수신, 전문적 재배포·상업 활용 | 개인 자동화에는 과함, 계약·라이선스 비용/절차 큼 | 상업/재배포 목적일 때만 |
| Alpaca/Massive/Twelve Data 등 해외 API | 대략 29~229달러대부터(상품별 상이) | 주로 미국/글로벌 시세, 일부 websocket/실시간 | 한국 KRX microstructure 문제를 직접 해결하지 못하거나 별도 exchange/add-on 확인 필요 | KR 문제 해결용으로 비추천 |

## 권장 작업 순서

1. 현재 적용한 REST 정규화 수정으로 다음 KR overlay에서 `LIVE_CHECKPOINT` / `LIVE_EXECUTION_READY`가 생성되는지 확인한다.
2. KIS WebSocket의 국내주식 실시간체결가, 실시간호가, 실시간프로그램매매를 별도 collector로 붙여 REST checkpoint 직전 30~90초 window를 보강한다.
3. KRX Open API와 공공데이터는 장마감 후 일별 검증·종목 마스터·공식 데이터 reconciliation에만 사용한다.
4. 상업적 재배포나 기관 수준 실시간 시세가 필요해질 때만 Koscom/KRX 계약을 검토한다.
5. 해외 API 유료 구독은 US overlay 품질 개선 목적일 때만 별도 검토한다.

## 성공 기준

- `chatgpt_execution_context.json` 티커 항목에 `last_price`, `session_vwap`, `relative_volume`가 모두 존재한다.
- `asof_execution_gate.core_fields_present = true`.
- fresh 정규장 checkpoint는 `freshness_class = LIVE_CHECKPOINT`, `execution_eligibility = LIVE_EXECUTION_READY`로 게시된다.
- 현재 주문 판단은 여전히 별도 표에서 현재 세션, quote delay, 시장경보, 손절/무효화 조건을 재확인한다.

## 참고 링크

- KIS Developers: https://apiportal.koreainvestment.com/
- KIS 실시간 WebSocket 접속키: https://apiportal.koreainvestment.com/apiservice-apiservice?%2Foauth2%2FApproval=
- KIS 국내주식 실시간시세 목록: https://apiportal.koreainvestment.com/apiservice-apiservice?%2Ftryitout%2FH0UPANC0=
- KRX Open API: https://openapi.krx.co.kr/
- KRX Open API 서비스 목록: https://openapi.krx.co.kr/contents/OPP/INFO/service/OPPINFO004.cmd
- KRX/Koscom 시세 이용계약 절차: https://openapi.krx.co.kr/contents/OPP/DATA/OPPDATA003.jsp
- 공공데이터포털 주식시세정보: https://www.data.go.kr/data/15094808/openapi.do
- Alpaca Market Data pricing: https://alpaca.markets/data
- Massive pricing: https://massive.com/pricing
- Twelve Data pricing: https://twelvedata.com/pricing
