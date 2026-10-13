# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-13T14:25:59.694033+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261013T232043_local-scheduler-us-overlay_only",
  "producer_finished_at": "2026-10-13T23:23:48.478848+09:00",
  "analysis_run_id": "20261013T175359_local-scheduler-us-full",
  "analysis_completed_at": "2026-10-13T22:07:17.421155+09:00",
  "analysis_trade_date_oldest": "2026-10-12",
  "analysis_trade_date_latest": "2026-10-12",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-13T10:20:00-04:00",
  "market_data_latest_at": "2026-10-13T10:20:00-04:00",
  "market_data_status": "FRESH"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-13T23:23:41.830813+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-13T23:23:41.830813+09:00",
    "run_started_at": "2026-10-13T23:20:43.113993+09:00",
    "run_finished_at": "2026-10-13T23:23:48.478848+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23572367,
    "total_market_value_krw": 24474074,
    "total_unrealized_pnl_krw": 901707,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 104766,
    "total_equity_krw": 25556013
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 544565,
      "current_price_krw": 591225,
      "market_value_krw": 7094700,
      "unrealized_pnl_krw": 559913
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 291879,
      "current_price_krw": 283810,
      "market_value_krw": 3121918,
      "unrealized_pnl_krw": -88755
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 423353,
      "current_price_krw": 470849,
      "market_value_krw": 2825096,
      "unrealized_pnl_krw": 284975
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 266741,
      "current_price_krw": 301910,
      "market_value_krw": 1811465,
      "unrealized_pnl_krw": 211017
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1876451,
      "current_price_krw": 1734756,
      "market_value_krw": 1734756,
      "unrealized_pnl_krw": -141695
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 554888,
      "current_price_krw": 569138,
      "market_value_krw": 1707416,
      "unrealized_pnl_krw": 42752
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1470101,
      "current_price_krw": 1325220,
      "market_value_krw": 1325220,
      "unrealized_pnl_krw": -144881
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 134263,
      "current_price_krw": 134287,
      "market_value_krw": 1208590,
      "unrealized_pnl_krw": 221
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 363890,
      "current_price_krw": 462687,
      "market_value_krw": 925375,
      "unrealized_pnl_krw": 197595
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 661494,
      "current_price_krw": 768418,
      "market_value_krw": 768418,
      "unrealized_pnl_krw": 106924
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1417297,
      "current_price_krw": 1574367,
      "market_value_krw": 686526,
      "unrealized_pnl_krw": 68492
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 568549,
      "current_price_krw": 476099,
      "market_value_krw": 476099,
      "unrealized_pnl_krw": -92450
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 135955,
      "current_price_krw": 110009,
      "market_value_krw": 440039,
      "unrealized_pnl_krw": -103782
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 347094,
      "current_price_krw": 348456,
      "market_value_krw": 348456,
      "unrealized_pnl_krw": 1362
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":212.57,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":213.31561082455528,"relative_volume":1.049832719143932,"spread_bps":0.4709982808558465,"day_high":213.94,"day_low":212.215,"execution_condition_ko":"211.50~211.80 지지, 완성 5분봉의 211.80 회복·재시험, 정규장 거래량가중평균가격 상회와 시간대 보정 상대거래량 1.2 이상을 관찰한다. 실제 체결 가능성과 전체 청산계획의 비용 후 손익비 2.0 이상까지 충족해야 소규모 최초 진입을 재검토한다. / 213.43 돌파만으로 추격하지 않는다. 214.05~214.97 저항 통과와 215.70 종가 회복을 구분하며 돌파 후 상단 목표가 없으면 추가하지 않는다.","risk_condition_ko":"209.81 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":260.4901,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":261.15953748724,"relative_volume":0.9980414852320626,"spread_bps":2.290863273643705,"day_high":262.835,"day_low":259.19,"execution_condition_ko":"258.85–259.27 회복을 완성된 정규장 5분봉 두 개에서 확인한다. 이 회복만으로 신규 매수를 승인하지 않는다. / 253.78–256.00에서 하락 정지와 지지 회복을 확인하고 첫 저항 262.13 및 실제 비용을 반영한 보상·위험을 재계산한다.","risk_condition_ko":"253.78 이하 하락, 종가 확인 후 (최소 거래량 충족을 매도 전제조건으로 요구하지 않음) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":425.99,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":424.29117077221144,"relative_volume":0.36613490347401195,"spread_bps":15.911643579183986,"day_high":429.0,"day_low":417.0,"execution_condition_ko":"계좌 순자산·보유분·결제 완료 현금·종목 및 업종 집중도·급락 스트레스 손실을 확인한다. 정보 부재를 여유나 한도 위반으로 간주하지 않는다. / 실제 거래일정, 정상 거래 여부, 최신 매수·매도호가, 정규장 5분봉, 당일 거래량가중평균가격 및 동시간대 상대거래량을 확인한다.","risk_condition_ko":"420 이하 하락, 2개 봉 확인 후 (매도 거래량 증가는 판단을 강화하지만 최초 감축의 필수조건은 아니다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":992.17,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":989.901683543907,"relative_volume":0.689167116142731,"spread_bps":11.06840272886461,"day_high":1001.6962,"day_low":963.48,"execution_condition_ko":"973.36–989.92에서 저점 상승, 지지 안정화, 정규장 거래량가중평균가격 회복과 반등 거래 참여 개선을 확인한다. 가격 접촉만으로 매수하지 않는다. / 1014.95 위에서 5분 봉 2개가 완성되고 재시험에 성공하며, 정규장 거래량가중평균가격과 같은 시각 대비 상대 거래량 1.2 이상을 유지하는지 관찰한다.","risk_condition_ko":"968.84 이하 하락, 종가 확인 후 (하락 거래량 확대와 979.70 회복 실패를 함께 확인한다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1179.045,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":1181.2671536800847,"relative_volume":0.338751957433251,"spread_bps":16.69079451588211,"day_high":1193.3,"day_low":1172.58,"execution_condition_ko":"1168–1174에서 정규장 안정화와 지지 확인, 해당 정규장 거래량가중평균가격 회복 및 비용 차감 후 2:1 이상 손익비가 확인되면 재검토한다. / 1188–1199와 1206.63–1215 저항을 관찰한다. 1199 또는 1206.63 상향 통과만으로 매수하지 않으며 1215 돌파·재시험과 거래 참여를 확인한다.","risk_condition_ko":"1,163.53 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1296.22,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":1303.14706357541,"relative_volume":0.40283354831413365,"spread_bps":26.146797784040345,"day_high":1314.99,"day_low":1284.19,"execution_condition_ko":"1311~1315 재시험 방어와 1315 상회 유지, 저점 상승, 정규장 거래량가중평균가격 상회 및 동시간대 상대거래량 1.2 이상을 확인한다. 마지막 종가가 1315 위라는 사실만으로 재시험 방어가 확인된 것은 아니다. / 1377.45 위 정규장 종가와 다음 검증된 거래일 첫 30~60분 지지 유지 여부를 확인한다. 첫 저항 1402까지의 비용 후 보상/위험을 다시 계산한다.","risk_condition_ko":"1,293.7 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":441.98,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":441.1029687049903,"relative_volume":0.5471796908598521,"spread_bps":6.550489592627772,"day_high":443.66,"day_low":437.4,"execution_condition_ko":"지지 반전: 432.58~434.67 시험 후 저점 상승, 434.67 위 정규장 5분봉 두 개 연속 종가, 반등 거래량 증가, 정규장 거래량가중평균가격 상회와 검증된 동시간대 상대거래량 1.2 이상을 확인한다. / 초기 회복: 444.35 재탈환과 449.75~454.40 저항 통과를 관찰한다. 이 회복만으로 목표 비중 진입을 허용하지 않는다.","risk_condition_ko":"432.58 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":100.53,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":100.52546390435613,"relative_volume":1.2847752290731107,"spread_bps":0.9947774185531076,"day_high":100.53,"day_low":100.52,"execution_condition_ko":"핵심 검증은 공식 보유내역·만기 구성·순자산가치·보수·비교 가능한 수익률·필요 유동성·현재 호가에 집중한다. 중립 분석가의 지적대로 기업 주당순이익이나 모든 소셜 자료의 확보를 재평가의 필수조건으로 삼지는 않는다. / 수익률 필드 3.69는 단위와 산식이 불명확해 계산에 사용하지 않는다. 시장 보고서의 50일 평균 100.1615와 개요 자료의 100.5424는 기준일·조정 방식을 대조해야 한다. 개요 조회시각 19:37:57은 시간대가 없어 결정시점 이전 자료인지 확인할 수 없다.","risk_condition_ko":"100.45 이하 하락, 종가 확인 후 (분배금 영향을 제외한 종가 이탈과 거래량·평균진폭 확대 동반) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":355.79,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":352.25044700713255,"relative_volume":0.9051117151097113,"spread_bps":3.6494813525538077,"day_high":356.78,"day_low":348.1101,"execution_condition_ko":"실제 거래일·정규장 일정·정상 거래 여부와 최신 호가·거래량·거래량가중평균가격을 먼저 확인한다. / 354.22와 349~350 지지, 실패 시 343.29와 335.20을 점검한다. 반등 실패 감축과 지지 실패 감축은 누적 수량으로 관리한다.","risk_condition_ko":"349 이하 하락, 거래량 조건 확인 후 (349 이탈 시 거래량 증가와 이후 349~350 회복 실패를 함께 확인) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":82.35,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":82.59264478970927,"relative_volume":0.5621613039545058,"spread_bps":1.2132241431610693,"day_high":82.85,"day_low":82.35,"execution_condition_ko":"82.57~82.64 회복, 83.11 돌파와 82.99~83.11 지지 전환을 순서대로 관찰한다. 전일 평균 수준과 갱신된 평균·가격 구조를 구분한다. / 82.28 근접 지지 약화와 80.75 핵심 지지 이탈을 구분한다. 상승 시 83.77~84.15, 84.52~84.89, 85.70의 저항과 실제 손익비를 재평가한다.","risk_condition_ko":"82.57 이하 하락, 2개 봉 확인 후 (거래량 증가를 위험 축소의 필수 조건으로 삼지 않는다.) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":346.295,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":345.13877346599065,"relative_volume":1.7282705755853105,"spread_bps":2.603225106659194,"day_high":348.1499,"day_low":341.12,"execution_condition_ko":"거래일 달력·정상 거래 상태·최신 호가·정규장 거래량가중평균가격·동일 경과시간 기준 상대거래량을 먼저 검증한다. / 335.44~336.51에서 저점 형성 후 336.51 위 연속 5분봉 두 개와 반등 거래량 증가를 관찰한다. 단순 지지 접촉은 진입 신호가 아니다.","risk_condition_ko":"335.44 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":575.3,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":567.6734579381408,"relative_volume":1.045259525757474,"spread_bps":28.69642527045932,"day_high":579.74,"day_low":548.4,"execution_condition_ko":"565~568 지지 후 576.76 회복 여부. 회복만으로 매수하지 않는다. / 585.32~588.40 및 595.06~595.51 저항대의 매물 소화와 거부 반응.","risk_condition_ko":"556.77 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":352.31,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":355.82542893230465,"relative_volume":1.1106258326519172,"spread_bps":2.5258549317326477,"day_high":358.58,"day_low":351.6,"execution_condition_ko":"345.14~346.08 재시험 후 5분봉 두 개의 346.08 이상 마감, 정규장 거래량가중평균가격 상회, 동일 시간대 상대거래량 1.2 이상을 확인한다. 단순 가격 도달은 매수 신호가 아니다. / 비용 후 보상비와 실제 출구 구조를 다시 계산한다. 355.59~356.83 및 359.44 저항을 무시하거나 근거 없는 상향 목표를 만들어 진입을 정당화하지 않는다.","risk_condition_ko":"345.14 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":225.5632,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":224.84504860435507,"relative_volume":0.8630784131516523,"spread_bps":1.7709301810772586,"day_high":226.61,"day_low":223.0602,"execution_condition_ko":"판단시각은 2026-10-13T06:27:02.664228-04:00이다. 2026-10-13T10:30:00-04:00은 아직 도래하지 않은 최초 재검토 가능시각이며 만료시각이 아니다. 실제 정규장 일정은 별도 검증해야 한다. / 2026-10-13 미국 동부시간 06:00의 224.7537은 지연된 개장 전 관측이다. 224.90 하회를 정규장 지지 붕괴로 처리하지 않는다. 개장 전 거래량가중평균가격 224.7107과 비교 기준이 불명확한 상대거래량 0.0717은 정규장 확인 자료로 대체하지 않는다.","risk_condition_ko":"222.46 이하 하락, 종가 확인 후 (하락 거래량 증가는 근거를 강화하지만 보호 조치의 필수조건은 아님) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":173.3,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":173.21530852859647,"relative_volume":0.5468393677802911,"spread_bps":4.610685263097949,"day_high":174.0899,"day_low":172.6518,"execution_condition_ko":"170.29~171.01에서 두 개의 완료된 5분봉으로 지지를 확인하고 정규장 거래량가중평균가격 회복, 동시간대 상대거래량 1.2 이상, 비용 차감 보상·위험 2배 이상을 함께 검증한다. 구간 전체가 매수 가능하지는 않다. / 172.55 돌파·재시험을 관찰하되 현재 168.50 위험 기준과 174.09 저항만으로는 신규 진입의 경제성이 부족하다. 돌파 확인만으로 추가 매수하지 않는다.","risk_condition_ko":"168.5 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":278.62,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":279.7326060504538,"relative_volume":0.5681898541790938,"spread_bps":9.706469181961738,"day_high":283.315,"day_low":277.65,"execution_condition_ko":"281.30 위 연속 5분봉 두 개, 재시험 지지, 최신 정규장 거래량가중평균가격 상회와 같은 시간대 상대거래량 1.2 이상을 함께 확인한다. 전일 일봉 거래량의 평균 대비 약 1.22배와 구분한다. / 276.01~277.60에서 매도 거래량 감소, 반등 거래량 회복과 거래량가중평균가격 회복을 확인한다. 277.00 진입·270.50 손절에서 281.30만 목표로 하면 비용 전 보상/위험은 약 0.66배로 불충분하다.","risk_condition_ko":"276.01 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"SPYM","display_name":"SPYM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":91.4991,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":91.5818147963528,"relative_volume":1.1798304483269733,"spread_bps":1.0929558992300252,"day_high":91.65,"day_low":91.47,"execution_condition_ko":"최종 판단 시계는 2026-10-13T08:04:31.684678-04:00이며 일봉 기준일은 2026-10-12다. 이 시계만으로 실제 거래일·정규장 시간·거래정지 여부·최신 호가를 확인할 수 없다. / 제공된 07:40 장전 자료에는 원천 지연 896초가 있었다. 현재 체결 가능성이나 정규장 진입 신호로 사용하지 않는다. 일평균 대비 거래량 약 1.88배도 동시간대 정규장 상대거래량 조건을 대신하지 않는다.","risk_condition_ko":"90.67 이하 하락, 다음 거래일 확인 후 (위험감축에 거래량 하한을 요구하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":217.145,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":216.8405623412907,"relative_volume":0.5053528056339165,"spread_bps":4.616805170821528,"day_high":217.4401,"day_low":215.965,"execution_condition_ko":"CVX의 211.55~213.75에서 연속 두 개의 15분봉 지지와 저점 상승, 정규장 거래량가중평균가격 회복, 동시간대 상대 거래량 1.2 이상을 확인한다. 첫 장애물 216.67까지 비용 차감 후 손익비를 다시 계산한다. / 217.78 위 정규장 종가와 재시험을 관찰한다. 돌파만으로 추격하지 않으며 손익비가 부족하면 계속 대기한다.","risk_condition_ko":"209.37 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":102.48,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":102.41507586214732,"relative_volume":0.932782792939695,"spread_bps":0.9760382606989317,"day_high":102.66,"day_low":102.11,"execution_condition_ko":"SHEL 100.03~100.87에서 하락 거래량 둔화, 정규장 5분봉 반등과 당일 거래량가중평균가격 회복을 함께 확인한다. / SHEL 102.47 위 정규장 5분봉 마감·재지지와 동일 시간대 상대거래량 1.2 이상을 확인한다. 1.2는 정책 문턱이며 관측값이 아니다.","risk_condition_ko":"99.29 이하 하락, 2개 봉 확인 후 (위험 감축에 거래량 조건 없음) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":959.235,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":961.9138570477091,"relative_volume":0.5270952272124529,"spread_bps":5.9343782697636795,"day_high":966.0,"day_low":958.32,"execution_condition_ko":"보유분·미체결 주문·순자산·현금·취득원가와 기존 위험한도를 확인한다. 한도 초과가 검증되면 초과분을 위험축소하며 자금조달 매도로 분류하지 않는다. / 거래소 달력·정규장 여부·거래정지·호가 시각·매매호가 차이·완성된 5분봉·현재 거래량가중평균가격·동일 시각 상대거래량을 확인한다.","risk_condition_ko":"931.58 이하 하락, 종가 확인 후 (보호 목적의 축소에는 최소 거래량 조건을 적용하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"META","display_name":"Meta Platforms","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":767.54,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":755.2515173144584,"relative_volume":2.607948469576268,"spread_bps":4.5645128686662195,"day_high":771.2698,"day_low":734.84,"execution_condition_ko":"727.64~728.07 지지 재시험과 739.39·742.96 순차 회복을 관찰한다. 회복 뒤 첫 저항 752.24까지 비용 차감 후 보상·위험이 2배 미만이면 계속 대기한다. / 752.24 위 정규장 5분봉 2개 마감과 재시험 지지, 최신 정규장 거래량가중평균가격 상회, 같은 시간대 상대거래량 1.2 이상을 확인한다. 이 조건만으로 매수를 승인하지 않는다.","risk_condition_ko":"711.68 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":152.73,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":153.11734720592358,"relative_volume":0.29781091438795204,"spread_bps":4.581301744168434,"day_high":154.71,"day_low":152.22,"execution_condition_ko":"거래소 정규장 일정·거래 상태, 최신 호가·분봉, 실적·배당락 일정과 자료 공개시각을 먼저 확인한다. 제공된 자료만으로 현재 실행 가능성은 확인할 수 없다. / 153.68 돌파·재시험, 정규장 거래량가중평균가격 상회, 시간대 보정 상대거래량 1.2 이상을 함께 관찰한다. 이는 미래 확인 기준이지 현재 충족된 조건이 아니다.","risk_condition_ko":"151.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":392.76,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":392.52183508564144,"relative_volume":0.6599345434789456,"spread_bps":6.1290157822158715,"day_high":394.72,"day_low":390.69,"execution_condition_ko":"V의 거래일·조기폐장 일정·거래정지 여부와 최신 정규장 호가·분봉·거래량을 확인한다. / 384.65~386.84 재시험 또는 391.81 돌파·재시험에서 두 개 완료 5분봉의 지지, 당일 거래량가중평균가격 상회, 동일 시간대 거래량 조건을 확인한다. 관찰 신호를 자동 주문으로 전환하지 않는다.","risk_condition_ko":"384.65 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"WMT","display_name":"WMT","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":114.01,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":114.14808060119262,"relative_volume":0.8243351973237126,"spread_bps":2.6298487836950373,"day_high":114.825,"day_low":113.725,"execution_condition_ko":"거래일·휴장·조기폐장 일정, 정규장 여부, 거래정지 여부와 시각이 명시된 체결 가능 호가를 확인한다. / 눌림목은 111.23–111.51 재시험 후 완료된 5분 봉 2개가 111.51 위에서 마감하고 정규장 거래량가중평균가격과 비교 가능한 동일 시간대 상대거래량 1.2 이상을 유지해야 한다.","risk_condition_ko":"111.23 이하 하락, 종가 확인 후 (하방 위험 축소에는 거래량 증가를 요구하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AMT","display_name":"AMT","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":180.18,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":182.08387803777478,"relative_volume":0.37106666846664815,"spread_bps":12.143290831815358,"day_high":184.75,"day_low":180.18,"execution_condition_ko":"실제 거래 세션·휴장 및 조기폐장 일정, 최신 호가·스프레드·유동성·거래정지 상태부터 확인한다. / 확인된 정규장에서 미국 동부시간 10:30 이후 183.31 돌파, 182.52~183.31 재시험 지지와 183.31 재회복을 관찰한다.","risk_condition_ko":"180.03 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":90.74,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":91.23293850984265,"relative_volume":1.1888558056035203,"spread_bps":2.2053148086885015,"day_high":92.64,"day_low":90.2,"execution_condition_ko":"먼저 최신 정규장 가격·매수매도 호가·거래량가중평균가격·동일 경과시간 거래량·거래일정·거래정지를 확인한다. 제공된 시각만으로 장 운영이나 진입조건 충족을 판단하지 않는다. / 90.71–90.76 또는 89.67–89.81에서 안정화와 지지 회복을 감시한다. 단순 가격 접촉은 매수 신호가 아니며 실제 손절 집행 가능성과 비용 차감 후 최소 2배의 보상 대비 위험을 검증해야 한다.","risk_condition_ko":"89.67 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"CEG","display_name":"CEG","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":293.9499,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":291.6094545086188,"relative_volume":0.7873390058207498,"spread_bps":24.383124130708534,"day_high":296.0,"day_low":286.1279,"execution_condition_ko":"291.00 회복 후 290.40~291.00 재시험 유지, 당일 정규장 거래량가중평균가격 상회, 같은 경과시간 기준 상대거래량 1.2 이상과 반등 봉 거래량 증가를 확인한다. 현재 충족 여부는 미확인이다. / 301.77 위 확정 종가와 다음 확인된 거래일의 지지 유지를 점검한다. 중립 분석가의 지적대로 돌파 확인만으로 나쁜 손익비가 개선되지는 않으므로 추격하지 않는다.","risk_condition_ko":"285.12 이하 하락, 2개 봉 확인 후 (위험축소에 거래량 증가를 요구하지 않음) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"NU","display_name":"NU","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":15.72,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":15.707791413794025,"relative_volume":0.33034528154349013,"spread_bps":6.359300476947399,"day_high":15.86,"day_low":15.585,"execution_condition_ko":"15.43~15.58에서 하락 거래량 감소, 저점 방어, 반등 거래량 회복과 정규장 거래량가중평균가격 회복을 확인한다. 가격 접촉만으로 매수하지 않는다. / 16.22 위 정규장 5분봉 마감·재시험 지지와 동시각 기준 상대거래량 1.2 이상을 확인한다.","risk_condition_ko":"15.18 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GOOG","display_name":"GOOG","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":348.19,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":351.55571530893053,"relative_volume":0.9302025225222362,"spread_bps":3.6904035314321737,"day_high":354.5,"day_low":347.57,"execution_condition_ko":"거래일·거래정지 여부와 최신 정규장 자료를 확인한다. 2026-10-13T07:36:08.232954-04:00은 제안된 미국 동부시간 10:30 재평가 시각 이전이지만, 거래일이나 진입 조건 충족을 증명하지 않는다. / 343.13–344.59 접촉 후 344.59 위 5분봉 마감, 성공적인 재시험, 정규장 거래량가중평균가격 지지와 동일 경과시간 상대거래량 1.2 이상을 확인한다.","risk_condition_ko":"338.19 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"HPE","display_name":"Hewlett Packard Enterprise","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":69.7906,"market_data_asof":"2026-10-13T10:20:00-04:00","session_vwap":69.62512391172132,"relative_volume":1.4024114255409776,"spread_bps":5.715918833953452,"day_high":71.18,"day_low":67.05,"execution_condition_ko":"최종 판단시계는 2026-10-13T06:58:32.553139-04:00이며 2026-10-13T10:58:32.553139+00:00과 같은 순간이다. 실제 거래일·휴장 및 조기종료·거래정지·호가 신선도는 별도 확인해야 한다. 06:30 지연 관측의 69.14는 실행가격이 아니다. / HPE 68.72~69.51 부근의 하락 정지와 69.51·정규장 거래량가중평균가격 회복 및 재시험을 관찰한다. 상대거래량 확인과 별개로 유리한 목표·손절 구조가 필요하다.","risk_condition_ko":"71.22 이상 도달, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-13T10:50:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-13T23:10:03.734590+09:00",
  "as_of": "2026-10-08T15:10:00-04:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
