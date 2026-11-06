# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-06T13:39:07.080632+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261106T175128_local-scheduler-us-full",
  "producer_finished_at": "2026-11-06T21:31:16.152610+09:00",
  "analysis_run_id": "20261106T175128_local-scheduler-us-full",
  "analysis_completed_at": "2026-11-06T20:56:54.446013+09:00",
  "analysis_trade_date_oldest": "2026-11-05",
  "analysis_trade_date_latest": "2026-11-05",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-06T08:52:00+00:00",
  "market_data_latest_at": "2026-11-06T06:35:00-05:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-06T20:57:22.397988+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-06T20:57:22.397988+09:00",
    "run_started_at": "2026-11-06T17:51:28.802206+09:00",
    "run_finished_at": "2026-11-06T21:31:16.152610+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23681783,
    "total_market_value_krw": 21713337,
    "total_unrealized_pnl_krw": -1968446,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 112218,
    "total_equity_krw": 22802207
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 547093,
      "current_price_krw": 507987,
      "market_value_krw": 6095847,
      "unrealized_pnl_krw": -469270
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 293234,
      "current_price_krw": 289469,
      "market_value_krw": 3184163,
      "unrealized_pnl_krw": -41413
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 425318,
      "current_price_krw": 382241,
      "market_value_krw": 2293451,
      "unrealized_pnl_krw": -258459
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1885161,
      "current_price_krw": 1599664,
      "market_value_krw": 1599664,
      "unrealized_pnl_krw": -285497
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 267979,
      "current_price_krw": 254456,
      "market_value_krw": 1526739,
      "unrealized_pnl_krw": -81137
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 557463,
      "current_price_krw": 458158,
      "market_value_krw": 1374476,
      "unrealized_pnl_krw": -297914
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 134886,
      "current_price_krw": 134844,
      "market_value_krw": 1213597,
      "unrealized_pnl_krw": -381
    },
    {
      "ticker": "GEV",
      "name": "GE버노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1476924,
      "current_price_krw": 1070916,
      "market_value_krw": 1070916,
      "unrealized_pnl_krw": -406008
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 365579,
      "current_price_krw": 456642,
      "market_value_krw": 913284,
      "unrealized_pnl_krw": 182126
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1423877,
      "current_price_krw": 1803325,
      "market_value_krw": 786367,
      "unrealized_pnl_krw": 165464
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 664565,
      "current_price_krw": 460883,
      "market_value_krw": 460883,
      "unrealized_pnl_krw": -203682
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 136586,
      "current_price_krw": 107883,
      "market_value_krw": 431533,
      "unrealized_pnl_krw": -114813
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 571188,
      "current_price_krw": 410397,
      "market_value_krw": 410397,
      "unrealized_pnl_krw": -160791
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 348705,
      "current_price_krw": 352020,
      "market_value_krw": 352020,
      "unrealized_pnl_krw": 3315
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":375.1697,"market_data_asof":"2026-11-06T05:10:00-05:00","session_vwap":372.813424629237,"relative_volume":0.23526345945123828,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"351.19~353.10 방어 구간의 일봉 종가 유지 또는 이탈을 확인한다. / 380.78 위 종가 회복 후 다음 확인된 거래일에도 지지가 유지되는지 점검한다. 단독 매수 신호는 아니다.","risk_condition_ko":"351.19 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T05:10:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T05:13:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":798.75,"market_data_asof":"2026-11-06T04:20:00-05:00","session_vwap":785.7277289836888,"relative_volume":0.05272614469630265,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"821.54 초과 종가와 다음 확인된 정규장의 지지 유지를 관찰한다. 이는 재검토 신호이지 자동 매수 신호가 아니다. / 832.83과 갱신된 857.50~857.64 저항을 확인하고 실제 진입가 기준 손익비를 다시 계산한다. 향후 별도 설정의 손절 구조는 새 근거로 정하되 기존 손절을 넓히지 않는다.","risk_condition_ko":"795.95 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T04:20:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T04:23:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":333.0,"market_data_asof":"2026-11-06T04:20:00-05:00","session_vwap":333.66422097539925,"relative_volume":0.01482099490837737,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"324.27 주변 일봉 종가와 저점 상승 여부를 확인한다. 장전 반등만으로 지지를 인정하지 않는다. / 종가 350.05 초과 회복 후 다음 확인된 정규장에서 346.46–350.05의 종가 지지를 점검한다.","risk_condition_ko":"324.27 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T04:20:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T04:23:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1245.14,"market_data_asof":"2026-11-06T04:45:00-05:00","session_vwap":1172.6591422121896,"relative_volume":0.008489053794761732,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"MPWR 1125~1135 지지 유지와 1125 미만 일봉 종가 여부를 확인한다. 현재 지지 붕괴로 분류하지 않는다. / MPWR 1168 회복은 초기 개선 관찰 신호일 뿐 매수 승인이 아니다.","risk_condition_ko":"1,125 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T04:45:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T04:48:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":189.25,"market_data_asof":"2026-11-06T04:45:00-05:00","session_vwap":187.15880038855693,"relative_volume":0.18306114584246178,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-05 저가 181.46과 종가 181.60의 관측 구간을 추적한다. 아직 검증된 바닥으로 간주하지 않는다. / 189.91은 지연된 장전 고가에 근거한 초기 회복 참고값일 뿐 정규장 돌파나 매수 신호가 아니다.","risk_condition_ko":"181.46 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T04:45:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T04:48:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":286.15,"market_data_asof":"2026-11-06T04:20:00-05:00","session_vwap":283.92909496615107,"relative_volume":0.0696017335946304,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"288.33–288.93 회복은 초기 개선으로만 관찰하며 매수 신호로 취급하지 않는다. / 295.60–296.82 저항 회복과 299.75–300.00 지지 전환을 순서대로 확인한다. 316.60–320.21은 이후의 조건부 저항이지 기대수익이나 가치평가 목표가가 아니다.","risk_condition_ko":"276.92 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T04:20:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T04:23:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":316.91,"market_data_asof":"2026-11-06T08:52:00+00:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"315.00 아래 마감 후 다음 거래일 회복 실패를 감시한다. 위험축소에 매수용 거래량 조건을 붙이지 않는다. / 335.59의 최신 기준값 회복, 315.00보다 높은 저점과 다음 거래일 지지는 재조사 신호다.","risk_condition_ko":"335.59 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T08:52:00+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T08:55:00+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":291.53,"market_data_asof":"2026-11-06T08:52:00+00:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-13까지 확인 가능한 정규장 종가를 검토한 뒤 계획을 갱신한다. 이는 약 1주의 검토기한이며 주문 만료나 특정 거래일 일정의 확인이 아니다. / 288.98–290.12에서 저점이 높아지는지 관찰하되 확정된 바닥으로 간주하지 않는다.","risk_condition_ko":"319.3 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T08:52:00+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T08:55:00+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":217.16,"market_data_asof":"2026-11-06T04:45:00-05:00","session_vwap":216.7801724137931,"relative_volume":0.00366808091019962,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"214.63–216.24 안정화 후 216.24 위 종가와 다음 거래일 지지를 관찰한다. 확인되지 않은 하락 매수는 하지 않는다. / 218.55 위 종가 이후 지지 유지와 220.04–220.95 저항을 반영한 비용 차감 후 보상·위험비를 다시 계산한다. 감축 권고 해제 전에는 매수하지 않는다.","risk_condition_ko":"218.55 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T04:45:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T04:48:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1350.0417,"market_data_asof":"2026-11-06T04:45:00-05:00","session_vwap":1349.4312684365782,"relative_volume":0.012037944880629575,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1364.73 초과 종가 이후 다음 거래일 1352.62–1357.80 지지를 확인하면 관찰을 재개한다. 1382.02와 1408–1418 저항까지의 비용 반영 보상비를 다시 계산한다. / 1408–1418 위 안착은 회복 근거를 강화하고 해당 구간에서 재차 밀리면 신규 진입 대기를 유지한다.","risk_condition_ko":"1,330 이하 하락, 종가 확인 후 (위험 축소에 매수세 거래량 확인은 불필요) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T04:45:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T04:48:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":344.17,"market_data_asof":"2026-11-06T08:52:00+00:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"342.06–343.70은 첫 지지 관찰 구간일 뿐 이 구간 유지로 매수하지 않는다. / 334.35–335.82 시험, 335.82 이상 종가 회복, 다음 정규장 지지 유지와 구간 내 실행 가능성을 확인한다. 확인 뒤 가격이 구간 위라면 추격하지 않는다.","risk_condition_ko":"334.35 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T08:52:00+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T08:55:00+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.4898,"market_data_asof":"2026-11-06T05:05:00-05:00","session_vwap":100.48577317726357,"relative_volume":0.5722262052822769,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"필수 자료와 경제성 검증 후 새 100.42~100.45 시험 및 종가 100.45 이상 회복: 다음 실제 거래일 첫 분할 검토. / 종가 100.50 초과와 다음 실제 거래일 100.49~100.50 재시험 유지: 가격대 의미와 순수익 이점을 재검증한 경우에만 대체 첫 분할 검토.","risk_condition_ko":"100.42 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T05:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T05:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":80.69,"market_data_asof":"2026-11-06T04:20:00-05:00","session_vwap":80.18039709586606,"relative_volume":0.06901846127512987,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"향후 1주일간 일별로 검토하며 조건부 첫 매수 허가는 2026-11-13T16:00:00-05:00에 종료한다. 이 시각은 제공된 현재 시각보다 미래이며 거래소 폐장시각을 검증한 것은 아니다. 자동 연장하지 않는다. / 첫 발동에는 이번 판단 시각 이후의 적격 정규장 종가와 후속 확인 거래일의 지지 재시험이 모두 필요하다. 현재 어느 조건도 충족된 것으로 확인되지 않았으며 실제 거래 일정도 확인해야 한다.","risk_condition_ko":"79.57 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T04:20:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T04:23:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":260.21,"market_data_asof":"2026-11-06T08:52:00+00:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"향후 실제 확인된 2~3거래일의 종가와 지지를 점검하고 늦어도 2026-11-13에 재평가한다. 조건 충족 전에는 활성화하지 않으며 만료·취소 후 자동 연장하거나 부활시키지 않는다. / 초기 진입 전 기본 공시·실제 거래비용·계좌 여력을 확인한다. 추가 증액에는 부문별 수익성과 투자 회수 검증을 더 요구한다.","risk_condition_ko":"252.27 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T08:52:00+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T08:55:00+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":565.72,"market_data_asof":"2026-11-06T05:25:00-05:00","session_vwap":565.6749297214413,"relative_volume":0.03164073046220523,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"571.10–572.33의 종가 회복과 다음 확인 거래일 지지를 관찰한다. 회복만으로 매수하지 않는다. / 559.58–562.50과 551.64–557.07에서 하락이 멈추고 종가 회복이 나타나는지 확인한다. 지지 후보 구간에 도달했다는 이유로 물타기하지 않는다.","risk_condition_ko":"579.09 이상 도달, 종가 확인 후 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T05:25:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T05:28:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":284.8,"market_data_asof":"2026-11-06T06:10:00-05:00","session_vwap":284.7216453674121,"relative_volume":0.008892945644231492,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-05 일봉을 출발점으로 향후 약 1주일간 283.32–284.70 방어와 288.62 초과 정규장 종가를 점검한다. / 적격 종가 이후 다음 실제 정규장에서 288.44–288.62 유지·회복과 288.62–289.00 체결 가능성을 확인한다. 가격이 먼저 올라 진입 상한을 넘으면 추격하지 않는다.","risk_condition_ko":"283.32 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T06:10:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T06:13:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MSFT","display_name":"Microsoft","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":528.6,"market_data_asof":"2026-11-06T06:20:00-05:00","session_vwap":531.0479253355213,"relative_volume":0.05420596238901048,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-06–2026-11-13 검토 기간에 새로운 회복 종가, 후속 거래일 재시험, 그다음 거래일의 적격 지정가 체결 가능성을 순서대로 확인한다. 2026-11-05 종가만으로 최신 약세 이후의 회복을 인정하지 않는다. / 첫 저항 541.29–543.45 통과 가능성과 비용·갭 반영 보상위험비를 재심사한다. 적격 가격이 없으면 추격하지 않는다.","risk_condition_ko":"520.99 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T06:20:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T06:23:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"KO","display_name":"KO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":94.22,"market_data_asof":"2026-11-06T05:35:00-05:00","session_vwap":94.36297607698943,"relative_volume":0.04840337007447912,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"새 일봉 종가 94.36 상회 후 후속 확인된 정규장에서 93.91 지지와 반등을 관찰한다. 93.91–94.10 체결범위와 비용 후 2배 조건을 함께 적용한다. / 95.73–96.56 매물대의 실제 저항 강도를 재평가한다. 이 구간이 청산 상한이면 기존 시험 매수안은 부적격이다.","risk_condition_ko":"92.55 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T05:35:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T05:38:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":644.92,"market_data_asof":"2026-11-06T06:10:00-05:00","session_vwap":648.3672222222223,"relative_volume":0.010168396661100757,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-13까지 확인 가능한 거래일마다 지지 시험→641.68 종가 회복→다음 거래일 재시험의 순서를 점검한다. 구간을 떠난 가격은 추격하지 않는다. / 653.85~655.92 회복, 672.68~673.50 및 680.01~681.99 공급을 관찰한다. 첫 저항에서는 잔여 보상 대비 위험을 재평가하되 자동 익절이나 추가 매수로 해석하지 않는다.","risk_condition_ko":"634.76 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T06:10:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T06:13:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WMT","display_name":"WMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":125.62,"market_data_asof":"2026-11-06T05:10:00-05:00","session_vwap":126.27431801259054,"relative_volume":0.02701689008944855,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"123–125 시험 이후 124.55 이상 종가와 바로 다음 확인된 거래일의 124.10–124.55 재시험을 추적한다. / 재시험을 놓치면 추격하지 않고 새 확인 순서를 요구한다. 매수 후 2–3개 확인된 거래일 동안 지지와 반등 지속성을 점검한다.","risk_condition_ko":"122.4 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T05:10:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T05:13:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":415.763,"market_data_asof":"2026-11-06T05:50:00-05:00","session_vwap":417.48671375714764,"relative_volume":0.008223990349411498,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-06 이후 검증된 정규장 일봉의 414.03~416.80 시험과 416.80 이상 마감, 이어지는 실제 세션 재시험 지지를 확인한다. / 421.93~422.59 지지 전환과 425.51~426.78 재매도 압력을 점검한다. 회복만으로 추가매수를 승인하지 않는다.","risk_condition_ko":"414.03 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T05:50:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T05:53:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WELL","display_name":"WELL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":245.38,"market_data_asof":"2026-11-06T05:05:00-05:00","session_vwap":244.82882882882882,"relative_volume":0.0007247810906968176,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"244.12 미만 종가는 초기 경고다. 재평가하되 자동 매도 신호로 취급하지 않는다. / 239–241 지지 시험과 241 이상 회복 종가를 관찰한다. 다음 거래일 실제 신규 매수 범위는 239–240으로 더 좁게 제한한다.","risk_condition_ko":"233.68 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T05:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T05:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1048.39,"market_data_asof":"2026-11-06T06:00:00-05:00","session_vwap":1052.2031785602992,"relative_volume":0.02705683112372984,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-05 종가는 방향 판단의 기준일 뿐 새로운 진입 확인 조건의 충족이 아니다. 새 종가와 그 다음 검증된 거래일의 지지를 확인한다. / 1040.55~1046.47 및 1017.44~1022.25 도달은 관찰 신호이며 저가 매수 허가가 아니다. 평균선 수치는 갱신하되 기존 손절을 완화하지 않는다.","risk_condition_ko":"1,061 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T06:00:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T06:03:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SPG","display_name":"Simon Property Group","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":224.5,"market_data_asof":"2026-11-06T06:25:00-05:00","session_vwap":225.13333333333333,"relative_volume":0.0002176630709759603,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"SPG의 224.61~225.29 지지와 228.50 회복 여부를 최신 완료 일봉으로 점검한다. 지연 소량 체결로 지지 붕괴를 확정하지 않는다. / SPG의 관찰 구간 시험, 종가 222.08 이상 회복, 다음 실제 거래일 219.05~220.00 재시험 및 종가 지지의 순서를 확인한다. 이후 주문 직전 새로운 약화가 나타나면 체결을 보류한다.","risk_condition_ko":"219.05 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T06:25:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T06:28:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":164.28,"market_data_asof":"2026-11-06T05:50:00-05:00","session_vwap":164.72519247219847,"relative_volume":0.00876277899565607,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"주문 전 실제 거래일·정규장 운영·거래정지 여부·최신 정규장 호가와 체결비용을 확인한다. 제공된 실행시각만으로 정상 거래나 진입 조건 충족을 확정하지 않는다. / 새 종가 165.75 이상 확인 후 다음 실제 정규장에서 164.50~164.80 재시험과 반등을 관찰한다. 단순한 가격대 접촉은 지지 확인이 아니다.","risk_condition_ko":"161.99 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T05:50:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T05:53:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SO","display_name":"SO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":93.0952,"market_data_asof":"2026-11-06T05:50:00-05:00","session_vwap":93.0625,"relative_volume":4.7196110553906836e-05,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"새 일봉의 92.65 지지 시험과 92.84 이상 종가를 확인한다. 2026-11-05 저가는 91.93이므로 기존 일봉을 이 조건의 충족으로 간주하지 않는다. / 확인 후 다음 검증된 정규장에서만 92.65–92.70 진입을 검토한다. 가격이 오르면 추격하지 않는다. 종가 92.65 미만이면 지지 신호를 초기화하고 새 확인을 요구한다.","risk_condition_ko":"91.28 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T05:50:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T05:53:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LIN","display_name":"LIN","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":513.8742,"market_data_asof":"2026-11-06T05:25:00-05:00","session_vwap":517.1152542372881,"relative_volume":0.008358919567966482,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"향후 며칠간 완성된 일봉에서 지지 하단 511.26, 상단 513.30과 회복 기준 517.17을 순서대로 확인한다. 다음 확인된 거래일의 재시험에서 지지 유지가 입증되지 않으면 매수하지 않는다. / 첫 저항 524.74–526.56과 공급구간 531.36–533.39를 우선 관찰한다. 545.42–546.40은 중간 저항을 넘어야 의미가 있는 상단 참고값이다.","risk_condition_ko":"511.26 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T05:25:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T05:28:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":197.49,"market_data_asof":"2026-11-06T06:35:00-05:00","session_vwap":198.13006654567454,"relative_volume":0.013793489950880105,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"PM의 195.37–195.57 재시험, 195.57 이상 정규장 종가, 다음 확인된 정규장의 지지 유지와 195.57–196.00 체결 가능성을 순서대로 확인한다. / 203.31–205.32 회복과 211.06–211.28 저항을 관찰한다. 203.31에서는 보유 위험과 잔여 상승 여력을 재심사하며 자동 추가 매수하지 않는다.","risk_condition_ko":"195.37 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T06:35:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T06:38:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"UNH","display_name":"UNH","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":388.41,"market_data_asof":"2026-11-06T06:05:00-05:00","session_vwap":388.64849203213487,"relative_volume":0.024510570583034907,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"395.72 초과 정규장 종가와 다음 정규장의 392.50–394.11 지지 유지 후 방향성과 진입 손익비를 재평가한다. 자동 재매수하지 않는다. / 404.89와 409.94 회복을 점검하고 이후 저항 구간 415.72–416.02 및 424.98–426.55까지의 거리를 새 손절 기준과 비교한다. 확인 과정의 가격 상승으로 손익비가 악화될 수 있다.","risk_condition_ko":"390.14 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T06:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T06:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CLF","display_name":"CLF","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":11.46,"market_data_asof":"2026-11-06T05:20:00-05:00","session_vwap":11.497846683893195,"relative_volume":0.002578202287905505,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"실행 전 최신 완료 일봉, 체결 가능 시세, 장 운영과 거래 가능 여부를 확인한다. 2026-11-06 미국 동부시간 05:20의 지연 장전 시세나 제공된 판단 시각만으로 회복 조건 충족 또는 정규장 운영을 판단하지 않는다. / 11.61 상회 종가 이후 다음 확인된 거래일에 11.35–11.61이 지지되는지 관찰하고 투자 판단을 다시 내린다.","risk_condition_ko":"11.35 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-06T05:20:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-06T05:23:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-06T03:15:40.828428+09:00",
  "as_of": "2026-11-05T11:11:00-05:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
