# 2026-08-17 자동화 실패·Telegram 반복 알림 사후 분석

## 결론

2026-08-17 KST의 반복 알림은 한 가지 오류가 아니라 두 문제가 겹친 사건이다.

1. 한국 증시 대체공휴일을 예약 실행 계층이 확인하지 않고 평일만으로 판단했다.
2. 실제로 반복 실패한 미국 장중 overlay 실행은 self-hosted runner가
   `actions/checkout`을 내려받는 과정에서 GitHub codeload의 HTTP 429를
   받았다. watchdog 재실행이 같은 실패를 더 많이 만들었다.
3. 429 응답마다 달라지는 GitHub correlation ID가 Telegram incident
   fingerprint에 그대로 포함되어 같은 원인이 매번 새로운 사건으로
   분류됐다.
4. watchdog dispatch 자체도 한 차례 GitHub API HTTP 503을 받아 별도의
   workflow failure가 됐다.

대체공휴일 누락은 실제 설계 결함이지만, 미국 overlay 429의 직접 원인은
아니다. 평일 기반 스케줄과 재시도 증폭, 불안정한 fingerprint가 결합되어
장애와 알림이 지속됐다.

## 확인한 증거

- Intraday Overlay Refresh 실패 run:
  `32037212020`, `32037676664`, `32039732012`,
  `32041531042`, `32043230818`, `32044517603`
- 각 실패 로그: `actions/checkout` codeload HTTP 429, 서로 다른
  colon-separated GitHub request ID
- Scheduled Actions Watchdog run `32049422775`: dispatch API HTTP 503
- `exchange_calendars 4.13.2`의 XKRX는 2026-08-17을 비영업일로 판정하지만,
  기존 workflow gate와 watchdog는 이 캘린더를 호출하지 않았다.

## 재설계

자동 실행은 다음 순서로 결정한다.

1. 수동 dispatch는 운영자의 명시적 복구 권한으로 기존처럼 허용한다.
2. 한국 자동 실행은 KIS 공식 `chk-holiday` 결과의 `opnd_yn`을 확인한다.
3. 결과를 KST 날짜별 GitHub Actions cache에 저장해 같은 날 중복 조회를
   막는다.
4. 전날 cache에 미래 영업일이 들어 있어도 당일 첫 실행에서 반드시 다시
   조회한다. 뒤늦게 지정된 임시휴일이 전날 예측에 가려지지 않는다.
5. 공식 조회가 활성화됐는데 credential 또는 API가 없으면 fail-closed로
   실행을 보류한다.
6. 미국 자동 실행과 로컬 fallback은 `exchange_calendars`를 사용한다.
7. native gate, intraday gate, cloud watchdog 세 경로가 같은 판정을 사용한다.

## 알림·재시도 보호

- GitHub request/trace/correlation ID를 `<request-id>`로 정규화한다.
  같은 429는 6시간 incident cooldown 안에서 한 사건으로 묶인다.
- cloud watchdog와 로컬 PowerShell dispatcher도 같은 정규화를 사용한다.
- watchdog dispatch의 일시적인 HTTP 503/네트워크 오류는 성공적으로
  “deferred” 처리한다. 다음 watchdog 주기가 재시도하므로 별도 failure
  storm을 만들지 않는다.
- 휴일 또는 캘린더 확인 불가 상태에서는 work job을 시작하지 않으므로
  self-hosted runner와 외부 API를 불필요하게 소비하지 않는다.

## 운영 조건

다음 GitHub secrets가 한국 자동 실행의 공식 영업일 판정에 필요하다.

- `KIS_APP_KEY`
- `KIS_APP_SECRET`

credential은 cache에 기록하지 않는다. cache에는 날짜별 open/closed 결과와
조회 시각만 저장한다.
