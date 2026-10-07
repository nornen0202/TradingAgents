# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-07T08:50:57.002640+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261007T001215_github-actions-overlay-us-37485104962-1",
  "producer_finished_at": "2026-10-07T00:14:04.139049+09:00",
  "analysis_run_id": "20261006T033425_github-actions-us",
  "analysis_completed_at": "2026-10-06T05:35:33.071536+09:00",
  "analysis_trade_date_oldest": "2026-10-02",
  "analysis_trade_date_latest": "2026-10-02",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-06T11:10:00-04:00",
  "market_data_latest_at": "2026-10-06T11:10:00-04:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-07T00:14:01.543559+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-07T00:14:01.543559+09:00",
    "run_started_at": "2026-10-07T00:12:15.595928+09:00",
    "run_finished_at": "2026-10-07T00:14:04.139049+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23972933,
    "total_market_value_krw": 26005459,
    "total_unrealized_pnl_krw": 2032526,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 88750,
    "total_equity_krw": 27070861
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 553819,
      "current_price_krw": 656984,
      "market_value_krw": 7883810,
      "unrealized_pnl_krw": 1237974
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 296839,
      "current_price_krw": 288878,
      "market_value_krw": 3177660,
      "unrealized_pnl_krw": -87574
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 430547,
      "current_price_krw": 473111,
      "market_value_krw": 2838667,
      "unrealized_pnl_krw": 255381
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1908339,
      "current_price_krw": 2001464,
      "market_value_krw": 2001464,
      "unrealized_pnl_krw": 93125
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 271274,
      "current_price_krw": 329001,
      "market_value_krw": 1974009,
      "unrealized_pnl_krw": 346364
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 564317,
      "current_price_krw": 602168,
      "market_value_krw": 1806506,
      "unrealized_pnl_krw": 113554
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1495083,
      "current_price_krw": 1412418,
      "market_value_krw": 1412418,
      "unrealized_pnl_krw": -82665
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 136544,
      "current_price_krw": 136467,
      "market_value_krw": 1228203,
      "unrealized_pnl_krw": -701
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 370073,
      "current_price_krw": 452190,
      "market_value_krw": 904380,
      "unrealized_pnl_krw": 164233
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 672735,
      "current_price_krw": 785756,
      "market_value_krw": 785756,
      "unrealized_pnl_krw": 113021
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1441383,
      "current_price_krw": 1572504,
      "market_value_krw": 685714,
      "unrealized_pnl_krw": 57177
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 578211,
      "current_price_krw": 512602,
      "market_value_krw": 512602,
      "unrealized_pnl_krw": -65609
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 138265,
      "current_price_krw": 111858,
      "market_value_krw": 447432,
      "unrealized_pnl_krw": -105631
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 352992,
      "current_price_krw": 346838,
      "market_value_krw": 346838,
      "unrealized_pnl_krw": -6154
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":483.95,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":483.9621153764915,"relative_volume":0.48193087744823754,"spread_bps":2.8936979392734,"day_high":486.0,"day_low":482.26,"execution_condition_ko":"TSM의 최신 가격 487.46달러 상회, 갱신된 거래량가중평균가 지지, 상대 거래량 1.2 이상 및 정상 거래 확인 / 갱신된 거래량가중평균가, 476.40달러, 474.79달러의 순차 이탈 감시","risk_condition_ko":"474.79 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":443.33,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":441.5181744977458,"relative_volume":0.3017648462728156,"spread_bps":8.823828862970155,"day_high":445.22,"day_low":434.02,"execution_condition_ko":"최신 가격의 439.76 및 최신 거래량가중평균가격 상회와 상대거래량 1.2 이상 확인 / 439.76 위 정규장 종가와 다음 실제 거래일의 유지 또는 재돌파 확인","risk_condition_ko":"431.38 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1040.01,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":1036.5070830142129,"relative_volume":1.2020306552655236,"spread_bps":10.706173411072692,"day_high":1052.78,"day_low":995.05,"execution_condition_ko":"최신 정규장 가격의 1006달러 상향 유지, 거래량가중평균가격 상회, 상대거래량 1.2 이상 / 1006달러 위 종가와 다음 확인된 정규거래일 첫 30~60분 지지 또는 재돌파","risk_condition_ko":"965.04 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1473.45,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":1472.6742481974325,"relative_volume":0.20276120697932382,"spread_bps":9.084314642694368,"day_high":1491.64,"day_low":1459.165,"execution_condition_ko":"검증된 정규장에서 최신 가격이 1465.50 위를 유지하고 갱신된 거래량가중평균가격 위이며 상대 거래량이 1.2 이상인지 확인 / 확인된 종가가 1465.50 위인지 확인하고 다음 확인된 거래일 첫 30~60분에 지지 또는 재돌파하는지 점검","risk_condition_ko":"1,432.38 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":377.15,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":372.791799459884,"relative_volume":1.3386705697953316,"spread_bps":2.6497787434755224,"day_high":377.7499,"day_low":364.01,"execution_condition_ko":"최신 가격이 366.55 위에서 유지되고 당일 거래량가중평균가격 위에 있으며 상대거래량이 1.2 이상인지 확인 / 366.55 위의 정규장 종가와 다음 검증된 거래일의 유지·재돌파 확인; 추가 매수 전 372.67 돌파 가능성과 기대손익 재평가","risk_condition_ko":"352.17 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":255.045,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":253.61060806556517,"relative_volume":0.9357019332556673,"spread_bps":1.5681969655385597,"day_high":255.73,"day_low":251.08,"execution_condition_ko":"최신 정규장 가격이 254.53과 거래량 가중 평균가격 위에 있고 상대거래량이 1.2 이상일 때 소규모 선행 진입의 순손익비 재검토 / 256.54 위 거래량 동반 종가 확인; 단독으로는 추격 매수 금지","risk_condition_ko":"250.18 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":212.56,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":212.30206045523178,"relative_volume":0.9492957910201707,"spread_bps":0.4708430444706973,"day_high":212.685,"day_low":211.54,"execution_condition_ko":"실제 정규장에서 211.30 위 돌파·유지, 갱신된 거래량가중평균가격 상회 및 시간 보정 상대거래량 1.2 이상 / 211.30 위 종가 확인 후 다음 실제 거래일 첫 30~60분에 해당 가격 유지 또는 재돌파","risk_condition_ko":"208.92 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.455,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":100.45527356437704,"relative_volume":1.3364295714273333,"spread_bps":0.9954706087293719,"day_high":100.46,"day_low":100.45,"execution_condition_ko":"SGOV의 최신 체결 가능 호가·거래 상태·순자산가치 괴리와 스프레드 확인 / SGOV의 100.45 초과 유지, 거래량가중평균가격 상회 및 상대 거래량 1.0 이상 확인","risk_condition_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":82.315,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":82.17230445987634,"relative_volume":0.3882336282730561,"spread_bps":1.2170632264352361,"day_high":82.366,"day_low":81.9619,"execution_condition_ko":"최신 정규장 자료에서 82.16 상향 돌파, 상대거래량 1.2 이상, 당시 거래량가중평균가격 상회 / 83.93 위 거래량 동반 종가와 다음 확인된 거래일의 83.43~83.93 유지 또는 재돌파","risk_condition_ko":"81.32 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":242.07,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":242.03948588165554,"relative_volume":0.7775696728141381,"spread_bps":0.8257297386569602,"day_high":243.37,"day_low":240.76,"execution_condition_ko":"신선한 정규장 자료에서 237.88 재시험, 실시간 거래량가중평균가격 상회 및 상대거래량 1.2 이상 확인 / 237.88 위 종가와 상대거래량 1.2 이상을 확인한 뒤 다음 거래일 첫 30~60분 지지 확인","risk_condition_ko":"233.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":332.66,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":332.67212092691807,"relative_volume":0.5372719439547142,"spread_bps":0.6008171112707826,"day_high":334.38,"day_low":330.62,"execution_condition_ko":"정규장 실시간 336.19 상향 돌파, 335.30 및 실시간 거래량가중평균가격 유지, 상대 거래량 1.2 이상 확인 / 345.34~346.62 저항대의 거래량 동반 돌파 여부","risk_condition_ko":"330.61 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":579.18,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":577.6200876783582,"relative_volume":0.6926730615944153,"spread_bps":13.620337405066483,"day_high":587.19,"day_low":561.775,"execution_condition_ko":"정규장 여부와 최신 호가·실시간 거래량가중평균가·상대 거래량 확인 후 560.10 회복 관찰 / 상대 거래량 1.2 이상인 568.00 위 종가 및 다음 거래일 유지·재돌파 확인","risk_condition_ko":"546 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":348.02,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":346.5063621906656,"relative_volume":0.5513701610910585,"spread_bps":0.287476103548631,"day_high":348.49,"day_low":344.6805,"execution_condition_ko":"최신 가격 347.89 상회, 실시간 거래량가중평균가격 상회, 동시간대 상대 거래량 1.2 이상 및 거래 가능 상태 확인 / 349.91과 352.60 저항 통과, 354.70 위 종가 및 다음 거래일 유지 여부","risk_condition_ko":"338.54 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1157.485,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":1155.0119977367524,"relative_volume":0.7525601406054678,"spread_bps":5.901036152524981,"day_high":1177.065,"day_low":1139.98,"execution_condition_ko":"실제 정규장에서 1165.73 및 최신 거래량가중평균가격 위 유지와 상대 거래량 1.2 이상 / 1176.28 위의 확인된 종가와 상대 거래량 1.2 이상, 이후 다음 실제 거래일의 유지 또는 재돌파","risk_condition_ko":"1,136.66 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":97.33,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":96.85136730649162,"relative_volume":0.7218132817456077,"spread_bps":1.0272741281001496,"day_high":97.42,"day_low":96.1,"execution_condition_ko":"정규장과 거래 가능 상태, 실시간 호가의 시점 확인 / 96.96 위 가격, 실시간 거래량가중평균가격 지지, 동시간대 상대거래량 1.2 이상","risk_condition_ko":"95.52 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":164.7,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":163.91357671863423,"relative_volume":0.2650596345480456,"spread_bps":1.8233202662048276,"day_high":164.8499,"day_low":162.94,"execution_condition_ko":"최신 시세·거래 가능 상태·실제 정규장 여부 확인 / 164.74달러 상회 종가와 제안 기준 상대거래량 1.2 이상 및 다음 실제 거래일 지지 확인","risk_condition_ko":"162.33 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"URI","display_name":"United Rentals","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1095.325,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":1089.431555489526,"relative_volume":0.2518458611604609,"spread_bps":27.196681455434778,"day_high":1097.26,"day_low":1075.0,"execution_condition_ko":"갱신된 정규장 가격의 1090.605달러 상회 유지, 거래량가중평균가격 상회 및 동시간대 상대거래량 1.2 이상 확인 / 1067.7201~1066.70달러 지지 재시험과 종가 확인","risk_condition_ko":"1,066.7 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CAT","display_name":"CAT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":866.27,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":866.398050275085,"relative_volume":0.5049574913215987,"spread_bps":15.772504812933612,"day_high":876.95,"day_low":851.79,"execution_condition_ko":"확인된 정규장에서 858.87 상향 돌파, 상대 거래량 1.2 이상, 당일 거래량가중평균가격 상회 / 858.87 위 종가와 거래량 2795464주 이상, 이후 다음 거래일 지지 유지","risk_condition_ko":"836.46 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CDNS","display_name":"Cadence Design Systems","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":360.725,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":357.90881029956864,"relative_volume":0.36595263327449473,"spread_bps":4.745753248747705,"day_high":360.95,"day_low":354.285,"execution_condition_ko":"CDNS가 새로 산출한 거래량가중평균가격을 회복하고 상대 거래량 1.2 이상으로 360.145를 돌파하는지 확인 / CDNS의 352.00~351.35 지지 구간과 확인된 종가 이탈 여부 감시","risk_condition_ko":"351.35 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":265.43,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":263.96275901895507,"relative_volume":0.3771186994432123,"spread_bps":11.397743246837557,"day_high":268.6999,"day_low":260.6197,"execution_condition_ko":"새로 확인된 정규장 시세가 269.39 위에 안착하고 실시간 거래량 가중 평균가격 위에서 동시간대 상대거래량 1.2 이상 / 269.39 위의 확인된 마감 후 다음 거래일 지지 또는 재돌파; 270.93 저항 재평가","risk_condition_ko":"257.84 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SCCO","display_name":"SCCO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":202.76,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":201.31554345293569,"relative_volume":0.681335198510162,"spread_bps":11.416375052739593,"day_high":206.9,"day_low":199.22,"execution_condition_ko":"SCCO의 211.78 상향 종가와 상대거래량 1.2 이상 확인 / 적격 돌파 다음 거래일 첫 30~60분에 211.78 유지 또는 회복","risk_condition_ko":"196.78 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SNPS","display_name":"Synopsys","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":504.105,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":495.73101489295624,"relative_volume":0.9629118211926422,"spread_bps":16.226124059736218,"day_high":504.74,"day_low":486.5,"execution_condition_ko":"새 정규장 호가에서 거래량가중평균가격 회복, 500.03 돌파, 상대거래량 1.2 이상을 확인하되 이는 자동 매수 승인이 아님 / 500.03 위 종가 후 다음으로 확인된 거래일 첫 30~60분간 해당 가격 지지 여부","risk_condition_ko":"500.03 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":507.30999755859375,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":507.05941613322784,"relative_volume":0.6375258296058873,"spread_bps":null,"day_high":508.5199890136719,"day_low":503.7799987792969,"execution_condition_ko":"새 정규 거래 자료에서 499.01 재시험·회복, 거래량가중평균가격 유지, 동일 시각 대비 상대거래량 1.2 이상 확인 / 507.38 위 종가 후 다음 실제 거래일의 지지 또는 재돌파 확인; 돌파 자체는 자동 매수 아님","risk_condition_ko":"495.85 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":207.13,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":206.1347376917823,"relative_volume":0.33858811706877184,"spread_bps":1.4500809628538143,"day_high":207.18,"day_low":204.8942,"execution_condition_ko":"CVX의 실시간 207.23 돌파 후 208.60 위 유지, 실시간 거래량가중평균가격 상회 및 동시간대 상대거래량 1.2 이상 확인 / CVX의 208.60 위 종가와 다음 확인된 거래일의 지지 또는 재돌파 확인","risk_condition_ko":"201.94 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":148.69,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":148.01933509611692,"relative_volume":0.4374211048966541,"spread_bps":3.3666633000022186,"day_high":148.93,"day_low":147.06,"execution_condition_ko":"검증된 정규장에서 146.21~146.60 회복, 당일 거래량가중평균가격 상회 및 비교 가능한 상대 거래량 1.2 이상 / 149.48 위 종가와 다음 검증된 거래일 첫 30~60분의 유지","risk_condition_ko":"143.4 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":191.49,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":190.68623284130723,"relative_volume":0.23225741437775063,"spread_bps":9.936978635495814,"day_high":191.61,"day_low":189.01,"execution_condition_ko":"정규장에서 188.40~188.91 회복 여부 확인; 188.91은 과거 평균이며 당일 거래량가중평균가격이 아님 / 190.36 위 유지, 당일 거래량가중평균가격 지지, 동시간대 상대거래량 1.2 이상을 함께 확인","risk_condition_ko":"185.3 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NU","display_name":"NU","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":15.495,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":15.48516418261943,"relative_volume":0.6782018355618267,"spread_bps":6.453694740238649,"day_high":15.67,"day_low":15.33,"execution_condition_ko":"다음 확인된 정규장에서 거래 상태와 신선한 가격·당일 거래량가중평균가격·동시간대 상대거래량을 확인하고 15.46 유지 여부 관찰 / 14.86 종가 이탈 시 과거 기준선 14.70과 14.25 재점검","risk_condition_ko":"14.86 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SPYM","display_name":"SPYM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":91.9,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":91.72486004013012,"relative_volume":1.0209320804034696,"spread_bps":1.0889094571791926,"day_high":91.92,"day_low":91.56,"execution_condition_ko":"실시간 가격 91.40 초과, 해당 거래일 거래량가중평균가격 지지, 시간 보정 상대거래량 1.2 이상 동시 확인 / 확인된 종가 91.40 초과 후 다음 거래일 지지 또는 재돌파","risk_condition_ko":"90.59 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"META","display_name":"Meta Platforms","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":740.625,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":742.1236319039496,"relative_volume":0.638801603615995,"spread_bps":2.8357493467638384,"day_high":747.6,"day_low":736.69,"execution_condition_ko":"검증된 정규거래에서 746.70 위 유지, 당일 거래량가중평균가 지지, 동시간대 상대거래량 1.2 이상 확인 / 750.58 위 종가와 다음 확인된 거래일에 746.70 유지 또는 회복","risk_condition_ko":"726.2 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MRK","display_name":"MRK","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":141.5,"market_data_asof":"2026-10-06T11:10:00-04:00","session_vwap":140.66329279792714,"relative_volume":0.6491070379825997,"spread_bps":7.090187180941173,"day_high":141.9,"day_low":139.75,"execution_condition_ko":"위험 대응 조건: 141.7 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"141.7 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-06T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-06T11:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-07T01:16:39.094381+09:00",
  "as_of": "2026-10-06T11:10:00-04:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
