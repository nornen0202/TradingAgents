# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-06T01:49:41.573279+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261006T033425_github-actions-us",
  "producer_finished_at": "2026-10-06T05:47:54.689748+09:00",
  "analysis_run_id": "20261006T033425_github-actions-us",
  "analysis_completed_at": "2026-10-06T05:35:33.071536+09:00",
  "analysis_trade_date_oldest": "2026-10-02",
  "analysis_trade_date_latest": "2026-10-02",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-05T14:35:00-04:00",
  "market_data_latest_at": "2026-10-05T16:15:00-04:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-06T05:35:56.287068+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-06T05:35:56.287068+09:00",
    "run_started_at": "2026-10-06T03:34:25.772273+09:00",
    "run_finished_at": "2026-10-06T05:47:54.689748+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23992351,
    "total_market_value_krw": 25824147,
    "total_unrealized_pnl_krw": 1831796,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 88822,
    "total_equity_krw": 26889621
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 554268,
      "current_price_krw": 660493,
      "market_value_krw": 7925924,
      "unrealized_pnl_krw": 1274707
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 297079,
      "current_price_krw": 287038,
      "market_value_krw": 3157426,
      "unrealized_pnl_krw": -110452
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 430896,
      "current_price_krw": 471060,
      "market_value_krw": 2826363,
      "unrealized_pnl_krw": 240985
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1909884,
      "current_price_krw": 2012058,
      "market_value_krw": 2012058,
      "unrealized_pnl_krw": 102174
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 271493,
      "current_price_krw": 324808,
      "market_value_krw": 1948850,
      "unrealized_pnl_krw": 319887
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 564774,
      "current_price_krw": 588162,
      "market_value_krw": 1764488,
      "unrealized_pnl_krw": 70165
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1496294,
      "current_price_krw": 1346004,
      "market_value_krw": 1346004,
      "unrealized_pnl_krw": -150290
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 136655,
      "current_price_krw": 136571,
      "market_value_krw": 1229146,
      "unrealized_pnl_krw": -753
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 370373,
      "current_price_krw": 452597,
      "market_value_krw": 905194,
      "unrealized_pnl_krw": 164448
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 673280,
      "current_price_krw": 750893,
      "market_value_krw": 750893,
      "unrealized_pnl_krw": 77613
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1442550,
      "current_price_krw": 1554185,
      "market_value_krw": 677726,
      "unrealized_pnl_krw": 48680
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 578679,
      "current_price_krw": 492868,
      "market_value_krw": 492868,
      "unrealized_pnl_krw": -85811
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 138377,
      "current_price_krw": 111351,
      "market_value_krw": 445404,
      "unrealized_pnl_krw": -108107
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 353278,
      "current_price_krw": 341803,
      "market_value_krw": 341803,
      "unrealized_pnl_krw": -11475
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":486.49,"market_data_asof":"2026-10-05T15:10:00-04:00","session_vwap":482.8448514070759,"relative_volume":0.5157415695058023,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"TSM의 최신 가격 487.46달러 상회, 갱신된 거래량가중평균가 지지, 상대 거래량 1.2 이상 및 정상 거래 확인 / 갱신된 거래량가중평균가, 476.40달러, 474.79달러의 순차 이탈 감시","risk_condition_ko":"474.79 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T15:40:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":81.89,"market_data_asof":"2026-10-05T14:45:00-04:00","session_vwap":81.80570771472078,"relative_volume":0.3701357812392584,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 정규장 자료에서 82.16 상향 돌파, 상대거래량 1.2 이상, 당시 거래량가중평균가격 상회 / 83.93 위 거래량 동반 종가와 다음 확인된 거래일의 83.43~83.93 유지 또는 재돌파","risk_condition_ko":"81.32 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T14:45:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T15:15:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1456.03,"market_data_asof":"2026-10-05T14:55:00-04:00","session_vwap":1448.3643129724605,"relative_volume":0.32970029300751325,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"검증된 정규장에서 최신 가격이 1465.50 위를 유지하고 갱신된 거래량가중평균가격 위이며 상대 거래량이 1.2 이상인지 확인 / 확인된 종가가 1465.50 위인지 확인하고 다음 확인된 거래일 첫 30~60분에 지지 또는 재돌파하는지 점검","risk_condition_ko":"1,432.38 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T14:55:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T15:25:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":436.81,"market_data_asof":"2026-10-05T14:45:00-04:00","session_vwap":437.11134347446256,"relative_volume":0.32259748780105457,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 가격의 439.76 및 최신 거래량가중평균가격 상회와 상대거래량 1.2 이상 확인 / 439.76 위 정규장 종가와 다음 실제 거래일의 유지 또는 재돌파 확인","risk_condition_ko":"431.38 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T14:45:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T15:15:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":990.8462,"market_data_asof":"2026-10-05T14:45:00-04:00","session_vwap":988.2010427914404,"relative_volume":0.43901083300796334,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 정규장 가격의 1006달러 상향 유지, 거래량가중평균가격 상회, 상대거래량 1.2 이상 / 1006달러 위 종가와 다음 확인된 정규거래일 첫 30~60분 지지 또는 재돌파","risk_condition_ko":"965.04 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T14:45:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T15:15:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":211.235,"market_data_asof":"2026-10-05T15:10:00-04:00","session_vwap":210.39370027478446,"relative_volume":0.3693984485651822,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"실제 정규장에서 211.30 위 돌파·유지, 갱신된 거래량가중평균가격 상회 및 시간 보정 상대거래량 1.2 이상 / 211.30 위 종가 확인 후 다음 실제 거래일 첫 30~60분에 해당 가격 유지 또는 재돌파","risk_condition_ko":"208.92 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T15:40:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":362.79,"market_data_asof":"2026-10-05T14:35:00-04:00","session_vwap":360.7341758555728,"relative_volume":0.4053618036240792,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 가격이 366.55 위에서 유지되고 당일 거래량가중평균가격 위에 있으며 상대거래량이 1.2 이상인지 확인 / 366.55 위의 정규장 종가와 다음 검증된 거래일의 유지·재돌파 확인; 추가 매수 전 372.67 돌파 가능성과 기대손익 재평가","risk_condition_ko":"352.17 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T14:35:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T15:05:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":253.52,"market_data_asof":"2026-10-05T14:35:00-04:00","session_vwap":252.73715400220522,"relative_volume":0.5344216023612811,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 정규장 가격이 254.53과 거래량 가중 평균가격 위에 있고 상대거래량이 1.2 이상일 때 소규모 선행 진입의 순손익비 재검토 / 256.54 위 거래량 동반 종가 확인; 단독으로는 추격 매수 금지","risk_condition_ko":"250.18 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T14:35:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T15:05:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.45,"market_data_asof":"2026-10-05T15:10:00-04:00","session_vwap":100.44538944522542,"relative_volume":0.7821144446997581,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"SGOV의 최신 체결 가능 호가·거래 상태·순자산가치 괴리와 스프레드 확인 / SGOV의 100.45 초과 유지, 거래량가중평균가격 상회 및 상대 거래량 1.0 이상 확인","risk_condition_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T15:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T15:40:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":239.4,"market_data_asof":"2026-10-05T15:00:00-04:00","session_vwap":237.22850196844496,"relative_volume":0.5663992950253591,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"신선한 정규장 자료에서 237.88 재시험, 실시간 거래량가중평균가격 상회 및 상대거래량 1.2 이상 확인 / 237.88 위 종가와 상대거래량 1.2 이상을 확인한 뒤 다음 거래일 첫 30~60분 지지 확인","risk_condition_ko":"233.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T15:00:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T15:30:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":332.94,"market_data_asof":"2026-10-05T14:35:00-04:00","session_vwap":333.8238020259128,"relative_volume":0.33465677580740477,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"정규장 실시간 336.19 상향 돌파, 335.30 및 실시간 거래량가중평균가격 유지, 상대 거래량 1.2 이상 확인 / 345.34~346.62 저항대의 거래량 동반 돌파 여부","risk_condition_ko":"330.61 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T14:35:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T15:05:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":551.75,"market_data_asof":"2026-10-05T14:35:00-04:00","session_vwap":553.8924086433665,"relative_volume":0.2331023882067573,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"정규장 여부와 최신 호가·실시간 거래량가중평균가·상대 거래량 확인 후 560.10 회복 관찰 / 상대 거래량 1.2 이상인 568.00 위 종가 및 다음 거래일 유지·재돌파 확인","risk_condition_ko":"546 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T14:35:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T15:05:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":347.7,"market_data_asof":"2026-10-05T14:55:00-04:00","session_vwap":345.21465888290487,"relative_volume":0.3628335416216253,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 가격 347.89 상회, 실시간 거래량가중평균가격 상회, 동시간대 상대 거래량 1.2 이상 및 거래 가능 상태 확인 / 349.91과 352.60 저항 통과, 354.70 위 종가 및 다음 거래일 유지 여부","risk_condition_ko":"338.54 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T14:55:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T15:25:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1149.435,"market_data_asof":"2026-10-05T14:55:00-04:00","session_vwap":1151.9303245692342,"relative_volume":0.3113996203036014,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"실제 정규장에서 1165.73 및 최신 거래량가중평균가격 위 유지와 상대 거래량 1.2 이상 / 1176.28 위의 확인된 종가와 상대 거래량 1.2 이상, 이후 다음 실제 거래일의 유지 또는 재돌파","risk_condition_ko":"1,136.66 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T14:55:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T15:25:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":96.485,"market_data_asof":"2026-10-05T15:50:00-04:00","session_vwap":96.21008630998355,"relative_volume":0.4947424386409708,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"정규장과 거래 가능 상태, 실시간 호가의 시점 확인 / 96.96 위 가격, 실시간 거래량가중평균가격 지지, 동시간대 상대거래량 1.2 이상","risk_condition_ko":"95.52 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T15:50:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T16:20:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":163.83,"market_data_asof":"2026-10-05T15:45:00-04:00","session_vwap":163.62668618374207,"relative_volume":0.2689376737229835,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 시세·거래 가능 상태·실제 정규장 여부 확인 / 164.74달러 상회 종가와 제안 기준 상대거래량 1.2 이상 및 다음 실제 거래일 지지 확인","risk_condition_ko":"162.33 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T15:45:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T16:15:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"URI","display_name":"United Rentals","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1081.2425,"market_data_asof":"2026-10-05T15:30:00-04:00","session_vwap":1081.8175564184446,"relative_volume":0.26454735660821166,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"갱신된 정규장 가격의 1090.605달러 상회 유지, 거래량가중평균가격 상회 및 동시간대 상대거래량 1.2 이상 확인 / 1067.7201~1066.70달러 지지 재시험과 종가 확인","risk_condition_ko":"1,066.7 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T15:30:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T16:00:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CAT","display_name":"CAT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":848.14,"market_data_asof":"2026-10-05T16:00:00-04:00","session_vwap":846.3027274542388,"relative_volume":0.5525399142429941,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"확인된 정규장에서 858.87 상향 돌파, 상대 거래량 1.2 이상, 당일 거래량가중평균가격 상회 / 858.87 위 종가와 거래량 2795464주 이상, 이후 다음 거래일 지지 유지","risk_condition_ko":"836.46 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T16:00:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T16:30:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CDNS","display_name":"Cadence Design Systems","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":354.21,"market_data_asof":"2026-10-05T15:25:00-04:00","session_vwap":355.86597453008915,"relative_volume":0.3208466499440952,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"CDNS가 새로 산출한 거래량가중평균가격을 회복하고 상대 거래량 1.2 이상으로 360.145를 돌파하는지 확인 / CDNS의 352.00~351.35 지지 구간과 확인된 종가 이탈 여부 감시","risk_condition_ko":"351.35 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T15:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T15:55:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SNPS","display_name":"Synopsys","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":485.93,"market_data_asof":"2026-10-05T15:20:00-04:00","session_vwap":493.6626726525383,"relative_volume":0.4536651198391698,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"새 정규장 호가에서 거래량가중평균가격 회복, 500.03 돌파, 상대거래량 1.2 이상을 확인하되 이는 자동 매수 승인이 아님 / 500.03 위 종가 후 다음으로 확인된 거래일 첫 30~60분간 해당 가격 지지 여부","risk_condition_ko":"500.03 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T15:20:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T15:50:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":266.61,"market_data_asof":"2026-10-05T15:30:00-04:00","session_vwap":263.50822080594594,"relative_volume":0.5474752586156971,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"새로 확인된 정규장 시세가 269.39 위에 안착하고 실시간 거래량 가중 평균가격 위에서 동시간대 상대거래량 1.2 이상 / 269.39 위의 확인된 마감 후 다음 거래일 지지 또는 재돌파; 270.93 저항 재평가","risk_condition_ko":"257.84 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T15:30:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T16:00:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SCCO","display_name":"SCCO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":206.26,"market_data_asof":"2026-10-05T15:55:00-04:00","session_vwap":206.3491779969061,"relative_volume":0.35368882536254315,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"SCCO의 211.78 상향 종가와 상대거래량 1.2 이상 확인 / 적격 돌파 다음 거래일 첫 30~60분에 211.78 유지 또는 회복","risk_condition_ko":"196.78 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T15:55:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T16:25:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":206.15,"market_data_asof":"2026-10-05T15:45:00-04:00","session_vwap":205.55854828248727,"relative_volume":0.2771541967433548,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"CVX의 실시간 207.23 돌파 후 208.60 위 유지, 실시간 거래량가중평균가격 상회 및 동시간대 상대거래량 1.2 이상 확인 / CVX의 208.60 위 종가와 다음 확인된 거래일의 지지 또는 재돌파 확인","risk_condition_ko":"201.94 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T15:45:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T16:15:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":146.358,"market_data_asof":"2026-10-05T16:10:00-04:00","session_vwap":145.6251882395993,"relative_volume":0.3356283381360752,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"검증된 정규장에서 146.21~146.60 회복, 당일 거래량가중평균가격 상회 및 비교 가능한 상대 거래량 1.2 이상 / 149.48 위 종가와 다음 검증된 거래일 첫 30~60분의 유지","risk_condition_ko":"143.4 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T16:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T16:40:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":504.5299987792969,"market_data_asof":"2026-10-05T15:55:00-04:00","session_vwap":504.43678513439386,"relative_volume":0.535180264107594,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"새 정규 거래 자료에서 499.01 재시험·회복, 거래량가중평균가격 유지, 동일 시각 대비 상대거래량 1.2 이상 확인 / 507.38 위 종가 후 다음 실제 거래일의 지지 또는 재돌파 확인; 돌파 자체는 자동 매수 아님","risk_condition_ko":"495.85 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T15:55:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T16:25:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":189.53,"market_data_asof":"2026-10-05T16:10:00-04:00","session_vwap":189.02420712350371,"relative_volume":0.5311500260127361,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"정규장에서 188.40~188.91 회복 여부 확인; 188.91은 과거 평균이며 당일 거래량가중평균가격이 아님 / 190.36 위 유지, 당일 거래량가중평균가격 지지, 동시간대 상대거래량 1.2 이상을 함께 확인","risk_condition_ko":"185.3 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T16:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T16:40:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MRK","display_name":"MRK","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":139.6,"market_data_asof":"2026-10-05T16:15:00-04:00","session_vwap":140.38885845477728,"relative_volume":0.5148095452859167,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"MRK의 2026-10-05 공식 종가와 다음 실제 정규장 확인 / 141.92 회복, 당일 거래량가중평균가격 상회, 상대거래량 1.2 이상","risk_condition_ko":"141.7 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T16:15:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T16:45:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NU","display_name":"NU","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":15.22,"market_data_asof":"2026-10-05T16:05:00-04:00","session_vwap":15.248776797619582,"relative_volume":1.42182263937652,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"다음 확인된 정규장에서 거래 상태와 신선한 가격·당일 거래량가중평균가격·동시간대 상대거래량을 확인하고 15.46 유지 여부 관찰 / 14.86 종가 이탈 시 과거 기준선 14.70과 14.25 재점검","risk_condition_ko":"14.86 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T16:05:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T16:35:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SPYM","display_name":"SPYM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":91.325,"market_data_asof":"2026-10-05T15:35:00-04:00","session_vwap":91.06897950052011,"relative_volume":0.3583608475559505,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"실시간 가격 91.40 초과, 해당 거래일 거래량가중평균가격 지지, 시간 보정 상대거래량 1.2 이상 동시 확인 / 확인된 종가 91.40 초과 후 다음 거래일 지지 또는 재돌파","risk_condition_ko":"90.59 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T15:35:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T16:05:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"META","display_name":"Meta Platforms","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":741.605,"market_data_asof":"2026-10-05T15:55:00-04:00","session_vwap":740.7197857670702,"relative_volume":0.32413252266749626,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"검증된 정규거래에서 746.70 위 유지, 당일 거래량가중평균가 지지, 동시간대 상대거래량 1.2 이상 확인 / 750.58 위 종가와 다음 확인된 거래일에 746.70 유지 또는 회복","risk_condition_ko":"726.2 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-05T15:55:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-05T16:25:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
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
