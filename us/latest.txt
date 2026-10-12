# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-12T13:51:03.250031+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261012T175405_local-scheduler-us-full",
  "producer_finished_at": "2026-10-12T22:47:19.826152+09:00",
  "analysis_run_id": "20261012T175405_local-scheduler-us-full",
  "analysis_completed_at": "2026-10-12T22:09:19.480861+09:00",
  "analysis_trade_date_oldest": "2026-10-09",
  "analysis_trade_date_latest": "2026-10-09",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-09T15:55:00-04:00",
  "market_data_latest_at": "2026-10-12T08:30:00-04:00",
  "market_data_status": "MISSING"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-12T22:09:48.363986+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-12T22:09:48.363986+09:00",
    "run_started_at": "2026-10-12T17:54:05.611414+09:00",
    "run_finished_at": "2026-10-12T22:47:19.826152+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23611188,
    "total_market_value_krw": 24842649,
    "total_unrealized_pnl_krw": 1231461,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 104939,
    "total_equity_krw": 25924211
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 545462,
      "current_price_krw": 608736,
      "market_value_krw": 7304837,
      "unrealized_pnl_krw": 759288
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 292360,
      "current_price_krw": 285101,
      "market_value_krw": 3136111,
      "unrealized_pnl_krw": -79850
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 424050,
      "current_price_krw": 469932,
      "market_value_krw": 2819594,
      "unrealized_pnl_krw": 275290
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1879542,
      "current_price_krw": 1834398,
      "market_value_krw": 1834398,
      "unrealized_pnl_krw": -45144
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 267180,
      "current_price_krw": 305557,
      "market_value_krw": 1833347,
      "unrealized_pnl_krw": 230263
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 555801,
      "current_price_krw": 572824,
      "market_value_krw": 1718473,
      "unrealized_pnl_krw": 51068
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1472522,
      "current_price_krw": 1334159,
      "market_value_krw": 1334159,
      "unrealized_pnl_krw": -138363
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 134484,
      "current_price_krw": 134509,
      "market_value_krw": 1210582,
      "unrealized_pnl_krw": 223
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 364489,
      "current_price_krw": 451982,
      "market_value_krw": 903965,
      "unrealized_pnl_krw": 174987
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 662584,
      "current_price_krw": 782435,
      "market_value_krw": 782435,
      "unrealized_pnl_krw": 119851
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1419632,
      "current_price_krw": 1586868,
      "market_value_krw": 691977,
      "unrealized_pnl_krw": 72925
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 569486,
      "current_price_krw": 480462,
      "market_value_krw": 480462,
      "unrealized_pnl_krw": -89024
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 136179,
      "current_price_krw": 110344,
      "market_value_krw": 441377,
      "unrealized_pnl_krw": -103340
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 347665,
      "current_price_krw": 350932,
      "market_value_krw": 350932,
      "unrealized_pnl_krw": 3267
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":82.54,"market_data_asof":"2026-10-12T05:35:00-04:00","session_vwap":82.74351987703486,"relative_volume":0.06636131006015257,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"거래일과 정규장 상태, 신선한 체결 가능 호가, 호가 차이·잔량을 확인한다. 신규 진입에는 동시점 순자산가치 등 상품 점검도 요구한다. / 82.59~82.82 유지 여부를 감시한다. 기준일 종가는 이미 위에 있었으므로 회복 신호를 새롭게 발생한 사실로 중복 계산하지 않는다.","risk_condition_ko":"81.96 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T05:35:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T06:05:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":359.92,"market_data_asof":"2026-10-12T04:50:00-04:00","session_vwap":361.866101280274,"relative_volume":0.030612515656541866,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"거래소 일정·거래정지 상태와 최신 정규장 호가·5분봉·거래량 가중평균가격·동일 시간대 상대거래량을 확보한다. 현재 실행 조건 충족은 미확인이다. / 357.41~358.81 방어, 저점 상승과 361.28 회복·재시험을 관찰한다. 단순 지지 접촉이나 회복만으로 매수하지 않는다.","risk_condition_ko":"367.11 이하 하락, 2개 봉 확인 후 (위험축소에는 거래량 증가를 요구하지 않음) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T04:50:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T05:20:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":999.15,"market_data_asof":"2026-10-12T05:25:00-04:00","session_vwap":1004.2376613515565,"relative_volume":0.011592346893221668,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"988.39 또는 973~978 시험 후 저점 갱신 중단, 지지선 및 당일 정규장 거래량가중평균가격 회복을 관찰한다. / 1015는 초기 회복, 1029.21은 중간 저항, 1052.78은 핵심 돌파선으로 구분한다. 상단 1065~1079와 1099.66도 손익비에 반영한다.","risk_condition_ko":"968.71 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T05:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T05:55:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":428.06,"market_data_asof":"2026-10-12T05:00:00-04:00","session_vwap":428.63598326359835,"relative_volume":0.0022571762663554993,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"420~421.42 재시험 후 연속 두 완결 5분봉의 지지·저점 상승, 최신 정규장 거래량가중평균가격 회복과 동시간대 상대거래량 1.2 이상 확인. / 새 지지 시험 후 427.26 위 종가와 다음 실제 거래일 426.33~427.26 재지지 확인. 마지막 종가가 이미 이 구간 위였으므로 단순 상회를 새 신호로 취급하지 않음.","risk_condition_ko":"420 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T05:00:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T05:30:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1372.4933,"market_data_asof":"2026-10-12T05:30:00-04:00","session_vwap":1379.808,"relative_volume":0.003447053855988075,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1349.39~1353.99 시험 이후 1353.99 회복, 연속 두 개 5분봉의 저점 안정, 정규장 거래량가중평균가격 상회 및 상대거래량 1.2 이상을 관찰한다. 1355는 후보 진입 상한이지 주문이 아니다. / 1401.76 상회 종가와 거래량을 확인한 뒤 새 지지·손절 및 현실적인 비용 후 보상/위험을 재산정한다. 돌파 자체만으로 확대하지 않는다.","risk_condition_ko":"1,349.39 이하 하락, 다음 거래일 확인 후 (위험 축소에 거래량 확인을 요구하지 않음) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T05:30:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T06:00:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":454.98,"market_data_asof":"2026-10-12T06:30:00-04:00","session_vwap":456.85875655765153,"relative_volume":0.08929868116160188,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"449.01~452.88에서 하락이 멈추고 452.88 위 정규장 5분봉 두 개가 유지되는지 확인한다. 회복만으로는 현재 보상·위험 기준을 통과하지 못한다. / 464.83 돌파·재시험 유지, 정규장 거래량가중평균가격 상회 및 검증된 동일시각 상대거래량 1.2 이상을 함께 확인한다. 충족 여부는 미확인이다.","risk_condition_ko":"449.01 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T06:30:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T07:00:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.5226,"market_data_asof":"2026-10-12T06:15:00-04:00","session_vwap":100.52131282222248,"relative_volume":0.15146778634948757,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단시각은 2026-10-12T06:38:00.702439-04:00이며 일별 가격 기준일은 2026-10-09이다. 2026-10-12 06:15-04:00의 지연 관측은 현재 호가나 진입 조건 충족을 입증하지 않는다. / 정규장 운영·휴장·단축 일정, 정상 거래 상태, 호가와 순자산가치 자료의 신선도를 각각 확인한다. 10:30은 정상 정규장이 확인된 날의 최초 재검토 시각이지 만기나 자동 주문 승인 시각이 아니다. 확인된 주문 만기가 없으므로 다음 날로 이월하지 않는다.","risk_condition_ko":"100.51 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T06:15:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T06:45:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1181.7988,"market_data_asof":"2026-10-12T05:30:00-04:00","session_vwap":1179.98738170347,"relative_volume":0.0027835683151667184,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1131~1152에서 하락 정지, 저점 상승과 지지 회복을 관찰한다. 구간 접촉만으로 매수하지 않으며 구간 상단에서는 가격 조건이 불충분할 수 있다. / 1197.01과 1206.63 회복을 1215 돌파와 구분한다. 돌파 이후에도 1238~1255 저항까지 실제 체결가·손절·부분청산을 반영하여 진입 타당성을 재검토한다.","risk_condition_ko":"1,131.21 이하 하락, 2개 봉 확인 후 (위험 축소에는 거래량 조건을 요구하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T05:30:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T06:00:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":263.3488,"market_data_asof":"2026-10-12T04:50:00-04:00","session_vwap":263.9079567036734,"relative_volume":0.034947365771305125,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"259.10–260.14 재시험에서 완료된 5분봉 2개가 지지를 유지하고 당일 거래량가중평균가격을 회복하며 동일 경과시간 기준 누적 상대거래량이 1.2 이상인지 확인한다. 그 뒤에도 실제 진입가 기준 비용 차감 후 손익비 2.0 이상을 별도로 충족해야 한다. / 262.80 돌파·재시험과 종가 및 다음 거래일의 지속성을 관찰한다. 같은 253.50 손절과 272.75 목표라면 262.80 진입의 비용 미반영 손익비는 약 1.07이므로 돌파만으로 추가 매수하지 않는다.","risk_condition_ko":"259.1 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T04:50:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T05:20:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":212.97,"market_data_asof":"2026-10-12T05:25:00-04:00","session_vwap":213.169921875,"relative_volume":0.001328333320149036,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"210.61~211.35 지지 회복과 두 개의 정규장 5분봉 저점 상승을 확인한다. 최신 세션 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상, 실제 비용 후 손익비와 계좌 한도가 함께 충족되어야 소액 초기 진입을 재심사할 수 있다. 현재는 주문이 아닌 감시 조건이다. / 213.29 돌파·재시험을 관찰하되 가까운 214.05~214.97 저항 때문에 단독 추격 신호로 사용하지 않는다. 본격 추가는 214.97과 갱신된 50일 평균 회복 후 별도 손절·목표를 검증한다.","risk_condition_ko":"210.61 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T05:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T05:55:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":229.7082,"market_data_asof":"2026-10-12T06:10:00-04:00","session_vwap":229.69558422891143,"relative_volume":0.043969007309265756,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 정규장에서 228.04~229.11 재시험 후 229.11 회복, 연속 두 개의 5분봉 상회, 저점 상승과 재시험 지지를 확인한다. 현재는 감시 기준이지 주문이 아니다. / 231.69 돌파·재시험, 정규장 거래량가중평균가격 상회와 동일 시간대 상대거래량 1.2 이상을 확인한다. 1.2는 제안 기준이며 관측값이 아니다. 이후에도 실제 진입가와 구조적 손절로 보상·위험을 다시 계산한다.","risk_condition_ko":"228.04 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T06:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T06:40:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":579.01,"market_data_asof":"2026-10-12T05:00:00-04:00","session_vwap":582.4580204013004,"relative_volume":0.023843881791028736,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"560.38–566.20 구간에서 저점 상승, 정규장 거래량가중평균가격 회복과 재시험 성공을 관찰한다. / 595.51 돌파·재시험 시 동시간대 상대거래량 1.2 이상, 안정된 호가와 비용 차감 후 손익비 2 이상을 확인한다.","risk_condition_ko":"560.38 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T05:00:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T05:30:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":352.59,"market_data_asof":"2026-10-12T05:40:00-04:00","session_vwap":352.99735436275756,"relative_volume":0.029895688857450708,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"GOOGL 345.55~346.96 재시험 후 346.96 위 5분봉 2개 유지, 정규장 거래량가중평균가격 상회, 검증된 동시간대 상대거래량 1.2 이상을 관찰한다. 이는 관심목록 유지 조건이지 자동 매수 조건이 아니다. / GOOGL 356.83 돌파·재시험을 관찰하되 364.17까지 여력 7.34가 제공 평균진폭 8.39보다 작아 추격하지 않는다. 364.17 돌파 후에도 새로운 상단 목표 근거가 필요하다.","risk_condition_ko":"345.55 이하 하락, 다음 거래일 확인 후 (기존 보호손절과 계좌 손실한도는 거래량 확인보다 우선) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T05:40:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T06:10:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"현재 명시된 위험 행동 없음","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":385.5,"market_data_asof":"2026-10-12T07:55:00-04:00","session_vwap":385.7805991440799,"relative_volume":0.011116032821377343,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 판단시각은 2026-10-12T08:23:36.286344-04:00다. 미국 동부시간 10:30은 최초 시험 진입 검토시각이며 만료시각이 아니다. 현재 시계만으로 거래소 운영·정규장 일정·호가 신선도·주문 유효성을 확정하지 않으며, 만료를 선언하거나 다음 세션으로 이월하지 않는다. / 검증된 정규장에서 386.84 위 두 개의 완료된 5분봉, 385.57~386.84 재시험 후 386.84 재회복, 최신 거래량가중평균가 상회 및 동일 경과시간 상대거래량 1.2 이상을 함께 확인한다.","risk_condition_ko":"381.54 이하 하락, 종가 확인 후 (위험 축소에 거래량 급증을 요구하지 않음) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T07:55:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T08:25:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMT","display_name":"AMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":182.33,"market_data_asof":"2026-10-12T08:30:00-04:00","session_vwap":182.71477272727273,"relative_volume":0.005534450781566608,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"실제 정규장 운영·거래정지·호가 시각·정상 스프레드와 계좌 보유량·현금·집중도를 먼저 확인한다. / 177.88~179.04에서 눌림 거래량 감소 후 반등 거래량 증가, 연속 5분봉 두 개의 지지와 정규장 거래량가중평균가격 회복을 확인한다.","risk_condition_ko":"175.02 이하 하락, 거래량 조건 확인 후 (하향 이탈 시 거래량 증가와 연속 정규장 5분봉 두 개의 회복 실패) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T08:30:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T09:00:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SPYM","display_name":"SPYM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":91.64,"market_data_asof":"2026-10-12T07:30:00-04:00","session_vwap":91.76280611699283,"relative_volume":0.028506917922695354,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"거래소 달력·실제 정규장·거래정지 여부와 최신 호가·분봉을 확인한다. 일봉 기준일 2026-10-09와 판단일 2026-10-12를 구분한다. / 제공된 07:30 지연 개장 전 자료는 진입 확인에 사용할 수 없다. 개장 전 상대거래량 0.0285와 거래량가중평균가격 91.7628을 정규장 필터로 대체하지 않는다.","risk_condition_ko":"90.67 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T07:30:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T08:00:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":213.1,"market_data_asof":"2026-10-12T07:05:00-04:00","session_vwap":212.95767027371102,"relative_volume":0.013202297556443256,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"205.50–206.30에서 완료된 5분 봉 두 개의 지지·재탈환, 정규장 거래량가중평균가격 회복, 동시간대 상대거래량 1.2 이상을 관찰한다. 미해결 매도 조건이 있으면 매수를 차단한다. / 213.72, 갱신된 215.54, 217.78의 저항 반응을 순서대로 확인한다. 217.78 돌파만으로 매수하지 않고 별도의 상단 목표와 손절선을 요구한다.","risk_condition_ko":"206.26 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T07:05:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T07:35:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":277.52,"market_data_asof":"2026-10-12T07:15:00-04:00","session_vwap":277.47907647907647,"relative_volume":0.0061187480891846694,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"270.38–272.42에서 매도 거래량 감소와 안정화 후 구간 회복을 확인한다. 단순 가격 접촉은 매수 신호가 아니다. / 277.60 위에서 정규장 5분봉 종가 2개, 성공적인 재시험, 거래량가중평균가격 지지와 동시간대 상대거래량 1.2배 이상을 확인한다.","risk_condition_ko":"269.39 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T07:15:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T07:45:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":151.2969,"market_data_asof":"2026-10-12T07:40:00-04:00","session_vwap":151.1095890410959,"relative_volume":0.0021695299657593895,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"149.50–150.00에서 지지 형성 여부를 관찰한다. 단순 도달은 매수 신호가 아니다. / 147.50–148.10에서 안정된 뒤 148.10을 회복하는지 관찰한다. 완성된 5분 봉 2개, 정규장 거래량가중평균가격 유지와 동일 경과시간 상대거래량 1.2 이상이 필요하지만 이것만으로 주문을 승인하지 않는다.","risk_condition_ko":"145.9 이하 하락, 종가 확인 후 (위험축소 판단에는 최소 거래량 조건을 두지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T07:40:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T08:10:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":101.48,"market_data_asof":"2026-10-12T08:15:00-04:00","session_vwap":100.48545208931378,"relative_volume":0.46548957776284944,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"거래소 일정·정규장 운영·거래정지 여부·최신 매수매도 호가와 정규장 5분봉을 확인한다. 제공된 시계만으로 정상 세션을 가정하지 않는다. / 101.17 돌파 후 재시험 지지와 5분봉 두 개의 상단 마감, 현재 정규장 거래량가중평균가격 상회, 검증된 동시간대 상대거래량 1.2 이상을 함께 관찰한다.","risk_condition_ko":"99.15 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T08:15:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T08:45:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ANET","display_name":"Arista Networks","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":216.4,"market_data_asof":"2026-10-12T06:35:00-04:00","session_vwap":217.4655858060569,"relative_volume":0.013025152318690988,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"기준 판단시각은 2026-10-12T07:04:07.923990-04:00이며 제안된 최초 재평가 시각 2026-10-12T10:30:00-04:00보다 이르다. 10:30은 만료시각이 아니다. 거래일·휴장·조기폐장·거래정지·실제 정규장 상태는 별도 확인하고 만료시각이나 다음 세션 이월을 만들지 않는다. / 217.41 위 연속 5분봉 두 개와 재시험 지지, 정규장 거래량가중평균가격 상회, 동일 시간대 상대 거래량 1.2 이상, 신선한 호가를 확인한다. 목표·보호 손절·순보상·위험비까지 충족해야 소규모 시험 진입을 재평가한다.","risk_condition_ko":"207.2 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T06:35:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T07:05:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"KO","display_name":"KO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":88.2188,"market_data_asof":"2026-10-12T06:40:00-04:00","session_vwap":88.19617083946981,"relative_volume":0.008426508583877959,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"87.00~87.66 조정 후 완성된 정규장 5분 봉의 지지 회복, 매도압력 완화, 해당 세션 거래량가중평균가격 상회와 동일 시간대 상대거래량 1.2 이상을 확인한다. 가격 도달만으로 매수하지 않는다. / 88.48 돌파는 관찰 신호에 그친다. 89.36~89.43과 89.82 저항을 순차 확인하고 가장 가까운 유효 저항까지 순보상위험비를 재계산한다.","risk_condition_ko":"87 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T06:40:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T07:10:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":169.9535,"market_data_asof":"2026-10-12T07:05:00-04:00","session_vwap":169.4659773984131,"relative_volume":0.012551363106006972,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"164.00~165.11에서 매도 거래량 감소·정규장 반등·거래량가중평균가격 회복을 관찰한다. 165.20은 재검토용 예시이며 현재 승인된 진입가가 아니다. / 170.29 위 정규장 5분봉 마감·재시험 유지·동일 시간대 상대거래량 1.2 이상을 관찰한다. 가격 돌파만으로 손익비 미달을 무시하지 않는다.","risk_condition_ko":"166.71 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T07:05:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T07:35:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NU","display_name":"NU","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":16.11,"market_data_asof":"2026-10-12T07:35:00-04:00","session_vwap":16.147109898288267,"relative_volume":0.0028304174991878486,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"실제 정규장 운영·휴장 또는 단축 여부·거래정지 상태·최신 호가·주문 가능성을 확인한다. / 15.50~15.70에서 높아지는 정규장 5분봉 저점, 당일 거래량가중평균가격 회복, 동시간대 상대거래량 1.2 이상을 확인한다. 구간 전체가 적격 매수가격은 아니다.","risk_condition_ko":"16.2 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T07:35:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T08:05:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOG","display_name":"GOOG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":348.49,"market_data_asof":"2026-10-12T07:00:00-04:00","session_vwap":349.086886682243,"relative_volume":0.03993533748950832,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-10-12T07:27:22.851671-04:00은 제안된 최초 검토 시각 10:30 이전이다. 10:30은 활성화 제한이지 만료시각이 아니다. 실제 거래일·정규장 운영·거래정지·최신 호가는 별도 미확인이고, 만료된 계획이나 다음 거래일로 이월할 주문도 없다. / 342.18~343.28 조정 이후 343.28 위 두 개 연속 5분봉 마감, 재시험 저점 유지, 정규장 거래량가중평균가격 회복과 동시간대 상대거래량 1.2 이상을 관찰한다. 비용 후 보상/위험 미달이면 계속 대기한다.","risk_condition_ko":"342.18 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T07:00:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T07:30:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CEG","display_name":"CEG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":301.5,"market_data_asof":"2026-10-12T08:10:00-04:00","session_vwap":301.30123250470024,"relative_volume":0.06892883883301945,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"285.45~286.83 회복 후 정규장 지지 유지와 거래량가중평균가격 회복을 관찰한다. 279.55~280.52는 하단 반응 관찰용이며 미해소 위험축소 상태에서 매수 신호로 사용하지 않는다. / 300.98 돌파 재시험의 정규장 5분봉 두 개 상회 마감과 동일 경과시간 상대거래량 1.2 이상을 확인한다. 299.95~300.98, 305.80~306.99, 309.80의 저항을 무시하지 않으며 현재 관찰선 충족만으로 매수하지 않는다.","risk_condition_ko":"285.45 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T08:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T08:40:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-A","display_name":"BRK-A","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":774299.625,"market_data_asof":"2026-10-09T15:55:00-04:00","session_vwap":773120.7116666667,"relative_volume":0.9208972845336482,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단 시각은 2026-10-12T08:53:28.282493-04:00이다. 같은 날짜의 10:30 최초 검토 시각 전이지만, 이 시계만으로 실제 거래 세션이나 주문 가능 여부가 확인되지는 않는다. 10:30은 만료 시각이 아니며 설정된 만료 시각은 없다. / BRK-A의 최신 호가, 실제 거래일·단축장 여부, 거래정지, 스프레드, 호가 깊이와 당일 거래량가중평균가격을 확인한다. 제공된 장중 관측은 2026-10-09 자료다.","risk_condition_ko":"761,500 이하 하락, 종가 확인 후 (위험 축소에 최소 거래량 조건을 요구하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-09T15:55:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-09T16:25:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CRM","display_name":"Salesforce","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":237.54,"market_data_asof":"2026-10-12T06:40:00-04:00","session_vwap":234.48279341476368,"relative_volume":0.035672087397828546,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"230.04, 230.71, 231.80 회복을 관찰하고 과거 이동평균 수치를 갱신한다. 이 가격들은 자동 매수 기준이 아니다. / 239.45 돌파·재시험, 정규장 거래량가중평균가격, 시간대 조정 상대거래량 1.2 이상과 실제 구조적 손절선의 형성을 확인한다.","risk_condition_ko":"220.29 이하 하락, 장중 확인 시 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T06:40:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T07:10:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"META","display_name":"Meta Platforms","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":730.96,"market_data_asof":"2026-10-12T07:40:00-04:00","session_vwap":729.5004140411202,"relative_volume":0.11693141191913924,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"711.68–716.20 시험 이후 716.20 회복, 장중 저점 상승, 당일 장중 거래량가중평균가격 회복 및 동시간대 정규장 상대거래량 1.2배 이상을 함께 확인한다. / 728.07과 지연된 장전 참고값 733.44를 새로운 정규장 자료로 재평가한 뒤 739.44–741.90 회복 및 747.60 돌파를 감시한다.","risk_condition_ko":"711.68 이하 하락, 종가 확인 후 (정규장 일일 거래량이 당시 20거래일 평균의 1.2배 이상) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T07:40:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T08:10:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-12T01:18:30.663067+09:00",
  "as_of": "2026-10-09T15:00:00-04:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
