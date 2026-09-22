# 제품 경험·성능·운영 종합 검토 — 2026-09-22

검토 대상은 PC/모바일 투자 전략, 공개 리서치와 계좌 현황, 정적 사이트 생성, 예약 실행과 복구·알림, 분석/모의매매의 검증 경계다. 시작 기준은 fork/main의 f7ca9734이며, 작업 중 병합된 #285의 모의매매·설정 보강도 통합했다.

**평가:** 데이터 출처·유효기간·실행 조건을 분리하는 기반과 테스트 범위는 잘 갖춰져 있다. 가장 큰 개선 여지는 많은 종목을 찾는 과정, 갱신 중 맥락 보존, 누락값의 정확한 표현, 가벼운 예약 실행 게이트의 실제 배포 호환성이다. 임의의 점수나 수익률 개선 주장은 사용하지 않았다.

## 확인한 문제와 적용 결과

| 영역 | 확인한 문제 | 적용 |
|---|---|---|
| 탐색 | 핵심/보유/관심/신규 구분만 있고 검색·정렬이 없음 | 종목명·티커·업종 검색, 우선순위/이름/등락률 정렬, 결과 수와 초기화 |
| 탐색 상태 | 만료 시 전체 화면 재생성이 시장·필터·펼친 상세를 초기화 | 만료 때 카드만 갱신하고 시장·검색·정렬·상세·키보드 초점 유지 |
| 공유/복원 | 시장 선택 후 주소가 그대로여서 새로 열 때 KR로 돌아감 | market/group/q/sort를 URL에 반영. 임의의 값은 허용 목록으로 제한 |
| 오류 복구 | 요청 실패 후 사용자에게 재시도 버튼이 없음 | 15초 연결 제한, 재시도, 중복 요청 억제, 갱신 실패 시 이전 데이터임을 표시 |
| 첫 화면 | 설명 영역이 전략 탐색보다 앞에 있고 모바일 통계 문구가 잘게 줄바꿈 | 설명은 아래의 접힌 상세로 이동, 안내 축약, 모바일 통계 3열 |
| 접근성 | 본문 건너뛰기와 명시적 초점 표시 부족, 계좌 탭의 화살표 조작 누락 | skip link, focus-visible, 44px 탐색 버튼, 결과 live region, 탭-패널 연결 및 방향키/Home/End |
| 데이터 정확성 | JS Number(null)가 0이어서 누락 가격/신뢰도/커버리지 값이 정상값처럼 보일 수 있음 | 숫자·비어 있지 않은 숫자 문자열만 허용. 없는 값은 '-' 표시, 누락 커버리지는 실행 가능 승격 차단 |
| 브라우저 보안 | 엄격한 CSP 아래에서 신뢰도 막대의 inline style이 차단됨 | 접근 가능한 native meter로 표시 |
| 초기 성능 | 보이지 않는 반대 시장의 카드까지 생성, Work 전략을 반복 선형 탐색 | 선택한 시장만 최초 생성, 시장별 전략 인덱스 재사용 |
| 사이트 생성 | 손상된 run/status JSON 하나가 전체 게시를 중단 | 유효한 리포트는 계속 생성하고 손상 기록은 경고. 경로와 불일치하는 run ID 제외 |
| 홈페이지 | 카드 링크 판단에 private portfolio JSON들을 전부 읽음 | 상태 파일 존재만 확인해 불필요한 읽기·파싱 제거. 공통 메뉴와 중복 CTA 정리 |
| 휴장일 검사 | status.reason 누락, 키워드 전용 함수의 잘못된 호출, 환경변수 별칭 불일치 | 실제 반환 타입과 호출을 맞추고 워크플로 변수/타임아웃/자격증명 별칭 지원 |
| 예약 게이트 시작 | 저장소 경로와 CLI 의존성이 없는 hosted runner에서 import 실패 가능 | 경로 초기화, scheduled 패키지의 CLI/LLM import 지연 |
| 휴장일 캐시 | 어제 예측을 오늘 응답과 합치면 누락 일자가 오늘 확인된 것처럼 승격 | 조회한 날짜가 실제 응답에 있을 때만 저장. HTTP 응답 닫기, 원자적 파일 교체 |
| Actions 캐시 | US 작업이 복원한 어제 파일을 오늘의 불변 캐시 키로 저장할 수 있음 | 당일 KR 결과와 조회 날짜를 확인한 경우에만 cache save |
| 장애 운영 | 매 요청마다 바뀌는 GitHub ID 때문에 동일 장애가 새 사건으로 분류됨 | Python 알림·watchdog와 PowerShell 복구의 서명에서 가변 요청 ID 제거 |
| 복구 | dispatch의 모든 HTTP 오류를 일시 장애로 처리 | 일시 네트워크/429/5xx와 인증·설정 오류를 구분, 휴장·캘린더 장애 보류 사유 기록 |
| 작업 폴더 | 첨부 사진·진단 다운로드·생성 리포트가 소스 변경에 섞임 | 해당 로컬 출력 경로를 Git 제외. 파일은 보존 |

