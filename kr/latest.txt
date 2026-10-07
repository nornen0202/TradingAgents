# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-07T08:50:57.002640+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261007T171515_github-actions-kr",
  "producer_finished_at": "2026-10-07T17:48:43.481040+09:00",
  "analysis_run_id": "20261007T171515_github-actions-kr",
  "analysis_completed_at": "2026-10-07T17:35:46.367279+09:00",
  "analysis_trade_date_oldest": "2026-10-06",
  "analysis_trade_date_latest": "2026-10-06",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-07T14:43:00+09:00",
  "market_data_latest_at": "2026-10-07T17:15:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-07T17:36:12.111019+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-07T17:36:12.111019+09:00",
    "run_started_at": "2026-10-07T17:15:15.283075+09:00",
    "run_finished_at": "2026-10-07T17:48:43.481040+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 10946520,
    "total_unrealized_pnl_krw": -3997716,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 11923172
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1723000,
      "market_value_krw": 3446000,
      "unrealized_pnl_krw": -1989000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 268500,
      "market_value_krw": 2685000,
      "unrealized_pnl_krw": -638851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 379000,
      "market_value_krw": 1895000,
      "unrealized_pnl_krw": -179643
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 205500,
      "market_value_krw": 822000,
      "unrealized_pnl_krw": -153000
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 628000,
      "market_value_krw": 628000,
      "unrealized_pnl_krw": -525000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 19540,
      "market_value_krw": 351720,
      "unrealized_pnl_krw": -216595
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 264500,
      "market_value_krw": 264500,
      "unrealized_pnl_krw": -109667
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 85200,
      "market_value_krw": 255600,
      "unrealized_pnl_krw": -44400
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 189000,
      "market_value_krw": 189000,
      "unrealized_pnl_krw": -93334
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 151300,
      "market_value_krw": 151300,
      "unrealized_pnl_krw": -21000
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 56200,
      "market_value_krw": 112400,
      "unrealized_pnl_krw": -5800
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 80500,
      "market_value_krw": 80500,
      "unrealized_pnl_krw": -32431
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
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":630000.0,"market_data_asof":"2026-10-07T15:05:00+09:00","session_vwap":654531.470439128,"relative_volume":1.8927162505829778,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"확인된 정규장에서 627,000원을 지키고 655,343원과 새로 계산한 당일 거래량가중평균가격을 5분봉 두 개 연속 회복하며 동시간대 상대거래량 1.2 이상 기록 / 확인된 종가의 693,000원 상회와 다음 거래일 690,000~693,000원 지지","risk_condition_ko":"655,343 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T15:05:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T15:35:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":207000.0,"market_data_asof":"2026-10-07T14:43:00+09:00","session_vwap":215740.32580557856,"relative_volume":2.1977549939544847,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"010120.KS의 새 체결 가능 가격과 갱신된 거래량가중평균가 확인 / 206,000원 지지 또는 검증된 종가 이탈","risk_condition_ko":"215,740 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T14:43:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T15:13:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":270000.0,"market_data_asof":"2026-10-07T14:44:00+09:00","session_vwap":273627.27941123885,"relative_volume":0.9016226376661112,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"현재 호가와 거래량가중평균가 재확인; 273627원은 14:44 기준치일 뿐임 / 상대거래량 1.2 이상을 수반한 279500원 돌파","risk_condition_ko":"268,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T14:44:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T15:14:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":378000.0,"market_data_asof":"2026-10-07T15:17:00+09:00","session_vwap":377429.8210648781,"relative_volume":1.5488320562201099,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 정규장 상태·호가·종가와 거래 가능 여부 확인 / 378,794원 회복과 같은 시간대 상대거래량 1.2배 이상 확인","risk_condition_ko":"363,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T15:17:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T15:47:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":85900.0,"market_data_asof":"2026-10-07T15:04:00+09:00","session_vwap":86884.9736770675,"relative_volume":1.0702999245690104,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 호가·실제 정규장·새 거래량가중평균가·상대 거래량 확인 / 86,900원 위 확정 종가와 88,000원·88,700원 순차 돌파","risk_condition_ko":"84,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T15:04:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T15:34:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":19550.0,"market_data_asof":"2026-10-07T14:43:00+09:00","session_vwap":19596.769435616283,"relative_volume":0.7255314281215005,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 시세와 정규 거래 여부를 확인하고 19600원 및 현재 거래량가중평균가격 회복 관찰 / 19770원 위 유지와 시간대별 거래 속도 보정 상대 거래량 1.2 이상 확인","risk_condition_ko":"19,440 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T14:43:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T15:13:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":189200.0,"market_data_asof":"2026-10-07T14:55:00+09:00","session_vwap":190013.04706623196,"relative_volume":0.6903894481857649,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 거래량가중평균가격과 190,300원 회복 여부 / 상대 거래량 1.2 이상을 동반한 191,400원 상향 유지, 확인된 종가와 다음 거래일 지속 여부","risk_condition_ko":"190,300 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T14:55:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T15:25:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":56000.0,"market_data_asof":"2026-10-07T15:05:00+09:00","session_vwap":55792.4116138846,"relative_volume":0.9660972892443458,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"083450.KQ의 실제 정규장 여부와 최신 거래 가능 가격 확인 / 56,900원 위 5분 종가, 시간 보정 상대거래량 1.2배 이상 및 실시간 거래량가중평균가격 상회","risk_condition_ko":"56,000 이상 도달, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T15:05:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T15:35:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":151100.0,"market_data_asof":"2026-10-07T15:18:00+09:00","session_vwap":151852.00802489682,"relative_volume":0.7760072635500587,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"실제 장 상태·최신 호가·2026-10-07 종가 확인 / 당일 거래량가중평균가격과 153,029원 회복·유지 및 비교 가능한 5분 거래량 1.2배 이상","risk_condition_ko":"156,200 이상 도달, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T15:18:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T15:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":65500.0,"market_data_asof":"2026-10-07T15:24:00+09:00","session_vwap":66893.67637365423,"relative_volume":0.8099711965964125,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"66,900원과 실시간 거래량가중평균가 회복·유지 및 동시간대 상대거래량 1.2배 이상 / 68,800원 회복, 70,000원 위의 확인된 종가 및 다음 실제 거래일의 지지","risk_condition_ko":"68,800 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T15:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T15:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":264000.0,"market_data_asof":"2026-10-07T15:04:00+09:00","session_vwap":269071.12348329753,"relative_volume":0.8191162799588434,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"정규장 확인 후 갱신된 거래량가중평균가격과 269071 위에서 5분봉 두 개 유지 및 상대거래량 1.2 이상 / 상대거래량 1.2 이상에서 확인된 275000 초과 종가와 다음 거래일 유지 또는 재돌파; 281500은 추가 저항","risk_condition_ko":"263,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T15:04:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T15:34:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":80600.0,"market_data_asof":"2026-10-07T14:54:00+09:00","session_vwap":81948.4590261178,"relative_volume":0.7872868863392466,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"원공시에서 재무제표 통화·단위·주식 기준과 주식예탁증서 전환비율 해당 여부 확인 / 계약 체결·정정 공시의 실제 조건과 현금 전환 확인","risk_condition_ko":"82,300 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T14:54:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T15:24:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1729000.0,"market_data_asof":"2026-10-07T14:44:00+09:00","session_vwap":1745700.5949798424,"relative_volume":0.7376965444719226,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"새 정규장 가격에서 당일 거래량가중평균가격 회복, 1,779,000원 상회 유지 및 상대거래량 1.2 이상 확인 / 1,790,900원과 1,793,971원 상회 종가 및 다음 확인된 거래일의 1,779,000원 유지","risk_condition_ko":"1,725,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T14:44:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T15:14:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":562000.0,"market_data_asof":"2026-10-07T15:35:00+09:00","session_vwap":566567.91229626,"relative_volume":0.9473643651824403,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"검증된 정규 거래일에 575,000원 회복·유지, 당일 거래량가중평균가격 상회, 동시간대 상대거래량 1.2배 이상 / 578,000원·592,000원·600,000원 저항과 비용 차감 후 보상·위험 재산정","risk_condition_ko":"575,000 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T15:35:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T16:05:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010950.KS","display_name":"S-Oil","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":169900.0,"market_data_asof":"2026-10-07T16:14:00+09:00","session_vwap":169809.55434831913,"relative_volume":0.9492752466861346,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"다음 실제 KRX 정규장과 최신 010950.KS 호가 확인 / 170800원 위 유지, 실시간 거래량가중평균가격 상회 및 상대 거래량 1.2배 이상 확인","risk_condition_ko":"167,800 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T16:14:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T16:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":138500.0,"market_data_asof":"2026-10-07T16:11:00+09:00","session_vwap":139067.4494478405,"relative_volume":1.1580287163616139,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"검증된 정규장에서 139067원 기준을 회복하고 141402원과 142000원을 넘으며 상대 거래량 1.3 이상과 실시간 거래량가중평균가격 상회를 확인함 / 090430.KS의 검증된 정규장 종가가 137442원 또는 134000원 아래로 내려감","risk_condition_ko":"134,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T16:11:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T16:41:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"128940.KS","display_name":"128940","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":534000.0,"market_data_asof":"2026-10-07T15:50:00+09:00","session_vwap":528251.6315314928,"relative_volume":1.3407991679611306,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"별도 확인된 정규장에서 10:30 이후 551000원 위 유지, 실시간 거래량가중평균가 지지, 시간 보정 상대거래량 1.2 이상 및 안정적 스프레드 / 검증된 정규장 종가 551000원 상회와 일일 거래량 104226주 초과","risk_condition_ko":"516,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T15:50:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T16:20:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"105560.KS","display_name":"105560","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":168300.0,"market_data_asof":"2026-10-07T16:14:00+09:00","session_vwap":168406.47120655703,"relative_volume":0.5926439277265316,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"다음 정규장 운영 여부와 105560.KS의 시세·거래량 신선도 확인 / 170,000원 회복 뒤 170,700원 상회, 시간대 보정 상대거래량 1.2배 이상 및 해당 장의 거래량가중평균가격 상회 확인","risk_condition_ko":"165,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T16:14:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T16:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"017670.KS","display_name":"017670","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":87400.0,"market_data_asof":"2026-10-07T15:29:00+09:00","session_vwap":87583.17207472074,"relative_volume":0.3292264337858201,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"실제 정규장과 최신 호가에서 88,300원 상회·실시간 거래량가중평균가격 상회·동시간대 상대거래량 1.2배 이상 동시 확인 / 89,400원 종가 회복과 재산출한 50일선 약 90,753원 위 종가 및 다음 실제 거래일 유지","risk_condition_ko":"87,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T15:29:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T15:59:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":179600.0,"market_data_asof":"2026-10-07T15:50:00+09:00","session_vwap":178811.40131136516,"relative_volume":0.805040117787421,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-10-07 공식 종가와 실제 정규장 여부·시세 시각 확인 / 향후 정규장에 179800원 위 종가, 일 거래량 221654주 초과 및 당일 거래량가중평균가격 상회 확인","risk_condition_ko":"175,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T15:50:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T16:20:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":159000.0,"market_data_asof":"2026-10-07T16:25:00+09:00","session_vwap":159471.6552243586,"relative_volume":0.9682168574983104,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-10-07 최종 종가와 159,000원 자료의 차이, 향후 정규장 일정 및 호가 신선도 확인 / 검증된 정규장 10:30 이후 162,700원 회복·유지, 실시간 거래량가중평균가격 상회 및 상대거래량 1.2배 이상","risk_condition_ko":"153,900 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T16:25:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T16:55:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"009150.KS","display_name":"삼성전기","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1604000.0,"market_data_asof":"2026-10-07T15:38:00+09:00","session_vwap":1639652.4645549057,"relative_volume":0.9226684999639986,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"다음 실제 정규장과 새 시세를 확인하고 2026-10-07 장후 표시 및 가격 기준일 차이를 재점검 / 새로 계산한 당일 거래량가중평균가격 회복; 1,639,652원은 토론상 2026-10-07 참고치일 뿐","risk_condition_ko":"1,601,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T15:38:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T16:08:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"373220.KS","display_name":"LG에너지솔루션","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":390500.0,"market_data_asof":"2026-10-07T15:26:00+09:00","session_vwap":390218.1724351683,"relative_volume":1.1844673724209782,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"새 정규장 호가가 395000원과 당시 거래량가중평균가격 위에서 유지되고 상대거래량 1.2 이상 및 호가 균형 개선 / 395000원 위 확인된 종가와 다음 거래일 지지 또는 재돌파","risk_condition_ko":"386,965 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T15:26:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T15:56:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000810.KS","display_name":"000810","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":627000.0,"market_data_asof":"2026-10-07T17:15:00+09:00","session_vwap":628309.0506875501,"relative_volume":0.773727982156116,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"확인된 향후 정규장에서 신선한 시세로 642,000~645,000원 회복·유지 확인 / 652,000원 위 정규장 종가와 일 거래량 83,838주 초과 확인","risk_condition_ko":"617,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T17:15:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T17:45:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"067290.KQ","display_name":"067290","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":2870.0,"market_data_asof":"2026-10-07T15:27:00+09:00","session_vwap":3065.1711560008216,"relative_volume":0.48539506189679876,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"신선한 정규장 시세에서 2,855원 지지와 2,920원 회복 확인 / 갱신된 거래량가중평균가와 과거 참고선 3,065원 회복 및 동일 시각대 상대거래량 1.2 이상","risk_condition_ko":"2,920 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T15:57:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000150.KS","display_name":"두산","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1402000.0,"market_data_asof":"2026-10-07T16:06:00+09:00","session_vwap":1425466.149923164,"relative_volume":0.6247062639944931,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"새로 확인된 정규장에서 1,471,000원 회복과 당일 거래량가중평균가격 지지 및 시간 조정 상대 거래량 1.2 이상 / 상대 거래량 1.2 이상을 동반한 1,491,000원 초과 종가와 다음 확인된 거래일의 지지 또는 재돌파","risk_condition_ko":"1,397,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T16:06:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T16:36:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"009830.KS","display_name":"009830","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":36200.0,"market_data_asof":"2026-10-07T16:03:00+09:00","session_vwap":36448.456010267626,"relative_volume":0.5935488955791146,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"009830.KS의 확인된 정규 거래일 37,500원 돌파·유지, 당일 거래량가중평균가격 상회 및 상대거래량 1.2배 이상 / 36,224원 장기 이동평균선과 36,000원·35,100원 지지 확인","risk_condition_ko":"36,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T16:03:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T16:33:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"088350.KS","display_name":"088350","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":5400.0,"market_data_asof":"2026-10-07T16:01:00+09:00","session_vwap":5331.521173840141,"relative_volume":0.5222476970258614,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"다음으로 확인된 정규장에서 5,400~5,420원 유지, 실시간 거래량가중평균가격 상회 및 시간 보정 상대거래량 1.2 이상 / 2026-10-06 기준 10일 이동평균 5,535원을 갱신한 뒤 그 위 정규장 종가 확인","risk_condition_ko":"5,220 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T16:01:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T16:31:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"180640.KS","display_name":"180640","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":133900.0,"market_data_asof":"2026-10-07T16:02:00+09:00","session_vwap":133445.11489502396,"relative_volume":0.3967436717121565,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"180640.KS가 135962원과 137605원을 회복하고 거래량 개선과 함께 139325원을 돌파하는지 확인 / 검증된 정규장 종가가 거래량 76233주를 넘기며 143800원 위에서 마감하고 다음 거래일에도 유지되는지 확인","risk_condition_ko":"129,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T16:02:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T16:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"047040.KS","display_name":"047040","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":17340.0,"market_data_asof":"2026-10-07T15:39:00+09:00","session_vwap":17637.94027010167,"relative_volume":0.43249756153179536,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"검증된 정규장에서 17,630~17,640원 회복 후 당일 거래량가중평균가 위 유지 및 상대 거래량 1.2 이상 / 상대 거래량 1.2 이상을 동반한 18,030원 초과 종가와 다음 검증 거래일의 17,976.08~18,030원 구간 유지","risk_condition_ko":"17,330 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-07T15:39:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-07T16:09:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-07T13:40:56.660073+09:00",
  "as_of": "2026-10-06T09:57:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
