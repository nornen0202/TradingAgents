# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-02T15:31:09.980915+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261103T002522_local-freshness-us-overlay",
  "producer_finished_at": "2026-11-03T00:28:12.606752+09:00",
  "analysis_run_id": "20261102T185558_local-scheduler-us-full",
  "analysis_completed_at": "2026-11-02T22:27:07.024446+09:00",
  "analysis_trade_date_oldest": "2026-10-30",
  "analysis_trade_date_latest": "2026-10-30",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-02T15:26:30+00:00",
  "market_data_latest_at": "2026-11-02T15:26:30+00:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-03T00:01:57.368765+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-03T00:01:57.368765+09:00",
    "run_started_at": "2026-11-03T00:00:36.469071+09:00",
    "run_finished_at": "2026-11-03T00:02:04.357506+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23597075,
    "total_market_value_krw": 22732172,
    "total_unrealized_pnl_krw": -864903,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 107858,
    "total_equity_krw": 23816682
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 545136,
      "current_price_krw": 541766,
      "market_value_krw": 6501198,
      "unrealized_pnl_krw": -40438
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 292185,
      "current_price_krw": 294551,
      "market_value_krw": 3240069,
      "unrealized_pnl_krw": 26031
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 423797,
      "current_price_krw": 381911,
      "market_value_krw": 2291466,
      "unrealized_pnl_krw": -251317
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1878418,
      "current_price_krw": 1681629,
      "market_value_krw": 1681629,
      "unrealized_pnl_krw": -196789
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 267020,
      "current_price_krw": 277803,
      "market_value_krw": 1666819,
      "unrealized_pnl_krw": 64694
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 555469,
      "current_price_krw": 498815,
      "market_value_krw": 1496447,
      "unrealized_pnl_krw": -169961
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 134404,
      "current_price_krw": 134289,
      "market_value_krw": 1208602,
      "unrealized_pnl_krw": -1034
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1471642,
      "current_price_krw": 1175378,
      "market_value_krw": 1175378,
      "unrealized_pnl_krw": -296264
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 364271,
      "current_price_krw": 454828,
      "market_value_krw": 909657,
      "unrealized_pnl_krw": 181115
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1418783,
      "current_price_krw": 1876532,
      "market_value_krw": 818290,
      "unrealized_pnl_krw": 199608
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 662188,
      "current_price_krw": 549756,
      "market_value_krw": 549756,
      "unrealized_pnl_krw": -112432
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 569145,
      "current_price_krw": 439657,
      "market_value_krw": 439657,
      "unrealized_pnl_krw": -129488
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 136097,
      "current_price_krw": 104716,
      "market_value_krw": 418864,
      "unrealized_pnl_krw": -125527
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 347458,
      "current_price_krw": 334340,
      "market_value_krw": 334340,
      "unrealized_pnl_krw": -13118
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":339.85,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":341.50205929525356,"relative_volume":1.1403577059313152,"spread_bps":2.0596413281742216,"day_high":343.78,"day_low":339.61,"execution_condition_ko":"지지 일봉과 다음 실제 거래 세션 확인이 끝난 뒤에도 338.70~339.27이 제공되는지 점검한다. 먼저 상승하면 추격하지 않는다. / 348.91~349.19와 351.43~351.73의 저항 반응을 관찰한다. 351.73 위에는 제공된 목표가가 없으므로 새로운 보상위험 평가가 필요하다.","risk_condition_ko":"338.7 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":220.875,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":220.1741593084575,"relative_volume":1.4892089233014734,"spread_bps":0.4527652638485457,"day_high":220.95,"day_low":219.51,"execution_condition_ko":"217.13~217.36 지지 시험, 217.36 이상 종가 회복, 다음 실제 거래일 지지·반등, 217.13~217.20 재접근 및 비용 후 보상·위험비율 1 초과를 순서대로 확인한다. / 216.03~216.26 회복 실패 시 신규 진입을 보류하고 214.72 종가 이탈 여부를 점검한다. 감시가격 도달과 매도 조건 충족을 구분한다.","risk_condition_ko":"214.72 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":411.035,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":408.34551715338415,"relative_volume":1.0787277744731572,"spread_bps":8.272103547272032,"day_high":414.7599,"day_low":403.27,"execution_condition_ko":"398.65–400.12의 새로운 시험, 400.12 초과 종가와 다음 거래일 지지 확인을 순서대로 점검한다. 이후 비용 조정된 400.12–402.50에서만 소액 진입을 검토한다. / 410.22–418.09의 매물 부담을 점검한다. 418.09 회복만으로 전체 비중 진입을 허용하지 않는다.","risk_condition_ko":"398.65 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.4299,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":100.42623806999211,"relative_volume":3.1222148832265,"spread_bps":0.9957679860597575,"day_high":100.43,"day_low":100.42,"execution_condition_ko":"2026-10-30 일별 가격과 2026-11-02 장전 가격, 상충하는 이동평균의 조정 기준을 먼저 대조한다. 공격적 분석가가 언급한 과거 가격 강세만으로 진입 가치를 인정하지 않는다. / 경제성 검증 후 종가 100.44 초과와 다음 확인된 거래일의 하단 100.42·상단 100.44 지지 재시험을 관찰한다.","risk_condition_ko":"100.42 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1403.88,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":1401.09364932745,"relative_volume":1.403152429492443,"spread_bps":6.41062168784449,"day_high":1411.64,"day_low":1387.1,"execution_condition_ko":"새 정규장 종가가 하단 1391.31, 상단 1408.36 안에서 안정된 뒤 다음 정규장 지지를 확인한다. 범위 밖 가격은 추격하지 않는다. / 1449.68은 관찰 저항이자 돌파 재평가선이다. 돌파와 재시험 성공만으로 자동 추가 매수하지 않는다.","risk_condition_ko":"1,330 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":417.8835,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":415.51647536103457,"relative_volume":0.750691887940698,"spread_bps":9.571667863125965,"day_high":424.13,"day_low":408.72,"execution_condition_ko":"413.00 방어와 일봉 저점 상승을 관찰한다. 장중 접촉이나 지지 유지 자체는 매수 신호가 아니다. / 441.08 종가 회복·다음 실제 거래일 지지와 447.93~456.44 매물 소화 여부를 확인한다.","risk_condition_ko":"413 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1306.56,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":1260.5815750394456,"relative_volume":1.0439535622822917,"spread_bps":24.05448263710749,"day_high":1306.99,"day_low":1230.82,"execution_condition_ko":"2026-10-30 이후 완료 일봉과 기존 감축 기록을 확인한다. 새 회복 증거가 있으면 감축 필요성을 재평가하되 지연된 장전 관측만으로 기존 신호를 취소하지 않는다. / 1217.41–1224.14의 종가 회복과 후속 지지를 관찰한다. 이 조건만으로 매수하지 않는다.","risk_condition_ko":"1,248.74 이상 도달, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":895.93,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":881.3239625354848,"relative_volume":0.9608551810005959,"spread_bps":17.186349128407443,"day_high":896.3935,"day_low":864.8397,"execution_condition_ko":"검증된 일봉 종가가 886.61을 넘고 다음 확인된 거래일에 883.45–886.61 지지 여부를 점검한다. 이는 자동 매수가 아닌 재평가 조건이다. / 899.33과 914.88을 순차 저항으로 확인한다. 934.50–943.76 회복과 유지 시 기술적 근거가 개선되지만 신규 매수에는 별도 판단이 필요하다.","risk_condition_ko":"844.08 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":377.49,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":373.02123201211816,"relative_volume":0.7432609988351018,"spread_bps":11.397219608518942,"day_high":377.49,"day_low":370.13,"execution_condition_ko":"주문 전 실제 거래일·거래 상태·정규 거래시간 및 최신 실행 가능 호가를 별도로 확인한다. 2026-11-02 미국 동부시간 05:34:44의 판단 시계는 거래 가능 여부나 진입 충족을 입증하지 않는다. / 364.84–366.11을 우선 감시하고 그 아래에서는 358.51–362.49와 기존 손절 기준에 따라 방어를 강화한다.","risk_condition_ko":"385.96 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":332.71,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":328.3806034325189,"relative_volume":0.8618382865789169,"spread_bps":3.606527815345912,"day_high":332.79,"day_low":324.31,"execution_condition_ko":"319.30~321.02 지지 관찰과 319.30 아래 종가 이탈을 구분한다. / 331.98~332.26 회복은 초기 반등 관찰에만 사용하고 신규매수 승인으로 해석하지 않는다.","risk_condition_ko":"319.3 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":286.0,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":285.06737321287665,"relative_volume":1.7236553458965331,"spread_bps":1.0488593654411174,"day_high":287.0,"day_low":282.36,"execution_condition_ko":"276.92 주변의 확인된 정규장 종가와 283.14~288.33 반등 실패를 감시한다. 현재 어느 추가 감축 조건도 충족됐다고 단정하지 않는다. / 288.33 상향 종가 이후 다음 세션 지지 또는 재돌파를 확인한다. 공시 검증과 새로운 손익비 평가 전에는 조건부 시험 매수도 승인하지 않는다.","risk_condition_ko":"276.92 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":252.955,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":249.01606190343338,"relative_volume":1.9868329059859267,"spread_bps":0.7907638779064617,"day_high":252.96,"day_low":242.28,"execution_condition_ko":"일봉 종가 243.79 상회 후 다음 확인된 거래일에 241.24–243.79 지지 유지: 자동 매수나 기계적인 추가 매도 대신 배분 판단을 재평가한다. / 246.45–250.73 회복 후 254.28 위 안착: 기술적 추세 복구 근거가 강화된다.","risk_condition_ko":"243.4 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":209.71,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":208.09736906891033,"relative_volume":1.1132728751174144,"spread_bps":1.4305810543382915,"day_high":209.825,"day_low":206.73,"execution_condition_ko":"2026-11-09까지 재검토하고 중대한 공식 발표 시 즉시 갱신한다. 이 날짜는 연구 검토 기한이며 주문 만료나 확인된 거래일 마감이 아니다. / 200.92–204.09의 일별 종가와 명시된 추가 감축·잔여 청산 순서를 점검한다. 더 엄격한 기존 손절은 즉시 우선한다.","risk_condition_ko":"210.18 이하 하락, 종가 확인 후 (위험 축소 매도에 추가 거래량 조건을 요구하지 않는다.) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":78.28,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":78.25844278981566,"relative_volume":2.361443622347868,"spread_bps":1.2772207676085197,"day_high":78.4399,"day_low":78.06,"execution_condition_ko":"다음 확인된 거래일 이후 일봉과 거래량을 갱신하고 78.06 및 78.63–79.19에서 회복 유지와 반락을 구분한다. / 새 매수 검토 시 가장 가까운 신뢰할 만한 저항까지 비용 후 보상 대비 위험을 다시 계산한다. 2:1은 선별 조건이지 수익성의 보장이 아니다.","risk_condition_ko":"78.63 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":183.17,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":182.84965004935356,"relative_volume":0.9308485325802061,"spread_bps":3.820439350524938,"day_high":184.586,"day_low":181.514,"execution_condition_ko":"위험 대응 조건: 184.59 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"184.59 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"UNH","display_name":"UNH","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":400.18,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":402.1077382430456,"relative_volume":0.9307686809635739,"spread_bps":5.49890021995527,"day_high":408.8798,"day_low":397.16,"execution_condition_ko":"위험 대응 조건: 404.31 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"404.31 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":206.975,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":207.8548796070262,"relative_volume":0.5854844428450555,"spread_bps":7.24795245343218,"day_high":209.94,"day_low":206.79,"execution_condition_ko":"2026-11-13T23:59:59-05:00까지 실제 거래일 기준으로 검토한다. 최초 활성화는 지지 확인 일봉의 다음 실제 거래일부터이며, 후속 진입 조건이 기한 안에 충족되지 않으면 미체결 계획을 종료한다. 자동 연장하거나 다음 세션으로 이월하지 않는다. / 208.02~208.50 이탈 후 회복 실패는 경고다. 해당 구간 바로 아래에 새 기계적 손절을 설정하지 않는다.","risk_condition_ko":"202.19 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":423.63,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":421.68647084108073,"relative_volume":0.8847576211430466,"spread_bps":2.1244703577379545,"day_high":424.13,"day_low":414.369,"execution_condition_ko":"2026-10-30을 가격 기준일로 유지하고, 새 일봉으로 414.34–417.00 저항과 410.54–411.82 초기 지지를 점검한다. / 403.46–404.98의 이동평균 기반 구간을 갱신한다. 단순 접촉은 매수 신호가 아니며 낮아진 평균으로 고정 손절을 대체하지 않는다.","risk_condition_ko":"403.46 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":288.76,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":288.52812872674997,"relative_volume":1.2503152585035329,"spread_bps":12.807864721256022,"day_high":294.86,"day_low":286.14,"execution_condition_ko":"290.79–292.67은 첫 지지 관찰 구간일 뿐 승인된 매수 구간이 아니다. 285.35–286.98에서만 완전한 확인 절차와 비용 후 최소 2배 보상·위험비를 평가한다. / 298.74–300.00 저항을 관찰한다. 300 초과 종가와 후속 지지는 재검토 사유지만 검증된 상위 목표가 없어 자동 추가 매수 조건은 아니다.","risk_condition_ko":"285.35 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1026.02,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":1023.8407719944297,"relative_volume":0.9488029475863313,"spread_bps":4.970154708249173,"day_high":1029.65,"day_low":1014.335,"execution_condition_ko":"993–994의 새 일봉 회복과 다음 정규장 지지 확인을 감시한다. 실행가는 994를 넘지 않아야 하며 비용 차감 후 보상 대비 위험도 통과해야 한다. / 1000–1006.56은 초기 지지 관찰 구간일 뿐, 유지된다는 이유만으로 최초 편입을 실행하지 않는다.","risk_condition_ko":"993 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":97.56,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":97.40356799639677,"relative_volume":0.10237986991760127,"spread_bps":3.075188355285421,"day_high":97.795,"day_low":96.75,"execution_condition_ko":"94.41~94.96 지지 테스트와 종가 확인 이후 다음 거래일 지속 여부를 관찰한다. 최초 체결 범위는 94.41~94.70이다. / 96.89~97.20 공급 압력과 98.09 돌파 후 지지 전환을 구분해 관찰한다. 확인 과정에서 체결가가 94.70을 넘으면 기존 계획으로 추격하지 않는다.","risk_condition_ko":"94.41 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RTX","display_name":"RTX","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":201.75,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":200.84833003746562,"relative_volume":0.5945175812675407,"spread_bps":9.911293919420618,"day_high":201.9,"day_low":199.8,"execution_condition_ko":"최초 활성화에는 2026-11-02 이후 적격 일봉과 그다음 검증된 정규장의 확인이 필요하다. 지연된 장전 관측이나 2026-10-30 종가로 이를 대체하지 않는다. 특정 다음 거래일은 거래 일정 확인 전 단정하지 않는다. / 지지 재시험 후 실제 매수가가 194.40 이상이고 194.80에서 주당 추정 왕복비용을 차감한 값 이하인지 확인한다. 순보상/위험비율 1.5 미달, 비용 확인 불가 또는 매수 구간 부재 시 계속 대기한다.","risk_condition_ko":"193.5 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NEE","display_name":"NEE","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":83.8386,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":83.74079301922234,"relative_volume":0.4815309567159815,"spread_bps":1.1928192282465695,"day_high":83.97,"day_low":83.27,"execution_condition_ko":"NEE의 새로운 82.40~82.90 재시험과 종가 82.84 이상 회복을 확인한다. 눌림 중 매도 거래량 감소는 보조 근거이며 저가 접촉만으로 진입하지 않는다. / 회복 신호 다음 실제 거래 세션의 82.40 지지, 82.40~82.90 체결 기회, 최소 차환 검증 및 계좌 잔여 위험예산을 함께 확인한다.","risk_condition_ko":"81.33 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":550.465,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":548.6579165402743,"relative_volume":0.6984983794619125,"spread_bps":1.9983105192884862,"day_high":550.74,"day_low":544.94,"execution_condition_ko":"537.33–539.23 시험과 539.23 이상 종가, 다음 확인된 거래일의 지지 유지 및 종가를 순차 확인한다. 단순 접촉은 매수 신호가 아니다. / 548.31–550.47에서 재차 거절되는지, 돌파 후 지지로 전환되는지 관찰한다.","risk_condition_ko":"537.33 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":654.78,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":651.2932125206778,"relative_volume":0.8222040191668908,"spread_bps":9.01017844734821,"day_high":655.63,"day_low":638.25,"execution_condition_ko":"새 정규장 종가 633.34 이상과 다음 실제 거래일의 633.29~633.34 지지 재시험을 확인한다. 해당 범위 밖에서는 추격하지 않는다. / 644.24 접근 시 저항·이익 보호 조건을 재평가하고 종가 돌파와 다음 거래일 지지 유지를 관찰한다. 관측되지 않은 상승 목표로 손익비를 부풀리지 않는다.","risk_condition_ko":"633.29 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SPG","display_name":"Simon Property Group","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":220.38,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":220.56316861321034,"relative_volume":0.4364727904117131,"spread_bps":13.163568688862805,"day_high":221.595,"day_low":218.64,"execution_condition_ko":"213.75–215.36 시험, 적격 반전 종가, 다음 정규장 지지 유지 순서를 확인한다. 비용 반영 후에도 유효한 213.75–214.20 이내 가격이 없으면 거래를 건너뛴다. / 218.40 종가 돌파와 다음 정규장 지지를 관찰하되 현재 승인 범위를 넘어 추격하지 않는다.","risk_condition_ko":"210.48 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":163.16,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":162.887446069974,"relative_volume":0.5830719335786946,"spread_bps":3.677371904878786,"day_high":163.85,"day_low":162.24,"execution_condition_ko":"158.42–159.23 시험, 159.23 초과 종가, 다음 확인된 거래일 지지를 순서대로 관찰한다. 159.00 이하 실행 가능성과 비용 후 보상 대비 위험 2 이상이 사라지면 추격하지 않는다. / 164.50·165.75에서는 최신 정규장 체결 가능 가격으로 이익실현 조건을 확인하고 이미 집행한 물량을 제외한다.","risk_condition_ko":"164.5 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":232.345,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":231.42350324404373,"relative_volume":0.7848958149954672,"spread_bps":5.16484462425775,"day_high":233.25,"day_low":229.645,"execution_condition_ko":"위험 대응 조건: 236.48 이상 도달, 장중 확인 시 이익실현성 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"236.48 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SMCI","display_name":"Super Micro Computer","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":33.425,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":33.08921421706309,"relative_volume":1.039029865464582,"spread_bps":5.98444045481841,"day_high":33.5,"day_low":32.51,"execution_condition_ko":"위험 대응 조건: 32.58 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"32.58 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"KVUE","display_name":"KVUE","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":19.31,"market_data_asof":"2026-11-02T15:26:30+00:00","session_vwap":null,"relative_volume":0.0,"spread_bps":129.29919834497025,"day_high":19.31,"day_low":19.31,"execution_condition_ko":"핵심 원공시 검증과 19.20~19.25 시험 후 19.25 이상 종가, 다음 거래가능 세션 재지지가 함께 충족되는지 확인 / 19.50~19.60 저항에서의 가격 반응과 실제 비용 차감 후 보상 여지 점검; 회복만으로 증액하지 않음","risk_condition_ko":"19.2 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-02T15:26:30+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-02T15:28:30+00:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:news_halt_status","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-02T23:15:11.329023+09:00",
  "as_of": "2026-11-02T04:10:00-05:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
