# 예약 분석 감사 — 2026-09-27

## 판정과 검토 범위

예약 실행·답변 발행은 진행됐지만, 이것을 최신 입력을 사용한 분석 성공으로 볼 수 없었다. **9월 25일 23:16 KST 미국 Work 보고서는 9월 22일 11:10 EDT 시세를 사용했다.** 사용자가 발견한 날짜 차이는 실제 archive에서도 확인된다.

- ChatGPT 웹 대화 `미국 주식 투자 전략`, `주식 투자 전략 제안`: 9월 14~25일 시장별 답변 10개, 총 20개 검토. 미국 9월 15·16일 답변은 도구의 20,000자 제한 때문에 끝부분이 잘려 있어 전수 원문 검토로 주장하지 않는다.
- 로컬 Work: KR·US 최근 6개씩 총 12개 정본, immutable packet, producer manifest·decision bundle 및 공개 Pages 대조.
- GitHub Actions의 작업별 성공·실패·건너뜀과 실제 시작·완료 시각 확인. Workflow 전체의 녹색 `success`만으로 분석 성공을 판정하지 않았다.
- 금융사실은 Fed 9월 성명과 NVIDIA FY27 Q2 원문을 표본 검증했다. 모든 기업 공시·가격을 다시 수집한 투자보고서는 아니다.

## 확인된 원인

