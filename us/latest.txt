# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-10T01:03:27.198378+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261010T040116_github-actions-us",
  "producer_finished_at": "2026-10-10T07:39:14.517828+09:00",
  "analysis_run_id": "20261010T040116_github-actions-us",
  "analysis_completed_at": "2026-10-10T07:13:39.334182+09:00",
  "analysis_trade_date_oldest": "2026-10-08",
  "analysis_trade_date_latest": "2026-10-08",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-09T15:00:00-04:00",
  "market_data_latest_at": "2026-10-09T17:35:00-04:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-10T07:14:03.015104+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-10T07:14:03.015104+09:00",
    "run_started_at": "2026-10-10T04:01:16.461991+09:00",
    "run_finished_at": "2026-10-10T07:39:14.517828+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23632369,
    "total_market_value_krw": 24886170,
    "total_unrealized_pnl_krw": 1253801,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 91119,
    "total_equity_krw": 25953941
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 545951,
      "current_price_krw": 607072,
      "market_value_krw": 7284873,
      "unrealized_pnl_krw": 733453
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 292622,
      "current_price_krw": 285303,
      "market_value_krw": 3138334,
      "unrealized_pnl_krw": -80512
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 424431,
      "current_price_krw": 470943,
      "market_value_krw": 2825658,
      "unrealized_pnl_krw": 279072
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1881227,
      "current_price_krw": 1856519,
      "market_value_krw": 1856519,
      "unrealized_pnl_krw": -24708
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 267420,
      "current_price_krw": 307051,
      "market_value_krw": 1842310,
      "unrealized_pnl_krw": 237789
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 556300,
      "current_price_krw": 575387,
      "market_value_krw": 1726161,
      "unrealized_pnl_krw": 57260
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1473843,
      "current_price_krw": 1345534,
      "market_value_krw": 1345534,
      "unrealized_pnl_krw": -128309
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 134605,
      "current_price_krw": 134602,
      "market_value_krw": 1211426,
      "unrealized_pnl_krw": -19
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 364816,
      "current_price_krw": 450828,
      "market_value_krw": 901656,
      "unrealized_pnl_krw": 172024
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 663178,
      "current_price_krw": 784851,
      "market_value_krw": 784851,
      "unrealized_pnl_krw": 121673
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1420905,
      "current_price_krw": 1579278,
      "market_value_krw": 688668,
      "unrealized_pnl_krw": 69061
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 569996,
      "current_price_krw": 484174,
      "market_value_krw": 484174,
      "unrealized_pnl_krw": -85822
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 136301,
      "current_price_krw": 111140,
      "market_value_krw": 444560,
      "unrealized_pnl_krw": -100646
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 347977,
      "current_price_krw": 351446,
      "market_value_krw": 351446,
      "unrealized_pnl_krw": 3469
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":82.9601,"market_data_asof":"2026-10-09T15:25:00-04:00","session_vwap":82.87933875881754,"relative_volume":0.3350932462639002,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 결정 시각은 2026-10-09T15:45:10.819938-04:00이며 2026-10-09T19:45:10.819938+00:00와 같은 순간이다. 연구 기준일은 2026-10-09, 일봉 가격 기준일은 2026-10-08이다. 이 시각만으로 실제 정규장 운영, 조기 폐장, 거래정지 여부를 확정하지 않는다. / 2026-10-09 미국 동부시간 15:25의 지연 가격 82.9601은 83.12 돌파를 입증하지 못하며 실행용 최신 호가가 아니다. 새 호가와 체결, 당일 거래량가중평균가격 및 비교 가능한 시간대의 상대거래량을 확보한다.","risk_condition_ko":"82.5 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T15:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T15:55:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":453.47,"market_data_asof":"2026-10-09T16:20:00-04:00","session_vwap":453.19195683484753,"relative_volume":0.49255970778185654,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"449.75~452.88 재시험 후 높은 저점, 당일 거래량가중평균가격 유지 및 동일 시간대 상대거래량 1.2 이상 확인 / 459.21 초기 회복과 갱신된 463.92 기준의 정규장 종가 돌파, 다음 검증된 거래일 지지 확인","risk_condition_ko":"449.75 이하 하락, 종가 확인 후 (매도에는 최소 상대거래량 조건을 적용하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T16:20:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T16:50:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":430.24,"market_data_asof":"2026-10-09T15:25:00-04:00","session_vwap":428.43020817122067,"relative_volume":0.3492776956932983,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 실행 자료로 420·421.42 지지, 425.46 회복·재시험, 당시 거래량가중평균가격 상회와 시간대별 상대거래량 1.2배 이상을 확인한다. / 435.14 위 정규장 종가 및 검증된 다음 거래일 첫 30~60분 지지를 확인한다. 저항 통과 근거와 비용 후 보상 대비 위험 2배가 부족하면 계속 대기한다.","risk_condition_ko":"420 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T15:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T15:55:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":229.505,"market_data_asof":"2026-10-09T15:50:00-04:00","session_vwap":230.49888900835188,"relative_volume":0.4363224450985383,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"229.11 위 안정화 이후 229.85 회복과 지지 재확인을 관찰한다. 지지선 접촉만으로 매수하지 않는다. / 231.15·232.22 회복, 당일 거래량가중평균가격 상회, 동일 시각 누적 상대거래량 1.2 이상을 확인한 뒤 손익비와 위험축소 판단을 재평가한다.","risk_condition_ko":"231.15 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T15:50:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T16:20:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1381.14,"market_data_asof":"2026-10-09T15:45:00-04:00","session_vwap":1372.6298137064066,"relative_volume":0.25019716801639613,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단 시각은 2026-10-09T16:17:03.099523-04:00이다. 2026-10-09 15:45 미국 동부시간의 지연 관측치는 같은 날짜 자료지만 최신 체결 가능 가격이나 종가가 아니다. 당일 종가, 실제 세션, 거래일 달력, 거래정지 여부를 별도로 확인한다. / 1349.39–1363.12 유지와 1391.02 회복·재시험, 1401.29 돌파를 관찰한다. 지지 확인과 매수 허용을 동일시하지 않는다.","risk_condition_ko":"1,349.39 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T15:45:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T16:15:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":362.46,"market_data_asof":"2026-10-09T15:00:00-04:00","session_vwap":364.00525731978956,"relative_volume":0.3243616390377217,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"357.41~358.69 지지 형성 후 361.22와 최신 거래량가중평균가격 회복을 관찰한다. 단순 지지 접촉은 매수 신호가 아니다. / 지연 참고값 364.01과 366.63을 갱신하고 366.63~367.00 회복·재시험 지지 또는 회복 실패를 확인한다.","risk_condition_ko":"367 이하 하락, 2개 봉 확인 후 (현재 정상 체결과 재시험 회복 실패를 확인) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T15:00:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T15:30:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":584.5,"market_data_asof":"2026-10-09T15:00:00-04:00","session_vwap":578.485176957695,"relative_volume":0.34757888090469496,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"555.99–564.51 시험 이후 저점 상승과 561.06·564.51 회복을 관찰한다. 561.06은 갱신이 필요한 10일 지수이동평균이며 지지 구간 접촉만으로 매수하지 않는다. / 587.19 회복은 중간 확인에 불과하다. 593.98–595.51 저항이 가까워 자동 진입으로 연결하지 않는다.","risk_condition_ko":"585 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T15:00:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T15:30:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.5162,"market_data_asof":"2026-10-09T16:15:00-04:00","session_vwap":100.51330248519287,"relative_volume":0.6807517464412105,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"공식 수익률과 현금 계좌 이자율을 동일 기간·통화·접근성으로 비교하고 신규 매수와 기존 보유의 향후 비용을 구분한다. 현재 최소 비용 회수 보유기간은 계산할 수 없다. / 보유 규모·자금 사용일·계좌별 자금 사용 가능 시점·집중도·환위험을 확인한다. 미래 매도가격을 보장하려 하지 말고 불리한 체결과 회수 지연에 대비한 현금 여유분을 산정한다.","risk_condition_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T16:15:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T16:45:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1176.75,"market_data_asof":"2026-10-09T15:45:00-04:00","session_vwap":1172.47582908756,"relative_volume":0.2643434740825078,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1131.21~1140 시험 후 1140 위 5분봉 두 개, 반등 고점 갱신, 당일 거래량가중평균가격 회복과 동시간대 상대거래량 1.2 이상을 확인한다. 1166.67과 1173.11의 저항 역할을 반영해 손익비를 재평가한다. / 1113.29~1118.12 시험 후 1118.12 위 동일한 확인 조건을 요구한다. 1131.21~1140이 가까운 저항이 될 수 있어 낮은 가격만으로 매수하지 않는다.","risk_condition_ko":"1,131.21 이하 하락, 2개 봉 확인 후 (방어적 매도에는 상대거래량 문턱을 적용하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T15:45:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T16:15:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":261.36,"market_data_asof":"2026-10-09T15:00:00-04:00","session_vwap":259.724474933952,"relative_volume":0.5092915301109431,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"거래 캘린더·세션·거래정지 상태, 최신 가격과 호가 시각, 갱신 거래량가중평균가격 및 실적 일정을 먼저 확보한다. / 260.14 지지 전환과 261.64 재돌파에 동일 시간대 누적 상대거래량 1.2 이상이 동반되는지 확인한다. 산식 불명인 기존 0.5093과 직접 비교하지 않는다.","risk_condition_ko":"251.92 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T15:00:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T15:30:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1003.72,"market_data_asof":"2026-10-09T15:25:00-04:00","session_vwap":997.0539957174428,"relative_volume":0.25221802056819687,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"973.36~984.76에서 매도 압력 감소, 저점 상승, 새로운 당일 거래량가중평균가격 회복과 완성된 5분봉 두 개 유지 여부를 확인한다. 가격 도달만으로 진입하지 않는다. / 1010, 1027~1029.21, 1052.78의 순차 통과와 지지 전환을 확인한다. 중립 분석가가 추가로 언급한 더 가까운 저항은 원천을 확인한 뒤 반영하며, 가장 가까운 유효 저항부터 순보상·위험을 계산한다.","risk_condition_ko":"968.26 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T15:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T15:55:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":213.015,"market_data_asof":"2026-10-09T15:55:00-04:00","session_vwap":212.75917226119694,"relative_volume":0.49673981097583486,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"분석 기준일은 2026-10-09이며 일별 가격과 역사적 지표의 기준일은 2026-10-08이다. 판단 시각 2026-10-09T16:12:50.576580-04:00은 2026-10-09T20:12:50.576580+00:00와 같은 순간이지만, 공식 종가·휴장 및 조기 종료 일정·거래 상태·주문 가능성을 확정하지 않는다. / 2026-10-09 미국 동부시간 15:55로 표시된 213.015 관측값에는 호가 지연 149초와 출처 지연 895초가 보고되었다. 약 0.50의 상대 거래량은 하루 전체 평균을 분모로 사용했으므로 같은 경과 시간 기준의 진입 요건 충족 여부를 판정할 수 없다.","risk_condition_ko":"209.81 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T15:55:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T16:25:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":337.915,"market_data_asof":"2026-10-09T15:00:00-04:00","session_vwap":333.81947166408423,"relative_volume":0.554941288432615,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"공식 거래일 달력·세션 상태·최신 호가·완결 5분봉·당일 거래량가중평균가격·시간 보정 상대거래량을 확인한다. 제공 상대거래량 0.55는 산정 방식이 미확인이라 실행 판정에 사용하지 않는다. / 335.27~335.90 재회복과 유지 여부를 관찰하되 지지 확인만으로 매수하지 않는다. 이탈하면 330.70·329.40 반응을 살피되 이미 확인된 축소 신호를 더 낮은 지지까지 미루지 않는다.","risk_condition_ko":"335.27 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T15:00:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T15:30:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":351.275,"market_data_asof":"2026-10-09T15:30:00-04:00","session_vwap":352.35991351508164,"relative_volume":0.3398026629486952,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"345.77~345.93 시험 후 345.93 회복, 높아지는 저점, 실시간 거래량가중평균가격 상회 및 동일 시간대 상대 거래량 1.2 이상을 관찰한다. 가격 접촉이나 회복만으로 매수하지 않는다. / 342.40과 339.46 지지의 유지·회복을 확인한다. 확인된 하방 실패나 계좌 한도 위반은 신규 진입 검토보다 우선한다.","risk_condition_ko":"339.46 이하 하락, 종가 확인 후 (검증된 비교 가능한 20일 평균 거래량의 1.2배 이상) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T15:30:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T16:00:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":276.0872,"market_data_asof":"2026-10-09T17:05:00-04:00","session_vwap":276.1605344917142,"relative_volume":0.5689510040999874,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"267.47–269.39에서 지지 전환, 가격 회복, 당일 거래량가중평균가격 회복 및 반등 거래 참여를 확인한다. / 265.27–266.56에서 지지 회복과 확인된 지지 실패를 구분한다. 269.39 이탈만으로 자동 매도하지 않는다.","risk_condition_ko":"265.27 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T17:05:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T17:35:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":212.3,"market_data_asof":"2026-10-09T17:15:00-04:00","session_vwap":212.45269380637419,"relative_volume":0.2985981587555932,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"CVX 최신 검증된 정규장 종가를 205.83·203.41·200.78과 먼저 대조하고 실제 보유 위험과 종목·업종 비중을 확인한다. 위험 축소 필요 여부를 신규 진입보다 우선 평가한다. / CVX 205.83~207.26 테스트 후 207.26 위 두 개 연속 5분봉, 저점 상승, 당일 거래량가중평균가격 상회, 같은 경과시간 기준 상대거래량 1.2 이상, 진입가 207.50 이하를 확인한다.","risk_condition_ko":"205.83 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T17:15:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T17:45:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"FFIV","display_name":"FFIV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":479.83,"market_data_asof":"2026-10-09T16:20:00-04:00","session_vwap":476.1252856045368,"relative_volume":0.7110684496761798,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"451.00–454.36의 과거 지지 구간을 갱신하고 454.36 회복, 완료된 5분봉 2개의 상회 및 재시험 지지를 확인한다. / 483.00의 출처와 현재 유효성을 확인하고 돌파·재시험·거래량을 검증한다. 지연 관측값만으로 매수나 돌파 실패를 선언하지 않는다.","risk_condition_ko":"451 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T16:20:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T16:50:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.0411,"market_data_asof":"2026-10-09T17:30:00-04:00","session_vwap":100.55177937710097,"relative_volume":0.738446538624953,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"99.15~99.44 재시험 후 99.44 회복, 높아지는 5분봉 저점, 당일 거래량가중평균가격 상회와 시간대 보정 상대거래량 1.2 이상을 관찰한다. 비용 차감 후 보상·위험 비율 2배와 계좌 여력이 없으면 계속 대기한다. / 100.60 돌파·재시험, 정규장 종가 상회와 다음 검증된 거래일의 후속 지지를 관찰한다. 검증된 상단 목표 없이는 진입을 활성화하지 않는다.","risk_condition_ko":"99.15 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T17:30:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T18:00:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":169.0,"market_data_asof":"2026-10-09T17:15:00-04:00","session_vwap":169.23299828051597,"relative_volume":0.33649851054005564,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"166.71~167.11 지지와 연속 5분봉 2개 확인, 당일 거래량가중평균가격 회복 및 동일 시각 정규장 상대거래량 1.2 이상을 감시한다. 166.80은 비활성 진입 예시다. / 169.64 상회 종가와 일일 거래량 확인 이후 다음 실제 거래일의 지지 유지 여부를 점검한다. 장중 상대거래량과 일일 거래량 비율을 혼용하지 않는다.","risk_condition_ko":"166.71 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T17:15:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T17:45:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SPYM","display_name":"SPYM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":91.7,"market_data_asof":"2026-10-09T17:10:00-04:00","session_vwap":91.54130427921547,"relative_volume":1.9614515401366366,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-10-09 공식 일봉·최신 지표·실시간 호가·공식 거래일 달력을 확보해 기준일 이후 추세를 재평가한다. / 90.62~90.81 시험 후 90.81 위 5분봉 두 개 마감, 세션 거래량가중평균가격 회복, 동시간대 상대거래량 1.2 이상 및 비용 반영 손익비 2:1 이상을 재검증한다.","risk_condition_ko":"90.09 이하 하락, 종가 확인 후 (공식 종가 이탈과 하락 거래량 확대 확인) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T17:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T17:40:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":385.3467,"market_data_asof":"2026-10-09T16:45:00-04:00","session_vwap":382.9843152413075,"relative_volume":0.47186653846491405,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"368.67–370.37에서 안정된 뒤 369.24 위로 5분봉 종가 두 개가 연속 형성되고, 최신 거래량가중평균가격 지지와 동일 시각 상대거래량 1.2 이상이 확인되면 최초 진입 검토를 재개한다. 비용 반영 수익구조·포트폴리오 여력·명시적 유효기한이 없으면 주문하지 않는다. / 385.57 위의 정규장 종가와 전체 거래량 확인 후, 다음 검증된 거래 세션의 지지 재확인 및 상위 목표 확보를 기다린다.","risk_condition_ko":"366.24 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T16:45:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T17:15:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":199.4227,"market_data_asof":"2026-10-09T17:15:00-04:00","session_vwap":200.28343999820888,"relative_volume":0.32110229786003697,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"필수 재무·사건 검증 후 193.80–195.00 재시험을 관찰한다. 195.00 위에서 완성된 5분봉 2개, 당일 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상 및 비용 차감 후 보상비 2배 이상을 모두 요구한다. / 202.70을 첫 필수 재평가 지점으로 둔다. 단순 돌파만으로 매수하지 않으며, 본격적인 확대에는 이 저항의 소화와 새롭게 검증된 보상 구조가 필요하다.","risk_condition_ko":"192.87 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T17:15:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T17:45:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":150.4665,"market_data_asof":"2026-10-09T16:45:00-04:00","session_vwap":151.1400937490653,"relative_volume":0.42108290277666005,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"실제 정규장 일정·거래 상태와 최신 가격·호가·당일 거래량가중평균가격·동시간대 상대거래량을 확인한다. 2026-10-08 일봉을 2026-10-09 현재 가격으로 취급하지 않는다. / 148.50~149.00 반등 후보, 149.48~150.02 지지 회복 및 150.76 재돌파를 구분해 관찰한다. 가격 도달만으로 주문하지 않으며 확인된 매도 위험이 있으면 신규 진입을 중단한다.","risk_condition_ko":"149.48 이하 하락, 다음 거래일 확인 후 (위험 감축에 최소 거래량 요건 없음) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T16:45:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T17:15:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOG","display_name":"GOOG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":348.2,"market_data_asof":"2026-10-09T17:35:00-04:00","session_vwap":348.43258776187844,"relative_volume":0.4771089420001157,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"338–340 접촉만으로 매수하지 않는다. 실제 지지 회복, 당일 거래량 가중 평균가 상회, 같은 시간대 기준 상대 거래량 1.2 이상과 실제 체결 예상가의 보상·위험 비율을 확인한다. 기존 보호 매도가 발생했다면 이를 완료하고 새로운 회복 근거를 독립적으로 재검증한다. / 353.53 위 정규장 종가와 완전한 정규장 기준 상대 거래량 1.2 이상, 이후 재시험 성공을 감시한다. 355.13과 359.98의 저항을 반영하며 돌파 확인만으로 매수를 허용하지 않는다.","risk_condition_ko":"342.45 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T17:35:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T18:05:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMT","display_name":"AMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":183.0,"market_data_asof":"2026-10-09T16:20:00-04:00","session_vwap":179.60362783373606,"relative_volume":1.6154498315459833,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"183.00 자료를 공식 정규장 가격과 대조하고 급등 원인을 확인한다. 보고된 일별 상대거래량 1.62는 같은 시간대 대비 장중 상대거래량 1.5 이상을 입증하지 않는다. / 179.60 재시험 후 연속 5분봉 2개가 해당 가격과 현재 정규장 거래량가중평균가격 위에서 마감하는지 확인한다. 저항의 유효성과 비용 차감 후 보상위험비 2배 이상도 별도로 검증한다.","risk_condition_ko":"179.6 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T16:20:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T16:50:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CEG","display_name":"CEG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":298.03,"market_data_asof":"2026-10-09T17:35:00-04:00","session_vwap":297.384071700465,"relative_volume":0.7918759570008505,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-10-09 확정 일봉, 최신 지표 및 실제 체결 가능한 호가를 확보한다. 지연된 장후 298.03 관측으로 종가나 매매 신호를 확정하지 않는다. / 280.16 및 갱신된 276.62~277.30의 회복·재시험을 관찰한다. 기존 감축 신호가 발동한 상태에서는 이를 곧바로 재매수 근거로 사용하지 않는다.","risk_condition_ko":"280.16 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T17:35:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T18:05:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-A","display_name":"BRK-A","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":774299.625,"market_data_asof":"2026-10-09T15:55:00-04:00","session_vwap":773011.2878048782,"relative_volume":0.9490966072318905,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"BRK-A의 새 공식 종가·정규장 시세·거래량·거래 달력·호가 깊이·거래정지 상태를 확인한다. 지연 관측의 769,676 상회는 현재 돌파 확인으로 인정하지 않는다. / 760,605~761,386.18 재시험 후 회복, 완료된 5분봉 2개의 지지, 새 거래량 가중평균가격 상회와 상대 거래량 1.2배 이상을 함께 관찰한다. 1.2배는 제안 실행 기준이며 검증된 성공 확률이 아니다.","risk_condition_ko":"756,564.35 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T15:55:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T16:25:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NU","display_name":"NU","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":16.08,"market_data_asof":"2026-10-09T16:50:00-04:00","session_vwap":15.88918613224144,"relative_volume":0.5925429985967191,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"15.18~15.20 지지 유지 여부를 최신 정규장 자료로 확인한다. 단순 접촉은 매수 신호가 아니다. / 14.84~14.98 재시험 후 두 개 5분봉의 지지 유지, 거래량가중평균가격 회복, 동시간대 상대거래량 1.2 이상을 함께 확인한다.","risk_condition_ko":"15.18 이하 하락, 다음 거래일 확인 후 (위험축소에 거래량 증가를 요구하지 않음) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T16:50:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T17:20:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"QCOM","display_name":"Qualcomm","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":175.5,"market_data_asof":"2026-10-09T17:25:00-04:00","session_vwap":174.52535601348697,"relative_volume":0.42964946098447204,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"누락된 2026-10-09 정규장 종가, 현재 체결 가능한 가격 및 갱신된 이동평균을 확보한다. 기존 손실방어 기준을 낮춰 허용손실을 늘리지 않는다. / 171.02–172.20 시험 후 172.20 회복, 연속 2개 5분봉 유지와 재시험 성공, 정규장 거래량가중평균가격 상회 및 동일 시각 대비 상대거래량 1.2 이상을 관찰한다. 구조적으로 타당한 손절과 가까운 저항 기준 순손익비도 별도로 통과해야 한다.","risk_condition_ko":"171.02 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T17:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T17:55:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"META","display_name":"Meta Platforms","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":718.3415,"market_data_asof":"2026-10-09T16:45:00-04:00","session_vwap":720.7451574318904,"relative_volume":0.3936104063673233,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"711.68–715.10 시험 후 715.10 재탈환, 높아지는 5분봉 저점, 당일 정규장 거래량가중평균가격 위에서 완성된 5분봉 2개 및 동일 시각 대비 상대거래량 1.2 이상을 관찰한다. / 726.12–728.08 회복 후 728.08 재시험 유지 여부와 최초 저항까지의 비용 차감 손익비를 확인한다.","risk_condition_ko":"711.68 이하 하락, 종가 확인 후 (지지 실패가 확인되면 거래량 부족을 이유로 위험 축소를 미루지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T16:45:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T17:15:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-10T07:55:16.549552+09:00",
  "as_of": "2026-10-09T15:00:00-04:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
