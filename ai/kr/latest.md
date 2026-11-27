# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-27T06:28:31.761737+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261127T151519_local-freshness-kr-overlay",
  "producer_finished_at": "2026-11-27T15:16:34.167602+09:00",
  "analysis_run_id": "20261127T045657_local-scheduler-kr-full",
  "analysis_completed_at": "2026-11-27T06:56:32.868662+09:00",
  "analysis_trade_date_oldest": "2026-11-26",
  "analysis_trade_date_latest": "2026-11-26",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-27T15:16:00+09:00",
  "market_data_latest_at": "2026-11-27T15:16:00+09:00",
  "market_data_status": "FRESH"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-27T13:50:52.099728+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-27T13:50:52.099728+09:00",
    "run_started_at": "2026-11-27T13:47:25.865623+09:00",
    "run_finished_at": "2026-11-27T13:51:20.399973+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 7356240,
    "total_unrealized_pnl_krw": -7587996,
    "settled_cash_krw": 1016882,
    "available_cash_krw": 1016882,
    "buying_power_krw": 1016882,
    "total_equity_krw": 8373122
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1094000,
      "market_value_krw": 2188000,
      "unrealized_pnl_krw": -3247000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 178400,
      "market_value_krw": 1784000,
      "unrealized_pnl_krw": -1539851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 300500,
      "market_value_krw": 1502500,
      "unrealized_pnl_krw": -572143
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 121300,
      "market_value_krw": 485200,
      "unrealized_pnl_krw": -489800
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 415500,
      "market_value_krw": 415500,
      "unrealized_pnl_krw": -737500
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 14630,
      "market_value_krw": 263340,
      "unrealized_pnl_krw": -304975
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 163450,
      "market_value_krw": 163450,
      "unrealized_pnl_krw": -118884
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 158800,
      "market_value_krw": 158800,
      "unrealized_pnl_krw": -215367
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 51300,
      "market_value_krw": 153900,
      "unrealized_pnl_krw": -146100
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 42625,
      "market_value_krw": 85250,
      "unrealized_pnl_krw": -32950
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 72300,
      "market_value_krw": 72300,
      "unrealized_pnl_krw": -100000
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 43650,
      "market_value_krw": 43650,
      "unrealized_pnl_krw": -69281
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 40350,
      "market_value_krw": 40350,
      "unrealized_pnl_krw": -14150
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":178600.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":175594.4075184449,"relative_volume":0.6845543865248501,"spread_bps":5.5975370836831795,"day_high":179900.0,"day_low":169000.0,"execution_condition_ko":"위험 대응 조건: 170,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"170,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":300000.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":301641.4821086559,"relative_volume":1.8354187062167302,"spread_bps":33.333333333333336,"day_high":322000.0,"day_low":294500.0,"execution_condition_ko":"위험 대응 조건: 303,160 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"303,160 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":72800.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":71258.48207519615,"relative_volume":0.6086299570160562,"spread_bps":13.745704467353953,"day_high":73200.0,"day_low":67300.0,"execution_condition_ko":"위험 대응 조건: 68,100 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"68,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":42800.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":41500.00650010978,"relative_volume":1.0057032971629811,"spread_bps":23.391812865497077,"day_high":43100.0,"day_low":38200.0,"execution_condition_ko":"위험 대응 조건: 38,600 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"38,600 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":40800.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":39428.08629295325,"relative_volume":1.2862271817342361,"spread_bps":12.26241569589209,"day_high":41200.0,"day_low":36800.0,"execution_condition_ko":"위험 대응 조건: 37,200 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"37,200 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1105000.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":1075435.796854985,"relative_volume":0.7103681331973238,"spread_bps":9.053870529651427,"day_high":1110000.0,"day_low":1022000.0,"execution_condition_ko":"1,098,000원 초과 정규장 종가와 직전 20거래일 평균 초과 거래량, 바로 다음 확인된 거래일의 1,097,000~1,098,000원 재시험과 지지 여부. / 11월 26일 기준 10일 지수이동평균 1,123,898원 부근 반응과 1,154,733~1,158,000원 저항대 회복 여부. 상단 회복 전에는 추세 전환으로 보지 않는다.","risk_condition_ko":"1,027,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":418000.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":412209.74284551956,"relative_volume":0.7949743807087332,"spread_bps":11.968880909634949,"day_high":421000.0,"day_low":391500.0,"execution_condition_ko":"393,000~400,000원 저항을 관찰한다. 400,000원 초과 종가와 다음 실제 거래 세션의 지지가 확인되면 예방 감축 및 409,000~416,500원까지의 비용 후 손익비를 재검토한다. 자동 매수나 감축 자동 취소는 아니다. / 383,000원 아래에서 마감하면 366,500~370,500원 지지대를, 그 하단도 이탈해 마감하면 346,000~352,000원 저점대를 확인한다.","risk_condition_ko":"383,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":163400.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":162629.54969737728,"relative_volume":0.4088326927413185,"spread_bps":6.1218243036424855,"day_high":164300.0,"day_low":159900.0,"execution_condition_ko":"158,000~162,200원은 대기 구간이다. 162,200원 위 종가는 반등 재평가 신호일 뿐이며, 166,800원과 168,000~170,000원 저항까지 여유가 작으면 추격하지 않는다. / 일상적인 수준보다 활발한 정규장 거래와 함께 173,845원과 181,570원을 순차 회복하고 다음 확인 정규장에도 지키는지 본다. 약세장 상대 강세의 반복과 11월 23일 보도 이후 외국인·기관 동반 순매도 완화는 보조 증거다. 반등일 투자자별·프로그램 수급과 전용 소셜 자료는 미확인이다.","risk_condition_ko":"158,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":160300.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":156074.7923971679,"relative_volume":0.9180787107773208,"spread_bps":6.240249609984399,"day_high":161500.0,"day_low":145900.0,"execution_condition_ko":"145,900~147,300원 지지, 156,400원 위 종가와 되밀림 방어, 160,157원 위 종가와 거래량 개선을 순서대로 확인한다. 166,353~167,000원은 다음 저항이며 매수·이익실현 주문 수준이 아니다. / 확정 발주나 납품 일정이 나오면 실적 가설부터 재검토한다. 공시 원문에서 반복 현금 창출력이 확인되고 새 지지선을 기준으로 갭과 비용을 반영한 손익비까지 개선돼야 소규모 첫 매수를 검토할 수 있다. 현재 유효한 조건부 매수 계획은 없다.","risk_condition_ko":"145,900 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":43800.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":42852.319857166956,"relative_volume":0.7382142473580304,"spread_bps":11.42204454597373,"day_high":44100.0,"day_low":40550.0,"execution_condition_ko":"43,850원 초과 일봉 종가와 다음 실제 거래일의 43,800~43,850원 지지 또는 재돌파는 기술적 재평가 신호다. 48,850원은 이전 고점이지 목표가가 아니다. 43,850원 대비 이전 고점까지 약 11.4%인 반면 38,400원까지 하방 거리는 약 12.4%이므로 가격 확인만으로 첫 진입을 승인하지 않는다. / 11월 16일 공급계약 정정의 상대방·금액·기간을 원문에서 확인한다. 두코바니 계약으로 간주하지 않는다.","risk_condition_ko":"40,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":121300.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":118878.81464748274,"relative_volume":0.6597370164984263,"spread_bps":8.247422680412372,"day_high":122000.0,"day_low":112000.0,"execution_condition_ko":"117,770원 초과 정규장 종가가 나온 뒤 다음 실제 거래일에 117,300~117,770원 구간의 지지 또는 재돌파와 거래 참여 회복을 확인한다. 122,000~123,600원 저항까지 남은 상방 대비 비용·갭을 반영한 하방 위험을 다시 계산한다. 이는 재평가 신호이지 주문 승인이 아니다. / 112,100원 미만에서 마감하면 110,800원과 105,000~108,500원 지지를 관찰하되 저점을 선매수하지 않는다.","risk_condition_ko":"112,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":52300.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":50736.00994532517,"relative_volume":1.1703007848499254,"spread_bps":19.175455417066154,"day_high":52600.0,"day_low":46700.0,"execution_condition_ko":"48,650원 회복과 49,550원 돌파는 개선 관찰 신호이며 매수 신호가 아니다. / 50,200원 초과 정규장 종가와 그 직후 실제 거래일의 50,000~50,200원 지지 재확인이 모두 나오면 53,900원 첫 저항까지의 비용 차감 후 보상과 갭 손실을 다시 비교한다.","risk_condition_ko":"46,750 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":14580.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":14483.956967487204,"relative_volume":0.8246112191734,"spread_bps":6.856359273225918,"day_high":14730.0,"day_low":13930.0,"execution_condition_ko":"14,410~14,670원 저항대 상단의 종가 돌파와 다음 실제 정규 거래일의 종가 지지를 관찰한다. 2026-11-26 거래량은 20일 평균의 71.6%로 매수세 회복을 확인한 수치가 아니다. / 14,670원에서 다음 저항인 14,970~15,080원까지 상승 여력은 300~410원, 13,820원까지 하방 폭은 850원이다. 비용 전 보상도 위험의 약 0.35~0.48배이므로 추격하지 않고 손절선을 억지로 좁히지 않는다.","risk_condition_ko":"13,820 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"180640.KS","display_name":"180640","is_held":false,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":251500.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":251642.86952413968,"relative_volume":0.3637755762891318,"spread_bps":19.860973187686195,"day_high":260000.0,"day_low":239000.0,"execution_condition_ko":"위험 대응 조건: 246,000 이상 도달, 장중 확인 시 이익실현성 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"246,000 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"지금 실행 검토 가능","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":true,"action_status":"ACTION_SIGNAL_PRESENT","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"034230.KS","display_name":"034230","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":11830.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":11692.998682482192,"relative_volume":1.122047086901666,"spread_bps":33.86960203217612,"day_high":11980.0,"day_low":11410.0,"execution_condition_ko":"11월 26일 저가 11,440원은 첫 지지 참고선이다. 이탈 자체로 매수나 손절을 발동하지 않고 10,900~11,000원 조정 구간의 반응을 본다. / 11,980~12,050원 저항대 위 종가, 거래량 개선, 다음 정규장 지지 재시험은 관찰만 한다. 11월 26일 기준 하락 중인 200일 이동평균 13,223.35원은 장기 추세 참고선이지 목표가가 아니다.","risk_condition_ko":"10,650 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"204620.KQ","display_name":"204620","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":6580.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":6577.347809258804,"relative_volume":1.2759431389483238,"spread_bps":15.186028853454822,"day_high":6740.0,"day_low":6400.0,"execution_condition_ko":"거래 참여 확대를 동반한 6,700원 초과 확정 종가와 다음 실제 정규장의 6,700원 재시험 지지. / 6,350~6,450원 되돌림 중 매도 거래량 둔화와 반등 거래량 회복, 6,450원 이상 확정 종가, 다음 실제 정규장의 6,450원 재시험 지지.","risk_condition_ko":"5,960 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"028050.KS","display_name":"028050","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":58500.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":57972.82979867614,"relative_volume":0.5591444339560042,"spread_bps":17.10863986313088,"day_high":58800.0,"day_low":56600.0,"execution_condition_ko":"55,490~55,527원 지지 시험과 회복 종가를 확인한 후 바로 다음 실제 거래일에 55,500원 초과~55,800원 이하에서 지지가 유지되는지 확인한다. / 60,100~60,550원, 63,200~63,221원, 70,300~70,343원은 반등 강도 확인용이다. 60,550원 돌파만으로는 다음 저항이 가까워 추격하지 않는다.","risk_condition_ko":"55,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":222000.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":221019.39212307468,"relative_volume":0.9828554513318011,"spread_bps":22.547914317925592,"day_high":223000.0,"day_low":218000.0,"execution_condition_ko":"실제 거래일과 정규장 시세의 최신성, 주문 호가의 가격 기준을 확인한 뒤 210,500~211,000원 시험·종가 회복·다음 거래일 재시험 순서를 추적한다. 전일 조회값으로 당일 조건을 충족 처리하지 않는다. / 219,000~220,000원 저항 위 종가와 이후 유지 여부는 관찰만 한다. 11월 25일의 상대 강세는 26일에 이어지지 않았다. 코스피·바이오 업종 대비 상대수익률과 전체 수급을 확인하되 일부 증권사 고객 순매도를 전체 수급으로 보지 않는다.","risk_condition_ko":"210,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"128940.KS","display_name":"128940","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":489000.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":494949.7762509412,"relative_volume":0.9051050260224042,"spread_bps":10.21972406745018,"day_high":506000.0,"day_low":477000.0,"execution_condition_ko":"478,000원 초과 정규장 종가와 거래 참여 개선을 먼저 확인하고, 바로 다음 실제 거래일에는 476,000~478,000원 지지 전환과 비용 반영 손익비를 확인한다. 구간 밖에서는 추격하지 않는다. / 하방은 463,365~464,160원 지지대 회복과 451,350원 종가 이탈을 점검한다. 상방은 493,000~497,000원 안착 후 502,813원과 523,000원을 차례로 본다.","risk_condition_ko":"463,365 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"003350.KS","display_name":"003350","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":14390.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":14240.968073897815,"relative_volume":0.6172726542340672,"spread_bps":6.9516857838025725,"day_high":14980.0,"day_low":13920.0,"execution_condition_ko":"11월 27일 또는 이후 완료된 실제 정규장에서 저가 13,780~14,000원과 같은 날 종가 14,000원 이상을 확인하고, 직후 실제 정규장에서 새 체결가로 지지 유지를 확인한다. / 14,870원 돌파와 재시험은 관찰만 한다. 15,070~15,460원은 저항 구간이지 확정 목표가가 아니다. 무효화 후 12,610~12,670원은 관찰 구간이지 자동 재진입 구간이 아니다.","risk_condition_ko":"13,350 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"048770.KQ","display_name":"048770","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":4340.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":4412.67091464327,"relative_volume":6.148251983717334,"spread_bps":23.014959723820482,"day_high":4665.0,"day_low":4105.0,"execution_condition_ko":"4,465원 위 정규장 종가와 다음 확인된 정규장의 신선한 호가에서 같은 가격 재시험 지지가 모두 나타나는지 확인 / 4,030~4,050원 구간에서 저점이 높아지고 4,240~4,250원을 회복하는지 관찰하되 이 반등만으로는 매수하지 않음","risk_condition_ko":"4,465 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"003230.KS","display_name":"003230","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":1298000.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":1292938.6405577199,"relative_volume":0.6273810053306433,"spread_bps":7.707129094412331,"day_high":1330000.0,"day_low":1272000.0,"execution_condition_ko":"1,326,000원 초과 정규장 종가와 직전 20거래일 평균 초과 거래량, 이어 다음 실제 정규장에서 1,324,000~1,326,000원 재시험 후 하단 지지와 반등 확인 / 1,383,000~1,388,000원 저항과 최신 변동성으로 비용 차감 후 보상 대비 위험 재평가. 자동 익절 구간은 아님","risk_condition_ko":"1,280,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"058610.KQ","display_name":"에스피지","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":92800.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":92395.4740301705,"relative_volume":1.5119702031034203,"spread_bps":10.781671159029651,"day_high":94600.0,"day_low":89600.0,"execution_condition_ko":"93,500원 위 확정 종가 이후 다음 실제 거래일의 93,500원 지지 전환과 94,600원 재돌파·안착을 확인한다. 관찰 신호이며 주문 승인이 아니다. / 92,500원과 91,600~91,943원의 방어 여부를 관찰한다. 지지 반응만으로 매수하지 않는다.","risk_condition_ko":"91,600 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"012030.KS","display_name":"012030","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":2330.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":2304.371751967093,"relative_volume":0.5349786428711546,"spread_bps":21.482277121374864,"day_high":2350.0,"day_low":2240.0,"execution_condition_ko":"2,220~2,240원의 지지 여부를 관찰한다. 2,310원 초과 종가와 거래량 증가가 확인되면 다음 실제 정규장의 지지 전환을 확인한다. 2026-12-04까지 재검토하며, 이 날짜는 주문 만료나 개장 일정이 아니다. / 판단 시각은 2026-11-27 06:23:25 한국시간이다. 일봉은 11월 26일까지이며 제공된 호가는 11월 26일 20:00 한국시간 기준 지연 자료다. 당일 실제 정규장과 최신 체결·공식 종가, 수정주가와 실거래 가격의 기준 일치는 미확인이다.","risk_condition_ko":"2,220 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"011200.KS","display_name":"011200","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":22400.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":22238.839233793624,"relative_volume":0.5182298007992758,"spread_bps":22.29654403567447,"day_high":22450.0,"day_low":22000.0,"execution_condition_ko":"위험 대응 조건: 21,850 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"21,850 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":176100.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":176822.11976474343,"relative_volume":0.9721514969359939,"spread_bps":5.680204487361545,"day_high":180500.0,"day_low":175800.0,"execution_condition_ko":"위험 대응 조건: 177,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"177,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":142200.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":142133.13139038725,"relative_volume":1.0967472485525405,"spread_bps":7.034822370735139,"day_high":147400.0,"day_low":139600.0,"execution_condition_ko":"위험 대응 조건: 144,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"144,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"003490.KS","display_name":"003490","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":30100.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":29935.617549430932,"relative_volume":0.5419918429133073,"spread_bps":16.62510390689942,"day_high":30300.0,"day_low":29150.0,"execution_condition_ko":"위험 대응 조건: 29,950 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"29,950 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"356680.KQ","display_name":"356680","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":14210.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":14316.874052875442,"relative_volume":1.697310686322316,"spread_bps":7.039774727208729,"day_high":14990.0,"day_low":13540.0,"execution_condition_ko":"위험 대응 조건: 13,020 이하 하락, 다음 거래일 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"13,020 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"007810.KS","display_name":"코리아써키트","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":76000.0,"market_data_asof":"2026-11-27T15:16:00+09:00","market_data_clock_status":null,"session_vwap":74852.22138885898,"relative_volume":0.8927688020266565,"spread_bps":13.166556945358789,"day_high":77100.0,"day_low":70800.0,"execution_condition_ko":"위험 대응 조건: 74,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"74,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-27T15:18:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-27T14:48:20.856771+09:00",
  "as_of": "2026-11-27T14:38:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
