# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-15T05:45:25.948515+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261015T021357_local-scheduler-us-overlay_only",
  "producer_finished_at": "2026-10-15T02:16:53.381900+09:00",
  "analysis_run_id": "20261014T175403_local-scheduler-us-full",
  "analysis_completed_at": "2026-10-14T21:53:46.194182+09:00",
  "analysis_trade_date_oldest": "2026-10-13",
  "analysis_trade_date_latest": "2026-10-13",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-14T13:10:00-04:00",
  "market_data_latest_at": "2026-10-14T13:15:00-04:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-15T02:16:47.598014+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-15T02:16:47.598014+09:00",
    "run_started_at": "2026-10-15T02:13:57.819618+09:00",
    "run_finished_at": "2026-10-15T02:16:53.381900+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23655299,
    "total_market_value_krw": 24000720,
    "total_unrealized_pnl_krw": 345421,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 105135,
    "total_equity_krw": 25082507
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 546481,
      "current_price_krw": 579015,
      "market_value_krw": 6948186,
      "unrealized_pnl_krw": 390407
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 292906,
      "current_price_krw": 283341,
      "market_value_krw": 3116756,
      "unrealized_pnl_krw": -105214
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 424843,
      "current_price_krw": 468290,
      "market_value_krw": 2809744,
      "unrealized_pnl_krw": 260686
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 267679,
      "current_price_krw": 297952,
      "market_value_krw": 1787717,
      "unrealized_pnl_krw": 181638
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1883053,
      "current_price_krw": 1679814,
      "market_value_krw": 1679814,
      "unrealized_pnl_krw": -203239
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 556840,
      "current_price_krw": 549088,
      "market_value_krw": 1647266,
      "unrealized_pnl_krw": -23255
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1475273,
      "current_price_krw": 1252590,
      "market_value_krw": 1252590,
      "unrealized_pnl_krw": -222683
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 134735,
      "current_price_krw": 134760,
      "market_value_krw": 1212844,
      "unrealized_pnl_krw": 223
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 365170,
      "current_price_krw": 460461,
      "market_value_krw": 920923,
      "unrealized_pnl_krw": 190583
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1422285,
      "current_price_krw": 1624980,
      "market_value_krw": 708597,
      "unrealized_pnl_krw": 88388
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 663822,
      "current_price_krw": 678078,
      "market_value_krw": 678078,
      "unrealized_pnl_krw": 14256
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 570550,
      "current_price_krw": 465073,
      "market_value_krw": 465073,
      "unrealized_pnl_krw": -105477
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 136433,
      "current_price_krw": 108124,
      "market_value_krw": 432498,
      "unrealized_pnl_krw": -113237
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 348315,
      "current_price_krw": 340634,
      "market_value_krw": 340634,
      "unrealized_pnl_krw": -7681
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.5348,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":100.53537375175182,"relative_volume":1.0487318095502676,"spread_bps":0.9946784701850218,"day_high":100.54,"day_low":100.53,"execution_condition_ko":"판단 시각은 2026-10-14T06:37:13.085739-04:00이다. 공식 거래일·정규장 운영·거래정지 여부와 최신 호가 시각은 별도로 확인한다. 현재 시계는 세션 정상 운영이나 진입조건 충족의 증거가 아니다. / 미국 동부시간 10:30은 향후 소규모 시작을 검토할 가장 이른 관리 시각이며 자동 활성화나 만료시각이 아니다. 확정된 유효기한이 없으므로 만료 또는 다음 세션 이월을 선언하지 않는다.","risk_condition_ko":"100.5 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":935.0,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":946.8925431199262,"relative_volume":0.7714158168942284,"spread_bps":13.644600788828193,"day_high":997.665,"day_low":929.0,"execution_condition_ko":"991~992.49 또는 978.04~982.69에서 하락 정지 후 각 구간 상단과 정규장 거래량가중평균가격을 회복하는지 확인한다. 단순 접촉은 매수 신호가 아니다. / 1014.95 돌파·재시험 지지와 동일 시간대 상대거래량 1.2 이상을 함께 확인한다. 이는 재심사 조건이며 현재 주문 승인이 아니다.","risk_condition_ko":"963.29 이하 하락, 다음 거래일 확인 후 (거래량 확대는 보강 근거이며 위험 축소의 필수 조건은 아님) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":254.21,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":256.51833122848245,"relative_volume":0.5282094415089275,"spread_bps":1.1798249926261386,"day_high":259.65,"day_low":254.085,"execution_condition_ko":"정규장 일정·실제 거래 상태·최신 매수 및 매도 호가·정규장 거래량가중평균가격·시간 보정 거래량과 공식 행사 시각을 확인한다. / 258.35 이탈은 조기 경고로 취급한다. 그 자체만으로 자동 매도하지 않되 252.78 방어 규칙의 접근 여부를 점검한다.","risk_condition_ko":"252.78 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1211.1201,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":1208.4148990466304,"relative_volume":0.5721883134085934,"spread_bps":5.281922619834447,"day_high":1216.714,"day_low":1174.24,"execution_condition_ko":"1131–1143에서 안정화한 뒤 1143 위의 완료된 15분 봉 종가 2개를 확인한다. 당일 거래량가중평균가격 상회와 같은 시간대 상대거래량 1.2 이상만으로는 부족하며 새로운 비용 차감 후 보상/위험 2 이상 구조가 필요하다. / 1169.29와 1175.27 회복은 단기 구조 개선 신호지만 독립적 매수 신호는 아니다. 이동평균 수치는 갱신해야 한다.","risk_condition_ko":"1,131 이하 하락, 종가 확인 후 (정규장 일일 거래량이 갱신된 20일 평균과 직전 거래일 거래량을 모두 초과해야 한다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":432.075,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":435.61279832805263,"relative_volume":0.5108235444600964,"spread_bps":1.8485569702147582,"day_high":440.39,"day_low":430.24,"execution_condition_ko":"437.40 일봉 지지와 442.00 개장 전 참고 저점을 정규장에서 별도로 검증하고 445.50 회복·재시험을 관찰한다. 현재 제시된 반등 진입 조합은 손익비 부족으로 실행하지 않는다. / 456.30~460.28 회복, 갱신된 460.28 기준의 재시험 유지, 정규장 거래량가중평균가격 상회와 동일 시간대 상대거래량 1.2 이상을 함께 확인한다.","risk_condition_ko":"433.38 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":347.125,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":349.7430943330845,"relative_volume":0.4775283775735117,"spread_bps":4.021486226409283,"day_high":354.25,"day_low":346.12,"execution_condition_ko":"360.69 회복 후 정규장 5분봉 두 개 유지·재시험 지지, 거래량가중평균가격 상회, 동일 시간대 상대거래량 1.2 이상을 관찰한다. 충족해도 재무 검증과 비용 후 손익비가 부족하면 신규 주문은 비활성으로 유지한다. / 363.87~366.63과 367.19 저항 통과, 370.03 위 종가·후속 지지, 50일 평균 하락 완화와 상대강도지수 50 회복을 확인한다. 지표 개선은 불리한 손익비를 대체하지 못한다.","risk_condition_ko":"348.11 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":349.64,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":354.32385304801267,"relative_volume":0.4808539306173452,"spread_bps":1.427042454511724,"day_high":359.4,"day_low":349.135,"execution_condition_ko":"350.31~351.60 지지 유지와 345.69~346.53 지지 후 346.53 회복을 감시한다. 자동 매수 가격이 아니다. / 359.44 위 연속 두 개 5분봉 종가, 358.58~359.44 재시험 지지, 정규장 거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상을 함께 확인한다. 제안 기준이지 관측된 신호가 아니다.","risk_condition_ko":"345.69 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":211.37,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":211.7758277184448,"relative_volume":0.5918093954095779,"spread_bps":0.47273500839061644,"day_high":212.905,"day_low":211.135,"execution_condition_ko":"결정시각은 2026-10-14T06:15:49.148371-04:00이다. 제안된 미국 동부시간 10:30 최초 검토시각 이전이며, 10:30은 만료시각이나 자동 매수시각이 아니다. 실제 세션과 발표 일정은 별도로 확인한다. / 211.98~212.21 지지 유지 후 212.21 재회복, 완료 5분봉 2개 지지, 정규장 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상과 비용 차감 보상/위험 1.5 이상을 함께 점검한다.","risk_condition_ko":"210.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":410.55,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":413.44939912500985,"relative_volume":1.1615145521131425,"spread_bps":8.000484877871001,"day_high":425.025,"day_low":407.71,"execution_condition_ko":"417~420 시험 후 완료된 연속 두 개의 5분봉 종가가 420 위에서 유지되고 저점이 높아지는지 확인한다. 정규장 거래량가중평균가 상회와 동시간대 상대거래량 1.2 이상을 함께 요구한다. / 433.05~433.95 회복 후 433.95 재시험 지지와 거래량 확인. 회복 자체를 전체 박스권 돌파나 자동 매수 승인으로 해석하지 않는다.","risk_condition_ko":"417 이하 하락, 종가 확인 후 (정규장 종가 이탈에는 거래량 조건 없음) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1254.08,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":1264.384029835496,"relative_volume":0.4094759163106692,"spread_bps":13.754337983041761,"day_high":1300.76,"day_low":1245.3,"execution_condition_ko":"최신 거래가능 상태와 보유자료를 우선 확인한다. 미국 동부시간 10:30은 검증된 정규장의 신규 진입 검토 시작 시각이며 만료시각이 아니다. 현재 확정된 조건부 주문이나 만료시각은 없고 다음 거래일로 이월할 기한도 없다. 위험감축에는 이 시작 시각 제한을 적용하지 않는다. / 1312.69–1319.55와 1283.81–1295.56 지지구간을 관찰한다. 1322.40 위의 연속 두 개 5분봉 종가, 재시험 지지, 정규장 거래량가중평균가격 상회와 동일 경과시간 대비 상대거래량 1.2 이상은 재평가 조건이지 자동 매수 조건이 아니다.","risk_condition_ko":"1,295.56 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":80.69,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":80.88526674119994,"relative_volume":0.47824025730358255,"spread_bps":1.238006809038083,"day_high":81.23,"day_low":80.57,"execution_condition_ko":"82.47~82.53 회복 후 83.11 돌파·재시험·참여도를 관찰한다. 초기 회복만으로 매수하지 않는다. / 83.94~84.53 저항과 갱신된 85.74 참고값을 반영해 순손익비를 재계산한다. 목표가를 근거 없이 늘리거나 손절폭을 줄여 기준을 맞추지 않는다.","risk_condition_ko":"81.32 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":343.8936,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":345.2377627020077,"relative_volume":0.7242153799995648,"spread_bps":0.8715989482698097,"day_high":347.07,"day_low":343.5,"execution_condition_ko":"최신 판단시각은 2026-10-14T05:16:14.207332-04:00이다. 이는 거래일 일정·거래정지 상태나 진입 조건을 검증하지 않는다. 제공된 04:50 미 동부시간 지연 장전 자료는 실행 근거로 사용하지 않는다. / 335.90–337.38 구간 시험 후 337.38 위 연속 두 개의 5분봉 종가, 정규장 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상을 함께 확인한다. 이동 기준값은 갱신한다.","risk_condition_ko":"335.9 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":222.39,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":223.73097603723863,"relative_volume":0.5103661414778387,"spread_bps":0.8981901468545483,"day_high":226.0,"day_low":221.12,"execution_condition_ko":"222.90~223.06 지지 시험 뒤 저점 상승과 정규장 거래량가중평균가격 회복, 224.90~226.32 회복 구조를 점검한다. 현재 제시된 가격 조합은 손익비 기준에 미달하므로 자동 매수하지 않는다. / 228.64~228.86 및 230.31 저항 해소 여부를 확인하고, 231.55 위 연속 두 개의 5분봉 마감·재시험 지지·동일 시간대 정규장 상대거래량 1.2 이상을 함께 확인한다.","risk_condition_ko":"222.9 이하 하락, 종가 확인 후 (거래량 증가는 이탈 신뢰도를 보강하지만 위험축소의 필수조건은 아님) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":506.48,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":522.4854240325261,"relative_volume":1.0191936297373747,"spread_bps":5.097239648682382,"day_high":547.17,"day_low":505.53,"execution_condition_ko":"판단시각은 2026-10-14T05:17:17.111709-04:00이며 일봉 기준일은 2026-10-13이다. 실제 거래일·정규장 운영시간·거래정지 여부와 최신 호가·5분봉·거래량을 별도로 검증한다. / 04:50 미국 동부시각 장전 가격 555.87은 지연 자료다. 현재 지지 이탈, 손절 발동 또는 진입 조건 충족의 증거로 쓰지 않는다.","risk_condition_ko":"557.71 이하 하락, 2개 봉 확인 후 (위험축소에는 거래량 확대를 요구하지 않음) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SPYM","display_name":"SPYM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":90.56,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":90.89256268030185,"relative_volume":0.6617055137772292,"spread_bps":1.1030831173118862,"day_high":91.37,"day_low":90.515,"execution_condition_ko":"공식 SPYM 상품 정체성, 보유종목, 보수, 추적 성과 및 같은 시각의 가격·순자산가치를 검증한다. / 91.10–91.25 지지, 91.16 위 5분봉 회복 종가, 강화된 반등 거래량, 당일 정규장 거래량가중평균가격 상회와 동일 경과시간 상대거래량 1.2 이상을 함께 확인한다.","risk_condition_ko":"90.67 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":392.885,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":393.20375661375664,"relative_volume":0.4816095200013419,"spread_bps":0.7632713811403163,"day_high":396.0,"day_low":391.01,"execution_condition_ko":"V: 현재 보유비중, 전체 계획손절위험, 기존 손절과 결제업종·펀드 내 간접노출을 확인한다. 한도 초과가 검증되면 389.27을 기다리지 않고 초과분을 위험 축소한다. / V: 390.69–391.81에서 매도거래량 감소, 두 5분봉의 지지 회복, 당일 거래량가중평균가격 회복과 반등 참여 증가를 관찰한다.","risk_condition_ko":"389.27 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":222.04,"market_data_asof":"2026-10-14T13:15:00-04:00","session_vwap":220.60341789766565,"relative_volume":0.49002169617409624,"spread_bps":2.251390233469679,"day_high":222.2,"day_low":218.54,"execution_condition_ko":"돌파 관찰: 신선한 정규장 가격으로 218.79를 넘고 217.78–218.79 재시험에 성공한 뒤, 218.79와 정규장 거래량가중평균가격 위에서 5분봉 종가가 두 번 연속 형성되며 상대거래량이 1.2 이상인지 확인한다. / 눌림 관찰: 215.95 또는 213.72–213.75에서 반전과 지지 유지가 확인되고 정규장 거래량가중평균가격을 회복하는지 확인한다. 가격 접촉만으로 매수하지 않는다.","risk_condition_ko":"210.89 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:15:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:45:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":177.11,"market_data_asof":"2026-10-14T13:15:00-04:00","session_vwap":175.91153246608795,"relative_volume":0.3639169437665216,"spread_bps":2.823502837620994,"day_high":177.355,"day_low":174.53,"execution_condition_ko":"거래일과 거래정지 여부, 최신 정규장 호가·5분봉, 순자산·기존 보유·미체결 주문·집중한도를 확인한다. / 172.14–172.65를 갱신한 뒤 지지 유지, 매도 거래량 감소, 반등 거래량 증가, 정규장 거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상을 관찰한다.","risk_condition_ko":"169.64 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:15:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:45:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"META","display_name":"Meta Platforms","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":736.5594,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":745.4797965944074,"relative_volume":0.6584894344235833,"spread_bps":2.576463329467837,"day_high":761.48,"day_low":734.2865,"execution_condition_ko":"734.33–742.96에서 지지 안정, 당일 정규장 거래량가중평균가격 회복, 동일 시간대 상대거래량 1.2배 이상을 확인한다. 가격 접촉만으로 매수하지 않는다. / 711.68과 777.59를 기준으로 삼는 경우 비용 전 진입 상한 약 738.04를 참고하되 실제 보호가격과 비용을 반영해 재계산한다. 742.96 위 회복 종가 뒤에도 불리한 가격이면 지지 재확인을 기다린다.","risk_condition_ko":"727.64 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":103.65,"market_data_asof":"2026-10-14T13:15:00-04:00","session_vwap":103.36882840599536,"relative_volume":0.5270463465743567,"spread_bps":0.9651112290696439,"day_high":103.77,"day_low":103.04,"execution_condition_ko":"103.09 위 5분봉 마감과 후속 재시험 지지, 정규장 거래량가중평균가격 상회, 동일 시간 누적 상대거래량 1.2 이상이면 신규 진입을 재평가한다. 자동 매수 조건은 아니다. / 102.09~102.47에서 매도 거래량 감소 후 반등과 거래량가중평균가격 회복을 확인하고 실제 진입가·구조적 손절가로 보상·위험비를 다시 계산한다.","risk_condition_ko":"104.83 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:15:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:45:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":284.37,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":282.6746251541168,"relative_volume":0.3980213886279064,"spread_bps":4.221338867977787,"day_high":284.635,"day_low":275.97,"execution_condition_ko":"271.35–273.70 반전 구간에서 273.70 회복과 재시험 성공, 정규장 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상을 확인한다. / 277.76 회복 시 281.12·283.43 저항까지의 실제 기대수익과 검증된 손절 위험을 다시 계산한다. 가격 회복만으로 매수하지 않는다.","risk_condition_ko":"271.35 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMD","display_name":"Advanced Micro Devices","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":573.36,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":581.0293648110068,"relative_volume":0.5186889424791287,"spread_bps":5.925616089791068,"day_high":591.88,"day_low":567.0,"execution_condition_ko":"586.54–594.24 시험 후 594.24 회복, 높아진 저점, 당일 거래량가중평균가격 지지 및 시간대 조정 상대 거래량 1.2 이상. / 613.36 회복·재시험 성공과 이후 620.84 위 정규장 종가 및 해당 20거래일 평균 대비 거래량 1.2 이상.","risk_condition_ko":"586.54 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMT","display_name":"AMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":178.37,"market_data_asof":"2026-10-14T13:15:00-04:00","session_vwap":177.9183139055693,"relative_volume":0.3547322821542257,"spread_bps":7.286791289481542,"day_high":179.43,"day_low":176.42,"execution_condition_ko":"최신 판단 시각은 2026-10-14T08:41:33.140398-04:00이며, 미국 동부 10:30은 아직 도래하지 않은 진입 검토 개시 시각이지 만료 시각이 아니다. 정규장 운영, 휴장·조기폐장 일정, 거래정지 및 호가 신선도는 별도로 검증한다. 유효기한이나 다음 거래일 이월을 만들어내지 않는다. / 완료된 일별 가격 기준일은 2026-10-13이다. 제공된 2026-10-14 미국 동부 08:05의 장전 가격 179.93, 거래량 78주, 약 3.40% 호가 차이는 진입 확인에 부적합하므로 최신 정규장 호가로 대체한다.","risk_condition_ko":"175.02 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:15:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:45:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DDOG","display_name":"Datadog","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":274.82,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":276.2287075552606,"relative_volume":0.24715825090754226,"spread_bps":15.281062397672034,"day_high":284.82,"day_low":270.76,"execution_condition_ko":"281.93 유지와 287.29 회복은 초기 안정화 신호로 관찰하되 단독 매수 조건으로 사용하지 않는다. / 274.24–277.65 시험 후 277.65 위 정규장 5분봉 두 개 마감, 재시험 유지, 거래량가중평균가격 상회 및 동시간대 상대거래량 1.2 이상을 우선 관찰한다.","risk_condition_ko":"293 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":155.6898,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":155.07653283608892,"relative_volume":0.4840606578196086,"spread_bps":2.5701985478373093,"day_high":155.7225,"day_low":154.285,"execution_condition_ko":"149.70~150.80에서 연속 두 5분봉 저점 상승, 세션 거래량가중평균가격 회복, 반등 시 검증된 동시간대 상대거래량 1.2 이상을 확인한다. 실제 체결가와 비용 후 손익비 조건도 동시에 충족해야 한다. / 154.75 위 정규장 5분봉 마감·재시험 지지·거래량 확인은 돌파 관찰 신호다. 별도 손익비 재설계 전에는 매수 신호로 전환하지 않는다.","risk_condition_ko":"149.7 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NU","display_name":"NU","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":15.04,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":15.014673203247705,"relative_volume":0.5565368122781069,"spread_bps":6.6511473229130615,"day_high":15.44,"day_low":14.765,"execution_condition_ko":"15.00~15.20에서 연속 5분봉 두 개의 저점 상승, 정규장 거래량가중평균가격 회복 및 산식이 확인된 동시간대 상대거래량 1.2 이상 확인. / 눌림 진입은 첫 저항 15.79~15.86과 주요 저항 16.14~16.22를 반영하고 부분 청산을 계획한다면 가중 보상도 계산한다. 비용 후 보상·위험 2배 미만이면 진입하지 않는다.","risk_condition_ko":"14.84 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":93.02,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":92.72609666091414,"relative_volume":0.6556013398522632,"spread_bps":1.0767160161497609,"day_high":93.38,"day_low":92.16,"execution_condition_ko":"90.20~90.71에서 저점 상승, 정규장 거래량가중평균가격 회복, 동일 경과시간 기준 상대거래량 1.2 이상 확인. 첫 저항 93.47까지 비용 차감 보상/위험 2배 이상이어야 하며 가격 도달만으로 매수하지 않는다. / 93.47·93.95를 거쳐 94.63 돌파·재시험과 참여 확대 관찰. 94.63 위의 근거 있는 목표와 유효 손절이 확보되지 않으면 계속 신규 진입을 보류한다. BTIG의 99를 실행 목표로 대체하지 않는다.","risk_condition_ko":"89.81 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CEG","display_name":"CEG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":281.68,"market_data_asof":"2026-10-14T13:15:00-04:00","session_vwap":283.3068933375659,"relative_volume":0.42013729310226994,"spread_bps":14.906832298135194,"day_high":294.5,"day_low":280.25,"execution_condition_ko":"284.79~286.40 시험 후 286.40 회복, 정규장 5분봉 두 개 유지, 재시험 성공 및 당일 거래량가중평균가격 회복을 관찰한다. 가격 조건만으로 매수를 승인하지 않는다. / 280.16~282.33 시험 후 282.33 회복·재시험을 관찰한다. 악재성 하락이면 기존 지지·저항과 사업가설부터 재평가한다.","risk_condition_ko":"284.79 이하 하락, 2개 봉 확인 후 (위험축소에는 최소 거래량 조건 없음) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:15:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:45:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOG","display_name":"GOOG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":345.5,"market_data_asof":"2026-10-14T13:15:00-04:00","session_vwap":350.23204832193755,"relative_volume":0.5712279589392519,"spread_bps":2.3106027784993812,"day_high":355.25,"day_low":344.94,"execution_condition_ko":"342.68~342.73 지지 방어와 342.73 재탈환, 최신 정규장 거래량가중평균가격 상회, 동일 시간대 상대거래량 1.2 이상을 관찰한다. 이 조건만으로 매수하지 않고 거래 구조와 비용 후 손익비를 먼저 재설계한다. / 기준일 거래량은 20일 평균의 86.43%, 최근 5일 평균은 20일 평균의 75.26%였다는 보수적 분석가의 지적을 반영해 거래량 회복을 확인한다. 이 일봉 비율을 장중 상대거래량과 혼동하지 않는다.","risk_condition_ko":"342.68 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:15:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:45:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WELL","display_name":"WELL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":232.84,"market_data_asof":"2026-10-14T13:10:00-04:00","session_vwap":231.4734502291769,"relative_volume":0.20121009556400266,"spread_bps":9.03167537578255,"day_high":233.28,"day_low":229.1,"execution_condition_ko":"최우선으로 기존 보유 수량·순자산·검증된 손절선·상관 노출을 확인하고 집중도 및 계획 손실한도 초과 여부를 계산한다. / 실제 거래일과 거래 상태를 확인한 뒤 최신 정규장 매수·매도 호가, 5분봉, 당일 거래량가중평균가격 및 동일 경과시간의 과거 거래량을 확보한다.","risk_condition_ko":"227.65 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T13:10:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T13:40:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-15T03:12:36.918527+09:00",
  "as_of": "2026-10-14T13:10:00-04:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
