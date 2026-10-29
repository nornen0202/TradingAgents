# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-29T05:54:04.521432+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261029T124921_manual-us-failed-recovery",
  "producer_finished_at": "2026-10-29T14:14:07.115277+09:00",
  "analysis_run_id": "20261029T124921_manual-us-failed-recovery",
  "analysis_completed_at": "2026-10-29T13:15:09.675150+09:00",
  "analysis_trade_date_oldest": "2026-10-28",
  "analysis_trade_date_latest": "2026-10-28",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-28T18:00:00-04:00",
  "market_data_latest_at": "2026-10-28T19:55:00-04:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-29T13:15:38.892216+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-29T13:15:38.892216+09:00",
    "run_started_at": "2026-10-29T12:49:21.009364+09:00",
    "run_finished_at": "2026-10-29T14:14:07.115277+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23581184,
    "total_market_value_krw": 23724266,
    "total_unrealized_pnl_krw": 143082,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 107064,
    "total_equity_krw": 24807982
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 544769,
      "current_price_krw": 587317,
      "market_value_krw": 7047806,
      "unrealized_pnl_krw": 510573
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 291988,
      "current_price_krw": 290551,
      "market_value_krw": 3196068,
      "unrealized_pnl_krw": -15807
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 423511,
      "current_price_krw": 434150,
      "market_value_krw": 2604903,
      "unrealized_pnl_krw": 63832
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 266841,
      "current_price_krw": 287812,
      "market_value_krw": 1726873,
      "unrealized_pnl_krw": 125826
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1877154,
      "current_price_krw": 1618553,
      "market_value_krw": 1618553,
      "unrealized_pnl_krw": -258601
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 555095,
      "current_price_krw": 525005,
      "market_value_krw": 1575016,
      "unrealized_pnl_krw": -90271
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 134313,
      "current_price_krw": 134565,
      "market_value_krw": 1211088,
      "unrealized_pnl_krw": 2267
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1470651,
      "current_price_krw": 1173311,
      "market_value_krw": 1173311,
      "unrealized_pnl_krw": -297340
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 364026,
      "current_price_krw": 459460,
      "market_value_krw": 918920,
      "unrealized_pnl_krw": 190868
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1417827,
      "current_price_krw": 1721555,
      "market_value_krw": 750710,
      "unrealized_pnl_krw": 132445
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 661742,
      "current_price_krw": 659851,
      "market_value_krw": 659851,
      "unrealized_pnl_krw": -1891
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 568762,
      "current_price_krw": 470123,
      "market_value_krw": 470123,
      "unrealized_pnl_krw": -98639
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 136006,
      "current_price_krw": 107705,
      "market_value_krw": 430823,
      "unrealized_pnl_krw": -113202
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 347224,
      "current_price_krw": 340221,
      "market_value_krw": 340221,
      "unrealized_pnl_krw": -7003
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":292.4,"market_data_asof":"2026-10-28T18:25:00-04:00","session_vwap":324.6159066859664,"relative_volume":1.6440476914773718,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"292.40 관측의 시각 2026-10-28T18:25:00-04:00을 신선한 집행 가능 시세와 대조한다. 판단 시각 2026-10-28T18:44:24.542969-04:00에는 약 19분 25초 지난 관측이며, 보고된 수집 지연 293초와 현재 경과시간은 다르다. / 공시 색인 9건의 원문, 재무제표 표시통화·단위·회계기간·주식 및 주당이익 기준, 예탁증서 적용 여부와 해당 시 교환비율을 확인한다. 재무자료가 2026-10-28T22:35:44.946227+00:00 이전 공개됐는지도 검증한다. 연구일 이후 조회된 자료를 사전 이용 가능 자료로 간주하지 않는다.","risk_condition_ko":"316.6 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T18:25:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T18:28:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":431.573,"market_data_asof":"2026-10-28T19:20:00-04:00","session_vwap":438.6523741235945,"relative_volume":0.3272622995658735,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"430.93–434.29에서 안정화 후 회복과 재시험을 확인한다. 단순 접촉은 매수 신호가 아니다. / 445.50 위 안착과 재시험을 관찰하되 실제 출구 기준 순보상위험이 부족하면 돌파해도 매수하지 않는다.","risk_condition_ko":"430.93 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T19:20:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T19:23:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1186.34,"market_data_asof":"2026-10-28T18:45:00-04:00","session_vwap":1209.1529384455418,"relative_volume":0.699374860077777,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"공식 실적 일정, 자료 공개시각, 거래소 달력, 실제 거래 가능 상태 및 시세 신선도를 확인한다. 2026-10-28 연구 기준일을 유지한다. / 1224.14와 갱신된 1236.88의 회복·재지지, 실제 장중 거래량가중평균가격 지지, 동시간대 상대거래량 1.2 이상과 비용 후 손익비 2:1 이상을 함께 검토한다. 충족만으로 자동 매수하지 않는다.","risk_condition_ko":"1,188.93 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T18:45:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T18:48:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":865.33,"market_data_asof":"2026-10-28T18:20:00-04:00","session_vwap":874.3799401146669,"relative_volume":1.369560379257532,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"다음 적격 정규장과 거래 상태·유동성·호가 신선도를 확인한다. 현재 승인된 신규 주문이나 연장할 진입 만료시각은 없다. / 901.07 위 종가와 성공적인 재확인, 실시간 거래량가중평균가격 지지, 동일 자료원의 동시간 대비 상대거래량 1.2 이상을 함께 관찰한다. 충족해도 순손익비와 위험예산 검토 전에는 매수하지 않는다.","risk_condition_ko":"889.42 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T18:20:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T18:23:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":488.88,"market_data_asof":"2026-10-28T18:00:00-04:00","session_vwap":494.91062027562936,"relative_volume":0.35130416697727745,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"공식 거래일·정규장 시간·거래정지 여부와 최신 실행 호가 확인 / 갱신된 512.73 기준선 위 정규장 종가와 다음 확인된 거래일 첫 30~60분 지지 유지","risk_condition_ko":"472.43 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T18:00:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T18:03:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":213.83,"market_data_asof":"2026-10-28T18:55:00-04:00","session_vwap":216.5317256882504,"relative_volume":0.6713558932745046,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"NVDA 동일 정규장 기준 214.47과 210.18~212.85 지지 유지 여부 확인. / NVDA 217.51~219.99 회복 실패를 확인하면 전술 비중 축소. 장후 가격만으로 실패를 확정하지 않는다.","risk_condition_ko":"217.51 이하 하락, 장중 확인 시 리스크 축소 · 추가 조건 확인 필요: 217.51~219.99 회복 시도 실패를 최신 정규장 자료로 확인하면 전술 비중을 축소한다. 계좌 한도 초과분 축소에는 이 구간 도달이 필요하지 않다.","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T18:55:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T18:58:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1301.074,"market_data_asof":"2026-10-28T18:45:00-04:00","session_vwap":1290.027122888507,"relative_volume":0.4643755844082947,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"LLY 공식 실적 일정·발표자료, 거래소 일정과 최신 정규장 실행 시세를 우선 확인한다. / 1260.34~1265.41에서 하락 중단 후 1265.41 재회복, 연속 완성봉 지지와 정규장 거래량가중평균가격 상회를 관찰한다.","risk_condition_ko":"1,251 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T18:45:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T18:48:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":80.26,"market_data_asof":"2026-10-28T18:20:00-04:00","session_vwap":80.07318844921622,"relative_volume":0.35426017837107987,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"80.75 회복과 지지 재시험, 이후 81.51 초과 정규장 종가를 확인한다. 단발성 체결이나 호가 차이에 따른 통과는 제외한다. / 81.43~81.51 및 82.60~83.11의 반등 거부, 79.51과 78.63의 종가 이탈을 구분하여 감시한다. 어느 조건도 이미 발생했다고 판단하지 않는다.","risk_condition_ko":"79.51 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T18:20:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T18:23:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":344.4627,"market_data_asof":"2026-10-28T18:00:00-04:00","session_vwap":344.4219824404296,"relative_volume":0.7228221436912237,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"341.03~343.53 방어 후 344.01 회복, 실시간 세션 거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상을 감시한다. 이는 가격 확인 조건이며 현재 구조에서 단독 매수 승인은 아니다. / 347.18~348.36 회복과 351.73 최종 돌파를 구분한다. 돌파 위 목표와 청산 구조를 검증하기 전에는 상승 여력을 임의로 가정하지 않는다.","risk_condition_ko":"341.03 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T18:00:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T18:03:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":217.5938,"market_data_asof":"2026-10-28T18:55:00-04:00","session_vwap":217.18188625853475,"relative_volume":0.5044730265970836,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"일봉과 지연 장중 자료의 불일치를 해소하고 최신 정규장 가격·거래량·당일 거래량가중평균가격을 확인한다. / 216.16–216.41 지지 회복과 214.77–215.25 심층 지지 구간을 관찰하고 실제 예상 체결가에서 비용 차감 후 보상·손실비를 다시 계산한다.","risk_condition_ko":"216.16 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T18:55:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T18:58:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":344.9,"market_data_asof":"2026-10-28T18:00:00-04:00","session_vwap":349.7306783282522,"relative_volume":0.8065621587756683,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"354 돌파·재지지 또는 344.35~345.67 및 339.32~340.14 반등을 관찰한다. 당시 거래량가중평균가격 상회, 동시간대 상대거래량 1.2배 이상, 최초 현실적인 저항까지 비용 후 보상위험 2배 이상을 각각 확인한다. / 352, 353.63, 357~362.50과 366.74의 저항 통과 및 지지 전환을 점검한다. 가격 도달만으로 매수하거나 이익실현하지 않는다.","risk_condition_ko":"339.32 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T18:00:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T18:03:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.69,"market_data_asof":"2026-10-28T19:05:00-04:00","session_vwap":100.69485415534227,"relative_volume":0.5747060713894607,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"기존 보유량·관련 단기국채 집중도·지출 통화와 사용일을 확인하고, 가까운 지출 준비금을 먼저 확보한다. / 기준시점에 적합한 운용사 자료와 순자산가치로 신규 편입 및 기존 유지의 순수익을 각각 계산해 달러 현금 대안과 비교한다.","risk_condition_ko":"100.63 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T19:05:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T19:08:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":255.47,"market_data_asof":"2026-10-28T18:00:00-04:00","session_vwap":253.7607217100825,"relative_volume":0.7016062155619833,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"지지 경로: 새로 246–248을 시험한 뒤 하락을 거부하고 248을 회복하는지 확인한다. 이미 248 위에 있다는 사실만으로는 매수 신호가 아니다. / 회복 경로: 255.87 재돌파·재시험, 당일 거래량가중평균가격 위 지지, 동시간대 상대거래량 1.2배 이상을 확인하되 구조적 손절과 중간 저항까지의 순손익비를 다시 계산한다.","risk_condition_ko":"246.45 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T18:00:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T18:03:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":391.49,"market_data_asof":"2026-10-28T18:15:00-04:00","session_vwap":392.7170431037653,"relative_volume":0.6043777577046391,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"연구 기준일까지 이용 가능했던 공식 자료의 공개시각, 재무제표 통화·단위·회계기간·주식 기준 및 해당되는 예탁증서 환산비율을 확인한다. 모든 지표의 호전보다 위험을 평가할 수 있는 신뢰성이 우선이다. / 정확한 실적 발표 시각, 발표를 넘겨 보유할 위험, 현재 계좌의 현금·보유량·상관 노출과 한도 준수 여부를 확인한다.","risk_condition_ko":"388.22 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T18:15:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T18:18:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":610.31,"market_data_asof":"2026-10-28T19:55:00-04:00","session_vwap":612.5137491259368,"relative_volume":0.5758612096496293,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-10-28 연구 기준일을 유지한다. 공식 발표 시각과 자료 공개 시점을 확인하고, 이후 나온 결과는 향후 판단에만 반영한다. / 판단 시각은 2026-10-28T20:36:53.547313-04:00이다. 이 시각만으로 거래 세션·휴장·조기 종료·시세 최신성 또는 주문 조건 충족을 판단하지 않는다. 적격 거래일과 새로운 유효기간은 별도로 검증한다.","risk_condition_ko":"605 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T19:55:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T19:58:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":400.6,"market_data_asof":"2026-10-28T19:55:00-04:00","session_vwap":401.5298984847445,"relative_volume":1.155319068997715,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"다음 실제 거래 가능한 정규장, 시세 시각, 거래정지 여부, 매수·매도 호가 차이, 일관된 봉 간격과 당일 거래량가중평균가격을 확인한다. 활성 주문이나 확정 만료는 없다. / 신규 매수 전 최신 공식 실적·전망·현금흐름 및 포트폴리오 비중을 검토한다. 설명 가능한 현금전환 약화는 허용할 수 있으나 중요한 미해결 차이는 매수를 보류하는 사유다.","risk_condition_ko":"394 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T19:55:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T19:58:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":540.34,"market_data_asof":"2026-10-28T19:55:00-04:00","session_vwap":541.1673860902532,"relative_volume":0.7671632506858171,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"거래소 휴장·단축장 일정, 실제 정규장 여부, 호가 시각, 매수·매도 호가 차이와 거래정지를 확인한다. 제공된 1분·5분 봉 표기 충돌을 해결하고 지연된 장외 자료로 주문을 활성화하지 않는다. / 533.65–537.70에서는 단순 접촉이 아니라 매도 안정, 저점 상승, 새 정규장 거래량가중 평균가격 회복과 비용 후 최소 2:1 손익비를 확인한다.","risk_condition_ko":"537.7 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T19:55:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T19:58:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":285.99,"market_data_asof":"2026-10-28T19:45:00-04:00","session_vwap":286.729140881253,"relative_volume":0.28385152610766257,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"282.70~283.99 지지 시험 후 283.99 회복, 신선한 당일 거래량가중평균가격 상회, 비교 가능한 장중 상대거래량 1.2 이상을 관찰한다. 이는 매수 승인이 아니라 재검토 조건이다. / 291.40 위 정규장 종가와 비교 가능한 일간 상대거래량 1.2 이상, 다음 검증된 거래일의 지지 확인을 관찰한다. 추가 상승 목표와 비용 차감 후 2:1 이상이 없으면 계속 대기한다.","risk_condition_ko":"282.7 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T19:45:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T19:48:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":229.2,"market_data_asof":"2026-10-28T19:55:00-04:00","session_vwap":229.87120500513768,"relative_volume":0.8719919067624683,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"226.39~227.63에서 지지 형성·회복과 최신 세션 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상을 함께 확인한다. / 231.56 회복은 반등 개선 신호로만 취급하며 최근 고점 돌파와 구분한다.","risk_condition_ko":"226.39 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T19:55:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T19:58:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":158.26,"market_data_asof":"2026-10-28T19:50:00-04:00","session_vwap":158.5751859977749,"relative_volume":0.5162764251631813,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"제공 시계는 2026-10-28T21:15:25.400329-04:00으로 연구일과 일치한다. 그러나 실제 세션·휴장·조기종료·거래정지·호가 신선도를 입증하지 않는다. 다음 정규장 날짜나 만기는 임의 지정하지 않는다. / 장중 자료는 조회 당시 약 3464초 지연됐고 봉 간격도 불일치한다. 신선한 호가, 정상 봉, 실제 세션 및 동시간대 거래량 비교자료를 확보하기 전에는 진입이나 실패 돌파를 확정하지 않는다.","risk_condition_ko":"157.4 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T19:50:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T19:53:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"UNH","display_name":"UNH","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":407.1,"market_data_asof":"2026-10-28T19:55:00-04:00","session_vwap":410.08882808231346,"relative_volume":0.6426260200972568,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"실제 거래 일정, 정규장 상태, 거래정지, 호가 신선도와 완결 봉을 먼저 확인한다. 제공 시계만으로 세션이나 다음 거래일을 확정하지 않으며, 확인되지 않은 만료를 선언하거나 기한을 이월하지 않는다. / 405.00 또는 400.00–401.43에서 지지 유지, 높아진 저점, 당일 거래량가중평균가격 회복을 확인한다. 단순 가격 접촉은 매수 신호가 아니다.","risk_condition_ko":"400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T19:55:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T19:58:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":183.0984,"market_data_asof":"2026-10-28T19:55:00-04:00","session_vwap":182.31133218884574,"relative_volume":0.5894279257096641,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"179.15~180.00 시험 후 저점 상승, 거래일 거래량가중평균가 회복 및 상대거래량 1.2 이상을 확인한다. 지지선 접촉만으로 매수하지 않는다. / 184.88 위의 검증된 정규장 종가와 상대거래량 1.2 이상, 다음 실제 거래일의 지지 유지를 확인한다.","risk_condition_ko":"177.83 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T19:55:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T19:58:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":94.78,"market_data_asof":"2026-10-28T19:55:00-04:00","session_vwap":94.87919402482737,"relative_volume":0.2913570957465149,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"93.30~94.05에서 저점 상승·당일 거래량가중평균가 회복·검증된 동시간대 상대거래량 1.2 이상 확인. 1.2는 제안 기준이지 관측값이 아니다. / 95.72 및 96.50~96.89 저항의 실제 소화 여부 확인. 96.89 돌파에는 재시험 지지와 근거 있는 손절선이 필요하다.","risk_condition_ko":"92.67 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T19:55:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T19:58:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":202.64,"market_data_asof":"2026-10-28T19:55:00-04:00","session_vwap":202.87061753465358,"relative_volume":0.7250374873660915,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"적격 정규장, 거래 상태, 시세 신선도와 봉 구간을 확인한다. 실행시각만으로 시장 개장이나 조건 충족을 추정하지 않는다. / 200.60~201.19 지지, 실시간 거래량가중평균가격 회복과 상대거래량 1.2 이상을 함께 확인한다. 상대거래량은 관측시각에 맞는 비교 기준을 사용한다.","risk_condition_ko":"199.3 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T19:55:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T19:58:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMT","display_name":"AMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":183.75,"market_data_asof":"2026-10-28T19:55:00-04:00","session_vwap":180.75257260075557,"relative_volume":1.0722718047478095,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"실제 거래일정·거래 상태·최신 호가·5분봉 구성과 보유 위험한도를 확인한다. 기존 한도 초과는 지지 이탈 전에도 위험축소 사유다. / 180.75~182.00 지지 형성과 최신 거래량가중평균가격 회복을 관찰하되, 첫 미해소 저항까지 비용 후 보상/위험 2배 미달이면 대기를 유지한다.","risk_condition_ko":"180.75 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T19:55:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T19:58:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SNOW","display_name":"Snowflake","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":329.0,"market_data_asof":"2026-10-28T19:45:00-04:00","session_vwap":343.390815227694,"relative_volume":0.35664277247199755,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"거래일정·거래상태·정규장 여부·가격 시각을 확인하고 기존 보유량과 집중도 및 손실예산을 대조한다. 미확인은 초과보유의 증거가 아니다. / 331.49–332.23 시험 후 회복, 거래량가중평균가격 회복과 매도세 약화를 관찰한다. 333.00 시험매수 검토에는 현실적인 목표 기준 순손익비와 새로운 시간대 포함 유효기한이 필요하다.","risk_condition_ko":"331.49 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T19:45:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T19:48:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":105.19,"market_data_asof":"2026-10-28T19:50:00-04:00","session_vwap":105.39901539725139,"relative_volume":0.6591570449039961,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"104.14–104.64에서 신선한 정규장 자료로 지지 안정·저점 상승·당일 거래량가중평균가격 회복을 확인한다. / 105.93 재탈환·재시험과 106.24 상회 종가를 관찰한다. 거래량 조건을 충족해도 손익비가 부적격이면 매수 대기를 유지한다.","risk_condition_ko":"104.14 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T19:50:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T19:53:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SNAP","display_name":"SNAP","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":5.88,"market_data_asof":"2026-10-28T19:30:00-04:00","session_vwap":5.942788227101117,"relative_volume":0.49932627660629303,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"5.84–5.87 지지를 방어하고 6.00을 회복한 뒤 실시간 거래량가중평균가격 위에서 재시험에 성공하는지 관찰한다. 이는 현재 매수 지시가 아니다. / 6.14–6.19와 6.29–6.35를 순차 회복하고 같은 정규장 경과시간 기준 상대거래량이 1.2 이상인지 확인한다. 가까운 저항을 반영한 비용 차감 손익비도 재계산한다.","risk_condition_ko":"5.99 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T19:30:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T19:33:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":982.73,"market_data_asof":"2026-10-28T19:55:00-04:00","session_vwap":983.0149352541464,"relative_volume":0.8061853877245627,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"989.40 회복 후 992.13 종가 돌파와 재지지 여부를 관찰한다. 989.40 회복만으로 목표비중 진입을 승인하지 않는다. / 978.01–980.32 방어, 저점 상승과 당일 거래량가중평균가격 회복을 확인한다. 지지 접촉만으로 매수하지 않는다.","risk_condition_ko":"968.68 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T19:55:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T19:58:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MU","display_name":"Micron Technology","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":958.4185,"market_data_asof":"2026-10-28T19:30:00-04:00","session_vwap":975.3393341411088,"relative_volume":0.832890385582262,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"거래소의 실제 정규장 일정·조기 폐장·거래정지·가격 시각과 주요 행사 일정을 확인한다. 제공된 실행 시각만으로 거래 가능 상태나 주문 만료를 확정하지 않는다. / 보고된 종가 983.23과 지연된 시간외 958.42, 거래량·저가 차이, 요청된 5분 봉과 반환된 1분 봉 표기의 불일치를 해소한다.","risk_condition_ko":"955 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-28T19:30:00-04:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-28T19:33:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-22T03:18:02.795423+09:00",
  "as_of": "2026-10-21T14:14:00-04:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
