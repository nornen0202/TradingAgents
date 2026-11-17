# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-17T03:46:38.793263+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261117T103257_local-scheduler-kr-overlay_only",
  "producer_finished_at": "2026-11-17T11:47:23.651319+09:00",
  "analysis_run_id": "20261117T044757_local-scheduler-kr-full",
  "analysis_completed_at": "2026-11-17T07:45:36.333520+09:00",
  "analysis_trade_date_oldest": "2026-11-13",
  "analysis_trade_date_latest": "2026-11-13",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-17T11:45:00+09:00",
  "market_data_latest_at": "2026-11-17T11:45:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-17T11:47:19.096677+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-17T11:47:19.096677+09:00",
    "run_started_at": "2026-11-17T10:32:57.969920+09:00",
    "run_finished_at": "2026-11-17T11:47:23.651319+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 7156160,
    "total_unrealized_pnl_krw": -7788076,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 8132812
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1133000,
      "market_value_krw": 2266000,
      "unrealized_pnl_krw": -3169000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 192400,
      "market_value_krw": 1924000,
      "unrealized_pnl_krw": -1399851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 221000,
      "market_value_krw": 1105000,
      "unrealized_pnl_krw": -969643
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 114700,
      "market_value_krw": 458800,
      "unrealized_pnl_krw": -516200
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 381500,
      "market_value_krw": 381500,
      "unrealized_pnl_krw": -771500
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 16220,
      "market_value_krw": 291960,
      "unrealized_pnl_krw": -276355
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 170700,
      "market_value_krw": 170700,
      "unrealized_pnl_krw": -111634
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 167500,
      "market_value_krw": 167500,
      "unrealized_pnl_krw": -206667
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 48150,
      "market_value_krw": 144450,
      "unrealized_pnl_krw": -155550
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 83300,
      "market_value_krw": 83300,
      "unrealized_pnl_krw": -89000
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 41350,
      "market_value_krw": 82700,
      "unrealized_pnl_krw": -35500
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 43300,
      "market_value_krw": 43300,
      "unrealized_pnl_krw": -69631
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 36950,
      "market_value_krw": 36950,
      "unrealized_pnl_krw": -17550
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":170800.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":171242.21793334122,"relative_volume":0.6332775514126338,"spread_bps":5.8530875036581795,"day_high":172900.0,"day_low":169900.0,"execution_condition_ko":"위험 대응 조건: 168,600 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"168,600 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":16240.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":16198.211872398966,"relative_volume":0.5561338015380025,"spread_bps":6.155740227762388,"day_high":16400.0,"day_low":16000.0,"execution_condition_ko":"11월 16일 이후 누락 일봉과 최신 거래상태를 확보해 이미 지지 실패나 손절 조건이 발생했는지 먼저 확인한다. 이미 발생했다면 기존 조건부 계획으로 재진입하지 않는다. / 3분기 원공시의 표시 기준을 검증하고 마진, 현금흐름 구성, 차입 만기, 투자자산 환금성 및 헤지 관련 현금 부담을 점검한다. 제공업체 유동비율 약 0.878과 운전자본 기여 약 43.5%는 검증 사유이지 위기 또는 안전의 확정 증거가 아니다.","risk_condition_ko":"16,120 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":382500.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":379688.4887144259,"relative_volume":0.9984729185782387,"spread_bps":13.080444735120995,"day_high":387500.0,"day_low":369000.0,"execution_condition_ko":"267260.KS의 2026-11-13 이후 신선한 정규장 자료를 확보하고 416100원 이상 종가 회복과 다음 실제 거래일 413500~416100원 종가 재지지를 순서대로 확인한다. / 최소 재무검증과 가격 확인 이후 413500~415500원에서만 비용 후 손익비와 계좌 한도를 심사한다. 확인 전 하락 접촉은 매수 신호가 아니다.","risk_condition_ko":"413,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":167600.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":169456.39444302808,"relative_volume":0.8956562788395246,"spread_bps":5.961251862891207,"day_high":173600.0,"day_low":164500.0,"execution_condition_ko":"166900~168300원 하단 관찰대의 최신 정규장 지지 여부; 일봉 지지와 야간 저가를 구분 / 173800원 회복은 초기 관찰 신호이며 현재 거래량가중평균가격 회복을 뜻하지 않음","risk_condition_ko":"166,900 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":41250.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":41488.33028180977,"relative_volume":1.091503392589757,"spread_bps":36.38568829593693,"day_high":43050.0,"day_low":40200.0,"execution_condition_ko":"40500~40700원 시험 후 종가 40700원 이상 회복과 다음 실제 거래일 종가 40700원 이상 유지: 가격 측 재심사 조건이다. 공시 검증과 비용후 투자 매력 개선 없이는 매수하지 않는다. / 42925~43500원 회복과 거래량 개선: 추세 재평가. 43500원 진입·40500원 방어·45675원 저항의 비용 전 손익비 약 0.73배로는 추격하지 않는다.","risk_condition_ko":"40,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1136000.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":1115153.4573206175,"relative_volume":1.0248645102989449,"spread_bps":8.798944126704797,"day_high":1138000.0,"day_low":1096000.0,"execution_condition_ko":"판단 시각은 2026-11-17T05:05:59.389182+09:00이다. 최신 정상거래 일봉·거래 가능 상태·휴장 및 단축거래 여부는 제공되지 않았으므로 실행 전에 확인한다. / 2026-11-16 20:00 한국시간의 1118000원 지연 호가는 현재가나 공식 정상거래 종가가 아니므로 지지선 이탈 또는 매수 조건 충족으로 취급하지 않는다.","risk_condition_ko":"1,190,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":192900.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":192510.0905081865,"relative_volume":1.1556954216963427,"spread_bps":5.182689816014512,"day_high":195900.0,"day_low":190400.0,"execution_condition_ko":"005930.KS의 거래소 일정·정규장 여부·최신 일별 가격을 확인한다. 판단 시각 2026-11-17T05:03:46.592046+09:00만으로 개장 여부, 호가 신선도나 조건 충족을 인정하지 않는다. / 208,000 초과 종가는 205,000–208,000 구간 회복으로 관찰하되 단독 매수 신호로 사용하지 않는다.","risk_condition_ko":"196,300 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":222000.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":226148.9773230026,"relative_volume":1.2200087340543881,"spread_bps":22.49718785151856,"day_high":237000.0,"day_low":220500.0,"execution_condition_ko":"278470.KS의 누락된 2026-11-16 일간 자료와 이후 확인 가능한 정규장 자료를 확보하여 지지 유지·이탈 여부를 판정한다. / 231000~233000원 지지 관찰 구간과 241500~243500원 초기 회복 구간을 추적하되 어느 쪽도 단독 매수 조건으로 삼지 않는다.","risk_condition_ko":"231,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":114800.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":114083.88199886012,"relative_volume":0.989781459916597,"spread_bps":17.40644038294169,"day_high":116300.0,"day_low":110600.0,"execution_condition_ko":"2026-11-16 공식 일봉으로 보도 가격 118,100원과 118,600원의 불일치를 해소한다. 모든 제시 가격선은 2026-11-13 기준이며 최신 가격과 분할·수정주가 기준이 같은지 확인한 후 적용한다. 확인 중에도 기존 계좌 손절은 유지한다. / 새 종가 124,800원 이상, 이어 131,300원 초과와 다음 실제 거래일 128,700~131,300원 지지 여부를 관찰한다. 가격 신호만으로 자동 매수하지 않는다.","risk_condition_ko":"115,200 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":83500.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":83869.39385720974,"relative_volume":1.0566659405413041,"spread_bps":11.968880909634949,"day_high":86600.0,"day_low":80000.0,"execution_condition_ko":"353200.KS의 78,200~80,100원 방어를 새 일봉으로 확인한다. 하단 미만 종가는 추가 감축 신호이지 저가 매수 신호가 아니다. / 90,000~90,900원은 이탈한 지지대다. 90,900원 위 종가와 다음 확인된 정규거래일 재지지는 미실행 감축 재검토의 첫 조건이다.","risk_condition_ko":"90,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":48150.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":48205.84469858914,"relative_volume":0.9108147583252449,"spread_bps":10.378827192527243,"day_high":49100.0,"day_low":47050.0,"execution_condition_ko":"최신 확정 일봉으로 49,500~50,200 유지·회복과 약 52,650 회복을 확인한다. 첫 회복만으로 매수하지 않는다. / 54,200~54,700 지지 전환 시 가까운 저항 55,600~57,000을 먼저 반영해 실제 진입가·손절가·비용으로 손익비를 재계산한다. 54,700 대비 상승 여유 약 1.6~4.2%와 과거 평균진폭의 비교 자체는 손익비 계산이 아니다.","risk_condition_ko":"48,300 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":43300.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":43349.973180698405,"relative_volume":0.896770064097591,"spread_bps":11.54068090017311,"day_high":43800.0,"day_low":42800.0,"execution_condition_ko":"최신 정규장 종가로 43700원 추가 축소와 42700원 청산 조건을 확인한다. 현재 충족 여부는 미확인이다. / 46550–47350원 회복·유지, 48000–48850원 저항 통과, 갱신된 단기 추세선 회복과 다음 실제 거래일 지지를 관찰한다. 단독 매수 신호가 아니다.","risk_condition_ko":"43,700 이하 하락, 종가 확인 후 (위험 축소에는 거래량 증가 불필요) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":37000.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":37083.18455578694,"relative_volume":0.8596632032404047,"spread_bps":13.522650439486139,"day_high":37850.0,"day_low":35900.0,"execution_condition_ko":"2026-11-16 거래자료의 존재와 최신 완료 거래일 공식 일봉을 확인하여 39,800원 이탈 여부부터 판정한다. 지연 시세나 기사 속 하락률로 공식 종가를 역산하지 않는다. / 종가 40,763원 회복, 이후 42,600원 상회와 다음 확인된 거래일의 42,350–42,600원 지지를 관찰한다. 모두 재검토 신호이며 자동 매수조건은 아니다.","risk_condition_ko":"39,800 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"028050.KS","display_name":"028050","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":69600.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":69034.55801686688,"relative_volume":0.7113970461968596,"spread_bps":14.378145219266715,"day_high":70300.0,"day_low":66600.0,"execution_condition_ko":"028050.KS의 최신 완성 일봉에서 기존 손절, 66000원 지지 및 돌파 실패 여부를 우선 확인한다. 전체 비중 5% 또는 계획손실 0.5% 한도 초과가 확인되면 초과 위험부터 축소한다. / 028050.KS의 67700원 재시험·종가 지지·다음 실제 거래일 유지와 67700~68800원 주문 범위, 최소 공시 점검 및 계좌 여력이 모두 확인되면 최초 단계 진입을 재검토한다.","risk_condition_ko":"66,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":214000.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":214399.0196013684,"relative_volume":0.5800689881473066,"spread_bps":23.33722287047841,"day_high":216500.0,"day_low":211000.0,"execution_condition_ko":"205000~207000원 내 반등 종가와 다음 실제 거래일의 205000원 이상 종가 지지. 단순 가격 도달은 매수 신호가 아니다. / 209000~210000원 관찰 지지와 202000~204000원 약화 구간 접근 여부.","risk_condition_ko":"202,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"030530.KQ","display_name":"030530","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":32100.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":31075.658326961628,"relative_volume":0.8636885999654708,"spread_bps":15.564202334630352,"day_high":32150.0,"day_low":29800.0,"execution_condition_ko":"29500~30000원 종가 안정과 다음 실제 거래일의 29500원 이상 종가를 확인한다. 이후 실제 매수가격도 해당 구간 안이어야 한다. / 30400~31000원은 가까운 지지 관찰대이며 단순 접촉은 매수 신호가 아니다.","risk_condition_ko":"29,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"036460.KS","display_name":"036460","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":38300.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":38163.887363266054,"relative_volume":0.6349875149648179,"spread_bps":13.04631441617743,"day_high":38400.0,"day_low":37850.0,"execution_condition_ko":"036460.KS 2026-11-13 이후 최신 완료 일봉과 2026-11-16 정정본 변경 내용을 먼저 확인한다. / 036460.KS 37100-37400원 눌림 뒤 종가 37400원 이상 회복, 다음 확인된 정규거래일 종가 37100원 이상 지지를 확인한다.","risk_condition_ko":"36,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"002990.KS","display_name":"002990","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":10150.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":10561.495157664354,"relative_volume":2.4250175305572523,"spread_bps":9.857072449482505,"day_high":11300.0,"day_low":9860.0,"execution_condition_ko":"판단시각 2026-11-17T06:12:57.326553+09:00은 유효기한 이전이다. 실제 거래일·정규장·가격 신선도·조건 충족을 입증하지는 않으므로 각각 확인한다. / 10,210~10,430원 시험, 종가 10,430원 이상 회복, 다음 실제 거래일 종가 10,210원 이상 유지 이후 구간 내 기회를 관찰한다. 재방문이 새로운 하락으로 변했다면 진입하지 않는다.","risk_condition_ko":"9,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"105560.KS","display_name":"105560","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":158700.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":158176.82814076895,"relative_volume":0.806021203621842,"spread_bps":6.3031831074692715,"day_high":161700.0,"day_low":156300.0,"execution_condition_ko":"거래소 휴장·조기폐장과 정규장 여부를 확인하고 최신 완료 일봉 및 이동평균을 갱신한다. 보도된 2026-11-16 상대강도도 독립 확인한다. / 식별된 공시 5건, 특히 2026-11-16 분기보고서와 2026-11-11 제재·정정 관련 원문을 검토한다. 중요한 손익·자본 영향이 해소되지 않으면 신규 집행을 계속 보류한다.","risk_condition_ko":"151,900 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"018260.KS","display_name":"삼성SDS","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":229500.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":226003.94842509145,"relative_volume":0.5281161222919123,"spread_bps":21.810250817884405,"day_high":229500.0,"day_low":217500.0,"execution_condition_ko":"누락 일봉과 원문 시각을 먼저 확인해 이미 발생한 지지 이탈이나 손절 조건이 있는지 점검한다. / 222000–223500원 시험 후 223500원 이상 종가와 다음 검증된 거래일 지지를 관찰한다. 단순 접촉이나 높은 시초가 추격은 매수 근거가 아니다.","risk_condition_ko":"223,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034730.KS","display_name":"034730","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":477500.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":467584.827974679,"relative_volume":0.5356343210144284,"spread_bps":10.465724751439037,"day_high":478000.0,"day_low":454000.0,"execution_condition_ko":"034730.KS의 최신 정규장 일봉·가격 기준 시각·실제 거래일을 먼저 확인한다. 상충하는 2026-11-16 야간 표시 가격은 진입·손절 판정에서 제외한다. / 최초 지지 시험과 500,000원 이상 종가, 다음 실제 거래일 재시험과 500,000원 이상 종가, 원문 지급능력 검증을 순차 확인한다. 두 번째 확인 종가와 공시 검증 이후 주문 가능한 정규장부터 활성화할 수 있으나 가격 구간을 벗어나면 추격하지 않는다.","risk_condition_ko":"490,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"024840.KQ","display_name":"024840","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":4210.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":4309.138776938632,"relative_volume":3.536781240032885,"spread_bps":11.869436201780415,"day_high":4500.0,"day_low":4090.0,"execution_condition_ko":"자료 범위는 제공된 계획과 토론에 한정된다. 누락된 2026-11-16 및 이후 완료 일봉부터 확보하고 4150 미만 종가가 있었는지 확인한다. 지연된 야간 호가와 불일치하는 분봉 가격은 현재 지지나 실행 가격의 증거로 쓰지 않는다. / 발행사의 재무제표 통화·표시 단위·분기와 누적 기간·연결 범위·기본 및 희석 주식 수 기준, 예탁증서 해당 여부와 원주 교환비율을 원문에서 확인한다. 거래 통화가 원화라는 이유로 재무제표 통화나 주식 기준을 가정하지 않는다. 확인 전 주당이익 비교·연율화·가치평가 목표 산출은 보류한다.","risk_condition_ko":"4,150 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"180640.KS","display_name":"180640","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":218000.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":211555.06234077914,"relative_volume":0.5818176605447195,"spread_bps":22.962112514351322,"day_high":219000.0,"day_low":204500.0,"execution_condition_ko":"197600~198700원 지지 유지 여부를 관찰한다. 접촉만으로 매수하지 않는다. / 191000~193000원 시험, 종가 회복, 다음 확인된 정규 거래일 재지지의 순서와 선행 검증을 모두 충족하면 소규모 진입을 검토한다.","risk_condition_ko":"191,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"086790.KS","display_name":"086790","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":126500.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":125384.65714955327,"relative_volume":0.9405026791717586,"spread_bps":7.9020150138285254,"day_high":127000.0,"day_low":123900.0,"execution_condition_ko":"누락된 완료 일봉과 최신 공시를 우선 확인해 매도 조건의 선행 발생 여부를 점검한다. / 최소 재무검증 통과 후 눌림·종가 121889 회복·다음 실제 거래일 지지·121900~122000 체결 가능 조건이 모두 성립하면 제한된 최초 편입을 검토한다.","risk_condition_ko":"121,889 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003490.KS","display_name":"003490","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":32100.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":31813.322234190386,"relative_volume":0.9484925503510662,"spread_bps":15.58846453624318,"day_high":32150.0,"day_low":31500.0,"execution_condition_ko":"누락된 2026-11-16 및 최신 완료 정규장 일봉을 확보해 지지·저항·거래량과 기존 매도 조건 충족 여부를 우선 확인한다. 오래된 자료만으로 지지가 현재도 유지된다고 단정하지 않는다. / 거래통화는 원화이나 재무제표의 보고통화·금액단위·기간·연결범위·주당 기준·예탁증서 적용 여부와 필요한 환산비율은 원문 미검증이다. 검증 전 재무 금액·주당이익 비교나 예상 주가수익비율 8.72배를 이용한 저평가 판단을 하지 않는다.","risk_condition_ko":"30,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"064400.KS","display_name":"LG CNS","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":78000.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":76578.67653751631,"relative_volume":0.79818072531851,"spread_bps":12.828736369467606,"day_high":78100.0,"day_low":74700.0,"execution_condition_ko":"064400.KS의 최신 일봉 기준시각, 실제 거래일 달력과 정규장 여부를 확인한다. 11월 16일 야간 지연·불일치 시세는 진입 확인에 사용하지 않는다. / 2026-11-17부터 새 정규장 일봉에서 76500원 부근 눌림과 76500~77000원 종가 회복을 확인하고 다음 실제 거래일도 76500원 이상에서 마감해야 한다. 이후 실제 체결가 역시 76500~77000원이어야 한다.","risk_condition_ko":"74,500 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"207940.KS","display_name":"207940","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1436000.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":1424955.5919784035,"relative_volume":0.8624741373573838,"spread_bps":6.961364427427776,"day_high":1445000.0,"day_low":1403000.0,"execution_condition_ko":"최신 일봉과 기업행동 조정 기준을 갱신하여 1390000~1406000원 지지 유지 여부를 먼저 점검한다. 방어 조건이 확인되면 조건부 매수보다 위험 축소를 우선한다. / 사건·최소 재무검증, 1457000원 이상 종가 회복, 다음 실제 거래일의 1449000~1457000원 재시험 및 1449000원 이상 종가 지지를 모두 확인한다. 확인 이후 같은 구간의 신선한 실행 가격이 있어야 소규모 진입을 검토한다.","risk_condition_ko":"1,390,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"128940.KS","display_name":"128940","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":457500.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":457864.0052166353,"relative_volume":0.8460742316420824,"spread_bps":10.934937124111535,"day_high":464000.0,"day_low":446000.0,"execution_condition_ko":"최신 완료 정규장 일봉·거래량·기준시각과 거래일 달력을 확인한다. 2026-11-13 이후 지지 이탈이 먼저 발생했는지도 점검하며, 발생했다면 현재 진입 계획을 자동 복구하지 않는다. / 핵심 임상·경제적 권리 자료와 최신 원공시를 검증한다. 기사상 이익 감소와 제공업체 개선 수치를 상쇄하지 말고 기간·단위·분류 차이를 확인한다.","risk_condition_ko":"452,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":181600.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":181468.5879484332,"relative_volume":0.634281433021853,"spread_bps":5.50812448361333,"day_high":184000.0,"day_low":179700.0,"execution_condition_ko":"033780.KS의 누락된 2026-11-16 및 이후 최신 완료 일봉을 확보해 이미 발생한 매도 조건부터 확인하고 이동평균·지지·저항을 갱신한다. / 173100~173200원에서 저점 갱신 중단, 173200원 위 종가 회복과 다음 실제 거래일 재지지를 관찰한다. 이것만으로 매수 승인이 부활하지 않는다.","risk_condition_ko":"170,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"036930.KQ","display_name":"주성엔지니어링","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":152100.0,"market_data_asof":"2026-11-17T11:45:00+09:00","session_vwap":153588.62121681005,"relative_volume":1.317513001334703,"spread_bps":6.576783952647156,"day_high":158000.0,"day_low":149600.0,"execution_condition_ko":"164,300~166,400원 구간 상단 위 정규장 종가와 다음 실제 거래일 재시험 지지를 확인한다. 현재 가격이 구간 아래라면 회복할 저항으로 취급한다. / 184,900원 초과 정규장 종가와 다음 실제 거래일 재시험 지지를 확인한다. 최근 일별 거래량 대비 참여 개선을 참고하되 고정 거래량 배수는 요구하지 않는다.","risk_condition_ko":"164,300 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-17T11:45:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-17T11:48:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-17T10:51:45.749703+09:00",
  "as_of": "2026-11-16T20:00:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
