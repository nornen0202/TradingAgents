# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-15T00:25:29.516519+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261015T055359_local-scheduler-kr-full",
  "producer_finished_at": "2026-10-15T07:55:28.373485+09:00",
  "analysis_run_id": "20261015T055359_local-scheduler-kr-full",
  "analysis_completed_at": "2026-10-15T07:45:21.350231+09:00",
  "analysis_trade_date_oldest": "2026-10-14",
  "analysis_trade_date_latest": "2026-10-14",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-14T20:00:00+09:00",
  "market_data_latest_at": "2026-10-14T20:00:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-15T07:45:45.464259+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-15T07:45:45.464259+09:00",
    "run_started_at": "2026-10-15T05:53:59.005331+09:00",
    "run_finished_at": "2026-10-15T07:55:28.373485+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 9221800,
    "total_unrealized_pnl_krw": -5722436,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 10198452
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1419000,
      "market_value_krw": 2838000,
      "unrealized_pnl_krw": -2597000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 232000,
      "market_value_krw": 2320000,
      "unrealized_pnl_krw": -1003851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 294500,
      "market_value_krw": 1472500,
      "unrealized_pnl_krw": -602143
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 177200,
      "market_value_krw": 708800,
      "unrealized_pnl_krw": -266200
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 543000,
      "market_value_krw": 543000,
      "unrealized_pnl_krw": -610000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 18950,
      "market_value_krw": 341100,
      "unrealized_pnl_krw": -227215
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 76000,
      "market_value_krw": 228000,
      "unrealized_pnl_krw": -72000
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 217500,
      "market_value_krw": 217500,
      "unrealized_pnl_krw": -156667
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 179400,
      "market_value_krw": 179400,
      "unrealized_pnl_krw": -102934
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 145000,
      "market_value_krw": 145000,
      "unrealized_pnl_krw": -27300
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 51000,
      "market_value_krw": 102000,
      "unrealized_pnl_krw": -16200
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 69400,
      "market_value_krw": 69400,
      "unrealized_pnl_krw": -43531
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 57100,
      "market_value_krw": 57100,
      "unrealized_pnl_krw": 2600
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1419000.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1,400,000~1,402,000 유지와 저점 갱신 중단을 관찰한다. 확정된 바닥으로 간주하지 않는다. / 갱신된 200일선과 1,458,000 회복·되돌림 지지 이후 1,497,000 위 종가 및 다음 거래일 지지를 확인한다.","risk_condition_ko":"1,400,000 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":232000.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"228000~231000원 재시험 후 회복과 높아지는 5분봉 저점을 관찰한다. 접촉만으로 매수하지 않는다. / 241500~244000원 회복·재시험 지지, 최신 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상을 확인한다. 손익비가 부족하면 계속 관망한다.","risk_condition_ko":"246,000 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":177200.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"010120.KS 173100~174100 지지 유지, 179900~182500 초기 회복과 183600~184200 재시험을 구분해 관찰한다. 관찰가격 도달만으로 주문하지 않는다. / 010120.KS 193800~195500 및 200000~200900에서 반등 지속 또는 실패를 확인한다. 저항 도달 자체는 자동 이익 실현 신호가 아니다.","risk_condition_ko":"173,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":294500.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"278470.KS 실제 정규장·거래 가능 여부와 최신 체결·호가·거래량·세션 거래량가중평균가격 확보 / 278470.KS 300,500원 위 5분봉 종가·재시험 지지·돌파 거래량 증가와 재시험 매도 거래량 감소 확인","risk_condition_ko":"279,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":543000.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"267260.KS 최신 체결시각·호가·거래정지 및 실제 정규장 운영 여부 확인 / 531000원 유지, 저점 상승 및 상대강도지수 30 회복 관찰; 과매도만으로 바닥 판단 금지","risk_condition_ko":"531,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":76000.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"058470.KQ 최신 정규장 자료에서 75,000~75,300원 지지와 위험예산 준수 여부 확인. / 058470.KQ 79,700원 회복 및 79,200~79,700원 재시험 후 가까운 저항과 비용을 반영한 손익비 재산정. 목표 상향이나 부당하게 좁은 손절로 기준을 맞추지 않는다.","risk_condition_ko":"75,000 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":217500.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"042700.KS의 213500~216000원 방어와 저점 상승을 최신 정상 거래에서 확인한다. / 228000~231500원 회복·재시험 지지, 실제 장중 거래량가중평균가격 상회, 동일 시간대 상대거래량 1.2배 이상을 확인한다. 전일 일거래량 비율 1.14는 당일 상대거래량이 아니다.","risk_condition_ko":"228,178 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":179400.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"035420.KS 거래 가능 상태와 최신 정규장 5분봉·체결량·호가·세션 거래량가중평균가격을 먼저 확보한다. / 177,800~178,000원 지지 방어와 173,200원 재시험을 구분해 관찰한다.","risk_condition_ko":"177,800 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":57100.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"403870.KQ 56,000~56,100원 방어 후 57,400원 재돌파·재지지, 거래량가중평균가격 상회 및 동일 시간대 상대거래량 1.2 이상 / 403870.KQ 61,000~61,600원 회복, 62,700원 위 종가 및 다음 실제 거래일 재지지","risk_condition_ko":"56,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":69400.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"034020.KS의 최신 정규장 시세로 68,300원 및 67,300원 방어 확인 / 70,500~70,700원 회복·재시험과 71,200~71,500원 저항 통과 확인; 자동 매수 금지","risk_condition_ko":"67,300 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":145000.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"353200.KS의 142,800~144,100원 지지와 최신 5분봉 두 개의 유지, 거래량가중평균가격 상회 및 동일 시간대 상대거래량 1.2 이상을 관찰한다. 이 조건만으로 신규 매수하지 않는다. / 353200.KS의 141,100원 장중 이탈 후 회복 실패는 위험 재점검 신호이고 단독 전량 청산 조건은 아니다.","risk_condition_ko":"145,000 이상 도달, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":51000.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단 시각은 2026-10-15T06:31:50.537744+09:00이다. 이 시각만으로 실제 거래일, 장 운영 상태, 호가 신선도를 확인할 수 없다. 최신 제공 장중 자료는 2026-10-14 20:00으로 표기되어 있으며 시간대와 거래 구분도 재확인해야 한다. / 10:30은 검증된 거래일의 최초 시험 매수 검토 가능 시각이지 만료 시각이 아니다. 활성 조건부 주문이나 확인된 만료 시각이 없어 다음 거래일로 임의 이월하지 않는다.","risk_condition_ko":"49,800 이하 하락, 장중 확인 시 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":18950.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"현재 명시된 위험 행동 없음","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":181800.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"033780.KS 실제 거래일·정규장·거래정지 상태와 시각이 있는 호가·체결·당일 거래량가중평균가격·동시간대 거래량을 확보한다. / 178,600~179,900원 접근에서는 방어 신호를 우선한다. 위험 축소 신호가 해소되고 179,900원 회복이 확인된 뒤에만 눌림 매수를 다시 검토한다.","risk_condition_ko":"179,900 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":163200.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"실제 거래일·정규장·거래정지 여부와 신선한 호가·5분봉·거래량가중평균가격 확보. / 165400원 상향 돌파와 재시험 지지, 거래량가중평균가격 상회, 동시간대 상대거래량 1.2배 이상. 과거 일평균 대비 1.27배 거래량은 이 조건의 충족 증거가 아니다.","risk_condition_ko":"152,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"062040.KS","display_name":"062040","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":212000.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"062040.KS 215,648원·217,219원 회복과 220,000원 돌파·재시험 지지를 관찰한다. 이동평균은 실행 전에 갱신한다. / 062040.KS 206,500원 지지 반등 또는 회복 실패와 199,800~201,500원 핵심 지지를 관찰한다. 지지 반등은 별도 진입·손절 구조를 검증하기 전 매수 신호가 아니다.","risk_condition_ko":"206,500 이하 하락, 장중 확인 시 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010950.KS","display_name":"S-Oil","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":162500.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"010950.KS의 159,700~161,200원 지지, 저점 상승과 당일 거래량가중평균가격 상회를 최신 정규장 자료로 확인한다. / 010950.KS의 166,000원 돌파·재시험 유지와 동시간대 상대거래량 1.2 이상을 확인한다. 1.2는 제안 기준이지 관측값이 아니다.","risk_condition_ko":"159,700 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"373220.KS","display_name":"LG에너지솔루션","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":422000.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"373220.KS 409,000~410,000원 저점 형성·반등, 거래량가중평균가격 회복, 동일 시간대 상대거래량 1.2 이상 확인 / 373220.KS 428,000원 상회 종가와 재시험 지지 이후 비용 차감 보상비율 재평가","risk_condition_ko":"409,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"093370.KS","display_name":"093370","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":14060.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"093370.KS 최신 정규장 체결 시각·거래 가능 상태·호가·당일 거래량가중평균가격·동일 시간대 누적 상대거래량 확보. / 093370.KS 14,650 회복과 14,890~15,000 돌파·재시험, 또는 13,330~13,770 지지대의 저점 상향과 실제 반등 체결 확인.","risk_condition_ko":"13,330 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"105560.KS","display_name":"105560","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":159200.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단 기준시각은 2026-10-15T07:28:31.810489+09:00이며 일봉 기준일은 2026-10-14다. 실제 거래일·휴장·조기종료·거래정지·최신 체결시각은 별도 확인해야 한다. / 10:30은 확인된 정규장의 최소 시험 진입 재평가 시각이지 활성화 또는 만료시각이 아니다. 유효한 진입 만료시각은 제공되지 않았다. 만료를 선언하거나 다음 거래일로 이월하지 않는다.","risk_condition_ko":"158,400 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"095340.KQ","display_name":"ISC","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":174200.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단 시각은 2026-10-15T07:38:40.769998+09:00이고 일별 가격 기준일은 2026-10-14다. 실제 거래일, 정규장 운영, 거래 상태와 시세 신선도는 별도 확인이 필요하다. / 공급된 기술 자료의 종가 174200과 하락률 5.17%를 기준 관찰값으로 사용한다. 뉴스의 하락률 5.50%와의 차이는 미해결이며 지연된 야간 가격으로 현재 조건을 판정하지 않는다.","risk_condition_ko":"170,400 이하 하락, 거래량 조건 확인 후 (매도 거래량 증가와 회복 실패 확인) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"452190.KQ","display_name":"452190","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":5400.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"452190.KQ의 실제 거래일·정규 세션·거래정지 여부·최신 체결 시각·호가·거래량·거래량가중평균가격을 확인한다. / 5,340 방어와 저점 상승, 5,600 회복을 관찰한다. 5,820~5,860 재지지 이후에도 첫 현실적 저항까지 비용 차감 보상/위험이 2 미만이면 매수하지 않는다.","risk_condition_ko":"5,340 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"018880.KS","display_name":"018880","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":3920.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"018880.KS의 실제 거래일·정규장 상태, 거래정지·변동성 제한, 최신 호가·체결·스프레드·5분봉을 확인한다. / 3880원 부근 장기 추세 경계 위에서 종가와 후속 지지가 지속되는지 확인한다.","risk_condition_ko":"3,630 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"086790.KS","display_name":"086790","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":121600.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"086790.KS 최신 정규장 거래 상태·가격·호가·장중 거래량가중평균가격·동일 시간대 상대거래량을 확보한다. / 086790.KS 120600 지지 반응, 119400 이탈 여부, 갱신한 200일 평균을 우선 감시한다. 상대강도지수 32.76만으로 매수하지 않는다.","risk_condition_ko":"119,400 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"088350.KS","display_name":"088350","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":4750.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단 시각은 2026-10-15T07:28:21.777020+09:00이며 일별 가격 기준일은 2026-10-14다. 이 시각만으로 개장 여부나 거래 가능성을 판단하지 않는다. 거래일·정규장·거래정지·호가 시각·스프레드·잔량을 별도 확인한다. / 088350.KS의 4680 지지와 갱신된 장기 이동평균 방어, 4810 회복·재시험을 관찰한다. 당일 거래량가중평균가격 상회와 같은 경과 시간 대비 상대거래량 1.2배 이상을 확인한다. 과거 일일 거래량 1.49배는 이를 대신하지 않는다.","risk_condition_ko":"4,680 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"041190.KQ","display_name":"041190","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":5540.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"041190.KQ의 실제 거래일·정규장 운영, 최신 체결 시각·호가·당일 거래량가중평균가격·동일 시간대 상대거래량을 확인한다. / 5,450~5,515원 방어, 5,660~5,680원 회복, 5,825~5,850원 회복·재지지 순서와 각 단계의 비용 후 보상·위험을 관찰한다.","risk_condition_ko":"5,450 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"066570.KS","display_name":"LG전자","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":177400.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"175,200원 종가 지지, 170,800원 하향 이탈 및 계좌 집중·갭 위험 변화. / 180,350~182,000원 회복·재시험과 184,500~184,700원 저항 소화. 단순 회복은 매수 승인 조건이 아니다.","risk_condition_ko":"175,200 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005935.KS","display_name":"005935","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":173600.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단 시각은 2026-10-15T06:47:13.223512+09:00이며 일별 가격 기준일은 2026-10-14다. 이 시각만으로 실제 거래일, 정규장 상태, 거래정지 여부 또는 조건 충족을 확인할 수 없다. / 이전 분석가의 시각보다 제공된 최종 판단 시각을 사용한다. 10:30은 향후 검토 계획의 가장 이른 진입 시각이지 만료 시각이 아니다. 승인된 진입이나 만료 기한이 없으므로 다음 거래일로 이월하지 않는다.","risk_condition_ko":"170,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"069540.KQ","display_name":"069540","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":4160.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단 기준 시각은 2026-10-15T07:41:02.373761+09:00이며 일봉 기준일은 2026-10-14다. 실제 거래일·세션·거래정지·시장경보·최신 체결 시각은 별도 확인이 필요하다. / 제공 장중 가격의 실제 시각은 2026-10-14 20:00이다. 이를 당일 가격으로 사용하거나 거래량 0·상대거래량 0을 수요 부재로 해석하지 않는다.","risk_condition_ko":"4,035 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":591000.0,"market_data_asof":"2026-10-14T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"006400.KS의 거래일 달력, 정규장 여부, 거래정지 상태, 최신 체결시각과 호가를 확인한다. / 575,000원 부근 매도 거래 감소와 지지 회복을 관찰하되 단순 가격 도달로 매수하지 않는다.","risk_condition_ko":"559,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-14T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-14T20:30:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-14T15:02:59.264434+09:00",
  "as_of": "2026-10-14T15:00:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
