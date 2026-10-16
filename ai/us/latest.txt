# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-16T14:10:42.654626+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261016T230356_local-scheduler-us-overlay_only",
  "producer_finished_at": "2026-10-16T23:07:06.643656+09:00",
  "analysis_run_id": "20261016T175401_local-scheduler-us-full",
  "analysis_completed_at": "2026-10-16T20:07:39.555584+09:00",
  "analysis_trade_date_oldest": "2026-10-15",
  "analysis_trade_date_latest": "2026-10-15",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-16T10:00:00-04:00",
  "market_data_latest_at": "2026-10-16T10:05:00-04:00",
  "market_data_status": "FRESH"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-16T23:07:01.029799+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-16T23:07:01.029799+09:00",
    "run_started_at": "2026-10-16T23:03:56.649235+09:00",
    "run_finished_at": "2026-10-16T23:07:06.643656+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23796481,
    "total_market_value_krw": 23733302,
    "total_unrealized_pnl_krw": -63179,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 108041,
    "total_equity_krw": 24817995
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 549743,
      "current_price_krw": 559115,
      "market_value_krw": 6709380,
      "unrealized_pnl_krw": 112464
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 294654,
      "current_price_krw": 291114,
      "market_value_krw": 3202255,
      "unrealized_pnl_krw": -38944
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 427378,
      "current_price_krw": 463776,
      "market_value_krw": 2782656,
      "unrealized_pnl_krw": 218385
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 269277,
      "current_price_krw": 291862,
      "market_value_krw": 1751175,
      "unrealized_pnl_krw": 135511
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1894291,
      "current_price_krw": 1647563,
      "market_value_krw": 1647563,
      "unrealized_pnl_krw": -246728
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 560163,
      "current_price_krw": 540559,
      "market_value_krw": 1621679,
      "unrealized_pnl_krw": -58811
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1484078,
      "current_price_krw": 1262007,
      "market_value_krw": 1262007,
      "unrealized_pnl_krw": -222071
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 135539,
      "current_price_krw": 135624,
      "market_value_krw": 1220617,
      "unrealized_pnl_krw": 759
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 367349,
      "current_price_krw": 463223,
      "market_value_krw": 926446,
      "unrealized_pnl_krw": 191747
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1430772,
      "current_price_krw": 1710046,
      "market_value_krw": 745691,
      "unrealized_pnl_krw": 121781
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 667783,
      "current_price_krw": 619797,
      "market_value_krw": 619797,
      "unrealized_pnl_krw": -47986
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 573955,
      "current_price_krw": 456500,
      "market_value_krw": 456500,
      "unrealized_pnl_krw": -117455
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 137248,
      "current_price_krw": 111568,
      "market_value_krw": 446272,
      "unrealized_pnl_krw": -102720
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 350394,
      "current_price_krw": 341264,
      "market_value_krw": 341264,
      "unrealized_pnl_krw": -9130
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1266.025,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":1260.4940984106147,"relative_volume":0.7105082284636723,"spread_bps":11.667916800608001,"day_high":1266.7841,"day_low":1255.0102,"execution_condition_ko":"1230.66–1235.04 재시험에서 완료된 5분봉 2개의 안정화, 저점 상승, 반등 거래량 증가 및 정규장 거래량가중평균가격 회복을 확인한다. 실제 체결가에서 순보상위험비를 다시 계산한다. / 1275.88 돌파와 재시험을 관찰하되 1280.28–1292.65 저항 때문에 이를 독립적인 매수 신호로 사용하지 않는다.","risk_condition_ko":"1,216.71 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":215.96,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":216.00957470563438,"relative_volume":1.3979211603417783,"spread_bps":0.4625453872657048,"day_high":216.295,"day_low":215.5,"execution_condition_ko":"215.42 위 5분봉 최소 두 개 마감과 215.00~215.42 재지지, 정규장 거래량가중평균가격 상회 및 비교 가능한 구간 대비 거래량 확대를 확인한다. / 213.90~214.20에서는 도달 자체가 아니라 하락 정지와 반등을 확인한다. 중립 분석가가 지적한 눌림 전술 고유의 실패 조건을 명확히 하기 전에는 해당 진입을 활성화하지 않는다.","risk_condition_ko":"212.54 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":343.91,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":345.4139481395334,"relative_volume":3.228472108210097,"spread_bps":1.165365342033668,"day_high":347.82,"day_low":342.03,"execution_condition_ko":"348.15 돌파·재시험 지지, 정규장 거래량가중평균가격 상회, 동일 시간대 상대거래량 1.2 이상과 비용 반영 보상/위험 2 이상 확인 / 337.08~339.05에서 저점 유지·반등 후 재시험 지지 확인; 347.09를 우선 저항으로 손익비 재계산","risk_condition_ko":"337.08 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":253.13,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":254.6927225680345,"relative_volume":1.5309305891567222,"spread_bps":2.366770541596082,"day_high":255.54,"day_low":252.9,"execution_condition_ko":"248.65–250.02 시험 후 저점 하락이 멈추고 250.02를 회복하여 재시험을 지지하는지 확인한다. / 253.54 부근 수급과 255.62·257.52 회복을 확인한다. 이는 구조 개선이지 독립적인 전체 배정 신호가 아니다.","risk_condition_ko":"244.3 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":344.32,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":347.97838715479486,"relative_volume":1.2304815430402045,"spread_bps":2.881097121782992,"day_high":350.66,"day_low":344.05,"execution_condition_ko":"340~343 시험 후 342 이상 정규장 5분봉 두 개 유지, 정규장 거래량가중평균가격 상회 및 동일 경과시간 상대거래량 1.0 이상을 확인한다. 342 이상이라는 조건은 무제한 추격 허용이 아니다. / 352.15~353.78 선행 저항과 356.86~359.44 상단 저항 반응을 확인하고, 청산 구조 변경 시 비용 후 손익비를 재계산한다.","risk_condition_ko":"340.42 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":415.125,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":416.3178571980476,"relative_volume":1.1328634251753686,"spread_bps":3.116048850058017,"day_high":421.4906,"day_low":412.4403,"execution_condition_ko":"423.66–428.06 회복 후 430.00–433.84의 지지 재확인을 관찰한다. 하락 공백 해소만으로 매수하지 않는다. / 433.84 위 종가, 개선된 모멘텀, 후속 지지 확인 시 현재의 위험 축소 판단을 재심의한다.","risk_condition_ko":"433.84 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":1221.0,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":1216.866005186605,"relative_volume":0.5646192609277433,"spread_bps":10.373529387550041,"day_high":1227.74,"day_low":1207.2,"execution_condition_ko":"1260.24 회복과 재시험을 관찰하되 단독 매수 신호로 사용하지 않는다. / 1298.71–1309 회복 이후 1327 유지, 비교 가능한 정규장 상대거래량 1.2 이상, 당일 거래량가중평균가격 상회와 모멘텀 개선을 확인한다.","risk_condition_ko":"1,195 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":401.17,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":399.8401100879675,"relative_volume":1.0212219950647943,"spread_bps":9.95346753925342,"day_high":403.725,"day_low":395.37,"execution_condition_ko":"거래일과 장 운영 상태, 동기화된 최신 호가, 실제 보유량, 승인된 손실·집중도 한도를 확인하고 초과 노출을 우선 처리한다. / 404.40과 408.85 회복, 408.85 이상에서 완료된 5분 봉 두 개, 거래량가중평균가격 상회 및 시간대 조정 상대거래량 1.2 이상을 관찰한다. 이것만으로 매수를 승인하지 않는다.","risk_condition_ko":"417 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":935.105,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":934.0357835732872,"relative_volume":1.1935776155380335,"spread_bps":24.968262914755027,"day_high":951.0,"day_low":916.015,"execution_condition_ko":"확인된 정규장에서 미국 동부시간 10:30 이후 941.78 위의 5분 봉 2개, 성공적인 재시험, 당일 거래량가중평균가격 상회와 동일 시각 상대 거래량 1.2 이상을 확인한다. / 950.00~957.63, 965.42, 972.94~973.44의 저항을 순차 평가한다. 회복 신호만으로 신규 매수하지 않는다.","risk_condition_ko":"931.99 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":458.615,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":461.530523294966,"relative_volume":1.4847807405352424,"spread_bps":10.27917810316418,"day_high":473.185,"day_low":451.3,"execution_condition_ko":"482.00 회복 이후 487.94 위 정규장 5분봉 안착·재시험 지지·정규장 거래량가중평균가격 상회와 비교 가능한 거래량 증가를 관찰한다. 자동 매수하지 않는다. / 452.42 재시험에서 저점 유지·매도량 둔화·반등 구조를 확인한다. 이탈과 회복 실패 시 전술 보유를 손절한다.","risk_condition_ko":"512.98 이상 도달, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":338.285,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":338.50959887568524,"relative_volume":1.4099067869163875,"spread_bps":3.845869388358715,"day_high":339.5495,"day_low":336.22,"execution_condition_ko":"335.20–338.65 방어 및 344.70–346.25 회복·재시험은 관찰 신호이며 자동 매수 조건이 아니다. / 갱신된 356.81 기준 위 정규장 종가, 비교 기준이 확인된 상대 거래량 1.2 이상, 다음 거래일 지지 확인 시 신규 진입 적합성을 재평가한다.","risk_condition_ko":"334.61 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":82.75,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":82.66622562930749,"relative_volume":0.7427336869415452,"spread_bps":1.2099945550251212,"day_high":82.925,"day_low":82.23,"execution_condition_ko":"판단 시각은 2026-10-16T05:23:29.315924-04:00이고 일별 가격 기준일은 2026-10-15이다. 05:10 지연 관측값은 현재 체결가나 정규장 진입 조건을 입증하지 않는다. 거래일·휴장·조기 종료 일정, 거래 정지, 호가 시각과 매수·매도 가격 차이를 별도로 확인한다. / 10:30은 별도 승인 후 시험 진입이 가능해지는 가장 이른 미국 동부 현지 시각일 뿐 만료 시각이나 자동 진입 시각이 아니다. 승인된 진입 기한은 없으며 만료 또는 다음 거래일 연장을 추정하지 않는다.","risk_condition_ko":"81.94 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":100.575,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":100.575866056167,"relative_volume":1.4706428403250063,"spread_bps":0.9942828734780131,"day_high":100.58,"day_low":100.57,"execution_condition_ko":"서로 다른 50일 평균 100.2040과 100.5466 및 과거 가격의 분배금 조정 방식을 대조한다. / 100.54–100.55 지지 유지와 실시간 정규장 거래량가중평균가격 회복을 관찰한다.","risk_condition_ko":"100.49 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":216.51,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":216.21898089830313,"relative_volume":1.3872714921012137,"spread_bps":1.853825833062615,"day_high":216.8,"day_low":215.07,"execution_condition_ko":"보유량, 계좌 자산, 상관된 기술주 노출과 기존 손절 조건을 확인한다. 정보 부재만으로 과도한 보유를 추정하지 않는다. / 재무제표 통화, 원단위, 회계기간, 주당이익·주식 수 기준, 예탁증서 해당 여부와 전환비율, 공시 공개 시각을 확인한다. 거래 통화가 미국 달러라는 사실로 재무제표 기준을 확정하지 않는다.","risk_condition_ko":"212.85 이하 하락, 거래량 조건 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":620.655,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":619.5406039743389,"relative_volume":1.053193222146612,"spread_bps":4.6785890020886445,"day_high":622.46,"day_low":617.87,"execution_condition_ko":"606.61–607.06 재시험 후 607.06 위에서 연속 2개 5분봉 마감, 저점 상승, 정규장 거래량가중평균가격 회복, 동일 시각 상대거래량 1.2 이상을 확인한다. / 619.80 돌파 후 재시험 유지, 정규장 거래량가중평균가격 상회, 동일 시각 상대거래량 1.2 이상을 확인한다.","risk_condition_ko":"606.61 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":95.94,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":96.06895841656649,"relative_volume":0.9251550252353755,"spread_bps":7.284458088349361,"day_high":96.49,"day_low":95.595,"execution_condition_ko":"기준 시각은 2026-10-16T06:27:48.383300-04:00이다. 10:30 미국 동부시간은 최초 관찰 가능 시각이지 만료 시각이 아니다. 정규장 개장 여부와 달력은 미확인이다. / 06:00 미국 동부시간의 지연된 172주 장전 자료로 체결 가능 가격이나 매수 조건 충족을 판단하지 않는다. 최신 호가·유동성·거래 상태를 확인한다.","risk_condition_ko":"93.96 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":403.575,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":402.99518463067636,"relative_volume":0.6759292970579983,"spread_bps":7.944192050844071,"day_high":404.742,"day_low":400.61,"execution_condition_ko":"395.26–397.19 시험 후 높아지는 저점과 397.19 위의 완료된 15분 봉 두 개를 확인한다. / 403.21 돌파·재시험을 확인하되, 404.47의 지연된 장전 관측값은 최신 저항으로 간주하지 않는다.","risk_condition_ko":"395.26 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":159.745,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":158.80686459388073,"relative_volume":0.8702726511450248,"spread_bps":1.8823529411747584,"day_high":159.98,"day_low":157.56,"execution_condition_ko":"156.53~156.79 첫 지지의 유지 여부. 이탈만으로 자동 매도하지 않고 154.29 방어선과 함께 평가한다. / 154.29~154.75 회복·재시험과 비용 후 손익비 2 이상을 동시에 충족하는 실제 체결 구조 확보.","risk_condition_ko":"154.29 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":105.53,"market_data_asof":"2026-10-16T10:05:00-04:00","session_vwap":105.46079939534057,"relative_volume":1.4859167813983774,"spread_bps":1.8953752843059153,"day_high":105.73,"day_low":105.17,"execution_condition_ko":"검증된 정규장에서 현지시각 10:30 이후 104.89 위 5분봉 마감과 재시험 성공, 정규장 거래량가중평균가격 상회, 동일 경과시간 상대거래량 1.2 이상을 관찰한다. / 100.59–101.27에서 매도 거래량 감소와 반등 확인을 관찰한다. 가격 도달만으로 매수하지 않는다.","risk_condition_ko":"103.04 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:35:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":285.52,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":283.8934940664727,"relative_volume":1.0515884532678876,"spread_bps":17.923981232538978,"day_high":285.52,"day_low":283.0,"execution_condition_ko":"281.75–283.66 회복 여부와 282.81 경고선 관찰. 회복 자체는 매수 승인이 아니다. / 초기 지지 실패 시 279.40–279.58, 이후 273–276의 안정화와 회복 확인.","risk_condition_ko":"272.03 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AMT","display_name":"AMT","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":183.04,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":182.07405256592247,"relative_volume":0.31231818739994516,"spread_bps":13.710274479695084,"day_high":183.1799,"day_low":180.54,"execution_condition_ko":"179.36~180.37 회복 후 두 개의 최신 정규장 5분봉 지지, 거래량가중평균가격 상회 및 동시간대 상대거래량 1.2 이상 확인. 기존 손절 구조로는 손익비가 부족하므로 가격 회복만으로 주문하지 않는다. / 184.75 돌파·재시험, 정규장 종가 유지와 다음 확인된 거래일의 후속 지지를 관찰한다. 비용 후 손익비가 부족하면 돌파해도 매수하지 않는다.","risk_condition_ko":"176.42 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":222.09,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":222.33789934647007,"relative_volume":0.5494104536350709,"spread_bps":2.251795807155439,"day_high":223.41,"day_low":220.41,"execution_condition_ko":"217.77–218.05 지지 여부를 관찰한다. 이탈만으로 중기 추세 반전을 확정하지 않는다. / 213.75–215.00에서는 매도 거래량 감소, 저점 방어, 후속 5분봉 고점 회복과 이탈한 지지선 재탈환을 확인한다. 현 목표·손절 구성의 보상위험비 충돌이 해소되지 않으면 거래하지 않는다.","risk_condition_ko":"214.08 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"SPYM","display_name":"SPYM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":90.795,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":90.9090289984097,"relative_volume":0.6053603252363585,"spread_bps":1.1001705264321595,"day_high":91.02,"day_low":90.75,"execution_condition_ko":"90.24~90.32 또는 89.98~90.00 시험 후 회복, 저점 상승, 연속 5분봉 두 개의 지지 유지와 동시간대 상대거래량 1.2 이상을 관찰한다. / 90.90~91.07 회복 후 91.37 및 91.65~91.74까지 남은 보상과 실제 세션 거래량가중평균가격을 다시 검증한다.","risk_condition_ko":"90 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":175.97,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":176.43601038902847,"relative_volume":0.8284327931962844,"spread_bps":2.2705341431567256,"day_high":177.365,"day_low":175.44,"execution_condition_ko":"170.42~171.01 지지, 저점 상승, 신선한 정규장 거래량가중평균가격 회복 및 동시간대 상대거래량 1.2 이상과 비용 후 보상 재계산. / 178.69 위 종가와 다음 실제 거래일 첫 30~60분 지지 확인. 돌파 경로는 별도 손절·보상 설계 없이는 매수하지 않는다.","risk_condition_ko":"170.42 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MSFT","display_name":"Microsoft","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":536.661,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":540.301942404524,"relative_volume":1.0089863250490085,"spread_bps":2.9780739306868527,"day_high":543.81,"day_low":534.84,"execution_condition_ko":"2026-10-16T06:11:24.063336-04:00은 제안된 10:30 활성화 시각보다 이르다. 10:30은 만료시각이 아니며 현재 주문 만료시각은 없다. 거래일 달력·실제 세션·거래 상태·호가 신선도는 별도로 확인한다. / 531.22 시험 후 회복, 장중 저점 상승, 정규장 거래량가중평균가격 상회 및 같은 시각 상대거래량 1.2 이상을 관찰한다. 이 조건만으로 매수를 승인하지 않는다.","risk_condition_ko":"526.47 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"META","display_name":"Meta Platforms","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":727.3574,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":733.2242892569818,"relative_volume":1.2250144326038879,"spread_bps":4.3767866179740444,"day_high":738.49,"day_low":725.99,"execution_condition_ko":"711.68~718.67 지지 시험 후 높아진 저점과 장중 거래량가중평균가격 회복, 동일 시간대 상대거래량 1.2 이상 확인 / 747.60 돌파 후 743.97~747.60 재지지와 실제 체결가격 기준 비용 후 보상위험비 재계산","risk_condition_ko":"711.68 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"NU","display_name":"NU","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":14.885,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":14.860356662242928,"relative_volume":0.21924474503861455,"spread_bps":6.736274840013329,"day_high":14.945,"day_low":14.71,"execution_condition_ko":"14.40–14.45 지지 유지와 14.66 회복을 관찰한다. 지지선 접촉 자체는 매수 신호가 아니다. / 15.02–15.06 회복 후 재시험, 정규장 거래량가중평균가격 상회 및 동일 경과시간 기준 상대거래량 1.2 이상을 확인한다.","risk_condition_ko":"14.33 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"BBD","display_name":"BBD","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":4.05,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":4.037437291605702,"relative_volume":0.7084109916275028,"spread_bps":24.844720496896084,"day_high":4.06,"day_low":4.02,"execution_condition_ko":"3.98–4.03 지지 후 4.12–4.16 회복과 성공적인 재시험을 확인한다. / 4.26 위 종가와 비교 가능한 시간대의 상대 거래량 1.2 이상을 확인하고, 중간 저항을 반영해 순보상위험비를 다시 산출한다.","risk_condition_ko":"3.98 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MRVL","display_name":"Marvell Technology","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":233.9687,"market_data_asof":"2026-10-16T10:00:00-04:00","session_vwap":234.34829842124552,"relative_volume":1.2323802688836298,"spread_bps":3.433476394849102,"day_high":236.49,"day_low":230.66,"execution_condition_ko":"위험 대응 조건: 240.65 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"240.65 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":204.31,"market_data_asof":"2026-10-16T10:05:00-04:00","session_vwap":203.01748409758503,"relative_volume":0.6730367217153456,"spread_bps":18.66038106462502,"day_high":204.43,"day_low":201.69,"execution_condition_ko":"위험 대응 조건: 198 이하 하락, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"198 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-16T10:35:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-16T03:13:14.985947+09:00",
  "as_of": "2026-10-15T14:00:00-04:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
