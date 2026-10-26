# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-26T00:57:21.311205+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261026T081100_local-scheduler-kr-full",
  "producer_finished_at": "2026-10-26T09:36:56.827168+09:00",
  "analysis_run_id": "20261026T081100_local-scheduler-kr-full",
  "analysis_completed_at": "2026-10-26T09:02:33.309877+09:00",
  "analysis_trade_date_oldest": "2026-10-23",
  "analysis_trade_date_latest": "2026-10-23",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-23T20:00:00+09:00",
  "market_data_latest_at": "2026-10-23T20:00:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-26T09:02:56.577422+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-26T09:02:56.577422+09:00",
    "run_started_at": "2026-10-26T08:11:00.820417+09:00",
    "run_finished_at": "2026-10-26T09:36:56.827168+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 8342720,
    "total_unrealized_pnl_krw": -6601516,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 9319372
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1288000,
      "market_value_krw": 2576000,
      "unrealized_pnl_krw": -2859000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 215000,
      "market_value_krw": 2150000,
      "unrealized_pnl_krw": -1173851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 280000,
      "market_value_krw": 1400000,
      "unrealized_pnl_krw": -674643
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 153100,
      "market_value_krw": 612400,
      "unrealized_pnl_krw": -362600
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 455500,
      "market_value_krw": 455500,
      "unrealized_pnl_krw": -697500
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 16640,
      "market_value_krw": 299520,
      "unrealized_pnl_krw": -268795
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 186700,
      "market_value_krw": 186700,
      "unrealized_pnl_krw": -187467
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 60100,
      "market_value_krw": 180300,
      "unrealized_pnl_krw": -119700
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 173800,
      "market_value_krw": 173800,
      "unrealized_pnl_krw": -108534
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 119400,
      "market_value_krw": 119400,
      "unrealized_pnl_krw": -52900
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 42150,
      "market_value_krw": 84300,
      "unrealized_pnl_krw": -33900
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 58400,
      "market_value_krw": 58400,
      "unrealized_pnl_krw": -54531
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 46400,
      "market_value_krw": 46400,
      "unrealized_pnl_krw": -8100
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1263000.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":1230863.7330056026,"relative_volume":22.65382196809118,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"000660.KS 거래일·정규장 여부, 거래 제한, 호가 신선도와 조정가격 비교 가능성을 먼저 확인한다. 현재 발동된 주문은 없다. / 1297000원 돌파와 1284000~1297000원 재시험, 현재 정규장의 거래량가중평균가격 및 동시간대 상대거래량을 관찰하되 새 매수 승인으로 간주하지 않는다.","risk_condition_ko":"1,223,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":213500.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":210382.9514104199,"relative_volume":17.622098730767938,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"005930.KS 203500~204500원에서는 저점 회복과 높아지는 단기 저점을 관찰한다. 지지 가격 도달만으로 매수하지 않는다. / 005930.KS 215500~219500원 반등 저항 회복 실패는 전술 물량 위험 축소 조건이다. 양 끝 가격을 별개의 중복 매도 신호로 사용하지 않는다.","risk_condition_ko":"203,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":154600.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":151939.8246674439,"relative_volume":29.809976321039663,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"147000~150000원 재시험 후 회복, 매도량 둔화와 당일 거래량가중평균가격 회복을 관찰한다. 접촉만으로 매수하지 않는다. / 157400원 돌파·재시험 지지를 확인하되 161400~164600원 가까운 저항까지의 비용 후 보상·위험이 2배 미만이면 진입하지 않는다.","risk_condition_ko":"147,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":470000.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"267260.KS의 실제 거래일·정규장·호가 시각·스프레드·거래량과 검증된 5분봉, 당일 거래량가중평균가격을 확인한다. / 483500원 회복·재지지, 당일 거래량가중평균가격 상회와 동시간대 누적 상대거래량 1.2 이상을 함께 관찰한다. 충족하더라도 현재 매수 주문이 활성화되지는 않는다.","risk_condition_ko":"448,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":61300.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":60934.61697896633,"relative_volume":15.259922050269203,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"59600원 방어와 저점 상승을 확인한다. 지지 실패는 신규 매수 차단·손실 통제 조건이며 자동 저가매수 신호가 아니다. / 62800원 돌파·재지지, 신선한 당일 거래량가중평균가격 상회, 검증된 동시간 누적 상대거래량 1.2 이상을 관찰한다. 현재 손익비는 부족하므로 새 가격구조에서 비용 후 손익비를 다시 계산한다.","risk_condition_ko":"59,600 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":172600.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":173311.89084140543,"relative_volume":14.07624091520051,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 정규장 가격으로 171900원과 171100원의 유지·이탈·회복을 구분한다. 핵심 지지 아래 다음 지지는 제공 자료로 확정할 수 없다. / 175400~176400원 회복과 재지지를 초기 개선 신호로 관찰하되 신규 매수를 자동 승인하지 않는다.","risk_condition_ko":"171,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":188500.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":187656.4961614978,"relative_volume":20.146747377955066,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"거래일·정규장·거래정지 여부와 신선한 호가를 확인한다. 188500원은 2026-10-23 참고 종가이며 현재가가 아니다. 2026-10-25 보도의 가격 반응도 미확인이다. / 192200원 돌파·재시험 지지, 당일 거래량가중평균가격 상회와 동시간대 상대거래량 1.2배 이상을 함께 관찰한다. 1.2배는 제안 기준이며 산식 불명인 20.15배는 사용하지 않는다. 관찰 조건 충족만으로 현재 매수가 활성화되지 않는다.","risk_condition_ko":"182,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":124200.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"353200.KS 최신 정규장 자료의 거래일·시세 시각·세션·봉 간격·표시가격 정합성을 우선 확인한다. / 353200.KS의 127500원 돌파·재시험 방어, 당일 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상을 동시 확인한다. 이는 재검토 신호이며 자동 매수 신호가 아니다.","risk_condition_ko":"116,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":16680.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":16689.193568286966,"relative_volume":18.310747338913732,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단시계는 2026-10-26T05:04:50.114332+09:00이다. 이는 실제 개장·휴장·조기종료·호가 신선도를 증명하지 않으므로 거래일 달력, 거래구분, 체결시각, 봉 간격과 최신 호가를 별도로 확인한다. / 2026-10-23 야간자료, 약 56.8시간 지연됐다고 보고된 장중자료, 산식 미검증 상대거래량 18.31 및 과거 거래량가중평균가격은 당일 신호에서 제외한다.","risk_condition_ko":"16,450 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":58900.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":58882.84527039357,"relative_volume":21.447861400721255,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단 시각은 2026-10-26T05:27:58.760887+09:00이고 일봉 기준일은 2026-10-23이다. 이 시각만으로 정규장 일정·휴장 여부·거래 상태·시세 신선도를 확정하지 않는다. 최신 자료 확인이 우선이며 활성 조건부 주문이나 만료시각은 없다. / 마지막 장중 봉 표시는 2026-10-23 20:00이며 요청 5분봉과 반환 1분봉이 불일치한다. 과거 상대거래량 21.45와 거래량가중평균가격 58882.85원은 현재 신호에서 제외한다. 일거래량의 20일 평균 대비 약 1.07배도 매도 소진 확인은 아니다.","risk_condition_ko":"57,700 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":42850.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단 시계는 2026-10-26T05:53:19.580991+09:00이고 가격 기준일은 2026-10-23이다. 실제 거래일·정규장·주문 가능 상태와 체결·호가 신선도는 별도 확인한다. 세부 봉과 요약값이 불일치하는 지연 자료로 현재 조건을 판정하지 않는다. / 43,800 회복, 43,200~43,800 재시험 지지, 거래량가중평균가 상회, 동시간대 상대거래량 1.2 이상, 비용 차감 후 손익비 2배 이상과 계좌 위험여력을 함께 확인한다. 상대거래량 기준은 제안 운용규칙이며 일간 평균 대비 거래량과 혼용하지 않는다.","risk_condition_ko":"41,700 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":284500.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"현재 명시된 위험 행동 없음","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":47700.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"현재 명시된 위험 행동 없음","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":490500.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"006400.KS의 실제 거래일·정규장·거래정지 상태와 최신 호가 시각부터 확인한다. 지연 요약가격 490500원과 마지막 분봉 484500원의 불일치를 해소하기 전 장중 판단에 사용하지 않는다. / 006400.KS의 475000~477500원 방어·재시험과 509000~512000원 회복·지지 전환을 확인한다. 향후 매수 재검토에는 실시간 거래량가중평균가격 상회와 동일 시간대 상대거래량 1.2 이상이 필요하다.","risk_condition_ko":"503,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003010.KS","display_name":"003010","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":9870.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"003010.KS의 9140~9376.2원 접근 후 최신 5분봉 저점 안정·반등·거래량 회복을 관찰한다. 단순 접촉은 매수 신호가 아니다. / 10044.3원과 10350원 회복·재시험 이후 10450~10510원 및 10860원 공급 소화를 확인한다. 가격 회복과 유리한 매수 손익비는 별개다.","risk_condition_ko":"10,350 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":128800.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 정규장 자료로 128100~128300원 방어와 130500~130600원 회복·재지지, 당일 거래량가중평균가격 상회를 확인한다. / 134100~134450원 저항대 돌파·종가 안착과 실제 다음 거래일 재지지를 확인한다. 가까운 저항까지 비용 후 보상·위험이 부족하면 계속 대기한다.","risk_condition_ko":"130,535 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":189400.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"033780.KS 공식 거래일·정규장·휴장 여부와 최신 가격시각·호가·당일 5분봉을 확인한다. 이전 거래일 1분봉이나 지연자료의 거래량 0은 당일 신호로 쓰지 않는다. / 033780.KS 188200~188800원 방어 후 189400원 회복·유지, 당일 거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상을 관찰한다. 손익비 미달이면 매수하지 않는다.","risk_condition_ko":"188,200 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"009150.KS","display_name":"삼성전기","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1122000.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"009150.KS의 공식 거래일정·정규장 구분·체결시각·호가·일봉 가격과 기업행동을 먼저 대조한다. 지연 자료의 거래량 0을 수요 부재로 해석하지 않는다. / 009150.KS의 1135000~1170000 회복 후 두 개의 완료된 5분봉 재시험 지지, 당일 거래량가중평균가격 상회와 동일 시각 기준 상대거래량 1.2 이상을 관찰한다. 기준일 거래량 약 1.09배와 상대강도지수 32.40만으로 반전을 확정하지 않는다.","risk_condition_ko":"1,048,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"131290.KQ","display_name":"티에스이","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":257000.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단시각은 2026-10-26T06:44:31.206574+09:00이다. 연구일과 현지 날짜는 같지만 거래일·정규장 운영·최신 체결 시각은 별도 확인 대상이다. 10:30은 서울 시간 기준 최초 시험 진입 검토시각이지 만료시각이 아니다. 확인된 만료시한이 없어 다음 거래일로 연장하거나 주문을 활성화하지 않는다. / 제공된 가격 표시는 2026-10-23 20:00이며 시간대가 미확인이다. 요약가 257000원과 마지막 봉 252000원, 요청 5분봉과 반환 1분봉의 불일치를 해결한다. 현재 가격은 확인할 수 없다.","risk_condition_ko":"265,850 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000100.KS","display_name":"000100","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":84700.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-10-26T07:00:06.830912+09:00 판단시각에도 실제 장 운영, 현재 호가와 신호 충족 여부는 미확인이다. 오래된 거래량 0 관측치를 현재 거래부진이나 상대거래량으로 해석하지 않는다. / 82,800~83,200원 지지 시험 후 83,200원을 회복하고 실제 5분봉 두 개에서 저점이 높아지는지 확인한다. 당일 거래량가중평균가격 지지와 동시간대 상대거래량 1.2 이상에 더해 순보상·위험비와 보유한도가 충족되어야 재검토한다.","risk_condition_ko":"81,779.57 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"064400.KS","display_name":"LG CNS","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":72800.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"거래일 달력·거래 상태와 실제 정규장을 확인하고 최신 체결가, 실제 5분봉, 해당 장 거래량가중평균가격, 동시간대 상대거래량, 호가차와 주문장 유동성을 확보한다. 과거 봉이나 장 시작 전 표시 거래량으로 오늘 조건을 판정하지 않는다. / 71,200~72,040원 지지 관찰과 72,040원 회복·재시험을 점검한다. 74,800~75,000원 저항 돌파도 별도로 관찰하되 현재 제시된 넓은 손절의 돌파 추격은 제외한다.","risk_condition_ko":"71,200 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"036460.KS","display_name":"036460","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":36600.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"036460.KS 최신 가격과 실제 정규장, 거래정지 여부 및 계좌 위험한도를 먼저 확인한다. / 36050~36262원에서 매도 거래량 둔화, 재상승과 거래량가중평균가격 회복을 확인한다. 가격 도달만으로 매수하지 않는다.","risk_condition_ko":"35,550 이하 하락, 종가 확인 후 (거래량 증가를 필수 조건으로 두지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":138100.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"공식 거래일·세션과 최신 정규장 호가·체결·5분봉·장중 거래량가중평균가격·동시간대 상대거래량·변동성완화장치 상태를 먼저 확인한다. 지연 자료를 당일 실행 신호로 사용하지 않는다. / 141700원 위 유효 5분봉 마감·재지지, 장중 거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상을 관찰한다. 충족하더라도 보상구조·공식 실적 일정·위험축소 필요성을 재평가하기 전에는 매수하지 않는다.","risk_condition_ko":"139,760 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003230.KS","display_name":"003230","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1225000.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"거래일·정규장 운영 여부, 최신 체결가격, 호가 간격, 정확한 봉 간격, 거래량가중평균가와 동시간대 상대거래량을 확인한다. 제공된 마지막 시세 시각 2026-10-23T20:00:00+09:00은 2026-10-26의 실행 조건을 입증하지 않는다. / 1,215,000~1,220,000원 지지와 1,191,000~1,203,000원 후속 지지를 관찰하고, 정해진 확인 조건이 충족되면 단계별 위험 축소·손절 규칙을 적용한다.","risk_condition_ko":"1,215,000 이하 하락, 종가 확인 후 (위험 축소에 거래량 증가를 요구하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"018880.KS","display_name":"018880","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":3680.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"원문 재무제표의 통화·단위·보고기간·공개시점·주식기준·해당 예탁증서 전환비율을 검증하고 차입 만기·약정·확약 신용한도를 확인한다. / 2026-10-23 20:00으로 표시된 지연 관찰값을 신선한 정규장 호가와 올바른 5분 봉으로 교체한다. 요약 거래량 0을 수요 부재로 해석하지 않는다.","risk_condition_ko":"3,600 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"396300.KQ","display_name":"396300","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":9210.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":null,"relative_volume":0.0016000218801700385,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"8940원 부근에서 연속 5분봉의 저점 상승과 당일 거래량가중평균가격 회복을 관찰한다. 가격 접촉이나 안정화만으로 매수를 승인하지 않는다. / 8720–8754원 지지구간과 8510원 잔여 전술 청산 기준을 재검증한다.","risk_condition_ko":"8,720 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"411080.KQ","display_name":"411080","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":6090.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 시각이 표시된 가격, 호가차, 체결 유동성, 거래제한, 실제 정규장 운영 여부를 확인한다. 분석 완료만으로 매수 조건이 충족되지는 않는다. / 높아지는 저점과 6380–6420 및 6500–6560 회복·유지 여부를 관찰하고 가까운 저항까지의 비용 후 보상 대비 위험을 다시 계산한다.","risk_condition_ko":"5,954 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"079650.KQ","display_name":"079650","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":7300.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"공식 거래 일정과 경고·정지 상태, 시각이 표시된 실제 체결을 확인한다. 거래량이 없는 오래된 봉은 확인 신호로 인정하지 않는다. / 7,070~7,210 지지대와 7,500~7,645 저항대 재시험을 관찰하고, 실제 장중 거래량가중 평균가격을 별도로 측정한다.","risk_condition_ko":"7,070 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"011200.KS","display_name":"011200","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":22650.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"011200.KS의 연구일은 2026-10-26, 일별 가격 기준일은 2026-10-23이다. 실제 거래소 일정·정규장 여부·휴장 및 조기종료 여부와 신선한 호가를 확인한다. / 판단 시각 2026-10-26T06:17:37.872722+09:00에서 10:30은 가장 이른 검토 시각이지 만료가 아니다. 유효기한은 제공되지 않았으므로 만료나 다음 거래일 이월을 추정하지 않는다.","risk_condition_ko":"22,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":194400.0,"market_data_asof":"2026-10-23T20:00:00+09:00","session_vwap":null,"relative_volume":0.0,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"068270.KS 거래소 달력·세션·최신 시세를 확인하고 일치하는 완성 5분봉·실거래량·거래량가중평균가격·동시간대 상대거래량을 확보한다. / 068270.KS 보유수량·순자산·현금·바이오 집중도와 갭 스트레스를 먼저 점검한다. 한도 초과가 확인되면 신규 매수 대기와 별개로 위험을 축소한다.","risk_condition_ko":"189,800 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-23T20:00:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-23T20:03:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
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
