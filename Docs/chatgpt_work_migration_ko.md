# ChatGPT Work·모바일 전달 운영 설계

## 운영 결론

KR·US·YouTube·PRISM 분석은 로컬 Work 산출물을 content-addressed 정본으로 남긴 뒤 대화와 웹·모바일이 같은 결과를 읽는 구조로 운영한다.

1. **분석·정본 경로**: ChatGPT 데스크톱 Work의 로컬 프로젝트 예약 작업이 producer archive를 읽고 Markdown과 구조화 전략을 `archive/work-reports/<surface>`에 publish한다.
2. **대화·스마트폰 소비 경로**: Work 대화는 같은 보고서를 보여 주고, Pages/mobile builder는 credential-free 구조화 보고서를 읽는다. GitHub Actions와 Telegram은 별도 전달 receipt를 담당한다.

ChatGPT 모바일의 **원격** 메뉴는 보조 관제 수단이다. Remote 연결이 끊겨도 이미 게시된 Pages와 Telegram 메시지는 스마트폰에서 계속 볼 수 있다. 다만 새로운 로컬 분석을 생산하는 self-hosted runner와 ChatGPT 로컬 Scheduled task는 각각 필요한 PC·앱·네트워크가 켜져 있어야 한다.

```text
self-hosted producer
  ├─ canonical local archive ──> local ChatGPT Work
  │                              ├─ Scheduled inbox
  │                              └─ archive/work-reports/<surface>/latest.json
  └─ GitHub workflow completion
       ├─ Telegram completion/failure alert
       ├─ /mobile/ public sanitized research
       └─ /mobile/private.html + plaintext strategy report
```

## 공식 ChatGPT 기능 경계

