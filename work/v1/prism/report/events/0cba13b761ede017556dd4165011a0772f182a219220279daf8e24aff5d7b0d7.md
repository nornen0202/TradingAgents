# PRISM 연구 델타 · 2026-10-30

신규 21건. ATI·BMO·PURR 미진입 검증 우선순위 상향. 시뮬레이터 위험 축소는 실제 주문과 분리; 과거 63건 미처리 유지.

- 소스 정상: 생산 성공 08:05:12 KST, 검증 10:38:53 KST. 사건 범위 02:52:55–04:56:55 KST, 모든 전송 사건·게시·신호 시각이 최근 24시간 이내이며 미래 시각 없음.
- ATI·BMO·PURR: 관심 이후 미진입. 공식 추세·재무·손익비 확인을 다음 US 연구의 우선 과제로 올림.
- LITE 매수 후 매도, LLY 매도, HALO·BKH 손절선 상향은 가상 포트폴리오 맥락. 실제 보유·확정 손익·현재 매도 지시로 해석하지 않음.
- 현재 창 21/21건, 신규 21·정정 0·동일 제외 0·전송 생략 0, 잘림 없음. 전체 과거 처리는 미완료: 현재 패킷 밖 신규 18·정정 45건은 ACK하지 않음.

## 종목별 연구 영향

| 종목 | 연구 영향 | 근거 event key |
|---|---|---|
| ATI | 관심 뒤 미진입. 하락하는 50일선 아래라는 출처 주장을 공식 조정주가와 대조하고 추세 회복 여부 확인을 우선한다. | stock_ai_agent:16913, stock_ai_agent:16907, stock_ai_agent:16901, stock_ai_agent:16900 |
| BMO | 관심 뒤 미진입. 최근 두 분기 영업흑자·재무 건전성이 검증되지 않았다는 출처 주장을 실제 공시와 대조한다. 원문 목표값이 관측가 아래인 충돌도 있어 수치 사용을 보류한다. | stock_ai_agent:16914, stock_ai_agent:16908, stock_ai_agent:16902, stock_ai_agent:16900 |
| PURR | 관심 뒤 미진입. 손익비 하한 미달 주장과 HYPE 가격 의존·스테이킹 수익 구조를 공식 공시로 검증한다. 높은 원문 점수는 신뢰도 상향 근거가 아니다. | stock_ai_agent:16915, stock_ai_agent:16909, stock_ai_agent:16903, stock_ai_agent:16900 |

동일 채널의 관심·차트·미진입은 독립 다중 출처가 아니다. balanced_external LOW_LABELED로 공식 위험 검증 우선순위만 상향하고 순위·thesis confidence·비중은 상향하지 않는다. PDF 16904–16906은 보관 본문이 없어 확인 근거로 쓰지 않으며 SBET·BLSH는 비교기업 언급만으로 신규 후보에 편입하지 않는다.

## 시뮬레이션과 분류 주의

16898 LITE BUY는 자체 simulation_only=false이나 16899 가상 보유, 16916 보유 점검, 16917 시뮬레이터 매도와 연결된다. 이를 실제 매수 추천으로 승격하지 않는다. 16912 LLY 매도는 시뮬레이터 성과이며, 16910 BKH·16911 HALO 조정 역시 16918 가상 보유와 연결된 연구 참고다. 포트폴리오 스냅샷의 HALO·CRGY·FRSH·BKH·BP·QCOM 및 과거 LLY·LITE는 사용자 보유 목록이 아니다. 다중 종목 가격·손절·목표와 성과는 실제 전략에 전사하지 않는다.

## KR·US 인계와 미처리

US는 ATI 추세, BMO 공시 재무, PURR 디지털자산 노출·손익비를 공식 자료로 확인한 후 재평가한다. KR에 직접 매핑된 신규 근거는 없다. 위험 축소 매도 연구는 신규 매수 자금·진입 판단과 별도로 유지한다. 현재 실행 권한은 없으며 시장·계좌·리스크·현재 가격의 모든 게이트를 재확인해야 한다.

정본 전체 338개 대조 결과 현재 창 밖 미열람 신규 18건과 정정 45건이 남았다. prepare는 24시간 창만 전송하므로 해당 과거 이벤트를 안전하게 묶을 정본 패킷 지원 전까지 PENDING_CANONICAL_BACKLOG_PACKET을 유지한다. 이번 ACK는 전송된 21건에만 적용하며 전체 완료를 뜻하지 않는다.

다음 확인: 다음 정상 생산 이벤트 또는 독립 복구 운영자 확인. 현재 첫 이벤트는 2026-10-31 02:52:55 KST에 24시간 경계를 넘음. 과거 18 신규·45 정정은 canonical backlog packet 지원 전까지 ACK 금지.

COVERAGE_RECEIPT {"event_id": "prism:ff3590b4b1b6cb0657dd3705c4f58921", "status": "COMPLETE", "window_events": 21, "transmitted_events": 21, "truncated": false, "new_events": 21, "revised_events": 0}

MOBILE_HANDOFF {"owner": "external_github_notification_pipeline", "status": "PENDING_EXTERNAL_VERIFICATION", "work_sent_notification": false}

로컬 발행·ACK는 외부 Telegram 또는 Pages 전달 완료를 뜻하지 않는다. 외부 영수증은 확인되지 않았다.