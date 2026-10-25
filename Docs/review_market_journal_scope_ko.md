# 보관 차트의 시장별 내부 모의 원장 분리

2026-10-26. 실제 390px 화면 검증에서 종목 목록은 표시됐지만 첫 종목의 snapshot이 HTTP422로 실패했다. 실제 첫 종목은 `000100.KS`였으며 선택 원본은 `20261023T144024_pre-report-kr-overlay`다.

## 원인과 수정 경계

설치된 `local_automation review`는 공통 `performance.sqlite`와 별도 내부 모의계좌인 `paper/kr.sqlite`, `paper/us.sqlite`를 하나의 `db_paths`에 전달했다. 두 내부 원장은 각각 `paper:account_seed`라는 같은 event ID를 사용하고 mode와 평가 통화도 모두 `paper / KRW`다. 시각과 원문이 달라 replay의 원래 `Conflicting lifecycle evidence across journals` 검사가 실패했다. 미국 내부 모의계좌도 원화로 평가하므로 통화별 분리만으로 해결할 수 없다.

직접 snapshot 호출은 원장 없이 또는 각 원장 단독일 때 정상이었고 세 원장을 합쳤을 때만 실패했다. 이 충돌은 서로 다른 계좌를 합치지 않도록 막는 정상 검증이다. 과거 seed ID나 원장을 수정하거나 충돌 행을 버리지 않는다.

수정한 서버는 공통 연구·추천 tracker와 `market_journals={KR:한국 내부 원장, US:미국 내부 원장}`을 명시적으로 구분한다. snapshot에 선택된 완료 원본의 시장과 순수 로컬 종목 resolver의 국가를 대조한 뒤 공통 tracker와 해당 시장의 내부 원장 한 개만 읽는다. 시장이 없거나 일치하지 않거나 해당 mapping이 없으면 `Archive journal market scope unverified`로 HTTP422를 반환한다. 다른 시장 원장이나 두 계좌 전체로 fallback하지 않는다. URL의 market/journal 인자로 원장을 바꿀 수 없다.

기존 단일 계좌의 `--journal`/`--tracker-db` 방식은 유지한다. 시장을 구분할 때는 공통 tracker만 `--journal`로 지정하고 `--paper-journal-kr`, `--paper-journal-us`에 각각 한 계좌를 지정할 수 있다. 같은 paper 원장을 두 시장에 등록하면 시작 단계에서 거절한다. 원래 replay의 동일 사건 충돌·중복 계좌 seed·PIT·정산 검증은 그대로다.

이번 변경은 읽기 전용 보관 화면의 입력 범위를 고친다. 정상 전략 주문이나 원래 승인·시장 달력·브로커·비용 정책을 바꾸지 않는다. 원래 봉·이벤트의 검증 실패를 무시하거나 미래·불량 봉을 표시하지 않는다. source market을 확인할 수 없는 보관자료를 임의의 시장으로 추정하지 않는다.

## 검증

- 같은 seed ID·같은 KRW·다른 원문의 두 계좌 fixture에서 기존 flat replay와 HTTP422를 재현했다. 수정 후 KR·US snapshot이 공통 tracker와 해당 계좌만 읽어 HTTP200을 반환하며 다른 계좌의 seed·보유분·현금·경로가 응답에 노출되지 않는다.
- 알 수 없는/다른 source market, mapping 누락·오류·공유 계좌, 미래/잘못된/시간대 없는 cutoff를 거절한다. 미래 원본·사건이 과거 조회 결과를 바꾸지 않는지 확인했다. 기존 단일 계좌 CLI와 설치된 review 호출의 시장 바인딩, root의 기존 `strategy_ledger_dir` 전달도 검증했다.
- 관련 새/기존 테스트 79개, Ruff·diff 검사가 통과했다. 이 수는 root의 다른 비용·화면 검사 수와 중복 합산하지 않는다.
- 실제 정본을 대상으로 새 catalog 전체 탐색 없이 알려진 두 원본과 선택된 원장만 읽어 직접 snapshot을 확인했다. KR `000100.KS`: series2/검증 봉289개, US `AAPL`: series1/검증 봉260개, 양쪽 rejected_bars 없음, read_only true/주문 전송0, 계좌 전체 자료 노출 없음. 같은 세 DB의 전후 SHA도 보존해 대조했다. 미국 원본은 `20261023T232607_local-scheduler-us-full`이다. 이는 보관자료 조회이며 현재 신선한 정상 연구나 승인·체결의 증거가 아니다.

실제 읽기 영수증: `G:/TradingAgentsData/migration-audits/review-market-journal-actual-replay-20261026.json`, SHA256 `ebec31af32a9c27f70f7c8df3d41c11e50d26be578458150b7502bd5a18a38ad`.

이 작업 자체에서는 production 서버 재시작·배포·브로커 호출·운영 원본 수정이 없다. 최종 head CI·배포와 실제 8766 화면의 390/1440px 검증은 root가 별도로 수행한다. 첫 화면의 약5초 지연은 root의 별도 조사 항목이며 이 원장 수정으로 해결됐다고 주장하지 않는다.
