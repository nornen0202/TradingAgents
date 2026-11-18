# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-18T19:51:25.986686+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261118T143232_local-scheduler-kr-overlay_only",
  "producer_finished_at": "2026-11-18T14:49:43.128198+09:00",
  "analysis_run_id": "20261118T044737_local-scheduler-kr-full",
  "analysis_completed_at": "2026-11-18T07:26:58.735506+09:00",
  "analysis_trade_date_oldest": "2026-11-16",
  "analysis_trade_date_latest": "2026-11-16",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-18T14:48:00+09:00",
  "market_data_latest_at": "2026-11-18T14:48:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-18T14:49:37.459348+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-18T14:49:37.459348+09:00",
    "run_started_at": "2026-11-18T14:32:32.211993+09:00",
    "run_finished_at": "2026-11-18T14:49:43.128198+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 7245960,
    "total_unrealized_pnl_krw": -7698276,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 8222612
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1148000,
      "market_value_krw": 2296000,
      "unrealized_pnl_krw": -3139000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 193300,
      "market_value_krw": 1933000,
      "unrealized_pnl_krw": -1390851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 233500,
      "market_value_krw": 1167500,
      "unrealized_pnl_krw": -907143
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 115500,
      "market_value_krw": 462000,
      "unrealized_pnl_krw": -513000
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 381000,
      "market_value_krw": 381000,
      "unrealized_pnl_krw": -772000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 15720,
      "market_value_krw": 282960,
      "unrealized_pnl_krw": -285355
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 170100,
      "market_value_krw": 170100,
      "unrealized_pnl_krw": -112234
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 165900,
      "market_value_krw": 165900,
      "unrealized_pnl_krw": -208267
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 47950,
      "market_value_krw": 143850,
      "unrealized_pnl_krw": -156150
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 41175,
      "market_value_krw": 82350,
      "unrealized_pnl_krw": -35850
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 80900,
      "market_value_krw": 80900,
      "unrealized_pnl_krw": -91400
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 42750,
      "market_value_krw": 42750,
      "unrealized_pnl_krw": -70181
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 37650,
      "market_value_krw": 37650,
      "unrealized_pnl_krw": -16850
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":170100.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":169892.88204001414,"relative_volume":0.5315120490509211,"spread_bps":5.8771672054069946,"day_high":172700.0,"day_low":168000.0,"execution_condition_ko":"위험 대응 조건: 168,600 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"168,600 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":115600.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":115232.85887596953,"relative_volume":0.589561410543923,"spread_bps":8.654262224145391,"day_high":118700.0,"day_low":112100.0,"execution_condition_ko":"위험 대응 조건: 110,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"110,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":15740.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":15704.626175740697,"relative_volume":0.5913129599981458,"spread_bps":6.355258976803305,"day_high":16380.0,"day_low":15360.0,"execution_condition_ko":"위험 대응 조건: 15,320 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"15,320 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":41200.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":41455.37045958185,"relative_volume":1.4610513815085597,"spread_bps":12.12856276531231,"day_high":44250.0,"day_low":39500.0,"execution_condition_ko":"2026-11-16 이후 정규장 일봉, 실제 거래 달력·거래 상태와 가격 조정 기준을 확인한다. 2026-11-17 20:00 KST의 지연 야간 가격은 진입 확인에 사용하지 않는다. / 40,600~40,700원 균형과 41,700~42,300원 저항 회복을 관찰하되 독립 매수 신호로 사용하지 않는다.","risk_condition_ko":"39,850 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1149000.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":1144136.1006401978,"relative_volume":0.8569957206303267,"spread_bps":8.707009142359599,"day_high":1173000.0,"day_low":1108000.0,"execution_condition_ko":"최신 정규장 일봉으로 1089000~1113000원 지지 유지와 저점 상승을 확인한다. 지연 야간 가격으로 현재 지지 이탈을 선언하지 않는다. / 1242000원 상회 마감 후 다음 실제 거래일 1201000~1242000원 재지지가 확인되면 배분 재평가를 앞당긴다. 이는 자동 매수 조건이 아니다.","risk_condition_ko":"1,089,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":193600.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":193761.1432502898,"relative_volume":0.9029945599981528,"spread_bps":5.1666236114699045,"day_high":199950.0,"day_low":188800.0,"execution_condition_ko":"187,000~189,200원 방어와 저점 갱신 중단을 새 일봉에서 관찰한다. 단독 매수 신호는 아니다. / 195,000~196,800원 회복과 199,800~201,500원 저항 반응을 확인한다.","risk_condition_ko":"187,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":234000.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":236303.5977545929,"relative_volume":0.604468478411773,"spread_bps":21.299254526091588,"day_high":243500.0,"day_low":231000.0,"execution_condition_ko":"231000~233000원 종가 회복과 다음 실제 정규거래일 재시험 유지 여부. / 243000~246000원 종가 회복은 초기 개선 신호로만 취급하며 단독 매수 신호로 사용하지 않는다.","risk_condition_ko":"231,000 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":42800.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":42621.739534106775,"relative_volume":0.769308252022125,"spread_bps":11.675423234092236,"day_high":43850.0,"day_low":41550.0,"execution_condition_ko":"034020.KS의 44,900원 초과 정규장 종가로 43,800~44,900원 회복을 관찰하고 다음 실제 거래일 유지 여부를 확인한다. 47,550원은 중간 저항이다. / 48,455~48,850원 회복과 후속 지지 확인 후 50,594~51,700원 공급대까지 거래비용 차감 보상위험을 재계산한다. 거래량 개선과 상대강도지수 30 회복은 보조 근거이며 자동 매수 조건이 아니다.","risk_condition_ko":"42,700 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":381500.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":380678.8193992132,"relative_volume":0.46795866677614467,"spread_bps":13.097576948264571,"day_high":391500.0,"day_low":370000.0,"execution_condition_ko":"267260.KS의 최신 정규장 종가와 거래 가능 상태를 먼저 확인한다. 가격 기준은 2026-11-16 일봉이며 채택된 뉴스는 2026-11-17까지다. / 2026-11-17 20:00+09:00의 376500원과 참고 저가 369000원은 지연 자료다. 현재가·확정 정규장 종가·활성 손절선으로 사용하지 않는다.","risk_condition_ko":"393,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":166100.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":166901.29733488258,"relative_volume":0.7455063426708001,"spread_bps":6.022282445046673,"day_high":172200.0,"day_low":161900.0,"execution_condition_ko":"178,200~178,500원 종가 회복과 다음 확인된 정규 거래일 재시험 지지 여부. 관찰 강화 조건이며 단독 매수 승인이 아니다. / 181,700~188,200원 저항대 돌파 유지 또는 반등 실패 확인. 추가 회복 시 191,000~193,500원 저항도 함께 평가한다.","risk_condition_ko":"168,300 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":80700.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":81751.03998401033,"relative_volume":0.8115370527258102,"spread_bps":12.38390092879257,"day_high":88300.0,"day_low":77500.0,"execution_condition_ko":"92100원 초과 정규장 종가 후 다음 실제 거래일 91800~92100원 지지와 종가 91800원 이상 유지 여부. 충족만으로 매수하지 않는다. / 81600원 및 78200~80100원 구간의 방어·이탈·회복 실패 여부. 이미 충족된 손절은 재평가일까지 유예하지 않는다.","risk_condition_ko":"81,600 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":47950.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":47934.993532762746,"relative_volume":0.6720328133958519,"spread_bps":10.422094841063053,"day_high":50100.0,"day_low":46150.0,"execution_condition_ko":"신선한 일봉으로 48,300원 지지와 45,150~45,550원 저점 구간 방어를 확인한다. 과거 가격이나 지연 호가만으로 조건 충족을 선언하지 않는다. / 51,989~52,200원 회복과 다음 실제 거래일 지지, 53,445~54,700원 저항 소화를 관찰한다. 회복만으로 자동 매수하지 않는다.","risk_condition_ko":"48,300 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":37650.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":36979.902355478574,"relative_volume":0.8389258353714795,"spread_bps":13.289036544850498,"day_high":37900.0,"day_low":35900.0,"execution_condition_ko":"403870.KQ: 39,399~40,120원 회복 구간을 감시한다. 40,120원 초과 종가와 다음 실제 거래일의 구간 지지를 확인하고 이동평균 값을 갱신한다. 이는 최초 감축과 약세 판단의 재평가 조건이다. / 403870.KQ: 42,600원 초과 종가와 다음 실제 거래일의 42,600원 초과 종가를 확인하면 기업 근거와 비용 차감 후 손익비를 다시 평가한다. 현재 조건부 매수는 없다.","risk_condition_ko":"39,399 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003230.KS","display_name":"003230","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1272000.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":1281445.121097578,"relative_volume":0.686922854291018,"spread_bps":15.723270440251573,"day_high":1307000.0,"day_low":1256000.0,"execution_condition_ko":"최신 완료 일봉과 계획 이후 가격 경로를 확보해 1,212,000원 이탈 및 선행 돌파 이후 실패 여부부터 확인한다. 매도 조건이 있으면 매수 검토보다 우선한다. / 최소 재무 점검을 통과하고 1,218,000~1,234,000원에서 회복 종가와 후속 실제 거래일 지지 유지가 확인되면 범위 내 소액 진입을 검토한다. 확인할 수 없으면 해당 유효기간에는 매수하지 않는다.","risk_condition_ko":"1,212,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"028050.KS","display_name":"028050","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":64000.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":63864.12743574954,"relative_volume":1.0980011028331376,"spread_bps":15.63721657544957,"day_high":69900.0,"day_low":61500.0,"execution_condition_ko":"028050.KS의 누락된 2026-11-17 이후 정규장 일봉·거래량과 거래 가능 상태를 먼저 확인한다. 제공된 지연 야간 가격으로 현재 조건 충족을 인정하지 않는다. / 028050.KS의 66,000~67,700원 안정, 66,100원 이상 종가, 다음 실제 거래일 66,000원 지지·저점 상승을 순서대로 확인한다.","risk_condition_ko":"66,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"036460.KS","display_name":"036460","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":38500.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":38308.10918467398,"relative_volume":0.7172244509890934,"spread_bps":12.99545159194282,"day_high":38500.0,"day_low":37700.0,"execution_condition_ko":"036460.KS의 누락된 2026-11-17 일봉과 최신 완료 정규장 자료를 확보한다. 실제 거래일·거래 가능 상태·호가 신선도를 별도로 확인하며 야간 지연 가격으로 조건 충족을 추정하지 않는다. / 37,300~37,600원 지지·반등과 다음 실제 거래일 종가 유지를 확인한다. 실제 비용·갭 여유와 유효 호가단위를 반영했을 때 허용 매수가 남는지 계산한다.","risk_condition_ko":"37,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"086790.KS","display_name":"086790","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":124100.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":123651.17211641268,"relative_volume":0.7762334481330788,"spread_bps":8.054772452678213,"day_high":125200.0,"day_low":122000.0,"execution_condition_ko":"124300–125600에서 지지 시험 후 정규장 종가가 124300 이상인지 확인한다. 다음 실제 거래일에도 지지가 유지되고 매수가가 124300–124600 안에 있을 때만 비용·저항·손실한도를 재심사한다. / 127000 상회 종가와 거래량 개선, 후속 지지 재시험은 돌파 전략의 새 검토 조건이지 자동 매수나 추가매수 지시가 아니다.","risk_condition_ko":"122,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":182200.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":182515.57953675344,"relative_volume":0.738946704971492,"spread_bps":5.486968449931413,"day_high":184500.0,"day_low":177400.0,"execution_condition_ko":"175900~177200원 지지 반응, 177200원 이상 회복 종가, 다음 정규장의 175900~176400원 재시험 방어를 순서대로 확인한다. / 180660원 중기 기준선과 181100~182400원 회복 여부를 관찰하되 이 구간 회복만으로 추격하지 않는다.","risk_condition_ko":"170,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":207500.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":209698.83401151383,"relative_volume":0.621129052099662,"spread_bps":24.1254523522316,"day_high":213000.0,"day_low":206750.0,"execution_condition_ko":"2026-11-17 및 이후 완료된 모든 정규장 시가·고가·저가·종가·거래량, 거래일 달력과 가격조정 기준을 확인한다. 보도된 0.70% 하락만으로 종가를 역산하거나 지연된 야간 자료를 사용하지 않는다. / 2026-11-18 이후 검증된 정규장에서 205000–207200원 지지 시험과 매도 거래량 감소, 반등 거래량 개선 및 207200원 이상 종가를 확인한다. 다음 검증 거래일에도 지지대 유지와 207200원 이상 종가가 필요하다.","risk_condition_ko":"203,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"030530.KQ","display_name":"030530","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":35250.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":34931.182164751095,"relative_volume":2.6538592063196167,"spread_bps":14.194464158977999,"day_high":36750.0,"day_low":32200.0,"execution_condition_ko":"30,400~30,850원 시험 후 30,850원 이상 종가 회복, 다음 실제 거래일 종가 유지, 이후 구간 내 재접근 / 29,770~29,860원 시험 후 29,860원 이상 종가 회복, 다음 실제 거래일 종가 유지, 이후 구간 내 재접근","risk_condition_ko":"29,770 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"018260.KS","display_name":"삼성SDS","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":233500.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":227771.61398646128,"relative_volume":0.5773991425495509,"spread_bps":21.390374331550802,"day_high":234000.0,"day_low":221500.0,"execution_condition_ko":"실행 전 2026-11-16 이후 최신 확정 정규장 일봉과 거래 가능 상태를 확인한다. 이미 지지 이탈이 확인되면 신규 매수보다 위험 축소가 우선이다. / 223,500~226,000원 시험과 226,000원 이상 회복 종가, 반등 거래량 개선, 다음 실제 거래일 재시험 지지를 순서대로 확인한다. 거래량 비교 날짜와 수치를 기록하고 미설정 상대거래량 기준을 충족했다고 주장하지 않는다.","risk_condition_ko":"223,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"105560.KS","display_name":"105560","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":155400.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":154916.87172122154,"relative_volume":0.6141083738715031,"spread_bps":6.43707756678468,"day_high":156700.0,"day_low":152800.0,"execution_condition_ko":"105560.KS의 2026-11-17 공식 종가와 이후 이용 가능한 일봉을 최우선 확인한다. 이미 159000원 미만 종가가 있었다면 현 매수 계획은 취소하며 이후 반등만으로 자동 복원하지 않는다. / 159000~159900원 재지지와 다음 실제 거래일 종가 159000원 이상 유지에 더해 수요 개선과 공시 검토가 확인될 때만 해당 범위의 소액 진입을 검토한다. 가격 확인 두 번만으로 충분하다고 보지 않는다.","risk_condition_ko":"159,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"211270.KQ","display_name":"211270","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":9630.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":9650.259307870252,"relative_volume":0.4571553312000264,"spread_bps":10.378827192527243,"day_high":10160.0,"day_low":9070.0,"execution_condition_ko":"최신 정규장 일봉을 확보해 9800원 이상 종가와 다음 실제 거래일의 9750~9800원 재시험·9800원 이상 종가 유지 여부를 확인한다. 충족 전 주문하지 않는다. / 10970~11000원 첫 저항과 11340~11480원 주요 저항을 구분한다. 10200원에서 첫 저항 11000원까지의 거리 800원은 제공 평균진폭 1086.3원보다 작으므로 허용 상한에서 기계적으로 매수하지 않는다.","risk_condition_ko":"9,750 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003490.KS","display_name":"003490","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":31300.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":31432.157554268848,"relative_volume":0.7016171254976614,"spread_bps":15.987210231814547,"day_high":32200.0,"day_low":30700.0,"execution_condition_ko":"주문 전 2026-11-17 이후 최신 완료 일봉, 실제 거래 가능 세션·휴장 및 단축장 달력, 시세 기준시각을 확인한다. 지연 요약가 31950원과 마지막 분봉 31750원은 현재 진입 증거가 아니다. / 원공시의 표시통화, 금액 단위, 기간 길이, 연결범위, 보통주 주당 기준과 예탁증서 환산 여부·비율은 현재 미검증이다. 거래통화가 원화라는 이유로 재무 표시통화를 확정하지 않으며 미검증 재무금액·주당이익·주가수익비율 비교를 투자 근거로 사용하지 않는다. 제공자 손실·낮은 유동성·투자 후 현금부족은 검증 우선순위를 높이는 경고이지 최신 지급불능의 확정 증거가 아니다.","risk_condition_ko":"30,350 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"064400.KS","display_name":"LG CNS","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":76800.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":77685.75265290187,"relative_volume":0.651116116624359,"spread_bps":13.012361743656475,"day_high":80400.0,"day_low":75450.0,"execution_condition_ko":"064400.KS의 누락된 2026-11-17 및 이후 정규장 일봉, 최신 가격, 실제 거래일·세션·거래정지 여부를 확인한다. / 76,500~76,800원 지지 시험과 76,800원 이상 종가 회복, 다음 확인된 정규장의 같은 구간 재시험을 관찰한다.","risk_condition_ko":"75,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"180640.KS","display_name":"180640","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":223000.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":222535.04481885335,"relative_volume":0.4760554429414278,"spread_bps":22.396416573348265,"day_high":229000.0,"day_low":209000.0,"execution_condition_ko":"203000~204000원, 197600~199100원 또는 194200~195800원에서 매도 압력 감소·종가 회복과 다음 확인된 거래일 지지 유지 여부를 관찰한다. 가격 도달만으로 매수하지 않는다. / 219500원 위 종가와 다음 확인된 거래일 재시험 지지·거래 개선을 확인한다. 223500원 저항과 실제 손절선을 반영해 비용 차감 손익비를 다시 계산한다.","risk_condition_ko":"218,500 이상 도달, 종가 확인 후 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"002990.KS","display_name":"002990","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":10060.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":10337.607472413132,"relative_volume":0.799057438227522,"spread_bps":9.945300845350571,"day_high":10940.0,"day_low":9860.0,"execution_condition_ko":"10,390원 또는 10,000~10,015원 접근 후 종가 회복과 다음 거래일 지지를 관찰한다. 단순 접촉은 매수 신호가 아니다. / 11,210원 종가 회복과 실제 다음 거래일 유지 시 전술적 축소 사유를 재평가한다. 갱신된 50일 평균 부근의 지지 전환은 신규 진입 재심사 자료다.","risk_condition_ko":"11,210 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"225190.KQ","display_name":"225190","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":4185.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":4454.693020000756,"relative_volume":1.4045898715865424,"spread_bps":35.90664272890485,"day_high":4815.0,"day_low":4120.0,"execution_condition_ko":"4460~4645에서 매도 압력 약화와 일봉 지지·반등을 확인한다. 아직 확정 지지대가 아니다. / 4735 위 종가와 다음 실제 거래일 재시험 지지를 확인한다. 돌파만으로 매수하지 않는다.","risk_condition_ko":"4,236 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267850.KS","display_name":"267850","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":12150.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":12204.176981468701,"relative_volume":0.4741779013717538,"spread_bps":16.474464579901152,"day_high":12790.0,"day_low":11650.0,"execution_condition_ko":"2026-11-18T06:06:01.936984+09:00은 제공된 판단 시각일 뿐 거래일 여부·정규장 상태·가격 신선도·조건 충족을 증명하지 않는다. 주문 전에 이를 각각 확인한다. / 상충하는 지연가격 12,020과 11,540으로 지지 이탈이나 매도 실행을 판정하지 않는다. 12,600–12,700 지지와 13,000 회복을 최신 일봉으로 점검한다.","risk_condition_ko":"12,600 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"207940.KS","display_name":"207940","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1373000.0,"market_data_asof":"2026-11-18T14:48:00+09:00","session_vwap":1382960.3905953735,"relative_volume":0.4359279925240176,"spread_bps":7.280669821623589,"day_high":1403000.0,"day_low":1373000.0,"execution_condition_ko":"위험 대응 조건: 1,390,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"1,390,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-18T14:48:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-18T14:51:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-18T13:39:49.255925+09:00",
  "as_of": "2026-11-18T13:29:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
