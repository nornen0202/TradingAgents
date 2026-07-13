# GPT-5.6 역할별 마이그레이션 및 검증 계획

## 목표

종목 분석과 투자자 리포트 생성에서 품질이 중요한 판단은 GPT-5.6 Sol에 유지하고, 반복적인 분석은 Terra, 출력·현지화·리포트 정리는 Luna로 분리한다. 모델 변경과 함께 역할별 reasoning effort 및 사용량 계측을 도입해 성공 리포트당 비용과 지연시간을 비교할 수 있게 한다.

## 기본 라우팅

| 역할 | 모델 | reasoning effort | 주요 호출 |
| --- | --- | --- | --- |
| `quick` | `gpt-5.6-terra` | `low` | 시장·뉴스·재무·소셜 분석, 토론, trader |
| `deep` | `gpt-5.6-sol` | `medium` | research manager, portfolio manager |
| `output` | `gpt-5.6-luna` | `low` | 출력 언어 현지화 및 보고용 후처리 |
| `writer` | `gpt-5.6-luna` | `low` | 종목·포트폴리오 투자자 요약 정리 |
| `judge` | `gpt-5.6-sol` | `medium` | semantic judge, action judge |
| `execution_summary` | 명시 모델 사용 | `low` | 선택적으로 활성화한 장중 실행 요약 |

기존 `codex_reasoning_effort`는 오래된 설정 파일과 외부 호출을 위한 fallback으로 유지한다. 역할별 설정이 있으면 역할별 값이 우선한다.

## PRISM YouTube 라우팅

PRISM YouTube는 하나의 deep model로 네 단계를 처리하던 구조를 세 역할로 분리한다.

| 단계 | 역할 | 모델 | reasoning effort | 선택 근거 |
| --- | --- | --- | --- | --- |
| 주장 추출·리서치 계획 | `quick` | `gpt-5.6-terra` | `low` | 긴 ASR 문맥에서 중요 주장을 빠뜨리지 않으면서 Sol 호출을 줄인다. |
| 외부 근거 판정 | `judge` | `gpt-5.6-sol` | `medium` | 잘못된 지지·반박 판정이 투자자 리포트에 미치는 위험이 가장 크다. |
| 최종 Markdown 작성 | `writer` | `gpt-5.6-luna` | `low` | 검증 완료된 구조화 payload만 재구성하며 새로운 사실 판단을 금지한다. |

모델별 프롬프트와 JSON 계약은 유지한다. 모델 교체와 프롬프트 전면 개편을 한 번에 묶지 않으며, 역할별 모델·effort·fallback 효과를 먼저 분리 측정한다.

## 가용성 및 fallback

GitHub Actions preflight는 `model/list`에서 Sol, Terra, Luna를 각각 확인한다. 배포 preflight와 실제 요청의 정책은 의도적으로 분리한다.

- `TRADINGAGENTS_CODEX_PREFLIGHT_ALLOW_MODEL_FALLBACK=1`: runner가 새 모델을 아직 노출하지 않을 때 역할 등급에 맞는 호환 모델을 선택한다.
- `TRADINGAGENTS_CODEX_ALLOW_MODEL_FALLBACK=0`: preflight가 내보낸 정확한 모델로 실제 요청을 fail-fast 실행한다.
- 따라서 새 모델 미노출은 전체 workflow 중단이 아니라 명시적 호환 모델 선택으로 처리하고, 선택 이후의 예기치 않은 모델 변경은 허용하지 않는다.

fallback은 다음 순서를 사용한다.

- `deep`, `judge`: 품질 보존을 위해 `gpt-5.5`를 우선한다.
- `quick`, `output`, `writer`, `execution_summary`: 비용·지연 등급 보존을 위해 `gpt-5.4-mini`를 우선한다.
- 실제 요청 모델과 해결된 모델은 workflow summary 및 실행 manifest에서 확인한다.

runner의 `CODEX_BINARY`는 정식 설치본을 가리켜야 한다. workflow는 선택한 binary 경로와 `codex --version`을 로그에 남겨 구형 sandbox binary 고정을 즉시 식별할 수 있게 한다.

## 계측

