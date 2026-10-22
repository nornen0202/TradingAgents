# PRISM 연구 델타 · 2026-10-22

기준 10:36 KST · 소스 정상(OK). 생산 성공 09:58:45 KST, 30시간 신선도 한도 안. 현재 24시간 창 2건 전송/2건, 생략 0건·잘림 없음. 신규 2·정정 0·중복 제외 0.

- **위험 재검증 우선**: 09:30:18 KST 공지(stock_ai_agent:16469)는 조정 구간을 이유로 오전 분석을 쉬고 종가 확인 시간대 하루 1회 분석한다고 설명한다. 손절·청산 감시는 계속된다는 생산자 설명이다. 분석 축소 자체를 소스 실패로 보지는 않는다. 조정 판단과 실제 감시 작동은 독립 검증되지 않았다.
- **BTC는 데모 정산**: 04:02:26 KST(stock_ai_agent:16468)는 데모 종료 기록이다. 본문 정산 시각은 04:02:07 KST로 게시 시각보다 19초 앞선다. 실계좌 수익·주식 매매 근거로 사용하지 않는다.
- **과거 분류 변경 46건은 별도 미ACK**: 정제 아카이브 206개 정본을 ACK 해시와 비교해 현재 2건 외에 46건의 과거 변경을 확인했다. 이전 ACK 패킷과 비교한 변경 필드는 모두 simulation_only뿐이다. 현재 prepare의 24시간 창에 포함되지 않아 해당 정정을 ACK할 계약이 없다. 과거 날짜를 보존하고 현재 근거에서 제외하며 복구 대상으로 남긴다. 전체 백로그 완료를 의미하지 않는다.

balanced_external 가중치는 LOW_LABELED. 16469를 후속 KR·US 시장 종합의 research_priority에 연결해 공식 거래소 지수의 고점 대비 하락·종가·변동성 확인을 우선한다. 종목 매핑과 독립 검증 근거가 없어 순위·thesis confidence·위험 한도 내 포지션 크기를 변경하지 않는다. 16468의 데모 정산 가중치는 실제 주식 전략에 0이다. 실행은 RESEARCH_ONLY이며 시장·계좌·리스크 게이트를 유지한다. 위험 축소 매도 감시를 신규 매수 허용으로 해석하지 않는다.

종목별 매수·매도 신호 없음. NO_ACTIONABLE_DELTA(종목 전략). 원문은 정제된 요약이며 BTC 미리보기 일부가 생략되어 수익률을 재계산하지 않았다. 현재 이벤트·게시·커버리지 시각은 파싱 가능하고 미래가 아니며 24시간 안이다. 모델 표시는 CONFIGURED_NOT_RUNTIME_VERIFIED를 유지한다.

다음 확인: 다음 종가 분석 또는 새 정정·소스 실패 발생 시. 46건의 과거 분류 정정은 정확한 패킷 생성·ACK 경로가 확보될 때 처리한다. Telegram·Pages 외부 전달 영수증은 없어 전달 미확인이다.

COVERAGE_RECEIPT {"event_id":"prism:248caa4d8452c7a25467601f26c2e3f2","status":"COMPLETE","window_events":2,"transmitted_events":2,"truncated":false,"new_events":2,"revised_events":0}

MOBILE_HANDOFF {"owner":"external_github_notification_pipeline","status":"PENDING_EXTERNAL_VERIFICATION","work_sent_notification":false}