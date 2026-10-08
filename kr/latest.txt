# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-08T01:47:56.487115+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261008T095721_github-actions-overlay-kr-37710239556-1",
  "producer_finished_at": "2026-10-08T09:58:49.033862+09:00",
  "analysis_run_id": "20261008T071336_github-actions-kr",
  "analysis_completed_at": "2026-10-08T07:29:41.125908+09:00",
  "analysis_trade_date_oldest": "2026-10-07",
  "analysis_trade_date_latest": "2026-10-07",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-08T09:57:00+09:00",
  "market_data_latest_at": "2026-10-08T09:58:00.706180+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-08T09:58:46.929708+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-08T09:58:46.929708+09:00",
    "run_started_at": "2026-10-08T09:57:21.975180+09:00",
    "run_finished_at": "2026-10-08T09:58:49.033862+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 10832660,
    "total_unrealized_pnl_krw": -4111576,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 11809312
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1728000,
      "market_value_krw": 3456000,
      "unrealized_pnl_krw": -1979000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 266500,
      "market_value_krw": 2665000,
      "unrealized_pnl_krw": -658851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 369000,
      "market_value_krw": 1845000,
      "unrealized_pnl_krw": -229643
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 196700,
      "market_value_krw": 786800,
      "unrealized_pnl_krw": -188200
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 598000,
      "market_value_krw": 598000,
      "unrealized_pnl_krw": -555000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 19120,
      "market_value_krw": 344160,
      "unrealized_pnl_krw": -224155
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 272000,
      "market_value_krw": 272000,
      "unrealized_pnl_krw": -102167
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 88700,
      "market_value_krw": 266100,
      "unrealized_pnl_krw": -33900
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 183800,
      "market_value_krw": 183800,
      "unrealized_pnl_krw": -98534
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 157400,
      "market_value_krw": 157400,
      "unrealized_pnl_krw": -14900
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 58000,
      "market_value_krw": 116000,
      "unrealized_pnl_krw": -2200
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 76900,
      "market_value_krw": 76900,
      "unrealized_pnl_krw": -36031
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 65500,
      "market_value_krw": 65500,
      "unrealized_pnl_krw": 11000
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":266250.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":267927.64755073184,"relative_volume":1.4462033738377,"spread_bps":18.779342723004696,"day_high":270000.0,"day_low":266000.0,"execution_condition_ko":"위험 대응 조건: 268,500 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"268,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":197500.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":200225.48216438235,"relative_volume":3.08760656652982,"spread_bps":5.0620096178182745,"day_high":205500.0,"day_low":197200.0,"execution_condition_ko":"위험 대응 조건: 207,716 이상 도달, 장중 확인 시 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"207,716 이상 도달, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":76700.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":77809.81283020129,"relative_volume":2.240415465192879,"spread_bps":13.029315960912053,"day_high":79600.0,"day_low":76600.0,"execution_condition_ko":"위험 대응 조건: 79,670 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"79,670 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":157600.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":156886.53072419632,"relative_volume":3.375963919743843,"spread_bps":6.34719136781974,"day_high":159900.0,"day_low":151200.0,"execution_condition_ko":"위험 대응 조건: 151,300 이상 도달, 장중 확인 시 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"151,300 이상 도달, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"지금 실행 검토 가능","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":58000.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":57086.54921265956,"relative_volume":3.1218785292957576,"spread_bps":17.22652885443583,"day_high":58200.0,"day_low":55700.0,"execution_condition_ko":"2026-10-08 정규장 여부와 실시간 가격·거래량가중평균가격·동시간대 상대거래량 확인 / 56,900~57,117원 돌파 지속과 57,117원 위 종가 확인","risk_condition_ko":"54,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":368500.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":366989.2527226436,"relative_volume":2.225212239149969,"spread_bps":13.559322033898306,"day_high":380500.0,"day_low":361500.0,"execution_condition_ko":"검증된 정규장 종가 384500원 초과, 상대거래량 1.2 이상 및 다음 거래 세션 지지 / 379033~381860원 저항 부근 재차 거절 또는 368093원 이탈","risk_condition_ko":"363,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":272000.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":267040.61103832844,"relative_volume":1.5925842385182392,"spread_bps":18.39926402943882,"day_high":273000.0,"day_low":261000.0,"execution_condition_ko":"042700.KS의 정규장 개장 여부, 실시간 가격, 당일 거래량가중평균가격, 상대거래량 확인 / 257400원 지지 후 264500원 재돌파 확인","risk_condition_ko":"275,000 이상 도달, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":65600.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":65176.26098025827,"relative_volume":1.607074061112576,"spread_bps":15.255530129672007,"day_high":66900.0,"day_low":63800.0,"execution_condition_ko":"68,800~70,000원 저항 재시험과 재차 밀림 여부 / 70,000원 초과 종가 및 일 거래량 2,445,605주 초과 여부","risk_condition_ko":"68,800 이상 도달, 장중 확인 시 (저항 재시험 후 재차 밀릴 때) 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1732000.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":1734269.6358467154,"relative_volume":1.418716767070478,"spread_bps":5.775339301183945,"day_high":1750000.0,"day_low":1722000.0,"execution_condition_ko":"1,683,000~1,690,000원 지지 반등과 신선한 장중 가격·거래량 확인 / 1,779,000원 재돌파 및 1,795,000~1,799,000원 회복","risk_condition_ko":"1,690,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":599000.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":607847.1613570339,"relative_volume":2.3700865911034277,"spread_bps":16.70843776106934,"day_high":626000.0,"day_low":598000.0,"execution_condition_ko":"실제 정규장과 267260.KS 실시간 호가·동시간대 거래량 확인 / 626000원 유지와 643000원 회복 여부","risk_condition_ko":"643,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":19130.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":19225.285967786887,"relative_volume":1.7594619039826633,"spread_bps":5.226025607525476,"day_high":19500.0,"day_low":19110.0,"execution_condition_ko":"확인된 정규장에서 20,150원 상회, 당일 거래량가중평균가 상회 및 같은 시각 기준 상대거래량 1.2 이상 / 20,150원 위 종가와 거래량 3,516,510주 이상 확인 후 다음 거래일 20,150원 유지","risk_condition_ko":"19,330 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":88600.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":87001.7781841996,"relative_volume":2.6676415485862788,"spread_bps":11.29305477131564,"day_high":89800.0,"day_low":84600.0,"execution_condition_ko":"검증된 정규장에서 86,247원과 86,529원 회복·유지 여부 / 88,700원 위 종가와 동시간대 상대거래량 1.2 이상 여부","risk_condition_ko":"84,300 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":183800.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":184311.81795710442,"relative_volume":3.044342196709753,"spread_bps":5.442176870748299,"day_high":188400.0,"day_low":183100.0,"execution_condition_ko":"035420.KS의 실제 거래일·정규장 상태·호가 신선도와 당일 거래량가중평균가격 확인 / 189,000원 지지와 191,400원·194,300원·194,700원·196,800원 순차 회복 여부","risk_condition_ko":"189,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":133500.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":134694.18225315356,"relative_volume":1.2498195266991416,"spread_bps":7.493443237167479,"day_high":138900.0,"day_low":132800.0,"execution_condition_ko":"위험 대응 조건: 137,800 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"137,800 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010950.KS","display_name":"S-Oil","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":168500.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":169550.79474003383,"relative_volume":1.0867084890441097,"spread_bps":5.932957579353308,"day_high":171600.0,"day_low":167500.0,"execution_condition_ko":"173700 위 정규장 종가와 일일 거래량 486490주 이상 / 160617~162900 구간의 확인된 지지 및 재매수세","risk_condition_ko":"170,600 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"105560.KS","display_name":"105560","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":165900.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":166951.66513856436,"relative_volume":1.0549853289581639,"spread_bps":6.0259114191021395,"day_high":168500.0,"day_low":165600.0,"execution_condition_ko":"검증된 정규장에서 170,471원 상향 돌파, 실시간 거래량가중평균가격 상회 및 시각 보정 상대거래량 1.2 이상 / 170,471원 위 정규장 종가와 약 900,776주 이상의 거래량","risk_condition_ko":"165,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"007660.KS","display_name":"이수페타시스","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":124700.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":122980.63641345067,"relative_volume":1.585024239239053,"spread_bps":8.022462896109104,"day_high":125600.0,"day_low":119800.0,"execution_condition_ko":"실제 정규장 체결로 121,000원과 119,365원 지지 확인 / 127,872원 위 종가와 상대거래량 1.2배 이상 확인","risk_condition_ko":"119,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"036930.KQ","display_name":"주성엔지니어링","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":262500.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":256783.75710646133,"relative_volume":3.9434050565072383,"spread_bps":19.065776930409914,"day_high":267000.0,"day_low":245000.0,"execution_condition_ko":"실제 거래 가능 세션에서 246500원과 242500원 지지 여부 확인 / 259666원 위 종가, 동일 시간대 상대거래량 1.2 이상, 다음 거래일 지지 확인","risk_condition_ko":"242,500 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":584000.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":580292.2034390677,"relative_volume":5.294000152076697,"spread_bps":17.13796058269066,"day_high":588000.0,"day_low":566000.0,"execution_condition_ko":"575186원 위 종가와 518000주 이상 거래량 / 540193~537834원 지지 구간 유지","risk_condition_ko":"535,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":178200.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":178987.67069161715,"relative_volume":1.0028569510926175,"spread_bps":5.613247263541959,"day_high":180800.0,"day_low":177600.0,"execution_condition_ko":"정규장과 시세를 검증한 뒤 180,000원 상회 유지, 시간대별 상대거래량 1.2 이상 및 종가 거래량 221,889주 초과 확인 / 돌파 종가 이후 다음 실제 거래일 초반 30~60분에 180,000원 지지 또는 재돌파 확인","risk_condition_ko":"176,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"095340.KQ","display_name":"ISC","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":204500.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":203175.99188392257,"relative_volume":1.459836398352032,"spread_bps":24.479804161566705,"day_high":207000.0,"day_low":200000.0,"execution_condition_ko":"095340.KQ의 실제 정규장 개장 여부와 최신 시세·거래량·유효한 장중 거래량가중평균가격 확인 / 199,900원 유지와 204,417~205,101원 회복 및 상대거래량 1.2 이상 확인","risk_condition_ko":"199,900 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"180640.KS","display_name":"180640","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":134600.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":134110.35253025749,"relative_volume":1.2009193978000905,"spread_bps":14.858841010401187,"day_high":135900.0,"day_low":131300.0,"execution_condition_ko":"180640.KS의 정규장 여부와 실시간 가격·거래량·거래량가중평균가격 확인 / 135600원 종가 회복과 일거래량 71925주 초과, 다음 거래일 지지 확인","risk_condition_ko":"129,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"011070.KS","display_name":"LG이노텍","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":574000.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":584343.0605950654,"relative_volume":1.8245122674699132,"spread_bps":17.40644038294169,"day_high":608000.0,"day_low":573000.0,"execution_condition_ko":"검증된 정규장에서 624020원 회복, 동시간대 상대거래량 1.2 이상 및 유효한 당일 거래량가중평균가격 지지 / 정규장 종가 624020원 초과와 거래량 최소 253365주, 이어지는 실제 다음 거래일의 지지 또는 재돌파","risk_condition_ko":"583,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"128940.KS","display_name":"128940","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":490500.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":499949.6937064741,"relative_volume":4.931458293769649,"spread_bps":10.198878123406425,"day_high":526000.0,"day_low":488000.0,"execution_condition_ko":"위험 대응 조건: 516,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"516,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"017670.KS","display_name":"017670","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":85800.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":86101.58060759002,"relative_volume":1.0620606024510966,"spread_bps":11.648223645894001,"day_high":86700.0,"day_low":85700.0,"execution_condition_ko":"위험 대응 조건: 87,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"87,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000150.KS","display_name":"두산","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1350000.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":1370254.2542888767,"relative_volume":1.074588315267468,"spread_bps":7.404664938911514,"day_high":1408000.0,"day_low":1348000.0,"execution_condition_ko":"위험 대응 조건: 1,397,000 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"1,397,000 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010170.KQ","display_name":"010170","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":16950.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":17225.649925556794,"relative_volume":1.1259369962812242,"spread_bps":5.897965202005309,"day_high":17940.0,"day_low":16930.0,"execution_condition_ko":"위험 대응 조건: 18,880 이상 도달, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"18,880 이상 도달, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000810.KS","display_name":"000810","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":613000.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":616995.8448753463,"relative_volume":0.9756725494797148,"spread_bps":16.299918500407497,"day_high":623000.0,"day_low":611000.0,"execution_condition_ko":"위험 대응 조건: 617,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"617,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"047040.KS","display_name":"047040","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":16810.0,"market_data_asof":"2026-10-08T09:57:00+09:00","session_vwap":16861.321979829754,"relative_volume":0.8559376107893852,"spread_bps":5.950609937518595,"day_high":17220.0,"day_low":16710.0,"execution_condition_ko":"위험 대응 조건: 17,214 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"17,214 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-08T09:57:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:27:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"373220.KS","display_name":"LG에너지솔루션","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":414500.0,"market_data_asof":"2026-10-08T09:58:00.706180+09:00","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":418000.0,"day_low":397000.0,"execution_condition_ko":"한국거래소 일정과 373220.KS의 실시간 정규장 가격·거래량 확인 / 395000원 돌파 시 당일 거래량가중평균가격 유지와 당시 상대거래량 1.2배 이상 확인","risk_condition_ko":"378,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-08T09:58:00.706180+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-08T10:28:00.706180+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-08T10:45:05.320106+09:00",
  "as_of": "2026-10-08T09:57:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
