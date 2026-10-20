# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-20T15:22:27.510736+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261021T001053_local-freshness-us-overlay",
  "producer_finished_at": "2026-10-21T00:15:03.277464+09:00",
  "analysis_run_id": "20261020T175013_local-scheduler-us-full",
  "analysis_completed_at": "2026-10-20T20:29:59.150766+09:00",
  "analysis_trade_date_oldest": "2026-10-19",
  "analysis_trade_date_latest": "2026-10-19",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-20T11:13:00-04:00",
  "market_data_latest_at": "2026-10-20T11:14:00-04:00",
  "market_data_status": "FRESH"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-21T00:14:56.240285+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-21T00:14:56.240285+09:00",
    "run_started_at": "2026-10-21T00:10:53.411465+09:00",
    "run_finished_at": "2026-10-21T00:15:03.277464+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23507067,
    "total_market_value_krw": 23541874,
    "total_unrealized_pnl_krw": 34807,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 106727,
    "total_equity_krw": 24625253
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 543057,
      "current_price_krw": 566748,
      "market_value_krw": 6800983,
      "unrealized_pnl_krw": 284297
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 291070,
      "current_price_krw": 287094,
      "market_value_krw": 3158036,
      "unrealized_pnl_krw": -43744
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 422180,
      "current_price_krw": 455464,
      "market_value_krw": 2732789,
      "unrealized_pnl_krw": 199704
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 266002,
      "current_price_krw": 288726,
      "market_value_krw": 1732356,
      "unrealized_pnl_krw": 136341
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1871254,
      "current_price_krw": 1688290,
      "market_value_krw": 1688290,
      "unrealized_pnl_krw": -182964
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 553351,
      "current_price_krw": 507476,
      "market_value_krw": 1522430,
      "unrealized_pnl_krw": -137623
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 133891,
      "current_price_krw": 134022,
      "market_value_krw": 1206203,
      "unrealized_pnl_krw": 1181
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1466029,
      "current_price_krw": 1195053,
      "market_value_krw": 1195053,
      "unrealized_pnl_krw": -270976
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 362882,
      "current_price_krw": 452421,
      "market_value_krw": 904842,
      "unrealized_pnl_krw": 179078
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1413371,
      "current_price_krw": 1724621,
      "market_value_krw": 752047,
      "unrealized_pnl_krw": 135725
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 659662,
      "current_price_krw": 615523,
      "market_value_krw": 615523,
      "unrealized_pnl_krw": -44139
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 566974,
      "current_price_krw": 447225,
      "market_value_krw": 447225,
      "unrealized_pnl_krw": -119749
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 135578,
      "current_price_krw": 108912,
      "market_value_krw": 435649,
      "unrealized_pnl_krw": -106666
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 346132,
      "current_price_krw": 350448,
      "market_value_krw": 350448,
      "unrealized_pnl_krw": 4316
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":339.86,"market_data_asof":"2026-10-20T11:13:00-04:00","session_vwap":341.17709361861773,"relative_volume":0.7497332278372495,"spread_bps":0.8805271422500273,"day_high":343.06,"day_low":338.7,"execution_condition_ko":"거래일·휴장·조기폐장·거래정지 여부와 신선한 정규장 5분봉을 확인한다. 지연된 장전 관측값은 실행 신호로 사용하지 않는다. / 340.12–340.41 회복과 재시험 지지, 실제 정규장 거래량가중평균가격 상회 및 동시간대 상대거래량 1.2 이상을 관찰한다.","risk_condition_ko":"338.43 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:23:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":263.2299,"market_data_asof":"2026-10-20T11:13:00-04:00","session_vwap":263.12247726392457,"relative_volume":1.0563363168795805,"spread_bps":0.7567731194202609,"day_high":265.3397,"day_low":260.42,"execution_condition_ko":"263.70~263.86 상회 후 두 개의 5분봉 유지·재시험 지지·정규장 거래량가중평균가격 상회·동시간대 상대거래량 1.2 이상 확인 / 256.03~256.84 눌림에서 하락 거래량 감소, 저점 상승과 반등 거래량 확인; 접촉만으로 매수하지 않음","risk_condition_ko":"255.04 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:23:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":100.6,"market_data_asof":"2026-10-20T11:14:00-04:00","session_vwap":100.60461028398453,"relative_volume":0.8955437022723597,"spread_bps":0.9939863823870698,"day_high":100.61,"day_low":100.6,"execution_condition_ko":"운용사 원문으로 SGOV 보유내역·듀레이션·비용 반영 순수익률·순자산가치·분배 일정을 확인하고 대안 현금의 이자조건과 비교한다. 기업식 주당순이익 자료 부재 자체를 운용 훼손으로 해석하지 않는다. / 가격 조정·분배금 처리·기준일을 통일해 50일 평균 100.2330과 100.5512의 차이를 해소한다. 공격 분석가가 언급한 약 0.21% 가격 상승을 총수익이나 독립적인 매수세 증거로 사용하지 않는다.","risk_condition_ko":"100.52 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:24:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":215.44,"market_data_asof":"2026-10-20T11:13:00-04:00","session_vwap":215.28808039478218,"relative_volume":0.6678800037639953,"spread_bps":0.4625453872657048,"day_high":216.255,"day_low":213.765,"execution_condition_ko":"212.93~211.73 방어·재회복과 당일 정규장 거래량가중평균가격 지지, 동일 시간대 상대거래량 1.2 이상 확인 / 216.30 위 완성된 정규장 종가 또는 다음 검증 거래일 재시험 지지 이후 구조적 손절·비용 차감 손익비 재계산","risk_condition_ko":"210.96 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:23:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":1267.94,"market_data_asof":"2026-10-20T11:13:00-04:00","session_vwap":1259.9896361772994,"relative_volume":0.34800409163277185,"spread_bps":34.042553191490356,"day_high":1284.87,"day_low":1222.2909,"execution_condition_ko":"판단시각은 2026-10-20T05:44:41.845263-04:00이다. 실제 거래일·정규장 운영시간·거래정지 여부와 신선한 시세·호가를 별도로 확인해야 한다. 10:30은 검증된 거래일의 검토 개시 하한이지 만료시각이 아니다. 현재 설정된 진입 만료시각은 없다. / 제공된 05:05 개장 전 시세는 판단시각보다 약 40분 전 자료다. 가격 1240.57, 거래량 109주, 호가 차이 약 2.30%와 저점 1232.88로 정규장 지지 실패나 진입 충족을 선언하지 않는다.","risk_condition_ko":"1,234.36 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:23:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":898.175,"market_data_asof":"2026-10-20T11:13:00-04:00","session_vwap":897.9184855355003,"relative_volume":0.9217896358666794,"spread_bps":12.448567037736735,"day_high":916.87,"day_low":877.44,"execution_condition_ko":"재무제표 통화·단위·주식 기준·해당 환산비율과 원자료 공개시각을 확인하고 연구 기준시각 이전 정보인지 검증한다. / 거래일정, 최신 정규장 가격, 거래량가중평균가격과 동일 경과시간 기준 상대거래량을 확보한다.","risk_condition_ko":"934.58 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:23:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":424.76,"market_data_asof":"2026-10-20T11:14:00-04:00","session_vwap":422.6187045045261,"relative_volume":0.8727013213476185,"spread_bps":3.0438905604269753,"day_high":427.36,"day_low":416.12,"execution_condition_ko":"거래소 일정·거래상태·신선한 매수매도 호가·가격차·정규장 봉과 실제 보유내역을 먼저 확인한다. / 410.58–415.50에서의 안정과 407.13의 확인된 실패를 구분한다. 지연된 장전 관측으로 지지 유지나 붕괴를 확정하지 않는다.","risk_condition_ko":"407.13 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:24:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":462.31,"market_data_asof":"2026-10-20T11:13:00-04:00","session_vwap":455.4027884829132,"relative_volume":0.7608346707467666,"spread_bps":11.998628728145404,"day_high":467.5843,"day_low":439.5,"execution_condition_ko":"448.55~450.00 회복과 새로 관측한 정규장 재시험 지지를 확인한다. 장전 관찰값과 구분한다. / 471.77~473.50 돌파·지지 전환, 482.00 통과, 동일시간대 누적 상대거래량 1.2배 이상과 정규장 거래량가중평균가격 상회를 관찰한다. 이는 재평가 조건이지 현재 매수 허가가 아니다.","risk_condition_ko":"448.55 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:23:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":380.2626,"market_data_asof":"2026-10-20T11:13:00-04:00","session_vwap":380.5542471569747,"relative_volume":1.0311028372878226,"spread_bps":9.849663037843325,"day_high":388.71,"day_low":372.79,"execution_condition_ko":"390.05~390.72 및 384.77~386.01 방어와 393.14 회복 지속성을 확인한다. 393.14 단독 회복은 추세 전환이나 축소 취소 승인이 아니다. / 400.00~403.73 반등 실패는 추가 위험 축소 조건이다. 403.73 돌파·재지지는 매수 재평가 신호일 뿐 주문 승인이 아니다.","risk_condition_ko":"393.14 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:23:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":335.63,"market_data_asof":"2026-10-20T11:13:00-04:00","session_vwap":336.4576217030203,"relative_volume":0.6126492362678373,"spread_bps":1.4773012660475207,"day_high":341.09,"day_low":330.8001,"execution_condition_ko":"실제 거래일·휴장·조기종료·거래정지 여부와 최신 정규장 호가·스프레드·호가 깊이를 확인한다. 지연 장전 자료로 대체하지 않는다. / 확인된 정규장 미국 동부시간 10:30 이후 340.20 돌파·재시험 지지, 정규장 누적 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상을 관찰한다. 충족만으로 매수하지 않는다.","risk_condition_ko":"328.58 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:23:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":81.7899,"market_data_asof":"2026-10-20T11:13:00-04:00","session_vwap":81.77851189387968,"relative_volume":0.606915782215476,"spread_bps":1.220628623741851,"day_high":82.18,"day_low":81.43,"execution_condition_ko":"GLDM 82.11·82.28 회복 여부와 82.73 저항 반응을 관찰한다. 82.11은 과거 자료의 거래량가중이동평균이며 당일 세션 거래량가중평균가격이 아니다. / 83.11 돌파·되돌림 이후에도 84.52 첫 저항까지 비용 차감 후 보상·위험을 다시 계산한다. 기존 진입·손절 예시로는 최소 2배 요건을 충족하지 못한다.","risk_condition_ko":"80.57 이하 하락, 거래량 조건 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:23:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":342.04,"market_data_asof":"2026-10-20T11:13:00-04:00","session_vwap":344.10001227426426,"relative_volume":0.4303550065814948,"spread_bps":2.038468818707121,"day_high":344.77,"day_low":341.0,"execution_condition_ko":"339.08–340.72에서 신선한 정규장 지지 반응, 높아진 저점, 거래량가중평균가격 회복과 동시간대 상대거래량 1.2 이상을 관찰한다. 관찰 충족만으로 매수하지 않고 최초 미돌파 저항까지 비용 차감 후 보상 대비 위험을 재계산한다. / 347.43 위 종가와 유지·재시험 성공을 확인한다. 이는 회복 신호이지 전체 가격범위 돌파가 아니다.","risk_condition_ko":"339.08 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:23:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":1294.135,"market_data_asof":"2026-10-20T11:13:00-04:00","session_vwap":1295.6076617811723,"relative_volume":1.0773469373302522,"spread_bps":4.69340883822666,"day_high":1311.75,"day_low":1260.17,"execution_condition_ko":"1230.66~1239.10 재시험 후 1239.10 회복, 연속 완성 5분봉의 저점 상승, 정규장 거래량가중평균가격 상회와 동일 경과시간 상대거래량 1.2 이상을 관찰한다. 기존 손익비가 부족하므로 이것만으로 매수하지 않는다. / 1208.74~1216.71 재시험 후 회복 시 실제 구조적 손절과 가까운 저항으로 비용 차감 손익비를 재계산한다. 깊은 눌림목 자체는 매수 근거가 아니다.","risk_condition_ko":"1,208.74 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:23:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":216.37,"market_data_asof":"2026-10-20T11:13:00-04:00","session_vwap":215.99378147643483,"relative_volume":0.7412266594923514,"spread_bps":0.9170525929653724,"day_high":218.46,"day_low":212.77,"execution_condition_ko":"거래 일정·상태, 최신 호가, 연속 정규장 봉과 출처 게시 시각을 먼저 검증한다. 보유 비중과 상관 노출도 실제 운용한도와 대조한다. / 212.85~214.13 지지와 이탈 확인 여부를 관찰한다. 아래 208.93~210.96 구간은 참고 지지일 뿐 자동 저가 매수 조건이 아니다.","risk_condition_ko":"212.85 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:23:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":406.985,"market_data_asof":"2026-10-20T11:14:00-04:00","session_vwap":406.506034627597,"relative_volume":0.7458513720522546,"spread_bps":1.4687882496926667,"day_high":408.585,"day_low":403.5401,"execution_condition_ko":"398.01–399.73에서 매도거래량 감소, 연속된 5분봉 2개의 반등 확인, 실시간 거래량가중평균가격 회복을 관찰한다. / 389.56–391.81에서는 하락 원인을 재평가하고 지지 형성을 확인한다. 과거 10일 지수이동평균 390.52는 반드시 갱신한다.","risk_condition_ko":"398.01 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:24:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":288.38,"market_data_asof":"2026-10-20T11:14:00-04:00","session_vwap":288.11178952571527,"relative_volume":0.47302561325055265,"spread_bps":4.507550146497193,"day_high":289.34,"day_low":285.0,"execution_condition_ko":"282.59–282.96과 279.40–279.58의 단기 지지, 이후 277–279 회복 구간을 관찰한다. 가격이 지지 구간에 들어오는 것만으로 매수하지 않는다. / 277–279에서 회복·재시험, 갱신된 추세 지지선 재탈환, 정규장 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상, 비용 차감 후 전체 거래 손익비 2배 이상과 포트폴리오 여력을 모두 확인한다. 미해소 매도 신호가 있으면 신규 진입을 차단한다.","risk_condition_ko":"277.26 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:24:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":995.4903,"market_data_asof":"2026-10-20T11:14:00-04:00","session_vwap":998.8953634069093,"relative_volume":0.8041076404284502,"spread_bps":6.41398248181021,"day_high":1003.0,"day_low":994.75,"execution_condition_ko":"977–983에서 완료봉 반등과 장중 거래량가중평균가격 회복, 동시간대 상대거래량 1.2 이상을 관찰한다. 이전 지지 실패가 미해결이면 매수를 차단한다. / 실제 진입가와 구조적 손절을 사용해 첫 저항 997.43까지 비용 후 손익비 2 이상인지 확인한다. 관찰구간 전체를 매수 가능 가격으로 취급하지 않는다.","risk_condition_ko":"977.24 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:24:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MSFT","display_name":"Microsoft","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":529.555,"market_data_asof":"2026-10-20T11:14:00-04:00","session_vwap":530.625217300278,"relative_volume":0.27794131787865173,"spread_bps":2.0704518290562244,"day_high":534.21,"day_low":525.84,"execution_condition_ko":"최종 판단시각은 2026-10-20T06:43:09.218217-04:00이다. 제안된 2026-10-20T10:30:00-04:00은 아직 도달하지 않은 최초 검토 가능 시점이지 만료시각이 아니다. 거래일·정규장·마감시각은 별도로 확인하며 임의로 다음 거래일로 이월하지 않는다. / 529.80–531.32 회복·재시험 또는 524.43–528.06 반등을 관찰한다. 완료된 5분봉 두 개, 정규장 거래량가중평균가격 지지, 동일 경과시간 상대거래량 1.2 이상을 확인한다.","risk_condition_ko":"524.43 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:24:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":222.925,"market_data_asof":"2026-10-20T11:14:00-04:00","session_vwap":223.89980825825245,"relative_volume":0.5480427379867918,"spread_bps":4.048674059245751,"day_high":227.16,"day_low":221.56,"execution_condition_ko":"정규장 일정·거래정지·신선한 호가와 분봉·동시간대 거래량·계좌 집중도를 확인한다. 장전 자료와 전일 일봉 거래량으로 대체하지 않는다. / 218.05~220.41에서 연속 두 개의 5분봉 지지·회복을 관찰하되 단순 도달은 매수 신호로 보지 않는다. 회복 후 실제 체결가격에서도 첫 목표까지 비용 차감 손익비 1.5배 이상인지 다시 계산한다.","risk_condition_ko":"222.55 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:24:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":621.73,"market_data_asof":"2026-10-20T11:14:00-04:00","session_vwap":620.6661917803815,"relative_volume":0.623728230277368,"spread_bps":6.744929258538905,"day_high":623.8799,"day_low":616.595,"execution_condition_ko":"598.60~606.61에서 하락 거래량 감소·저점 방어·단기 고점 회복을 확인한다. 기존 감축 신호가 해소되고 비용 차감 후 손익비가 최소 2배일 때만 신규 진입을 재평가한다. / 622.49 위 정규장 5분봉 마감·재시험 지지·정규장 거래량가중평균가격 상회·동일 시간대 상대거래량 1.2 이상을 확인한다. 독립적으로 타당한 손절·목표가 없으면 계속 대기한다.","risk_condition_ko":"608.59 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:24:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AMT","display_name":"AMT","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":184.36,"market_data_asof":"2026-10-20T11:14:00-04:00","session_vwap":183.8701670132234,"relative_volume":0.33630022784494235,"spread_bps":14.102077344469864,"day_high":184.72,"day_low":182.96,"execution_condition_ko":"거래 일정·거래정지·신선한 정규장 호가와 완성된 5분봉을 먼저 확인한다. / 179.36~181.31에서 두 개의 완성된 5분봉 저점 상승, 정규장 거래량가중평균가격 회복, 동시간대 상대거래량 1.2 이상을 관찰하되 이것만으로 매수하지 않는다.","risk_condition_ko":"178.16 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:24:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"CLF","display_name":"CLF","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":13.45,"market_data_asof":"2026-10-20T11:14:00-04:00","session_vwap":13.214596830949448,"relative_volume":1.8413064113643038,"spread_bps":7.371913011426307,"day_high":13.72,"day_low":12.625,"execution_condition_ko":"공식 실적·현금흐름·신용 자료와 공개 시각, 보고 기간, 통화·단위·주식 기준을 먼저 확인한다. 여러 분기의 완전한 회복 확정 대신 현재 유동성과 개선 가능성을 검증한다. / 거래일·거래 상태·신선한 정규장 자료·보유 여력을 확인하고, 조건부 주문 활성화 전에 시간대가 포함된 유한 만료 시각을 별도로 정한다.","risk_condition_ko":"12.94 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:24:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":94.15,"market_data_asof":"2026-10-20T11:14:00-04:00","session_vwap":93.81333345635606,"relative_volume":1.0044301239012072,"spread_bps":3.178471155374385,"day_high":94.92,"day_low":93.42,"execution_condition_ko":"91.97~92.67에서 하락 멈춤, 정규장 5분봉 2개의 저점 상승, 세션 거래량가중평균가격 회복과 동일 시간대 상대거래량 1.2 이상을 함께 관찰한다. 가격 접촉만으로 매수하지 않는다. / 96.50 돌파·재지지와 거래 참여를 관찰하되 비용 차감 후 최소 2배 손익비가 없으면 진입하지 않는다. 98.00~100.00은 관찰 구간이지 확정 목표가가 아니다.","risk_condition_ko":"90.51 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:24:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":158.27,"market_data_asof":"2026-10-20T11:14:00-04:00","session_vwap":158.6097990840103,"relative_volume":0.3317065769705729,"spread_bps":1.2609545425893847,"day_high":159.45,"day_low":158.06,"execution_condition_ko":"현재 기준시각은 2026-10-20T06:25:24.302751-04:00이다. 2026-10-20T10:30:00-04:00은 가장 이른 신규 진입 재평가 시각이지 만료시각이 아니다. 거래일·세션·주문 유효기간은 별도 확인한다. / 정규장 운영·거래 가능 상태·실적 발표시각·호가 시각·5분봉을 확인한다. 날짜만 있는 당일 기사와 시간대 미기재 재무조회는 결정시각 이전 공개 자료로 확정하지 않는다.","risk_condition_ko":"154.19 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:24:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":104.81,"market_data_asof":"2026-10-20T11:14:00-04:00","session_vwap":105.28871799913507,"relative_volume":1.006372423498724,"spread_bps":0.9570751782543815,"day_high":106.505,"day_low":104.315,"execution_condition_ko":"신선한 정규장 매도 가능 가격이 104.82와 106.11의 부분 이익실현 기준을 충족하는지 확인한다. 제공된 지연 장전 호가로 실행하지 않는다. / 103.04–103.31은 첫 관찰 구간이다. 102.09–102.47에서는 저점 상승, 102.30 회복, 정규장 거래량가중평균가격 지지와 동시간대 상대거래량 1.2 이상을 함께 관찰한다. 가격 도달만으로 매수하지 않는다.","risk_condition_ko":"104.82 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:24:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"UNH","display_name":"UNH","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":418.085,"market_data_asof":"2026-10-20T11:14:00-04:00","session_vwap":415.9524790722298,"relative_volume":0.7681442680021504,"spread_bps":2.628089498393608,"day_high":419.31,"day_low":408.28,"execution_condition_ko":"399.20~400.00 정규장 지지, 해당 세션 거래량가중평균가격 회복, 시간대 보정 상대거래량 1.2 이상과 비용 차감 손익비 2.0 이상을 함께 확인한다. 모두 확인되고 자료·계좌·유효기간 검증까지 완료되면 소규모 최초 진입을 새로 판단할 수 있다. / 414.12 위 정규장 5분봉 마감과 재시험 지지를 관찰하되, 돌파만으로 매수하지 않고 408.50 및 420~425 공급을 포함해 손익비를 재산정한다.","risk_condition_ko":"395.52 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:24:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":201.575,"market_data_asof":"2026-10-20T11:14:00-04:00","session_vwap":201.43582007624704,"relative_volume":0.3652868939692173,"spread_bps":7.931393446685996,"day_high":203.03,"day_low":200.3,"execution_condition_ko":"공식 발표시각, 거래일 일정, 거래정지와 최신 호가를 확인하고 계좌의 보유·집중·현금 한도를 점검한다. / 재무 표시통화·단위·기간·주식 기준을 대조한다. 조건부 배당충당 계산을 확정된 연간 자금 부족으로 해석하지 않는다.","risk_condition_ko":"198.85 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:24:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":176.07,"market_data_asof":"2026-10-20T11:14:00-04:00","session_vwap":176.96658337188862,"relative_volume":0.4636845210460262,"spread_bps":3.41860862628923,"day_high":180.26,"day_low":174.915,"execution_condition_ko":"179.30 정규장 돌파 재시험과 완료된 5분봉 2개 유지, 당일 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상. / 173.12~174.68에서 지지 반전 후 174.68 회복. 단순 지지선 접촉은 진입 신호가 아니다.","risk_condition_ko":"177.23 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:24:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"TXN","display_name":"Texas Instruments","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":280.18,"market_data_asof":"2026-10-20T11:14:00-04:00","session_vwap":277.5307659419802,"relative_volume":0.43624362381304177,"spread_bps":15.248497313782401,"day_high":282.45,"day_low":272.01,"execution_condition_ko":"지지 경로: 272.07–273.59에서 안정되고 정규장 5분봉 저점이 높아지며 당일 거래량가중평균가격을 회복해야 한다. 281.13까지 비용 차감 후 손익비 2:1을 충족해야 한다. / 돌파 경로: 281.13 회복 후 283.12 돌파와 재시험 성공을 관찰한다. 검증된 정규장 동일시각 상대거래량 1.2 이상과 287.85까지 적정 손익비가 필요하다.","risk_condition_ko":"272.07 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:24:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"TSLA","display_name":"Tesla","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":374.605,"market_data_asof":"2026-10-20T11:14:00-04:00","session_vwap":371.5898486985674,"relative_volume":1.0322581790904528,"spread_bps":3.17939750417308,"day_high":377.59,"day_low":363.64,"execution_condition_ko":"위험 대응 조건: 349.33 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"349.33 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T11:24:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-20T23:28:06.918178+09:00",
  "as_of": "2026-10-20T10:21:00-04:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
