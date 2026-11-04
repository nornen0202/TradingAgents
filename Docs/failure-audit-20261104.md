# 누적 실패 점검 및 수정 — 2026-11-04

## 확인 범위

- `nornen0202/TradingAgents`에 보관된 실패 Actions 실행 482건
  (2026-04-05~2026-11-04)의 실행 및 job/실패 단계 메타데이터를 전부 조회했다.
  조회 실패는 0건이며 job/실패 단계 조합은 81개였다. 오래된 로그가 만료된
  실행은 메타데이터만 확인할 수 있으므로 개별 원인까지 확정했다고 보지 않는다.
- 로컬 archive의 `attempt.json` 2,180개를 조사했다. SUCCESS 2,084개,
  RUNNING 3개, 실패 또는 부분 실패 93개였다. 실패 93개 중 30개에 terminal
  `run.json`이 있었고 여기서 실패한 ticker 기록 348개를 확인했다. 나머지
  63개는 terminal manifest가 없으며 기존 attempt와 launcher 로그를 보존했다.
- 최근 KR/US full 및 overlay, 연구 갱신, Pages 게시 로그, 기존 사고 보고서,
  Windows 러너 설치와 GitHub annotation을 대조했다. 과거 실패 결론을
  성공으로 바꾸거나 원본·정산·주문 원장을 수정하지 않았다.

## 수정 1: 연구 완료와 overlay 시작 사이의 경쟁

실제 KR `20261104T105106_local-freshness-kr-overlay`는
10:51:06.503676 KST에 시작했지만 10:51:23.928477 KST에 완료된
`20261104T101545_local-thesis-refresh-kr`의 immutable reference 90개를
저장했다. 이후 `ResearchArtifactStore.make()`의 기존 시점 검증에서
`Referenced source was unavailable when overlay started`가 발생했다.
US에도 동일한 예외와 refresh 한도 소진이 기록돼 있었다.

원인은 source/revision 탐색과 snapshot 생성이 overlay의 시작시각 대신
각 호출의 현재시각을 사용한 것이다. 긴 탐색 도중 새 연구가 끝나면 당해
overlay가 이를 채택할 수 있었다.

- 실행 시작시각을 bootstrap, full/revision 선택, immutable store에 전달한다.
- 기준시각 이후 완료한 full/revision은 다음 실행부터 선택할 수 있다.
- 완료시각이 누락·잘못된 형식·naive·역전·미래인 source를 선택하지 않는다.
- 기존 overlay에 그 시작보다 늦게 완료된 reference가 있으면 해당 source를
  제외하고 유효한 부모/full/revision 경로를 사용한다. 원본 bytes와 시각은 보존한다.
- 명시적으로 전달된 source도 복사/쓰기 전에 같은 검사를 받는다. 자료가
  없으면 중단한다. reference의 해시·정체성·계보 검증은 그대로 유지한다.

오프라인 fixture는 실제 17초 순서를 재현하며, 이후 실행에서의 정상 채택,
잘못된 날짜, 빈 후보, 기존 invalid chain 제외, 일반 복사와 lightweight
snapshot 모두를 검증한다.

## 수정 2: 온라인 표시 뒤에 숨은 러너 설치 손상

