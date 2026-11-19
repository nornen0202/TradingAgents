# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-19T18:45:06.695230+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261120T010229_local-scheduler-us-overlay_only",
  "producer_finished_at": "2026-11-20T01:49:24.456872+09:00",
  "analysis_run_id": "20261119T175051_local-scheduler-us-full",
  "analysis_completed_at": "2026-11-19T19:49:04.465545+09:00",
  "analysis_trade_date_oldest": "2026-11-18",
  "analysis_trade_date_latest": "2026-11-18",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-20T01:45:21+09:00",
  "market_data_latest_at": "2026-11-19T16:45:23+00:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-20T01:49:12.707868+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-20T01:49:12.707868+09:00",
    "run_started_at": "2026-11-20T01:02:29.022093+09:00",
    "run_finished_at": "2026-11-20T01:49:24.456872+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23489417,
    "total_market_value_krw": 21280076,
    "total_unrealized_pnl_krw": -2209341,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 111905,
    "total_equity_krw": 22368633
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 542649,
      "current_price_krw": 484334,
      "market_value_krw": 5812008,
      "unrealized_pnl_krw": -699786
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 290852,
      "current_price_krw": 284935,
      "market_value_krw": 3134287,
      "unrealized_pnl_krw": -65090
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 421863,
      "current_price_krw": 385187,
      "market_value_krw": 2311122,
      "unrealized_pnl_krw": -220061
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1869849,
      "current_price_krw": 1799793,
      "market_value_krw": 1799793,
      "unrealized_pnl_krw": -70056
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 552935,
      "current_price_krw": 455036,
      "market_value_krw": 1365109,
      "unrealized_pnl_krw": -293698
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 265802,
      "current_price_krw": 203684,
      "market_value_krw": 1222109,
      "unrealized_pnl_krw": -372707
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 133790,
      "current_price_krw": 133915,
      "market_value_krw": 1205237,
      "unrealized_pnl_krw": 1120
    },
    {
      "ticker": "GEV",
      "name": "GE 버노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1464928,
      "current_price_krw": 1043083,
      "market_value_krw": 1043083,
      "unrealized_pnl_krw": -421845
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 362609,
      "current_price_krw": 465845,
      "market_value_krw": 931690,
      "unrealized_pnl_krw": 206471
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1412312,
      "current_price_krw": 1815125,
      "market_value_krw": 791512,
      "unrealized_pnl_krw": 175652
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 566549,
      "current_price_krw": 481245,
      "market_value_krw": 481245,
      "unrealized_pnl_krw": -85304
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 659167,
      "current_price_krw": 434684,
      "market_value_krw": 434684,
      "unrealized_pnl_krw": -224483
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 135477,
      "current_price_krw": 97110,
      "market_value_krw": 388441,
      "unrealized_pnl_krw": -153467
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 345873,
      "current_price_krw": 359756,
      "market_value_krw": 359756,
      "unrealized_pnl_krw": 13883
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":782.25,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":788.4572364005707,"relative_volume":0.4606296442571437,"spread_bps":21.708594049291857,"day_high":806.49,"day_low":775.785,"execution_condition_ko":"위험 대응 조건: 747 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"747 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":341.485,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":342.9010617036169,"relative_volume":0.5232932266460155,"spread_bps":18.151477003249834,"day_high":347.2,"day_low":337.21,"execution_condition_ko":"위험 대응 조건: 331.27 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"331.27 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1349.76,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":1354.6563585612646,"relative_volume":0.32784103395191383,"spread_bps":36.00106669827348,"day_high":1378.06,"day_low":1322.14,"execution_condition_ko":"1327.65 미국 달러 회복과 1355.00 돌파를 정규장 종가로 관찰한다. 둘 다 단독 매수 신호가 아니다. / 1398.67 상회 마감 뒤 다음 확인된 정규장에서 1390.00~1398.67 재시험과 1390.00 이상 마감을 확인한다. 재시험이 없거나 가격이 구간을 벗어나면 추격하지 않는다.","risk_condition_ko":"1,280 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":349.855,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":350.9191228415102,"relative_volume":0.62963513240792,"spread_bps":2.286628937288746,"day_high":355.28,"day_low":347.5,"execution_condition_ko":"349.67~351.47달러 시험 후 351.47달러 위 종가와 다음 거래일 지지·상회 종가를 확인한다. 349.67달러 아래로 마감하면 매수 대신 346.79달러를 관찰한다. / 360.83달러 위 종가 뒤 다음 거래일 지지 또는 재돌파를 관찰한다. 거래량 개선은 보강 근거일 뿐 추격 매수 조건이 아니다.","risk_condition_ko":"340.92 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":363.02,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":367.2743466533237,"relative_volume":0.7675626351293273,"spread_bps":4.131150249935529,"day_high":374.7705,"day_low":360.12,"execution_condition_ko":"368.85~373.10달러 돌파와 373.10달러 지지는 관찰만 한다. 373.10달러에서 다음 저항 384.11~385.47달러까지는 11.01~12.37달러인 반면 하단 지지 351.19달러까지는 21.91달러다. / 11월 18일은 최신 완료 일봉이다. 11월 19일 04:35 미국 동부시간의 장전 관측값 362.31달러는 제공 당시 245초 지연됐다. 11월 19일 04:50:21 미국 동부시간 기준 검토 시한은 지나지 않았지만, 실제 거래일·조기 종료 일정, 거래정지 여부, 현재 호가와 진입 조건 충족 여부는 별도로 확인해야 한다.","risk_condition_ko":"351.19 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":213.93,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":214.10341845631007,"relative_volume":0.6450028748566271,"spread_bps":0.9348852428369201,"day_high":216.25,"day_low":213.16,"execution_condition_ko":"216.89달러는 반등 진단선으로만 본다. 218.93~219.32달러, 221.82~222.93달러, 223.45~224.20달러에서 후속 수요를 점검한다. / 독립 자료로 11월 상승 종목 비율, RSP 순유출입, VOO 대비 상대수익률과 편입 기업 이익 추정치를 확인한다. 운용사 원문에서 보유 비중, 순자산가치 괴리, 추적 성과와 보수를 확인한다. 보도상 연 보수는 RSP 0.20%, VOO 0.03%로 원문은 미확인이다.","risk_condition_ko":"214.28 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":269.87,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":270.74686426969606,"relative_volume":0.7099115046618617,"spread_bps":2.9640607632450573,"day_high":274.0,"day_low":267.13,"execution_condition_ko":"AMZN: 255.12~258.85달러 눌림 후 258.85달러 이상 정규장 종가와 다음 검증 정규 거래일의 같은 수준 이상 종가를 확인한다. 두 종가는 주문 신호가 아니라 최신 호가에서 손익비를 재평가할 조건이다. / AMZN: 270.87달러 회복은 예비 신호다. 275.60달러 초과 종가와 275.34~275.60달러 재시험을 관찰하되, 확인된 상방 목표가 없어 이번 조건부 매수에는 포함하지 않는다.","risk_condition_ko":"254 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.6002,"market_data_asof":"2026-11-20T01:45:21+09:00","market_data_clock_status":null,"session_vwap":100.60450425691963,"relative_volume":1.0409862621809003,"spread_bps":0.9939863823870698,"day_high":100.61,"day_low":100.6,"execution_condition_ko":"분배락이 아닌 정규장에서 100.58~100.59달러 시험 후 100.58달러 이상 마감하는지 확인한다. 1차 후보가 취소되면 전체 무효화 조건에 걸리지 않은 경우에만 100.52~100.54달러의 별도 안정 신호를 관찰한다. / 100.61달러 초과 종가와 다음 실제 정규장의 유지 여부는 관찰만 한다. 11월 18일 거래량은 20일 평균보다 약 2% 많았고 상승 탄력도 둔화했다. 지연된 장전 가격 접촉은 돌파 확인이 아니다.","risk_condition_ko":"100.52 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T01:45:21+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T01:48:21+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1361.02,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":1361.544525559877,"relative_volume":0.7621800743701999,"spread_bps":14.841482678814018,"day_high":1381.9999,"day_low":1341.46,"execution_condition_ko":"1380.00–1380.34 지지 회복, 1410.27 상회 종가, 다음 정규장의 1405.00–1410.27 재시험을 순서대로 확인한다. 1423.11–1432.28과 1458.23–1475.25에서는 남은 상승 여력을 재평가한다. / 2026년 11월 19일 미국 동부시간 04:34:57 기준 계획 만료 시각은 지나지 않았다. 정규장 일정과 휴장·조기 마감 여부, 거래정지, 최신 실행 호가, 진입 조건 충족은 미확인이다. 기존 10:30 표기는 장중 진입 허용 시각이 아니다.","risk_condition_ko":"1,380 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":360.92,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":362.0752768867504,"relative_volume":0.7246679126690427,"spread_bps":3.878223773511354,"day_high":369.26,"day_low":352.81,"execution_condition_ko":"340.74~344.06달러 시험 후 344.06달러 이상 종가와 다음 실제 거래일 종가 지지를 확인한다. 계약 위험과 순손익비가 개선되지 않으면 관찰에 그친다. / 357.34~358.47달러 돌파는 관찰만 한다. 다음 저항 366.74~369.82달러까지 약 8~12달러로 평균 실제 변동폭 17.57달러보다 짧다. 369.82달러 상회 종가와 다음 거래일 지지는 증액 재평가 조건이지 자동 매수가 아니다.","risk_condition_ko":"340.74 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":152.825,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":154.5721437368894,"relative_volume":1.042331837755174,"spread_bps":1.308643590918683,"day_high":158.1301,"day_low":151.48,"execution_condition_ko":"153.84달러 회복은 지연 장전 고점 회복을 관찰하는 신호일 뿐 매수 신호가 아니다. 158.19~159.70달러 저항대 돌파와 지지 전환을 우선 확인하고, 이후 163.20달러 및 170.00~171.30달러 저항을 본다. / 2026-11-19 04:36:02 미 동부시간 기준 계획은 미만료다. 실제 정규장 일정, 거래정지 여부, 시세의 최신성 및 진입 조건 충족 여부는 미확인이다. 기존안의 10:30 표기는 일중 선행 매수 금지와 상충하므로 개시 시각으로 적용하지 않는다.","risk_condition_ko":"150.33 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":325.8951,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":327.4035160962185,"relative_volume":0.6763574030145528,"spread_bps":29.450562935238807,"day_high":336.32,"day_low":316.11,"execution_condition_ko":"305.80~308.93달러: 최근 지지대다. 하단 아래 정규장 종가가 확정되면 보유 위험을 추가로 줄인다. / 329.25~332.36달러: 종가 회복과 다음 확인된 정규장 지지는 단기 반등 관찰 신호일 뿐 매수 신호가 아니다.","risk_condition_ko":"305.8 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":288.56,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":291.64793123050526,"relative_volume":0.7196348873103428,"spread_bps":1.7328319672845267,"day_high":295.43,"day_low":287.7,"execution_condition_ko":"276.92~279.69달러를 시험한 뒤 279.69달러 위에서 정규장 마감하고 다음 확인된 거래일에도 지지를 지키면, 실제 후보가에서 첫 저항 하단 296.33달러까지의 순손익비를 다시 계산한다. / 291.10달러는 관찰선이다. 296.49달러 위에서 정규장 마감하고 다음 확인된 거래일에 296.33~296.49달러가 지지로 바뀌면, 다음 저항 302.56~304.97달러까지의 보상을 재평가한다. 두 가격 경로 모두 주문 신호는 아니다.","risk_condition_ko":"276.92 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":72.93,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":73.0179761711516,"relative_volume":1.4153830925017954,"spread_bps":1.3708958804585807,"day_high":73.49,"day_low":72.56,"execution_condition_ko":"74.76달러 위 정규장 종가와 다음 거래일 지지는 반등 관찰 신호일 뿐이다. 81.50달러는 2026-11-18 기준 하락 중인 50일 이동평균으로, 목표가가 아니며 재평가 때 갱신한다. / 동시점 GLDM 시장가격과 공식 주당 순자산가치를 대조한다. 78.13달러 회복 후에도 금 현물 반등을 순설정·실질금리·달러 중 적어도 하나가 뒷받침하는지 확인하고, 새 지지·저항과 실제 거래비용으로 보상/위험을 다시 계산한다.","risk_condition_ko":"75.96 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":282.36,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":282.1242238169219,"relative_volume":0.5591662527891342,"spread_bps":4.2498937526563445,"day_high":286.0488,"day_low":279.9,"execution_condition_ko":"2026-11-19T05:15:55.817292-05:00 기준 계획은 만료되지 않았으나 거래소 일정·정규장 거래 가능 상태·진입 조건은 미확인이다. 04:50 개장 전 관측은 약 14분 29초 지연됐고 호가 차이가 약 1.78%였다. 저가 283.06달러를 정규장 지지 이탈이나 주문 근거로 쓰지 않는다. / 283.12~284.91달러 지지 방어를 우선 확인한다. 이후 292.10~292.55달러 회복과 지지 전환, 294.50~295.46달러 저항 돌파 여부, 돌파 시 300.42~302.93달러 고점 재시험을 본다.","risk_condition_ko":"283.12 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GE","display_name":"GE","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":324.07,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":326.26656576139777,"relative_volume":0.35878285742770893,"spread_bps":9.874714559033821,"day_high":330.0,"day_low":323.62,"execution_condition_ko":"323.28~325.00달러 재시험, 325.00달러 초과 종가 회복, 다음 실제 정규장의 지지 유지와 체결 가능 가격을 차례로 확인한다. / 331.71~333.48달러의 첫 저항과 342.90~343.59달러의 박스권 상단 반응을 확인한다. 343.59달러 위 종가가 나와도 다음 정규장 지지와 거래량만 점검한다. 351.43달러까지의 7.84달러는 평균진폭 9.98달러보다 짧아 추격하지 않는다.","risk_condition_ko":"323.28 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1085.76,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":1088.3302080707401,"relative_volume":0.5880795934432598,"spread_bps":3.7760350710777066,"day_high":1094.54,"day_low":1083.16,"execution_condition_ko":"1,083.89~1,096.01달러 지지 시험 후 1,096.01달러 위 정규장 종가 회복과 다음 실제 정규장 재시험 지지를 확인한다. / 1,123.67달러 위 정규장 종가에 평소보다 강한 거래량이 동반되고 다음 실제 정규장에서도 지지되면 돌파를 별도로 재평가한다. 자동 매수는 아니다.","risk_condition_ko":"1,083.89 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"KO","display_name":"KO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":95.705,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":95.5022635037396,"relative_volume":0.8205902548240073,"spread_bps":1.0448774881135683,"day_high":96.68,"day_low":94.73,"execution_condition_ko":"96.63~97.16달러 시험 후 97.16달러 위 종가 회복과 다음 실제 정규장 지지 확인. 실행 전 거래소 일정·개장 및 거래정지 여부, 최신 체결 가능 호가와 새 중요 공시를 확인한다. / 98.87~99.61달러는 보유 위험과 손익비를 재평가할 첫 저항이지 자동 익절 구간이 아니다. 100.56달러 위 종가, 거래 참여 개선과 다음 정규장 지지 전환은 별도 관찰 신호이며 이번 매수에 포함하지 않는다.","risk_condition_ko":"96.63 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WELL","display_name":"WELL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":246.645,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":245.71035633664326,"relative_volume":0.6381884333259074,"spread_bps":8.108984755109352,"day_high":247.25,"day_low":244.57,"execution_condition_ko":"11월 18일 회복에 이어 다음 실제 정규장에서 243.68달러 재시험과 그 이상 종가를 확인한다. 이후 거래 가능한 정규장에서 243.68~243.90달러에 체결할 수 있고 비용 차감 손익비와 위험 여력이 충족될 때만 첫 진입을 검토한다. / 249.75달러를 웃도는 종가와 다음 정규장 지지는 관찰 신호일 뿐이다. 251.12~253.37달러 저항대와 254.42달러 변동성 참고치까지 여력을 다시 계산하되 자동 매수하지 않는다.","risk_condition_ko":"241.52 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WMT","display_name":"WMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":125.64,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":125.28041816234804,"relative_volume":1.1538349250255227,"spread_bps":3.1836994587704583,"day_high":126.22,"day_low":123.29,"execution_condition_ko":"$126.60 회복은 관찰 신호다. 신규 매수 판단은 공식 실적 확인 후 $126.99~$127.36 재시험에서 따로 내린다. / $127.77~$127.78에서 재차 밀리면 신규 매수를 보류한다. $129.85 위 종가와 다음 실제 거래일 지지가 확인되면 $131.82까지의 순손익비를 다시 계산한다.","risk_condition_ko":"125.07 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":568.45,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":568.8655091154071,"relative_volume":0.488161252533178,"spread_bps":3.518339343828512,"day_high":573.13,"day_low":567.1,"execution_condition_ko":"570.89–573.09달러 지지, 574.82달러 종가 회복, 다음 정규장의 지지 재확인을 순서대로 본다. 거래소 일정, 거래정지 여부, 최신 체결 가능 호가는 별도로 확인한다. / 586.45달러를 상회하는 종가에 거래 참여가 강화되고 이후 583.72–586.45달러가 지지되면 추가 매수를 별도로 검토한다. 592.94–596.92달러까지의 비용 차감 후 보상과 애플·알파벳 중복 노출을 다시 따진다.","risk_condition_ko":"570.89 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LIN","display_name":"LIN","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":512.77,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":512.7057467880132,"relative_volume":0.7773319844901667,"spread_bps":9.93929236136131,"day_high":515.92,"day_low":510.34,"execution_condition_ko":"508.00~510.01달러 시험과 510.01달러 위 정규장 종가에 이어 다음 실제 정규장에서 510.01달러 재시험이 유지되는지 확인한다. / 519.56달러 위 정규장 종가와 다음 정규장 재시험 안착은 별도로 관찰한다. 다음 저항 하단 525.30달러까지 5.74달러에 불과해 추격하지 않는다.","risk_condition_ko":"508 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.525,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":100.63624592744922,"relative_volume":0.3844466763748028,"spread_bps":3.9793076004781387,"day_high":101.5,"day_low":100.0,"execution_condition_ko":"11월 19일 04:50 미국 동부시간의 100.27달러 관측은 지연된 100주 자료이며 호가 차이는 약 2.60%였다. 거래 상태와 정규장 호가가 미확인이라 지지나 체결 신호로 쓰지 않는다. / 실적 검토 후 101.44~101.60달러 회복·재시험과 103.34~104.49달러의 첫 저항 소화 여부를 본다. 다음 저항은 105.72~106.20달러다.","risk_condition_ko":"99.59 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AES","display_name":"AES","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":15.02,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":15.02462517703271,"relative_volume":3.370995249592135,"spread_bps":6.65557404326109,"day_high":15.04,"day_low":15.02,"execution_condition_ko":"실제 정규장 개장과 거래 가능 여부를 확인하고, $15.03 초과 종가 뒤 다음 정규장의 $15.00~$15.03 재시험과 $15.00 이상 종가를 점검한다. / 공식 거래 문서와 신선한 매수·매도 가능 호가가 확보되면 정상 종결·지연·무산 시나리오별 순보상과 기존 보유분의 스트레스 손실을 다시 계산한다.","risk_condition_ko":"14.94 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SO","display_name":"SO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":92.495,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":92.9946206674952,"relative_volume":0.3575652256641991,"spread_bps":4.324791869391961,"day_high":94.24,"day_low":92.425,"execution_condition_ko":"93.13~93.15달러 시험 후 93.15달러 위 종가와 다음 거래일 지지 유지를 먼저 본다. 돌파는 94.94달러 위 종가와 94.77~94.94달러 지지 전환을 본다. 확인이 끝난 뒤 가격이 비용 반영 상한을 넘으면 매수하지 않는다. / 기사 17건에서 목표주가 상향과 하향은 각각 3건이다. 전용 소셜·투자자 포지셔닝, 금리·물가 및 동종사 비교 자료는 없다. 거시 자료는 주가지수 선물 보도 1건으로, 금리 방향이나 유틸리티로의 자금 이동을 확인할 수 없다.","risk_condition_ko":"90.8 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":168.11,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":167.84184339321163,"relative_volume":0.3601854438400089,"spread_bps":2.379252914584347,"day_high":168.665,"day_low":166.888,"execution_condition_ko":"투자자의 날 발표가 판매량·점유율 방어와 비용 상쇄의 구체적 근거를 제시하는지 확인한다. / 발표 기준 충족 후 168.62~168.80달러 지지와 170.29달러 이상 새 일봉 마감, 이어 다음 정규장의 168.80~169.66달러 재시험을 순서대로 확인한다. 재시험이 없거나 169.66달러를 넘으면 추격하지 않는다.","risk_condition_ko":"167.2 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":403.7,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":406.89324918118785,"relative_volume":0.8679139389709231,"spread_bps":3.468351294439321,"day_high":413.51,"day_low":402.515,"execution_condition_ko":"411.83~411.99달러 지지 시험과 회복, 422.79달러 위 정규장 종가, 다음 실제 정규장의 420.05~422.79달러 재시험 및 420.05달러 이상 마감을 순서대로 확인한다. / 425.99~430.99달러 저항에서는 추격하지 않는다. 430.99달러 위 종가와 다음 정규장 지지가 확인되면 435.95~441.41달러를 다음 저항으로 본다.","risk_condition_ko":"411.83 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NKE","display_name":"NKE","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":34.475,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":34.95382100506594,"relative_volume":0.7886575724338588,"spread_bps":2.900652646844964,"day_high":36.0,"day_low":34.41,"execution_condition_ko":"36.82~36.88달러 회복은 관찰 신호다. 다음 확인 거래일의 지지 여부와 첫 저항 37.62~37.79달러를 확인한다. 38.71달러 위 종가가 나와도 40.44~41.10달러 저항과 하락 중인 200일선 43.84달러를 감안해 추격하지 않는다. / 36.02달러 회복 여부와 34.96달러 지지를 우선 점검한다. 2026-11-25까지 가격 계획을 재검토한다. 이 날짜는 주문 만료일이 아니다.","risk_condition_ko":"34.96 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":630.7,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":633.4488067298313,"relative_volume":0.5478170979562762,"spread_bps":4.915446393886757,"day_high":641.0,"day_low":629.455,"execution_condition_ko":"거래 참여가 개선되며 654.41달러 위에서 마감한 뒤 651.10~654.41달러가 다음 확인 거래일에 지지로 바뀌는지 본다. 새로 확인된 지지를 근거로 비용 반영 보상 대 위험이 1.5배 이상이 되기 전에는 신규 배정을 0으로 유지한다. 손절을 임의로 당기거나 첫 저항을 건너뛰지 않는다. / 636.39~638.01달러 지지 방어를 점검하고, 하단 종가 이탈 시 633.30달러 부근의 반응을 살핀다. 기존 노출은 갭을 반영해 계좌·종목 한도와 대조한다.","risk_condition_ko":"636.39 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MRVL","display_name":"Marvell Technology","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":148.61,"market_data_asof":"2026-11-19T16:45:23+00:00","market_data_clock_status":null,"session_vwap":150.3444826240173,"relative_volume":0.6249603862567353,"spread_bps":6.05999394000629,"day_high":154.5146,"day_low":145.11,"execution_condition_ko":"위험 대응 조건: 140.9 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"140.9 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-19T16:45:23+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T16:48:23+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-20T03:14:28.568216+09:00",
  "as_of": "2026-11-20T01:45:21+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
