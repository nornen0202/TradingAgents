# Codex 세션 상태 격리와 언어 변환 실패 보존

2026-10-26. 국내 정상 연구의 자연 재시도 `20261026T081100_local-scheduler-kr-full`은 이전 성공 25개를 재사용하고 실패 5개를 다시 분석했다. 원래 세션의 두 번째 시도이며 강제 실행이나 예산 초기화는 하지 않았다. immutable source는 `ef2983a78d95789c447e741d0f3e756250a4d3a5`다.

## 실제 실패와 확인 범위

APR·HPSP는 KIS 일별 자료를 각각 645·1043행 수집했고, 저장된 자료 영수증은 `VERIFIED_RETRIEVED_SERIES`였다. 각 17회 LLM·28회 Tool 호출 뒤 08:39경 보고서 언어 변환의 새 app-server `initialize`에서 SQLite 상태 초기화 오류가 발생했다. 이전 가격 복구 실패와 구분한다. 실패 시점에는 새 최종 analysis·승인이 완성되지 않았으며, 오류 원문을 성공으로 바꾸지 않는다.

읽기 전용 파일 메타데이터에서는 두 worker home의 별도 file ID, 일반 디렉터리, 쓰기 허용 권한을 확인했다. 내부 SQLite errno·BUSY·I/O·손상 여부는 확인하지 못했다. 당시 source의 deep/quick/output 역할별 session은 같은 worker의 `.codex-home`을 사용하고 lock은 session 인스턴스별이었다. 이는 동시 접근의 구조적 위험이지만, 이번 두 실패의 유일한 원인으로 입증된 것은 아니다. 원본 DB 연결·수정·삭제·복구를 시도하지 않는다.

## 새 프로세스의 상태 디렉터리

실제 새 app-server 프로세스를 시작할 때마다 기존 worker home 아래에 독점 생성한 `sqlite-session-<UUID>`를 사용한다. 기존 `CODEX_HOME`과 인증·모델 seed 동작은 유지하고, `CODEX_SQLITE_HOME` 및 TOML 인용한 CLI `-c sqlite_home=...`를 같은 절대 경로로 지정한다. 공식 문서는 `sqlite_home` 설정이 환경 변수보다 우선한다고 설명하므로 두 경로를 명시적으로 일치시킨다. [공식 환경 변수 문서](https://learn.chatgpt.com/docs/config-file/environment-variables#core-locations), [공식 전역 인자 문서](https://learn.chatgpt.com/docs/developer-commands#global-flags).

경로의 reparse·alias·경계 탈출을 거절하고 생성한 디렉터리의 device/file ID를 묶는다. 살아 있는 같은 프로세스에 대한 `start`는 기존 scope를 유지하며 종료 뒤 새 프로세스에는 새 scope를 배정한다. 기존 worker DB를 복사·이동·재사용하지 않는다. 종료가 확인된 자기 프로세스의 자기 scope에서만 단일 링크 로그 파일을 정리한다. 종료 여부가 불명확하면 프로세스 소유권과 로그를 유지한다. 다른 역할·과거 공용 home·상태 DB는 정리하지 않는다.

이 변경은 별도 감사 동작의 자동 승인 거절을 우회하지 않는다. 거절된 실제 source/worker 설정 존재 감사와 보고서 생성은 재시도하지 않았고, 새 검증은 저장소 코드·합성 Mock·새 빈 home의 초기화에 한정한다.

## 언어 변환 실패와 금융 판단의 경계

보고서용 지역화에서 알려진 `CodexAppServerError`만 발생하면 해당 원문을 그대로 보존하고 남은 번역 호출을 중단한다. 이미 성공한 번역은 유지하므로 혼합 언어가 될 수 있다. 새 `analysis.json`/`error.json`에는 닫힌 필드 목록·상태·원문 텍스트 SHA만 갖는 `presentation-diagnostics/v1`을 기록한다. 잘못된 진단·추가 개인 키·getter 오류는 `UNVERIFIED`로 격리해 원래 분석 오류를 마스킹하지 않는다.

DEGRADED인 새 complete report의 Markdown·HTML에는 “언어 변환 미완료(DEGRADED): 변환되지 않은 원문을 보존했습니다. 금융 판단·가격·승인 조건은 변경하지 않았습니다.”라는 정적 안내를 추가한다. 정상·미지정 보고서 바이트와 재사용 원본은 유지한다. `PROCESSED`는 언어의 완전성을 독립 검증했다는 뜻이 아니다.

금융 graph/provider 오류, 알려지지 않은 예외, 정형 판단 검증 실패와 기존 LLM fallback 차단은 계속 실패한다. 이 처리는 금융 대체 응답을 만들지 않으며 가격·판단·원래 승인·시각·위험 검증을 완화하지 않는다. `execution_authorized=false`이고 WAIT를 BUY로 변경하지 않는다. 계좌·공유 잠금·원장·일일 한도·최대 연구 4회·60분 간격·현재 정규장·120초 시세 계약도 그대로다. 포트폴리오 후처리는 실행 후보의 입력이므로 임의로 생략하지 않는다.

## 검증과 남은 조건

root는 관련 Codex client/env/lifecycle/storage·지역화·보고서·provenance runner 10개 파일에서 150 PASS·20 subtests PASS, 네이티브 디렉터리 symlink 권한 검사 1 SKIP을 확인했다. reparse Mock은 통과했다. author의 66/60 표적 검사 및 독립 standalone 합성 11사례와 중복되므로 더하지 않는다. 독립 검토에서 추가 P1/P2는 없었다. CI와 실제 초기화·배포 결과는 별도 증거로 기록한다.

실제 초기화 검증은 새 private 빈 home, 별도의 합성 config/env 경로, 같은 workspace에서 동시 3개 세션을 사용한다. 원래 인증·설정·DB는 읽지 않고 `initialize`/`initialized`만 허용한다. 성공하더라도 실제 경로 적용의 증거이며 과거 오류의 재현·유일 원인·인증된 모델 호출·정상 연구 완료·주문·체결 증거는 아니다.

실행 중인 이전 source의 연구를 중단하거나 새 코드로 소급 해석하지 않는다. 새 정상 연구가 실제 채택한 자료·필수 증거·원래 판단·승인을 완성하고, 정상 전략 소유 BUY·SELL의 모의 증권사 체결과 귀속 가능한 실제 비용을 확인해야 한다. 아직 정상 전략 체결 및 실제 비용·반복 표본·기간 외 성과는 미충족이며 실투자 판정은 NOT_READY다. 실계좌 주문과 자동 실투자 전환은 false를 유지한다.
