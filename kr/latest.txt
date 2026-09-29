# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-09-29T03:58:25.392134+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20260929T125551_github-actions-overlay-kr",
  "producer_finished_at": "2026-09-29T12:56:38.971098+09:00",
  "analysis_run_id": "20260929T074115_github-actions-kr",
  "analysis_completed_at": "2026-09-29T10:05:08.449263+09:00",
  "analysis_trade_date_oldest": "2026-09-28",
  "analysis_trade_date_latest": "2026-09-28",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-09-29T12:56:00+09:00",
  "market_data_latest_at": "2026-09-29T12:56:20.376049+09:00",
  "market_data_status": "FRESH"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-09-29T12:56:54.719074+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 10893350,
    "total_unrealized_pnl_krw": -4050886,
    "settled_cash_krw": 975902,
    "available_cash_krw": 975902,
    "buying_power_krw": 975902,
    "total_equity_krw": 11869252
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1759000,
      "market_value_krw": 3518000,
      "unrealized_pnl_krw": -1917000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 271250,
      "market_value_krw": 2712500,
      "unrealized_pnl_krw": -611351
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 359500,
      "market_value_krw": 1797500,
      "unrealized_pnl_krw": -277143
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 203000,
      "market_value_krw": 812000,
      "unrealized_pnl_krw": -163000
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 675000,
      "market_value_krw": 675000,
      "unrealized_pnl_krw": -478000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 19275,
      "market_value_krw": 346950,
      "unrealized_pnl_krw": -221365
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 249500,
      "market_value_krw": 249500,
      "unrealized_pnl_krw": -124667
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 72700,
      "market_value_krw": 218100,
      "unrealized_pnl_krw": -81900
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 194200,
      "market_value_krw": 194200,
      "unrealized_pnl_krw": -88134
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 127000,
      "market_value_krw": 127000,
      "unrealized_pnl_krw": -45300
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 51500,
      "market_value_krw": 103000,
      "unrealized_pnl_krw": -15200
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 79300,
      "market_value_krw": 79300,
      "unrealized_pnl_krw": -33631
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 60300,
      "market_value_krw": 60300,
      "unrealized_pnl_krw": 5800
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":359500.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":362850.1432360079,"relative_volume":0.5544001735722542,"spread_bps":13.89854065323141,"day_high":371500.0,"day_low":359500.0,"execution_condition_ko":"위험 대응 조건: 357,000 이탈 시 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"357,000 이탈 시 리스크 축소","decision_state_ko":"실행 조건 감시 중","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":249000.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":246587.7671597125,"relative_volume":1.3023798687380488,"spread_bps":20.060180541624874,"day_high":252000.0,"day_low":235000.0,"execution_condition_ko":"당일 거래량 가중 평균가격 회복과 245,000원 위 종가·일 거래량 426,000주 초과 / 234,000원 아래 종가 시 위험 축소와 225,000원 지지 확인","risk_condition_ko":"234,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":204000.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":203820.85504111502,"relative_volume":0.4968098742595919,"spread_bps":24.539877300613497,"day_high":207500.0,"day_low":201500.0,"execution_condition_ko":"201000~199494원 지지 반등, 장중 거래량가중평균가격 유지 및 상대 거래량 1.2 이상 / 224000원 초과 일일 종가와 상대 거래량 1.2 이상","risk_condition_ko":"199,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":51500.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":50456.94320892807,"relative_volume":1.5607872325518344,"spread_bps":19.398642095053347,"day_high":51700.0,"day_low":48750.0,"execution_condition_ko":"50,400원 위 종가와 155,000주 이상 거래량 / 48,300~48,800원 조정 구간 지지 및 거래량 회복 확인","risk_condition_ko":"47,448 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":60200.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":59474.91478229077,"relative_volume":3.003795638259071,"spread_bps":16.59751037344398,"day_high":61500.0,"day_low":55800.0,"execution_condition_ko":"54,170~54,800원 지지와 매도세 완화 및 당일 거래량가중평균가격 회복 / 1,890,000주 이상 거래량을 동반한 57,600원 위 종가","risk_condition_ko":"54,170 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":271500.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":271925.1984606651,"relative_volume":0.8683557270338383,"spread_bps":18.433179723502302,"day_high":276000.0,"day_low":266000.0,"execution_condition_ko":"005930.KS가 285,500원 위로 종가 마감하고 거래량이 21,346,064주 초과하며 다음 거래일에도 해당 가격 유지 / 005930.KS가 266,900~267,800원 지지 구간에서 반등·유지","risk_condition_ko":"266,900 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":72600.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":72647.58555742053,"relative_volume":0.913021515796739,"spread_bps":13.764624913971094,"day_high":73800.0,"day_low":71300.0,"execution_condition_ko":"058470.KQ의 실시간 거래소 호가 확인 및 2026-08-14 반기 공시 대조 / 70,500 지지 여부와 70,000 아래 종가 감시","risk_condition_ko":"70,000 이탈 시 리스크 축소","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":194400.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":194940.5085218935,"relative_volume":0.7322105737396307,"spread_bps":5.145356315924878,"day_high":197200.0,"day_low":193800.0,"execution_condition_ko":"203,500원 위 종가와 일일 거래량 663,000주 초과 / 돌파 다음 거래일 203,500원과 당일 거래량가중평균가 유지 및 비용 차감 후 손익비 개선","risk_condition_ko":"194,000 이탈 시 리스크 축소","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":127200.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":126500.00239903008,"relative_volume":1.500897185739773,"spread_bps":7.858546168958743,"day_high":128500.0,"day_low":121500.0,"execution_condition_ko":"353200.KS가 상대거래량 1.2 이상으로 129100원 위에 마감하면 별도 진입 심사 / 121400원 및 119400원 재시험 후 지지 여부","risk_condition_ko":"123,300 이탈 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":79300.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":79512.30093488857,"relative_volume":0.7198667899964771,"spread_bps":12.618296529968456,"day_high":81100.0,"day_low":79000.0,"execution_condition_ko":"84,502원 이상 종가와 당일 거래량 2,510,000주 이상 동시 확인 / 86,500~87,119원 회복과 다음 거래일 추세 유지","risk_condition_ko":"80,500 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":1759000.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":1769823.5986695348,"relative_volume":0.8794771470427616,"spread_bps":5.683432793407218,"day_high":1788000.0,"day_low":1755000.0,"execution_condition_ko":"1,798,268~1,803,440원 회복 후 1,840,000원 돌파 여부 관찰; 현재 매수 허가는 아님 / 상대거래량 1.2 이상을 동반한 1,935,000원 초과 종가와 다음 거래일 유지","risk_condition_ko":"1,768,000 이탈 시 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":676000.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":676707.8091525588,"relative_volume":0.9869109021011988,"spread_bps":14.803849000740191,"day_high":686000.0,"day_low":671000.0,"execution_condition_ko":"매도 측 위험 재평가 후 상대 거래량 1.2 이상을 동반한 715059 위 종가 / 725602 위 종가와 다음 거래일 지지 또는 재돌파","risk_condition_ko":"689,000 이탈 시 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":19275.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":19483.177876222144,"relative_volume":2.125771835284599,"spread_bps":5.188067444876784,"day_high":20100.0,"day_low":19160.0,"execution_condition_ko":"20,000~20,050원 지지 구간의 종가 유지 여부 / 20,550~20,680.1원 회복 여부: 초기 개선 신호이나 매수 확인은 아님","risk_condition_ko":"20,000 이탈 시 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"000150.KS","display_name":"두산","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1379000.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":1378888.6838868388,"relative_volume":0.7730718190091408,"spread_bps":7.249003262051468,"day_high":1413000.0,"day_low":1361000.0,"execution_condition_ko":"000150.KS 종가 1,535,000원 초과 및 거래량 150,000주 이상 / 종가 1,410,000원 이탈 후 1,402,697원 이탈 여부","risk_condition_ko":"1,402,697 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"011070.KS","display_name":"LG이노텍","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":575000.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":577153.6715153862,"relative_volume":1.0292188331697747,"spread_bps":17.37619461337967,"day_high":591000.0,"day_low":561000.0,"execution_condition_ko":"563,000~565,000원 지지와 검증된 실시간 거래 조건 / 571,000원 회복 여부와 회복 후 재이탈 여부","risk_condition_ko":"563,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":512000.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":516676.4327749626,"relative_volume":0.8030866954589899,"spread_bps":19.550342130987293,"day_high":527000.0,"day_low":510000.0,"execution_condition_ko":"510000~524000원 지지 확인 후 상대거래량 1.2 이상으로 535000원 위 종가 회복 / 543500~550000원 거래량 동반 회복과 다음 거래일 지지 여부","risk_condition_ko":"524,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"055550.KS","display_name":"055550","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":109900.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":109850.18570591499,"relative_volume":0.489598105995418,"spread_bps":9.095043201455207,"day_high":110800.0,"day_low":109200.0,"execution_condition_ko":"2026-09-29 이후 가격·거래량·거래량가중평균가격 확인 / 112200 회복 후 113300 초과 종가","risk_condition_ko":"108,200 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":142700.0,"market_data_asof":"2026-09-29T12:56:20.376049+09:00","session_vwap":142728.1283559192,"relative_volume":0.6268423911399569,"spread_bps":7.010164738871364,"day_high":144200.0,"day_low":141100.0,"execution_condition_ko":"149109~149400원 저항 구간 돌파 여부와 197000주 초과 거래량 확인 / 150800원 초과 후 당일 거래량 가중 평균가격 유지 및 예상 거래량 236400주 이상 확인","risk_condition_ko":"140,200 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:20.376049+09:00"}}
```

```json
{"ticker":"105560.KS","display_name":"105560","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":172700.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":172398.0448040014,"relative_volume":0.5822870341192611,"spread_bps":5.788712011577424,"day_high":174500.0,"day_low":171300.0,"execution_condition_ko":"175821원 위 상대 거래량 1.2배 이상 종가 및 다음 거래일 유지 / 181700원 위 종가 이후 새 목표가격과 비용 반영 손익비 검증","risk_condition_ko":"170,200 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"128940.KS","display_name":"128940","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":511000.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":503200.1462947082,"relative_volume":0.552071708011813,"spread_bps":19.58863858961802,"day_high":514000.0,"day_low":490000.0,"execution_condition_ko":"원공시와 충돌하는 전년 영업이익 비교값 대조 / 534000원 초과 마감 및 상대 거래량 1.2 이상","risk_condition_ko":"498,500 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"000810.KS","display_name":"000810","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":651000.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":652123.6813052011,"relative_volume":0.5462731475577114,"spread_bps":15.372790161414297,"day_high":664000.0,"day_low":646000.0,"execution_condition_ko":"000810.KS 종가 668,000원 초과 및 일일 거래량 121,200주 이상 / 종가 694,250원 초과 후 다음 거래일 686,000원 지지 여부와 705,000원 접근","risk_condition_ko":"642,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"062040.KS","display_name":"062040","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":202000.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":201735.34706565554,"relative_volume":0.5398714131484547,"spread_bps":24.783147459727385,"day_high":204000.0,"day_low":199800.0,"execution_condition_ko":"2026-09-29 가격·거래량·장중 거래량가중평균가격을 확인한다. / 199900~200500원 지지와 205500원 회복을 관찰한다.","risk_condition_ko":"198,610 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"088350.KS","display_name":"088350","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":5770.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":5787.455171717746,"relative_volume":0.28029380417324645,"spread_bps":17.316017316017316,"day_high":5840.0,"day_low":5740.0,"execution_condition_ko":"5,870~5,900원 회복과 최근 5일 평균 대비 거래량 1.2배 이상 / 다음 거래일 5,900원 및 당일 거래량가중평균가 유지 또는 재돌파","risk_condition_ko":"5,550 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"093370.KS","display_name":"093370","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":13960.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":13908.595680017823,"relative_volume":0.4524438679927589,"spread_bps":7.165890361877462,"day_high":14130.0,"day_low":13610.0,"execution_condition_ko":"공식 거래소 자료로 2026-09-28 종가 14,000원과 13,870원의 차이를 해소하고 당일 시세 확보 / 13,730원 지지 후 14,055.7원 부근 재돌파; 10:30 이후 당일 거래량가중평균가격 지지와 상대거래량 1.2 이상","risk_condition_ko":"13,510 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"005935.KS","display_name":"005935","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":200250.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":203822.75875480118,"relative_volume":1.0837199039847363,"spread_bps":24.968789013732835,"day_high":207000.0,"day_low":200000.0,"execution_condition_ko":"2026-09-29 실제 배당락 가격·배당금과 조정된 기준 가격 확인 / 조정 후 206500 및 203318 상당 지지선, 이어 201440 상당 종가 지지 여부 확인","risk_condition_ko":"201,440 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

```json
{"ticker":"047040.KS","display_name":"047040","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":17340.0,"market_data_asof":"2026-09-29T12:56:00+09:00","session_vwap":17513.882858813548,"relative_volume":1.1298147924057176,"spread_bps":5.768676088837611,"day_high":18480.0,"day_low":17240.0,"execution_condition_ko":"10:30 이후 19,240원 및 당일 거래량가중평균가격 상회와 상대거래량 1.2 이상 / 19,240원 위 종가 후 다음 거래일 첫 30~60분 동안 해당 가격 유지 또는 재돌파","risk_condition_ko":"17,300 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T13:26:00+09:00"}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-09-29T10:52:20.212944+09:00",
  "as_of": "2026-09-29T10:22:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
