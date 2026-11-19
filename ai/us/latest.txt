# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-19T06:32:44.970311+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261119T030300_local-scheduler-us-overlay_only",
  "producer_finished_at": "2026-11-19T04:00:27.396224+09:00",
  "analysis_run_id": "20261118T175052_local-scheduler-us-full",
  "analysis_completed_at": "2026-11-18T20:34:00.384193+09:00",
  "analysis_trade_date_oldest": "2026-11-17",
  "analysis_trade_date_latest": "2026-11-17",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-18T15:52:00+00:00",
  "market_data_latest_at": "2026-11-18T18:57:11+00:00",
  "market_data_status": "MISSING"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-19T04:00:16.939731+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-19T04:00:16.939731+09:00",
    "run_started_at": "2026-11-19T03:03:00.178283+09:00",
    "run_finished_at": "2026-11-19T04:00:27.396224+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23625294,
    "total_market_value_krw": 21265890,
    "total_unrealized_pnl_krw": -2359404,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 112552,
    "total_equity_krw": 22355094
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 545788,
      "current_price_krw": 482543,
      "market_value_krw": 5790524,
      "unrealized_pnl_krw": -758939
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 292534,
      "current_price_krw": 289475,
      "market_value_krw": 3184228,
      "unrealized_pnl_krw": -33656
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 424304,
      "current_price_krw": 379897,
      "market_value_krw": 2279387,
      "unrealized_pnl_krw": -266438
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1880665,
      "current_price_krw": 1752301,
      "market_value_krw": 1752301,
      "unrealized_pnl_krw": -128364
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 556134,
      "current_price_krw": 456490,
      "market_value_krw": 1369471,
      "unrealized_pnl_krw": -298931
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 267340,
      "current_price_krw": 203832,
      "market_value_krw": 1222993,
      "unrealized_pnl_krw": -381049
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 134564,
      "current_price_krw": 134681,
      "market_value_krw": 1212135,
      "unrealized_pnl_krw": 1052
    },
    {
      "ticker": "GEV",
      "name": "GE 버노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1473402,
      "current_price_krw": 1043607,
      "market_value_krw": 1043607,
      "unrealized_pnl_krw": -429795
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 364707,
      "current_price_krw": 473439,
      "market_value_krw": 946879,
      "unrealized_pnl_krw": 217465
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1420480,
      "current_price_krw": 1865671,
      "market_value_krw": 813553,
      "unrealized_pnl_krw": 194131
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 569826,
      "current_price_krw": 476907,
      "market_value_krw": 476907,
      "unrealized_pnl_krw": -92919
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 662980,
      "current_price_krw": 420784,
      "market_value_krw": 420784,
      "unrealized_pnl_krw": -242196
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 136260,
      "current_price_krw": 98870,
      "market_value_krw": 395481,
      "unrealized_pnl_krw": -149562
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 347873,
      "current_price_krw": 357640,
      "market_value_krw": 357640,
      "unrealized_pnl_krw": 9767
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":352.2049865722656,"market_data_asof":"2026-11-18T15:52:00+00:00","market_data_clock_status":null,"session_vwap":354.4126153220109,"relative_volume":0.9199212297425132,"spread_bps":null,"day_high":356.4200134277344,"day_low":352.2049865722656,"execution_condition_ko":"349.67–350.58 시험 후 350.58 이상 일봉 마감, 이어지는 검증된 거래일의 지지 재시험을 순서대로 확인한다. 현재 두 단계의 충족은 확인되지 않았다. / 355.36–356.27과 357.13–360.83 접근 시 저항 소화와 비용 반영 손익비를 재평가한다. 단순 회복을 매수 신호로 보지 않는다.","risk_condition_ko":"346.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T15:52:00+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T15:55:00+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":267.1761,"market_data_asof":"2026-11-18T13:57:00-05:00","market_data_clock_status":null,"session_vwap":264.1970830464398,"relative_volume":0.4493784586933611,"spread_bps":1.4970620157926426,"day_high":267.97,"day_low":259.63,"execution_condition_ko":"2026-11-17 회복 이후 실제 후속 거래일에 254.81–257.00 재시험과 지지 유지가 완료되는지 확인한다. / 254.81–255.96 안에서 비용·갭 반영 손익비 2:1을 만족하는 체결 가능 가격이 있는지 확인한다. 상한은 비용 반영 후 더 낮아질 수 있다.","risk_condition_ko":"254 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T13:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:00:00-05:00","expired_at_build":true,"provider_limitations":["feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1309.875,"market_data_asof":"2026-11-18T13:57:00-05:00","market_data_clock_status":null,"session_vwap":1313.9978468163642,"relative_volume":0.3088944328117403,"spread_bps":25.499102950718925,"day_high":1340.12,"day_low":1288.02,"execution_condition_ko":"1280~1295.96 재시험, 1295.96 이상 종가 회복, 다음 확인된 정규장 종가 기준 1280 지지 유지의 순차 확인. / 확인 이후 1280 초과~1295.63 이하에서 거래비용 때문에 더 낮아지는 실제 매수 상한을 충족하는지 점검.","risk_condition_ko":"1,280 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T13:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.5999984741211,"market_data_asof":"2026-11-18T15:52:00+00:00","market_data_clock_status":null,"session_vwap":100.59472270826683,"relative_volume":1.4428352981384178,"spread_bps":null,"day_high":100.5999984741211,"day_low":100.58999633789062,"execution_condition_ko":"100.58~100.59 시험, 100.59 이상 완료 일봉 종가 회복, 다음 실제 거래일 지지 유지와 경제성 검증을 함께 확인한다. / 100.52~100.53 접근 시 가격 기준과 분배락 여부를 점검한다. 자동 물타기 구간이 아니다.","risk_condition_ko":"100.52 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T15:52:00+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T15:55:00+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":216.49,"market_data_asof":"2026-11-18T18:57:11+00:00","market_data_clock_status":null,"session_vwap":215.62700666452656,"relative_volume":1.0656645005888696,"spread_bps":0.4617124916310411,"day_high":216.89,"day_low":214.69,"execution_condition_ko":"2026-11-18 분석일부터 2026-11-25까지 약 7일간 새 일봉과 후속 확인 거래일의 지지 시험을 검토한다. 2026-11-17 종가는 신규 확인으로 인정하지 않는다. / 218.42의 공급 부담과 219.59 초과 종가·후속 지지 전환을 관찰한다. 증액에는 독립적인 참여 확산 또는 상대수익 개선도 필요하다.","risk_condition_ko":"214.75 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T18:57:11+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T19:00:11+00:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1394.885,"market_data_asof":"2026-11-18T13:57:00-05:00","market_data_clock_status":null,"session_vwap":1398.3599556831994,"relative_volume":0.4463324213951266,"spread_bps":6.667216293815162,"day_high":1423.11,"day_low":1384.59,"execution_condition_ko":"1410 이상 종가 이후 다음 검증된 거래일의 1407.40–1410 시험, 1401.66 이상 저가와 1410 이상 종가를 확인한다. 이후 같은 가격대가 다시 제공될 때만 조건부 소액 매수를 검토한다. / 1432.28–1443.50 및 1458.23 회복을 관찰하되 자동 증액하지 않는다. 1475.25 돌파 종가와 후속 지지는 새 검토 사유이지 상단 목표 없는 추격 허가가 아니다.","risk_condition_ko":"1,401.66 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T13:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":152.8209991455078,"market_data_asof":"2026-11-18T15:52:00+00:00","market_data_clock_status":null,"session_vwap":155.75183520643125,"relative_volume":2.7982362015672866,"spread_bps":null,"day_high":159.6999969482422,"day_low":151.60000610351562,"execution_condition_ko":"162.85~163.20 종가 회복은 초기 개선 관찰 신호이며 단독 매수 조건이 아니다. / 173.58 상회 종가와 다음 실제 거래일의 172.37~173.58 재시험·종가 지지를 확인한다. 이후 주문 시점에도 지지가 유효해야 한다.","risk_condition_ko":"148.8 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T15:52:00+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T15:55:00+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":356.13,"market_data_asof":"2026-11-18T13:57:00-05:00","market_data_clock_status":null,"session_vwap":350.5610166302585,"relative_volume":0.49197337844417144,"spread_bps":2.807648033243191,"day_high":356.87,"day_low":340.74,"execution_condition_ko":"미래의 완결된 일봉에서 333.40–335.80 시험 후 335.80 위 종가 반등을 확인한다. 단순 접촉은 불충분하며 336.34 회복은 보강 증거다. / 그 다음 확인된 거래일에 지지가 유지되고 333.40–335.80 안에서 비용 차감 후 최소 2:1 보상비율이 확보되는지 확인한다. 위로 갭이 나면 추격하지 않는다.","risk_condition_ko":"327.8 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T13:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":780.21,"market_data_asof":"2026-11-18T13:57:00-05:00","market_data_clock_status":null,"session_vwap":782.6572730393534,"relative_volume":0.3750560063170851,"spread_bps":7.945560097909864,"day_high":800.53,"day_low":770.0,"execution_condition_ko":"753.03~760.00 재시험 후 종가 760.00 이상 회복과 다음 확인된 거래일 지지 유지. 현재는 매수 승인 조건이 아닌 재심사 조건이다. / 797.77~805.62 회복 이후 805.62~816.68의 지지 전환 여부. 가격 회복만으로 자동 매수하지 않는다.","risk_condition_ko":"747 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T13:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":360.83,"market_data_asof":"2026-11-18T13:57:00-05:00","market_data_clock_status":null,"session_vwap":361.7068111246031,"relative_volume":0.4375276031841598,"spread_bps":1.9397835755751645,"day_high":368.845,"day_low":356.77,"execution_condition_ko":"351.19–353.50의 지지 방어와 일봉 종가 기준 실패를 구분한다. 단순 접촉은 매수 신호도 붕괴 확정도 아니다. / 375.44 초과 일봉 종가 이후 다음으로 확인된 거래일에 373.10–375.44가 지지되는지 확인한다. 현재는 재검토 신호이지 조건부 매수 주문이 아니다.","risk_condition_ko":"351.19 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T13:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":314.9025,"market_data_asof":"2026-11-18T13:57:00-05:00","market_data_clock_status":null,"session_vwap":316.64319873882283,"relative_volume":0.48077677162438925,"spread_bps":8.575920720378567,"day_high":329.25,"day_low":308.9262,"execution_condition_ko":"315.00–318.03은 2026-11-17 장중 훼손된 지지·재시험 구간이다. 종가 이탈이 확정되었다거나 견고한 바닥이라고 해석하지 않는다. / 332.36 초과 일봉 종가는 첫 회복 관문이며 매수 신호가 아니다.","risk_condition_ko":"305.8 이하 하락, 종가 확인 후 (보호 매도에 거래량 조건 없음) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T13:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:00:00-05:00","expired_at_build":true,"provider_limitations":["feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":341.2104,"market_data_asof":"2026-11-18T13:57:00-05:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.37253260357682466,"spread_bps":6.445564279855482,"day_high":342.44,"day_low":334.71,"execution_condition_ko":"331.27~336.20 방어 또는 재회복 후 다음 실제 거래일의 저점 상승을 관찰한다. 구간 도달 자체는 매수 신호가 아니다. / 347.30 위 종가 후 다음 실제 거래일 345.09~347.30 재시험 지지를 확인한다.","risk_condition_ko":"331.27 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T13:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:00:00-05:00","expired_at_build":true,"provider_limitations":["feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":283.8,"market_data_asof":"2026-11-18T13:57:00-05:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.3214480524467418,"spread_bps":1.7618972109171158,"day_high":284.13,"day_low":280.1432,"execution_condition_ko":"2026-11-18~2026-11-25를 1차 검토 기간으로 삼아 확인된 정규장 종가마다 지지·회복 여부를 점검한다. 2026-11-25는 계획 검토일이지 주문 만기나 거래 세션 확정일이 아니다. / 290.00 위 종가와 다음 확인된 세션의 286.26~290.00 지지 유지 시 새 구조적 손절과 가까운 293.44 저항부터 비용차감 손익비를 다시 계산한다. 유리한 비율을 만들기 위해 손절만 임의로 좁히지 않는다.","risk_condition_ko":"276.92 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T13:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:00:00-05:00","expired_at_build":true,"provider_limitations":["feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":73.905,"market_data_asof":"2026-11-18T13:57:00-05:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.7672346984718945,"spread_bps":1.3521736190914617,"day_high":74.155,"day_low":73.735,"execution_condition_ko":"75.96–76.10의 일봉 회복과 지지 실패를 구분한다. 제공된 2026-11-17 저가는 75.97이며 75.96은 더 넓은 지지 참고값이다. / 76.89–76.95 저항대와 76.95 상회 종가 이후의 후속 지지를 관찰한다. 단일 돌파만으로 매수하지 않는다.","risk_condition_ko":"75.96 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T13:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:00:00-05:00","expired_at_build":true,"provider_limitations":["feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.98,"market_data_asof":"2026-11-18T18:57:11+00:00","market_data_clock_status":null,"session_vwap":100.69949740728399,"relative_volume":0.35163158593122296,"spread_bps":2.9704440813902804,"day_high":102.46,"day_low":99.59,"execution_condition_ko":"101.18–101.60 시험 후 종가 101.60 이상 회복을 관찰한다. 다음 거래일 해당 구간 내 체결기회가 없으면 추격하지 않는다. / 103.34–104.49 저항을 관찰한다. 104.49 상향 종가 돌파와 재시험 성공은 관찰조건 개선이지 자동 매수 승인이 아니다.","risk_condition_ko":"100.02 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T18:57:11+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T19:00:11+00:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":574.63,"market_data_asof":"2026-11-18T13:57:00-05:00","market_data_clock_status":null,"session_vwap":578.3594632614635,"relative_volume":0.4119074934031714,"spread_bps":2.784400396778481,"day_high":583.72,"day_low":574.39,"execution_condition_ko":"제공된 결정 시계 2026-11-18T06:16:32.728417-05:00 기준으로 조건부 진입 만료는 지나지 않았다. 다만 실제 거래 세션·휴장·조기폐장·최신 가격은 별도 확인해야 한다. / 2026-11-18T06:00:21-05:00의 582.66은 지연된 저유동성 개장 전 관측이다. 현재 체결가나 정규장 진입 조건 충족으로 취급하지 않는다.","risk_condition_ko":"580.91 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T13:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":170.88,"market_data_asof":"2026-11-18T13:57:00-05:00","market_data_clock_status":null,"session_vwap":170.56315632024513,"relative_volume":0.30389023135727455,"spread_bps":1.7555666091231612,"day_high":171.64,"day_low":169.415,"execution_condition_ko":"167.96~168.66 접촉, 168.66 이상 회복 종가, 다음 유효 거래일 재시험과 168.47 이상 지지 종가를 순차 확인한다. 확인 후 가격 재하락이 새로운 약세인지 주문 직전에 재점검한다. / 170.73~171.24 지지 후보와 173.57~173.59 저항을 관찰한다. 상대강도지수 73.10→69.32와 양수인 이동평균 수렴·확산 지표 막대값의 감소는 경계 신호이나 단독 매도 근거로 보지 않는다.","risk_condition_ko":"168.47 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T13:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1111.3854,"market_data_asof":"2026-11-18T13:57:00-05:00","market_data_clock_status":null,"session_vwap":1106.7036915971166,"relative_volume":0.4165295545570719,"spread_bps":5.667378837288736,"day_high":1113.81,"day_low":1097.5,"execution_condition_ko":"1091.92–1092.64: 지지 시험, 1092.64 이상 일봉 마감, 다음 거래일 지지 재확인 순으로 관찰한다. 매수는 해당 구간 안에서만 가능하다. / 1104.89–1108.68: 최근 지지 유지와 회복을 확인한다. 지연된 개장 전 관측만으로 붕괴나 회복을 확정하지 않는다.","risk_condition_ko":"1,081.06 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T13:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":416.86,"market_data_asof":"2026-11-18T13:57:00-05:00","market_data_clock_status":null,"session_vwap":415.6065602171017,"relative_volume":0.3718151566467489,"spread_bps":1.439332149882509,"day_high":417.9,"day_low":411.83,"execution_condition_ko":"411.99~416.41 방어, 416.41 위 종가 재회복, 다음 실제 정규 세션의 재시험·반등을 순서대로 확인한다. 구간 내 가격만으로 진입하지 않는다. / 421.12~422.23은 회복·청산 재평가 구간이며 추격 지시가 아니다. 동적 평균선은 최신 검증 일봉으로 갱신한다. 추가 저항은 425.19~425.76, 430.99, 435.95~441.41이다.","risk_condition_ko":"411.99 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T13:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WMT","display_name":"WMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":127.44,"market_data_asof":"2026-11-18T13:57:00-05:00","market_data_clock_status":null,"session_vwap":126.52799415054042,"relative_volume":0.6344852548442826,"spread_bps":1.5693659761453251,"day_high":127.675,"day_low":125.07,"execution_condition_ko":"공식 발표 정보를 최우선 확인한다. 중립 분석가가 지적한 대로 15건 중 목표가격 관련 6건은 독립적인 실적 근거로 중복 계산하지 않는다. / 126.31–126.40의 새 종가 확인과 다음 거래일 재지지를 관찰하되 범위 밖 추격은 금지한다.","risk_condition_ko":"126.31 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T13:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LIN","display_name":"LIN","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":511.542,"market_data_asof":"2026-11-18T13:57:00-05:00","market_data_clock_status":null,"session_vwap":510.64188531066117,"relative_volume":0.29433130965090765,"spread_bps":6.254886630179694,"day_high":512.69,"day_low":508.0,"execution_condition_ko":"510.01~514.34: 지지 시험, 514.34 초과 종가, 다음 거래일 구간 내 지지 확인 및 비용 후 최소 2:1 구조적 보상 대비 위험을 순서대로 점검한다. / 518.62~519.72: 전체 구간 회복과 후속 지지 여부를 관찰하되 자동 매수나 추가 매수는 하지 않는다.","risk_condition_ko":"510.01 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T13:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":287.67,"market_data_asof":"2026-11-18T13:57:00-05:00","market_data_clock_status":null,"session_vwap":291.592692929267,"relative_volume":0.37373364498752226,"spread_bps":5.562702082535485,"day_high":292.55,"day_low":287.0,"execution_condition_ko":"291.00~292.84 유지와 294.06 회복은 개선 신호지만 자동 매수 조건은 아니다. / 284.70~288.00 시험 후 지정 구간의 상승 종가와 다음 검증된 거래일의 일봉 지지를 순서대로 확인한다. 가격이 287.50 위로 떠나면 추격하지 않는다.","risk_condition_ko":"284.7 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T13:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"KO","display_name":"KO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":97.955,"market_data_asof":"2026-11-18T13:57:00-05:00","market_data_clock_status":null,"session_vwap":98.01005422776228,"relative_volume":0.38647647753487363,"spread_bps":1.0208769332847638,"day_high":98.87,"day_low":97.16,"execution_condition_ko":"97.38~98.53 시험, 98.53 이상 마감, 다음 정규 세션 재시험 지지를 순서대로 확인한다. 11/17 저가가 구간 상단에 닿았다는 사실만으로 전체 과정 충족을 가정하지 않는다. / 100.56 상회 마감과 갱신된 20일 평균 대비 정규장 거래량 개선 이후 다음 세션 지지를 확인한다. 재시험 없이 멀어지면 추격하지 않는다.","risk_condition_ko":"97.38 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T13:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GE","display_name":"GE","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":329.62,"market_data_asof":"2026-11-18T13:57:00-05:00","market_data_clock_status":null,"session_vwap":328.12650776245164,"relative_volume":0.23468332843321585,"spread_bps":4.853779881083152,"day_high":331.71,"day_low":325.04,"execution_condition_ko":"11월 17일 회복 다음 실제 정규 거래세션의 323.28~323.40 지지 유지와 확인 이후 323.40~324.00 체결 기회. / 새 지지 시험이 발생하면 그날 종가 324.00 이상 회복 후 다음 실제 거래세션 지지를 다시 확인한다. 확인 이전의 체결 기회를 소급 적용하지 않는다.","risk_condition_ko":"323.28 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T13:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":644.145,"market_data_asof":"2026-11-18T13:57:00-05:00","market_data_clock_status":null,"session_vwap":641.7327811372066,"relative_volume":0.2947067414206682,"spread_bps":4.502091920296884,"day_high":647.1,"day_low":636.41,"execution_condition_ko":"2026-11-18부터 새 일봉의 638.01~644.88 지지 시험과 하락 중단을 관찰한다. 단순 가격 접촉은 매수 신호가 아니다. / 다음 실제 거래일에도 지지와 저점 안정이 유지되고 실제 매수가가 비용 반영 상한 이하일 때만 소액 진입 조건을 평가한다. 재하락이 안정적 재시험인지 새로운 매도 압력인지 구분한다.","risk_condition_ko":"638.01 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T13:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LRCX","display_name":"Lam Research","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":209.69500732421875,"market_data_asof":"2026-11-18T15:52:00+00:00","market_data_clock_status":null,"session_vwap":211.31028857987042,"relative_volume":0.7996192779246416,"spread_bps":null,"day_high":214.89999389648438,"day_low":206.42999267578125,"execution_condition_ko":"위험 대응 조건: 201.91 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"201.91 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T15:52:00+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T15:55:00+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOG","display_name":"GOOG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":280.72,"market_data_asof":"2026-11-18T13:57:00-05:00","market_data_clock_status":null,"session_vwap":279.46121760952,"relative_volume":0.31464498988387535,"spread_bps":1.4250596743725685,"day_high":282.3599,"day_low":276.89,"execution_condition_ko":"위험 대응 조건: 275.35 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"275.35 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-18T13:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WELL","display_name":"WELL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":247.395,"market_data_asof":"2026-11-18T13:57:00-05:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.6280325260554072,"spread_bps":6.871602093817074,"day_high":247.65,"day_low":246.27,"execution_condition_ko":"2026-11-18 이후의 정규장 여부를 확인하고 242.46~244.08 시험, 244.08 이상 종가, 다음 거래일 242.46~243.50 진입 기회를 순서대로 관찰한다. / 249.75 초과 종가는 완료된 거래일끼리 거래량을 비교하고 후속 지지 확인과 함께 평가한다. 약 1.05배였던 기존 거래량만으로 강한 수요 확인을 주장하지 않는다.","risk_condition_ko":"241.52 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T13:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:00:00-05:00","expired_at_build":true,"provider_limitations":["feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SO","display_name":"SO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":94.375,"market_data_asof":"2026-11-18T18:57:11+00:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.36937418902171065,"spread_bps":1.059602649005659,"day_high":94.49,"day_low":93.13,"execution_condition_ko":"2026-11-17 종가 93.60을 기준으로 이후 확정 일봉의 지지 유지와 추진력 변화를 점검한다. 지연 장전 표시 93.19는 진입 확인에 사용하지 않는다. / 조달 원문 검증, 회복 종가, 다음 실제 정규장 지지, 92.70~92.95 체결 범위 및 비용 후 손익비가 모두 충족될 때만 최초 소규모 진입 후보를 활성화한다. 범위 밖에서는 추격하지 않는다.","risk_condition_ko":"91.17 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T18:57:11+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T19:00:11+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AIQUY","display_name":"AIQUY","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"date_only","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-18 이후 완료된 일봉에서 41.61~41.71 시험과 종가 41.80 이상 반등을 확인하고 다음 실제 거래일 재지지를 점검한다. / 42.16 회복과 다음 거래일 유지, 42.34~42.96 매물대 반응을 관찰한다. 42.96 돌파 후에도 43.45~43.57 저항까지 공간이 좁아 추격하지 않는다.","risk_condition_ko":"41.61 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-17"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-19T03:13:46.726564+09:00",
  "as_of": "2026-11-18T15:52:00+00:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
