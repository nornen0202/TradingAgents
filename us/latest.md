# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-10T07:40:42.783383+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261110T022226_local-scheduler-us-full",
  "producer_finished_at": "2026-11-10T05:43:34.484106+09:00",
  "analysis_run_id": "20261110T022226_local-scheduler-us-full",
  "analysis_completed_at": "2026-11-10T05:12:20.114745+09:00",
  "analysis_trade_date_oldest": "2026-11-06",
  "analysis_trade_date_latest": "2026-11-06",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-09T12:20:00-05:00",
  "market_data_latest_at": "2026-11-09T14:50:00-05:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-10T05:12:57.627379+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-10T05:12:57.627379+09:00",
    "run_started_at": "2026-11-10T02:22:26.174438+09:00",
    "run_finished_at": "2026-11-10T05:43:34.484106+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23962358,
    "total_market_value_krw": 22732747,
    "total_unrealized_pnl_krw": -1229611,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 113547,
    "total_equity_krw": 23822946
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 553575,
      "current_price_krw": 531964,
      "market_value_krw": 6383569,
      "unrealized_pnl_krw": -259332
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 296708,
      "current_price_krw": 301114,
      "market_value_krw": 3312257,
      "unrealized_pnl_krw": 48465
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 430357,
      "current_price_krw": 393112,
      "market_value_krw": 2358672,
      "unrealized_pnl_krw": -223473
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1907496,
      "current_price_krw": 1880922,
      "market_value_krw": 1880922,
      "unrealized_pnl_krw": -26574
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 564068,
      "current_price_krw": 492007,
      "market_value_krw": 1476023,
      "unrealized_pnl_krw": -216182
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 271154,
      "current_price_krw": 240932,
      "market_value_krw": 1445593,
      "unrealized_pnl_krw": -181333
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 136484,
      "current_price_krw": 136467,
      "market_value_krw": 1228209,
      "unrealized_pnl_krw": -152
    },
    {
      "ticker": "GEV",
      "name": "GE버노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1494423,
      "current_price_krw": 1134416,
      "market_value_krw": 1134416,
      "unrealized_pnl_krw": -360007
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 369910,
      "current_price_krw": 477342,
      "market_value_krw": 954685,
      "unrealized_pnl_krw": 214865
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1440746,
      "current_price_krw": 1925310,
      "market_value_krw": 839560,
      "unrealized_pnl_krw": 211301
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 672438,
      "current_price_krw": 472834,
      "market_value_krw": 472834,
      "unrealized_pnl_krw": -199604
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 138204,
      "current_price_krw": 111076,
      "market_value_krw": 444304,
      "unrealized_pnl_krw": -108515
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 577956,
      "current_price_krw": 436619,
      "market_value_krw": 436619,
      "unrealized_pnl_krw": -141337
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 352836,
      "current_price_krw": 365084,
      "market_value_krw": 365084,
      "unrealized_pnl_krw": 12248
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":389.26,"market_data_asof":"2026-11-09T13:25:00-05:00","session_vwap":388.8746838833048,"relative_volume":0.50924308539624,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"398.14–400.76 회복과 지지 여부를 확인하고 200일 평균 400.03 등 날짜가 지난 평균값은 갱신한다. / 375.44, 367.95 및 351.19–353.10을 관찰한다. 해당 가격이 지지를 보장하지는 않는다.","risk_condition_ko":"400.03 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T13:25:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T13:28:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":361.75,"market_data_asof":"2026-11-09T12:40:00-05:00","session_vwap":358.5287609467266,"relative_volume":0.6235939159993484,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"향후 2~5개 확인된 거래세션 동안 364.10~366.95의 회복 또는 저항 거부를 관찰한다. 단순 접근은 거부 확인이 아니다. / 366.95 위 종가 이후 다음 확인된 거래세션의 재시험 지지와 종가 유지를 확인한다. 검증된 상대거래량 1 이상과 히스토그램 개선은 보강 근거이며 제공된 상대거래량 0.62는 돌파 참여를 확인하지 못한다.","risk_condition_ko":"345.28 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T12:40:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T12:43:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":291.04,"market_data_asof":"2026-11-09T12:50:00-05:00","session_vwap":293.64529352908465,"relative_volume":0.6386095639285461,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"293.65~294.63 회복대를 관찰하되 2026-11-09 장중 거래량가중평균가격과 2026-11-06 10일 지수이동평균이라는 서로 다른 관측시점의 동적 기준이므로 갱신한다. / 296.49 위 종가와 다음 실제 거래일의 296.33~296.49 지지를 확인하면 신속히 재평가한다. 원공시·타당한 손절·개선된 비용 반영 보상·위험이 확보돼야 별도의 소규모 진입을 검토하며 현재 조건부 매수는 없다.","risk_condition_ko":"284.59 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T12:50:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T12:53:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":176.65,"market_data_asof":"2026-11-09T13:05:00-05:00","session_vwap":176.45454367866168,"relative_volume":3.2300219973734117,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"179.92 상회 종가와 이후 181.46~186.64 구간의 안착 또는 거부를 관찰한다. 그 자체로 매수를 허용하지 않는다. / 196.25 상회 종가와 다음 검증된 거래일의 194.90 이상 종가 유지 시 방향성·일차 재무자료·새로운 위험 대비 보상을 재심사한다. 매도 위험이 해소되어야 소액 신규 진입을 검토할 수 있다.","risk_condition_ko":"204.39 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T13:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T13:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":320.8881,"market_data_asof":"2026-11-09T12:20:00-05:00","session_vwap":313.63721335468756,"relative_volume":0.9806383648097778,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"AVGO의 검증된 일봉 종가와 다음 확인된 정규 거래일의 319.55–323.87 지지·재돌파를 관찰한다. 분봉, 특정 시각, 거래량가중평균가격 또는 수치화된 상대거래량을 기계적으로 요구하지 않는다. / 321.28–323.87 및 332.13–335.74 저항 거부, 이후 304.292 하회 종가, 288.98–290.12 하단 구간을 구분해 감시한다. 단순 접촉은 저항 거부가 아니다.","risk_condition_ko":"304.29 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T12:20:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T12:23:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":829.545,"market_data_asof":"2026-11-09T12:40:00-05:00","session_vwap":823.5709948503691,"relative_volume":0.650429591382767,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"821.50–823.57 재시험과 832.76 회복을 관찰한다. 어느 하나만으로 매수하지 않는다. 823.57은 과거 거래량가중평균가이지 향후 고정 지지나 필수 매수 조건이 아니다. / 846.59 초과 종가 이후 다음 확인된 거래일의 842.34–846.59 유지 여부를 평가한다. 다음 저항 857.87–862.25까지의 여유를 계산하고 이동평균 등 변동 지표를 갱신한다.","risk_condition_ko":"821.5 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T12:40:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T12:43:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":352.52,"market_data_asof":"2026-11-09T12:20:00-05:00","session_vwap":344.6307985382199,"relative_volume":0.6443468604022188,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"354.50 상회 종가와 다음 확인된 정규거래일의 350.36~354.50 지지 또는 재돌파를 관찰한다. 당시 실제 진입가·손절가·저항까지의 비용 후 보상을 다시 계산한다. / 336.65 아래 종가, 325.10~328.30 방어 구간 하단 이탈, 315.00 반등 무효화를 구분하고 누적 축소량을 확인한다.","risk_condition_ko":"336.65 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T12:20:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T12:23:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":349.91,"market_data_asof":"2026-11-09T12:20:00-05:00","session_vwap":349.1500555216819,"relative_volume":0.47484137173577323,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"335.26~338.30 재시험 후 336.01 이상 마감과 다음 실제 거래일 지지 유지: 336.01~338.30의 조건부 초기 매수 후보. / 최초 진입 이후 별도의 338.30 회복 마감과 후속 지지: 추가 25% 검토. 최초 매수와 자동으로 동시 집행하지 않는다.","risk_condition_ko":"335.26 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T12:20:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T12:23:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":221.379,"market_data_asof":"2026-11-09T13:10:00-05:00","session_vwap":219.88660880582245,"relative_volume":0.6460805418583522,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"218.09~218.47 재시험부터 종가 회복과 다음 정규 세션의 일봉 지지까지 순서대로 확인한다. 확인 후 재하락이 체결 기회인지 새로운 지지 훼손인지 재검토한다. / 221.44 회복만으로 추격하거나 비중을 확대하지 않는다. 223.33~224.20 저항까지의 순보상과 새로운 철회 기준을 재계산한다.","risk_condition_ko":"214.54 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T13:10:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T13:13:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":268.975,"market_data_asof":"2026-11-09T12:20:00-05:00","session_vwap":270.85770789813097,"relative_volume":0.8267518475572102,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"258.53–259.30 구간은 단순 접촉으로 매수하지 않는다. 재시험과 259.30 초과 종가 이후 후속 거래일 되돌림을 기다린다. / 완료 일봉 종가가 258.53 미만이면 최초 매수를 일시중단하고 새로운 적격 회복을 요구한다. 252.27 미만에서는 기존 허가를 취소한다.","risk_condition_ko":"252.27 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T12:20:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T12:23:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":81.1499,"market_data_asof":"2026-11-09T12:45:00-05:00","session_vwap":81.46406642987775,"relative_volume":0.5380118516005171,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-09 이후 새 정규장 종가부터 지지 시험·회복·다음 거래일 지지의 순서를 매일 점검한다. 날짜만으로 거래 세션이나 조건 성립을 추정하지 않는다. / 81.78, 82.20–82.60 및 갱신된 50일 평균을 관찰한다. 83.07은 2026-11-06의 평균값이지 앞으로 고정되는 돌파 기준이 아니다.","risk_condition_ko":"79.52 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T12:45:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T12:48:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1355.57,"market_data_asof":"2026-11-09T13:00:00-05:00","session_vwap":1318.6308149380552,"relative_volume":0.5668802120916593,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1319 이상 완결 종가 이후 다음 실제 거래일의 1317–1319 지지와 1317–1320 체결 가능성을 확인한다. 가격 조건만이 아니라 거래 가능 상태·호가·비용·계좌 여유·중대한 미확인 행사 위험도 재검토한다. / 1364 초과 종가와 후속 지지는 별도 확대 검토 신호일 뿐이다. 이번 조건부 권한은 되돌림 소액 매수만 포함한다.","risk_condition_ko":"1,317 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T13:00:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T13:03:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.495,"market_data_asof":"2026-11-09T13:15:00-05:00","session_vwap":100.49585038368205,"relative_volume":0.9506699586444798,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"발행사 핵심 자료, 동일 시점 가격과 순자산가치, 기존 집중도 및 실제 지급일·결제 가능성을 우선 검증한다. / 핵심 검증을 통과한 뒤 종가 100.50 초과와 다음 확인된 거래일 100.49–100.50 유지 또는 회복이면 전술적 편입을 재심사한다. 현재 활성화된 조건부 매수는 아니다.","risk_condition_ko":"100.42 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T13:15:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T13:18:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1404.05,"market_data_asof":"2026-11-09T12:55:00-05:00","session_vwap":1392.336889803243,"relative_volume":0.509564889724305,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-06 지지 확인 이후 다음 실제 거래일이 언제인지와 해당 진입 기회의 유효성을 확인한다. 기회가 지났다면 1330~1333.22 재시험과 1333.22 이상 종가를 새로 요구한다. / 지지 유지 및 정보 검증 후 1333.22~1345.76 안의 체결 가능 가격을 관찰하되, 비용·가격 공백 반영 상한을 넘으면 매수하지 않는다.","risk_condition_ko":"1,330 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T12:55:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T12:58:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1059.258,"market_data_asof":"2026-11-09T14:00:00-05:00","session_vwap":1052.3995862295037,"relative_volume":0.3529954190020104,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1043~1045.73 접근, 1045.73 이상 일봉 회복, 다음 실제 거래일 1043 지지와 진입대 내 가격을 순차 확인한다. 진입대를 벗어나 반등하면 추격하지 않는다. / 1065.59 상회 일봉 마감과 1063.02~1065.59 재지지는 별도 관찰 대상이다. 이번 계획의 자동 진입·추가매수 신호가 아니다.","risk_condition_ko":"1,043 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T14:00:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T14:03:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":573.82,"market_data_asof":"2026-11-09T13:45:00-05:00","session_vwap":568.4443954614042,"relative_volume":0.44191824408121994,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"새로운 557.90~559.61 시험, 559.61 이상 일봉 마감, 다음 확인된 거래일의 구간 내 지지 재시험을 순서대로 관찰한다. 현재 충족된 신규 진입 조건은 없다. / 579.09~580.65 및 586.30은 저항과 손익비 재평가 구간이다. 자동 매수·자동 차익실현 가격이 아니며, 저항 도달 후 지속적인 모멘텀 약화가 확인되면 부분 차익실현을 별도 검토한다.","risk_condition_ko":"557.9 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T13:45:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T13:48:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":659.77,"market_data_asof":"2026-11-09T18:54:57+00:00","session_vwap":656.445710569319,"relative_volume":0.3754838090053448,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"643.68–648.54 시험, 643.68 이상 지지 종가, 다음 검증 거래일의 지지 유지 및 조정된 매수 상한 이내 실행가격을 함께 확인한다. / 661.34 상회 종가와 후속 지지는 별도 검토만 촉발하며 현재 계획의 매수 신호가 아니다.","risk_condition_ko":"636.93 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T18:54:57+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T18:57:57+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":168.13,"market_data_asof":"2026-11-09T14:05:00-05:00","session_vwap":167.47717420778116,"relative_volume":0.3191718954738325,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"162.13~163.07 시험 이후 163.07 상회 일봉 종가와 다음 검증된 거래일의 구간 내 지지·반등을 순서대로 확인한다. 구간 위 추격은 금지한다. / 165.40 상회는 두 번째 물량의 검토 기준이다. 기존 170.52 저항까지 거리가 줄어 손익비가 악화될 수 있으므로 가격 회복만으로 증액하지 않는다.","risk_condition_ko":"162.13 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T14:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T14:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SPG","display_name":"Simon Property Group","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":233.38,"market_data_asof":"2026-11-09T14:40:00-05:00","session_vwap":231.72906649916456,"relative_volume":0.502901665918832,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"220.75–222.28 시험, 222.28 이상 일봉 종가 회복, 다음 검증된 거래 세션의 220.75 지지를 순서대로 확인한다. 실제 진입가는 222.28 이하여야 한다. / 깊은 조정 이후 228.42–228.965를 첫 회복 점검대로 관찰한다. 현재 지지가 확인되었다는 뜻은 아니다.","risk_condition_ko":"220.75 이하 하락, 종가 확인 후 (위험축소에는 거래량 확인이 필요하지 않다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T14:40:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T14:43:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":423.895,"market_data_asof":"2026-11-09T14:10:00-05:00","session_vwap":422.0565411413849,"relative_volume":0.4121902494452006,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"새 일봉 확인 다음 실제 거래일의 417.69–417.87 지지 재시험을 관찰한다. 신규 확인과 실제 진입 모두 만료 전이어야 하며 지지 감소 절차가 진행 중이면 매수하지 않는다. / 412.75–415.22는 더 깊은 지지의 재검토 구간일 뿐 두 번째 매수 구간이나 물타기 승인이 아니다.","risk_condition_ko":"412.75 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T14:10:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T14:13:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"KO","display_name":"KO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":95.79,"market_data_asof":"2026-11-09T14:20:00-05:00","session_vwap":95.51581334235124,"relative_volume":0.35742617274787836,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"검증된 거래일마다 종가를 점검하고 늦어도 2026-11-16T23:59:59-05:00까지 공식 재평가한다. 매수 승인 만료는 보유분의 자동 청산을 뜻하지 않는다. / 94.12–94.48 시험, 94.48 이상 회복 종가와 다음 실제 거래일의 같은 기준 충족을 순서대로 확인한다. 실행 가격은 계속 94.12–94.50으로 제한한다.","risk_condition_ko":"94.12 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T14:20:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T14:23:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LIN","display_name":"LIN","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":522.16,"market_data_asof":"2026-11-09T14:10:00-05:00","session_vwap":518.0396264253587,"relative_volume":0.28409044696050983,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"필수 원문 검증과 지지 회복·다음 세션 확인이 모두 끝난 뒤에도 512.23~513.65에서 체결 가능한지 점검한다. 범위로 돌아오지 않으면 미체결을 받아들인다. / 522.55, 526.56, 533.39 도달 시 매도 압력과 이익실현 필요성을 재평가한다. 526.56 종가 돌파와 후속 지지 전환은 별도 판단 사항이며 자동 매수하지 않는다.","risk_condition_ko":"512.23 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T14:10:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T14:13:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WMT","display_name":"WMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":125.485,"market_data_asof":"2026-11-09T14:25:00-05:00","session_vwap":124.63873857878909,"relative_volume":0.41932049798417503,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"새 일봉의 123.03–124.64 지지 시험과 124.22 이상 종가를 확인한 뒤 다음 검증된 거래일의 123.03–124.30 진입 가능성을 점검한다. / 124.22와 123.03의 종가 이탈 및 다음 거래일 회복 실패를 확인하고 단계별 매도 조건과 기존 체결을 대조한다.","risk_condition_ko":"124.22 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T14:25:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T14:28:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":293.615,"market_data_asof":"2026-11-09T13:50:00-05:00","session_vwap":292.1418015113387,"relative_volume":0.42717412864661375,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"298.74와 302.93에서 단계적 부분 매도 가능 여부와 저항 반응을 확인한다. 두 가격은 적정가치가 아니다. / 288.80~289.00 재시험, 289.00 이상 마감 및 다음 실제 거래일 지지 유지 시 신규 매수를 재심사하되 이번 결정만으로 매수하지 않는다.","risk_condition_ko":"298.74 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T13:50:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T13:53:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SO","display_name":"SO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":93.83,"market_data_asof":"2026-11-09T14:30:00-05:00","session_vwap":93.26529079558263,"relative_volume":0.4357455292252321,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최초 진입에도 핵심 공시 검증을 요구한다. 핵심 위험을 평가할 수 없으면 가격 조건이 충족돼도 대기한다. / 완성 일봉의 91.65~91.85 시험과 91.85 이상 마감 후 다음 실제 거래일 재시험이 유지되면 소규모 진입을 평가한다.","risk_condition_ko":"91.65 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T14:30:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T14:33:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WELL","display_name":"WELL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":246.22,"market_data_asof":"2026-11-09T14:30:00-05:00","session_vwap":246.69950785203588,"relative_volume":0.34613628229710525,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단 기준은 2026-11-09이며 최신 완료 일봉 근거는 2026-11-06이다. 실행 전 일봉 가격과 지지 구조를 갱신하고 실제 거래일·장 운영·거래 가능 여부와 호가 신선도를 확인한다. 지연된 2026-11-09 시세는 진입 확인 자료가 아니다. / 제공된 판단시각 2026-11-09T14:48:22.190484-05:00은 2026-11-16T23:59:59-05:00보다 이르다. 논쟁의 다른 시각 표기는 재확인하되 만료로 해석하지 않는다. 유효기한은 분석상 재검토 마감이지 검증된 거래소 폐장시각이 아니다.","risk_condition_ko":"240.18 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T14:30:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T14:33:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CDNS","display_name":"Cadence Design Systems","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":336.35,"market_data_asof":"2026-11-09T13:30:00-05:00","session_vwap":332.6142116990814,"relative_volume":0.2531285489868111,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"332.61–333.00은 고정된 관찰가격 구간이지 미래 거래량가중평균가격이 아니다. 333.00 위에서는 이번 계획으로 매수하지 않는다. / 336.5037 위 종가와 거래 참여도 개선을 관찰하되, 상대거래량의 임의 최소치를 만들지 않는다.","risk_condition_ko":"327.73 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T13:30:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T13:33:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"JPM","display_name":"JPM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":342.88,"market_data_asof":"2026-11-09T14:50:00-05:00","session_vwap":340.5270887299429,"relative_volume":0.2952261442041818,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"339.46 이탈 이후의 다음 실제 거래세션과 해당 종가를 우선 확인한다. 장중 342.88 회복으로 확인 절차를 초기화하지 않는다. / 340.53~340.93 재시험 후 340.93 위 종가와 후속 지지를 관찰한다. 340.53은 과거 관측 누적 거래량가중평균가격의 고정 관찰선이지 실시간 지표가 아니다.","risk_condition_ko":"339.46 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T14:50:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T14:53:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SNPS","display_name":"Synopsys","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":467.73,"market_data_asof":"2026-11-09T13:30:00-05:00","session_vwap":465.0063862276702,"relative_volume":0.3513324263478831,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"450.46–453.60 시험, 완성된 일봉 종가 453.60 이상, 다음 검증된 거래일의 450.46 지지와 구간 내 재시험을 순서대로 확인한다. 모두 충족돼야 최초 시험 편입이 가능하다. / 458.93, 469.30, 475.40 및 481.90–491.39에서 회복 지속과 저항 반응을 점검한다. 상대강도지수 50 초과와 음의 추세 지표 개선은 보조 근거이지 추가적인 분 단위 매매 조건이 아니다.","risk_condition_ko":"441.61 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T13:30:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T13:33:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMD","display_name":"Advanced Micro Devices","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":505.63,"market_data_asof":"2026-11-09T13:35:00-05:00","session_vwap":489.9487442456519,"relative_volume":1.266949711503068,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"487.93–492.59 시험과 492.59 이상 종가를 확인한 뒤 다음 실제 거래일의 지지를 점검한다. 구간 내 체결 기회가 없으면 매수하지 않는다. / 514.61 회복, 512.82–514.61 지지, 529.98 및 546.81 저항을 관찰한다. 후속 가격 회복은 재심사 조건이지 자동 증액 신호가 아니다.","risk_condition_ko":"487.93 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T13:35:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T13:38:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-10T03:14:15.100895+09:00",
  "as_of": "2026-11-09T17:19:52+00:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
