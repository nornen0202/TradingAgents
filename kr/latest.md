# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-20T05:20:41.182774+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261120T125231_local-scheduler-kr-overlay_only",
  "producer_finished_at": "2026-11-20T13:28:16.017246+09:00",
  "analysis_run_id": "20261120T044759_local-scheduler-kr-full",
  "analysis_completed_at": "2026-11-20T06:40:56.610680+09:00",
  "analysis_trade_date_oldest": "2026-11-18",
  "analysis_trade_date_latest": "2026-11-18",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-20T13:26:00+09:00",
  "market_data_latest_at": "2026-11-20T13:27:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-20T13:28:10.404864+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-20T13:28:10.404864+09:00",
    "run_started_at": "2026-11-20T12:52:31.549407+09:00",
    "run_finished_at": "2026-11-20T13:28:16.017246+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 7064390,
    "total_unrealized_pnl_krw": -7879846,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 8041042
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1106000,
      "market_value_krw": 2212000,
      "unrealized_pnl_krw": -3223000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 183700,
      "market_value_krw": 1837000,
      "unrealized_pnl_krw": -1486851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 240000,
      "market_value_krw": 1200000,
      "unrealized_pnl_krw": -874643
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 110300,
      "market_value_krw": 441200,
      "unrealized_pnl_krw": -533800
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 391500,
      "market_value_krw": 391500,
      "unrealized_pnl_krw": -761500
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 15180,
      "market_value_krw": 273240,
      "unrealized_pnl_krw": -295075
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 162000,
      "market_value_krw": 162000,
      "unrealized_pnl_krw": -120334
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 155900,
      "market_value_krw": 155900,
      "unrealized_pnl_krw": -218267
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 46450,
      "market_value_krw": 139350,
      "unrealized_pnl_krw": -160650
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 49100,
      "market_value_krw": 98200,
      "unrealized_pnl_krw": -20000
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 74500,
      "market_value_krw": 74500,
      "unrealized_pnl_krw": -97800
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 40800,
      "market_value_krw": 40800,
      "unrealized_pnl_krw": -72131
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 38700,
      "market_value_krw": 38700,
      "unrealized_pnl_krw": -15800
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":156000.0,"market_data_asof":"2026-11-20T13:26:00+09:00","market_data_clock_status":null,"session_vwap":158157.0533139897,"relative_volume":0.8611927874469396,"spread_bps":6.408202499198975,"day_high":161400.0,"day_low":155000.0,"execution_condition_ko":"위험 대응 조건: 159,600 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"159,600 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-20T13:26:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:29:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":110300.0,"market_data_asof":"2026-11-20T13:26:00+09:00","market_data_clock_status":null,"session_vwap":111847.95169920567,"relative_volume":0.6123880853223357,"spread_bps":9.062075215224286,"day_high":114900.0,"day_low":110000.0,"execution_condition_ko":"위험 대응 조건: 110,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"110,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-20T13:26:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:29:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":40800.0,"market_data_asof":"2026-11-20T13:26:00+09:00","market_data_clock_status":null,"session_vwap":41287.75122789365,"relative_volume":0.6076149462434419,"spread_bps":12.24739742804654,"day_high":41950.0,"day_low":40700.0,"execution_condition_ko":"위험 대응 조건: 41,550 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"41,550 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-20T13:26:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:29:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":46450.0,"market_data_asof":"2026-11-20T13:26:00+09:00","market_data_clock_status":null,"session_vwap":47362.0209655344,"relative_volume":1.3430774388163194,"spread_bps":10.770059235325794,"day_high":49850.0,"day_low":46400.0,"execution_condition_ko":"실제 정규장 일정과 11월 19일 이후 공식 일봉의 종가·거래량, 주문 시점의 호가를 확인한다. 보도 수익률과 지연 표시값을 돌파 확인에 쓰지 않는다. / 50,100원 회복, 51,350원 돌파와 다음 정규장 지지, 일부 실제 출하 재개를 확인한다. 53,800~54,700원 저항대에서는 추격하지 않는다.","risk_condition_ko":"46,150 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T13:26:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:29:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":48600.0,"market_data_asof":"2026-11-20T13:26:00+09:00","market_data_clock_status":null,"session_vwap":48118.09927595988,"relative_volume":2.3567270636129267,"spread_bps":20.554984583761563,"day_high":50300.0,"day_low":46450.0,"execution_condition_ko":"11월 19일 거래소 확정 종가·거래량과 11월 20일 이후 실제 정규장 일정 및 거래 데이터를 확인한다. 11월 20일 05:26:05 한국시간은 계획 만료 전이지만 세션 여부, 시세 신선도나 신호 충족을 증명하지 않는다. / 45,550~45,850원 재시험과 다음 실제 정규장 지지, 갱신된 변동폭 및 예상 체결비용을 확인한다. 50,300원 초과 종가와 다음 거래일 재지지는 별도 재평가 신호이며 자동 매수 조건이 아니다.","risk_condition_ko":"45,550 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T13:26:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:29:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":391000.0,"market_data_asof":"2026-11-20T13:26:00+09:00","market_data_clock_status":null,"session_vwap":396912.8612716763,"relative_volume":0.5747454596510976,"spread_bps":12.779552715654953,"day_high":407500.0,"day_low":389000.0,"execution_condition_ko":"267260.KS의 11월 19일 보도 종가를 동일 수정 기준의 공식 거래소 일봉과 대조하고, 404500원 초과 마감과 다음 정규장의 401700~404500원 재시험을 순서대로 확인한다. / 효성중공업·LS일렉트릭 대비 상대 강세와 종목별 외국인 순매수가 여러 정규장에서 지속되는지 확인한다. 하루 반등이나 뉴스에서 추론한 심리를 지속적인 매수세로 보지 않는다.","risk_condition_ko":"369,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T13:26:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:29:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":15190.0,"market_data_asof":"2026-11-20T13:26:00+09:00","market_data_clock_status":null,"session_vwap":15379.516600075069,"relative_volume":0.5518454172579403,"spread_bps":6.585446163977609,"day_high":15610.0,"day_low":15180.0,"execution_condition_ko":"한국투자증권의 2026-11-18까지 한국거래소 수정 일봉 248개를 기준으로 15,260~15,360원 지지와 16,350~16,480원 저항을 추적한다. 이후 정규장 일봉, 거래소 일정 및 실제 정규장 여부, 시세 신선도와 수정 일봉·실제 주문가의 가격 기준 일치를 실행 전에 확인한다. 2026-11-19 20:00 한국시간 지연 야간봉의 16,090원은 정규장 신호가 아니다. / 2026-11-20T05:02:04.596697+09:00 기준 검토 기한은 남았지만 진입 조건은 확인되지 않았다. 16,500원을 넘거나 17,010~17,280원 저항에 급접근하면 추격하지 않는다. 2026-11-27T23:59:59+09:00까지 조건 미충족 또는 미체결이면 연장하지 않고 최신 일봉으로 재평가한다.","risk_condition_ko":"15,260 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T13:26:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:29:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1106000.0,"market_data_asof":"2026-11-20T13:26:00+09:00","market_data_clock_status":null,"session_vwap":1109612.677041885,"relative_volume":0.7222582750599007,"spread_bps":9.045680687471732,"day_high":1124000.0,"day_low":1096000.0,"execution_condition_ko":"2026-11-18 반등 범위 1,108,000~1,173,000원: 하단 종가 이탈은 반등 약화, 상단 회복은 관찰 신호다. / 첫 저항 1,192,000~1,201,000원은 관찰 전용이다. 두 번째 저항 1,244,000~1,264,000원의 돌파와 다음 정규장 지지, 그 위 검증 가능한 저항을 추적한다.","risk_condition_ko":"1,089,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T13:26:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:29:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":239500.0,"market_data_asof":"2026-11-20T13:26:00+09:00","market_data_clock_status":null,"session_vwap":239407.28268781365,"relative_volume":0.5410114165369939,"spread_bps":20.898641588296762,"day_high":245000.0,"day_low":235500.0,"execution_condition_ko":"243,500~244,500원 회복과 거래량 개선은 초기 반등 관찰 신호다. 244,500원에서 첫 저항 251,000원까지 6,500원은 평균 실제 변동폭보다 작아 추격하지 않는다. / 259,500원 초과 정규장 종가와 거래량 개선, 바로 다음 실제 정규장의 251,000~256,000원 재시험을 순서대로 확인한다.","risk_condition_ko":"231,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T13:26:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:29:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":183800.0,"market_data_asof":"2026-11-20T13:26:00+09:00","market_data_clock_status":null,"session_vwap":185890.15409064243,"relative_volume":0.8334295228966406,"spread_bps":5.4392167527875985,"day_high":189300.0,"day_low":183000.0,"execution_condition_ko":"거래소 정규장 일정과 최신 완료 일봉의 거래일·수정 기준·거래량을 확인한다. 기준은 2026-11-18 수정 일봉이다. 11월 19일 지연 가격 197,400원은 11월 20일 정규장 신호가 아니다. 주문 전 일봉 기준과 실제 호가의 가격 기준을 대조한다. / 201,500원 회복, 206,000원 돌파, 204,256~206,000원 재지지 순서를 추적한다. 188,800~190,100원 지지대 하단이 깨지면 신규 진입보다 188,800원 회복 여부와 179,200원 재시험 위험을 먼저 본다.","risk_condition_ko":"188,800 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T13:26:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:29:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":38650.0,"market_data_asof":"2026-11-20T13:26:00+09:00","market_data_clock_status":null,"session_vwap":39101.54350278869,"relative_volume":1.2967976307166942,"spread_bps":12.92824822236587,"day_high":40150.0,"day_low":38450.0,"execution_condition_ko":"40,000~40,053원은 11월 19일 야간 참고대일 뿐 당일 지지가 아니다. 이탈하면 38,480~38,610원 시험과 회복을 관찰한다. / 11월 19일에는 동종주도 급등했고 미국 반도체주는 약세였다는 보도가 있었다. 하루 상대 강세를 독자적인 재평가로 보지 말고 업종이 쉬어갈 때도 상대 강세가 이어지는지 확인한다. 기관 순매수의 지속성은 미확인이다.","risk_condition_ko":"35,750 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T13:26:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:29:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":162000.0,"market_data_asof":"2026-11-20T13:26:00+09:00","market_data_clock_status":null,"session_vwap":164067.50386788437,"relative_volume":0.6524643841442906,"spread_bps":6.174745291756715,"day_high":166800.0,"day_low":161900.0,"execution_condition_ko":"166,000~168,000원 지지와 172,700원 이상 종가를 관찰한다. 172,700원 회복은 매수 신호가 아니다. / 181,695원 종가 회복과 다음 확인된 거래일의 지지 이후 187,872원 안착을 확인한다. 212,838원은 장기 추세 기준이지 단기 목표가가 아니다.","risk_condition_ko":"166,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-20T13:26:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:29:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":74600.0,"market_data_asof":"2026-11-20T13:26:00+09:00","market_data_clock_status":null,"session_vwap":76142.13134255006,"relative_volume":0.6259051322154302,"spread_bps":13.395847287340924,"day_high":78400.0,"day_low":74600.0,"execution_condition_ko":"77,500~80,000원 재시험 후 80,000원 이상 정규장 종가와 다음 확인된 거래일의 지지 유지를 관찰한다. 88,300원 돌파만으로 추격하지 않는다. / 91,053~93,400원 저항대 상단을 거래 확대와 함께 종가로 회복하고 다음 거래일에도 지키면 99,600~100,700원까지의 손익비를 재계산한다. 107,415.50원과 114,618원 회복, 50일선 하락세 둔화는 중기 추세 재평가 기준이다.","risk_condition_ko":"77,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-20T13:26:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:29:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003230.KS","display_name":"003230","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1241000.0,"market_data_asof":"2026-11-20T13:27:00+09:00","market_data_clock_status":null,"session_vwap":1247948.764619317,"relative_volume":0.4092153337098574,"spread_bps":8.061265618702137,"day_high":1268000.0,"day_low":1230000.0,"execution_condition_ko":"003230.KS의 11월 19일 공식 정규장 종가, 이후 정규장 일정과 최신 호가, 수정 일봉과 주문 호가의 가격 기준을 확인한다. 1,251,000~1,256,000원 시험 후 종가 회복과 다음 거래일 지지, 또는 거래량을 동반한 돌파와 지지 전환을 감시한다. / 11월 16일 분기보고서 제출은 확인됐지만 원문 표시 통화·단위, 주당 수치의 주식 기준 및 미국예탁증권 대 보통주 환산 비율은 미검증이다. 공급사가 제시한 3분기 세전이익과 영업이익 간 688억 원 차이 및 2분기 잉여현금흐름 128억 원 적자는 잠정 참고치다. 거래 통화로 재무제표 기준을 추정하지 않고 주당이익과 검증되지 않은 선행 주가수익비율은 가치 판단에 쓰지 않는다.","risk_condition_ko":"1,251,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T13:27:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"011200.KS","display_name":"011200","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":22000.0,"market_data_asof":"2026-11-20T13:27:00+09:00","market_data_clock_status":null,"session_vwap":22153.134791557266,"relative_volume":0.4720653617745075,"spread_bps":22.753128555176335,"day_high":22400.0,"day_low":21900.0,"execution_condition_ko":"21,750~21,850원 눌림 뒤 21,850원 이상 정규장 마감과 다음 정규장 지지를 확인한다. 체결 가능가가 21,850~21,900원 밖이거나 비용 차감 후 보상과 갭 위험이 기준을 충족하지 못하면 대기한다. / 22,500~22,650원 저항 상단을 같은 시간대 평소보다 활발한 정규장 거래와 함께 넘고 되밀림에도 지키는지 관찰한다. 상단이 지지로 바뀌면 23,600~23,800원과 24,250원을 점검하되, 22,650원 추격 매수의 첫 후속 저항까지 손익비는 비용 전 약 0.76~0.92배여서 자동 매수하지 않는다.","risk_condition_ko":"21,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T13:27:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"028050.KS","display_name":"028050","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":60500.0,"market_data_asof":"2026-11-20T13:27:00+09:00","market_data_clock_status":null,"session_vwap":61005.8864763905,"relative_volume":0.6435722506132359,"spread_bps":16.515276630883566,"day_high":62200.0,"day_low":60000.0,"execution_condition_ko":"65,207원 상회 정규장 종가, 바로 다음 정규장의 64,675~65,207원 재시험과 64,675원 이상 마감, 이후 구간 내 실제 호가에서 비용 반영 보상 대비 위험 1.4배 이상을 순서대로 확인한다. 조건 불충족 시 신규 자금은 현금으로 유지한다. / 69,700~70,300원 저항을 향해 추격하지 않는다. 61,500원 이탈 뒤 58,300~58,500원은 관찰과 갭 위험 점검에만 쓰며 자동 매수나 손절 완화 기준으로 삼지 않는다.","risk_condition_ko":"61,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T13:27:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":213500.0,"market_data_asof":"2026-11-20T13:26:00+09:00","market_data_clock_status":null,"session_vwap":214597.06024901563,"relative_volume":0.7971771497719684,"spread_bps":23.391812865497077,"day_high":216500.0,"day_low":211000.0,"execution_condition_ko":"11월 19일 이후 실제 정규장 일봉과 거래일정을 확인한다. 11월 19일 3.61% 반등은 코스피 회복과 겹친 시황 보도이고, 같은 날 20:00 한국시간의 지연 표시가 215,000원과 거래량 0주는 11월 20일 정규장 체결 근거가 아니다. / 206,500~208,125원 지지·회복 여부를 우선 관찰한다. 이탈하면 202,000~203,500원을 관찰하되 자동 매수하지 않는다. 215,000~216,000원 저항 돌파와 다음 확인 거래일 방어를 살피되, 216,000원에서 직전 고점 219,000원까지 여유가 작아 대체 매수 신호로 쓰지 않는다.","risk_condition_ko":"206,500 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T13:26:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:29:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":139350.0,"market_data_asof":"2026-11-20T13:27:00+09:00","market_data_clock_status":null,"session_vwap":141384.38451162758,"relative_volume":1.1949727097308174,"spread_bps":7.176175098672408,"day_high":144100.0,"day_low":139100.0,"execution_condition_ko":"090430.KS의 2026-11-19 정규장 종가와 표시값 불일치 원인, 실제 후속 거래일·세션과 최신 정규장 체결을 확인한다. 11월 19일 미국 증시 급락이 국내 수급에 미친 영향은 미확인이다. / 129,590원 회복, 131,206~132,100원 돌파 후 지지, 134,735~134,906원 저항 상단 위 마감을 차례로 본다. 실제 정규장 시초가가 140,000원 위로 갭 상승하면 141,900~142,000원대의 체결과 거래량을 확인하되 추격하지 않는다. 실제 과열이나 상승세 둔화가 확인될 때만 부분 차익실현을 재검토한다.","risk_condition_ko":"126,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T13:27:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"030530.KQ","display_name":"030530","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":31100.0,"market_data_asof":"2026-11-20T13:27:00+09:00","market_data_clock_status":null,"session_vwap":32932.51692410374,"relative_volume":0.8959539669861114,"spread_bps":16.090104585679807,"day_high":34750.0,"day_low":31050.0,"execution_condition_ko":"2026-11-20 06:30:30.796120 한국 표준시 기준 계획은 만료되지 않았다. 실제 정규장 일정과 시세는 미확인이다. 11월 20일부터 확인된 정규장에서 신호를 평가하고, 11월 27일 23:59:59 한국 표준시까지 종가·다음 거래일 지지·유효한 주문 기회가 모두 갖춰지지 않으면 연장하지 않고 재심사한다. 이 기한은 거래소 마감이 아니다. / 35,350원은 11월 18일 수급 비교선이지 확정 지지가 아니다. 거래량이 늘며 그 아래로 밀리거나 외국인·기관이 순매도로 전환되면 경계한다. 11월 19일 미국 기술주 약세의 국내 전이는 미확인이다.","risk_condition_ko":"34,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T13:27:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":181800.0,"market_data_asof":"2026-11-20T13:27:00+09:00","market_data_clock_status":null,"session_vwap":183138.66995073893,"relative_volume":0.8045861418153224,"spread_bps":11.007154650522839,"day_high":185500.0,"day_low":181600.0,"execution_condition_ko":"184,850원 위 종가와 거래량 개선, 다음 정규장 184,500~184,850원 지지를 순서대로 확인한다. 186,040원 위 종가 안착 시 188,200원과 192,000원을 후속 저항으로 본다. 검토기한이 지나면 기존 조건부 진입 계획을 종료하고 자동 연장하지 않는다. / 11월 16일 코스피 대비 6.37%포인트 초과성과가 시장 반등일에도 코스피와 필수소비재 업종 대비 반복되는지 본다. 당시 업종도 강세였으며 기사 논조는 직접 소셜 여론이나 투자자별 순매수의 증거가 아니다. 환율·금리 방향은 미확인이다.","risk_condition_ko":"177,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T13:27:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"018260.KS","display_name":"삼성SDS","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":211000.0,"market_data_asof":"2026-11-20T13:27:00+09:00","market_data_clock_status":null,"session_vwap":210683.6903779295,"relative_volume":0.9165331820376345,"spread_bps":23.72479240806643,"day_high":216500.0,"day_low":204000.0,"execution_condition_ko":"11월 19일 이후 실제 정규장 종가·거래량과 거래일정을 확인해 선행 지지 이탈부터 점검한다. 약세 출발이 확인되면 216,154~217,500원 회복을 관찰하되 그 자체로는 매수하지 않는다. 221,200~221,500원 재시험을 우선하고 239,000~242,500원 저항대에서는 추격하지 않는다. / 공시 3건은 접수만 확인됐다. 공급자의 원화 표시는 원문 증빙이 아니며, 재무제표 표시 통화·단위·주당 기준과 미국예탁증권 대 보통주 환산 비율은 미검증이다. 재무 금액과 주당순이익 비교, 예탁증권 환산, 예상 주가수익비율에 근거한 가치평가는 하지 않는다.","risk_condition_ko":"216,154 이하 하락, 종가 확인 후 (거래량 확인 불필요.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T13:27:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"086790.KS","display_name":"086790","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":124500.0,"market_data_asof":"2026-11-20T13:27:00+09:00","market_data_clock_status":null,"session_vwap":125505.12618206187,"relative_volume":0.8661013456826602,"spread_bps":8.028904054596548,"day_high":126800.0,"day_low":122200.0,"execution_condition_ko":"2026년 11월 20일 한국시간 06:24:30.574338 현재 계획은 미만료이나 발동은 미확인이다. 마지막 검증 일봉은 11월 18일 수정종가 124,200원이다. 11월 20일 06:13 조회된 123,900원·거래량 0주는 11월 19일 20:00 기준 장외 자료다. 실제 거래일·정규장 여부와 최신 정규장 가격을 확인하기 전에는 해당 표시를 주문이나 지지 판단에 쓰지 않는다. / 122,000~122,300원 지지 시험과 다음 실제 거래일 재시험을 확인한다. 127,000원 초과 종가와 다음 거래일 안착은 별도의 재평가 신호다.","risk_condition_ko":"122,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T13:27:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"105560.KS","display_name":"105560","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":152900.0,"market_data_asof":"2026-11-20T13:27:00+09:00","market_data_clock_status":null,"session_vwap":153895.77550471522,"relative_volume":0.7604275411688338,"spread_bps":6.542361792607132,"day_high":155700.0,"day_low":150900.0,"execution_condition_ko":"한국거래소의 실제 거래 일정, 최신 정규장 시세, 11월 18일 수정 일봉과 실주문 가격의 기준을 대조한다. 11월 19일 20:00 한국시간 표시값 152,900원은 검증된 정규장 종가도 11월 20일 체결가도 아니다. / 지지 구간 시험과 다음 거래일 지지 유지, 은행주 대비 상대수익률 개선을 확인한다. 코스피 대비 약세 보도는 은행주 대비 수익률, 투자자 수급, 공매도 또는 실적 악화의 증거로 쓰지 않는다. 확인이 부족하거나 비용 후 손익비가 맞지 않으면 현금을 우선한다.","risk_condition_ko":"152,800 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T13:27:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"180640.KS","display_name":"180640","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":240000.0,"market_data_asof":"2026-11-20T13:27:00+09:00","market_data_clock_status":null,"session_vwap":235678.99155536978,"relative_volume":0.9414454299324769,"spread_bps":20.855057351407716,"day_high":246000.0,"day_low":217500.0,"execution_condition_ko":"한국거래소 일정과 실제 정규장 여부, 11월 19일 이후 누락된 정규장 일봉, 최신 보통주 시세 및 수정주가와 실제 주문가의 기준을 확인한다. 209000원 회복을 우선, 229000원 돌파를 대안으로 관찰한다. / 239000~245000원 저항 반응을 확인한다. 204500원 이탈 뒤에는 196200~200000원과 185900원을 하방 관찰점으로만 본다.","risk_condition_ko":"204,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T13:27:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003490.KS","display_name":"003490","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":31850.0,"market_data_asof":"2026-11-20T13:27:00+09:00","market_data_clock_status":null,"session_vwap":31962.607985658688,"relative_volume":0.6129861968543464,"spread_bps":15.686274509803921,"day_high":32400.0,"day_low":31650.0,"execution_condition_ko":"최신 완료 정규장의 거래일·종가·거래량을 먼저 확인한다. 11월 18일 일봉이 가격 판단의 기준이며, 11월 19일 20:00 한국시간의 32,450원은 거래량 0주의 지연 표시값으로 현재가나 돌파 근거가 아니다. / 30,700~30,950원 재시험과 30,950원 이상 종가를 확인한다. 반등 실패 시 30,100~30,460원은 관찰 구간이지 자동 매수 구간이 아니다. 32,200~32,300원은 첫 저항이며, 32,800원 위 종가와 거래량 증가 및 후속 지지와는 구분한다.","risk_condition_ko":"30,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T13:27:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"064400.KS","display_name":"LG CNS","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":72600.0,"market_data_asof":"2026-11-20T13:27:00+09:00","market_data_clock_status":null,"session_vwap":72652.98804605525,"relative_volume":0.47331033912847753,"spread_bps":13.764624913971094,"day_high":73800.0,"day_low":71700.0,"execution_condition_ko":"2026-11-18 종가 76,800원은 두 이동평균 위였지만 50일선은 200일선 아래였고, 상대강도지수는 61.24에서 53.89로 하락했다. 거래량도 약 75만 주로 앞선 반등일의 156만~164만 주에 못 미쳤다. 이후 한국거래소의 실제 개장 일정, 정규장 종가·거래량과 시세 최신성을 확인해 지지·회복·저항을 다시 점검한다. 11월 19일 20:00 한국시간의 75,000원은 거래량 0주의 비정규장 참고가로 제외한다. / 11월 16일 분기보고서와 10월 30일 잠정실적을 대사하고, 11월 13일 계열사 거래 변경의 금액·조건을 확인한다. 거래통화는 원화이나 재무제표 원문의 표시 통화·금액 단위, 주당순이익의 보통주 기준, 미국예탁증서 대 보통주 환산비와 그 적용 여부는 미확인이다. 동일 공급자의 증감률과 마진만 잠정 사용했으며 재무 절대금액이나 주당순이익은 비교하지 않았다. 전망·시장 예상치·다음 실적 일정은 미확인이고 중요 공시가 나오면 만료 전이라도 재검토한다.","risk_condition_ko":"74,500 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-20T13:27:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034230.KS","display_name":"034230","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":11570.0,"market_data_asof":"2026-11-20T13:26:00+09:00","market_data_clock_status":null,"session_vwap":11706.916320859593,"relative_volume":2.2642253229978038,"spread_bps":8.646779074794638,"day_high":11980.0,"day_low":11430.0,"execution_condition_ko":"11월 18일 수정 종가 10,470원은 하락 중인 200일선 13,399원보다 약 22% 낮다. 11월 11일에도 11,470원을 찍은 뒤 다음 거래일에 6.82% 하락했다. 11월 19일 14:49 보도 가격 11,550원은 장중 값이고 20:00의 11,570원은 거래량이 0으로 표시된 지연 스냅숏이다. 11월 19일 공식 종가와 11월 20일부터의 실제 정규장 일정·가격·거래를 별도로 확인한다. / 공시 원문에서 재무제표 표시통화, 표시 단위, 주당 기준 및 미국예탁증서 대 보통주 비율을 확인한다. 원화 거래와 제공사의 원화 표시는 원공시 검증을 대신하지 않는다. 실적과 예상치 비교는 보도에서 같은 억 원 단위로 제시된 수치에 한정했고, 주당순이익 환산과 기준 시점이 불명확한 선행 주가수익비율은 사용하지 않았다.","risk_condition_ko":"10,200 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-20T13:26:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:29:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003350.KS","display_name":"003350","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":11950.0,"market_data_asof":"2026-11-20T13:26:00+09:00","market_data_clock_status":null,"session_vwap":12870.410839734022,"relative_volume":3.2709965950659385,"spread_bps":8.371703641691084,"day_high":13550.0,"day_low":11890.0,"execution_condition_ko":"판단 시각은 2026-11-20T05:43:36.484421+09:00이며 검증된 일봉은 11월 18일까지다. 11월 19일 정규장 종가·거래량, 11월 20일 실제 세션과 정규장 체결은 미확인이다. 거래소 일정과 정규장 자료를 먼저 대조한다. 11월 19일 현지 20:00 지연 자료는 요약 12,700원과 분봉 종가 12,550원이 다르고 요약 거래량도 0이어서 제외한다. / 11,300~11,700원 회복과 다음 실제 거래일 지지, 12,380~12,610원 및 13,040원 저항, 10,597원 및 10,250~10,290원 지지를 추적한다.","risk_condition_ko":"10,597 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-20T13:26:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:29:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"036460.KS","display_name":"036460","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":37600.0,"market_data_asof":"2026-11-20T13:27:00+09:00","market_data_clock_status":null,"session_vwap":37926.31744628409,"relative_volume":0.35203212549546153,"spread_bps":13.30671989354624,"day_high":38250.0,"day_low":37550.0,"execution_condition_ko":"11월 18일 이후 누락된 정규장 일봉을 우선 확인한다. 11월 19일 20:00 한국시간의 38,150원은 지연 표시가로, 정규장 종가나 현재 체결가가 아니다. 실제 거래일, 정규장 여부, 시세 신선도는 별도로 확인한다. / 37,400~37,700원 지지 확인, 38,150원 이상 회복 종가, 다음 확인 거래일의 회복 유지 순으로 본다. 39,000원 위 종가 돌파는 최근 거래일 대비 거래량 개선과 후속 지지를 관찰하되 자동 증액하지 않는다.","risk_condition_ko":"37,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-20T13:27:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"261780.KQ","display_name":"261780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":5180.0,"market_data_asof":"2026-11-20T13:26:00+09:00","market_data_clock_status":null,"session_vwap":5267.216953778476,"relative_volume":1.4110407454967366,"spread_bps":19.32367149758454,"day_high":5900.0,"day_low":4965.0,"execution_condition_ko":"위험 대응 조건: 4,635 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"4,635 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-20T13:26:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-20T13:29:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-20T13:47:16.046740+09:00",
  "as_of": "2026-11-20T13:26:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
