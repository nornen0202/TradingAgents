# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-20T22:53:20.109104+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261021T044513_local-scheduler-kr-full",
  "producer_finished_at": "2026-10-21T07:30:19.484908+09:00",
  "analysis_run_id": "20261021T044513_local-scheduler-kr-full",
  "analysis_completed_at": "2026-10-21T07:07:20.515277+09:00",
  "analysis_trade_date_oldest": "2026-10-20",
  "analysis_trade_date_latest": "2026-10-20",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-20T20:00:00+09:00",
  "market_data_latest_at": "2026-10-20T20:00:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-21T07:07:44.805564+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-21T07:07:44.805564+09:00",
    "run_started_at": "2026-10-21T04:45:13.141162+09:00",
    "run_finished_at": "2026-10-21T07:30:19.484908+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 8444360,
    "total_unrealized_pnl_krw": -6499876,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 9421012
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1223000,
      "market_value_krw": 2446000,
      "unrealized_pnl_krw": -2989000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 211500,
      "market_value_krw": 2115000,
      "unrealized_pnl_krw": -1208851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 310000,
      "market_value_krw": 1550000,
      "unrealized_pnl_krw": -524643
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 155200,
      "market_value_krw": 620800,
      "unrealized_pnl_krw": -354200
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 487500,
      "market_value_krw": 487500,
      "unrealized_pnl_krw": -665500
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 17320,
      "market_value_krw": 311760,
      "unrealized_pnl_krw": -256555
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 67500,
      "market_value_krw": 202500,
      "unrealized_pnl_krw": -97500
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 199900,
      "market_value_krw": 199900,
      "unrealized_pnl_krw": -174267
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 178000,
      "market_value_krw": 178000,
      "unrealized_pnl_krw": -104334
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 132300,
      "market_value_krw": 132300,
      "unrealized_pnl_krw": -40000
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 43750,
      "market_value_krw": 87500,
      "unrealized_pnl_krw": -30700
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 62800,
      "market_value_krw": 62800,
      "unrealized_pnl_krw": -50131
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 50300,
      "market_value_krw": 50300,
      "unrealized_pnl_krw": -4200
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1190000.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":1221337.2103260236,"relative_volume":20.11103290438962,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"000660.KS 최신 정규장 자료에서 1183000~1208000원 후보 지지 방어와 저점 상승을 확인한다. 지지 방어만으로 매수하지 않는다. / 000660.KS 1262000~1290000원 회복과 되돌림 지지, 당일 거래량가중평균가격 상회, 동시간대 상대거래량 1.2배 이상을 확인하고 새로운 지지 기준으로 손익비를 다시 계산한다.","risk_condition_ko":"1,183,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":209000.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":212296.15620481916,"relative_volume":17.7510632111731,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"005930.KS의 208750~210000원 및 204500~206500원에서 최신 매수 수요를 확인한다. 반복 접촉이나 거래량 감소만으로 바닥을 선언하지 않는다. / 005930.KS의 222500원 돌파·재시험 지지·당일 거래량가중평균가격 상회·동시간대 상대거래량 1.2배 이상을 함께 관찰하고 228000·232000·233000원 저항까지 손익비를 다시 계산한다.","risk_condition_ko":"204,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":305000.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":312862.9555654428,"relative_volume":12.645152531510295,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 정규장 자료로 307000 지지와 기준 종가 310000 회복 여부를 확인한다. / 329500 위 완성 5분봉 2개, 재시험 지지, 당일 정규장 거래량가중평균가격 상회와 검증된 동일 시간대 상대거래량 1.2배 이상을 관찰한다. 충족해도 현재 계획에서는 자동 매수하지 않는다.","risk_condition_ko":"307,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":152400.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":154692.22873261708,"relative_volume":23.610204654480263,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"010120.KS의 적용 거래일정·거래상태·시각 표시 체결 가능 가격·정규장 거래량가중평균가격·정확한 5분봉을 확보한다. / 149200–150000 방어, 저점 상승과 158600 회복을 관찰한다. 2026-10-21 충족 여부는 미확인이다.","risk_condition_ko":"149,200 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":481500.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":490305.5629541463,"relative_volume":15.18321547173233,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-10-21T05:34:36.204928+09:00은 판단시각일 뿐 실제 개장일·정규장 운영·체결가능성·호가 최신성을 입증하지 않는다. 거래 일정, 최신 시각이 있는 호가와 거래 깊이, 당일 거래량가중평균가격 및 동시간대 상대거래량을 확인한다. / 473500–476000원에서 재시험·높아지는 저점·실제 거래를 동반한 회복을 관찰한다. 단순 접촉이나 과매도 수치만으로 매수하지 않는다.","risk_condition_ko":"473,500 이하 하락, 2개 봉 확인 후 (보호적 매도에는 최소 거래량 조건을 적용하지 않는다.) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":66500.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":68410.52643247042,"relative_volume":11.210703325053611,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단 기준시각은 2026-10-21T05:19:54.555350+09:00이고 가격 근거는 2026-10-20 완료 일봉이다. 실제 거래일·정규장·거래정지·최신 호가와 봉 간격을 별도로 확인해야 한다. / 70,626~71,700 회복·재시험 지지, 당일 거래량가중평균가격 상회, 검증된 동시간대 상대거래량 1.2 이상을 함께 관찰한다. 이는 재심사 조건이지 현재 매수 승인이 아니다.","risk_condition_ko":"66,100 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":176800.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":178965.16685869521,"relative_volume":13.037986383741483,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"035420.KS의 177,000원 지지 실패와 171,100~173,200원 하단 재시험을 신선한 정규장 자료로 확인한다. / 035420.KS의 182,300~185,000원 반등 실패와 185,000원 회복·다음 거래일 지지를 구분한다. 저항 189,000~191,400원 및 193,700~194,700원을 반영해 비용 차감 후 손익비를 다시 계산한다.","risk_condition_ko":"177,000 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":196000.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":202220.6537196321,"relative_volume":17.196368136792767,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"거래소 일정·거래정지 여부·정규장 구분과 신선한 가격·호가·거래량을 먼저 확인한다. 2026-10-20까지의 자료를 2026-10-21 진입 확인으로 사용하지 않는다. / 197400~198000원 방어, 저점 상승과 당일 거래량가중평균가 회복을 함께 관찰한다. 지지 방어만으로 진입하지 않는다.","risk_condition_ko":"187,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":129500.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":135388.03400898338,"relative_volume":24.77270159125791,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단 시각은 2026-10-21T05:37:48.578994+09:00이고 가격 기준일은 2026-10-20이다. 실제 거래일·정규장 운영·최신 호가·실제 5분봉과 거래량 산식을 별도 확인한다. / 353200.KS의 136900원 회복 후 연속 5분봉 두 개의 재시험 지지, 당일 거래량가중평균가 상회와 동일 시간대 상대거래량 1.2 이상을 확인한다. 현재 충족 관측치는 없다.","risk_condition_ko":"130,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":61700.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":63100.88721272773,"relative_volume":15.551373037655518,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"공식 거래일·정규장 운영·호가 시각·실제 봉 간격을 먼저 확인한다. 런타임 날짜만으로 거래 가능 상태를 확정하지 않는다. 10:30은 확인된 거래일의 관찰 개시 기준이며 주문 만료시각이 아니다. / 61500~61800원 방어 후 63300~64600원 회복·재시험을 관찰한다. 과매도나 하락폭만으로 안전마진을 인정하지 않는다.","risk_condition_ko":"61,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":17220.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":17500.796470283905,"relative_volume":21.120367645291854,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단 시각은 2026-10-21T05:00:21.861394+09:00이며 일봉 기준일은 2026-10-20이다. 실제 거래일·정규장·거래정지·호가 시각은 미확인이다. 제공 종가 17320원을 현재 체결 가능 가격으로 사용하지 않는다. / 전일 야간 가격 17220원과 해당 시간대 거래량가중평균가격 17500.80원, 정의가 불명확한 상대거래량 21.12는 당일 정규장 진입 확인에 사용하지 않는다. 일봉 거래량의 평균 대비 약 1.06배는 투매나 매집의 증거가 아니다.","risk_condition_ko":"17,210 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":50300.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"실제 정규장 일정·휴장·단축장·거래정지와 최신 공시를 확인하고 신선한 가격·거래량가중평균가격·동시간대 거래량을 확보한다. / 51595~51600원을 동일한 이동평균 확인구간으로 취급한다. 5원 차이를 독립 신호로 사용해 반복 매매하지 않는다. 회복·되눌림과 52900원 종가 돌파는 재평가 신호이지 매수 주문이 아니다.","risk_condition_ko":"51,595 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":43100.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":44042.94032776506,"relative_volume":10.561149469480075,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"실제 거래일과 거래정지 여부, 시각이 일치하는 정규장 가격·거래량·호가차이·거래량가중평균가격을 확인한다. 보유량과 순자산도 확보해 기술적 매도신호와 별개로 위험예산 준수 여부를 판정한다. / 43,250과 43,050을 감시하고 43,000은 정규장 지지로 단정하지 않는다. 44,800–45,850 반등 실패와 갱신된 200일 평균선 회복 실패도 별도로 점검한다.","risk_condition_ko":"43,050 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":194000.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"033780.KS의 실제 KRX 거래일·정규장·정지 여부와 시세 신선도를 확인한다. 2026-10-21자 신청 관련 보도의 발행시점이 보고서 간 달라 판단시각 이전 공개 여부도 재확인한다. / 189400~191000원에서 매도 거래량 감소 후 연속 5분봉 상승 저점·지지 회복·거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상을 관찰한다. 관측만으로 매수 승인하지 않는다.","risk_condition_ko":"189,400 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"396300.KQ","display_name":"396300","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":9770.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"9,370~9,500에서 하락 거래량 감소·반등 거래량 증가, 완성된 5분봉 두 개의 재안착과 당일 거래량가중평균가격 유지를 확인한다. / 10,000은 심리적 저항 회복이고 11,250은 전일 고점 돌파다. 두 신호를 구분하며 돌파 추격은 별도 손익구조 검토가 필요하다.","risk_condition_ko":"10,000 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"131290.KQ","display_name":"티에스이","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":263000.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"131290.KQ의 258,000~262,470 방어, 263,000 회복·유지와 하락 운동량 완화. 지지 접촉만으로 매수하지 않는다. / 280,000 돌파 후 276,500~280,000 재시험 유지, 당일 거래량가중평균가격 상회와 동일 시간대 누적 상대거래량 1.2 이상. 1.2는 제안 필터이지 관측값이나 충분조건이 아니다.","risk_condition_ko":"258,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003230.KS","display_name":"003230","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1221000.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"003230.KS의 거래일·정규장 상태·거래정지 여부, 최신 체결시각, 호가·스프레드와 실제 5분봉을 먼저 확인한다. 제공된 2026-10-20 종가 1221000원은 현재 실행 가격이 아니다. / 1208000~1218000원 시험 후 회복·유지, 당일 거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상을 관찰한다. 이 조건만으로 부족한 손익비가 개선되지는 않는다.","risk_condition_ko":"1,191,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":148100.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단 기준은 2026-10-21T06:27:20.935172+09:00이며 일봉 기준일은 2026-10-20이다. 이 시계만으로 거래일·휴장 여부·정규장 상태·거래 가능성·호가 신선도를 확정하지 않는다. / 제공 장중 자료는 지연·봉 간격 및 요약가격 불일치가 지적됐다. 최신 정규장 가격 시각, 완료 봉, 거래정지 여부와 유효 호가를 검증하기 전 실행 근거로 사용하지 않는다.","risk_condition_ko":"148,100 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":137900.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"090430.KS 공식 거래일·정규장 상태, 최신 가격·호가·거래량·당일 거래량가중평균가격 및 실제 분봉 간격부터 확인한다. / 135300~136300에서 저점 상승·거래 회복·당일 거래량가중평균가격 재상회와 동시간대 상대거래량 1.0 이상을 관찰한다. 가격 접촉만으로 주문하지 않는다.","risk_condition_ko":"135,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"051900.KS","display_name":"051900","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":273000.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"270000~272000 시험 후 회복, 완성 5분봉 저점 상승, 신선한 당일 거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상. 단독 매수 신호가 아니다. / 284500 돌파와 재시험 지지 여부. 가까운 291500~294000 저항을 반영해 추격하지 않는다.","risk_condition_ko":"282,000 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000100.KS","display_name":"000100","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":86200.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"실제 정규장·휴장·거래정지 여부와 호가 타임스탬프를 확인하고 86,200과 85,200의 가격 불일치 및 봉 간격 오류를 해소한다. / 85,300 방어, 실제 5분봉 두 개의 저점 상승, 당일 거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상을 확인한다. 이 조건만으로 자동 매수하지 않는다.","risk_condition_ko":"85,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"036460.KS","display_name":"036460","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":36550.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"36000~36200원 또는 35850~35950원에서 최신 정규장 5분봉 두 개의 지지 회복·유지, 당일 거래량가중평균가격 상회와 동시간대 상대거래량 1.5 이상 확인. / 36750~37000원 저항 회복과 37250원 돌파·재지지·종가 유지 확인. 가까운 저항 기준 비용 차감 후 보상·위험 비율 검증 전 추격하지 않는다.","risk_condition_ko":"35,850 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"018880.KS","display_name":"018880","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":3905.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"거래소 달력·정규장 여부·거래 상태·호가 시각을 확인한다. 오래된 2026-10-20 20:00 한국시간 자료의 상세 마지막 가격 3890과 일별 요약 3905의 차이 및 실제 5분봉 여부를 대조한다. 오래된 거래량 0을 수요 부재로 해석하지 않는다. / 3830–3860 지지 시험 후 연속된 새로운 5분봉 두 개가 3860 위에서 마감하는지 확인한다. 3895–3905 회복은 추가 증거이며 지지선 접촉만으로 매수하지 않는다.","risk_condition_ko":"3,750 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"086790.KS","display_name":"086790","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":121800.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"086790.KS의 거래일, 정규장 상태, 신선한 호가, 당일 거래량 가중평균가격과 동시간대 상대거래량을 확인한다. 기존 일중 자료에는 지연, 요청·반환 간격 불일치와 상충하는 최종가격이 있어 현재 신호로 사용할 수 없다. 요약 거래량 0은 수요 부재의 증거가 아니다. / 120500–121600원 지지 후보의 실제 유지, 119400원 종가 이탈, 118300원 종가 이탈 후 회복 실패를 각각 구분해 감시한다.","risk_condition_ko":"125,600 이상 도달, 장중 확인 시 (매도 위험관리에 최소 상대거래량 조건을 적용하지 않는다.) 리스크 축소 · 추가 조건 확인 필요: 제공된 기술 분석의 124550–125600원 저항 구간에서 신선한 정규장 자료로 거부 또는 회복·유지 실패가 확인될 때 적용한다. 단순 접촉이나 현재 확인되지 않은 실패를 매도 신호로 간주하지 않는다.","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"105560.KS","display_name":"105560","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":160900.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"105560.KS의 최신 체결 가능 시세·거래일·거래상태·호가·당일 거래량가중평균가격과 비교 가능한 동시간대 상대거래량을 확인한다. / 162,700–163,300 초기 저항과 164,000–164,900 회복 구간을 감시한다. 돌파와 투자경제성은 별도로 평가한다.","risk_condition_ko":"159,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"122350.KQ","display_name":"122350","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1642.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"122350.KQ의 거래 가능 상태, 최신 정규장 체결·스프레드·거래량가중평균가격·동시간대 상대거래량을 확보하고 1642와 지연 분봉 1620의 차이를 해소한다. / 122350.KQ의 1612~1620 재시험 후 1620 회복과 연속 두 개 완성된 5분봉 지지를 관찰한다. 단순 접촉이나 거래량 감소만으로 매수 수요를 확정하지 않는다.","risk_condition_ko":"1,612 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"373220.KS","display_name":"LG에너지솔루션","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":414000.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"눌림목 재평가: 400000~405000 지지, 검증된 5분봉의 저점 상승, 연속 2개 봉의 405000 상회 마감, 거래량가중평균가격 회복과 동시간대 상대거래량 1.2 이상. 현재 매수 지시는 아니다. / 돌파 재평가: 검증된 정규장 종가 433000 초과, 재시험 지지와 다음 확인된 거래일의 유지. 442000~455000 저항까지의 비용 차감 후 손익비를 다시 계산한다.","risk_condition_ko":"422,000 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"011200.KS","display_name":"011200","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":23450.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"011200.KS의 2026-10-21 실제 거래일·휴장·단축장 여부와 최신 정규장 호가·봉 시각을 확인한다. 거래자가 지적한 요약가 23450원과 마지막 봉 23250원의 불일치, 요청한 5분봉 대신 반환된 1분봉 문제를 해소한다. / 기존 보유수량·취득가·현금·업종 집중도·채택 손절을 확인하고 종목 5%, 해운업 10%, 전술 계획손실 0.5% 한도를 점검한다. 초과 확인 시 필요한 만큼 위험 감축하며 자금 마련 목적의 매도로 분류하지 않는다.","risk_condition_ko":"22,600 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":197400.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"195100~196000원 지지·재회복을 신선한 정규장 5분봉, 당일 거래량가중평균가격, 동일 경과시간 상대거래량 1.2 이상으로 확인한다. 단순 가격 도달은 매수 신호가 아니다. / 202000원 초과 종가와 거래량 확인 후 재시험 지지를 관찰한다. 203000원 진입·195000원 방어 예시는 210500원까지 비용 전 약 0.94배여서 그대로 추격하지 않는다.","risk_condition_ko":"195,100 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":556000.0,"market_data_asof":"2026-10-20T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"006400.KS가 553500을 유지하고 556500 위에서 검증된 5분봉 종가 두 개를 연속 형성하는지 관찰한다. 당일 거래량가중평균가격 상회와 같은 경과시간 기준 상대거래량 1.2 이상을 별도로 확인하되, 손익비 미충족 상태에서는 매수하지 않는다. / 545200 이탈 시 526000~530000 지지 구간과 포트폴리오 손실 여력을 재검토한다. 수동적인 저가 주문이나 추가 매수는 하지 않는다.","risk_condition_ko":"526,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-20T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-20T20:10:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-20T14:46:45.874185+09:00",
  "as_of": "2026-10-20T14:43:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
