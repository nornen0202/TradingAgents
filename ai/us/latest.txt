# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-12T16:45:11.674415+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261113T000249_local-scheduler-us-overlay_only",
  "producer_finished_at": "2026-11-13T00:31:18.117063+09:00",
  "analysis_run_id": "20261112T175110_local-scheduler-us-full",
  "analysis_completed_at": "2026-11-12T20:49:50.895998+09:00",
  "analysis_trade_date_oldest": "2026-11-11",
  "analysis_trade_date_latest": "2026-11-11",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-12T15:29:53+00:00",
  "market_data_latest_at": "2026-11-12T15:29:53+00:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-13T00:31:10.125165+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-13T00:31:10.125165+09:00",
    "run_started_at": "2026-11-13T00:02:49.029812+09:00",
    "run_finished_at": "2026-11-13T00:31:18.117063+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23588248,
    "total_market_value_krw": 22595573,
    "total_unrealized_pnl_krw": -992675,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 111774,
    "total_equity_krw": 23684012
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 544932,
      "current_price_krw": 541523,
      "market_value_krw": 6498286,
      "unrealized_pnl_krw": -40904
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 292076,
      "current_price_krw": 296520,
      "market_value_krw": 3261721,
      "unrealized_pnl_krw": 48884
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 423638,
      "current_price_krw": 394847,
      "market_value_krw": 2369086,
      "unrealized_pnl_krw": -172746
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1877715,
      "current_price_krw": 1892326,
      "market_value_krw": 1892326,
      "unrealized_pnl_krw": 14611
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 555261,
      "current_price_krw": 473816,
      "market_value_krw": 1421450,
      "unrealized_pnl_krw": -244335
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 266921,
      "current_price_krw": 220094,
      "market_value_krw": 1320566,
      "unrealized_pnl_krw": -280960
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 134353,
      "current_price_krw": 134371,
      "market_value_krw": 1209345,
      "unrealized_pnl_krw": 162
    },
    {
      "ticker": "GEV",
      "name": "GE 버노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1471091,
      "current_price_krw": 1096234,
      "market_value_krw": 1096234,
      "unrealized_pnl_krw": -374857
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 364135,
      "current_price_krw": 478318,
      "market_value_krw": 956636,
      "unrealized_pnl_krw": 228366
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1418251,
      "current_price_krw": 1930749,
      "market_value_krw": 841932,
      "unrealized_pnl_krw": 223482
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 568932,
      "current_price_krw": 482849,
      "market_value_krw": 482849,
      "unrealized_pnl_krw": -86083
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 661940,
      "current_price_krw": 475925,
      "market_value_krw": 475925,
      "unrealized_pnl_krw": -186015
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 136047,
      "current_price_krw": 102157,
      "market_value_krw": 408629,
      "unrealized_pnl_krw": -135559
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 347328,
      "current_price_krw": 360588,
      "market_value_krw": 360588,
      "unrealized_pnl_krw": 13260
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":76.32,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":76.77291599608543,"relative_volume":0.9278056301540781,"spread_bps":1.3101867016056492,"day_high":77.21,"day_low":76.18,"execution_condition_ko":"위험 대응 조건: 79.88 이상 도달, 다음 거래일 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"79.88 이상 도달, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":221.6,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":222.0406897094507,"relative_volume":0.45064642933096943,"spread_bps":0.9025270758127361,"day_high":222.925,"day_low":221.25,"execution_condition_ko":"2026-11-11 이후 새로 확정되는 일봉마다 지지·거래량·보상구조를 재평가한다. 최종 신규 실행기한은 2026-11-19T23:59:59-05:00이며 자동 연장하지 않는다. / 눌림 재시험 후 219.68 이상 종가와 다음 실제 거래일 지지 유지를 확인한다. 확인 과정에서 가격이 저항 가까이 상승하면 추격하지 않는다.","risk_condition_ko":"218.9 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":357.85,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":357.6854194373832,"relative_volume":0.8316108705756786,"spread_bps":1.397174912327592,"day_high":359.3684,"day_low":355.92,"execution_condition_ko":"연구 기준일은 2026-11-12, 최신 제공 일봉은 2026-11-11이다. 2026-11-12T04:06:52.325438-05:00 기준 유효기한은 지나지 않았지만 거래일정, 현재 세션, 호가 신선도와 진입 충족 여부는 확인되지 않았다. / 2026-11-12부터 실제 완료되는 각 일봉을 검토한다. 최초 활성화는 적격 일봉 확정 뒤 다음 실제 거래일이며, 확인과 체결 모두 2026-11-19T23:59:59-05:00 전에 완료해야 한다. 이 시각은 행정적 검토기한이지 거래소 마감시각이 아니며 자동 연장하지 않는다.","risk_condition_ko":"349.33 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":360.785,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":360.20162158936455,"relative_volume":2.7317151266129347,"spread_bps":7.48368141691142,"day_high":365.713,"day_low":354.72,"execution_condition_ko":"324.40–326.06 시험, 326.06 이상 완료 종가, 다음 검증된 거래일의 지지 유지, 이후 범위 내 재시험 순서로 관찰한다. 단순 접촉이나 높은 가격으로의 대체 진입은 허용하지 않는다. / 331.98–334.67은 관찰용 지지이며 이 범위에 도달했다는 이유만으로 매수하지 않는다.","risk_condition_ko":"324.4 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":269.76,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":270.7125609846654,"relative_volume":0.9796579918514182,"spread_bps":1.482854494901339,"day_high":273.5998,"day_low":267.835,"execution_condition_ko":"258.53–260.78을 관찰하되 확인 없는 지정가 매수는 하지 않는다. 실제 최초 매수 가능 범위는 258.53–259.00으로 제한한다. / 260.78 회복과 다음 거래일 유지가 확인되어도 추가 매수는 별도 검토한다.","risk_condition_ko":"258.53 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1414.9,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":1430.5693884988682,"relative_volume":0.5936427235663616,"spread_bps":34.906973621916876,"day_high":1464.6308,"day_low":1408.0,"execution_condition_ko":"1390~1396.55 시험 → 1396.55 이상 종가 회복 → 다음 확인된 거래일의 지지 유지·저점 상승 → 구간 내 재시험 순서로 확인한다. 실제 매수가가 1396.55를 넘으면 계속 대기한다. / 2026-11-11 종가 1478.69에서 첫 저항 1491.64까지 여력은 12.95인 반면 지지 1390까지 거리는 88.69다. 현 수준의 신규 진입은 불리하다. 상한 1396.55에서 첫 저항 구간까지 여력도 평균 진폭의 약 1.05~1.29배일 뿐, 기대수익이나 손실확률을 반영한 보장 손익비가 아니다.","risk_condition_ko":"1,390 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":404.685,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":403.13534002229653,"relative_volume":1.2649762734429306,"spread_bps":16.799248974751887,"day_high":409.9189,"day_low":393.9149,"execution_condition_ko":"399.50~401.03 시험, 401.03 이상 정규장 종가, 다음 실제 정규장의 지지 재시험을 순서대로 확인한다. 단순 접촉이나 상한 초과 상승은 매수 신호가 아니다. / 416.80 및 428.00~430.47 회복과 거래 참여 개선을 관찰한다. 공격적 분석가의 평균 거래량 대비 약 94%라는 수치는 장중 상대거래량 기준으로 전용하지 않는다.","risk_condition_ko":"396.32 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":["feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.5285,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":100.53114453340666,"relative_volume":1.361277644417732,"spread_bps":0.9947774185531076,"day_high":100.54,"day_low":100.52,"execution_condition_ko":"판단시각 이후 확인된 정규세션에서 100.49~100.50 지지와 종가 100.50 이상, 다음 확인된 세션 동일 구간 재지지 및 경제성 검증이 모두 충족되면 소액 신규진입 후보로 전환한다. / 100.53~100.54는 회복 관찰대이며 단독 매수 신호가 아니다. 100.55~100.58 회복·유지는 추가 배분 재검토 계기다.","risk_condition_ko":"100.42 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":819.46,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":807.0568205813674,"relative_volume":0.7294682473625891,"spread_bps":17.572547775363542,"day_high":826.75,"day_low":783.6238,"execution_condition_ko":"845.00 위 종가 후 다음 확인된 정규 거래일에 827.82~845.00 지지 유지 또는 845.00 재돌파를 점검한다. 원문 검증과 비용 차감 후 유리한 손익비가 확보되면 소액 진입 가능성을 별도 심사하되 현재 매수 승인은 없다. / 797.04 하회 종가는 추가 감축, 770.51~774.11은 하방 관찰, 747.00 하회 종가는 잔여 청산 기준이다. 하방 관찰 구간은 자동 매수선이 아니다.","risk_condition_ko":"845 이상 도달, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":354.06,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":353.3983252984552,"relative_volume":0.9494663158982773,"spread_bps":17.21388963357029,"day_high":356.9633,"day_low":349.57,"execution_condition_ko":"360.67~361.79 회복과 364.95~368.63 저항 상단의 종가 돌파를 관찰한다. 이후 다음 실제 거래일 지지와 거래량 개선을 확인하되 자동 매수하지 않는다. / 375.41~377.07 및 390.50~401.66의 저항을 반영해 비용 차감 후 보상·위험을 재계산한다. 비율을 맞추려고 손절을 억지로 좁히거나 목표를 멀리 잡지 않는다.","risk_condition_ko":"352 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":295.595,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":295.0715931701758,"relative_volume":1.0654690144829995,"spread_bps":1.6913891378993409,"day_high":296.9499,"day_low":293.8,"execution_condition_ko":"2026-11-12부터 7일간 관찰하고 2026-11-19T16:00:00-05:00까지 재평가한다. 판단 시계 2026-11-12T04:35:24.686633-05:00 기준 이 마감은 지나지 않았다. 이는 검토 마감이며 매수 주문 만료나 확인된 거래소 폐장시각이 아니다. / 2026-11-11 일봉을 기준으로 292.55~292.60, 295.74~296.49, 289.48, 284.59, 276.92를 추적하고 이동평균은 새 일봉으로 갱신한다. 300과 316.60~324.89는 관찰 구간이지 확정 목표가가 아니다.","risk_condition_ko":"289.48 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":356.9518,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":354.00989039662863,"relative_volume":1.4348186217154715,"spread_bps":24.665751044089905,"day_high":366.635,"day_low":337.165,"execution_condition_ko":"다음 3~5개의 확인된 거래일을 관찰하고 2026-11-19까지 정식 재평가한다. 이 날짜는 검토 기한이며 주문 만료일이나 거래일 확정이 아니다. / 상방은 378.16~384.69와 391.25~394.53의 종가 회복 및 후속 지지를, 하방은 358.52, 340.20~346.31, 325.10~334.38, 315.00을 점검한다. 이동평균은 갱신하되 기존 손절은 낮추지 않는다.","risk_condition_ko":"358.52 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":164.61,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":158.31003306133263,"relative_volume":9.774463844074798,"spread_bps":1.2153621779279176,"day_high":166.0,"day_low":148.8,"execution_condition_ko":"165.89 지지와 168.89–170.77 회복구간, 173.73 재탈환을 우선 추적한다. 177.54–179.92, 181.60–186.64, 188.57–188.88에서는 거절과 지지 여부를 구분한다. 어느 가격도 단독 매수 지시가 아니다. / 2026-11-12부터 7일간 매일 검토하고 2026-11-19T16:00:00-05:00까지 근거와 수준을 갱신한다. 이는 분석 검토기한이며 주문 만료나 실제 거래소 마감시각을 뜻하지 않는다. 중대한 검증 뉴스나 위험 조건 발생 시 앞당겨 검토한다.","risk_condition_ko":"165.89 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1443.62,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":1446.5958918368044,"relative_volume":0.6784987986143692,"spread_bps":6.99385441011144,"day_high":1460.0,"day_low":1433.5,"execution_condition_ko":"1440.47–1453.00 저항 돌파의 종가 확인과 다음 거래일 지지 여부를 관찰한다. 장전 고가만으로 돌파를 인정하지 않는다. / 1400.00–1414.37 및 1380.06–1389.55에서 안정과 반전을 관찰한다. 구간 도달은 자동 매수 신호가 아니며, 위험 축소 조건이 우선한다.","risk_condition_ko":"1,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":592.545,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":593.5605375285509,"relative_volume":1.2823199150489977,"spread_bps":11.308875779594384,"day_high":596.9,"day_low":591.02,"execution_condition_ko":"매 확인된 정규장 종가 후 576.80~579.09 지지, 569.32 위험선, 588.54~593.32 저항 관찰 구간을 재점검한다. / 가격 기준일은 2026-11-11이다. 제공된 2026-11-12 06:00 동부시간 지연 장전 봉은 정규장 조건 충족 증거가 아니다. 실행 전 거래일·휴장 및 단축거래 여부·거래정지 상태·가격 신선도를 확인한다.","risk_condition_ko":"569.32 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TM","display_name":"TM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":211.15,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":211.8250081195193,"relative_volume":0.5510265450315396,"spread_bps":16.09696051510155,"day_high":213.695,"day_low":210.96,"execution_condition_ko":"210.67~212.47 시험, 212.47 이상 종가 회복, 다음 실제 정규장의 210.67 지지와 210.67~211.00 재시험을 순서대로 확인한다. / 214.49~215.65 및 216.19~218.51 저항에서 반등이 반복적으로 막히는지 관찰한다. 먼 저항까지의 계산만으로 매수를 정당화하지 않는다.","risk_condition_ko":"206.72 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1098.355,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":1096.3693348791492,"relative_volume":1.0573032518600207,"spread_bps":7.7394799979980835,"day_high":1102.84,"day_low":1088.98,"execution_condition_ko":"1065.59–1071.34 시험, 1071.34 위 일봉 재탈환, 다음 확인된 거래일 지지 재시험을 순서대로 관찰한다. 단순 접촉만으로 매수하지 않는다. / 실제 신규 진입은 1065.59–1067.46 안에서도 비용 조정 상한을 충족하는 가격만 허용한다. 조정 상한이 1065.59 미만이면 이번 계획으로 매수하지 않는다.","risk_condition_ko":"1,043 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":297.0,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":295.98903453600644,"relative_volume":0.5494963390674599,"spread_bps":8.417650128790047,"day_high":300.42,"day_low":295.37,"execution_condition_ko":"ABBV의 290.22–291.32와 인접 저점 289.73을 관찰하되 가격 접촉만으로 매수하지 않는다. / 283.32–286.00 시험 후 286.00 이상 회복 종가, 직전 정규장보다 증가한 거래량, 다음 실제 거래일의 지지 유지와 구간 내 실행 가격을 순서대로 확인한다.","risk_condition_ko":"281.07 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"KO","display_name":"KO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":98.01,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":97.84452089454166,"relative_volume":0.45456679017822815,"spread_bps":3.060443764345946,"day_high":98.34,"day_low":97.44,"execution_condition_ko":"매수 전 원문 보고 기준, 주요 공지, 거래 가능 여부, 실제 정규장과 계좌 위험예산을 확인한다. / 2026-11-12 이후 지지 시험과 회복 종가를 확인한 뒤 후속 정규장의 95.59~95.80 재시험을 관찰한다. 추정 비용 반영 손익비가 2 미만이면 진입하지 않는다.","risk_condition_ko":"94.61 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LIN","display_name":"LIN","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":527.105,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":527.5190703154287,"relative_volume":0.5649917355915942,"spread_bps":6.449777103291886,"day_high":530.19,"day_low":524.472,"execution_condition_ko":"새 정규장 일봉에서 517–520 시험과 520 이상 마감을 확인한 뒤 바로 다음 확인된 정규장의 517–518 재시험을 점검한다. 첫 활성화 가능 시점은 이 확인 종가 이후의 다음 정규장이다. / 526.56–526.75의 거절과 533.39의 돌파·재실패를 구분한다. 어느 쪽도 현재 계획의 추격 매수를 허용하지 않는다.","risk_condition_ko":"510 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":660.73,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":661.6390106816201,"relative_volume":0.28661355686675527,"spread_bps":5.449921278915068,"day_high":667.505,"day_low":659.12,"execution_condition_ko":"MA가 646.26–650.51을 시험하고 650.51 이상으로 마감한 뒤 다음 검증된 거래일에 지지를 유지하거나 회복하는지 확인한다. 하락 중 단순 접촉만으로 매수하지 않는다. / MA의 661.84, 672.68–673.50, 681.99 저항 반응을 관찰한다. 어느 저항의 단순 상향 통과도 현재 계획의 매수나 추가 매수를 자동 승인하지 않는다.","risk_condition_ko":"638.01 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":169.0875,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":169.2128294579342,"relative_volume":0.566424930873971,"spread_bps":4.140664280854939,"day_high":169.95,"day_low":168.3901,"execution_condition_ko":"165.37~165.88 지지를 관찰하되 이 구간 반등만으로 추격 매수하지 않는다. / 164.07~164.22 지지 시험, 164.07 이상 첫 종가, 다음 실제 거래일의 164.07 이상 유지 종가를 순서대로 확인한다. 이후 재시험도 새로운 매도 압력일 수 있으므로 체결 직전 지지와 악재를 다시 점검한다.","risk_condition_ko":"164.07 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WELL","display_name":"WELL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":246.7,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":246.55809001451848,"relative_volume":0.2593450565591202,"spread_bps":9.729203826820541,"day_high":249.751,"day_low":245.1756,"execution_condition_ko":"검토 이후 새 지지 시험과 243.80 이상 종가, 다음 검증된 거래일의 242.91–243.50 재시험을 순서대로 관찰한다. 과거 종가만으로 신규 확인을 대체하지 않는다. / 248.83 상향 종가와 다음 거래일 지지 확인 시 별도 심사한다. 250.26–251.12와 253.37은 추가 저항이며 자동 추격매수 가격이 아니다.","risk_condition_ko":"242.91 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SO","display_name":"SO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":93.5,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":93.5956319879426,"relative_volume":0.9994233447380337,"spread_bps":1.069461526122145,"day_high":94.17,"day_low":93.065,"execution_condition_ko":"2026-11-11 이후 완성된 일봉의 93.08~93.18 시험과 93.18 이상 종가를 확인한다. 단순 접촉은 부족하다. / 확인 다음 실제 거래일의 지지 재시험과 구간 내 매수 가능 가격을 점검한다. 구간 위로 갭이 발생하면 추격하지 않고, 재시험 실패 시 새로운 확인을 기다린다.","risk_condition_ko":"91.77 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":425.56,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":426.39026512297045,"relative_volume":0.3914279665345504,"spread_bps":4.229820232640273,"day_high":430.18,"day_low":424.24,"execution_condition_ko":"2026-11-11 지지 시험과 회복을 원자료로 확인하고 이후 종가에 지지 이탈이 없는지 점검한다. 유효 회복 다음의 실제 정규장에서 416.89–419.00의 안정적인 재시험을 관찰한다. / 첫 재시험 기회를 놓치거나 지지 시험이 불확실하면 추격하지 않는다. 새로운 지지 시험 후 420.03 위 회복 종가와 그다음 거래일의 재시험을 다시 요구한다.","risk_condition_ko":"416.43 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WMT","display_name":"WMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":126.36,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":126.39248136795736,"relative_volume":0.9142423254777378,"spread_bps":1.5826541109437384,"day_high":127.66,"day_low":125.48,"execution_condition_ko":"WMT의 124.68~124.86 시험, 124.86 이상 종가 회복, 다음 실제 정규장 재지지를 순서대로 확인한다. 조건 충족 전 신규 배정자금은 현금으로 유지한다. / 126.64 위 종가와 후속 지지는 재평가 신호다. 127.69~127.94의 인접 저항 때문에 자동 추격하지 않는다. 129.17과 130.94~131.82도 보상·잔여 위험 점검 구간이지 승인된 자동 익절 가격이 아니다.","risk_condition_ko":"123.03 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"JHX","display_name":"JHX","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":28.12,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":28.343568211101733,"relative_volume":0.5070429035827464,"spread_bps":7.112375533428014,"day_high":28.555,"day_low":28.055,"execution_condition_ko":"2026-11-12부터 2026-11-19T23:59:59-05:00까지 매일 종가 기준으로 재검토한다. 제공된 실행시각 2026-11-12T06:41:41.762624-05:00은 만료 전이지만 실제 정규장·휴장·조기폐장·호가 신선도와 조건 충족 여부는 확인되지 않았다. 이 기한은 연구 유효기간이지 거래소 폐장시각이 아니다. / 적격 일봉 확인 이후에만 다음 검증된 정규장의 재시험을 평가한다. 지지 아래 갭, 비용 조정 상한 초과 또는 재시험 기회 상실 시 건너뛰고 새로운 일봉 확인을 요구한다.","risk_condition_ko":"28.23 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TSLA","display_name":"Tesla","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":389.596,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":391.73108023499276,"relative_volume":0.7918408678084292,"spread_bps":5.645223371223998,"day_high":396.2,"day_low":385.2,"execution_condition_ko":"383.00~386.00 시험과 386.00 이상 종가 이후 다음 확인된 거래일의 같은 구간 재시험을 관찰한다. 사건 위험·거래 참여·계좌 점검까지 통과해야 소액 진입이 가능하다. / 395.43의 첫 저항과 398.50~404.22의 공급 부담을 우선 점검한다. 먼 상단만으로 기대수익을 정당화하지 않는다.","risk_condition_ko":"381.2 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"JPM","display_name":"JPM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":342.9975,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":344.2290203839075,"relative_volume":0.3265482253388099,"spread_bps":4.956918546165412,"day_high":347.155,"day_low":342.36,"execution_condition_ko":"340.20~340.70 지지와 344.85~345.75 저항 반응을 관찰한다. 347.76 위 종가 이후 다음 확인된 거래일 안착을 확인하고 손익비를 재계산한다. 352.11~352.33과 359.80은 관찰 저항이지 확정 목표가가 아니다. / 실행 전 최신 완료 일봉의 날짜·신선도, 현재 가격, 거래소 일정과 거래 상태를 확인한다. 제공된 2026-11-12 시계와 지연된 장전 스냅샷은 진입 충족이나 실제 거래 세션을 증명하지 않는다.","risk_condition_ko":"340 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"HPE","display_name":"Hewlett Packard Enterprise","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":49.46,"market_data_asof":"2026-11-12T15:29:53+00:00","session_vwap":49.00053354739319,"relative_volume":0.4740799936838248,"spread_bps":12.135922330097548,"day_high":49.82,"day_low":47.56,"execution_condition_ko":"위험 대응 조건: 47.54 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"47.54 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-12T15:29:53+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T15:32:53+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-13T01:10:14.819039+09:00",
  "as_of": "2026-11-12T15:29:53+00:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
