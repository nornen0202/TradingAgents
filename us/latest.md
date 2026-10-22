# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-22T13:27:44.414816+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261022T192108_local-scheduler-us-full",
  "producer_finished_at": "2026-10-22T22:12:10.153812+09:00",
  "analysis_run_id": "20261022T192108_local-scheduler-us-full",
  "analysis_completed_at": "2026-10-22T21:48:03.274898+09:00",
  "analysis_trade_date_oldest": "2026-10-21",
  "analysis_trade_date_latest": "2026-10-21",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-22T06:25:00-04:00",
  "market_data_latest_at": "2026-10-22T08:20:00-04:00",
  "market_data_status": "MISSING"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-22T21:48:29.424199+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-22T21:48:29.424199+09:00",
    "run_started_at": "2026-10-22T19:21:08.178958+09:00",
    "run_finished_at": "2026-10-22T22:12:10.153812+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23390605,
    "total_market_value_krw": 23148561,
    "total_unrealized_pnl_krw": -242044,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 106199,
    "total_equity_krw": 24231412
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 540366,
      "current_price_krw": 553170,
      "market_value_krw": 6638050,
      "unrealized_pnl_krw": 153651
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 289628,
      "current_price_krw": 286162,
      "market_value_krw": 3147791,
      "unrealized_pnl_krw": -38126
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 420089,
      "current_price_krw": 436093,
      "market_value_krw": 2616562,
      "unrealized_pnl_krw": 96028
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 264684,
      "current_price_krw": 287591,
      "market_value_krw": 1725548,
      "unrealized_pnl_krw": 137441
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1861982,
      "current_price_krw": 1642167,
      "market_value_krw": 1642167,
      "unrealized_pnl_krw": -219815
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 550609,
      "current_price_krw": 507268,
      "market_value_krw": 1521806,
      "unrealized_pnl_krw": -130022
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 133228,
      "current_price_krw": 133385,
      "market_value_krw": 1200465,
      "unrealized_pnl_krw": 1413
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1458765,
      "current_price_krw": 1183737,
      "market_value_krw": 1183737,
      "unrealized_pnl_krw": -275028
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 361084,
      "current_price_krw": 455780,
      "market_value_krw": 911561,
      "unrealized_pnl_krw": 189393
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1406370,
      "current_price_krw": 1705984,
      "market_value_krw": 743920,
      "unrealized_pnl_krw": 130651
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 656394,
      "current_price_krw": 613057,
      "market_value_krw": 613057,
      "unrealized_pnl_krw": -43337
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 564165,
      "current_price_krw": 433995,
      "market_value_krw": 433995,
      "unrealized_pnl_krw": -130170
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 134907,
      "current_price_krw": 107179,
      "market_value_krw": 428719,
      "unrealized_pnl_krw": -110909
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 344417,
      "current_price_krw": 341183,
      "market_value_krw": 341183,
      "unrealized_pnl_krw": -3234
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":418.3797,"market_data_asof":"2026-10-22T07:25:00-04:00","session_vwap":419.0056647784072,"relative_volume":0.143820026892664,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"415.50~417.00 시험 후 417.00 위 두 개의 정규장 5분봉 마감과 높아지는 저점을 감시한다. 가까운 저항까지 손익비가 부족하면 계속 관망한다. / 435.16 돌파 후 433.95~434.15 재시험 지지와 435.16 재회복, 정규장 거래량가중평균가격 및 거래량을 확인한다. 숫자 도달만으로 주문을 발동하지 않는다.","risk_condition_ko":"407.13 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T07:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T07:28:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1243.0,"market_data_asof":"2026-10-22T06:40:00-04:00","session_vwap":1248.9520661157026,"relative_volume":0.018386405893736187,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"실제 거래일·정규장·거래정지 여부와 새로운 MPWR 호가를 확인한다. 2026-10-22 미국 동부시간 06:40의 1243 관측은 현재 체결가격이나 종가 손절 확인이 아니다. / 1286.92–1288.27, 1298.22–1305.18, 1321.78을 순차 관찰한다. 어느 한 가격의 회복만으로 매수하지 않는다.","risk_condition_ko":"1,259.87 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T06:40:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T06:43:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":328.9852,"market_data_asof":"2026-10-22T06:50:00-04:00","session_vwap":329.8395106484952,"relative_volume":0.1373174516573051,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"330.38 회복과 정규장 거래량가중평균가격 재시험 성공을 신속히 재검토한다. 관찰 조건이지 매수 승인은 아니다. / 335.11, 337.27–338.36, 340.94의 회복 여부와 저항 실패를 점검한다.","risk_condition_ko":"330.38 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T06:50:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T06:53:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":80.9098,"market_data_asof":"2026-10-22T06:25:00-04:00","session_vwap":80.78858948769128,"relative_volume":0.05948837930028466,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 결정 시각은 2026-10-22T06:45:20.827639-04:00이다. 제안된 미국 동부시간 10:30은 장중 시험 매수 재검토의 최초 시각이지 만료 시각이 아니다. 조건부 매수 기한은 설정되지 않았고 거래일·정규장 상태도 미확인이다. / 2026-10-22 06:25 미국 동부시간의 지연된 장전 가격 80.9098은 정규장 지지선 이탈이나 진입 성립을 확인하지 못한다. 최신 체결·호가·거래량가중평균가격·동시간대 상대거래량으로 대체한다.","risk_condition_ko":"80.43 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T06:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T06:28:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":328.53,"market_data_asof":"2026-10-22T06:30:00-04:00","session_vwap":329.3695295045341,"relative_volume":0.11410311566718796,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"신선한 정규장 호가·완성 5분봉·당일 거래량가중평균가격·동시간대 상대거래량을 확보한다. 06:30 미국 동부 기준 328.53은 지연된 장전 관측이며 현재 체결가나 지지선 붕괴 확인이 아니다. / 330.80–332.29와 337.80 회복을 관찰하되 안정화 신호만으로 매수하지 않는다.","risk_condition_ko":"327.01 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T06:30:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T06:33:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.62,"market_data_asof":"2026-10-22T07:25:00-04:00","session_vwap":100.624204448527,"relative_volume":0.18936667461368523,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단시각은 2026-10-22T07:37:38.387080-04:00이다. 2026-10-22T10:30:00-04:00은 아직 미래인 최초 재검토 시각이지 만료시각이 아니다. 실제 거래일·정규장 일정·정상 거래 여부는 별도 확인한다. / 2026-10-22 07:25 미국 동부시간 자료는 지연 장전 스냅샷이다. 최신 정규장 호가·5분봉·당일 거래량가중평균가격·동일시간대 상대거래량을 확보하고 수정 일봉과 대조한다. 장전 상대거래량 약 0.1894는 산식이 미확인이라 진입 근거로 쓰지 않는다.","risk_condition_ko":"100.59 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T07:25:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T07:28:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1283.23,"market_data_asof":"2026-10-22T06:55:00-04:00","session_vwap":1281.1791839148432,"relative_volume":0.02956350236155084,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"1260.17–1261.08 시험 뒤 1261.08 위의 연속 두 개 정규장 5분봉 종가 회복을 관찰한다. 단순 접촉은 신호가 아니다. / 첫 지지 실패 시 1251.25와 1231.45–1240.34를 관찰하되 자동 저가 매수하지 않는다. 주요 지지 실패 뒤 1208.19와 1183.52는 재평가 기준이다.","risk_condition_ko":"1,231.45 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T06:55:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T06:58:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":215.98,"market_data_asof":"2026-10-22T07:20:00-04:00","session_vwap":215.7222486898523,"relative_volume":0.015037937208635862,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"거래일·정규장 시간·거래정지·호가 신선도·가격 조정 기준과 포트폴리오 여력을 먼저 확인한다. / 215.00–215.10 시험 후 215.20 회복, 상승하는 5분봉 저점, 정규장 거래량가중평균가격 지지와 비교시점 상대거래량 1.2 이상을 관찰한다. 기존 예시는 순손익비 미달이므로 그대로 진입하지 않는다.","risk_condition_ko":"213.22 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T07:20:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T07:23:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":343.178,"market_data_asof":"2026-10-22T06:30:00-04:00","session_vwap":344.0388034693475,"relative_volume":0.054953364364354274,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"348.15 돌파·재시험 지지, 실시간 당일 거래량가중평균가격 상회, 동일 경과시간 상대거래량 1.2 이상을 함께 확인한다. 현재 충족 여부는 미확인이다. / 339.87~340.93 회복과 345.25~346.00 및 347.82~348.15 저항의 반복 거부를 관찰한다. 이동평균 기준은 갱신한다.","risk_condition_ko":"338.7 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T06:30:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T06:33:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":258.76,"market_data_asof":"2026-10-22T06:30:00-04:00","session_vwap":258.4927038961292,"relative_volume":0.11571014922303773,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"보유수량·순자산·승인 한도·상관 노출·갭 손실 감내능력을 확인한다. 초과분이 확인되면 차트 신호를 기다리지 않고 위험을 축소한다. / 실제 거래일과 거래 상태, 최신 호가 및 실적 일정을 확인한다. 장전 자료로 정규장 진입 조건을 충족 처리하지 않는다.","risk_condition_ko":"255.22 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T06:30:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T06:33:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"현재 명시된 위험 행동 없음","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"현재 명시된 위험 행동 없음","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":217.75,"market_data_asof":"2026-10-22T10:59:14+00:00","session_vwap":217.22778405158283,"relative_volume":0.10619782988326658,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"NVDA 판단시각은 2026-10-22T07:22:10.284865-04:00이다. 최초 시험매수 재평가 시각 2026-10-22T10:30:00-04:00 이전이며, 해당 시각은 만료시각이 아니다. 공식 거래일·정규장·조기폐장·거래정지 상태는 별도 확인이 필요하다. 검증된 주문 만료시각이 없어 주문을 활성화하거나 다음 거래일로 자동 연장하지 않는다. / NVDA 장전 가격 217.75는 약 06:59:14 기준으로 판단시각보다 약 23분 오래됐다. 관측 당시 57초 지연을 현재 신선도로 간주하지 않는다. 장전 거래량가중평균가격 217.23과 상대거래량 0.106은 정규장 조건을 대체하지 않는다.","risk_condition_ko":"212.77 이하 하락, 종가 확인 후 (정규장 종가 이탈 또는 거래량 동반 이탈 후 회복 실패) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T10:59:14+00:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T11:02:14+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"현재 명시된 위험 행동 없음","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":408.1,"market_data_asof":"2026-10-22T07:45:00-04:00","session_vwap":407.80973451327435,"relative_volume":0.008577987266381613,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"410.28 위에서 정규장 재시험 성공, 거래량가중평균가격 지지, 시간대 보정 상대거래량 1.2 이상을 확인한다. 조건 충족만으로 자동 매수하지 않는다. / 403.39–404.04에서는 저점 상승과 수요 회복을 확인한다. 단순 접촉은 매수 신호가 아니다.","risk_condition_ko":"403.39 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T07:45:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T07:48:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":286.457,"market_data_asof":"2026-10-22T08:20:00-04:00","session_vwap":284.94068576335644,"relative_volume":0.1931761738049984,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"282.15–282.96 지지 방어와 279.40–280.39의 더 깊은 지지 반응을 확인한다. 단순 접촉은 반등 확인이 아니다. / 279.40–282.96 구간의 신규 매수 검토에는 갱신된 280.39 기준 회복과 구조적 지지 확인을 요구한다. 지지 붕괴에 따른 위험 축소와 신규 매수 신호가 충돌하면 매수를 보류한다.","risk_condition_ko":"280.39 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T08:20:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T08:23:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1005.6611,"market_data_asof":"2026-10-22T08:10:00-04:00","session_vwap":1004.7971808927173,"relative_volume":0.04531520470831009,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"988.47–991.00에서 매도 압력 둔화와 지지 회복을 확인한다. 단순 접촉만으로 매수하지 않는다. / 976.20–982.00에서는 회복 확인과 보유 축소 조건을 구분한다. 종가 지지 이탈 이후에는 매수보다 위험축소가 우선이다.","risk_condition_ko":"976.2 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T08:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T08:13:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"UNH","display_name":"UNH","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":420.0,"market_data_asof":"2026-10-22T11:59:43+00:00","session_vwap":418.9356931481903,"relative_volume":0.029182430914431106,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"판단 시각은 2026-10-22T08:14:57.640562-04:00이다. 2026-10-22 미 동부시간 08:00:31의 420.00 관측값은 현재 체결 가능한 호가가 아니다. 거래일정·정규장 자격·거래 제한·새 호가를 별도로 확인한다. / 미 동부시간 10:30은 가장 이른 시험 진입 검토 시각이지 만료나 매수 승인이 아니다. 검증된 만료가 없어 조건부 주문을 설정하지 않으며 다음 거래일도 임의로 지정하지 않는다.","risk_condition_ko":"414.12 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T11:59:43+00:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T12:02:43+00:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":161.63,"market_data_asof":"2026-10-22T07:40:00-04:00","session_vwap":160.47776933308,"relative_volume":0.11565643945904562,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"159.35~159.98 재시험 후 지지 전환을 확인한다. 가격 접촉만으로 진입하지 않는다. / 156.80~157.08 또는 155.44 부근에서 저점 형성과 회복을 확인하고 가장 가까운 저항까지 손익비를 다시 계산한다.","risk_condition_ko":"155.44 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T07:40:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T07:43:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":623.67,"market_data_asof":"2026-10-22T08:05:00-04:00","session_vwap":622.616881961496,"relative_volume":1.1305382467993732,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"결정시각은 2026-10-22T08:20:14.699413-04:00이며 같은 날짜의 최초 검토시각 2026-10-22T10:30:00-04:00 이전이다. 10:30은 만료가 아니다. 실제 거래일·정규장·조기폐장·거래정지 여부는 별도 검증해야 하며 다음 세션이나 만료시각을 임의 지정하지 않는다. / 최신 정규장 호가·5분봉·당일 거래량가중평균가격·동일 시간대 상대거래량을 확보한다. 산식 미확인 장전 상대거래량 1.13과 지연 호가를 조건 충족에 사용하지 않는다.","risk_condition_ko":"624.66 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T08:05:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T08:08:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":92.6873,"market_data_asof":"2026-10-22T08:15:00-04:00","session_vwap":92.91446028513238,"relative_volume":0.001978812241860826,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"92.56~92.71 방어 후 93.03 회복, 세션 거래량가중평균가격 상회 및 동일 경과시간 상대거래량 1.2 이상을 확인한다. / 94.92~95.30에서는 추격하지 않는다. 96.24~96.50 저항 상단 돌파에는 재시험 지지와 새로운 목표 구조가 필요하다.","risk_condition_ko":"90.69 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T08:15:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T08:18:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NTAP","display_name":"NetApp","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":214.8,"market_data_asof":"2026-10-22T07:35:00-04:00","session_vwap":212.50533333333334,"relative_volume":0.005817723492823283,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"거래소 휴장·조기폐장 일정, 실제 세션, 거래 가능 여부, 최신 매수·매도 호가와 완료된 5분봉을 확인한다. / 217.84–218.43 회복과 재시험을 관찰하되 매수 신호로 단독 사용하지 않는다.","risk_condition_ko":"211.42 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T07:35:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T07:38:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"HD","display_name":"HD","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":314.8,"market_data_asof":"2026-10-22T07:40:00-04:00","session_vwap":314.1623479640402,"relative_volume":0.006899692689110621,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"309.96–311.14 재시험 후 완료된 5분 봉 두 개의 지지 수용, 정규장 거래량가중평균가격 상회와 시간보정 상대거래량 1.2 이상을 확인한다. 이는 매수 검토 자격일 뿐 주문 발동이 아니다. / 317.71 돌파·재시험·후속 지지를 관찰하고, 가까운 저항을 반영한 순보상위험비가 2 미만이면 매수하지 않는다.","risk_condition_ko":"306 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T07:40:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T07:43:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMT","display_name":"AMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":179.5946,"market_data_asof":"2026-10-22T07:50:00-04:00","session_vwap":178.13725490196077,"relative_volume":0.0035431245871810875,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"지지 경로: 175.02–177.10 시험 후 더 높은 저점, 176.04와 당일 거래량가중평균가격 회복, 동일 경과시간 대비 상대 거래량 1.2 이상을 확인한다. / 회복 경로: 178.87–179.94 회복과 재지지를 관찰하되 181.31–183.78 및 186 저항을 반영한 비용 후 보상·위험비가 2 미만이면 매수하지 않는다.","risk_condition_ko":"175.02 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T07:50:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T07:53:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TXN","display_name":"Texas Instruments","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":282.7695,"market_data_asof":"2026-10-22T08:20:00-04:00","session_vwap":282.5728847152093,"relative_volume":0.07670706499090331,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"283.30 회복 후 281.27–283.30 재시험을 완료된 정규장 5분봉 2개로 확인한다. 일봉 거래량가중이동평균 283.30은 당일 정규장 거래량가중평균가격과 다르다. / 277.37 및 272.00–274.20 지지를 관찰한다. 종가 272 미만이 검증되면 보유 대응을 위험 축소로 변경한다.","risk_condition_ko":"272 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":"2026-10-22T08:20:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-10-22T08:23:00-04:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"현재 명시된 위험 행동 없음","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"현재 명시된 위험 행동 없음","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"현재 명시된 위험 행동 없음","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"RHHBY","display_name":"RHHBY","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"현재 명시된 위험 행동 없음","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"추가 실행 조건 없음","risk_condition_ko":"현재 명시된 위험 행동 없음","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 시각 확인 필요","reference_strategy":{"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","decision_state_ko":"-","market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":null,"expired_at_build":false,"provider_limitations":[],"provider_blockers":["work_packet_row_invalid_timestamp"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-22T03:18:02.795423+09:00",
  "as_of": "2026-10-21T14:14:00-04:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
