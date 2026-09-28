# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-09-28T05:44:47.246430+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20260926T060129_github-actions-overlay-us",
  "producer_finished_at": "2026-09-26T06:01:59.083985+09:00",
  "analysis_run_id": "20260925T212622_github-actions-us",
  "analysis_completed_at": "2026-09-26T00:04:22.912385+09:00",
  "analysis_trade_date_oldest": "2026-09-24",
  "analysis_trade_date_latest": "2026-09-24",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-09-25T15:10:00-04:00",
  "market_data_latest_at": "2026-09-25T15:10:00-04:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-09-26T06:01:59.121659+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23999416,
    "total_market_value_krw": 25020656,
    "total_unrealized_pnl_krw": 1021240,
    "settled_cash_krw": 0,
    "available_cash_krw": 975902,
    "buying_power_krw": 76255,
    "total_equity_krw": 26072813
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 554431,
      "current_price_krw": 612829,
      "market_value_krw": 7353955,
      "unrealized_pnl_krw": 700781
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 297167,
      "current_price_krw": 287109,
      "market_value_krw": 3158205,
      "unrealized_pnl_krw": -110635
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 431023,
      "current_price_krw": 467731,
      "market_value_krw": 2806387,
      "unrealized_pnl_krw": 220248
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1910446,
      "current_price_krw": 1859704,
      "market_value_krw": 1859704,
      "unrealized_pnl_krw": -50742
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 271573,
      "current_price_krw": 306095,
      "market_value_krw": 1836571,
      "unrealized_pnl_krw": 207129
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 564940,
      "current_price_krw": 598372,
      "market_value_krw": 1795118,
      "unrealized_pnl_krw": 100296
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1496734,
      "current_price_krw": 1302376,
      "market_value_krw": 1302376,
      "unrealized_pnl_krw": -194358
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 136695,
      "current_price_krw": 136897,
      "market_value_krw": 1232078,
      "unrealized_pnl_krw": 1818
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 370482,
      "current_price_krw": 463855,
      "market_value_krw": 927710,
      "unrealized_pnl_krw": 186746
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 673478,
      "current_price_krw": 765530,
      "market_value_krw": 765530,
      "unrealized_pnl_krw": 92052
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1442975,
      "current_price_krw": 1609505,
      "market_value_krw": 701849,
      "unrealized_pnl_krw": 72618
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 578849,
      "current_price_krw": 479821,
      "market_value_krw": 479821,
      "unrealized_pnl_krw": -99028
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 138418,
      "current_price_krw": 115450,
      "market_value_krw": 461801,
      "unrealized_pnl_krw": -91873
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 353382,
      "current_price_krw": 339551,
      "market_value_krw": 339551,
      "unrealized_pnl_krw": -13831
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":344.25,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":343.82796160016704,"relative_volume":0.278680566567956,"spread_bps":0.5811926072295074,"day_high":347.03,"day_low":341.11,"execution_condition_ko":"GOOGL이 거래량 개선과 함께 344.57 위로 마감하면 매수 가능성을 재평가 / GOOGL이 상대 거래량 1.2 이상으로 354.77 위에서 마감하고 다음 거래일에도 지지되면 위험 축소 사유 해소 여부를 재평가","risk_condition_ko":"354.77 이탈 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":351.92,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":352.2242110522237,"relative_volume":0.2911304584909025,"spread_bps":1.1354926618792536,"day_high":354.43,"day_low":349.43,"execution_condition_ko":"355.15 위 종가와 상대 거래량 1.2 이상 / 366.55~367.27 위 종가, 다음 거래일 지지 및 손익비 재평가","risk_condition_ko":"346.89 이탈 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":952.95,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":952.4295584604863,"relative_volume":0.19921546864931122,"spread_bps":7.470813845207225,"day_high":965.3453,"day_low":943.392,"execution_condition_ko":"962.85달러, 971.34달러, 974.48달러의 순차적 회복 / 984.16달러 위에서 2439000주 초과 거래량을 동반한 종가와 다음 거래일 지지","risk_condition_ko":"931.94 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1365.95,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":1362.8110707387245,"relative_volume":0.1575207182385997,"spread_bps":4.990642545228165,"day_high":1377.14,"day_low":1329.47,"execution_condition_ko":"MPWR의 현재 가격, 거래량가중평균가격, 거래량, 가치평가 및 기존 보유 비중 확인 / 미국 동부시간 10:30 이후 1373.16 회복과 거래량 조건 확인 시 소규모 시험 매수 재검토","risk_condition_ko":"1,302.59 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":438.16,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":439.9761441335325,"relative_volume":0.30492822869043984,"spread_bps":2.514716808596071,"day_high":447.33,"day_low":436.1751,"execution_condition_ko":"443.64 초과 종가와 일일 거래량 2614300주 초과 / 447.47 초과 종가 이후 다음 거래일 지지 확인","risk_condition_ko":"425.81 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":450.8,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":451.8112656885141,"relative_volume":0.1806359631663493,"spread_bps":2.658631690889856,"day_high":455.02,"day_low":449.03,"execution_condition_ko":"정규장 10:30 이후 454.66 돌파, 당일 거래량가중평균가격 상회 및 상대 거래량 1.2 이상 / 454.66 초과 종가와 일일 거래량 11,256,000주 이상, 다음 거래일 지지 또는 재돌파","risk_condition_ko":"438.29 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.6503,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":100.65484936069294,"relative_volume":0.9375386820492857,"spread_bps":0.9934926233163682,"day_high":100.66,"day_low":100.65,"execution_condition_ko":"2026-09-28 10:30 이후 100.63 상향 유지, 상대거래량 1.2 이상 및 장중 거래량가중평균가 상회 / 100.67 위 종가 이후 다음 거래일 첫 30~60분 동안 100.67 유지","risk_condition_ko":"100.54 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":249.37,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":249.1256064531599,"relative_volume":0.48288162166208376,"spread_bps":1.201995312218328,"day_high":250.8775,"day_low":247.18,"execution_condition_ko":"2026-10-02T16:00:00-04:00 전 $252.96 상향 돌파, 실시간 거래량가중평균가 유지, 상대거래량 1.2 이상 확인 / 거래량 증가를 동반한 $256.18 초과 종가와 다음 거래일 지지 확인","risk_condition_ko":"245.2 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":211.045,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":210.72735342769414,"relative_volume":0.3554040073308118,"spread_bps":0.4739673436509385,"day_high":211.52,"day_low":209.885,"execution_condition_ko":"최신 RSP 가격, 매수·매도 호가 차이, 순자산가치와의 괴리, 보유량 및 현금 확인 / 211.23 회복 후 212.53 위 종가 확인","risk_condition_ko":"209.81 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":84.9299,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":84.69859233644208,"relative_volume":0.44255878312846697,"spread_bps":1.1770937555165564,"day_high":85.05,"day_low":84.15,"execution_condition_ko":"83.94와 83.77의 종가 지지 여부를 확인한다. / 84.80, 85.17, 85.63의 순차 회복과 85.89의 거래량 동반 돌파를 확인한다.","risk_condition_ko":"83.77 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1182.765,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":1171.5532753991804,"relative_volume":0.28617538251325625,"spread_bps":15.535947988347349,"day_high":1190.0,"day_low":1160.84,"execution_condition_ko":"1197.79 상회 유지와 상대거래량 1.2 이상 및 거래량가중평균가격 지지 / 1197.79 상회 종가와 다음 거래일 유지 또는 재돌파","risk_condition_ko":"1,151 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":223.97,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":224.76444659430948,"relative_volume":0.3330798614241735,"spread_bps":0.44617958728347595,"day_high":226.94,"day_low":223.1329,"execution_condition_ko":"221.09~222.82 지지 후 224.94 회복 여부 / 230.14 위 종가와 갱신한 5일 평균 초과 거래량, 이후 233.17 및 234.50 시험 여부","risk_condition_ko":"221.09 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":340.16,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":338.34830274347865,"relative_volume":0.31934025572488917,"spread_bps":0.2939404182769479,"day_high":340.48,"day_low":334.53,"execution_condition_ko":"334.16~334.30 시험 후 334.30 위 일일 종가 / 345.34 위 일일 종가와 최근 10일 평균의 1.2배 이상 거래량","risk_condition_ko":"329.86 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":565.15,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":562.256111864628,"relative_volume":0.46763291342107255,"spread_bps":8.634741618573665,"day_high":573.8,"day_low":541.2351,"execution_condition_ko":"547.37 및 551.69 위 거래량 증가를 동반한 일간 종가 / 다음 거래일 첫 30~60분 동안 551.69 지지 또는 재돌파","risk_condition_ko":"530.45 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"ANET","display_name":"Arista Networks","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":207.585,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":208.55168173475383,"relative_volume":0.23463103955539766,"spread_bps":6.746662811431487,"day_high":212.0,"day_low":205.525,"execution_condition_ko":"미국 동부시간 10:30 이후 197.81 재시험과 지지, 당일 거래량가중평균가 상회 및 동시간대 상대거래량 1.2 이상 / 208.38 위 일봉 마감과 거래량 4786000주 초과","risk_condition_ko":"197.81 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"CRM","display_name":"Salesforce","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":234.095,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":235.65585072585077,"relative_volume":0.17449647985848335,"spread_bps":3.8475514610009363,"day_high":239.37,"day_low":233.76,"execution_condition_ko":"CRM의 242.09 회복 및 245.59 거래량 동반 돌파 / 236.25~237.00과 229.81~230.42 지지 구간 시험","risk_condition_ko":"229.81 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":264.355,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":263.84479271483195,"relative_volume":0.07940197152263664,"spread_bps":3.40155337604078,"day_high":266.0,"day_low":262.59,"execution_condition_ko":"269.43 초과 종가와 4,184,895주 초과 거래량 / 다음 거래일 첫 30~60분 동안 269.39~269.43 유지 또는 회복","risk_condition_ko":"263.05 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":367.2125,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":366.4751964166864,"relative_volume":0.21234938505664094,"spread_bps":1.9043214494604832,"day_high":368.3347,"day_low":363.79,"execution_condition_ko":"과거 기준 369.27 회복과 370.90–371.81 위 거래량 동반 종가 확인 / 다음 거래일 첫 30–60분 동안 돌파 구간과 당일 거래량가중평균가격 유지 확인","risk_condition_ko":"359.8 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":95.695,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":95.60302794182492,"relative_volume":0.3867135943232795,"spread_bps":1.0459703990382425,"day_high":96.095,"day_low":95.28,"execution_condition_ko":"94.10~95.04 지지 후 95.04 회복과 동시간대 상대거래량 1.2 이상 / 96.76 위 거래량 동반 종가와 다음 거래일 유지","risk_condition_ko":"94.1 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"KO","display_name":"KO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":87.66,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":87.84221578359504,"relative_volume":0.22108798085882328,"spread_bps":1.1405759908759754,"day_high":88.3183,"day_low":87.555,"execution_condition_ko":"89.36 위 종가와 직전 10거래일 평균의 1.2배 이상 거래량, 이후 89.82 돌파 여부 / 87.12~87.03 지지 구간 및 86.99의 50일 평균선 유지 여부","risk_condition_ko":"87.03 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":189.465,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":188.8950025417907,"relative_volume":0.19305818983284467,"spread_bps":5.278158978148123,"day_high":190.988,"day_low":187.31,"execution_condition_ko":"$195.50 위 종가와 상대 거래량 1.2 이상, 다음 거래일 $194.70 유지 및 $195.50 재돌파 / $189.20–$190.10 재시험 후 종가 기준 지지와 비용 차감 후 유리한 손익비","risk_condition_ko":"189.2 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":566.6,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":566.4779563940538,"relative_volume":0.22109741129991062,"spread_bps":3.1713591035616124,"day_high":568.78,"day_low":562.29,"execution_condition_ko":"$568.50 회복 후 $571.35 위에서 최소 2,598,480주를 동반한 종가 / 돌파 다음 거래일 첫 30~60분 동안 $571.35 유지 또는 재돌파","risk_condition_ko":"553.12 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":160.535,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":160.6885950657047,"relative_volume":0.2420655461798047,"spread_bps":1.246494234964801,"day_high":161.79,"day_low":159.78,"execution_condition_ko":"158.69~159.50 재시험에서 158.69 유지, 현재 거래량가중평균가 회복 및 상대거래량 1.2 이상 / 164.91 위 일간 종가와 상대거래량 1.2 이상: 매수 확정이 아닌 후속 확인 신호","risk_condition_ko":"155.74 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"JNJ","display_name":"JNJ","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":270.49,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":270.2884357693187,"relative_volume":0.19189408041273232,"spread_bps":4.061063629483826,"day_high":272.2459,"day_low":269.2573,"execution_condition_ko":"275.23 회복 후 상대거래량 1.2 이상을 동반한 276.34 상향 종가 / 278.89와 281.07 돌파 및 다음 거래일 지지","risk_condition_ko":"265.04 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":204.53,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":204.79218715969364,"relative_volume":0.31778558967730797,"spread_bps":2.448519869737908,"day_high":206.5389,"day_low":203.4901,"execution_condition_ko":"208.10 재돌파 후 실시간 거래량가중평균 유지와 상대 거래량 1.2 이상 / 210.05 위 종가, 비교 가능한 정규장 거래량 9,382,800주 초과 및 다음 거래일 지지","risk_condition_ko":"203.48 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

```json
{"ticker":"WBD","display_name":"WBD","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":30.845,"market_data_asof":"2026-09-25T15:10:00-04:00","session_vwap":30.837446260940204,"relative_volume":0.5690269920429953,"spread_bps":3.242016534284832,"day_high":30.87,"day_low":30.8,"execution_condition_ko":"WBD 일일 종가 $30.92 초과 및 거래량 46,106,500주 초과 / $30.68~$30.71 시험 후 확인된 반등; 단순 접촉은 진입 신호가 아님","risk_condition_ko":"30.68 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-25T15:40:00-04:00"}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-09-28T01:19:42.805519+09:00",
  "as_of": "2026-09-25T15:10:00-04:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
