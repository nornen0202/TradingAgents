# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-30T00:53:07.778027+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261030T094817_local-freshness-kr-overlay",
  "producer_finished_at": "2026-10-30T09:49:56.486734+09:00",
  "analysis_run_id": "20261030T050115_local-scheduler-kr-full",
  "analysis_completed_at": "2026-10-30T07:45:48.480457+09:00",
  "analysis_trade_date_oldest": "2026-10-29",
  "analysis_trade_date_latest": "2026-10-29",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-30T09:49:00+09:00",
  "market_data_latest_at": "2026-10-30T09:49:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-30T09:31:27.759865+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-30T09:31:27.759865+09:00",
    "run_started_at": "2026-10-30T09:30:35.052104+09:00",
    "run_finished_at": "2026-10-30T09:31:34.333392+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 8668650,
    "total_unrealized_pnl_krw": -6275586,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 9645302
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1417000,
      "market_value_krw": 2834000,
      "unrealized_pnl_krw": -2601000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 221500,
      "market_value_krw": 2215000,
      "unrealized_pnl_krw": -1108851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 291000,
      "market_value_krw": 1455000,
      "unrealized_pnl_krw": -619643
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 152200,
      "market_value_krw": 608800,
      "unrealized_pnl_krw": -366200
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 428500,
      "market_value_krw": 428500,
      "unrealized_pnl_krw": -724500
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 15850,
      "market_value_krw": 285300,
      "unrealized_pnl_krw": -283015
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 187400,
      "market_value_krw": 187400,
      "unrealized_pnl_krw": -186767
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 174500,
      "market_value_krw": 174500,
      "unrealized_pnl_krw": -107834
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 57300,
      "market_value_krw": 171900,
      "unrealized_pnl_krw": -128100
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 124700,
      "market_value_krw": 124700,
      "unrealized_pnl_krw": -47600
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 42350,
      "market_value_krw": 84700,
      "unrealized_pnl_krw": -33500
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 55100,
      "market_value_krw": 55100,
      "unrealized_pnl_krw": -57831
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 43750,
      "market_value_krw": 43750,
      "unrealized_pnl_krw": -10750
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1415000.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":1426554.3401596309,"relative_volume":2.0273093473384827,"spread_bps":7.069635913750442,"day_high":1446000.0,"day_low":1408000.0,"execution_condition_ko":"위험 대응 조건: 1,479,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"1,479,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":121600.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":126204.75565680764,"relative_volume":3.280839793885317,"spread_bps":8.227067050596462,"day_high":132900.0,"day_low":121200.0,"execution_condition_ko":"위험 대응 조건: 132,500 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"132,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":279500.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":282534.7163188636,"relative_volume":2.625116823006296,"spread_bps":17.873100983020553,"day_high":291500.0,"day_low":272500.0,"execution_condition_ko":"278470.KS의 실제 거래일·세션·최신 가격·호가·거래량가중평균가격·거래량과 거래정지·시장경보 상태를 먼저 확인한다. 전일 지연 자료로 당일 진입을 승인하지 않는다. / 293000원 통과, 재계산한 단기 지수이동평균 회복, 304000원 돌파·재지지를 관찰한다. 307000~319000원과 331500~339000원 매물대를 고려해 새 손절선과 비용 후 보상·위험을 재산정한다.","risk_condition_ko":"272,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":172200.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":173173.3744097906,"relative_volume":1.88061799633092,"spread_bps":5.808887598024978,"day_high":174800.0,"day_low":171600.0,"execution_condition_ko":"최신 정규장에서 178000원 회복 후 177300~178000원 재시험 지지, 당일 거래량가중평균가격 상회와 동시간대 상대거래량 1.2배 이상을 확인한다. 이는 재검토 조건이며 자동 매수 허가는 아니다. / 172100원 및 170900~171100원 지지 반응을 관찰하고, 170900원 실패 확인 시 손절 규칙을 적용한다.","risk_condition_ko":"170,900 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":222500.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":224442.31989685132,"relative_volume":2.1379339988837356,"spread_bps":22.49718785151856,"day_high":229500.0,"day_low":221000.0,"execution_condition_ko":"224994~227160원 지지 형성과 227200원 위 정규장 5분봉 두 개 유지, 당일 거래량가중평균가격 상회 및 검증 가능한 거래량 개선을 관찰한다. 자동 매수 신호는 아니다. / 236900원 회복·재시험 지지와 정규장 종가 유지 시 가격 신호에 따른 위험 축소 필요성을 재평가한다. 사업 검증과 계좌 한도는 별도로 충족해야 한다.","risk_condition_ko":"236,881 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":425500.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":426256.7886223794,"relative_volume":1.303909573689975,"spread_bps":11.757789535567314,"day_high":431500.0,"day_low":421500.0,"execution_condition_ko":"443000~450000원 회복 후 457000원 돌파·재지지, 실제 일중 거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상을 확인한다. 이 조건만으로 매수하지 않는다. / 473000원 및 갱신된 10일 지수이동평균 회복·유지, 상대강도지수 30 초과와 다음 실제 거래일의 지지 지속 여부를 확인한다.","risk_condition_ko":"432,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":186700.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":187911.9401440291,"relative_volume":2.2465657212317343,"spread_bps":5.357621216180016,"day_high":191100.0,"day_low":185800.0,"execution_condition_ko":"189200~189700원 지지 유지와 184000원·182100원 접근을 감시한다. 지지 접근 자체는 매수 신호가 아니다. / 10일 지수이동평균 기준값 201322.7원을 최신 값으로 갱신하고 204500~205350원 저항 통과·지지 전환을 확인한다.","risk_condition_ko":"189,200 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":150200.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":151196.61932066246,"relative_volume":1.4221651450354666,"spread_bps":6.66000666000666,"day_high":153700.0,"day_low":149700.0,"execution_condition_ko":"신선한 정규장 호가, 거래량가중평균가격과 동일 경과시간 기준 상대거래량을 확보한다. 전일 저녁 지연 자료와 비교기준이 맞지 않는 상대거래량 18.84는 진입 근거에서 제외한다. / 163000–165900 회복·재확인과 169200 상회 종가를 관찰하되, 높은 돌파 가격 자체가 손익비를 개선한다고 가정하지 않는다.","risk_condition_ko":"154,300 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":15880.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":15698.378894185591,"relative_volume":3.027758492067946,"spread_bps":6.291286568103176,"day_high":16050.0,"day_low":15320.0,"execution_condition_ko":"010140.KS의 실제 거래일·정규장 시간·거래정지 여부·호가 신선도를 확인한다. 제공된 판단 시각 2026-10-30T05:20:54.163540+09:00은 세션이나 조건 충족을 입증하지 않는다. 10:30은 향후 시험 매수 검토의 최초 시각이지 만료시각이 아니다. / 16270~16300원 회복·재시험 지지와 16440~16510원 저항 통과를 관찰한다. 위험축소 판단 해소와 비용 후 손익비 재설계 전에는 매수하지 않는다.","risk_condition_ko":"16,270 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":57100.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":57498.912209411756,"relative_volume":1.6555796274310284,"spread_bps":17.497812773403325,"day_high":59700.0,"day_low":56200.0,"execution_condition_ko":"60500 방어와 58900~59600 저점 구간 재시험. 현재 지지 이탈은 확인되지 않았다. / 63400~63500 돌파는 관찰 신호일 뿐 매수 허가가 아니다. 65400 회복 후에도 66700~67800 공급대 대비 실제 비용 후 손익구조를 재계산한다.","risk_condition_ko":"60,500 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":55000.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":54822.78179795932,"relative_volume":1.8665813691691517,"spread_bps":18.198362147406733,"day_high":55900.0,"day_low":54000.0,"execution_condition_ko":"034020.KS의 실제 거래일·정규장·거래 가능 상태와 최신 봉의 시간대·간격·가격 조정 기준을 먼저 확인한다. / 57000~57200원 회복 후 재시험 지지와 저점 상승을 관찰한다. 이는 위험 완화의 단서이지 매수 승인 조건 충족이 아니다.","risk_condition_ko":"57,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":43400.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":43582.64024806341,"relative_volume":1.032947087866987,"spread_bps":11.514104778353484,"day_high":44650.0,"day_low":43000.0,"execution_condition_ko":"403870.KQ의 44100원 방어와 44900원 회복을 관찰한다. 44900원은 이미 장중 이탈했으므로 확인된 지지선으로 취급하지 않는다. / 47200~47950원 회복 구간과 47950원 상향 종가·재시험을 관찰한다. 상대거래량 1.2배는 제안된 심사 기준이지 관측값이 아니다.","risk_condition_ko":"44,100 이하 하락, 종가 확인 후 (위험매도에 최소 상대거래량 조건은 없다.) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":42100.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":41971.26338937363,"relative_volume":0.7702768017301189,"spread_bps":11.883541295306001,"day_high":42650.0,"day_low":41400.0,"execution_condition_ko":"거래소 달력·정규장 여부·실제 시세 타임스탬프·당일 거래량가중평균가격·동시간대 비교 거래량을 확인한다. 전일 지연 시세를 당일 돌파 증거로 사용하지 않는다. / 44800~44900원 회복·재지지는 초기 개선 신호로만 관리하고, 46300원에 이어 46800~46900원 저항 소화 여부를 확인한다.","risk_condition_ko":"46,300 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"017670.KS","display_name":"017670","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":74900.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":74585.47108403571,"relative_volume":0.9948639729830348,"spread_bps":13.360053440213761,"day_high":75100.0,"day_low":73900.0,"execution_condition_ko":"017670.KS의 실제 거래일·정규장 운영·휴장 및 조기 종료 여부·시세 기준시각·체결 유동성을 확인한다. 제공 시계 2026-10-30T07:21:38.707780+09:00만으로 세션이나 조건 충족을 확정하지 않는다. / 76900~77400원 회복, 이후 79300원 돌파·재지지와 당일 거래량가중평균가격 상회, 검증된 동시간 상대거래량 1.2 이상을 관찰한다. 77400원의 일봉 거래량가중이동평균 기준은 당일 거래량가중평균가격과 다르다.","risk_condition_ko":"77,400 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"131290.KQ","display_name":"티에스이","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":236000.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":239980.9655338057,"relative_volume":1.6485638247036947,"spread_bps":21.208907741251327,"day_high":249500.0,"day_low":235500.0,"execution_condition_ko":"131290.KQ의 실제 거래일정·정규장 상태·최신 체결·호가·거래량가중평균가격을 검증하고 야간 자료의 가격·봉 간격·거래량 불일치를 해소한다. 2026-10-30T07:20:16.339668+09:00이라는 기준 시각만으로 세션이나 조건 충족을 판단하지 않는다. / 131290.KQ의 267000~268000원 회복·재지지를 하나의 구간으로 평가한다. 중립 분석가의 지적대로 가까운 가격 기준을 별개의 강한 신호로 중복 계산하지 않는다.","risk_condition_ko":"266,970 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"001210.KS","display_name":"001210","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":7440.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":7641.774498162436,"relative_volume":0.6349925746848032,"spread_bps":26.881720430107528,"day_high":7820.0,"day_low":7440.0,"execution_condition_ko":"판단 시각은 2026-10-30T06:17:05.778445+09:00이다. 실제 거래일·정규장 상태·거래 가능 여부와 최신 시각이 붙은 호가는 미확인이다. 지연 야간자료, 요약과 봉 가격 불일치 및 봉 간격 불일치로 실행 조건 충족을 판정하지 않는다. / 7,500–7,520 지지 유지와 7,440 종가 기준을 감시한다. 어느 가격도 보장된 바닥은 아니다.","risk_condition_ko":"7,440 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"039980.KQ","display_name":"039980","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":4625.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":4779.540225888516,"relative_volume":1.095671592283002,"spread_bps":10.804970286331713,"day_high":5030.0,"day_low":4610.0,"execution_condition_ko":"039980.KQ의 실제 거래일·거래 자격·호가 시각·봉 간격을 확인하고, 오래된 5,090원 요약과 5,160원 상세 봉의 차이를 해소한다. / 5,050~5,100원 방어와 5,200~5,300원 회복·재시험을 관찰한다. 상대거래량은 비교 가능한 동시간대 기준으로 확인한다.","risk_condition_ko":"5,050 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"011200.KS","display_name":"011200","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":23100.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":22884.78345085105,"relative_volume":1.6798179895033225,"spread_bps":21.668472372697725,"day_high":23150.0,"day_low":22300.0,"execution_condition_ko":"011200.KS: 21,700~21,750원 부근 안정 이후 22,100원 회복은 재검토 신호이지 자동 매수 조건이 아니다. / 011200.KS: 22,550~22,650원 회복과 단기 추세 안정 여부를 점검한다. 22,850~22,900원 저항이 남아 있다.","risk_condition_ko":"21,700 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":193700.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":193387.80708819977,"relative_volume":0.6439406039763969,"spread_bps":10.325245224574084,"day_high":194500.0,"day_low":192100.0,"execution_condition_ko":"188600~189200원 접근 후 매도 거래량 둔화, 189200원 회복과 연속 두 정규장 5분봉 지지, 장중 거래량가중평균가격 상회 및 동시간대 상대거래량 1.2 이상을 확인한다. 이는 관찰 기준이지 자동 매수 승인이 아니다. / 실제 예상 체결가와 검증된 목표·무효화 가격으로 비용·갭 완충 후 보상·위험 2.0 이상을 확인한다. 기존 189200원·196400원·185600원 구조를 그대로 적용하면 비용 후 기준 미달이므로 계속 대기한다.","risk_condition_ko":"185,600 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000810.KS","display_name":"000810","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":652000.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":650979.0295049988,"relative_volume":1.1251543076399468,"spread_bps":15.349194167306216,"day_high":659000.0,"day_low":640000.0,"execution_condition_ko":"000810.KS의 거래일·정규장·시장경보·정지 여부와 최신 5분봉·거래량가중평균가격·호가·동시간대 상대거래량을 확인한다. 전일 야간 지연 자료나 거래량 0으로 당일 조건 충족·실패를 판단하지 않는다. / 637000~639000에서 하락 거래량 감소 후 반등과 거래량가중평균가격 회복을 관찰한다. 돌파 경로는 661000 초과 연속 5분봉 두 개의 마감·재시험 지지와 동시간대 상대거래량 1.2 이상을 제안 확인기준으로 삼는다.","risk_condition_ko":"625,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"036460.KS","display_name":"036460","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":36800.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":36820.92399294325,"relative_volume":0.8455067885219045,"spread_bps":13.540961408259985,"day_high":37050.0,"day_low":36550.0,"execution_condition_ko":"036460.KS의 실제 거래일·정규세션·거래 가능 상태와 최신 체결·호가·당일 거래량가중평균가격을 확인한다. 기존 요약가 36900원과 마지막 봉 37050원의 불일치를 해소하며 거래량 0을 당일 매도 압력으로 해석하지 않는다. / 36250~36400원에서 실제 지지·재상승을 관찰한다. 거래량가중평균가격 회복과 동시간대 상대거래량 1.5 이상이 나와도 비용 후 보상 대비 위험이 부족하면 대기한다.","risk_condition_ko":"36,250 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"207940.KS","display_name":"207940","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1421000.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":1399189.3461470432,"relative_volume":1.6638832530398588,"spread_bps":7.039774727208729,"day_high":1431000.0,"day_low":1350000.0,"execution_condition_ko":"207940.KS의 실제 거래일·거래상태·호가 시각·스프레드와 조정가격 호환성을 확인한다. / 1,350,000–1,355,000원 지지의 단순 접촉과 이탈 후 회복 실패를 구분한다.","risk_condition_ko":"1,350,000 이하 하락, 장중 확인 시 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":552000.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":542879.738874437,"relative_volume":2.9230107006288706,"spread_bps":18.13236627379873,"day_high":555000.0,"day_low":527000.0,"execution_condition_ko":"006400.KS의 실제 거래일·정규장 시간·거래정지·변동성 완화장치·시장경보와 최신 체결·호가를 확인한다. 기존 장중 자료는 2026-10-29 20:00 한국시간 기준이며 봉 간격과 요약 거래량도 불일치해 주문 근거로 사용하지 않는다. / 판단 기준시각은 2026-10-30T06:39:41.282231+09:00이다. 10:30은 최초 소규모 진입 검토 가능시각이지 만료시각이 아니다. 실제 세션·주문 유효기한과 2026-10-30 기사들의 기준시각 이전 공개 여부는 미확인이다.","risk_condition_ko":"528,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":190900.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":190539.53296220335,"relative_volume":1.3706349868543202,"spread_bps":5.239717055279016,"day_high":192600.0,"day_low":188200.0,"execution_condition_ko":"정정 원공시의 통화·단위·기간·주당 기준과 공개 시각을 확인한다. 2026-10-30 기사도 판단 시각 이전 공개 여부를 검증한다. / 187700~188400원에서 저점 상승과 188400원 재회복을 관찰하되 단순 접촉을 지지 성공으로 보지 않는다.","risk_condition_ko":"187,700 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"028050.KS","display_name":"028050","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":61100.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":61836.182162101846,"relative_volume":1.4041842078363376,"spread_bps":16.35322976287817,"day_high":62800.0,"day_low":60800.0,"execution_condition_ko":"위험 대응 조건: 64,900 이상 도달, 장중 확인 시 이익실현성 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"64,900 이상 도달, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"064400.KS","display_name":"LG CNS","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":72500.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":74631.09131020324,"relative_volume":4.523628547915077,"spread_bps":13.802622498274673,"day_high":77800.0,"day_low":71200.0,"execution_condition_ko":"위험 대응 조건: 75,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"75,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"072950.KQ","display_name":"072950","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":15200.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":15439.001696141018,"relative_volume":1.1986675163189617,"spread_bps":6.572461386789353,"day_high":15900.0,"day_low":15060.0,"execution_condition_ko":"위험 대응 조건: 15,250 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"15,250 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010170.KQ","display_name":"010170","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":14170.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":14247.903646701594,"relative_volume":1.4928212570656882,"spread_bps":7.0546737213403885,"day_high":14570.0,"day_low":14010.0,"execution_condition_ko":"위험 대응 조건: 14,600 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"14,600 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000270.KS","display_name":"000270","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":105200.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":105640.21534128534,"relative_volume":1.2575148362280995,"spread_bps":9.501187648456057,"day_high":106400.0,"day_low":104400.0,"execution_condition_ko":"위험 대응 조건: 105,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"105,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"065450.KQ","display_name":"065450","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":3160.0,"market_data_asof":"2026-10-30T09:49:00+09:00","session_vwap":3151.042378585697,"relative_volume":3.605673941245632,"spread_bps":15.860428231562253,"day_high":3255.0,"day_low":3020.0,"execution_condition_ko":"위험 대응 조건: 2,910 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"2,910 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-30T09:49:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-30T09:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-30T06:42:47.839721+09:00",
  "as_of": "2026-10-29T16:14:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
