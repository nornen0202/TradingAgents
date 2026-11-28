# PRISM 리서치 델타 · 11월 28일

원천 정상. 최근 24시간 신규 15건, 정정 0건. INFY·AMD·DV 공식 데이터 대조를 우선합니다. 실행 가능한 변화 없음.

- **INFY** · 눌림 후 회복을 근거로 비중을 늘렸다는 원천 기록이 있습니다. 당시 가격 구간과 거래량을 거래소 기준 ADR 조정 일봉에서 먼저 확인합니다. `stock_ai_agent:18121`
- **AMD** · 관심 신호 뒤 진입을 보류했습니다. 원천의 관측 가격이 서로 달라 확정 종가와 5일 추세 확인을 우선합니다. `stock_ai_agent:18123`, `stock_ai_agent:18126`, `stock_ai_agent:18131`, `stock_ai_agent:18134`
- **DV** · 관심 신호 뒤 진입을 보류했습니다. 확정 거래량과 공시 기반 상대 밸류에이션으로 보류 근거를 점검합니다. `stock_ai_agent:18123`, `stock_ai_agent:18125`, `stock_ai_agent:18130`, `stock_ai_agent:18133`

### 범위와 근거

- 수집 성공 11월 28일 08:08:12 KST. 이벤트 범위 11월 28일 02:46:32–04:56:04 KST, 원천 분석일 11월 27일 미국 현지. 최근 24시간 전송 15/15, 동일 해시 제외 0건, 생략 0건, 잘림 없음.
- **주식 리서치** · AMD·DV의 관심에서 미진입으로 이어진 기록은 같은 채널의 순차 관측입니다. 독립 확인 전 `balanced_external`의 `LOW_LABELED`를 적용해 공식 근거 확인 순서에만 반영합니다. ANT는 거래소의 종목 식별과 상장 여부 확인 전 종목 판단에서 보류합니다. `stock_ai_agent:18124`, `stock_ai_agent:18132`
- **시뮬레이션** · INFY 비중 확대와 INFY·COST·AAPL·VRSN·PANW·AS 가상 보유는 시뮬레이터 기록입니다. 다종목 스냅샷의 목표가·손절가와 가상 손익은 후속 전략에 반영하지 않았습니다. `stock_ai_agent:18122`, `stock_ai_agent:18135`
- **기타 자료** · PDF 3건은 패킷에서 본문을 확인할 수 없어 근거 가중에서 제외했습니다. `stock_ai_agent:18127`–`stock_ai_agent:18129`
- **KR·US 인계** · KR 연구 우선순위를 조정할 근거가 없습니다. US에는 INFY·AMD·DV 검증을 넘깁니다. 투자 논지 순위·신뢰도·비중과 실행 적격성은 이번 연구 근거로 조정하지 않았습니다.
- **과거 미처리** · 현재 24시간 범위 밖의 미처리 130건과 변경 45건은 정본 과거 패킷을 기다립니다. 11월 25일 미처리 19건은 미처리 130건에 포함됩니다.

다음 US 브리핑 전에 거래소 기준 조정 일봉·확정 거래량과 필요 시 SEC·기업 IR을 확인합니다. 첫 이벤트는 11월 29일 02:46:32 KST부터 24시간 범위를 벗어납니다.

COVERAGE_RECEIPT {"event_id":"prism:2227c300fb17501fc264905df35a2a16","status":"COMPLETE","window_events":15,"transmitted_events":15,"truncated":false,"new_events":15,"revised_events":0}

MOBILE_HANDOFF {"owner":"external_github_notification_pipeline","status":"PENDING_EXTERNAL_VERIFICATION","work_sent_notification":false}