| 문제 | 확인한 증거 | 영향·조치 |
|---|---|---|
| 보고서 발행과 입력 갱신 혼동 | US 9/24 23:17, 9/25 23:16 Work 모두 9/22 11:10 EDT 입력 | 원분석 거래일·시세 범위·계좌 시각·발행 시각을 별도로 표시하고 source receipt를 발행 시 검증 |
| producer 완료 전 Work 실행 | `20260925T212622_github-actions-us`: 9/25 21:26 시작, 9/26 00:04 완료. 23:10 예약이 먼저 실행됨 | 해당 시점에는 새 full run이 아직 없었음. 보고서를 최신 입력 분석이라고 표현하지 않도록 계약 강화. 기존 후속 01:10·03:10 예약은 유지 |
| 분석 실패 후 성공처럼 보이는 건너뜀 | [9/23 KR 실패](https://github.com/nornen0202/TradingAgents/actions/runs/35801837937)는 Windows resource guard에서 중단. [후속 run](https://github.com/nornen0202/TradingAgents/actions/runs/35803856348)은 gate 성공, 실제 분석·배포는 skipped | 9/23 생산 공백 확인. 디스크 임계값은 이미 [PR #289](https://github.com/nornen0202/TradingAgents/pull/289)에서 수정됨. 같은 수정 중복 적용 없음 |
| 휴장과 장애의 혼동 가능성 | XKRX 캘린더상 9/24~26 휴장, 9/23은 거래일 | KR 9/24~25 새 장중자료가 없는 사실과 9/23 생산 실패를 구분. 오래됐다는 이유만으로 휴장일 생산 실패라고 단정하지 않음 |
| overlay ID를 원분석 ID처럼 전달 | US 최신 bundle의 analysis_source_run_id는 직전 overlay를 가리킴 | 명시적 overlay 부모를 따라 full run을 추적하고 추적 불가·순환·다른 시장은 UNVERIFIED |
| 실행 만료가 투자 논지를 지움 | 9/26 23:20 보고서 26개 thesis가 모두 RESEARCH. producer에는 원결정이 남아 있음 | DATA_CHECK 행의 thesis를 같은 manifest의 원결정에서 보존. 현재 실행은 재확인 상태 유지. 명시적 SELL/REDUCE 등 기존 방향을 덮어쓰지 않음 |
| 매수 코드 매핑 누락 | BUY_NOW·BUY_ON_CONFIRMATION이 Work stance 매핑에 없어 RESEARCH로 변환 | 매수 논지로 매핑. 실행 준비도는 별도 유지 |
| 잘못된 입력 시각 허용 | 누락·파싱 실패·시간대 없음·미래 시각이 만료 판단을 피할 수 있음 | 해당 행 실행 차단. 페이지 생성 시각으로 시세 유효시간을 만들지 않음 |
| 파일 수정일로 최신 run 선택 | mtime 정렬 후 첫 READY에서 탐색 종료 | restore·재게시로 과거 파일이 최신이 될 수 있어 producer 시각으로 정렬 후 선택 |
| 웹 추출 실패 | 웹 답변들이 JSON 접근 실패 후 오래된 HTML에 의존 | JavaScript 없는 `/work/v1/{market}/status.html`, 보고서 `latest.html`·`latest.md` 제공 및 llms.txt에 연결 |
| 실제 예약과 저장소 prompt 불일치 | 설치된 KR·US 예약 prompt에는 exact Pages handoff 단계가 없음 | 저장소 정본 prompt와 실제 예약 정의를 동기화. 일정·모델 유지 |
| 새 YouTube 생산 장애 | [9/26 실패](https://github.com/nornen0202/TradingAgents/actions/runs/36280941117): Codex alias의 Path.exists에서 PermissionError | 파일 검사도 예외 처리, 실행 검증 timeout, 실제 버전별 설치 경로 fallback 추가. 동일 결함이 있는 KR·US workflow도 수정 |

## 답변 내용의 품질 문제

1. **서로 다른 시각을 결합한 현금 잔차.** 9/25 답변은 오래된 계좌수량을 새 가격으로 재평가하고 `총자산−증권`을 현금성 잔차로 사용한다. 총자산도 같은 시각으로 조정됐다는 reconciliation이 없으면 현금으로 확정할 수 없다. 현금·증권·부채·미결제를 각각 확인하고 불명확한 수량·비중은 가상 시뮬레이션으로 한정하도록 보완했다.
2. **조건과 수량의 불일치.** AAPL 상세에는 조건부 1주 축소와 증감 `0주`가 함께 있다. ETN 3주 중 1주 축소 시 비중은 단순 계산상 6.92%→약 4.61%로, 제시한 목표 5~6% 아래다. 정수 거래단위와 목표 범위의 불일치를 설명해야 한다.
3. **취소 조건이 위험 조건을 무력화.** GOOGL의 `공식 악재 없음`이라는 넓은 취소 조건은 기술적 이탈과 동시에 참일 수 있다. 발동·취소의 우선순위와 AND/OR를 명시해야 한다.
4. **미확인과 0% 혼동.** 자료 접근 실패만으로 데이터 자체의 충족률을 0%라고 단정할 수 없다. 생산 데이터 없음, 모델이 미열람, 자료가 만료됨을 구분하도록 보완했다.
5. **제약 미충족 시나리오 표현.** 약 230만원 추가안의 AI·전력 54.26%는 임시 목표 50%를 충족하지 않는다. 일부 집중 개선과 모든 한도 충족을 구분해야 한다. 비용을 제외한 값은 비용 후 실행안으로 승격할 수 없다.
6. **신뢰도의 의미 불분명.** 사업 논거의 신뢰도가 높더라도 현재 계좌·미시구조 자료의 신뢰도까지 높다는 뜻은 아니다. 사업·데이터·실행을 구분하도록 보완했다.
7. **출처의 범위 불일치.** 환율 페이지 하나를 유가·금리 근거까지 포괄하는 인용으로 쓰지 않도록 숫자별 직접 출처를 요구했다.
8. **유지할 적절한 부분.** 미확인 주문자료를 발명하지 않은 점, 현재 주문을 보류한 점, 테마 집중과 통계적 상관계수를 구분한 점, 성과자료 없이 우월한 수익률을 주장하지 않은 점은 유지한다. TSM 1주 축소 비중과 MPWR 제외 테마 비중 산식 자체는 제공된 가정 안에서 대체로 일치한다. 문제는 입력의 확정성과 실행 가능성이다.

Fed의 25bp 인상·3.75~4.00%는 [공식 성명](https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm), NVIDIA의 매출·데이터센터 매출·가이던스는 [공식 실적](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-second-quarter-fiscal-2027)과 표본 대조했다. 이 수치들을 단지 이례적이라는 이유로 오류 처리하지 않았다.

## 운영 검증과 재현

```powershell
python -m tools.audit_work_freshness --archive-dir C:\TradingAgentsData\archive --output .runtime/freshness-audit.json
python -m pytest -q
python .github/scripts/mobile_layout_regression.py
python .github/scripts/strategy_interaction_regression.py
```

감사 명령은 자료를 읽기만 하며 prepare·publish·ACK·주문을 실행하지 않는다. 과거 보고서를 소급 수정하지 않는다. 다음 예약은 v10 입력 계약을 적용하고, 기존 보고서는 발행 당시 참고자료로 보존한다. 공개 source receipt에는 계좌 식별자·보유집합·계좌 시각을 넣지 않으며, 개인 전략 화면은 기존 공개 범위 내에서 계좌 기준시각만 별도로 표시한다.

로컬 Scheduled task와 공개 웹 재분석 대화는 다른 실행 경로다. 로컬 prompt를 고쳐도 이미 저장된 별도 클라우드 예약 prompt가 자동 변경되는 것은 아니다. 따라서 로컬 KR·US 예약을 정본과 동기화한 뒤, ChatGPT 예약 UI의 `TradingAgents 미국 투자전략 23시30분`과 `TradingAgents 국내 투자전략 13시`에도 신선도·계산 검증 절을 직접 저장하고 재조회해 일치를 확인했다. 제목·반복 일정·활성 상태는 유지했다. 다음 실제 예약 답변의 품질까지 관측한 것은 아니므로 설정 적용·코드 검증과 향후 모델 출력의 정확성을 구분한다. [공식 Scheduled tasks 안내](https://learn.chatgpt.com/docs/automations)
