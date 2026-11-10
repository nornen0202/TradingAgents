# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-10T13:40:35.199947+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261110T175022_local-scheduler-us-full",
  "producer_finished_at": "2026-11-10T21:08:30.645921+09:00",
  "analysis_run_id": "20261110T175022_local-scheduler-us-full",
  "analysis_completed_at": "2026-11-10T20:34:00.440522+09:00",
  "analysis_trade_date_oldest": "2026-11-09",
  "analysis_trade_date_latest": "2026-11-09",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-09T15:55:00-05:00",
  "market_data_latest_at": "2026-11-10T05:50:00-05:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-10T20:34:30.285546+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-10T20:34:30.285546+09:00",
    "run_started_at": "2026-11-10T17:50:22.213699+09:00",
    "run_finished_at": "2026-11-10T21:08:30.645921+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23923536,
    "total_market_value_krw": 22671120,
    "total_unrealized_pnl_krw": -1252416,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 113363,
    "total_equity_krw": 23761135
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 552678,
      "current_price_krw": 529573,
      "market_value_krw": 6354879,
      "unrealized_pnl_krw": -277259
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 296227,
      "current_price_krw": 300762,
      "market_value_krw": 3308382,
      "unrealized_pnl_krw": 49878
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 429660,
      "current_price_krw": 394305,
      "market_value_krw": 2365832,
      "unrealized_pnl_krw": -212130
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1904406,
      "current_price_krw": 1866097,
      "market_value_krw": 1866097,
      "unrealized_pnl_krw": -38309
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 563154,
      "current_price_krw": 492278,
      "market_value_krw": 1476835,
      "unrealized_pnl_krw": -212628
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 270715,
      "current_price_krw": 243944,
      "market_value_krw": 1463667,
      "unrealized_pnl_krw": -160623
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 136263,
      "current_price_krw": 136248,
      "market_value_krw": 1226233,
      "unrealized_pnl_krw": -138
    },
    {
      "ticker": "GEV",
      "name": "GE 버노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1492002,
      "current_price_krw": 1115971,
      "market_value_krw": 1115971,
      "unrealized_pnl_krw": -376031
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 369311,
      "current_price_krw": 476135,
      "market_value_krw": 952270,
      "unrealized_pnl_krw": 213648
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1438411,
      "current_price_krw": 1923467,
      "market_value_krw": 838756,
      "unrealized_pnl_krw": 211515
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 671349,
      "current_price_krw": 470360,
      "market_value_krw": 470360,
      "unrealized_pnl_krw": -200989
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 137980,
      "current_price_krw": 109174,
      "market_value_krw": 436698,
      "unrealized_pnl_krw": -115225
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 577019,
      "current_price_krw": 430765,
      "market_value_krw": 430765,
      "unrealized_pnl_krw": -146254
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 352265,
      "current_price_krw": 364375,
      "market_value_krw": 364375,
      "unrealized_pnl_krw": 12110
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":393.04,"market_data_asof":"2026-11-10T04:35:00-05:00","session_vwap":393.0101882009402,"relative_volume":0.08276561171363866,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"391.61–394.39와 396.41–400.31의 저항 반응을 관찰한다. 구간 도달만으로 매수하지 않는다. / 380.33–380.78, 이어 367.95–375.44와 351.19–353.10을 구별해 관찰한다. 어느 구간도 자동 저가매수 지점이 아니다.","risk_condition_ko":"391.61 이상 도달, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T04:35:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T04:38:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":181.51,"market_data_asof":"2026-11-10T04:20:00-05:00","session_vwap":181.08104461743392,"relative_volume":0.17879566175375136,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"183.10 위 종가는 초기 회복 관찰 신호일 뿐 매수 주문 조건이 아니다. / 186.64 위 종가 후 다음 실제 거래일 185.22~186.64 지지와 비용 후 보상 대비 위험을 점검한다. 회복이 유지되면 아직 발생하지 않은 실패 반등을 가정해 추가 매도하지 않는다.","risk_condition_ko":"185.22 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T04:20:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T04:23:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":828.0,"market_data_asof":"2026-11-10T04:05:00-05:00","session_vwap":829.4952893674293,"relative_volume":0.0036221926772743687,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"843.12 초과 종가와 다음 확인된 거래일의 839.98–843.12 지지를 관찰한다. 921.42까지 기다리지 않고 재평가하되 자동 매수하지 않는다. / 795.95–806.40과 750.00–751.25 지지 구간을 관찰한다. 지지 구간 도달 자체는 매수 신호가 아니다.","risk_condition_ko":"795.95 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T04:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T04:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":290.41,"market_data_asof":"2026-11-10T04:05:00-05:00","session_vwap":290.9023152319829,"relative_volume":0.027317007562051125,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"288.01~288.15 유지 여부와 이후 282.57~284.78의 종가 방어 여부를 점검한다. / 293.46 회복 이후 296.02~296.49 돌파·재지지를 관찰한다. 저항 접근만으로 매수하지 않는다.","risk_condition_ko":"282.57 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T04:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T04:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":359.99,"market_data_asof":"2026-11-10T04:05:00-05:00","session_vwap":358.2130177514793,"relative_volume":0.0009987885252915568,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"363.23~365.34 저항 거부와 365.34 위 종가 회복을 구분한다. 현재 어느 조건도 충족됐다고 간주하지 않는다. / 상단 369.97~378.23, 391.70~399.30, 396.35·404.40을 관찰한다. 먼 저항을 선택해 가까운 매물 부담을 무시하지 않으며 이동평균은 재산출한다.","risk_condition_ko":"345.28 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T04:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T04:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":346.31,"market_data_asof":"2026-11-10T08:51:16+00:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"337.81의 종가 이탈과 다음 확인된 거래일의 회복 실패를 관찰한다. 기준 종가에서는 미발동이다. / 지지 범위는 하단 325.10·상단 328.30, 깊은 무효화 수준은 315.00이다.","risk_condition_ko":"337.81 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T08:51:16+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T08:54:16+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":350.69,"market_data_asof":"2026-11-10T08:50:49+00:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-10 이후 실제 정규장 일봉의 344.17–344.78 시험 또는 회복과 344.78 이상 종가를 확인하고, 다음 실제 거래일 종가 확인 뒤 같은 구간에서만 신규 진입을 검토한다. / 351.43–352.33과 354.50–355.38 저항을 관찰한다. 355.38 돌파는 별도 추가 투자 검토 신호이며 자동 매수나 확정 수익 목표가 아니다.","risk_condition_ko":"336.63 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T08:50:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T08:53:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":319.48,"market_data_asof":"2026-11-10T08:50:33+00:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-10 연구 기준 이후 새로 완료된 일봉이 311.52–314.00을 시험하고 311.52 이상에서 마감하는지 확인한다. 다음 검증된 거래일에 해당 경계가 유지되거나 회복 후 유지되는지 확인한다. / 진입은 확인 이후에도 311.52–312.00에서만 가능하다. 312.00 위로 가격이 뛰면 건너뛰며 돌파만으로 추가 매수하지 않는다.","risk_condition_ko":"304.29 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T08:50:33+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T08:53:33+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":266.93,"market_data_asof":"2026-11-10T08:50:49+00:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"258.53~260.21 시험 → 종가 260.21 이상 회복 → 다음 검증된 정규장의 258.53~259.00 지지 확인 → 비용 후 2배 이상 및 공시·계좌 점검 통과 시에만 소규모 최초 진입. / 269.65 및 273.23~275.34에서 매도 압력이 반복되고 지지나 모멘텀이 추가로 약화되면 보유 위험과 부분 익절 필요성을 재심사한다. 현재 자동 익절 신호는 아니다.","risk_condition_ko":"253.56 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T08:50:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T08:53:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":221.4,"market_data_asof":"2026-11-10T04:15:00-05:00","session_vwap":221.35343618513323,"relative_volume":0.005276633608847855,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-17까지 향후 7일 동안 검증된 일별 자료로 점검하고 무효화나 중요 정보 발생 시 즉시 갱신한다. 이는 분석 검토기간이지 매수 주문 만료시각이 아니다. / 218.61~218.73 지지 유지·회복을 관찰한다. 단순 접촉은 매수가 아니며 기존 눌림 사례는 보상위험비 기준에 미달한다.","risk_condition_ko":"217.67 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T04:15:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T04:18:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":81.12,"market_data_asof":"2026-11-10T04:05:00-05:00","session_vwap":81.11297898640296,"relative_volume":0.01956134210198904,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"79.68~80.20 시험부터 종가 회복과 다음 실제 거래일 확인까지 순서를 기록한다. 구간 도달이나 과거의 확인만으로 매수하지 않는다. 새 종가가 80.20 아래면 보류하고 다시 확인한다. / 82.04 상회 종가는 관찰 신호일 뿐 매수 승인이 아니다. 83.74 상회 종가와 다음 실제 거래일 지지가 확인되면 비용·거래량·잔여 위험예산을 갱신해 후속 배분을 별도 심사한다.","risk_condition_ko":"79.68 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T04:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T04:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1370.0,"market_data_asof":"2026-11-10T04:15:00-05:00","session_vwap":1363.3837890625,"relative_volume":0.018252617347975494,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1319.22–1345 조정, 1337.91–1345의 새 종가, 다음 확인된 거래일의 1337.91 이상 종가를 순서대로 관찰한다. / 1396.55 돌파와 재시험 성공 시 추세와 비용 후 보상 대비 위험을 재평가하며 추격매수하지 않는다.","risk_condition_ko":"1,319.22 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T04:15:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T04:18:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.5026,"market_data_asof":"2026-11-10T04:35:00-05:00","session_vwap":100.50744123906728,"relative_volume":0.21358578779045373,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"100.44~100.45 시험 후 종가 100.45 이상 회복과 다음 실제 정규장 재시험·종가 유지 / 100.53 이상 종가 회복은 기술적 개선 관찰 신호이며 단독 매수 조건이 아님","risk_condition_ko":"100.41 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T04:35:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T04:38:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1418.55,"market_data_asof":"2026-11-10T04:15:00-05:00","session_vwap":1418.0264650283555,"relative_volume":0.00687944683005266,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"LLY 지지 재시험 → 1367.08 이상 종가 회복 → 다음 실제 정규세션 지지 유지 → 1365~1367 체결 가능 여부를 순서대로 확인한다. 확인 뒤 가격이 돌아오지 않으면 거래하지 않는다. / LLY 1419.67~1421.99 돌파만으로 추격하지 않는다. 1445.96~1453의 반복 거부와 탄력 약화가 확인되면 부분 이익실현을 별도 결정한다.","risk_condition_ko":"1,364.58 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T04:15:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T04:18:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":573.49,"market_data_asof":"2026-11-10T05:45:00-05:00","session_vwap":573.6467828418231,"relative_volume":0.005782443974943841,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"핵심 공시의 최소 사건 검증을 완료한다. 뉴스·사회관계망 자료 부재는 중립 심리가 아니라 관측 불가로 취급한다. / 559.61~562.45 시험 후 정규장 종가 562.45 이상 회복을 첫 신호로 기록한다.","risk_condition_ko":"556 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T05:45:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T05:48:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"KO","display_name":"KO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":96.0089,"market_data_asof":"2026-11-10T05:00:00-05:00","session_vwap":96.25976423803436,"relative_volume":0.007522752609142216,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"97.39 초과 종가 → 다음 실제 거래일 재시험 및 종가 97.39 이상 → 이후 실제 집행가 97.40~97.60의 순서를 확인한다. 순서가 끝나기 전에는 최초 진입하지 않는다. / 94.26~94.76 지지와 96.26~96.56 저항 반응을 관찰한다. 지지 접촉이나 상승 방향성만으로 매수하지 않는다.","risk_condition_ko":"94.26 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T05:00:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T05:03:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":423.33,"market_data_asof":"2026-11-10T05:10:00-05:00","session_vwap":423.91907107670653,"relative_volume":0.003797760655966287,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"416.22–418.65는 단순 접촉이 아닌 날짜가 확인되는 시험·회복을 관찰하고, 416.22–419.00은 확인 이후에만 체결 가능 범위로 사용한다. / 426.46–426.78에서 매도압력과 동등한 정규장 기준 거래참여를 점검한다. 저항이 해소되지 않으면 상단 목표 손익비만으로 진입하지 않는다.","risk_condition_ko":"412.75 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T05:10:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T05:13:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":168.2035,"market_data_asof":"2026-11-10T05:20:00-05:00","session_vwap":168.88352655702346,"relative_volume":0.0068039495117836225,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"매수 후보 범위는 하단 163.08, 상단 164.02다. 일봉 회복과 다음 검증 거래일 지지 유지 후에도 범위 내 체결 기회가 없으면 매수를 포기한다. / 165.23–166.32는 관찰 전용 지지 구간이며 이번 승인으로 매수하지 않는다.","risk_condition_ko":"163.08 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T05:20:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T05:23:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":653.0167,"market_data_asof":"2026-11-10T05:05:00-05:00","session_vwap":657.4902912621359,"relative_volume":0.0011490466261081548,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"645.89–648.54 시험과 648.54 이상 종가를 새로 확인한 뒤, 다음 확인 거래일에 비용 조정 상한 이하의 진입 기회를 관찰한다. / 638.01–638.94는 핵심 지지대다. 633.34–635.70은 하단 반응 관찰 구간일 뿐 손절 연기 근거가 아니다.","risk_condition_ko":"638.01 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T05:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T05:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SPG","display_name":"Simon Property Group","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":231.92,"market_data_asof":"2026-11-10T05:50:00-05:00","session_vwap":232.76923076923077,"relative_volume":0.00017871053637925278,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"222.28–224.61 시험, 224.61 이상 확정 종가 및 다음 확인 거래일의 224.61–225.29 진입 기회를 관찰한다. / 228.97–231.66의 지지·회복을 추적한다. 깊은 지지구간까지 하락하면 과거 상승 모멘텀이 그대로 유지된다고 가정하지 않는다.","risk_condition_ko":"222.28 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T05:50:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T05:53:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WMT","display_name":"WMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":124.65,"market_data_asof":"2026-11-10T05:00:00-05:00","session_vwap":125.17461309989058,"relative_volume":0.01667613669517274,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"새로운 123.81~124.48 시험, 124.48 이상 정규장 종가 회복, 다음 검증된 정규장 재지지를 순서대로 확인한다. 단순 지정가 접촉은 지지 확인이 아니다. / 125.99 회복과 127.69~129.17 저항 소화 여부를 점검하고, 거래량 개선은 보조 자료로 사용한다.","risk_condition_ko":"123.03 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T05:00:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T05:03:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LIN","display_name":"LIN","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":517.8512,"market_data_asof":"2026-11-10T04:35:00-05:00","session_vwap":519.2184265010352,"relative_volume":0.0088966877249458,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"LIN의 지지 시험, 514.87 위 종가 회복, 다음 실제 거래일의 지지 유지 및 같은 기준 위 종가라는 순서를 확인한다. 이후 513.20~513.79 재접근이 정상 눌림인지 새 지지 실패인지 재평가한다. / 523.42~526.56 저항 통과와 533.39 돌파·재시험을 관찰한다. 544.85~546.40은 돌파 유지 후의 참고 구간이며 현재 목표가 아니다.","risk_condition_ko":"510.01 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T04:35:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T04:38:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1064.336,"market_data_asof":"2026-11-10T05:25:00-05:00","session_vwap":1062.2476145038167,"relative_volume":0.0170475432271833,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1043.00~1046.47 시험 이후 1043.00 이상 종가와 다음 실제 거래일의 구간 내 지지를 확인한다. 재방문이 없으면 매수하지 않는다. / 1046.47 위 회복은 후속 배분 검토 신호일 뿐 자동 추가매수 신호가 아니다.","risk_condition_ko":"1,034.89 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T05:25:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T05:28:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WELL","display_name":"WELL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":247.35,"market_data_asof":"2026-11-10T04:00:00-05:00","session_vwap":227.0,"relative_volume":1.2856143726778055e-05,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"244.12–244.80은 초기 지지 관찰 구간이며 자동 매수 구간이 아니다. / 240.61–241.48 시험, 241.48 이상 확정 종가, 다음 거래일 240.61 지지 유지와 241.48–242.00 체결 가능 여부를 순서대로 확인한다.","risk_condition_ko":"240.61 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T04:00:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T04:03:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SO","display_name":"SO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":93.7777,"market_data_asof":"2026-11-10T04:00:00-05:00","session_vwap":null,"relative_volume":2.796282651190912e-06,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"92.90–92.91 시험 후 종가 92.91 이상, 이어 다음 유효 거래일의 지지·재시험 및 구간 내 체결 가능성을 확인한다. 충족해도 시범매수는 선택이며 의무가 아니다. / 92.90 지지가 실패하면 얕은 눌림목 매수를 보류한다. 91.69–91.85는 재평가 구간이며 매수가를 자동으로 낮추지 않는다.","risk_condition_ko":"91.69 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T04:00:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T04:03:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":294.27,"market_data_asof":"2026-11-10T05:15:00-05:00","session_vwap":293.8957055214724,"relative_volume":0.0005737188087311199,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"283.32–286.00: 구간 시험, 286.00 이상 일봉 종가, 다음 검증된 거래일의 구간 내 지지 재시험을 순서대로 관찰한다. / 289.12–289.75: 종가 이탈은 경고이며 회복은 개선 신호지만 자동 증액 근거가 아니다.","risk_condition_ko":"283.32 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T05:15:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T05:18:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SIEGY","display_name":"SIEGY","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":153.42999267578125,"market_data_asof":"2026-11-09T15:55:00-05:00","session_vwap":152.509929321895,"relative_volume":0.11203943394008643,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-17T23:59:59-05:00까지 매일 재검토한다. 기준시각 2026-11-10T04:59:08.540980-05:00은 만료 전이지만 실제 거래일·정규장 운영·시세 신선도·조건 충족을 입증하지 않는다. 최초 활성은 확인 절차 완료 후이며 만료와 다르다. 만료는 분석일로부터 7일 뒤의 관리상 기한으로, 거래소 폐장시각이 아니며 자동 연장하지 않는다. / 지지 재시험, 종가 회복, 다음 거래일 저점 상승을 순서대로 확인한다. 확인 후 다시 후보 구간으로 내려올 때 지지 훼손이나 새로운 악재가 나타나면 과거 확인만으로 주문을 유지하지 않는다.","risk_condition_ko":"149.18 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-09T15:55:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-09T15:58:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ANET","display_name":"Arista Networks","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":187.5,"market_data_asof":"2026-11-10T04:40:00-05:00","session_vwap":185.8737247353224,"relative_volume":0.01231316055935564,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"175.09–176.25 시험 후 176.25 이상 종가 회복과 다음 확인 거래일의 범위 내 재지지: 핵심 공시 확인 및 위험한도 충족 시에만 스타터 검토. / 188.20–188.53 회복·재지지: 관찰 신호이며 추격 진입 승인이 아니다.","risk_condition_ko":"175 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T04:40:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T04:43:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"JPM","display_name":"JPM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":344.85,"market_data_asof":"2026-11-10T05:00:00-05:00","session_vwap":343.42056074766356,"relative_volume":0.001972988060331524,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-10부터 형성되는 새 정규장 일봉이 339.41~340.66을 시험하고 340.66 이상으로 마감하는지 확인한다. 이후 실제 거래일에 구간 안에서만 첫 매수를 검토하며 상승 갭을 추격하지 않는다. / 첫 확인 후 2~3개의 실제 거래일 안에 지지 유지와 거래량을 재평가하되 조건부 만료시각을 넘기지 않는다. 추가 매수는 별도 재승인 사항이다.","risk_condition_ko":"333 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T05:00:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T05:03:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CRM","display_name":"Salesforce","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":214.82,"market_data_asof":"2026-11-10T04:35:00-05:00","session_vwap":215.58252184769037,"relative_volume":0.011018096355920465,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"218.77 위 정규장 종가와 갱신된 20일 평균 초과 일거래량은 초기 회복 경보다. 매수 승인이 아니다. / 222.20~225.28 회복 후 다음 확인된 정규장의 재시험 지지와 상단 위 종가 유지 여부를 점검한다. 첫 재심사를 반드시 50일선 회복까지 미루지는 않는다.","risk_condition_ko":"211 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-10T04:35:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-10T04:38:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
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