- 데스크톱 Work는 사용자가 허용한 로컬 폴더를 읽을 수 있지만, 그 스레드와 로컬 파일은 해당 컴퓨터에 남고 web/mobile Work 대화로 동기화되지 않는다. 따라서 로컬 파일이 필요한 새 분석에는 컴퓨터와 ChatGPT 앱이 실행 중이어야 한다. [ChatGPT Work and Codex](https://help.openai.com/en/articles/20001275/)
- ChatGPT web/mobile Work는 클라우드에서 실행되며 이 PC의 로컬 폴더나 worktree를 직접 읽지 않는다. Cloud Scheduled task를 프로젝트에서 만들더라도 프로젝트 파일은 task에 전달되지 않는다. [Scheduled Tasks in ChatGPT](https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt)
- Scheduled 화면은 실행 결과와 다음 실행을 모아 보여 주는 inbox이며, ChatGPT push/email 알림은 계정 설정과 플랫폼 권한에 따른다. 이 저장소는 별도로 Telegram 전달 receipt를 검증한다. [Scheduled Tasks in ChatGPT](https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt)
- ChatGPT Scheduled Tasks는 공식적으로 Pro 모델을 지원하지 않는다. 그러므로 `GPT-5.6 Pro`를 웹 예약 작업에 강제로 선택하는 방식 대신, 로컬 Work/Codex 실행 모델을 `gpt-5.6-sol`/`xhigh`로 고정하고 모바일 전달을 검증 가능한 외부 파이프라인으로 분리한다. [Scheduled Tasks in ChatGPT](https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt)
- 모바일 Remote는 연결된 host의 환경을 사용한다. host가 sleep 상태가 되거나 네트워크를 잃거나 앱이 종료되면 연결이 중단된다. [Remote connections](https://learn.chatgpt.com/docs/remote-connections)

공식 문서는 기존 chat에서 실행되는 Scheduled task는 설명하지만, 외부 GitHub workflow가 임의의 개인 ChatGPT 대화에 결과를 주입하는 공개 전달 계약은 설명하지 않는다. 따라서 이 저장소는 “ChatGPT 대화 전송 완료”를 주장하지 않는다. 스마트폰의 확정 전달 채널은 Telegram과 Pages이며, ChatGPT Work는 로컬 분석·상세 대화 경로로 유지한다.

## 데이터 계층과 보안 경계

### 로컬 정본

- 시장·계좌 archive: `C:\TradingAgentsData\archive`
- sanitized PRISM archive: `C:\TradingAgentsData\prism-telegram-archive`
- Work state·ledger·immutable outbox·draft 경로: `.runtime/chatgpt-work`
- 최종 Work 보고서: `C:\TradingAgentsData\archive\work-reports\<surface>\latest.json`

Work 보고서에 읽거나 기록하면 안 되는 자료:

- `C:\TradingAgentsData\telegram-stock-ai-agent.session`
- `C:\TradingAgentsData\prism-telegram-private`
- API key, bot token, 계좌 식별자, session path

### 공개 모바일 Pages

`/mobile/`과 `/mobile/public.json`에는 계좌와 독립적으로 정해진 watchlist/scanner 리서치와 source health만 게시한다. 그 종목이 실제 보유 종목과 겹치더라도 보유 여부는 제거한다. 다음 값은 공개하지 않는다.

- 보유 여부·보유 종목 집합
- 계좌 수량·평균원가·평가액·현금
- 현재/조건부 매수·매도 금액과 목표 비중
- 계좌 식별자와 private archive 경로

공개 Work fallback인 `/work/v1`도 같은 원칙을 따른다. 공개 packet은 개인 전략 복구용이 아니라 source 장애 때 제한된 공개 리서치를 확인하는 용도다.

### Plaintext 전략 Pages

사용자 선택에 따라 종합 전략 보고서는 별도 복호화 없이 `mobile/private.html`에서 읽는다. Pages builder는 검증된 `tradingagents.work-report/v1`만 사용하며 계좌 식별자, API/bot credential, token, session path 또는 로컬 비밀 경로를 포함한 보고서는 publish 단계에서 거부한다. 보유·관심 전략 자체는 표시하되 원시 계좌번호나 인증정보는 표시하지 않는다.

## 모바일 알림 수명주기

`.github/workflows/tradingagents-mobile-notifications.yml`은 다음 producer workflow의 `completed` event를 감지한다.

- Daily Codex Analysis
- Intraday Overlay Refresh
- Account Portfolio Report Verify
- Daily YouTube Verified Reports
- Daily PRISM Telegram Reports

처리 순서는 다음과 같다.

1. main branch의 신뢰된 notifier code로 upstream run ID·workflow·결론을 검증한다.
2. GitHub-hosted runner가 성공/실패 공통 Telegram 알림과 Pages 링크를 보낸다. 숫자형 양의 개인 chat ID만 허용하며, 개인 액션 카드 전송 전에는 Telegram `getChat` 응답의 chat ID와 `type=private`까지 검증한다. credential이나 session 정보는 어떤 chat에도 보내지 않는다.
3. 성공 run이면 self-hosted Windows runner가 로컬 archive에서 개인 액션 카드가 있는지 확인하고 별도 continuation을 보낸다.
4. 동일 upstream run과 hosted incident ledger 갱신은 workflow concurrency로 직렬화한다. self-hosted 개인 액션 카드는 archive ledger를 사용하고, GitHub-hosted 기본 알림은 `actions/cache`에 보존한 ledger와 부분 전송 cursor를 사용한다. 최초 실패는 알리되 동일 원인 fingerprint는 마지막 실제 발송부터 6시간 동안 억제한다. 억제된 사건은 cooldown을 연장하지 않는다.
5. Telegram API 오류는 성공처럼 삼키지 않고 재시도 후 job 실패로 남겨 관제할 수 있게 한다.

필수 GitHub secret:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_NOTIFICATION_CHAT_ID` (양의 정수인 본인 1:1 private chat ID; group/supergroup/channel은 거부)

Work 응답 자체에는 다음 handoff만 남긴다. 이것은 알림 성공 receipt가 아니다.

```text
MOBILE_HANDOFF {"owner":"external_github_notification_pipeline","status":"PENDING_EXTERNAL_VERIFICATION","work_sent_notification":false}
```

## 보유·관심종목 전수 커버리지

시장 producer의 요구 순서는 **보유 전체 → 설정/profile 관심종목 전체 → scanner 추가 후보**다. `ticker_universe_mode=config_plus_account`를 사용하며 daily full run은 ticker cap이나 조기 runtime 종료 때문에 필수 종목을 생략하지 않는다.

`run.json.active_universe`가 다음을 기록한다.

- 계좌 snapshot 상태
- 기대 보유/관심종목 수
- 누락 보유/관심종목 수와 로컬 종목 목록
- 전체 분석 수·성공 수·실패 수와 실패 종목

로컬 Work packet은 이를 `body.current.universe_coverage`로 전달한다. 판정은 다음과 같다.

- `COMPLETE`: 계좌 snapshot을 확인했고 보유·관심 누락 0, ticker 실패 0
- `INCOMPLETE`: 계약은 있으나 누락 또는 분석 실패가 하나 이상
- `UNVERIFIED`: 필요한 계약이나 수치가 없음

Work 보고서는 모든 보유 종목과 설정/profile 관심종목을 화면에 표시한다. 관심목록 밖 scanner/discovery 신규 후보만 최대 5개로 제한한다. 보고서의 `COVERAGE_RECEIPT`로 upstream 전수 분석과 응답 전수 표시를 함께 확인한다. 공개 Pages에는 보유 종목 이름을 노출하지 않고 count도 포트폴리오를 추론하지 못하도록 제한한다.

## 로컬 Work 실행 계약

프로젝트 Skill은 `.agents/skills/tradingagents-daily-investment-work/SKILL.md`, task 정본은 `config/chatgpt_work_tasks.json`이다.

```powershell
python -m tradingagents.work prepare --surface kr --archive-dir C:\TradingAgentsData\archive --youtube-archive-dir C:\TradingAgentsData\archive\youtube-archive --prism-archive-dir C:\TradingAgentsData\prism-telegram-archive
```

- `NEW`: 새 immutable event의 보고서를 완성한 뒤 같은 invocation에서 ACK
- `RESUME`: ACK 전 중단된 동일 event를 같은 ID로 다시 보고하고 ACK 재시도
- `NOOP`: 이전 보고서를 반복하지 않음
- `SOURCE_REGRESSION`: watermark와 ACK를 전진시키지 않음
- `BUSY_NO_STATE_ADVANCE`: 다음 예약에서 재시도

로컬 packet이 없으면 public Pages로 개인 전략을 재구성하지 않고 `ERROR`로 끝낸다. `current`와 `last_ready`를 합치지 않고 응답 현재 시각에 source·시장 데이터·행별 유효시간을 다시 검사한다. stale/failed/missing data는 현재 주문 행동으로 표현하지 않는다.

실행 순서는 `prepare → Markdown/structured JSON 작성 → publish → ACK → KR/US Pages handoff`다. KR·US는 publish가 없으면 ACK가 실패한다. YouTube·PRISM publish는 선택 가능하다.

구조화 보고서는 packet의 `surface`, `event_id`, `source_sha256`에 묶인다. KR·US `strategies`는 prepared packet의 전체 ticker를 canonical identity 기준으로 정확히 한 번씩 포함해야 하며 누락·중복·unknown ticker는 publish가 거부한다. 구조화 `coverage_receipt`는 packet의 `current.universe_coverage`, `model_receipt`는 packet의 `model_provenance`와 정확히 일치해야 한다. 종목 분석은 실제 LLM usage가 있으면 관측 모델을 표시하지만 Work 종합은 호스트가 서명된 응답별 모델 receipt를 제공하지 않으므로 `CONFIGURED_NOT_RUNTIME_VERIFIED`를 유지한다. 이를 ChatGPT Chat/Pro 모드 실행으로 추정하지 않는다. Report execution은 packet readiness를 승격하거나 유효시간을 연장할 수 없고 packet blockers·required rechecks를 모두 보존한다. stale 시에는 `execution.readiness`만 `NEEDS_LIVE_RECHECK`로 낮추고 분석 시점 `thesis`와 조건·무효화·기간을 지우지 않는다.

시장 packet의 supporting context는 보유→관심→탐색 종목 순서의 round-robin으로 YouTube 12건, PRISM 20건까지 고르고, 잘린 수와 실제 전송 수를 coverage에 기록한다. structured report는 `external_evidence_receipt`를 그대로 돌려주고 정상·관련 event의 정확한 `event_key`와 영향을 받은 필드를 종목별 `source_contributions`에 묶어야 한다. 따라서 모델이 외부 근거를 받았지만 조용히 무시하거나, 받지 않은 근거를 인용한 보고서는 publish되지 않는다.

```powershell
python -m tradingagents.work publish --surface kr --event-id <event_id> --source-sha256 <source_sha256> --markdown-file <report_markdown_path> --structured-file <report_structured_path> --archive-dir C:\TradingAgentsData\archive
```

publish는 동일 내용을 `work-reports/<surface>/events/<report_sha256>.json`과 `latest.json`에 기록한다. 보고서를 완성·검증·publish하고 coverage·mobile handoff를 출력한 다음에만 정확한 event를 ACK한다.

```powershell
python -m tradingagents.work ack --surface kr --event-id <event_id> --status rendered
```

ACK는 Work event 렌더링 receipt다. producer 신선도, Telegram 전송, Pages 배포 성공을 의미하지 않는다. ACK 실패 시 `PENDING_ACK`로 남겨 다음 run이 같은 event를 `RESUME`하게 한다. 공개 Pages event ID는 로컬 ACK·recover에 사용하지 않는다. State 복구는 canonical ACK ledger가 증명하는 receipt만 허용하며 KR·US는 exact `report_sha256`와 content-addressed latest report까지 일치해야 한다. 이미 state가 있는 동일 surface를 과거 receipt로 덮어쓰지 않는다.

KR·US ACK 뒤에는 exact hash handoff를 수행한다.

```powershell
python -m tradingagents.work handoff --surface kr --event-id <event_id> --report-sha256 <report_sha256> --repository nornen0202/TradingAgents --ref main
```

`DISPATCH_ACCEPTED`는 GitHub 요청 접수만 증명하며 배포 성공은 아니다. 전용 workflow가 report/latest byte identity와 빌드 후 Work lineage를 검증한다. 정상 handoff 성공은 Telegram에 보내지 않고 실제 workflow 실패만 중복 incident cooldown 정책으로 알린다.

## YouTube·PRISM 안전 규칙

- YouTube event key: `video_id + content_sha256`
- PRISM event key: `channel:message_id + content_sha256`
- 동일 key의 hash 변경은 revision, 동일 hash는 NOOP
- source health와 producer/event 시각을 응답 현재 시각에 재검증
- stale/failed/missing 또는 유효한 새 event 없음: `NO_ACTIONABLE_DELTA`
- `coverage.truncated=true`: 전수 분석이라고 표현 금지
- YouTube·PRISM: `balanced_external`로 종목 순위, thesis confidence, 기존 위험 한도 안의 크기, 리서치 우선순위에 상·하향 반영
- YouTube·PRISM: 항상 execution-ineligible이며 시장·계좌·위험 실행 gate 우회 금지
- PRISM Work: Telegram session/private archive 직접 접근 금지

시장 structured report는 양의 고유 rank, 알려진 portfolio role, 0~1 confidence를 사용한다. 모든 thesis는 무효화 조건 발생 시 실제로 취할 `invalidation_action`을 포함한다. 실행 가능한 thesis는 구체적인 진입·무효화 조건과 horizon·position sizing을 포함하고 placeholder·tautology를 허용하지 않는다. `top_actions`의 ticker/readiness/action은 대응하는 strategy와 정확히 일치해야 하며, RESEARCH가 조건을 제시하지 못하면 필요한 데이터와 이유 및 보류·제외·재분석 행동을 명시한다.

## 예약 정의

`config/chatgpt_work_tasks.json`의 네 task는 local mode, GPT-5.6 Sol, `xhigh`, Asia/Seoul을 사용한다. 각 prompt는 다음을 명시한다.

- stale/unavailable local data fail-closed
- KR·US 보유/관심종목 coverage receipt
- 모바일 우선 요약
- 외부 Telegram/Pages 전달 완료 주장 금지
- ChatGPT web/mobile이 로컬 private state를 읽었다는 주장 금지

YouTube와 PRISM은 state lock 충돌을 줄이도록 실행 분을 엇갈린다.

## 배포 후 검증

1. Work packet·prompt·Skill·task manifest 계약 테스트와 Skill validation을 통과시킨다.
2. 실제 최신 KR·US packet에서 `universe_coverage=COMPLETE`, 누락 0, 분석 실패 0인지 확인한다.
3. 네 surface의 `prepare`가 NEW/RESUME/NOOP을 결정적으로 반환하고, KR·US는 publish 전 ACK가 거부되는지 확인한다.
4. report event/source binding, 전체 ticker coverage, content-addressed event와 latest hash를 확인한다.
5. exact-hash handoff의 report 사전 검증과 site 사후 lineage 검증을 확인한다.
6. `/mobile/`, `/mobile/public.json`, `/mobile/private.html`과 `/work/v1/<surface>/report/latest.json`을 확인한다.
7. 공개 site 전체에 계좌 식별자, credential, token, session 경로, key가 없는지 확인한다.
8. Telegram에 producer 성공과 실패 테스트 알림이 모두 도착하는지 확인한다.
9. 360/390/430 px viewport에서 KR·US 액션 카드가 가로 overflow 없이 보이는지 확인한다.
10. 과거 raw decision bundle·portfolio 공개 URL이 404인지 확인한다.
11. 다음 정규 full run에서 보유·관심종목 전수 분석과 완료 알림을 다시 확인한다.

## 장애와 롤백

- Telegram 실패: workflow run과 notifier log를 확인하고 secret/chat ID/API 상태를 복구한 뒤 같은 upstream run ID로 수동 재실행한다.
- strategy dashboard 로드 실패: `work-reports/<surface>/latest.json` binding·hash·Pages build 시각을 확인한다.
- local Work 실패: PC·ChatGPT 앱·archive 경로·state lock을 확인한다. public packet으로 ACK하지 않는다.
- Pages privacy 회귀: 배포를 중단하고 노출 artifact를 제거한 뒤 식별자 검사와 전체 site 안전 rebuild를 우선한다. 이미 노출된 credential이 있으면 해당 credential을 별도로 폐기·회전한다.
- Work task 롤백: task를 pause할 수 있지만 Chrome-to-ChatGPT 자동화와 같은 surface를 동시에 실행하지 않는다.
