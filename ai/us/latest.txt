# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-18T18:57:01.006804+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261119T010253_local-scheduler-us-overlay_only",
  "producer_finished_at": "2026-11-19T02:09:00.318652+09:00",
  "analysis_run_id": "20261118T175052_local-scheduler-us-full",
  "analysis_completed_at": "2026-11-18T20:34:00.384193+09:00",
  "analysis_trade_date_oldest": "2026-11-17",
  "analysis_trade_date_latest": "2026-11-17",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-18T15:52:00+00:00",
  "market_data_latest_at": "2026-11-18T16:57:03+00:00",
  "market_data_status": "MISSING"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-19T00:32:30.768373+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "INVALID_SNAPSHOT",
    "account_as_of": "2026-11-19T02:08:48.996573+09:00",
    "run_started_at": "2026-11-19T01:02:53.005800+09:00",
    "run_finished_at": "2026-11-19T02:09:00.318652+09:00",
    "selected_for_public_account": false
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23625294,
    "total_market_value_krw": 21262619,
    "total_unrealized_pnl_krw": -2362675,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 112552,
    "total_equity_krw": 22352081
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 545788,
      "current_price_krw": 485127,
      "market_value_krw": 5821530,
      "unrealized_pnl_krw": -727933
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 292534,
      "current_price_krw": 288618,
      "market_value_krw": 3174803,
      "unrealized_pnl_krw": -43081
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 424304,
      "current_price_krw": 377347,
      "market_value_krw": 2264084,
      "unrealized_pnl_krw": -281741
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1880665,
      "current_price_krw": 1745500,
      "market_value_krw": 1745500,
      "unrealized_pnl_krw": -135165
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 556134,
      "current_price_krw": 450198,
      "market_value_krw": 1350594,
      "unrealized_pnl_krw": -317808
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 267340,
      "current_price_krw": 205023,
      "market_value_krw": 1230142,
      "unrealized_pnl_krw": -373900
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 134564,
      "current_price_krw": 134676,
      "market_value_krw": 1212089,
      "unrealized_pnl_krw": 1006
    },
    {
      "ticker": "GEV",
      "name": "GE 버노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1473402,
      "current_price_krw": 1053602,
      "market_value_krw": 1053602,
      "unrealized_pnl_krw": -419800
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 364707,
      "current_price_krw": 472676,
      "market_value_krw": 945353,
      "unrealized_pnl_krw": 215939
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1420480,
      "current_price_krw": 1872271,
      "market_value_krw": 816432,
      "unrealized_pnl_krw": 197010
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 569826,
      "current_price_krw": 471123,
      "market_value_krw": 471123,
      "unrealized_pnl_krw": -98703
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 662980,
      "current_price_krw": 425390,
      "market_value_krw": 425390,
      "unrealized_pnl_krw": -237590
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 136260,
      "current_price_krw": 99576,
      "market_value_krw": 398307,
      "unrealized_pnl_krw": -146736
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 347873,
      "current_price_krw": 353670,
      "market_value_krw": 353670,
      "unrealized_pnl_krw": 5797
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":351.55,"market_data_asof":"2026-11-18T11:57:00-05:00","session_vwap":353.58996743226953,"relative_volume":0.4685042993339422,"spread_bps":0.5688767528509774,"day_high":356.42,"day_low":351.4706,"execution_condition_ko":"349.67–350.58 시험 후 350.58 이상 일봉 마감, 이어지는 검증된 거래일의 지지 재시험을 순서대로 확인한다. 현재 두 단계의 충족은 확인되지 않았다. / 355.36–356.27과 357.13–360.83 접근 시 저항 소화와 비용 반영 손익비를 재평가한다. 단순 회복을 매수 신호로 보지 않는다.","risk_condition_ko":"346.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T11:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T12:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":262.6300048828125,"market_data_asof":"2026-11-18T15:52:00+00:00","session_vwap":262.8042819017212,"relative_volume":1.0035729693590356,"spread_bps":null,"day_high":264.8699951171875,"day_low":260.0101013183594,"execution_condition_ko":"2026-11-17 회복 이후 실제 후속 거래일에 254.81–257.00 재시험과 지지 유지가 완료되는지 확인한다. / 254.81–255.96 안에서 비용·갭 반영 손익비 2:1을 만족하는 체결 가능 가격이 있는지 확인한다. 상한은 비용 반영 후 더 낮아질 수 있다.","risk_condition_ko":"254 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T15:52:00+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T15:55:00+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1306.9200439453125,"market_data_asof":"2026-11-18T15:52:00+00:00","session_vwap":1317.5066086291242,"relative_volume":0.5388119563129573,"spread_bps":null,"day_high":1340.1199951171875,"day_low":1290.010009765625,"execution_condition_ko":"1280~1295.96 재시험, 1295.96 이상 종가 회복, 다음 확인된 정규장 종가 기준 1280 지지 유지의 순차 확인. / 확인 이후 1280 초과~1295.63 이하에서 거래비용 때문에 더 낮아지는 실제 매수 상한을 충족하는지 점검.","risk_condition_ko":"1,280 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T15:52:00+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T15:55:00+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.59,"market_data_asof":"2026-11-18T11:57:00-05:00","session_vwap":100.59441554487225,"relative_volume":1.2062923389106077,"spread_bps":0.9940851931001445,"day_high":100.6,"day_low":100.59,"execution_condition_ko":"100.58~100.59 시험, 100.59 이상 완료 일봉 종가 회복, 다음 실제 거래일 지지 유지와 경제성 검증을 함께 확인한다. / 100.52~100.53 접근 시 가격 기준과 분배락 여부를 점검한다. 자동 물타기 구간이 아니다.","risk_condition_ko":"100.52 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T11:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T12:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":215.51,"market_data_asof":"2026-11-18T11:57:00-05:00","session_vwap":215.36312114984653,"relative_volume":0.7925905233696324,"spread_bps":0.9280311818481849,"day_high":216.29,"day_low":214.69,"execution_condition_ko":"2026-11-18 분석일부터 2026-11-25까지 약 7일간 새 일봉과 후속 확인 거래일의 지지 시험을 검토한다. 2026-11-17 종가는 신규 확인으로 인정하지 않는다. / 218.42의 공급 부담과 219.59 초과 종가·후속 지지 전환을 관찰한다. 증액에는 독립적인 참여 확산 또는 상대수익 개선도 필요하다.","risk_condition_ko":"214.75 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T11:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T12:00:00-05:00","expired_at_build":true,"provider_limitations":["feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1387.98,"market_data_asof":"2026-11-18T11:57:00-05:00","session_vwap":1399.8546953873538,"relative_volume":0.6254462513473981,"spread_bps":6.555322237310459,"day_high":1423.11,"day_low":1384.59,"execution_condition_ko":"1410 이상 종가 이후 다음 검증된 거래일의 1407.40–1410 시험, 1401.66 이상 저가와 1410 이상 종가를 확인한다. 이후 같은 가격대가 다시 제공될 때만 조건부 소액 매수를 검토한다. / 1432.28–1443.50 및 1458.23 회복을 관찰하되 자동 증액하지 않는다. 1475.25 돌파 종가와 후속 지지는 새 검토 사유이지 상단 목표 없는 추격 허가가 아니다.","risk_condition_ko":"1,401.66 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T11:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T12:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":151.065,"market_data_asof":"2026-11-18T11:57:00-05:00","session_vwap":154.91845160567803,"relative_volume":1.3967530516443463,"spread_bps":1.9856372240792362,"day_high":159.7,"day_low":150.85,"execution_condition_ko":"162.85~163.20 종가 회복은 초기 개선 관찰 신호이며 단독 매수 조건이 아니다. / 173.58 상회 종가와 다음 실제 거래일의 172.37~173.58 재시험·종가 지지를 확인한다. 이후 주문 시점에도 지지가 유효해야 한다.","risk_condition_ko":"148.8 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T11:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T12:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":347.36,"market_data_asof":"2026-11-18T11:57:00-05:00","session_vwap":349.9643787156044,"relative_volume":0.6547127399590569,"spread_bps":4.3183486634720705,"day_high":355.8,"day_low":340.74,"execution_condition_ko":"미래의 완결된 일봉에서 333.40–335.80 시험 후 335.80 위 종가 반등을 확인한다. 단순 접촉은 불충분하며 336.34 회복은 보강 증거다. / 그 다음 확인된 거래일에 지지가 유지되고 333.40–335.80 안에서 비용 차감 후 최소 2:1 보상비율이 확보되는지 확인한다. 위로 갭이 나면 추격하지 않는다.","risk_condition_ko":"327.8 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T11:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T12:00:00-05:00","expired_at_build":true,"provider_limitations":["feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":789.2000122070312,"market_data_asof":"2026-11-18T15:52:00+00:00","session_vwap":785.6648803580658,"relative_volume":1.0944751490977285,"spread_bps":null,"day_high":800.530029296875,"day_low":770.0,"execution_condition_ko":"753.03~760.00 재시험 후 종가 760.00 이상 회복과 다음 확인된 거래일 지지 유지. 현재는 매수 승인 조건이 아닌 재심사 조건이다. / 797.77~805.62 회복 이후 805.62~816.68의 지지 전환 여부. 가격 회복만으로 자동 매수하지 않는다.","risk_condition_ko":"747 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T15:52:00+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T15:55:00+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":358.085,"market_data_asof":"2026-11-18T11:57:00-05:00","session_vwap":362.0824539970878,"relative_volume":0.6034468204890618,"spread_bps":13.397342860331621,"day_high":368.845,"day_low":356.77,"execution_condition_ko":"351.19–353.50의 지지 방어와 일봉 종가 기준 실패를 구분한다. 단순 접촉은 매수 신호도 붕괴 확정도 아니다. / 375.44 초과 일봉 종가 이후 다음으로 확인된 거래일에 373.10–375.44가 지지되는지 확인한다. 현재는 재검토 신호이지 조건부 매수 주문이 아니다.","risk_condition_ko":"351.19 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T11:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T12:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":334.71,"market_data_asof":"2026-11-18T11:57:00-05:00","session_vwap":336.41769700309356,"relative_volume":0.40347507297869534,"spread_bps":7.17038630456243,"day_high":340.159,"day_low":332.42,"execution_condition_ko":"331.27~336.20 방어 또는 재회복 후 다음 실제 거래일의 저점 상승을 관찰한다. 구간 도달 자체는 매수 신호가 아니다. / 347.30 위 종가 후 다음 실제 거래일 345.09~347.30 재시험 지지를 확인한다.","risk_condition_ko":"331.27 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T11:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T12:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":309.82,"market_data_asof":"2026-11-18T11:57:00-05:00","session_vwap":318.3064216332136,"relative_volume":0.5610722986969247,"spread_bps":10.904076200251172,"day_high":329.25,"day_low":308.9262,"execution_condition_ko":"315.00–318.03은 2026-11-17 장중 훼손된 지지·재시험 구간이다. 종가 이탈이 확정되었다거나 견고한 바닥이라고 해석하지 않는다. / 332.36 초과 일봉 종가는 첫 회복 관문이며 매수 신호가 아니다.","risk_condition_ko":"305.8 이하 하락, 종가 확인 후 (보호 매도에 거래량 조건 없음) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T11:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T12:00:00-05:00","expired_at_build":true,"provider_limitations":["feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":73.9699,"market_data_asof":"2026-11-18T11:57:00-05:00","session_vwap":74.33964596097418,"relative_volume":0.9210009684578707,"spread_bps":1.3519908064632078,"day_high":74.76,"day_low":73.865,"execution_condition_ko":"75.96–76.10의 일봉 회복과 지지 실패를 구분한다. 제공된 2026-11-17 저가는 75.97이며 75.96은 더 넓은 지지 참고값이다. / 76.89–76.95 저항대와 76.95 상회 종가 이후의 후속 지지를 관찰한다. 단일 돌파만으로 매수하지 않는다.","risk_condition_ko":"75.96 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T11:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T12:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":280.06,"market_data_asof":"2026-11-18T16:57:03+00:00","session_vwap":null,"relative_volume":0.37926274571954444,"spread_bps":1.0709504685398559,"day_high":280.06,"day_low":280.06,"execution_condition_ko":"2026-11-18~2026-11-25를 1차 검토 기간으로 삼아 확인된 정규장 종가마다 지지·회복 여부를 점검한다. 2026-11-25는 계획 검토일이지 주문 만기나 거래 세션 확정일이 아니다. / 290.00 위 종가와 다음 확인된 세션의 286.26~290.00 지지 유지 시 새 구조적 손절과 가까운 293.44 저항부터 비용차감 손익비를 다시 계산한다. 유리한 비율을 만들기 위해 손절만 임의로 좁히지 않는다.","risk_condition_ko":"276.92 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T16:57:03+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T17:00:03+00:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":101.15,"market_data_asof":"2026-11-18T11:57:00-05:00","session_vwap":100.53270795757331,"relative_volume":0.49665603534615643,"spread_bps":2.965159377316643,"day_high":102.46,"day_low":99.59,"execution_condition_ko":"101.18–101.60 시험 후 종가 101.60 이상 회복을 관찰한다. 다음 거래일 해당 구간 내 체결기회가 없으면 추격하지 않는다. / 103.34–104.49 저항을 관찰한다. 104.49 상향 종가 돌파와 재시험 성공은 관찰조건 개선이지 자동 매수 승인이 아니다.","risk_condition_ko":"100.02 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T11:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T12:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WELL","display_name":"WELL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":247.2,"market_data_asof":"2026-11-18T16:57:03+00:00","session_vwap":246.13705109257407,"relative_volume":0.8361952466992992,"spread_bps":7.685928682672183,"day_high":248.265,"day_low":241.98,"execution_condition_ko":"2026-11-18 이후의 정규장 여부를 확인하고 242.46~244.08 시험, 244.08 이상 종가, 다음 거래일 242.46~243.50 진입 기회를 순서대로 관찰한다. / 249.75 초과 종가는 완료된 거래일끼리 거래량을 비교하고 후속 지지 확인과 함께 평가한다. 약 1.05배였던 기존 거래량만으로 강한 수요 확인을 주장하지 않는다.","risk_condition_ko":"241.52 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T16:57:03+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T17:00:03+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":577.425,"market_data_asof":"2026-11-18T16:57:03+00:00","session_vwap":579.3988336051004,"relative_volume":0.5180355820562658,"spread_bps":1.5586439797381797,"day_high":583.72,"day_low":576.36,"execution_condition_ko":"제공된 결정 시계 2026-11-18T06:16:32.728417-05:00 기준으로 조건부 진입 만료는 지나지 않았다. 다만 실제 거래 세션·휴장·조기폐장·최신 가격은 별도 확인해야 한다. / 2026-11-18T06:00:21-05:00의 582.66은 지연된 저유동성 개장 전 관측이다. 현재 체결가나 정규장 진입 조건 충족으로 취급하지 않는다.","risk_condition_ko":"580.91 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T16:57:03+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T17:00:03+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":170.68,"market_data_asof":"2026-11-18T11:57:00-05:00","session_vwap":170.51208318846992,"relative_volume":0.3650982253204223,"spread_bps":4.686584651435999,"day_high":171.64,"day_low":169.415,"execution_condition_ko":"167.96~168.66 접촉, 168.66 이상 회복 종가, 다음 유효 거래일 재시험과 168.47 이상 지지 종가를 순차 확인한다. 확인 후 가격 재하락이 새로운 약세인지 주문 직전에 재점검한다. / 170.73~171.24 지지 후보와 173.57~173.59 저항을 관찰한다. 상대강도지수 73.10→69.32와 양수인 이동평균 수렴·확산 지표 막대값의 감소는 경계 신호이나 단독 매도 근거로 보지 않는다.","risk_condition_ko":"168.47 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T11:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T12:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1106.2578,"market_data_asof":"2026-11-18T11:57:00-05:00","session_vwap":1104.482315003548,"relative_volume":0.47227890930784305,"spread_bps":5.603658646807887,"day_high":1110.45,"day_low":1097.5,"execution_condition_ko":"1091.92–1092.64: 지지 시험, 1092.64 이상 일봉 마감, 다음 거래일 지지 재확인 순으로 관찰한다. 매수는 해당 구간 안에서만 가능하다. / 1104.89–1108.68: 최근 지지 유지와 회복을 확인한다. 지연된 개장 전 관측만으로 붕괴나 회복을 확정하지 않는다.","risk_condition_ko":"1,081.06 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T11:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T12:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":417.11,"market_data_asof":"2026-11-18T11:57:00-05:00","session_vwap":414.9085982776717,"relative_volume":0.4617311540799189,"spread_bps":1.6781138000885367,"day_high":417.88,"day_low":411.83,"execution_condition_ko":"411.99~416.41 방어, 416.41 위 종가 재회복, 다음 실제 정규 세션의 재시험·반등을 순서대로 확인한다. 구간 내 가격만으로 진입하지 않는다. / 421.12~422.23은 회복·청산 재평가 구간이며 추격 지시가 아니다. 동적 평균선은 최신 검증 일봉으로 갱신한다. 추가 저항은 425.19~425.76, 430.99, 435.95~441.41이다.","risk_condition_ko":"411.99 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T11:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T12:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WMT","display_name":"WMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":126.58,"market_data_asof":"2026-11-18T11:57:00-05:00","session_vwap":126.34541699949934,"relative_volume":0.8188562425982837,"spread_bps":2.369949046095599,"day_high":127.255,"day_low":125.07,"execution_condition_ko":"공식 발표 정보를 최우선 확인한다. 중립 분석가가 지적한 대로 15건 중 목표가격 관련 6건은 독립적인 실적 근거로 중복 계산하지 않는다. / 126.31–126.40의 새 종가 확인과 다음 거래일 재지지를 관찰하되 범위 밖 추격은 금지한다.","risk_condition_ko":"126.31 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T11:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T12:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LIN","display_name":"LIN","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":510.535,"market_data_asof":"2026-11-18T11:57:00-05:00","session_vwap":510.29912642763605,"relative_volume":0.3791540834805174,"spread_bps":3.5243670824115836,"day_high":512.01,"day_low":508.0,"execution_condition_ko":"510.01~514.34: 지지 시험, 514.34 초과 종가, 다음 거래일 구간 내 지지 확인 및 비용 후 최소 2:1 구조적 보상 대비 위험을 순서대로 점검한다. / 518.62~519.72: 전체 구간 회복과 후속 지지 여부를 관찰하되 자동 매수나 추가 매수는 하지 않는다.","risk_condition_ko":"510.01 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T11:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T12:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":289.29,"market_data_asof":"2026-11-18T16:57:03+00:00","session_vwap":289.21999946325775,"relative_volume":0.4568003987120148,"spread_bps":2.7653911300074006,"day_high":292.55,"day_low":287.0,"execution_condition_ko":"291.00~292.84 유지와 294.06 회복은 개선 신호지만 자동 매수 조건은 아니다. / 284.70~288.00 시험 후 지정 구간의 상승 종가와 다음 검증된 거래일의 일봉 지지를 순서대로 확인한다. 가격이 287.50 위로 떠나면 추격하지 않는다.","risk_condition_ko":"284.7 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T16:57:03+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T17:00:03+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"KO","display_name":"KO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":98.3101,"market_data_asof":"2026-11-18T16:57:03+00:00","session_vwap":97.99013401099936,"relative_volume":0.5395840280195199,"spread_bps":2.0343810395683066,"day_high":98.87,"day_low":97.16,"execution_condition_ko":"97.38~98.53 시험, 98.53 이상 마감, 다음 정규 세션 재시험 지지를 순서대로 확인한다. 11/17 저가가 구간 상단에 닿았다는 사실만으로 전체 과정 충족을 가정하지 않는다. / 100.56 상회 마감과 갱신된 20일 평균 대비 정규장 거래량 개선 이후 다음 세션 지지를 확인한다. 재시험 없이 멀어지면 추격하지 않는다.","risk_condition_ko":"97.38 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T16:57:03+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T17:00:03+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SO","display_name":"SO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":94.09,"market_data_asof":"2026-11-18T16:57:03+00:00","session_vwap":93.85975988282524,"relative_volume":0.40737070481058985,"spread_bps":3.188944990699031,"day_high":94.3,"day_low":93.13,"execution_condition_ko":"2026-11-17 종가 93.60을 기준으로 이후 확정 일봉의 지지 유지와 추진력 변화를 점검한다. 지연 장전 표시 93.19는 진입 확인에 사용하지 않는다. / 조달 원문 검증, 회복 종가, 다음 실제 정규장 지지, 92.70~92.95 체결 범위 및 비용 후 손익비가 모두 충족될 때만 최초 소규모 진입 후보를 활성화한다. 범위 밖에서는 추격하지 않는다.","risk_condition_ko":"91.17 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T16:57:03+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T17:00:03+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GE","display_name":"GE","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":326.1099853515625,"market_data_asof":"2026-11-18T15:52:00+00:00","session_vwap":328.074657610599,"relative_volume":0.5505320710970234,"spread_bps":null,"day_high":331.7099914550781,"day_low":325.0400085449219,"execution_condition_ko":"11월 17일 회복 다음 실제 정규 거래세션의 323.28~323.40 지지 유지와 확인 이후 323.40~324.00 체결 기회. / 새 지지 시험이 발생하면 그날 종가 324.00 이상 회복 후 다음 실제 거래세션 지지를 다시 확인한다. 확인 이전의 체결 기회를 소급 적용하지 않는다.","risk_condition_ko":"323.28 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T15:52:00+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T15:55:00+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":644.115,"market_data_asof":"2026-11-18T11:57:00-05:00","session_vwap":640.9753983940705,"relative_volume":0.3929041061031778,"spread_bps":4.501672604218802,"day_high":647.1,"day_low":636.41,"execution_condition_ko":"2026-11-18부터 새 일봉의 638.01~644.88 지지 시험과 하락 중단을 관찰한다. 단순 가격 접촉은 매수 신호가 아니다. / 다음 실제 거래일에도 지지와 저점 안정이 유지되고 실제 매수가가 비용 반영 상한 이하일 때만 소액 진입 조건을 평가한다. 재하락이 안정적 재시험인지 새로운 매도 압력인지 구분한다.","risk_condition_ko":"638.01 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T11:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T12:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LRCX","display_name":"Lam Research","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":208.385,"market_data_asof":"2026-11-18T11:57:00-05:00","session_vwap":211.55851594720215,"relative_volume":0.40111223559107606,"spread_bps":11.03726275883532,"day_high":214.9,"day_low":206.43,"execution_condition_ko":"위험 대응 조건: 201.91 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"201.91 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T11:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T12:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOG","display_name":"GOOG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":277.365,"market_data_asof":"2026-11-18T11:57:00-05:00","session_vwap":279.60069063527595,"relative_volume":0.4084532138381398,"spread_bps":1.8029387902284815,"day_high":282.3599,"day_low":276.89,"execution_condition_ko":"위험 대응 조건: 275.35 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"275.35 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-18T11:57:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T12:00:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AIQUY","display_name":"AIQUY","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":"2026-11-17","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-18 이후 완료된 일봉에서 41.61~41.71 시험과 종가 41.80 이상 반등을 확인하고 다음 실제 거래일 재지지를 점검한다. / 42.16 회복과 다음 거래일 유지, 42.34~42.96 매물대 반응을 관찰한다. 42.96 돌파 후에도 43.45~43.57 저항까지 공간이 좁아 추격하지 않는다.","risk_condition_ko":"41.61 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-17"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
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