Codex usage 이벤트는 `model` 외에 `role`을 저장한다. 각 종목 및 배치 결과의 `codex_usage`에는 `by_model`, `by_role`, `events`가 포함된다.

비교 시 다음 값을 역할별로 집계한다.

- 호출 수
- 입력·출력·총 토큰
- 종목당 총 실행시간과 timeout 비율
- 구조화 출력 재시도와 실패율
- 성공 리포트당 토큰 및 크레딧 추정치

현재 app-server usage 이벤트는 cached input을 별도로 제공하지 않으므로, 크레딧 계산은 캐시 비중을 알 수 없는 추정치로 표시한다.

## 검증 행렬

1. 설정 검증
   - 기본값과 TOML/env override 우선순위를 검사한다.
   - writer와 judge가 각각 Luna와 Sol을 선택하는지 검사한다.
   - 역할별 effort와 usage role 태그를 검사한다.
2. 계약 검증
   - 구조화 의사결정 스키마, tool call 변환, parser retry가 기존과 동일하게 동작해야 한다.
   - 투자 판단, 수치, 진입·무효화·축소 조건을 writer가 변경하지 않아야 한다.
3. workflow 검증
   - US/KR/YouTube workflow YAML을 파싱한다.
   - 로컬 및 runner의 `model/list`에서 세 모델을 확인하고, 5.6 미노출 fixture에서는 등급별 fallback을 확인한다.
   - preflight가 각 역할별 환경 변수를 올바르게 내보내는지 검사한다.
4. 회귀 검증
   - 모델 호출을 mock 처리한 전체 테스트 스위트를 실행한다.
   - 최근 KR/US 실행 스냅샷을 고정 입력으로 사용해 이전 모델과 5.6 결과를 비교한다.

## 운영 rollout

1. Shadow: 기존 게시 결과는 유지하고 5.6 결과를 비공개 artifact로 저장한다.
2. Canary 10%: 대표 종목과 held ticker를 포함해 게시 범위를 제한한다.
3. Canary 50%: schema 성공률, timeout, 판단 변경률, 역할별 토큰을 비교한다.
4. Full: 품질 gate가 유지되고 성공 리포트당 비용 또는 지연이 개선될 때 전체 적용한다.

rollout 중에는 다음 조건을 hard gate로 사용한다.

- 구조화 출력 및 parser 성공률이 기존보다 낮아지지 않을 것
- 필수 근거와 수치 보존에 회귀가 없을 것
- 모델 unavailable, auth, timeout 오류가 증가하지 않을 것
- 판단 변경은 근거 차이를 설명할 수 있을 것
- 역할별 토큰과 성공 리포트당 비용이 manifest에서 추적 가능할 것

## 롤백

환경 변수만으로 역할별 롤백할 수 있다.

```text
TRADINGAGENTS_CODEX_QUICK_MODEL=gpt-5.4-mini
TRADINGAGENTS_CODEX_DEEP_MODEL=gpt-5.5
TRADINGAGENTS_CODEX_OUTPUT_MODEL=gpt-5.4-mini
TRADINGAGENTS_CODEX_WRITER_MODEL=gpt-5.4-mini
TRADINGAGENTS_CODEX_JUDGE_MODEL=gpt-5.5
TRADINGAGENTS_YOUTUBE_QUICK_MODEL=gpt-5.4-mini
TRADINGAGENTS_YOUTUBE_DEEP_MODEL=gpt-5.5
TRADINGAGENTS_YOUTUBE_OUTPUT_MODEL=gpt-5.4-mini
```

긴급 전체 롤백은 `TRADINGAGENTS_CODEX_MODEL=gpt-5.5`로 가능하지만, 모든 역할을 flagship 모델로 합치므로 비용 증가를 감수해야 한다.

## 이번 변경에서 제외한 항목

- 과거 실행 artifact, fixture, 비교 문서의 모델 문자열
- Pro mode, persisted reasoning, explicit prompt caching, Programmatic Tool Calling
- OpenAI API 요청 스키마나 Codex app-server 프로토콜 변경

이 항목들은 모델 역할 마이그레이션과 분리해 독립적인 실험과 검증 후 도입한다.
