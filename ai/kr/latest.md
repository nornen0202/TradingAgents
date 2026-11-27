# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-27T00:18:12.600085+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261127T045657_local-scheduler-kr-full",
  "producer_finished_at": "2026-11-27T07:17:57.075372+09:00",
  "analysis_run_id": "20261127T045657_local-scheduler-kr-full",
  "analysis_completed_at": "2026-11-27T06:56:32.868662+09:00",
  "analysis_trade_date_oldest": "2026-11-26",
  "analysis_trade_date_latest": "2026-11-26",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-26T20:00:00+09:00",
  "market_data_latest_at": "2026-11-26T20:00:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-27T06:57:14.229857+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-27T06:57:14.229857+09:00",
    "run_started_at": "2026-11-27T04:56:57.460545+09:00",
    "run_finished_at": "2026-11-27T07:17:57.075372+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 7077150,
    "total_unrealized_pnl_krw": -7867086,
    "settled_cash_krw": 1016882,
    "available_cash_krw": 1016882,
    "buying_power_krw": 1016882,
    "total_equity_krw": 8094032
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1053000,
      "market_value_krw": 2106000,
      "unrealized_pnl_krw": -3329000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 171300,
      "market_value_krw": 1713000,
      "unrealized_pnl_krw": -1610851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 298500,
      "market_value_krw": 1492500,
      "unrealized_pnl_krw": -582143
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 113400,
      "market_value_krw": 453600,
      "unrealized_pnl_krw": -521400
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 387500,
      "market_value_krw": 387500,
      "unrealized_pnl_krw": -765500
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 13900,
      "market_value_krw": 250200,
      "unrealized_pnl_krw": -318115
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 160200,
      "market_value_krw": 160200,
      "unrealized_pnl_krw": -122134
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 147700,
      "market_value_krw": 147700,
      "unrealized_pnl_krw": -226467
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 46750,
      "market_value_krw": 140250,
      "unrealized_pnl_krw": -159750
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 39100,
      "market_value_krw": 78200,
      "unrealized_pnl_krw": -40000
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 69900,
      "market_value_krw": 69900,
      "unrealized_pnl_krw": -102400
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 40500,
      "market_value_krw": 40500,
      "unrealized_pnl_krw": -72431
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 37600,
      "market_value_krw": 37600,
      "unrealized_pnl_krw": -16900
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":324000.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":307309.8640364432,"relative_volume":26.4578625161456,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"303160~307310원 시험 후 307310원 이상 정규장 종가와 바로 다음 실제 거래일의 지지·반등을 확인한다. 343000원 돌파는 관찰만 하고 추격하지 않는다. / 350500~353015원 저항대 상단을 넘는 종가와 다음 실제 거래일 지지, 업종 대비 상대강도 지속 여부를 확인한다.","risk_condition_ko":"303,160 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":389500.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":390134.2780852213,"relative_volume":11.482338127539016,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"393,000~400,000원 저항을 관찰한다. 400,000원 초과 종가와 다음 실제 거래 세션의 지지가 확인되면 예방 감축 및 409,000~416,500원까지의 비용 후 손익비를 재검토한다. 자동 매수나 감축 자동 취소는 아니다. / 383,000원 아래에서 마감하면 366,500~370,500원 지지대를, 그 하단도 이탈해 마감하면 346,000~352,000원 저점대를 확인한다.","risk_condition_ko":"383,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":148400.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":151112.3380740152,"relative_volume":12.300395440935555,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"145,900~147,300원 지지, 156,400원 위 종가와 되밀림 방어, 160,157원 위 종가와 거래량 개선을 순서대로 확인한다. 166,353~167,000원은 다음 저항이며 매수·이익실현 주문 수준이 아니다. / 확정 발주나 납품 일정이 나오면 실적 가설부터 재검토한다. 공시 원문에서 반복 현금 창출력이 확인되고 새 지지선을 기준으로 갭과 비용을 반영한 손익비까지 개선돼야 소규모 첫 매수를 검토할 수 있다. 현재 유효한 조건부 매수 계획은 없다.","risk_condition_ko":"145,900 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":160400.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":160429.18373397845,"relative_volume":11.080615342120048,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"158,000~162,200원은 대기 구간이다. 162,200원 위 종가는 반등 재평가 신호일 뿐이며, 166,800원과 168,000~170,000원 저항까지 여유가 작으면 추격하지 않는다. / 일상적인 수준보다 활발한 정규장 거래와 함께 173,845원과 181,570원을 순차 회복하고 다음 확인 정규장에도 지키는지 본다. 약세장 상대 강세의 반복과 11월 23일 보도 이후 외국인·기관 동반 순매도 완화는 보조 증거다. 반등일 투자자별·프로그램 수급과 전용 소셜 자료는 미확인이다.","risk_condition_ko":"158,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":40600.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":40741.16806304946,"relative_volume":12.04980940240857,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"다음 확인된 정규장에서 39,600~40,000원 지지와 41,450원 저항을 점검한다. 41,450원 단독 돌파는 관찰용이다. / 43,850원 상회 종가 이후 다음 실제 거래일의 43,400~43,850원 지지와 거래량을 점검하고, 2026-12-04 한국시간까지 재평가한다.","risk_condition_ko":"39,600 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":39150.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":39917.88770090198,"relative_volume":33.52669525510737,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"38,600원 방어와 39,918~41,000원 회복은 초기 관찰 신호일 뿐 매수 신호는 아니다. / 거래량을 동반한 43,631원 초과 종가 뒤 바로 다음으로 확인된 정규장에서 43,050~43,631원 재시험과 하단 방어를 점검한다. 구간 접촉만으로 사거나 재시험 없는 갭 상승을 추격하지 않는다.","risk_condition_ko":"38,600 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":69700.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":70583.42733501011,"relative_volume":10.805823493581403,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"72,300~73,400원 회복은 초기 반등 관찰 신호일 뿐 매수 조건이 아니다. / 기관 순매도 완화, 동종주 대비 상대 강세, 비교 기준이 확인된 거래량은 보조 신호로만 쓴다. 기준이 불명확한 상대 거래량 10.81배는 제외한다.","risk_condition_ko":"68,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":113000.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":114446.63296429145,"relative_volume":10.928580482820637,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"117,770원 초과 정규장 종가가 나온 뒤 다음 실제 거래일에 117,300~117,770원 구간의 지지 또는 재돌파와 거래 참여 회복을 확인한다. 122,000~123,600원 저항까지 남은 상방 대비 비용·갭을 반영한 하방 위험을 다시 계산한다. 이는 재평가 신호이지 주문 승인이 아니다. / 112,100원 미만에서 마감하면 110,800원과 105,000~108,500원 지지를 관찰하되 저점을 선매수하지 않는다.","risk_condition_ko":"112,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":37600.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"38,964원 일봉 거래량가중 이동평균 회복과 40,750원 돌파·유지는 반등 관찰 신호다. 40,750원에서 단기 저항까지의 폭은 평균 실제 변동폭 3,532원보다 작아 단독 매수 조건이 아니다. / 42,600원 초과 종가 뒤 바로 다음 정규장에 42,350~42,600원 재시험과 지지 유지를 확인한다. 재시험 없이 상승하면 추격하지 않는다. 47,483~48,681원에서는 비중과 손익비를 재평가하되 자동 차익실현은 하지 않는다.","risk_condition_ko":"37,200 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":47100.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":48183.360769566054,"relative_volume":15.860600732732646,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"48,650원 회복과 49,550원 돌파는 개선 관찰 신호이며 매수 신호가 아니다. / 50,200원 초과 정규장 종가와 그 직후 실제 거래일의 50,000~50,200원 지지 재확인이 모두 나오면 53,900원 첫 저항까지의 비용 차감 후 보상과 갭 손실을 다시 비교한다.","risk_condition_ko":"46,750 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1055000.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":1068071.3111163874,"relative_volume":18.404986564982398,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1,098,000원 초과 정규장 종가와 직전 20거래일 평균 초과 거래량, 바로 다음 확인된 거래일의 1,097,000~1,098,000원 재시험과 지지 여부. / 11월 26일 기준 10일 지수이동평균 1,123,898원 부근 반응과 1,154,733~1,158,000원 저항대 회복 여부. 상단 회복 전에는 추세 전환으로 보지 않는다.","risk_condition_ko":"1,027,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":13980.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":14062.51517587601,"relative_volume":14.317630575561727,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"14,410~14,670원 저항대 상단의 종가 돌파와 다음 실제 정규 거래일의 종가 지지를 관찰한다. 2026-11-26 거래량은 20일 평균의 71.6%로 매수세 회복을 확인한 수치가 아니다. / 14,670원에서 다음 저항인 14,970~15,080원까지 상승 여력은 300~410원, 13,820원까지 하방 폭은 850원이다. 비용 전 보상도 위험의 약 0.35~0.48배이므로 추격하지 않고 손절선을 억지로 좁히지 않는다.","risk_condition_ko":"13,820 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":171500.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":173481.5548493583,"relative_volume":15.189149497936624,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"170,000~170,700원 지지를 일봉으로 관찰한다. 지지 유지 자체는 매수 조건이 아니다. 이탈 후 167,000~167,300원은 후속 관찰대일 뿐 손절 대체선이 아니다. / 176,700~179,900원 저항대 상단의 공식 종가 돌파와 다음 실제 거래일의 지지 전환을 확인한다. 185,725원에 가까우면 추격하지 않으며, 189,400~191,500원은 첫 저항을 소화한 이후에만 평가한다.","risk_condition_ko":"170,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"128940.KS","display_name":"128940","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":466500.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"478,000원 초과 정규장 종가와 거래 참여 개선을 먼저 확인하고, 바로 다음 실제 거래일에는 476,000~478,000원 지지 전환과 비용 반영 손익비를 확인한다. 구간 밖에서는 추격하지 않는다. / 하방은 463,365~464,160원 지지대 회복과 451,350원 종가 이탈을 점검한다. 상방은 493,000~497,000원 안착 후 502,813원과 523,000원을 차례로 본다.","risk_condition_ko":"463,365 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003230.KS","display_name":"003230","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1315000.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1,326,000원 초과 정규장 종가와 직전 20거래일 평균 초과 거래량, 이어 다음 실제 정규장에서 1,324,000~1,326,000원 재시험 후 하단 지지와 반등 확인 / 1,383,000~1,388,000원 저항과 최신 변동성으로 비용 차감 후 보상 대비 위험 재평가. 자동 익절 구간은 아님","risk_condition_ko":"1,280,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"180640.KS","display_name":"180640","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":241500.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"233,500~241,500원 눌림목에서 지지가 형성된 뒤 241,500원을 웃도는 종가와 다음 실제 거래일의 지지·보통주 매수세가 함께 확인되면 소액 진입을 재심사한다. 후속 지분 공시는 분쟁 프리미엄의 별도 검증 자료이지 첫 재심사의 필수조건은 아니다. / 253,000원 초과 종가와 다음 거래일 지지는 관찰하되 추격하지 않는다. 269,236원 변동성 참고치까지 16,236원, 233,500원까지 하방 19,500원으로 비용 전 비교도 약 0.83배이며, 상단은 목표가가 아니다.","risk_condition_ko":"246,000 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034230.KS","display_name":"034230","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":11650.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"11월 26일 저가 11,440원은 첫 지지 참고선이다. 이탈 자체로 매수나 손절을 발동하지 않고 10,900~11,000원 조정 구간의 반응을 본다. / 11,980~12,050원 저항대 위 종가, 거래량 개선, 다음 정규장 지지 재시험은 관찰만 한다. 11월 26일 기준 하락 중인 200일 이동평균 13,223.35원은 장기 추세 참고선이지 목표가가 아니다.","risk_condition_ko":"10,650 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"011200.KS","display_name":"011200","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":22150.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"22,350원 회복은 관찰 신호다. 22,750원 초과 종가와 거래량 개선, 다음 실제 거래일의 재시험 지지를 순서대로 확인한다. 안착 시 23,600~23,800원에서 매물 반응과 순보상 여력을 다시 평가한다. / 21,850~22,030원이 무너지면 21,200~21,350원 반응을 본다. 21,200원 미만 종가 뒤 19,840~20,000원은 다음 관찰 구간일 뿐 손절을 미룰 근거가 아니다.","risk_condition_ko":"21,850 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"204620.KQ","display_name":"204620","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":6460.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"거래 참여 확대를 동반한 6,700원 초과 확정 종가와 다음 실제 정규장의 6,700원 재시험 지지. / 6,350~6,450원 되돌림 중 매도 거래량 둔화와 반등 거래량 회복, 6,450원 이상 확정 종가, 다음 실제 정규장의 6,450원 재시험 지지.","risk_condition_ko":"5,960 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003490.KS","display_name":"003490","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":29700.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"29,950~30,100원 회복, 새 정규장 30,100원 초과 종가, 바로 다음 실제 정규장의 30,100~30,200원 지지를 순서대로 본다. 30,911원, 31,350~31,375원, 32,950원은 목표가가 아닌 저항이다. 첫 저항 너머의 상승 여력을 뒷받침할 운영 진척과 실제 비용 반영 후 손익비도 확인한다. / 전자공시시스템의 분기보고서와 자산 양수 공시는 접수만 확인됐다. 원공시 표시 통화·단위·연결 범위·기간·보통주 기준과 해당 시 미국예탁증서 대비 보통주 환산비율은 미확인이다. 거래 통화를 재무제표 표시 통화로 간주하지 않았고, 기간 간 재무금액·주당순이익 비교 및 산정 근거가 불명확한 선행 주가수익비율은 판단에서 제외했다.","risk_condition_ko":"29,950 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"028050.KS","display_name":"028050","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":56800.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"55,490~55,527원 지지 시험과 회복 종가를 확인한 후 바로 다음 실제 거래일에 55,500원 초과~55,800원 이하에서 지지가 유지되는지 확인한다. / 60,100~60,550원, 63,200~63,221원, 70,300~70,343원은 반등 강도 확인용이다. 60,550원 돌파만으로는 다음 저항이 가까워 추격하지 않는다.","risk_condition_ko":"55,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":215500.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"실제 거래일과 정규장 시세의 최신성, 주문 호가의 가격 기준을 확인한 뒤 210,500~211,000원 시험·종가 회복·다음 거래일 재시험 순서를 추적한다. 전일 조회값으로 당일 조건을 충족 처리하지 않는다. / 219,000~220,000원 저항 위 종가와 이후 유지 여부는 관찰만 한다. 11월 25일의 상대 강세는 26일에 이어지지 않았다. 코스피·바이오 업종 대비 상대수익률과 전체 수급을 확인하되 일부 증권사 고객 순매도를 전체 수급으로 보지 않는다.","risk_condition_ko":"210,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":146100.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"눌림목 우선 관찰: 같은 정규장에서 144,100~144,200원 시험과 거래를 동반한 146,300원 이상 마감이 나온 뒤 다음 실제 거래일에도 146,300원을 지키는지 확인한다. / 돌파 관찰: 뚜렷한 거래 참여 속에 152,800원 초과 마감한 뒤 다음 실제 거래일에 152,800원을 지지하거나 되찾는지 확인한다. 가격 확인은 주문 허가와 다르다.","risk_condition_ko":"144,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":179500.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"178,550~178,800원 지지 시험 후 180,000원 회복은 반등 관찰 신호일 뿐 매수가 아니다. 첫 반등 저항은 182,288~183,475원이다. / 186,700원 초과 종가의 거래량과 다음 정규장 재시험을 확인한다. 재시험이 없거나 188,000원을 넘으면 추격하지 않는다.","risk_condition_ko":"177,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003350.KS","display_name":"003350","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":14570.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"11월 27일 또는 이후 완료된 실제 정규장에서 저가 13,780~14,000원과 같은 날 종가 14,000원 이상을 확인하고, 직후 실제 정규장에서 새 체결가로 지지 유지를 확인한다. / 14,870원 돌파와 재시험은 관찰만 한다. 15,070~15,460원은 저항 구간이지 확정 목표가가 아니다. 무효화 후 12,610~12,670원은 관찰 구간이지 자동 재진입 구간이 아니다.","risk_condition_ko":"13,350 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"048770.KQ","display_name":"048770","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":4250.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"4,465원 위 정규장 종가와 다음 확인된 정규장의 신선한 호가에서 같은 가격 재시험 지지가 모두 나타나는지 확인 / 4,030~4,050원 구간에서 저점이 높아지고 4,240~4,250원을 회복하는지 관찰하되 이 반등만으로는 매수하지 않음","risk_condition_ko":"4,465 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"012030.KS","display_name":"012030","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":2250.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2,220~2,240원의 지지 여부를 관찰한다. 2,310원 초과 종가와 거래량 증가가 확인되면 다음 실제 정규장의 지지 전환을 확인한다. 2026-12-04까지 재검토하며, 이 날짜는 주문 만료나 개장 일정이 아니다. / 판단 시각은 2026-11-27 06:23:25 한국시간이다. 일봉은 11월 26일까지이며 제공된 호가는 11월 26일 20:00 한국시간 기준 지연 자료다. 당일 실제 정규장과 최신 체결·공식 종가, 수정주가와 실거래 가격의 기준 일치는 미확인이다.","risk_condition_ko":"2,220 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058610.KQ","display_name":"에스피지","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":89600.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-27 05:53 서울 시각 판단에 사용된 장중 표시는 전일 20:00 서울 시각 기준 지연 자료다. 11월 27일 정규장 체결이나 거래소 일정은 확인되지 않았다. 11월 26일 등락률도 수정주가 자료의 -1.32%와 마감 보도의 -0.44%가 다르므로 거래소 공식 종가와 수정주가 기준을 대조한 뒤 가격선을 적용한다. / 88,100~88,600원 저점대 반응은 관찰하되 독립 매수 신호로 쓰지 않는다. 93,500원 돌파 여부와 비용 차감 후 보상 대비 위험을 2026-12-04 서울 날짜 기준까지 재평가한다. 이는 검토 기한이지 주문 만료나 거래일 지정이 아니다.","risk_condition_ko":"88,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"356680.KQ","display_name":"356680","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":13530.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"13,215~13,230원 일봉 지지가 유지되는지 관찰한다. 지지 확인만으로 매수하지 않는다. / 14,110~14,400원 저항을 넘어 14,400원 위에서 정규장이 마감하고 다음 실제 거래일 종가가 14,400원 이상이면 반등을 재평가한다. 14,950원 부근에서는 추격하지 않으며 다음 저항은 약 15,541원이다.","risk_condition_ko":"13,020 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"007810.KS","display_name":"코리아써키트","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":74100.0,"market_data_asof":"2026-11-26T20:00:00+09:00","market_data_clock_status":null,"session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"74,000~74,100원 시험 후 종가 회복과 다음 실제 거래일의 지지, 동종주 대비 약세 완화를 관찰한다. 77,800원 회복은 첫 개선 신호일 뿐이다. 11월 26일 상대강도지수 45.12와 20일 평균 대비 거래량 62.7%는 과매도나 매도 소진을 입증하지 않는다. / 80,900원 초과 종가 뒤 재시험과 비교 가능한 거래량 개선이 확인되면 84,331원 및 86,980원까지의 보상을 다시 계산한다. 첫 저항을 기준으로 체결비용과 가격 공백을 포함한 위험을 비교하며 자동 매수는 하지 않는다.","risk_condition_ko":"74,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-26T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-26T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-26T15:16:53.425654+09:00",
  "as_of": "2026-11-26T14:38:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
