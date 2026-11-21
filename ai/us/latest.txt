# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-21T20:46:49.869038+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261121T030312_local-scheduler-us-overlay_only",
  "producer_finished_at": "2026-11-21T03:37:35.708519+09:00",
  "analysis_run_id": "20261120T175052_local-scheduler-us-full",
  "analysis_completed_at": "2026-11-20T19:36:27.503854+09:00",
  "analysis_trade_date_oldest": "2026-11-19",
  "analysis_trade_date_latest": "2026-11-19",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-20T18:34:49+00:00",
  "market_data_latest_at": "2026-11-20T18:34:49+00:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-21T03:37:23.283516+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-21T03:37:23.283516+09:00",
    "run_started_at": "2026-11-21T03:03:12.458376+09:00",
    "run_finished_at": "2026-11-21T03:37:35.708519+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23484121,
    "total_market_value_krw": 19695735,
    "total_unrealized_pnl_krw": -3788386,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 111880,
    "total_equity_krw": 20784267
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 542527,
      "current_price_krw": 432829,
      "market_value_krw": 5193952,
      "unrealized_pnl_krw": -1316375
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 290786,
      "current_price_krw": 280226,
      "market_value_krw": 3082492,
      "unrealized_pnl_krw": -116164
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 421768,
      "current_price_krw": 363747,
      "market_value_krw": 2182485,
      "unrealized_pnl_krw": -348128
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1869427,
      "current_price_krw": 1558220,
      "market_value_krw": 1558220,
      "unrealized_pnl_krw": -311207
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 552811,
      "current_price_krw": 416447,
      "market_value_krw": 1249341,
      "unrealized_pnl_krw": -409092
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 133760,
      "current_price_krw": 133925,
      "market_value_krw": 1205325,
      "unrealized_pnl_krw": 1479
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 265742,
      "current_price_krw": 181388,
      "market_value_krw": 1088328,
      "unrealized_pnl_krw": -506129
    },
    {
      "ticker": "GEV",
      "name": "GE 버노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1464598,
      "current_price_krw": 939245,
      "market_value_krw": 939245,
      "unrealized_pnl_krw": -525353
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 362527,
      "current_price_krw": 460217,
      "market_value_krw": 920434,
      "unrealized_pnl_krw": 195379
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1411993,
      "current_price_krw": 1800785,
      "market_value_krw": 785259,
      "unrealized_pnl_krw": 169538
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 566421,
      "current_price_krw": 410152,
      "market_value_krw": 410152,
      "unrealized_pnl_krw": -156269
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 659018,
      "current_price_krw": 376243,
      "market_value_krw": 376243,
      "unrealized_pnl_krw": -282775
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 135446,
      "current_price_krw": 92650,
      "market_value_krw": 370601,
      "unrealized_pnl_krw": -171185
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 345795,
      "current_price_krw": 333658,
      "market_value_krw": 333658,
      "unrealized_pnl_krw": -12137
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":325.025,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":330.3116251438571,"relative_volume":1.2307757773738637,"spread_bps":5.233265095661498,"day_high":343.75,"day_low":319.85,"execution_condition_ko":"위험 대응 조건: 351.14 이하 하락, 종가 확인 후 손절 조건 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"351.14 이하 하락, 종가 확인 후 손절 조건","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":705.025,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":715.9725652950295,"relative_volume":0.7443993204699614,"spread_bps":11.619833071179272,"day_high":745.2,"day_low":699.0,"execution_condition_ko":"위험 대응 조건: 747 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"747 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":312.54,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":316.56675346945184,"relative_volume":0.5736971239111116,"spread_bps":8.629920253143746,"day_high":327.98,"day_low":309.61,"execution_condition_ko":"위험 대응 조건: 323.28 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"323.28 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.635,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":100.63485659140397,"relative_volume":1.364659436718301,"spread_bps":0.9936900680682781,"day_high":100.64,"day_low":100.63,"execution_condition_ko":"새 정규장 종가의 100.60달러 지지와 바로 다음 실제 정규장의 100.60~100.61달러 재시험을 확인한다. 100.64달러는 지연 장전 고가로 관찰만 하며 추격하지 않는다. / 거래 가능 상태, 실시간 호가, 동시점 순자산가치, 최신 단기 국채 금리와 운용사 수익률·보수·분배 일정을 확인한다. 산식과 기준일이 불명확한 공급자 수치 3.64는 쓰지 않는다.","risk_condition_ko":"100.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":345.9376,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":349.1026495056447,"relative_volume":0.6375084635463667,"spread_bps":1.1563367252549859,"day_high":354.3,"day_low":344.57,"execution_condition_ko":"346.47~347.43달러 시험과 347.43달러 회복, 350.61달러 위 정규장 마감, 다음 정규장 재시험 지지를 순서대로 확인한다. / 355.28~356.42달러 돌파만으로 추격하지 않는다. 359.37~360.83달러 직전 고점대 상단 위 마감과 다음 정규장 지지를 확인한다.","risk_condition_ko":"346.47 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1170.88,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":1200.942094509521,"relative_volume":0.5679251827648197,"spread_bps":50.51970439146006,"day_high":1271.13,"day_low":1155.63,"execution_condition_ko":"1280~1297달러 지지 방어, 거래량 개선을 동반한 1328.47달러 초과 종가, 바로 다음 확인된 정규장의 1324~1328.47달러 재시험 성공을 순서대로 확인한다. / 첫 저항 1355달러까지 비용·갭 반영 후 보상 대비 위험을 다시 계산한다. 2배가 안 되면 1378.06달러를 대신 목표로 삼아 추격하지 않는다.","risk_condition_ko":"1,280 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":250.75,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":253.763225005988,"relative_volume":0.7195077575463071,"spread_bps":1.1963392020417976,"day_high":259.97,"day_low":249.16,"execution_condition_ko":"254.00–256.75달러 지지 유지, 262.92달러 초과 종가, 다음 정규 거래일의 262.45–262.92달러 재시험과 상단 회복을 순서대로 확인한다. / 275.67달러 초과 종가와 이후 지지 확인은 별도 재평가 신호이지 매수 신호가 아니다. 돌파 뒤 274.00달러 아래로 마감하면 해당 관찰을 중단한다.","risk_condition_ko":"254 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":210.51,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":211.4759155752367,"relative_volume":0.6370438021481365,"spread_bps":1.4246028919439249,"day_high":213.5899,"day_low":209.65,"execution_condition_ko":"211.00~211.34달러 지지와 212.52달러 회복은 관찰 신호다. 상대강도지수 50 회복도 보조 신호일 뿐이다. 216.25달러와 218.83달러는 저항이며, 210.17달러 이탈 뒤에는 207.16~208.09달러를 다음 지지 후보로 본다. / 11월 20일 미 동부 04:20:43 장전 자료는 57초 지연, 누적 3,800주, 호가 차이 약 0.63%였다. 판단 시각인 04:30:06에는 계획이 만료되지 않았지만 정규장 일정·거래정지 여부·실행 호가와 진입 조건 충족은 확인되지 않았다.","risk_condition_ko":"210.17 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1353.57,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":1358.461746681365,"relative_volume":0.4111614729040233,"spread_bps":9.456753821488793,"day_high":1372.05,"day_low":1350.2567,"execution_condition_ko":"1328.39~1341.46달러 시험 후 1341.46달러 위 정규장 종가, 바로 다음 검증된 정규장의 지지 유지와 1341.46~1349.03달러 실행 범위 확인. / 1380~1382달러에서는 추격하지 않고 최근 대비 거래량이 개선된 상향 마감과 재시험을 관찰한다. 이후 1395.20~1404.94달러 저항대가 지지로 바뀌는지 확인한다.","risk_condition_ko":"1,328.39 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":307.73,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":320.891208927025,"relative_volume":1.0731046838299831,"spread_bps":1.9495077492933774,"day_high":342.9,"day_low":304.65,"execution_condition_ko":"2026-11-19의 345.00달러 저가와 346.65달러 종가에 이어 바로 다음 확인된 거래일에 더 높은 저점과 345.00달러 위 종가가 나오는지 본다. 후속 확인이 실패하면 그 후보는 폐기하며, 지지 이탈이 없을 때만 만료 전 새 지지 시험을 관찰한다. / 366.94~370.03달러 저항을 종가로 돌파하고 다음 거래일에도 지지하는지 관찰한다. 다음 저항인 376.97~380.84달러가 가까워 돌파만으로 매수하거나 증액하지 않는다.","risk_condition_ko":"343.79 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":282.07,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":286.8074474400411,"relative_volume":0.8926346329177706,"spread_bps":13.832485059142257,"day_high":303.34,"day_low":276.0,"execution_condition_ko":"305.80~311.00달러는 지지 후보이지 매수 구간이 아니다. 336.36달러 위 일봉 마감은 반등 관찰 신호이며, 340.87~348.02달러 저항대 상단 돌파와 다음 실제 거래일의 지지 확인이 추세 개선 신호다. / 2026-11-20 미국 동부시간 04:01:32 기준, 03:51:50 관측값 312.54달러는 2026-11-19 종가와 같고 호가 지연은 28,307초로 표시됐다. 체결·5분봉·세션 거래량가중평균가격이 없어 실제 거래 세션, 거래정지 여부, 최신 호가 및 당일 조건 충족은 확인되지 않았다.","risk_condition_ko":"305.8 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":273.595,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":276.470397178958,"relative_volume":0.7326347014140004,"spread_bps":3.28953379995888,"day_high":283.14,"day_low":271.95,"execution_condition_ko":"270.479~272.36달러 지지 구간에서 272.36달러를 회복해 재시험을 견디는지, 이어 276.92달러를 정규장 종가로 되찾는지 확인한다. / 286.83달러 종가 돌파가 다음 거래일에도 유지되면 295.43~296.49달러를 다음 저항으로 본다. 돌파 후 285.72달러 아래로 마감하면 매수 재평가를 취소한다.","risk_condition_ko":"276.92 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":136.19,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":138.2520253213775,"relative_volume":1.2411381214458455,"spread_bps":1.468213184553062,"day_high":143.725,"day_low":134.82,"execution_condition_ko":"후속 정규장 종가의 145.71~145.98달러 회복과 다음 정규장 지지는 관찰 신호일 뿐 매수 조건이 아니다. / 150.33~150.96달러 돌파와 지지 이후 158.13~159.70달러, 다음으로 164.38~168.57달러를 확인한다. 모두 기술적 기준이며 가치평가 목표가가 아니다.","risk_condition_ko":"142.82 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":69.58,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":70.13023087393084,"relative_volume":0.9211409644448788,"spread_bps":1.4368848336792737,"day_high":70.92,"day_low":69.405,"execution_condition_ko":"72.34달러 위에서 정규장을 마감하고 다음 확인된 거래일에 72.32~72.34달러 구간을 지키면 안정화 신호로만 본다. / 76.18달러 돌파 종가, 75.96~76.18달러 재시험 방어, 이후 77.73달러 상회 종가를 순서대로 확인하면 새 매수 판단을 내린다. 자동 주문 조건은 아니다.","risk_condition_ko":"75.96 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":288.57,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":288.2490692665537,"relative_volume":0.4591721346164874,"spread_bps":3.1192056422955616,"day_high":290.23,"day_low":286.39,"execution_condition_ko":"278.01~279.88달러 시험 뒤 279.88달러 이상 종가와 차기 정규장 지지 유지. 279.88~280.25달러를 놓치거나 286.05~286.32달러 저항에 접근하면 추격하지 않는다. / 290.13~291.25달러 회복과 차기 정규장 재시험. 294.50~295.46달러와 298.74~302.93달러는 돌파 후 관찰할 저항대다.","risk_condition_ko":"277.64 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1114.16,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":1114.048678123308,"relative_volume":0.7400838895450798,"spread_bps":6.5498755075033595,"day_high":1122.81,"day_low":1099.3,"execution_condition_ko":"1083.15~1085.70달러 시험 후 1085.70달러 이상 정규장 종가와 다음 정규장 지지 유지를 확인한다. / 1108.50달러는 개장 전 관측에 근거한 잠정 첫 저항으로 정규장에서 재검증한다. 이후 1117.00달러와 1123.67달러를 관찰한다. 1123.67달러 상회 종가와 다음 정규장 지지는 재평가 신호일 뿐 자동 매수가 아니다.","risk_condition_ko":"1,075.05 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":407.57,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":407.09124413618116,"relative_volume":0.43142796448635523,"spread_bps":6.133689905173154,"day_high":408.735,"day_low":402.25,"execution_condition_ko":"V의 400.74달러 지지와 411.83~413.51달러 회복 여부를 먼저 본다. 이후 416.81달러, 422.05달러, 430.99달러 순으로 저항과 지지 전환을 점검한다. / 미국 합의와 영국 잠재 소송을 추적한다. 달러 강세 및 장기금리 하락은 시장 보도에 근거하며 V의 국경 간 결제와 손익에 미치는 순효과는 미확인이다.","risk_condition_ko":"400.74 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":571.89,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":573.6583739409105,"relative_volume":0.41714696235476334,"spread_bps":4.547362529732596,"day_high":576.89,"day_low":570.12,"execution_condition_ko":"583.72~588.54달러에서는 추격하지 않는다. 588.54달러 위 정규장 종가와 첫 저항 구간의 지지 전환이 확인되면 595.83~596.92달러까지의 비용 차감 후 보상을 다시 계산한다. / 11월 19일 수시공시는 제출 사실만 확인됐다. 공시 본문과 다음 실적 일정을 확인할 때까지 방향과 날짜를 가정하지 않는다. 공급자 분기표의 판단 시점 이전 이용 가능성과 공시 원문의 재무제표 표시통화·단위·B주 주당 기준, 미국예탁증서 적용 여부 및 해당 시 보통주 전환비율은 미확인이다. 절대금액·주당이익·평가배수는 판단에서 제외했다.","risk_condition_ko":"565.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LIN","display_name":"LIN","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":509.23,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":511.4539712226843,"relative_volume":0.6065255790958421,"spread_bps":2.7478998194234583,"day_high":516.425,"day_low":507.86,"execution_condition_ko":"508.00~510.21달러를 시험한 뒤 저점이 더 낮아지지 않고 510.21달러를 종가로 회복하는지 확인한다. 이는 지지 신호이지 단독 매수 신호가 아니다. / 519.54달러 종가 돌파 뒤 다음 정규장의 519.54~520.00달러 재시험과 체결 여건을 확인한다. 526.75달러 및 530.35~533.39달러에서는 추세를 재평가하되 추격하지 않는다.","risk_condition_ko":"508 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SO","display_name":"SO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":94.255,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":94.12624653439612,"relative_volume":0.34364680865719005,"spread_bps":3.1828550209539164,"day_high":94.485,"day_low":93.83,"execution_condition_ko":"92.42~92.79달러 시험 후 하단을 방어하고 거래 증가와 함께 92.79달러 위에서 마감한 뒤 다음 정규장에도 상단이 지지로 유지되는지 확인한다. / 94.94달러 초과 일봉 마감 후 다음 정규장에서 해당 가격이 지지로 바뀌는지 본다. 이는 추세 재평가 신호이며, 이후 저항 96.39달러와 97.65달러는 자동 매수·익절 기준이 아니다.","risk_condition_ko":"92.42 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":633.005,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":633.3935941472018,"relative_volume":0.3623725693649052,"spread_bps":6.003728631465786,"day_high":637.03,"day_low":626.6825,"execution_condition_ko":"641.06달러 상향 종가와 바로 다음 정규장의 지지 여부를 본다. 반등 시 654.08달러와 661~668달러에서 보유 근거와 손익비를 재평가한다. / 624.10~625.08달러의 이탈과 회복 여부를 우선 확인한다. 약 620달러와 605~606달러는 다음 관찰 구간이지 자동 매수선이 아니다.","risk_condition_ko":"624.1 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"KO","display_name":"KO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":97.715,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":97.36105476745736,"relative_volume":0.4711565053301685,"spread_bps":1.0233843319864009,"day_high":97.78,"day_low":96.765,"execution_condition_ko":"94.18~94.73달러 지지 시험 후 94.73달러 이상 정규장 마감과 다음 실제 정규장의 94.73달러 재지지를 확인한다. 허용 체결 구간은 94.73~95.10달러지만 첫 저항 기준 손익비를 통과한 호가에서만 스타터를 검토한다. / 96.72~97.25달러 회복과 정규장 거래가 뒷받침된 97.39달러 초과 마감, 다음 정규장 재지지를 관찰한다. 97.39달러에서 98.38달러까지 비용 전 0.99달러뿐이므로 돌파 자체로 비중을 늘리지 않는다. 98.38달러를 소화하면 100.56달러를 다음 저항으로 재평가한다.","risk_condition_ko":"94.18 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WMT","display_name":"WMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":129.85,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":129.3603095331026,"relative_volume":0.8223870081796487,"spread_bps":1.5403573629067937,"day_high":130.52,"day_low":127.22,"execution_condition_ko":"11월 19일 확인 마감 직후 첫 실제 정규장에서 123.03달러 지지 유지와 123.27~124.00달러 체결 가능성을 확인한다. 놓치면 만료 전 새 일봉 지지 시험과 그다음 실제 거래일 확인이 필요하다. / 126.76달러 종가 회복과 128.70달러를 넘는 정규장 종가 및 다음 거래일 유지는 반등 점검 신호다. 129.85달러와 131.49~131.82달러 저항을 앞두고 추격하지 않는다.","risk_condition_ko":"123.03 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":170.33,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":170.74545728283448,"relative_volume":0.36413494202768915,"spread_bps":2.935736723131337,"day_high":171.6125,"day_low":169.8,"execution_condition_ko":"2026-11-20 미국 동부시간 04:55:42 기준 원안의 검토 기한은 지나지 않았다. 다만 04:45의 169.41달러는 1,740주에 그친 지연 장전 관측이다. 실제 정규장 운영과 최신 호가를 확인하며, 169.79~170.73달러에서는 추격하지 않는다. / 원공시 공개 시각과 재무제표 표시 통화·단위, 주당 수치의 주식 기준, 예탁증서 해당 여부와 해당 시 보통주 환산비율을 확인한다. 확인 전에는 공급자의 재무 금액·주당순이익·평가배수 비교를 제외한다. 유로화 채권은 자금 용도·조달비용·순부채 효과를 확인하기 전에는 차환 개선으로 보지 않는다.","risk_condition_ko":"166.89 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ORCL","display_name":"Oracle","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":103.21,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":104.54764148535973,"relative_volume":0.49707361499384733,"spread_bps":6.782617121262843,"day_high":108.99,"day_low":101.89,"execution_condition_ko":"109.21~110.24달러 지지 구간을 회복하고 다음으로 확인된 정규장 재시험에서 지키는지 관찰 / 거래량 증가를 동반한 118.50~118.68달러 구간 돌파, 121.35달러 위 정규장 종가, 다음 정규장 지지 여부를 순서대로 확인","risk_condition_ko":"109.21 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":101.1391,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":101.70138393968057,"relative_volume":0.34909672997607005,"spread_bps":4.943398091848056,"day_high":102.605,"day_low":100.86,"execution_condition_ko":"실적 전에는 99.59~100.00달러 지지, 101.29달러 회복, 101.95달러 초과 정규장 종가와 다음 실제 정규장 재시험을 기록만 합니다. 재시험이 성공해도 주문하지 않습니다. / 102.86~104.49달러 첫 저항에서는 추격하지 않습니다. 이 구간을 소화할 때만 105.72~106.20달러를 다음 저항으로 봅니다.","risk_condition_ko":"99.59 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WELL","display_name":"WELL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":243.63,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":243.8722707838119,"relative_volume":0.2548207488939726,"spread_bps":11.490007796791051,"day_high":246.75,"day_low":242.7158,"execution_condition_ko":"241.52~243.03달러 지지와 244.46달러 종가 회복을 관찰한다. 다음 실제 거래 세션에서 지지를 확인하더라도 기존 244.46~244.75달러 구간은 주문 구간이 아니다. / 249.75달러 위 첫 돌파는 추격하지 않는다. 다음 저항 253.37달러까지 3.62달러로 11월 19일 평균 실제 변동폭 5.25달러보다 짧다. 하락 시 234.58달러와 221.08달러는 추세 재평가 기준이지 추가 매수 가격이 아니다.","risk_condition_ko":"240.18 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AES","display_name":"AES","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":15.02,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":15.02576278177568,"relative_volume":2.1063220652490986,"spread_bps":6.65557404326109,"day_high":15.03,"day_low":15.02,"execution_condition_ko":"최신 체결 가능 호가와 거래 가능 여부를 확인하고, 공식 인수 조건에 근거해 순수익·최고 매수가·무산 하방을 다시 산정한다. / $15.04 초과 정규장 종가 또는 $14.97~$14.99 지지 뒤 $15.02 이상 정규장 종가를 확인하고 다음 실제 거래일의 지지를 점검한다.","risk_condition_ko":"14.97 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NU","display_name":"NU","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":11.455,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":11.52819589056906,"relative_volume":0.3788994178889632,"spread_bps":8.72981230903672,"day_high":11.91,"day_low":11.32,"execution_condition_ko":"위험 대응 조건: 11.65 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"11.65 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SPCX","display_name":"SPCX","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":129.7977,"market_data_asof":"2026-11-20T18:34:49+00:00","market_data_clock_status":null,"session_vwap":130.20408530481933,"relative_volume":0.8376751394613209,"spread_bps":3.0811893390842737,"day_high":133.8408,"day_low":127.93,"execution_condition_ko":"위험 대응 조건: 133.14 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"133.14 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-20T18:34:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T18:37:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-21T01:11:15.178376+09:00",
  "as_of": "2026-11-20T16:04:30+00:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
