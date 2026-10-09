# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-09T01:42:48.032981+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261009T060240_github-actions-overlay-us-37843616669-1",
  "producer_finished_at": "2026-10-09T06:03:34.905278+09:00",
  "analysis_run_id": "20261008T175703_github-actions-us",
  "analysis_completed_at": "2026-10-08T22:30:16.387321+09:00",
  "analysis_trade_date_oldest": "2026-10-07",
  "analysis_trade_date_latest": "2026-10-07",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-08T15:10:00-04:00",
  "market_data_latest_at": "2026-10-08T15:10:00-04:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-09T06:03:32.195630+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-09T06:03:32.195630+09:00",
    "run_started_at": "2026-10-09T06:02:40.213715+09:00",
    "run_finished_at": "2026-10-09T06:03:34.905278+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23632369,
    "total_market_value_krw": 24845462,
    "total_unrealized_pnl_krw": 1213093,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 91119,
    "total_equity_krw": 25913233
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 545951,
      "current_price_krw": 613340,
      "market_value_krw": 7360082,
      "unrealized_pnl_krw": 808662
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 292622,
      "current_price_krw": 283736,
      "market_value_krw": 3121099,
      "unrealized_pnl_krw": -97747
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 424431,
      "current_price_krw": 466429,
      "market_value_krw": 2798579,
      "unrealized_pnl_krw": 251993
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 267420,
      "current_price_krw": 308658,
      "market_value_krw": 1851952,
      "unrealized_pnl_krw": 247431
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1881227,
      "current_price_krw": 1834436,
      "market_value_krw": 1834436,
      "unrealized_pnl_krw": -46791
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 556300,
      "current_price_krw": 568503,
      "market_value_krw": 1705511,
      "unrealized_pnl_krw": 36610
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1473843,
      "current_price_krw": 1338329,
      "market_value_krw": 1338329,
      "unrealized_pnl_krw": -135514
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 134605,
      "current_price_krw": 134549,
      "market_value_krw": 1210944,
      "unrealized_pnl_krw": -501
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 364816,
      "current_price_krw": 455890,
      "market_value_krw": 911780,
      "unrealized_pnl_krw": 182148
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 663178,
      "current_price_krw": 769437,
      "market_value_krw": 769437,
      "unrealized_pnl_krw": 106259
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1420905,
      "current_price_krw": 1566328,
      "market_value_krw": 683020,
      "unrealized_pnl_krw": 63413
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 569996,
      "current_price_krw": 482299,
      "market_value_krw": 482299,
      "unrealized_pnl_krw": -87697
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 136301,
      "current_price_krw": 109439,
      "market_value_krw": 437757,
      "unrealized_pnl_krw": -107449
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 347977,
      "current_price_krw": 340237,
      "market_value_krw": 340237,
      "unrealized_pnl_krw": -7740
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":455.205,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":461.759801558746,"relative_volume":0.34037700463901627,"spread_bps":2.192597789861926,"day_high":471.1231,"day_low":452.88,"execution_condition_ko":"477.72와 당일 정규장 거래량가중평균가격 위 연속 두 개의 5분봉 마감 여부를 확인해 최초 축소 판단을 재평가한다. 회복만으로 신규 매수를 자동 승인하지 않는다. / 464.10~465.24 시험 후 465.24·갱신한 10일 지수이동평균·당일 정규장 거래량가중평균가격 회복, 연속 두 개의 5분봉 유지, 반등 거래량 증가와 동일 시간대 상대거래량 1.2 이상을 확인한다. 현재는 관찰 신호다.","risk_condition_ko":"477.72 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":81.635,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":81.59195505464791,"relative_volume":0.979824269879454,"spread_bps":1.2255652919898163,"day_high":81.96,"day_low":81.16,"execution_condition_ko":"81.32 재회복과 80.75 방어 여부를 우선 관찰한다. 82.16은 초기 회복 관찰선이고 82.68, 83.10, 83.34가 후속 저항이다. / 83.34 회복 이후에도 83.77, 84.53, 85.58까지 남는 보상과 구조적 손절 위험을 다시 계산한다. 회복 확인으로 진입가격이 높아져 보상·손실비가 악화되면 매수하지 않는다.","risk_condition_ko":"81.32 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1356.98,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":1385.7631474146237,"relative_volume":0.27663183899044574,"spread_bps":22.125028388902184,"day_high":1416.62,"day_low":1355.64,"execution_condition_ko":"1393.13~1395.73 시험 후 회복, 높아지는 저점, 완료된 5분봉 두 개의 지지 유지, 정규장 거래량가중평균가격 상회 및 동일 경과시간 상대거래량 1.2 이상을 확인한다. 1412.68 회복은 추가 확인 신호다. / 1450.71~1455.99와 1482.97~1491.64에서 저항을 점검한다. 1491.64 돌파·재시험 이후에도 구조적 손절과 비용 후 보상/위험 기준이 없으면 신규 매수를 하지 않는다.","risk_condition_ko":"1,393.13 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":988.85,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":1003.8397670149723,"relative_volume":0.4745234202149922,"spread_bps":8.944678669957439,"day_high":1027.0,"day_low":973.365,"execution_condition_ko":"판단시각 2026-10-08T06:07:07.669146-04:00은 거래소 현지 10:30의 최초 검토시각 이전이다. 10:30은 만료시각이 아니며, 거래일·정규장 운영 여부나 주문 유효기간을 입증하지 않는다. 만료를 다음 거래일로 이월하지 않는다. / 966–970 시험 후 정규장 5분봉이 두 번 연속 970 이상이면서 당일 거래량가중평균가격 위에서 마감하는지 확인한다. 시간대 대응 상대거래량은 최소 1.2이며 반등 봉 거래량이 직전 하락 봉보다 커야 한다.","risk_condition_ko":"966 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1159.23,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":1149.8511543169836,"relative_volume":0.5217301288701081,"spread_bps":9.663169519601487,"day_high":1186.0903,"day_low":1131.21,"execution_condition_ko":"최종 판단 시각은 2026-10-08T06:30:11.497693-04:00이다. 미국 동부시간 10:30은 아직 도래하지 않은 진입 검토 시작 기준이며 만료 시각이 아니다. 확인된 만료 시각이 없으므로 기한을 다음 거래일로 넘기지 않는다. / 주문 검토 전에 거래일·휴장 및 조기 종료 일정·정규장 상태·거래 정지 여부·최신 체결 가능 호가·중요 행사 일정을 각각 확인한다. 지연된 장전 표본은 주문 근거로 사용하지 않는다.","risk_condition_ko":"1,136.66 이하 하락, 종가 확인 후 (보호 목적 축소에는 최소 거래량 조건 없음) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":254.72,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":257.225637651022,"relative_volume":0.5258902179438368,"spread_bps":0.7854225573362486,"day_high":259.8599,"day_low":253.78,"execution_condition_ko":"판단 시각은 2026-10-08T05:29:35.113792-04:00이며 2026-10-08T09:29:35.113792+00:00와 같은 순간이다. 제안 관찰 개시 2026-10-08T10:30:00-04:00보다 이르다. 이는 개시 조건이지 만료시각이 아니며, 별도의 유효기간은 미제공이다. 만료 또는 다음 세션 자동 연장을 주장하지 않는다. / 거래소 달력, 정상 정규장과 거래 가능 상태, 최신 시세를 별도로 확인해야 한다. 04:55 장전 지연 자료와 날짜 표기만으로 진입 조건이나 당일 정상 세션을 확인할 수 없다.","risk_condition_ko":"258.01 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":357.735,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":366.6135859995067,"relative_volume":0.5634429291732603,"spread_bps":1.9480971265565483,"day_high":373.35,"day_low":357.665,"execution_condition_ko":"369.12 지지 관찰 후 372.09 위 연속 두 개의 정규장 5분봉 마감, 재시험 지지, 당일 거래량가중평균가격 상회와 동일 시간대 누적 상대거래량 1.2 이상 확인. / 380.84 위 연속 두 개의 정규장 5분봉 마감과 재시험 지지 확인. 가격·거래량 신호 충족만으로 자동 매수하지 않는다.","risk_condition_ko":"366.88 이하 하락, 종가 확인 후 (거래량 증가는 보조 정보이며 감축의 필수조건이 아니다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":422.485,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":428.0502623742488,"relative_volume":0.6638798917111807,"spread_bps":8.951918773115867,"day_high":439.01,"day_low":421.415,"execution_condition_ko":"정규 거래일과 장 운영시간, 최신 정규장 호가, 거래정지 여부, 실제 호가 차이, 장중 거래량가중평균가격 및 동일 경과시간 상대거래량을 확인한다. / 423.00–424.19 시험 후 상단 재탈환과 재시험 성공을 관찰한다. 426.00 진입 및 414.00 손절 예시는 재계산 전 주문으로 취급하지 않는다.","risk_condition_ko":"423 이하 하락, 종가 확인 후 (회복 실패 확인 후 위험 축소에는 최소 거래량 조건을 붙이지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.47,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":100.4755646775005,"relative_volume":0.7325480251042159,"spread_bps":0.9952724558352939,"day_high":100.48,"day_low":100.47,"execution_condition_ko":"공식 운용자료·수익률 정의·분배 일정·가격 조정 기준·최신 순자산가치와 호가, 자금 사용계획을 먼저 확인한다. / 보유기간 순수익 우위와 자금 적합성이 검증되면 신규 대기를 재평가한다. 핵심 현금성 편입에 기술적 돌파가 반드시 필요한지도 계획 갱신 때 별도로 판단한다.","risk_condition_ko":"100.44 이하 하락, 종가 확인 후 (거래량만으로 지지 실패를 판정하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":211.785,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":210.93091119186093,"relative_volume":0.6606988823397011,"spread_bps":0.4726232956018103,"day_high":211.84,"day_low":209.805,"execution_condition_ko":"거래소 일정, 정규장 여부, 거래정지, 신선한 호가, 체결 가능한 호가 차이와 가격 조정 기준을 확인한다. / 209.00–210.08에서 실제 지지 방어와 회복을 관찰한다. 단순 접촉이나 지연된 장전 가격은 매수 신호가 아니다. 이 경로의 진입가·구조적 손절·보상·위험은 아직 정해지지 않았다.","risk_condition_ko":"207.16 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":571.2211,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":577.3671696361477,"relative_volume":0.372569334707479,"spread_bps":11.266629111235902,"day_high":585.745,"day_low":564.51,"execution_condition_ko":"557.54~563.00에서 하락 중단 후 완성된 15분봉 두 개의 563.00 상회, 당일 정규장 거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상을 확인한다. 단순 접촉은 매수 신호가 아니다. / 585.00~587.19 돌파·재시험 후에도 592.44~595.51 저항까지 남은 수익 여력을 다시 계산한다.","risk_condition_ko":"546 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":230.1599,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":233.4540096244917,"relative_volume":0.501593328097089,"spread_bps":0.43441430091839117,"day_high":237.07,"day_low":229.85,"execution_condition_ko":"최종 판단 시각은 2026-10-08T06:39:47.484840-04:00이며 일봉 기준일은 2026-10-07이다. 제안된 10:30 미국 동부시간은 아직 도달하지 않은 최초 재평가 시각이지 만료 시각이 아니다. 활성 주문이나 검증된 만료가 없으므로 다음 거래일로 기한을 이월하지 않는다. 실제 거래일·정규장·조기종료 일정과 거래 가능 여부는 별도 확인한다. / 2026-10-08 06:10 미국 동부시간의 235.83은 지연된 개장 전 참고값이다. 개장 전 거래량가중평균가격 236.16과 비교 시간대가 불명확한 상대거래량 0.0572는 정규장 실행 신호로 사용하지 않는다.","risk_condition_ko":"232.61 이하 하락, 종가 확인 후 (매도량 확대는 추가 경고이며 축소의 필수 조건은 아니다) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":341.0269,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":338.54133969303234,"relative_volume":0.3949160772963538,"spread_bps":0.8787732325665367,"day_high":341.57,"day_low":335.9,"execution_condition_ko":"판단 시각은 2026-10-08T05:21:57.163359-04:00이며 일별 가격 기준일은 2026-10-07이다. 04:55 미국 동부시간 관측값은 지연된 정규장 전 자료로 신규 진입 조건을 충족하지 않는다. / 휴장·조기폐장 일정, 실제 세션, 거래정지 여부, 매수·매도 호가의 신선도와 정규장 지표를 확인한다. 미국 동부시간 10:30은 가장 이른 재검토 시각이지 만료시각이 아니다. 확인된 유효기간이 없어 만료나 다음 거래일 자동 연장을 선언하지 않는다.","risk_condition_ko":"325.81 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":348.24,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":350.7585671279432,"relative_volume":0.372814906441818,"spread_bps":0.8626515031694597,"day_high":356.83,"day_low":346.52,"execution_condition_ko":"판단 시각은 2026-10-08T09:59:57.416576+00:00이며 미국 동부시간으로 2026-10-08T05:59:57.416576-04:00이다. 제안된 10:30 최초 진입 가능 시각은 아직 도래하지 않았고 만료시각도 아니다. 유효기한은 미제공 상태이므로 생성하거나 다음 거래일로 이월하지 않는다. / 거래소 달력, 정규장 운영시간, 조기 종료·거래정지 여부와 시세 시각을 별도로 확인한다. 제공된 05:35 미국 동부시간 자료는 지연된 장전 자료이며 정규장 진입이나 방어 조건의 확인으로 사용할 수 없다.","risk_condition_ko":"343.07 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.495,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":99.89778251772458,"relative_volume":0.7081101861202916,"spread_bps":0.9969592742141583,"day_high":100.5299,"day_low":99.29,"execution_condition_ko":"96.19–96.54 지지구간 회복 또는 95.60 재돌파를 관찰한다. 단순 가격 접촉이 아니라 완료된 5분봉과 매수 참여 회복이 필요하다. / 99.15 위에서 5분봉 종가 2회, 재시험 성공, 정규장 거래량가중평균가격 상회 및 동일 경과시간 상대거래량 1.2배 이상을 확인한다.","risk_condition_ko":"95.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SPYM","display_name":"SPYM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":90.985,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":91.22132600858664,"relative_volume":2.853467713705293,"spread_bps":1.0993239157923504,"day_high":91.46,"day_low":90.68,"execution_condition_ko":"실제 거래일·정규장·거래정지 여부와 최신 호가·체결 시각을 검증한다. 향후 주문 전 시간대가 명시된 유효기한을 별도로 확정한다. / 91.05~91.22 회복·재시험, 91.49~91.56 저항 통과, 92.00 돌파·재시험을 관찰하되 가격 조건만으로 매수하지 않는다.","risk_condition_ko":"89.99 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CEG","display_name":"CEG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":282.83,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":291.1579010606485,"relative_volume":1.3294489233435542,"spread_bps":10.62059687754492,"day_high":306.99,"day_low":280.16,"execution_condition_ko":"실제 거래일·정규장 일정·조기폐장·거래정지와 최신 호가·스프레드·5분봉·정규장 거래량가중평균가격·시간대 보정 상대거래량을 확인한다. / 291.00~291.11 또는 286.08~286.40에서 첫 접촉이 아닌 하락 정지와 재회복을 관찰한다. 비용 포함 보상·위험비 2 이상과 변동성에 맞는 손절이 없으면 대기를 유지한다.","risk_condition_ko":"305.8 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":378.26,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":376.4610636321412,"relative_volume":0.3382284776816092,"spread_bps":0.7902743569135233,"day_high":379.965,"day_low":371.4,"execution_condition_ko":"실제 거래일·정규장 운영·거래정지 여부, 최신 가격·호가·스프레드·정규장 거래량가중평균가격을 확인한다. / 368.15~369.10 재시험 후 369.10 위 연속 두 개 정규장 5분봉 종가, 정규장 거래량가중평균가격 회복과 동일 시간대 상대거래량 1.2 이상을 관찰한다. 현재 손절 예시로는 보상비가 부족하므로 관찰 신호이지 매수 승인이 아니다.","risk_condition_ko":"366.14 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NU","display_name":"NU","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":15.485,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":15.584039206244208,"relative_volume":0.2989764717219592,"spread_bps":6.432936635575146,"day_high":15.79,"day_low":15.37,"execution_condition_ko":"14.84~14.98에서 하락 중단·반등·재시험 지지를 확인하고 15.33~15.43 지지 후보와 15.18 추진력 경계를 점검한다. 단순 가격 접촉은 매수 신호가 아니다. / 15.69~15.84와 16.22에서 저항 반응을 확인한다. 손익비는 비용과 부분 청산 경로를 반영하며, 저항 실패와 상승 둔화가 확인되면 보유분의 부분 이익실현을 재판정한다.","risk_condition_ko":"14.84 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":169.06,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":168.27497585236597,"relative_volume":0.38856802541447333,"spread_bps":2.370229912301022,"day_high":169.075,"day_low":166.71,"execution_condition_ko":"162.08–163.19에서 안정화·반등, 하락 구간보다 개선된 거래량, 정규장 거래량가중평균가격 상회 및 독립적으로 타당한 비용 후 보상·위험을 확인한다. / 166.86 위에서 두 번 연속 5분봉 종가 형성, 성공적인 재시험, 같은 시각 기준 상대거래량 1.2 이상을 확인한다.","risk_condition_ko":"160.83 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOG","display_name":"GOOG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":345.11,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":347.6376268814051,"relative_volume":0.3364997787412776,"spread_bps":2.0312522670224213,"day_high":353.53,"day_low":343.51,"execution_condition_ko":"342.80~342.91 재시험 저점 유지 후 정규장 5분봉 두 개가 342.91 위에서 마감하고 거래량가중평균가격 회복 및 동시간대 상대거래량 1.2 이상을 충족하는지 확인한다. / 351.17 위 종가와 최신 20일 평균의 1.2배 이상 거래량, 다음 검증된 거래일 첫 30~60분의 350.09~351.17 지지 전환을 확인한다.","risk_condition_ko":"337.65 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":150.5,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":149.42982866376843,"relative_volume":0.2710980894666698,"spread_bps":1.3313806417242584,"day_high":150.555,"day_low":147.05,"execution_condition_ko":"146.27~146.86에서 장중 저점 갱신이 멈추고 반전한 뒤 신선한 정규장 거래량가중평균가격을 회복하며, 동일 시간대 대비 상대거래량 1.2 이상이 검증되는지 관찰한다. / 정규장 5분봉 종가가 149.70을 초과한 뒤 149.50~149.70 재시험에서 지지가 확인되는지 관찰한다. 상대거래량 1.2는 관측값이 아니라 진입 정책 기준이다.","risk_condition_ko":"146.27 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":212.3,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":210.9770586909135,"relative_volume":0.43936398319049286,"spread_bps":1.8877719571472011,"day_high":212.3,"day_low":208.96,"execution_condition_ko":"201.96–202.98에서 바닥을 형성한 뒤 저점이 높아지고, 완료된 정규장 5분봉 2개가 202.98 위에서 연속 마감하며 재시험을 지키는지 확인한다. / 206.31–206.80 및 207.95–208.69 회복은 단기 구조 개선 신호이지만 단독 매수 신호는 아니다.","risk_condition_ko":"200.78 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LIN","display_name":"LIN","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":482.21,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":483.3106861772134,"relative_volume":0.4150063018604297,"spread_bps":2.4970867321459242,"day_high":486.6,"day_low":480.35,"execution_condition_ko":"477.81~478.24 지지대를 갱신한 뒤 시험·회복과 저점 상승을 관찰한다. 479.00 부근은 매수 주문이 아닌 재평가 후보이며 가까운 저항까지 비용 후 보상·위험 기준을 충족해야 한다. / 484.50 및 485.94 회복은 개선 신호지만 단독 매수 조건은 아니다. 돌파·재지지가 확인되면 기존 저항과 손절 구조를 새로 평가한다.","risk_condition_ko":"477.81 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":271.815,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":268.5368793399659,"relative_volume":0.30023725543204793,"spread_bps":4.056121978650552,"day_high":271.87,"day_low":265.71,"execution_condition_ko":"거래소 일정·실제 세션·거래정지 여부·신선한 매수매도 호가·정규장 봉을 별도로 확인한다. 연구일과 현지 날짜가 같다는 사실만으로 거래 가능 여부나 진입 충족을 판단하지 않는다. / 미국 동부 현지시각 10:30은 검증된 거래일의 최초 시험 매수 검토 시각이며 만료 시각이 아니다. 현재 만료 시각은 없고 다음 거래일로 이월할 주문도 없다.","risk_condition_ko":"269.39 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CDNS","display_name":"Cadence Design Systems","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":349.345,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":352.1295578409687,"relative_volume":0.25004727300039403,"spread_bps":4.580458618418258,"day_high":357.875,"day_low":347.8757,"execution_condition_ko":"우선 거래일, 세션, 최신 호가와 정규장 가격봉, 실적 일정, 공시, 동시간대 거래량 기준 및 포트폴리오 여력을 확인한다. 회사 뉴스 수집 실패를 뉴스 부재로 해석하지 않는다. / 350–353.84에서는 단순 접촉이 아니라 5분봉 저점 상승과 정규장 거래량가중평균가격 회복을 확인한다.","risk_condition_ko":"337.85 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":202.52,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":200.19419519803202,"relative_volume":0.3881231510885518,"spread_bps":3.9696323128062363,"day_high":202.6994,"day_low":192.97,"execution_condition_ko":"194.99 위 정규장 5분봉 마감과 재시험 지지, 정규장 거래량가중평균가격 상회, 동일시각 상대거래량 1.2 이상을 함께 확인한다. / 189.85~190.39 또는 188.18~188.83에서 하락 거래량 감소 후 구간 회복·재시험을 관찰한다. 접촉만으로 매수하지 않는다.","risk_condition_ko":"188.18 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"QCOM","display_name":"Qualcomm","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":174.44,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":173.52731486352297,"relative_volume":0.29723702353246734,"spread_bps":5.737893045674933,"day_high":175.04,"day_low":171.02,"execution_condition_ko":"177.22 위에서 정규장 5분봉 두 개가 연속 마감하고 재시험에 성공하며 정규장 거래량가중 평균가격 위를 유지하고 동일 시각 대비 상대거래량이 1.2 이상인지 확인한다. 179.82의 첫 저항 때문에 이 조건만으로 매수하지 않는다. / 171.77–172.04에서 정규장 지지대 형성과 성공적인 재시험을 관찰한다. 단순 접촉은 신호가 아니다. 신뢰할 무효화 가격과 비용 후 손익비 2:1 이상이 확보되면 추후 별도 소규모 진입을 검토할 수 있다.","risk_condition_ko":"175.35 이하 하락, 2개 봉 확인 후 (방어조치에 최소 거래량 조건을 부과하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NOK","display_name":"NOK","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":10.03,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":10.167050402980637,"relative_volume":0.4353115005534523,"spread_bps":9.925558312654877,"day_high":10.45,"day_low":9.9,"execution_condition_ko":"10.08–10.20에서 지지 재시험 후 완성된 5분봉 2개가 지지를 유지하고, 최신 정규장 거래량가중평균가격 위에서 동시간대 상대거래량 1.2 이상을 충족하는지 관찰한다. 실제 가격의 비용 후 보상/위험비 검증은 별도다. / 10.55 회복은 단기 구조 개선 신호일 뿐 단독 매수 신호가 아니다. 회복 뒤에도 낮은 지지 가격에 체결된다고 가정하지 않는다.","risk_condition_ko":"10.08 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"META","display_name":"Meta Platforms","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":719.2501,"market_data_asof":"2026-10-08T15:10:00-04:00","session_vwap":720.3370964457463,"relative_volume":0.4088535986249937,"spread_bps":2.5066495843132475,"day_high":724.76,"day_low":711.6832,"execution_condition_ko":"713.19~720.15 지지, 완성된 5분봉 저점 상승, 720.15 재탈환 후 두 봉 유지, 당일 거래량가중평균가격 상회와 동일 경과시간 상대거래량 1.2 이상을 함께 확인한다. 충족해도 실제 손절과 순손익비 검증 전에는 진입하지 않는다. / 727.28과 733.34의 순차 회복·재시험을 관찰한다. 738.29와 747.60은 저항이며, 가까운 미돌파 저항을 건너뛰어 진입 보상을 계산하지 않는다.","risk_condition_ko":"713.19 이하 하락, 종가 확인 후 (완료된 직전 5정규장 평균보다 당일 거래량 증가) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-08T15:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-09T03:17:31.821877+09:00",
  "as_of": "2026-10-08T13:10:00-04:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
