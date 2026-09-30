# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-09-30T18:21:04.547703+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261001T031100_github-actions-overlay-us",
  "producer_finished_at": "2026-10-01T03:19:27.886272+09:00",
  "analysis_run_id": "20261001T000500_github-actions-us",
  "analysis_completed_at": "2026-10-01T00:32:08.634901+09:00",
  "analysis_trade_date_oldest": "2026-09-29",
  "analysis_trade_date_latest": "2026-09-29",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-09-30T14:10:00-04:00",
  "market_data_latest_at": "2026-09-30T14:10:00-04:00",
  "market_data_status": "FRESH"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-01T03:19:24.442996+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23971170,
    "total_market_value_krw": 25027091,
    "total_unrealized_pnl_krw": 1055921,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 87019,
    "total_equity_krw": 26090762
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 553778,
      "current_price_krw": 622513,
      "market_value_krw": 7470167,
      "unrealized_pnl_krw": 824820
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 296817,
      "current_price_krw": 283796,
      "market_value_krw": 3121766,
      "unrealized_pnl_krw": -143228
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 430516,
      "current_price_krw": 474069,
      "market_value_krw": 2844417,
      "unrealized_pnl_krw": 261321
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 271254,
      "current_price_krw": 313423,
      "market_value_krw": 1880541,
      "unrealized_pnl_krw": 253016
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1908198,
      "current_price_krw": 1810264,
      "market_value_krw": 1810264,
      "unrealized_pnl_krw": -97934
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 564276,
      "current_price_krw": 586781,
      "market_value_krw": 1760343,
      "unrealized_pnl_krw": 67515
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1494973,
      "current_price_krw": 1296810,
      "market_value_krw": 1296810,
      "unrealized_pnl_krw": -198163
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 136534,
      "current_price_krw": 136763,
      "market_value_krw": 1230873,
      "unrealized_pnl_krw": 2060
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 370046,
      "current_price_krw": 456925,
      "market_value_krw": 913850,
      "unrealized_pnl_krw": 173757
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 672686,
      "current_price_krw": 738371,
      "market_value_krw": 738371,
      "unrealized_pnl_krw": 65685
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1441275,
      "current_price_krw": 1588580,
      "market_value_krw": 692724,
      "unrealized_pnl_krw": 64234
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 578168,
      "current_price_krw": 480744,
      "market_value_krw": 480744,
      "unrealized_pnl_krw": -97424
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 138255,
      "current_price_krw": 111504,
      "market_value_krw": 446017,
      "unrealized_pnl_krw": -107005
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 352966,
      "current_price_krw": 340204,
      "market_value_krw": 340204,
      "unrealized_pnl_krw": -12762
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":457.98,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":458.5341489340207,"relative_volume":0.24796458602705526,"spread_bps":0.8733624454140528,"day_high":461.87,"day_low":454.9,"execution_condition_ko":"2026-09-30 10:30 이후 459.43 상회 유지, 당일 거래량가중평균가격 상회 및 같은 시각 기준 상대 거래량 1.2 이상 / 463.72 위 거래량 동반 종가와 다음 거래일 지지 확인","risk_condition_ko":"447.07 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1332.11,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":1338.1096934499453,"relative_volume":0.15381895528043224,"spread_bps":6.827142015806368,"day_high":1361.44,"day_low":1325.0,"execution_condition_ko":"10:30 이후 1387.46 회복, 거래량가중평균가격 상회 및 상대거래량 1.2 이상 / 1409.71 위 종가와 다음 거래일 첫 30~60분 동안 1387.46 유지","risk_condition_ko":"1,320.8 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":353.83,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":354.3021354151383,"relative_volume":0.2678948805609711,"spread_bps":1.979610016826492,"day_high":357.9,"day_low":352.32,"execution_condition_ko":"361.86 회복과 366.55 상향 돌파 시 정규장 거래량 및 거래량 가중 평균가격 확인 / 375.15 위 종가와 다음 거래일 유지 여부 확인; 자동 매수 신호는 아님","risk_condition_ko":"349.43 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":432.1284,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":431.2774776684888,"relative_volume":0.27487617419047483,"spread_bps":5.091296197728062,"day_high":434.75,"day_low":428.0,"execution_condition_ko":"정규장 437.05 회복 / 10:30 이후 447.33 상회 유지, 상대거래량 1.2 이상 및 거래량 가중 평균가격 상회","risk_condition_ko":"420.1 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":208.985,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":209.34814174972126,"relative_volume":0.38014944540932855,"spread_bps":0.47843456211369173,"day_high":210.0189,"day_low":208.785,"execution_condition_ko":"10:30 이후 RSP가 211.39와 거래량가중평균가격 위에 머물고 상대거래량이 1.2 이상인지 확인 / 211.95 위 종가와 다음 거래일 첫 30~60분의 211.39 지지 확인","risk_condition_ko":"208.47 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":956.1,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":956.875870792952,"relative_volume":0.23215247957636484,"spread_bps":15.983702891169502,"day_high":971.99,"day_low":948.31,"execution_condition_ko":"GEV가 거래량 개선과 함께 968.41 및 973.41 위에서 마감 / GEV가 상대 거래량 1.2 이상으로 988.48 위에서 마감","risk_condition_ko":"944.85 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":250.67,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":250.257492258437,"relative_volume":0.5495782595983749,"spread_bps":1.1947669208865621,"day_high":252.44,"day_low":246.09,"execution_condition_ko":"미국 동부시간 10:30 이후 250.17과 251.34 회복, 당일 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상 / 종가 251.34 상회와 다음 거래일 유지 여부; 256.09 돌파 이후 비용 차감 보상·위험 재평가","risk_condition_ko":"244.24 이하 하락, 거래량 조건 확인 후 (거래량 증가를 동반한 정규장 종가 이탈) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":100.685,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":101.0453708510634,"relative_volume":1.3797090681899253,"spread_bps":0.9931966032667136,"day_high":100.69,"day_low":100.68,"execution_condition_ko":"미 동부시간 10:30 이후 100.68~100.69 유지와 거래량가중평균가격·시간대별 상대 거래량 확인 / 발행사 순자산가치, 보수, 보유자산, 듀레이션, 분배 산식과 일정 및 대체 수단의 세후 수익률 확인","risk_condition_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":82.105,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":82.29581083692239,"relative_volume":0.5563968013398581,"spread_bps":1.218249375647818,"day_high":82.995,"day_low":82.044,"execution_condition_ko":"10:30 이후 84.39와 장중 거래량가중평균가격 동시 회복 및 상대거래량 1.2 이상 / 84.74를 거쳐 85.40 위 정규장 종가와 상대거래량 1.2 이상","risk_condition_ko":"81.32 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":1173.98,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":1187.3129477442333,"relative_volume":0.546896183535361,"spread_bps":13.090229079008573,"day_high":1214.99,"day_low":1170.84,"execution_condition_ko":"기한 내 10:30 이후 1197.79 상향 돌파·유지, 시간 보정 상대거래량 1.2 이상, 거래량가중평균가격 상회 / 1197.79 위 종가와 가급적 270만 주 초과 거래량, 다음 거래일 지지 또는 재돌파","risk_condition_ko":"1,168.47 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":230.63,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":230.53342694878057,"relative_volume":0.4245657204553098,"spread_bps":0.8687719907914614,"day_high":232.37,"day_low":228.8,"execution_condition_ko":"233.21 회복 후 234.14~234.50 돌파·지지와 동시간대 상대거래량 1.2 이상 / 다음 거래일 정규장 첫 30~60분 동안 234.50 유지","risk_condition_ko":"221.71 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":336.51,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":336.475644713848,"relative_volume":0.5151474814455422,"spread_bps":0.5939653124269022,"day_high":339.5,"day_low":330.1401,"execution_condition_ko":"새 정규장 호가와 거래량, 현재 AAPL 보유 비중·현금·거래비용 확인 / 333.99~334.77 회복과 당일 거래량가중평균가격 상회, 상대 거래량 1.2 이상","risk_condition_ko":"328.7 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":542.69,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":544.6988444552976,"relative_volume":0.2423723042932091,"spread_bps":8.996685914678537,"day_high":553.48,"day_low":537.67,"execution_condition_ko":"555.54달러 회복과 당일 거래량가중평균 상회 및 같은 시각 기준 상대거래량 1.2배 이상 확인 / 573.80달러 위 종가 후 다음 거래일 첫 30~60분 유지 여부 확인","risk_condition_ko":"530.45 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":349.21,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":349.5133267853759,"relative_volume":0.565014877636434,"spread_bps":2.002202422664736,"day_high":352.6,"day_low":344.08,"execution_condition_ko":"345.42 회복 후 349.91 위에서 당일 거래량가중평균가 지지와 동시간대 상대거래량 1.2 이상 확인 / 354.66을 거래량과 함께 종가 돌파하고 다음 거래일 지지; 359.44와 364.17 저항 확인","risk_condition_ko":"337.45 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"JNJ","display_name":"JNJ","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":266.885,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":280.72507563357766,"relative_volume":0.19644545873336022,"spread_bps":2.994908655287546,"day_high":268.48,"day_low":265.96,"execution_condition_ko":"다음 정규장 10:30 이후 265.08~263.26 지지 확인 뒤 269.92와 거래량가중평균가격 회복, 상대 거래량 1.2 이상 / 상대 거래량 1.2 이상으로 275.23 위 마감 후 다음 거래일 첫 30~60분간 해당 가격 유지","risk_condition_ko":"263.26 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"SCCO","display_name":"SCCO","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":203.2024,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":205.88215427673498,"relative_volume":0.45095392657778405,"spread_bps":15.779870802307471,"day_high":211.075,"day_low":201.7,"execution_condition_ko":"199.44–200.00의 실시간 지지 회복과 적정 호가 차이 / 205.41 상향 돌파 및 206.14 위 마감 여부","risk_condition_ko":"195.75 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"LRCX","display_name":"Lam Research","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":327.61,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":325.5242790955929,"relative_volume":0.23798626845950488,"spread_bps":9.479107740761762,"day_high":328.12,"day_low":322.06,"execution_condition_ko":"10:30 이후 328.32 및 당일 거래량가중평균가격 위 유지와 같은 시각 기준 상대거래량 1.2 이상 / 332.93 위 종가와 다음 거래일 지지 또는 재돌파","risk_condition_ko":"319.15 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":192.04,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":192.69545929138295,"relative_volume":0.23952136117670714,"spread_bps":4.674960392696851,"day_high":195.22,"day_low":191.79,"execution_condition_ko":"정규장에서 195.49 초과 유지, 거래량가중평균가격 상회 및 동시간대 상대거래량 1.2 이상 / 196.34 위 종가 후 다음 거래일 초반 195.49 유지","risk_condition_ko":"190.12 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":500.79998779296875,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":500.4296157917048,"relative_volume":0.657275255236191,"spread_bps":null,"day_high":502.1199951171875,"day_low":499.0799865722656,"execution_condition_ko":"최신 정규장 가격의 500.23 및 502.35 회복, 실시간 거래량가중평균가격 지지, 동시간대 상대거래량 1.2 이상 / 거래량을 동반한 506.76 위 종가와 다음 거래일 유지; 이후 저항선 509.05","risk_condition_ko":"497.83 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":263.4689,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":263.7652749913768,"relative_volume":0.16390900634469222,"spread_bps":4.552179355866794,"day_high":265.1603,"day_low":262.89,"execution_condition_ko":"ABBV가 269.39 위를 유지하고 시각 보정 상대 거래량 1.2 이상과 당일 거래량가중평균가격 상회를 충족하는지 확인 / ABBV가 270.78 위에서 마감한 뒤 다음 거래일 첫 30~60분 동안 269.39를 지키는지 확인","risk_condition_ko":"261.52 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":146.61,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":147.25644123378416,"relative_volume":0.3039232074268938,"spread_bps":2.0439448134901133,"day_high":149.05,"day_low":146.57,"execution_condition_ko":"10:30 이후 149.57 상회 유지, 거래량가중평균가격 상회, 상대거래량 1.2 이상 / 149.57 위 일일 종가와 다음 거래일 첫 30~60분 지지 유지","risk_condition_ko":"145.87 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"WBD","display_name":"WBD","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":30.805,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":30.82477789093521,"relative_volume":1.2243252189517206,"spread_bps":3.2462262619698135,"day_high":30.86,"day_low":30.8,"execution_condition_ko":"30.92달러 위 종가, 시간대별 상대 거래량 1.2 이상, 다음 거래일 지지 확인 / 30.90~30.92달러에서 반복적인 거부","risk_condition_ko":"30.9 이상 도달, 장중 확인 시 (실시간 가격 확인) 이익실현성 축소 · 추가 조건 확인 필요: 30.90~30.92달러 저항 재시험에서 거부가 확인되거나 보유 비중이 높을 때","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":163.965,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":163.3111617640036,"relative_volume":0.2683911998541766,"spread_bps":1.8264284192262723,"day_high":164.3699,"day_low":161.93,"execution_condition_ko":"신선한 정규장 가격이 163.32와 당일 거래량가중평균가격 위에서 유지되고 상대거래량 1.2 이상 / 164.91 상향 종가 후 다음 확인된 거래일 첫 30~60분간 164.91 유지 또는 회복; 저항 168.12와 169.64 대비 보상·위험 재평가","risk_condition_ko":"159.27 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":206.4345,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":205.7297157976047,"relative_volume":0.2287512940543163,"spread_bps":1.9344230583238449,"day_high":206.8262,"day_low":204.25,"execution_condition_ko":"200.78~201.17 지지 후 202.70 회복과 실시간 거래량가중평균가격·상대 거래량 확인 / 205.48 및 206.43 회복","risk_condition_ko":"200.78 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":95.65,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":95.24006627508966,"relative_volume":0.7838353102325871,"spread_bps":1.0453143782998084,"day_high":95.775,"day_low":94.9,"execution_condition_ko":"$95.36 및 $95.78 회복 여부 / 10:30 이후 $96.47 돌파와 실시간 거래량가중평균가 지지 및 상대 거래량 1.2 이상","risk_condition_ko":"94.72 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"SPYM","display_name":"SPYM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":90.31,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":90.33791141815854,"relative_volume":0.8390061063838455,"spread_bps":1.1068681166628929,"day_high":90.55,"day_low":90.16,"execution_condition_ko":"미국 동부시간 10:30 이후 90.15와 90.41 위 유지, 거래량가중평균가격 상회, 상대 거래량 1.2 이상 / 90.89와 91.22 위 마감 및 91.31 저항 반응","risk_condition_ko":"89.55 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"MRK","display_name":"MRK","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":147.06,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":147.14358832322685,"relative_volume":0.4038773204147149,"spread_bps":2.0449200777070407,"day_high":149.27,"day_low":146.22,"execution_condition_ko":"2026-10-02 16:00 미국 동부시간까지 147.07 부근 재시험, 147.25 이하, 10:30 이후 당일 거래량가중평균가격 유지와 동시간대 상대거래량 1.2 이상 / 150.36 회복 후 152.64 위 종가와 약 1,165만 주 이상 거래량","risk_condition_ko":"146.09 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"INTC","display_name":"INTC","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":119.4468,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":118.75258813703101,"relative_volume":0.4857240969998135,"spread_bps":1.6708437761066017,"day_high":120.41,"day_low":116.0,"execution_condition_ko":"113.97~114.71 지지 유지와 115.87 재돌파 / 118.75 회복 후 121.71 상회, 실시간 거래량가중평균가격 지지 및 동시간대 상대거래량 1.2 이상","risk_condition_ko":"112.27 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":556.22,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":556.5544765569912,"relative_volume":0.4130620221165035,"spread_bps":5.389479735555377,"day_high":562.26,"day_low":554.085,"execution_condition_ko":"실시간 $553.12~$553.84 지지 확인 후 $561.30 및 거래량가중평균가격 회복 / 상대거래량 1.2 이상을 동반한 $565.85, 이어서 $569.64 상향 종가","risk_condition_ko":"553.12 이하 하락, 종가 확인 후 (거래량 증가 확인) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

```json
{"ticker":"MRVL","display_name":"Marvell Technology","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":262.54,"market_data_asof":"2026-09-30T14:10:00-04:00","session_vwap":260.09933791843895,"relative_volume":0.27447987151846925,"spread_bps":3.4345246045516995,"day_high":265.0,"day_low":256.24,"execution_condition_ko":"9월 30일 10:30 이후 267.48 위 5분봉 2개, 당일 거래량 가중 평균가격 지지, 동시간대 상대 거래량 1.0 이상 확인 / 267.48 위 정규장 종가와 거래량 18.16백만 주 초과 후 다음 거래일 초반 지지 또는 재돌파 확인","risk_condition_ko":"256.88 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T14:40:00-04:00"}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-01T03:18:41.497176+09:00",
  "as_of": "2026-09-30T13:10:00-04:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
