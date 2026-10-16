# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-16T01:50:41.769607+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261016T103356_local-scheduler-kr-overlay_only",
  "producer_finished_at": "2026-10-16T10:36:04.979235+09:00",
  "analysis_run_id": "20261016T044900_local-scheduler-kr-full",
  "analysis_completed_at": "2026-10-16T06:51:22.608695+09:00",
  "analysis_trade_date_oldest": "2026-10-15",
  "analysis_trade_date_latest": "2026-10-15",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-16T10:34:00+09:00",
  "market_data_latest_at": "2026-10-16T10:34:00+09:00",
  "market_data_status": "FRESH"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-16T10:36:01.807327+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-16T10:36:01.807327+09:00",
    "run_started_at": "2026-10-16T10:33:56.921648+09:00",
    "run_finished_at": "2026-10-16T10:36:04.979235+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 8821100,
    "total_unrealized_pnl_krw": -6123136,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 9797752
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1302000,
      "market_value_krw": 2604000,
      "unrealized_pnl_krw": -2831000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 216250,
      "market_value_krw": 2162500,
      "unrealized_pnl_krw": -1161351
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 322500,
      "market_value_krw": 1612500,
      "unrealized_pnl_krw": -462143
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 160200,
      "market_value_krw": 640800,
      "unrealized_pnl_krw": -334200
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 529000,
      "market_value_krw": 529000,
      "unrealized_pnl_krw": -624000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 18800,
      "market_value_krw": 338400,
      "unrealized_pnl_krw": -229915
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 69500,
      "market_value_krw": 208500,
      "unrealized_pnl_krw": -91500
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 202000,
      "market_value_krw": 202000,
      "unrealized_pnl_krw": -172167
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 182500,
      "market_value_krw": 182500,
      "unrealized_pnl_krw": -99834
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 130700,
      "market_value_krw": 130700,
      "unrealized_pnl_krw": -41600
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 45950,
      "market_value_krw": 91900,
      "unrealized_pnl_krw": -26300
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 65100,
      "market_value_krw": 65100,
      "unrealized_pnl_krw": -47831
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 53200,
      "market_value_krw": 53200,
      "unrealized_pnl_krw": -1300
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"SELL","strategy_ko":"매도·청산 검토","last_price":65200.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":64578.90196959906,"relative_volume":1.7466316187740685,"spread_bps":15.32567049808429,"day_high":65700.0,"day_low":63500.0,"execution_condition_ko":"위험 대응 조건: 61,500 이하 하락, 2개 봉 확인 후 손절 조건 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"61,500 이하 하락, 2개 봉 확인 후 손절 조건","decision_state_ko":"투자 근거 무효화","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"BUY_NOW","strategy_ko":"지금 분할매수 검토","last_price":18830.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":18643.814553573193,"relative_volume":1.6352425342921648,"spread_bps":5.3120849933598935,"day_high":18990.0,"day_low":18110.0,"execution_condition_ko":"010140.KS의 17,780~17,910원 지지 유지와 18,570원 회복·재시험을 관찰한다. 단독 매수 신호는 아니다. / 19,192원 초과 종가와 직전 완료된 20거래일 평균 대비 1.2배 이상 거래량을 확인한 뒤, 다음 확인된 거래일 첫 30~60분의 지지 유지 여부를 점검한다.","risk_condition_ko":"17,210 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"지금 실행 검토 가능","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":1299000.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":1280348.834090194,"relative_volume":2.4248159217609904,"spread_bps":7.701193685021178,"day_high":1308000.0,"day_low":1247000.0,"execution_condition_ko":"000660.KS 1238000원 방어, 1332000원 돌파·재지지, RSI 30 재돌파와 음의 이동평균 수렴·확산 막대 축소를 관찰한다. 중립 분석가의 의견대로 초기 개선은 약세 강도 재평가 조건이며 자동 매수 승인이 아니다. / 1402000원 저항 회복과 기준일 200일 평균 1452545원 부근의 저항 해소를 확인한다. 이동평균은 실행 전에 갱신한다.","risk_condition_ko":"1,238,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":160300.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":157228.50865545167,"relative_volume":2.8423600632419714,"spread_bps":12.492192379762647,"day_high":161600.0,"day_low":153900.0,"execution_condition_ko":"151600원 방어와 과거 저점 후보 150300원·148000원을 최신 정규장 자료로 확인한다. 지지 이탈 코드는 향후 조건이지 현재 관측 사실이 아니다. / 165600원 회복·재지지, 높아지는 저점, 상승 거래 증가·눌림 거래 감소와 신선한 세션 거래량가중평균가격 상회를 확인한다.","risk_condition_ko":"151,600 이하 하락, 2개 봉 확인 후 (최신 정규장 완료 5분봉 두 개의 종가가 연속으로 기준선 아래이고 두 번째 봉 거래량이 첫 번째보다 증가) 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":529000.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":515516.59037611616,"relative_volume":2.4761107342764763,"spread_bps":18.921475875118258,"day_high":533000.0,"day_low":492500.0,"execution_condition_ko":"267260.KS의 거래일 달력, 실제 거래 상태, 호가 시각, 매수·매도 가격 차이와 정규장 유동성을 확인한다. / 2026-10-15 기준종가 487000원과 뉴스의 481000원 인용값을 대조한다. 지연된 475000원 야간 인용값은 진입 확인에 사용하지 않는다.","risk_condition_ko":"473,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":202000.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":197180.0240105671,"relative_volume":2.2278313781991694,"spread_bps":24.783147459727385,"day_high":202500.0,"day_low":190800.0,"execution_condition_ko":"판단 시각은 2026-10-16T05:18:11.360581+09:00이고 일봉 기준일은 2026-10-15다. 실제 거래일·정규장 운영·거래정지·시장경보 및 최신 시세 시각은 별도 확인이 필요하다. / 10:30은 확인된 정규장에서 시험 진입 재심사를 시작할 수 있는 시각이며 만료 시각이 아니다. 제공된 만료 시각이 없으므로 만료 판정이나 다음 세션 이월을 하지 않는다.","risk_condition_ko":"187,500 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":182400.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":179556.24268293724,"relative_volume":1.493443233700084,"spread_bps":5.483959418700302,"day_high":183800.0,"day_low":174000.0,"execution_condition_ko":"035420.KS 거래일·정규장 시간, 최신 호가 시각, 매수·매도 호가 차이와 체결 유동성을 확인한 뒤 실행한다. / 171100 방어와 종가 이탈, 176100 회복·재시험 및 178000–180500 반락을 구분해 관찰한다. 현재 세션의 충족 신호는 없다.","risk_condition_ko":"171,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"지금 실행 검토 가능","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":130100.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":130895.08191994786,"relative_volume":1.4583732133118037,"spread_bps":15.384615384615385,"day_high":134000.0,"day_low":127700.0,"execution_condition_ko":"353200.KS 실제 거래일·정규장·신선한 호가·거래량·거래량가중평균가격 확인. 전일 야간 122700원과 산식 미확인 상대거래량 23.55는 실행 근거에서 제외한다. / 353200.KS 130300원 회복 및 재시험 지지 후 첫 저항까지 비용 반영 손익비 재계산. 회복만으로 자동 매수하지 않는다.","risk_condition_ko":"135,600 이상 도달, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":45900.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":45643.76016872552,"relative_volume":0.9113220951060657,"spread_bps":43.47826086956522,"day_high":46500.0,"day_low":44900.0,"execution_condition_ko":"083450.KQ 거래일, 거래정지 여부, 시각이 확인된 정규장 호가 및 보유·자산 정보를 먼저 확인한다. / 43,850원과 43,000원의 신규 5분봉 및 제한된 회복 평가 구간을 관찰한다.","risk_condition_ko":"43,850 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":216000.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":213923.2895581988,"relative_volume":1.4820023191522864,"spread_bps":23.174971031286212,"day_high":217500.0,"day_low":210500.0,"execution_condition_ko":"204500원 재시험 후 높은 저점, 상대강도지수 30 회복 및 이동평균 수렴·확산 지표의 음의 폭 축소. / 216500원과 221500원 회복 후 재시험 지지, 최신 정규장 거래량가중평균가격 상회 및 검증된 동일 시간대 상대거래량 1.2배 이상.","risk_condition_ko":"231,273 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":322500.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":322573.27258685336,"relative_volume":3.1376566577292824,"spread_bps":15.49186676994578,"day_high":337000.0,"day_low":300500.0,"execution_condition_ko":"278470.KS의 301000원 돌파·재시험 지지, 저점 상승, 정규장 거래량가중평균가격 상회와 동일 시간대 상대거래량 1.2 이상을 확인한다. 비용 후 보상·위험비 2배 미만이면 매수하지 않는다. / 278470.KS의 278500원부터 283000원까지 지지와 266500원 무효화 기준을 점검한다. 333000원 회복 후 다음 확인된 거래일 지지는 추세 개선 재검토 조건이다.","risk_condition_ko":"278,500 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":69400.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":69237.43068081245,"relative_volume":1.0687719647268803,"spread_bps":14.398848092152628,"day_high":70500.0,"day_low":67900.0,"execution_condition_ko":"66100원 방어와 저점 상승, 63100~64300원 지지 후보 반응 / 갱신된 50일 평균선 회복·재시험과 71600~72700원 저항 소화","risk_condition_ko":"70,270 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":53300.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":51905.44423124231,"relative_volume":1.973335035408719,"spread_bps":18.779342723004696,"day_high":53700.0,"day_low":50300.0,"execution_condition_ko":"403870.KQ의 48,400 지지와 갱신된 50,534 회복, 거래량이 줄어드는 재시험 후 매수 거래량 증가를 확인한다. 이는 관찰 조건이지 현재 매수 주문이 아니다. / 403870.KQ가 50,534 회복에 실패하거나 48,400을 종가로 이탈하면 추가 방어를 검토한다.","risk_condition_ko":"48,400 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"036930.KQ","display_name":"주성엔지니어링","is_held":false,"strategy_code":"SELL","strategy_ko":"매도·청산 검토","last_price":208500.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":209617.15821844526,"relative_volume":2.3427144534539415,"spread_bps":23.952095808383234,"day_high":215000.0,"day_low":202000.0,"execution_condition_ko":"위험 대응 조건: 199,100 이하 하락, 장중 확인 시 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"199,100 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"투자 근거 무효화","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"093370.KS","display_name":"093370","is_held":false,"strategy_code":"SELL","strategy_ko":"매도·청산 검토","last_price":12100.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":12081.464311240476,"relative_volume":0.8884346938394553,"spread_bps":8.261049153242462,"day_high":12510.0,"day_low":11800.0,"execution_condition_ko":"위험 대응 조건: 11,840 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"11,840 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"투자 근거 무효화","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"069540.KQ","display_name":"069540","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":4010.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":3927.8003437226384,"relative_volume":0.9753565321642321,"spread_bps":12.476606363069244,"day_high":4060.0,"day_low":3790.0,"execution_condition_ko":"4035~4085 회복·재시험 지지, 상승하는 5분봉 고점·저점, 당일 거래량가중평균가격 상회와 동일 시간대 상대거래량 1.2 이상 확인. / 4165 상회 종가 이후 다음 실제 거래일 첫 30~60분 동안 4160~4165 지지 유지 확인.","risk_condition_ko":"4,035 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":192900.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":192823.0933823118,"relative_volume":1.8961386354781928,"spread_bps":5.182689816014512,"day_high":195500.0,"day_low":185700.0,"execution_condition_ko":"033780.KS의 거래일 달력, 정규장 여부, 거래 정지, 실행 가능한 최신 호가, 호가 차이, 거래량가중평균가격 및 동일 경과 시간 대비 상대 거래량을 확인한다. / 184000~184600원에서 매도 거래량 감소 후 실제 반등을 확인한다. 단순 접촉은 불충분하며 184400원은 비용 차감 전 산술 상한이지 매수 주문가가 아니다.","risk_condition_ko":"181,800 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"지금 실행 검토 가능","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010950.KS","display_name":"S-Oil","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":157000.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":157999.35476026766,"relative_volume":1.481736135713674,"spread_bps":6.367398917542184,"day_high":162200.0,"day_low":155900.0,"execution_condition_ko":"010950.KS의 156800 회복·다음 5분봉 지지·재시험 유지와 당일 거래량가중평균가격 회복. / 160300~160900, 162500~162700 저항 해소 때마다 가장 가까운 잔여 저항 기준 손익비 재산정.","risk_condition_ko":"156,800 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"086790.KS","display_name":"086790","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":124500.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":123925.14206048149,"relative_volume":1.597628760863436,"spread_bps":8.035355564483728,"day_high":125600.0,"day_low":122400.0,"execution_condition_ko":"086790.KS의 124800원 돌파와 124400~124800원 재지지, 정규장 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상을 확인한다. 모두 충족해도 순손익비와 재무 검증 전에는 매수하지 않는다. / 117800~118300원 방어와 이탈 후 회복 여부를 관찰한다. 113000~114000원은 과거 거래 구간일 뿐 확정 지지나 자동 매수 구간이 아니다.","risk_condition_ko":"117,800 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"지금 실행 검토 가능","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"018880.KS","display_name":"018880","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":3880.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":3831.2345825712073,"relative_volume":1.2000545679595152,"spread_bps":12.894906511927788,"day_high":3900.0,"day_low":3775.0,"execution_condition_ko":"018880.KS: 3,710 또는 3,630–3,670 부근 안정 이후 3,770–3,805 회복과 재시험 성공을 관찰한다. 지지선 접촉만으로 매수하지 않는다. / 018880.KS: 3,920 위 종가와 다음 실제 거래일의 지지 유지 여부를 확인한다. 4,085 돌파도 근거 있는 추가 상승 목표 없이는 매수 사유가 아니다.","risk_condition_ko":"3,630 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":541000.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":536411.3762057006,"relative_volume":2.173938227172667,"spread_bps":18.501387604070306,"day_high":550000.0,"day_low":526000.0,"execution_condition_ko":"위험 대응 조건: 519,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"519,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"지금 실행 검토 가능","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":152600.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":152448.97909317884,"relative_volume":1.1074786164419241,"spread_bps":6.555227794165847,"day_high":156200.0,"day_low":149000.0,"execution_condition_ko":"위험 대응 조건: 152,700 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"152,700 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"373220.KS","display_name":"LG에너지솔루션","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":406500.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":403208.92489313165,"relative_volume":1.543298196831712,"spread_bps":12.307692307692308,"day_high":409500.0,"day_low":397000.0,"execution_condition_ko":"위험 대응 조건: 386,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"386,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"018260.KS","display_name":"삼성SDS","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":201500.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":199782.09631125757,"relative_volume":1.4596938333846574,"spread_bps":24.783147459727385,"day_high":202500.0,"day_low":196200.0,"execution_condition_ko":"위험 대응 조건: 191,100 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"191,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"062040.KS","display_name":"062040","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":180100.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":178544.68665599375,"relative_volume":2.414023236017768,"spread_bps":5.554012774229381,"day_high":182900.0,"day_low":173200.0,"execution_condition_ko":"위험 대응 조건: 172,300 이하 하락, 장중 확인 시 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"172,300 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"131290.KQ","display_name":"티에스이","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":281500.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":278277.55464723654,"relative_volume":2.0588043766449444,"spread_bps":17.74622892635315,"day_high":286000.0,"day_low":269500.0,"execution_condition_ko":"위험 대응 조건: 263,500 이하 하락, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"263,500 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"419050.KQ","display_name":"419050","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":2100.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":2062.5078523152065,"relative_volume":0.9298041310659187,"spread_bps":23.837902264600714,"day_high":2120.0,"day_low":2005.0,"execution_condition_ko":"위험 대응 조건: 1,955 이하 하락, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"1,955 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"033790.KQ","display_name":"033790","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":9340.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":9079.956155224372,"relative_volume":1.3786230384926847,"spread_bps":10.712372790573111,"day_high":9340.0,"day_low":8760.0,"execution_condition_ko":"위험 대응 조건: 8,450 이하 하락, 종가 확인 후 (보호 조치에는 거래량 증가를 요구하지 않는다.) 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"8,450 이하 하락, 종가 확인 후 (보호 조치에는 거래량 증가를 요구하지 않는다.) 리스크 축소","decision_state_ko":"지금 실행 검토 가능","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"036540.KQ","display_name":"036540","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":9170.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":8949.946715127004,"relative_volume":1.0914268894214696,"spread_bps":10.911074740861974,"day_high":9280.0,"day_low":8590.0,"execution_condition_ko":"위험 대응 조건: 8,560 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"8,560 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"452190.KQ","display_name":"452190","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":5120.0,"market_data_asof":"2026-10-16T10:34:00+09:00","session_vwap":5014.006277246931,"relative_volume":0.3151648814174807,"spread_bps":19.550342130987293,"day_high":5150.0,"day_low":4835.0,"execution_condition_ko":"위험 대응 조건: 4,790 이하 하락, 다음 거래일 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"4,790 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-16T11:04:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-16T10:44:51.598956+09:00",
  "as_of": "2026-10-16T10:34:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
