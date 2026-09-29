# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-09-29T04:58:23.828810+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20260929T060104_github-actions-overlay-us",
  "producer_finished_at": "2026-09-29T06:01:33.175257+09:00",
  "analysis_run_id": "20260929T020356_github-actions-us",
  "analysis_completed_at": "2026-09-29T04:33:13.882368+09:00",
  "analysis_trade_date_oldest": "2026-09-25",
  "analysis_trade_date_latest": "2026-09-25",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-09-28T15:45:00-04:00",
  "market_data_latest_at": "2026-09-28T15:45:00-04:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-09-29T06:01:33.206496+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23858238,
    "total_market_value_krw": 24784075,
    "total_unrealized_pnl_krw": 925837,
    "settled_cash_krw": 0,
    "available_cash_krw": 975902,
    "buying_power_krw": 85852,
    "total_equity_krw": 25845829
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 551169,
      "current_price_krw": 612293,
      "market_value_krw": 7347525,
      "unrealized_pnl_krw": 733487
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 295419,
      "current_price_krw": 283568,
      "market_value_krw": 3119253,
      "unrealized_pnl_krw": -130358
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 428487,
      "current_price_krw": 463398,
      "market_value_krw": 2780388,
      "unrealized_pnl_krw": 209462
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 269976,
      "current_price_krw": 309418,
      "market_value_krw": 1856512,
      "unrealized_pnl_krw": 236655
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1899208,
      "current_price_krw": 1826822,
      "market_value_krw": 1826822,
      "unrealized_pnl_krw": -72386
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 561617,
      "current_price_krw": 583266,
      "market_value_krw": 1749798,
      "unrealized_pnl_krw": 64946
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1487930,
      "current_price_krw": 1284089,
      "market_value_krw": 1284089,
      "unrealized_pnl_krw": -203841
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 135891,
      "current_price_krw": 136105,
      "market_value_krw": 1224952,
      "unrealized_pnl_krw": 1928
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 368303,
      "current_price_krw": 457516,
      "market_value_krw": 915033,
      "unrealized_pnl_krw": 178427
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 669517,
      "current_price_krw": 734717,
      "market_value_krw": 734717,
      "unrealized_pnl_krw": 65200
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1434485,
      "current_price_krw": 1601822,
      "market_value_krw": 698498,
      "unrealized_pnl_krw": 72969
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 575444,
      "current_price_krw": 472618,
      "market_value_krw": 472618,
      "unrealized_pnl_krw": -102826
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 137604,
      "current_price_krw": 110269,
      "market_value_krw": 441076,
      "unrealized_pnl_krw": -109341
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 351303,
      "current_price_krw": 332794,
      "market_value_krw": 332794,
      "unrealized_pnl_krw": -18509
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1343.715,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":1341.317846025638,"relative_volume":0.2246921185389703,"spread_bps":16.097863138488695,"day_high":1359.76,"day_low":1320.91,"execution_condition_ko":"1387.46 위 종가, 거래량 643920 이상, 확인된 상대거래량 1.2 이상 / 1329.47 지지 또는 재탈환","risk_condition_ko":"1,303.82 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":452.94,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":449.5902692895828,"relative_volume":0.2166261659281011,"spread_bps":2.6464361326747654,"day_high":455.2718,"day_low":443.11,"execution_condition_ko":"현재 TSM 가격·거래량·당일 거래량 가중평균가격·이동평균·이전 고점 갱신 / 457.68 상향 돌파와 상대거래량 1.2 이상, 이후 종가 확인 및 다음 거래일 455.03 유지","risk_condition_ko":"440.53 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":246.1,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":246.40486853864294,"relative_volume":0.414949580927407,"spread_bps":0.8128429181064918,"day_high":247.7699,"day_low":244.725,"execution_condition_ko":"252.37 신규 돌파와 실시간 거래량가중평균가격 상회 및 시간 보정 상대 거래량 1.2 이상 / 256.18 위 일일 종가와 거래량 41059560주 이상, 이어지는 다음 거래일 지지","risk_condition_ko":"244.3 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":349.3999,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":350.83463043518583,"relative_volume":0.31044715340050916,"spread_bps":1.1429551104386222,"day_high":355.85,"day_low":347.32,"execution_condition_ko":"최신 AVGO 가격으로 349.43 지지 여부 확인 / 362.90을 거래량 25.66백만 주 초과로 종가 돌파한 뒤 다음 정규장 지지 확인","risk_condition_ko":"349.43 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":209.795,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":209.84592623573616,"relative_volume":0.4489038009652373,"spread_bps":0.4765422097257931,"day_high":210.77,"day_low":209.04,"execution_condition_ko":"RSP의 최신 가격과 당일 거래량·가격 가중 평균을 확인 / RSP가 상대 거래량 1.2 이상으로 212.83 위에서 마감하고 다음 거래일에도 유지","risk_condition_ko":"209.81 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":430.015,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":431.0656142945503,"relative_volume":0.47111400642365453,"spread_bps":7.908080197237564,"day_high":441.94,"day_low":423.83,"execution_condition_ko":"428.39~436.10 되돌림에서 지지와 매수 거래량 회복 확인 / 450.73 상향 돌파, 거래량가중평균가 유지, 상대 거래량 1.2 이상 확인","risk_condition_ko":"428.39 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":946.805,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":954.2679562569547,"relative_volume":0.3165741211758079,"spread_bps":8.105476459906649,"day_high":967.0,"day_low":944.855,"execution_condition_ko":"GEV의 최신 가격·거래량·당일 거래량가중평균가격·중요 뉴스를 확보하고 기준 가격대를 재검증 / 974.20 위 종가와 거래량 2426520주 이상 확인","risk_condition_ko":"943.39 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":81.645,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":81.77391210264906,"relative_volume":0.7093441414660473,"spread_bps":1.2230171833903143,"day_high":82.29,"day_low":81.32,"execution_condition_ko":"GLDM 최신 시세와 순자산가치 괴리·호가 차이·고유 자금 흐름 확인 / 10:30 이후 85.67 상회, 장중 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상","risk_condition_ko":"83.77 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.6606,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":100.66424873007585,"relative_volume":0.8520786202927039,"spread_bps":0.9933939303635938,"day_high":100.67,"day_low":100.66,"execution_condition_ko":"SGOV의 최신 순자산가치·호가·보유채권·보수·분배금 및 세후 비교수익 확보 / 기존 SGOV와 현금성 자산의 합산 비중 확인","risk_condition_ko":"100.59 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":228.57,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":230.61436765347196,"relative_volume":0.6055025306067093,"spread_bps":0.4361574528400787,"day_high":233.21,"day_low":228.28,"execution_condition_ko":"실시간 가격·거래량·거래량가중평균가격을 갱신하고 $234.50 돌파 및 상대 거래량 1.2 이상 확인 / $234.50 위 종가 뒤 다음 거래일 첫 30~60분 지지 또는 신속한 재돌파 확인","risk_condition_ko":"221.05 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":540.96,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":543.7486799784938,"relative_volume":0.32599947382478656,"spread_bps":8.67791102371705,"day_high":556.785,"day_low":535.5,"execution_condition_ko":"2026-09-28 종가와 현재 DELL 시세 확인 / $550.19~$554.64 재시험 후 10:30 이후 $554.64 재돌파, 당일 거래량가중평균가격 상회 및 상대거래량 1.2 이상","risk_condition_ko":"530.45 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":338.49,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":340.63778708243944,"relative_volume":0.3642909241807269,"spread_bps":0.2957048865229808,"day_high":342.988,"day_low":338.04,"execution_condition_ko":"평결 이후 AAPL의 정규장 가격 범위·당일 거래량가중평균가격·거래량 확인 / 재검증된 345.34 위 종가와 상대 거래량 1.2 이상 및 다음 거래일 지지","risk_condition_ko":"334.3 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1186.545,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":1188.2149308452651,"relative_volume":0.27066418714543844,"spread_bps":4.795699015198465,"day_high":1194.09,"day_low":1172.56,"execution_condition_ko":"마지막 제공 거래일인 2026-09-25 이후의 LLY 시세와 거래량 갱신 / 1197.79 위 거래량 동반 종가 및 다음 거래일 지지 확인","risk_condition_ko":"1,176.74 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":342.19,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":341.5006222508403,"relative_volume":0.29688341063200935,"spread_bps":0.8776934216870061,"day_high":343.59,"day_low":339.56,"execution_condition_ko":"344.45 회복 유지와 거래량가중평균가격 상회 및 상대거래량 1.2 이상 확인 / 349.50 첫 저항 시험에서 상승세 유지 여부","risk_condition_ko":"337.45 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"DDOG","display_name":"Datadog","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":269.57,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":267.93921263402734,"relative_volume":0.45768754723362065,"spread_bps":5.901881224641277,"day_high":272.79,"day_low":255.5,"execution_condition_ko":"2026-09-28 하락의 실제 종가와 현재 DDOG 가격 확인 / 263.69 및 261.00 지지 여부 확인","risk_condition_ko":"261 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"AMD","display_name":"Advanced Micro Devices","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":606.4903,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":607.6959830940133,"relative_volume":0.47252823109042835,"spread_bps":4.114853799244513,"day_high":629.645,"day_low":596.07,"execution_condition_ko":"639.00 위 종가와 25,318,900주 이상 거래량이 확인되면 매도 측 계획을 먼저 정리한 뒤 진입 재평가 / 653.17 부근의 안착 또는 거부","risk_condition_ko":"653.17 이탈 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":193.555,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":192.49114733797862,"relative_volume":0.30193775852027416,"spread_bps":2.582177808763031,"day_high":193.78,"day_low":189.69,"execution_condition_ko":"10:30 이후 195.49 상향 돌파, 상대거래량 1.2배 이상 및 장중 거래량가중평균가 상회 시 시험 매수 검토 / 195.49 위 거래량 확인 종가와 다음 거래일 유지 또는 재돌파 시 확대 검토","risk_condition_ko":"189.77 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":206.46,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":206.79884068469426,"relative_volume":0.42778815635908557,"spread_bps":2.4279505669270094,"day_high":208.2443,"day_low":205.38,"execution_condition_ko":"CVX의 최신 시세에서 208.10 돌파, 장중 거래량가중평균가격 유지, 동시간대 상대거래량 1.2 이상 / 208.10 위 종가와 갱신된 5일 평균 대비 거래량 1.2배 이상; 이후 209.86 회복","risk_condition_ko":"200.31 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":503.3299865722656,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":504.4008804924296,"relative_volume":0.5310356852361672,"spread_bps":null,"day_high":507.239990234375,"day_low":502.7300109863281,"execution_condition_ko":"2026-09-25 이후의 BRK-B 가격·거래량과 기존 보유 규모 확인 / 511.28 상향 돌파 시 실시간 거래량가중평균가격 및 상대 거래량 1.2 이상 확인","risk_condition_ko":"501.41 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":96.64,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":97.07371920335142,"relative_volume":0.5931229930075589,"spread_bps":1.0362157401176224,"day_high":97.63,"day_low":96.42,"execution_condition_ko":"95.17~95.28 재시험 지지, 당일 거래량가중평균가격 상회, 상대거래량 1.2 이상 / 상대거래량 1.2 이상을 동반한 96.76 초과 종가","risk_condition_ko":"93.19 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":266.74,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":266.3017928050796,"relative_volume":0.23251995044459006,"spread_bps":2.9935638377482445,"day_high":267.735,"day_low":263.38,"execution_condition_ko":"ABBV의 현재 가격·당일 거래량가중평균가격·거래량 확보 / 269.91 초과 일일 종가와 401만 주 초과 거래량","risk_condition_ko":"257.05 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":149.18,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":148.3118173022316,"relative_volume":0.4130697569888514,"spread_bps":0.6707582922487778,"day_high":149.48,"day_low":145.11,"execution_condition_ko":"PG가 149.20달러 위에서 마감하고 일일 거래량이 7428400주를 초과하며 상대거래량이 1.2 이상임 / PG가 145.76~146.02달러 균형 구간을 잃은 뒤 145.33달러 아래에서 마감함","risk_condition_ko":"145.33 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"SPYM","display_name":"SPYM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":90.085,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":90.22859349084403,"relative_volume":0.32604789545022,"spread_bps":1.1096931698391073,"day_high":90.56,"day_low":89.88,"execution_condition_ko":"91.49 상향 돌파 시 당일 거래량가중평균가격과 상대거래량 1.2 이상 확인 / 91.49 위 마감 후 다음 거래일 91.34~91.49 지지 또는 재돌파 확인","risk_condition_ko":"89.43 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":162.62,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":162.50661179636916,"relative_volume":0.3162445736616127,"spread_bps":2.470355731224805,"day_high":163.54,"day_low":161.075,"execution_condition_ko":"갱신된 정규장 자료로 159.78~159.01 지지 방어, 당일 거래량가중평균가격 회복, 상대거래량 1.2 이상 및 비용 반영 보상 대비 위험을 확인한다. / 164.91 위 종가와 상대거래량 1.2 이상, 다음 거래일 유지 또는 재돌파를 확인하되 168.48~169.64 저항까지의 여력을 재평가한다.","risk_condition_ko":"159.01 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"JNJ","display_name":"JNJ","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":272.06,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":272.09567150210574,"relative_volume":0.34948825302830394,"spread_bps":4.047167902279793,"day_high":273.78,"day_low":269.27,"execution_condition_ko":"2026-09-25 이후 JNJ 가격·거래량·공시 확인 / 275.23 위 종가와 상대 거래량 1.2 이상 확인 후 276.45 및 281.07 저항, 비용 차감 후 손익비 재평가","risk_condition_ko":"269 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":369.04,"market_data_asof":"2026-09-28T15:45:00-04:00","session_vwap":368.733389207725,"relative_volume":0.3360713521113406,"spread_bps":0.8132174950198442,"day_high":370.5,"day_low":366.0604,"execution_condition_ko":"368.81 회복과 372 위 거래량 동반 종가 / 375–376 저항 돌파 후 382.55 및 385.57 접근","risk_condition_ko":"359.8 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-28T16:15:00-04:00"}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-09-29T03:23:20.649358+09:00",
  "as_of": "2026-09-28T11:55:00-04:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
