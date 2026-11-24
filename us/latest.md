# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-24T15:42:03.372599+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261125T000228_local-scheduler-us-overlay_only",
  "producer_finished_at": "2026-11-25T00:23:21.000802+09:00",
  "analysis_run_id": "20261124T175248_local-scheduler-us-full",
  "analysis_completed_at": "2026-11-24T19:39:21.453992+09:00",
  "analysis_trade_date_oldest": "2026-11-23",
  "analysis_trade_date_latest": "2026-11-23",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-24T10:22:00-05:00",
  "market_data_latest_at": "2026-11-24T10:22:00-05:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-25T00:23:14.262825+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-25T00:23:14.262825+09:00",
    "run_started_at": "2026-11-25T00:02:28.311418+09:00",
    "run_finished_at": "2026-11-25T00:23:21.000802+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23762946,
    "total_market_value_krw": 20598426,
    "total_unrealized_pnl_krw": -3164520,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 113208,
    "total_equity_krw": 21687963
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 548968,
      "current_price_krw": 462301,
      "market_value_krw": 5547614,
      "unrealized_pnl_krw": -1040007
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 294239,
      "current_price_krw": 286920,
      "market_value_krw": 3156120,
      "unrealized_pnl_krw": -80512
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 426776,
      "current_price_krw": 376839,
      "market_value_krw": 2261035,
      "unrealized_pnl_krw": -299623
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1891622,
      "current_price_krw": 1610789,
      "market_value_krw": 1610789,
      "unrealized_pnl_krw": -280833
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 559374,
      "current_price_krw": 433039,
      "market_value_krw": 1299118,
      "unrealized_pnl_krw": -379005
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 268897,
      "current_price_krw": 205969,
      "market_value_krw": 1235815,
      "unrealized_pnl_krw": -377572
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 135348,
      "current_price_krw": 135548,
      "market_value_krw": 1219937,
      "unrealized_pnl_krw": 1798
    },
    {
      "ticker": "GEV",
      "name": "GE 버노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1481987,
      "current_price_krw": 969552,
      "market_value_krw": 969552,
      "unrealized_pnl_krw": -512435
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 366832,
      "current_price_krw": 474043,
      "market_value_krw": 948087,
      "unrealized_pnl_krw": 214423
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1428757,
      "current_price_krw": 1895703,
      "market_value_krw": 826649,
      "unrealized_pnl_krw": 203618
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 573146,
      "current_price_krw": 405515,
      "market_value_krw": 405515,
      "unrealized_pnl_krw": -167631
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 666843,
      "current_price_krw": 392789,
      "market_value_krw": 392789,
      "unrealized_pnl_krw": -274054
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 137054,
      "current_price_krw": 95615,
      "market_value_krw": 382461,
      "unrealized_pnl_krw": -165757
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 349900,
      "current_price_krw": 342945,
      "market_value_krw": 342945,
      "unrealized_pnl_krw": -6955
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1199.38,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":1253.889587334377,"relative_volume":0.7707588228538323,"spread_bps":11.75837784421279,"day_high":1287.88,"day_low":1198.44,"execution_condition_ko":"위험 대응 조건: 1,278.24 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"1,278.24 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":343.5188,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":351.54902914568623,"relative_volume":0.9701740358498916,"spread_bps":11.05776225811132,"day_high":357.1594,"day_low":343.28,"execution_condition_ko":"위험 대응 조건: 359.09 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"359.09 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":721.015,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":728.4733361525709,"relative_volume":0.6295262516193193,"spread_bps":18.865568949493174,"day_high":748.06,"day_low":719.3206,"execution_condition_ko":"위험 대응 조건: 748.98 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"748.98 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":279.95,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":279.9866715654884,"relative_volume":0.7844351419141264,"spread_bps":1.4292860716079634,"day_high":281.395,"day_low":277.03,"execution_condition_ko":"위험 대응 조건: 275.36 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"275.36 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":152.94,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":155.97009101013433,"relative_volume":1.7316888922926026,"spread_bps":0.6536588554446074,"day_high":159.92,"day_low":152.56,"execution_condition_ko":"위험 대응 조건: 156.93 이하 하락, 다음 거래일 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"156.93 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":213.14,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":213.1788878391085,"relative_volume":0.8375110178167915,"spread_bps":0.46916418400709975,"day_high":214.24,"day_low":211.28,"execution_condition_ko":"위험 대응 조건: 208.21 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"208.21 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":322.0,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":325.0117189706132,"relative_volume":0.6932415491938339,"spread_bps":35.399329275865924,"day_high":329.75,"day_low":321.95,"execution_condition_ko":"위험 대응 조건: 330 이하 하락, 다음 거래일 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"330 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":301.4,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":302.71360820233997,"relative_volume":0.8560397838030037,"spread_bps":6.967831842992729,"day_high":309.18,"day_low":298.41,"execution_condition_ko":"위험 대응 조건: 301.02 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"301.02 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":292.27,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":302.70952117803853,"relative_volume":2.2210404875100647,"spread_bps":20.868613263543683,"day_high":318.06,"day_low":291.694,"execution_condition_ko":"위험 대응 조건: 322.31 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"322.31 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":254.69,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":253.30440520672377,"relative_volume":0.6249914873339113,"spread_bps":1.963363634579207,"day_high":255.5599,"day_low":250.53,"execution_condition_ko":"위험 대응 조건: 245.31 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"245.31 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.65,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":100.65553203212761,"relative_volume":1.051585120889146,"spread_bps":0.9934926233163682,"day_high":100.66,"day_low":100.65,"execution_condition_ko":"100.60~100.61달러만 신규 편입 후보 구간이다. 100.65~100.66달러는 2026-11-23 고가와 2026-11-24 지연 개장 전 고가 부근의 저항이며 돌파 자체는 매수 신호가 아니다. 100.55~100.58달러는 하단 지지 재평가 구간이지 추가 매수 구간이 아니다. / 같은 매체의 보도 2건과 기사 기반 심리는 활용 사례일 뿐이다. 750억 달러는 초단기 채권 상장지수펀드 상품군 전체 유입이며 SGOV 순유입이 아니다. 공시 2건은 색인만 확인됐고 미국 1·3개월 국채 금리와 실효 연방기금금리 원자료는 없다.","risk_condition_ko":"100.55 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":352.28,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":350.58734683870426,"relative_volume":0.8327573193999748,"spread_bps":2.2708563967181608,"day_high":353.92,"day_low":345.88,"execution_condition_ko":"349.71달러 종가 회복과 다음 실제 정규 거래일 지지를 우선 확인한다. 352.60~355.28달러는 첫 저항대다. 360.83달러 위 종가와 후속 지지는 박스권 돌파 재평가 조건이지 추가 매수 승인이나 추격 신호가 아니다. / 다음 실적 발표 일정과 검증된 시장 전망은 미확인이다. 공시 원문·접수 시각과 판단 시점 이전 가용성, 재무제표 표시 통화·단위, 주당순이익의 주식 기준 및 예탁증서 환산비율 적용 여부를 발행사 원문에서 확인하기 전에는 재무 금액·주당순이익·예상 배수를 비교하거나 매매 근거로 쓰지 않는다.","risk_condition_ko":"340.56 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1406.77,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":1399.85638952718,"relative_volume":0.6882665375014746,"spread_bps":3.625442072899756,"day_high":1410.937,"day_low":1370.0,"execution_condition_ko":"실제 정규장 일정과 개장 여부, 거래정지 여부, 시세 신선도를 확인한다. 1341.46–1344.00달러 지지 회복을 우선 보되 1397.78–1401.66달러 상단 돌파도 추적한다. 1381.65–1382.48달러 첫 저항 돌파만으로는 매수하지 않는다. / 공급자 자료가 시사하는 매출 성장과 총마진 개선, 순이익률과 투자 후 현금흐름 약화는 검증 항목으로만 둔다. 공표 시각과 현금흐름 집계 정의를 대조하지 못했고 발행사 원문에서 재무제표 표시 통화·단위, 주당순이익 산정 주식 기준과 예탁증서 대 보통주 환산의 적용 여부 및 비율을 확인할 수 없다. 미국 달러 거래는 이를 입증하지 않으므로 재무 금액·주당순이익·가치평가 배수 비교는 제외한다.","risk_condition_ko":"1,331.6 이하 하락, 종가 확인 후 (별도 거래량 조건 없음) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":71.015,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":71.477838699079,"relative_volume":1.601570711262191,"spread_bps":1.4081532070676483,"day_high":71.81,"day_low":70.841,"execution_condition_ko":"72.96달러 위 정규장 종가와 다음 실제 거래일 지지를 확인한 뒤 73.49~73.55달러 상단 회복을 관찰한다. 두 구간은 반등 관찰 기준이지 매수 신호가 아니다. / 76.31달러 위 정규장 종가와 다음 실제 거래일 지지가 확인되면 80.65달러를 다음 저항으로 본다. 같은 시점의 호가·주당 순자산가치 괴리·스프레드와 예상 슬리피지, 금 현물 및 GLDM 순설정을 확인한다. 실제 되돌림에서 형성된 지지를 손절 기준으로 삼아 갭과 비용을 반영해도 손익비가 충분할 때만 소규모 첫 진입을 검토한다.","risk_condition_ko":"71.78 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WMT","display_name":"WMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":132.15,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":131.20361844524018,"relative_volume":0.8842818890576292,"spread_bps":2.2700616700087886,"day_high":132.295,"day_low":129.74,"execution_condition_ko":"127.18달러 시험 후 종가 회복과 다음 정규장 지지 유지를 우선 본다. 131.82달러 초과 종가와 다음 정규장 재시험은 차선이며, 130.52~130.56달러 통과만으로는 매수하지 않는다. 123.03~123.27달러는 무효화 이후 재평가할 관찰 구간으로, 손절 연기나 즉시 재매수 근거가 아니다. / 11월 24일 미 동부 시각 05:23:50의 판단 시점은 12월 1일 16:00 만료 전이지만, 05:10의 지연된 개장 전 자료로는 조건 충족을 확인할 수 없다. 실행 전 실제 정규장 일정, 거래정지 여부, 최신 호가·스프레드와 예정된 중요 발표를 확인한다. 다음 실적 발표일은 미확인이다.","risk_condition_ko":"125.84 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LIN","display_name":"LIN","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":518.17,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":516.1658108340325,"relative_volume":0.6503409144203469,"spread_bps":8.106699608175397,"day_high":519.065,"day_low":511.86,"execution_condition_ko":"검증된 정규장 종가 518.00달러 이상과 다음 확인된 거래일의 517.95~518.00달러 재시험을 순서대로 확인한다. 거래량은 보조 근거로만 사용한다. / 526.75~530.35달러 첫 저항대 접근 시 추가 매수보다 남은 상승 여력을 재평가한다. 533.39달러는 다음 저항이며 첫 분할의 손익비 산정에는 쓰지 않는다.","risk_condition_ko":"506.42 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":644.99,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":643.6848634909793,"relative_volume":0.3406079966217878,"spread_bps":10.230179028132497,"day_high":648.04,"day_low":632.05,"execution_condition_ko":"2026-11-24부터 확인된 정규장에서 624.11~625.08달러 지지 시험 후 624.11달러 이상 종가, 바로 다음 정규장에서 629.00달러 이상 종가를 차례로 확인한다. 어느 하나라도 충족되지 않으면 해당 신호로 매수하지 않는다. / 638.67~644.24달러에서는 전술 보유분을 재평가하되 자동 익절하지 않는다. 650.81달러 위 종가, 11월 23일 대비 거래량 증가와 다음 정규장 재지지는 관찰 전용이다. 상단 저항은 658.00~668.00달러와 673.50~681.99달러이며, 지지 이탈 후 605.00~607.98달러는 자동 재매수 구간이 아니다.","risk_condition_ko":"624.11 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":414.675,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":413.40155171693425,"relative_volume":0.5443911278433814,"spread_bps":5.064817606271603,"day_high":416.4,"day_low":407.4,"execution_condition_ko":"400.74~401.19달러 시험, 401.19달러 위 일봉 마감, 직후 정규장의 401.19달러 재시험 지지, 401.19~402.00달러 내 지정가와 순손익비 충족을 순서대로 확인한다. / 413.51달러 위 일봉 마감과 413.24~413.51달러의 지지 전환을 관찰한다. 다음 저항은 419.64달러이며 돌파 자체는 매수나 자동 익절 신호가 아니다.","risk_condition_ko":"400.74 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":579.46,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":576.9921226994497,"relative_volume":0.5397969991838331,"spread_bps":4.141429828648498,"day_high":579.77,"day_low":571.34,"execution_condition_ko":"565.60~566.52달러 지지 시험, 같은 날 568.35달러 이상 정규장 종가, 바로 다음 정규장 지지 유지를 순서대로 확인한다. / 576.02~578.64달러 회복과 586.45~588.54달러 및 596.92달러 저항을 관찰한다. 578.64달러 초과 종가만으로 추격하거나 적정가치를 높이지 않는다.","risk_condition_ko":"565.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1093.03,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":1082.7136783625895,"relative_volume":1.0264248735882833,"spread_bps":2.3787522529527716,"day_high":1094.75,"day_low":1068.0,"execution_condition_ko":"1,090.36달러 이상의 새로운 정규장 종가를 확인한 뒤 다음 거래일에 같은 가격의 지지와 1,090.36~1,095.00달러의 실제 체결 가능 호가를 점검한다. 손익비 두 기준을 통과할 때만 소액 진입한다. / 1,101.50달러에서 매수세가 막히는지 관찰한다. 1,123.67달러를 정규장 종가로 돌파하고 거래량과 이후 지지가 뒷받침되면 별도의 돌파 계획을 검토한다. 현재 계획의 대체 매수 신호는 아니다.","risk_condition_ko":"1,064 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":172.2199,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":171.34140994414687,"relative_volume":0.7589785579368387,"spread_bps":1.7424132423407077,"day_high":172.35,"day_low":169.83,"execution_condition_ko":"PG의 새 정규장 일봉에서 167.49~168.93달러 시험 후 168.93달러 이상 마감이 나오는지, 바로 다음 정규장에서 지지와 허용 체결가가 유지되는지 순서대로 확인한다. / PG의 170.64~171.61달러 및 173.57~173.59달러는 저항으로 관찰한다. 171.61달러 위에서 후속 저항까지 1.96~1.98달러로 평균 실제 변동폭 3.20달러보다 좁아 독립 돌파 매수 신호로 쓰지 않는다.","risk_condition_ko":"166.89 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"WELL","display_name":"WELL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":243.88,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":241.85230663300436,"relative_volume":0.39830172669948477,"spread_bps":10.656174433378045,"day_high":244.54,"day_low":238.71,"execution_condition_ko":"238.91달러 방어와 241.30달러 이상 정규장 종가를 확인한 후 다음 실제 정규장에서 241.30~241.80달러 구간과 비용 반영 손익비를 점검 / 244.77달러 위 종가와 후속 지지에서 추가 비중을 재검토. 249.75달러를 거래량 증가와 함께 돌파하고 재시험에서도 지키면 253.37~254.72달러를 다음 저항으로 관찰하되 추격하지 않음","risk_condition_ko":"238.91 이하 하락, 종가 확인 후 (거래량 조건 없음) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"IBM","display_name":"IBM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":233.1,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":233.68028860676466,"relative_volume":0.6018413440867403,"spread_bps":10.295126973233058,"day_high":235.865,"day_low":231.74,"execution_condition_ko":"235.10~235.72달러 회복은 관찰 신호다. 238.70~241.38달러 저항권을 넘는 종가와 상대강도지수 50 회복을 확인한다. / 돌파 다음 거래일의 241.38달러 지지 여부를 종가로 확인한다. 지지가 확인돼도 241.38~243.00달러 범위를 벗어나거나 상승 여력의 근거가 부족하면 매수하지 않는다.","risk_condition_ko":"228.4 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"JNJ","display_name":"JNJ","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":274.195,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":271.9909012854436,"relative_volume":0.5218263224037716,"spread_bps":5.10594842992036,"day_high":274.53,"day_low":268.08,"execution_condition_ko":"267.36~267.50달러 지지 시험, 267.50달러 이상 종가, 다음 정규장 지지 및 267.50~268.50달러 내 체결 가능성을 순서대로 확인한다. 첫 저항까지의 순보상으로 최종 선별한다. / 272.50달러 초과 종가와 다음 정규장 지지는 관찰 신호일 뿐 추격 매수 신호가 아니다. 거래량 증가와 상대강도지수 50 회복은 보조 근거다. 276.33달러 안착 후 282.33~283.25달러와 288.11~290.25달러를 차례로 관찰한다.","risk_condition_ko":"264.68 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"KO","display_name":"KO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":97.525,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":96.87287416601245,"relative_volume":0.4971106247531737,"spread_bps":2.0506510817194945,"day_high":97.6,"day_low":95.66,"execution_condition_ko":"거래량이 뒷받침된 97.00달러 초과 정규장 종가와 바로 다음 실제 정규장의 96.85~97.00달러 지지 재시험을 순서대로 본다. 둘 다 충족돼도 주문 신호는 아니다. 94.60~94.73달러에서 반등하더라도 96.85달러를 회복하지 못하면 매수 근거가 아니다. / 상방은 97.79~98.38달러와 99.30~100.56달러, 하방은 94.60달러 이탈 후 93.00달러와 91.94달러를 점검한다. 첫 저항대를 넘겨도 높아진 가격 때문에 비용 차감 후 여력이 줄면 추격하지 않는다.","risk_condition_ko":"94.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":296.02,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":293.7901415283444,"relative_volume":0.8079150727608303,"spread_bps":4.728292073357532,"day_high":296.515,"day_low":288.7001,"execution_condition_ko":"283.54~284.45 지지 시험, 289.24 이상 종가 회복, 다음 정규 거래일 종가 유지 순으로 확인한다. 모두 충족해도 기존 구간에서는 매수하지 않고 손익비를 다시 계산한다. / 290.91~291.07은 돌파 관찰대다. 294.45~295.03을 종가로 넘어 후속 지지가 확인되기 전에는 300.42~302.93을 목표가나 증액 근거로 쓰지 않는다.","risk_condition_ko":"283.54 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"HD","display_name":"HD","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":348.39,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":348.09517371331845,"relative_volume":0.272972644207491,"spread_bps":6.027641039623977,"day_high":350.06,"day_low":343.195,"execution_condition_ko":"HD의 345.87달러 거래량가중 이동평균 회복과 348.12달러 위 정규장 종가를 단기 강도 관찰선으로만 사용한다. / HD의 336.68~339.25달러 눌림 구간 시험, 339.25달러 이상 종가, 다음 확인된 정규장 지지를 차례로 본다. 11월 23일 저점은 구간 상단에 닿았지만 후속 지지는 확인되지 않았다. 가격 확인만으로는 주문하지 않는다.","risk_condition_ko":"330.31 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ANT","display_name":"ANT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":79.695,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":81.33365659204009,"relative_volume":0.8515942106202642,"spread_bps":2.5097251850917335,"day_high":83.49,"day_low":79.42,"execution_condition_ko":"84.61~87.64달러는 매수 구간이 아니라 회복 관찰 구간이다. 84.61달러 회복·재시험 방어, 87.64달러 이상 정규장 종가, 다음 실제 정규 거래일의 87.64달러 지지 또는 재돌파를 순서대로 확인한다. 이후 94.24달러 저항까지 실제 진입가 기준 손익비를 다시 계산한다. / 2026-12-01 미국 동부시간 기준으로 가격과 원공시를 재검토한다. 이는 관찰 재검토일이지, 주문의 최초 활성화 시각이나 만료일이 아니다. 미확인 상태면 신규 배분을 계속 보류한다.","risk_condition_ko":"84.14 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":["feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TXN","display_name":"Texas Instruments","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":265.31,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":272.1757908906528,"relative_volume":1.122443502138721,"spread_bps":9.41850170474881,"day_high":281.38,"day_low":265.0,"execution_condition_ko":"위험 대응 조건: 282.99 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"282.99 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":98.875,"market_data_asof":"2026-11-24T10:22:00-05:00","market_data_clock_status":null,"session_vwap":98.34542729727127,"relative_volume":2.5378938235370403,"spread_bps":9.103322712790515,"day_high":100.925,"day_low":94.52,"execution_condition_ko":"위험 대응 조건: 99.44 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"99.44 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-11-24T10:22:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-24T10:25:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-24T23:12:43.290679+09:00",
  "as_of": "2026-11-24T08:53:31+00:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
