# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-22T16:56:23.305807+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261022T165722_local-thesis-refresh-kr-post-repair-427",
  "producer_finished_at": "2026-10-22T17:44:07.740891+09:00",
  "analysis_run_id": "20261022T050013_local-scheduler-kr-full",
  "analysis_completed_at": "2026-10-22T07:34:14.045585+09:00",
  "analysis_trade_date_oldest": "2026-10-21",
  "analysis_trade_date_latest": "2026-10-21",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-22T17:03:00+09:00",
  "market_data_latest_at": "2026-10-22T17:25:00+09:00",
  "market_data_status": "MISSING"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-22T15:30:15.048843+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "PIPELINE_DISABLED",
    "account_as_of": null,
    "run_started_at": "2026-10-22T16:57:22.109266+09:00",
    "run_finished_at": "2026-10-22T17:44:07.740891+09:00",
    "selected_for_public_account": false
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 8374860,
    "total_unrealized_pnl_krw": -6569376,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 9351512
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
      "current_price_krw": 214500,
      "market_value_krw": 2145000,
      "unrealized_pnl_krw": -1178851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 291000,
      "market_value_krw": 1455000,
      "unrealized_pnl_krw": -619643
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 161400,
      "market_value_krw": 645600,
      "unrealized_pnl_krw": -329400
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 490000,
      "market_value_krw": 490000,
      "unrealized_pnl_krw": -663000
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
      "current_price_krw": 64200,
      "market_value_krw": 192600,
      "unrealized_pnl_krw": -107400
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 191200,
      "market_value_krw": 191200,
      "unrealized_pnl_krw": -182967
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 176400,
      "market_value_krw": 176400,
      "unrealized_pnl_krw": -105934
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 127500,
      "market_value_krw": 127500,
      "unrealized_pnl_krw": -44800
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 41900,
      "market_value_krw": 83800,
      "unrealized_pnl_krw": -34400
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 61600,
      "market_value_krw": 61600,
      "unrealized_pnl_krw": -51331
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 48400,
      "market_value_krw": 48400,
      "unrealized_pnl_krw": -6100
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"1,254,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"217,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"154,200 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"17,170 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":61100.0,"market_data_asof":"2026-10-22T17:03:00+09:00","session_vwap":62277.734244771316,"relative_volume":0.5969700109666,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"61,050 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T17:03:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T17:06:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"177,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"197,400 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":63400.0,"market_data_asof":"2026-10-22T17:25:00+09:00","session_vwap":65381.351410813484,"relative_volume":0.5284648738156951,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"62,800 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T17:25:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T17:28:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"43,050 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"485,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"331,500 이상 도달, 장중 확인 시 (매도에는 상대거래량 하한을 적용하지 않는다.) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"127,000 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"51,881 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"000100.KS","display_name":"000100","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"88,500 이상 도달, 2개 봉 확인 후 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"003230.KS","display_name":"003230","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"1,216,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"526,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"010950.KS","display_name":"S-Oil","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"151,135 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"011200.KS","display_name":"011200","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"22,850 이하 하락, 종가 확인 후 (방어적 매도에는 거래량 확인을 필수로 요구하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"014950.KQ","display_name":"014950","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"7,977 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"018260.KS","display_name":"삼성SDS","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"194,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"018880.KS","display_name":"018880","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"3,775 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"189,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"064400.KS","display_name":"LG CNS","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"71,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"195,100 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"079650.KQ","display_name":"079650","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"7,320 이하 하락, 2개 봉 확인 후 (실제 거래가 있는 연속 두 개의 5분봉 종가가 7320 미만이고 회복하지 못할 때) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"134,600 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"160,900 이상 도달, 2개 봉 확인 후 리스크 축소 · 추가 조건 확인 필요: 제공된 분석의 159,600–160,900원 저항 구간에서 거부가 확인되면 초기 축소의 미집행분에 활용한다. 필수 매도 가격이나 이익 실현 목표가 아니며, 해당 가격을 기다리느라 축소를 미루지 않는다.","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"131290.KQ","display_name":"티에스이","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"258,000 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"373220.KS","display_name":"LG에너지솔루션","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"402,500 이하 하락, 종가 확인 후 (확정 종가 하회와 일봉 거래량 증가를 함께 확인) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"396300.KQ","display_name":"396300","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"11,250 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-22T14:48:57.208041+09:00",
  "as_of": "2026-10-22T14:47:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
