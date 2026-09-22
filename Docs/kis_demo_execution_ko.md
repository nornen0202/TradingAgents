# 조건부 진입·수량 산정·KIS 모의투자 연결

2026-09-22 후속 개선: [간편 등록 안내](kis_demo_quickstart_ko.md), [외부 프로젝트 조사·적용 결과](external_trading_review_20260922_ko.md).
간편 등록 화면은 전용 정보를 Windows 사용자용으로 암호화하고 기존 환경변수/JSON보다 우선 사용한다.
로컬 일일 손실 제한은 기본적으로 보유분 축소만 허용하며, 수동 긴급 중단은 전체 주문을 정지한다.

기존 계좌를 기준으로 한 모의매매의 실행 준비 단계다. 수익 우위 검증이나 실거래 준비 완료를 뜻하지 않는다.
계좌·원장·접속정보는 저장소에 커밋하지 않고 비공개 로컬 경로에 둔다.

## 조건부 매수 의도

현재 `WAIT`와 조건 충족 후 `STARTER`/`ADD`를 별도로 저장한다. 기존 `BULLISH + WAIT`만으로 매수를 만들지 않는다.
구조화된 판단에 아래 필드를 추가할 수 있다. 예시는 가상값이며 현재 매수 지시가 아니다.

```json
{
  "portfolio_stance": "BULLISH",
  "entry_action": "WAIT",
  "risk_action": "HOLD",
  "conditional_entry_action": "STARTER",
  "conditional_entry_valid_until": "2026-09-21T15:00:00+09:00",
  "execution_levels": {
    "levels": [{"level_type": "BREAKOUT", "price": 70000, "confirmation": "intraday"}],
    "min_relative_volume": 1.2,
    "vwap_required": true,
    "earliest_pilot_time_local": "10:30"
  }
}
```

전체 판단의 기존 필수 필드도 필요하다. 명시적 숫자 진입 가격과 시간대가 있는 만료시각을 요구하며,
매도 위험 조치와 충돌하면 거부한다. 자연어에서 다른 진입 구간을 추가로 추출하지 않는다.
만료시각은 실행 계약과 아카이브 복원을 거쳐 유지된다.

현재 조건부 진입은 정규장 `intraday` 확인만 실행한다. 종가·두 봉 유지·다음 날 확인은 별도 증거가 없어 대기한다.
겹치는 지지 구간이 확인 요건이나 실패한 돌파를 우회할 수 없다. 거래량, VWAP, 실행자료 품질과 시간 조건도 유지한다.
미래 시각의 시세는 거부하며, 오래된 리포트의 과거 시각을 현재 시각으로 바꿔 재생하지 않는다.

## 수량과 한도

`sizing.py`는 명시적 정수 수량 또는 제안의 원화 예산과 신선한 가격으로 정수 주식을 계산한다.
신규 종목도 계산 가능하며, 예산에는 가격 여유와 비용을 반영한다. 한 주 예산이 부족하면 올림하지 않는다.
매도는 확인된 매도가능 수량 이내이며, 계좌 NAV·현금·시세 검증은 원장에서 다시 수행한다.

| 한도 | 기본값 | 의미 |
|---|---:|---|
| 신규 매수 주문 | NAV 1% | 기존 소규모 진입 한도 유지 |
| 매도 주문 | NAV 20% | 매수 한도 때문에 위험 축소가 불가능한 문제 분리 |
| 하루 회전 | NAV 10% | 매도에도 적용되므로 실제 허용량은 더 작을 수 있음 |
| 하루 주문 / 손실 | 5건 / 2% | 기존 차단 유지 |
| 단일 종목 / 현금 하한 | 35% / 250만원 | 모의 연구 설정 |
| 한 주 예외 | 비활성 | `one_share_nav_ceiling`을 별도 실험에 명시한 경우만 적용 |

한 주 예외도 충분한 명시 예산/수량이 필요하며 현금·회전·집중도 제한을 우회하지 않는다.
`paper_from_archive.py --limits <JSON>`으로 별도 한도를 지정한다. 한도가 바뀌면 **새 원장**을 사용한다.
이전 실험 원장을 덮어쓰거나 새로운 한도로 과거 성과를 이어 붙이지 않는다.

## KIS 모의투자 전용 연결

`kis_demo.py`는 VTS 주소와 국내주식 거래 ID만 허용한다. 실계좌 연결 코드와 키를 공유하지 않는다.
다음 네 설정을 환경변수 또는 기존 로컬 API 키 JSON 설정에 등록한다. 키 값은 채팅이나 Git에 남기지 않는다.

- `KIS_DEMO_APP_KEY`
- `KIS_DEMO_APP_SECRET`
- `KIS_DEMO_ACCOUNT_NO`: 모의계좌 앞 8자리
- `KIS_DEMO_PRODUCT_CODE`: 모의계좌 상품 코드 2자리

설정 파일은 `TRADINGAGENTS_API_KEYS_PATH`로 지정할 수 있다. `KIS_VTS_*` 별칭도 지원한다.
전용 값이 없을 때 실계좌 키로 대체하지 않는다.

```powershell
$env:PYTHONPATH='.'
python tools/check_kis_demo.py --connect --output .runtime/kis-demo-readiness.json
```

이 명령은 인증·잔고·당일 주문 조회만 수행한다. `MISSING_DEMO_SETTINGS`는 접속정보 부재,
`READ_CONNECTION_VERIFIED`는 조회 연결 검증 완료이며 주문/체결 검증을 의미하지 않는다.
2026-09-21 로컬 점검에서는 전용 설정 4개가 모두 없어 서버 검증을 진행하지 못했다. 전송 주문은 0건이다.

주문 전송 모듈은 명시된 수량·지정가·유효시간과 영속 의도 ID를 받는다. 주문 접수는 `ACKNOWLEDGED`로 저장하고,
당일 주문 조회로 `OPEN`·`PARTIAL`·`FILLED`·`CANCELLED`를 구분하여 별도 대사 기록을 남긴다.
응답 유실·불명확한 접수는 `UNKNOWN`으로 저장하며 재시작해도 재전송하지 않고 추가 전송도 차단한다.
주문번호를 확인할 수 없는 경우 수동 대사가 필요하다. 원장 삭제로 이 차단을 해제해서는 안 된다.
같은 계좌·원래 거래일의 주문만 대사하며 취소 접수를 취소 완료로 간주하지 않는다.

## 완료 범위와 남은 연결

로컬 원장 어댑터는 VTS 전송 모듈을 자동 호출하지 않는다. 전략·위험 검사·모의계좌 대사를 묶는 상시 실행도 아직 설치하지 않았다.
실계좌 복제 원장의 잔고와 증권사 모의계좌 잔고는 서로 다를 수 있으므로 그대로 주문을 복사하면 안 된다.
다음 단계는 전용 설정 후 조회 연결 검증, 모의계좌 잔고 대사, 제한된 주문→체결→취소 실증이다.
부분체결과 취소 경로는 가상 응답으로 검증했으며 실제 VTS 동작은 미검증이다.
공식 취소가능 조회 예제에는 VTS ID가 없어 실계좌 조회로 대체하지 않았다. 현재 취소 전에는 당일 주문의 잔량을 확인한다.
미국 주문 전송과 시간 검증된 미국 시세/환율 어댑터는 후속 작업이다.

공식 API 근거: [현금 주문](https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/order_cash/order_cash.py),
[당일 주문·체결](https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/inquire_daily_ccld/inquire_daily_ccld.py),
[정정·취소](https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/order_rvsecncl/order_rvsecncl.py).
