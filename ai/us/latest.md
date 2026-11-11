# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-11T15:50:53.958543+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261111T205119_local-scheduler-us-full",
  "producer_finished_at": "2026-11-12T00:38:37.166994+09:00",
  "analysis_run_id": "20261111T205119_local-scheduler-us-full",
  "analysis_completed_at": "2026-11-12T00:00:58.774332+09:00",
  "analysis_trade_date_oldest": "2026-11-10",
  "analysis_trade_date_latest": "2026-11-10",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-11T06:50:00-05:00",
  "market_data_latest_at": "2026-11-11T09:30:00-05:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-11T03:35:16.739386+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-11T03:35:16.739386+09:00",
    "run_started_at": "2026-11-11T03:02:25.946492+09:00",
    "run_finished_at": "2026-11-11T03:35:23.304626+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23923536,
    "total_market_value_krw": 22316512,
    "total_unrealized_pnl_krw": -1607024,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 113363,
    "total_equity_krw": 23406487
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 552678,
      "current_price_krw": 529577,
      "market_value_krw": 6354925,
      "unrealized_pnl_krw": -277213
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 296227,
      "current_price_krw": 298864,
      "market_value_krw": 3287504,
      "unrealized_pnl_krw": 29000
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 429660,
      "current_price_krw": 387431,
      "market_value_krw": 2324591,
      "unrealized_pnl_krw": -253371
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1904406,
      "current_price_krw": 1809107,
      "market_value_krw": 1809107,
      "unrealized_pnl_krw": -95299
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 563154,
      "current_price_krw": 476481,
      "market_value_krw": 1429443,
      "unrealized_pnl_krw": -260020
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 270715,
      "current_price_krw": 228123,
      "market_value_krw": 1368741,
      "unrealized_pnl_krw": -255549
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 136263,
      "current_price_krw": 136266,
      "market_value_krw": 1226401,
      "unrealized_pnl_krw": 30
    },
    {
      "ticker": "GEV",
      "name": "GE 버노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1492002,
      "current_price_krw": 1048309,
      "market_value_krw": 1048309,
      "unrealized_pnl_krw": -443693
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 369311,
      "current_price_krw": 471675,
      "market_value_krw": 943350,
      "unrealized_pnl_krw": 204728
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1438411,
      "current_price_krw": 1928368,
      "market_value_krw": 840893,
      "unrealized_pnl_krw": 213652
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 577019,
      "current_price_krw": 443530,
      "market_value_krw": 443530,
      "unrealized_pnl_krw": -133489
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 671349,
      "current_price_krw": 443435,
      "market_value_krw": 443435,
      "unrealized_pnl_krw": -227914
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 137980,
      "current_price_krw": 107974,
      "market_value_krw": 431898,
      "unrealized_pnl_krw": -120025
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 352265,
      "current_price_krw": 364385,
      "market_value_krw": 364385,
      "unrealized_pnl_krw": 12120
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":175.884,"market_data_asof":"2026-11-11T07:35:00-05:00","session_vwap":175.40603153506396,"relative_volume":1.0208926709084492,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"174.69~175.41 회복은 초기 안정 관찰 조건이다. 175.41은 과거 장전 거래량가중평균가격의 정적 참고값이며 최신 값이나 매수 신호가 아니다. / 178.36~179.92 구간 상단 초과 종가와 다음 실제 거래일 지지 또는 재돌파를 관찰한다. 현재 조건부 매수 승인은 없다.","risk_condition_ko":"165.89 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T07:35:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T07:38:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":289.98,"market_data_asof":"2026-11-11T07:15:00-05:00","session_vwap":290.1948709107768,"relative_volume":0.10711469265076988,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"285.68–288.01달러와 276.92–278.80달러 지지 구간을 일봉 종가로 점검한다. / 294.00달러 및 296.49달러 상향 종가는 재평가 신호다. 상대강도지수의 40–50 회복은 보조 증거일 뿐 매수 신호를 대체하지 않는다.","risk_condition_ko":"285.68 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T07:15:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T07:18:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":368.9571,"market_data_asof":"2026-11-11T07:10:00-05:00","session_vwap":365.11687887691807,"relative_volume":0.017938408360692135,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"360.68~362.39 회복, 369.98 상향 종가, 다음 실제 거래일 365.12~369.98 지지 전환을 순서대로 관찰한다. 365.12는 장전 거래량가중평균가격 유래이므로 정규장 자료로 재검증한다. / 375.41~377.07과 383.02~392.51에서 반등 지속성과 거래량을 관찰한다. 상승 확인만으로 가까운 저항까지의 보상/위험이 좋아졌다고 가정하지 않는다.","risk_condition_ko":"344.22 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T07:10:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T07:13:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":357.5,"market_data_asof":"2026-11-11T06:50:00-05:00","session_vwap":358.5614521339908,"relative_volume":0.15270375487134324,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"회복 구간 하단 354.50·상단 362.99: 상단 초과 종가와 다음 거래일 구간 방어를 관찰한다. 자동 매수 조건은 아니다. / 저항 구간 하단 366.62·상단 379.15: 향후 구간 거래 후 366.62 미만 종가는 추가 축소 신호다. 단순 접촉은 거부 확인이 아니다.","risk_condition_ko":"338.91 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T06:50:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T06:53:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":838.7325,"market_data_asof":"2026-11-11T07:15:00-05:00","session_vwap":833.3856144677353,"relative_volume":0.11265679271320306,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"842.00 상회 정규장 종가 후 다음 확인된 거래일에 832.17–833.82 유지 또는 회복과 842.00 재상회를 점검한다. 자동 매수가 아니라 신속한 재평가 신호다. / 이후 정규장 종가가 797.04를 하회하면 추가 감축, 747.00을 하회하면 남은 전술적 보유분 정리 절차를 적용한다.","risk_condition_ko":"797.04 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T07:15:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T07:18:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":80.0001,"market_data_asof":"2026-11-11T07:15:00-05:00","session_vwap":80.12412114656571,"relative_volume":0.0854719275970953,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"79.39~79.47 방어와 이탈 후 회복 실패를 우선 점검한다. 78.63과 77.46은 하방 진행 관찰선이다. / 80.11~80.40 회복 뒤 81.10과 81.78~82.04 저항 통과 여부를 확인한다. 저항 접근만으로 매수하지 않는다.","risk_condition_ko":"79.39 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T07:15:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T07:18:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":346.34,"market_data_asof":"2026-11-11T06:50:00-05:00","session_vwap":346.14617817921373,"relative_volume":0.04071751241322039,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"344.46–346.46 지지시험, 346.46 이상 일봉 마감, 다음 검증 거래일의 지지 확인을 순서대로 관찰한다. 실제 체결가격은 344.46–345.13 이내이면서 비용·갭 여유 반영 손익비 1.5 이상이어야 한다. / 350.69–353.87의 저항 반응과 354.50–355.38 돌파 후보 구간을 관찰한다. 첫 저항에서 매도할 계획으로 바뀌면 진입 손익비도 재계산한다.","risk_condition_ko":"344.46 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T06:50:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T06:53:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":221.25,"market_data_asof":"2026-11-11T07:35:00-05:00","session_vwap":221.3479752011608,"relative_volume":0.013940522916783037,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-11 이후 실제 완료된 거래일에 218.90–219.02 지지를 시험하고 219.02 이상으로 마감하는지 관찰한다. 다음 실제 거래일에도 지지 유지와 219.02 이상 종가가 필요하다. / 221.16–221.90 첫 저항이 상승을 계속 제한하는지 확인한다. 제한한다면 223.50까지의 보상을 가정한 신규 매수를 보류한다.","risk_condition_ko":"218.9 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T07:35:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T07:38:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":271.555,"market_data_asof":"2026-11-11T06:50:00-05:00","session_vwap":271.644395447417,"relative_volume":0.05116582129810778,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"266.14–266.91을 첫 지지로 관찰한다. 종가 266.14 미만은 위험 점검 신호이나 그 자체로 중기 가설의 무효화는 아니다. / 258.53–260.21 시험, 260.21 상회 종가, 다음 거래일 지지 유지의 순서를 확인한다. 허용 첫 매수 범위는 259.00–260.21뿐이다.","risk_condition_ko":"258.53 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T06:50:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T06:53:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.5274,"market_data_asof":"2026-11-11T07:55:00-05:00","session_vwap":null,"relative_volume":0.1958454291185199,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"공식 보유자산·듀레이션·비용·분배일·수익률 산식과 동시점 순자산가치를 확보한다. 표시값 3.64는 검증된 연환산 수익률로 사용하지 않는다. / 동일한 배당·조정 기준의 완료 일봉으로 100.56 회복과 100.53–100.56 재시험을 추적한다. 100.49–100.51과 100.44–100.46은 관찰 구간이지 독립 매수 신호가 아니다.","risk_condition_ko":"100.42 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T07:55:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T07:58:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1420.0,"market_data_asof":"2026-11-11T07:30:00-05:00","session_vwap":1412.9345351043644,"relative_volume":0.03700544912763505,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1290.00–1320.70에서는 단순 가격 접촉이 아니라 일봉 회복과 다음 적격 정규장의 지지 재시험 유지를 관찰한다. 첫 재시험이 확인되지 않으면 새 일봉 확인 순서를 요구한다. / 1387.87–1396.55의 첫 공급대, 1439.73–1455.99와 1479.89–1491.64의 후속 저항에서 수용 또는 거절을 관찰한다. 저항 거절과 추세 둔화가 확인되면 별도 이익실현 판단을 재검토한다.","risk_condition_ko":"1,290 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T07:30:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T07:33:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":345.0,"market_data_asof":"2026-11-11T06:50:00-05:00","session_vwap":343.8695332099233,"relative_volume":0.10986565497469347,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"334.00–336.00은 매수 승인 구간이 아니라 감시용 후보 구간이다. 336.00 이상 마감, 다음 확인된 거래일의 해당 구간 재시험 및 334.00 이상 마감을 순서대로 확인한다. / 기술 조건이 완성돼도 중요 사건 검토와 비용 반영 보상·위험 재평가가 필요하다. 현재 첫 저항 기준 비율 0.70–0.98만으로 최초 매수를 승인하지 않는다. 336.00 위 추격 매수도 승인하지 않는다.","risk_condition_ko":"321.8 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T06:50:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T06:53:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":414.4,"market_data_asof":"2026-11-11T07:55:00-05:00","session_vwap":414.2498427120527,"relative_volume":0.31884620540088726,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-11부터 2026-11-18까지 완료된 일봉과 후속 거래일 지지 시험을 검토한다. 현재 분석 이후의 회복·재시험 완료는 확인되지 않았다. / 395.75–396.66의 초기 경고와 387.20–391.61의 핵심 지지 상태를 감시한다. 412.35–418.50 및 424.37–430.46은 보장된 목표나 적정가치가 아닌 저항 구간이다.","risk_condition_ko":"387.2 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T07:55:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T07:58:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1414.7187,"market_data_asof":"2026-11-11T07:25:00-05:00","session_vwap":1413.06026546778,"relative_volume":0.05960421765875437,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1400.00–1412.00의 첫 지지 여부를 관찰하되 이 구간 유지 자체로 매수하지 않는다. / 1373.51–1378.94 시험, 1378.94 이상 종가 회복, 다음 정규장 방어의 순서를 확인하고 체결 상한 1380.00을 유지한다.","risk_condition_ko":"1,373.51 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T07:25:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T07:28:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":654.76,"market_data_asof":"2026-11-11T08:20:00-05:00","session_vwap":652.1909669947886,"relative_volume":0.9352478539001592,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"제공된 최신 의사결정 시각은 2026-11-11T08:49:33.830023-05:00이다. 11/11 08:20 동부시간의 지연 개장 전 가격 654.76은 정규장 조건 충족 증거가 아니다. 주문 전 실제 거래일 달력·휴장 및 단축 일정·거래 가능 상태·가격 신선도를 확인한다. / 런타임 이후의 정규장 일봉에서 648.24~651.53 재시험과 648.24 이상 회복 마감을 확인하고 다음 실제 거래일의 종가 방어를 점검한다. 이후에도 실제 첫 매수가는 648.24~649.50으로 제한한다.","risk_condition_ko":"648.24 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T08:20:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T08:23:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"KO","display_name":"KO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":95.9,"market_data_asof":"2026-11-11T09:10:00-05:00","session_vwap":95.82022859542809,"relative_volume":0.0709034309850982,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"매 실제 거래일 일봉으로 지지 시험·반등과 다음 세션 종가 확인을 갱신한다. / 가격·핵심 공시·비용 후 손익비·손절 적합성이 모두 충족되고 실제 가격이 94.48~94.90일 때만 소액 시작한다. 구간을 벗어나면 추격하지 않는다.","risk_condition_ko":"94.48 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T09:10:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T09:13:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":578.72,"market_data_asof":"2026-11-11T08:20:00-05:00","session_vwap":577.4950821603156,"relative_volume":0.06593031089642158,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"559.49–565.11 시험, 575.25 초과 회복 종가, 이후 정규장 재시험을 순서대로 확인한다. 재시험 중 지지와 매도위험을 새로 평가하지 못하면 주문하지 않는다. / 574.00–575.25는 위험관리 구간이며 독립적인 얕은 조정 매수 구간이 아니다. 매도 조건이 발생하면 조건부 매수를 중단한다.","risk_condition_ko":"574 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T08:20:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T08:23:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":419.44,"market_data_asof":"2026-11-11T08:50:00-05:00","session_vwap":419.54354795618485,"relative_volume":0.02025465082639875,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단 시각은 2026-11-11T09:11:25.637980-05:00이며 승인 만료 전이다. 이는 거래일·정규장 상태·시세 신선도·진입 충족을 입증하지 않는다. 거래 달력과 실제 거래 가능 여부를 별도 확인한다. / 일봉 근거는 2026-11-10이다. 2026-11-11 08:50 동부시간의 419.44 관측은 지연된 개장 전 자료로 지지 확인이나 실행 호가로 사용하지 않는다.","risk_condition_ko":"416.28 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T08:50:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T08:53:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WMT","display_name":"WMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":124.255,"market_data_asof":"2026-11-11T09:15:00-05:00","session_vwap":124.29539727572292,"relative_volume":0.09861506001273096,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"새 정규장 종가와 다음 거래일 지지 확인을 순서대로 점검한다. 가격이 허용 구간을 벗어나면 추격하지 않고 해당 기회를 보낸다. / 123.78 회복 실패, 123.03 미만 종가 및 122.70 보호손절을 매수 조건과 독립적으로 감시한다. 위험축소에는 신규 매수용 현금이나 상승 거래량 확인이 필요하지 않다.","risk_condition_ko":"123.78 이하 하락, 장중 확인 시 (위험축소에 거래량 조건을 붙이지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T09:15:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T09:18:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SO","display_name":"SO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":93.46,"market_data_asof":"2026-11-11T09:30:00-05:00","session_vwap":93.20288659793815,"relative_volume":0.02064951817613521,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-10 저가 92.50과 종가 93.65의 정규장·날짜 정합성을 확인한다. 충족했다면 불필요하게 새 일봉 확인을 추가하지 않는다. / 첫 일봉 요건 이후 다음 적격 거래일의 92.50–92.55 재시험을 확인한다. 단순 가격 접촉만으로 안정적인 지지 확인을 대신하지 않는다.","risk_condition_ko":"91.73 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T09:30:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T09:33:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1083.02,"market_data_asof":"2026-11-11T08:45:00-05:00","session_vwap":1071.1716843549202,"relative_volume":0.11233082177181536,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단시각 2026-11-11T09:02:26.885484-05:00은 2026-11-18T23:59:59-05:00 이전이다. 다만 실제 개장 여부, 휴장·단축장 달력, 거래 상태와 실행 가능한 호가는 별도 확인해야 한다. / 2026-11-11 08:45 미국 동부시간의 지연된 장전 자료는 정규장 확인이나 매수 조건 충족을 뜻하지 않는다. 최초 활성화는 2026-11-11 이후의 적격 일봉 다음 검증된 거래일이다.","risk_condition_ko":"1,040.57 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T08:45:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T08:48:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SPG","display_name":"Simon Property Group","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":234.34,"market_data_asof":"2026-11-11T09:30:00-05:00","session_vwap":234.16902887139108,"relative_volume":0.05342703959301216,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"230.45–231.66에서 일봉 지지와 다음 확인된 거래일 유지 여부를 관찰한다. 가격 접촉만으로 매수하지 않는다. / 235.97 위 종가와 거래량 확대 및 다음 거래일 재시험을 확인한다. 제공된 최근 거래량은 20일 평균의 94.4%여서 돌파 참여 확대가 입증되지 않았지만, 이를 매도 물량 출회 증거로도 해석하지 않는다.","risk_condition_ko":"235.05 이상 도달, 종가 확인 후 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T09:30:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T09:33:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LIN","display_name":"LIN","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":520.06,"market_data_asof":"2026-11-11T08:45:00-05:00","session_vwap":517.2353780313838,"relative_volume":0.012841422212795139,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"514.20~517.01 시험 후 517.01 이상 종가와 다음 실제 거래일 지지·종가 확인, 이후 같은 구간 재방문 여부. / 실제 진입가·양방향 비용을 반영한 526.56까지 순손익비 1.5 이상 여부와 523.51 저항의 가격 반응.","risk_condition_ko":"510.01 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T08:45:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T08:48:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":166.41,"market_data_asof":"2026-11-11T08:45:00-05:00","session_vwap":166.28751156336725,"relative_volume":0.009807894200748212,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-10 일별 자료를 기준으로 판단하며 검증된 거래일 종료마다 가격과 이동평균을 갱신한다. 167.19 이탈은 조기 경고이지 자동 청산 기준은 아니다. / 2026-11-11 08:45 미국 동부시간의 지연된 장전 자료와 166.41은 체결 가능 가격이나 정규장 지지 이탈을 입증하지 않는다. 주문 전 거래소 일정·거래 상태·신선한 실행 가능 호가를 별도로 확인한다.","risk_condition_ko":"162.13 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T08:45:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T08:48:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WELL","display_name":"WELL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":247.9,"market_data_asof":"2026-11-11T09:15:00-05:00","session_vwap":246.52892561983472,"relative_volume":0.000776640088931035,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"241.93–243.40의 새로운 눌림과 243.40 이상 종가 이후 다음 거래일 지지를 확인한다. 비용·갭 반영 보상·위험비 1.5를 충족하는 하단 가격에서만 최초 소액 진입을 검토한다. 적격 가격이 없으면 현금을 유지한다. / 248.83 초과 종가와 개선된 일별 거래 참여, 다음 거래일 248.26–248.83 지지를 확인하면 재평가한다. 251.12–253.37 저항 때문에 돌파 매수는 자동 허용하지 않는다.","risk_condition_ko":"241.93 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T09:15:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T09:18:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":290.57,"market_data_asof":"2026-11-11T08:20:00-05:00","session_vwap":290.1971937381465,"relative_volume":0.44940738635472033,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"286.00–287.71에서 적격 종가가 형성된 뒤 다음 검증 거래일에 지지가 유지되면, 공시·계좌 여력·손익비 조건을 함께 점검해 소액 첫 진입을 검토한다. / 289.51–291.04 회복은 기술적 개선이지만 더 높은 가격의 자동 매수 신호가 아니다.","risk_condition_ko":"281.07 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T08:20:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T08:23:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"JHX","display_name":"JHX","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":29.17,"market_data_asof":"2026-11-11T07:55:00-05:00","session_vwap":29.115681233933163,"relative_volume":0.0005361476589741917,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-11-11부터 2026-11-18까지 실제로 확인된 거래 세션에서 지지 구간 시험, 회복 종가, 다음 거래일 지지, 이후 허용 가격 재시험을 순차 관찰한다. / 28.64~28.68은 첫 지지 관찰 구간이며 접촉만으로 매수하지 않는다.","risk_condition_ko":"28.19 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T07:55:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T07:58:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"JPM","display_name":"JPM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":342.67,"market_data_asof":"2026-11-11T09:10:00-05:00","session_vwap":341.8311538461538,"relative_volume":0.021804827200168915,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"340.18~340.41 재시험과 확인 종가 이후 다음 실제 거래일 지지·구간 내 체결 가능성을 관찰한다. 사건 점검과 계좌 한도까지 통과해야 최초 소액 진입이 가능하다. / 344.85 회복과 345.75~347.14 돌파·재지지는 관찰 신호다. 기존 계획을 돌파 추격매수로 바꾸지 않는다.","risk_condition_ko":"333 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T09:10:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T09:13:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"META","display_name":"Meta Platforms","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":648.9,"market_data_asof":"2026-11-11T08:00:00-05:00","session_vwap":647.0734516713225,"relative_volume":0.111823450048716,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"630–631: 지지 시험과 종가 631 이상, 바로 다음 거래일 종가 631 이상, 이후 진입 구간 재방문을 순서대로 확인한다. / 647.25–650.43: 첫 저항과 향후 돌파 여부를 관찰한다. 돌파 후 647–650 지지 전환은 별도 검토 사유이지 추격 매수 승인이 아니다.","risk_condition_ko":"630 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T08:00:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T08:03:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"QCOM","display_name":"Qualcomm","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":180.39,"market_data_asof":"2026-11-11T08:20:00-05:00","session_vwap":178.7235632536904,"relative_volume":0.07057847869160652,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"170.22–171.75의 새로운 종가와 다음 완료 거래일의 170.22 이상 종가를 순서대로 확인한다. 활성화는 두 확인이 끝난 뒤의 체결 가능한 정규장부터이며 만료 전이어야 한다. / 178.28과 180.76 회복은 진입 승인과 분리해서 관찰한다. 180.39의 지연 관측을 체결 기준으로 사용하지 않는다.","risk_condition_ko":"168.53 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-11-11T08:20:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-11-11T08:23:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-11T23:10:05.359536+09:00",
  "as_of": "2026-11-10T12:36:00-05:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
