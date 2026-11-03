# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-03T15:23:19.537608+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261104T002021_local-freshness-us-overlay",
  "producer_finished_at": "2026-11-04T00:22:16.109620+09:00",
  "analysis_run_id": "20261102T185558_local-scheduler-us-full",
  "analysis_completed_at": "2026-11-02T22:27:07.024446+09:00",
  "analysis_trade_date_oldest": "2026-10-30",
  "analysis_trade_date_latest": "2026-10-30",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-03T10:21:00-05:00",
  "market_data_latest_at": "2026-11-03T15:21:37+00:00",
  "market_data_status": "FRESH"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-04T00:02:07.346791+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-04T00:02:07.346791+09:00",
    "run_started_at": "2026-11-04T00:01:27.912713+09:00",
    "run_finished_at": "2026-11-04T00:02:16.028704+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23664119,
    "total_market_value_krw": 22893684,
    "total_unrealized_pnl_krw": -770435,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 108165,
    "total_equity_krw": 23978581
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 546685,
      "current_price_krw": 542038,
      "market_value_krw": 6504466,
      "unrealized_pnl_krw": -55759
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 293015,
      "current_price_krw": 293611,
      "market_value_krw": 3229731,
      "unrealized_pnl_krw": 6559
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 425001,
      "current_price_krw": 373394,
      "market_value_krw": 2240368,
      "unrealized_pnl_krw": -309641
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1883756,
      "current_price_krw": 1761202,
      "market_value_krw": 1761202,
      "unrealized_pnl_krw": -122554
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 267779,
      "current_price_krw": 279102,
      "market_value_krw": 1674614,
      "unrealized_pnl_krw": 67936
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 557048,
      "current_price_krw": 526986,
      "market_value_krw": 1580958,
      "unrealized_pnl_krw": -90186
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1475824,
      "current_price_krw": 1215844,
      "market_value_krw": 1215844,
      "unrealized_pnl_krw": -259980
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 134785,
      "current_price_krw": 134690,
      "market_value_krw": 1212210,
      "unrealized_pnl_krw": -863
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 365306,
      "current_price_krw": 445439,
      "market_value_krw": 890879,
      "unrealized_pnl_krw": 160266
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1422815,
      "current_price_krw": 1917757,
      "market_value_krw": 836266,
      "unrealized_pnl_krw": 215826
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 664069,
      "current_price_krw": 551372,
      "market_value_krw": 551372,
      "unrealized_pnl_krw": -112697
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 570763,
      "current_price_krw": 446418,
      "market_value_krw": 446418,
      "unrealized_pnl_krw": -124345
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 136484,
      "current_price_krw": 104490,
      "market_value_krw": 417962,
      "unrealized_pnl_krw": -127976
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 348445,
      "current_price_krw": 331394,
      "market_value_krw": 331394,
      "unrealized_pnl_krw": -17051
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":332.36,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":329.2110158521643,"relative_volume":2.340442242397991,"spread_bps":2.1061182735845585,"day_high":334.5,"day_low":325.33,"execution_condition_ko":"지지 일봉과 다음 실제 거래 세션 확인이 끝난 뒤에도 338.70~339.27이 제공되는지 점검한다. 먼저 상승하면 추격하지 않는다. / 348.91~349.19와 351.43~351.73의 저항 반응을 관찰한다. 351.73 위에는 제공된 목표가가 없으므로 새로운 보상위험 평가가 필요하다.","risk_condition_ko":"338.7 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":219.49,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":219.17099083144893,"relative_volume":1.1777533683406451,"spread_bps":0.9112447603430941,"day_high":219.68,"day_low":218.55,"execution_condition_ko":"217.13~217.36 지지 시험, 217.36 이상 종가 회복, 다음 실제 거래일 지지·반등, 217.13~217.20 재접근 및 비용 후 보상·위험비율 1 초과를 순서대로 확인한다. / 216.03~216.26 회복 실패 시 신규 진입을 보류하고 214.72 종가 이탈 여부를 점검한다. 감시가격 도달과 매도 조건 충족을 구분한다.","risk_condition_ko":"214.72 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":405.04,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":405.1702560245867,"relative_volume":0.7643230180489614,"spread_bps":7.898699182978135,"day_high":408.08,"day_low":403.15,"execution_condition_ko":"398.65–400.12의 새로운 시험, 400.12 초과 종가와 다음 거래일 지지 확인을 순서대로 점검한다. 이후 비용 조정된 400.12–402.50에서만 소액 진입을 검토한다. / 410.22–418.09의 매물 부담을 점검한다. 418.09 회복만으로 전체 비중 진입을 허용하지 않는다.","risk_condition_ko":"398.65 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":100.4344,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":100.43521181638471,"relative_volume":1.3859167539324064,"spread_bps":0.9956688405427296,"day_high":100.44,"day_low":100.43,"execution_condition_ko":"2026-10-30 일별 가격과 2026-11-02 장전 가격, 상충하는 이동평균의 조정 기준을 먼저 대조한다. 공격적 분석가가 언급한 과거 가격 강세만으로 진입 가치를 인정하지 않는다. / 경제성 검증 후 종가 100.44 초과와 다음 확인된 거래일의 하단 100.42·상단 100.44 지지 재시험을 관찰한다.","risk_condition_ko":"100.42 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1423.005,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":1426.0147388140047,"relative_volume":0.7994440167970349,"spread_bps":10.611272544562011,"day_high":1436.9995,"day_low":1393.6085,"execution_condition_ko":"새 정규장 종가가 하단 1391.31, 상단 1408.36 안에서 안정된 뒤 다음 정규장 지지를 확인한다. 범위 밖 가격은 추격하지 않는다. / 1449.68은 관찰 저항이자 돌파 재평가선이다. 돌파와 재시험 성공만으로 자동 추가 매수하지 않는다.","risk_condition_ko":"1,330 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":278.6599,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":279.08539246886556,"relative_volume":1.198778392001103,"spread_bps":1.4353895288341216,"day_high":281.36,"day_low":277.56,"execution_condition_ko":"276.92 주변의 확인된 정규장 종가와 283.14~288.33 반등 실패를 감시한다. 현재 어느 추가 감축 조건도 충족됐다고 단정하지 않는다. / 288.33 상향 종가 이후 다음 세션 지지 또는 재돌파를 확인한다. 공시 검증과 새로운 손익비 평가 전에는 조건부 시험 매수도 승인하지 않는다.","risk_condition_ko":"276.92 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":1326.595,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":1310.6554332120058,"relative_volume":0.9460592721011396,"spread_bps":30.385396913959354,"day_high":1331.3654,"day_low":1275.75,"execution_condition_ko":"2026-10-30 이후 완료 일봉과 기존 감축 기록을 확인한다. 새 회복 증거가 있으면 감축 필요성을 재평가하되 지연된 장전 관측만으로 기존 신호를 취소하지 않는다. / 1217.41–1224.14의 종가 회복과 후속 지지를 관찰한다. 이 조건만으로 매수하지 않는다.","risk_condition_ko":"1,248.74 이상 도달, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":911.75,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":904.3557408037842,"relative_volume":1.0775131402620328,"spread_bps":14.707819291390788,"day_high":916.01,"day_low":882.0,"execution_condition_ko":"검증된 일봉 종가가 886.61을 넘고 다음 확인된 거래일에 883.45–886.61 지지 여부를 점검한다. 이는 자동 매수가 아닌 재평가 조건이다. / 899.33과 914.88을 순차 저항으로 확인한다. 934.50–943.76 회복과 유지 시 기술적 근거가 개선되지만 신규 매수에는 별도 판단이 필요하다.","risk_condition_ko":"844.08 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":207.8504,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":207.70024106222772,"relative_volume":1.0972145394694306,"spread_bps":1.9242795978251812,"day_high":209.14,"day_low":205.93,"execution_condition_ko":"204.09~204.64달러 지지 참고 구간과 200.92달러 무효화 기준을 최신 일별 자료로 점검한다. 이동평균 갱신을 이유로 기존 손절을 낮추지 않는다. / 210.18달러 종가 회복과 다음 확인된 거래일의 지지 유지는 재검토 조건이지 자동 매수 조건이 아니다. 212.08~213.66달러의 가까운 저항을 함께 평가한다.","risk_condition_ko":"210.18 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":409.445,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":409.73206378919326,"relative_volume":0.8174894274532967,"spread_bps":28.587135788895388,"day_high":418.1679,"day_low":396.5206,"execution_condition_ko":"413.00 재탈환과 424.13~426.69 상단 위 일봉 마감은 초기 안정 신호로만 관찰한다. / 439.50~441.08 회복·지지와 408.72 하회 종가를 점검한다. 현재 장중 관측값으로 당일 종가 조건이 충족됐다고 판단하지 않는다.","risk_condition_ko":"439.5 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":392.745,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":388.5665670733313,"relative_volume":0.9812779607189703,"spread_bps":19.84328889793501,"day_high":393.98,"day_low":376.56,"execution_condition_ko":"주문 전 실제 거래일·거래 상태·정규 거래시간 및 최신 실행 가능 호가를 별도로 확인한다. 2026-11-02 미국 동부시간 05:34:44의 판단 시계는 거래 가능 여부나 진입 충족을 입증하지 않는다. / 364.84–366.11을 우선 감시하고 그 아래에서는 358.51–362.49와 기존 손절 기준에 따라 방어를 강화한다.","risk_condition_ko":"385.96 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":333.055,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":332.23411801731584,"relative_volume":0.805099979190864,"spread_bps":5.704763477503649,"day_high":335.74,"day_low":326.605,"execution_condition_ko":"319.30~321.02 지지 관찰과 319.30 아래 종가 이탈을 구분한다. / 331.98~332.26 회복은 초기 반등 관찰에만 사용하고 신규매수 승인으로 해석하지 않는다.","risk_condition_ko":"319.3 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":246.98,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":247.54698523051502,"relative_volume":0.8106716507559647,"spread_bps":1.6196299145653508,"day_high":249.82,"day_low":245.89,"execution_condition_ko":"일봉 종가 243.79 상회 후 다음 확인된 거래일에 241.24–243.79 지지 유지: 자동 매수나 기계적인 추가 매도 대신 배분 판단을 재평가한다. / 246.45–250.73 회복 후 254.28 위 안착: 기술적 추세 복구 근거가 강화된다.","risk_condition_ko":"243.4 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":77.73,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":77.88686063553293,"relative_volume":0.650261508487935,"spread_bps":1.2865873271154864,"day_high":78.0805,"day_low":77.7,"execution_condition_ko":"다음 확인된 거래일 이후 일봉과 거래량을 갱신하고 78.06 및 78.63–79.19에서 회복 유지와 반락을 구분한다. / 새 매수 검토 시 가장 가까운 신뢰할 만한 저항까지 비용 후 보상 대비 위험을 다시 계산한다. 2:1은 선별 조건이지 수익성의 보장이 아니다.","risk_condition_ko":"78.63 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"SELL","strategy_ko":"매도·청산 검토","last_price":178.62,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":178.66850220264317,"relative_volume":0.660168602265552,"spread_bps":3.3592743967288423,"day_high":180.3,"day_low":177.8,"execution_condition_ko":"위험 대응 조건: 184.59 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"184.59 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"투자 근거 무효화","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":true,"action_status":"ACTION_SIGNAL_PRESENT","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"UNH","display_name":"UNH","is_held":false,"strategy_code":"SELL","strategy_ko":"매도·청산 검토","last_price":399.215,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":398.9509094214854,"relative_volume":0.3673944609341255,"spread_bps":7.5174781366680365,"day_high":402.08,"day_low":397.01,"execution_condition_ko":"위험 대응 조건: 404.31 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"404.31 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"투자 근거 무효화","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":true,"action_status":"ACTION_SIGNAL_PRESENT","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":206.88,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":207.03282507412115,"relative_volume":0.3893299140863187,"spread_bps":14.500459181206582,"day_high":208.21,"day_low":205.06,"execution_condition_ko":"2026-11-13T23:59:59-05:00까지 실제 거래일 기준으로 검토한다. 최초 활성화는 지지 확인 일봉의 다음 실제 거래일부터이며, 후속 진입 조건이 기한 안에 충족되지 않으면 미체결 계획을 종료한다. 자동 연장하거나 다음 세션으로 이월하지 않는다. / 208.02~208.50 이탈 후 회복 실패는 경고다. 해당 구간 바로 아래에 새 기계적 손절을 설정하지 않는다.","risk_condition_ko":"202.19 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":420.035,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":420.3730929658908,"relative_volume":0.7395256926967181,"spread_bps":5.714829983808198,"day_high":423.364,"day_low":418.34,"execution_condition_ko":"2026-10-30을 가격 기준일로 유지하고, 새 일봉으로 414.34–417.00 저항과 410.54–411.82 초기 지지를 점검한다. / 403.46–404.98의 이동평균 기반 구간을 갱신한다. 단순 접촉은 매수 신호가 아니며 낮아진 평균으로 고정 손절을 대체하지 않는다.","risk_condition_ko":"403.46 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":288.955,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":289.4273803748226,"relative_volume":0.5469525577900959,"spread_bps":4.4988147353484145,"day_high":291.322,"day_low":286.9063,"execution_condition_ko":"290.79–292.67은 첫 지지 관찰 구간일 뿐 승인된 매수 구간이 아니다. 285.35–286.98에서만 완전한 확인 절차와 비용 후 최소 2배 보상·위험비를 평가한다. / 298.74–300.00 저항을 관찰한다. 300 초과 종가와 후속 지지는 재검토 사유지만 검증된 상위 목표가 없어 자동 추가 매수 조건은 아니다.","risk_condition_ko":"285.35 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1020.35,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":1028.096131584222,"relative_volume":0.8318820106688655,"spread_bps":5.779469170450572,"day_high":1034.7699,"day_low":1020.35,"execution_condition_ko":"993–994의 새 일봉 회복과 다음 정규장 지지 확인을 감시한다. 실행가는 994를 넘지 않아야 하며 비용 차감 후 보상 대비 위험도 통과해야 한다. / 1000–1006.56은 초기 지지 관찰 구간일 뿐, 유지된다는 이유만으로 최초 편입을 실행하지 않는다.","risk_condition_ko":"993 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":99.0,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":98.74903485023796,"relative_volume":0.14357688937237814,"spread_bps":3.030762236702645,"day_high":99.14,"day_low":98.17,"execution_condition_ko":"94.41~94.96 지지 테스트와 종가 확인 이후 다음 거래일 지속 여부를 관찰한다. 최초 체결 범위는 94.41~94.70이다. / 96.89~97.20 공급 압력과 98.09 돌파 후 지지 전환을 구분해 관찰한다. 확인 과정에서 체결가가 94.70을 넘으면 기존 계획으로 추격하지 않는다.","risk_condition_ko":"94.41 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"RTX","display_name":"RTX","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":203.59,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":202.9696065500986,"relative_volume":0.4050662588933161,"spread_bps":12.281089578267384,"day_high":203.88,"day_low":201.65,"execution_condition_ko":"최초 활성화에는 2026-11-02 이후 적격 일봉과 그다음 검증된 정규장의 확인이 필요하다. 지연된 장전 관측이나 2026-10-30 종가로 이를 대체하지 않는다. 특정 다음 거래일은 거래 일정 확인 전 단정하지 않는다. / 지지 재시험 후 실제 매수가가 194.40 이상이고 194.80에서 주당 추정 왕복비용을 차감한 값 이하인지 확인한다. 순보상/위험비율 1.5 미달, 비용 확인 불가 또는 매수 구간 부재 시 계속 대기한다.","risk_condition_ko":"193.5 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"NEE","display_name":"NEE","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":83.845,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":83.98967936619032,"relative_volume":0.5548778762323469,"spread_bps":1.1926769634433665,"day_high":85.0079,"day_low":83.795,"execution_condition_ko":"NEE의 새로운 82.40~82.90 재시험과 종가 82.84 이상 회복을 확인한다. 눌림 중 매도 거래량 감소는 보조 근거이며 저가 접촉만으로 진입하지 않는다. / 회복 신호 다음 실제 거래 세션의 82.40 지지, 82.40~82.90 체결 기회, 최소 차환 검증 및 계좌 잔여 위험예산을 함께 확인한다.","risk_condition_ko":"81.33 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":555.52,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":553.8396451570665,"relative_volume":0.5726880168782419,"spread_bps":3.240674060203622,"day_high":556.0,"day_low":551.81,"execution_condition_ko":"537.33–539.23 시험과 539.23 이상 종가, 다음 확인된 거래일의 지지 유지 및 종가를 순차 확인한다. 단순 접촉은 매수 신호가 아니다. / 548.31–550.47에서 재차 거절되는지, 돌파 후 지지로 전환되는지 관찰한다.","risk_condition_ko":"537.33 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":647.9,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":650.4553375495796,"relative_volume":0.6715060508355795,"spread_bps":6.329358187641821,"day_high":654.39,"day_low":646.66,"execution_condition_ko":"새 정규장 종가 633.34 이상과 다음 실제 거래일의 633.29~633.34 지지 재시험을 확인한다. 해당 범위 밖에서는 추격하지 않는다. / 644.24 접근 시 저항·이익 보호 조건을 재평가하고 종가 돌파와 다음 거래일 지지 유지를 관찰한다. 관측되지 않은 상승 목표로 손익비를 부풀리지 않는다.","risk_condition_ko":"633.29 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"SPG","display_name":"Simon Property Group","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":220.27,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":220.80194828280912,"relative_volume":0.7371338118565485,"spread_bps":8.170676350430249,"day_high":222.35,"day_low":219.75,"execution_condition_ko":"213.75–215.36 시험, 적격 반전 종가, 다음 정규장 지지 유지 순서를 확인한다. 비용 반영 후에도 유효한 213.75–214.20 이내 가격이 없으면 거래를 건너뛴다. / 218.40 종가 돌파와 다음 정규장 지지를 관찰하되 현재 승인 범위를 넘어 추격하지 않는다.","risk_condition_ko":"210.48 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"SMCI","display_name":"Super Micro Computer","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":31.685,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":31.639130939476082,"relative_volume":1.2779786381099596,"spread_bps":3.156067539845846,"day_high":32.28,"day_low":30.935,"execution_condition_ko":"32.58~32.69의 종가 유지와 31.33~31.43 재시험 여부를 관찰한다. 장중 저점만으로 종가 기준 이탈을 확정하지 않는다. / 34.51 위 종가와 다음 거래일 34.33~34.51 지지를 확인하면 약세 판단과 추가 감축 필요성을 재평가한다. 자동 매수하지 않는다.","risk_condition_ko":"32.58 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":161.9,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":162.1178028193439,"relative_volume":0.4359392807586117,"spread_bps":3.705762460626414,"day_high":163.19,"day_low":161.6225,"execution_condition_ko":"158.42–159.23 시험, 159.23 초과 종가, 다음 확인된 거래일 지지를 순서대로 관찰한다. 159.00 이하 실행 가능성과 비용 후 보상 대비 위험 2 이상이 사라지면 추격하지 않는다. / 164.50·165.75에서는 최신 정규장 체결 가능 가격으로 이익실현 조건을 확인하고 이미 집행한 물량을 제외한다.","risk_condition_ko":"164.5 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":226.31,"market_data_asof":"2026-11-03T10:21:00-05:00","session_vwap":226.0597601602631,"relative_volume":0.5331625281513913,"spread_bps":3.5341933203751763,"day_high":227.56,"day_low":224.4627,"execution_condition_ko":"위험 대응 조건: 236.48 이상 도달, 장중 확인 시 이익실현성 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"236.48 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-03T10:23:00-05:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"KVUE","display_name":"KVUE","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":19.31,"market_data_asof":"2026-11-03T15:21:37+00:00","session_vwap":null,"relative_volume":0.0,"spread_bps":129.29919834497025,"day_high":19.31,"day_low":19.31,"execution_condition_ko":"핵심 원공시 검증과 19.20~19.25 시험 후 19.25 이상 종가, 다음 거래가능 세션 재지지가 함께 충족되는지 확인 / 19.50~19.60 저항에서의 가격 반응과 실제 비용 차감 후 보상 여지 점검; 회복만으로 증액하지 않음","risk_condition_ko":"19.2 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"핵심 데이터 누락: VWAP","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-11-03T15:23:37+00:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:news_halt_status","feed_limited:orderbook"],"provider_blockers":null}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-03T23:09:46.922579+09:00",
  "as_of": "2026-11-02T15:50:31+00:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
