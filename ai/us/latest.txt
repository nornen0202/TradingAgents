# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-13T19:45:06.363802+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261114T030226_local-scheduler-us-overlay_only",
  "producer_finished_at": "2026-11-14T03:47:43.364989+09:00",
  "analysis_run_id": "20261113T175022_local-scheduler-us-full",
  "analysis_completed_at": "2026-11-13T20:48:18.744261+09:00",
  "analysis_trade_date_oldest": "2026-11-12",
  "analysis_trade_date_latest": "2026-11-12",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-13T18:45:51+00:00",
  "market_data_latest_at": "2026-11-13T18:45:51+00:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-14T03:47:36.415303+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-14T03:47:36.415303+09:00",
    "run_started_at": "2026-11-14T03:02:26.560692+09:00",
    "run_finished_at": "2026-11-14T03:47:43.364989+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23512360,
    "total_market_value_krw": 22245566,
    "total_unrealized_pnl_krw": -1266794,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 111415,
    "total_equity_krw": 23333633
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 543179,
      "current_price_krw": 529349,
      "market_value_krw": 6352190,
      "unrealized_pnl_krw": -165964
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 291136,
      "current_price_krw": 294200,
      "market_value_krw": 3236206,
      "unrealized_pnl_krw": 33705
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 422275,
      "current_price_krw": 393904,
      "market_value_krw": 2363424,
      "unrealized_pnl_krw": -170231
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1871675,
      "current_price_krw": 1849769,
      "market_value_krw": 1849769,
      "unrealized_pnl_krw": -21906
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 553475,
      "current_price_krw": 468764,
      "market_value_krw": 1406294,
      "unrealized_pnl_krw": -254133
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 266062,
      "current_price_krw": 215762,
      "market_value_krw": 1294573,
      "unrealized_pnl_krw": -301801
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 133921,
      "current_price_krw": 133979,
      "market_value_krw": 1205815,
      "unrealized_pnl_krw": 522
    },
    {
      "ticker": "GEV",
      "name": "GE 버노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1466359,
      "current_price_krw": 1060363,
      "market_value_krw": 1060363,
      "unrealized_pnl_krw": -405996
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 362963,
      "current_price_krw": 477179,
      "market_value_krw": 954358,
      "unrealized_pnl_krw": 228431
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1413690,
      "current_price_krw": 1928262,
      "market_value_krw": 840847,
      "unrealized_pnl_krw": 224386
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 567102,
      "current_price_krw": 461196,
      "market_value_krw": 461196,
      "unrealized_pnl_krw": -105906
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 659811,
      "current_price_krw": 457346,
      "market_value_krw": 457346,
      "unrealized_pnl_krw": -202465
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 135609,
      "current_price_krw": 102235,
      "market_value_krw": 408940,
      "unrealized_pnl_krw": -133497
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 346210,
      "current_price_krw": 354245,
      "market_value_krw": 354245,
      "unrealized_pnl_krw": 8035
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":795.705,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":797.7448639361805,"relative_volume":0.4356661672961965,"spread_bps":14.205706168167849,"day_high":838.9672,"day_low":787.3101,"execution_condition_ko":"위험 대응 조건: 783.62 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"783.62 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":397.345,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":397.25051275883055,"relative_volume":0.4356922101134067,"spread_bps":8.554104712304701,"day_high":408.085,"day_low":391.5,"execution_condition_ko":"위험 대응 조건: 393.91 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"393.91 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":351.81,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":351.46187833594297,"relative_volume":0.21481722232746175,"spread_bps":7.955675522090431,"day_high":363.13,"day_low":347.58,"execution_condition_ko":"위험 대응 조건: 349.57 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"349.57 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":342.7201,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":342.4871762234567,"relative_volume":0.7690557587286376,"spread_bps":4.084848131181582,"day_high":375.27,"day_low":330.4183,"execution_condition_ko":"위험 대응 조건: 335.2 이하 하락, 다음 거래일 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"335.2 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":220.81,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":220.54621381511797,"relative_volume":0.303691294150053,"spread_bps":0.9057971014497387,"day_high":221.82,"day_low":219.43,"execution_condition_ko":"판단 시각은 2026-11-13T04:58:50.232232-05:00, 일봉 기준일은 2026-11-12다. 만료 시각은 아직 지나지 않았지만 실제 거래일·휴장·조기폐장 일정·정규장 호가 신선도와 조건 충족은 별도 확인한다. / 최초 활성화는 지지 시험과 회복 종가 이후 다음 확인 거래일이다. 제공된 2026-11-12 저가 220.58은 219.39~219.87 시험 조건을 충족하지 않으므로 해당 종가만으로 진입 자격을 인정하지 않는다.","risk_condition_ko":"219.39 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":358.1771,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":358.66899447972423,"relative_volume":0.3877970240615656,"spread_bps":0.5583628800352274,"day_high":360.83,"day_low":357.3,"execution_condition_ko":"2026-11-13부터 2026-11-20까지 검토한다. 제공된 기준시각 2026-11-13T04:08:13.906946-05:00에서 2026-11-20T23:59:59-05:00 기한은 아직 미래다. 다만 이 시각만으로 거래일·정규장·조기폐장이나 시세 신선도를 단정하지 않는다. / 최초 인정 종가는 2026-11-13 또는 이후여야 하며, 확인 종가와 그 다음 검증된 거래장의 실행 가능한 재시험이 모두 기한 전에 발생해야 한다. 최초 활성화 조건과 만료시각을 구분하고 거래일을 임의로 다음 날로 이월하지 않는다.","risk_condition_ko":"348.28 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.5591,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":100.55634224363516,"relative_volume":0.744639161853759,"spread_bps":0.994480632490191,"day_high":100.56,"day_low":100.55,"execution_condition_ko":"판단시점 이용 가능성이 검증된 공식 펀드 자료와 동일 기준 가격·순자산가치를 확보하고, 현금 대비 보수적 순수익 조건을 통과할 것. / 정규장 일봉의 100.52~100.53 재시험 및 100.53 이상 마감 후 다음 확인 거래일의 지지·실행 가능 호가를 확인할 것.","risk_condition_ko":"100.5 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":265.9,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":267.19908080697326,"relative_volume":0.30024483050541384,"spread_bps":1.128307350921365,"day_high":269.94,"day_low":263.91,"execution_condition_ko":"2026-11-12 기준 첫 지지 265.62~267.20과 핵심 지지 258.53~261.99의 후속 일봉 반응을 확인한다. / 회복 종가와 다음 실제 거래일 종가가 모두 261.99 이상인지 확인한 뒤, 후속 지지 재시험에서만 소규모 진입을 검토한다. 갭상승으로 구간을 벗어나면 추격하지 않는다.","risk_condition_ko":"258.53 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":346.505,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":348.91905319872296,"relative_volume":0.6723403484453058,"spread_bps":2.597590013708781,"day_high":358.47,"day_low":337.67,"execution_condition_ko":"354.72는 첫 지지 관찰선이며 자동 매수선이 아니다. 이탈하면 깊은 지지 시험과 반등 실패 가능성을 함께 점검한다. / 2026-11-13 이후 344.31-345.44 시험과 345.44 이상 종가가 확인되면 유효기간 안의 바로 다음 검증된 정규장 진입만 검토한다.","risk_condition_ko":"344.31 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1389.195,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":1380.497194504128,"relative_volume":0.3071908138228666,"spread_bps":10.72694875902168,"day_high":1450.0,"day_low":1347.01,"execution_condition_ko":"1390~1403.39 지지 테스트 → 1403.39~1405 회복 종가 → 다음 정규 거래세션 전체의 지지 확인 → 이후 정규 세션의 같은 가격 범위 재진입 기회. / 1464.63~1491.64 공급 소화 여부와 가격·거래 참여의 쇠퇴를 관찰한다. 반등률만으로 이익실현하지 않되 공급 구간에서 상승이 막히고 보유 보상 구조가 악화되면 부분 이익실현을 재평가한다.","risk_condition_ko":"1,390 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1447.1594,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":1436.3247163659287,"relative_volume":0.3079215909004161,"spread_bps":6.635700066357252,"day_high":1447.18,"day_low":1419.81,"execution_condition_ko":"판단시각 2026-11-13T04:49:23.123322-05:00은 계획 만료 전이다. 다만 실제 거래일·정규장·거래정지 여부와 최신 가격은 별도로 확인해야 한다. / 제공된 장전 자료는 175초 지연되고 거래량이 1040주에 불과하므로 정규장 진입 조건의 충족 근거로 사용하지 않는다.","risk_condition_ko":"1,388 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":295.77,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":297.87242550914846,"relative_volume":0.49062938885757335,"spread_bps":0.6762011022071817,"day_high":304.9699,"day_low":293.44,"execution_condition_ko":"292.14–293.69: 일봉 종가 지지 관찰 구간이다. 단순 접촉은 매수나 확정 이탈 신호가 아니다. / 302.56: 상회 종가와 다음 거래일 유지 시 투자 판단을 재평가한다. 신규 매수 자동 승인은 아니다.","risk_condition_ko":"292.14 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":76.74,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":76.82382546180325,"relative_volume":0.37372851432750653,"spread_bps":1.303186290479039,"day_high":77.1199,"day_low":76.5,"execution_condition_ko":"76.18–76.60의 지지 여부를 검증된 일봉으로 점검한다. 장중 76.18 하회만으로 종가 기준 손절이 충족되었다고 보지 않으며 기존의 더 엄격한 손절은 유지한다. / 77.21–77.53, 이후 78.76–79.28의 회복과 다음 거래일 지지를 관찰한다. 새 판단에서는 실제 진입가, 손절거리, 비용과 보유 위험을 다시 계산한다.","risk_condition_ko":"76.18 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":161.92,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":162.3010431126039,"relative_volume":1.437670095735321,"spread_bps":1.23517786561328,"day_high":170.0,"day_low":158.39,"execution_condition_ko":"165.89~167.14의 일봉 지지 형성과 165.89~166.30 회복 여부를 점검한다. / 169.29는 지연 장전 고가 기반 보조선이며 단독 매수 신호가 아니다.","risk_condition_ko":"162.7 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":592.75,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":593.2583467559842,"relative_volume":0.47429631355677926,"spread_bps":1.6870234158834783,"day_high":595.15,"day_low":590.62,"execution_condition_ko":"583.34~588.54 시험, 588.54 초과 종가, 다음 실제 거래일의 지지 재시험 성공을 순서대로 확인한다. / 대안으로 596.92 초과 종가, 갱신된 일간 기준 대비 거래 참여 개선, 다음 거래일 지지 전환을 확인한다. 과도한 상승 갭이면 건너뛴다.","risk_condition_ko":"573.05 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1103.08,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":1104.242595689122,"relative_volume":0.4456191139830765,"spread_bps":2.900968198135551,"day_high":1109.5,"day_low":1092.64,"execution_condition_ko":"1057-1066 시험, 종가 1066 이상, 다음 거래일 지지 유지의 순서를 관찰한다. 실제 소규모 편입은 1057-1060 범위와 비용 차감 후 보상 조건을 모두 충족해야 한다. / 종가 1102.84 돌파와 다음 거래일 지지 전환은 새로운 심사 대상으로 유지한다. 기존 조건부 허가로 추격하지 않는다.","risk_condition_ko":"1,056.96 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":660.79,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":660.296238048618,"relative_volume":0.3051899536087529,"spread_bps":5.145512054119162,"day_high":662.68,"day_low":655.0,"execution_condition_ko":"650.89–652.08은 첫 지지 관찰 구간이다. 유지 또는 이탈만으로 신규 매수를 실행하지 않는다. / 643.90–645.50의 새 일봉 시험, 645.50 위 종가, 다음 검증 거래일의 구간 내 방어된 재시험을 순서대로 확인한다. 구간 위로 뛰면 추격하지 않는다.","risk_condition_ko":"643.9 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":170.045,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":170.0857406915407,"relative_volume":0.3220543042048373,"spread_bps":0.5880796259824944,"day_high":170.73,"day_low":168.5,"execution_condition_ko":"2026-11-13T06:09:29.000694-05:00 기준 진입 기한은 미래다. 다만 거래 일정, 휴장·단축장·거래정지 여부 및 최신 정규장 가격은 별도로 확인해야 한다. 지연된 05:30 동부 장전 관측은 진입 확인이 아니다. / 분석일 이후 3회 검증된 정규거래 회기 이내 및 2026-11-20T18:00:00-05:00 중 먼저 도래하는 시점까지 재검토한다. 중요 정보나 지지 이탈이 나타나면 앞당긴다.","risk_condition_ko":"164.48 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WELL","display_name":"WELL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":243.93,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":244.65116142093,"relative_volume":0.23258356824808002,"spread_bps":3.6899612554057923,"day_high":247.27,"day_low":242.9,"execution_condition_ko":"새 지지 시험과 244.65 이상 종가 이후 다음 적격 거래일에 비용 차감 매수 상한 이하의 지지 재시험이 가능한지 확인한다. / 248.83–249.75와 253.37 저항을 관찰한다. 돌파만으로 자동 매수하지 않는다.","risk_condition_ko":"243.28 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"KO","display_name":"KO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":99.205,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":98.85923414313879,"relative_volume":0.3489552560889525,"spread_bps":1.0080137089855254,"day_high":99.29,"day_low":97.96,"execution_condition_ko":"현재 진입 조건 충족 증거는 없다. 최초 활성화는 적격 회복 일봉 다음의 검증된 정규 세션이며, 단순 가격 도달은 매수 신호가 아니다. / 기업 주요 사건·일정과 계좌 한도를 확인한 뒤 지지 회복, 후속 재시험, 비용 후 손익비 1.5배 이상을 함께 점검한다. 중기 증액에는 재무 원문 대조와 현금흐름 검증을 추가로 요구한다.","risk_condition_ko":"94.72 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WMT","display_name":"WMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":127.55,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":127.67147650708552,"relative_volume":0.3344815499462304,"spread_bps":2.3519266198884345,"day_high":128.27,"day_low":126.24,"execution_condition_ko":"125.00–125.50 시험, 125.10 상회 종가, 다음 확인된 거래일의 125.00 유지와 더 높은 완성 일봉 저가를 순서대로 점검한다. 가격 접촉만으로 매수하지 않는다. / 123.58은 경고 지지, 123.03은 종가 기준 위험 축소선, 122.20은 신규 첫 매수분의 손절선이다.","risk_condition_ko":"123.03 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":295.325,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":294.8709669590322,"relative_volume":0.2731640123057472,"spread_bps":4.401930077033623,"day_high":297.25,"day_low":293.56,"execution_condition_ko":"284.70~286.00에서 일봉 반전과 다음 실제 거래 세션 지지 확인 후, 필수 검증을 충족한 범위 내 초도만 검토한다. / 290.93~291.89 유지·회복은 단기 안정 관찰 신호일 뿐 독립적인 매수 신호가 아니다.","risk_condition_ko":"284.7 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":426.385,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":425.885348603329,"relative_volume":0.2615947335397972,"spread_bps":1.876304618055701,"day_high":427.455,"day_low":422.59,"execution_condition_ko":"판단시각 이후 지지 구간 재시험, 420.08 이상 종가 회복, 다음 실제 거래 세션의 417.66 이상 종가 지지를 순서대로 확인한다. / 425.76·430.18에서 반등이 유지되는지 관찰한다. 435.95·441.41은 추가 저항이며 자동 증액이나 확정 매도 주문이 아니다.","risk_condition_ko":"411.99 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LIN","display_name":"LIN","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":525.28,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":524.6001706887472,"relative_volume":0.280437447753247,"spread_bps":1.5229682651495542,"day_high":526.775,"day_low":521.47,"execution_condition_ko":"일별 가격 근거는 2026-11-12 종가 522.49까지다. 제공된 2026-11-13 장전 525.00은 지연되고 거래가 적은 관측치이므로 현재 정규장 가격이나 발동 신호로 사용하지 않는다. / 제공된 결정시각 2026-11-13T05:54:52.046700-05:00 기준으로 2026-11-20T23:59:59-05:00 만료는 아직 미래다. 유효기간이 열려 있다는 사실과 매수 조건 충족은 다르다. 거래소 일정·거래 상태·최신 실행 가격은 별도로 확인한다.","risk_condition_ko":"516 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TSLA","display_name":"Tesla","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":390.695,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":392.4125225525097,"relative_volume":0.5756266256986009,"spread_bps":4.094899291071201,"day_high":404.4,"day_low":385.8302,"execution_condition_ko":"재시험일 종가 회복과 다음 실제 정규장 지지 확인 후에도 385.32~386.00 진입이 가능한지 확인한다. 확인 중 386.00을 넘으면 추격하지 않는다. / 401.22 돌파와 후속 지지, 403.30~407.46 및 410.85~414.23 저항을 관찰한다. 419.89는 변동성 상단 참고값이지 보장된 목표가가 아니다.","risk_condition_ko":"382.86 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TTD","display_name":"TTD","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":15.81,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":15.788651772324558,"relative_volume":0.45191826068277313,"spread_bps":6.3271116735209025,"day_high":16.09,"day_low":15.4536,"execution_condition_ko":"14.20~14.30 시험 후 종가 14.30 이상 회복을 확인한다. 최초 진입 가능 시점은 그다음 확인된 정규 세션의 구간 내 지지 재시험이다. / 15.45~15.47 및 14.93~15.08 이탈은 다음 지지 점검 신호이지 자동 저가 매수 신호가 아니다.","risk_condition_ko":"14.2 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"JPM","display_name":"JPM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":344.55,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":344.4524842776974,"relative_volume":0.22343170452567931,"spread_bps":2.902336380787193,"day_high":346.8,"day_low":342.79,"execution_condition_ko":"339.99–341.22 재시험과 341.22 이상 종가 이후 바로 다음 정규장의 339.99–340.25를 관찰한다. / 347.20–348.23과 352.11–352.33의 공급 부담을 재평가한다. 상향 돌파만으로 자동 매수하지 않는다.","risk_condition_ko":"333 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LHX","display_name":"L3Harris Technologies","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":268.965,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":269.6832388118367,"relative_volume":0.14139736938562977,"spread_bps":6.690206281360596,"day_high":272.98,"day_low":268.6,"execution_condition_ko":"새로운 267.69–270.58 시험, 종가 270.58 이상 회복, 다음 확인된 거래일의 269.21–270.58 지지와 범위 내 체결을 순서대로 확인한다. 범위 위로 상승하면 추격하지 않는다. / 276.59–279.93 및 281.11–283.71 공급 구간에서 참여도와 비용 차감 손익비를 재평가한다. 가까운 저항에서 청산할 계획이라면 먼 저항까지의 보상으로 진입을 정당화하지 않는다.","risk_condition_ko":"267.69 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"JHX","display_name":"JHX","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":27.79,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":27.699243774920003,"relative_volume":0.22478341494212928,"spread_bps":3.597769382983113,"day_high":27.945,"day_low":27.395,"execution_condition_ko":"다음 몇 차례의 확인된 거래일 종가를 검토하고 2026-11-20T23:59:59-05:00까지 계획을 갱신한다. 이는 달력상 검토 기한이며 주문 만료나 거래소 마감시각이 아니다. / 27.52, 27.18~27.24, 26.79 순서로 지지 여부를 감시한다. 현재 확인된 것은 28.11 단기 추세 이탈이며 27.52 종가 이탈은 아니다.","risk_condition_ko":"28.11 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"OKTA","display_name":"Okta","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":183.015,"market_data_asof":"2026-11-13T18:45:51+00:00","session_vwap":179.98831177589253,"relative_volume":0.21962471722986948,"spread_bps":28.959374914624547,"day_high":185.98,"day_low":175.0,"execution_condition_ko":"위험 대응 조건: 180 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"180 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-13T18:45:51+00:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-13T18:48:51+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-14T03:09:54.966366+09:00",
  "as_of": "2026-11-13T16:03:41+00:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
