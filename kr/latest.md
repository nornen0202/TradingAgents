# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-09-29T03:43:15.851533+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20260929T115556_github-actions-overlay-kr",
  "producer_finished_at": "2026-09-29T11:56:37.765622+09:00",
  "analysis_run_id": "20260929T074115_github-actions-kr",
  "analysis_completed_at": "2026-09-29T10:05:08.449263+09:00",
  "analysis_trade_date_oldest": "2026-09-28",
  "analysis_trade_date_latest": "2026-09-28",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-09-29T11:56:00+09:00",
  "market_data_latest_at": "2026-09-29T11:56:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-09-29T11:56:52.403762+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 10925880,
    "total_unrealized_pnl_krw": -4018356,
    "settled_cash_krw": 975902,
    "available_cash_krw": 975902,
    "buying_power_krw": 975902,
    "total_equity_krw": 11901782
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1769000,
      "market_value_krw": 3538000,
      "unrealized_pnl_krw": -1897000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 272000,
      "market_value_krw": 2720000,
      "unrealized_pnl_krw": -603851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 361500,
      "market_value_krw": 1807500,
      "unrealized_pnl_krw": -267143
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
      "current_price_krw": 674000,
      "market_value_krw": 674000,
      "unrealized_pnl_krw": -479000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 19260,
      "market_value_krw": 346680,
      "unrealized_pnl_krw": -221635
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 249000,
      "market_value_krw": 249000,
      "unrealized_pnl_krw": -125167
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 72600,
      "market_value_krw": 217800,
      "unrealized_pnl_krw": -82200
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 194000,
      "market_value_krw": 194000,
      "unrealized_pnl_krw": -88334
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 126900,
      "market_value_krw": 126900,
      "unrealized_pnl_krw": -45400
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 49850,
      "market_value_krw": 99700,
      "unrealized_pnl_krw": -18500
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 79100,
      "market_value_krw": 79100,
      "unrealized_pnl_krw": -33831
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 61200,
      "market_value_krw": 61200,
      "unrealized_pnl_krw": 6700
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":361500.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":363121.5797606379,"relative_volume":0.6391140969382156,"spread_bps":13.840830449826989,"day_high":371500.0,"day_low":360000.0,"execution_condition_ko":"위험 대응 조건: 357,000 이탈 시 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"357,000 이탈 시 리스크 축소","decision_state_ko":"실행 조건 감시 중","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":126900.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":126314.66509105316,"relative_volume":1.734422761468379,"spread_bps":7.883326763894363,"day_high":128500.0,"day_low":121500.0,"execution_condition_ko":"위험 대응 조건: 123,300 이탈 시 이익실현성 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"123,300 이탈 시 이익실현성 축소","decision_state_ko":"지금 실행 검토 가능","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":249000.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":245830.03749287015,"relative_volume":1.4535614476896068,"spread_bps":20.100502512562816,"day_high":250000.0,"day_low":235000.0,"execution_condition_ko":"당일 거래량 가중 평균가격 회복과 245,000원 위 종가·일 거래량 426,000주 초과 / 234,000원 아래 종가 시 위험 축소와 225,000원 지지 확인","risk_condition_ko":"234,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":203000.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":203862.32006243616,"relative_volume":0.5826402755489843,"spread_bps":24.600246002460025,"day_high":207500.0,"day_low":201500.0,"execution_condition_ko":"201000~199494원 지지 반등, 장중 거래량가중평균가격 유지 및 상대 거래량 1.2 이상 / 224000원 초과 일일 종가와 상대 거래량 1.2 이상","risk_condition_ko":"199,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":49850.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":49837.297737925415,"relative_volume":1.0628511771559996,"spread_bps":10.025062656641603,"day_high":50500.0,"day_low":48750.0,"execution_condition_ko":"50,400원 위 종가와 155,000주 이상 거래량 / 48,300~48,800원 조정 구간 지지 및 거래량 회복 확인","risk_condition_ko":"47,448 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":61200.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":59321.64283675387,"relative_volume":3.5401336687701255,"spread_bps":16.35322976287817,"day_high":61500.0,"day_low":55800.0,"execution_condition_ko":"54,170~54,800원 지지와 매도세 완화 및 당일 거래량가중평균가격 회복 / 1,890,000주 이상 거래량을 동반한 57,600원 위 종가","risk_condition_ko":"54,170 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":272000.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":271885.00353171566,"relative_volume":1.0117200019951447,"spread_bps":18.39926402943882,"day_high":276000.0,"day_low":266000.0,"execution_condition_ko":"005930.KS가 285,500원 위로 종가 마감하고 거래량이 21,346,064주 초과하며 다음 거래일에도 해당 가격 유지 / 005930.KS가 266,900~267,800원 지지 구간에서 반등·유지","risk_condition_ko":"266,900 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":72700.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":72620.8908908611,"relative_volume":1.0579215797454191,"spread_bps":13.764624913971094,"day_high":73800.0,"day_low":71300.0,"execution_condition_ko":"058470.KQ의 실시간 거래소 호가 확인 및 2026-08-14 반기 공시 대조 / 70,500 지지 여부와 70,000 아래 종가 감시","risk_condition_ko":"70,000 이탈 시 리스크 축소","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":79100.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":79583.56137246867,"relative_volume":0.808294345408995,"spread_bps":12.634238787113075,"day_high":81100.0,"day_low":79100.0,"execution_condition_ko":"84,502원 이상 종가와 당일 거래량 2,510,000주 이상 동시 확인 / 86,500~87,119원 회복과 다음 거래일 추세 유지","risk_condition_ko":"80,500 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":1768000.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":1770438.6456646787,"relative_volume":1.0208797413467745,"spread_bps":5.654509471303364,"day_high":1788000.0,"day_low":1755000.0,"execution_condition_ko":"1,798,268~1,803,440원 회복 후 1,840,000원 돌파 여부 관찰; 현재 매수 허가는 아님 / 상대거래량 1.2 이상을 동반한 1,935,000원 초과 종가와 다음 거래일 유지","risk_condition_ko":"1,768,000 이탈 시 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":673000.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":677028.3916136703,"relative_volume":1.1338829956651817,"spread_bps":14.847809948032664,"day_high":686000.0,"day_low":671000.0,"execution_condition_ko":"매도 측 위험 재평가 후 상대 거래량 1.2 이상을 동반한 715059 위 종가 / 725602 위 종가와 다음 거래일 지지 또는 재돌파","risk_condition_ko":"689,000 이탈 시 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":19260.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":19499.229152309315,"relative_volume":2.651446189906627,"spread_bps":5.190760446405398,"day_high":20100.0,"day_low":19160.0,"execution_condition_ko":"20,000~20,050원 지지 구간의 종가 유지 여부 / 20,550~20,680.1원 회복 여부: 초기 개선 신호이나 매수 확인은 아님","risk_condition_ko":"20,000 이탈 시 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":194000.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":195052.93928030782,"relative_volume":0.8630671003549129,"spread_bps":5.155968032998196,"day_high":197200.0,"day_low":193800.0,"execution_condition_ko":"203,500원 위 종가와 일일 거래량 663,000주 초과 / 돌파 다음 거래일 203,500원과 당일 거래량가중평균가 유지 및 비용 차감 후 손익비 개선","risk_condition_ko":"194,000 이탈 시 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"000150.KS","display_name":"두산","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1374000.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":1378504.3969307698,"relative_volume":0.92620749212447,"spread_bps":7.280669821623589,"day_high":1413000.0,"day_low":1361000.0,"execution_condition_ko":"000150.KS 종가 1,535,000원 초과 및 거래량 150,000주 이상 / 종가 1,410,000원 이탈 후 1,402,697원 이탈 여부","risk_condition_ko":"1,402,697 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"011070.KS","display_name":"LG이노텍","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":575500.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":577045.2576721831,"relative_volume":1.237315485470862,"spread_bps":17.37619461337967,"day_high":591000.0,"day_low":561000.0,"execution_condition_ko":"563,000~565,000원 지지와 검증된 실시간 거래 조건 / 571,000원 회복 여부와 회복 후 재이탈 여부","risk_condition_ko":"563,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":513000.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":517411.2257228638,"relative_volume":0.9325575171612626,"spread_bps":19.51219512195122,"day_high":527000.0,"day_low":510000.0,"execution_condition_ko":"510000~524000원 지지 확인 후 상대거래량 1.2 이상으로 535000원 위 종가 회복 / 543500~550000원 거래량 동반 회복과 다음 거래일 지지 여부","risk_condition_ko":"524,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"055550.KS","display_name":"055550","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":109600.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":109834.98892647482,"relative_volume":0.5378198907634493,"spread_bps":9.119927040583676,"day_high":110800.0,"day_low":109200.0,"execution_condition_ko":"2026-09-29 이후 가격·거래량·거래량가중평균가격 확인 / 112200 회복 후 113300 초과 종가","risk_condition_ko":"108,200 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":143600.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":142661.05645784995,"relative_volume":0.6966404063986538,"spread_bps":6.966213862765588,"day_high":144200.0,"day_low":141100.0,"execution_condition_ko":"149109~149400원 저항 구간 돌파 여부와 197000주 초과 거래량 확인 / 150800원 초과 후 당일 거래량 가중 평균가격 유지 및 예상 거래량 236400주 이상 확인","risk_condition_ko":"140,200 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"105560.KS","display_name":"105560","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":172300.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":172359.1128896276,"relative_volume":0.6552564424419764,"spread_bps":5.805515239477503,"day_high":174500.0,"day_low":171300.0,"execution_condition_ko":"175821원 위 상대 거래량 1.2배 이상 종가 및 다음 거래일 유지 / 181700원 위 종가 이후 새 목표가격과 비용 반영 손익비 검증","risk_condition_ko":"170,200 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"128940.KS","display_name":"128940","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":509000.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":502139.05585691246,"relative_volume":0.637940407305113,"spread_bps":19.665683382497544,"day_high":514000.0,"day_low":490000.0,"execution_condition_ko":"원공시와 충돌하는 전년 영업이익 비교값 대조 / 534000원 초과 마감 및 상대 거래량 1.2 이상","risk_condition_ko":"498,500 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"000810.KS","display_name":"000810","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":651000.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":652355.7465329006,"relative_volume":0.6104082718945447,"spread_bps":15.349194167306216,"day_high":664000.0,"day_low":646000.0,"execution_condition_ko":"000810.KS 종가 668,000원 초과 및 일일 거래량 121,200주 이상 / 종가 694,250원 초과 후 다음 거래일 686,000원 지지 여부와 705,000원 접근","risk_condition_ko":"642,000 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"062040.KS","display_name":"062040","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":202500.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":201592.25121579933,"relative_volume":0.6130792826717856,"spread_bps":24.72187886279357,"day_high":204000.0,"day_low":199800.0,"execution_condition_ko":"2026-09-29 가격·거래량·장중 거래량가중평균가격을 확인한다. / 199900~200500원 지지와 205500원 회복을 관찰한다.","risk_condition_ko":"198,610 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"088350.KS","display_name":"088350","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":5800.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":5788.276750091247,"relative_volume":0.310758052122082,"spread_bps":17.25625539257981,"day_high":5840.0,"day_low":5740.0,"execution_condition_ko":"5,870~5,900원 회복과 최근 5일 평균 대비 거래량 1.2배 이상 / 다음 거래일 5,900원 및 당일 거래량가중평균가 유지 또는 재돌파","risk_condition_ko":"5,550 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"093370.KS","display_name":"093370","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":13960.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":13898.324947430747,"relative_volume":0.5239869419439486,"spread_bps":7.165890361877462,"day_high":14130.0,"day_low":13610.0,"execution_condition_ko":"공식 거래소 자료로 2026-09-28 종가 14,000원과 13,870원의 차이를 해소하고 당일 시세 확보 / 13,730원 지지 후 14,055.7원 부근 재돌파; 10:30 이후 당일 거래량가중평균가격 지지와 상대거래량 1.2 이상","risk_condition_ko":"13,510 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"005935.KS","display_name":"005935","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":202000.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":204306.3603716153,"relative_volume":1.2240226105907732,"spread_bps":24.783147459727385,"day_high":207000.0,"day_low":201500.0,"execution_condition_ko":"2026-09-29 실제 배당락 가격·배당금과 조정된 기준 가격 확인 / 조정 후 206500 및 203318 상당 지지선, 이어 201440 상당 종가 지지 여부 확인","risk_condition_ko":"201,440 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
```

```json
{"ticker":"047040.KS","display_name":"047040","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":17330.0,"market_data_asof":"2026-09-29T11:56:00+09:00","session_vwap":17530.502361989056,"relative_volume":1.380564422155901,"spread_bps":5.768676088837611,"day_high":18480.0,"day_low":17240.0,"execution_condition_ko":"10:30 이후 19,240원 및 당일 거래량가중평균가격 상회와 상대거래량 1.2 이상 / 19,240원 위 종가 후 다음 거래일 첫 30~60분 동안 해당 가격 유지 또는 재돌파","risk_condition_ko":"17,300 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-29T12:26:00+09:00"}}
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
