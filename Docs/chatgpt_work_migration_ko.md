# ChatGPT Work 전환 운영 설계

## 결론

KR·US·YouTube·PRISM은 ChatGPT 데스크톱 Work의 **로컬 프로젝트 예약 작업**으로 실행한다. 브라우저를 열어 ChatGPT 웹 composer에 붙여넣는 경로는 사용하지 않는다.

정본은 다음 세 계층으로 나눈다.

1. self-hosted producer archive: 시장 분석, YouTube 검증, PRISM 수집 결과
2. `.runtime/chatgpt-work`: 원자적 state, append-only ledger, immutable outbox
3. `/work/v1`: 비식별·허용목록 기반 Pages 장애시 데이터 fallback packet

로컬 `state.json`, `memory.md`, Python을 Work가 못 읽는다는 전제는 웹 standalone task에는 맞지만 데스크톱 로컬 프로젝트 task에는 맞지 않는다. 데스크톱 Work는 프로젝트 디렉터리에서 Python을 실행할 수 있으므로 결정적 처리와 상태 관리는 Python에 유지한다. Pages에 state나 계좌 상세를 공개하지 않는다.

## 보안 경계

Work가 읽어도 되는 경로:

- `C:\Projects\TradingAgents`
- `C:\TradingAgentsData\archive`
- `C:\TradingAgentsData\prism-telegram-archive`

금지 경로:

- `C:\TradingAgentsData\telegram-stock-ai-agent.session`
- `C:\TradingAgentsData\prism-telegram-private`
- API key, 계좌 식별자, Telegram 인증 자료

Pages packet은 보유 여부, 보유 종목, 정확한 계좌 수량·평균원가·현금·주문을 포함하지 않는다. 로컬 Work packet의 private overlay에는 필요한 포트폴리오 action만 포함하며 공개 site builder는 이를 생성하지 않는다. 로컬 packet과 공개 packet은 의도적으로 event ID와 source hash가 다르므로 Pages event를 로컬 ACK·resume에 사용하지 않는다.

## 로컬 Work 실행 계약

프로젝트 skill: `.agents/skills/tradingagents-daily-investment-work/SKILL.md`

준비 명령:

```powershell
python -m tradingagents.work prepare --surface kr --archive-dir C:\TradingAgentsData\archive --youtube-archive-dir C:\TradingAgentsData\archive\youtube-archive --prism-archive-dir C:\TradingAgentsData\prism-telegram-archive
```

결과 상태:

- `NEW`: 새 immutable event의 보고서를 완성한 뒤 같은 invocation에서 ACK
- `RESUME`: ACK 전 중단된 동일 event를 같은 ID로 다시 보고하고 ACK 재시도
- `NOOP`: 이전 보고서를 반복하지 않음
- `SOURCE_REGRESSION`: watermark와 ack를 전진시키지 않음
- `BUSY_NO_STATE_ADVANCE`: 다음 예약에서 재시도

Standalone Scheduled run은 이전 run의 대화 문맥을 물려받지 않는다. 따라서 보고서 본문을 먼저 완성·검증한 뒤 같은 invocation에서 다음을 실행한다. ACK 성공 후에만 `SUCCESS` receipt를 출력하며, ACK 실패 시 `PENDING_ACK`로 남겨 다음 run이 같은 event를 `RESUME`한다.

Scheduled에는 사용자 화면 저장 완료 뒤 실행되는 별도 post-delivery hook이 없으므로 ACK 직후 최종 응답 저장 실패라는 매우 짧은 이론적 구간은 남는다. 이를 줄이기 위해 본문을 먼저 완성하고 ACK를 마지막 상태 변경으로 제한하며, immutable outbox·append-only ledger·`recover` 명령으로 동일 event를 감사·복구한다.

```powershell
python -m tradingagents.work ack --surface kr --event-id <event_id> --status rendered
```

원자적 state가 손상된 경우에는 자동으로 revision 0으로 초기화하지 않는다. 이미 보이는 conversation recovery mirror와 immutable local outbox가 정확히 일치할 때만 `python -m tradingagents.work recover ...`로 복구한다.

