# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-01T01:00:49.980430+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261001T074058_github-actions-overlay-us",
  "producer_finished_at": "2026-10-01T07:41:34.736562+09:00",
  "analysis_run_id": "20261001T000500_github-actions-us",
  "analysis_completed_at": "2026-10-01T00:32:08.634901+09:00",
  "analysis_trade_date_oldest": "2026-09-29",
  "analysis_trade_date_latest": "2026-09-29",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-09-30T15:10:00-04:00",
  "market_data_latest_at": "2026-09-30T15:10:00-04:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-01T07:41:32.213796+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23971170,
    "total_market_value_krw": 24896521,
    "total_unrealized_pnl_krw": 925351,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 87019,
    "total_equity_krw": 25960192
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 553778,
      "current_price_krw": 619688,
      "market_value_krw": 7436261,
      "unrealized_pnl_krw": 790914
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 296817,
      "current_price_krw": 282574,
      "market_value_krw": 3108318,
      "unrealized_pnl_krw": -156676
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 430516,
      "current_price_krw": 467398,
      "market_value_krw": 2804389,
      "unrealized_pnl_krw": 221293
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 271254,
      "current_price_krw": 310231,
      "market_value_krw": 1861388,
      "unrealized_pnl_krw": 233863
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1908198,
      "current_price_krw": 1830063,
      "market_value_krw": 1830063,
      "unrealized_pnl_krw": -78135
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 564276,
      "current_price_krw": 583718,
      "market_value_krw": 1751154,
      "unrealized_pnl_krw": 58326
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1494973,
      "current_price_krw": 1291145,
      "market_value_krw": 1291145,
      "unrealized_pnl_krw": -203828
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
      "current_price_krw": 452374,
      "market_value_krw": 904748,
      "unrealized_pnl_krw": 164655
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 672686,
      "current_price_krw": 730751,
      "market_value_krw": 730751,
      "unrealized_pnl_krw": 58065
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1441275,
      "current_price_krw": 1571777,
      "market_value_krw": 685397,
      "unrealized_pnl_krw": 56907
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 578168,
      "current_price_krw": 477056,
      "market_value_krw": 477056,
      "unrealized_pnl_krw": -101112
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 138255,
      "current_price_krw": 111633,
      "market_value_krw": 446533,
      "unrealized_pnl_krw": -106489
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 352966,
      "current_price_krw": 338445,
      "market_value_krw": 338445,
      "unrealized_pnl_krw": -14521
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":82.115,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":82.27993337007165,"relative_volume":0.7481404514607407,"spread_bps":1.2181009805701815,"day_high":82.995,"day_low":82.044,"execution_condition_ko":"10:30 이후 84.39와 장중 거래량가중평균가격 동시 회복 및 상대거래량 1.2 이상 / 84.74를 거쳐 85.40 위 정규장 종가와 상대거래량 1.2 이상","risk_condition_ko":"81.32 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":457.425,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":458.4390473984118,"relative_volume":0.22562967810591827,"spread_bps":2.844358870570632,"day_high":461.87,"day_low":454.9,"execution_condition_ko":"2026-09-30 10:30 이후 459.43 상회 유지, 당일 거래량가중평균가격 상회 및 같은 시각 기준 상대 거래량 1.2 이상 / 463.72 위 거래량 동반 종가와 다음 거래일 지지 확인","risk_condition_ko":"447.07 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1339.47,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":1337.5439785784497,"relative_volume":0.14749088155228843,"spread_bps":15.099782518057696,"day_high":1361.44,"day_low":1325.0,"execution_condition_ko":"10:30 이후 1387.46 회복, 거래량가중평균가격 상회 및 상대거래량 1.2 이상 / 1409.71 위 종가와 다음 거래일 첫 30~60분 동안 1387.46 유지","risk_condition_ko":"1,320.8 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":353.66,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":354.2459567034784,"relative_volume":0.24285285287298145,"spread_bps":2.545428834053082,"day_high":357.9,"day_low":352.32,"execution_condition_ko":"361.86 회복과 366.55 상향 돌파 시 정규장 거래량 및 거래량 가중 평균가격 확인 / 375.15 위 종가와 다음 거래일 유지 여부 확인; 자동 매수 신호는 아님","risk_condition_ko":"349.43 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":433.0265,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":431.51231197812507,"relative_volume":0.297127350448334,"spread_bps":12.248246536404551,"day_high":434.75,"day_low":428.0,"execution_condition_ko":"정규장 437.05 회복 / 10:30 이후 447.33 상회 유지, 상대거래량 1.2 이상 및 거래량 가중 평균가격 상회","risk_condition_ko":"420.1 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":208.74,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":209.2626427015154,"relative_volume":0.361606734237413,"spread_bps":0.47926002252478517,"day_high":210.0189,"day_low":208.58,"execution_condition_ko":"10:30 이후 RSP가 211.39와 거래량가중평균가격 위에 머물고 상대거래량이 1.2 이상인지 확인 / 211.95 위 종가와 다음 거래일 첫 30~60분의 211.39 지지 확인","risk_condition_ko":"208.47 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":954.975,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":956.5809930534433,"relative_volume":0.21674953432398045,"spread_bps":11.315298702931928,"day_high":971.99,"day_low":948.31,"execution_condition_ko":"GEV가 거래량 개선과 함께 968.41 및 973.41 위에서 마감 / GEV가 상대 거래량 1.2 이상으로 988.48 위에서 마감","risk_condition_ko":"944.85 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":250.15,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":250.2603729269703,"relative_volume":0.5206731400181388,"spread_bps":0.7995522507399949,"day_high":252.44,"day_low":246.09,"execution_condition_ko":"미국 동부시간 10:30 이후 250.17과 251.34 회복, 당일 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상 / 종가 251.34 상회와 다음 거래일 유지 여부; 256.09 돌파 이후 비용 차감 보상·위험 재평가","risk_condition_ko":"244.24 이하 하락, 거래량 조건 확인 후 (거래량 증가를 동반한 정규장 종가 이탈) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.6801,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":100.99662260070097,"relative_volume":1.3154988809004087,"spread_bps":0.9931966032667136,"day_high":100.69,"day_low":100.68,"execution_condition_ko":"미 동부시간 10:30 이후 100.68~100.69 유지와 거래량가중평균가격·시간대별 상대 거래량 확인 / 발행사 순자산가치, 보수, 보유자산, 듀레이션, 분배 산식과 일정 및 대체 수단의 세후 수익률 확인","risk_condition_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1162.65,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":1184.4121339045303,"relative_volume":0.5288057567582183,"spread_bps":4.1147324566668795,"day_high":1214.99,"day_low":1159.16,"execution_condition_ko":"기한 내 10:30 이후 1197.79 상향 돌파·유지, 시간 보정 상대거래량 1.2 이상, 거래량가중평균가격 상회 / 1197.79 위 종가와 가급적 270만 주 초과 거래량, 다음 거래일 지지 또는 재돌파","risk_condition_ko":"1,168.47 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":230.68,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":230.5394859558154,"relative_volume":0.3878623210849776,"spread_bps":0.8682816705731445,"day_high":232.37,"day_low":228.8,"execution_condition_ko":"233.21 회복 후 234.14~234.50 돌파·지지와 동시간대 상대거래량 1.2 이상 / 다음 거래일 정규장 첫 30~60분 동안 234.50 유지","risk_condition_ko":"221.71 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":336.27,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":336.47269493606973,"relative_volume":0.46845833295339473,"spread_bps":1.188707280831014,"day_high":339.5,"day_low":330.1401,"execution_condition_ko":"새 정규장 호가와 거래량, 현재 AAPL 보유 비중·현금·거래비용 확인 / 333.99~334.77 회복과 당일 거래량가중평균가격 상회, 상대 거래량 1.2 이상","risk_condition_ko":"328.7 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":545.02,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":544.5672025629912,"relative_volume":0.23549050027960367,"spread_bps":6.076956365612546,"day_high":553.48,"day_low":537.67,"execution_condition_ko":"555.54달러 회복과 당일 거래량가중평균 상회 및 같은 시각 기준 상대거래량 1.2배 이상 확인 / 573.80달러 위 종가 후 다음 거래일 첫 30~60분 유지 여부 확인","risk_condition_ko":"530.45 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":348.98,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":349.4810134573459,"relative_volume":0.5097409513073727,"spread_bps":1.1453441759238236,"day_high":352.6,"day_low":344.08,"execution_condition_ko":"345.42 회복 후 349.91 위에서 당일 거래량가중평균가 지지와 동시간대 상대거래량 1.2 이상 확인 / 354.66을 거래량과 함께 종가 돌파하고 다음 거래일 지지; 359.44와 364.17 저항 확인","risk_condition_ko":"337.45 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"JNJ","display_name":"JNJ","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":265.6,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":278.2937078401586,"relative_volume":0.19441075294563645,"spread_bps":3.761661149562364,"day_high":268.48,"day_low":265.535,"execution_condition_ko":"다음 정규장 10:30 이후 265.08~263.26 지지 확인 뒤 269.92와 거래량가중평균가격 회복, 상대 거래량 1.2 이상 / 상대 거래량 1.2 이상으로 275.23 위 마감 후 다음 거래일 첫 30~60분간 해당 가격 유지","risk_condition_ko":"263.26 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"SCCO","display_name":"SCCO","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":202.19,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":205.57944009768894,"relative_volume":0.40684788984242864,"spread_bps":22.764388578215865,"day_high":211.075,"day_low":201.69,"execution_condition_ko":"199.44–200.00의 실시간 지지 회복과 적정 호가 차이 / 205.41 상향 돌파 및 206.14 위 마감 여부","risk_condition_ko":"195.75 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"LRCX","display_name":"Lam Research","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":329.195,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":326.0500028320856,"relative_volume":0.24368829299603437,"spread_bps":7.015296396273297,"day_high":329.34,"day_low":322.06,"execution_condition_ko":"10:30 이후 328.32 및 당일 거래량가중평균가격 위 유지와 같은 시각 기준 상대거래량 1.2 이상 / 332.93 위 종가와 다음 거래일 지지 또는 재돌파","risk_condition_ko":"319.15 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":191.89,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":192.4206410610666,"relative_volume":0.253521430536377,"spread_bps":3.650872297703685,"day_high":195.22,"day_low":190.87,"execution_condition_ko":"정규장에서 195.49 초과 유지, 거래량가중평균가격 상회 및 동시간대 상대거래량 1.2 이상 / 196.34 위 종가 후 다음 거래일 초반 195.49 유지","risk_condition_ko":"190.12 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":499.5249938964844,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":500.3252713639415,"relative_volume":0.6812814427818611,"spread_bps":null,"day_high":502.1199951171875,"day_low":498.79998779296875,"execution_condition_ko":"최신 정규장 가격의 500.23 및 502.35 회복, 실시간 거래량가중평균가격 지지, 동시간대 상대거래량 1.2 이상 / 거래량을 동반한 506.76 위 종가와 다음 거래일 유지; 이후 저항선 509.05","risk_condition_ko":"497.83 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":262.84,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":263.61060604731347,"relative_volume":0.17341069404639442,"spread_bps":7.223647942210731,"day_high":265.1603,"day_low":262.67,"execution_condition_ko":"ABBV가 269.39 위를 유지하고 시각 보정 상대 거래량 1.2 이상과 당일 거래량가중평균가격 상회를 충족하는지 확인 / ABBV가 270.78 위에서 마감한 뒤 다음 거래일 첫 30~60분 동안 269.39를 지키는지 확인","risk_condition_ko":"261.52 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":146.055,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":147.0811250283663,"relative_volume":0.3088178763712046,"spread_bps":2.0524749427018185,"day_high":149.05,"day_low":145.99,"execution_condition_ko":"10:30 이후 149.57 상회 유지, 거래량가중평균가격 상회, 상대거래량 1.2 이상 / 149.57 위 일일 종가와 다음 거래일 첫 30~60분 지지 유지","risk_condition_ko":"145.87 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"WBD","display_name":"WBD","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":30.79,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":30.822752183779045,"relative_volume":1.088683234259276,"spread_bps":3.2472804026632773,"day_high":30.86,"day_low":30.79,"execution_condition_ko":"30.92달러 위 종가, 시간대별 상대 거래량 1.2 이상, 다음 거래일 지지 확인 / 30.90~30.92달러에서 반복적인 거부","risk_condition_ko":"30.9 이상 도달, 장중 확인 시 (실시간 가격 확인) 이익실현성 축소 · 추가 조건 확인 필요: 30.90~30.92달러 저항 재시험에서 거부가 확인되거나 보유 비중이 높을 때","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":163.51,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":163.3698907444901,"relative_volume":0.2579934326553703,"spread_bps":0.6115272894047334,"day_high":164.3699,"day_low":161.93,"execution_condition_ko":"신선한 정규장 가격이 163.32와 당일 거래량가중평균가격 위에서 유지되고 상대거래량 1.2 이상 / 164.91 상향 종가 후 다음 확인된 거래일 첫 30~60분간 164.91 유지 또는 회복; 저항 168.12와 169.64 대비 보상·위험 재평가","risk_condition_ko":"159.27 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":205.705,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":205.79054506903628,"relative_volume":0.22831499488226784,"spread_bps":2.4286581663636366,"day_high":206.8262,"day_low":204.25,"execution_condition_ko":"200.78~201.17 지지 후 202.70 회복과 실시간 거래량가중평균가격·상대 거래량 확인 / 205.48 및 206.43 회복","risk_condition_ko":"200.78 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":95.56,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":95.33769538103508,"relative_volume":0.8144702823910306,"spread_bps":1.04520512150563,"day_high":95.85,"day_low":94.9,"execution_condition_ko":"$95.36 및 $95.78 회복 여부 / 10:30 이후 $96.47 돌파와 실시간 거래량가중평균가 지지 및 상대 거래량 1.2 이상","risk_condition_ko":"94.72 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"SPYM","display_name":"SPYM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":90.2341,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":90.31692670373664,"relative_volume":0.8632708658873383,"spread_bps":1.1089548100920559,"day_high":90.55,"day_low":90.15,"execution_condition_ko":"미국 동부시간 10:30 이후 90.15와 90.41 위 유지, 거래량가중평균가격 상회, 상대 거래량 1.2 이상 / 90.89와 91.22 위 마감 및 91.31 저항 반응","risk_condition_ko":"89.55 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"MRK","display_name":"MRK","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":145.93,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":147.00476085217602,"relative_volume":0.40344085573007377,"spread_bps":2.7416038382448287,"day_high":149.27,"day_low":145.808,"execution_condition_ko":"2026-10-02 16:00 미국 동부시간까지 147.07 부근 재시험, 147.25 이하, 10:30 이후 당일 거래량가중평균가격 유지와 동시간대 상대거래량 1.2 이상 / 150.36 회복 후 152.64 위 종가와 약 1,165만 주 이상 거래량","risk_condition_ko":"146.09 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"INTC","display_name":"INTC","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":119.85,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":118.81659736326124,"relative_volume":0.4529467987218589,"spread_bps":1.6844942306069253,"day_high":120.41,"day_low":116.0,"execution_condition_ko":"113.97~114.71 지지 유지와 115.87 재돌파 / 118.75 회복 후 121.71 상회, 실시간 거래량가중평균가격 지지 및 동시간대 상대거래량 1.2 이상","risk_condition_ko":"112.27 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":553.495,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":556.1950482666208,"relative_volume":0.40740619057908195,"spread_bps":1.9880895363235458,"day_high":562.26,"day_low":553.07,"execution_condition_ko":"실시간 $553.12~$553.84 지지 확인 후 $561.30 및 거래량가중평균가격 회복 / 상대거래량 1.2 이상을 동반한 $565.85, 이어서 $569.64 상향 종가","risk_condition_ko":"553.12 이하 하락, 종가 확인 후 (거래량 증가 확인) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
```

```json
{"ticker":"MRVL","display_name":"Marvell Technology","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":263.225,"market_data_asof":"2026-09-30T15:10:00-04:00","session_vwap":260.3515152729427,"relative_volume":0.2520491549628814,"spread_bps":5.338417540514255,"day_high":265.0,"day_low":256.24,"execution_condition_ko":"9월 30일 10:30 이후 267.48 위 5분봉 2개, 당일 거래량 가중 평균가격 지지, 동시간대 상대 거래량 1.0 이상 확인 / 267.48 위 정규장 종가와 거래량 18.16백만 주 초과 후 다음 거래일 초반 지지 또는 재돌파 확인","risk_condition_ko":"256.88 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":false,"row_valid_until":"2026-09-30T15:40:00-04:00"}}
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
