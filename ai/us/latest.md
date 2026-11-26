# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-26T01:28:38.771624+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261126T060125_local-freshness-us-overlay",
  "producer_finished_at": "2026-11-26T06:08:23.846400+09:00",
  "analysis_run_id": "20261125T201205_local-scheduler-us-full",
  "analysis_completed_at": "2026-11-25T20:25:45.645612+09:00",
  "analysis_trade_date_oldest": "2026-11-24",
  "analysis_trade_date_latest": "2026-11-24",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": null,
  "market_data_latest_at": null,
  "market_data_status": "MISSING"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-26T02:32:36.680021+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-26T02:32:36.680021+09:00",
    "run_started_at": "2026-11-26T02:18:24.093203+09:00",
    "run_finished_at": "2026-11-26T02:33:47.760835+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23710005,
    "total_market_value_krw": 19976338,
    "total_unrealized_pnl_krw": -3733667,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 113534,
    "total_equity_krw": 21066465
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 547745,
      "current_price_krw": 444153,
      "market_value_krw": 5329846,
      "unrealized_pnl_krw": -1243099
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 293583,
      "current_price_krw": 287906,
      "market_value_krw": 3166972,
      "unrealized_pnl_krw": -62449
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 425825,
      "current_price_krw": 362530,
      "market_value_krw": 2175180,
      "unrealized_pnl_krw": -379773
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1887408,
      "current_price_krw": 1521438,
      "market_value_krw": 1521438,
      "unrealized_pnl_krw": -365970
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 558128,
      "current_price_krw": 417261,
      "market_value_krw": 1251785,
      "unrealized_pnl_krw": -422599
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 135047,
      "current_price_krw": 135260,
      "market_value_krw": 1217341,
      "unrealized_pnl_krw": 1916
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 268298,
      "current_price_krw": 193636,
      "market_value_krw": 1161816,
      "unrealized_pnl_krw": -447977
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 366014,
      "current_price_krw": 472570,
      "market_value_krw": 945141,
      "unrealized_pnl_krw": 213112
    },
    {
      "ticker": "GEV",
      "name": "GE 버노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1478685,
      "current_price_krw": 927621,
      "market_value_krw": 927621,
      "unrealized_pnl_krw": -551064
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1425574,
      "current_price_krw": 1866179,
      "market_value_krw": 813775,
      "unrealized_pnl_krw": 192132
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 571869,
      "current_price_krw": 385425,
      "market_value_krw": 385425,
      "unrealized_pnl_krw": -186444
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 665357,
      "current_price_krw": 381152,
      "market_value_krw": 381152,
      "unrealized_pnl_krw": -284205
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 136749,
      "current_price_krw": 92930,
      "market_value_krw": 371720,
      "unrealized_pnl_krw": -175277
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 349121,
      "current_price_krw": 327126,
      "market_value_krw": 327126,
      "unrealized_pnl_krw": -21995
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"691.72~700.00달러 구간에서 저점이 더 낮아지지 않고 708.97달러를 회복하는지 관찰한다. 단독 매수 신호는 아니다. / 748.44달러 초과 정규장 종가와 다음 실제 정규 거래일의 재시험을 관찰한다. 첫 저항 762.32달러와 상단 저항 776.62~778.98달러에 가까워질수록 추격하지 않는다.","risk_condition_ko":"691.72 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"308.22~316.41달러 지지 구간의 정규장 종가 방어 여부를 확인한다. 316.41달러 회복만으로는 매수하지 않는다. / 329.75달러 초과 종가와 다음 확인된 거래일의 지지, 336.34~342.50달러 저항 소화 여부는 매수 주문이 아닌 재평가 신호다.","risk_condition_ko":"308.22 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"150.50달러 회복은 낙폭 축소 신호일 뿐 매수 신호는 아니다. 145.71~146.30달러에서는 하방 지지 여부를 관찰한다. / 161.15달러 초과 정규장 마감과 다음 확인 거래일의 158.12~161.15달러 구간 지지를 본다. 실제 진입가에서 171.50달러까지의 상승 여지가 손절·갭·체결비용을 충분히 보상할 때만 첫 진입을 재검토한다.","risk_condition_ko":"145.71 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"335.88~339.73달러 지지와 349.20~351.02달러 회복을 관찰한다. 357.20달러 돌파만으로는 매수하지 않는다. 상위 저항은 386.90달러, 402.32달러, 419.77달러다. / 공급사 표의 영업이익률 58.7%와 현금흐름은 회사 원문과 공개 시점이 미확인이다. 재무제표 통화·단위와 미국 예탁증서 대 보통주 비율을 원문에서 확인하기 전에는 달러 표시 주가와 재무금액·주당이익을 직접 비교하지 않는다. 기준이 불명확한 예상 주가수익비율은 저평가 근거에서 제외한다.","risk_condition_ko":"335.88 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"같은 완료 정규장에서 1,387~1,396달러를 재시험하고 1,396달러 이상으로 마감한 뒤, 바로 다음 실제 정규장에서 1,396달러 지지와 1,396~1,400달러의 신선한 시세가 확인될 때만 초기 매수를 검토한다. / 1,415달러 돌파만으로는 매수하지 않는다. 1,435~1,439달러 돌파 후 지지 전환과 거래 참여 개선은 추세 재평가 신호일 뿐이다. 1,458.23~1,475.25달러는 다음 저항 구간으로 자동 익절 가격이 아니다.","risk_condition_ko":"1,387 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"100.63~100.66달러는 11월 20~24일 첫 눌림 관찰 구간, 100.60~100.61달러는 11월 19일 후속 관찰 구간이다. 둘 다 독립 매수 신호나 새 손절 기준이 아니다. / 2026-11-25 05:11:35 미국 동부시간 기준 유효기한은 지나지 않았다. 실제 정규장 일정, 거래정지 여부, 신선한 호가와 진입 조건 충족 여부는 미확인이다. 실제 세션을 확인해 12월 2일까지 검토한다.","risk_condition_ko":"100.63 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"318.22달러 회복은 관찰 신호일 뿐이다. 328.70달러 초과 정규장 종가와 거래량 증가가 함께 나타나면 바로 다음 거래일의 324.04~328.70달러 지지를 확인한다. / 349.37달러는 11월 24일 기준 200일 이동평균이자 첫 저항이다. 회복 후 안착하면 새 지지와 저항을 기준으로 손익비를 다시 평가한다.","risk_condition_ko":"290.5 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"350.03~350.04달러 지지대 시험, 같은 정규장 350.04달러 이상 종가, 바로 다음 정규장 350.04~351.00달러 지지를 순서대로 확인한다. / 354.40~355.64달러와 359.37~360.83달러 저항 반응을 관찰한다. 360.83달러 위 종가와 다음 정규장 지지가 확인되면 손익비를 다시 계산하되 자동 매수하거나 증액하지 않는다.","risk_condition_ko":"345.44 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"309.18달러 회복과 313.55·324.46달러 돌파는 반등 관찰 신호일 뿐 매수 조건이 아니다. 341.29달러와 366.62달러는 각각 중기·장기 저항이며 확정 목표가가 아니다. / 정규장 일정과 거래 가능 여부, 시세 신선도를 신호 확인 전에 별도로 검증한다. 2026-11-25 미국 동부시간 04:14:59 기준 원안의 만료는 지나지 않았으나, 이 시계와 2026-11-24까지의 일봉 255개만으로 당일 거래 여부나 진입 조건 충족을 확인할 수 없다.","risk_condition_ko":"297.8 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"255.15~255.56달러 회복과 재시험, 261.56~262.48달러 저항의 지지 전환 여부를 관찰한다. 하락 시 250.53달러 회복 여부와 245.31~245.59달러 지지를 확인한다. 주요 지지 붕괴 후 229.36달러는 과거 저점 참고치이며 재매수 신호가 아니다. / 2026-11-25 미국 동부시간 04:09:32 판단 기준으로 원안의 2026-12-02T23:59:59-05:00 시한은 지나지 않았다. 다만 이번 결정에서는 이를 약 1주의 관찰 시한으로만 유지한다. 미국 동부시간 03:58 조회는 전일 종가를 반복했고 체결이 없었다. 실제 정규장 일정과 신선한 체결을 별도로 확인하며 관찰 시한을 자동 연장하지 않는다.","risk_condition_ko":"250.53 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"214.70~214.80달러는 첫 저항 관찰 구간이다. 이 구간의 단독 돌파가 아니라 216.52달러 상회 종가와 다음 실제 정규장 지지를 확인한다. / 2026-11-24 나스닥 약세와 다우 상승의 엇갈림은 시장 폭 개선의 증거가 아니다. 업종별 상승 참여와 분배금 포함 VOO 대비 상대 총수익률을 직접 확인한다.","risk_condition_ko":"211.28 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1,125~1,133달러 정규장 지지 시험, 같은 날 1,174달러 이상 종가, 다음 실제 정규장의 재시험 유지와 1,174~1,180달러 신선한 호가를 순서대로 확인한다. / 1,125달러 이탈 후 1,092.38달러는 하방 변동성 기준으로만 본다. 1,282.60~1,295.63달러에서 보상 대비 위험을 다시 평가하고, 상단 회복 후 1,328.93~1,341.98달러를 관찰한다.","risk_condition_ko":"1,125 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"275.36~276.03달러 회복은 초기 안정화 신호일 뿐 매수 조건이 아니다. / 직전 완료 정규장보다 거래량이 늘어난 날 285.14달러를 초과해 마감한 뒤, 다음 실제 거래일에 284.74~285.14달러 재시험에서 지지가 유지되는지 확인한다.","risk_condition_ko":"272.31 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"69.28달러를 지킨 뒤 2026-11-24 저점인 70.13달러를 회복하고 재시험에서도 유지하면 반등 후보로 본다. 그 자체는 매수 신호가 아니다. / 2026-12-02까지 돌파·재시험·다음 실제 정규장 지지와 최신 이동평균을 재검토한다. 80.35달러는 중기 추세 참고선이며 진입 요건이나 목표가가 아니다.","risk_condition_ko":"69.28 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"$1,061.55~$1,066.23 테스트와 같은 날 $1,066.23 초과 종가가 확인되면 바로 다음 실제 거래 세션에서 $1,066.23 지지와 $1,066.23~$1,068.50 내 가격을 확인한다. / $1,094.75 초과 종가가 나오면 평소보다 강한 거래량과 이후 안착 여부를 살피되, 신규 매수로 연결하지 않는다.","risk_condition_ko":"1,053.55 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"정규장에서 579.79달러를 넘은 뒤 거래 참여가 개선된 상태로 그 위를 유지하는지 본다. 이는 추세 점검 신호이지 매수 신호가 아니다. 상위 저항은 586.30~588.54달러, 다음 기준은 11월 12일 고점 596.92달러다. / 기술주가 반등할 때도 BRK-B가 미국 주식시장 대비 상대 강세를 유지하는지 확인한다. 기사 25건 중 22건이 같은 매체에 집중됐으며 실제 자금 흐름이나 투자자 포지션은 확인되지 않았다.","risk_condition_ko":"565.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"WMT","display_name":"WMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"132.42달러 초과 정규장 종가와 직전 20거래일 평균 초과 거래량을 확인한 뒤, 바로 다음 실제 정규장에서 131.82~132.42달러 지지를 확인한다. 133.61달러와 134.84달러는 저항 참고선이지 별도 매수 신호가 아니다. / 실제 정규장 일정·조기 종료 여부, 거래정지 여부와 호가 신선도를 확인한다. 계획 본문의 고정 시각 없음과 별도 항목의 10:30은 서로 충돌하므로 집행 전에 재확인한다. 10:30 자체는 진입 신호가 아니다.","risk_condition_ko":"131.82 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"LIN","display_name":"LIN","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"519.64달러 초과 정규장 종가가 나오면 다음 실제 거래일에 같은 가격의 재시험 지지와 522.93달러까지의 비용 후 손익비를 확인한다. 보상이 부족하면 추격하지 않는다. / 511.78달러 아래에서 반등이 막히면 매수를 계속 보류하고 506.42달러와 500.26달러를 차례로 관찰한다.","risk_condition_ko":"500.26 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"직전 20거래일 평균을 넘는 거래량으로 419.00달러를 초과해 마감한 뒤 다음 실제 정규장에서 418.18~419.00달러의 지지 전환을 확인한다. 실제 거래 일정과 거래 가능 상태, 최신 정규장 호가는 별도로 확인한다. / 425.00~425.99달러와 430.18~430.99달러의 가격·거래량 반응을 관찰한다. 441.41달러는 이전 고점 참고치이고, 393.27~395.58달러는 하방 관찰 구간이지 매수나 손절 연장 기준이 아니다.","risk_condition_ko":"407.4 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"VRT","display_name":"Vertiv","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"168.27~173.82달러 구간 상단을 정규장 종가로 회복한 뒤 첫 되밀림에서 구간 지지를 확인한다. / 180.53달러 상회 종가와 다음 실제 정규장 재시험을 확인한 뒤 188.38달러·199.24달러까지의 비용 반영 손익비를 다시 계산한다.","risk_condition_ko":"163.48 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"302.93달러 초과 마감에 뚜렷한 거래량 증가가 동반된 뒤 다음 정규장 재시험에서 지지하는지 확인한다. / 291.25~291.34달러를 시험한 날 291.34달러를 회복해 마감하고 다음 정규장에도 그 수준을 지키는지 확인한다.","risk_condition_ko":"288.45 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"KO","display_name":"KO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"97.00~97.08달러 시험과 같은 날 97.08달러 초과 종가 이후 바로 다음 정규장의 97.08~97.20달러 및 순손익비를 확인한다. / 98.94달러 초과 마감과 다음 정규장의 지지 여부를 관찰한다. 99.30~99.61달러 저항을 넘어 지지로 전환하기 전에는 100.56달러를 기본 수익 목표로 삼지 않는다.","risk_condition_ko":"94.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"JNJ","display_name":"JNJ","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"268.08~271.15달러에서 매도 압력이 둔화하며 마감하는지, 직후 실제 다음 정규장에서 최신 호가가 지지와 비용 반영 손익비 기준을 함께 충족하는지 확인한다. / 275.09달러 회복·유지와 280.52~280.62달러 저항대 돌파 후 다음 정규장 지지는 재평가 신호다. 285.57달러와 288.81달러는 후속 저항이며 이익실현 주문가가 아니다.","risk_condition_ko":"266.39 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"WELL","display_name":"WELL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"239.93달러 이상 종가와 다음 정규장의 238.59~239.93달러 지지 재확인을 순서대로 관찰한다. 유효기한은 2026년 12월 2일 미국 동부시간 17:00이며, 조건이 확인되지 않으면 연장하지 않고 만료시킨다. / 244.64~245.39달러를 회복해 유지하면 반등 신뢰도가 높아지지만 추가 매수 신호는 아니다.","risk_condition_ko":"238.59 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"651.53달러 상회 정규장 종가와 거래량 참여 개선을 확인한 뒤, 다음 실제 정규장에서 648.48~648.66달러 지지와 648.66~649.70달러 회복을 순서대로 확인한다. 정규장 일정과 거래 상태, 최신 호가를 확인할 수 없으면 진입하지 않는다. / 분기보고서·수시공시 및 내부자 신고 4건은 색인에서만 확인됐다. 공식 원문과 공개 시점, 재무제표 통화와 표시 단위, 주당이익의 주식 기준 및 해당 시 미국예탁증서와 보통주 간 환산비율을 확인할 때까지 재무 금액·주당이익·가치평가 배수는 비교하지 않는다. 신고만으로 실제 내부자 매도나 가이던스 변화를 단정하지 않는다.","risk_condition_ko":"642.56 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"94.49~95.02달러 재시험, 같은 정규장 95.02달러 이상 종가, 직후 정규장의 95.02~96.13달러 구간 하단 지지를 순서대로 확인한다. / 99.44~100.00달러 회복 뒤 101.15달러 초과 종가와 다음 정규장 안착을 관찰한다. 이는 별도 증액 검토 조건이지 스타터의 대체 신호가 아니다.","risk_condition_ko":"94.49 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"169.34~169.56달러 눌림 시험, 같은 정규장의 169.56달러 상회 종가, 바로 다음 정규장의 지지를 순서대로 확인한다. 173.59달러 위 거래량 동반 종가와 다음 정규장 지지는 관찰 신호이며 174.32달러를 넘겨 추격하지 않는다. / 2026년 11월 25일 05:52:45 미국 동부시간 기준 2026년 12월 2일 18:00 미국 동부시간 만료는 지나지 않았다. 이 시각은 약 일주일의 재검토 기한이지 거래소 마감이나 진입 허가가 아니다. 공식 거래 일정, 실제 거래 가능 상태와 최신 정규장 시세는 미확인이다. 고정 시각을 두지 않는 본문과 10:30 필드가 충돌하므로 최종 계획에는 고정 시각을 두지 않고 주문 전 해당 제한과 실제 일정을 재확인한다.","risk_condition_ko":"169.34 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"HD","display_name":"HD","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단 시점 이후 실제 정규장 저가가 343.20~345.58달러에 들고 같은 날 종가가 345.58달러를 넘은 뒤, 바로 다음 실제 정규장에서 345.58달러 지지와 345.58~347.00달러의 신선한 호가 확인 / 354.81~356.90달러 저항 통과와 362.44달러 위 종가 및 다음 거래일 지지 관찰. 별도 매수 조건은 아님","risk_condition_ko":"343.2 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"INSM","display_name":"INSM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"다음으로 확인되는 정규장에서 거래 상태와 실제 양방향 호가를 확인해 보도 대가 175.00달러와의 가격 차이를 다시 계산한다. 175.00달러 이상에서는 공식 대가 상향 근거 없이 신규 매수하지 않고 잔여 거래 노출을 낮춘다. / 가격 차이가 넓어지면 먼저 계약 훼손 때문인지 확인한다. 원문과 종결 일정의 근거를 확보하고, 실제 매수 가능 호가에서 거래비용과 자금이 묶이는 기간을 반영한 보상이 같은 기간의 현금보다 충분하며 119.80달러 아래로 급락해도 기존 위험 예산을 지킬 수 있을 때만 새 소규모 진입안을 심사한다. 현재 승인된 조건부 진입은 없다.","risk_condition_ko":"170.15 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"SNDK","display_name":"SNDK","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"75.67달러 위 정규장 종가와 다음 정규 거래 세션의 74.83~75.67달러 재시험 방어는 반등 관찰 신호일 뿐 매수 신호가 아니다. / 83.82달러와 96.19~99.07달러 저항대를 통과한 뒤 102.62달러 위 종가와 다음 정규 거래 세션의 지지를 확인한다. 회사의 판매단가·마진 근거가 함께 개선될 때만 진입을 재평가한다.","risk_condition_ko":"72 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-26T03:58:04.791734+09:00",
  "as_of": "2026-11-25T17:54:54+00:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
