# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-30T14:24:48.579672+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261030T232151_local-freshness-us-overlay",
  "producer_finished_at": "2026-10-30T23:23:23.036387+09:00",
  "analysis_run_id": "20261030T175058_local-scheduler-us-full",
  "analysis_completed_at": "2026-10-30T21:03:21.361439+09:00",
  "analysis_trade_date_oldest": "2026-10-29",
  "analysis_trade_date_latest": "2026-10-29",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-30T10:07:00-04:00",
  "market_data_latest_at": "2026-10-30T14:22:01+00:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-30T23:02:32.865524+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-30T23:02:32.865524+09:00",
    "run_started_at": "2026-10-30T23:01:21.803557+09:00",
    "run_finished_at": "2026-10-30T23:02:42.933834+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23563547,
    "total_market_value_krw": 22854869,
    "total_unrealized_pnl_krw": -708678,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 106984,
    "total_equity_krw": 23938465
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 544361,
      "current_price_krw": 555858,
      "market_value_krw": 6670304,
      "unrealized_pnl_krw": 137963
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 291770,
      "current_price_krw": 292684,
      "market_value_krw": 3219528,
      "unrealized_pnl_krw": 10056
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 423195,
      "current_price_krw": 375299,
      "market_value_krw": 2251796,
      "unrealized_pnl_krw": -287374
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 266641,
      "current_price_krw": 277428,
      "market_value_krw": 1664571,
      "unrealized_pnl_krw": 64722
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1875749,
      "current_price_krw": 1652947,
      "market_value_krw": 1652947,
      "unrealized_pnl_krw": -222802
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 554680,
      "current_price_krw": 504943,
      "market_value_krw": 1514831,
      "unrealized_pnl_krw": -149210
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 134213,
      "current_price_krw": 134517,
      "market_value_krw": 1210659,
      "unrealized_pnl_krw": 2742
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1469551,
      "current_price_krw": 1164595,
      "market_value_krw": 1164595,
      "unrealized_pnl_krw": -304956
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 363753,
      "current_price_krw": 460918,
      "market_value_krw": 921837,
      "unrealized_pnl_krw": 194330
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1416768,
      "current_price_krw": 1907642,
      "market_value_krw": 831856,
      "unrealized_pnl_krw": 214053
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 661247,
      "current_price_krw": 580581,
      "market_value_krw": 580581,
      "unrealized_pnl_krw": -80666
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 568336,
      "current_price_krw": 439233,
      "market_value_krw": 439233,
      "unrealized_pnl_krw": -129103
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 135904,
      "current_price_krw": 103405,
      "market_value_krw": 413622,
      "unrealized_pnl_krw": -129996
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 346964,
      "current_price_krw": 318509,
      "market_value_krw": 318509,
      "unrealized_pnl_krw": -28455
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":861.745,"market_data_asof":"2026-10-30T10:22:00-04:00","session_vwap":866.9621933642078,"relative_volume":1.4539835503802752,"spread_bps":17.30515728529711,"day_high":886.07,"day_low":845.66,"execution_condition_ko":"위험 대응 조건: 854 이하 하락, 다음 거래일 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"854 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T10:24:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":345.91,"market_data_asof":"2026-10-30T10:22:00-04:00","session_vwap":345.6320527890203,"relative_volume":1.3691934903560075,"spread_bps":2.3127403081721862,"day_high":348.7696,"day_low":344.13,"execution_condition_ko":"눌림·344.90 이상 종가 회복·다음 확인된 거래일 지지를 순서대로 확인한다. 가격이 이미 진입구간 위로 이탈하면 추격하지 않는다. / 348.91과 351.43~351.73에서 저항 반응과 잔여 손익비를 점검한다. 351.98 돌파만으로 증액하지 않는다.","risk_condition_ko":"344.46 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T10:24:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":218.715,"market_data_asof":"2026-10-30T10:22:00-04:00","session_vwap":219.48994548145836,"relative_volume":1.0755767947588006,"spread_bps":0.9144529285359716,"day_high":220.23,"day_low":218.66,"execution_condition_ko":"218.18–218.29의 새로운 시험, 218.29 이상 정규장 종가 회복, 후속 정규장의 지지 유지와 범위 내 매수 가능 여부를 순서대로 확인한다. / 220.40–220.54, 221.94–222.13, 222.60의 저항 거부와 지속 돌파를 구분한다. 상단 목표 도달 가능성을 첫 저항의 존재와 함께 평가한다.","risk_condition_ko":"218.18 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T10:24:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":412.79,"market_data_asof":"2026-10-30T10:22:00-04:00","session_vwap":415.47157293601737,"relative_volume":1.3612865248368389,"spread_bps":5.087517412633506,"day_high":418.0895,"day_low":412.42,"execution_condition_ko":"2026-10-30 또는 이후 실제 확인된 정규장에서 지지 구간 시험과 412.61 이상 종가를 관찰하고, 다음 확인 거래 세션의 재시험을 별도로 확인한다. 현재 조건 충족을 주장하지 않는다. / 425.70, 431.09~434.71, 438.58~440.88 및 449~453의 회복·저항 반응을 관찰한다. 회복 돌파만으로 추가매수하지 않는다.","risk_condition_ko":"410.22 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T10:24:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":327.495,"market_data_asof":"2026-10-30T10:22:00-04:00","session_vwap":330.23758240461405,"relative_volume":1.3585082401468562,"spread_bps":3.053901358986799,"day_high":331.98,"day_low":326.75,"execution_condition_ko":"2026-10-30 장전 관측 이후 새 정규장 종가 340.35 초과, 다음 확인된 거래일의 338.80–340.35 지지 및 종가 338.80 이상을 순서대로 확인한다. 2026-10-29 종가만으로 이 절차가 완료되지는 않는다. / 진입은 하단 구간으로 제한하고 실제 비용과 보수적인 갭 여유 적용 후 손익비 1.5 이상인지 확인한다. 모든 후보가 탈락하면 매수하지 않는다.","risk_condition_ko":"330.8 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T10:24:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":100.7385,"market_data_asof":"2026-10-30T10:22:00-04:00","session_vwap":100.73421445794686,"relative_volume":3.2583167190208986,"spread_bps":0.9927036283308587,"day_high":100.74,"day_low":100.73,"execution_condition_ko":"공식 운용자료의 내용과 공표 시각, 수익률 산식, 분배금 일정·금액, 실제 현금 대안의 수익 및 계좌 여력을 확인한다. 주변적인 기사·사회관계망 자료 부족만으로 검증 완료 후에도 무기한 대기하지 않는다. / 2026-10-29의 보고 가격 100.70–100.71과 이례적으로 매끄러운 가격 이력의 조정 방식을 실행 가능한 가격에 대조한다.","risk_condition_ko":"100.7 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T10:24:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1431.05,"market_data_asof":"2026-10-30T10:22:00-04:00","session_vwap":1428.5709283103854,"relative_volume":1.8064333873253817,"spread_bps":15.803864254595993,"day_high":1449.6799,"day_low":1417.375,"execution_condition_ko":"1321.21~1330.00 시험, 1330.00 초과 일봉 종가, 다음 검증된 거래일의 지지 유지 재시험을 순서대로 확인한다. / 1408.38 초과 일봉 종가와 이후 성공적인 재시험은 돌파 경로를 새로 평가할 사유다. 이번 눌림목 진입 허가로 추격 매수하지 않는다.","risk_condition_ko":"1,321.21 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T10:24:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":1218.16,"market_data_asof":"2026-10-30T10:22:00-04:00","session_vwap":1221.1530146206949,"relative_volume":2.999416491261361,"spread_bps":19.516675276965476,"day_high":1263.05,"day_low":1171.02,"execution_condition_ko":"1230.42 초과 종가와 다음 거래일의 1218.70–1230.42 지지를 관찰한다. 이는 검토 재개 조건이지 자동 매수 신호가 아니다. 원문 실적 근거, 개선된 정규장 참여, 비용 후 최소 2:1의 보상 대비 위험 및 매도 위험 판단의 해소가 함께 필요하다. / 1163.86–1167.93 및 1126.57–1140.12의 지지 유지와 실패를 구분한다. 단순한 지지 접촉은 매수 근거가 아니다.","risk_condition_ko":"1,218.7 이상 도달, 장중 확인 시 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T10:24:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":431.56,"market_data_asof":"2026-10-30T10:22:00-04:00","session_vwap":431.1930218964666,"relative_volume":1.7076039605901958,"spread_bps":11.811981054508609,"day_high":441.0757,"day_low":413.0,"execution_condition_ko":"결정 이후 검증된 정규장 종가의 439.50 회복과 448.00–456.44 회복을 초기 안정화 검토 신호로 관찰한다. / 456.44 초과 종가 이후 다음 검증 거래일에 448.00–451.09 방어와 448.00 이상 종가를 확인하면 조기 회복 재심사를 진행한다. 자동 매수 조건은 아니다.","risk_condition_ko":"484.88 이하 하락, 종가 확인 후 (위험 축소에 매수 거래량 확인을 요구하지 않는다.) 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T10:24:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":206.53,"market_data_asof":"2026-10-30T10:22:00-04:00","session_vwap":207.2939980571066,"relative_volume":1.4673813433599499,"spread_bps":0.9683823173380046,"day_high":209.05,"day_low":205.71,"execution_condition_ko":"새로운 정규장 종가의 212.08 상회 후 다음 검증된 거래일에 210.18–212.08 지지를 확인한다. 213.66의 가까운 저항도 함께 평가한다. / 216.81–217.67 유지 여부를 확인하되 219.99와 221.92–222.19 저항 아래에서 자동 증액하지 않는다. 더 높은 진입가는 오히려 보상위험비를 악화시킬 수 있다.","risk_condition_ko":"207.3 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T10:24:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":374.845,"market_data_asof":"2026-10-30T10:22:00-04:00","session_vwap":378.45861028180144,"relative_volume":0.7325614615104201,"spread_bps":8.270305601131223,"day_high":382.235,"day_low":372.88,"execution_condition_ko":"단기 회복대 하단 389.51, 상단 391.39의 유지·재회복 여부. 2026-10-29 종가 393.72는 이미 이 구간 위였으므로 현재 미회복 상태라고 단정하지 않는다. / 추세 재평가대 하단 395.46, 상단 400의 종가 돌파와 다음 확인된 정규세션 지지. 충족해도 자동 매수는 아니다.","risk_condition_ko":"384.31 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T10:24:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":280.01,"market_data_asof":"2026-10-30T10:22:00-04:00","session_vwap":281.0203423776156,"relative_volume":2.932644862111715,"spread_bps":1.0713711765431393,"day_high":281.9899,"day_low":279.0,"execution_condition_ko":"향후 3~5개 확인된 거래세션 동안 관찰하고 2026-11-06T21:00:00Z까지 재평가한다. 이는 연구 검토기한이며 주문 만료나 확인된 거래소 종가 시각이 아니다. / 280.36 종가 이탈은 추가 위험축소 조건이다. 278.15와 271.77~273.61은 과거 저점 관찰대일 뿐 확정 지지·매수 지정가·손절 연기 근거가 아니다.","risk_condition_ko":"280.36 이하 하락, 종가 확인 후 (위험감축에는 매수 거래량 조건을 적용하지 않는다.) 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T10:24:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":235.7,"market_data_asof":"2026-10-30T10:22:00-04:00","session_vwap":234.72515167746815,"relative_volume":4.734708585359444,"spread_bps":2.5453928389615763,"day_high":240.21,"day_low":229.3632,"execution_condition_ko":"다음 3~5개의 확인된 거래일 동안 점검하고 2026-11-06까지 연구를 갱신한다. 이는 검토 기한이며 주문 만료나 거래소 마감 시각이 아니다. / 232.05 초과 종가와 이후 230.86~232.05 지지를 관찰한다. 더 강한 244.30 회복을 기다리지 않고 개선 근거를 먼저 검토할 수 있지만 매수는 별도 결정이다.","risk_condition_ko":"244.3 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T10:24:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":77.211,"market_data_asof":"2026-10-30T10:22:00-04:00","session_vwap":77.52432538204789,"relative_volume":2.3936845251957957,"spread_bps":1.2950851518493964,"day_high":78.06,"day_low":77.135,"execution_condition_ko":"2026-10-29 저점 79.19 회복을 관찰하되 이것만으로 매수하지 않는다. / 80.62와 80.94 상회 종가 및 후속 80.62–80.94 지지를 확인한다. 새 가격과 저항을 갱신하고 구조적 손절 및 예상 비용 차감 후 최소 2:1 보상·위험 비율이 확보되는 경우에만 소액 진입 가능성을 별도로 재심사한다.","risk_condition_ko":"78.63 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T10:24:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"INTC","display_name":"INTC","is_held":false,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":65.815,"market_data_asof":"2026-10-30T14:22:01+00:00","session_vwap":66.19555239742088,"relative_volume":7.199616754383741,"spread_bps":1.5194104687367478,"day_high":68.77,"day_low":64.12,"execution_condition_ko":"위험 대응 조건: 84.65 이하 하락, 장중 확인 시 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"84.65 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"지금 실행 검토 가능","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":true,"action_status":"ACTION_SIGNAL_PRESENT","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T14:24:01+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":236.32,"market_data_asof":"2026-10-30T14:22:01+00:00","session_vwap":235.25926884533303,"relative_volume":0.8769086985916151,"spread_bps":3.38581344167869,"day_high":236.46,"day_low":233.2224,"execution_condition_ko":"227.31–227.63 시험과 227.63 이상 종가 후 다음 확인된 정규장에서 해당 구간의 지지와 실행 가능한 가격을 확인한다. 현재 충족된 매수 신호는 없다. / 234.08 초과 종가와 다음 정규장 233.74–234.08 지지는 신규 판단을 요청하는 조건이며 자동 돌파 매수 신호가 아니다.","risk_condition_ko":"227 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T14:24:01+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":294.8475,"market_data_asof":"2026-10-30T14:22:01+00:00","session_vwap":295.17803855968486,"relative_volume":0.990736302421306,"spread_bps":12.556205989649769,"day_high":298.74,"day_low":291.01,"execution_condition_ko":"공식 발표시각과 실적·가이던스 원문을 확보한다. 결과가 없다는 사실을 실적 부진으로 해석하지 않는다. 중대한 재무 문제가 미해결이면 매수는 계속 보류한다. / 가격은 미국 달러 기준이다. 그러나 재무제표 표시통화·금액 단위·회계기간·주당이익의 주식 기준, 예탁증서 해당 여부와 교환비율은 1차 출처로 확인되지 않았다. 검증 전 재무금액·주당이익 비교는 하지 않는다. 보수 분석가의 잠정 현금배당·유동성 수치도 확정적 부실 근거로 사용하지 않는다.","risk_condition_ko":"283.82 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T14:24:01+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":412.695,"market_data_asof":"2026-10-30T14:22:01+00:00","session_vwap":413.64674500054593,"relative_volume":0.7127269349451563,"spread_bps":3.877096055053993,"day_high":416.99,"day_low":411.82,"execution_condition_ko":"401.87~403.72 접촉 후 403.72 이상 종가 회복, 다음 완료된 거래세션 401.87 이상 종가 유지, 이후 진입 구간 재시험의 순차 확인 / 최신 실적·전망·중요 공시 원문 검토와 실제 비용 반영 보상/위험 1.5배 이상, 계좌·집중·손실 한도 확인","risk_condition_ko":"401.87 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T14:24:01+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":634.94,"market_data_asof":"2026-10-30T14:22:01+00:00","session_vwap":638.4012345124125,"relative_volume":0.7919314608227871,"spread_bps":5.670541536716972,"day_high":644.21,"day_low":633.41,"execution_condition_ko":"2026-11-06T23:59:59-05:00까지 원문 기본 검증, 재시험 종가 확인, 다음 실제 정규장 진입 조건이 모두 완성돼야 한다. 기한은 자체 재검토 시점이며 거래소 장마감 시각이 아니다. 조건 미충족 시 자동 연장하지 않는다. / 641.57 종가 돌파와 다음 실제 거래일 유지를 관찰하되 신고가만으로 탄력 회복이나 증액을 승인하지 않는다.","risk_condition_ko":"633.21 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T14:24:01+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":187.77,"market_data_asof":"2026-10-30T14:22:01+00:00","session_vwap":187.48515073354554,"relative_volume":1.1191464011293453,"spread_bps":4.793225574521525,"day_high":188.5,"day_low":185.875,"execution_condition_ko":"179.77–180.94 시험 후 180.94 초과 회복 종가가 나오면 다중 정규장 확인 절차를 시작한다. 단순 가격 접촉은 매수 신호가 아니다. / 다음 실제 정규장에서 179.77–180.25 재시험과 종가 기준 179.77 유지가 확인되면, 그 다음 정규장의 같은 가격 범위에서만 소규모 진입을 검토한다. 공식 발표·계좌·보상 대비 위험 검토가 통과되어야 한다.","risk_condition_ko":"179.77 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T14:24:01+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"EQIX","display_name":"EQIX","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1007.6,"market_data_asof":"2026-10-30T10:22:00-04:00","session_vwap":1020.8826241791721,"relative_volume":0.6572657098702794,"spread_bps":17.181021426620834,"day_high":1039.16,"day_low":1006.64,"execution_condition_ko":"2026-10-30부터 2026-11-06까지 새로운 1023~1026 시험, 종가 1026 이상, 다음 검증된 거래일의 지지 재시험을 순차적으로 관찰한다. / 1047~1052 및 1057~1068.33의 공급을 점검한다. 이후 1079~1104는 기술적 저항 범위이지 적정가치가 아니다.","risk_condition_ko":"1,023 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T10:24:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":97.13,"market_data_asof":"2026-10-30T14:22:01+00:00","session_vwap":97.29648152816947,"relative_volume":0.12121447607180652,"spread_bps":5.148535241723437,"day_high":98.09,"day_low":96.87,"execution_condition_ko":"반등 확인 종가와 다음 정규장 지지, 94.61~94.88 범위 및 비용 후 보상·위험비 1.8을 함께 점검한다. 단순 가격 도달은 매수 신호가 아니다. / 95.17 재확보와 97.20 위 종가는 추세 관찰 신호다. 이를 더 낮은 매수 상한을 우회하는 허가로 사용하지 않는다.","risk_condition_ko":"94.01 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T14:24:01+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1011.265,"market_data_asof":"2026-10-30T14:22:01+00:00","session_vwap":1012.0324957006084,"relative_volume":1.1025743195312363,"spread_bps":5.043188481752962,"day_high":1016.63,"day_low":1008.14,"execution_condition_ko":"2026-10-30T07:31:09.339357-04:00 기준 만료 시각은 아직 미래다. 다만 이 시계는 개장 여부, 실제 거래일, 시세 신선도 또는 진입 조건 충족을 입증하지 않는다. / 모든 확인과 체결은 2026-11-06T17:00:00-05:00 이전에 끝나야 한다. 이는 관리자가 정한 검토 기한이지 검증된 거래소 폐장 시각이 아니다. 조건 미완료분은 자동 이월하지 않는다.","risk_condition_ko":"980.32 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T14:24:01+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":163.35,"market_data_asof":"2026-10-30T14:22:01+00:00","session_vwap":164.04083766114186,"relative_volume":1.0580793701572873,"spread_bps":3.060631102132216,"day_high":165.35,"day_low":162.74,"execution_condition_ko":"158.35–158.45 시험과 158.50 이상 종가, 차기 정규장 지지 유지·회복, 공식 전망·조달 점검을 모두 통과해야 최대 0.625%의 최초 진입을 검토한다. / 160.95–161.60은 첫 저항, 164.50–165.75는 상단 저항과 이익실현 재검토 구간이다. 지연된 장전 표시 163.68은 정규장 돌파나 진입 충족을 입증하지 않는다.","risk_condition_ko":"157.4 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T14:24:01+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"UNH","display_name":"UNH","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":408.3901,"market_data_asof":"2026-10-30T14:22:01+00:00","session_vwap":412.312535311246,"relative_volume":0.42179402127584575,"spread_bps":11.012811570793744,"day_high":416.11,"day_low":408.3901,"execution_condition_ko":"매수 준비: 새 일봉의 404.31~408.51 지지와 408.51 이상 종가를 확인한다. 실제 소액 진입은 다음 확인된 거래 세션의 재시험, 중요 공시 점검, 비용 반영 최소 2의 손익비 및 계좌 위험 확인까지 필요하다. / 첫 저항 414.76~416.19에서는 회복 유지 여부를 평가한다. 지지가 유지되면 소액 물량을 보유하되 자동 추가 매수하지 않으며, 새 회복이 종가 414.76 미만으로 실패하면 그 회복에 근거한 추가분을 축소한다.","risk_condition_ko":"403.25 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T14:24:01+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"RTX","display_name":"RTX","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":200.04,"market_data_asof":"2026-10-30T14:22:01+00:00","session_vwap":201.58356207783336,"relative_volume":0.5399566926693649,"spread_bps":9.495489642419738,"day_high":204.21,"day_low":199.69,"execution_condition_ko":"194~195 지지 접촉과 종가 195 이상 회복 후 다음 확인 거래일 재시험을 관찰한다. 실제 매수는 194~194.66 중 비용 후 보상/위험 2배를 충족하는 가격에만 제한하며, 유효 가격대가 없어지면 거래를 생략한다. / 197.75~198.75는 최근 회복의 첫 지지 관찰 범위다. 유지 자체는 신규 매수 신호가 아니다.","risk_condition_ko":"194 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T14:24:01+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":545.59,"market_data_asof":"2026-10-30T14:22:01+00:00","session_vwap":546.5756581235878,"relative_volume":0.568213847904424,"spread_bps":7.1494697476622155,"day_high":550.3,"day_low":544.3971,"execution_condition_ko":"538.48–539.23 시험과 539.23 이상 종가 이후 다음 확인된 정규장의 지지 유지 여부를 점검한다. 매수가격은 해당 범위로 제한한다. / 549.96 초과 종가와 548.77–549.96 재시험 성공은 새로운 추가 편입 판단을 요청하는 관찰 조건이다.","risk_condition_ko":"532.02 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T14:24:01+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"RHHBY","display_name":"RHHBY","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":60.93000030517578,"market_data_asof":"2026-10-30T10:07:00-04:00","session_vwap":61.24717796418808,"relative_volume":0.1596348059552639,"spread_bps":null,"day_high":61.43000030517578,"day_low":60.93000030517578,"execution_condition_ko":"59.26-59.70 일봉 안정 이후 다음 실제 거래일 지지 유지와 59.26-59.29의 비용 적격 체결 가능성을 관찰한다. 61.03이 최종 청산 장애물이 되는지 반드시 재평가한다. / 61.49 상향 종가와 갱신된 20일 평균 대비 최소 1.5배 일간 거래량을 돌파 재심사 조건으로 본다. 과거 평균 기준 약 2200000주는 참고치일 뿐이다.","risk_condition_ko":"59.26 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-30T10:07:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T10:09:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SPG","display_name":"Simon Property Group","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":216.85,"market_data_asof":"2026-10-30T10:22:00-04:00","session_vwap":216.57661503045418,"relative_volume":0.24672646246285979,"spread_bps":16.13907269499432,"day_high":218.4,"day_low":215.37,"execution_condition_ko":"약 1주 동안 210.05~210.49 시험, 211 상회 종가, 다음 거래일 210.50~211.00 지지 유지 순서를 추적한다. 가격이 범위에 들어온 사실만으로 매수하지 않는다. / 213.50~213.75 이탈은 돌파 추격 경로를 취소한다. 재탈환 실패와 하방위험 증가가 확인되면 조기 비중 축소를 검토하며, 별도의 하단 지지 반전 확인을 생략하지 않는다.","risk_condition_ko":"210 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T10:24:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":210.135,"market_data_asof":"2026-10-30T14:22:01+00:00","session_vwap":211.6558089194091,"relative_volume":0.4345394569144662,"spread_bps":13.323182337266898,"day_high":214.35,"day_low":210.0661,"execution_condition_ko":"다음 1–2개 적격 거래일과 이후 관련 완료 일봉마다 회복·지지·가격 조건을 점검하고, 늦어도 2026-11-06T22:00:00+00:00 전에 재심사한다. / 신규 편입 전에 2026-10-21 및 2026-10-23 공시의 원문과 공개시각을 확인하고 중요한 가이던스·자금조달·규제·배당 위험을 검토한다. 완전한 장기 확실성까지 요구하지 않되 중요한 미해결 상충은 진입을 막는다.","risk_condition_ko":"201.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-30T14:24:01+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-30T23:15:25.307647+09:00",
  "as_of": "2026-10-30T09:52:00-04:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
