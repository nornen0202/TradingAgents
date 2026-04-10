# KIS 접근 토큰(24시간) 자동 갱신 조사 및 구현 설계안

작성일: 2026-04-10 (UTC)

## 1) 조사 결론 (핵심)

- **가능합니다.** 현재 TradingAgents의 KIS 연동은 `client_credentials`로 접근 토큰을 발급하고 메모리에만 보관하므로, 스케줄러/보고서 실행 전에 토큰 만료를 선제적으로 처리하는 자동화가 가능합니다.
- 단, KIS 생태계에는 문서 체계가 둘로 나뉘어 보입니다.
  - **일반 Open Trading API(개인/법인 앱키 기반 샘플)**: 실사용 샘플/커뮤니티에서 접근 토큰 1일(24시간) 안내가 반복됨.
  - **제휴(투자자문/일임) Provider 문서**: access token 90일 + refresh token 기반 갱신 플로우가 별도로 존재.
- 따라서 TradingAgents MVP는 현재 코드 흐름(`grant_type=client_credentials`)을 유지하면서, **"24시간 access token 선제 재발급"** 방식으로 설계하는 것이 가장 현실적입니다.

## 2) 근거 정리

### 2.1 현재 TradingAgents 코드 기준

- `KisClient.issue_access_token()`은 `/oauth2/tokenP`에 `grant_type=client_credentials`로 요청합니다.
- `ensure_access_token()`은 토큰 문자열 유무만 확인하며, 만료 시각/선제 갱신/401 재시도 로직이 없습니다.
- 즉, 장시간 운용(일일 배치, 다회 실행)에서 토큰 만료가 발생하면 해당 시점에 API 호출이 실패할 수 있습니다.

### 2.2 외부 문서 조사 요약

- 사용자 제시 참고 글(hotorch, 2023-03-25)은 "일반 고객 토큰 유효기간 1일" 전제를 두고 스케줄링 발급을 권장합니다.
- 한국투자증권 공식 GitHub 샘플(`open-trading-api`)의 인증 유틸 주석에도
  "토큰 유효시간 1일, 6시간 이내 재발급 시 기존 토큰값 동일" 취지 문구가 포함되어 있습니다.
- 반면 KIS Developers 제휴 문서(provider-doc4)는 제휴 맥락에서
  access token 90일, refresh token 운용(고객 재신청 포함)을 설명합니다.

### 2.3 실무적 해석

- 현재 TradingAgents는 제휴 인가코드/refresh_token 플로우가 아니라 `client_credentials` 기반입니다.
- 따라서 지금 단계에서 안정적 자동화 전략은 다음 2가지입니다.
  1. **만료 시각 기반 선제 재발급**
  2. **API 거부(토큰 만료 추정) 시 1회 재발급 후 재시도**

## 3) 목표 동작 (요구사항)

1. 보고서 런 시작 전, 유효한 KIS access token을 반드시 확보한다.
2. 토큰 만료 임박(예: 20분 이하)이면 호출 전에 선제 갱신한다.
3. 호출 중 토큰 만료/인증 실패 발생 시 1회에 한해 자동 재발급 후 재시도한다.
4. 토큰 캐시는 프로세스 메모리 + 파일 캐시(옵션)로 관리한다.
5. 로그에는 토큰 원문을 절대 남기지 않는다.

## 4) 제안 아키텍처

```text
KisClient
 ├─ issue_access_token()           # 발급 API 호출
 ├─ ensure_access_token()          # 만료 임박 체크 + 선제 갱신
 ├─ request_json()                 # 401/토큰만료 에러 시 1회 재시도
 └─ TokenStore (new)
     ├─ load() / save()
     ├─ access_token
     ├─ expires_at_utc
     └─ last_issued_at_utc
```

### 4.1 TokenStore 설계

- 기본 경로: `~/.cache/tradingagents/kis_token_{env}_{appkey_prefix}.json`
- 저장 필드:
  - `access_token`
  - `expires_at` (ISO8601 UTC)
  - `issued_at` (ISO8601 UTC)
  - `source` (`api` | `cache`)
- 파일 권한: POSIX 기준 `0o600` 권장
- 보안: 앱키/시크릿 미저장, 액세스 토큰만 최소 저장

