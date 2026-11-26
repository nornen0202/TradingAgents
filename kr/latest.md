# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-26T01:28:38.771624+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261126T093840_local-freshness-kr-overlay",
  "producer_finished_at": "2026-11-26T09:44:05.389796+09:00",
  "analysis_run_id": "20261126T061440_local-scheduler-kr-full",
  "analysis_completed_at": "2026-11-26T08:50:27.837023+09:00",
  "analysis_trade_date_oldest": "2026-11-25",
  "analysis_trade_date_latest": "2026-11-25",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-26T09:42:00+09:00",
  "market_data_latest_at": "2026-11-26T09:43:00+09:00",
  "market_data_status": "MISSING"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-25T15:29:52.735143+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-25T15:29:52.735143+09:00",
    "run_started_at": "2026-11-25T15:29:14.298955+09:00",
    "run_finished_at": "2026-11-25T15:29:57.413592+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 7006000,
    "total_unrealized_pnl_krw": -7938236,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 7982652
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1033000,
      "market_value_krw": 2066000,
      "unrealized_pnl_krw": -3369000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 171100,
      "market_value_krw": 1711000,
      "unrealized_pnl_krw": -1612851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 292000,
      "market_value_krw": 1460000,
      "unrealized_pnl_krw": -614643
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
      "current_price_krw": 382500,
      "market_value_krw": 382500,
      "unrealized_pnl_krw": -770500
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 14100,
      "market_value_krw": 253800,
      "unrealized_pnl_krw": -314515
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 158900,
      "market_value_krw": 158900,
      "unrealized_pnl_krw": -123434
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 147300,
      "market_value_krw": 147300,
      "unrealized_pnl_krw": -226867
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 46150,
      "market_value_krw": 138450,
      "unrealized_pnl_krw": -161550
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 41100,
      "market_value_krw": 82200,
      "unrealized_pnl_krw": -36000
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 68100,
      "market_value_krw": 68100,
      "unrealized_pnl_krw": -104200
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 40000,
      "market_value_krw": 40000,
      "unrealized_pnl_krw": -72931
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 38950,
      "market_value_krw": 38950,
      "unrealized_pnl_krw": -15550
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1079000.0,"market_data_asof":"2026-11-26T09:42:00+09:00","market_data_clock_status":null,"session_vwap":1068000.7245382413,"relative_volume":2.39424065770703,"spread_bps":9.263547938860583,"day_high":1094000.0,"day_low":1041000.0,"execution_condition_ko":"위험 대응 조건: 1,027,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"1,027,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-26T09:42:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":14040.0,"market_data_asof":"2026-11-26T09:42:00+09:00","market_data_clock_status":null,"session_vwap":14214.312228041505,"relative_volume":1.494870043087132,"spread_bps":7.125044531528322,"day_high":14410.0,"day_low":14010.0,"execution_condition_ko":"위험 대응 조건: 13,530 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"13,530 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-26T09:42:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":294500.0,"market_data_asof":"2026-11-26T09:42:00+09:00","market_data_clock_status":null,"session_vwap":301051.449386256,"relative_volume":2.744513421940495,"spread_bps":16.963528413910094,"day_high":309500.0,"day_low":292500.0,"execution_condition_ko":"270,500원 시험 당일 종가 회복과 다음 실제 정규장의 270,500~274,000원 지지 여부를 확인한다. 기한 내 확인되지 않으면 조건부 진입 계획을 이월하지 않는다. / 298,000원 돌파와 304,120원 위 종가 안착은 추세 재평가 신호일 뿐 별도 매수 신호가 아니다. 352,745원은 11월 25일 기준 200일선이다.","risk_condition_ko":"263,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-26T09:42:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":174600.0,"market_data_asof":"2026-11-26T09:42:00+09:00","market_data_clock_status":null,"session_vwap":173813.0979455559,"relative_volume":1.9916311968051963,"spread_bps":5.729017473503294,"day_high":176700.0,"day_low":170700.0,"execution_condition_ko":"170,000~171,500원 방어 후 179,900원 이상 종가와 다음 실제 거래일의 지지 여부를 본다. 거래량과 SK하이닉스 대비 상대주가는 반등의 질을 판단하는 보조 증거다. / 170,000원 회복에 실패하면 166,000~167,000원을 하방 관찰 구간으로만 본다. 확인된 지지나 매수 대안은 아니다.","risk_condition_ko":"170,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-26T09:42:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":153400.0,"market_data_asof":"2026-11-26T09:42:00+09:00","market_data_clock_status":null,"session_vwap":152987.38095682702,"relative_volume":1.448671057921363,"spread_bps":6.521030322791001,"day_high":156400.0,"day_low":149400.0,"execution_condition_ko":"145,900~146,200원 지지 후보가 유지된 뒤 155,700원 상회 종가와 다음으로 확인된 정규장의 되돌림 지지가 나오면 단기 반등을 재평가한다. / 162,770~167,000원 저항대 상단을 종가로 넘고 다음 정규장에서 지키면 기술적 약세를 재검토한다. 두 가격 신호 모두 매수 승인이 아니며 실제 발주와 현금 전환의 확인을 대신하지 않는다.","risk_condition_ko":"145,900 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-26T09:42:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":70900.0,"market_data_asof":"2026-11-26T09:42:00+09:00","market_data_clock_status":null,"session_vwap":70400.2114936051,"relative_volume":1.6873304679606203,"spread_bps":28.208744710860366,"day_high":72300.0,"day_low":68100.0,"execution_condition_ko":"66,700~67,800원 지지 또는 회복, 73,400원 상회 종가, 다음 확인 가능한 정규 거래일의 재시험 순서로 관찰한다. 자동 주문 조건은 아니다. / 73,400원 기준 첫 저항 78,000원까지 4,600원, 지지 하단 66,700원까지 6,700원이다. 상단 저항 81,176~81,700원을 목표로 잡아도 비용 전 보상은 위험의 약 1.16~1.24배다.","risk_condition_ko":"66,700 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-26T09:42:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":48600.0,"market_data_asof":"2026-11-26T09:42:00+09:00","market_data_clock_status":null,"session_vwap":48833.0985053532,"relative_volume":3.233638977218937,"spread_bps":10.282776349614394,"day_high":49550.0,"day_low":47150.0,"execution_condition_ko":"45,000~45,400원 지지 구간 재시험 후 45,400원 초과 종가는 안정 신호일 뿐 매수 조건은 아니다. / 49,300원 초과 정규장 종가를 일봉 거래량이 뒷받침하고 다음 실제 거래일 재시험 후에도 49,300원 위에서 마감하면 재평가한다. 업종 매도 완화와 상대강도가 동반되고 53,900~54,700원 저항대 하단까지 비용·갭 반영 후 보상이 충분할 때만 소규모 진입을 새로 승인할 수 있다.","risk_condition_ko":"45,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-26T09:42:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":41750.0,"market_data_asof":"2026-11-26T09:42:00+09:00","market_data_clock_status":null,"session_vwap":42254.199587470284,"relative_volume":1.6168744014905077,"spread_bps":48.019207683073226,"day_high":43050.0,"day_low":41400.0,"execution_condition_ko":"43,129~44,400원 회복, 44,400원 초과 정규장 종가, 다음 거래일 되돌림 지지를 순서대로 확인한다. 모두 매수 주문이 아닌 재심사 기준이다. / 45,714~46,250원을 돌파한 뒤 되돌림에서 지지로 전환되면 49,201~50,300원을 다음 저항으로 두고 실제 호가에서 순손익비를 다시 계산한다. 돌파만으로 진입하지 않는다.","risk_condition_ko":"40,300 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-26T09:42:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":40550.0,"market_data_asof":"2026-11-26T09:42:00+09:00","market_data_clock_status":null,"session_vwap":40447.723412073334,"relative_volume":1.1757321270932195,"spread_bps":12.338062924120914,"day_high":40950.0,"day_low":40000.0,"execution_condition_ko":"41,150원 회복 종가와 다음 실제 거래일의 지지는 초기 개선 신호일 뿐 매수 조건이 아니다. / 43,192~43,400원 구간 상단을 거래 증가와 함께 종가로 돌파하면 다음 실제 거래일 재시험과 44,094원 저항까지의 보상을 재평가한다.","risk_condition_ko":"39,600 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-26T09:42:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":39250.0,"market_data_asof":"2026-11-26T09:42:00+09:00","market_data_clock_status":null,"session_vwap":39647.46541832364,"relative_volume":4.129126273481991,"spread_bps":12.73074474856779,"day_high":40750.0,"day_low":38550.0,"execution_condition_ko":"40,750원 회복은 첫 관찰 신호다. 42,450~42,600원 저항대 상단 돌파와 다음 실제 거래일의 42,450원 지지 또는 재회복을 함께 확인한다. / 38,450원 미만 종가 이후 35,750~36,400원을 관찰한다. 35,750원 미만 종가 이후 32,050~32,200원은 재시험 관찰 구간이지 자동 재매수 구간이 아니다.","risk_condition_ko":"38,450 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-26T09:42:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":115000.0,"market_data_asof":"2026-11-26T09:42:00+09:00","market_data_clock_status":null,"session_vwap":115693.24285210914,"relative_volume":1.0617262284631714,"spread_bps":8.69187309865276,"day_high":117300.0,"day_low":114000.0,"execution_condition_ko":"117,600~118,500원 회복 또는 123,600원 위 정규장 마감 뒤 다음 실제 정규장의 지지와 업종 대비 상대강도를 확인한다. 다음 저항은 128,700~131,300원이며 가격 회복은 재검토 신호일 뿐이다. / 11월 16일 분기보고서와 11월 5일 단기차입 공시의 제출 사실만 확인됐다. 원문에서 재무제표 표시통화·단위·연결 범위·주식수와 소급조정 기준, 차입 규모·목적·금리·만기를 확인한다. 거래 통화는 원화이나 재무제표 표시통화를 뜻하지 않는다. 국내 상장 보통주 분석이므로 예탁증서 환산은 적용하지 않는다. 원문 검증 전에는 재무 금액과 주당순이익의 기간 비교 및 공급자 배수에 근거한 저평가 판단을 유보한다. 회사 전망과 시장 예상치도 미확인이다.","risk_condition_ko":"108,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-26T09:42:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":390000.0,"market_data_asof":"2026-11-26T09:42:00+09:00","market_data_clock_status":null,"session_vwap":391289.07860824745,"relative_volume":0.8444459971929323,"spread_bps":12.828736369467606,"day_high":396500.0,"day_low":383000.0,"execution_condition_ko":"389,775원 회복과 409,000원 초과 일봉 마감 후 실제 다음 거래일의 409,000원 지지를 확인한다. 409,000~416,500원은 관찰 구간이다. / 416,500원 초과 마감 뒤 지지가 확인되면 430,000~437,500원 저항대까지의 여유를 실제 거래가격, 방어선, 거래비용과 비교해 첫 매수 여부를 재평가한다.","risk_condition_ko":"366,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-26T09:42:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":160400.0,"market_data_asof":"2026-11-26T09:42:00+09:00","market_data_clock_status":null,"session_vwap":160715.40807771258,"relative_volume":1.0086410116818556,"spread_bps":6.236357966947303,"day_high":162200.0,"day_low":158000.0,"execution_condition_ko":"161,400원 초과 정규장 종가 뒤 다음 확인된 정규 거래일에 160,900~161,400원의 지지 또는 재돌파를 관찰한다. 매수 신호는 아니다. / 166,800원 초과 종가 뒤 166,000~166,800원이 후속 일봉에서 지지로 전환되고, 원공시상 수익성과 투자 후 현금흐름 중 하나가 안정되며 다른 쪽의 뚜렷한 악화가 이를 상쇄하지 않을 때만 중기 배분을 재심사한다. 176,000원은 다음 저항 참고값이다.","risk_condition_ko":"151,700 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-26T09:42:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003230.KS","display_name":"003230","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1308000.0,"market_data_asof":"2026-11-26T09:43:00+09:00","market_data_clock_status":null,"session_vwap":1311459.3267882187,"relative_volume":1.097003679820411,"spread_bps":15.290519877675841,"day_high":1323000.0,"day_low":1295000.0,"execution_condition_ko":"1,321,000원 초과 정규장 종가 직후의 다음 확인된 정규장에서 실제 재시험과 1,321,000원 이상 지지를 신선한 시세로 확인한다. 재시험 없는 시초가 급등은 추격하지 않는다. / 1,219,000~1,227,000원 구간을 시험한 뒤 1,227,000원 이상으로 마감하면 눌림 손익비를 별도로 재평가한다. 자동 매수나 대체 진입 조건은 아니다.","risk_condition_ko":"1,219,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:45:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"034230.KS","display_name":"034230","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":11650.0,"market_data_asof":"2026-11-26T09:43:00+09:00","market_data_clock_status":null,"session_vwap":11844.836863768698,"relative_volume":2.2967820022634338,"spread_bps":8.587376556462,"day_high":12050.0,"day_low":11440.0,"execution_condition_ko":"10,840~10,860원 테스트, 직전 조정 거래일보다 거래량이 늘어난 10,860원 이상 정규장 종가, 직후 실제 거래일의 10,860~10,950원 지지를 순서대로 확인한다. / 11,700원 위 정규장 종가와 다음 실제 거래일 지지는 별도로 관찰한다. 11,890~11,980원 저항이 가까워 이번 계획은 돌파 매수를 허용하지 않는다.","risk_condition_ko":"10,650 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:45:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":147500.0,"market_data_asof":"2026-11-26T09:43:00+09:00","market_data_clock_status":null,"session_vwap":150345.309388598,"relative_volume":1.962471094812924,"spread_bps":6.777363605557438,"day_high":152800.0,"day_low":147100.0,"execution_condition_ko":"실제 거래소 정규장 일정과 수정 일봉·실제 호가의 가격 기준을 대조한 뒤 완료 일봉의 눌림·종가 회복과 바로 다음 거래일의 신선한 정규장 시세로 재시험 지지를 확인한다. / 149,400원은 손익비와 보유 위험을 재평가할 첫 저항이다. 151,200~152,500원 저항대 상단을 거래량과 함께 넘고 재시험에서도 지켜야 별도 매수 기회로 검토한다.","risk_condition_ko":"142,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:45:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"012330.KS","display_name":"현대모비스","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":334500.0,"market_data_asof":"2026-11-26T09:43:00+09:00","market_data_clock_status":null,"session_vwap":338317.25431823113,"relative_volume":2.5803284993413995,"spread_bps":14.958863126402393,"day_high":355000.0,"day_low":329500.0,"execution_condition_ko":"012330.KS의 같은 정규장에서 저가 345,500~346,300원 시험, 직전 20거래일 평균을 웃도는 거래량, 349,500원 이상 종가를 확인한 뒤 다음 실제 정규장에서 349,500~350,000원의 신선한 시세와 순손익비를 확인한다. / 357,670~360,000원 저항 돌파 후 364,500원 위 안착은 관찰만 한다. 다음 저항 370,000~372,500원까지 여유가 좁아 별도 매수 경로로 쓰지 않는다.","risk_condition_ko":"345,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:45:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"003350.KS","display_name":"003350","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":14280.0,"market_data_asof":"2026-11-26T09:43:00+09:00","market_data_clock_status":null,"session_vwap":14276.771614677444,"relative_volume":6.227235745261799,"spread_bps":42.13483146067416,"day_high":14870.0,"day_low":13350.0,"execution_condition_ko":"실제 정규장 편성, 시세의 신선도, 수정주가와 실제 호가의 비교 가능성을 확인한다. 돌파 다음 정규장의 14,000~14,010원 재시험과 15,070원까지의 실질 손익비를 점검한다. / 돌파 실패 시 13,300원 회복과 12,270~12,450원 지지 여부를 관찰한다. 눌림이나 지지 구간 도달만으로 매수하지 않는다.","risk_condition_ko":"12,270 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:45:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":215000.0,"market_data_asof":"2026-11-26T09:43:00+09:00","market_data_clock_status":null,"session_vwap":216370.7644536009,"relative_volume":1.4784923045904939,"spread_bps":23.28288707799767,"day_high":220000.0,"day_low":213000.0,"execution_condition_ko":"정규장 210,000~211,000원 눌림에서 매도 거래량 둔화와 같은 날 211,000원 초과 종가를 확인한다. 다음 실제 정규장에는 211,000원 재지지와 211,000~213,000원 체결 가능 범위를 확인한다. / 219,000원 위 종가와 다음 거래일 재지지, 거래량 개선을 관찰한다. 확인 시 224,430원 부근을 다음 저항으로 보되 단독 매수 신호로 쓰지 않는다.","risk_condition_ko":"199,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:45:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"180640.KS","display_name":"180640","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":237500.0,"market_data_asof":"2026-11-26T09:43:00+09:00","market_data_clock_status":null,"session_vwap":239740.1615228885,"relative_volume":0.8555380505325648,"spread_bps":21.03049421661409,"day_high":249500.0,"day_low":233500.0,"execution_condition_ko":"11월 25일까지의 한국투자증권 한국거래소 수정 일봉 248개가 가격 기준이다. 11월 26일 08:28:42 한국시간 판단 시점에 계획은 만료되지 않았으나 08:17:53 조회는 당일 정규장 체결 근거가 아니다. 실제 거래일과 신선한 정규장 체결을 별도로 확인한다. / 234,000~236,000원에서는 반등과 거래량 회복을 관찰한다. 구간을 회복하지 못하면 추가 매수를 보류하고, 반등만으로는 매수하지 않는다. 221,500원 이탈 뒤에는 214,500~214,800원을 재평가한다.","risk_condition_ko":"221,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:45:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"011200.KS","display_name":"011200","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":21950.0,"market_data_asof":"2026-11-26T09:43:00+09:00","market_data_clock_status":null,"session_vwap":22093.60234282068,"relative_volume":0.9630694135748542,"spread_bps":22.753128555176335,"day_high":22350.0,"day_low":21850.0,"execution_condition_ko":"22,275~22,350원 회복은 관찰 신호다. 거래 참여가 회복된 22,750원 상회 마감과 직후 실제 정규장의 22,750~22,850원 지지, 비용 차감 후 손익비 개선이 함께 확인되면 소량 진입을 재심사한다. / 21,900원 하회 마감 뒤에는 21,200~21,370원을, 21,200원 하회 마감 뒤에는 19,840~19,925원을 관찰한다. 두 구간 모두 저가매수 신호가 아니다.","risk_condition_ko":"21,900 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:45:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"128940.KS","display_name":"128940","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":468500.0,"market_data_asof":"2026-11-26T09:43:00+09:00","market_data_clock_status":null,"session_vwap":467484.4210598478,"relative_volume":0.9617109584375497,"spread_bps":10.678056593699946,"day_high":476000.0,"day_low":460000.0,"execution_condition_ko":"464,000~464,250원 지지와 476,000원 상회 종가를 관찰한다. 돌파 시 다음 실제 거래일의 지지 유지 또는 재돌파, 후속 수요, 493,000원 대비 비용·갭 반영 순손익비를 함께 점검한다. 가격과 사업 근거는 2026-12-03 한국시간까지 재검토한다. 이는 검토 기한이지 주문 만료일이나 확정 거래일이 아니다. / 원공시에서 공시·접수 시각, 재무제표 보고통화와 표시 단위, 분기 구분, 보통주 기준, 예탁증서 적용 여부와 해당 시 보통주 환산 비율을 확인한다. 공급업체의 원화 표시나 거래통화만으로 보고 기준을 확정하지 않는다. 미검증 주당이익과 예상이익 산출 근거가 불명확한 선행 주가수익비율은 사용하지 않는다.","risk_condition_ko":"451,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:45:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"028050.KS","display_name":"028050","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":58000.0,"market_data_asof":"2026-11-26T09:43:00+09:00","market_data_clock_status":null,"session_vwap":58877.15376285481,"relative_volume":1.0094804665139803,"spread_bps":17.25625539257981,"day_high":60100.0,"day_low":57800.0,"execution_condition_ko":"위험 대응 조건: 57,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"57,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:45:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"003490.KS","display_name":"003490","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":29850.0,"market_data_asof":"2026-11-26T09:43:00+09:00","market_data_clock_status":null,"session_vwap":30234.664483647124,"relative_volume":2.9242421797780924,"spread_bps":16.736401673640167,"day_high":31350.0,"day_low":29650.0,"execution_condition_ko":"위험 대응 조건: 30,450 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"30,450 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:45:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":180300.0,"market_data_asof":"2026-11-26T09:43:00+09:00","market_data_clock_status":null,"session_vwap":180642.87484393327,"relative_volume":1.4985685798098558,"spread_bps":5.547850208044383,"day_high":184500.0,"day_low":179000.0,"execution_condition_ko":"위험 대응 조건: 177,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"177,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:45:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"439090.KQ","display_name":"439090","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":16690.0,"market_data_asof":"2026-11-26T09:43:00+09:00","market_data_clock_status":null,"session_vwap":16683.528274488654,"relative_volume":2.1093574326869224,"spread_bps":5.989817310572028,"day_high":16950.0,"day_low":16400.0,"execution_condition_ko":"위험 대응 조건: 16,250 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"16,250 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:45:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"030530.KQ","display_name":"030530","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":28850.0,"market_data_asof":"2026-11-26T09:43:00+09:00","market_data_clock_status":null,"session_vwap":28684.17618526388,"relative_volume":2.2162955231576356,"spread_bps":17.346053772766695,"day_high":29400.0,"day_low":27700.0,"execution_condition_ko":"위험 대응 조건: 27,100 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"27,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:45:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010170.KQ","display_name":"010170","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":13930.0,"market_data_asof":"2026-11-26T09:43:00+09:00","market_data_clock_status":null,"session_vwap":13932.947165692736,"relative_volume":1.7719571078757859,"spread_bps":7.176175098672408,"day_high":14190.0,"day_low":13600.0,"execution_condition_ko":"위험 대응 조건: 13,105 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"13,105 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:45:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"108490.KQ","display_name":"로보티즈","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":290500.0,"market_data_asof":"2026-11-26T09:42:00+09:00","market_data_clock_status":null,"session_vwap":290772.5666840033,"relative_volume":4.447592599669097,"spread_bps":17.196904557179707,"day_high":299500.0,"day_low":281000.0,"execution_condition_ko":"위험 대응 조건: 283,500 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"283,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-26T09:42:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-26T09:44:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"356680.KQ","display_name":"356680","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"market_data_clock_status":"missing","session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"현재 명시된 위험 행동 없음","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 재확인","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-25T14:42:00.640864+09:00",
  "as_of": "2026-11-25T14:33:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
