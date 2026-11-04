# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-04T01:34:27.694764+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261104T102947_local-freshness-kr-overlay",
  "producer_finished_at": "2026-11-04T10:31:11.535600+09:00",
  "analysis_run_id": "20261103T060107_local-scheduler-kr-full",
  "analysis_completed_at": "2026-11-03T08:54:19.761378+09:00",
  "analysis_trade_date_oldest": "2026-10-30",
  "analysis_trade_date_latest": "2026-10-30",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-04T10:30:00+09:00",
  "market_data_latest_at": "2026-11-04T10:30:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-04T10:16:07.737622+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-04T10:16:07.737622+09:00",
    "run_started_at": "2026-11-04T10:15:15.107864+09:00",
    "run_finished_at": "2026-11-04T10:16:16.697813+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 8283360,
    "total_unrealized_pnl_krw": -6660876,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 9260012
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1386000,
      "market_value_krw": 2772000,
      "unrealized_pnl_krw": -2663000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 217500,
      "market_value_krw": 2175000,
      "unrealized_pnl_krw": -1148851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 241500,
      "market_value_krw": 1207500,
      "unrealized_pnl_krw": -867143
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 150300,
      "market_value_krw": 601200,
      "unrealized_pnl_krw": -373800
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 432000,
      "market_value_krw": 432000,
      "unrealized_pnl_krw": -721000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 17170,
      "market_value_krw": 309060,
      "unrealized_pnl_krw": -259255
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 183200,
      "market_value_krw": 183200,
      "unrealized_pnl_krw": -190967
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 167300,
      "market_value_krw": 167300,
      "unrealized_pnl_krw": -115034
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 54200,
      "market_value_krw": 162600,
      "unrealized_pnl_krw": -137400
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 99800,
      "market_value_krw": 99800,
      "unrealized_pnl_krw": -72500
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 41200,
      "market_value_krw": 82400,
      "unrealized_pnl_krw": -35800
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 51400,
      "market_value_krw": 51400,
      "unrealized_pnl_krw": -61531
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 39900,
      "market_value_krw": 39900,
      "unrealized_pnl_krw": -14600
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":148600.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":153787.4098799648,"relative_volume":1.5215784875671894,"spread_bps":6.7272115708039015,"day_high":158600.0,"day_low":148400.0,"execution_condition_ko":"2026-10-30 이후 일별 시가·고가·저가·종가·거래량과 지표를 갱신하고 2026-11-02 보도 종가 160,600과 조정 기준을 대조한다. 지연된 20:00 자료는 현재 호가가 아니다. / 153,700–155,200 눌림, 이후 155,200 이상 종가, 다음 확인된 거래일의 구간 지지를 순서대로 관찰한다. 가격 접촉이나 보도된 반등만으로 매수하지 않는다.","risk_condition_ko":"153,700 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":17100.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":17537.380452830435,"relative_volume":2.445996372549044,"spread_bps":5.846243788365975,"day_high":18050.0,"day_low":16900.0,"execution_condition_ko":"2026-11-02 공식 일봉 가격·거래량과 이후 자료를 확보한다. 보도된 17,120원과 지연 자료의 마지막 17,180원 및 등락률 불일치를 해소하며 어느 값도 현재 체결가로 사용하지 않는다. / 단기 지수이동평균, 거래량가중이동평균, 50일 이동평균과 중간 저항선을 갱신한다. 17,320원 초과 종가와 다음 실제 거래일의 17,260–17,320원 지지를 확인한다.","risk_condition_ko":"15,320 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1375000.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":1427108.7537735072,"relative_volume":1.4286792624044056,"spread_bps":7.26480203414457,"day_high":1476000.0,"day_low":1375000.0,"execution_condition_ko":"1381000~1399000원 지지와 저점 상승을 감시한다. 지지구간 접촉만으로 매수하지 않으며 1449000원 회복도 초기 점검에 불과하다. / 1495000원 종가 돌파와 거래량 개선, 다음 정규장 재시험·종가 확인, 이후 1479000~1495000원 지지 재확인을 순서대로 확인한다.","risk_condition_ko":"1,381,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":427500.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":442794.0501062642,"relative_volume":1.3393906777038371,"spread_bps":11.702750146284377,"day_high":459500.0,"day_low":427000.0,"execution_condition_ko":"418,000원 방어·종가 이탈 여부를 최신 정규장 일봉으로 확인한다. 위험한도를 지킬 수 없으면 보유 없이 관찰한다. / 431,500~440,500원과 447,000~462,500원 순차 회복을 관찰하되 매수 승인으로 해석하지 않는다.","risk_condition_ko":"418,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":181900.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":187035.1964743777,"relative_volume":1.4478252491342283,"spread_bps":5.496015388843088,"day_high":191000.0,"day_low":181800.0,"execution_condition_ko":"한국시간 2026-11-03~2026-11-10에 공식 일봉과 원공시를 갱신한다. 2026-11-10은 재검토일이지 주문 만료일이나 확인된 거래일이 아니다. / 181100~184000원 종가 지지 형성을 관찰하되 지지만으로 신규 매수하지 않는다.","risk_condition_ko":"181,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":41150.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":41759.27597641857,"relative_volume":1.0789169102178826,"spread_bps":12.158054711246201,"day_high":42700.0,"day_low":41100.0,"execution_condition_ko":"083450.KQ의 42650원 위 종가와 다음 실제 정규거래일 42350~42650원 지지: 회복 관찰 및 약세 강도 재평가. / 44350원 위 종가와 정규장 거래량 개선, 이후 44200~44350원 지지: 근거·비용 반영 손익비 재평가. 자동 매수하지 않는다.","risk_condition_ko":"40,550 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":216500.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":222082.4312828619,"relative_volume":1.229721291867256,"spread_bps":23.06805074971165,"day_high":228000.0,"day_low":216000.0,"execution_condition_ko":"005930.KS의 누락된 2026-11-02 일봉과 최신 확인 정규장 자료를 확보하고, 수정주가와 실제 주문가격의 기준 및 거래 가능 여부를 대조한다. / 005930.KS의 220000~222776 방어와 216500 종가 이탈 여부를 신규 매수 검토보다 먼저 확인한다.","risk_condition_ko":"237,323 이하 하락, 종가 확인 후 (위험 축소에 거래량 조건 없음.) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":240500.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":245222.19608659451,"relative_volume":1.303615911944478,"spread_bps":20.811654526534863,"day_high":252000.0,"day_low":239500.0,"execution_condition_ko":"266500원 회복은 첫 점검 신호일 뿐 매수나 축소 취소 조건이 아니다. / 종가 279000원 이상과 다음 확인된 정규거래일의 272000~279000원 지지 유지는 미집행 축소와 약세 강도 재평가 조건이다.","risk_condition_ko":"266,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":167100.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":169317.12440892952,"relative_volume":1.2285465373051916,"spread_bps":5.986231667165519,"day_high":172400.0,"day_low":166700.0,"execution_condition_ko":"170,700~171,100 지지대의 종가 유지와 이탈 후 다음 실제 거래일 종가 회복 여부를 우선 확인한다. / 174,800~175,400 및 176,400~178,000 반등 구간 진입 후 하단 미만 종가 복귀 여부를 확인해 추가 축소 조건을 판정한다.","risk_condition_ko":"170,700 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":99900.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":103699.88317291457,"relative_volume":3.4128057640453906,"spread_bps":10.005002501250624,"day_high":109000.0,"day_low":99300.0,"execution_condition_ko":"2026-11-02 및 이후 최신 정규장 일봉·체결 가능 가격을 확보하고 실제 KRX 거래일·휴장 여부를 확인한다. 2026-11-03T07:01:46.853489+09:00이라는 판단 시각만으로 세션이나 신호 충족을 추정하지 않는다. / 120300원 초과 종가와 다음 실제 거래일 119700~120300원 지지 유지, 잔여 위험한도 충족 시 추가 위험축소 종료를 검토한다. 신규매수는 별도 판단이다.","risk_condition_ko":"114,300 이하 하락, 종가 확인 후 (거래량 증가를 요구하지 않음) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":54200.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":55234.04388641301,"relative_volume":0.9052607448140225,"spread_bps":18.467220683287163,"day_high":56100.0,"day_low":54100.0,"execution_condition_ko":"55,200~55,500원 종가 회복과 56,100원 초과 여부를 초기 개선 신호로 관찰한다. 자동 매수 조건은 아니다. / 57,700원 초과 종가 후 다음 실제 거래세션의 지지 또는 재돌파를 확인한다. 58,900원까지 여유는 57,700원 기준 약 2.1%에 불과하므로 실제 진입가·손절가·비용으로 보상 대비 위험을 다시 계산한다.","risk_condition_ko":"55,200 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":51100.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":52560.806969392506,"relative_volume":1.2802710249830798,"spread_bps":19.58863858961802,"day_high":54000.0,"day_low":50700.0,"execution_condition_ko":"034020.KS의 52,400~52,500원 지지 후보 방어 여부를 확인한다. 아직 바닥 확정은 아니다. / 034020.KS의 55,700~55,800원 종가 회복 또는 중요한 원문 공시 확인 시 약세 근거를 조기 재점검한다. 단독 매수 승인은 아니다.","risk_condition_ko":"52,400 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":39900.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":40850.22614177243,"relative_volume":1.087224311933925,"spread_bps":12.539184952978058,"day_high":41650.0,"day_low":39800.0,"execution_condition_ko":"공식 2026-11-02 일봉과 이후 최신 정규장 자료를 확보하고 회복·손절 조건의 충족 여부를 먼저 확인한다. 기사별 상승률이나 지연 야간 가격으로 돌파를 확정하지 않는다. / 44900원 이상 종가 이후 다음 실제 거래일 44650-44900원 재시험 지지와 44650원 이상 종가 유지 여부를 확인한다.","risk_condition_ko":"42,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"028050.KS","display_name":"028050","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":64000.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":64497.54465361564,"relative_volume":2.082695772805388,"spread_bps":15.63721657544957,"day_high":65500.0,"day_low":62400.0,"execution_condition_ko":"2026-11-02로 표기된 누락 일봉과 이후 이용 가능한 정규장 자료를 확보해 감축·손절 조건의 선행 충족 여부부터 확인한다. 거래일·휴장·거래 가능 상태와 가격 신선도는 별도로 검증한다. / 최초 확인 종가는 2026-11-03 또는 이후 확인된 실제 정규장에서 형성돼야 한다. 60,100~60,400원 재시험 후 종가 60,400원 이상 회복과 다음 실제 거래일 지지 유지가 필요하며 단순 가격 도달은 매수 신호가 아니다.","risk_condition_ko":"60,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":194900.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":194400.38549672984,"relative_volume":0.7068458725250076,"spread_bps":5.129520389843549,"day_high":196400.0,"day_low":191100.0,"execution_condition_ko":"192100~194000에서 새 일봉 지지와 다음 실제 거래일 유지 여부를 우선 확인한다. 가격 조건뿐 아니라 공시·예정 사건·계좌 위험 점검이 완료돼야 첫 진입을 검토한다. / 189600~190500은 더 깊은 지지 관찰대일 뿐 자동 매수 구간이 아니다. 현재 계획 취소 후에는 새로운 손익비와 위험 기준 없이 재진입하지 않는다.","risk_condition_ko":"192,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":124500.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":126858.2343554649,"relative_volume":1.6537531904192377,"spread_bps":8.028904054596548,"day_high":130900.0,"day_low":124000.0,"execution_condition_ko":"090430.KS는 2026-11-03~2026-11-10의 약 1주 동안 지지 회복형 진입을 관찰한다. 123500~124300원 시험 후 124300원 이상 종가 회복, 다음 실제 거래일 124300~125000원에서만 제한적 첫 진입을 검토한다. / 130700원 종가 회복과 다음 실제 거래일 지지 확인은 추세 개선 재평가 신호이며 자동 추가매수 신호가 아니다.","risk_condition_ko":"123,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"036460.KS","display_name":"036460","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":37300.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":37476.74382114877,"relative_volume":1.5496146367322108,"spread_bps":40.18754186202277,"day_high":37650.0,"day_low":37200.0,"execution_condition_ko":"36300~36450원 방문 후 36450원 이상 종가 회복과 다음 실제 거래일 종가 지지를 순서대로 확인한다. 확인 후 구간을 재방문하면 새로운 악재나 지지 훼손을 다시 점검하고 과거 신호를 기계적으로 재사용하지 않는다. / 37250원 위 종가와 다음 실제 거래일 지지를 관찰하되 첫 돌파만으로 매수하지 않는다. 38100원 위 종가와 다음 실제 거래일 지지가 확인되면 새 목표·손절·비용 후 보상·위험을 설정해 별도 재평가한다.","risk_condition_ko":"36,300 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"271560.KS","display_name":"271560","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":116800.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":116985.39786988671,"relative_volume":0.694612806747988,"spread_bps":8.557980316645272,"day_high":117600.0,"day_low":115700.0,"execution_condition_ko":"111900-112000원 지지 회복과 112000원 이상 종가, 다음 실제 정규 거래일 지지 유지 확인. 가격 도달만으로 매수하지 않는다. / 110800원 미만 종가는 신규 매수 보류, 110100원 미만 종가는 손절성 감축 우선이다.","risk_condition_ko":"110,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000810.KS","display_name":"000810","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":653500.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":656254.4717485791,"relative_volume":1.12939702354202,"spread_bps":15.30221882172915,"day_high":664000.0,"day_low":646000.0,"execution_condition_ko":"2026-10-30 이후 최신 정규장 일봉, 실제 거래일 달력·거래 가능 상태·자료 신선도를 확인한다. 불일치하는 지연 야간 가격은 제외한다. / 최초 진입 전에 핵심 재무 원문과 표시통화·단위·주식 기준을 확인한다. 확인할 수 없으면 신규 대기를 유지한다.","risk_condition_ko":"637,000 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003490.KS","display_name":"003490","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":28950.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":29490.267959340872,"relative_volume":1.872787958268681,"spread_bps":17.28608470181504,"day_high":30100.0,"day_low":28900.0,"execution_condition_ko":"003490.KS의 2026-10-30 이후 전체 누락 일봉·거래량, 최신 공시, 거래 가능 상태와 가격 조정 기준을 우선 점검한다. 중간 무효화가 있었다면 이후 가격 회복만으로 기존 계획을 재사용하지 않는다. / 003490.KS의 26000~26210원 재시험, 26210원 이상 종가 회복과 다음 유효 정규장 지지 유지가 확인되면 비용 후 보상·위험을 재계산해 최대 0.5% 스타터를 검토한다.","risk_condition_ko":"25,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"180640.KS","display_name":"180640","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":187400.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":182363.0679862061,"relative_volume":24.2597344556041,"spread_bps":5.334755934915977,"day_high":199300.0,"day_low":161900.0,"execution_condition_ko":"누락된 2026-11-02 정규장 원시 일봉과 이후 가격·거래량, 실제 거래 가능 상태를 확인한다. 2026-10-30 종가 123900원은 사건 이후의 지지 이탈 증거가 아니며, 기사상 134800원과 장후 144100원도 현재 체결가가 아니다. / 127300~130600원 재시험과 확인 종가·다음 실제 거래일 지지, 집행 근거, 비용 및 체결 여유를 반영한 최소 2배 보상을 함께 확인한다.","risk_condition_ko":"127,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"207940.KS","display_name":"207940","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1415000.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":1419902.2514071295,"relative_volume":0.43097687341754176,"spread_bps":7.069635913750442,"day_high":1432000.0,"day_low":1411000.0,"execution_condition_ko":"207940.KS는 향후 1주간 관찰한다. 2026-11-05 예정 결과의 실제 발표 직후 검토하며, 날짜 도래만으로 진입을 허용하지 않는다. 발표가 확인되지 않거나 핵심 조건 공백이 남으면 대기한다. / 207940.KS는 사건 검토 후 새 일봉의 1395000~1411000원 시험, 1411000원 이상 종가 회복, 다음 실제 거래일 재시험 지지를 순서대로 확인한다.","risk_condition_ko":"1,395,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"011200.KS","display_name":"011200","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":23400.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":23466.905168188503,"relative_volume":0.6500289701438059,"spread_bps":21.390374331550802,"day_high":23700.0,"day_low":23000.0,"execution_condition_ko":"2026-10-30 이후 완료된 정규장 가격을 확보하고 기존 매도 조건 충족 여부부터 확인한다. / 22650–22800원 시험과 22800원 이상 회복 종가 이후 바로 다음 검증 정규장의 22650–22700원 기회를 관찰한다.","risk_condition_ko":"22,650 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":464000.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":481177.8296355295,"relative_volume":2.251941197071087,"spread_bps":10.770059235325794,"day_high":506000.0,"day_low":462500.0,"execution_condition_ko":"531000~541000원 재시험, 541000원 이상 종가 회복과 다음 실제 정규장 지지 유지. 후속 주문 직전에도 지지 실패로 바뀌지 않았는지 재확인한다. / 최초 진입 전 공식 자금 여력과 계좌 위험을 확인한다. 지속적인 현금흐름 회복은 후속 증액에 더 엄격하게 적용한다.","risk_condition_ko":"527,000 이하 하락, 종가 확인 후 (매도에 거래량 확인을 요구하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"028670.KS","display_name":"028670","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":5610.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":5699.905294181704,"relative_volume":0.4534298546578622,"spread_bps":17.809439002671414,"day_high":5780.0,"day_low":5560.0,"execution_condition_ko":"5600~5630원 방어와 5630원 이상 종가를 연속된 두 실제 거래일에서 확인한다. 이후 재접근 때도 최신 지지·악재·호가를 다시 확인하며 과거 신호를 무기한 재사용하지 않는다. / 공식 자료에서 통화·단위·기간, 사용 제한 없는 현금, 가까운 리스·차입 만기, 필수 투자와 이를 충당할 자금원을 확인한다. 한 분기 현금흐름이 음수라는 이유만으로 자동 배제하지 않지만 부족분의 조달 근거가 없으면 매수하지 않는다.","risk_condition_ko":"5,600 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"017670.KS","display_name":"017670","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":76000.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":75951.27482066743,"relative_volume":1.2359983086598219,"spread_bps":13.166556945358789,"day_high":76800.0,"day_low":74800.0,"execution_condition_ko":"017670.KS는 2026-10-30 이후 완결 일봉, 배당 관련 가격 조정 여부, 거래가능 상태와 거래일·휴장·단축장 정보를 먼저 확인한다. 2026-11-02 20:00 표시가 75900원은 현재 체결 근거가 아니다. / 017670.KS 종가 77000원 이상 회복과 다음 실제 거래일 76600원 이상 방어가 확인되면 기술적 위험축소 필요성을 재평가한다. 모든 재무 불확실성의 해소까지 기다릴 필요는 없지만 재탈환만으로 신규매수를 승인하지 않는다.","risk_condition_ko":"76,600 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"017900.KS","display_name":"017900","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":8920.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":9451.333487707147,"relative_volume":7.698406149253517,"spread_bps":11.204481792717086,"day_high":9900.0,"day_low":8810.0,"execution_condition_ko":"2026-10-30보다 최신인 일관된 일봉 가격·거래량을 확보하고 관측 시각, 거래일 여부, 실제 거래 가능 상태를 확인한다. / 8,530–8,633 지지와 8,787 초과 종가, 다음 확인된 정규장의 지지 유지를 관찰한다. 이 조건은 재평가 계기이며 자동 매수가 아니다.","risk_condition_ko":"8,530 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010170.KQ","display_name":"010170","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":12840.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":13334.61256506989,"relative_volume":1.0537981938175642,"spread_bps":7.791195948578107,"day_high":13830.0,"day_low":12820.0,"execution_condition_ko":"2026-10-30 이후 일봉과 거래일정을 갱신하고 각 지지·손절 조건의 실제 충족 여부를 확인한다. / 14,220 상회 종가와 이후 14,054–14,220 지지를 관찰한다. 이는 재평가 신호이며 조건부 매수 주문이 아니다.","risk_condition_ko":"13,590 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":193100.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":192707.09039918962,"relative_volume":1.836259118923306,"spread_bps":5.177323323841574,"day_high":194900.0,"day_low":187500.0,"execution_condition_ko":"189985~190500원 재시험 후 190500원 이상 종가와 다음 실제 정규 거래일 지지 유지: 기술적 재심사 조건이며 현재 매수 허용 신호는 아니다. / 원문 재무·정정 공시·가까운 차입 만기와 상환 재원 확인 및 현실적 첫 저항까지 순보상/위험 1.5배 이상인 새 구조 확인: 소액 진입 계획을 새로 심사한다.","risk_condition_ko":"187,700 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"072950.KQ","display_name":"072950","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":12860.0,"market_data_asof":"2026-11-04T10:30:00+09:00","session_vwap":13802.067408694706,"relative_volume":1.0083875986410178,"spread_bps":7.779074290159471,"day_high":14390.0,"day_low":12800.0,"execution_condition_ko":"위험 대응 조건: 14,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"14,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-04T10:30:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T10:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-03T14:37:22.827855+09:00",
  "as_of": "2026-11-03T14:34:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
