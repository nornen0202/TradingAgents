# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-09-28T14:27:15.761842+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20260928T231100_github-actions-overlay-us",
  "producer_finished_at": "2026-09-28T23:11:52.850413+09:00",
  "analysis_run_id": "20260925T212622_github-actions-us",
  "analysis_completed_at": "2026-09-26T00:04:22.912385+09:00",
  "analysis_trade_date_oldest": "2026-09-24",
  "analysis_trade_date_latest": "2026-09-24",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-09-28T10:10:00-04:00",
  "market_data_latest_at": "2026-09-28T10:10:00-04:00",
  "market_data_status": "FRESH"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-09-28T23:12:20.688368+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23858238,
    "total_market_value_krw": 24686930,
    "total_unrealized_pnl_krw": 828692,
    "settled_cash_krw": 0,
    "available_cash_krw": 975902,
    "buying_power_krw": 85852,
    "total_equity_krw": 25748651
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 551169,
      "current_price_krw": 601971,
      "market_value_krw": 7223654,
      "unrealized_pnl_krw": 609616
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 295419,
      "current_price_krw": 284454,
      "market_value_krw": 3128994,
      "unrealized_pnl_krw": -120617
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 428487,
      "current_price_krw": 460687,
      "market_value_krw": 2764123,
      "unrealized_pnl_krw": 193197
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 269976,
      "current_price_krw": 311756,
      "market_value_krw": 1870538,
      "unrealized_pnl_krw": 250681
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1899208,
      "current_price_krw": 1808475,
      "market_value_krw": 1808475,
      "unrealized_pnl_krw": -90733
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 561617,
      "current_price_krw": 590878,
      "market_value_krw": 1772634,
      "unrealized_pnl_krw": 87782
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1487930,
      "current_price_krw": 1287358,
      "market_value_krw": 1287358,
      "unrealized_pnl_krw": -200572
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 135891,
      "current_price_krw": 136092,
      "market_value_krw": 1224830,
      "unrealized_pnl_krw": 1806
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 368303,
      "current_price_krw": 462789,
      "market_value_krw": 925579,
      "unrealized_pnl_krw": 188973
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 669517,
      "current_price_krw": 730242,
      "market_value_krw": 730242,
      "unrealized_pnl_krw": 60725
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1434485,
      "current_price_krw": 1605946,
      "market_value_krw": 700296,
      "unrealized_pnl_krw": 74767
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 575444,
      "current_price_krw": 474092,
      "market_value_krw": 474092,
      "unrealized_pnl_krw": -101352
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 137604,
      "current_price_krw": 110755,
      "market_value_krw": 443023,
      "unrealized_pnl_krw": -107394
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 351303,
      "current_price_krw": 333092,
      "market_value_krw": 333092,
      "unrealized_pnl_krw": -18211
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":951.86,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":951.0501677515556,"relative_volume":0.5845299160641179,"spread_bps":16.409652241601194,"day_high":955.46,"day_low":944.855,"execution_condition_ko":"962.85달러, 971.34달러, 974.48달러의 순차적 회복 / 984.16달러 위에서 2439000주 초과 거래량을 동반한 종가와 다음 거래일 지지","risk_condition_ko":"931.94 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1337.605,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":1349.7746776763727,"relative_volume":0.34515613228121,"spread_bps":18.941152439137284,"day_high":1359.76,"day_low":1336.84,"execution_condition_ko":"MPWR의 현재 가격, 거래량가중평균가격, 거래량, 가치평가 및 기존 보유 비중 확인 / 미국 동부시간 10:30 이후 1373.16 회복과 거래량 조건 확인 시 소규모 시험 매수 재검토","risk_condition_ko":"1,302.59 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":437.545,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":439.5804022738522,"relative_volume":0.6133838366427282,"spread_bps":18.00221039798604,"day_high":441.94,"day_low":435.02,"execution_condition_ko":"443.64 초과 종가와 일일 거래량 2614300주 초과 / 447.47 초과 종가 이후 다음 거래일 지지 확인","risk_condition_ko":"425.81 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":445.415,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":447.4037992226171,"relative_volume":0.44544676671502703,"spread_bps":3.360553819270179,"day_high":449.6,"day_low":445.415,"execution_condition_ko":"정규장 10:30 이후 454.66 돌파, 당일 거래량가중평균가격 상회 및 상대 거래량 1.2 이상 / 454.66 초과 종가와 일일 거래량 11,256,000주 이상, 다음 거래일 지지 또는 재돌파","risk_condition_ko":"438.29 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":100.67,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":100.66427689518822,"relative_volume":1.5193517914195387,"spread_bps":0.9933939303635938,"day_high":100.67,"day_low":100.66,"execution_condition_ko":"2026-09-28 10:30 이후 100.63 상향 유지, 상대거래량 1.2 이상 및 장중 거래량가중평균가 상회 / 100.67 위 종가 이후 다음 거래일 첫 30~60분 동안 100.67 유지","risk_condition_ko":"100.54 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":245.855,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":245.90388735624109,"relative_volume":1.1941311546670188,"spread_bps":0.8143985666589394,"day_high":246.87,"day_low":244.725,"execution_condition_ko":"2026-10-02T16:00:00-04:00 전 $252.96 상향 돌파, 실시간 거래량가중평균가 유지, 상대거래량 1.2 이상 확인 / 거래량 증가를 동반한 $256.18 초과 종가와 다음 거래일 지지 확인","risk_condition_ko":"245.2 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":210.37,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":209.771283721245,"relative_volume":1.141793382667417,"spread_bps":0.4763379141158408,"day_high":210.48,"day_low":209.06,"execution_condition_ko":"최신 RSP 가격, 매수·매도 호가 차이, 순자산가치와의 괴리, 보유량 및 현금 확인 / 211.23 회복 후 212.53 위 종가 확인","risk_condition_ko":"209.81 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":81.8901,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":82.08238550789005,"relative_volume":1.3616439312018802,"spread_bps":1.2163230554041373,"day_high":82.29,"day_low":81.8338,"execution_condition_ko":"83.94와 83.77의 종가 지지 여부를 확인한다. / 84.80, 85.17, 85.63의 순차 회복과 85.89의 거래량 동반 돌파를 확인한다.","risk_condition_ko":"83.77 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":340.605,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":341.99634355434205,"relative_volume":0.777458860344901,"spread_bps":2.338907730089583,"day_high":343.59,"day_low":340.2701,"execution_condition_ko":"GOOGL이 거래량 개선과 함께 344.57 위로 마감하면 매수 가능성을 재평가 / GOOGL이 상대 거래량 1.2 이상으로 354.77 위에서 마감하고 다음 거래일에도 지지되면 위험 축소 사유 해소 여부를 재평가","risk_condition_ko":"354.77 이탈 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":350.9146,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":352.4511595138444,"relative_volume":0.7011096218861951,"spread_bps":4.546875444031516,"day_high":355.85,"day_low":350.85,"execution_condition_ko":"355.15 위 종가와 상대 거래량 1.2 이상 / 366.55~367.27 위 종가, 다음 거래일 지지 및 손익비 재평가","risk_condition_ko":"346.89 이탈 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":1185.28,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":1185.242657073778,"relative_volume":0.5742100929585917,"spread_bps":9.893496928365778,"day_high":1192.959,"day_low":1172.56,"execution_condition_ko":"1197.79 상회 유지와 상대거래량 1.2 이상 및 거래량가중평균가격 지지 / 1197.79 상회 종가와 다음 거래일 유지 또는 재돌파","risk_condition_ko":"1,151 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":230.815,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":231.1508790796996,"relative_volume":2.0600389361551397,"spread_bps":2.1578231879684684,"day_high":233.21,"day_low":229.4975,"execution_condition_ko":"221.09~222.82 지지 후 224.94 회복 여부 / 230.14 위 종가와 갱신한 5일 평균 초과 거래량, 이후 233.17 및 234.50 시험 여부","risk_condition_ko":"221.09 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":341.82,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":341.79213491291694,"relative_volume":0.8656132426663686,"spread_bps":2.0456770460438074,"day_high":342.988,"day_low":340.17,"execution_condition_ko":"334.16~334.30 시험 후 334.30 위 일일 종가 / 345.34 위 일일 종가와 최근 10일 평균의 1.2배 이상 거래량","risk_condition_ko":"329.86 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":542.53,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":548.9668502742129,"relative_volume":0.5585645002965817,"spread_bps":13.337840183439233,"day_high":556.785,"day_low":542.1801,"execution_condition_ko":"547.37 및 551.69 위 거래량 증가를 동반한 일간 종가 / 다음 거래일 첫 30~60분 동안 551.69 지지 또는 재돌파","risk_condition_ko":"530.45 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"ANET","display_name":"Arista Networks","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":204.155,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":205.61738355209152,"relative_volume":0.41461679380115146,"spread_bps":10.69986868342974,"day_high":208.2,"day_low":204.155,"execution_condition_ko":"미국 동부시간 10:30 이후 197.81 재시험과 지지, 당일 거래량가중평균가 상회 및 동시간대 상대거래량 1.2 이상 / 208.38 위 일봉 마감과 거래량 4786000주 초과","risk_condition_ko":"197.81 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"CRM","display_name":"Salesforce","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":228.0,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":224.39205684751238,"relative_volume":1.069217633854454,"spread_bps":9.341844791921883,"day_high":228.12,"day_low":221.18,"execution_condition_ko":"CRM의 242.09 회복 및 245.59 거래량 동반 돌파 / 236.25~237.00과 229.81~230.42 지지 구간 시험","risk_condition_ko":"229.81 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":264.865,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":264.75771350644925,"relative_volume":0.26571482406444036,"spread_bps":17.398540035552767,"day_high":265.715,"day_low":263.38,"execution_condition_ko":"269.43 초과 종가와 4,184,895주 초과 거래량 / 다음 거래일 첫 30~60분 동안 269.39~269.43 유지 또는 회복","risk_condition_ko":"263.05 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":370.13,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":368.52257095143887,"relative_volume":0.5375056627176347,"spread_bps":5.6857409738856495,"day_high":370.31,"day_low":366.0604,"execution_condition_ko":"과거 기준 369.27 회복과 370.90–371.81 위 거래량 동반 종가 확인 / 다음 거래일 첫 30–60분 동안 돌파 구간과 당일 거래량가중평균가격 유지 확인","risk_condition_ko":"359.8 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":97.26,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":97.19470053800381,"relative_volume":1.511670068885404,"spread_bps":1.029495032686994,"day_high":97.44,"day_low":96.83,"execution_condition_ko":"94.10~95.04 지지 후 95.04 회복과 동시간대 상대거래량 1.2 이상 / 96.76 위 거래량 동반 종가와 다음 거래일 유지","risk_condition_ko":"94.1 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"KO","display_name":"KO","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":87.65,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":87.36573766167176,"relative_volume":0.456539895878068,"spread_bps":2.288853284504008,"day_high":87.69,"day_low":87.05,"execution_condition_ko":"89.36 위 종가와 직전 10거래일 평균의 1.2배 이상 거래량, 이후 89.82 돌파 여부 / 87.12~87.03 지지 구간 및 86.99의 50일 평균선 유지 여부","risk_condition_ko":"87.03 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":193.08,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":192.1427420313594,"relative_volume":0.2759813629170097,"spread_bps":20.280283923974224,"day_high":193.08,"day_low":189.69,"execution_condition_ko":"$195.50 위 종가와 상대 거래량 1.2 이상, 다음 거래일 $194.70 유지 및 $195.50 재돌파 / $189.20–$190.10 재시험 후 종가 기준 지지와 비용 차감 후 유리한 손익비","risk_condition_ko":"189.2 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":569.22,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":567.4887360349545,"relative_volume":0.2773400593334385,"spread_bps":4.755404869886519,"day_high":569.52,"day_low":563.5,"execution_condition_ko":"$568.50 회복 후 $571.35 위에서 최소 2,598,480주를 동반한 종가 / 돌파 다음 거래일 첫 30~60분 동안 $571.35 유지 또는 재돌파","risk_condition_ko":"553.12 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":162.93,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":162.93745205881874,"relative_volume":0.5373035663214142,"spread_bps":6.752401706516905,"day_high":163.54,"day_low":162.05,"execution_condition_ko":"158.69~159.50 재시험에서 158.69 유지, 현재 거래량가중평균가 회복 및 상대거래량 1.2 이상 / 164.91 위 일간 종가와 상대거래량 1.2 이상: 매수 확정이 아닌 후속 확인 신호","risk_condition_ko":"155.74 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"JNJ","display_name":"JNJ","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":272.16,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":271.52218377525975,"relative_volume":0.8387869853330143,"spread_bps":11.786372007368325,"day_high":273.25,"day_low":269.27,"execution_condition_ko":"275.23 회복 후 상대거래량 1.2 이상을 동반한 276.34 상향 종가 / 278.89와 281.07 돌파 및 다음 거래일 지지","risk_condition_ko":"265.04 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":207.63,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":207.0001618253904,"relative_volume":0.5704553710246162,"spread_bps":3.384176557325204,"day_high":207.785,"day_low":206.1,"execution_condition_ko":"208.10 재돌파 후 실시간 거래량가중평균 유지와 상대 거래량 1.2 이상 / 210.05 위 종가, 비교 가능한 정규장 거래량 9,382,800주 초과 및 다음 거래일 지지","risk_condition_ko":"203.48 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

```json
{"ticker":"WBD","display_name":"WBD","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":30.845,"market_data_asof":"2026-09-28T10:10:00-04:00","session_vwap":30.856032808502405,"relative_volume":2.7863655046624025,"spread_bps":3.239915762190689,"day_high":30.88,"day_low":30.84,"execution_condition_ko":"WBD 일일 종가 $30.92 초과 및 거래량 46,106,500주 초과 / $30.68~$30.71 시험 후 확인된 반등; 단순 접촉은 진입 신호가 아님","risk_condition_ko":"30.68 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T10:40:00-04:00"}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-09-28T23:25:11.001664+09:00",
  "as_of": "2026-09-25T15:10:00-04:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