## 외부 프로젝트·서비스 비교

공식 문서와 공개 저장소의 관련 설계를 조사했다. 외부 서비스를 설치·결제하거나 전체 코드를 감사한 것은 아니다. 아래 적용은 우리 데이터와 정적 배포 구조에 맞게 직접 구현한 것이며 외부 소스 코드를 복제하지 않았다.

| 출처 | 참고점 | 채택/판단 |
|---|---|---|
| [TradingView Watchlists](https://www.tradingview.com/support/solutions/43000745825-mastering-the-tradingview-watchlists/) | 관심 종목의 검색, 그룹, 지표 정렬과 상세 진입 | 기존 역할 필터에 검색·정렬·결과 피드백 추가. 수정 시세가 없는 차트나 가격 알림을 새로 만들지는 않음 |
| [OpenBB Widget 구조](https://docs.openbb.co/workspace/analysts/widgets/overview), [Dashboard](https://docs.openbb.co/workspace/analysts/dashboards) | 데이터의 출처·설명·상태를 분석 단위와 함께 제공 | 출처/분석 시각/현재 실행 상태를 유지하면서 탐색을 앞에 배치. 별도 위젯 서버 없이 현재 카드 확장 |
| [Grafana URL variables](https://grafana.com/docs/grafana/latest/visualizations/dashboards/build-dashboards/create-dashboard-url-variables/) | 선택한 대시보드 조건을 주소로 복원 | 시장·검색·필터·정렬 URL 동기화. API 키나 계좌 식별정보를 상태에 추가하지 않음 |
| [Ghostfolio](https://github.com/ghostfolio/ghostfolio) | 포트폴리오 중심의 자산·성과 탐색과 공개/비공개 경계 | 기존 공개 계좌 계약 유지, 탭 접근성 보강. 자체 계좌 원장·성과 엔진이 있어 전체 제품 도입의 이점은 제한적 |
| [Freqtrade Backtesting](https://www.freqtrade.io/en/stable/backtesting/), [Strategy Quickstart](https://www.freqtrade.io/en/stable/strategy-101/) | 재현 가능한 결과와 실시간 dry-run을 구분 | 기존 비용/슬리피지/다음 시가 체결, 모의매매 검증 체계를 검토. 화면의 실행 상태가 누락 수치로 승격되지 않도록 보강 |
| [한국투자증권 공식 휴장일 조회 예제](https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/chk_holiday/chk_holiday.py) | BASS_DT, CTCA0903R, opnd_yn, 과도한 호출 방지 | 공식 개장 여부와 당일 캐시를 우선 사용하고 응답 불확실 시 자동 실행 보류 |
| [W3C Tabs Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/), [WCAG 2.2](https://www.w3.org/TR/wcag/) | 키보드 조작, 초점, 상태 전달 | 계좌 탭 연결·방향키, focus-visible, 검색 결과 알림. 전체 WCAG 적합성 인증을 의미하지 않음 |
| [web.dev DOM와 상호작용](https://web.dev/articles/dom-size-and-interactivity), [content-visibility](https://web.dev/articles/content-visibility) | 불필요한 DOM 및 렌더 작업 줄이기 | 반대 시장 DOM 생성을 지연. CSS containment로 상세/인쇄를 복잡하게 만드는 방식은 이번에 사용하지 않음 |

정량 전략과 체결 엔진의 외부 비교는 같은 날 최신 main에 반영된 [외부 투자 프로젝트 검토](external_trading_review_20260922_ko.md)와 [전략 감사·모의매매](strategy_audit_and_paper_trading_ko.md)에 별도로 정리돼 있다. UI 개선과 투자 수익 검증은 구분한다.

## 성능 측정

로컬 Windows, Python 3.14.3, Chrome 153.0.8010.48 headless, localhost 정적 서버에서 KR 100개 + US 100개의 동일 합성 데이터를 사용했다. 1440px 화면으로 기준 버전/수정 버전을 각각 5회 열었다. 카드 DOM 생성 뒤 두 animation frame이 지난 시점을 측정했다. 순서 고정·작은 표본의 개발 환경 측정이며 네트워크/LCP/INP/실서비스 SLA 측정은 아니다.

| 지표 | 기준 버전 | 수정 버전 |
|---|---:|---:|
| 초기 생성 카드 | 200 | 100 |
| 초기 DOM 요소 | 15,719 | 7,802 |
| 관찰 시점까지 중앙값 | 142.9ms | 100.8ms |

초기 카드 수 50%, DOM 요소 약 50.4% 감소를 확인했다. 시간은 이 실험에서 약 29.5% 짧았지만 사용자 기기별 개선율을 보장하지 않는다. Work 조회 인덱스는 종목 수에 따라 반복 검색이 늘어나는 구조를 제거한다. 서버 생성에서는 홈페이지의 private JSON 읽기를 없앴으며 실제 아카이브 전체 생성 시간의 개선율은 측정하지 않았다.

## 미커밋 변경 통합

17개 수정 파일과 휴장일 모듈/테스트, Windows 리소스 검사 파일을 최신 main과 3-way 비교했다. 원본 패치와 파일은 로컬 별도 백업에 보존했다.

- 텔레그램 종목 카드 중단, Work packet 보강, 페이지 스냅샷 테스트, PRISM/Windows 리소스 보강은 이미 main에 반영된 부분을 유지했다.
- 신규 휴장일 검사·서명 정규화는 위 오류를 고쳐 반영했다.
- 중복 삽입된 Pages 리소스 검사 단계를 제거했다. 최신 main의 시간 제한과 기존 메모리/디스크 사전 검사를 유지했다.
- 수동 실행 입력에만 적용된 동시 작업 수 1 설정은 자동 실행과 일치하지 않았다. 최신 main의 기본 4 및 기존 자원 보호를 유지하고, 명시적 입력으로 1을 선택할 수 있다.
- 첨부·임시 파일과 생성 리포트는 소스 변경으로 게시하지 않는다.

## 검증과 남은 범위

정적 검사와 워크플로 YAML 검증 통과, 전체 Python 테스트 **1,159개 통과·1개 건너뜀**(subtest 78개), 실제 Chromium 모바일 360/390/430px 레이아웃 통과, 모바일 3종·PC 1440px의 상호작용 **각 33개 검사 통과**를 확인했다. 재현 명령:

~~~powershell
python -m ruff check . --select E9,F63,F7,F82
python -m pytest -q
$env:PYTHONPATH='.'
python .github/scripts/mobile_layout_regression.py
python .github/scripts/strategy_interaction_regression.py
~~~

브라우저 회귀는 검색, 숫자 정렬과 누락값, 빈 결과 복구, URL 선택, 지연 생성, 만료 시 상세·초점 보존, 연결 실패·재시도, HTML 이스케이프, 커버리지 누락 시 실행 차단을 확인한다. CI에도 추가했다.

남은 검증은 실제 KIS 자격증명과 운영 네트워크에서의 다음 예약 실행, Safari/Firefox 및 화면 낭독기, 대형 실제 아카이브의 장시간 빌드 측정이다. 백테스트 수익성이나 새 자동 매매 전략을 이번 UI 변경의 효과로 해석하지 않는다. 긴 생성 모듈의 템플릿/자산 분리는 다음 유지보수 후보이며 이번에는 배포·패키징 경로를 유지했다.
