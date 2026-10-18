# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-18T07:33:57.883164+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261016T143355_local-scheduler-kr-overlay_only",
  "producer_finished_at": "2026-10-16T14:35:59.467083+09:00",
  "analysis_run_id": "20261016T044900_local-scheduler-kr-full",
  "analysis_completed_at": "2026-10-16T06:51:22.608695+09:00",
  "analysis_trade_date_oldest": "2026-10-15",
  "analysis_trade_date_latest": "2026-10-15",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-16T14:34:00+09:00",
  "market_data_latest_at": "2026-10-16T14:34:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-16T14:35:55.310733+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-16T14:35:55.310733+09:00",
    "run_started_at": "2026-10-16T14:33:55.689409+09:00",
    "run_finished_at": "2026-10-16T14:35:59.467083+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 8842040,
    "total_unrealized_pnl_krw": -6102196,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 9818692
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1287000,
      "market_value_krw": 2574000,
      "unrealized_pnl_krw": -2861000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 218500,
      "market_value_krw": 2185000,
      "unrealized_pnl_krw": -1138851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 326500,
      "market_value_krw": 1632500,
      "unrealized_pnl_krw": -442143
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 160700,
      "market_value_krw": 642800,
      "unrealized_pnl_krw": -332200
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 524000,
      "market_value_krw": 524000,
      "unrealized_pnl_krw": -629000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 18730,
      "market_value_krw": 337140,
      "unrealized_pnl_krw": -231175
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 71100,
      "market_value_krw": 213300,
      "unrealized_pnl_krw": -86700
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 208000,
      "market_value_krw": 208000,
      "unrealized_pnl_krw": -166167
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 181000,
      "market_value_krw": 181000,
      "unrealized_pnl_krw": -101334
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 131900,
      "market_value_krw": 131900,
      "unrealized_pnl_krw": -40400
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 46050,
      "market_value_krw": 92100,
      "unrealized_pnl_krw": -26100
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 65700,
      "market_value_krw": 65700,
      "unrealized_pnl_krw": -47231
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 54600,
      "market_value_krw": 54600,
      "unrealized_pnl_krw": 100
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":65800.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":65062.58229742236,"relative_volume":0.856807755075156,"spread_bps":15.20912547528517,"day_high":66400.0,"day_low":63500.0,"execution_condition_ko":"위험 대응 조건: 61,500 이하 하락, 2개 봉 확인 후 손절 조건 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"61,500 이하 하락, 2개 봉 확인 후 손절 조건","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1287000.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":1288641.2252946508,"relative_volume":1.249623452853814,"spread_bps":7.766990291262136,"day_high":1325000.0,"day_low":1247000.0,"execution_condition_ko":"000660.KS 1238000원 방어, 1332000원 돌파·재지지, RSI 30 재돌파와 음의 이동평균 수렴·확산 막대 축소를 관찰한다. 중립 분석가의 의견대로 초기 개선은 약세 강도 재평가 조건이며 자동 매수 승인이 아니다. / 1402000원 저항 회복과 기준일 200일 평균 1452545원 부근의 저항 해소를 확인한다. 이동평균은 실행 전에 갱신한다.","risk_condition_ko":"1,238,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":160800.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":158928.44588215934,"relative_volume":1.3783553354093367,"spread_bps":6.216972334473112,"day_high":162700.0,"day_low":153900.0,"execution_condition_ko":"151600원 방어와 과거 저점 후보 150300원·148000원을 최신 정규장 자료로 확인한다. 지지 이탈 코드는 향후 조건이지 현재 관측 사실이 아니다. / 165600원 회복·재지지, 높아지는 저점, 상승 거래 증가·눌림 거래 감소와 신선한 세션 거래량가중평균가격 상회를 확인한다.","risk_condition_ko":"151,600 이하 하락, 2개 봉 확인 후 (최신 정규장 완료 5분봉 두 개의 종가가 연속으로 기준선 아래이고 두 번째 봉 거래량이 첫 번째보다 증가) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":524000.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":521875.8612654313,"relative_volume":1.4406254107817418,"spread_bps":19.065776930409914,"day_high":534000.0,"day_low":492500.0,"execution_condition_ko":"267260.KS의 거래일 달력, 실제 거래 상태, 호가 시각, 매수·매도 가격 차이와 정규장 유동성을 확인한다. / 2026-10-15 기준종가 487000원과 뉴스의 481000원 인용값을 대조한다. 지연된 475000원 야간 인용값은 진입 확인에 사용하지 않는다.","risk_condition_ko":"473,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":208000.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":200973.11594411533,"relative_volume":1.0588904646820907,"spread_bps":24.067388688327316,"day_high":210000.0,"day_low":190800.0,"execution_condition_ko":"판단 시각은 2026-10-16T05:18:11.360581+09:00이고 일봉 기준일은 2026-10-15다. 실제 거래일·정규장 운영·거래정지·시장경보 및 최신 시세 시각은 별도 확인이 필요하다. / 10:30은 확인된 정규장에서 시험 진입 재심사를 시작할 수 있는 시각이며 만료 시각이 아니다. 제공된 만료 시각이 없으므로 만료 판정이나 다음 세션 이월을 하지 않는다.","risk_condition_ko":"187,500 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":181000.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":180774.65768266283,"relative_volume":0.8961046862284049,"spread_bps":5.5263885051119095,"day_high":183800.0,"day_low":174000.0,"execution_condition_ko":"035420.KS 거래일·정규장 시간, 최신 호가 시각, 매수·매도 호가 차이와 체결 유동성을 확인한 뒤 실행한다. / 171100 방어와 종가 이탈, 176100 회복·재시험 및 178000–180500 반락을 구분해 관찰한다. 현재 세션의 충족 신호는 없다.","risk_condition_ko":"171,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":131400.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":130512.90324656107,"relative_volume":0.8656597272111359,"spread_bps":15.220700152207002,"day_high":134000.0,"day_low":126500.0,"execution_condition_ko":"353200.KS 실제 거래일·정규장·신선한 호가·거래량·거래량가중평균가격 확인. 전일 야간 122700원과 산식 미확인 상대거래량 23.55는 실행 근거에서 제외한다. / 353200.KS 130300원 회복 및 재시험 지지 후 첫 저항까지 비용 반영 손익비 재계산. 회복만으로 자동 매수하지 않는다.","risk_condition_ko":"135,600 이상 도달, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":46150.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":46009.495957894316,"relative_volume":0.7611354888635089,"spread_bps":10.840108401084011,"day_high":47000.0,"day_low":44900.0,"execution_condition_ko":"083450.KQ 거래일, 거래정지 여부, 시각이 확인된 정규장 호가 및 보유·자산 정보를 먼저 확인한다. / 43,850원과 43,000원의 신규 5분봉 및 제한된 회복 평가 구간을 관찰한다.","risk_condition_ko":"43,850 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":18740.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":18749.18894271476,"relative_volume":0.926058273901073,"spread_bps":5.3376034160661865,"day_high":18990.0,"day_low":18110.0,"execution_condition_ko":"010140.KS의 17,780~17,910원 지지 유지와 18,570원 회복·재시험을 관찰한다. 단독 매수 신호는 아니다. / 19,192원 초과 종가와 직전 완료된 20거래일 평균 대비 1.2배 이상 거래량을 확인한 뒤, 다음 확인된 거래일 첫 30~60분의 지지 유지 여부를 점검한다.","risk_condition_ko":"17,210 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":218250.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":216129.1718684522,"relative_volume":0.9529029020597635,"spread_bps":22.90950744558992,"day_high":222500.0,"day_low":210500.0,"execution_condition_ko":"204500원 재시험 후 높은 저점, 상대강도지수 30 회복 및 이동평균 수렴·확산 지표의 음의 폭 축소. / 216500원과 221500원 회복 후 재시험 지지, 최신 정규장 거래량가중평균가격 상회 및 검증된 동일 시간대 상대거래량 1.2배 이상.","risk_condition_ko":"231,273 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":326000.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":322734.35978410125,"relative_volume":1.1824890176720306,"spread_bps":15.32567049808429,"day_high":337000.0,"day_low":300500.0,"execution_condition_ko":"278470.KS의 301000원 돌파·재시험 지지, 저점 상승, 정규장 거래량가중평균가격 상회와 동일 시간대 상대거래량 1.2 이상을 확인한다. 비용 후 보상·위험비 2배 미만이면 매수하지 않는다. / 278470.KS의 278500원부터 283000원까지 지지와 266500원 무효화 기준을 점검한다. 333000원 회복 후 다음 확인된 거래일 지지는 추세 개선 재검토 조건이다.","risk_condition_ko":"278,500 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":71300.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":69837.61015916562,"relative_volume":0.5813317030706765,"spread_bps":14.035087719298245,"day_high":71700.0,"day_low":67900.0,"execution_condition_ko":"66100원 방어와 저점 상승, 63100~64300원 지지 후보 반응 / 갱신된 50일 평균선 회복·재시험과 71600~72700원 저항 소화","risk_condition_ko":"70,270 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":54700.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":52873.38475289235,"relative_volume":0.9489831086558148,"spread_bps":36.56307129798903,"day_high":55300.0,"day_low":50300.0,"execution_condition_ko":"403870.KQ의 48,400 지지와 갱신된 50,534 회복, 거래량이 줄어드는 재시험 후 매수 거래량 증가를 확인한다. 이는 관찰 조건이지 현재 매수 주문이 아니다. / 403870.KQ가 50,534 회복에 실패하거나 48,400을 종가로 이탈하면 추가 방어를 검토한다.","risk_condition_ko":"48,400 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"036930.KQ","display_name":"주성엔지니어링","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":212500.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":209919.49837430546,"relative_volume":1.0652856850910717,"spread_bps":23.55712603062426,"day_high":216500.0,"day_low":202000.0,"execution_condition_ko":"위험 대응 조건: 199,100 이하 하락, 장중 확인 시 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"199,100 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"093370.KS","display_name":"093370","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":12190.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":12089.76220410338,"relative_volume":0.5235520485117265,"spread_bps":8.206811653672547,"day_high":12510.0,"day_low":11800.0,"execution_condition_ko":"위험 대응 조건: 11,840 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"11,840 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":191400.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":192402.7449869989,"relative_volume":1.2160809999766207,"spread_bps":10.449320794148381,"day_high":195500.0,"day_low":185700.0,"execution_condition_ko":"033780.KS의 거래일 달력, 정규장 여부, 거래 정지, 실행 가능한 최신 호가, 호가 차이, 거래량가중평균가격 및 동일 경과 시간 대비 상대 거래량을 확인한다. / 184000~184600원에서 매도 거래량 감소 후 실제 반등을 확인한다. 단순 접촉은 불충분하며 184400원은 비용 차감 전 산술 상한이지 매수 주문가가 아니다.","risk_condition_ko":"181,800 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"069540.KQ","display_name":"069540","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":3965.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":3944.470716529607,"relative_volume":0.42486430289328236,"spread_bps":12.618296529968456,"day_high":4060.0,"day_low":3790.0,"execution_condition_ko":"4035~4085 회복·재시험 지지, 상승하는 5분봉 고점·저점, 당일 거래량가중평균가격 상회와 동일 시간대 상대거래량 1.2 이상 확인. / 4165 상회 종가 이후 다음 실제 거래일 첫 30~60분 동안 4160~4165 지지 유지 확인.","risk_condition_ko":"4,035 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"452190.KQ","display_name":"452190","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":5220.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":5072.424127780448,"relative_volume":0.16013000543375008,"spread_bps":38.38771593090211,"day_high":5240.0,"day_low":4835.0,"execution_condition_ko":"4,790~4,880 지지 후보 방어, 실패 시 4,645~4,695와 4,530을 점검한다. 하단 지지는 물타기 주문이 아니다. / 5,130 회복 후 5,340~5,400 저항을 반영해 보상/위험을 다시 계산한다. 기술적 관찰 재개와 실제 자금 배정은 구분한다.","risk_condition_ko":"4,790 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":153800.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":152942.75547212287,"relative_volume":0.7587444000538099,"spread_bps":6.504065040650406,"day_high":156200.0,"day_low":149000.0,"execution_condition_ko":"096770.KS: 거래일정과 정규장 상태를 확인하고 시각이 명시된 가격·호가차이·거래량가중평균가격·동시간대 상대거래량을 확보한다. / 096770.KS: 152700–153000 지지, 5분봉 저점 상승과 155000 회복을 관찰한다. 이후 159800–160900과 163000–165400 통과 여부를 확인한다.","risk_condition_ko":"152,700 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"018880.KS","display_name":"018880","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":3895.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":3871.051082214501,"relative_volume":0.7339502610472612,"spread_bps":12.845215157353884,"day_high":3955.0,"day_low":3775.0,"execution_condition_ko":"018880.KS: 3,710 또는 3,630–3,670 부근 안정 이후 3,770–3,805 회복과 재시험 성공을 관찰한다. 지지선 접촉만으로 매수하지 않는다. / 018880.KS: 3,920 위 종가와 다음 실제 거래일의 지지 유지 여부를 확인한다. 4,085 돌파도 근거 있는 추가 상승 목표 없이는 매수 사유가 아니다.","risk_condition_ko":"3,630 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":539000.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":537999.8438176642,"relative_volume":1.1472292792522016,"spread_bps":18.570102135561747,"day_high":550000.0,"day_low":526000.0,"execution_condition_ko":"위험 대응 조건: 519,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"519,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"지금 실행 검토 가능","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"373220.KS","display_name":"LG에너지솔루션","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":407000.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":405308.3738341387,"relative_volume":0.8984757844720233,"spread_bps":12.277470841006751,"day_high":411000.0,"day_low":397000.0,"execution_condition_ko":"위험 대응 조건: 386,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"386,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010950.KS","display_name":"S-Oil","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":154300.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":156264.8725516578,"relative_volume":1.1860527362997886,"spread_bps":6.4787819889860705,"day_high":162200.0,"day_low":154100.0,"execution_condition_ko":"위험 대응 조건: 156,800 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"156,800 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"018260.KS","display_name":"삼성SDS","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":201500.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":200706.5381835983,"relative_volume":0.7424087878610982,"spread_bps":24.783147459727385,"day_high":203500.0,"day_low":196200.0,"execution_condition_ko":"위험 대응 조건: 191,100 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"191,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"062040.KS","display_name":"062040","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":183100.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":180632.99688730203,"relative_volume":1.3285650803054116,"spread_bps":5.46000546000546,"day_high":184800.0,"day_low":173200.0,"execution_condition_ko":"위험 대응 조건: 172,300 이하 하락, 장중 확인 시 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"172,300 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"086790.KS","display_name":"086790","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":122900.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":123884.97688594164,"relative_volume":0.9777805296864921,"spread_bps":8.13338755591704,"day_high":125600.0,"day_low":122400.0,"execution_condition_ko":"위험 대응 조건: 117,800 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"117,800 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"131290.KQ","display_name":"티에스이","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":297000.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":284226.3253589374,"relative_volume":1.1269581752976126,"spread_bps":33.67003367003367,"day_high":301000.0,"day_low":269500.0,"execution_condition_ko":"위험 대응 조건: 263,500 이하 하락, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"263,500 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"419050.KQ","display_name":"419050","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":2140.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":2175.093854027802,"relative_volume":2.184810824726969,"spread_bps":23.33722287047841,"day_high":2275.0,"day_low":2005.0,"execution_condition_ko":"위험 대응 조건: 1,955 이하 하락, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"1,955 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033790.KQ","display_name":"033790","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":9330.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":9184.496344302632,"relative_volume":0.6785741984796991,"spread_bps":10.712372790573111,"day_high":9440.0,"day_low":8760.0,"execution_condition_ko":"위험 대응 조건: 8,450 이하 하락, 종가 확인 후 (보호 조치에는 거래량 증가를 요구하지 않는다.) 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"8,450 이하 하락, 종가 확인 후 (보호 조치에는 거래량 증가를 요구하지 않는다.) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"036540.KQ","display_name":"036540","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":9660.0,"market_data_asof":"2026-10-16T14:34:00+09:00","session_vwap":9164.353128719777,"relative_volume":0.6073481628384695,"spread_bps":10.346611484738748,"day_high":9730.0,"day_low":8590.0,"execution_condition_ko":"위험 대응 조건: 8,560 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"8,560 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-16T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-16T14:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-16T14:45:00.409039+09:00",
  "as_of": "2026-10-16T14:34:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
