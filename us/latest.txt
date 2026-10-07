# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-07T14:06:35.480850+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261007T230122_github-actions-overlay-us-37632909674-1",
  "producer_finished_at": "2026-10-07T23:04:05.816440+09:00",
  "analysis_run_id": "20261007T185750_github-actions-us",
  "analysis_completed_at": "2026-10-07T20:58:44.746731+09:00",
  "analysis_trade_date_oldest": "2026-10-06",
  "analysis_trade_date_latest": "2026-10-06",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-07T10:00:00-04:00",
  "market_data_latest_at": "2026-10-07T10:00:00-04:00",
  "market_data_status": "FRESH"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-07T23:04:03.061998+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-07T23:04:03.061998+09:00",
    "run_started_at": "2026-10-07T23:01:22.838848+09:00",
    "run_finished_at": "2026-10-07T23:04:05.816440+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23706483,
    "total_market_value_krw": 25264234,
    "total_unrealized_pnl_krw": 1557751,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 91404,
    "total_equity_krw": 26332370
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 547663,
      "current_price_krw": 635240,
      "market_value_krw": 7622881,
      "unrealized_pnl_krw": 1050915
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 293540,
      "current_price_krw": 283027,
      "market_value_krw": 3113302,
      "unrealized_pnl_krw": -115639
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 425762,
      "current_price_krw": 464655,
      "market_value_krw": 2787931,
      "unrealized_pnl_krw": 233358
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 268258,
      "current_price_krw": 320588,
      "market_value_krw": 1923533,
      "unrealized_pnl_krw": 313980
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1887127,
      "current_price_krw": 1911322,
      "market_value_krw": 1911322,
      "unrealized_pnl_krw": 24195
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 558045,
      "current_price_krw": 573134,
      "market_value_krw": 1719404,
      "unrealized_pnl_krw": 45269
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1478465,
      "current_price_krw": 1327695,
      "market_value_krw": 1327695,
      "unrealized_pnl_krw": -150770
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 135027,
      "current_price_krw": 134970,
      "market_value_krw": 1214736,
      "unrealized_pnl_krw": -508
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 365960,
      "current_price_krw": 450428,
      "market_value_krw": 900857,
      "unrealized_pnl_krw": 168937
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 665258,
      "current_price_krw": 773959,
      "market_value_krw": 773959,
      "unrealized_pnl_krw": 108701
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1425360,
      "current_price_krw": 1590515,
      "market_value_krw": 693567,
      "unrealized_pnl_krw": 72017
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 571784,
      "current_price_krw": 497340,
      "market_value_krw": 497340,
      "unrealized_pnl_krw": -74444
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 136729,
      "current_price_krw": 108808,
      "market_value_krw": 435235,
      "unrealized_pnl_krw": -111681
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 349069,
      "current_price_krw": 342472,
      "market_value_krw": 342472,
      "unrealized_pnl_krw": -6597
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":255.055,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":254.50338555385224,"relative_volume":1.2868832105193753,"spread_bps":1.5762925598988036,"day_high":255.65,"day_low":253.17,"execution_condition_ko":"검증된 정규장 10:30 미국 동부시간 이후 259.49 위 유지, 실시간 거래량가중평균가격 지지, 동일 시간대 상대거래량 1.2 이상이면 작은 시험 매수 재평가 / 정규장 종가가 259.49 위에서 확인되면 증액 가능성 재평가","risk_condition_ko":"251.08 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":473.565,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":473.05270473179144,"relative_volume":0.7561327637238711,"spread_bps":1.2707287629455974,"day_high":474.6055,"day_low":471.3,"execution_condition_ko":"정규장에서 487.47달러 회복·유지, 실시간 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상 / 477.72~476.40달러 지지 구간의 반응과 실패 시 463.69달러","risk_condition_ko":"476.4 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":426.105,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":430.15573073370587,"relative_volume":0.6475269595885538,"spread_bps":19.501323304082085,"day_high":439.5052,"day_low":425.73,"execution_condition_ko":"446.73~447.33달러 저항대 재시험 / 452.00달러 위 종가의 거래량 확인과 다음 실제 거래일 유지·재돌파","risk_condition_ko":"431.52 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":985.75,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":997.9589950817734,"relative_volume":0.9329377561113265,"spread_bps":32.63895555342248,"day_high":1014.95,"day_low":983.57,"execution_condition_ko":"2026-10-07 정규장 운영 여부와 최신 호가·거래정지·발표 시각 확인 / 10:30 미국 동부 시각 이후 1052.78 위 5분봉 두 개, 정규장 거래량가중평균가격 위 가격, 상대 거래량 1.2 이상 동시 확인","risk_condition_ko":"995.05 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1428.1,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":1432.5229556875286,"relative_volume":0.33493454113710386,"spread_bps":39.820072266057586,"day_high":1450.705,"day_low":1412.68,"execution_condition_ko":"실제 정규장 운영·거래 중단 여부와 최신 가격·거래량 확인 / 1491.64달러 위 돌파, 상대거래량 1.2 이상 및 당일 거래량가중평균가격 상회 확인","risk_condition_ko":"1,432.38 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":210.61,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":211.17668029844222,"relative_volume":1.1235938450658915,"spread_bps":0.4736979228355238,"day_high":211.68,"day_low":210.5504,"execution_condition_ko":"RSP의 $212.93 회복, $215.03 시험, $215.94 접근을 차례로 관찰 / 신선한 정규장 자료에서 $215.94 위 유지, 상대거래량 1.2 이상 및 시장 폭 개선 확인","risk_condition_ko":"208.02 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":370.64,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":371.63739050569023,"relative_volume":1.2458437246462146,"spread_bps":2.7002214181553676,"day_high":374.34,"day_low":369.12,"execution_condition_ko":"정규장 일정, 신선한 가격, 실시간 거래량가중평균가격 및 거래 비용 확인 / 372.16~373.33 재시험 뒤 지지 확인","risk_condition_ko":"372.16 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1184.025,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":1178.645412241976,"relative_volume":0.8347586184493654,"spread_bps":10.5827720936533,"day_high":1186.9999,"day_low":1166.0,"execution_condition_ko":"정규장과 실시간 자료 확인 후 1174.49~1177.07 회복 여부 점검 / 1197.79 위 종가와 약 223만 주 이상의 거래량, 다음 거래일 지지 여부 점검","risk_condition_ko":"1,136 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":81.11,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":80.94754838290687,"relative_volume":1.2335043243606796,"spread_bps":1.2351015871061712,"day_high":81.11,"day_low":80.745,"execution_condition_ko":"GLDM이 83.03을 회복한 뒤 83.57과 장중 거래량가중평균가 위를 동시간대 상대 거래량 1.2 이상으로 유지하는지 확인 / GLDM의 85.55 위 종가와 다음 거래일 추종 여부를 확인하고 순손익비를 다시 계산","risk_condition_ko":"81.32 이하 하락, 종가 확인 후 (정규장에서 증가한 거래량으로 이탈 확인) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":100.465,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":100.46586271927946,"relative_volume":2.0219573683450793,"spread_bps":0.9953715224212527,"day_high":100.47,"day_low":100.46,"execution_condition_ko":"검증된 정규장에서 100.47 위 거래와 시간대에 적절한 거래량을 확인하되 가격만으로 매수하지 않음 / 분배금 조정 후 100.45 아래 약세 지속 여부를 순자산가치와 함께 확인","risk_condition_ko":"100.45 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":238.69,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":237.94544465417815,"relative_volume":1.0153246264275284,"spread_bps":0.8401949252230815,"day_high":238.9,"day_low":237.06,"execution_condition_ko":"정규장 상태와 최신 NVDA 호가 확인 후 243.37 돌파 및 유지 여부 점검 / 243.37 위 종가 확인과 다음 검증된 거래일의 지지 또는 재돌파 확인","risk_condition_ko":"238.5 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":334.815,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":335.45206477372045,"relative_volume":1.241790894425487,"spread_bps":3.279128348064976,"day_high":338.67,"day_low":332.79,"execution_condition_ko":"정규장 여부, 최신 AAPL 가격, 장중 거래량가중평균가격 및 상대 거래량 확인 / 10:30 이후 339.50 상회 유지, 장중 거래량가중평균가격 지지 및 상대 거래량 1.2 이상이면 소액 시범 진입 검토","risk_condition_ko":"330.62 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":345.77,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":345.3832564569052,"relative_volume":1.0110434039433474,"spread_bps":2.9048656499643495,"day_high":347.25,"day_low":343.0658,"execution_condition_ko":"GOOGL의 정규장 일정·거래 가능 여부·실시간 호가·거래량 확인 / 349.09 회복 후 352.60~353.22 돌파·유지와 시간조정 상대거래량 1.2 이상 확인","risk_condition_ko":"344.25 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":576.92,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":574.5470423161248,"relative_volume":0.8560146034067454,"spread_bps":15.987210231813837,"day_high":580.9786,"day_low":560.76,"execution_condition_ko":"2026-10-07 정규장 일정·개장 상태·최신 호가·당일 거래량가중평균가격·같은 시각 기준 상대거래량 확인 / 589.18 저항과 595.51 위 거래량 동반 종가 관찰","risk_condition_ko":"553.42 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"SPYM","display_name":"SPYM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":91.15,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":91.2554982627576,"relative_volume":0.6532145242797874,"spread_bps":1.0970325270134282,"day_high":91.345,"day_low":91.105,"execution_condition_ko":"92.00 돌파와 동시간대 상대거래량 1.2 이상 / 91.40 지지 재시험 후 반등","risk_condition_ko":"90.59 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"NTAP","display_name":"NetApp","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":233.095,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":233.37406231272087,"relative_volume":1.3782994993687483,"spread_bps":50.39302250457575,"day_high":235.65,"day_low":230.83,"execution_condition_ko":"NTAP의 당일 정규장 일정과 최신 시세를 확인한다. / 10:30 이후 231.90 유지, 거래량가중평균가격 상회, 동시간대 상대거래량 1.2배 이상일 때에만 소규모 시범 매수를 검토한다.","risk_condition_ko":"223.95 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"CDNS","display_name":"Cadence Design Systems","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":355.635,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":358.97537571649565,"relative_volume":0.6827388494291617,"spread_bps":24.841946603770573,"day_high":361.42,"day_low":355.39,"execution_condition_ko":"2026-10-07의 실제 거래 일정과 실시간 CDNS 가격·호가 차이·거래량가중평균가격·동시간대 상대거래량을 확인 / 361.91 또는 367.89에서 거부 신호, 352.00~350.73 아래 종가 및 336.67 이탈을 감시","risk_condition_ko":"361.91 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":271.6068,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":270.95209925966304,"relative_volume":0.46002410251269116,"spread_bps":19.91884913316195,"day_high":272.04,"day_low":266.89,"execution_condition_ko":"정규장 270.44 위 안착, 거래량가중평균가격 지지, 동시간대 상대 거래량 1.2 이상 / 270.44 위 종가 후 다음 확인된 거래일 첫 30~60분 동안 해당 수준 지지 또는 재돌파","risk_condition_ko":"263.91 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"LIN","display_name":"LIN","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":485.08,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":488.0758029600635,"relative_volume":1.0930450978443744,"spread_bps":15.009303712232954,"day_high":490.25,"day_low":484.6534,"execution_condition_ko":"정규장 일정과 신선한 LIN 호가, 당일 거래량 가중 평균가 및 동시간대 상대 거래량 확인 / 492.10~493.11 유지 또는 거부와 497.54·500 저항 확인","risk_condition_ko":"482.69 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"CAT","display_name":"CAT","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":820.225,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":832.61022822398,"relative_volume":1.6226000092047823,"spread_bps":12.0815261383818,"day_high":845.0,"day_low":819.11,"execution_condition_ko":"2026-10-07 정규장 여부와 CAT 실시간 시세·장중 거래량가중평균가격·동시간대 상대거래량 확인 / 876.95 돌파 유지와 종가 확인 여부","risk_condition_ko":"845.42 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":206.93,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":208.18625203091545,"relative_volume":0.5745333597435147,"spread_bps":5.2964826540199645,"day_high":210.1,"day_low":206.685,"execution_condition_ko":"208.69~209.00 저항대의 정규장 돌파·유지와 당시 거래량가중평균가격·동시간대 상대거래량 확인 / 206.56 및 205.00~204.89 지지 반응","risk_condition_ko":"204.89 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"URI","display_name":"United Rentals","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1048.93,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":1063.5108239637523,"relative_volume":0.2824943795767104,"spread_bps":26.085895787784413,"day_high":1070.955,"day_low":1047.92,"execution_condition_ko":"실제 정규장 개장 여부와 1101.41 상향 거래, 실시간 거래량가중평균가격·호가·동시간대 거래량 확인 / 1101.41 초과 종가와 약 493000주 이상 거래량 확인","risk_condition_ko":"1,062.16 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":97.12,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":97.56288487150071,"relative_volume":1.058864035009492,"spread_bps":2.052966536646503,"day_high":98.06,"day_low":97.05,"execution_condition_ko":"SHEL이 96.05~96.10에 접근해 실시간 정규장 가격으로 지지와 반등을 보이는지 확인 / 98.27 회복 후 99.15 상향 돌파·유지, 상대거래량 1.2 이상 및 당일 거래량가중평균가격 상회 확인","risk_condition_ko":"96.05 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":165.16,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":165.81655831396458,"relative_volume":0.4448000300436555,"spread_bps":12.081672103418427,"day_high":166.85,"day_low":165.06,"execution_condition_ko":"개장 후 실제 정규장 상태, 거래 중단 여부, 최신 시세·호가·거래량을 확인 / 166.00 위 유지 시 168.17과 169.64에서 순보상 대비 위험을 다시 계산","risk_condition_ko":"163.19 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"NU","display_name":"NU","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":15.575,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":15.596896974680199,"relative_volume":0.6228196384467061,"spread_bps":6.420545746388306,"day_high":15.69,"day_low":15.52,"execution_condition_ko":"정규장 개장과 시세 신선도를 확인한 뒤 10:30 뉴욕 현지 시각 이후 15.74달러, 정규장 거래량가중평균가격, 동일 시점 대비 상대 거래량을 점검 / 다음 확인된 거래일 초반 30~60분 동안 15.74달러 유지 또는 재돌파 여부 점검","risk_condition_ko":"15.33 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":149.06,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":148.8663399531524,"relative_volume":3.290037328117568,"spread_bps":6.017852963792812,"day_high":149.665,"day_low":148.19,"execution_condition_ko":"PG 정규장 운영 여부와 신선한 호가·실시간 거래량가중평균가격·동시간대 상대거래량 확인 / 검증된 정규장에서 PG의 5분봉 2개가 149.70 위로 마감하고 동시간대 상대거래량이 1.2 이상인지 확인","risk_condition_ko":"145.7 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":191.72,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":191.73884749148894,"relative_volume":0.7275253622913368,"spread_bps":26.617259466090097,"day_high":192.63,"day_low":190.385,"execution_condition_ko":"188.29~189.17달러 지지 유지 여부 / 192.05달러 직전 고점 재돌파 여부","risk_condition_ko":"188.29 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"CEG","display_name":"CEG","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":292.61,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":291.2469028352255,"relative_volume":5.374529414908495,"spread_bps":13.401831583649297,"day_high":295.1799,"day_low":286.4,"execution_condition_ko":"검증된 정규장에서 300.40과 당일 거래량가중평균가격 위 두 개 봉 및 시간대별 상대 거래량 1.2 이상 / 상대 거래량 1.2 이상을 동반한 정규장 종가 309.80 초과와 다음 거래일 유지","risk_condition_ko":"300.4 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"META","display_name":"Meta Platforms","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":722.41,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":728.1302255206375,"relative_volume":0.9002847794669545,"spread_bps":2.347434047459028,"day_high":738.0,"day_low":721.9,"execution_condition_ko":"정규장 일정·시세 최신성·거래량가중평균가격·동일 시각 상대 거래량·기존 편입 비중 확인 / 747.60 돌파와 757.27·763.90·779.82 저항에서 비용 반영 손익비 재계산","risk_condition_ko":"728.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"SMCI","display_name":"Super Micro Computer","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":44.025,"market_data_asof":"2026-10-07T10:00:00-04:00","session_vwap":43.628302258996506,"relative_volume":1.550826365114782,"spread_bps":4.563084645220882,"day_high":44.37,"day_low":42.46,"execution_condition_ko":"SMCI의 거래 상태, 거래일 일정 및 실시간 정규장 가격·거래량 확인 / 44.74 저항과 45.25 위 거래량 동반 종가 확인","risk_condition_ko":"42.28 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-07T10:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
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
