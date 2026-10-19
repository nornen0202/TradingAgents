# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-19T15:03:29.791935+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261020T000011_local-scheduler-us-overlay_only",
  "producer_finished_at": "2026-10-20T00:02:13.177434+09:00",
  "analysis_run_id": "20261019T175010_local-scheduler-us-full",
  "analysis_completed_at": "2026-10-19T20:24:43.799959+09:00",
  "analysis_trade_date_oldest": "2026-10-16",
  "analysis_trade_date_latest": "2026-10-16",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-19T11:01:00-04:00",
  "market_data_latest_at": "2026-10-19T11:01:00-04:00",
  "market_data_status": "FRESH"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-19T23:47:00.667396+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-19T23:47:00.667396+09:00",
    "run_started_at": "2026-10-19T23:45:07.979479+09:00",
    "run_finished_at": "2026-10-19T23:47:07.594903+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23688834,
    "total_market_value_krw": 23730352,
    "total_unrealized_pnl_krw": 41518,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 107553,
    "total_equity_krw": 24814437
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 547256,
      "current_price_krw": 566680,
      "market_value_krw": 6800168,
      "unrealized_pnl_krw": 233094
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 293321,
      "current_price_krw": 286531,
      "market_value_krw": 3151842,
      "unrealized_pnl_krw": -74695
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 425445,
      "current_price_krw": 463745,
      "market_value_krw": 2782473,
      "unrealized_pnl_krw": 229802
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 268059,
      "current_price_krw": 292368,
      "market_value_krw": 1754208,
      "unrealized_pnl_krw": 145853
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1885722,
      "current_price_krw": 1681986,
      "market_value_krw": 1681986,
      "unrealized_pnl_krw": -203736
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 557629,
      "current_price_krw": 527704,
      "market_value_krw": 1583112,
      "unrealized_pnl_krw": -89777
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1477364,
      "current_price_krw": 1240350,
      "market_value_krw": 1240350,
      "unrealized_pnl_krw": -237014
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 134926,
      "current_price_krw": 135045,
      "market_value_krw": 1215408,
      "unrealized_pnl_krw": 1069
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 365687,
      "current_price_krw": 461919,
      "market_value_krw": 923839,
      "unrealized_pnl_krw": 192464
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1424301,
      "current_price_krw": 1672476,
      "market_value_krw": 729308,
      "unrealized_pnl_krw": 108220
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 664763,
      "current_price_krw": 624215,
      "market_value_krw": 624215,
      "unrealized_pnl_krw": -40548
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 571358,
      "current_price_krw": 452925,
      "market_value_krw": 452925,
      "unrealized_pnl_krw": -118433
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 136627,
      "current_price_krw": 110049,
      "market_value_krw": 440199,
      "unrealized_pnl_krw": -106309
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 348809,
      "current_price_krw": 350319,
      "market_value_krw": 350319,
      "unrealized_pnl_krw": 1510
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":213.525,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":213.7208217852687,"relative_volume":0.5936787403340035,"spread_bps":0.46865846514310044,"day_high":214.61,"day_low":213.225,"execution_condition_ko":"실제 정규장 일정·거래 상태·최신 호가·발행 시각을 확인한다. 조건부 주문은 시차가 포함된 유효기한과 포트폴리오 입력값을 기록한 뒤에만 활성화한다. / 212.80~213.40에서 단순 접촉이 아닌 지지 회복, 완료된 5분 봉 2개, 당일 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상을 관찰한다.","risk_condition_ko":"210.95 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":343.75,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":343.8775027050998,"relative_volume":0.7558570643026512,"spread_bps":1.4522851707164524,"day_high":346.0,"day_low":340.115,"execution_condition_ko":"실제 세션 달력, 거래정지 여부, 최신 정규장 호가·완료된 5분봉·거래량가중평균가격을 확보한다. / 348.15 돌파·재시험 지지와 검증된 동시간대 상대거래량 1.2 이상을 관찰한다. 충족하더라도 숫자 손절·목표·비용 후 손익비와 계좌 위험을 별도 심사한다.","risk_condition_ko":"337.67 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":262.24,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":258.5926607010252,"relative_volume":1.5596305894545108,"spread_bps":3.4495314386452924,"day_high":262.68,"day_low":255.22,"execution_condition_ko":"최신 판단 시각은 2026-10-19T05:05:50.485035-04:00이다. 거래일 확인을 전제로 한 최초 검토 후보 시각 2026-10-19T10:30:00-04:00보다 이르며, 이 시각은 만료시각이 아니다. 거래 캘린더와 정규장 일정은 아직 검증되지 않았다. / 253.85~255.60 회복과 257.08 지지를 관찰하고, 첫 저항 259.65~260.14 및 상단 저항 262.80~263.70까지 비용 후 보상위험비를 다시 계산한다. 현재 자료에는 263.70 위의 근거 있는 목표가 없다.","risk_condition_ko":"248.6 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":345.705,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":343.9999968395889,"relative_volume":0.6446252043622022,"spread_bps":1.158446523212965,"day_high":346.26,"day_low":341.85,"execution_condition_ko":"339.08–340.56 부근의 실제 지지 여부를 새 정규장 자료로 확인한다. 과거 종가가 200일 평균보다 0.03 높았다는 사실이나 지지선 접촉만으로 방어 성공을 인정하지 않는다. / 339.08 미만 종가는 전술적 50% 감축, 335.51 미만 종가는 잔여 전술적 보유분 손절의 재확인 신호다. 실제 집중도 또는 계획손실 한도 초과는 별도의 즉시 위험 축소 사유다.","risk_condition_ko":"339.08 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":100.59,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":100.59304144165266,"relative_volume":1.2979284798253712,"spread_bps":0.9940851931001445,"day_high":100.6,"day_low":100.59,"execution_condition_ko":"중립 분석가의 제안대로 핵심 현금운용 경제성 평가와 전술적 돌파 거래를 분리한다. 경제성이 확인돼도 현재 감시 규칙이 자동 매수 승인으로 바뀌지는 않는다. / 보수적 분석가가 지적한 200일 평균 99.1467과 100.53595의 차이, 기준일 및 조정 여부를 해소한다. 불일치한 이동평균을 매수 근거로 사용하지 않는다.","risk_condition_ko":"100.57 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":1263.09,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":1251.6814303322506,"relative_volume":0.7342850187321341,"spread_bps":12.815378454144247,"day_high":1271.56,"day_low":1236.255,"execution_condition_ko":"1260.24 돌파·재시험 지지는 재심사 신호일 뿐이다. 첫 저항까지 순보상/위험이 부족하면 매수하지 않는다. / 1300.17~1306.08 회복·유지 시 갱신된 지지와 다음 저항으로 손익비를 새로 계산한다. 더 높은 진입가 자체가 유리한 것은 아니다.","risk_condition_ko":"1,195 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":921.165,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":924.8229667992796,"relative_volume":0.4853029433064438,"spread_bps":20.041708420226122,"day_high":939.0,"day_low":917.0001,"execution_condition_ko":"실제 정규장 일정·거래정지 여부와 시각이 확인된 최신 호가·분봉·세션 거래량가중평균가·동시간대 상대거래량을 확보한다. 05:05의 지연 장전 가격 935.60은 회복 증거가 아니다. / 933.30 재시험 지지와 942~951 저항 돌파를 관찰하되 비용 차감 후 최소 보상 대비 위험 조건이 없으면 매수하지 않는다.","risk_condition_ko":"933.3 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":423.5,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":419.5479926627903,"relative_volume":0.7257374711340457,"spread_bps":3.5543760292875195,"day_high":423.59,"day_low":415.5001,"execution_condition_ko":"최신 판단시각은 2026-10-19T06:01:19.228848-04:00이다. 완료된 일별 가격은 2026-10-16 기준이며 신선한 정규장 진입 조건은 확인되지 않았다. 시계만으로 거래일·세션·호가 신선도를 확정하지 않는다. / 매도 위험 해소 후 423.66 회복·재시험, 정규장 거래량가중평균가격 지지와 동일 시각 기준 상대거래량 1.2 이상을 확인한다. 이 수치는 제안된 기준이며 관측값이 아니다.","risk_condition_ko":"407.13 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":462.34,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":464.4888875220207,"relative_volume":0.6189811433946114,"spread_bps":16.143787332508207,"day_high":471.765,"day_low":459.64,"execution_condition_ko":"DELL 실제 거래일 운영과 거래 가능 상태, 최신 정규장 가격·거래량가중평균가격·동시간대 상대거래량을 확인한다. / 450.00 유지 여부와 473.50~482.00 반등 실패를 구분하고 이미 집행한 축소 물량을 대조한다.","risk_condition_ko":"513.26 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":394.03,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":393.8024620475494,"relative_volume":1.0010050427764772,"spread_bps":14.00364094664497,"day_high":400.0,"day_low":390.72,"execution_condition_ko":"정규장에서 386.01–390.05 방어, 392.76 회복, 높아지는 5분 봉 저점, 당일 거래량가중평균가 유지와 동시간대 상대거래량 1.2 이상을 관찰한다. / 403.73 위 정규장 종가와 다음으로 확인된 거래일의 재시험 성공은 매수 재평가 계기이지 자동 주문이 아니다. 408.85–416.48 및 421.09–423.72 저항을 포함해 남은 보상 대비 위험을 다시 산정한다.","risk_condition_ko":"392.76 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":336.86,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":336.496632726095,"relative_volume":0.6198801948775067,"spread_bps":2.371564936411943,"day_high":338.775,"day_low":333.82,"execution_condition_ko":"공식 재무제표의 통화·단위·기간·주식 기준·예탁증서 전환 적용 여부를 확인하고 현금흐름·매출총이익 불일치를 대사한다. / 발표시각이 확인되는 공식 전망·경영진 설명·다음 실적 발표일을 확보한다.","risk_condition_ko":"334.61 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":1246.96,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":1251.5394368734308,"relative_volume":0.4329277859860986,"spread_bps":6.8990966996656935,"day_high":1259.75,"day_low":1240.23,"execution_condition_ko":"검증된 정규장에서 미국 동부시간 10:30 이후 1230.66 위의 지지 봉 2개, 거래량가중평균가격 회복, 시간대 조정 상대거래량 1.2 이상을 확인한다. 첫 저항까지 비용 차감 후 보상·위험비 2 이상이어야 하며 1245.29 접촉만으로 매수하지 않는다. / 1251.25와 1257.03 회복은 구조 개선 신호지만 기존 보상·위험비 한도를 초과하는 매수를 정당화하지 않는다.","risk_condition_ko":"1,275.88 이상 도달, 2개 봉 확인 후 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":82.005,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":82.10344265595491,"relative_volume":0.4371383930273937,"spread_bps":1.2198841110100782,"day_high":82.41,"day_low":81.93,"execution_condition_ko":"판단 기준 시각은 2026-10-19T05:21:44.319963-04:00이다. 거래일·휴장·조기폐장·거래정지·호가 시각과 유동성을 별도 확인한다. 지연된 05:05 장전 자료는 정규장 실행 근거가 아니다. / 미국 동부시간 10:30은 최초 재평가 가능 시각이지 만료가 아니다. 검증된 만료 시각이 없으며 임의로 다음 거래일로 이월하지 않는다.","risk_condition_ko":"80.57 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":217.75,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":216.66152926318435,"relative_volume":0.7674570322014597,"spread_bps":1.3785180930487173,"day_high":218.409,"day_low":214.7,"execution_condition_ko":"원문 재무제표에서 표시 통화·단위·비교 기간·주식 및 주당이익 기준·예탁증서 적용 여부와 전환비율·발표 시각을 확인하고 연구 기준시점 안의 자료인지 점검한다. / 보수적 분석이 제시한 매출채권 증가율 약 54.9%와 현금 전환율 약 40.3%는 미검증 경고 지표로 조사한다. 회수기간·채권 연령·신용 조건과 투자 관련 이익 영향을 확인하기 전 회수 실패나 지급불능으로 해석하지 않는다.","risk_condition_ko":"212.85 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":105.225,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":105.59339921765721,"relative_volume":0.7139384573265154,"spread_bps":0.9499833752900684,"day_high":106.11,"day_low":105.18,"execution_condition_ko":"106.68 돌파 후 완료된 15분 봉 2개에 걸친 재시험 지지, 정규장 거래량가중평균가격 상회, 동일 시각 상대거래량 1.2 이상을 확인한다. 가격·거래량 확인만으로는 부족하며 독립적으로 검증된 순기대손익비가 최소 2배여야 한다. / 104.70–105.17 시험 후 105.17 회복과 높아지는 장중 저점을 확인한다. 104.70 아래 지속 거래가 없어야 하며 거래량가중평균가격과 거래 참여도 확인도 필요하다.","risk_condition_ko":"104.7 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":177.73,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":178.2849212091165,"relative_volume":0.4237738103350001,"spread_bps":3.9402212152764164,"day_high":179.3,"day_low":177.2337,"execution_condition_ko":"거래일 달력·정규장 여부·거래정지·최신 호가 시각·스프레드·정규장 거래량가중평균가격을 확인한다. / 173.60–175.15 지지 형성과 174.50 회복을 감시하되, 중립 분석가가 지적한 175.15 경고 해소 여부를 별도로 검증한다.","risk_condition_ko":"173.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":613.1,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":615.2600141390933,"relative_volume":0.45503378332863303,"spread_bps":2.4424994911474203,"day_high":618.0,"day_low":608.5901,"execution_condition_ko":"실제 MA 보유량과 상관 노출부터 점검한다. 집중도·계획 손실·별도 갭 위험 한도 위반이 확인되면 가격 지지 여부와 무관하게 감축한다. / 거래일과 정규장 상태, 최신 호가 차이 0.10% 이하, 거래량가중평균가격 및 동시간대 상대거래량 1.2 이상 여부를 확인한다.","risk_condition_ko":"603.24 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":401.15,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":401.9103980424703,"relative_volume":0.3346778553916567,"spread_bps":1.9905944412646268,"day_high":403.485,"day_low":398.01,"execution_condition_ko":"404.74 상회 시 정규장 5분봉 종가, 지지 재시험, 당일 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상을 확인한다. 이후 보호청산가·검증된 목표·비용 차감 후 2:1 이상 기대손익비를 다시 판단한다. / 399.73–400.00 또는 395.26–397.19에서는 매도 압력 감소와 지지 회복을 요구한다. 가격 접촉만으로 매수하지 않는다.","risk_condition_ko":"395.26 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":223.8,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":223.64423960830754,"relative_volume":0.929884162778054,"spread_bps":4.4656812396728585,"day_high":225.67,"day_low":223.12,"execution_condition_ko":"거래일정·장 상태·거래정지 여부·최신 정규장 호가와 봉 자료·다음 실적발표 일정을 확인한다. 제공된 미국 동부시간 06:15 지연 장전 관측은 진입 확인으로 사용하지 않는다. / 미국 동부시간 10:30 이후 검증된 정규장에서 225.42 상단을 재검증하고 연속 5분봉 두 개의 상회 종가, 225.31–225.42 재시험 성공, 실시간 거래량가중평균가격 지지와 동시간대 상대거래량 1.2 이상을 확인한다.","risk_condition_ko":"220.41 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AMT","display_name":"AMT","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":182.97,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":183.69385656631974,"relative_volume":0.2939985356160291,"spread_bps":10.38166270524417,"day_high":186.0,"day_low":182.845,"execution_condition_ko":"제공된 2026-10-19T07:03:52.424482-04:00 기준 미 동부시간 10:30은 아직 도래하지 않은 최초 진입 검토 시각이지 만료 시각이 아니다. 거래일·휴장·조기종료·실제 장 상태는 별도 확인해야 한다. 주문 만료를 새로 만들거나 다음 거래일로 이월하지 않는다. / 호가·호가 차이·정규장 거래량가중평균가격·동시간대 상대거래량을 갱신한다. 상대거래량 1.2 이상은 제안된 기준이며 관찰값이 아니다.","risk_condition_ko":"176.42 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":990.57,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":989.8889077420882,"relative_volume":0.5913629483366374,"spread_bps":5.955294913270031,"day_high":993.92,"day_low":985.01,"execution_condition_ko":"COST의 거래 일정·거래정지·최신 시세·정규장 5분봉·거래량가중평균가격·동일 시간대 상대거래량을 확보한다. / 977.24-982.00 시험 뒤 982.00 이상이면서 장중 거래량가중평균가격 위인 5분봉 종가 두 개를 확인한다. 순보상·위험비가 부족하면 계속 대기한다.","risk_condition_ko":"977.24 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":157.575,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":157.9574115311551,"relative_volume":0.5568587960713219,"spread_bps":3.7991515228267128,"day_high":158.42,"day_low":157.21,"execution_condition_ko":"156.53–157.56 지지와 회복을 관찰한다. 단순 접촉은 매수 신호가 아니며 이탈 확인은 위험축소 신호다. / 153.20–154.75에서 154.50 부근 반등을 감시한다. 151.90 손절과 159.98 저항 기준 순손익비 2.0 이상이 실제로 가능한지 확인한다.","risk_condition_ko":"156.53 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":283.92,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":285.75855694986427,"relative_volume":0.4741175664670003,"spread_bps":11.264036044915102,"day_high":287.9299,"day_low":283.63,"execution_condition_ko":"281.75~283.00 시험 후 완성된 정규장 5분봉 2개가 283.00 이상에서 마감하고 당일 거래량가중평균가격을 유지하는지 확인한다. / 291.40 돌파·재지지, 동일 경과시간 대비 상대거래량 1.2 이상, 호가 간격 0.25% 이하와 근거 있는 상단 목표를 확인한다.","risk_condition_ko":"288.28 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":202.85,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":202.4894766263878,"relative_volume":0.35606721999792246,"spread_bps":14.30438750092446,"day_high":203.2,"day_low":201.435,"execution_condition_ko":"201.69 방어와 199.30~200.50 시험 후 200.50 회복을 구분한다. / 205.79~205.99 저항과 다음 관측 저항 210.45를 확인한다. 205.99에서 210.45까지 차이 4.46만으로 매수 손익비가 충족되지는 않는다.","risk_condition_ko":"199.26 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":92.88,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":93.76322266056643,"relative_volume":0.662705952859144,"spread_bps":2.147996992805309,"day_high":94.8,"day_low":92.75,"execution_condition_ko":"93.96–94.26 시험 후 94.26 회복을 관찰하되, 정규장 5분봉 두 개와 거래량가중평균가격 상회가 확인되어도 손익비를 별도로 심사한다. / 91.79–93.01 시험 후 93.01 회복을 관찰한다. 93.01 진입·91.79 손절·95.45 저항은 비용 전 손익비가 정확히 2 대 1이므로 비용 차감 후 기준에는 미달한다.","risk_condition_ko":"91.79 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MSFT","display_name":"Microsoft","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":534.5475,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":532.0331870980119,"relative_volume":0.3564054203442807,"spread_bps":1.3094024448423578,"day_high":535.44,"day_low":528.4797,"execution_condition_ko":"실제 거래일·휴장 및 조기폐장 일정, 거래정지 여부, 호가와 가격의 최신성, 정규장 분봉 및 동시간대 상대거래량을 확인한다. 2026-10-19 06:35 미국 동부시간의 지연된 장전 자료는 진입 확인 자료가 아니다. / 제공된 기준시각 2026-10-19T06:51:27.735707-04:00은 미국 동부시간 10:30 검토 개시 전이다. 개시 시각은 만료가 아니며 현재 세션 상태나 조건 충족을 증명하지 않는다. 만료를 임의로 다음 거래일로 넘기지 않는다.","risk_condition_ko":"524.43 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"ITUB","display_name":"ITUB","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":9.465,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":9.512934392858723,"relative_volume":0.708861691312045,"spread_bps":10.565240359217947,"day_high":9.61,"day_low":9.45,"execution_condition_ko":"거래 달력·거래정지·호가 시각을 확인하고 완료된 5분봉, 당일 거래량가중평균가격, 같은 시각 기준 비교 거래량을 확보한다. / 9.39 유지, 9.60 위에서 완료된 5분봉 2개, 9.55–9.60 재시험 성공, 당일 거래량가중평균가격 상회, 상대거래량 1.2 이상을 관찰한다. 기술 조건 충족만으로 매수하지 않는다.","risk_condition_ko":"9.39 이하 하락, 거래량 조건 확인 후 (새 정규장 이탈, 회복 실패와 매도 거래량 확대를 함께 확인) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"TXN","display_name":"Texas Instruments","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":272.8,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":277.3142487602482,"relative_volume":0.548985859981101,"spread_bps":19.387288523089996,"day_high":283.12,"day_low":272.0701,"execution_condition_ko":"273.59~274.16에서 단순 접촉이 아니라 안정화와 높아진 저점을 확인한다. / 검증된 정규장에서 10:30 이후 282.24 및 실시간 거래량가중평균가격 위의 연속 2개 5분봉 종가와 동시간대 상대거래량 1.2 이상을 관찰한다. 현재 관측값이 아닌 제안된 조건이다.","risk_condition_ko":"272.3 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"META","display_name":"Meta Platforms","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":702.61,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":700.7416974905157,"relative_volume":1.0678650780229082,"spread_bps":2.9968960719260247,"day_high":708.7,"day_low":693.86,"execution_condition_ko":"위험 대응 조건: 711.68 이하 하락, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"711.68 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"CCC","display_name":"CCC","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":7.625,"market_data_asof":"2026-10-19T11:01:00-04:00","session_vwap":7.624619086130752,"relative_volume":2.3296307527838747,"spread_bps":13.114754098360375,"day_high":7.63,"day_low":7.61,"execution_condition_ko":"위험 대응 조건: 7.59 이하 하락, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"7.59 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-19T11:11:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:orderbook"],"provider_blockers":null}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-19T23:19:02.052991+09:00",
  "as_of": "2026-10-19T10:10:00-04:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
