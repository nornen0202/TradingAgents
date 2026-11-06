# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-06T16:47:23.709090+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261107T000227_local-scheduler-us-overlay_only",
  "producer_finished_at": "2026-11-07T00:13:15.900500+09:00",
  "analysis_run_id": "20261106T175128_local-scheduler-us-full",
  "analysis_completed_at": "2026-11-06T20:56:54.446013+09:00",
  "analysis_trade_date_oldest": "2026-11-05",
  "analysis_trade_date_latest": "2026-11-05",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-06T15:11:43+00:00",
  "market_data_latest_at": "2026-11-06T15:11:43+00:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-07T00:13:08.969539+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-07T00:13:08.969539+09:00",
    "run_started_at": "2026-11-07T00:02:27.779433+09:00",
    "run_finished_at": "2026-11-07T00:13:15.900500+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23681783,
    "total_market_value_krw": 21729053,
    "total_unrealized_pnl_krw": -1952730,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 112218,
    "total_equity_krw": 22817742
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 547093,
      "current_price_krw": 503437,
      "market_value_krw": 6041254,
      "unrealized_pnl_krw": -523863
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 293234,
      "current_price_krw": 290865,
      "market_value_krw": 3199515,
      "unrealized_pnl_krw": -26061
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 425318,
      "current_price_krw": 387502,
      "market_value_krw": 2325015,
      "unrealized_pnl_krw": -226895
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1885161,
      "current_price_krw": 1606810,
      "market_value_krw": 1606810,
      "unrealized_pnl_krw": -278351
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 267979,
      "current_price_krw": 257731,
      "market_value_krw": 1546386,
      "unrealized_pnl_krw": -61490
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 557463,
      "current_price_krw": 455850,
      "market_value_krw": 1367551,
      "unrealized_pnl_krw": -304839
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 134886,
      "current_price_krw": 134844,
      "market_value_krw": 1213597,
      "unrealized_pnl_krw": -381
    },
    {
      "ticker": "GEV",
      "name": "GE버노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1476924,
      "current_price_krw": 1062266,
      "market_value_krw": 1062266,
      "unrealized_pnl_krw": -414658
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 365579,
      "current_price_krw": 460990,
      "market_value_krw": 921981,
      "unrealized_pnl_krw": 190823
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1423877,
      "current_price_krw": 1834312,
      "market_value_krw": 799879,
      "unrealized_pnl_krw": 178976
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 664565,
      "current_price_krw": 455635,
      "market_value_krw": 455635,
      "unrealized_pnl_krw": -208930
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 136586,
      "current_price_krw": 107621,
      "market_value_krw": 430486,
      "unrealized_pnl_krw": -115860
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 571188,
      "current_price_krw": 405746,
      "market_value_krw": 405746,
      "unrealized_pnl_krw": -165442
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 348705,
      "current_price_krw": 352932,
      "market_value_krw": 352932,
      "unrealized_pnl_krw": 4227
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":342.525,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":340.80292639526976,"relative_volume":1.129866182215303,"spread_bps":2.919537545251836,"day_high":343.6,"day_low":338.3,"execution_condition_ko":"342.06–343.70은 첫 지지 관찰 구간일 뿐 이 구간 유지로 매수하지 않는다. / 334.35–335.82 시험, 335.82 이상 종가 회복, 다음 정규장 지지 유지와 구간 내 실행 가능성을 확인한다. 확인 뒤 가격이 구간 위라면 추격하지 않는다.","risk_condition_ko":"334.35 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":80.19,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":80.00692066617731,"relative_volume":1.0697842356416323,"spread_bps":1.2469605336997467,"day_high":80.2,"day_low":79.69,"execution_condition_ko":"향후 1주일간 일별로 검토하며 조건부 첫 매수 허가는 2026-11-13T16:00:00-05:00에 종료한다. 이 시각은 제공된 현재 시각보다 미래이며 거래소 폐장시각을 검증한 것은 아니다. 자동 연장하지 않는다. / 첫 발동에는 이번 판단 시각 이후의 적격 정규장 종가와 후속 확인 거래일의 지지 재시험이 모두 필요하다. 현재 어느 조건도 충족된 것으로 확인되지 않았으며 실제 거래 일정도 확인해야 한다.","risk_condition_ko":"79.57 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.48,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":100.48561908306286,"relative_volume":2.211133175867757,"spread_bps":0.9951734089656072,"day_high":100.49,"day_low":100.48,"execution_condition_ko":"필수 자료와 경제성 검증 후 새 100.42~100.45 시험 및 종가 100.45 이상 회복: 다음 실제 거래일 첫 분할 검토. / 종가 100.50 초과와 다음 실제 거래일 100.49~100.50 재시험 유지: 가격대 의미와 순수익 이점을 재검증한 경우에만 대체 첫 분할 검토.","risk_condition_ko":"100.42 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":262.81,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":261.54785074665676,"relative_volume":1.2238744199061657,"spread_bps":2.28284442415258,"day_high":263.55,"day_low":258.53,"execution_condition_ko":"향후 실제 확인된 2~3거래일의 종가와 지지를 점검하고 늦어도 2026-11-13에 재평가한다. 조건 충족 전에는 활성화하지 않으며 만료·취소 후 자동 연장하거나 부활시키지 않는다. / 초기 진입 전 기본 공시·실제 거래비용·계좌 여력을 확인한다. 추가 증액에는 부문별 수익성과 투자 회수 검증을 더 요구한다.","risk_condition_ko":"252.27 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":374.6,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":377.8774584570173,"relative_volume":2.45627880799567,"spread_bps":10.678056593700857,"day_high":380.72,"day_low":373.395,"execution_condition_ko":"351.19~353.10 방어 구간의 일봉 종가 유지 또는 이탈을 확인한다. / 380.78 위 종가 회복 후 다음 확인된 거래일에도 지지가 유지되는지 점검한다. 단독 매수 신호는 아니다.","risk_condition_ko":"351.19 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":338.7824,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":340.5560645530724,"relative_volume":1.0940546153380593,"spread_bps":17.408494755321396,"day_high":347.5,"day_low":337.07,"execution_condition_ko":"324.27 주변 일봉 종가와 저점 상승 여부를 확인한다. 장전 반등만으로 지지를 인정하지 않는다. / 종가 350.05 초과 회복 후 다음 확인된 정규장에서 346.46–350.05의 종가 지지를 점검한다.","risk_condition_ko":"324.27 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":288.47,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":286.31510483676345,"relative_volume":1.666085813428933,"spread_bps":1.386337642533548,"day_high":290.49,"day_low":284.78,"execution_condition_ko":"288.33–288.93 회복은 초기 개선으로만 관찰하며 매수 신호로 취급하지 않는다. / 295.60–296.82 저항 회복과 299.75–300.00 지지 전환을 순서대로 확인한다. 316.60–320.21은 이후의 조건부 저항이지 기대수익이나 가치평가 목표가가 아니다.","risk_condition_ko":"276.92 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1196.02,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":1190.375449604575,"relative_volume":1.5517903753091595,"spread_bps":38.259486385231476,"day_high":1208.66,"day_low":1153.34,"execution_condition_ko":"MPWR 1125~1135 지지 유지와 1125 미만 일봉 종가 여부를 확인한다. 현재 지지 붕괴로 분류하지 않는다. / MPWR 1168 회복은 초기 개선 관찰 신호일 뿐 매수 승인이 아니다.","risk_condition_ko":"1,125 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":789.86,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":802.2360186204529,"relative_volume":2.4891052266534786,"spread_bps":25.954459419252565,"day_high":821.5031,"day_low":785.6675,"execution_condition_ko":"821.54 초과 종가와 다음 확인된 정규장의 지지 유지를 관찰한다. 이는 재검토 신호이지 자동 매수 신호가 아니다. / 832.83과 갱신된 857.50~857.64 저항을 확인하고 실제 진입가 기준 손익비를 다시 계산한다. 향후 별도 설정의 손절 구조는 새 근거로 정하되 기존 손절을 넓히지 않는다.","risk_condition_ko":"795.95 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":216.6,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":215.6063122230806,"relative_volume":1.3715400757272247,"spread_bps":0.46164854696077856,"day_high":216.79,"day_low":214.75,"execution_condition_ko":"214.63–216.24 안정화 후 216.24 위 종가와 다음 거래일 지지를 관찰한다. 확인되지 않은 하락 매수는 하지 않는다. / 218.55 위 종가 이후 지지 유지와 220.04–220.95 저항을 반영한 비용 차감 후 보상·위험비를 다시 계산한다. 감축 권고 해제 전에는 매수하지 않는다.","risk_condition_ko":"218.55 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":338.39,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":342.48678140895316,"relative_volume":2.2019335776806095,"spread_bps":20.11596260797559,"day_high":350.35,"day_low":336.0,"execution_condition_ko":"315.00 아래 마감 후 다음 거래일 회복 실패를 감시한다. 위험축소에 매수용 거래량 조건을 붙이지 않는다. / 335.59의 최신 기준값 회복, 315.00보다 높은 저점과 다음 거래일 지지는 재조사 신호다.","risk_condition_ko":"335.59 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":302.03,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":306.0590694452469,"relative_volume":2.0202937752456482,"spread_bps":4.303139636881066,"day_high":311.52,"day_low":301.02,"execution_condition_ko":"2026-11-13까지 확인 가능한 정규장 종가를 검토한 뒤 계획을 갱신한다. 이는 약 1주의 검토기한이며 주문 만료나 특정 거래일 일정의 확인이 아니다. / 288.98–290.12에서 저점이 높아지는지 관찰하되 확정된 바닥으로 간주하지 않는다.","risk_condition_ko":"319.3 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":191.86,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":192.00747196030815,"relative_volume":2.9579325863493677,"spread_bps":1.563599405832285,"day_high":194.895,"day_low":190.0,"execution_condition_ko":"2026-11-05 저가 181.46과 종가 181.60의 관측 구간을 추적한다. 아직 검증된 바닥으로 간주하지 않는다. / 189.91은 지연된 장전 고가에 근거한 초기 회복 참고값일 뿐 정규장 돌파나 매수 신호가 아니다.","risk_condition_ko":"181.46 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1367.53,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":1363.2744699680409,"relative_volume":1.1098577679891075,"spread_bps":10.825043885313182,"day_high":1377.2771,"day_low":1333.22,"execution_condition_ko":"1364.73 초과 종가 이후 다음 거래일 1352.62–1357.80 지지를 확인하면 관찰을 재개한다. 1382.02와 1408–1418 저항까지의 비용 반영 보상비를 다시 계산한다. / 1408–1418 위 안착은 회복 근거를 강화하고 해당 구간에서 재차 밀리면 신규 진입 대기를 유지한다.","risk_condition_ko":"1,330 이하 하락, 종가 확인 후 (위험 축소에 매수세 거래량 확인은 불필요) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":287.51,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":286.501690349973,"relative_volume":0.5304503377061383,"spread_bps":7.303966749560181,"day_high":288.71,"day_low":281.07,"execution_condition_ko":"위험 대응 조건: 283.32 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"283.32 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SO","display_name":"SO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":92.3625,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":91.74208187576818,"relative_volume":0.7002637180295043,"spread_bps":7.580269641019349,"day_high":92.41,"day_low":91.09,"execution_condition_ko":"위험 대응 조건: 91.28 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"91.28 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"KO","display_name":"KO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":95.26,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":94.1745889395576,"relative_volume":1.0724256425513115,"spread_bps":4.198152812761549,"day_high":95.325,"day_low":93.0,"execution_condition_ko":"새 일봉 종가 94.36 상회 후 후속 확인된 정규장에서 93.91 지지와 반등을 관찰한다. 93.91–94.10 체결범위와 비용 후 2배 조건을 함께 적용한다. / 95.73–96.56 매물대의 실제 저항 강도를 재평가한다. 이 구간이 청산 상한이면 기존 시험 매수안은 부적격이다.","risk_condition_ko":"92.55 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MSFT","display_name":"Microsoft","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":532.925,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":529.6827462418014,"relative_volume":1.2488226727813085,"spread_bps":4.879421976165729,"day_high":532.97,"day_low":524.612,"execution_condition_ko":"2026-11-06–2026-11-13 검토 기간에 새로운 회복 종가, 후속 거래일 재시험, 그다음 거래일의 적격 지정가 체결 가능성을 순서대로 확인한다. 2026-11-05 종가만으로 최신 약세 이후의 회복을 인정하지 않는다. / 첫 저항 541.29–543.45 통과 가능성과 비용·갭 반영 보상위험비를 재심사한다. 적격 가격이 없으면 추격하지 않는다.","risk_condition_ko":"520.99 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":652.235,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":650.756141341121,"relative_volume":0.7382176811613527,"spread_bps":13.341409742296173,"day_high":653.6,"day_low":639.04,"execution_condition_ko":"2026-11-13까지 확인 가능한 거래일마다 지지 시험→641.68 종가 회복→다음 거래일 재시험의 순서를 점검한다. 구간을 떠난 가격은 추격하지 않는다. / 653.85~655.92 회복, 672.68~673.50 및 680.01~681.99 공급을 관찰한다. 첫 저항에서는 잔여 보상 대비 위험을 재평가하되 자동 익절이나 추가 매수로 해석하지 않는다.","risk_condition_ko":"634.76 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WELL","display_name":"WELL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":244.855,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":244.2231272315298,"relative_volume":0.34928086937026087,"spread_bps":15.51083717702745,"day_high":245.6252,"day_low":241.19,"execution_condition_ko":"244.12 미만 종가는 초기 경고다. 재평가하되 자동 매도 신호로 취급하지 않는다. / 239–241 지지 시험과 241 이상 회복 종가를 관찰한다. 다음 거래일 실제 신규 매수 범위는 239–240으로 더 좁게 제한한다.","risk_condition_ko":"233.68 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WMT","display_name":"WMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":125.25,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":124.37655227846982,"relative_volume":1.5286829230484176,"spread_bps":3.9918566125102517,"day_high":125.56,"day_low":123.04,"execution_condition_ko":"123–125 시험 이후 124.55 이상 종가와 바로 다음 확인된 거래일의 124.10–124.55 재시험을 추적한다. / 재시험을 놓치면 추격하지 않고 새 확인 순서를 요구한다. 매수 후 2–3개 확인된 거래일 동안 지지와 반등 지속성을 점검한다.","risk_condition_ko":"122.4 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1057.47,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":1049.8588113233188,"relative_volume":1.4790636363000471,"spread_bps":5.391065019080932,"day_high":1057.857,"day_low":1043.0,"execution_condition_ko":"2026-11-05 종가는 방향 판단의 기준일 뿐 새로운 진입 확인 조건의 충족이 아니다. 새 종가와 그 다음 검증된 거래일의 지지를 확인한다. / 1040.55~1046.47 및 1017.44~1022.25 도달은 관찰 신호이며 저가 매수 허가가 아니다. 평균선 수치는 갱신하되 기존 손절을 완화하지 않는다.","risk_condition_ko":"1,061 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SPG","display_name":"Simon Property Group","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":227.83,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":226.35971737059384,"relative_volume":0.5021964574931895,"spread_bps":14.910318817698329,"day_high":228.0,"day_low":222.7,"execution_condition_ko":"SPG의 224.61~225.29 지지와 228.50 회복 여부를 최신 완료 일봉으로 점검한다. 지연 소량 체결로 지지 붕괴를 확정하지 않는다. / SPG의 관찰 구간 시험, 종가 222.08 이상 회복, 다음 실제 거래일 219.05~220.00 재시험 및 종가 지지의 순서를 확인한다. 이후 주문 직전 새로운 약화가 나타나면 체결을 보류한다.","risk_condition_ko":"219.05 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":165.76,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":164.0742306884211,"relative_volume":0.48666583984974715,"spread_bps":7.84006272050149,"day_high":165.92,"day_low":162.13,"execution_condition_ko":"주문 전 실제 거래일·정규장 운영·거래정지 여부·최신 정규장 호가와 체결비용을 확인한다. 제공된 실행시각만으로 정상 거래나 진입 조건 충족을 확정하지 않는다. / 새 종가 165.75 이상 확인 후 다음 실제 정규장에서 164.50~164.80 재시험과 반등을 관찰한다. 단순한 가격대 접촉은 지지 확인이 아니다.","risk_condition_ko":"161.99 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LIN","display_name":"LIN","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":519.69,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":514.4072643648317,"relative_volume":0.9345859093212221,"spread_bps":10.204376329697098,"day_high":519.69,"day_low":510.01,"execution_condition_ko":"향후 며칠간 완성된 일봉에서 지지 하단 511.26, 상단 513.30과 회복 기준 517.17을 순서대로 확인한다. 다음 확인된 거래일의 재시험에서 지지 유지가 입증되지 않으면 매수하지 않는다. / 첫 저항 524.74–526.56과 공급구간 531.36–533.39를 우선 관찰한다. 545.42–546.40은 중간 저항을 넘어야 의미가 있는 상단 참고값이다.","risk_condition_ko":"511.26 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":419.3,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":418.47546164559503,"relative_volume":0.8655939640603442,"spread_bps":13.593599084221887,"day_high":420.795,"day_low":413.0,"execution_condition_ko":"2026-11-06 이후 검증된 정규장 일봉의 414.03~416.80 시험과 416.80 이상 마감, 이어지는 실제 세션 재시험 지지를 확인한다. / 421.93~422.59 지지 전환과 425.51~426.78 재매도 압력을 점검한다. 회복만으로 추가매수를 승인하지 않는다.","risk_condition_ko":"414.03 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":200.025,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":197.44631383381633,"relative_volume":1.01383002943274,"spread_bps":16.503713335501114,"day_high":200.025,"day_low":193.62,"execution_condition_ko":"PM의 195.37–195.57 재시험, 195.57 이상 정규장 종가, 다음 확인된 정규장의 지지 유지와 195.57–196.00 체결 가능성을 순서대로 확인한다. / 203.31–205.32 회복과 211.06–211.28 저항을 관찰한다. 203.31에서는 보유 위험과 잔여 상승 여력을 재심사하며 자동 추가 매수하지 않는다.","risk_condition_ko":"195.37 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CLF","display_name":"CLF","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":11.85,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":11.722839292225279,"relative_volume":0.5655456227487767,"spread_bps":16.87763713080133,"day_high":11.91,"day_low":11.45,"execution_condition_ko":"실행 전 최신 완료 일봉, 체결 가능 시세, 장 운영과 거래 가능 여부를 확인한다. 2026-11-06 미국 동부시간 05:20의 지연 장전 시세나 제공된 판단 시각만으로 회복 조건 충족 또는 정규장 운영을 판단하지 않는다. / 11.61 상회 종가 이후 다음 확인된 거래일에 11.35–11.61이 지지되는지 관찰하고 투자 판단을 다시 내린다.","risk_condition_ko":"11.35 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":568.605,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":564.9063743100312,"relative_volume":0.9626401109955455,"spread_bps":3.5167926850700155,"day_high":568.85,"day_low":559.61,"execution_condition_ko":"위험 대응 조건: 579.09 이상 도달, 종가 확인 후 이익실현성 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"579.09 이상 도달, 종가 확인 후 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"UNH","display_name":"UNH","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":394.825,"market_data_asof":"2026-11-06T15:11:43+00:00","session_vwap":392.07824222087316,"relative_volume":0.9331765479480654,"spread_bps":8.104548677945324,"day_high":396.63,"day_low":388.0,"execution_condition_ko":"위험 대응 조건: 390.14 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"390.14 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-06T15:11:43+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-06T15:14:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-07T01:10:13.064550+09:00",
  "as_of": "2026-11-06T15:11:43+00:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
