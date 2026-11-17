# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-17T13:48:41.360110+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261117T175035_local-scheduler-us-full",
  "producer_finished_at": "2026-11-17T21:40:03.631486+09:00",
  "analysis_run_id": "20261117T175035_local-scheduler-us-full",
  "analysis_completed_at": "2026-11-17T21:02:49.923284+09:00",
  "analysis_trade_date_oldest": "2026-11-16",
  "analysis_trade_date_latest": "2026-11-16",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-17T08:51:09+00:00",
  "market_data_latest_at": "2026-11-17T06:30:00-05:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-17T21:03:20.502988+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-17T21:03:20.502988+09:00",
    "run_started_at": "2026-11-17T17:50:35.386672+09:00",
    "run_finished_at": "2026-11-17T21:40:03.631486+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23558239,
    "total_market_value_krw": 21528954,
    "total_unrealized_pnl_krw": -2029285,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 112233,
    "total_equity_krw": 22617439
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 544239,
      "current_price_krw": 497955,
      "market_value_krw": 5975460,
      "unrealized_pnl_krw": -555413
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 291704,
      "current_price_krw": 292365,
      "market_value_krw": 3216015,
      "unrealized_pnl_krw": 7264
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 423099,
      "current_price_krw": 378770,
      "market_value_krw": 2272624,
      "unrealized_pnl_krw": -265975
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1875327,
      "current_price_krw": 1791583,
      "market_value_krw": 1791583,
      "unrealized_pnl_krw": -83744
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 554555,
      "current_price_krw": 453579,
      "market_value_krw": 1360738,
      "unrealized_pnl_krw": -302929
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 266581,
      "current_price_krw": 210596,
      "market_value_krw": 1263577,
      "unrealized_pnl_krw": -335912
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 134182,
      "current_price_krw": 134260,
      "market_value_krw": 1208348,
      "unrealized_pnl_krw": 703
    },
    {
      "ticker": "GEV",
      "name": "GE 버노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1469220,
      "current_price_krw": 1034625,
      "market_value_krw": 1034625,
      "unrealized_pnl_krw": -434595
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 363672,
      "current_price_krw": 470967,
      "market_value_krw": 941935,
      "unrealized_pnl_krw": 214591
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1416449,
      "current_price_krw": 1882496,
      "market_value_krw": 820890,
      "unrealized_pnl_krw": 203226
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 568209,
      "current_price_krw": 450626,
      "market_value_krw": 450626,
      "unrealized_pnl_krw": -117583
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 661098,
      "current_price_krw": 437605,
      "market_value_krw": 437605,
      "unrealized_pnl_krw": -223493
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 135874,
      "current_price_krw": 102100,
      "market_value_krw": 408403,
      "unrealized_pnl_krw": -135093
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 346886,
      "current_price_krw": 346525,
      "market_value_krw": 346525,
      "unrealized_pnl_krw": -361
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":368.0,"market_data_asof":"2026-11-17T05:05:00-05:00","session_vwap":370.8485449572481,"relative_volume":0.10941361495433895,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"잠정 지지 범위 367.46–372.46을 정규장 종가로 관찰한다. 장전에서 나온 하단을 확립된 정규장 지지로 간주하지 않는다. / 385.47 위 종가는 초기 안정화 신호일 뿐 중기 추세 전환이나 매수 승인이 아니다.","risk_condition_ko":"367.46 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T05:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T05:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":334.3053,"market_data_asof":"2026-11-17T04:10:00-05:00","session_vwap":337.144,"relative_volume":0.0015634205474615403,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"ETN 347.30 회복과 지지 전환은 관찰 신호이며 단독 매수 신호가 아니다. / ETN 358.48 위 종가와 다음 확인 가능한 정규거래일의 355.00~358.48 지지에서 투자 판단을 재심사한다. 신규 진입은 실제 가격·다음 저항·손절·비용으로 다시 평가한다.","risk_condition_ko":"336.2 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T04:10:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T04:13:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":155.269,"market_data_asof":"2026-11-17T04:40:00-05:00","session_vwap":156.09873844025185,"relative_volume":0.106280277588904,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"156.14 회복과 158.17 상회는 초기 안정화 관찰 신호이며 독립적인 매수 신호가 아님 / 163.20 상회 일봉 마감 후 다음 실제 거래일 162.85~163.20 지지 유지 또는 재돌파 시 투자 적합성 재검토","risk_condition_ko":"154.23 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T04:40:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T04:43:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":759.01,"market_data_asof":"2026-11-17T04:10:00-05:00","session_vwap":765.5672897196262,"relative_volume":0.00983904879386595,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"760.00과 747.00–750.00 방어 여부를 후속 일봉으로 확인한다. 바닥 형성이나 747.00 붕괴를 미리 선언하지 않는다. / 800.32 상회 종가 후 783.62–800.32 지지 확인 시 회복 검토를 시작한다. 자동 매수하지 않는다.","risk_condition_ko":"747 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T04:10:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T04:13:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":281.29,"market_data_asof":"2026-11-17T04:20:00-05:00","session_vwap":283.13224491042655,"relative_volume":0.03152273740761404,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"294.14 상회 종가로 290.05–294.14 회복 구간을 넘고 다음 확인된 거래일에 지지가 유지되면 조기 재검토한다. 이는 자동 매수 신호가 아니다. / 304.97 상회 종가와 다음 거래일 지지가 확인되면 실제 보호청산 거리와 316.60–322.66 저항을 비교해 신규 매수 가능성을 다시 평가한다.","risk_condition_ko":"276.92 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T04:20:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T04:23:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":320.55,"market_data_asof":"2026-11-17T08:51:09+00:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"315.00~318.03 지지 유지와 315.00 하회 후 회복 실패를 구분한다. 지지 유지 자체는 매수 신호가 아니다. / 공격·중립 분석가의 조기 재평가 제안을 반영해 332.36 회복·지지 또는 새로운 공식 사업 근거 발생 시 즉시 분석을 갱신한다. 자동 매수는 하지 않는다.","risk_condition_ko":"315 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T08:51:09+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T08:54:09+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":333.4,"market_data_asof":"2026-11-17T08:51:27+00:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"327.80–329.51에서 안정화와 저점 상승을 관찰한다. 구간 접촉만으로 매수하지 않는다. / 337.74 초과 종가 이후 다음 확인된 거래일에 335.17–337.74 구간이 지지로 유지되면 재심사한다.","risk_condition_ko":"344.78 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T08:51:27+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T08:54:27+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":76.4,"market_data_asof":"2026-11-17T04:15:00-05:00","session_vwap":76.637341529005,"relative_volume":0.011728727205152514,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"77.21 초과 종가와 76.89–77.21 재시험 지지를 관찰한다. 초기 회복 신호일 뿐 매수 지시는 아니다. / 78.33–78.88 추세 복구 구간을 갱신하고, 79.39–79.75 및 81.91–81.97 저항을 관찰한다. 회복 후에도 투자 조건을 다시 평가하기 전에는 소액 매수를 허가하지 않는다.","risk_condition_ko":"75.96 이하 하락, 다음 거래일 확인 후 (위험 축소에는 거래량 증가가 필요하지 않다.) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T04:15:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T04:18:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":218.18,"market_data_asof":"2026-11-17T04:40:00-05:00","session_vwap":218.09548656404905,"relative_volume":0.007293164642618363,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"217.36–218.42 지지 시험, 종가 218.42 이상 회복, 다음 실제 정규장 지지 유지와 218.42–218.75의 실행 가능 가격을 순서대로 확인한다. / 219.68–220.11 회복 구간과 221.25–221.90, 222.82–222.93, 223.50–224.20 저항에서 가격 반응을 재평가한다. 먼 상단 가격만으로 매수 타당성을 판단하지 않는다.","risk_condition_ko":"214.75 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T04:40:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T04:43:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1432.99,"market_data_asof":"2026-11-17T04:25:00-05:00","session_vwap":1429.8380700594844,"relative_volume":0.009923892101235007,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1419–1428의 일별 지지 반응을 관찰하고 실패 시 1401–1409를 재평가한다. 가격 접촉만으로 매수하지 않는다. / 1401–1409의 종가 지지와 다음 확인된 거래일 유지가 나오면 일관된 손절·수량·목표를 이용해 신규 진입 경제성을 다시 계산한다.","risk_condition_ko":"1,449 이상 도달, 종가 확인 후 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T04:25:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T04:28:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":257.75,"market_data_asof":"2026-11-17T08:51:09+00:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"254.80~256.85 지지 시험 → 257.75 위 새로운 일봉 마감 → 다음 실제 거래가능 세션의 256.85~257.75 재지지 순서를 확인한다. / 262.40~262.92 회복과 그 이후 실패 여부를 구분한다. 266.17~270.87 저항이 남아 있으므로 회복만으로 추가 매수하지 않는다.","risk_condition_ko":"254.8 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T08:51:09+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T08:54:09+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":352.78,"market_data_asof":"2026-11-17T08:51:27+00:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"350.29–351.31 시험과 351.31 이상 종가 회복 이후 다음 검증된 정규장에서 지지 유지 및 비용 차감 후 손익비를 재확인한다. 비용 전 약 350.56 상한도 비용을 반영해 낮추며 구간 위로 가격이 뛰면 추격하지 않는다. / 355.75–357.13 첫 저항에서 거부되면 359.37 도달 가정을 재평가하고 추가 위험을 늘리지 않는다. 359.37–360.83은 확정 수익 목표가 아닌 주요 저항이다.","risk_condition_ko":"350.29 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T08:51:27+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T08:54:27+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.5729,"market_data_asof":"2026-11-17T05:00:00-05:00","session_vwap":100.57497754695615,"relative_volume":0.105058570540125,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"100.52~100.56 구간의 정규장 종가와 다음 실제 거래일의 100.52 지지 유지. 운용·비용·유동성 검증을 통과한 경우에만 100.56 이하 소규모 진입을 검토한다. / 100.58 상회 종가와 다음 거래일 유지 여부는 관찰만 한다. 독립적인 돌파매수나 추격매수 근거로 사용하지 않는다.","risk_condition_ko":"100.47 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T05:00:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T05:03:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1310.25,"market_data_asof":"2026-11-17T04:35:00-05:00","session_vwap":1335.7250673854448,"relative_volume":0.01978326042884883,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"지지대 시험, 1286.19 이상 완료 종가, 후속 세션의 1280.00~1286.19 재시험을 순서대로 확인한다. 지지 유지와 비용·계좌 점검까지 충족해야 최초분을 검토한다. / 1337.78 상회 종가와 후속 지지 전환은 별도 재검토 신호다. 1338 진입·1275 손절·1390 목표의 약 0.83 보상·위험 비율은 추격매수 근거로 부족하다.","risk_condition_ko":"1,275.47 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T04:35:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T04:38:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"KO","display_name":"KO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":99.3,"market_data_asof":"2026-11-17T19:29:27+09:00","session_vwap":99.33078613048046,"relative_volume":0.011380256298340425,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"관찰 구간의 일봉 지지와 다음 세션 유지, 실제 체결 가능 범위 97.07~97.42 및 비용 후 보상·위험 최소 1.5배를 함께 확인한다. / 100.00~100.56에서 반복 실패와 탄력 둔화가 함께 나타나면 부분 이익실현을 재검토한다. 돌파 후 100.56 미만 종가는 신규 돌파 매수 배제 조건이며 단독 자동 청산 신호는 아니다.","risk_condition_ko":"97.07 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T19:29:27+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T19:32:27+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1115.0,"market_data_asof":"2026-11-17T05:55:00-05:00","session_vwap":1112.8013732221677,"relative_volume":0.016859901316574142,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"눌림 경로는 1104.89~1109.50 시험, 1109.50 초과 종가, 다음 확인된 정규장에서 1104.89 지지 유지 또는 회복의 순서로 확인한다. / 돌파 경로는 1117.00 초과 종가와 다음 확인된 정규장의 1117.00 재시험 성공을 요구한다. 재시험 없이 크게 오른 갭은 추격하지 않는다.","risk_condition_ko":"1,104.89 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T05:55:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T05:58:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":294.7,"market_data_asof":"2026-11-17T05:35:00-05:00","session_vwap":294.5051724137931,"relative_volume":0.0022222868764839605,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-17부터 2026-11-24까지 새로 완료된 거래일마다 지지대 시험, 292.84 초과 재탈환, 다음 완료 거래일의 저가·종가 291.93 이상 유지 순서를 점검한다. / 모든 선행 확인 이후의 재시험에서만 291.93–292.30 및 더 낮은 비용 조정 상한, 유효한 288.24 손절, 비용 후 수익위험비 2 이상을 함께 적용한다.","risk_condition_ko":"291.93 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T05:35:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T05:38:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WELL","display_name":"WELL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":244.66,"market_data_asof":"2026-11-17T04:00:00-05:00","session_vwap":251.0,"relative_volume":6.5929124018577644e-06,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"242.90–243.70 시험 후 243.70 이상 회복 종가를 확인한다. 2026-11-16 종가만으로 이 순서가 충족됐다고 보지 않는다. / 다음 확인 거래일에 242.90 지지가 유지되고 242.90–243.23 안에서 비용 반영 최소 1:1 조건을 만족하는 가격이 나올 때만 소규모 초도 편입을 검토한다. 위로 갭 상승하면 추격하지 않는다.","risk_condition_ko":"239.85 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T04:00:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T04:03:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":103.47,"market_data_asof":"2026-11-17T06:05:00-05:00","session_vwap":103.58356545961003,"relative_volume":0.0017682825135834337,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"100.02–101.44 시험, 101.44 이상 일봉 종가, 이후 정규장의 100.02–101.00 지지 재시험 순서를 추적한다. / 106.20 상향 종가 돌파에 일별 거래 참여 확대와 다음 정규장 지지 유지가 동반되면 돌파 전략을 새로 평가한다. 자동 추가 매수는 아니다.","risk_condition_ko":"100.02 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T06:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T06:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LIN","display_name":"LIN","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":523.84,"market_data_asof":"2026-11-17T05:50:00-05:00","session_vwap":522.4195519348269,"relative_volume":0.004743647973980462,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-17 또는 이후 520.75~522.36 재시험과 522.36 이상 종가, 다음 실제 거래일의 520.75 지지 유지 여부. / 첫 매수 후보 가격이 520.75~521.70 안에 있고 비용 반영 후 최소 보상 기준까지 충족하는지 확인. 충족하지 않으면 매수하지 않는다.","risk_condition_ko":"517.84 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T05:50:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T05:53:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":425.14,"market_data_asof":"2026-11-17T06:05:00-05:00","session_vwap":424.9560047562426,"relative_volume":0.00476809125298904,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"420.02~422.09 시험, 422.09 이상 회복 종가, 다음 확인된 거래일 지지 유지, 420.02~421.00 체결 가능 순서를 관찰한다. 마지막 가격 재진입이 지지 유지인지 재차 붕괴인지 구분한다. / 430.18~430.99 공급과 435.76~435.95 및 441.41 접근 시 거부·안착과 탄력을 재평가한다. 보수·중립 분석가가 강조한 중간 저항을 무시하고 먼 고점만으로 보상을 계산하지 않는다.","risk_condition_ko":"420 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T06:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T06:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":591.42,"market_data_asof":"2026-11-17T05:30:00-05:00","session_vwap":590.9123048668504,"relative_volume":0.00838756076215893,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-24T23:59:59-05:00까지 완료된 거래일 자료로 매일 점검하고, 그때 보유·수익실현·매수 보류 결정을 재평가한다. 이 시각은 거래소 마감이나 자동 갱신 시점이 아니다. / 595.83–596.92에서 분할 수익실현 조건을 확인한다. 강한 돌파가 나타나면 미체결 후속 매도와 재진입 가능성을 재심사하되 자동 매수하지 않는다.","risk_condition_ko":"595.83 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T05:30:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T05:33:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":661.9375,"market_data_asof":"2026-11-17T05:45:00-05:00","session_vwap":659.9062068965517,"relative_volume":0.004463654295036851,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"MA 649.82~655.00 시험과 655.00 이상 새 일봉 종가 회복 후 다음 확인된 거래일의 654.00~655.00 지지 재시험. 가격·원문 검토·비용·포트폴리오 여력이 모두 충족돼야 소액 첫 진입이 가능하다. / MA 668.31 회복과 672.68~673.50 돌파·재시험 및 일거래량 개선은 관찰 신호이며 자동 추격매수 승인이 아니다.","risk_condition_ko":"649.82 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T05:45:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T05:48:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WMT","display_name":"WMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":128.42,"market_data_asof":"2026-11-17T05:25:00-05:00","session_vwap":128.24377353504659,"relative_volume":0.013826858997419726,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"125.87~126.15 지지 시험, 126.15 이상 종가, 다음 확인된 정규장 지지 유지 순서를 추적한다. 구간 위로 벌어진 가격을 추격하지 않는다. / 129.85 회복은 초기 개선일 뿐이며 130.94~131.82 공급 구간을 별도로 점검한다.","risk_condition_ko":"125.87 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T05:25:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T05:28:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":172.39,"market_data_asof":"2026-11-17T06:25:00-05:00","session_vwap":172.5979951607328,"relative_volume":0.005608185496638145,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"170.73–171.93 안정 마감 후 다음 확인된 거래일의 170.73 지지와 170.73–170.78-C 적격 체결을 관찰한다. / 170.73 지지 이탈, 167.75 손절, 173.57 돌파 실패 조건을 신규 매수 조건과 별도로 감시한다.","risk_condition_ko":"170.73 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T06:25:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T06:28:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GE","display_name":"GE","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":324.5,"market_data_asof":"2026-11-17T06:30:00-05:00","session_vwap":324.3802521008403,"relative_volume":0.001718443780922173,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"분석 기준 시점 이후의 새로운 정규장 지지 시험, 323.30 이상 종가, 후속 거래일 지지 유지와 321.28–323.30 내 재시험을 순서대로 확인한다. 제공된 지연 장전 관측은 이를 충족하지 않는다. / 새 일봉마다 검토하고 다음 1–3개의 확인된 거래일 안에 진입 가능성을 재평가한다. 계획 만료는 2026-11-24T18:00:00-05:00이다. 제공된 실행 시각보다 뒤이지만 거래일 일정이나 진입 충족을 뜻하지 않는다. 이 시각은 검토 기한이지 거래소 폐장 시각이 아니다.","risk_condition_ko":"321.28 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T06:30:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T06:33:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SO","display_name":"SO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":94.62,"market_data_asof":"2026-11-17T05:10:00-05:00","session_vwap":94.60402684563758,"relative_volume":0.0014219238668376523,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"93.15의 첫 지지 반응은 관찰만 한다. 그 가격 도달만으로 매수하지 않는다. / 92.57~92.80 재시험, 종가 92.80 이상 회복, 다음 실제 거래 세션의 92.57 방어와 구간 내 체결 가능성을 순서대로 확인한다. 핵심 조달조건과 계좌 위험 확인도 필요하다.","risk_condition_ko":"92.57 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T05:10:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T05:13:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CRWV","display_name":"CRWV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":48.79,"market_data_asof":"2026-11-17T05:20:00-05:00","session_vwap":49.49969559531829,"relative_volume":0.07804039988283692,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"53.13 초과 종가 이후 다음 확인된 거래일에 52.92–53.13 지지와 일별 거래 참여 개선을 확인하면 신규 배분 심사를 시작한다. 자동 매수는 아니다. / 48.02 미만 종가에서 조건부 추가 매도를 한 번 집행하고, 이후에도 해당 수준 아래에서 마감하면 잔여 전술 물량을 청산한다.","risk_condition_ko":"48.02 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T05:20:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T05:23:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"COHR","display_name":"Coherent","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":201.35,"market_data_asof":"2026-11-17T05:05:00-05:00","session_vwap":202.08606509223358,"relative_volume":0.03508436672555747,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"196.12 유지 여부를 우선 확인한다. 이탈 시 187.16, 179.04, 하단 160.23·상단 169.76은 관찰 지점일 뿐 매도를 미룰 근거가 아니다. / 회복 구간 하단 208.15·상단 215.48과 다음 거래일 지지를 확인한다. 209.31은 과거 거래량가중이동평균이며 일중 거래량가중평균가격으로 대체하지 않는다.","risk_condition_ko":"196.12 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T05:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T05:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CAT","display_name":"CAT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":566.37,"market_data_asof":"2026-11-17T05:05:00-05:00","session_vwap":568.2291280148423,"relative_volume":0.011161906774504135,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"568.25 지지 유지 여부와 이탈 후 다음 실제 정규 거래일 종가의 회복 여부. / 550.81~554.61 저점 구간 재시험과 550.81 미만 종가 여부.","risk_condition_ko":"568.25 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-17T05:05:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-17T05:08:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-17T03:20:28.227571+09:00",
  "as_of": "2026-11-16T11:13:00-05:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
