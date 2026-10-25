# 정형 판단의 입력 필드·보완 이력 검증

2026-10-26. 정상 KR 연구의 보존된 25개 판단을 다시 검토했다. PM 정규화 결과와 저장 decision은 같았고, 위험 축소18개·HOLD7개 및 손익비·손절·기한·지연 자료 사유가 있었다. 명시된 산술55개도 반올림 범위에서 일치했다. 이 사실이 투자 판단의 수익성이나 원래 LLM 응답의 모든 필드 존재를 증명하지는 않는다.

기존 경로는 LLM 입력을 `ensure_structured_decision_json`으로 정규화한 뒤 저장했다. 누락된 조건부 진입 필드는 이전 자료 호환을 위해 NONE/null로 보완된다. 보존된 정규화 JSON만으로는 모델이 이를 직접 명시했는지, 누락이 보완됐는지, bounded repair를 거쳤는지 확정할 수 없었다. 노드별 설명에는 조건부 계약이 있었지만 공통 JSON 예시에 두 필드가 빠진 것도 확인했다. 이번 공백이 관측된 모든 WAIT의 단일 원인이라고 하지 않는다.

## 새 분석에서 남기는 근거

공통 출력 예시에 기존 `conditional_entry_action`과 `conditional_entry_valid_until`을 명시한다. 근거가 있는 BULLISH WAIT·숫자 수준·매도 위험 충돌 없음·명시된 aware 유효기간을 갖춘 경우만 기존 STARTER/ADD 조건부 계약을 사용한다. 나머지는 NONE/null이며 예시로 특정 투자 결론을 강제하지 않는다. 기존 파서의 legacy 수용과 실행 엔진 검증은 그대로다.

새 ticker 그래프의 선택적 recorder는 다음을 기록한다.

- 정규화에 실제 전달한 메시지 content 텍스트의 UTF-8 SHA. HTTP 원문 바이트나 모델 내부 추론이라고 부르지 않는다.
- RM·Trader·PM 단계, 시도 번호와 실제 기록한 aware 시각, 두 필드의 누락/명시null/타입/형태 상태 및 기존 파서가 적용한 기본값 필드 목록.
- 최초 유효 판단·repair 성공·검증 거절·구조적 fallback·공급자 fallback·공급자 예외의 한정된 구분과 정규화 결과 SHA.
- 지역화 전 정규화 SHA와 최종 선택된 지역화 후 텍스트 SHA의 구분, 선택 단계 및 결합 근거.

지역화 결합은 실제 번역하는 `entry_logic/exit_logic/position_sizing/risk_limits/catalysts/invalidators/watchlist_triggers` 7개만 제외한 canonical projection을 별도로 사용한다. 숫자 가격·volume·confirmation·만료·위험 계획이 달라지면 이 hash도 달라진다. 제외 필드와 scope를 영수증에 명시하며 전체 문장 번역 충실성·가격의 외부 정확성·주문 승인 증명으로 쓰지 않는다. 정확한 정규화 텍스트가 같을 때와 이 제한된 projection만 같을 때도 구분한다. 후보가 여러 개면 임의로 하나를 선택하지 않는다.

## 경계와 실패 동작

원래 반환 tuple·LLM 호출 수·3회 repair 예산·파서·투자 판단과 graph는 바꾸지 않는다. recorder 미활성 시 기존 동작을 유지하며 기록 실패·상한 초과·결합 실패는 UNVERIFIED로 남긴다. 추적 실패 때문에 모델을 추가 호출하거나 BUY를 만들지 않는다. ticker별 ContextVar와 공유 lock으로 복사된 child context를 묶고, 실행 종료 시 reset한다. 최대96개 event·입력 텍스트 상한50만자를 적용한다.

원시 응답·프롬프트·Tool 인자·계좌·임의 context 문자열·예외 개인문구를 새로 저장하지 않는다. 새로 실제 실행한 analysis/error에만 versioned metadata를 추가한다. PR441의 재사용 원문·artifact set·hash·원래 승인 clock은 그대로다. 이전 raw 응답을 복원하거나 오래된 WAIT를 소급하여 ‘모델이 명시했다’고 표시하지 않는다. 영수증은 항상 `execution_authorized=false`다.

외부 API 없는 Mock는 legacy 누락과 명시 NONE/null, 근거 있는 조건부 판단, malformed·aware/naive 시각, 기존 첫 JSON 후보 선택, repair/fallback·호출 수 보존, 복사 context 동시성·다른 ticker 격리, reset·sink 실패·overflow, 원문 비저장 및 지역화 결합 범위를 검증한다. 새 성공/실패 JSON의 저장도 별도 fixture로 확인한다. 전용 및 기존 retry42검사와 독립 표적10검사는 범위가 겹치므로 합산하지 않는다. 최종 정확 head CI·배포·새 정상 실행에서의 실제 metadata 채택은 별도 증거다.

최신 병합 main 통합 후 root는 새 provenance·runner와 기존 retry·정형 schema·지역화·batched 지역화·엄격 연구 재사용의 관련 7파일197검사(18.57초), Ruff·diff를 확인했다. 앞선 표적 검사 수에 더하지 않는다.
