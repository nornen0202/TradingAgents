# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-23T11:45:43.157056+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261123T175107_local-scheduler-us-full",
  "producer_finished_at": "2026-11-23T20:05:01.359071+09:00",
  "analysis_run_id": "20261123T175107_local-scheduler-us-full",
  "analysis_completed_at": "2026-11-23T19:42:40.725338+09:00",
  "analysis_trade_date_oldest": "2026-11-20",
  "analysis_trade_date_latest": "2026-11-20",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-23T08:51:34+00:00",
  "market_data_latest_at": "2026-11-23T05:25:00-05:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-23T19:43:09.407530+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-23T19:43:09.407530+09:00",
    "run_started_at": "2026-11-23T17:51:07.620327+09:00",
    "run_finished_at": "2026-11-23T20:05:01.359071+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23598843,
    "total_market_value_krw": 20327269,
    "total_unrealized_pnl_krw": -3271574,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 112426,
    "total_equity_krw": 21416347
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 545177,
      "current_price_krw": 456594,
      "market_value_krw": 5479132,
      "unrealized_pnl_krw": -1062993
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 292207,
      "current_price_krw": 282862,
      "market_value_krw": 3111485,
      "unrealized_pnl_krw": -102794
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 423828,
      "current_price_krw": 373240,
      "market_value_krw": 2239442,
      "unrealized_pnl_krw": -303531
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1878558,
      "current_price_krw": 1635617,
      "market_value_krw": 1635617,
      "unrealized_pnl_krw": -242941
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 555511,
      "current_price_krw": 437096,
      "market_value_krw": 1311289,
      "unrealized_pnl_krw": -355244
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 134414,
      "current_price_krw": 134599,
      "market_value_krw": 1211393,
      "unrealized_pnl_krw": 1667
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 267040,
      "current_price_krw": 181645,
      "market_value_krw": 1089872,
      "unrealized_pnl_krw": -512373
    },
    {
      "ticker": "GEV",
      "name": "GE 버노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1471752,
      "current_price_krw": 974102,
      "market_value_krw": 974102,
      "unrealized_pnl_krw": -497650
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 364298,
      "current_price_krw": 465748,
      "market_value_krw": 931497,
      "unrealized_pnl_krw": 202900
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1418889,
      "current_price_krw": 1808056,
      "market_value_krw": 788430,
      "unrealized_pnl_krw": 169702
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 569188,
      "current_price_krw": 429286,
      "market_value_krw": 429286,
      "unrealized_pnl_krw": -139902
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 662237,
      "current_price_krw": 399464,
      "market_value_krw": 399464,
      "unrealized_pnl_krw": -262773
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 136108,
      "current_price_krw": 95710,
      "market_value_krw": 382842,
      "unrealized_pnl_krw": -161590
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 347484,
      "current_price_krw": 343418,
      "market_value_krw": 343418,
      "unrealized_pnl_krw": -4066
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":344.7,"market_data_asof":"2026-11-23T04:30:00-05:00","market_data_clock_status":null,"session_vwap":342.1757005817827,"relative_volume":0.10591301834572216,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"343.75~345.40달러는 반등 관찰 구간이다. 345.40달러를 넘어도 매수하지 않고, 351.19달러 초과 종가와 다음 거래일 351.14~351.19달러 지지 여부를 확인한다. / 351.19달러에서 371.94달러까지 상승 여력은 20.75달러, 318.48달러까지 하락 폭은 32.71달러로 비용 전 손익비는 약 0.63 대 1이다. 318.48달러가 유일하게 근거 있는 손절 기준이라면 매수하지 않는다.","risk_condition_ko":"351.14 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T04:30:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T04:33:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":278.02,"market_data_asof":"2026-11-23T08:51:49+00:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"303.60달러 초과 종가는 초기 회복 신호일 뿐 매수 신호가 아니다. / 실적 원문 검토 후 거래량 참여가 확인된 정규장 종가가 315.00달러를 넘고, 다음 확인된 정규장에서 305.80~315.00달러 구간이 지지되면 재심사한다. 현실적인 청산가 기준 순손익비와 급락 충격 시험을 모두 통과해야 소규모 진입을 검토한다.","risk_condition_ko":"274.35 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T08:51:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T08:54:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1244.1395,"market_data_asof":"2026-11-23T04:05:00-05:00","market_data_clock_status":null,"session_vwap":1202.264869888476,"relative_volume":0.03679533751357028,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1,244.14달러 회복은 초기 관찰 신호다. 1,271.13달러와 1,287.01~1,291.00달러 저항을 넘고 기존 지지대 상단 1,295.96달러를 종가로 되찾아 지키는지 본다. 이 단계에서는 매수하지 않는다. / 1,328.43달러 위 종가와 다음 확인 가능한 정규장의 지지가 나와도 손익비를 다시 계산한다. 1,328.43달러 진입과 1,125.00달러 손절을 가정하면 전고점 1,513.49달러까지 비용 전 보상 대 위험은 약 0.91대 1이다. 전고점은 저항 참고치이지 목표가가 아니다. 새 지지에 근거한 유효 손절과 현실적인 상승 여력으로 비용 차감 후 최소 2대 1이 확보되지 않으면 계속 대기한다.","risk_condition_ko":"1,280 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T04:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T04:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":277.93,"market_data_asof":"2026-11-23T04:05:00-05:00","market_data_clock_status":null,"session_vwap":276.0738823792522,"relative_volume":0.05529497284764383,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"정규장 종가 기준 278.19달러 회복, 285.59달러 상향 돌파, 282.01~285.59달러 재시험 순으로 확인한다. 대형 기술주를 따라 오르는 데 그치지 않고 상대강도가 개선되는지도 본다. / 돌파가 유지되면 295.43달러, 그다음 302.56~304.97달러를 저항으로 관찰한다. 두 구간 모두 현재 매도 주문이 아니다. 272.36달러를 회복한 뒤 종가로 다시 이탈하면 재편입한 단기 노출을 줄인다.","risk_condition_ko":"272.36 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T04:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T04:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":323.565,"market_data_asof":"2026-11-23T04:05:00-05:00","market_data_clock_status":null,"session_vwap":323.9906639004149,"relative_volume":0.005774650148451638,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"323.28달러의 정규장 종가 회복 여부로 단기 매매분의 1차 축소 필요성을 판단한다. / 327.99~329.96달러 상단 돌파와 다음 정규장의 지지는 반등 확인 신호일 뿐 매수 신호가 아니다. 345.69~347.20달러 상단 종가 돌파와 다음 정규장 지지는 새 손절·목표 및 순보상 대 위험을 산정할 계기다.","risk_condition_ko":"323.28 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T04:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T04:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":730.0,"market_data_asof":"2026-11-23T04:05:00-05:00","market_data_clock_status":null,"session_vwap":727.8959518233523,"relative_volume":0.013371370535730958,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"745.39~756.28달러 회복 구간을 통과해 756.28달러 위에서 정규장을 마친 뒤 다음 실제 거래일의 747.00~750.00달러 재지지 또는 756.28달러 재돌파·유지 확인 / 2026-11-20 기준 10일 지수이동평균 774.89달러와 거래량 가중 이동평균 792.84달러의 순차 회복 확인. 두 가격은 저항선이며 매수 승인이나 목표가가 아니다.","risk_condition_ko":"747 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T04:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T04:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":71.43,"market_data_asof":"2026-11-23T04:05:00-05:00","market_data_clock_status":null,"session_vwap":71.47590409116087,"relative_volume":0.04927958584089907,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"71.22~71.92달러는 지연 장전 관찰 범위일 뿐 정규장 지지나 돌파가 아니다. 확인된 정규장 일봉으로 회복 구간과 이동평균을 갱신한다. / 금 현물, 미국 실질금리와 달러, GLDM 순설정·순환매, 최신 좌당 순자산가치와 할증·할인, 보수 및 추적 차이를 확인한다. 개별 뉴스와 소셜 자료는 조회 불가였으며 중립 신호로 보지 않는다.","risk_condition_ko":"72.32 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T04:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T04:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":342.56,"market_data_asof":"2026-11-23T08:51:34+00:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"340.56~341.59달러 지지 시험, 341.59달러 위 종가와 다음 정규장 지지 유지 여부를 순서대로 확인한다. 342.56달러 위에서는 추격하지 않는다. / 348.02~349.15달러 저항 회복과 349.15달러 위 안착을 관찰한다. 이후 저항은 354.34~355.28달러와 359.37~360.83달러다.","risk_condition_ko":"340.56 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T08:51:34+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T08:54:34+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.6402,"market_data_asof":"2026-11-23T04:30:00-05:00","market_data_clock_status":null,"session_vwap":100.64498240521408,"relative_volume":0.11137488080168928,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"100.59~100.61달러 접촉 후 100.61달러 이상 정규장 종가 회복과 다음 정규장 지지 재확인, 또는 100.65달러 초과 정규장 종가와 통상보다 많은 거래량 이후 다음 정규장 재시험 지지를 확인한다. / 공식 수익률·분배 일정, 정규장 실시간 호가와 동시점 순자산가치, 대안 조건 및 실제 현금 사용 가능일을 확인한다. 단위·산식·기준일이 불명확한 3.64는 사용하지 않는다.","risk_condition_ko":"100.56 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T04:30:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T04:33:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":211.5,"market_data_asof":"2026-11-23T04:20:00-05:00","market_data_clock_status":null,"session_vwap":211.09233954451346,"relative_volume":0.004186530293837219,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"206.86~208.14달러 방어와 211.63달러 회복을 먼저 본다. 돌파 후에는 217.79달러와 221.16달러에서 상승세가 이어지는지 점검한다. / 정규장 상승 종목 비중과 RSP의 VOO 대비 상대성과를 같은 시점에 확인한다. 기사 12건 중 10건이 한 매체에 집중됐고 전용 소셜 자료가 없어 기사 논조를 실제 투자 비중이나 순유입으로 해석하지 않는다.","risk_condition_ko":"206.86 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T04:20:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T04:23:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":246.82,"market_data_asof":"2026-11-23T08:51:49+00:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"245.15~245.31 시험, 245.31 상회 종가, 다음 확인된 정규장의 지지 유지와 245.31~246.82 실제 거래를 순서대로 확인한다. / 255.03 회복 후 지지 전환과 259.97~262.47 저항을 확인한다. 262.47을 거래량 증가와 함께 돌파한 뒤에만 274.00~275.75를 다음 저항으로 본다.","risk_condition_ko":"245.15 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T08:51:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T08:54:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1355.5719,"market_data_asof":"2026-11-23T04:15:00-05:00","market_data_clock_status":null,"session_vwap":1348.8535784635587,"relative_volume":0.009596263073268508,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"신선한 정규장 시세로 1,341.46–1,341.76달러 지지와 1,372.05–1,382.00달러 저항 돌파, 1,400.96달러의 후속 재시험을 순서대로 점검한다. 상단을 넘겨 추격하지 않는다. / 판단 시각은 2026-11-23 미 동부시간 04:29:23이다. 2026-11-30 미 동부시간 16:00 만료는 아직 지나지 않았다. 약 일주일의 검토 기한일 뿐 실제 거래일·조기 폐장·거래정지·호가 신선도·다음 회사 일정을 확인한 것은 아니다. 진입 전에 이를 별도로 확인한다.","risk_condition_ko":"1,341.46 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T04:15:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T04:18:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":137.75,"market_data_asof":"2026-11-23T04:15:00-05:00","market_data_clock_status":null,"session_vwap":135.51732917258735,"relative_volume":0.20512275718190082,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"138.00달러는 초기 반등 관찰선이다. 145.98달러 초과 정규장 종가가 나온 뒤 바로 다음 정규장의 143.73~145.98달러 지지 여부를 확인한다. / 133.57달러 미만 정규장 종가가 나오면 124.50~125.53달러를 점검한다. 124.50달러 아래 확인된 다음 지지선은 없다.","risk_condition_ko":"133.57 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T04:15:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T04:18:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":304.41,"market_data_asof":"2026-11-23T08:51:49+00:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단 기준은 2026-11-23 미국 동부시간 04:03:22이며, 마지막으로 확인된 가격은 2026-11-20 정규장 종가 304.41달러다. 2026-11-23 03:52:25 지연 야간 조회의 같은 표시가와 보고 거래량 0주는 최신 체결·거래 가능 여부·지지 방어를 입증하지 않는다. 거래소 일정과 거래정지 여부를 확인하고 최신 정규장 자료로 재판단한다. / 301.02달러 방어와 319.30–323.05달러 회복을 먼저 관찰한다. 이후 329.82달러 안착, 342.65달러 돌파, 366.92–371.07달러 저항 순으로 점검한다. 첫 회복 구간은 단독 매수 신호가 아니다.","risk_condition_ko":"301.02 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T08:51:49+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T08:54:49+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":572.01,"market_data_asof":"2026-11-23T05:00:00-05:00","market_data_clock_status":null,"session_vwap":571.7904509283819,"relative_volume":0.022669064356165877,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"577.49달러 상회 마감과 다음 실제 거래일의 576.84~577.49달러 재시험을 확인한다. 첫 저항은 586.04~588.54달러, 다음 저항은 595.15~596.92달러다. / 565.60~566.52달러 지지를 점검한다. 하단이 종가로 무너지면 559.61~562.45달러를 다음 지지 구간으로 본다.","risk_condition_ko":"565.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T05:00:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T05:03:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":286.75,"market_data_asof":"2026-11-23T05:00:00-05:00","market_data_clock_status":null,"session_vwap":286.5884749708964,"relative_volume":0.0064446239869505,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"정규장 일정·거래 가능 상태·신선한 호가를 확인하고 $290.92 상회 종가와 다음 확인된 정규장의 $290.23~$290.92 지지를 점검한다. / $294.45~$295.03 저항 돌파와 지지 전환, $298.42~$302.93까지의 추가 분할 여력을 확인한다.","risk_condition_ko":"278.25 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T05:00:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T05:03:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":169.3,"market_data_asof":"2026-11-23T05:10:00-05:00","market_data_clock_status":null,"session_vwap":169.20637507923573,"relative_volume":0.022828252408904667,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"168.41~169.05달러 시험, 169.05달러 이상 정규장 종가, 다음 확인된 정규장의 재시험 지지와 169.05달러 회복을 순서대로 확인한다. / 171.61달러 위 거래량 동반 안착은 관찰만 한다. 173.57~173.59달러까지 1.96~1.98달러로 11월 20일 평균 실제 변동폭 3.20달러보다 짧아 추격하지 않는다.","risk_condition_ko":"166.89 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T05:10:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T05:13:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":405.16,"market_data_asof":"2026-11-23T04:45:00-05:00","market_data_clock_status":null,"session_vwap":404.8816373817339,"relative_volume":0.014153908919867942,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"400.74~402.25달러 지지 유지와 408.74달러 회복을 관찰하고, 413.51달러 초과 정규장 종가와 다음 정규장 재지지를 순서대로 확인한다. / 420.62달러 회복, 상대강도지수 50 복귀, 이동평균 수렴·확산 막대값의 음수 폭 축소는 조정 완화의 보조 근거로만 쓴다.","risk_condition_ko":"400.74 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T04:45:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T04:48:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WMT","display_name":"WMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":127.6904,"market_data_asof":"2026-11-23T04:50:00-05:00","market_data_clock_status":null,"session_vwap":127.65971093816813,"relative_volume":0.03947694358002058,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"$126.99~$127.18 시험, $127.18 위 종가, 다음 정규장 지지와 비용 반영 후 매수 범위를 순서대로 확인한다. 진입 전 거래소 일정, 거래 가능 상태, 정규장 시세를 별도로 확인한다. / $130.52 회복은 초기 관찰 신호다. $131.82 위 종가와 다음 정규장 지지 전환을 별도로 관찰하되, 돌파 기준에서 $133.84~$134.84 저항까지 여유가 $2.02~$3.02에 불과하므로 이번 계획은 추격 매수에 적용하지 않는다.","risk_condition_ko":"123.03 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T04:50:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T04:53:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1101.05,"market_data_asof":"2026-11-23T05:05:00-05:00","market_data_clock_status":null,"session_vwap":1103.078967943706,"relative_volume":0.04002145638204939,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1098.51~1100.00달러 첫 방어 구간의 일봉 유지나 회복은 관찰만 한다. 방어에 실패하면 1082.37~1083.15달러를 관찰한다. / 1082.37~1083.15달러 시험 후 1083.15달러 위 일봉 마감과 다음 실제 정규장의 지지 유지가 확인되면, 기한과 손익비를 다시 확인해 소액 진입을 검토한다.","risk_condition_ko":"1,082.37 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T05:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T05:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":101.49,"market_data_asof":"2026-11-23T04:00:00-05:00","market_data_clock_status":null,"session_vwap":100.93380614657211,"relative_volume":0.0022825188457018643,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"실적 실제 공개와 연간 전망 확인, $99.59 부근 지지 시험, $100.00 이상 정규장 종가, 다음 실제 정규장 지지 유지 순으로 확인한다. 거래소 일정, 최신 정규장 호가 및 거래 가능 상태는 미확인이다. / $102.61 위 종가 돌파와 다음 실제 정규장의 지지 유지를 관찰한다. 다음 저항 $104.49까지 $1.88로 평균진폭 $2.41보다 짧아 첫 돌파는 추격하지 않는다. 그 위 저항은 $106.20~$106.66이다.","risk_condition_ko":"99.59 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T04:00:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T04:03:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"HD","display_name":"HD","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":344.1417,"market_data_asof":"2026-11-23T04:10:00-05:00","market_data_clock_status":null,"session_vwap":341.88862559241704,"relative_volume":0.013532014485810684,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"매수 관찰: 347.70달러 초과 정규장 종가, 다음 정규장의 지지 전환, 347.70~349.00달러 내 체결 가능 호가와 비용 반영 손익비를 차례로 확인한다. / 보유 위험 관찰: 330.31~332.34달러 지지대와 328.60달러 정규장 종가를 확인한다. 신규 돌파 물량에는 345.41달러 실패 기준을 별도로 적용한다.","risk_condition_ko":"330.31 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T04:10:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T04:13:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WELL","display_name":"WELL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":243.33,"market_data_asof":"2026-11-23T05:10:00-05:00","market_data_clock_status":null,"session_vwap":241.41181102362205,"relative_volume":0.007598565553375249,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"239.93~241.52달러 지지, 244.79달러 초과 정규장 종가, 후속 정규장의 243.65~244.79달러 재시험과 243.65달러 이상 종가를 순서대로 확인한다. 이후 구간 내 체결과 비용 차감 후 손익비 2배가 모두 가능한지 확인한다. / 248.29~249.75달러 저항 접근 시 손익비를 다시 평가한다. 249.75달러에서 253.37달러까지 3.62달러는 최근 평균 실제 변동폭 5.36달러보다 짧아 첫 돌파를 추격하지 않는다.","risk_condition_ko":"239.93 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T05:10:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T05:13:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":632.5,"market_data_asof":"2026-11-23T04:40:00-05:00","market_data_clock_status":null,"session_vwap":630.1063664596273,"relative_volume":0.007879699306105225,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단 기준은 2026-11-23T04:58:57.101483-05:00이며 계획 검토 기한은 아직 지나지 않았다. 11월 23일 04:40 동부시간 장전 관측 $632.50은 493초 지연됐고 표시 거래량은 1,288주, 호가 차이는 약 0.61%였다. 정규장 일정, 거래정지 여부, 실시간 호가와 진입 조건은 별도로 확인한다. / $642.80 상회 종가 이후 $637.03 지지 재시험을 관찰한다. $652.06 상회 종가와 후속 지지는 비중 확대를 재검토할 조건이지 자동 매수 신호가 아니다.","risk_condition_ko":"624.11 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T04:40:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T04:43:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NTAP","display_name":"NetApp","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":162.03,"market_data_asof":"2026-11-23T04:00:00-05:00","market_data_clock_status":null,"session_vwap":162.68354430379748,"relative_volume":0.0008234870811309563,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"155.34~156.55달러 지지 유지와 168.21~170.18달러 회복을 정규장 종가와 다음 정규장 재시험으로 확인한다. 초기 회복만으로 추격하지 않는다. / 176.75달러 상회 마감 뒤 재시험에서 지지로 전환되면 실제 체결 가능 가격과 재시험 무효화 수준으로 188.01달러까지 비용·갭 반영 순보상 대 위험을 재산정한다. 최소 2배일 때만 소규모 첫 진입을 별도로 검토한다. 201.81달러를 첫 목표처럼 사용하지 않는다.","risk_condition_ko":"168.21 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T04:00:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T04:03:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SO","display_name":"SO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":93.28,"market_data_asof":"2026-11-23T04:00:00-05:00","market_data_clock_status":null,"session_vwap":93.23791821561338,"relative_volume":0.0012475416450189365,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"눌림목: 92.80~93.00달러를 시험하고 93.00달러 초과로 마감한 뒤, 다음 확인 거래일에도 지지가 유지되고 93.00달러 초과로 마감하는지 본다. 충족 후 93.00~93.35달러에서만 검토한다. / 돌파: 최근 통상적인 일간 거래량보다 뚜렷하게 많은 거래량으로 94.94달러를 넘겨 마감한 뒤, 다음 확인 거래일에 94.68~94.94달러를 재시험하고 94.94달러 초과로 마감하는지 본다. 충족 후 94.94~95.50달러에서만 검토한다.","risk_condition_ko":"90.35 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T04:00:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T04:03:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LIN","display_name":"LIN","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":508.1,"market_data_asof":"2026-11-23T05:25:00-05:00","market_data_clock_status":null,"session_vwap":506.732181425486,"relative_volume":0.050154619069784634,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"500.26~502.83달러 지지, 510달러 종가 돌파와 508~510달러 재시험, 514.32~518.02달러 저항대 회복을 순서대로 점검한다. 526~533.39달러는 후속 저항이지 자동 익절 구간이 아니다. / 공시 색인 3건의 본문은 미확보다. 재무제표 표시 통화·단위, 주당 수치의 주식 기준, 미국 예탁증서 해당 여부와 해당 시 보통주 환산비율을 원문에서 확인하기 전에는 절대 주당순이익이나 서로 다른 통화 금액을 비교하지 않는다. 조회 시간대가 없는 공급사 마진·현금흐름 자료는 판단 시점 이전 이용 가능 여부가 불명이라 제외했다.","risk_condition_ko":"500.26 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T05:25:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T05:28:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"KO","display_name":"KO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":96.7717,"market_data_asof":"2026-11-23T04:55:00-05:00","market_data_clock_status":null,"session_vwap":96.68406832644858,"relative_volume":0.0464700262714405,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"KO의 판단 이후 정규장 종가가 96.86달러 이상이고 다음 실제 거래일에 96.75~96.86달러가 지지되면 눌림 지지의 증거로 기록한다. 그 자체로 매수하지 않는다. / KO가 97.79달러를 넘겨 마감한 뒤 그 가격을 지키면 98.38~98.87달러까지 남은 보상을 검토한다. 98.87달러 초과 종가와 다음 실제 거래일의 지지 확인은 100.56달러 재시험 가능성과 증액을 평가하는 기준이지 자동 주문 신호가 아니다.","risk_condition_ko":"94.72 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T04:55:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T04:58:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AES","display_name":"AES","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":15.03,"market_data_asof":"2026-11-23T05:15:00-05:00","market_data_clock_status":null,"session_vwap":15.020605280103027,"relative_volume":0.002012971555635782,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"공식 인수·배당 조건과 최신 체결 가능 호가를 확보해 성사·지연·무산 손익과 대안 대비 보상을 다시 계산한다. 정규장 일정과 거래 가능 상태는 별도로 확인한다. / AES가 14.98~15.00달러 시험 후 15.00달러 이상에서 마감하거나 15.04달러를 초과해 마감한 뒤, 다음으로 확인된 정규장 종가에서도 해당 기준선을 지키는지 본다.","risk_condition_ko":"14.98 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T05:15:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T05:18:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"JNJ","display_name":"JNJ","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":272.29,"market_data_asof":"2026-11-23T04:30:00-05:00","market_data_clock_status":null,"session_vwap":270.7931400282885,"relative_volume":0.007183337701015731,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"264.68~267.43달러 눌림 구간과 267.43달러 종가 회복 및 다음 정규장 지지를 확인한다. 272.50달러까지 남은 순상승 여력이 부족하면 매수하지 않는다. / 276.38달러 위 정규장 종가와 다음 정규장 지지는 추세 개선 신호다. 다만 첫 저항 282.02~283.25달러까지의 상승 여력 5.64~6.87달러가 무효화선까지의 하방 11.70달러보다 작아 이번 매수는 발동하지 않는다.","risk_condition_ko":"264.68 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-23T04:30:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-23T04:33:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
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
