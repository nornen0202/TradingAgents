# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-01T15:47:04.682941+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261002T002809_github-actions-overlay-us",
  "producer_finished_at": "2026-10-02T00:37:23.625963+09:00",
  "analysis_run_id": "20261001T000500_github-actions-us",
  "analysis_completed_at": "2026-10-01T00:32:08.634901+09:00",
  "analysis_trade_date_oldest": "2026-09-29",
  "analysis_trade_date_latest": "2026-09-29",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-01T11:25:00-04:00",
  "market_data_latest_at": "2026-10-01T11:25:00-04:00",
  "market_data_status": "FRESH"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-02T00:37:20.894708+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23923536,
    "total_market_value_krw": 24747105,
    "total_unrealized_pnl_krw": 823569,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 88567,
    "total_equity_krw": 25812324
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 552678,
      "current_price_krw": 615270,
      "market_value_krw": 7383250,
      "unrealized_pnl_krw": 751112
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 296227,
      "current_price_krw": 281334,
      "market_value_krw": 3094683,
      "unrealized_pnl_krw": -163821
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 429660,
      "current_price_krw": 461351,
      "market_value_krw": 2768108,
      "unrealized_pnl_krw": 190146
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 270715,
      "current_price_krw": 311560,
      "market_value_krw": 1869361,
      "unrealized_pnl_krw": 245071
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1904406,
      "current_price_krw": 1816760,
      "market_value_krw": 1816760,
      "unrealized_pnl_krw": -87646
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 563154,
      "current_price_krw": 582002,
      "market_value_krw": 1746006,
      "unrealized_pnl_krw": 56543
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1492002,
      "current_price_krw": 1303430,
      "market_value_krw": 1303430,
      "unrealized_pnl_krw": -188572
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 136263,
      "current_price_krw": 136119,
      "market_value_krw": 1225071,
      "unrealized_pnl_krw": -1300
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 369311,
      "current_price_krw": 444439,
      "market_value_krw": 888878,
      "unrealized_pnl_krw": 150256
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 671349,
      "current_price_krw": 721557,
      "market_value_krw": 721557,
      "unrealized_pnl_krw": 50208
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1438411,
      "current_price_krw": 1556546,
      "market_value_krw": 678755,
      "unrealized_pnl_krw": 51514
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 577019,
      "current_price_krw": 470658,
      "market_value_krw": 470658,
      "unrealized_pnl_krw": -106361
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 137980,
      "current_price_krw": 111614,
      "market_value_krw": 446459,
      "unrealized_pnl_krw": -105464
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 352265,
      "current_price_krw": 334129,
      "market_value_krw": 334129,
      "unrealized_pnl_krw": -18136
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":455.25,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":455.8352236225735,"relative_volume":0.3452409061822126,"spread_bps":4.620106262443586,"day_high":457.818,"day_low":453.461,"execution_condition_ko":"2026-09-30 10:30 이후 459.43 상회 유지, 당일 거래량가중평균가격 상회 및 같은 시각 기준 상대 거래량 1.2 이상 / 463.72 위 거래량 동반 종가와 다음 거래일 지지 확인","risk_condition_ko":"447.07 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1345.02,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":1347.024088217389,"relative_volume":0.25704530929029445,"spread_bps":12.394256829908104,"day_high":1355.7,"day_low":1331.0,"execution_condition_ko":"10:30 이후 1387.46 회복, 거래량가중평균가격 상회 및 상대거래량 1.2 이상 / 1409.71 위 종가와 다음 거래일 첫 30~60분 동안 1387.46 유지","risk_condition_ko":"1,320.8 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":348.43,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":349.59644559424277,"relative_volume":0.5344749587000754,"spread_bps":4.324448993123471,"day_high":354.45,"day_low":346.09,"execution_condition_ko":"361.86 회복과 366.55 상향 돌파 시 정규장 거래량 및 거래량 가중 평균가격 확인 / 375.15 위 종가와 다음 거래일 유지 여부 확인; 자동 매수 신호는 아님","risk_condition_ko":"349.43 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":430.145,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":427.7672464175203,"relative_volume":0.3205634323042532,"spread_bps":17.29982466393943,"day_high":431.2,"day_low":423.0,"execution_condition_ko":"정규장 437.05 회복 / 10:30 이후 447.33 상회 유지, 상대거래량 1.2 이상 및 거래량 가중 평균가격 상회","risk_condition_ko":"420.1 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":207.61,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":207.73611514101086,"relative_volume":1.238871025133039,"spread_bps":0.4818232190618577,"day_high":208.76,"day_low":207.16,"execution_condition_ko":"10:30 이후 RSP가 211.39와 거래량가중평균가격 위에 머물고 상대거래량이 1.2 이상인지 확인 / 211.95 위 종가와 다음 거래일 첫 30~60분의 211.39 지지 확인","risk_condition_ko":"208.47 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":963.765,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":955.8304141486565,"relative_volume":0.5028660692294686,"spread_bps":10.775354775940334,"day_high":966.545,"day_low":942.0,"execution_condition_ko":"GEV가 거래량 개선과 함께 968.41 및 973.41 위에서 마감 / GEV가 상대 거래량 1.2 이상으로 988.48 위에서 마감","risk_condition_ko":"944.85 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":246.82,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":248.8281065591362,"relative_volume":0.8765560910064908,"spread_bps":2.433583451632621,"day_high":251.83,"day_low":246.1167,"execution_condition_ko":"미국 동부시간 10:30 이후 250.17과 251.34 회복, 당일 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상 / 종가 251.34 상회와 다음 거래일 유지 여부; 256.09 돌파 이후 비용 차감 보상·위험 재평가","risk_condition_ko":"244.24 이하 하락, 거래량 조건 확인 후 (거래량 증가를 동반한 정규장 종가 이탈) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":100.4,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":100.4054740579839,"relative_volume":3.0019584272320334,"spread_bps":0.9959663363369259,"day_high":100.41,"day_low":100.4,"execution_condition_ko":"미 동부시간 10:30 이후 100.68~100.69 유지와 거래량가중평균가격·시간대별 상대 거래량 확인 / 발행사 순자산가치, 보수, 보유자산, 듀레이션, 분배 산식과 일정 및 대체 수단의 세후 수익률 확인","risk_condition_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":82.4,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":82.30007100738926,"relative_volume":0.6180921857000512,"spread_bps":1.2170632264352361,"day_high":82.56,"day_low":82.08,"execution_condition_ko":"10:30 이후 84.39와 장중 거래량가중평균가격 동시 회복 및 상대거래량 1.2 이상 / 84.74를 거쳐 85.40 위 정규장 종가와 상대거래량 1.2 이상","risk_condition_ko":"81.32 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":1150.367,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":1148.4646542005685,"relative_volume":0.4488082957208583,"spread_bps":7.116202377852436,"day_high":1158.72,"day_low":1141.5,"execution_condition_ko":"기한 내 10:30 이후 1197.79 상향 돌파·유지, 시간 보정 상대거래량 1.2 이상, 거래량가중평균가격 상회 / 1197.79 위 종가와 가급적 270만 주 초과 거래량, 다음 거래일 지지 또는 재돌파","risk_condition_ko":"1,168.47 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":230.6607,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":230.07904710779678,"relative_volume":0.6562239497557574,"spread_bps":1.3104728622911932,"day_high":231.91,"day_low":228.16,"execution_condition_ko":"233.21 회복 후 234.14~234.50 돌파·지지와 동시간대 상대거래량 1.2 이상 / 다음 거래일 정규장 첫 30~60분 동안 234.50 유지","risk_condition_ko":"221.71 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":328.67,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":330.31185421777076,"relative_volume":0.5861155633840901,"spread_bps":1.2136290542801802,"day_high":332.4816,"day_low":328.37,"execution_condition_ko":"새 정규장 호가와 거래량, 현재 AAPL 보유 비중·현금·거래비용 확인 / 333.99~334.77 회복과 당일 거래량가중평균가격 상회, 상대 거래량 1.2 이상","risk_condition_ko":"328.7 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":531.01,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":529.5150000548582,"relative_volume":0.5004037443721804,"spread_bps":11.395362087630767,"day_high":543.15,"day_low":520.2,"execution_condition_ko":"555.54달러 회복과 당일 거래량가중평균 상회 및 같은 시각 기준 상대거래량 1.2배 이상 확인 / 573.80달러 위 종가 후 다음 거래일 첫 30~60분 유지 여부 확인","risk_condition_ko":"530.45 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":340.9,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":344.59392538406354,"relative_volume":1.0332478649951997,"spread_bps":2.939879464940935,"day_high":353.22,"day_low":339.62,"execution_condition_ko":"345.42 회복 후 349.91 위에서 당일 거래량가중평균가 지지와 동시간대 상대거래량 1.2 이상 확인 / 354.66을 거래량과 함께 종가 돌파하고 다음 거래일 지지; 359.44와 364.17 저항 확인","risk_condition_ko":"337.45 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"JNJ","display_name":"JNJ","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":261.84,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":262.9413015429438,"relative_volume":0.3362982289259677,"spread_bps":8.76374097430007,"day_high":263.975,"day_low":261.83,"execution_condition_ko":"다음 정규장 10:30 이후 265.08~263.26 지지 확인 뒤 269.92와 거래량가중평균가격 회복, 상대 거래량 1.2 이상 / 상대 거래량 1.2 이상으로 275.23 위 마감 후 다음 거래일 첫 30~60분간 해당 가격 유지","risk_condition_ko":"263.26 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"SCCO","display_name":"SCCO","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":198.5001,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":199.14766400387316,"relative_volume":0.39421060654979095,"spread_bps":23.753569352841527,"day_high":202.95,"day_low":197.42,"execution_condition_ko":"199.44–200.00의 실시간 지지 회복과 적정 호가 차이 / 205.41 상향 돌파 및 206.14 위 마감 여부","risk_condition_ko":"195.75 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"LRCX","display_name":"Lam Research","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":335.66,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":335.93234639166053,"relative_volume":0.5117102644591132,"spread_bps":14.63800803596795,"day_high":340.55,"day_low":331.045,"execution_condition_ko":"10:30 이후 328.32 및 당일 거래량가중평균가격 위 유지와 같은 시각 기준 상대거래량 1.2 이상 / 332.93 위 종가와 다음 거래일 지지 또는 재돌파","risk_condition_ko":"319.15 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":187.78,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":188.37554774188987,"relative_volume":0.29160855990367424,"spread_bps":7.970032677134279,"day_high":193.12,"day_low":186.92,"execution_condition_ko":"정규장에서 195.49 초과 유지, 거래량가중평균가격 상회 및 동시간대 상대거래량 1.2 이상 / 196.34 위 종가 후 다음 거래일 초반 195.49 유지","risk_condition_ko":"190.12 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":498.8399963378906,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":497.6760796843775,"relative_volume":0.9259601254798294,"spread_bps":null,"day_high":499.75,"day_low":495.9599914550781,"execution_condition_ko":"최신 정규장 가격의 500.23 및 502.35 회복, 실시간 거래량가중평균가격 지지, 동시간대 상대거래량 1.2 이상 / 거래량을 동반한 506.76 위 종가와 다음 거래일 유지; 이후 저항선 509.05","risk_condition_ko":"497.83 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":260.6,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":260.54740970671884,"relative_volume":0.2874996589392729,"spread_bps":7.660193802902778,"day_high":262.3158,"day_low":259.0,"execution_condition_ko":"ABBV가 269.39 위를 유지하고 시각 보정 상대 거래량 1.2 이상과 당일 거래량가중평균가격 상회를 충족하는지 확인 / ABBV가 270.78 위에서 마감한 뒤 다음 거래일 첫 30~60분 동안 269.39를 지키는지 확인","risk_condition_ko":"261.52 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":144.18,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":144.149681986646,"relative_volume":0.41630609572869226,"spread_bps":0.6935534209516181,"day_high":145.0,"day_low":143.51,"execution_condition_ko":"10:30 이후 149.57 상회 유지, 거래량가중평균가격 상회, 상대거래량 1.2 이상 / 149.57 위 일일 종가와 다음 거래일 첫 30~60분 지지 유지","risk_condition_ko":"145.87 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"WBD","display_name":"WBD","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":30.935,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":30.948567603504237,"relative_volume":2.1997495192864727,"spread_bps":3.231539828727746,"day_high":30.96,"day_low":30.93,"execution_condition_ko":"30.92달러 위 종가, 시간대별 상대 거래량 1.2 이상, 다음 거래일 지지 확인 / 30.90~30.92달러에서 반복적인 거부","risk_condition_ko":"30.9 이상 도달, 장중 확인 시 (실시간 가격 확인) 이익실현성 축소 · 추가 조건 확인 필요: 30.90~30.92달러 저항 재시험에서 거부가 확인되거나 보유 비중이 높을 때","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":163.615,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":163.10225724081786,"relative_volume":0.3303051381312368,"spread_bps":4.27546190258013,"day_high":163.78,"day_low":160.84,"execution_condition_ko":"신선한 정규장 가격이 163.32와 당일 거래량가중평균가격 위에서 유지되고 상대거래량 1.2 이상 / 164.91 상향 종가 후 다음 확인된 거래일 첫 30~60분간 164.91 유지 또는 회복; 저항 168.12와 169.64 대비 보상·위험 재평가","risk_condition_ko":"159.27 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":206.35,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":205.68253093841574,"relative_volume":0.3789799886303238,"spread_bps":3.391719359449242,"day_high":206.59,"day_low":202.915,"execution_condition_ko":"200.78~201.17 지지 후 202.70 회복과 실시간 거래량가중평균가격·상대 거래량 확인 / 205.48 및 206.43 회복","risk_condition_ko":"200.78 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":95.33,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":95.0477931729686,"relative_volume":1.4051946532399757,"spread_bps":1.0488226965221987,"day_high":95.44,"day_low":94.34,"execution_condition_ko":"$95.36 및 $95.78 회복 여부 / 10:30 이후 $96.47 돌파와 실시간 거래량가중평균가 지지 및 상대 거래량 1.2 이상","risk_condition_ko":"94.72 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"SPYM","display_name":"SPYM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":89.565,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":89.73740763752808,"relative_volume":0.612860487048461,"spread_bps":1.1182555213872087,"day_high":90.0799,"day_low":89.31,"execution_condition_ko":"미국 동부시간 10:30 이후 90.15와 90.41 위 유지, 거래량가중평균가격 상회, 상대 거래량 1.2 이상 / 90.89와 91.22 위 마감 및 91.31 저항 반응","risk_condition_ko":"89.55 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MRK","display_name":"MRK","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":144.96,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":144.63147846465407,"relative_volume":0.3495398770463946,"spread_bps":2.7567195037899404,"day_high":145.388,"day_low":144.0,"execution_condition_ko":"2026-10-02 16:00 미국 동부시간까지 147.07 부근 재시험, 147.25 이하, 10:30 이후 당일 거래량가중평균가격 유지와 동시간대 상대거래량 1.2 이상 / 150.36 회복 후 152.64 위 종가와 약 1,165만 주 이상 거래량","risk_condition_ko":"146.09 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"INTC","display_name":"INTC","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":119.39,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":119.07489441109577,"relative_volume":0.7712116301666933,"spread_bps":0.8426374552353162,"day_high":120.23,"day_low":117.36,"execution_condition_ko":"113.97~114.71 지지 유지와 115.87 재돌파 / 118.75 회복 후 121.71 상회, 실시간 거래량가중평균가격 지지 및 동시간대 상대거래량 1.2 이상","risk_condition_ko":"112.27 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":546.57,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":551.5409506377558,"relative_volume":0.3778716171421769,"spread_bps":4.197424971028974,"day_high":557.165,"day_low":546.57,"execution_condition_ko":"실시간 $553.12~$553.84 지지 확인 후 $561.30 및 거래량가중평균가격 회복 / 상대거래량 1.2 이상을 동반한 $565.85, 이어서 $569.64 상향 종가","risk_condition_ko":"553.12 이하 하락, 종가 확인 후 (거래량 증가 확인) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MRVL","display_name":"Marvell Technology","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":266.66,"market_data_asof":"2026-10-01T11:25:00-04:00","session_vwap":262.96378111770605,"relative_volume":0.5551504531971683,"spread_bps":12.887086381381,"day_high":266.94,"day_low":257.58,"execution_condition_ko":"9월 30일 10:30 이후 267.48 위 5분봉 2개, 당일 거래량 가중 평균가격 지지, 동시간대 상대 거래량 1.0 이상 확인 / 267.48 위 정규장 종가와 거래량 18.16백만 주 초과 후 다음 거래일 초반 지지 또는 재돌파 확인","risk_condition_ko":"256.88 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-01T11:55:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-01T23:17:02.485827+09:00",
  "as_of": "2026-09-30T15:10:00-04:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
