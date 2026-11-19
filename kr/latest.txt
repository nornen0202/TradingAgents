# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-19T14:34:58.804148+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261119T144409_local-scheduler-kr-overlay_only",
  "producer_finished_at": "2026-11-19T15:37:31.267933+09:00",
  "analysis_run_id": "20261118T044737_local-scheduler-kr-full",
  "analysis_completed_at": "2026-11-18T07:26:58.735506+09:00",
  "analysis_trade_date_oldest": "2026-11-16",
  "analysis_trade_date_latest": "2026-11-16",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-19T14:29:00+09:00",
  "market_data_latest_at": "2026-11-19T14:29:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-19T15:37:26.087094+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-19T15:37:26.087094+09:00",
    "run_started_at": "2026-11-19T14:44:09.511793+09:00",
    "run_finished_at": "2026-11-19T15:37:31.267933+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 7442370,
    "total_unrealized_pnl_krw": -7501866,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 8419022
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1175000,
      "market_value_krw": 2350000,
      "unrealized_pnl_krw": -3085000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 195100,
      "market_value_krw": 1951000,
      "unrealized_pnl_krw": -1372851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 242500,
      "market_value_krw": 1212500,
      "unrealized_pnl_krw": -862143
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 119400,
      "market_value_krw": 477600,
      "unrealized_pnl_krw": -497400
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 412000,
      "market_value_krw": 412000,
      "unrealized_pnl_krw": -741000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 15990,
      "market_value_krw": 287820,
      "unrealized_pnl_krw": -280495
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 168800,
      "market_value_krw": 168800,
      "unrealized_pnl_krw": -205367
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 167800,
      "market_value_krw": 167800,
      "unrealized_pnl_krw": -114534
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 50900,
      "market_value_krw": 152700,
      "unrealized_pnl_krw": -147300
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 46950,
      "market_value_krw": 93900,
      "unrealized_pnl_krw": -24300
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 84000,
      "market_value_krw": 84000,
      "unrealized_pnl_krw": -88300
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 43100,
      "market_value_krw": 43100,
      "unrealized_pnl_krw": -69831
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 41150,
      "market_value_krw": 41150,
      "unrealized_pnl_krw": -13350
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1157000.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":1141123.8902125226,"relative_volume":0.5709397282756988,"spread_bps":8.639308855291576,"day_high":1168000.0,"day_low":1115000.0,"execution_condition_ko":"최신 정규장 일봉으로 1089000~1113000원 지지 유지와 저점 상승을 확인한다. 지연 야간 가격으로 현재 지지 이탈을 선언하지 않는다. / 1242000원 상회 마감 후 다음 실제 거래일 1201000~1242000원 재지지가 확인되면 배분 재평가를 앞당긴다. 이는 자동 매수 조건이 아니다.","risk_condition_ko":"1,089,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":405500.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":396602.2180391583,"relative_volume":0.530401783822925,"spread_bps":24.691358024691358,"day_high":408000.0,"day_low":383000.0,"execution_condition_ko":"267260.KS의 최신 정규장 종가와 거래 가능 상태를 먼저 확인한다. 가격 기준은 2026-11-16 일봉이며 채택된 뉴스는 2026-11-17까지다. / 2026-11-17 20:00+09:00의 376500원과 참고 저가 369000원은 지연 자료다. 현재가·확정 정규장 종가·활성 손절선으로 사용하지 않는다.","risk_condition_ko":"393,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":193100.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":192980.4468524801,"relative_volume":0.5570475401200923,"spread_bps":5.18000518000518,"day_high":196300.0,"day_low":189800.0,"execution_condition_ko":"187,000~189,200원 방어와 저점 갱신 중단을 새 일봉에서 관찰한다. 단독 매수 신호는 아니다. / 195,000~196,800원 회복과 199,800~201,500원 저항 반응을 확인한다.","risk_condition_ko":"187,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":240000.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":238053.6974118442,"relative_volume":0.5119397462691728,"spread_bps":20.855057351407716,"day_high":244000.0,"day_low":233000.0,"execution_condition_ko":"231000~233000원 종가 회복과 다음 실제 정규거래일 재시험 유지 여부. / 243000~246000원 종가 회복은 초기 개선 신호로만 취급하며 단독 매수 신호로 사용하지 않는다.","risk_condition_ko":"231,000 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":165200.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":163068.1540545405,"relative_volume":0.7823699551681439,"spread_bps":6.055101422948834,"day_high":168300.0,"day_low":159600.0,"execution_condition_ko":"178,200~178,500원 종가 회복과 다음 확인된 정규 거래일 재시험 지지 여부. 관찰 강화 조건이며 단독 매수 승인이 아니다. / 181,700~188,200원 저항대 돌파 유지 또는 반등 실패 확인. 추가 회복 시 191,000~193,500원 저항도 함께 평가한다.","risk_condition_ko":"168,300 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":167700.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":168924.07522422442,"relative_volume":0.46502879493290095,"spread_bps":11.918951132300357,"day_high":172400.0,"day_low":167100.0,"execution_condition_ko":"035420.KS: 신선한 정규장 호가 또는 완료 일봉과 거래소 일정을 먼저 확인한다. 2026-11-18T05:21:06.169788+09:00은 실제 세션·휴장 여부·호가 신선도·조건 충족을 증명하지 않는다. 제공된 최신 완료 일봉 이후의 거래 상황은 미확인이다. / 035420.KS: 170700 회복과 168600 이탈을 구별하고, 178300 및 180368–182148에서는 실제 반등 시험 후 실패했는지 확인한다. 저항 아래에 있다는 이유만으로 새 실패 신호를 만들지 않는다.","risk_condition_ko":"168,600 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":116400.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":114871.48761519701,"relative_volume":0.4818844258863246,"spread_bps":8.587376556462,"day_high":117800.0,"day_low":112000.0,"execution_condition_ko":"010120.KS의 최신 완성 일봉, 실제 거래일·정규장 운영·거래정지 여부 및 주문 가능한 호가를 확인한다. 2026-11-18T05:03:33.960910+09:00이라는 판단 시각만으로 거래 가능 상태를 확정하지 않는다. / 2026-11-17 20:00 KST 지연 가격을 현재가나 2026-11-18 지지 확인으로 사용하지 않는다. 가격 근거는 2026-11-16 일봉, 뉴스 근거는 제공된 2026-11-17까지의 자료로 구분한다.","risk_condition_ko":"110,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":80500.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":79886.7819413058,"relative_volume":0.37291485474104724,"spread_bps":12.43008079552517,"day_high":82500.0,"day_low":77900.0,"execution_condition_ko":"92100원 초과 정규장 종가 후 다음 실제 거래일 91800~92100원 지지와 종가 91800원 이상 유지 여부. 충족만으로 매수하지 않는다. / 81600원 및 78200~80100원 구간의 방어·이탈·회복 실패 여부. 이미 충족된 손절은 재평가일까지 유예하지 않는다.","risk_condition_ko":"81,600 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":48850.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":48287.06823121659,"relative_volume":0.5426603031152571,"spread_bps":10.240655401945725,"day_high":49500.0,"day_low":47250.0,"execution_condition_ko":"신선한 일봉으로 48,300원 지지와 45,150~45,550원 저점 구간 방어를 확인한다. 과거 가격이나 지연 호가만으로 조건 충족을 선언하지 않는다. / 51,989~52,200원 회복과 다음 실제 거래일 지지, 53,445~54,700원 저항 소화를 관찰한다. 회복만으로 자동 매수하지 않는다.","risk_condition_ko":"48,300 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":15900.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":15901.318053733141,"relative_volume":0.4056372445306544,"spread_bps":6.287331027978623,"day_high":16060.0,"day_low":15650.0,"execution_condition_ko":"010140.KS의 계획 수립 이후 새로 확인된 정규장 종가가 16584원 이상인지, 다음 확인 거래일에 16470~16584원 지지가 유지되는지 관찰한다. 2026-11-16 종가만으로 새 조건 충족을 선언하지 않는다. / 010140.KS의 17010원·17280원 돌파와 후속 지지, 비교 가능한 일별 거래량 개선을 확인한다. 17460~18050원 저항 및 18739.8원 역사적 50일 평균은 목표가가 아닌 관찰 수준이다.","risk_condition_ko":"15,320 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":42550.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":42356.53024175318,"relative_volume":0.5669845502390713,"spread_bps":11.743981209630064,"day_high":43550.0,"day_low":41700.0,"execution_condition_ko":"034020.KS의 44,900원 초과 정규장 종가로 43,800~44,900원 회복을 관찰하고 다음 실제 거래일 유지 여부를 확인한다. 47,550원은 중간 저항이다. / 48,455~48,850원 회복과 후속 지지 확인 후 50,594~51,700원 공급대까지 거래비용 차감 보상위험을 재계산한다. 거래량 개선과 상대강도지수 30 회복은 보조 근거이며 자동 매수 조건이 아니다.","risk_condition_ko":"42,700 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":39900.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":38983.92821799755,"relative_volume":1.1475597142026495,"spread_bps":12.539184952978058,"day_high":40300.0,"day_low":37850.0,"execution_condition_ko":"403870.KQ: 39,399~40,120원 회복 구간을 감시한다. 40,120원 초과 종가와 다음 실제 거래일의 구간 지지를 확인하고 이동평균 값을 갱신한다. 이는 최초 감축과 약세 판단의 재평가 조건이다. / 403870.KQ: 42,600원 초과 종가와 다음 실제 거래일의 42,600원 초과 종가를 확인하면 기업 근거와 비용 차감 후 손익비를 다시 평가한다. 현재 조건부 매수는 없다.","risk_condition_ko":"39,399 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":44050.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":43050.119799170214,"relative_volume":1.5238542726893456,"spread_bps":11.370096645821489,"day_high":44800.0,"day_low":41000.0,"execution_condition_ko":"2026-11-16 이후 정규장 일봉, 실제 거래 달력·거래 상태와 가격 조정 기준을 확인한다. 2026-11-17 20:00 KST의 지연 야간 가격은 진입 확인에 사용하지 않는다. / 40,600~40,700원 균형과 41,700~42,300원 저항 회복을 관찰하되 독립 매수 신호로 사용하지 않는다.","risk_condition_ko":"39,850 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003230.KS","display_name":"003230","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1242000.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":1248996.791653935,"relative_volume":0.5803179153925733,"spread_bps":8.048289738430583,"day_high":1273000.0,"day_low":1216000.0,"execution_condition_ko":"최신 완료 일봉과 계획 이후 가격 경로를 확보해 1,212,000원 이탈 및 선행 돌파 이후 실패 여부부터 확인한다. 매도 조건이 있으면 매수 검토보다 우선한다. / 최소 재무 점검을 통과하고 1,218,000~1,234,000원에서 회복 종가와 후속 실제 거래일 지지 유지가 확인되면 범위 내 소액 진입을 검토한다. 확인할 수 없으면 해당 유효기간에는 매수하지 않는다.","risk_condition_ko":"1,212,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"028050.KS","display_name":"028050","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":62800.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":63065.47417692491,"relative_volume":0.44268167405479103,"spread_bps":15.936254980079681,"day_high":65100.0,"day_low":61600.0,"execution_condition_ko":"028050.KS의 누락된 2026-11-17 이후 정규장 일봉·거래량과 거래 가능 상태를 먼저 확인한다. 제공된 지연 야간 가격으로 현재 조건 충족을 인정하지 않는다. / 028050.KS의 66,000~67,700원 안정, 66,100원 이상 종가, 다음 실제 거래일 66,000원 지지·저점 상승을 순서대로 확인한다.","risk_condition_ko":"66,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"036460.KS","display_name":"036460","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":38300.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":38400.17156538241,"relative_volume":0.33179402927464563,"spread_bps":39.19007184846506,"day_high":38600.0,"day_low":38100.0,"execution_condition_ko":"036460.KS의 누락된 2026-11-17 일봉과 최신 완료 정규장 자료를 확보한다. 실제 거래일·거래 가능 상태·호가 신선도를 별도로 확인하며 야간 지연 가격으로 조건 충족을 추정하지 않는다. / 37,300~37,600원 지지·반등과 다음 실제 거래일 종가 유지를 확인한다. 실제 비용·갭 여유와 유효 호가단위를 반영했을 때 허용 매수가 남는지 계산한다.","risk_condition_ko":"37,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"086790.KS","display_name":"086790","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":124400.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":124452.0471905854,"relative_volume":0.6005826885294081,"spread_bps":8.041817450743867,"day_high":127000.0,"day_low":122700.0,"execution_condition_ko":"124300–125600에서 지지 시험 후 정규장 종가가 124300 이상인지 확인한다. 다음 실제 거래일에도 지지가 유지되고 매수가가 124300–124600 안에 있을 때만 비용·저항·손실한도를 재심사한다. / 127000 상회 종가와 거래량 개선, 후속 지지 재시험은 돌파 전략의 새 검토 조건이지 자동 매수나 추가매수 지시가 아니다.","risk_condition_ko":"122,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":183800.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":183892.37251567378,"relative_volume":0.5956148494661092,"spread_bps":5.4392167527875985,"day_high":185600.0,"day_low":182000.0,"execution_condition_ko":"175900~177200원 지지 반응, 177200원 이상 회복 종가, 다음 정규장의 175900~176400원 재시험 방어를 순서대로 확인한다. / 180660원 중기 기준선과 181100~182400원 회복 여부를 관찰하되 이 구간 회복만으로 추격하지 않는다.","risk_condition_ko":"170,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":215000.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":212400.40587144083,"relative_volume":0.6271737808938865,"spread_bps":23.28288707799767,"day_high":215000.0,"day_low":207000.0,"execution_condition_ko":"2026-11-17 및 이후 완료된 모든 정규장 시가·고가·저가·종가·거래량, 거래일 달력과 가격조정 기준을 확인한다. 보도된 0.70% 하락만으로 종가를 역산하거나 지연된 야간 자료를 사용하지 않는다. / 2026-11-18 이후 검증된 정규장에서 205000–207200원 지지 시험과 매도 거래량 감소, 반등 거래량 개선 및 207200원 이상 종가를 확인한다. 다음 검증 거래일에도 지지대 유지와 207200원 이상 종가가 필요하다.","risk_condition_ko":"203,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"180640.KS","display_name":"180640","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":225500.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":226760.06448785376,"relative_volume":0.2884048411802948,"spread_bps":22.197558268590456,"day_high":232500.0,"day_low":217000.0,"execution_condition_ko":"203000~204000원, 197600~199100원 또는 194200~195800원에서 매도 압력 감소·종가 회복과 다음 확인된 거래일 지지 유지 여부를 관찰한다. 가격 도달만으로 매수하지 않는다. / 219500원 위 종가와 다음 확인된 거래일 재시험 지지·거래 개선을 확인한다. 223500원 저항과 실제 손절선을 반영해 비용 차감 손익비를 다시 계산한다.","risk_condition_ko":"218,500 이상 도달, 종가 확인 후 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"030530.KQ","display_name":"030530","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":33650.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":33652.91065417724,"relative_volume":1.0077037389757166,"spread_bps":14.847809948032664,"day_high":35500.0,"day_low":32500.0,"execution_condition_ko":"30,400~30,850원 시험 후 30,850원 이상 종가 회복, 다음 실제 거래일 종가 유지, 이후 구간 내 재접근 / 29,770~29,860원 시험 후 29,860원 이상 종가 회복, 다음 실제 거래일 종가 유지, 이후 구간 내 재접근","risk_condition_ko":"29,770 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"018260.KS","display_name":"삼성SDS","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":214500.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":212410.1507909319,"relative_volume":1.6969789747761677,"spread_bps":23.33722287047841,"day_high":232000.0,"day_low":206500.0,"execution_condition_ko":"실행 전 2026-11-16 이후 최신 확정 정규장 일봉과 거래 가능 상태를 확인한다. 이미 지지 이탈이 확인되면 신규 매수보다 위험 축소가 우선이다. / 223,500~226,000원 시험과 226,000원 이상 회복 종가, 반등 거래량 개선, 다음 실제 거래일 재시험 지지를 순서대로 확인한다. 거래량 비교 날짜와 수치를 기록하고 미설정 상대거래량 기준을 충족했다고 주장하지 않는다.","risk_condition_ko":"223,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"002990.KS","display_name":"002990","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":9920.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":9833.785934851561,"relative_volume":0.3918109678537051,"spread_bps":10.085728693898135,"day_high":10100.0,"day_low":9600.0,"execution_condition_ko":"10,390원 또는 10,000~10,015원 접근 후 종가 회복과 다음 거래일 지지를 관찰한다. 단순 접촉은 매수 신호가 아니다. / 11,210원 종가 회복과 실제 다음 거래일 유지 시 전술적 축소 사유를 재평가한다. 갱신된 50일 평균 부근의 지지 전환은 신규 진입 재심사 자료다.","risk_condition_ko":"11,210 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"105560.KS","display_name":"105560","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":154800.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":156197.08545857904,"relative_volume":0.34250038406163474,"spread_bps":6.462035541195477,"day_high":163700.0,"day_low":153200.0,"execution_condition_ko":"105560.KS의 2026-11-17 공식 종가와 이후 이용 가능한 일봉을 최우선 확인한다. 이미 159000원 미만 종가가 있었다면 현 매수 계획은 취소하며 이후 반등만으로 자동 복원하지 않는다. / 159000~159900원 재지지와 다음 실제 거래일 종가 159000원 이상 유지에 더해 수요 개선과 공시 검토가 확인될 때만 해당 범위의 소액 진입을 검토한다. 가격 확인 두 번만으로 충분하다고 보지 않는다.","risk_condition_ko":"159,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"211270.KQ","display_name":"211270","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":9300.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":9366.808835715765,"relative_volume":0.12953951624280843,"spread_bps":42.96455424274973,"day_high":9850.0,"day_low":9010.0,"execution_condition_ko":"최신 정규장 일봉을 확보해 9800원 이상 종가와 다음 실제 거래일의 9750~9800원 재시험·9800원 이상 종가 유지 여부를 확인한다. 충족 전 주문하지 않는다. / 10970~11000원 첫 저항과 11340~11480원 주요 저항을 구분한다. 10200원에서 첫 저항 11000원까지의 거리 800원은 제공 평균진폭 1086.3원보다 작으므로 허용 상한에서 기계적으로 매수하지 않는다.","risk_condition_ko":"9,750 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003490.KS","display_name":"003490","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":32600.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":32412.616037952226,"relative_volume":0.9071708085758139,"spread_bps":15.349194167306216,"day_high":32950.0,"day_low":31650.0,"execution_condition_ko":"주문 전 2026-11-17 이후 최신 완료 일봉, 실제 거래 가능 세션·휴장 및 단축장 달력, 시세 기준시각을 확인한다. 지연 요약가 31950원과 마지막 분봉 31750원은 현재 진입 증거가 아니다. / 원공시의 표시통화, 금액 단위, 기간 길이, 연결범위, 보통주 주당 기준과 예탁증서 환산 여부·비율은 현재 미검증이다. 거래통화가 원화라는 이유로 재무 표시통화를 확정하지 않으며 미검증 재무금액·주당이익·주가수익비율 비교를 투자 근거로 사용하지 않는다. 제공자 손실·낮은 유동성·투자 후 현금부족은 검증 우선순위를 높이는 경고이지 최신 지급불능의 확정 증거가 아니다.","risk_condition_ko":"30,350 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"064400.KS","display_name":"LG CNS","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":74200.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":73580.16331201907,"relative_volume":0.873305079032981,"spread_bps":40.34969737726968,"day_high":78500.0,"day_low":71700.0,"execution_condition_ko":"064400.KS의 누락된 2026-11-17 및 이후 정규장 일봉, 최신 가격, 실제 거래일·세션·거래정지 여부를 확인한다. / 76,500~76,800원 지지 시험과 76,800원 이상 종가 회복, 다음 확인된 정규장의 같은 구간 재시험을 관찰한다.","risk_condition_ko":"75,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"207940.KS","display_name":"207940","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1371000.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":1352216.765578635,"relative_volume":0.4849824353848179,"spread_bps":7.291286912139992,"day_high":1380000.0,"day_low":1338000.0,"execution_condition_ko":"1,390,000~1,401,000원 방어 후 1,401,000원 초과 종가와 다음 확인된 거래일의 지지 유지를 관찰한다. 접근만으로 매수하지 않는다. / 1,444,000~1,468,000원 회복 구간에서 1,468,000원 초과 종가와 후속 지지 여부를 확인한다. 가까운 저항을 향해 추격하지 않는다.","risk_condition_ko":"1,390,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"225190.KQ","display_name":"225190","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":4285.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":4239.912662211227,"relative_volume":0.6889707498568376,"spread_bps":34.944670937682005,"day_high":4430.0,"day_low":4030.0,"execution_condition_ko":"4460~4645에서 매도 압력 약화와 일봉 지지·반등을 확인한다. 아직 확정 지지대가 아니다. / 4735 위 종가와 다음 실제 거래일 재시험 지지를 확인한다. 돌파만으로 매수하지 않는다.","risk_condition_ko":"4,236 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267850.KS","display_name":"267850","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":12970.0,"market_data_asof":"2026-11-19T14:29:00+09:00","market_data_clock_status":null,"session_vwap":13516.41524427999,"relative_volume":1.6143009754480504,"spread_bps":7.707129094412331,"day_high":14450.0,"day_low":12050.0,"execution_condition_ko":"2026-11-18T06:06:01.936984+09:00은 제공된 판단 시각일 뿐 거래일 여부·정규장 상태·가격 신선도·조건 충족을 증명하지 않는다. 주문 전에 이를 각각 확인한다. / 상충하는 지연가격 12,020과 11,540으로 지지 이탈이나 매도 실행을 판정하지 않는다. 12,600–12,700 지지와 13,000 회복을 최신 일봉으로 점검한다.","risk_condition_ko":"12,600 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-19T14:29:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-19T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-19T14:48:30.768754+09:00",
  "as_of": "2026-11-19T14:29:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