### 4.2 만료 계산 정책

- 24시간 정책 가정 시:
  - `expires_at = issued_at + 24h`
- 안전 마진(선제 갱신): `refresh_skew = 20m` (설정화)
- 판정:
  - `now >= expires_at - refresh_skew`면 재발급

### 4.3 실패 복구 정책

- `request_json()`에서 인증 실패(HTTP 401 또는 KIS 토큰 만료 코드/메시지) 감지 시:
  - 내부 토큰 무효화
  - `issue_access_token(force=True)`
  - 동일 요청 1회 재시도
- 2차 실패 시 원 예외 상승

### 4.4 동시성 정책

- 멀티프로세스/크론 중복 실행 대비 파일 락(예: `fcntl`) 적용
- 동일 시점 다중 발급 폭주 방지를 위해
  - 락 획득 후 캐시 재검증(double-check)

## 5) TradingAgents 반영 포인트

### 5.1 수정 대상

- `tradingagents/portfolio/kis.py`
  - `KisClient`에 토큰 메타데이터(`_token_expires_at`) 추가
  - `issue_access_token()`이 `expires_in` 응답이 있으면 우선 사용
  - 없으면 정책 기본값(24h)으로 계산
  - `ensure_access_token()`에서 선제 갱신
  - `request_json()`에 1회 자동 재시도

### 5.2 신규 설정(예시)

- 환경변수:
  - `KIS_TOKEN_REFRESH_SKEW_SECONDS` (default 1200)
  - `KIS_TOKEN_TTL_SECONDS_DEFAULT` (default 86400)
  - `KIS_TOKEN_CACHE_PATH` (optional)
  - `KIS_TOKEN_FILE_CACHE_ENABLED` (default true)

### 5.3 관측성(Observability)

- INFO: `KIS token loaded from cache`, `KIS token renewed proactively`
- WARN: `KIS token renewal triggered by auth failure`
- 메트릭(선택): `kis_token_issued_total`, `kis_token_refresh_retry_total`

## 6) 구현 단계(권장 순서)

1. **Step 1 (안정성 최소요건)**
   - 메모리 기준 만료시각 추적 + 선제 갱신 + 1회 재시도
2. **Step 2 (운영성 강화)**
   - 파일 캐시 + 파일 락 + 설정값 주입
3. **Step 3 (검증/회귀테스트)**
   - 토큰 만료 시나리오 단위테스트 추가
4. **Step 4 (운영 가이드)**
   - 계좌 리포트 스케줄러 문서에 토큰 로테이션 절차 반영

## 7) 테스트 시나리오

- `test_issue_token_sets_expiry`
- `test_ensure_token_refreshes_when_near_expiry`
- `test_request_json_retries_once_after_auth_failure`
- `test_file_cache_load_save_roundtrip`
- `test_concurrent_refresh_uses_single_issue_call`

## 8) 리스크와 대응

- 리스크: 공식 문서 체계(개인 API vs 제휴 API) 간 토큰 정책 차이
  - 대응: `expires_in` 응답값 우선 사용 + 기본 TTL 설정값 외부화
- 리스크: 토큰 파일 유출
  - 대응: 권한 제한(600), 저장 경로 사용자 홈 하위 고정, 로그 마스킹
- 리스크: 대량 배치 시 재발급 폭주
  - 대응: 파일 락 + double-check + 랜덤 지터(옵션)

## 9) 운영 체크리스트

- [ ] API 호출 서버 시간 동기화(NTP)
- [ ] 토큰 파일 권한 600 확인
- [ ] 스케줄러 시작 전 dry-run으로 토큰 선확보
- [ ] 인증 실패 재시도 알람 연결

## 10) 최종 권고

- 질문하신 "유효기간 전에 자동 발급/갱신" 방식은 **현 구조에서 충분히 구현 가능**합니다.
- TradingAgents에는 우선 `kis.py`에 토큰 만료 인지 + 선제 갱신 + 인증실패 1회 재시도를 넣는 것이 효과 대비 개발비용이 가장 낮습니다.
- 이후 파일 캐시/락까지 추가하면, 일일 계좌 운용 리포트 배치에서 토큰 만료로 인한 실패 확률을 크게 낮출 수 있습니다.
