# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-22T00:12:53.813600+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261022T090814_local-freshness-kr-overlay",
  "producer_finished_at": "2026-10-22T09:10:24.590248+09:00",
  "analysis_run_id": "20261022T050013_local-scheduler-kr-full",
  "analysis_completed_at": "2026-10-22T07:34:14.045585+09:00",
  "analysis_trade_date_oldest": "2026-10-21",
  "analysis_trade_date_latest": "2026-10-21",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-22T09:09:00+09:00",
  "market_data_latest_at": "2026-10-22T09:10:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-22T09:01:41.253614+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-22T09:01:41.253614+09:00",
    "run_started_at": "2026-10-22T09:01:11.354959+09:00",
    "run_finished_at": "2026-10-22T09:01:45.035851+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 8733100,
    "total_unrealized_pnl_krw": -6211136,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 9709752
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1279000,
      "market_value_krw": 2558000,
      "unrealized_pnl_krw": -2877000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 221750,
      "market_value_krw": 2217500,
      "unrealized_pnl_krw": -1106351
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 314000,
      "market_value_krw": 1570000,
      "unrealized_pnl_krw": -504643
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 165900,
      "market_value_krw": 663600,
      "unrealized_pnl_krw": -311400
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 497500,
      "market_value_krw": 497500,
      "unrealized_pnl_krw": -655500
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 17400,
      "market_value_krw": 313200,
      "unrealized_pnl_krw": -255115
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 200500,
      "market_value_krw": 200500,
      "unrealized_pnl_krw": -173667
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 66500,
      "market_value_krw": 199500,
      "unrealized_pnl_krw": -100500
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 177900,
      "market_value_krw": 177900,
      "unrealized_pnl_krw": -104434
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 134500,
      "market_value_krw": 134500,
      "unrealized_pnl_krw": -37800
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 43800,
      "market_value_krw": 87600,
      "unrealized_pnl_krw": -30600
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 63100,
      "market_value_krw": 63100,
      "unrealized_pnl_krw": -49831
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 50200,
      "market_value_krw": 50200,
      "unrealized_pnl_krw": -4300
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1281000.0,"market_data_asof":"2026-10-22T09:09:00+09:00","session_vwap":1279629.034711685,"relative_volume":1.557917078557122,"spread_bps":7.803355442840422,"day_high":1293000.0,"day_low":1267000.0,"execution_condition_ko":"000660.KS의 1329000~1332000원 돌파·재시험 지지, 신선한 당일 거래량가중평균가격 상회와 동일 시간대 상대거래량 1.2배 이상을 관찰한다. 충족돼도 현재 계획에서는 매수가 발동하지 않는다. / 000660.KS의 1402000원 종가 회복·후속 지지 후 1467000원까지의 비용 후 손익비와 근거 있는 손절폭을 다시 계산한다. 추세 판단 개선과 신규 매수 승인을 구분한다.","risk_condition_ko":"1,254,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-22T09:09:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:11:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":496500.0,"market_data_asof":"2026-10-22T09:09:00+09:00","session_vwap":497341.90763615945,"relative_volume":0.9226936463463162,"spread_bps":10.065425264217414,"day_high":502000.0,"day_low":494000.0,"execution_condition_ko":"267260.KS의 실제 거래일·세션·현재가 시각·거래정지·변동성완화장치·호가단위를 먼저 검증 / 506500 돌파·재시험 지지와 당일 거래량가중평균가격 상회, 동일 경과시간 기준 상대거래량 1.2 이상을 확인하되 손익비 미달이면 계속 대기","risk_condition_ko":"485,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-22T09:09:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:11:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":224250.0,"market_data_asof":"2026-10-22T09:09:00+09:00","session_vwap":222631.56074042313,"relative_volume":1.3720489191762923,"spread_bps":22.29654403567447,"day_high":225500.0,"day_low":220000.0,"execution_condition_ko":"실제 거래일·정규장 일정·거래 가능 상태·최신 체결시각·봉 간격을 먼저 확인한다. 전일 20:00 지연 자료와 산식 미확인 상대거래량 18.24는 현재 진입 신호로 사용하지 않는다. / 228000원 돌파·재지지, 230500~233500원 회복, 당일 거래량가중평균가격 상회와 검증된 동일 시간대 누적 상대거래량 1.2 이상을 관찰한다. 충족만으로 자동 매수하지 않는다.","risk_condition_ko":"217,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-22T09:09:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:11:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":311500.0,"market_data_asof":"2026-10-22T09:09:00+09:00","session_vwap":313105.17501256074,"relative_volume":0.3854639858919277,"spread_bps":16.06425702811245,"day_high":315000.0,"day_low":311000.0,"execution_condition_ko":"원공시의 표시통화·단위·기간·공개 시점·주식 기준과 예탁증서 비율 적용 여부를 확인하고 현금흐름표 이익 출발점 불일치를 조정한다. / 계좌 총비중 3%와 종목 손실예산 0.25% 초과 여부를 먼저 확인한다. 초과분 축소는 저항 구간 도달과 독립적으로 집행한다.","risk_condition_ko":"331,500 이상 도달, 장중 확인 시 (매도에는 상대거래량 하한을 적용하지 않는다.) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-22T09:09:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:11:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":200500.0,"market_data_asof":"2026-10-22T09:09:00+09:00","session_vwap":200750.42586140148,"relative_volume":0.4253087522547703,"spread_bps":24.906600249066003,"day_high":202500.0,"day_low":199600.0,"execution_condition_ko":"042700.KS 최신 정규장 자료에서 212000원 돌파·재지지, 당일 거래량가중평균가격 상회, 검증된 동시간대 상대거래량 1.2배 이상 확인. 1.2배는 제안 기준이지 관측값이 아니다. / 042700.KS 197400~198000원 지지 유지와 이탈 후 회복 여부 확인. 추가 하방 참고 구간은 190800~192200원이며 구조적 손절 기준은 187500원이다.","risk_condition_ko":"197,400 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-22T09:09:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:11:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":177600.0,"market_data_asof":"2026-10-22T09:09:00+09:00","session_vwap":178091.40501666375,"relative_volume":0.9577416850894604,"spread_bps":11.26126126126126,"day_high":179200.0,"day_low":177300.0,"execution_condition_ko":"035420.KS의 실제 거래 일정과 신선한 정규장 자료를 확보하고 181,800원·183,300원의 회복 및 재확인, 동일 거래일 거래량가중평균가 지지와 시간대 보정 상대거래량을 점검한다. / 185,000원 상회 종가, 갱신된 20거래일 평균 대비 1.2배 이상의 하루 거래량, 다음 실제 거래일의 지지를 관찰한다. 통과하더라도 매수 경제성과 별도 승인 여부를 다시 판단한다.","risk_condition_ko":"177,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-22T09:09:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:11:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":165300.0,"market_data_asof":"2026-10-22T09:09:00+09:00","session_vwap":165230.3576150185,"relative_volume":1.8038046470505296,"spread_bps":18.1653042688465,"day_high":167600.0,"day_low":163000.0,"execution_condition_ko":"거래소 일정·정규장 상태·시각이 명시된 최신 시세·시간대가 포함된 주문 유효기한을 확인하고 위험축소 지시를 재평가한다. / 168500 위에서 새로 완료된 5분봉 2개, 성공적인 재지지, 장중 거래량가중평균가격 상회와 동일 경과시간 상대거래량 1.2 이상을 관찰한다. 전일 일거래량 1.73배를 대체 지표로 쓰지 않는다.","risk_condition_ko":"154,200 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-22T09:09:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:11:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":136900.0,"market_data_asof":"2026-10-22T09:09:00+09:00","session_vwap":135126.96073660237,"relative_volume":2.521174917276325,"spread_bps":7.307270734380709,"day_high":137300.0,"day_low":131700.0,"execution_condition_ko":"거래소 달력·거래 가능 여부·현재 호가 시각·정규장 5분봉 집계와 기존 매도 실행 내역을 먼저 확인한다. 오래된 자료의 가격·거래량 불일치를 해소한다. / 136000–136500원 회복과 재시험 성공을 관찰하되 자동 매수로 연결하지 않는다.","risk_condition_ko":"127,000 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-22T09:09:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:11:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":66600.0,"market_data_asof":"2026-10-22T09:09:00+09:00","session_vwap":66664.27452559971,"relative_volume":0.416501582431999,"spread_bps":15.003750937734434,"day_high":67400.0,"day_low":66100.0,"execution_condition_ko":"058470.KQ 원문 접수 시각과 재무통화·단위·기간·주식 기준 확인 및 요약·분기 자료 충돌 해소 / 실제 정규거래 세션, 최신 체결·호가, 당일 거래량가중평균가격과 동시간대 상대거래량 검증","risk_condition_ko":"66,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-22T09:09:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:11:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":62600.0,"market_data_asof":"2026-10-22T09:09:00+09:00","session_vwap":62985.594143025766,"relative_volume":0.8347977006961941,"spread_bps":15.961691939345572,"day_high":63500.0,"day_low":62500.0,"execution_condition_ko":"61500~62600원 방어 구간의 유지와 이탈 후 회복 능력을 관찰한다. 64800원 회복만으로 매수하지 않는다. / 65600원·66400원·66600원 매물 소화를 확인한다. 66600원 지지 전환은 약세 판단의 재검토 신호이지 현재 매수 주문이 아니다.","risk_condition_ko":"64,800 이상 도달, 장중 확인 시 리스크 축소 · 추가 조건 확인 필요: 세 분석가 모두 저항대 도달 자체와 저항 실패를 구분했다. 약한 반등 거래량과 가격 거부 또는 돌파 후 회복 실패가 확인될 때 감축한다.","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-22T09:09:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:11:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":17350.0,"market_data_asof":"2026-10-22T09:09:00+09:00","session_vwap":17410.131772591794,"relative_volume":1.0543552543099552,"spread_bps":11.52073732718894,"day_high":17540.0,"day_low":17280.0,"execution_condition_ko":"010140.KS 실제 거래일·정규장 운영·거래정지 여부와 타임스탬프가 있는 최신 가격·호가·거래량 확보. / 010140.KS 17170~17270원 지지 후보대 유지 또는 이탈 후 재탈환 실패 확인.","risk_condition_ko":"17,170 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-22T09:09:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:11:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":50200.0,"market_data_asof":"2026-10-22T09:09:00+09:00","session_vwap":50082.147039356445,"relative_volume":0.8728196534224731,"spread_bps":19.90049751243781,"day_high":50700.0,"day_low":49300.0,"execution_condition_ko":"403870.KQ의 51,900 회복과 52,800~52,900 돌파·재지지를 신선한 정규장 자료로 확인한다. / 55,000~55,300 회복과 거래량 확대가 낮아지는 고점 구조를 개선하는지 확인하고, 첫 유효 저항까지 비용 후 손익비를 다시 계산한다.","risk_condition_ko":"51,881 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-22T09:09:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:11:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":44000.0,"market_data_asof":"2026-10-22T09:09:00+09:00","session_vwap":44157.546481954065,"relative_volume":0.35262950344225147,"spread_bps":22.675736961451246,"day_high":44600.0,"day_low":43100.0,"execution_condition_ko":"43,050~43,250에서 실제 방어·회복을 관찰하되 가격 접촉만으로 매수하지 않는다. / 45,700~46,400 반등 이후의 회복 실패를 추가 감축 신호로 감시한다. 현재 가격이 구간 아래라는 사실만으로 새 실패 신호를 선언하지 않는다.","risk_condition_ko":"43,050 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-22T09:09:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:11:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":194400.0,"market_data_asof":"2026-10-22T09:09:00+09:00","session_vwap":194925.51990493166,"relative_volume":1.125630863052634,"spread_bps":20.597322348094746,"day_high":196300.0,"day_low":193600.0,"execution_condition_ko":"033780.KS가 196400원을 초과 돌파·재지지하고 장중 거래량가중평균가격과 상대거래량 조건을 충족하면 첫 진입 검토 우선순위를 높인다. 단순 저항 접근은 매수 신호가 아니다. / 033780.KS의 189400~190900원 방어, 하락 거래량 축소와 반등 체결 증가를 감시한다. 190900원 초과 종가 회복 전에는 전체 목표비중 진입을 검토하지 않는다.","risk_condition_ko":"189,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-22T09:09:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:11:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"064400.KS","display_name":"LG CNS","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":73200.0,"market_data_asof":"2026-10-22T09:09:00+09:00","session_vwap":73354.10601412423,"relative_volume":3.628371505977,"spread_bps":13.651877133105803,"day_high":74500.0,"day_low":71400.0,"execution_condition_ko":"실제 거래일·정규장·거래정지 상태·최신 체결 시각을 먼저 확인한다. 현재 보유 유지 판단을 당일 지지 확인으로 오해하지 않는다. / 71000~71600원 지지와 71600원 회복 또는 72800원 돌파·재시험을 관찰한다. 새로운 구조적 손절과 현실적인 첫 저항 기준의 비용 후 보상/위험이 부족하면 거래를 건너뛴다.","risk_condition_ko":"71,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-22T09:09:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:11:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"396300.KQ","display_name":"396300","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":10420.0,"market_data_asof":"2026-10-22T09:10:00+09:00","session_vwap":10502.426390074932,"relative_volume":2.9490078318731086,"spread_bps":28.77697841726619,"day_high":10880.0,"day_low":10170.0,"execution_condition_ko":"396300.KQ의 11,140원 요약값과 마지막 분봉 11,410원 차이를 대조하고 최신 호가를 확보한다. 요청한 5분봉 대신 반환된 1분봉을 그대로 사용하지 말고 완성된 5분봉을 검증한다. / 실제 거래일·휴장·단축거래 여부, 거래 가능 상태, 공식 시장경보, 호가 차이·잔량, 당일 거래량가중평균가격과 동일 경과시간 기준 상대거래량을 확인한다.","risk_condition_ko":"11,250 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"131290.KQ","display_name":"티에스이","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":275000.0,"market_data_asof":"2026-10-22T09:10:00+09:00","session_vwap":278920.6513554217,"relative_volume":1.3563401625548492,"spread_bps":36.36363636363637,"day_high":285500.0,"day_low":270000.0,"execution_condition_ko":"제공된 기준시계는 2026-10-22T06:52:15.581419+09:00이다. 실제 거래일·정규장 일정·거래정지·호가 최신성을 별도로 확인한다. 10:30은 향후 시험 매수의 최초 활성화 하한이지 만료시각이 아니다. 확인된 주문 만료시각은 없으며 다음 세션으로 임의 이월하지 않는다. / 요청한 5분봉과 제공된 1분봉, 요약 가격·거래량의 불일치를 해소한다. 전일 야간 지연 자료를 제외하고 실제 정규장 5분봉·거래량가중평균가격·시간대 보정 상대거래량을 확보한다.","risk_condition_ko":"258,000 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":134000.0,"market_data_asof":"2026-10-22T09:10:00+09:00","session_vwap":133750.90571295866,"relative_volume":0.7556668432307184,"spread_bps":14.925373134328359,"day_high":135600.0,"day_low":132500.0,"execution_condition_ko":"제공된 실행시각 2026-10-22T06:53:48.534012+09:00만으로 거래일·정규장·가격 신선도를 확정하지 않는다. 전일 야간 지연 표시, 1분·5분 봉과 요약가격·거래량 불일치를 먼저 해소한다. / 10:30은 확인된 거래일의 시험 매수 재검토 개시시각이지 만료시각이 아니다. 주문 유효기간은 미확인이므로 새 만료일을 만들거나 다음 거래일로 자동 이월하지 않는다.","risk_condition_ko":"134,600 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"000100.KS","display_name":"000100","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":84200.0,"market_data_asof":"2026-10-22T09:10:00+09:00","session_vwap":85006.71101256467,"relative_volume":2.0464172195497126,"spread_bps":11.883541295306001,"day_high":86500.0,"day_low":84000.0,"execution_condition_ko":"000100.KS 거래 가능 상태와 최신 정규장 자료를 확인한다. 전일 20:00 표시 지연자료, 요약가 86600원과 마지막 봉 86400원의 차이, 요청 5분봉과 반환 1분봉의 차이를 해소한다. 요약 거래량 0을 수요 부재로 해석하지 않는다. / 000100.KS의 85300원 재시험 뒤 85800원 회복을 실제 5분봉 두 개로 확인하고 거래량가중평균가격 상회·반등 거래량 개선·동시간대 상대거래량 1.2 이상을 관찰한다. 이는 매수 예약이 아니다.","risk_condition_ko":"88,500 이상 도달, 2개 봉 확인 후 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"018880.KS","display_name":"018880","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":3805.0,"market_data_asof":"2026-10-22T09:10:00+09:00","session_vwap":3818.1904843734005,"relative_volume":0.6441397943359477,"spread_bps":26.246719160104988,"day_high":3865.0,"day_low":3785.0,"execution_condition_ko":"018880.KS의 실제 거래일·정규장 운영, 타임스탬프가 검증된 최신 시세, 일관된 정규장 5분봉과 당일 거래량가중평균가격 확보. 일봉 거래량가중이동평균을 당일 지표로 대체하지 않는다. / 018880.KS의 3775~3790원 시험 후 회복, 연속 두 개의 완성 5분봉에서 높아지는 저점, 당일 거래량가중평균가격 상회와 동일 시간대 상대거래량 1.2 이상 확인.","risk_condition_ko":"3,775 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"003230.KS","display_name":"003230","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":1254000.0,"market_data_asof":"2026-10-22T09:10:00+09:00","session_vwap":1258479.2452830188,"relative_volume":0.4396357935426073,"spread_bps":15.923566878980893,"day_high":1268000.0,"day_low":1247000.0,"execution_condition_ko":"거래소의 실제 거래일·정규장 상태·거래제한, 시각이 명시된 체결 가능 호가·호가차이·장중 거래량가중평균가격·동시간대 상대거래량을 확인한다. 요청한 봉 주기와 반환된 봉 주기의 불일치도 먼저 해소한다. / 1216000~1218000에서 같은 주기 정규장 봉 두 개의 저점 상승, 장중 거래량가중평균가격 회복, 동시간대 상대거래량 1.2 이상을 관찰한다. 이 조건만으로 진입하지 않고 저항과 손익비를 다시 검증한다.","risk_condition_ko":"1,216,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"011200.KS","display_name":"011200","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":22700.0,"market_data_asof":"2026-10-22T09:09:00+09:00","session_vwap":22795.509708737864,"relative_volume":2.019380268026486,"spread_bps":22.002200220022,"day_high":23200.0,"day_low":22450.0,"execution_condition_ko":"011200.KS의 실제 거래일·거래상태·정규장 시세를 먼저 확인한다. 제공된 야간 시세로 당일 진입이나 지지 이탈을 판정하지 않는다. / 22,850–22,900 지지 유지 후 완료된 5분봉의 22,900 상향 회복, 당일 거래량가중평균가격 상회, 직전 하락봉보다 큰 반등 거래량과 같은 시각 기준 상대거래량 1.2 이상을 관찰한다. 현행 22,000 예시 손절선으로는 신규 손익비 기준을 충족하지 못한다.","risk_condition_ko":"22,850 이하 하락, 종가 확인 후 (방어적 매도에는 거래량 확인을 필수로 요구하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-22T09:09:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:11:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":193800.0,"market_data_asof":"2026-10-22T09:09:00+09:00","session_vwap":193066.90985619082,"relative_volume":2.540994254242473,"spread_bps":5.161290322580645,"day_high":196500.0,"day_low":191200.0,"execution_condition_ko":"068270.KS: 거래일·정규장 상태·거래 제한·호가 시각·스프레드·5분봉 집계와 전체 보유 집중도를 먼저 확인한다. / 068270.KS: 195,100~196,800원 방어, 저점 상승과 거래량가중평균가 회복을 관찰한다. 동시간대 상대거래량 1.2 이상은 제안된 매수 조건이지 이미 충족된 관측치가 아니다.","risk_condition_ko":"195,100 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-22T09:09:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:11:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":540000.0,"market_data_asof":"2026-10-22T09:09:00+09:00","session_vwap":543641.7484187428,"relative_volume":2.5214120778266693,"spread_bps":18.501387604070306,"day_high":554000.0,"day_low":536000.0,"execution_condition_ko":"006400.KS 판단 기준시각은 2026-10-22T06:29:02.312102+09:00이다. 실제 거래일·정규장 운영·거래정지·시세 신선도는 확인 불가다. 2026-10-22T10:30:00+09:00은 이후 최초 검토 가능 시각이지 만료시각이 아니다. 확인된 만료시각이 없으며 다음 세션으로 자동 이월하지 않는다. / 006400.KS 전일 20:00 지연 자료의 요약 554000원과 마지막 분봉 557000원 차이를 대사한다. 요청한 5분봉·최신 호가·당일 거래량가중평균가격·동시간대 상대거래량을 확보한다. 1분봉이나 일봉 거래량가중이동평균 558501원으로 대체하지 않는다.","risk_condition_ko":"526,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-22T09:09:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:11:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"018260.KS","display_name":"삼성SDS","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":211500.0,"market_data_asof":"2026-10-22T09:10:00+09:00","session_vwap":207267.9537590437,"relative_volume":5.924370628800473,"spread_bps":23.668639053254438,"day_high":215000.0,"day_low":198000.0,"execution_condition_ko":"위험 대응 조건: 194,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"194,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"014950.KQ","display_name":"014950","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":8640.0,"market_data_asof":"2026-10-22T09:09:00+09:00","session_vwap":8393.116736520775,"relative_volume":0.9613318899059421,"spread_bps":34.78260869565217,"day_high":8640.0,"day_low":8230.0,"execution_condition_ko":"위험 대응 조건: 7,977 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"7,977 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-22T09:09:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:11:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":143000.0,"market_data_asof":"2026-10-22T09:09:00+09:00","session_vwap":146148.67435636785,"relative_volume":2.2448904269415726,"spread_bps":6.990562740300594,"day_high":151100.0,"day_low":142700.0,"execution_condition_ko":"위험 대응 조건: 160,900 이상 도달, 2개 봉 확인 후 리스크 축소 · 추가 조건 확인 필요: 제공된 분석의 159,600–160,900원 저항 구간에서 거부가 확인되면 초기 축소의 미집행분에 활용한다. 필수 매도 가격이나 이익 실현 목표가 아니며, 해당 가격을 기다리느라 축소를 미루지 않는다. (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"160,900 이상 도달, 2개 봉 확인 후 리스크 축소 · 추가 조건 확인 필요: 제공된 분석의 159,600–160,900원 저항 구간에서 거부가 확인되면 초기 축소의 미집행분에 활용한다. 필수 매도 가격이나 이익 실현 목표가 아니며, 해당 가격을 기다리느라 축소를 미루지 않는다.","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-22T09:09:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:11:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"079650.KQ","display_name":"079650","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":7340.0,"market_data_asof":"2026-10-22T09:09:00+09:00","session_vwap":7456.981951907078,"relative_volume":0.5881654722857197,"spread_bps":13.6332651670075,"day_high":7640.0,"day_low":7330.0,"execution_condition_ko":"위험 대응 조건: 7,320 이하 하락, 2개 봉 확인 후 (실제 거래가 있는 연속 두 개의 5분봉 종가가 7320 미만이고 회복하지 못할 때) 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"7,320 이하 하락, 2개 봉 확인 후 (실제 거래가 있는 연속 두 개의 5분봉 종가가 7320 미만이고 회복하지 못할 때) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-22T09:09:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:11:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"373220.KS","display_name":"LG에너지솔루션","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":396000.0,"market_data_asof":"2026-10-22T09:10:00+09:00","session_vwap":400005.25172039116,"relative_volume":2.2104564608103194,"spread_bps":12.634238787113075,"day_high":409000.0,"day_low":395500.0,"execution_condition_ko":"위험 대응 조건: 402,500 이하 하락, 종가 확인 후 (확정 종가 하회와 일봉 거래량 증가를 함께 확인) 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"402,500 이하 하락, 종가 확인 후 (확정 종가 하회와 일봉 거래량 증가를 함께 확인) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010950.KS","display_name":"S-Oil","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":138200.0,"market_data_asof":"2026-10-22T09:10:00+09:00","session_vwap":141091.60954408892,"relative_volume":1.9612846090960627,"spread_bps":14.47178002894356,"day_high":149200.0,"day_low":137500.0,"execution_condition_ko":"위험 대응 조건: 151,135 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"151,135 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-22T09:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-21T14:47:34.830079+09:00",
  "as_of": "2026-10-21T14:44:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
