# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-06T08:18:24.159921+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261006T171526_github-actions-overlay-us-37367005555-2",
  "producer_finished_at": "2026-10-06T17:16:20.217963+09:00",
  "analysis_run_id": "20261006T033425_github-actions-us",
  "analysis_completed_at": "2026-10-06T05:35:33.071536+09:00",
  "analysis_trade_date_oldest": "2026-10-02",
  "analysis_trade_date_latest": "2026-10-02",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-09-22T11:10:00-04:00",
  "market_data_latest_at": "2026-10-01T11:25:00-04:00",
  "market_data_status": "MISSING"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-06T17:16:17.570260+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-06T17:16:17.570260+09:00",
    "run_started_at": "2026-10-06T17:15:26.458537+09:00",
    "run_finished_at": "2026-10-06T17:16:20.217963+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23972933,
    "total_market_value_krw": 25861822,
    "total_unrealized_pnl_krw": 1888889,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 88750,
    "total_equity_krw": 26927224
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 553819,
      "current_price_krw": 658600,
      "market_value_krw": 7903209,
      "unrealized_pnl_krw": 1257373
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 296839,
      "current_price_krw": 287051,
      "market_value_krw": 3157561,
      "unrealized_pnl_krw": -107673
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 430547,
      "current_price_krw": 473274,
      "market_value_krw": 2839645,
      "unrealized_pnl_krw": 256359
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1908339,
      "current_price_krw": 2029571,
      "market_value_krw": 2029571,
      "unrealized_pnl_krw": 121232
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 271274,
      "current_price_krw": 327504,
      "market_value_krw": 1965028,
      "unrealized_pnl_krw": 337383
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 564317,
      "current_price_krw": 588515,
      "market_value_krw": 1765547,
      "unrealized_pnl_krw": 72595
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1495083,
      "current_price_krw": 1349044,
      "market_value_krw": 1349044,
      "unrealized_pnl_krw": -146039
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 136544,
      "current_price_krw": 136474,
      "market_value_krw": 1228274,
      "unrealized_pnl_krw": -630
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 370073,
      "current_price_krw": 452353,
      "market_value_krw": 904706,
      "unrealized_pnl_krw": 164559
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 672735,
      "current_price_krw": 755326,
      "market_value_krw": 755326,
      "unrealized_pnl_krw": 82591
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1441383,
      "current_price_krw": 1559232,
      "market_value_krw": 679926,
      "unrealized_pnl_krw": 51389
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 578211,
      "current_price_krw": 495241,
      "market_value_krw": 495241,
      "unrealized_pnl_krw": -82970
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 138265,
      "current_price_krw": 111329,
      "market_value_krw": 445316,
      "unrealized_pnl_krw": -107747
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 352992,
      "current_price_krw": 343428,
      "market_value_krw": 343428,
      "unrealized_pnl_krw": -9564
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":82.4,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":82.30007100738926,"relative_volume":0.6180921857000512,"spread_bps":1.2170632264352361,"day_high":82.56,"day_low":82.08,"execution_condition_ko":"최신 정규장 자료에서 82.16 상향 돌파, 상대거래량 1.2 이상, 당시 거래량가중평균가격 상회 / 83.93 위 거래량 동반 종가와 다음 확인된 거래일의 83.43~83.93 유지 또는 재돌파","risk_condition_ko":"81.32 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":455.25,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":455.8352236225735,"relative_volume":0.3452409061822126,"spread_bps":4.620106262443586,"day_high":457.818,"day_low":453.461,"execution_condition_ko":"TSM의 최신 가격 487.46달러 상회, 갱신된 거래량가중평균가 지지, 상대 거래량 1.2 이상 및 정상 거래 확인 / 갱신된 거래량가중평균가, 476.40달러, 474.79달러의 순차 이탈 감시","risk_condition_ko":"474.79 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":430.145,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":427.7672464175203,"relative_volume":0.3205634323042532,"spread_bps":17.29982466393943,"day_high":431.2,"day_low":423.0,"execution_condition_ko":"최신 가격의 439.76 및 최신 거래량가중평균가격 상회와 상대거래량 1.2 이상 확인 / 439.76 위 정규장 종가와 다음 실제 거래일의 유지 또는 재돌파 확인","risk_condition_ko":"431.38 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":963.765,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":955.8304141486565,"relative_volume":0.5028660692294686,"spread_bps":10.775354775940334,"day_high":966.545,"day_low":942.0,"execution_condition_ko":"최신 정규장 가격의 1006달러 상향 유지, 거래량가중평균가격 상회, 상대거래량 1.2 이상 / 1006달러 위 종가와 다음 확인된 정규거래일 첫 30~60분 지지 또는 재돌파","risk_condition_ko":"965.04 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1345.02,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":1347.024088217389,"relative_volume":0.25704530929029445,"spread_bps":12.394256829908104,"day_high":1355.7,"day_low":1331.0,"execution_condition_ko":"검증된 정규장에서 최신 가격이 1465.50 위를 유지하고 갱신된 거래량가중평균가격 위이며 상대 거래량이 1.2 이상인지 확인 / 확인된 종가가 1465.50 위인지 확인하고 다음 확인된 거래일 첫 30~60분에 지지 또는 재돌파하는지 점검","risk_condition_ko":"1,432.38 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":348.43,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":349.59644559424277,"relative_volume":0.5344749587000754,"spread_bps":4.324448993123471,"day_high":354.45,"day_low":346.09,"execution_condition_ko":"최신 가격이 366.55 위에서 유지되고 당일 거래량가중평균가격 위에 있으며 상대거래량이 1.2 이상인지 확인 / 366.55 위의 정규장 종가와 다음 검증된 거래일의 유지·재돌파 확인; 추가 매수 전 372.67 돌파 가능성과 기대손익 재평가","risk_condition_ko":"352.17 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":246.82,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":248.8281065591362,"relative_volume":0.8765560910064908,"spread_bps":2.433583451632621,"day_high":251.83,"day_low":246.1167,"execution_condition_ko":"최신 정규장 가격이 254.53과 거래량 가중 평균가격 위에 있고 상대거래량이 1.2 이상일 때 소규모 선행 진입의 순손익비 재검토 / 256.54 위 거래량 동반 종가 확인; 단독으로는 추격 매수 금지","risk_condition_ko":"250.18 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":207.61,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":207.73611514101086,"relative_volume":1.238871025133039,"spread_bps":0.4818232190618577,"day_high":208.76,"day_low":207.16,"execution_condition_ko":"실제 정규장에서 211.30 위 돌파·유지, 갱신된 거래량가중평균가격 상회 및 시간 보정 상대거래량 1.2 이상 / 211.30 위 종가 확인 후 다음 실제 거래일 첫 30~60분에 해당 가격 유지 또는 재돌파","risk_condition_ko":"208.92 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.4,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":100.4054740579839,"relative_volume":3.0019584272320334,"spread_bps":0.9959663363369259,"day_high":100.41,"day_low":100.4,"execution_condition_ko":"SGOV의 최신 체결 가능 호가·거래 상태·순자산가치 괴리와 스프레드 확인 / SGOV의 100.45 초과 유지, 거래량가중평균가격 상회 및 상대 거래량 1.0 이상 확인","risk_condition_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":230.6607,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":230.07904710779678,"relative_volume":0.6562239497557574,"spread_bps":1.3104728622911932,"day_high":231.91,"day_low":228.16,"execution_condition_ko":"신선한 정규장 자료에서 237.88 재시험, 실시간 거래량가중평균가격 상회 및 상대거래량 1.2 이상 확인 / 237.88 위 종가와 상대거래량 1.2 이상을 확인한 뒤 다음 거래일 첫 30~60분 지지 확인","risk_condition_ko":"233.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":328.67,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":330.31185421777076,"relative_volume":0.5861155633840901,"spread_bps":1.2136290542801802,"day_high":332.4816,"day_low":328.37,"execution_condition_ko":"정규장 실시간 336.19 상향 돌파, 335.30 및 실시간 거래량가중평균가격 유지, 상대 거래량 1.2 이상 확인 / 345.34~346.62 저항대의 거래량 동반 돌파 여부","risk_condition_ko":"330.61 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":531.01,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":529.5150000548582,"relative_volume":0.5004037443721804,"spread_bps":11.395362087630767,"day_high":543.15,"day_low":520.2,"execution_condition_ko":"정규장 여부와 최신 호가·실시간 거래량가중평균가·상대 거래량 확인 후 560.10 회복 관찰 / 상대 거래량 1.2 이상인 568.00 위 종가 및 다음 거래일 유지·재돌파 확인","risk_condition_ko":"546 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":340.9,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":344.59392538406354,"relative_volume":1.0332478649951997,"spread_bps":2.939879464940935,"day_high":353.22,"day_low":339.62,"execution_condition_ko":"최신 가격 347.89 상회, 실시간 거래량가중평균가격 상회, 동시간대 상대 거래량 1.2 이상 및 거래 가능 상태 확인 / 349.91과 352.60 저항 통과, 354.70 위 종가 및 다음 거래일 유지 여부","risk_condition_ko":"338.54 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1150.367,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":1148.4646542005685,"relative_volume":0.4488082957208583,"spread_bps":7.116202377852436,"day_high":1158.72,"day_low":1141.5,"execution_condition_ko":"실제 정규장에서 1165.73 및 최신 거래량가중평균가격 위 유지와 상대 거래량 1.2 이상 / 1176.28 위의 확인된 종가와 상대 거래량 1.2 이상, 이후 다음 실제 거래일의 유지 또는 재돌파","risk_condition_ko":"1,136.66 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":95.33,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":95.0477931729686,"relative_volume":1.4051946532399757,"spread_bps":1.0488226965221987,"day_high":95.44,"day_low":94.34,"execution_condition_ko":"정규장과 거래 가능 상태, 실시간 호가의 시점 확인 / 96.96 위 가격, 실시간 거래량가중평균가격 지지, 동시간대 상대거래량 1.2 이상","risk_condition_ko":"95.52 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":163.615,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":163.10225724081786,"relative_volume":0.3303051381312368,"spread_bps":4.27546190258013,"day_high":163.78,"day_low":160.84,"execution_condition_ko":"최신 시세·거래 가능 상태·실제 정규장 여부 확인 / 164.74달러 상회 종가와 제안 기준 상대거래량 1.2 이상 및 다음 실제 거래일 지지 확인","risk_condition_ko":"162.33 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"URI","display_name":"United Rentals","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"갱신된 정규장 가격의 1090.605달러 상회 유지, 거래량가중평균가격 상회 및 동시간대 상대거래량 1.2 이상 확인 / 1067.7201~1066.70달러 지지 재시험과 종가 확인","risk_condition_ko":"1,066.7 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"CAT","display_name":"CAT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"확인된 정규장에서 858.87 상향 돌파, 상대 거래량 1.2 이상, 당일 거래량가중평균가격 상회 / 858.87 위 종가와 거래량 2795464주 이상, 이후 다음 거래일 지지 유지","risk_condition_ko":"836.46 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"CDNS","display_name":"Cadence Design Systems","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"CDNS가 새로 산출한 거래량가중평균가격을 회복하고 상대 거래량 1.2 이상으로 360.145를 돌파하는지 확인 / CDNS의 352.00~351.35 지지 구간과 확인된 종가 이탈 여부 감시","risk_condition_ko":"351.35 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":260.6,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":260.54740970671884,"relative_volume":0.2874996589392729,"spread_bps":7.660193802902778,"day_high":262.3158,"day_low":259.0,"execution_condition_ko":"새로 확인된 정규장 시세가 269.39 위에 안착하고 실시간 거래량 가중 평균가격 위에서 동시간대 상대거래량 1.2 이상 / 269.39 위의 확인된 마감 후 다음 거래일 지지 또는 재돌파; 270.93 저항 재평가","risk_condition_ko":"257.84 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SCCO","display_name":"SCCO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":198.5001,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":199.14766400387316,"relative_volume":0.39421060654979095,"spread_bps":23.753569352841527,"day_high":202.95,"day_low":197.42,"execution_condition_ko":"SCCO의 211.78 상향 종가와 상대거래량 1.2 이상 확인 / 적격 돌파 다음 거래일 첫 30~60분에 211.78 유지 또는 회복","risk_condition_ko":"196.78 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SNPS","display_name":"Synopsys","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"새 정규장 호가에서 거래량가중평균가격 회복, 500.03 돌파, 상대거래량 1.2 이상을 확인하되 이는 자동 매수 승인이 아님 / 500.03 위 종가 후 다음으로 확인된 거래일 첫 30~60분간 해당 가격 지지 여부","risk_condition_ko":"500.03 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":498.8399963378906,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":497.6760796843775,"relative_volume":0.9259601254798294,"spread_bps":null,"day_high":499.75,"day_low":495.9599914550781,"execution_condition_ko":"새 정규 거래 자료에서 499.01 재시험·회복, 거래량가중평균가격 유지, 동일 시각 대비 상대거래량 1.2 이상 확인 / 507.38 위 종가 후 다음 실제 거래일의 지지 또는 재돌파 확인; 돌파 자체는 자동 매수 아님","risk_condition_ko":"495.85 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":206.35,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":205.68253093841574,"relative_volume":0.3789799886303238,"spread_bps":3.391719359449242,"day_high":206.59,"day_low":202.915,"execution_condition_ko":"CVX의 실시간 207.23 돌파 후 208.60 위 유지, 실시간 거래량가중평균가격 상회 및 동시간대 상대거래량 1.2 이상 확인 / CVX의 208.60 위 종가와 다음 확인된 거래일의 지지 또는 재돌파 확인","risk_condition_ko":"201.94 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":144.18,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":144.149681986646,"relative_volume":0.41630609572869226,"spread_bps":0.6935534209516181,"day_high":145.0,"day_low":143.51,"execution_condition_ko":"검증된 정규장에서 146.21~146.60 회복, 당일 거래량가중평균가격 상회 및 비교 가능한 상대 거래량 1.2 이상 / 149.48 위 종가와 다음 검증된 거래일 첫 30~60분의 유지","risk_condition_ko":"143.4 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":187.78,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":188.37554774188987,"relative_volume":0.29160855990367424,"spread_bps":7.970032677134279,"day_high":193.12,"day_low":186.92,"execution_condition_ko":"정규장에서 188.40~188.91 회복 여부 확인; 188.91은 과거 평균이며 당일 거래량가중평균가격이 아님 / 190.36 위 유지, 당일 거래량가중평균가격 지지, 동시간대 상대거래량 1.2 이상을 함께 확인","risk_condition_ko":"185.3 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MRK","display_name":"MRK","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":144.96,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":144.63147846465407,"relative_volume":0.3495398770463946,"spread_bps":2.7567195037899404,"day_high":145.388,"day_low":144.0,"execution_condition_ko":"MRK의 2026-10-05 공식 종가와 다음 실제 정규장 확인 / 141.92 회복, 당일 거래량가중평균가격 상회, 상대거래량 1.2 이상","risk_condition_ko":"141.7 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NU","display_name":"NU","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"다음 확인된 정규장에서 거래 상태와 신선한 가격·당일 거래량가중평균가격·동시간대 상대거래량을 확인하고 15.46 유지 여부 관찰 / 14.86 종가 이탈 시 과거 기준선 14.70과 14.25 재점검","risk_condition_ko":"14.86 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"SPYM","display_name":"SPYM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":89.565,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":89.73740763752808,"relative_volume":0.612860487048461,"spread_bps":1.1182555213872087,"day_high":90.0799,"day_low":89.31,"execution_condition_ko":"실시간 가격 91.40 초과, 해당 거래일 거래량가중평균가격 지지, 시간 보정 상대거래량 1.2 이상 동시 확인 / 확인된 종가 91.40 초과 후 다음 거래일 지지 또는 재돌파","risk_condition_ko":"90.59 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-01T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"META","display_name":"Meta Platforms","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":747.72,"market_data_asof":"2026-09-22T11:10:00-04:00","session_vwap":746.3958786640645,"relative_volume":1.8009834273322114,"spread_bps":4.005982266851225,"day_high":757.27,"day_low":730.0,"execution_condition_ko":"검증된 정규거래에서 746.70 위 유지, 당일 거래량가중평균가 지지, 동시간대 상대거래량 1.2 이상 확인 / 750.58 위 종가와 다음 확인된 거래일에 746.70 유지 또는 회복","risk_condition_ko":"726.2 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-09-22T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-22T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-06T03:17:42.267341+09:00",
  "as_of": "2026-10-05T10:25:00-04:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
