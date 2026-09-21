# 리포트 성과 감사와 로컬 모의매매

리포트의 상승/하락 전망, 현재 실행 가능성, 실제 체결 성과를 분리한다.
이 기능은 **로컬 연구·모의매매 전용**이며 KIS 실계좌/VTS 주문을 전송하지 않는다.
개인 리포트, 계좌 복제본, 가격 캐시와 원장은 `.runtime/` 등 비공개 위치에 저장한다.

## 구성

- `tools/audit_strategy_history.py`: 원본 아카이브·Work 집계. 장중 복제 논지는 ticker와 analysis_asof로 중복 제거한다.
- `tools/evaluate_report_signals.py`: 현지일 첫 리포트의 발표 이후 첫 개장부터 1/5/10일 가격 움직임. 조건 충족/체결 증명이 아니며 중첩 수익을 복리 연결하지 않는다.
- `tradingagents/execution/research_backtest.py`: 전일 종가 신호, 다음 시가 체결, 현금·거래비용을 반영한 장기 연구.
- `tools/backtest_strategy_candidates.py`: 고정된 추세·모멘텀·보유 기준선 6개, 개발/평가 구간 및 편도 10/30bp 비용 가정.
- `tradingagents/execution/paper.py`: 현재 계좌를 복제한 SQLite 모의 원장. 제안 생성과 이후 시세 체결을 분리한다.
- `tools/run_paper_trading.py`: 명시적인 JSON 입력으로 원장 초기화/진행.
- `tools/paper_from_archive.py`: 완료된 정본 실행의 KIS 기반 시세·명시적 정수 수량 제안을 소비한다.

## 실행

프로젝트 가상환경에서 저장소 루트를 Python import 경로에 둔다.

```powershell
$env:PYTHONPATH='.'
python tools/audit_strategy_history.py --archive C:/TradingAgentsData/archive --output .runtime/strategy-audit
python tools/backtest_strategy_candidates.py --prices .runtime/strategy-audit/etf_prices.pkl --output .runtime/strategy-audit
python tools/evaluate_report_signals.py --archive C:/TradingAgentsData/archive --directory .runtime/strategy-audit
python tools/paper_from_archive.py --run <완료된-run-디렉터리> --ledger .runtime/paper-kr.sqlite --output .runtime/paper-kr.json --seed
```

`--seed`는 새 원장의 첫 실행에만 사용한다. 다음 실행은 같은 원장을 사용하고 `--seed`를 뺀다.
다른 실험/한도/계좌에는 다른 원장을 사용한다. 실제 계좌를 다시 읽어서 모의 체결 내역을 덮어쓰지 않는다.
`--run`은 생산자가 파일 쓰기를 완료한 성공 실행이어야 한다. 이 명령을 호출하는 상시 작업은 자동 설치하지 않는다.

가격 캐시는 로컬에서 직접 생성한 신뢰 가능한 pandas 피클만 허용한다. 외부에서 받은 피클을 열지 않는다.
ETF 캐시는 yfinance의 `download(..., auto_adjust=True)` 결과로 Open/Close 컬럼 수준과 ticker 컬럼 수준을 가진다.
원본 분석은 `analysis_asof`와 최초 보관 실행의 `finished_at` 중 늦은 시각, Work는 `published_at`을 사용한다.
장전 분석이어도 실행이 장중에 끝났다면 이미 지난 당일 시가로 진입하지 않는다.
이벤트 평가는 저장된 `source_manifest.json`의 Work 파일 목록을 적용해 이후 추가 보고서를 섞지 않는다.

## 모의 입력 계약

```json
{
  "now": "2026-09-21T10:00:00+09:00",
  "quotes": {
    "005930.KS": {
      "as_of": "2026-09-21T10:00:00+09:00",
      "price_krw": 70000,
      "session": "regular",
      "executable": true,
      "spread_bps": 5
    }
  },
  "signals": [{
    "signal_id": "example-only-plan-1",
    "ticker": "005930.KS",
    "action": "BUY",
    "quantity": 1,
    "execution_ready": true,
    "available_at": "2026-09-21T09:59:00+09:00",
    "valid_until": "2026-09-21T10:02:00+09:00"
  }],
  "halted": false
}
```

예시 숫자는 가상 데이터이며 현재 주문 지시가 아니다. quote의 실행 가능성과 정규장 여부는 검증된 어댑터가 제공해야 한다.
모든 보유 종목의 신선한 평가가격이 없으면 신규 매수를 막는다. 미래/지연 시각, 부족한 현금, 없는 수량을 정상값으로 채우지 않는다.
매도 수량도 명시적으로 받아 보유 정수 주식 수 이내로 제한한다. 기존 소수 주식 잔여분은 평가액으로 보존한다.
계좌 NAV에는 평가용 현금이 포함될 수 있으므로 별도로 매수가능액을 제한한다. 시장별 원화 현금이 중복될 수 있어 합산 금지.

## 기본 모의 한도와 한계

기본값은 주문당 NAV 1%, 하루 회전 10%, 하루 5건, 하루 손실 2%, 단일 종목 35%, 현금 하한 250만원이다.
이 기본값은 최적화되거나 실계좌 승인된 설정이 아니다. 고가 주식은 한 주가 한도를 넘으면 주문하지 않는다.
필요한 위험 축소가 이 때문에 실행되지 않으면 거부 사유를 검토하고 별도 실험에서 정책을 변경한다.

모의 체결은 주문보다 엄격히 이후인 신선한 시세에만 가능하다. 스프레드 절반과 슬리피지를 불리한 방향으로 반영하며
지정가를 벗어나면 대기한다. 만료/긴급 중단 주문은 취소한다. 의도 ID를 영속 저장해 재시작/중복 입력을 방지한다.
수수료·매도세는 연구 가정이다. 부분체결·주문 대기열·호가 잔량·결제일·배당 지급·환전 체결은 구현하지 않았다.
매도대금은 즉시 재사용하는 단순화가 있다. 산업/상관군 한도, 증권사 주문 대사, 운영 알림도 별도 구현이 필요하다.

미국 계좌는 원화 평가액으로 복제 가능하나 아카이브 어댑터의 미국 실시간 FX/호가 변환은 연결하지 않았다.
미국 모의 체결을 위해서는 독립적으로 시간 검증된 `price_krw` 입력이 필요하다. 지연 시세의 실행 승격은 금지한다.
KR VTS 주문 preview는 공식 예제의 요청 매핑을 확인하는 순수 함수이며 계좌번호/토큰이나 전송 기능을 포함하지 않는다.

## 실증 단계

1. 동일 현금흐름/통화/평가시각의 기존 계좌 보유 기준선과 모의 전략을 대조한다.
2. 명시적 조건·수량·유효시간을 확보하고 실행자료/원장 오류를 없앤다.
3. 비용·구독료 차감 성과, 낙폭, 놓친 수익과 회피 손실을 함께 검토한다.
4. 독립 미래 표본이 쌓이기 전 수익 우위나 실거래 준비 완료를 주장하지 않는다.

공식 참고: [KIS 예제](https://github.com/koreainvestment/open-trading-api),
[QuantConnect 체결 모형](https://www.quantconnect.com/docs/v2/writing-algorithms/reality-modeling/trade-fills/key-concepts),
[다중 실험 선택 편향](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf).