YouTube event key는 `video_id + content_sha256`, PRISM은 `channel:message_id + content_sha256`다. 같은 ID의 hash 변경은 revision이고 동일 hash는 NOOP다.

## 시장 실행 안전성

- bundle 전역 준비율은 행을 승격하지 못한다.
- 모든 보유 행이 execution-ready일 때만 portfolio-wide READY다.
- 일부 유효 행이 있으면 MIXED로 유지해 보유 위험축소 신호를 숨기지 않는다.
- stale BUY/SELL/REDUCE는 즉시 행동이 아니라 실시간 재확인 경고다.
- `current_execution_promotion=POSSIBLE`과 provider 상태 gate 통과가 즉시 행동의 필수조건이다.
- YouTube와 PRISM은 항상 execution-ineligible이며 실행 전략을 상향하지 못한다.

## Pages 장애시 데이터 fallback API

전체 site rebuild가 다음을 생성한다.

```text
/work/v1/index.json
/work/v1/{kr,us,youtube,prism}/status.json
/work/v1/{stream}/latest.json
/work/v1/{stream}/events/{event_id}.json
/work/v1/prompts/*.md
```

event ID는 schema, prompt·Skill·task manifest contract hash와 공개 source hash를 포함한다. build 시각은 semantic hash에서 제외한다. 공개 event는 canonical archive의 `work-public`에 보존하고 최근 120개를 site에 재게시한다. 로컬 market packet은 보유 전체와 신규 5개를 포함하지만, 공개 Pages packet은 포트폴리오 관계와 action을 제거하고 비보유 연구 후보만 최대 5개 포함한다. PRISM public sidecar와 YouTube summary URL은 raw session이나 private path를 노출하지 않는다. 이 API는 로컬 private/delta delivery의 동일 event 복구가 아니라, 로컬 archive 접근 장애 시 제한된 공개 데이터로 새 분석을 재구성하는 fallback이다.

YouTube·PRISM source는 마지막 producer run 시각·상태를 포함하고 `OK`, `DEGRADED`, `FAILED`, `EMPTY`, `STALE`, `MISSING`을 구분한다. 공개 packet은 deterministic byte budget으로 오래된 event부터 생략하고 coverage에 생략 수를 기록한다.

## Pages 덮어쓰기 방지

모든 producer workflow는 세 archive 경로를 전달하고, 각 Pages 배포 job은 공통 `tradingagents-pages-deploy` concurrency group으로 직렬화한다. 새 배포가 대기 중인 더 오래된 배포를 대체할 수는 있지만 실행 중인 배포를 취소하지 않으며, producer 자체는 서로 막지 않는다. YouTube·PRISM 수집 뒤에는 전체 site와 Work context를 다시 생성한다. 따라서 overlay가 정상 PRISM/YouTube subtree를 빈 결과로 지우거나 Work packet이 한 run 뒤처지는 문제를 막는다.

## 예약 정의

정본 설정은 `config/chatgpt_work_tasks.json`이다. 네 task 모두 다음 조건을 사용한다.

- project: `C:\Projects\TradingAgents`
- mode: Local
- model: GPT-5.6 Sol
- reasoning: 매우 높음(`xhigh`)
- timezone: Asia/Seoul

YouTube와 PRISM은 state lock 충돌을 피하도록 5분 간격으로 엇갈린다.

## 전환 검증과 롤백

1. 단위 테스트, packet schema/size/hash, skill validation 통과
2. 네 surface의 로컬 `prepare`가 NEW/RESUME을 생성하는지 확인
3. Work task를 각 1회 수동 실행해 `SUCCESS` STATE/receipt와 Scheduled inbox 표시 확인
4. 동일 입력으로 두 번째 실행해 NOOP 확인
5. Pages 배포 후 네 status/latest/event/prompt URL의 200과 SHA 일치 확인
6. 새 Work task 성공 후 기존 Chrome 자동화 네 개를 pause

롤백 시 기존 자동화 TOML은 삭제하지 않고 pause 상태로 보존한다. Work task를 중지하고 Chrome 자동화를 다시 활성화할 수 있지만, 같은 surface의 두 전달 경로를 동시에 실행하지 않는다.
