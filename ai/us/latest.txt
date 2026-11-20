# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-20T15:39:01.509404+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261120T175052_local-scheduler-us-full",
  "producer_finished_at": "2026-11-20T19:57:25.766108+09:00",
  "analysis_run_id": "20261120T175052_local-scheduler-us-full",
  "analysis_completed_at": "2026-11-20T19:36:27.503854+09:00",
  "analysis_trade_date_oldest": "2026-11-19",
  "analysis_trade_date_latest": "2026-11-19",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-20T08:51:27+00:00",
  "market_data_latest_at": "2026-11-20T05:15:00-05:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-20T19:37:00.003194+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-20T19:37:00.003194+09:00",
    "run_started_at": "2026-11-20T17:50:52.788984+09:00",
    "run_finished_at": "2026-11-20T19:57:25.766108+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23484121,
    "total_market_value_krw": 20351729,
    "total_unrealized_pnl_krw": -3132392,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 111880,
    "total_equity_krw": 21439941
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 542527,
      "current_price_krw": 452432,
      "market_value_krw": 5429184,
      "unrealized_pnl_krw": -1081143
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 290786,
      "current_price_krw": 282395,
      "market_value_krw": 3106353,
      "unrealized_pnl_krw": -92303
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 421768,
      "current_price_krw": 366941,
      "market_value_krw": 2201648,
      "unrealized_pnl_krw": -328965
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1869427,
      "current_price_krw": 1693842,
      "market_value_krw": 1693842,
      "unrealized_pnl_krw": -175585
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 552811,
      "current_price_krw": 431844,
      "market_value_krw": 1295533,
      "unrealized_pnl_krw": -362900
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 133760,
      "current_price_krw": 133931,
      "market_value_krw": 1205385,
      "unrealized_pnl_krw": 1539
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 265742,
      "current_price_krw": 191036,
      "market_value_krw": 1146218,
      "unrealized_pnl_krw": -448239
    },
    {
      "ticker": "GEV",
      "name": "GE 버노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1464598,
      "current_price_krw": 985098,
      "market_value_krw": 985098,
      "unrealized_pnl_krw": -479500
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 362527,
      "current_price_krw": 466445,
      "market_value_krw": 932890,
      "unrealized_pnl_krw": 207835
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1411993,
      "current_price_krw": 1803021,
      "market_value_krw": 786234,
      "unrealized_pnl_krw": 170513
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 566421,
      "current_price_krw": 451260,
      "market_value_krw": 451260,
      "unrealized_pnl_krw": -115161
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 659018,
      "current_price_krw": 401595,
      "market_value_krw": 401595,
      "unrealized_pnl_krw": -257423
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 135446,
      "current_price_krw": 94486,
      "market_value_krw": 377947,
      "unrealized_pnl_krw": -163839
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 345795,
      "current_price_krw": 338542,
      "market_value_krw": 338542,
      "unrealized_pnl_krw": -7253
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":272.21,"market_data_asof":"2026-11-20T04:05:00-05:00","market_data_clock_status":null,"session_vwap":271.7793553311821,"relative_volume":0.06664432317129766,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"270.479~272.36달러 지지 구간에서 272.36달러를 회복해 재시험을 견디는지, 이어 276.92달러를 정규장 종가로 되찾는지 확인한다. / 286.83달러 종가 돌파가 다음 거래일에도 유지되면 295.43~296.49달러를 다음 저항으로 본다. 돌파 후 285.72달러 아래로 마감하면 매수 재평가를 취소한다.","risk_condition_ko":"276.92 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T04:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T04:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":70.759,"market_data_asof":"2026-11-20T04:00:00-05:00","market_data_clock_status":null,"session_vwap":70.1687201601725,"relative_volume":0.05363034007844851,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"72.34달러 위에서 정규장을 마감하고 다음 확인된 거래일에 72.32~72.34달러 구간을 지키면 안정화 신호로만 본다. / 76.18달러 돌파 종가, 75.96~76.18달러 재시험 방어, 이후 77.73달러 상회 종가를 순서대로 확인하면 새 매수 판단을 내린다. 자동 주문 조건은 아니다.","risk_condition_ko":"75.96 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T04:00:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T04:03:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":143.28,"market_data_asof":"2026-11-20T04:15:00-05:00","market_data_clock_status":null,"session_vwap":143.6082801764282,"relative_volume":0.08755524982223,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"후속 정규장 종가의 145.71~145.98달러 회복과 다음 정규장 지지는 관찰 신호일 뿐 매수 조건이 아니다. / 150.33~150.96달러 돌파와 지지 이후 158.13~159.70달러, 다음으로 164.38~168.57달러를 확인한다. 모두 기술적 기준이며 가치평가 목표가가 아니다.","risk_condition_ko":"142.82 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T04:15:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T04:18:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":312.54,"market_data_asof":"2026-11-20T08:51:46+00:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"305.80~311.00달러는 지지 후보이지 매수 구간이 아니다. 336.36달러 위 일봉 마감은 반등 관찰 신호이며, 340.87~348.02달러 저항대 상단 돌파와 다음 실제 거래일의 지지 확인이 추세 개선 신호다. / 2026-11-20 미국 동부시간 04:01:32 기준, 03:51:50 관측값 312.54달러는 2026-11-19 종가와 같고 호가 지연은 28,307초로 표시됐다. 체결·5분봉·세션 거래량가중평균가격이 없어 실제 거래 세션, 거래정지 여부, 최신 호가 및 당일 조건 충족은 확인되지 않았다.","risk_condition_ko":"305.8 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T08:51:46+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T08:54:46+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":742.098,"market_data_asof":"2026-11-20T04:00:00-05:00","market_data_clock_status":null,"session_vwap":737.3005718370265,"relative_volume":0.012853469256090993,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"747~750달러 지지 후보를 750달러 이상 정규장 종가로 확인하고 다음 확인된 정규장 재시험에서 747달러를 지키는지 본다. / 791.68~806.49달러 회복 구간과 806.49달러 초과 종가, 후속 재시험을 확인한다. 836.93달러까지 비용과 갭 여유를 반영한 보상 대비 위험이 최소 2배가 아니면 추격하지 않는다.","risk_condition_ko":"747 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T04:00:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T04:03:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.6324,"market_data_asof":"2026-11-20T04:30:00-05:00","market_data_clock_status":null,"session_vwap":100.63590637482231,"relative_volume":0.12488294081826706,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"새 정규장 종가의 100.60달러 지지와 바로 다음 실제 정규장의 100.60~100.61달러 재시험을 확인한다. 100.64달러는 지연 장전 고가로 관찰만 하며 추격하지 않는다. / 거래 가능 상태, 실시간 호가, 동시점 순자산가치, 최신 단기 국채 금리와 운용사 수익률·보수·분배 일정을 확인한다. 산식과 기준일이 불명확한 공급자 수치 3.64는 쓰지 않는다.","risk_condition_ko":"100.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T04:30:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T04:33:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":211.71,"market_data_asof":"2026-11-20T09:19:46+00:00","market_data_clock_status":null,"session_vwap":211.81684210526316,"relative_volume":0.006902058840560189,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"211.00~211.34달러 지지와 212.52달러 회복은 관찰 신호다. 상대강도지수 50 회복도 보조 신호일 뿐이다. 216.25달러와 218.83달러는 저항이며, 210.17달러 이탈 뒤에는 207.16~208.09달러를 다음 지지 후보로 본다. / 11월 20일 미 동부 04:20:43 장전 자료는 57초 지연, 누적 3,800주, 호가 차이 약 0.63%였다. 판단 시각인 04:30:06에는 계획이 만료되지 않았지만 정규장 일정·거래정지 여부·실행 호가와 진입 조건 충족은 확인되지 않았다.","risk_condition_ko":"210.17 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T09:19:46+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T09:22:46+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":349.21,"market_data_asof":"2026-11-20T08:51:27+00:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"346.47~347.43달러 시험과 347.43달러 회복, 350.61달러 위 정규장 마감, 다음 정규장 재시험 지지를 순서대로 확인한다. / 355.28~356.42달러 돌파만으로 추격하지 않는다. 359.37~360.83달러 직전 고점대 상단 위 마감과 다음 정규장 지지를 확인한다.","risk_condition_ko":"346.47 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T08:51:27+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T08:54:27+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":257.37,"market_data_asof":"2026-11-20T08:51:27+00:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"254.00–256.75달러 지지 유지, 262.92달러 초과 종가, 다음 정규 거래일의 262.45–262.92달러 재시험과 상단 회복을 순서대로 확인한다. / 275.67달러 초과 종가와 이후 지지 확인은 별도 재평가 신호이지 매수 신호가 아니다. 돌파 뒤 274.00달러 아래로 마감하면 해당 관찰을 중단한다.","risk_condition_ko":"254 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T08:51:27+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T08:54:27+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1281.24,"market_data_asof":"2026-11-20T04:05:00-05:00","market_data_clock_status":null,"session_vwap":1273.5511811023623,"relative_volume":0.0068421366452930425,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1280~1297달러 지지 방어, 거래량 개선을 동반한 1328.47달러 초과 종가, 바로 다음 확인된 정규장의 1324~1328.47달러 재시험 성공을 순서대로 확인한다. / 첫 저항 1355달러까지 비용·갭 반영 후 보상 대비 위험을 다시 계산한다. 2배가 안 되면 1378.06달러를 대신 목표로 삼아 추격하지 않는다.","risk_condition_ko":"1,280 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T04:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T04:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":337.94,"market_data_asof":"2026-11-20T04:30:00-05:00","market_data_clock_status":null,"session_vwap":340.99943183135827,"relative_volume":0.11043163072703463,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"$353.50 위 정규장 종가 이후 바로 다음 확인된 정규장에서 $351.14~$353.50 방어와 $353.50 재회복을 점검한다. / 11월 20일 지연 장전 저점 $337.48을 실제 정규장에서 하회하면 신규 매수 검토를 중단하고 기존 손절과 집중도를 재점검한다. 일봉 지지나 자동 손절가는 아니다.","risk_condition_ko":"351.14 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T04:30:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T04:33:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":325.5,"market_data_asof":"2026-11-20T04:00:00-05:00","market_data_clock_status":null,"session_vwap":324.64813039309684,"relative_volume":0.0064926686741347385,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"329.96~332.42달러 회복과 재시험 지지는 관찰 신호다. 350.09달러 위 정규장 종가, 거래량 증가, 다음 정규장 재시험 지지와 손익비 개선이 확인돼야 첫 편입을 다시 판단한다. / 368.63달러는 다음 저항이며 자동 익절선이 아니다. 394.00~395.08달러는 11월 19일 기준 중기 회복 구간으로 재평가 때 갱신한다.","risk_condition_ko":"323.28 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T04:00:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T04:03:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":346.65,"market_data_asof":"2026-11-20T08:51:27+00:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-19의 345.00달러 저가와 346.65달러 종가에 이어 바로 다음 확인된 거래일에 더 높은 저점과 345.00달러 위 종가가 나오는지 본다. 후속 확인이 실패하면 그 후보는 폐기하며, 지지 이탈이 없을 때만 만료 전 새 지지 시험을 관찰한다. / 366.94~370.03달러 저항을 종가로 돌파하고 다음 거래일에도 지지하는지 관찰한다. 다음 저항인 376.97~380.84달러가 가까워 돌파만으로 매수하거나 증액하지 않는다.","risk_condition_ko":"343.79 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T08:51:27+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T08:54:27+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1346.6057,"market_data_asof":"2026-11-20T04:15:00-05:00","market_data_clock_status":null,"session_vwap":1347.665243381725,"relative_volume":0.015057799414488208,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1328.39~1341.46달러 시험 후 1341.46달러 위 정규장 종가, 바로 다음 검증된 정규장의 지지 유지와 1341.46~1349.03달러 실행 범위 확인. / 1380~1382달러에서는 추격하지 않고 최근 대비 거래량이 개선된 상향 마감과 재시험을 관찰한다. 이후 1395.20~1404.94달러 저항대가 지지로 바뀌는지 확인한다.","risk_condition_ko":"1,328.39 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T04:15:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T04:18:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WMT","display_name":"WMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":128.579,"market_data_asof":"2026-11-20T05:05:00-05:00","market_data_clock_status":null,"session_vwap":127.85473238748881,"relative_volume":0.032776953520389555,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"11월 19일 확인 마감 직후 첫 실제 정규장에서 123.03달러 지지 유지와 123.27~124.00달러 체결 가능성을 확인한다. 놓치면 만료 전 새 일봉 지지 시험과 그다음 실제 거래일 확인이 필요하다. / 126.76달러 종가 회복과 128.70달러를 넘는 정규장 종가 및 다음 거래일 유지는 반등 점검 신호다. 129.85달러와 131.49~131.82달러 저항을 앞두고 추격하지 않는다.","risk_condition_ko":"123.03 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T05:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T05:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":284.87,"market_data_asof":"2026-11-20T04:55:00-05:00","market_data_clock_status":null,"session_vwap":284.7544964028777,"relative_volume":0.004339782108399425,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"278.01~279.88달러 시험 뒤 279.88달러 이상 종가와 차기 정규장 지지 유지. 279.88~280.25달러를 놓치거나 286.05~286.32달러 저항에 접근하면 추격하지 않는다. / 290.13~291.25달러 회복과 차기 정규장 재시험. 294.50~295.46달러와 298.74~302.93달러는 돌파 후 관찰할 저항대다.","risk_condition_ko":"277.64 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T04:55:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T04:58:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1107.0,"market_data_asof":"2026-11-20T04:45:00-05:00","market_data_clock_status":null,"session_vwap":1103.6875224739301,"relative_volume":0.022516430982949084,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1083.15~1085.70달러 시험 후 1085.70달러 이상 정규장 종가와 다음 정규장 지지 유지를 확인한다. / 1108.50달러는 개장 전 관측에 근거한 잠정 첫 저항으로 정규장에서 재검증한다. 이후 1117.00달러와 1123.67달러를 관찰한다. 1123.67달러 상회 종가와 다음 정규장 지지는 재평가 신호일 뿐 자동 매수가 아니다.","risk_condition_ko":"1,075.05 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T04:45:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T04:48:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SO","display_name":"SO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":94.05,"market_data_asof":"2026-11-20T05:00:00-05:00","market_data_clock_status":null,"session_vwap":93.18887601390499,"relative_volume":0.0020219878422549392,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"92.42~92.79달러 시험 후 하단을 방어하고 거래 증가와 함께 92.79달러 위에서 마감한 뒤 다음 정규장에도 상단이 지지로 유지되는지 확인한다. / 94.94달러 초과 일봉 마감 후 다음 정규장에서 해당 가격이 지지로 바뀌는지 본다. 이는 추세 재평가 신호이며, 이후 저항 96.39달러와 97.65달러는 자동 매수·익절 기준이 아니다.","risk_condition_ko":"92.42 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T05:00:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T05:03:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":575.0,"market_data_asof":"2026-11-20T04:55:00-05:00","market_data_clock_status":null,"session_vwap":575.0025414860219,"relative_volume":0.025701774878734037,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"583.72~588.54달러에서는 추격하지 않는다. 588.54달러 위 정규장 종가와 첫 저항 구간의 지지 전환이 확인되면 595.83~596.92달러까지의 비용 차감 후 보상을 다시 계산한다. / 11월 19일 수시공시는 제출 사실만 확인됐다. 공시 본문과 다음 실적 일정을 확인할 때까지 방향과 날짜를 가정하지 않는다. 공급자 분기표의 판단 시점 이전 이용 가능성과 공시 원문의 재무제표 표시통화·단위·B주 주당 기준, 미국예탁증서 적용 여부 및 해당 시 보통주 전환비율은 미확인이다. 절대금액·주당이익·평가배수는 판단에서 제외했다.","risk_condition_ko":"565.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T04:55:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T04:58:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LIN","display_name":"LIN","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":511.58,"market_data_asof":"2026-11-20T04:55:00-05:00","market_data_clock_status":null,"session_vwap":512.5096774193548,"relative_volume":0.017520170567337973,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"508.00~510.21달러를 시험한 뒤 저점이 더 낮아지지 않고 510.21달러를 종가로 회복하는지 확인한다. 이는 지지 신호이지 단독 매수 신호가 아니다. / 519.54달러 종가 돌파 뒤 다음 정규장의 519.54~520.00달러 재시험과 체결 여건을 확인한다. 526.75달러 및 530.35~533.39달러에서는 추세를 재평가하되 추격하지 않는다.","risk_condition_ko":"508 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T04:55:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T04:58:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":405.38,"market_data_asof":"2026-11-20T05:15:00-05:00","market_data_clock_status":null,"session_vwap":403.49792354381856,"relative_volume":0.026267065455804525,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"V의 400.74달러 지지와 411.83~413.51달러 회복 여부를 먼저 본다. 이후 416.81달러, 422.05달러, 430.99달러 순으로 저항과 지지 전환을 점검한다. / 미국 합의와 영국 잠재 소송을 추적한다. 달러 강세 및 장기금리 하락은 시장 보도에 근거하며 V의 국경 간 결제와 손익에 미치는 순효과는 미확인이다.","risk_condition_ko":"400.74 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T05:15:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T05:18:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":169.4092,"market_data_asof":"2026-11-20T04:45:00-05:00","market_data_clock_status":null,"session_vwap":169.04080459770114,"relative_volume":0.0036275572767318757,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-20 미국 동부시간 04:55:42 기준 원안의 검토 기한은 지나지 않았다. 다만 04:45의 169.41달러는 1,740주에 그친 지연 장전 관측이다. 실제 정규장 운영과 최신 호가를 확인하며, 169.79~170.73달러에서는 추격하지 않는다. / 원공시 공개 시각과 재무제표 표시 통화·단위, 주당 수치의 주식 기준, 예탁증서 해당 여부와 해당 시 보통주 환산비율을 확인한다. 확인 전에는 공급자의 재무 금액·주당순이익·평가배수 비교를 제외한다. 유로화 채권은 자금 용도·조달비용·순부채 효과를 확인하기 전에는 차환 개선으로 보지 않는다.","risk_condition_ko":"166.89 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T04:45:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T04:48:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AES","display_name":"AES","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":15.02,"market_data_asof":"2026-11-20T04:00:00-05:00","market_data_clock_status":null,"session_vwap":15.013513513513514,"relative_volume":0.0006275265572167946,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 체결 가능 호가와 거래 가능 여부를 확인하고, 공식 인수 조건에 근거해 순수익·최고 매수가·무산 하방을 다시 산정한다. / $15.04 초과 정규장 종가 또는 $14.97~$14.99 지지 뒤 $15.02 이상 정규장 종가를 확인하고 다음 실제 거래일의 지지를 점검한다.","risk_condition_ko":"14.97 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T04:00:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T04:03:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":101.84,"market_data_asof":"2026-11-20T04:35:00-05:00","market_data_clock_status":null,"session_vwap":101.12525667351129,"relative_volume":0.0013413002603438165,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"실적 전에는 99.59~100.00달러 지지, 101.29달러 회복, 101.95달러 초과 정규장 종가와 다음 실제 정규장 재시험을 기록만 합니다. 재시험이 성공해도 주문하지 않습니다. / 102.86~104.49달러 첫 저항에서는 추격하지 않습니다. 이 구간을 소화할 때만 105.72~106.20달러를 다음 저항으로 봅니다.","risk_condition_ko":"99.59 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T04:35:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T04:38:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WELL","display_name":"WELL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":251.225,"market_data_asof":"2026-11-20T04:35:00-05:00","market_data_clock_status":null,"session_vwap":244.75757575757575,"relative_volume":0.00020100757230401885,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"241.52~243.03달러 지지와 244.46달러 종가 회복을 관찰한다. 다음 실제 거래 세션에서 지지를 확인하더라도 기존 244.46~244.75달러 구간은 주문 구간이 아니다. / 249.75달러 위 첫 돌파는 추격하지 않는다. 다음 저항 253.37달러까지 3.62달러로 11월 19일 평균 실제 변동폭 5.25달러보다 짧다. 하락 시 234.58달러와 221.08달러는 추세 재평가 기준이지 추가 매수 가격이 아니다.","risk_condition_ko":"240.18 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T04:35:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T04:38:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"KO","display_name":"KO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":97.3317,"market_data_asof":"2026-11-20T09:59:49+00:00","market_data_clock_status":null,"session_vwap":97.02502891997055,"relative_volume":0.020106569044893458,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"94.18~94.73달러 지지 시험 후 94.73달러 이상 정규장 마감과 다음 실제 정규장의 94.73달러 재지지를 확인한다. 허용 체결 구간은 94.73~95.10달러지만 첫 저항 기준 손익비를 통과한 호가에서만 스타터를 검토한다. / 96.72~97.25달러 회복과 정규장 거래가 뒷받침된 97.39달러 초과 마감, 다음 정규장 재지지를 관찰한다. 97.39달러에서 98.38달러까지 비용 전 0.99달러뿐이므로 돌파 자체로 비중을 늘리지 않는다. 98.38달러를 소화하면 100.56달러를 다음 저항으로 재평가한다.","risk_condition_ko":"94.18 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T09:59:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T10:02:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NU","display_name":"NU","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":11.67,"market_data_asof":"2026-11-20T04:30:00-05:00","market_data_clock_status":null,"session_vwap":11.700098293898757,"relative_volume":0.012617177535126473,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"11.65~11.80달러 지지 방어, 12.40달러 이상 정규장 종가, 다음 확인된 정규장의 12.40달러 재시험과 종가 유지 여부를 순서대로 본다. 모두 충족해도 순손익비가 개선되지 않으면 대기를 유지한다. / 13.19~13.25달러 첫 저항을 소화하는지 확인하고, 11월 19일 기준 13.52달러인 50일선은 재평가 시 갱신한다.","risk_condition_ko":"11.65 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T04:30:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T04:33:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":631.0983,"market_data_asof":"2026-11-20T05:15:00-05:00","market_data_clock_status":null,"session_vwap":629.3076923076923,"relative_volume":0.01097928823787645,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"641.06달러 상향 종가와 바로 다음 정규장의 지지 여부를 본다. 반등 시 654.08달러와 661~668달러에서 보유 근거와 손익비를 재평가한다. / 624.10~625.08달러의 이탈과 회복 여부를 우선 확인한다. 약 620달러와 605~606달러는 다음 관찰 구간이지 자동 매수선이 아니다.","risk_condition_ko":"624.1 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T05:15:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T05:18:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ORCL","display_name":"Oracle","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":108.3,"market_data_asof":"2026-11-20T04:30:00-05:00","market_data_clock_status":null,"session_vwap":107.87034663737337,"relative_volume":0.048294772416196306,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"109.21~110.24달러 지지 구간을 회복하고 다음으로 확인된 정규장 재시험에서 지키는지 관찰 / 거래량 증가를 동반한 118.50~118.68달러 구간 돌파, 121.35달러 위 정규장 종가, 다음 정규장 지지 여부를 순서대로 확인","risk_condition_ko":"109.21 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T04:30:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T04:33:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SPCX","display_name":"SPCX","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":133.6412,"market_data_asof":"2026-11-20T04:40:00-05:00","market_data_clock_status":null,"session_vwap":134.5932910256577,"relative_volume":0.1495178081069654,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"$135.50 이상 정규장 종가와 다음 실제 정규장에서의 $135.00–$135.50 지지 여부를 본다. $137.67–$139.97 회복은 단기 반등의 보강 증거이지 매수 신호는 아니다. / $148.18 초과 정규장 종가와 다음 실제 정규장의 지지 유지, 원공시 검증 및 자금 부담 점검이 함께 충족되면 소규모 첫 진입을 별도로 판단한다.","risk_condition_ko":"133.14 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-20T04:40:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-20T04:43:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-20T23:12:41.460039+09:00",
  "as_of": "2026-11-20T08:51:27+00:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
