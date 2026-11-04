# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-04T00:23:57.441554+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261104T091954_local-freshness-kr-overlay",
  "producer_finished_at": "2026-11-04T09:21:13.033121+09:00",
  "analysis_run_id": "20261103T060107_local-scheduler-kr-full",
  "analysis_completed_at": "2026-11-03T08:54:19.761378+09:00",
  "analysis_trade_date_oldest": "2026-10-30",
  "analysis_trade_date_latest": "2026-10-30",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-04T09:20:00+09:00",
  "market_data_latest_at": "2026-11-04T09:20:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-04T09:02:06.740279+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-04T09:02:06.740279+09:00",
    "run_started_at": "2026-11-04T09:00:14.262493+09:00",
    "run_finished_at": "2026-11-04T09:02:11.857887+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 8600750,
    "total_unrealized_pnl_krw": -6343486,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 9577402
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1465000,
      "market_value_krw": 2930000,
      "unrealized_pnl_krw": -2505000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 226250,
      "market_value_krw": 2262500,
      "unrealized_pnl_krw": -1061351
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 243500,
      "market_value_krw": 1217500,
      "unrealized_pnl_krw": -857143
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 154000,
      "market_value_krw": 616000,
      "unrealized_pnl_krw": -359000
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 449000,
      "market_value_krw": 449000,
      "unrealized_pnl_krw": -704000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 17400,
      "market_value_krw": 313200,
      "unrealized_pnl_krw": -255115
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 188900,
      "market_value_krw": 188900,
      "unrealized_pnl_krw": -185267
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
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 55500,
      "market_value_krw": 166500,
      "unrealized_pnl_krw": -133500
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 107500,
      "market_value_krw": 107500,
      "unrealized_pnl_krw": -64800
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 42600,
      "market_value_krw": 85200,
      "unrealized_pnl_krw": -33000
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 52600,
      "market_value_krw": 52600,
      "unrealized_pnl_krw": -60331
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 41150,
      "market_value_krw": 41150,
      "unrealized_pnl_krw": -13350
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":155300.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":155805.56643374544,"relative_volume":2.49296145659072,"spread_bps":6.43707756678468,"day_high":158600.0,"day_low":153500.0,"execution_condition_ko":"2026-10-30 이후 일별 시가·고가·저가·종가·거래량과 지표를 갱신하고 2026-11-02 보도 종가 160,600과 조정 기준을 대조한다. 지연된 20:00 자료는 현재 호가가 아니다. / 153,700–155,200 눌림, 이후 155,200 이상 종가, 다음 확인된 거래일의 구간 지지를 순서대로 관찰한다. 가격 접촉이나 보도된 반등만으로 매수하지 않는다.","risk_condition_ko":"153,700 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":17680.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":17659.297551086667,"relative_volume":5.331741041127416,"spread_bps":5.654509471303364,"day_high":18050.0,"day_low":16900.0,"execution_condition_ko":"2026-11-02 공식 일봉 가격·거래량과 이후 자료를 확보한다. 보도된 17,120원과 지연 자료의 마지막 17,180원 및 등락률 불일치를 해소하며 어느 값도 현재 체결가로 사용하지 않는다. / 단기 지수이동평균, 거래량가중이동평균, 50일 이동평균과 중간 저항선을 갱신한다. 17,320원 초과 종가와 다음 실제 거래일의 17,260–17,320원 지지를 확인한다.","risk_condition_ko":"15,320 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1445000.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":1462096.7461063105,"relative_volume":2.0510236160823205,"spread_bps":6.918021445866483,"day_high":1476000.0,"day_low":1444000.0,"execution_condition_ko":"1381000~1399000원 지지와 저점 상승을 감시한다. 지지구간 접촉만으로 매수하지 않으며 1449000원 회복도 초기 점검에 불과하다. / 1495000원 종가 돌파와 거래량 개선, 다음 정규장 재시험·종가 확인, 이후 1479000~1495000원 지지 재확인을 순서대로 확인한다.","risk_condition_ko":"1,381,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":448000.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":451034.4455181038,"relative_volume":1.8910773344709473,"spread_bps":11.166945840312675,"day_high":459500.0,"day_low":443000.0,"execution_condition_ko":"418,000원 방어·종가 이탈 여부를 최신 정규장 일봉으로 확인한다. 위험한도를 지킬 수 없으면 보유 없이 관찰한다. / 431,500~440,500원과 447,000~462,500원 순차 회복을 관찰하되 매수 승인으로 해석하지 않는다.","risk_condition_ko":"418,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":223500.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":225990.68891290814,"relative_volume":1.7748048439939552,"spread_bps":22.3463687150838,"day_high":228000.0,"day_low":223000.0,"execution_condition_ko":"005930.KS의 누락된 2026-11-02 일봉과 최신 확인 정규장 자료를 확보하고, 수정주가와 실제 주문가격의 기준 및 거래 가능 여부를 대조한다. / 005930.KS의 220000~222776 방어와 216500 종가 이탈 여부를 신규 매수 검토보다 먼저 확인한다.","risk_condition_ko":"237,323 이하 하락, 종가 확인 후 (위험 축소에 거래량 조건 없음.) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":250500.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":245148.7593288428,"relative_volume":2.7839057978863884,"spread_bps":19.98001998001998,"day_high":252000.0,"day_low":239500.0,"execution_condition_ko":"266500원 회복은 첫 점검 신호일 뿐 매수나 축소 취소 조건이 아니다. / 종가 279000원 이상과 다음 확인된 정규거래일의 272000~279000원 지지 유지는 미집행 축소와 약세 강도 재평가 조건이다.","risk_condition_ko":"266,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":188700.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":188832.62702838168,"relative_volume":2.318360867045141,"spread_bps":5.3008216273522395,"day_high":191000.0,"day_low":185400.0,"execution_condition_ko":"한국시간 2026-11-03~2026-11-10에 공식 일봉과 원공시를 갱신한다. 2026-11-10은 재검토일이지 주문 만료일이나 확인된 거래일이 아니다. / 181100~184000원 종가 지지 형성을 관찰하되 지지만으로 신규 매수하지 않는다.","risk_condition_ko":"181,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":170900.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":171303.67809670136,"relative_volume":1.3894647378428824,"spread_bps":5.8530875036581795,"day_high":172400.0,"day_low":170300.0,"execution_condition_ko":"170,700~171,100 지지대의 종가 유지와 이탈 후 다음 실제 거래일 종가 회복 여부를 우선 확인한다. / 174,800~175,400 및 176,400~178,000 반등 구간 진입 후 하단 미만 종가 복귀 여부를 확인해 추가 축소 조건을 판정한다.","risk_condition_ko":"170,700 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":103400.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":106163.98535969052,"relative_volume":7.41310056075854,"spread_bps":19.36108422071636,"day_high":109000.0,"day_low":102900.0,"execution_condition_ko":"2026-11-02 및 이후 최신 정규장 일봉·체결 가능 가격을 확보하고 실제 KRX 거래일·휴장 여부를 확인한다. 2026-11-03T07:01:46.853489+09:00이라는 판단 시각만으로 세션이나 신호 충족을 추정하지 않는다. / 120300원 초과 종가와 다음 실제 거래일 119700~120300원 지지 유지, 잔여 위험한도 충족 시 추가 위험축소 종료를 검토한다. 신규매수는 별도 판단이다.","risk_condition_ko":"114,300 이하 하락, 종가 확인 후 (거래량 증가를 요구하지 않음) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":55300.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":55551.43650453539,"relative_volume":1.3190293699264843,"spread_bps":18.066847335140018,"day_high":56100.0,"day_low":55000.0,"execution_condition_ko":"55,200~55,500원 종가 회복과 56,100원 초과 여부를 초기 개선 신호로 관찰한다. 자동 매수 조건은 아니다. / 57,700원 초과 종가 후 다음 실제 거래세션의 지지 또는 재돌파를 확인한다. 58,900원까지 여유는 57,700원 기준 약 2.1%에 불과하므로 실제 진입가·손절가·비용으로 보상 대비 위험을 다시 계산한다.","risk_condition_ko":"55,200 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":53200.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":53235.05864027854,"relative_volume":2.0136945056308933,"spread_bps":37.66478342749529,"day_high":54000.0,"day_low":52500.0,"execution_condition_ko":"034020.KS의 52,400~52,500원 지지 후보 방어 여부를 확인한다. 아직 바닥 확정은 아니다. / 034020.KS의 55,700~55,800원 종가 회복 또는 중요한 원문 공시 확인 시 약세 근거를 조기 재점검한다. 단독 매수 승인은 아니다.","risk_condition_ko":"52,400 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":42000.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":42263.86092996881,"relative_volume":1.1350501869888778,"spread_bps":23.837902264600714,"day_high":42700.0,"day_low":41850.0,"execution_condition_ko":"083450.KQ의 42650원 위 종가와 다음 실제 정규거래일 42350~42650원 지지: 회복 관찰 및 약세 강도 재평가. / 44350원 위 종가와 정규장 거래량 개선, 이후 44200~44350원 지지: 근거·비용 반영 손익비 재평가. 자동 매수하지 않는다.","risk_condition_ko":"40,550 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":40950.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":41152.89151205212,"relative_volume":2.152152652761322,"spread_bps":24.390243902439025,"day_high":41650.0,"day_low":40800.0,"execution_condition_ko":"공식 2026-11-02 일봉과 이후 최신 정규장 자료를 확보하고 회복·손절 조건의 충족 여부를 먼저 확인한다. 기사별 상승률이나 지연 야간 가격으로 돌파를 확정하지 않는다. / 44900원 이상 종가 이후 다음 실제 거래일 44650-44900원 재시험 지지와 44650원 이상 종가 유지 여부를 확인한다.","risk_condition_ko":"42,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"028050.KS","display_name":"028050","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":65000.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":64445.35110450162,"relative_volume":3.640193421306461,"spread_bps":15.39645881447267,"day_high":65500.0,"day_low":62400.0,"execution_condition_ko":"2026-11-02로 표기된 누락 일봉과 이후 이용 가능한 정규장 자료를 확보해 감축·손절 조건의 선행 충족 여부부터 확인한다. 거래일·휴장·거래 가능 상태와 가격 신선도는 별도로 검증한다. / 최초 확인 종가는 2026-11-03 또는 이후 확인된 실제 정규장에서 형성돼야 한다. 60,100~60,400원 재시험 후 종가 60,400원 이상 회복과 다음 실제 거래일 지지 유지가 필요하며 단순 가격 도달은 매수 신호가 아니다.","risk_condition_ko":"60,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":194400.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":192743.69747899158,"relative_volume":1.0574536856342924,"spread_bps":5.142710208279763,"day_high":194500.0,"day_low":191100.0,"execution_condition_ko":"192100~194000에서 새 일봉 지지와 다음 실제 거래일 유지 여부를 우선 확인한다. 가격 조건뿐 아니라 공시·예정 사건·계좌 위험 점검이 완료돼야 첫 진입을 검토한다. / 189600~190500은 더 깊은 지지 관찰대일 뿐 자동 매수 구간이 아니다. 현재 계획 취소 후에는 새로운 손익비와 위험 기준 없이 재진입하지 않는다.","risk_condition_ko":"192,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":128700.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":128891.82535641547,"relative_volume":2.3717554138060946,"spread_bps":7.766990291262136,"day_high":130900.0,"day_low":127200.0,"execution_condition_ko":"090430.KS는 2026-11-03~2026-11-10의 약 1주 동안 지지 회복형 진입을 관찰한다. 123500~124300원 시험 후 124300원 이상 종가 회복, 다음 실제 거래일 124300~125000원에서만 제한적 첫 진입을 검토한다. / 130700원 종가 회복과 다음 실제 거래일 지지 확인은 추세 개선 재평가 신호이며 자동 추가매수 신호가 아니다.","risk_condition_ko":"123,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"036460.KS","display_name":"036460","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":37450.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":37452.33947703604,"relative_volume":1.9928158680401544,"spread_bps":13.3422281521014,"day_high":37600.0,"day_low":37200.0,"execution_condition_ko":"36300~36450원 방문 후 36450원 이상 종가 회복과 다음 실제 거래일 종가 지지를 순서대로 확인한다. 확인 후 구간을 재방문하면 새로운 악재나 지지 훼손을 다시 점검하고 과거 신호를 기계적으로 재사용하지 않는다. / 37250원 위 종가와 다음 실제 거래일 지지를 관찰하되 첫 돌파만으로 매수하지 않는다. 38100원 위 종가와 다음 실제 거래일 지지가 확인되면 새 목표·손절·비용 후 보상·위험을 설정해 별도 재평가한다.","risk_condition_ko":"36,300 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"271560.KS","display_name":"271560","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":117300.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":116602.5746652935,"relative_volume":0.8103038191690959,"spread_bps":17.064846416382252,"day_high":117600.0,"day_low":115700.0,"execution_condition_ko":"111900-112000원 지지 회복과 112000원 이상 종가, 다음 실제 정규 거래일 지지 유지 확인. 가격 도달만으로 매수하지 않는다. / 110800원 미만 종가는 신규 매수 보류, 110100원 미만 종가는 손절성 감축 우선이다.","risk_condition_ko":"110,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000810.KS","display_name":"000810","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":658000.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":652279.0544109879,"relative_volume":1.5866075024717647,"spread_bps":15.20912547528517,"day_high":658000.0,"day_low":646000.0,"execution_condition_ko":"2026-10-30 이후 최신 정규장 일봉, 실제 거래일 달력·거래 가능 상태·자료 신선도를 확인한다. 불일치하는 지연 야간 가격은 제외한다. / 최초 진입 전에 핵심 재무 원문과 표시통화·단위·주식 기준을 확인한다. 확인할 수 없으면 신규 대기를 유지한다.","risk_condition_ko":"637,000 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003490.KS","display_name":"003490","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":29400.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":29671.62974954886,"relative_volume":4.761423532345873,"spread_bps":16.99235344095157,"day_high":30100.0,"day_low":28900.0,"execution_condition_ko":"003490.KS의 2026-10-30 이후 전체 누락 일봉·거래량, 최신 공시, 거래 가능 상태와 가격 조정 기준을 우선 점검한다. 중간 무효화가 있었다면 이후 가격 회복만으로 기존 계획을 재사용하지 않는다. / 003490.KS의 26000~26210원 재시험, 26210원 이상 종가 회복과 다음 유효 정규장 지지 유지가 확인되면 비용 후 보상·위험을 재계산해 최대 0.5% 스타터를 검토한다.","risk_condition_ko":"25,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"180640.KS","display_name":"180640","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":172200.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":172762.07371197015,"relative_volume":39.23795555358536,"spread_bps":5.808887598024978,"day_high":179300.0,"day_low":161900.0,"execution_condition_ko":"누락된 2026-11-02 정규장 원시 일봉과 이후 가격·거래량, 실제 거래 가능 상태를 확인한다. 2026-10-30 종가 123900원은 사건 이후의 지지 이탈 증거가 아니며, 기사상 134800원과 장후 144100원도 현재 체결가가 아니다. / 127300~130600원 재시험과 확인 종가·다음 실제 거래일 지지, 집행 근거, 비용 및 체결 여유를 반영한 최소 2배 보상을 함께 확인한다.","risk_condition_ko":"127,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"207940.KS","display_name":"207940","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1419000.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":1421899.5598239296,"relative_volume":0.5936280493742344,"spread_bps":14.094432699083862,"day_high":1432000.0,"day_low":1411000.0,"execution_condition_ko":"207940.KS는 향후 1주간 관찰한다. 2026-11-05 예정 결과의 실제 발표 직후 검토하며, 날짜 도래만으로 진입을 허용하지 않는다. 발표가 확인되지 않거나 핵심 조건 공백이 남으면 대기한다. / 207940.KS는 사건 검토 후 새 일봉의 1395000~1411000원 시험, 1411000원 이상 종가 회복, 다음 실제 거래일 재시험 지지를 순서대로 확인한다.","risk_condition_ko":"1,395,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"011200.KS","display_name":"011200","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":23500.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":23368.89077921624,"relative_volume":0.8951568696682316,"spread_bps":21.253985122210413,"day_high":23550.0,"day_low":23000.0,"execution_condition_ko":"2026-10-30 이후 완료된 정규장 가격을 확보하고 기존 매도 조건 충족 여부부터 확인한다. / 22650–22800원 시험과 22800원 이상 회복 종가 이후 바로 다음 검증 정규장의 22650–22700원 기회를 관찰한다.","risk_condition_ko":"22,650 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":490000.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":497036.177244433,"relative_volume":2.772575250861805,"spread_bps":10.198878123406425,"day_high":506000.0,"day_low":488000.0,"execution_condition_ko":"531000~541000원 재시험, 541000원 이상 종가 회복과 다음 실제 정규장 지지 유지. 후속 주문 직전에도 지지 실패로 바뀌지 않았는지 재확인한다. / 최초 진입 전 공식 자금 여력과 계좌 위험을 확인한다. 지속적인 현금흐름 회복은 후속 증액에 더 엄격하게 적용한다.","risk_condition_ko":"527,000 이하 하락, 종가 확인 후 (매도에 거래량 확인을 요구하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"028670.KS","display_name":"028670","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":5690.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":5695.689807608822,"relative_volume":0.6648583700537678,"spread_bps":17.559262510974538,"day_high":5780.0,"day_low":5560.0,"execution_condition_ko":"5600~5630원 방어와 5630원 이상 종가를 연속된 두 실제 거래일에서 확인한다. 이후 재접근 때도 최신 지지·악재·호가를 다시 확인하며 과거 신호를 무기한 재사용하지 않는다. / 공식 자료에서 통화·단위·기간, 사용 제한 없는 현금, 가까운 리스·차입 만기, 필수 투자와 이를 충당할 자금원을 확인한다. 한 분기 현금흐름이 음수라는 이유만으로 자동 배제하지 않지만 부족분의 조달 근거가 없으면 매수하지 않는다.","risk_condition_ko":"5,600 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"017900.KS","display_name":"017900","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":9520.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":9585.586251711822,"relative_volume":23.326795461215234,"spread_bps":31.529164477141357,"day_high":9900.0,"day_low":9040.0,"execution_condition_ko":"2026-10-30보다 최신인 일관된 일봉 가격·거래량을 확보하고 관측 시각, 거래일 여부, 실제 거래 가능 상태를 확인한다. / 8,530–8,633 지지와 8,787 초과 종가, 다음 확인된 정규장의 지지 유지를 관찰한다. 이 조건은 재평가 계기이며 자동 매수가 아니다.","risk_condition_ko":"8,530 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"072950.KQ","display_name":"072950","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":13920.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":14158.47713943945,"relative_volume":2.43394558947704,"spread_bps":7.19165767709457,"day_high":14390.0,"day_low":13820.0,"execution_condition_ko":"2026-11-03 판단에 사용된 마지막 신뢰 가능한 일봉은 2026-10-30이다. 이후 실제 완료된 모든 정규장 자료, 거래소 일정과 현재 경고·거래제한 상태를 확인한다. 실행 시계만으로 개장이나 조건 충족을 추정하지 않는다. / 야간 요약 14090원과 마지막 분봉 종가 14640원이 충돌한다. 어느 값도 현재 정규장 가격이나 지지이탈의 증거로 사용하지 않는다.","risk_condition_ko":"14,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":191600.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":191049.01517124625,"relative_volume":2.364216034276737,"spread_bps":5.217845030002609,"day_high":193300.0,"day_low":187500.0,"execution_condition_ko":"189985~190500원 재시험 후 190500원 이상 종가와 다음 실제 정규 거래일 지지 유지: 기술적 재심사 조건이며 현재 매수 허용 신호는 아니다. / 원문 재무·정정 공시·가까운 차입 만기와 상환 재원 확인 및 현실적 첫 저항까지 순보상/위험 1.5배 이상인 새 구조 확인: 소액 진입 계획을 새로 심사한다.","risk_condition_ko":"187,700 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"017670.KS","display_name":"017670","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":75900.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":75935.37050934839,"relative_volume":1.7428878039448332,"spread_bps":13.166556945358789,"day_high":76700.0,"day_low":74800.0,"execution_condition_ko":"위험 대응 조건: 76,600 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"76,600 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010170.KQ","display_name":"010170","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":13420.0,"market_data_asof":"2026-11-04T09:20:00+09:00","session_vwap":13644.908066235133,"relative_volume":1.816609009201815,"spread_bps":7.4487895716946,"day_high":13830.0,"day_low":13410.0,"execution_condition_ko":"위험 대응 조건: 13,590 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"13,590 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T09:20:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T09:22:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-03T14:37:22.827855+09:00",
  "as_of": "2026-11-03T14:34:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
