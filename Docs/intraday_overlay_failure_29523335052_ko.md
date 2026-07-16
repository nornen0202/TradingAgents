# Intraday Overlay Refresh 실패 29523335052 분석

## 사건

- 대상: [GitHub Actions run 29523335052](https://github.com/nornen0202/TradingAgents/actions/runs/29523335052)
- 실패 job: `overlay_refresh_us`
- 직접 오류: `Overlay bootstrap requires one prior source run with successful analysis artifacts for every target; ... ABT`

## 근본 원인

US daily full run은 당시 정본 40종목의 분석 artifact를 정상 생성했다. 그 이후 intraday 시작 시점에 PRISM/scanner가 `ABT`를 신규 후보로 universe에 추가했다.

기존 gate는 “최근 성공 full source가 있는가”만 확인했지만 실제 bootstrap은 “현재 동적으로 다시 구성한 모든 ticker가 같은 full source에 존재하는가”를 요구했다. 따라서 full run 이후 처음 나타난 정상적인 신규 후보도 코드·데이터 장애처럼 전체 overlay를 중단시켰다.

실패가 반복된 이유는 세 실행 주체가 같은 장애를 독립적으로 복구하려 했기 때문이다.

1. GitHub native schedule이 실패했다.
2. cloud scheduled-actions watchdog이 성공 checkpoint 부재를 보고 같은 profile을 재실행했다.
3. 로컬 Windows watchdog도 최근 성공 부재를 보고 다시 재실행했다.
4. Telegram dedupe key가 원인 fingerprint가 아니라 workflow run ID 중심이어서 동일 원인도 매번 새 장애처럼 보였다.

## 적용한 수정

### Overlay universe 계약

- intraday overlay는 동일 시장의 자체 완전한 production `full` baseline universe로 고정한다. 기준선은 96시간 이내이며 더 새로운 거래 세션은 최대 1개만 허용해 금요일 full→월요일 intraday는 살리고 오래된 분석 재사용은 차단한다.
- 최신 수동·custom·smoke·test 부분 run은 기준선 후보에서 제외하고, 요청 종목 coverage가 가장 큰 최근 정규 full을 선택한다.
- full 이후 새로 발견된 비보유 PRISM/scanner 후보는 실패시키지 않고 다음 full run까지 `deferred_new_candidates`로 기록한다.
- 현재 계좌에 실제로 새 보유종목이 생겼는데 baseline 분석이 없으면 이는 무시할 수 없는 coverage 결함이므로 `OVERLAY_BASELINE_HOLDING_COVERAGE_GAP`으로 중단한다.
- manifest에 baseline run, 실행 ticker, live discovery, deferred ticker를 분리해 남긴다.

### Recovery budget

- cloud/local watchdog은 `head SHA + profile + target job/failed step` fingerprint로 동일 장애를 묶는다.
- 최근 성공 뒤의 연속 동일 실패만 세고, cooldown 안에서 동일 실패는 최대 두 번까지만 시도한다.
- 명시적으로 증명된 gate no-work·superseded deploy만 무시한다. 필수 분석·publish·deploy job이 누락되거나 skipped된 불완전 실행은 synthetic failure로 budget을 소비한다.
- 성공 또는 다른 fingerprint가 나타나면 이전 incident 연속성을 끝낸다.

### Telegram 정책

- native/manual/cloud/local 구분과 무관하게 새 root failure의 최초 사건은 알린다.
- 동일 root failure는 마지막 실제 전송부터 6시간 동안 억제하며, 억제 자체는 cooldown을 연장하지 않는다. 로그를 얻지 못한 Telegram 경로는 서로 다른 장애를 숨기지 않도록 run-scoped fail-open한다.
- 명시적 cancel/no-work·superseded Pages deploy는 알리지 않지만 필수 job이 불완전한 실행은 알린다.
- GitHub Actions에는 모든 run과 `recovery_source`가 남으므로 억제된 retry도 감사 가능하다.

## 회귀 계약

- full baseline에 `NVDA`, `AAPL`만 있고 live scanner가 `ABT`를 추가해도 overlay는 두 baseline ticker로 성공하고 `ABT`를 defer해야 한다.
- `ABT`가 현재 보유종목이면 같은 상황을 성공으로 위장하지 않고 fatal coverage gap이어야 한다.
- 서로 다른 SHA 또는 실패 stage는 같은 retry incident로 합치지 않는다.
- 명시적 no-work로 증명된 skipped workflow만 retry 실패 budget을 소비하지 않으며, 필수 target/publish/deploy 누락은 실패로 센다.
