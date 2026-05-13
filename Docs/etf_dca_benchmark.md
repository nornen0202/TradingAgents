# 동일 입금일 ETF 대체 포트폴리오 벤치마크

이 기능은 "같은 입금일에 같은 금액으로 ETF를 샀다면?"을 계산합니다. 기간 시작일에 한 번 투자한 지수 수익률과 달리, 실제 계좌의 날짜별 입금/출금 흐름을 그대로 사용하므로 큰 중간 입금이 있었던 계좌를 더 공정하게 비교할 수 있습니다.

## 필요한 데이터

- 날짜별 현금흐름: `date,type,amount_krw` 형식의 CSV 또는 JSON
- ETF 가격 시계열: KOSPI200, KOSDAQ150, S&P500, Nasdaq100, blended benchmark 구성 ETF
- 해외상장 ETF를 쓰는 경우: USD/KRW 같은 FX 시계열
- 실제 계좌 성과: 한국투자증권 앱 기준 broker performance가 있으면 이를 우선 사용합니다.

KIS 기간손익 summary의 총입금액만 있고 입금 날짜가 없으면 exact benchmark는 계산하지 않습니다. 총액을 임의 날짜에 배정하면 DCA 비교가 왜곡되기 때문입니다.

## Manual CSV 예시

```csv
date,type,amount_krw,currency,description
2026-04-13,DEPOSIT,10000000,KRW,initial deposit
2026-04-20,DEPOSIT,5000000,KRW,monthly contribution
2026-05-02,WITHDRAWAL,200000,KRW,withdrawal
```

지원 alias:

- `date`, `event_date`
- `type`, `cashflow_type`
- `amount_krw`, `amount`, `amount_local`
- `description`, `memo`, `note`

## 설정

```toml
[etf_dca_benchmarks]
enabled = true
require_dated_cashflows = true
cashflow_source = "auto"
manual_cashflow_csv_path = "config/account_cashflows.csv"
price_history_path = "config/etf_prices.json"
fx_history_path = ""
period_start = ""
period_end = ""
price_basis = "close"
cashflow_trade_timing = "same_day_close"
withdrawal_policy = "pro_rata_current_weights"
min_initial_seed_krw = 10000
reinvest_dividends = true
show_in_portfolio_report = true
generate_standalone_report = true
core_satellite_policy_enabled = true

[etf_dca_benchmarks.instruments.kospi200]
display_name = "KOSPI200 ETF"
ticker = "069500.KS"
market = "KR"
currency = "KRW"

[etf_dca_benchmarks.portfolios.blended_default]
display_name = "혼합 벤치마크"
weights = { kospi200 = 0.35, kosdaq150 = 0.15, sp500_krw = 0.30, nasdaq100_krw = 0.20 }
```

기본 ETF ticker는 설정 예시이며, 운용 계좌에 맞게 override할 수 있습니다. 가격 조회에 실패한 ETF는 0으로 대체하지 않고 unavailable로 표시합니다.

## 산출물

- `etf_dca_comparison.json`: 실제 계좌와 ETF 대체 포트폴리오 비교 요약
- `etf_dca_benchmark_results.json`: 벤치마크별 결과
- `etf_dca_policy_recommendation.json`: core/satellite 정책 판정
- `etf_alternative_portfolios_public.json`: 투자자 화면용 public payload
- `etf_alternative_portfolios_raw.json`: private 진단 payload
- `cashflows_audit.json`: 날짜별 현금흐름 사용 가능 여부와 경고
- `etf_dca_benchmark_transactions.json`: 가상 ETF 매수/매도 체결 내역
- `etf_dca_equity_curves.json`: 벤치마크별 equity curve

날짜별 현금흐름 원장은 민감할 수 있으므로 기본 portfolio page에는 집계값과 이벤트 marker만 표시합니다. raw cashflow와 가상 거래 내역은 private artifact로 남기며, public 비교 JSON에는 금액 없는 marker와 equity curve만 포함합니다.

## 정책 판정

리포트는 다음 규칙을 report-only로 계산합니다.

- 3개월 연속 blended benchmark 언더퍼폼: 신규 개별 종목 매수 중단 권고
- 6개월 누적 초과수익 음수: 개별 종목 sleeve를 10~15% 수준으로 축소 권고
- 12개월 수익률, MDD, 회전율이 모두 불리: ETF core 중심 전환 권고
- ADD/STARTER 액션 성과가 ETF보다 낮음: TradingAgents 매수 신호를 관찰용으로 강등 권고

기본값은 주문 실행이나 자동 ETF 매수를 하지 않습니다.
