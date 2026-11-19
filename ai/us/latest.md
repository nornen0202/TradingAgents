# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-19T16:49:43.177061+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261120T000256_local-scheduler-us-overlay_only",
  "producer_finished_at": "2026-11-20T00:37:58.659835+09:00",
  "analysis_run_id": "20261119T175051_local-scheduler-us-full",
  "analysis_completed_at": "2026-11-19T19:49:04.465545+09:00",
  "analysis_trade_date_oldest": "2026-11-18",
  "analysis_trade_date_latest": "2026-11-18",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-19T10:36:00-05:00",
  "market_data_latest_at": "2026-11-19T10:36:00-05:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-20T00:37:50.621088+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-20T00:37:50.621088+09:00",
    "run_started_at": "2026-11-20T00:02:56.122077+09:00",
    "run_finished_at": "2026-11-20T00:37:58.659835+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23489417,
    "total_market_value_krw": 21141620,
    "total_unrealized_pnl_krw": -2347797,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 111905,
    "total_equity_krw": 22228664
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 542649,
      "current_price_krw": 481871,
      "market_value_krw": 5782458,
      "unrealized_pnl_krw": -729336
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 290852,
      "current_price_krw": 284083,
      "market_value_krw": 3124916,
      "unrealized_pnl_krw": -74461
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 421863,
      "current_price_krw": 384062,
      "market_value_krw": 2304373,
      "unrealized_pnl_krw": -226810
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1869849,
      "current_price_krw": 1775474,
      "market_value_krw": 1775474,
      "unrealized_pnl_krw": -94375
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 552935,
      "current_price_krw": 449712,
      "market_value_krw": 1349136,
      "unrealized_pnl_krw": -309671
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 265802,
      "current_price_krw": 202014,
      "market_value_krw": 1212087,
      "unrealized_pnl_krw": -382729
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
      "current_price_krw": 1035728,
      "market_value_krw": 1035728,
      "unrealized_pnl_krw": -429200
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 362609,
      "current_price_krw": 463861,
      "market_value_krw": 927723,
      "unrealized_pnl_krw": 202504
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1412312,
      "current_price_krw": 1799727,
      "market_value_krw": 784798,
      "unrealized_pnl_krw": 168938
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 566549,
      "current_price_krw": 471768,
      "market_value_krw": 471768,
      "unrealized_pnl_krw": -94781
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 659167,
      "current_price_krw": 423476,
      "market_value_krw": 423476,
      "unrealized_pnl_krw": -235691
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 135477,
      "current_price_krw": 96997,
      "market_value_krw": 387991,
      "unrealized_pnl_krw": -153917
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 345873,
      "current_price_krw": 356455,
      "market_value_krw": 356455,
      "unrealized_pnl_krw": 10582
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":779.96,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":791.8428372739917,"relative_volume":0.5784679109858272,"spread_bps":7.437613808315265,"day_high":806.49,"day_low":778.37,"execution_condition_ko":"위험 대응 조건: 747 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"747 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":338.67,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":344.1237925854714,"relative_volume":0.7524458602237851,"spread_bps":18.027869312724828,"day_high":347.2,"day_low":338.375,"execution_condition_ko":"위험 대응 조건: 331.27 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"331.27 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1337.13,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":1359.9088516797183,"relative_volume":0.4801945459357635,"spread_bps":29.328146042195467,"day_high":1378.06,"day_low":1332.11,"execution_condition_ko":"1327.65 미국 달러 회복과 1355.00 돌파를 정규장 종가로 관찰한다. 둘 다 단독 매수 신호가 아니다. / 1398.67 상회 마감 뒤 다음 확인된 정규장에서 1390.00~1398.67 재시험과 1390.00 이상 마감을 확인한다. 재시험이 없거나 가격이 구간을 벗어나면 추격하지 않는다.","risk_condition_ko":"1,280 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":362.415,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":369.4019922109151,"relative_volume":1.0849680347715764,"spread_bps":7.72584294465067,"day_high":374.7705,"day_low":361.6476,"execution_condition_ko":"368.85~373.10달러 돌파와 373.10달러 지지는 관찰만 한다. 373.10달러에서 다음 저항 384.11~385.47달러까지는 11.01~12.37달러인 반면 하단 지지 351.19달러까지는 21.91달러다. / 11월 18일은 최신 완료 일봉이다. 11월 19일 04:35 미국 동부시간의 장전 관측값 362.31달러는 제공 당시 245초 지연됐다. 11월 19일 04:50:21 미국 동부시간 기준 검토 시한은 지나지 않았지만, 실제 거래일·조기 종료 일정, 거래정지 여부, 현재 호가와 진입 조건 충족 여부는 별도로 확인해야 한다.","risk_condition_ko":"351.19 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":348.4,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":351.52721212033,"relative_volume":0.9485466651301718,"spread_bps":1.1481715368265577,"day_high":355.28,"day_low":348.18,"execution_condition_ko":"349.67~351.47달러 시험 후 351.47달러 위 종가와 다음 거래일 지지·상회 종가를 확인한다. 349.67달러 아래로 마감하면 매수 대신 346.79달러를 관찰한다. / 360.83달러 위 종가 뒤 다음 거래일 지지 또는 재돌파를 관찰한다. 거래량 개선은 보강 근거일 뿐 추격 매수 조건이 아니다.","risk_condition_ko":"340.92 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":213.6,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":214.7633539484503,"relative_volume":0.5974449822758432,"spread_bps":0.4681757531773171,"day_high":216.25,"day_low":213.58,"execution_condition_ko":"216.89달러는 반등 진단선으로만 본다. 218.93~219.32달러, 221.82~222.93달러, 223.45~224.20달러에서 후속 수요를 점검한다. / 독립 자료로 11월 상승 종목 비율, RSP 순유출입, VOO 대비 상대수익률과 편입 기업 이익 추정치를 확인한다. 운용사 원문에서 보유 비중, 순자산가치 괴리, 추적 성과와 보수를 확인한다. 보도상 연 보수는 RSP 0.20%, VOO 0.03%로 원문은 미확인이다.","risk_condition_ko":"214.28 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":267.4861,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":271.6420647021384,"relative_volume":0.9814836457193936,"spread_bps":5.233644859812574,"day_high":274.0,"day_low":267.26,"execution_condition_ko":"AMZN: 255.12~258.85달러 눌림 후 258.85달러 이상 정규장 종가와 다음 검증 정규 거래일의 같은 수준 이상 종가를 확인한다. 두 종가는 주문 신호가 아니라 최신 호가에서 손익비를 재평가할 조건이다. / AMZN: 270.87달러 회복은 예비 신호다. 275.60달러 초과 종가와 275.34~275.60달러 재시험을 관찰하되, 확인된 상방 목표가 없어 이번 조건부 매수에는 포함하지 않는다.","risk_condition_ko":"254 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.6099,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":100.60396537406943,"relative_volume":1.3041977695208635,"spread_bps":0.9939863823870698,"day_high":100.61,"day_low":100.6,"execution_condition_ko":"분배락이 아닌 정규장에서 100.58~100.59달러 시험 후 100.58달러 이상 마감하는지 확인한다. 1차 후보가 취소되면 전체 무효화 조건에 걸리지 않은 경우에만 100.52~100.54달러의 별도 안정 신호를 관찰한다. / 100.61달러 초과 종가와 다음 실제 정규장의 유지 여부는 관찰만 한다. 11월 18일 거래량은 20일 평균보다 약 2% 많았고 상승 탄력도 둔화했다. 지연된 장전 가격 접촉은 돌파 확인이 아니다.","risk_condition_ko":"100.52 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1353.01,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":1367.2583429089245,"relative_volume":1.0168681342740087,"spread_bps":4.876859302609725,"day_high":1381.9999,"day_low":1353.01,"execution_condition_ko":"1380.00–1380.34 지지 회복, 1410.27 상회 종가, 다음 정규장의 1405.00–1410.27 재시험을 순서대로 확인한다. 1423.11–1432.28과 1458.23–1475.25에서는 남은 상승 여력을 재평가한다. / 2026년 11월 19일 미국 동부시간 04:34:57 기준 계획 만료 시각은 지나지 않았다. 정규장 일정과 휴장·조기 마감 여부, 거래정지, 최신 실행 호가, 진입 조건 충족은 미확인이다. 기존 10:30 표기는 장중 진입 허용 시각이 아니다.","risk_condition_ko":"1,380 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":354.315,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":363.8845808793414,"relative_volume":1.0153379929959203,"spread_bps":7.33551517887346,"day_high":369.26,"day_low":353.91,"execution_condition_ko":"340.74~344.06달러 시험 후 344.06달러 이상 종가와 다음 실제 거래일 종가 지지를 확인한다. 계약 위험과 순손익비가 개선되지 않으면 관찰에 그친다. / 357.34~358.47달러 돌파는 관찰만 한다. 다음 저항 366.74~369.82달러까지 약 8~12달러로 평균 실제 변동폭 17.57달러보다 짧다. 369.82달러 상회 종가와 다음 거래일 지지는 증액 재평가 조건이지 자동 매수가 아니다.","risk_condition_ko":"340.74 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":152.18,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":155.28304576775733,"relative_volume":1.5438067631551868,"spread_bps":1.3142331449605882,"day_high":158.1301,"day_low":152.0,"execution_condition_ko":"153.84달러 회복은 지연 장전 고점 회복을 관찰하는 신호일 뿐 매수 신호가 아니다. 158.19~159.70달러 저항대 돌파와 지지 전환을 우선 확인하고, 이후 163.20달러 및 170.00~171.30달러 저항을 본다. / 2026-11-19 04:36:02 미 동부시간 기준 계획은 미만료다. 실제 정규장 일정, 거래정지 여부, 시세의 최신성 및 진입 조건 충족 여부는 미확인이다. 기존안의 10:30 표기는 일중 선행 매수 금지와 상충하므로 개시 시각으로 적용하지 않는다.","risk_condition_ko":"150.33 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":318.3201,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":329.57671949234975,"relative_volume":0.9409711029974926,"spread_bps":21.663029998587124,"day_high":336.32,"day_low":317.87,"execution_condition_ko":"305.80~308.93달러: 최근 지지대다. 하단 아래 정규장 종가가 확정되면 보유 위험을 추가로 줄인다. / 329.25~332.36달러: 종가 회복과 다음 확인된 정규장 지지는 단기 반등 관찰 신호일 뿐 매수 신호가 아니다.","risk_condition_ko":"305.8 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":288.62,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":292.64614805293456,"relative_volume":1.0670541245113543,"spread_bps":2.772290951936824,"day_high":295.43,"day_low":288.355,"execution_condition_ko":"276.92~279.69달러를 시험한 뒤 279.69달러 위에서 정규장 마감하고 다음 확인된 거래일에도 지지를 지키면, 실제 후보가에서 첫 저항 하단 296.33달러까지의 순손익비를 다시 계산한다. / 291.10달러는 관찰선이다. 296.49달러 위에서 정규장 마감하고 다음 확인된 거래일에 296.33~296.49달러가 지지로 바뀌면, 다음 저항 302.56~304.97달러까지의 보상을 재평가한다. 두 가격 경로 모두 주문 신호는 아니다.","risk_condition_ko":"276.92 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":72.845,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":73.2720536152676,"relative_volume":1.224876008599595,"spread_bps":1.3725893898847186,"day_high":73.49,"day_low":72.845,"execution_condition_ko":"74.76달러 위 정규장 종가와 다음 거래일 지지는 반등 관찰 신호일 뿐이다. 81.50달러는 2026-11-18 기준 하락 중인 50일 이동평균으로, 목표가가 아니며 재평가 때 갱신한다. / 동시점 GLDM 시장가격과 공식 주당 순자산가치를 대조한다. 78.13달러 회복 후에도 금 현물 반등을 순설정·실질금리·달러 중 적어도 하나가 뒷받침하는지 확인하고, 새 지지·저항과 실제 거래비용으로 보상/위험을 다시 계산한다.","risk_condition_ko":"75.96 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":282.45,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":282.9711958810178,"relative_volume":0.6597797119425292,"spread_bps":14.513531212940695,"day_high":286.0488,"day_low":280.4612,"execution_condition_ko":"2026-11-19T05:15:55.817292-05:00 기준 계획은 만료되지 않았으나 거래소 일정·정규장 거래 가능 상태·진입 조건은 미확인이다. 04:50 개장 전 관측은 약 14분 29초 지연됐고 호가 차이가 약 1.78%였다. 저가 283.06달러를 정규장 지지 이탈이나 주문 근거로 쓰지 않는다. / 283.12~284.91달러 지지 방어를 우선 확인한다. 이후 292.10~292.55달러 회복과 지지 전환, 294.50~295.46달러 저항 돌파 여부, 돌파 시 300.42~302.93달러 고점 재시험을 본다.","risk_condition_ko":"283.12 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GE","display_name":"GE","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":324.58,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":327.7410839843145,"relative_volume":0.3721996967333883,"spread_bps":6.778198847707038,"day_high":330.0,"day_low":324.56,"execution_condition_ko":"323.28~325.00달러 재시험, 325.00달러 초과 종가 회복, 다음 실제 정규장의 지지 유지와 체결 가능 가격을 차례로 확인한다. / 331.71~333.48달러의 첫 저항과 342.90~343.59달러의 박스권 상단 반응을 확인한다. 343.59달러 위 종가가 나와도 다음 정규장 지지와 거래량만 점검한다. 351.43달러까지의 7.84달러는 평균진폭 9.98달러보다 짧아 추격하지 않는다.","risk_condition_ko":"323.28 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"KO","display_name":"KO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":95.755,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":95.47919540952438,"relative_volume":1.1398253686706152,"spread_bps":1.044331888674755,"day_high":96.68,"day_low":94.73,"execution_condition_ko":"96.63~97.16달러 시험 후 97.16달러 위 종가 회복과 다음 실제 정규장 지지 확인. 실행 전 거래소 일정·개장 및 거래정지 여부, 최신 체결 가능 호가와 새 중요 공시를 확인한다. / 98.87~99.61달러는 보유 위험과 손익비를 재평가할 첫 저항이지 자동 익절 구간이 아니다. 100.56달러 위 종가, 거래 참여 개선과 다음 정규장 지지 전환은 별도 관찰 신호이며 이번 매수에 포함하지 않는다.","risk_condition_ko":"96.63 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1088.91,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":1089.4578619605427,"relative_volume":0.8033108392993609,"spread_bps":6.061440969831307,"day_high":1094.54,"day_low":1084.0101,"execution_condition_ko":"1,083.89~1,096.01달러 지지 시험 후 1,096.01달러 위 정규장 종가 회복과 다음 실제 정규장 재시험 지지를 확인한다. / 1,123.67달러 위 정규장 종가에 평소보다 강한 거래량이 동반되고 다음 실제 정규장에서도 지지되면 돌파를 별도로 재평가한다. 자동 매수는 아니다.","risk_condition_ko":"1,083.89 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WELL","display_name":"WELL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":246.03,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":245.48451238178262,"relative_volume":0.8922194037918049,"spread_bps":10.565240359217801,"day_high":247.25,"day_low":244.57,"execution_condition_ko":"11월 18일 회복에 이어 다음 실제 정규장에서 243.68달러 재시험과 그 이상 종가를 확인한다. 이후 거래 가능한 정규장에서 243.68~243.90달러에 체결할 수 있고 비용 차감 손익비와 위험 여력이 충족될 때만 첫 진입을 검토한다. / 249.75달러를 웃도는 종가와 다음 정규장 지지는 관찰 신호일 뿐이다. 251.12~253.37달러 저항대와 254.42달러 변동성 참고치까지 여력을 다시 계산하되 자동 매수하지 않는다.","risk_condition_ko":"241.52 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WMT","display_name":"WMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":125.565,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":125.29049298231844,"relative_volume":1.7491497765550323,"spread_bps":3.98231850583387,"day_high":126.22,"day_low":123.29,"execution_condition_ko":"$126.60 회복은 관찰 신호다. 신규 매수 판단은 공식 실적 확인 후 $126.99~$127.36 재시험에서 따로 내린다. / $127.77~$127.78에서 재차 밀리면 신규 매수를 보류한다. $129.85 위 종가와 다음 실제 거래일 지지가 확인되면 $131.82까지의 순손익비를 다시 계산한다.","risk_condition_ko":"125.07 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":568.73,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":569.6359117236386,"relative_volume":0.5213015349179355,"spread_bps":3.1648351648362842,"day_high":573.13,"day_low":567.94,"execution_condition_ko":"570.89–573.09달러 지지, 574.82달러 종가 회복, 다음 정규장의 지지 재확인을 순서대로 본다. 거래소 일정, 거래정지 여부, 최신 체결 가능 호가는 별도로 확인한다. / 586.45달러를 상회하는 종가에 거래 참여가 강화되고 이후 583.72–586.45달러가 지지되면 추가 매수를 별도로 검토한다. 592.94–596.92달러까지의 비용 차감 후 보상과 애플·알파벳 중복 노출을 다시 따진다.","risk_condition_ko":"570.89 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LIN","display_name":"LIN","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":513.995,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":513.0710901390473,"relative_volume":0.8653331687531116,"spread_bps":4.086119840056091,"day_high":515.92,"day_low":510.34,"execution_condition_ko":"508.00~510.01달러 시험과 510.01달러 위 정규장 종가에 이어 다음 실제 정규장에서 510.01달러 재시험이 유지되는지 확인한다. / 519.56달러 위 정규장 종가와 다음 정규장 재시험 안착은 별도로 관찰한다. 다음 저항 하단 525.30달러까지 5.74달러에 불과해 추격하지 않는다.","risk_condition_ko":"508 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.915,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":100.92291797925601,"relative_volume":0.34929568470999794,"spread_bps":2.973093503790807,"day_high":101.5,"day_low":100.0,"execution_condition_ko":"11월 19일 04:50 미국 동부시간의 100.27달러 관측은 지연된 100주 자료이며 호가 차이는 약 2.60%였다. 거래 상태와 정규장 호가가 미확인이라 지지나 체결 신호로 쓰지 않는다. / 실적 검토 후 101.44~101.60달러 회복·재시험과 103.34~104.49달러의 첫 저항 소화 여부를 본다. 다음 저항은 105.72~106.20달러다.","risk_condition_ko":"99.59 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AES","display_name":"AES","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":15.025,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":15.024724610204084,"relative_volume":6.686674074443608,"spread_bps":6.65557404326109,"day_high":15.04,"day_low":15.02,"execution_condition_ko":"실제 정규장 개장과 거래 가능 여부를 확인하고, $15.03 초과 종가 뒤 다음 정규장의 $15.00~$15.03 재시험과 $15.00 이상 종가를 점검한다. / 공식 거래 문서와 신선한 매수·매도 가능 호가가 확보되면 정상 종결·지연·무산 시나리오별 순보상과 기존 보유분의 스트레스 손실을 다시 계산한다.","risk_condition_ko":"14.94 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SO","display_name":"SO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":92.8,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":93.17162433569439,"relative_volume":0.490509778535917,"spread_bps":5.386479935361935,"day_high":94.24,"day_low":92.6275,"execution_condition_ko":"93.13~93.15달러 시험 후 93.15달러 위 종가와 다음 거래일 지지 유지를 먼저 본다. 돌파는 94.94달러 위 종가와 94.77~94.94달러 지지 전환을 본다. 확인이 끝난 뒤 가격이 비용 반영 상한을 넘으면 매수하지 않는다. / 기사 17건에서 목표주가 상향과 하향은 각각 3건이다. 전용 소셜·투자자 포지셔닝, 금리·물가 및 동종사 비교 자료는 없다. 거시 자료는 주가지수 선물 보도 1건으로, 금리 방향이나 유틸리티로의 자금 이동을 확인할 수 없다.","risk_condition_ko":"90.8 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":168.37,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":167.6219370696893,"relative_volume":0.4986434151436808,"spread_bps":7.127160420502735,"day_high":168.54,"day_low":166.888,"execution_condition_ko":"투자자의 날 발표가 판매량·점유율 방어와 비용 상쇄의 구체적 근거를 제시하는지 확인한다. / 발표 기준 충족 후 168.62~168.80달러 지지와 170.29달러 이상 새 일봉 마감, 이어 다음 정규장의 168.80~169.66달러 재시험을 순서대로 확인한다. 재시험이 없거나 169.66달러를 넘으면 추격하지 않는다.","risk_condition_ko":"167.2 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":407.3,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":408.94696657441756,"relative_volume":0.7984803163102018,"spread_bps":3.682653474582995,"day_high":413.51,"day_low":406.51,"execution_condition_ko":"411.83~411.99달러 지지 시험과 회복, 422.79달러 위 정규장 종가, 다음 실제 정규장의 420.05~422.79달러 재시험 및 420.05달러 이상 마감을 순서대로 확인한다. / 425.99~430.99달러 저항에서는 추격하지 않는다. 430.99달러 위 종가와 다음 정규장 지지가 확인되면 435.95~441.41달러를 다음 저항으로 본다.","risk_condition_ko":"411.83 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":633.685,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":635.3145917330737,"relative_volume":0.5136660455685867,"spread_bps":8.994579582305139,"day_high":641.0,"day_low":633.0,"execution_condition_ko":"위험 대응 조건: 636.39 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"636.39 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NKE","display_name":"NKE","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":34.9904,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":35.24650417122685,"relative_volume":0.8613991391789335,"spread_bps":2.857551078724963,"day_high":36.0,"day_low":34.87,"execution_condition_ko":"위험 대응 조건: 34.96 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"34.96 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MRVL","display_name":"Marvell Technology","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":146.79,"market_data_asof":"2026-11-19T10:36:00-05:00","market_data_clock_status":null,"session_vwap":151.63321997983203,"relative_volume":0.8981747874591266,"spread_bps":17.02823280999898,"day_high":154.5146,"day_low":146.41,"execution_condition_ko":"위험 대응 조건: 140.9 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"140.9 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-19T10:36:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-19T10:39:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-20T01:16:51.379028+09:00",
  "as_of": "2026-11-19T10:36:00-05:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
