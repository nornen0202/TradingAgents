# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-13T09:10:28.837736+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261012T224903_local-scheduler-us-full",
  "producer_finished_at": "2026-10-13T03:54:30.811906+09:00",
  "analysis_run_id": "20261012T224903_local-scheduler-us-full",
  "analysis_completed_at": "2026-10-13T03:21:59.183390+09:00",
  "analysis_trade_date_oldest": "2026-10-09",
  "analysis_trade_date_latest": "2026-10-09",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-12T09:45:00-04:00",
  "market_data_latest_at": "2026-10-12T13:45:00-04:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-13T03:22:26.192061+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-13T03:22:26.192061+09:00",
    "run_started_at": "2026-10-12T22:49:03.963068+09:00",
    "run_finished_at": "2026-10-13T03:54:30.811906+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23611188,
    "total_market_value_krw": 24608712,
    "total_unrealized_pnl_krw": 997524,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 104939,
    "total_equity_krw": 25690303
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 545462,
      "current_price_krw": 597443,
      "market_value_krw": 7169325,
      "unrealized_pnl_krw": 623776
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 292360,
      "current_price_krw": 285074,
      "market_value_krw": 3135817,
      "unrealized_pnl_krw": -80144
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 424050,
      "current_price_krw": 470507,
      "market_value_krw": 2823046,
      "unrealized_pnl_krw": 278742
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 267180,
      "current_price_krw": 302983,
      "market_value_krw": 1817900,
      "unrealized_pnl_krw": 214816
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1879542,
      "current_price_krw": 1769705,
      "market_value_krw": 1769705,
      "unrealized_pnl_krw": -109837
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 555801,
      "current_price_krw": 573426,
      "market_value_krw": 1720279,
      "unrealized_pnl_krw": 52874
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1472522,
      "current_price_krw": 1334467,
      "market_value_krw": 1334467,
      "unrealized_pnl_krw": -138055
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 134484,
      "current_price_krw": 134491,
      "market_value_krw": 1210419,
      "unrealized_pnl_krw": 60
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 364489,
      "current_price_krw": 454525,
      "market_value_krw": 909050,
      "unrealized_pnl_krw": 180072
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 662584,
      "current_price_krw": 766954,
      "market_value_krw": 766954,
      "unrealized_pnl_krw": 104370
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1419632,
      "current_price_krw": 1577341,
      "market_value_krw": 687823,
      "unrealized_pnl_krw": 68771
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 569486,
      "current_price_krw": 474709,
      "market_value_krw": 474709,
      "unrealized_pnl_krw": -94777
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 136179,
      "current_price_krw": 110358,
      "market_value_krw": 441432,
      "unrealized_pnl_krw": -103285
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 347665,
      "current_price_krw": 347786,
      "market_value_krw": 347786,
      "unrealized_pnl_krw": 121
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1325.0,"market_data_asof":"2026-10-12T10:50:00-04:00","session_vwap":1338.8742797890086,"relative_volume":0.7078816667878977,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1315.24 지지 유지 후 1351.26과 최신 당일 거래량가중평균가격 회복·재시험, 완료 5분봉 두 개의 유지 및 검증된 시간대 보정 상대 거래량 1.2 이상을 확인한다. 이는 재평가 조건이며 현재 유효한 매수 주문이 아니다. / 1402.00 위 정규장 종가와 검증된 완성 거래량 증가 후 다음 확인된 거래 세션 첫 30~60분의 지지 또는 재돌파를 관찰한다. 실제 진입가에서 보수적 목표와 구조 손절을 재산정해 순보상 대비 위험 2 이상이 아니면 매수하지 않는다.","risk_condition_ko":"1,349.39 이하 하락, 2개 봉 확인 후 (축소에 거래량 증가를 요구하지 않음) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T10:50:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T11:20:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":82.355,"market_data_asof":"2026-10-12T10:25:00-04:00","session_vwap":82.50342323231207,"relative_volume":0.4348780661932981,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 호가·5분봉·보유량·거래정지 상태와 실제 거래일·정규장 종료·조기폐장 여부를 확인한다. 의사결정 시계만으로 세션을 확정하지 않는다. / 82.59·82.82 회복 후 83.11 돌파와 재시험을 관찰한다. 상대강도지수 50 회복과 이동평균 수렴·확산 히스토그램 양수 전환은 보완 증거로만 사용한다.","risk_condition_ko":"82.28 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T10:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T10:55:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":360.3322,"market_data_asof":"2026-10-12T09:45:00-04:00","session_vwap":359.3285221978685,"relative_volume":1.0236948793234897,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"357.41–358.81에서 안정화와 저점 상승을 확인하고 361.28을 회복하는지 관찰한다. 가격 접촉만으로 매수하지 않는다. / 367.11 위 완료 5분봉 돌파와 재시험 성공, 실시간 장중 거래량가중평균가격 상회, 동일 시간대 기준 상대거래량 1.2 이상을 확인한다. 이는 재검토 조건이다.","risk_condition_ko":"367.11 이상 도달, 2개 봉 확인 후 (보호 매도에는 거래량 증가를 요구하지 않는다.) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T09:45:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T10:15:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":998.18,"market_data_asof":"2026-10-12T10:20:00-04:00","session_vwap":998.1830793429772,"relative_volume":0.3739765504629812,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"988.39~991.00 시험 후 더 높은 5분봉 저점, 991.00 위의 완료된 5분봉 종가 2개, 당일 거래량가중평균가 회복과 검증된 시간대 보정 상대거래량 1.2 이상을 확인한다. 충족해도 곧바로 주문하지 않고 손절 근거와 비용 차감 후 보상 대비 위험을 재평가한다. / 973.36~978.04 중간 지지와 968.71 종가 위험축소 기준을 구분해 관찰한다.","risk_condition_ko":"968.71 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T10:20:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T10:50:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":446.6,"market_data_asof":"2026-10-12T11:25:00-04:00","session_vwap":449.3783506499416,"relative_volume":0.5360531875872514,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 호가 시각, 실제 거래일·정규장·조기종료 일정, 거래정지 여부와 완료된 5분봉을 우선 확인한다. / 449.75 및 최신 장중 거래량가중평균가격 위 완료된 5분봉 두 개와 재시험 지지, 이어 454.40 돌파 및 검증된 동시간대 상대거래량 1.2 이상을 확인한다.","risk_condition_ko":"440.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T11:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T11:55:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.53,"market_data_asof":"2026-10-12T11:20:00-04:00","session_vwap":100.52374182008002,"relative_volume":0.7730269510704026,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"중립 분석가의 우선순위에 따라 지급 필요일·집중도·공식 자산구조·보유기간 순수익·순자산가치·실행조건부터 검증한다. 직접 사회관계망 자료나 일반 기업 실적자료의 부재는 별도 필수조건으로 추가하지 않는다. / 공식 보유내역·보수·수익률 산식·분배 및 분배락 일정을 확인하고 보고서 간 이동평균 차이를 해소한다. 기록상 분배금 0.307에서 0.301로의 약 1.95% 감소는 지급 대상 기간 확인 전 지속적인 소득 악화로 해석하지 않는다.","risk_condition_ko":"100.43 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T11:20:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T11:50:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1181.91,"market_data_asof":"2026-10-12T10:50:00-04:00","session_vwap":1181.7258054692734,"relative_volume":0.33626794354589046,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1131~1143에서 매도 압력 완화와 가격 회복, 당일 거래량가중평균가격 상회, 검증된 동시간대 상대거래량 1.2 이상을 확인하고 비용 후 첫 목표 손익비를 재계산한다. / 1215 위 검증된 일봉 마감과 최신 20일 평균 이상 거래량을 확인한다. 제공된 평균 2277652주는 실행 전 갱신한다.","risk_condition_ko":"1,131 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T10:50:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T11:20:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":261.145,"market_data_asof":"2026-10-12T09:45:00-04:00","session_vwap":262.5396838106953,"relative_volume":1.2499951665084252,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"AMZN의 실제 거래일·정규장 일정·거래정지 여부와 실시간 시세 신선도를 확인한다. 제공된 런타임은 세션이나 조건 충족의 증거가 아니다. / AMZN 259.10~260.14에서 연속 두 개 5분봉 지지, 당시 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상을 확인한다. 지연 자료의 1.25는 현재 충족 증거가 아니다.","risk_condition_ko":"259.1 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T09:45:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T10:15:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":213.215,"market_data_asof":"2026-10-12T11:10:00-04:00","session_vwap":213.05548142479745,"relative_volume":0.5191611304722967,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"210.61~211.35 지지 형성 이후 211.40 부근 회복, 저점 상승, 당일 거래량가중평균가격 상회와 정의가 검증된 동일 경과시간 상대거래량 1.2 이상을 확인한다. / 213.29~213.36 돌파와 재시험은 관찰 신호다. 213.87~214.97 및 215.72 저항 때문에 단독 매수 신호로 사용하지 않는다.","risk_condition_ko":"210.61 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T11:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T11:40:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":431.705,"market_data_asof":"2026-10-12T10:20:00-04:00","session_vwap":430.1032448377581,"relative_volume":0.5890446666819912,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"420.00~426.33달러 재시험 후 426.33달러를 연속 두 개의 완료된 5분 봉에서 회복·유지하는지 확인한다. 회복형 진입 재심사 범위는 426.33~427.26달러이며 상단을 추격하지 않는다. 손익비 검증은 별도 필수다. / 434.77달러 회복은 초기 개선 신호다. 439.76~442.49달러 및 446.73~452.00달러 저항을 구분하고 초기 회복을 전체 박스권 돌파로 해석하지 않는다.","risk_condition_ko":"420 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T10:20:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T10:50:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":579.0,"market_data_asof":"2026-10-12T09:45:00-04:00","session_vwap":578.6457373983436,"relative_volume":0.9147096369228176,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"실제 거래일·정규장 운영·거래정지 여부와 최신 DELL 호가를 확인한다. 09:45 관측값 579.00은 판단 시각 2026-10-12T10:14:29.467613-04:00 기준 약 29분 29초 전 자료로 현재 체결 판단에 사용할 수 없다. / 595.51 돌파와 595.06~595.51 재시험, 또는 564.51~566.20 시험 뒤 566.20 회복을 관찰한다. 552.29~555.68로 하락했다는 이유만으로 추가 매수하지 않는다.","risk_condition_ko":"552.29 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T09:45:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T10:15:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":340.9136,"market_data_asof":"2026-10-12T09:45:00-04:00","session_vwap":340.3449036290408,"relative_volume":1.4683023861329312,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"330.70~333.00 지지 반등, 331.50 이하 실제 체결 가능성, 당일 거래량가중평균가격 상회와 검증된 동시간대 상대거래량 1.2 이상을 함께 확인한다. 저항대 대응까지 포함한 비용 후 손익비가 2 미만이면 진입을 포기한다. / 345.34 위 최신 두 개 5분봉 유지·재시험과 종가 돌파를 감시한다. 이후 목표·손절·위험예산이 정해지기 전에는 매수 신호로 승격하지 않는다.","risk_condition_ko":"330.7 이하 하락, 2개 봉 확인 후 (위험축소에는 거래량 확인을 요구하지 않음) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T09:45:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T10:15:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":353.425,"market_data_asof":"2026-10-12T10:25:00-04:00","session_vwap":353.5176781985918,"relative_volume":0.7225745509144943,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"345.55~346.14에서 하락 정지 후 346.14 재탈환과 연속 5분봉 두 개 유지, 당일 거래량가중평균가격 상회 및 검증된 동시간대 상대거래량 1.2 이상을 확인한다. 실제 진입가로 비용 후 보상위험비를 다시 계산한다. / 356.83 위 정규장 종가와 일거래량의 최신 20일 평균 대비 1.2배 이상을 확인한 뒤 다음 검증된 거래일 재시험을 관찰한다. 359.44와 364.17 저항을 생략하지 않는다.","risk_condition_ko":"345.55 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T10:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T10:55:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":225.96,"market_data_asof":"2026-10-12T10:55:00-04:00","session_vwap":226.66225323440293,"relative_volume":0.7808156338826336,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"주문용 최신 정규장 시세, 거래정지 상태, 당일과 다음 거래일 세션 일정, 기존 NVDA 및 인공지능·반도체 관련 노출을 먼저 확인한다. / 2026-10-12 10:55 미국 동부시간 관측가격 225.96, 당시 거래량가중평균가격 226.66과 상대거래량 0.78은 지연 자료다. 현재 진입 충족이나 지지 붕괴를 확정하는 데 사용하지 않는다.","risk_condition_ko":"221.09 이하 하락, 종가 확인 후 (완성 일봉 거래량이 갱신된 20일 평균을 초과하는지 확인) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T10:55:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T11:25:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SPYM","display_name":"SPYM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":91.605,"market_data_asof":"2026-10-12T12:40:00-04:00","session_vwap":91.6164818725027,"relative_volume":3.580352847163278,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 정규장 호가·완결된 5분 봉·거래량가중평균가격·거래소 일정·거래정지 상태를 확보한다. 현재 감시 규칙은 활성 주문이 아니다. / 92.00 돌파·재시험 또는 90.67~90.96 눌림 회복을 확인한다. 거래량 조건 충족만으로 매수하지 않고 실제 목표·손절·비용으로 순손익비를 다시 계산한다.","risk_condition_ko":"90.67 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T12:40:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T13:10:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":280.165,"market_data_asof":"2026-10-12T12:50:00-04:00","session_vwap":279.1061063610811,"relative_volume":0.2902219658129451,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"신선한 정규장 자료에서 280.32 위 완성된 5분봉 두 개, 재시험 지지, 최신 거래량가중평균가격 상회와 검증된 동일 시간대 상대거래량 1.2 이상을 확인한다. / 277.60 또는 276.01~276.47의 지지 확인 후 반등을 감시한다. 가격 접촉만으로 진입하지 않는다.","risk_condition_ko":"268.36 이하 하락, 다음 거래일 확인 후 (거래량 부족을 이유로 손실 관리를 지연하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T12:50:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T13:20:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":391.125,"market_data_asof":"2026-10-12T12:05:00-04:00","session_vwap":389.3123620665634,"relative_volume":0.3869098974272815,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"V의 실행 가능한 최신 호가, 정규장·거래정지 상태, 실시간 거래량가중평균가격과 산출 방법이 명확한 동일시각 대비 상대거래량을 확보한다. / 385.57–386.84에서 지지가 확인되고 반등하는지 관찰한다. 가격이 구간에 가까운 것만으로 매수하지 않는다.","risk_condition_ko":"379.99 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T12:05:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T12:35:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":172.125,"market_data_asof":"2026-10-12T13:05:00-04:00","session_vwap":171.87602431615264,"relative_volume":0.3040115317739069,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"170.29~171.01 재시험 후 지지 회복과 높은 저점 형성을 관찰한다. 구간 접촉만으로 매수하지 않는다. / 165.11~166.71에서 기존 보유의 손실 통제를 먼저 처리한 뒤 별도 눌림 회복 전략을 검토한다. 166.00은 체결 지시가 아닌 계산 예시다.","risk_condition_ko":"170.29 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T13:05:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T13:35:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMT","display_name":"AMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":182.72,"market_data_asof":"2026-10-12T13:45:00-04:00","session_vwap":182.06789365092152,"relative_volume":0.42615351224147474,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"180.03–180.25의 지지 유지와 최신 거래량가중평균가격 회복을 관찰한다. 자동 매수 구간은 아니다. / 177.88–179.04에서 하락 거래량 감소와 반등 참여 확대를 확인한다. 손절 174.50 적용 시 비용 반영 진입 상한은 178.10보다 낮으며, 거래량가중평균가격 회복에 필요한 가격이 상한을 넘으면 매수하지 않는다.","risk_condition_ko":"175.02 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T13:45:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T14:15:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":101.89,"market_data_asof":"2026-10-12T13:25:00-04:00","session_vwap":101.71921509617572,"relative_volume":0.554389523401492,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"102.46 위 5분봉 마감·재시험 지지·최신 거래량가중평균가격 상회·검증된 동시간대 상대거래량 1.2 이상을 함께 확인한다. 1.2는 제안 실행 기준이다. / 101.17~101.28 구간 지지와 최신 거래량가중평균가격 회복을 확인한다. 101.72는 2026-10-12 13:25의 과거 관측값으로만 취급한다.","risk_condition_ko":"100.03 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T13:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T13:55:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":152.91,"market_data_asof":"2026-10-12T12:05:00-04:00","session_vwap":152.3383961707984,"relative_volume":0.3187142888496477,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"150.76~151.60에서 연속 5분봉 두 개의 지지·반등, 최신 거래량가중평균가격 회복과 동일 시간대 상대거래량 1.2 이상을 확인한다. 손절·목표를 포함한 비용 후 손익비 2가 없으면 계속 대기한다. / 148.10 반등은 독립적인 신규 거래로 심사한다. 계좌 위험, 비용, 최신 시세, 정규장과 시간대가 명시된 유효기간을 검증한 새 결정에서만 소규모 시험 진입을 허용할 수 있다. 현재 조건부 매수 지시는 없다.","risk_condition_ko":"149.48 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T12:05:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T12:35:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":91.48,"market_data_asof":"2026-10-12T11:35:00-04:00","session_vwap":91.0039671938994,"relative_volume":0.6847993776798622,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"90.71–91.00 재시험 후 완료된 5분봉 2개가 91.00과 현재 거래량가중평균가격을 모두 웃돌고, 비교 가능한 시간대 보정 상대거래량이 1.2 이상인지 확인한다. 충족되어도 별도 승인과 만료시각 없이는 주문하지 않는다. / 92.87 위 종가와 다음 확인된 거래일의 지지 유지 또는 재돌파를 관찰한다. 새로운 손절 근거와 현실적인 비용 차감 보상대위험비가 확보되어야 추가 매수를 검토한다.","risk_condition_ko":"90.71 이하 하락, 2개 봉 확인 후 (방어적 매도에는 상대거래량 증가를 요구하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T11:35:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T12:05:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":215.2635,"market_data_asof":"2026-10-12T12:50:00-04:00","session_vwap":215.0797097753043,"relative_volume":0.37240725668650493,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"205–207 도달 자체가 아니라 질서 있는 조정과 지지 안정화인지 확인한다. 기존 위험 축소 신호를 먼저 처리하고 별도의 신규 거래 구조를 검증한다. / 206.00 부근에서 당일 거래량가중평균가격 회복, 동일 경과시간 상대거래량 1.2 이상, 비용 차감 후 보상 대비 위험 2배 이상 및 보유 여력을 확인한다. 명시적인 시간대 포함 만료 시각을 새로 정하기 전에는 주문을 활성화하지 않는다.","risk_condition_ko":"203.83 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T12:50:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T13:20:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CEG","display_name":"CEG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":292.235,"market_data_asof":"2026-10-12T13:20:00-04:00","session_vwap":295.9966705906825,"relative_volume":0.34793842857683505,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"돌파 경로: 최신 거래량가중평균가격 상회, 301.74 돌파·재시험 방어, 시간대 보정 상대거래량 1.2 이상을 확인한다. 306.99~309.80 저항까지 비용 후 손익비가 2 미만이면 진입하지 않는다. 309.80 위 목표가는 근거가 없다. / 되돌림 경로: 285.45~286.83에서 실제 저점 형성, 하락 거래량 둔화와 반등 거래량 회복을 확인하고 291.00~291.62 등 가장 가까운 회복 저항까지 손익비를 다시 계산한다. 이 경로에 301.74 돌파를 기계적으로 요구하지 않지만 가격 도달만으로 매수하지 않는다.","risk_condition_ko":"285.45 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T13:20:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T13:50:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NU","display_name":"NU","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":16.035,"market_data_asof":"2026-10-12T12:35:00-04:00","session_vwap":16.06611867944628,"relative_volume":0.3969118290840962,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"현재 NU 호가·거래 가능 상태·정규장 달력을 확인하고 계좌 비중과 전체 위험을 먼저 계산한다. 실제 임시 한도 초과가 확인되면 축소한다. / 15.48–15.79에서는 단순 접촉이 아니라 안정, 높아지는 저점, 현재 거래량가중평균가격 회복을 확인한다.","risk_condition_ko":"15.18 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T12:35:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T13:05:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOG","display_name":"GOOG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":347.67,"market_data_asof":"2026-10-12T13:10:00-04:00","session_vwap":350.10081037101963,"relative_volume":0.3931271506140143,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단 시각은 2026-10-12T13:34:54.068289-04:00이며 연구 기준일은 2026-10-12다. 10:30은 최초 검토 가능 시각이지 만료 시각이 아니다. 판단 시각이 이를 지났다는 사실만으로 정규장 운영, 조기 폐장 여부, 거래정지 여부 또는 진입 조건 충족이 확인되지는 않는다. 만료 시각이 없으므로 새로 만들거나 다음 거래일로 이월하지 않는다. / 2026-10-09 일봉과 지연된 2026-10-12 13:10 미국 동부시간 관측을 최신 호가·체결·거래량으로 갱신한다. 과거 거래량가중평균가격 350.10을 현재 고정 매매 기준으로 사용하지 않는다.","risk_condition_ko":"338.02 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T13:40:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"QCOM","display_name":"Qualcomm","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":173.635,"market_data_asof":"2026-10-12T13:35:00-04:00","session_vwap":173.79275881683438,"relative_volume":0.22406566176863915,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"171.02~172.69 지지 재시험, 높은 저점, 최신 거래량가중평균가격 위 완결 5분봉 2개와 시간대 보정 상대거래량 1.2 이상을 확인한다. 실제 손절 구조가 없으면 시험매수를 허용하지 않는다. / 175.22~176.40 및 179.82~180.88 저항을 반영해 비용 차감 손익비를 재계산한다. 180.88 회복 이후에도 첫 상위 저항 184.00~185.48까지 보상이 부족하면 계속 대기한다.","risk_condition_ko":"171.02 이하 하락, 2개 봉 확인 후 (171.02 아래 완결 5분봉 2개, 재시험 회복 실패 및 비교 가능한 구간 대비 거래량 증가) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T13:35:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T14:05:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"JPM","display_name":"JPM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":334.672,"market_data_asof":"2026-10-12T11:55:00-04:00","session_vwap":334.61768234262377,"relative_volume":0.3349668094515192,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"공식 실적 발표 일정, 거래소 달력·세션·거래정지 여부, 최신 호가와 기존 포트폴리오 위험 수용능력을 먼저 확인한다. / 333.55–334.14 재돌파와 재확인, 장중 거래량가중평균가격 상회, 일관된 산식의 동시간대 상대거래량 1.2 이상을 확인한다.","risk_condition_ko":"330.58 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T11:55:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T12:25:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SPCX","display_name":"SPCX","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":164.16,"market_data_asof":"2026-10-12T11:40:00-04:00","session_vwap":164.0958277108169,"relative_volume":0.8991222816384411,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"검증 작업은 우선하되 자본 배분 우선순위는 낮게 유지한다. SPCX 발행사·상품 유형·재무 통화와 단위·주식 기준 및 공시 발표·접수 시각을 먼저 확인한다. / 실제 정규장과 거래 가능 상태, 최신 호가·체결·연속 5분봉을 확인한다. 날짜만 있는 뉴스는 결정시각 이전 가용성이 확인된 자료로 취급하지 않는다.","risk_condition_ko":"157.44 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T11:40:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T12:10:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"META","display_name":"Meta Platforms","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":746.245,"market_data_asof":"2026-10-12T12:15:00-04:00","session_vwap":743.1065949740902,"relative_volume":0.7396602272943589,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"739.44~743.11 구간의 지지 전환, 현행 거래량가중평균가격 상회, 산식이 확인된 시간대 보정 상대거래량 1.2 이상을 확인한다. 743.11은 과거 관측값으로 갱신이 필요하다. / 751.58~751.66 돌파·재시험과 종가 확인을 관찰하되 747.60·757.27·763.90 저항을 반영한다. 779.82만 목표로 골라 보상/위험을 높이지 않는다.","risk_condition_ko":"739.44 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-12T12:15:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-12T12:45:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-13T16:07:39.397781+09:00",
  "as_of": "2026-10-12T09:45:00-04:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
