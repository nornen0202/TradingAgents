# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-15T16:20:37.323018+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261016T010355_local-scheduler-us-overlay_only",
  "producer_finished_at": "2026-10-16T01:06:45.818905+09:00",
  "analysis_run_id": "20261015T175401_local-scheduler-us-full",
  "analysis_completed_at": "2026-10-15T20:16:34.027640+09:00",
  "analysis_trade_date_oldest": "2026-10-14",
  "analysis_trade_date_latest": "2026-10-14",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-15T12:00:00-04:00",
  "market_data_latest_at": "2026-10-15T12:00:00-04:00",
  "market_data_status": "FRESH"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-16T01:06:39.820752+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-16T01:06:39.820752+09:00",
    "run_started_at": "2026-10-16T01:03:55.426280+09:00",
    "run_finished_at": "2026-10-16T01:06:45.818905+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23621777,
    "total_market_value_krw": 23662993,
    "total_unrealized_pnl_krw": 41216,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 104986,
    "total_equity_krw": 24744631
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 545707,
      "current_price_krw": 561241,
      "market_value_krw": 6734898,
      "unrealized_pnl_krw": 186414
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 292491,
      "current_price_krw": 286500,
      "market_value_krw": 3151506,
      "unrealized_pnl_krw": -65897
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 424240,
      "current_price_krw": 467332,
      "market_value_krw": 2803992,
      "unrealized_pnl_krw": 258547
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 267300,
      "current_price_krw": 291239,
      "market_value_krw": 1747435,
      "unrealized_pnl_krw": 143633
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1880384,
      "current_price_krw": 1656919,
      "market_value_krw": 1656919,
      "unrealized_pnl_krw": -223465
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 556051,
      "current_price_krw": 535935,
      "market_value_krw": 1607805,
      "unrealized_pnl_krw": -60348
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1473182,
      "current_price_krw": 1227587,
      "market_value_krw": 1227587,
      "unrealized_pnl_krw": -245595
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 134544,
      "current_price_krw": 134589,
      "market_value_krw": 1211305,
      "unrealized_pnl_krw": 403
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 364652,
      "current_price_krw": 459641,
      "market_value_krw": 919283,
      "unrealized_pnl_krw": 189978
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1420269,
      "current_price_krw": 1699847,
      "market_value_krw": 741244,
      "unrealized_pnl_krw": 121914
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 662881,
      "current_price_krw": 628057,
      "market_value_krw": 628057,
      "unrealized_pnl_krw": -34824
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 569741,
      "current_price_krw": 454033,
      "market_value_krw": 454033,
      "unrealized_pnl_krw": -115708
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 136240,
      "current_price_krw": 109805,
      "market_value_krw": 439220,
      "unrealized_pnl_krw": -105741
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 347821,
      "current_price_krw": 339709,
      "market_value_krw": 339709,
      "unrealized_pnl_krw": -8112
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1269.629,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":1258.931307977334,"relative_volume":0.9511783488855258,"spread_bps":7.022942928725809,"day_high":1274.4199,"day_low":1230.74,"execution_condition_ko":"판단 시각은 2026-10-15T05:39:54.068832-04:00이다. 거래소 일정, 실제 거래 상태, 최신 호가, 당일 거래량가중평균가격과 비교 가능한 상대거래량은 별도 확인이 필요하다. / 미국 동부시간 10:30은 검증된 정규장에서 시험 진입을 검토할 수 있는 최초 시각이지 만료 시각이 아니다. 현재 명시된 만료 시각은 없으며 만료 또는 다음 거래일 이월을 선언하지 않는다.","risk_condition_ko":"1,172 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":343.2,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":345.3311295915986,"relative_volume":0.7527819253558612,"spread_bps":1.4549475491411843,"day_high":347.85,"day_low":342.56,"execution_condition_ko":"348.15 돌파·유지 또는 재시험 지지, 정규장 거래량가중평균가격 상회, 같은 시간대 상대거래량 1.2 이상을 확인한다. / 338.39 부근 지지 회복 시 339 부근 눌림 진입과 335 손절의 구조적 타당성 및 비용 후 손익비를 재평가한다.","risk_condition_ko":"336.67 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":100.54,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":100.54565595405224,"relative_volume":1.510238174327751,"spread_bps":0.9945795414979268,"day_high":100.55,"day_low":100.54,"execution_condition_ko":"최신 공식 보유내역·수익률·보수·순자산가치·분배 일정과 계좌 현금 및 VBIL의 동일 기간 총비용 확보. / 2026-10-14 종가 100.54의 분배금 조정 기준을 확인하고, 50일 평균 100.1899와 100.5466의 차이를 해소.","risk_condition_ko":"100.48 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":253.82,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":251.59909347761263,"relative_volume":0.7772032153649056,"spread_bps":1.5787188696369752,"day_high":254.56,"day_low":248.65,"execution_condition_ko":"249.10~250.00 방어와 실패 시 244.30~246.20 재시험을 감시한다. / 253.20~254.10 회복은 관찰 신호일 뿐 매수 승인이 아니다. 257.90~259.70 첫 반등 저항까지 비용 후 보상위험비를 다시 계산한다.","risk_condition_ko":"249.1 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":348.95,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":347.98286240477427,"relative_volume":0.5496707433047806,"spread_bps":1.1458363172826624,"day_high":352.13,"day_low":340.61,"execution_condition_ko":"340.24 지지 재시험과 최신 정규장 5분봉 저점 상승을 확인한다. 이동평균에서 유래한 340.24·345.09는 2026-10-14 기준값이므로 이후 갱신 여부도 확인한다. / 336.83~338.02는 관찰 구간이지 자동 매수 구간이 아니다. 340.24 위험 축소 조건이 발동한 상태에서는 하단 가격 도달을 이유로 신규 진입하지 않는다.","risk_condition_ko":"340.24 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":419.73,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":413.95096180906955,"relative_volume":1.3223384626698262,"spread_bps":3.8127010604080787,"day_high":420.85,"day_low":407.15,"execution_condition_ko":"기준시각은 2026-10-15T06:04:08.633698-04:00, 일봉 기준일은 2026-10-14다. 연구일과 거래소 현지 날짜는 일치하지만 실제 거래 일정과 최신 조건 충족은 별도 확인한다. / 10:30은 제안된 최초 시험 진입 검토 시각이며 만료가 아니다. 확정된 주문 만료시각은 없고 다음 세션으로 자동 이월하지 않는다.","risk_condition_ko":"433.66 이상 도달, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":217.572,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":215.72528897951412,"relative_volume":0.8862314213097526,"spread_bps":0.9213193292799996,"day_high":218.045,"day_low":212.85,"execution_condition_ko":"거래일 달력, 정규장 상태, 거래정지 여부, 호가 신선도와 체결 가능 가격을 먼저 확인한다. / 219.64·221.30 회복과 갱신된 223.09 재시험 성공은 재평가 신호이며 자동 매수 신호가 아니다.","risk_condition_ko":"219.64 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":1238.02,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":1225.6594540217613,"relative_volume":0.5867673882912933,"spread_bps":9.79959424820355,"day_high":1245.17,"day_low":1195.0,"execution_condition_ko":"1234.36의 지속 이탈과 회복 실패 여부를 신선한 정규장 시세로 확인한다. 1210–1224, 1187–1202, 1132–1146은 관찰 구간이지 매수 지시가 아니다. / 1301 상향 회복 후 1284–1301 재시험 지지, 정규장 거래량가중평균가격 상회, 동일 경과시간 기준 상대 거래량 1.2 이상을 확인한다.","risk_condition_ko":"1,234.36 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":400.1,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":393.08620032006365,"relative_volume":1.4390540714171371,"spread_bps":10.524205673048408,"day_high":401.18,"day_low":386.01,"execution_condition_ko":"정규장 일정, 거래정지 여부, 호가 시각, 매수·매도 호가 차이, 유동성, 당일 거래량가중평균가격과 동일 시간대 상대 거래량을 확인한다. / 398–400 방어, 404.40 회복, 408.85 회복·재시험을 순서대로 관찰하되 충족 자체를 매수 승인으로 해석하지 않는다.","risk_condition_ko":"417 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":920.02,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":900.6852025508588,"relative_volume":1.1708325516222777,"spread_bps":9.91874260862896,"day_high":921.19,"day_low":871.155,"execution_condition_ko":"거래일정과 거래 상태, 최신 정규장 가격·호가차·유동성·거래량가중평균가격·동시간대 상대거래량을 먼저 확인한다. 이번 응답에는 이를 확인할 도구가 없다. / 922.24–930.66 회복·재시험을 관찰한다. 898.53–911.93과 868.25–882.81은 하방 관찰 구간이지 자동 매수 구간이 아니다.","risk_condition_ko":"922.24 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":469.06,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":466.2439279090285,"relative_volume":1.7070856127375207,"spread_bps":15.379028985197055,"day_high":482.0,"day_low":452.4201,"execution_condition_ko":"502.32~507.93 회복·재시험 지지 시 반등 실패에 따른 추가 축소 필요성을 재평가하되 자동 매수하지 않음 / 512.76~520.18 종가 회복과 다음 검증된 거래일 첫 30~60분 지지 확인","risk_condition_ko":"512.76 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":82.04,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":82.12211923137737,"relative_volume":0.41257205648811324,"spread_bps":1.218843317690402,"day_high":82.345,"day_low":81.955,"execution_condition_ko":"82.23~82.28 회복, 83.11 돌파·재시험, 84.52 저항까지 남은 비용 후 상승 여력을 순서대로 점검한다. / 80.57 정규장 종가 이탈을 확인한다. 추가 하락 시 79.51·78.33은 과거 저점 관찰값일 뿐 지지나 매수 신호로 가정하지 않는다.","risk_condition_ko":"80.57 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":339.455,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":338.9372853295743,"relative_volume":0.9131877233022354,"spread_bps":3.235912748025759,"day_high":342.35,"day_low":334.61,"execution_condition_ko":"342.82–343.29 회복 및 재시험 성공 후 346.25 회복 여부를 관찰한다. / 357.16–358.06 회복·재시험, 당일 거래량 가중평균가격 상회, 동일 경과시간 상대 거래량 1.2 이상, 358.06 상회 종가를 확인하되 매수로 자동 연결하지 않는다.","risk_condition_ko":"342.82 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":214.02,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":213.61425144719576,"relative_volume":1.3761483713404707,"spread_bps":0.46669000116630055,"day_high":214.555,"day_low":212.79,"execution_condition_ko":"210.78–210.96 회복, 높아진 저점, 당일 거래량가중평균가격 지지와 동일 시간대 상대거래량 1.2 이상을 확인한다. / 213.94 돌파와 재시험을 관찰하되 215.50까지의 제한된 상승 여력 및 비용을 반영해 진입 타당성을 다시 계산한다.","risk_condition_ko":"209.81 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":220.475,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":221.31126464352621,"relative_volume":0.45225945793188493,"spread_bps":3.167492477205058,"day_high":223.4605,"day_low":220.46,"execution_condition_ko":"217.78–218.79 시험 후 정규장 5분봉이 218.79 위에서 마감하고 거래량가중평균가격을 회복하는지 확인한다. / 222.55 위의 정규장 5분봉 마감과 성공적인 재시험, 같은 시각 기준 상대거래량 1.2배 이상을 확인한다. 충족만으로 매수하지 않고 순보상·위험을 재산정한다.","risk_condition_ko":"217.78 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":174.76,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":175.45185890240572,"relative_volume":0.4112222844874829,"spread_bps":2.85657154283494,"day_high":178.585,"day_low":174.48,"execution_condition_ko":"174.09~174.89에서 매도 거래량 감소, 저점 상승, 175.00 회복 및 정규장 거래량가중평균가격 상회 여부를 관찰한다. / 179.00 위 신선한 5분봉 종가, 성공적인 재시험, 증가하는 돌파 봉 거래량과 동일 시간대 상대 거래량 최소 1.2를 확인한다.","risk_condition_ko":"174.09 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":287.915,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":288.68515208193355,"relative_volume":0.6263867119539047,"spread_bps":10.414496979794297,"day_high":291.33,"day_low":286.97,"execution_condition_ko":"285.40 위 5분봉 마감, 재시험 지지, 정규장 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상과 비용 차감 손익비 2 이상을 함께 점검한다. / 275.97~277.60에서 연속 두 개 5분봉의 회복 구조를 확인하고 285.40까지의 보상과 구조적 손절 위험을 다시 계산한다.","risk_condition_ko":"273.56 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"SPYM","display_name":"SPYM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":90.64,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":90.4021106426944,"relative_volume":0.6139090847023997,"spread_bps":1.1032048099735356,"day_high":90.76,"day_low":89.98,"execution_condition_ko":"검증된 정규장의 미국 동부시간 10:30 이후 지지 회복, 완성된 5분 봉 두 개, 당일 거래량가중평균가격 및 반등 거래량을 확인한다. 10:30은 최초 검토 시각이지 만료 시각이 아니다. / 소규모 진입도 현실적인 저항까지의 순보상과 손실 위험이 적절하지 않으면 건너뛴다. 종가 돌파 확인만으로 매수를 자동 승인하지 않는다.","risk_condition_ko":"90.24 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":103.97,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":104.21110281714883,"relative_volume":0.6813882441007441,"spread_bps":0.960845544079281,"day_high":104.67,"day_low":103.88,"execution_condition_ko":"104.55 위 새로운 5분봉 마감, 재시험 지지, 정규장 거래량가중평균가격 상회 및 동일 시간대 상대거래량 1.2 이상. / 100.00–101.30에서 매도 거래량 감소 후 높아진 저점과 반등 거래량 증가.","risk_condition_ko":"102.09 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":399.2,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":397.7290175412961,"relative_volume":0.6028554131193503,"spread_bps":3.2592481165305416,"day_high":399.88,"day_low":395.26,"execution_condition_ko":"384.65–385.57 시험 후 회복, 하락 거래량 감소와 반등 거래량 증가, 당일 거래량가중평균가격 지지 및 비용 차감 후 보상위험비 2 이상을 재검토한다. 미해결 축소 신호가 있으면 물타기하지 않는다. / 397.19 돌파 종가와 재시험 지지, 동시간대 상대거래량 1.2 이상 및 검증된 상위 목표 확보를 확인한다.","risk_condition_ko":"389.56 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"META","display_name":"Meta Platforms","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":733.21,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":730.8694733819843,"relative_volume":0.6716262024003532,"spread_bps":3.9507114686439833,"day_high":736.2,"day_low":715.58,"execution_condition_ko":"718~721 재시험에서 매도 거래량 감소와 반등 거래량 증가 확인. 실제 진입가로 734까지 비용 후 손익비를 다시 계산한다. / 734~737 회복과 재지지 확인. 기존 무효화 711.68을 적용한 신규 매수는 손익비 부족으로 계속 보류한다.","risk_condition_ko":"711.68 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":158.08,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":158.82107360102955,"relative_volume":1.085381161925593,"spread_bps":2.5203200806497414,"day_high":159.95,"day_low":158.05,"execution_condition_ko":"154.29–154.75 재시험 이후 저점 상승과 154.75 위에서 완료된 정규장 5분봉 2개를 확인한다. / 156.63 위 종가와 다음 검증된 세션의 지지 유지를 확인하되 신규 체결가격의 보상위험비를 별도로 계산한다.","risk_condition_ko":"154.29 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":95.225,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":95.36583755349113,"relative_volume":1.1678246789290703,"spread_bps":2.0938023450582097,"day_high":95.945,"day_low":93.9588,"execution_condition_ko":"판단 시각은 2026-10-15T06:57:44.759912-04:00이다. 10:30은 미국 동부시간 기준 최초 검토 시각이지 만료 시각이 아니다. 거래일과 정규장 상태는 미확인이고, 기존 유효기간을 임의로 설정하거나 다음 거래일로 연장하지 않는다. / 정규장 5분봉 두 개의 94.72 상회 마감, 재시험 지지, 정규장 거래량가중평균가격 상회 및 동일 시각 상대거래량 1.2 이상을 관찰한다. 제공된 일일 거래량 1.60배는 이 장중 조건을 대체하지 않는다.","risk_condition_ko":"89.99 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"AMT","display_name":"AMT","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":182.625,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":183.559222919029,"relative_volume":0.3286026630314823,"spread_bps":8.21625174595225,"day_high":184.69,"day_low":182.215,"execution_condition_ko":"보유 수량, 순자산, 현금, 단일 종목 및 상관 업종 노출을 확인하고 초과 위험을 우선 축소한다. / 공식 재무자료의 통화·단위·기간·주식 기준을 검증하고 연간 잉여현금흐름 및 차입 현금흐름 분류 차이를 조정한다.","risk_condition_ko":"175.02 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"BBD","display_name":"BBD","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":4.085,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":4.087698001977415,"relative_volume":0.5756787752936467,"spread_bps":24.360535931792143,"day_high":4.1379,"day_low":3.9801,"execution_condition_ko":"판단 기준 시각은 2026-10-15T06:04:15.343451-04:00이며 일봉 기준일은 2026-10-14다. 실제 거래일·휴장·단축장 여부와 최신 호가·거래량을 별도로 검증한다. / 10:30은 검증된 정규 거래일의 최초 탐색 진입 검토 시각이지 만료 시각이 아니다. 아직 유효기한이 설정된 주문은 없으며 다음 거래일로 임의 이월하지 않는다.","risk_condition_ko":"4.06 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"NU","display_name":"NU","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":14.93,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":14.857235077541866,"relative_volume":0.6371202269861291,"spread_bps":6.686726847209337,"day_high":15.065,"day_low":14.4,"execution_condition_ko":"거래소 일정, 정규장 여부, 거래정지 상태, 호가·봉 자료의 최신성과 동일 시각 상대거래량 산식을 확인한다. / 14.44–14.67 지지, 14.77–14.84 회복·재시험 및 15.08 종가 회복을 구분해 관찰한다.","risk_condition_ko":"14.44 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"MRNA","display_name":"MRNA","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":238.7,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":233.0858224430864,"relative_volume":3.6143862629398504,"spread_bps":12.141257248120912,"day_high":242.29,"day_low":217.0221,"execution_condition_ko":"227.46 상회 최신 정규장 5분봉 마감, 227.09~227.46 재시험 지지, 정규장 거래량 가중 평균가격 상회 및 동시간대 상대거래량 1.2 이상. / 210.91~211.24에서 하락 중단과 반등 거래량 회복, 정규장 거래량 가중 평균가격 재탈환. 낮은 가격 자체는 매수 신호가 아니다.","risk_condition_ko":"204.7 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"GOOG","display_name":"GOOG","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":344.68,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":344.11250530174726,"relative_volume":0.47059766825265587,"spread_bps":2.029897490176548,"day_high":348.3982,"day_low":336.82,"execution_condition_ko":"위험 대응 조건: 355.25 이상 도달, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"355.25 이상 도달, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"OKTA","display_name":"Okta","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":207.99,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":206.8192530839858,"relative_volume":1.1286767675405582,"spread_bps":12.53918495297762,"day_high":210.3499,"day_low":203.0,"execution_condition_ko":"위험 대응 조건: 214.06 이하 하락, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"214.06 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

```json
{"ticker":"DDOG","display_name":"Datadog","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":264.36,"market_data_asof":"2026-10-15T12:00:00-04:00","session_vwap":262.38823376266305,"relative_volume":0.6927361130508042,"spread_bps":24.214907302307466,"day_high":266.91,"day_low":256.22,"execution_condition_ko":"위험 대응 조건: 268.37 이하 하락, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"268.37 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-15T12:30:00-04:00","expired_at_build":false,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":null}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-16T01:16:05.781099+09:00",
  "as_of": "2026-10-15T12:00:00-04:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
