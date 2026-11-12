# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-12T06:10:25.358559+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261112T131230_local-scheduler-kr-overlay_only",
  "producer_finished_at": "2026-11-12T13:38:08.621157+09:00",
  "analysis_run_id": "20261111T044726_local-scheduler-kr-full",
  "analysis_completed_at": "2026-11-11T07:25:38.907432+09:00",
  "analysis_trade_date_oldest": "2026-11-09",
  "analysis_trade_date_latest": "2026-11-09",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-12T13:33:00+09:00",
  "market_data_latest_at": "2026-11-12T13:33:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-12T13:37:57.432395+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-12T13:37:57.432395+09:00",
    "run_started_at": "2026-11-12T13:12:30.738471+09:00",
    "run_finished_at": "2026-11-12T13:38:08.621157+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 7852990,
    "total_unrealized_pnl_krw": -7091246,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 8829642
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1282000,
      "market_value_krw": 2564000,
      "unrealized_pnl_krw": -2871000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 209000,
      "market_value_krw": 2090000,
      "unrealized_pnl_krw": -1233851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 237500,
      "market_value_krw": 1187500,
      "unrealized_pnl_krw": -887143
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 125300,
      "market_value_krw": 501200,
      "unrealized_pnl_krw": -473800
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 423000,
      "market_value_krw": 423000,
      "unrealized_pnl_krw": -730000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 16580,
      "market_value_krw": 298440,
      "unrealized_pnl_krw": -269875
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 182700,
      "market_value_krw": 182700,
      "unrealized_pnl_krw": -99634
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 182400,
      "market_value_krw": 182400,
      "unrealized_pnl_krw": -191767
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 52300,
      "market_value_krw": 156900,
      "unrealized_pnl_krw": -143100
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 95900,
      "market_value_krw": 95900,
      "unrealized_pnl_krw": -76400
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 41750,
      "market_value_krw": 83500,
      "unrealized_pnl_krw": -34700
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 46650,
      "market_value_krw": 46650,
      "unrealized_pnl_krw": -66281
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 40800,
      "market_value_krw": 40800,
      "unrealized_pnl_krw": -13700
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":182400.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":184353.97718413174,"relative_volume":1.8464366068907951,"spread_bps":5.480953685941354,"day_high":189200.0,"day_low":181100.0,"execution_condition_ko":"035420.KS가 179300~180200을 시험한 뒤 180200 이상으로 종가를 형성하고, 다음 실제 거래일에 지지와 구간 내 재시험이 확인되는지 관찰한다. 가격 도달만으로 매수하지 않는다. / 186000과 184900 지지 여부를 관찰한다. 이탈은 하단 구간의 중요성을 높이지만 자동 매수 신호가 아니다.","risk_condition_ko":"179,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":125200.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":124835.06712689271,"relative_volume":1.1488353963877367,"spread_bps":7.984031936127744,"day_high":128700.0,"day_low":118800.0,"execution_condition_ko":"116500~120000원 재시험 후 120000원 이상 마감과 다음 실제 거래일 지지 여부. / 127150~129800원 저항 거절 또는 129800원 위 회복·유지 여부.","risk_condition_ko":"120,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":40800.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":41109.33246786894,"relative_volume":1.3608291070593448,"spread_bps":12.24739742804654,"day_high":42350.0,"day_low":39800.0,"execution_condition_ko":"거래일 여부를 확인하고 누락된 2026-11-10 일봉 및 이후 존재하는 정규장 확정 일봉을 확보한다. 최신 가격 구조에 따라 2026-11-09 기준 수준의 유효성을 재검토한다. / 32,050–32,200원 지지 방어와 36,450원 초과 정규장 종가를 관찰한다. 이후 다음 실제 거래일에 36,150–36,450원이 지지되는지 확인하되 자동 매수로 연결하지 않는다.","risk_condition_ko":"32,050 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1280000.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":1283962.0645825064,"relative_volume":0.7735028730772054,"spread_bps":7.809449433814916,"day_high":1310000.0,"day_low":1254000.0,"execution_condition_ko":"1,116,000원 지지 약화 시 1,089,000원 손절 조건을 우선 점검한다. 그 아래 하락 목표가는 근거가 없어 설정하지 않는다. / 1,193,000원 위 종가와 다음 실제 거래일 1,171,000~1,193,000원 지지를 관찰한다. 이는 매수 승인과 구분하며 1,217,000원 저항을 함께 점검한다.","risk_condition_ko":"1,089,000 이하 하락, 종가 확인 후 (매도에 거래량 확인을 요구하지 않는다.) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":423000.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":420156.04637576954,"relative_volume":1.0198440542639708,"spread_bps":11.813349084465445,"day_high":430000.0,"day_low":403000.0,"execution_condition_ko":"352000원 지지와 346000원 정규장 종가 이탈 여부 확인 / 371500~376500원 회복구간의 후속 정규장 유지 여부 확인","risk_condition_ko":"401,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":209000.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":210507.07284421596,"relative_volume":0.8087176561418072,"spread_bps":23.952095808383234,"day_high":214000.0,"day_low":206000.0,"execution_condition_ko":"005930.KS의 2026-11-09 이후 정규장 일봉, 현재 체결 가능 가격과 실제 거래일 달력을 확인한다. 판단시각 2026-11-11T05:02:02.509740+09:00만으로 거래 세션이나 가격 조건 충족을 확정하지 않는다. / 187000·179200과 기존 손절을 대조하고, 계좌 집중도·레버리지·최근 감축 내역을 확인한다. 기존 손실 한도 대응이 회복 신호 관찰보다 우선한다.","risk_condition_ko":"187,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":238000.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":243354.16224876887,"relative_volume":1.0824936431889194,"spread_bps":20.986358866736623,"day_high":257500.0,"day_low":238000.0,"execution_condition_ko":"2026-11-11부터 2026-11-18까지 확인 가능한 완성 일봉으로 244000~246000원 지지와 237000~238000원 하방 위험을 점검한다. 지지 실패가 이미 발생했다고 가정하지 않는다. / 254000~256000원 회복은 초기 개선으로만 분류한다. 기사상 2026-11-10 종가 251000원과 1.62% 반등은 2026-11-09 지표를 갱신하거나 추세 반전을 확인하지 않는다.","risk_condition_ko":"244,000 이하 하락, 다음 거래일 확인 후 (위험 축소에 거래량 확인 불필요) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":182150.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":181695.48581098355,"relative_volume":1.0661817306721886,"spread_bps":5.489980785067252,"day_high":186300.0,"day_low":177700.0,"execution_condition_ko":"174400원 상회 새 종가는 반등 진전 관찰선이며 단독 매수 신호가 아니다. / 182767원 상회 종가 후 다음 확인된 거래일에 179268~182767원 재시험 지지와 상단 유지를 확인한다. 갱신 가격·유효 손절·비용을 기준으로 보상/위험을 다시 계산한다.","risk_condition_ko":"166,900 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":96200.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":96921.85268673308,"relative_volume":1.69181203246908,"spread_bps":10.400416016640667,"day_high":100700.0,"day_low":90000.0,"execution_condition_ko":"71,200원과 67,800~68,600원에서 지지 유지 및 일봉 저점 상승 여부를 확인한다. 지지 후보 자체는 매수 신호가 아니다. / 79,800원 회복은 초기 안정 신호다. 82,700원 초과 종가와 다음 실제 거래일 80,636~82,700원 지지 또는 재돌파는 배분 관점 재검토 조건이지 자동 매수 조건이 아니다.","risk_condition_ko":"71,200 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":52300.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":52546.37801334006,"relative_volume":0.88076939620492,"spread_bps":19.138755980861244,"day_high":53800.0,"day_low":51300.0,"execution_condition_ko":"058470.KQ 최신 공식 일봉·거래 가능 여부·가격 조정 기준을 확인하고 보도된 48,600원과 48,250원의 시점 및 가격 충돌을 해소한다. / 058470.KQ 45,150~45,550원 방어와 더 높은 저점 형성을 관찰한다. 두 거래일 저가만으로 강한 바닥을 확정하거나 과매도만으로 매수하지 않는다.","risk_condition_ko":"45,150 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":16540.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":16591.888145448902,"relative_volume":0.7842761924560175,"spread_bps":6.044122091266243,"day_high":16800.0,"day_low":16260.0,"execution_condition_ko":"2026-11-11부터 2026-11-18까지 최신 확인된 정규장 일봉으로 15,260~15,320원 유지와 15,880~16,200원 회복을 관찰한다. 저점 구간은 검증된 바닥이나 저가매수 승인이 아니다. / 16,580원 위 종가 돌파와 다음 확인된 거래일 지지 전환을 점검한다. 이동평균 기반 구간은 새 일봉으로 갱신하고 16,960~17,460원 및 18,050원 저항까지의 비용 차감 보상비율을 다시 계산한다.","risk_condition_ko":"15,260 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":46750.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":47114.079871078866,"relative_volume":0.7512410157957771,"spread_bps":10.700909577314071,"day_high":48000.0,"day_low":46250.0,"execution_condition_ko":"034020.KS 정규장 종가 46,150원 초과 후 다음 확인된 거래일의 45,050~46,150원 재지지 / 48,700~49,300원 반등 거부 여부 또는 해당 저항의 종가 돌파·유지","risk_condition_ko":"42,700 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":41850.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":42460.445251546946,"relative_volume":0.9081659700762746,"spread_bps":11.940298507462687,"day_high":43300.0,"day_low":41800.0,"execution_condition_ko":"083450.KQ의 36,600원 위 정규장 종가 회복과 다음 확인된 거래일의 36,300~36,600원 지지를 관찰한다. 충족해도 자동 매수하거나 소액 선행매수를 활성화하지 않는다. / 39,100~39,608원 회복·지지 여부와 이후 41,173~42,654원, 45,958원 저항을 점검한다. 이동평균 기반 저항은 새 일봉으로 재계산한다.","risk_condition_ko":"33,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"028050.KS","display_name":"028050","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":66100.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":66227.45137287557,"relative_volume":0.5088345701281197,"spread_bps":15.14004542013626,"day_high":67100.0,"day_low":64800.0,"execution_condition_ko":"2026-11-10 이후 완료 일봉, 실제 정규장 일정·거래정지 여부·시세 기준시각을 먼저 확인한다. 제공된 2026-11-11T06:18:10.442889+09:00은 거래 가능성이나 진입 조건 충족을 증명하지 않는다. / 58,300~58,500원 시험 후 종가 회복과 다음 실제 거래일 후속 수요를 확인한다. 가격·거래량·원공시·비용 후 보상·잔여 집중한도가 모두 통과해야 소규모 진입을 허용한다.","risk_condition_ko":"58,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":206000.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":207790.377806497,"relative_volume":0.549867814084514,"spread_bps":24.30133657351154,"day_high":213000.0,"day_low":205000.0,"execution_condition_ko":"068270.KS 최신 완료 일봉, 실제 정규장 일정, 신선한 실행 호가 및 계좌의 현금·종목·업종 여력을 확인한다. / 203500–206000원 안정화는 관찰만 한다. 이 구간만으로 매수하지 않는다.","risk_condition_ko":"200,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003010.KS","display_name":"003010","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":8950.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":9307.850864663085,"relative_volume":0.7011450944559396,"spread_bps":11.179429849077698,"day_high":9780.0,"day_low":8900.0,"execution_condition_ko":"핵심 계약·유동성·계좌 검증과 누락 일봉 점검을 통과한 뒤 8,075~8,140원 지지, 종가 8,140원 이상 회복, 다음 유효 거래일 재시험을 확인한다. 가격 조건만으로 초회가 승인되지는 않는다. / 9,102.60원 종가 회복은 중기 개선 관찰 신호다. 9,500원 상회 종가와 9,400~9,500원 재시험 지지는 별도 매수·증액 계획의 재평가 조건이지 자동 매수 지시가 아니다.","risk_condition_ko":"7,900 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"259960.KS","display_name":"259960","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":198300.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":199358.24357992498,"relative_volume":1.530925555606398,"spread_bps":5.044136191677175,"day_high":203500.0,"day_low":194800.0,"execution_condition_ko":"209000~212000원 시험 후 하락 구간보다 개선된 반등 거래량과 212000원 이상 종가를 확인한다. 다음 실제 거래일에도 지지가 유지되고 같은 가격대에서 체결 가능해야 소액 진입을 검토한다. / 진입 전 첫 저항 221000원까지 비용 차감 상승 여력과 변동성 위험을 다시 비교한다. 209000원에서도 비용 전 비율은 약 1.31배에 불과하므로 하단 접근 자체가 매수 근거는 아니다.","risk_condition_ko":"209,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":171000.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":171916.7484874291,"relative_volume":0.839720154055355,"spread_bps":5.846243788365975,"day_high":175900.0,"day_low":170500.0,"execution_condition_ko":"2026-11-10 및 이후 최신 정규장 일봉·거래량, 수정주가 기준, 실제 거래 가능 세션을 먼저 확인한다. 2026-11-09 종가 182400원은 당시 지지 위에 있었다는 근거일 뿐 현재 가격이 아니다. / 2026-11-10 20:00 기준 야간 지연 대표가 175700원과 상세 봉 176700원은 불일치하므로 현재 지지 붕괴나 진입 충족 근거에서 제외한다.","risk_condition_ko":"180,688 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"036460.KS","display_name":"036460","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":36350.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":36599.21071547053,"relative_volume":0.5949841157670533,"spread_bps":13.745704467353953,"day_high":36950.0,"day_low":36300.0,"execution_condition_ko":"누락된 2026-11-10 일봉과 이후의 신선한 정규장 자료를 확보한다. 2026-11-09 종가 36,750 또는 불일치하는 2026-11-10 20:00 지연 호가를 현재 가격으로 사용하지 않는다. / 실제 실적 발표와 원문 검증 후 36,000–36,050 재시험, 종가 36,050 이상, 다음 확인된 거래일의 해당 구간 지지를 순서대로 확인한다. 조건 충족은 매수 의무가 아니다.","risk_condition_ko":"35,800 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003490.KS","display_name":"003490","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":31400.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":31420.03167280047,"relative_volume":0.6675457617806153,"spread_bps":15.910898965791567,"day_high":31850.0,"day_low":30950.0,"execution_condition_ko":"2026-11-11부터 2026-11-25까지 30,100~30,350원 되돌림과 종가 회복·다음 실제 거래일 지지를 점검한다. 단순 접촉은 매수 신호가 아니다. / 보수적 분석가의 영업이익률 약 -2.86%, 설비투자 대비 영업현금흐름 약 45.8%, 유동비율 약 0.587은 잠정 경고다. 원문 기간·공개시각·범위·단위를 확인하기 전 현재 지급불능이나 확정된 실적 추세로 해석하지 않는다. 공시 3건의 본문과 다음 실적발표 일정도 확보한다.","risk_condition_ko":"30,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"207940.KS","display_name":"207940","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1427000.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":1419948.4240687678,"relative_volume":0.680763482587761,"spread_bps":14.025245441795231,"day_high":1449000.0,"day_low":1390000.0,"execution_condition_ko":"207940.KS의 공식 2026-11-10 일봉과 판단 시점 최신 자료를 확보하여 지지·손절 상태부터 확인한다. 보도된 -2.78%로 공식 종가나 지지 이탈을 역산하지 않는다. / 207940.KS의 증자·주식 수·신주 공급 일정·지분 취득 정정과 가격 조정 기준을 확인한다. 계좌의 잔여 집중도·현금·손실예산도 점검한다.","risk_condition_ko":"1,465,585 이하 하락, 다음 거래일 확인 후 (위험 축소에 거래량 증가 불필요) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"064400.KS","display_name":"LG CNS","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":75200.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":76701.96537349335,"relative_volume":0.781001791334958,"spread_bps":13.289036544850498,"day_high":78800.0,"day_low":75200.0,"execution_condition_ko":"누락된 2026-11-10 일봉, 최신 정규장 종가·거래량, 거래소 달력과 실제 거래 상태부터 확인한다. 지연 대표가 80100원과 마지막 분봉 78700원의 불일치는 현재 돌파의 증거가 아니다. / 74400~74600원 눌림과 두 차례 일봉 확인 후에도 다시 범위로 하락하면 최신 지지와 악재 여부를 재점검한다. 과거 확인만으로 지정가를 방치하지 않는다.","risk_condition_ko":"74,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"128940.KS","display_name":"128940","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":460500.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":464631.1657053185,"relative_volume":2.0875104533062903,"spread_bps":10.851871947911015,"day_high":483000.0,"day_low":452500.0,"execution_condition_ko":"실제 거래일·휴장 여부·종목 거래 상태와 새 정규장 시세를 확인한다. 제공 시각은 거래 가능 상태를 증명하지 않는다. / 457000~465000원 재시험 후 465000원 초과 종가, 다음 실제 거래일 종가 457000원 이상을 순서대로 확인한다.","risk_condition_ko":"457,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"180640.KS","display_name":"180640","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":198000.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":193942.76817427584,"relative_volume":1.567593646889968,"spread_bps":20.181634712411707,"day_high":203750.0,"day_low":185900.0,"execution_condition_ko":"180640.KS의 2026-11-09 이후 정규장 일봉과 신선한 거래 가능 가격을 확보해 가격 공백·조정 기준·보통주 거래 상태를 확인한다. / 180640.KS의 219500원·223500원 미집행 이익실현 조건과 196100원·177400원 위험관리 조건을 각각 점검한다.","risk_condition_ko":"219,500 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"036930.KQ","display_name":"주성엔지니어링","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":171650.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":175978.8788423212,"relative_volume":1.6129337372170256,"spread_bps":5.825808330905913,"day_high":181500.0,"day_low":170400.0,"execution_condition_ko":"위험 대응 조건: 141,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"141,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"222800.KQ","display_name":"심텍","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":124800.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":126251.56677110797,"relative_volume":1.4393365208256772,"spread_bps":8.016032064128256,"day_high":129800.0,"day_low":121200.0,"execution_condition_ko":"위험 대응 조건: 97,100 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"97,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000810.KS","display_name":"000810","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":525500.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":538849.6324948826,"relative_volume":1.8342220420243045,"spread_bps":19.029495718363464,"day_high":564000.0,"day_low":523000.0,"execution_condition_ko":"위험 대응 조건: 590,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"590,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"030530.KQ","display_name":"030530","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":30650.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":31319.46290105621,"relative_volume":0.8154224377657915,"spread_bps":16.299918500407497,"day_high":32100.0,"day_low":30250.0,"execution_condition_ko":"위험 대응 조건: 26,550 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"26,550 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"036540.KQ","display_name":"036540","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":8760.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":8538.91242979543,"relative_volume":2.1432159657505827,"spread_bps":11.409013120365088,"day_high":8860.0,"day_low":8230.0,"execution_condition_ko":"위험 대응 조건: 6,540 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"6,540 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"015760.KS","display_name":"015760","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":30200.0,"market_data_asof":"2026-11-12T13:33:00+09:00","session_vwap":30416.75019193711,"relative_volume":1.1828271804266688,"spread_bps":16.570008285004143,"day_high":30800.0,"day_low":30000.0,"execution_condition_ko":"위험 대응 조건: 29,300 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"29,300 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-12T13:33:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-12T13:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-12T13:47:56.938698+09:00",
  "as_of": "2026-11-12T13:33:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
