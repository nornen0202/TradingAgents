# PRISM 리서치 델타 · 2026-10-18

신규 5건은 BTC 데모 진입·보호 변경·종료 기록. 실제 주식 리서치에 반영할 새 근거는 없어 NO_ACTIONABLE_DELTA.

- 소스 정상: 생산 성공 09:16:30 KST. 검증 시각 2026-10-18T11:57:45+09:00; 생산 경과 2.69시간으로 30시간 한도 내.
- 5건 모두 최근 24시간 내이며 미래·역전 시각 없음. 신규 5, 수정 0, 중복 제외 0; 전송 5/5, 생략 0, 잘림 없음. 이는 현재 창의 이벤트 커버리지이며 보유·관심종목 전수 커버리지를 뜻하지 않음.
- 본문은 BTC 데모지만 정규화 simulation_only=false. 충돌을 명시하고 전부 시뮬레이션 참고로만 처리.

| 이벤트 | 발생 KST | 연구상 변화 |
|---|---|---|
| stock_ai_agent:16262 | 10/18 06:33:27 | BTC 데모 숏 진입 기록 |
| stock_ai_agent:16263 | 10/18 08:06:27 | 데모 보호 조건 변경 |
| stock_ai_agent:16264 | 10/18 08:11:27 | 데모 보호 조건 재변경 |
| stock_ai_agent:16265 | 10/18 08:16:28 | 데모 보호 조건 확인 |
| stock_ai_agent:16266 | 10/18 08:57:27 | 데모 종료·정산 주장; 독립 확인 안 됨 |

실제 주식 신호와 기타 공식 근거는 이번 델타에 없다. 계좌·가격·손익 숫자는 실제 투자 근거로 전환하지 않는다. 첨부·전체 원문을 독립 검증한 것으로 해석하지 않는다.

balanced_external: 다섯 이벤트는 같은 채널의 한 데모 연속 기록이며 독립 다중 출처 합의가 아니다. LOW_LABELED로 제한한다. 종목 매핑이 없으므로 KR·US 종목 순위, thesis 신뢰도 및 위험 한도 내 비중은 변경하지 않는다. 후속 리서치에는 다섯 event key에 연결해 데모 분류 충돌 확인 우선순위를 높인다. 실행은 RESEARCH_ONLY이며 시장·계좌·위험 게이트를 유지한다.

다음 확인: 다음 성공한 sanitized 생산 또는 새/수정 이벤트 도착 시. 실제 종목 후보가 생기면 기업 IR·공시·거래소 근거와 최신 시세를 별도 검증한다. 데모 메타데이터 정합성 확인 전 실제 실행 근거로 사용하지 않는다.

COVERAGE_RECEIPT {"event_id":"prism:2fec84c1ac320f568f4fe7c15c252de0","status":"COMPLETE","window_events":5,"transmitted_events":5,"truncated":false,"new_events":5,"revised_events":0}

MOBILE_HANDOFF {"owner":"external_github_notification_pipeline","status":"PENDING_EXTERNAL_VERIFICATION","work_sent_notification":false}

로컬 보고서 저장과 Work ACK는 외부 전달 증명이 아니다. Telegram·Pages 전달 확인은 대기 중이다.