PRISM 실행 [41761785883](https://github.com/nornen0202/TradingAgents/actions/runs/41761785883)의
`prepare_self_hosted_runner`는 단계 0개 상태에서 통신 단절로 실패했다.
Listener 로그에는 Worker 기동 요청이 있지만 실제 Worker 시작 기록이 없었다.
GitHub의 `online`, `busy=false`만으로 작업 실행 가능성을 판단할 수 없었다.

실제 `C:/actions-runner/bin`은 `bin.2.338.0`을 가리키며 Worker 실행 파일,
DLL, runtime config 등을 포함한 파일 194개가 누락돼 있었다.

- [공식 v2.338.0 배포본](https://github.com/actions/runner/releases/tag/v2.338.0)의
  Windows x64 ZIP SHA-256
  `f48e0750a21812bca5f82de5f7f5aeae71abee647fab5a582f1742d07eba455f`를 확인했다.
- 기존 bin 파일 74개가 모두 동일 배포본과 일치함을 먼저 확인한 뒤 누락된
  194개만 복원했다. 기존 파일은 덮어쓰지 않았다. 복원 후 bin 268개와
  externals 4개가 모두 배포본과 일치했다.
- Listener `--version`은 `2.338.0`을 반환했고 Worker도 .NET 진입점까지
  기동했다. 무인자 Worker probe는 예상한 인자 검증 오류(exit 1)를 반환했다.
  이는 실제 PRISM 수집 완료의 증거와는 구분한다.
- keepalive는 Worker 실행 파일/DLL/deps/runtimeconfig가 누락됐으면
  서비스가 Running이어도 정상이라고 보고하지 않고 설치 손상을 알린다.

별도로 저장공간 정리 코드가 version 폴더의 수정시각 순서만으로 오래된
backup을 골라, 실제 `bin`/`externals` junction의 활성 대상을 삭제할 수 있는
결함을 확인했다. 활성 alias를 삭제 직전에 다시 해석하여 활성 대상과 그
상위 폴더를 보존한다. alias가 누락됐거나 확인할 수 없거나 경계 밖이면
version 폴더 정리를 생략한다. 실제 Windows junction fixture로 검증했다.
현재 손상이 이 정리에서 발생했다는 직접 로그는 부족하므로 유일한 원인으로
단정하지 않는다.

복구 영수증과 원본 파일 목록은 로컬 `H:/TradingAgentsAudit/20261104-runner`에
보존했다. 서비스 재시작과 원래 PRISM workflow 재시도는 하지 않았다.

## 남은 운영 확인

| 항목 | 확인 결과와 재개 조건 |
|---|---|
| KR full 28/30 | `396470.KQ`, `328130.KQ`의 필수 거래일 이력 누락과 Alpha Vantage 한도 오류. 해당 범위의 날짜·가격·정체성이 검증되는 완전한 원천 이력을 확보한 뒤 기존 예산 안에서 검증한다. |
| US full 29/30 | `KVUE`의 Alpaca 이력이 불완전하거나 시간 한도를 넘었다. 검증 가능한 완전한 이력 확보가 필요하다. |
| 연구 공급자 429/timeout | 과거 115개 ticker 기록에 429가 남아 있다. 기존 provider circuit과 retry 한도를 유지한다. 완료하지 못한 분석을 성공으로 간주하지 않는다. |
| PRISM 실제 수집 | 설치 복원과 실행 파일 기동까지 확인했다. 다음 허용된 원래 수집 창에서 collection·게시·전달 영수증을 확인해야 한다. |
| KR/US 갱신 실패 예산 | 당시 연속 실패 3회 기록을 보존한다. 패치 설치가 기존 한도 초기화나 추가 주문 승인을 의미하지 않는다. |
| Pages/Work 과거 오류 | exact handoff 불일치와 오래된 snapshot 차단은 실패 기록으로 보존한다. 새 세대의 실제 공개 bytes/ACK/전달 영수증으로 별도 판정한다. |

시세 공백을 채우거나 검증을 우회해 성공시키지 않는다. 검증되지 않은 종목은
신규 매수 근거로 사용하지 않으며 위험 축소 매도의 별도 경로도 유지한다.

## 검증

- 수정 관련 오프라인 테스트: 280 passed, 2 skipped. 별도 revision 시점
  회귀 테스트 포함. Windows junction·실제 PowerShell 실행을 사용했다.
- Ruff `E9,F63,F7,F82`와 `git diff --check` 통과.
- 병합 전 필수 Windows CI의 unit/browser/test 및 CodeQL 결과를 확인한다.
  전체 CI 결과와 운영 채택 영수증은 PR과 후속 점검에 기록한다.
