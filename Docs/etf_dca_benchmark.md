# 동일 입금일 ETF 대체 포트폴리오 벤치마크

이 기능은 "같은 입금일에 같은 금액으로 ETF를 샀다면?"을 계산합니다. 기간 시작일에 한 번 투자한 지수 수익률과 달리, 실제 계좌의 날짜별 입금/출금 흐름을 그대로 사용하므로 큰 중간 입금이 있었던 계좌를 더 공정하게 비교할 수 있습니다.

## 필요한 데이터

- 날짜별 현금흐름: `date,type,amount_krw` 형식의 CSV 또는 JSON
- ETF 가격 시계열: KOSPI200, KOSDAQ150, S&P500, Nasdaq100, blended benchmark 구성 ETF
- 해외상장 ETF를 쓰는 경우: USD/KRW 같은 FX 시계열
- 실제 계좌 성과: 한국투자증권 앱 기준 broker performance가 있으면 이를 우선 사용합니다.

KIS 기간손익 summary의 총입금액만 있고 입금 날짜가 없으면 exact benchmark는 계산하지 않습니다. 총액을 임의 날짜에 배정하면 DCA 비교가 왜곡되기 때문입니다.

동일 기간의 날짜별 입출금 합계가 브로커 총액과 일치해야 합니다. 실제 계좌의 배당·세금·FX 이체는 벤치마크 현금흐름에서 제외합니다. 해외 ETF 가상 체결에는 그 거래일의 명시된 FX 페어(예: USD/KRW)만 사용합니다. 보고서는 ETF와 실제 계좌의 세후 비교 가능성이 확인될 때까지 이를 미검증으로 표시합니다.

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

## ETF 일봉·환율 정규 공급

정규 포트폴리오의 Yahoo 가격 경로는 종목별 일봉 응답의 심볼·통화, 배당 및 분할 열을 검사합니다. 거래소 캘린더에서 분석 기준 시각까지 종가가 확정된 세션만 포함합니다. 휴일 납입은 다음 거래일 종가로 이월하고, 정상 거래일 봉이 빠진 시계열은 해당 ETF 계산에서 제외합니다. 공급자가 반환한 조정 종가에 분배금이 반영되므로 분배금을 다시 더하지 않습니다. 각 ETF의 관측 범위, 수집 시각, 거래소, 조정 기준과 해시를 결과에서 확인할 수 있습니다. [Yahoo history API](https://ranaroussi.github.io/yfinance/reference/yfinance.price_history.html)

직접 설정한 환율 원천이 없으면 Yahoo `KRW=X`의 검증된 KRW 표시 응답을 사용합니다. 단위는 USD 1당 KRW이고, 거래일 이전의 최신 유효 일자 값으로 환산합니다. 이 값은 연구용 환산 기준이며 브로커 적용환율과 결제 시각은 별도입니다. 원본 가격 캐시는 아카이브의 `benchmark-series` 아래 두며 계좌 자료를 저장하지 않습니다. 새 수집의 조정값은 과거 시점 원본 보존과 구분하므로 결과에 historical vintage 미검증을 표시합니다.

여섯 단일 ETF 결과와 기존 혼합 결과를 함께 보존합니다. 정규 계좌 원장의 입·출금 날짜와 금액은 동일 기간 브로커 합계에 대사합니다. 입출금 내역의 완전성 근거가 없으면 연구용 수익률만 표시하고 정확 비교, 초과수익 및 정책 판단을 보류합니다. 보고서의 수익률은 조정 가격, 설정된 거래비용과 적용 환율에 따른 연구 결과이며 실제 계좌와 동일한 세후 수익률은 증빙이 확보되는 범위에서만 비교할 수 있습니다.
