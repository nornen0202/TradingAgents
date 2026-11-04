# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-11-04T17:29:05.459554+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261105T022657_local-freshness-us-overlay",
  "producer_finished_at": "2026-11-05T02:28:09.856988+09:00",
  "analysis_run_id": "20261104T175053_local-scheduler-us-full",
  "analysis_completed_at": "2026-11-04T21:07:57.017629+09:00",
  "analysis_trade_date_oldest": "2026-11-03",
  "analysis_trade_date_latest": "2026-11-03",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-11-04T12:10:00-05:00",
  "market_data_latest_at": "2026-11-04T17:26:53+00:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-11-05T02:01:54.671303+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-11-05T02:01:54.671303+09:00",
    "run_started_at": "2026-11-05T02:01:13.908539+09:00",
    "run_finished_at": "2026-11-05T02:02:01.959547+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23667667,
    "total_market_value_krw": 22692706,
    "total_unrealized_pnl_krw": -974961,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 108181,
    "total_equity_krw": 23777232
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 546767,
      "current_price_krw": 534917,
      "market_value_krw": 6419010,
      "unrealized_pnl_krw": -142194
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 293059,
      "current_price_krw": 298913,
      "market_value_krw": 3288045,
      "unrealized_pnl_krw": 64392
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 425064,
      "current_price_krw": 391174,
      "market_value_krw": 2347047,
      "unrealized_pnl_krw": -203342
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1884037,
      "current_price_krw": 1724126,
      "market_value_krw": 1724126,
      "unrealized_pnl_krw": -159911
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 267819,
      "current_price_krw": 273189,
      "market_value_krw": 1639134,
      "unrealized_pnl_krw": 32216
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 557131,
      "current_price_krw": 479361,
      "market_value_krw": 1438084,
      "unrealized_pnl_krw": -233309
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 134806,
      "current_price_krw": 134723,
      "market_value_krw": 1212511,
      "unrealized_pnl_krw": -743
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1476044,
      "current_price_krw": 1106275,
      "market_value_krw": 1106275,
      "unrealized_pnl_krw": -369769
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 365361,
      "current_price_krw": 474610,
      "market_value_krw": 949220,
      "unrealized_pnl_krw": 218498
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1423028,
      "current_price_krw": 1918693,
      "market_value_krw": 836675,
      "unrealized_pnl_krw": 216142
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 664168,
      "current_price_krw": 502815,
      "market_value_krw": 502815,
      "unrealized_pnl_krw": -161353
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 570848,
      "current_price_krw": 439772,
      "market_value_krw": 439772,
      "unrealized_pnl_krw": -131076
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 136505,
      "current_price_krw": 107725,
      "market_value_krw": 430900,
      "unrealized_pnl_krw": -115120
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 348497,
      "current_price_krw": 359092,
      "market_value_krw": 359092,
      "unrealized_pnl_krw": 10595
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":203.47,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":203.92779082301809,"relative_volume":1.044213417049648,"spread_bps":0.9828492800634051,"day_high":206.79,"day_low":200.94,"execution_condition_ko":"위험 대응 조건: 204.27 이하 하락, 다음 거래일 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"204.27 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":223.3,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":222.1395791074451,"relative_volume":1.0312844611042757,"spread_bps":0.44781800676164457,"day_high":223.305,"day_low":221.07,"execution_condition_ko":"217.15~217.94 시험과 종가 217.94 이상 회복, 다음 실제 거래세션 지지 재확인 후 실행 구간과 비용 조건을 충족하면 소규모 첫 진입 후보로 전환한다. / 220.95 초과 종가와 다음 거래세션 재지지는 강세 확인용이며 독립적인 매수 승인은 아니다.","risk_condition_ko":"217.15 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1279.435,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":1300.2339576666764,"relative_volume":0.8154767897979864,"spread_bps":33.37410653921443,"day_high":1335.1,"day_low":1213.5,"execution_condition_ko":"2026-11-04 이후 실제 거래일의 새로운 지지 확인을 관찰한다. 2026-11-03 종가만으로 신규 조건이 충족된 것은 아니다. / 1360.97–1369.80, 1378.58–1386.29, 1425.98–1439.73에서 추세와 보상 여력을 재평가한다. 확정 목표가나 상시 매도주문이 아니다.","risk_condition_ko":"1,273.19 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":822.2703,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":832.1623433131842,"relative_volume":1.5748400498362956,"spread_bps":15.086626435662948,"day_high":879.0365,"day_low":806.4001,"execution_condition_ko":"881.90~886.61 시험, 886.61 이상 확정 종가 회복, 다음 실제 세션 재시험 지지와 구간 내 체결 가능 여부를 순서대로 확인한다. / 929.77~932.15 회복 시 참여 확대를 보조 확인하되 가격에서 파생된 여러 지표를 독립 호재로 중복 계산하지 않는다.","risk_condition_ko":"878.75 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":355.22,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":359.14436788905493,"relative_volume":1.2873837585416756,"spread_bps":7.319407691009733,"day_high":378.23,"day_low":351.5,"execution_condition_ko":"지지대 시험, 384.05 이상 회복 종가, 다음 실제 정규 세션의 383.58 이상 종가 지지를 순서대로 확인한다. 확인 완료 후에도 구간으로 돌아오지 않으면 거래하지 않는다. / 395.63~396.09와 399.30~400에서 저항 대응을 관찰하고 409.73 부근에서는 추세와 보상·위험을 재평가한다. 돌파만으로 추가 편입하지 않는다.","risk_condition_ko":"383.58 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:news_halt_status"],"provider_blockers":null}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":100.445,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":100.44516847904512,"relative_volume":1.1050039039422064,"spread_bps":0.9955697147697861,"day_high":100.45,"day_low":100.44,"execution_condition_ko":"100.42~100.44 지지, 새 일봉 100.45 이상 종가, 다음 확인된 거래일 100.42~100.45 재지지를 순서대로 점검한다. 가격 조건만으로 매수하지 않는다. / 2026-11-03 기준 50일 평균 100.5361은 보조 회복 참고값이며 사용 전 갱신한다. 고정 매도선이나 이익실현 목표가 아니고, 같은 월초 갭을 반영하는 다른 지표와 독립 악재로 중복 집계하지 않는다.","risk_condition_ko":"100.42 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":268.06,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":267.39980703884737,"relative_volume":1.7329337832507898,"spread_bps":2.6110147522330958,"day_high":271.49,"day_low":263.85,"execution_condition_ko":"판단시각 2026-11-04T04:13:06.087253-05:00은 만료 2026-11-11T23:59:59-05:00 이전이다. 최초 활성화에는 판단시각 이후의 지지 시험·회복 종가·후속 거래일 확인이 필요하다. 만료 전이라는 사실은 세션 존재나 신호 충족을 증명하지 않는다. / 2026-11-03 종가 250.69를 일봉 기준값으로 사용한다. 토론의 야간 표시가격 250.69와 거래량 0은 신규 신호에서 제외한다. 진입 전에 실제 거래 일정, 거래정지 여부, 가격 신선도와 일봉 확정 여부를 확인한다.","risk_condition_ko":"243.5 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1429.015,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":1423.5609722841723,"relative_volume":0.7809223789751204,"spread_bps":6.787892359422591,"day_high":1445.96,"day_low":1401.59,"execution_condition_ko":"1382.02–1393.47 신규 시험, 1393.47 이상 정규장 종가 회복, 다음 검증 거래일 지지 유지와 구간 내 체결 가능성을 순서대로 확인한다. / 1437.00–1449.68은 기존 보유분의 저항 관찰구간이다. 확인되지 않은 돌파를 추격하거나 1449.68 위 목표를 임의로 만들지 않는다.","risk_condition_ko":"1,382.02 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":328.41,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":328.3862425945227,"relative_volume":0.7670227229597621,"spread_bps":6.090133982947279,"day_high":334.12,"day_low":321.74,"execution_condition_ko":"333.75~335.74 회복과 다음 실제 거래일 지지 유지는 관찰 강화 및 약세 판단 재점검 신호이며 자동 매수 조건이 아니다. / 326.60 아래 완료 종가에서 누적 최소 50% 감축, 319.30 아래 완료 종가에서 전략 잔여분 손절 청산을 적용한다.","risk_condition_ko":"326.6 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":398.39,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":399.77899561667,"relative_volume":0.8117691230712015,"spread_bps":7.27939053930152,"day_high":410.5899,"day_low":391.6103,"execution_condition_ko":"TSM의 398.29–400.12 지지를 관찰한다. 중립 분석가가 지적한 이전 장기 이동평균 이탈과 이후 하루의 회복을 고려하면 지지의 지속성은 아직 확정되지 않았다. / 408.37–410.22는 초기 저항일 뿐 매수 신호가 아니다. 핵심 재평가 조건은 418.44 초과 종가와 다음 확인된 거래일의 지지·종가 확인이다.","risk_condition_ko":"398.29 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":["feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":376.775,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":380.162425828366,"relative_volume":1.100674217583873,"spread_bps":7.1660805520546385,"day_high":394.485,"day_low":366.96,"execution_condition_ko":"391.25 종가 이탈과 391.25~394.49 재시험 후 회복 실패를 확인해 누적 축소 목표를 조정한다. 377.10 종가 이탈과 기존 장중 손절 충족은 별도로 확인한다. / 408.40 저항, 424.30 상회 종가, 다음 실제 거래일의 418.17~424.30 지지를 관찰한다. 회복은 재평가 신호이며 자동 매수나 축소 중단 지시가 아니다.","risk_condition_ko":"391.25 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":353.065,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":350.6313356570805,"relative_volume":1.479278182402642,"spread_bps":2.832219327065332,"day_high":354.47,"day_low":340.99,"execution_condition_ko":"334.50 위 완료 일봉과 다음 실제 거래일 334.05~334.50 지지를 확인하면 미실행 감축을 재평가한다. 이는 신규 매수 승인과 구별한다. / 회복 실패 또는 325.33 아래 종가에서는 추가 감축·손절을 우선하고 거래량 확인을 기다리지 않는다.","risk_condition_ko":"334.05 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":291.77,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":290.6022901045365,"relative_volume":1.2953628531259667,"spread_bps":1.0281542916883857,"day_high":296.49,"day_low":283.51,"execution_condition_ko":"276.92~277.20 지지 후보의 종가 방어와 276.92 미만 종가를 구분해 관찰한다. / 302.45~306.04의 실제 시험, 종가 302.45 미만의 실패, 종가 306.04 초과 및 다음 검증된 거래일의 지지 전환을 각각 구분한다.","risk_condition_ko":"302.45 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":80.405,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":80.00247461070853,"relative_volume":0.6884470336782634,"spread_bps":1.2437037497656742,"day_high":80.44,"day_low":79.69,"execution_condition_ko":"다음 확인된 거래일에 점검하고 2026-11-11 미 동부시간까지 재평가한다. 이는 검토 기한이며 주문 만료나 특정 장 마감 시각이 아니다. / 의사결정 시각 2026-11-04T04:34:16.507727-05:00은 04:10 장전 관측값 80.00을 갱신하지 않는다. 거래일·정규장 운영·조기폐장 여부와 실행 호가의 시점을 별도로 확인한다.","risk_condition_ko":"79.15 이하 하락, 장중 확인 시 (위험 축소에 거래량 확인은 필요하지 않다.) 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"BRK-A","display_name":"BRK-A","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":860664.5,"market_data_asof":"2026-11-04T12:10:00-05:00","session_vwap":853102.5845085469,"relative_volume":2.2128142458100557,"spread_bps":null,"day_high":861264.8125,"day_low":844952.75,"execution_condition_ko":"다음 1–3개 검증된 거래일 동안 재검토하되 조건부 진입 의사는 2026-11-11T16:00:00-05:00에 만료한다. 이는 관리자가 정한 기한이지 확인된 거래소 폐장시각이 아니며 자동 연장하지 않는다. / 판단시각 2026-11-04T05:24:36.671137-05:00에서 위 만료시각은 아직 미래다. 다만 현재 거래 세션, 휴장·단축장 여부와 진입 조건 충족은 별도 확인이 필요하다.","risk_condition_ko":"824,765 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-11-04T12:10:00-05:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-11-04T12:12:00-05:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":210.455,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":210.73350229900728,"relative_volume":0.3854531930497012,"spread_bps":9.972693814555761,"day_high":214.26,"day_low":209.095,"execution_condition_ko":"2026-11-03 이후 추가 일봉의 205.02 지지 유지와 205.57 이상 마감, 이후 정규 세션의 205.57~206.00 실행가격을 순서대로 확인한다. / 공시 최소 검토를 통과해도 하락 중 지정가를 기계적으로 체결하지 않는다. 실행 시 지지와 새로운 중요 공시를 다시 확인한다.","risk_condition_ko":"205.02 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":167.81,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":166.8481888506182,"relative_volume":0.6847555739815293,"spread_bps":1.1913981056759284,"day_high":168.16,"day_low":164.82,"execution_condition_ko":"최근 중요 공시의 내용, 포트폴리오 집중도와 가용자금, 거래 상태 및 호가를 먼저 확인한다. 중요하지 않은 모든 공급업체 불일치의 완전 해소를 무기한 요구하지는 않되 미조정 재무수치를 매수 근거로 쓰지 않는다. / 160.03~160.30 시험, 160.30 이상 종가, 다음 확인된 거래일의 성공적인 재시험을 순서대로 확인한다. 구간을 벗어나 상승하면 추격하지 않는다.","risk_condition_ko":"160.03 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":573.238,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":569.1974608278942,"relative_volume":0.8329877245919848,"spread_bps":1.9189337706178733,"day_high":574.575,"day_low":562.5,"execution_condition_ko":"559.58 초과 종가 이후 다음 실제 거래일의 재시험 지지를 확인한다. 확인 자료나 559.58~559.60 체결 기회가 없으면 대기하며, 최초 활성화 조건과 만료 기한을 구분한다. / 550.47~551.81 지지 실패는 신규 매수보다 기존 보유의 위험 축소를 우선할 신호다. 위험 축소에 신규 매수용 거래량이나 가용현금 조건을 적용하지 않는다.","risk_condition_ko":"550.47 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":104.83,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":104.14082079820032,"relative_volume":0.2848599547601315,"spread_bps":1.9080328181640929,"day_high":105.225,"day_low":99.8,"execution_condition_ko":"96.32-96.75의 새로운 정규장 시험, 종가 96.75 이상, 다음 검증된 거래일의 동일 범위 실행 가능 여부를 순서대로 확인한다. 다음 날 가격이 범위를 벗어나면 추격하지 않고 새로 적격인 확인 과정을 기다린다. / 종가 100.00 초과 뒤 99.95-100.00 지지를 관찰하되, 추가매수는 별도로 보상 대비 위험을 심사한다. 선행 돌파 없이 99.95 미만이라는 이유만으로 돌파 실패를 선언하지 않는다.","risk_condition_ko":"96.32 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"UNH","display_name":"UNH","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":409.125,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":400.9216312975736,"relative_volume":1.2118950321724942,"spread_bps":9.286639458442178,"day_high":409.1699,"day_low":392.5,"execution_condition_ko":"핵심 공시의 중대한 훼손 여부를 판단할 수 있고 최신 실행 자료가 확보되면 현재 비활성인 진입 조건을 재점검한다. / 394.11~397.00 지지 종가 이후 다음 검증된 정규장의 394.11~395.00 재시험 유지: 비용 후 손익비 2 이상과 계좌 한도 충족 시 소규모 최초 진입. 395.00 초과는 추격하지 않는다.","risk_condition_ko":"389.89 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":290.525,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":286.85320347807465,"relative_volume":0.7298102947471151,"spread_bps":4.474041952747077,"day_high":292.33,"day_low":283.32,"execution_condition_ko":"284.70 이탈 시 하단 지지 범위 281.23–282.81을 재평가한다. 이탈 자체는 매수나 자동 청산 신호가 아니다. / 새 지지 시험·안정화, 종가 283.00 이상, 다음 확인된 거래일의 282.81–283.00 안정적 되돌림 순서를 확인한다. 단순 가격 접촉은 충분하지 않다.","risk_condition_ko":"278.01 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"KO","display_name":"KO","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":95.65,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":95.47386887868936,"relative_volume":0.8381159969790072,"spread_bps":1.0455329604271122,"day_high":96.39,"day_low":94.35,"execution_condition_ko":"94.08~94.28 첫 지지와 93.42~93.44 핵심 지지 반응을 관찰한다. 평균선은 2026-11-03 기준이므로 갱신하되 기존 손절을 낮추지 않는다. / 2026-11-04 05:05 동부시간 장전 가격 95.13과 지연·소량 거래는 매수 확인이 아니다. 주문 전 실제 거래 가능 세션·휴장 또는 단축장·거래정지·최신 가격과 비용을 확인한다.","risk_condition_ko":"93.42 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":667.76,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":665.1573598755679,"relative_volume":0.7505957407090137,"spread_bps":3.593944204016369,"day_high":673.5,"day_low":655.0,"execution_condition_ko":"2026-11-03 일봉을 기준으로 이후 확인된 거래일마다 갱신하고 2026-11-11T23:59:59-05:00까지 재검토한다. 재시험을 기다리는 중이라도 지지선 이탈이 먼저 발생하면 매수 계획을 취소한다. / 관찰 지지 구간은 633.21–638.25, 실제 매수 후보는 비용 반영 후 633.21–637.05 이내다. 최초 저항 654.39까지 순보상위험비 1.5 이상을 재계산한다.","risk_condition_ko":"633.21 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"SPG","display_name":"Simon Property Group","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":227.155,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":226.3958048686616,"relative_volume":0.4359672517430562,"spread_bps":11.88720364540957,"day_high":227.845,"day_low":224.61,"execution_condition_ko":"218.50~219.73 접촉 후 완료 일봉 반등과 다음 실제 정규 세션 지지 유지 여부를 확인한다. 실행가격이 218.50~219.50 밖이면 추격하지 않는다. / 223.59 돌파·재시험과 돌파 실패를 구분한다. 실패와 하방 위험 확대가 함께 확인되면 기존 보유도 위험축소 대상으로 전환한다.","risk_condition_ko":"218.5 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":431.815,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":430.14155732452656,"relative_volume":0.7008184603587223,"spread_bps":5.327342003775885,"day_high":434.9922,"day_low":423.28,"execution_condition_ko":"414.37–415.00의 새로운 시험부터 종가 확인과 다음 거래일 지지 확인까지 전체 절차를 관찰한다. 체결 가격이 415.00을 넘으면 기다린다. / 2026-10-27 주요사건 공시와 날짜가 확인된 실적·전망 자료를 검토한다. 소유 관련 공시도 확인하되 제출 기록만으로 실제 내부자 매도를 단정하지 않는다.","risk_condition_ko":"410.84 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"LIN","display_name":"LIN","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":523.985,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":520.5050609228781,"relative_volume":0.6433708618487162,"spread_bps":8.969722415718529,"day_high":525.13,"day_low":513.26,"execution_condition_ko":"506.74~508.60 유지·회복은 추세 점검 신호일 뿐 해당 가격의 자동 매수 허가가 아니다. / 503.15~504.00 반전과 다음 세션 지지를 관찰한다. 앞서 매도 신호가 발생했다면 가격 도달만으로 매수 계획을 복원하지 않는다.","risk_condition_ko":"498.35 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"SO","display_name":"SO","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":93.03,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":91.6071971367576,"relative_volume":2.0034523839084057,"spread_bps":3.22459289514711,"day_high":93.06,"day_low":90.405,"execution_condition_ko":"새 지지 시험→92.64 상회 종가→다음 검증 거래일 91.95 유지라는 순서를 확인한다. 재시험 없이 상승하면 추격하지 않는다. / 91.95에서는 비용 전 보상비율이 약 2.34지만 92.02에서는 약 2.03에 불과하다. 실제 거래비용이 기회를 없애면 매수하지 않는다.","risk_condition_ko":"91.28 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"RTX","display_name":"RTX","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":196.935,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":196.853626566024,"relative_volume":0.8316021279426152,"spread_bps":5.585032113933906,"day_high":201.26,"day_low":194.9101,"execution_condition_ko":"2026-11-04 이후 197–200 안정화와 197.87 초과 정규장 종가를 확인한다. 2026-11-03 종가만으로 새 계획이 활성화되지는 않는다. / 다음 실제 거래일의 197.87 지지 유지와 197.87–198.00 체결 가능성을 확인한다. 구간을 놓치면 추격하지 않는다.","risk_condition_ko":"194.45 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":215.11,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":218.20595637830775,"relative_volume":0.7736394937488176,"spread_bps":3.718854592784682,"day_high":223.01,"day_low":214.7342,"execution_condition_ko":"이후 확인된 정규장 종가를 224.46 및 227.94–228.01과 비교한다. 지연된 장전 관측만으로 종가 기준 매수·매도를 발동하지 않는다. / 회복 종가 이후 다음 확인 정규장의 재시험·반등과 실제 체결 가능성을 점검한다. 지정가 체결 자체를 지지 확인으로 간주하지 않는다.","risk_condition_ko":"224.46 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"WAITING_TRIGGER","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":1051.72,"market_data_asof":"2026-11-04T17:26:53+00:00","session_vwap":1043.9023420955007,"relative_volume":0.6802807971844893,"spread_bps":2.6622549299275495,"day_high":1053.6599,"day_low":1028.5,"execution_condition_ko":"1002.62–1006.56 지지 시험과 회복을 관찰하되, 단순 회복만으로 매수하지 않는다. 지지가 깨지면 987.58–994.61을 관찰하며 자동 물타기는 하지 않는다. / 1019.94–1021.31 회복, 1034.77 저항, 1042.57 돌파 여부를 추적하고 가장 가까운 저항까지의 순보상 대비 위험을 다시 계산한다.","risk_condition_ko":"1,002.62 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-11-04T17:28:53+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-11-05T01:13:12.905749+09:00",
  "as_of": "2026-11-04T10:57:00-05:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
