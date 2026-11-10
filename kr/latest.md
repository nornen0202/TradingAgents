# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-10T03:40:57.501115+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261110T103225_local-scheduler-kr-overlay_only",
  "producer_finished_at": "2026-11-10T10:42:18.738439+09:00",
  "analysis_run_id": "20261109T044749_local-scheduler-kr-full",
  "analysis_completed_at": "2026-11-09T07:20:13.822249+09:00",
  "analysis_trade_date_oldest": "2026-11-06",
  "analysis_trade_date_latest": "2026-11-06",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-10T10:41:00+09:00",
  "market_data_latest_at": "2026-11-10T10:41:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-10T10:42:15.130253+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-10T10:42:15.130253+09:00",
    "run_started_at": "2026-11-10T10:32:25.989573+09:00",
    "run_finished_at": "2026-11-10T10:42:18.738439+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 7562650,
    "total_unrealized_pnl_krw": -7381586,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 8539302
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1202000,
      "market_value_krw": 2404000,
      "unrealized_pnl_krw": -3031000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 198900,
      "market_value_krw": 1989000,
      "unrealized_pnl_krw": -1334851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 251500,
      "market_value_krw": 1257500,
      "unrealized_pnl_krw": -817143
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 122000,
      "market_value_krw": 488000,
      "unrealized_pnl_krw": -487000
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 388000,
      "market_value_krw": 388000,
      "unrealized_pnl_krw": -765000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 15750,
      "market_value_krw": 283500,
      "unrealized_pnl_krw": -284815
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 193500,
      "market_value_krw": 193500,
      "unrealized_pnl_krw": -88834
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 172200,
      "market_value_krw": 172200,
      "unrealized_pnl_krw": -201967
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 49250,
      "market_value_krw": 147750,
      "unrealized_pnl_krw": -152250
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 81800,
      "market_value_krw": 81800,
      "unrealized_pnl_krw": -90500
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 37300,
      "market_value_krw": 74600,
      "unrealized_pnl_krw": -43600
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 46200,
      "market_value_krw": 46200,
      "unrealized_pnl_krw": -66731
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 36600,
      "market_value_krw": 36600,
      "unrealized_pnl_krw": -17900
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":121900.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":121465.33299402721,"relative_volume":1.8795890503592063,"spread_bps":8.206811653672547,"day_high":124800.0,"day_low":117600.0,"execution_condition_ko":"위험 대응 조건: 127,150 이상 도달, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"127,150 이상 도달, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":193500.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":194708.14701634948,"relative_volume":3.2444457356589087,"spread_bps":5.169294391315585,"day_high":197300.0,"day_low":190500.0,"execution_condition_ko":"178400원 지지 시험, 그 위 종가, 다음 확인된 거래일의 지지 유지와 178400~180600원 지정가 가능 여부를 순서대로 점검한다. / 184900~186900원이 지지인지 유효한 상단 매물인지 확인한다. 유효 저항이면 해당 저항을 기준으로 계산하여 미달 거래를 거절한다.","risk_condition_ko":"178,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1204000.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":1217972.2849175315,"relative_volume":1.2787426942746893,"spread_bps":8.309098462816785,"day_high":1242000.0,"day_low":1193000.0,"execution_condition_ko":"000660.KS의 1171000~1183000원 종가 지지 여부. 2026-11-06 장중 하회 이력이 있어 확정 지지로 취급하지 않는다. / 000660.KS의 1217000원 종가 회복과 다음 실제 거래일 유지 시 최신 가격·비용·주문 상황 검토를 재개한다. 분석 재개를 1277000원까지 미루지 않는다.","risk_condition_ko":"1,171,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":251000.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":252773.72882612952,"relative_volume":0.739164900379447,"spread_bps":19.90049751243781,"day_high":258500.0,"day_low":247500.0,"execution_condition_ko":"278470.KS의 271,500원 위 종가와 다음 실제 거래일 268,000~271,500원 재시험 지지를 확인한다. 가격 회복은 약세 판단 완화의 근거가 될 수 있으나 자동 매수 승인은 아니다. / 275,000~286,000원 및 291,000~300,500원 저항을 반영해 당시 가격 구조와 비용 기준 손익비를 다시 계산한다.","risk_condition_ko":"250,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":15770.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":15799.325745679611,"relative_volume":1.423513815113251,"spread_bps":6.3391442155309035,"day_high":16150.0,"day_low":15450.0,"execution_condition_ko":"15570~15580원 지지와 하단 이탈 후 다음 실제 거래일 종가의 회복 여부를 확인한다. 현재 지지 붕괴로 분류하지 않는다. / 16870원 위 종가 이후 16690~16870원 지지 또는 재돌파를 확인한다. 충족해도 자동 매수하지 않으며, 별도 재평가를 통과하면 소액 첫 진입 가능성을 검토한다.","risk_condition_ko":"15,570 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":199200.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":199256.73883844234,"relative_volume":1.2949409540386077,"spread_bps":5.021340697966357,"day_high":201500.0,"day_low":196600.0,"execution_condition_ko":"005930.KS 196500원 회복은 첫 관문이며 단독 매수 신호가 아니다. / 005930.KS 199800~201500원 지지 전환과 다음 확인된 거래일의 지속성을 관찰한다. 재심의 시 실제 지지·현실적인 저항으로 비용 차감 후 보상·위험을 재계산한다.","risk_condition_ko":"179,200 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":388000.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":385388.3541262453,"relative_volume":2.0364608738780077,"spread_bps":25.77319587628866,"day_high":397500.0,"day_low":375500.0,"execution_condition_ko":"377,000원 종가 회복은 첫 개선 단서이며 매수 승인이 아니다. 회복 후 그 아래로 재마감하면 초기 반등 시나리오를 취소한다. / 401,500원 위 종가 후 달력과 세션이 확인된 다음 실제 정규 거래일에 393,500~401,500원 지지 또는 재돌파를 점검한다.","risk_condition_ko":"393,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":172600.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":170766.4360769484,"relative_volume":1.3632070433336603,"spread_bps":5.795421616922631,"day_high":173800.0,"day_low":167500.0,"execution_condition_ko":"166,100~166,900원 종가 회복 후 다음 확인된 거래일 지지를 점검한다. 169,100원 회복은 추가 안정화 단서이며 자동 매수 신호가 아니다. / 185,300원 위 종가와 후속 지지 확인 시 사업 증거와 함께 배분을 재심사한다. 저항대는 2026-11-06 지표이므로 당시 이동평균을 갱신한다.","risk_condition_ko":"148,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":81900.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":81130.5639147324,"relative_volume":2.1644409349363998,"spread_bps":12.217470983506415,"day_high":82700.0,"day_low":78600.0,"execution_condition_ko":"2026-11-06 거래소 일봉과 수정주가 기준을 대조해 71,200원 종가와 기사·개별 봉의 74,600원 충돌을 해소한다. 어느 값을 최신 가격으로 단정하지 않는다. / 67,800원 방어와 저점 상승을 관찰하고 상대강도지수 30 회복 및 음의 추세 막대 축소는 보조 근거로만 사용한다.","risk_condition_ko":"67,800 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":49500.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":49105.15879640671,"relative_volume":1.4629028342824588,"spread_bps":20.222446916076848,"day_high":50200.0,"day_low":48450.0,"execution_condition_ko":"45,150원 방어와 저점 상승을 실제 거래일 일봉으로 확인한다. 48,150원 회복만으로 바닥이나 추세 전환을 선언하지 않는다. / 50,300원 종가 상회 후 다음 실제 거래일부터 2~3개 거래일 동안 49,500~50,300원 지지를 확인하면 매수 심의를 다시 연다. 재무 검증과 유리한 비용 반영 보상·위험이 추가로 필요하며 자동 매수는 아니다.","risk_condition_ko":"45,150 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":46250.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":46461.575094428765,"relative_volume":2.232328028375387,"spread_bps":10.804970286331713,"day_high":47775.0,"day_low":45300.0,"execution_condition_ko":"46,150원 상회 일봉 종가 이후 다음 실제 정규거래일의 지지 또는 재돌파 여부를 확인한다. 소액 진입 자동 실행 조건은 아니다. / 48,700~49,300원 구간 회복과 49,300원 상회 종가 여부, 반대로 구간 진입 후 48,700원 아래 종가 회귀 여부를 관찰한다.","risk_condition_ko":"43,700 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":37300.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":36860.86340550655,"relative_volume":1.2825152580354224,"spread_bps":26.80965147453083,"day_high":37500.0,"day_low":36275.0,"execution_condition_ko":"35,750원 초과 종가, 36,600원 초과 종가, 다음 실제 정규장의 36,300~36,600원 재지지를 순차 확인한다. 현재 충족 여부는 미확인이며 자동 매수 조건이 아니다. / 저항 시험 후 반등 실패와 32,000원 종가 이탈은 매수 관찰보다 보유 위험관리를 우선한다. 두 반등 실패 조건에 따른 추가 축소는 중복 집행하지 않는다.","risk_condition_ko":"32,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":36550.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":36485.81223239856,"relative_volume":1.3067451977223299,"spread_bps":40.955631399317404,"day_high":37300.0,"day_low":35450.0,"execution_condition_ko":"기준시각 2026-11-09T05:55:43.489007+09:00은 실제 코스닥 개장 여부나 호가 신선도를 입증하지 않는다. 거래일·휴장·단축장 여부와 현재 정규장 가격을 별도로 확인한다. / 2026-11-06 20:00 한국시간의 기존 관측치는 현재 자료가 아니며 요약가격과 최종 관측가격도 불일치하므로 오늘의 매매 확인에서 제외한다.","risk_condition_ko":"32,050 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"180640.KS","display_name":"180640","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":233000.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":228849.19469642654,"relative_volume":4.34291179900249,"spread_bps":21.482277121374864,"day_high":243000.0,"day_low":209500.0,"execution_condition_ko":"위험 대응 조건: 199,300 이상 도달, 장중 확인 시 이익실현성 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"199,300 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"지금 실행 검토 가능","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":179000.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":179793.25227006126,"relative_volume":1.1901955056105524,"spread_bps":5.585032113934655,"day_high":185400.0,"day_low":178000.0,"execution_condition_ko":"033780.KS의 187,000~188,200원 시험, 종가 회복, 다음 실제 거래일 재시험 지지 여부를 확인한다. 계좌·공시 검증까지 완료된 경우에만 최대 0.5% 첫 진입을 검토한다. / 033780.KS의 191,500원·192,400원 회복은 관찰 신호이며 독립적인 매수 조건은 아니다.","risk_condition_ko":"185,600 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":128500.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":129140.02302025782,"relative_volume":0.7997005322243863,"spread_bps":7.779074290159471,"day_high":131600.0,"day_low":127800.0,"execution_condition_ko":"090430.KS의 원공시 핵심 실적 기준, 최신 실제 거래일 가격과 세션, 기존 보유·현금·관련 노출 및 잔여 위험예산을 실행 전에 확인한다. / 090430.KS가 130700~130900원을 재시험하고 130900원 이상으로 마감한 최초 신호일을 기록한다. 다음 실제 거래일도 130900원 이상 종가인지 확인한다.","risk_condition_ko":"130,700 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"030200.KS","display_name":"030200","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":51200.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":51846.06009216763,"relative_volume":1.8074289220267714,"spread_bps":19.550342130987293,"day_high":53200.0,"day_low":51000.0,"execution_condition_ko":"030200.KS의 새로운 지지 시험, 종가 회복, 다음 실제 거래일 지지 유지와 이후 진입 범위 재접근을 순서대로 확인한다. 과거 확인을 이유로 지정가 주문을 방치하지 않는다. / 030200.KS의 53900원은 돌파 관찰선이자 향후 신규 전술분의 절반 회수 기준이다. 자동 매수 신호가 아니며 54300~54500원과 갱신된 200일선 저항을 별도로 재평가한다.","risk_condition_ko":"51,268 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":210500.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":210324.58705824835,"relative_volume":1.0024543300939783,"spread_bps":23.781212841854934,"day_high":213000.0,"day_low":209000.0,"execution_condition_ko":"2026-11-09~2026-11-13에 새 일봉의 지지 접근과 종가 회복을 확인하고, 다음 확인된 거래일 205,000~206,000에서 비용 차감 손익비와 계좌 위험을 재평가한다. / 216,000 위 종가와 비교 가능한 일봉 거래량 증가, 다음 거래일 재시험 방어가 확인되면 별도 돌파 전략을 검토한다. 223,500~228,300은 과거 고점 참고 구간일 뿐 확정 목표가가 아니다.","risk_condition_ko":"203,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"259960.KS","display_name":"259960","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":216000.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":218244.1069977093,"relative_volume":1.212976083103844,"spread_bps":23.174971031286212,"day_high":221000.0,"day_low":215000.0,"execution_condition_ko":"결정 기준시각 2026-11-09T06:05:33.879164+09:00은 조건부 진입 만료 전이다. 그러나 정규장·휴장 일정이나 진입 조건 충족을 입증하지 않는다. 최신 가격의 실제 시각과 거래 가능 일정을 별도로 확인한다. / 209000~212000 재시험 후 유효한 일봉 반등과 다음 실제 정규장의 지지 유지를 확인한다. 209000~211000 안에서도 비용·체결 지연 완충 반영 보상/위험이 1.5배에 미달하면 매수하지 않는다.","risk_condition_ko":"209,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"028050.KS","display_name":"028050","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":63700.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":63570.43171439495,"relative_volume":0.9603963716525227,"spread_bps":15.686274509803921,"day_high":65300.0,"day_low":62400.0,"execution_condition_ko":"028050.KS 판단 시각은 2026-11-09T06:20:01.238295+09:00이며 신규 진입 기한 2026-11-20T23:59:59+09:00 이전이다. 기한이 남았다는 사실은 활성화를 뜻하지 않는다. 실제 거래소 달력·정규장 여부·가격 기준시각을 먼저 확인한다. / 028050.KS의 58,300~59,300원 지지·저점 상승 → 61,000원 이상 종가 회복 → 다음 실제 정규장 재지지를 순서대로 확인한다. 신규 주문 가격은 59,300~59,400원 안에서도 비용·갭 반영 손익비 기준을 통과해야 한다.","risk_condition_ko":"58,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"271560.KS","display_name":"271560","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":114400.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":114696.98338711605,"relative_volume":1.3925529897396476,"spread_bps":8.73743993010048,"day_high":116100.0,"day_low":113600.0,"execution_condition_ko":"115200~115600원 시험, 종가 115600원 이상, 다음 실제 정규거래일 지지 유지와 구간 내 진입 가능성을 순서대로 점검한다. 제공된 과거 종가만으로 확인 절차가 완료됐다고 간주하지 않는다. / 121000~122800원에서 반복되는 상승분 반납과 동력 둔화는 익절 재평가 신호다. 종가 122800원 돌파는 자동 매수가 아니라 재시험과 비용 후 손익비 재평가 신호다.","risk_condition_ko":"115,200 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"036460.KS","display_name":"036460","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":36050.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":36310.44064526261,"relative_volume":1.2873993249165654,"spread_bps":27.700831024930746,"day_high":37100.0,"day_low":36000.0,"execution_condition_ko":"2026-11-09부터 2026-11-11까지 지지 시험, 36800원 이상 회복 종가, 다음 확인된 정규거래일의 36600~36800원 재시험 지지를 순서대로 점검한다. 실제 거래일정·거래상태·가격 신선도는 별도 확인한다. / 36900~37100원 첫 저항과 37550~38000원 상단에서 상승 지속성을 재평가한다. 중립 분석가의 지적대로 38000원 도달을 확정 수익으로 간주하지 않는다.","risk_condition_ko":"36,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"011200.KS","display_name":"011200","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":20650.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":20884.327721099842,"relative_volume":1.0955247305409188,"spread_bps":24.183796856106408,"day_high":21600.0,"day_low":20600.0,"execution_condition_ko":"011200.KS: 새 지지 시험과 21900원 이상 종가, 다음 검증 거래일 전체의 21750원 이상 유지, 이후 거래일의 적격 진입가라는 순서를 확인한다. 2026-11-06 종가만으로 새 조건이 충족된 것으로 보지 않는다. / 011200.KS: 22900원 초과 종가와 이후 22800~22900원 지지, 비교 가능한 일별 거래량 개선은 회복 재평가 사유다. 자동 증액 조건은 아니다.","risk_condition_ko":"21,750 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"207940.KS","display_name":"207940","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1473000.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":1486380.9352702633,"relative_volume":0.8927072550851601,"spread_bps":6.791171477079796,"day_high":1537000.0,"day_low":1466000.0,"execution_condition_ko":"1480000–1500000원 신규 지지 재시험, 1500000원 이상 종가 회복, 다음 검증된 거래일 1500000–1510000원 체결 가능성을 순서대로 확인한다. / 1575000–1578000원 저항과 1600000–1632000원 잠재 매물대를 관찰한다. 돌파 시 보상 대비 위험을 새로 평가하며 저항 접촉만으로 매도하지 않는다.","risk_condition_ko":"1,480,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"030530.KQ","display_name":"030530","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":29750.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":28517.573767706257,"relative_volume":2.2635268637853354,"spread_bps":16.79261125104954,"day_high":29800.0,"day_low":27300.0,"execution_condition_ko":"030530.KQ의 28,000~28,200원 눌림, 종가 28,200원 이상 회복, 다음 실제 거래일의 완성된 일봉 재지지를 순서대로 관찰한다. 확인 전 장중 매수나 구간 밖 추격은 하지 않는다. / 030530.KQ의 28,850~29,200원 회복은 추세 개선 관찰 신호이지 단독 진입 또는 추가매수 승인이 아니다.","risk_condition_ko":"26,550 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"064400.KS","display_name":"LG CNS","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":79200.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":80516.61990558395,"relative_volume":3.6830178112365695,"spread_bps":12.634238787113075,"day_high":82100.0,"day_low":78600.0,"execution_condition_ko":"원공시의 기간·통화·단위·이익 항목, 회수 지연과 단기투자 사용제한, 계약 경제성을 최초 신규 진입 전에 확인한다. / 71800~72700원 시험 후 종가 회복과 다음 확인된 정규장 종가 지지를 관찰한다. 이후 실제 72700~73000원 안에서도 비용·갭 조정 조건을 별도로 충족해야 한다.","risk_condition_ko":"71,800 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000810.KS","display_name":"000810","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":609000.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":614038.4720104552,"relative_volume":1.4781302133518341,"spread_bps":16.433853738701725,"day_high":626000.0,"day_low":606000.0,"execution_condition_ko":"000810.KS의 592000 방어, 608000~612000 종가 회복, 다음 확인 거래일의 지지 유지를 초기 안정 신호로 관찰한다. 이것만으로 매수하지 않는다. / 000810.KS의 626000~635000 지지 전환과 원문 실적 검증이 진전되면 실제 진입가·손절·640600~648000 저항까지의 비용 반영 보상/위험을 다시 계산한다.","risk_condition_ko":"592,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"396470.KQ","display_name":"396470","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":6140.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":6097.285425891109,"relative_volume":1.1104669354526842,"spread_bps":48.97959183673469,"day_high":6250.0,"day_low":5950.0,"execution_condition_ko":"396470.KQ의 5,400원 지지 유지와 종가 이탈을 구분한다. 지지 접촉이나 하락 폭만으로 저평가·매수 기회를 판단하지 않는다. / 396470.KQ의 6,000원 상회 종가 이후 다음 확인된 정규장에서 5,930~6,000원 지지 유지 또는 재돌파를 점검한다. 이는 자동 매수 신호가 아니다.","risk_condition_ko":"5,400 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"443670.KQ","display_name":"443670","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":5850.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":5874.848700776753,"relative_volume":12.268907991628037,"spread_bps":17.10863986313088,"day_high":6290.0,"day_low":5210.0,"execution_condition_ko":"4363~4410원 지지 유지와 4525원 종가 회복을 관찰하고, 다음 실제 거래일에도 회복이 유지되는지 확인한다. / 4650원 이상 종가 회복과 다음 거래일 4646~4650원 재지지 시 실제 진입가·유효 손절·거래비용·계약 경제성을 함께 재평가한다. 가격 회복만으로 소액 진입이나 비중 확대를 승인하지 않는다.","risk_condition_ko":"4,363 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003490.KS","display_name":"003490","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":31850.0,"market_data_asof":"2026-11-10T10:41:00+09:00","session_vwap":31842.711198601737,"relative_volume":6.317097089696396,"spread_bps":15.710919088766694,"day_high":32800.0,"day_low":30100.0,"execution_condition_ko":"2026-11-09부터 2026-11-16까지 일주일간 관찰하고 재평가한다. 실제 거래일은 별도 확인하며 재검토일은 주문 만기나 자동 진입일이 아니다. / 29000원 지지·회복 또는 28400~28500원 구간의 하락 정지와 종가 회복, 다음 실제 거래일 지지 지속을 관찰한다. 단순 도달은 매수 신호가 아니다.","risk_condition_ko":"28,400 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-10T10:41:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-10T10:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-10T10:44:53.744876+09:00",
  "as_of": "2026-11-10T10:41:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
