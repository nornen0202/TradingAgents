# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-16T17:55:40.226251+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261117T000615_local-scheduler-us-overlay_only",
  "producer_finished_at": "2026-11-17T01:30:34.398185+09:00",
  "analysis_run_id": "20261116T175030_local-scheduler-us-full",
  "analysis_completed_at": "2026-11-16T21:08:14.047711+09:00",
  "analysis_trade_date_oldest": "2026-11-13",
  "analysis_trade_date_latest": "2026-11-13",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-16T11:13:00-05:00",
  "market_data_latest_at": "2026-11-16T11:28:00-05:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-17T01:30:22.381716+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-17T01:30:22.381716+09:00",
    "run_started_at": "2026-11-17T00:06:15.338992+09:00",
    "run_finished_at": "2026-11-17T01:30:34.398185+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23535303,
    "total_market_value_krw": 21709035,
    "total_unrealized_pnl_krw": -1826268,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 112124,
    "total_equity_krw": 22797811
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 543709,
      "current_price_krw": 505979,
      "market_value_krw": 6071749,
      "unrealized_pnl_krw": -452764
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 291420,
      "current_price_krw": 293467,
      "market_value_krw": 3228140,
      "unrealized_pnl_krw": 22514
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 422687,
      "current_price_krw": 385079,
      "market_value_krw": 2310475,
      "unrealized_pnl_krw": -225652
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1873501,
      "current_price_krw": 1772513,
      "market_value_krw": 1772513,
      "unrealized_pnl_krw": -100988
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 554015,
      "current_price_krw": 456352,
      "market_value_krw": 1369056,
      "unrealized_pnl_krw": -292991
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 266322,
      "current_price_krw": 213125,
      "market_value_krw": 1278751,
      "unrealized_pnl_krw": -319181
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 134052,
      "current_price_krw": 134131,
      "market_value_krw": 1207185,
      "unrealized_pnl_krw": 716
    },
    {
      "ticker": "GEV",
      "name": "GE 버노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1467790,
      "current_price_krw": 1037725,
      "market_value_krw": 1037725,
      "unrealized_pnl_krw": -430065
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 363317,
      "current_price_krw": 473463,
      "market_value_krw": 946927,
      "unrealized_pnl_krw": 220292
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1415068,
      "current_price_krw": 1940500,
      "market_value_krw": 846184,
      "unrealized_pnl_krw": 229122
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 567655,
      "current_price_krw": 448690,
      "market_value_krw": 448690,
      "unrealized_pnl_krw": -118965
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 660454,
      "current_price_krw": 435319,
      "market_value_krw": 435319,
      "unrealized_pnl_krw": -225135
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 135741,
      "current_price_krw": 101761,
      "market_value_krw": 407045,
      "unrealized_pnl_krw": -135922
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 346548,
      "current_price_krw": 349276,
      "market_value_krw": 349276,
      "unrealized_pnl_krw": 2728
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":777.965,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":782.7481383998755,"relative_volume":0.6227172730030661,"spread_bps":16.453288086790742,"day_high":800.32,"day_low":771.4,"execution_condition_ko":"위험 대응 조건: 770.51 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"770.51 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":336.44,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":332.44229938254733,"relative_volume":0.7722370112465845,"spread_bps":6.540805708338648,"day_high":336.71,"day_low":327.8,"execution_condition_ko":"위험 대응 조건: 335.56 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"335.56 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":220.085,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":220.4586922511655,"relative_volume":0.5884446890292812,"spread_bps":0.45445249835348794,"day_high":221.25,"day_low":219.89,"execution_condition_ko":"2026-11-13 회복만으로 조건을 충족했다고 보지 말고 2026-11-16부터 새로운 지지 시험과 확인 종가를 기다린다. / 확인 다음 검증된 정규장에서 219.43–220.11 재시험을 관찰한다. 첫 시험 매수 후 추가 배분은 별도의 일간 추세 지속과 손익비 재평가가 필요하다.","risk_condition_ko":"219.43 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":354.965,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":355.83615385267035,"relative_volume":0.6408566519416259,"spread_bps":1.1268557906307706,"day_high":357.1,"day_low":353.02,"execution_condition_ko":"354.41–355.75는 초기 지지 관찰 구간이며 단순 접촉은 매수 신호가 아니다. / 349.00–350.00 시험, 350.00 이상 종가, 다음 확인된 거래일 349.73–350.00 내 지지·회복 순서를 추적한다.","risk_condition_ko":"349.73 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.57,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":100.57193761229216,"relative_volume":0.9781960677166592,"spread_bps":0.9942828734780131,"day_high":100.58,"day_low":100.56,"execution_condition_ko":"새 일봉에서 100.52~100.55 시험과 100.55 이상 마감 여부를 확인한 뒤 후속 정규장 재시험을 관찰한다. 100.55 위에서만 거래되면 추격하지 않는다. / 100.56은 2026-11-13 고가·종가이며 100.57은 지연된 장전 참고값이다. 어느 가격도 단독 돌파매수 신호가 아니다.","risk_condition_ko":"100.49 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1328.76,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":1311.5209952818072,"relative_volume":0.4326931179894058,"spread_bps":11.213504370632727,"day_high":1332.0,"day_low":1280.0,"execution_condition_ko":"다음 2–5개의 검증된 정규장에서 지지 시험·종가 회복·후속 지지의 순서를 확인한다. 현재 시각이나 이전 종가만으로 조건 충족을 추정하지 않는다. / 조건 충족 후에도 지정가가 1343.07–1347.01 안에 있어야 한다. 범위 위로 갭 상승하거나 지지가 실패하면 매수하지 않는다.","risk_condition_ko":"1,325.16 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":261.8,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":261.48397864329985,"relative_volume":0.6940836174553208,"spread_bps":1.1458910257624078,"day_high":262.92,"day_low":259.03,"execution_condition_ko":"실제 거래일 달력·정규장 운영 여부·새로운 가격 관측을 먼저 확인한다. 2026-11-16 야간 자료는 2026-11-13 종가 반복으로 신규 진입을 활성화하지 못한다. / 유효기한 2026-11-23T23:59:59-05:00은 제공된 현재시각 2026-11-16T04:09:02.592951-05:00보다 뒤다. 이는 달력상 재검토 경계이지 거래소 폐장시각이 아니다. 조건 충족 후에만 활성화하고 미충족 시 자동 연장 없이 만료한다.","risk_condition_ko":"258.53 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1453.375,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":1462.1259638091333,"relative_volume":0.7026535849558491,"spread_bps":5.160402511395889,"day_high":1475.25,"day_low":1452.89,"execution_condition_ko":"1393.56~1403.58: 선호 매수 관찰구간. 회복 종가와 후속 거래일 재시험·종가 유지가 모두 필요하다. / 1419.77~1425.55: 인접 지지 관찰만 수행하며 접촉 자체는 매수 사유가 아니다.","risk_condition_ko":"1,393.56 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":159.87,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":159.57529583539292,"relative_volume":1.544989326524196,"spread_bps":0.6254886630174139,"day_high":163.0,"day_low":158.11,"execution_condition_ko":"첫 검토기간은 2026-11-16~2026-11-20이며 2026-11-20까지 재평가한다. 이는 검토 마감이지 주문 만료시각이나 검증된 거래일정이 아니다. 중요 공시·손실한도 도달 시 즉시 앞당긴다. / 158.39~159.22와 148.80~151.01의 종가 반응을 확인한다. 159.22는 장전 잠정 수준이며 151.01은 검증된 매집 지지가 아니다.","risk_condition_ko":"158.39 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":76.3399,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":76.50604409915358,"relative_volume":0.469062461426282,"spread_bps":1.3100150651739195,"day_high":76.8801,"day_low":76.2691,"execution_condition_ko":"76.18 지지와 76.54–76.70 회복 구간을 확인된 일봉으로 관찰한다. 지연된 장전 관측을 조건 충족으로 처리하지 않는다. / 77.21 회복·재시험과 79.05 위 종가·후속 지지 유지를 확인한다. 이후 80.60과 81.91–82.20을 새 손절 구조와 비교하며 자동 매수하지 않는다.","risk_condition_ko":"76.18 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":379.205,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":377.6439642184918,"relative_volume":1.1837359179079263,"spread_bps":8.438818565400663,"day_high":385.469,"day_low":372.46,"execution_condition_ko":"최신 가격으로 379.84–380.33을 점검하되 지연 장전 관측을 일봉 지지 실패로 처리하지 않는다. / 401.67 상회 종가와 다음 거래일 400.25–401.67 지지 확인 시 신속히 재평가한다. 자동 매수는 아니다.","risk_condition_ko":"379.84 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":341.9698,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":342.6093030761579,"relative_volume":0.3864266229617547,"spread_bps":14.911626683039952,"day_high":347.3,"day_low":340.0,"execution_condition_ko":"344.22~347.58 지지와 344.22 미만 종가 여부를 점검한다. 지연되고 거래가 희박한 장전 342.65만으로 지지 붕괴를 확정하지 않는다. / 첫 지지 실패 시 332.84~340.67, 이후 323.28~326.02를 관찰한다. 가격 하락 자체를 저가 매수 신호로 사용하지 않는다.","risk_condition_ko":"344.22 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":326.325,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":325.47129269601356,"relative_volume":0.8543000629287574,"spread_bps":17.460828010843883,"day_high":332.3586,"day_low":321.16,"execution_condition_ko":"342.61 부근의 일봉 반응을 관찰한다. 보고된 장기 이동평균에 가깝다는 사실만으로 지지를 확정하지 않는다. / 330.42, 325.10 및 315.00–316.91의 하방 반응을 확인한다. 지지구간 도달 자체는 매수 신호가 아니다.","risk_condition_ko":"330.42 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":288.65,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":289.0083556504648,"relative_volume":0.5807877776562712,"spread_bps":1.0393029741397017,"day_high":294.13,"day_low":285.455,"execution_condition_ko":"291.49–294.05 지지와 다음 거래일 회복 여부를 관찰한다. 이 구간은 상시 매수 구간이 아니다. / 결정 이후 새로 나타나는 298.70–304.97 저항 시험과 298.70 아래 종가를 감시한다. 2026-11-13의 기존 저항 실패를 새 감축 신호로 재사용하지 않는다.","risk_condition_ko":"291.49 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":594.174,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":593.1551790680516,"relative_volume":0.5506655434713862,"spread_bps":2.8612544075953306,"day_high":595.83,"day_low":588.55,"execution_condition_ko":"586.30–590.19 시험, 589.02 이상 반전 종가, 후속 세션의 589.02–590.19 지지 유지 순서를 관찰한다. 단순 접촉은 충분하지 않다. / 실제 매수 가능 구간은 589.02부터 589.25−1주당 왕복비용까지다. 상단 초과 갭은 추격하지 않는다.","risk_condition_ko":"586.3 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1111.42,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":1111.1022806948602,"relative_volume":0.6742915480224588,"spread_bps":6.657011002060155,"day_high":1117.0,"day_low":1104.886,"execution_condition_ko":"1088.98–1092.64 시험, 1092.64 이상 회복 종가, 다음 확인된 정규장 지지 재확인을 순서대로 관찰한다. / 1109.50 돌파와 후속 지지는 추가 검토 신호일 뿐 자동 추가 매수 승인이 아니다. 거래 참여와 이동평균 구조도 갱신한다.","risk_condition_ko":"1,065.91 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":172.285,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":172.70894566693087,"relative_volume":0.6515844477195959,"spread_bps":4.643333913750798,"day_high":173.57,"day_low":171.925,"execution_condition_ko":"167.20은 가장 가까운 하방 경고선이며 자동 매도선은 아니다. 가격 도달만으로 첫 매수를 실행하지 않는다. / 170.52–170.73 저항을 관찰한다. 지연된 장전 고점 171.49는 정규장 돌파나 체결 가능한 매매 신호가 아니다.","risk_condition_ko":"165.05 이하 하락, 종가 확인 후 (방어적 매도에는 거래량 확인이 필요하지 않다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WMT","display_name":"WMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":128.21,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":128.87773163525102,"relative_volume":0.6449069363388739,"spread_bps":1.560062402496898,"day_high":129.85,"day_low":127.96,"execution_condition_ko":"2026-11-16부터 2026-11-20까지 확인 가능한 각 일봉을 검토한다. 125.39–126.22 시험 뒤 125.64 이상 종가 회복을 관찰한다. / 다음 검증된 정규장에서 지지가 유지될 때만 125.39–125.64 재시험을 검토한다. 선호 가격은 125.50이며 범위 위로 뛰면 추격하지 않는다.","risk_condition_ko":"123.03 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"KO","display_name":"KO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":99.53,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":100.13021321883296,"relative_volume":0.6933643740440675,"spread_bps":3.014318010550227,"day_high":100.56,"day_low":99.515,"execution_condition_ko":"11/13 일봉의 97.96 접촉과 99.25 종가는 구간 접촉·98.38 이상 회복 조건을 충족했다. 다음 실제 거래일의 완결 일봉 지지는 아직 미확인이다. / 후속 완결 일봉이 97.96 이상으로 마감한 뒤, 이후 거래 가능한 정규장에서 실제 매수가가 97.96~98.38 안에 있을 때만 스타터를 검토한다. 확인 전에 매수하거나 구간 위를 추격하지 않는다.","risk_condition_ko":"97.96 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":429.97,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":429.76029722181255,"relative_volume":0.40824484047456955,"spread_bps":2.093339690884246,"day_high":430.99,"day_low":428.1609,"execution_condition_ko":"지지관찰 구간은 418.69–421.11이다. 일봉 회복 후 다음 확인된 거래일 재시험을 확인하되 실제 매수는 비용 반영 상한 이하에서만 검토한다. / 416.43–416.92는 하락 진행을 관찰할 보조 지지구간이며 자동 추가매수 구간이 아니다.","risk_condition_ko":"418.69 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":665.32,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":666.4626593097997,"relative_volume":0.33445270644661595,"spread_bps":7.665657104636084,"day_high":668.1,"day_low":664.13,"execution_condition_ko":"652~655 시험 후 655 이상 일봉 마감과 다음 실제 거래세션의 구간 재시험을 확인한다. 지지 확인 뒤에도 순보상·위험과 계좌 위험 필터를 통과해야 한다. / 652, 645~646, 638의 종가 조건을 점검한다. 위험 축소에는 신규 매수 현금이나 거래량 증가가 필요하지 않다.","risk_condition_ko":"652 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WELL","display_name":"WELL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":245.715,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":246.64571539671917,"relative_volume":0.24153538721523782,"spread_bps":13.020833333333057,"day_high":247.46,"day_low":245.63,"execution_condition_ko":"242.90~243.49 지지 유지·회복과 240.18~241.78 시험 후 241.78 이상 마감, 후속 정규장 재시험의 순서를 관찰한다. 실제 진입은 비용 조건을 통과한 240.18~241.09 하단부에 한정하고 추격하지 않는다. / 247.27~249.75 및 251.12~253.37에서 종가 반응을 점검한다. 동적 이동평균은 갱신하되 기존 손절을 완화하지 않는다.","risk_condition_ko":"238.17 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"JPM","display_name":"JPM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":343.04,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":343.48986587694185,"relative_volume":0.34269849596460344,"spread_bps":4.0818706630120225,"day_high":346.5116,"day_low":341.81,"execution_condition_ko":"341.85~342.00 시험과 두 단계의 일봉 확인 이후에도 같은 구간에서 체결 가능한지 점검한다. 기회를 주지 않으면 추격하지 않는다. / 347.20 돌파는 단독 매수 신호가 아니다. 352.33 돌파와 지지 전환도 자동 증액 주문이 아니라 재심사 조건이다.","risk_condition_ko":"339.7 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LIN","display_name":"LIN","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":528.245,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":528.5462823020389,"relative_volume":0.43158027468877713,"spread_bps":5.30062092987984,"day_high":530.35,"day_low":526.8675,"execution_condition_ko":"진입 감시: 하단 520.15·상단 521.47에서 새 일봉 회복과 다음 적격 거래일의 지지 재시험을 확인한다. 조건 충족은 매수 의무가 아니다. / 하방 감시: 하단 515.25·상단 516.75 접근은 재평가, 515.25 미만 종가는 25–50% 위험 감축, 510.01 미만 종가는 남은 전술적 보유분 손절로 구분한다.","risk_condition_ko":"515.25 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SO","display_name":"SO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":93.86,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":94.36877918948593,"relative_volume":0.8799411633824472,"spread_bps":4.262120404902105,"day_high":94.7324,"day_low":93.15,"execution_condition_ko":"2026-11-16부터 2026-11-23까지 검증된 일봉과 관련 공시를 점검한다. 조건부 승인은 2026-11-23T23:59:59-05:00에 만료하며 자동 연장하지 않는다. / 공시의 중요 위험 검토, 계좌 여력 및 실행 비용 확인을 먼저 완료한다. 그 뒤 91.83–92.18 시험, 92.18 이상 종가, 다음 검증된 거래일의 지지 확인 순서를 요구한다.","risk_condition_ko":"91.83 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GRAB","display_name":"GRAB","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":3.245,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":3.222853873236515,"relative_volume":0.8568014762095607,"spread_bps":30.816640986131855,"day_high":3.25,"day_low":3.18,"execution_condition_ko":"2026-11-16부터 2026-11-20까지 새 종가 확인과 다음 실제 거래일의 3.20–3.21 되돌림을 관찰한다. 활성화와 체결 모두 2026-11-20T23:59:59-05:00 이전이어야 한다. / 제공된 현재 시각 2026-11-16T05:26:09.535581-05:00은 만료 전이지만, 진입 조건 충족이나 실제 거래 세션을 입증하지 않는다. 기한을 자동 연장하거나 다음 거래일로 이월하지 않는다.","risk_condition_ko":"3.18 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TSLA","display_name":"Tesla","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":381.58,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":381.84052428226164,"relative_volume":0.7266933434546998,"spread_bps":5.503360981170106,"day_high":389.7983,"day_low":376.18,"execution_condition_ko":"382.73–385.26에서 정해진 종가 확인 순서를 추적한다. 확인 후 가격이 범위를 벗어나면 추격하지 않고 기회를 넘긴다. / 397.45–404.40 및 407.46–414.23에서 매물과 남은 손익비를 재평가한다. 더 먼 저항은 확정 목표가 아니다.","risk_condition_ko":"374.74 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BABA","display_name":"BABA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":91.96,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":92.0060074857309,"relative_volume":0.7994900834260927,"spread_bps":2.175805047868824,"day_high":92.6,"day_low":91.38,"execution_condition_ko":"91.98~93.12는 확정 지지가 아닌 관찰 구간이다. 지연 장전의 93.12 하회와 정규장 종가 이탈을 구분한다. / 95.92 위 정규장 종가와 다음 실제 세션 재시험 지지가 확인되면 별도 단기 매수 계획을 재심사한다. 이 신호만으로 소액 매수도 승인하지 않는다.","risk_condition_ko":"91.98 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":297.74,"market_data_asof":"2026-11-16T11:28:00-05:00","session_vwap":298.5444724635862,"relative_volume":0.4463103935734699,"spread_bps":5.038375627698775,"day_high":301.18,"day_low":297.5,"execution_condition_ko":"291.36~293.56 시험 후 292.46 이상 종가 회복과 다음 실제 거래일 지지 유지. 단독 매수 신호가 아니며 목표·손절과 손익비 재산정이 필요하다. / 297.25~298.74 중간 저항과 300.42~302.93 핵심 저항에서의 종가 반응을 확인한다. 저항 도달만으로 매도하지 않는다.","risk_condition_ko":"291.36 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-16T11:28:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:31:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TCEHY","display_name":"TCEHY","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":49.77000045776367,"market_data_asof":"2026-11-16T11:13:00-05:00","session_vwap":49.887518186413,"relative_volume":0.21858373735223036,"spread_bps":null,"day_high":50.02000045776367,"day_low":49.619998931884766,"execution_condition_ko":"위험 대응 조건: 49.25 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"49.25 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-16T11:13:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-16T11:16:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-16T23:13:42.619982+09:00",
  "as_of": "2026-11-13T15:55:00-05:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
