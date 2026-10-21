# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-21T17:52:46.813022+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261022T025110_local-freshness-us-overlay",
  "producer_finished_at": "2026-10-22T02:51:48.760597+09:00",
  "analysis_run_id": "20261021T175015_local-scheduler-us-full",
  "analysis_completed_at": "2026-10-21T21:13:33.227411+09:00",
  "analysis_trade_date_oldest": "2026-10-20",
  "analysis_trade_date_latest": "2026-10-20",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-22T02:50:57+09:00",
  "market_data_latest_at": "2026-10-21T13:51:00-04:00",
  "market_data_status": "FRESH"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-22T02:46:38.395495+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-22T02:46:38.395495+09:00",
    "run_started_at": "2026-10-22T02:46:08.878147+09:00",
    "run_finished_at": "2026-10-22T02:46:44.651990+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23434719,
    "total_market_value_krw": 23688705,
    "total_unrealized_pnl_krw": 253986,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 106399,
    "total_equity_krw": 24771756
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 541385,
      "current_price_krw": 570595,
      "market_value_krw": 6847141,
      "unrealized_pnl_krw": 350512
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 290175,
      "current_price_krw": 287857,
      "market_value_krw": 3166430,
      "unrealized_pnl_krw": -25496
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 420881,
      "current_price_krw": 444747,
      "market_value_krw": 2668483,
      "unrealized_pnl_krw": 143195
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 265183,
      "current_price_krw": 294430,
      "market_value_krw": 1766585,
      "unrealized_pnl_krw": 175483
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1865494,
      "current_price_krw": 1696971,
      "market_value_krw": 1696971,
      "unrealized_pnl_krw": -168523
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 551647,
      "current_price_krw": 524785,
      "market_value_krw": 1574357,
      "unrealized_pnl_krw": -80586
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1461517,
      "current_price_krw": 1237496,
      "market_value_krw": 1237496,
      "unrealized_pnl_krw": -224021
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 133479,
      "current_price_krw": 133614,
      "market_value_krw": 1202527,
      "unrealized_pnl_krw": 1214
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 361765,
      "current_price_krw": 457555,
      "market_value_krw": 915111,
      "unrealized_pnl_krw": 191581
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1409021,
      "current_price_krw": 1688459,
      "market_value_krw": 736277,
      "unrealized_pnl_krw": 121852
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 657632,
      "current_price_krw": 642605,
      "market_value_krw": 642605,
      "unrealized_pnl_krw": -15027
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 565229,
      "current_price_krw": 449554,
      "market_value_krw": 449554,
      "unrealized_pnl_krw": -115675
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 135161,
      "current_price_krw": 108603,
      "market_value_krw": 434415,
      "unrealized_pnl_krw": -106231
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 345067,
      "current_price_krw": 350753,
      "market_value_krw": 350753,
      "unrealized_pnl_krw": 5686
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"SELL","strategy_ko":"매도·청산 검토","last_price":100.6123,"market_data_asof":"2026-10-22T02:50:57+09:00","session_vwap":100.61440295981636,"relative_volume":0.6139715671869133,"spread_bps":0.9938875913139309,"day_high":100.62,"day_low":100.61,"execution_condition_ko":"위험 대응 조건: 100.59 이하 하락, 종가 확인 후 손절 조건 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"100.59 이하 하락, 종가 확인 후 손절 조건","decision_state_ko":"투자 근거 무효화","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T03:00:57+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"SELL","strategy_ko":"매도·청산 검토","last_price":484.36,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":488.0672589321439,"relative_volume":0.5816440667113713,"spread_bps":4.95417389150378,"day_high":502.0,"day_low":480.52,"execution_condition_ko":"위험 대응 조건: 439.5 이하 하락, 종가 확인 후 손절 조건 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"439.5 이하 하락, 종가 확인 후 손절 조건","decision_state_ko":"투자 근거 무효화","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":334.73,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":333.3248987268427,"relative_volume":0.7852672058272128,"spread_bps":1.1948145050487027,"day_high":337.27,"day_low":330.38,"execution_condition_ko":"위험 대응 조건: 335.51 이하 하락, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"335.51 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":81.8001,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":81.7091245502886,"relative_volume":0.42421021124831576,"spread_bps":1.2224191675331724,"day_high":81.89,"day_low":81.515,"execution_condition_ko":"위험 대응 조건: 80.57 이하 하락, 거래량 조건 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"80.57 이하 하락, 거래량 조건 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1270.64,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":1269.1957693541356,"relative_volume":0.3939476126849628,"spread_bps":6.533452457325356,"day_high":1279.28,"day_low":1261.69,"execution_condition_ko":"제공된 판단 시각은 2026-10-21T05:53:11.015831-04:00이다. 05:35 미국 동부시간 자료는 지연된 장전 분석용이다. 거래일·휴장·조기폐장·거래정지·신선한 실행 호가와 실제 정규장 봉을 별도 확인한다. / 1260.17–1275.88에서 지지를 유지하는 두 5분봉 종가, 높아지는 저점, 정규장 거래량가중평균가격 회복과 동시간대 상대거래량 1.2 이상을 관찰한다. 확인되더라도 기대수익 조건을 별도로 충족해야 한다.","risk_condition_ko":"1,260.17 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":344.65,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":342.308282633914,"relative_volume":0.5013936058285562,"spread_bps":0.5802988539108851,"day_high":345.25,"day_low":338.83,"execution_condition_ko":"판단시각은 2026-10-21T05:08:00.624809-04:00이다. 2026-10-21 04:50 미동부 관측은 지연된 분석용 장전 자료이며 실행 가능한 현재 시세나 정규장 지지 이탈을 입증하지 않는다. / 실제 거래일·휴장 및 조기폐장 일정·거래정지·현재 호가를 확인한다. 10:30은 정규장 시험 진입의 개시 하한이지 만료시각이 아니며 활성 주문창이나 조건부 매수 만료는 설정되지 않았다.","risk_condition_ko":"338.7 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":264.2014,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":261.71826273560055,"relative_volume":0.5249289260878761,"spread_bps":1.1354819174515831,"day_high":264.35,"day_low":259.29,"execution_condition_ko":"거래일정·정규장·거래정지 여부, 신선한 시세, 정규장 거래량가중평균가격과 비교 가능한 동시간대 거래량 기준을 먼저 확인한다. / 265.34 위 5분봉 종가 두 차례, 그 사이 성공적인 재시험, 동시간대 상대거래량 1.2 이상을 관찰한다.","risk_condition_ko":"256.07 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":429.85,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":428.2856280769035,"relative_volume":0.4219736354956496,"spread_bps":2.326392927764706,"day_high":435.16,"day_low":423.74,"execution_condition_ko":"공식 재무제표의 통화·단위·주식예탁증서 비율·공개시각·최신 전망을 확인해 잠정 재무평가를 대조한다. / 거래소 일정·거래상태·신선한 정규장 시세·뉴스 공개시각을 확인한다.","risk_condition_ko":"415.5 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":1280.11,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":1276.7116512558653,"relative_volume":0.3895313584325876,"spread_bps":15.071236973727348,"day_high":1288.265,"day_low":1260.0,"execution_condition_ko":"1287.72 회복 후 최신 값으로 갱신한 1303.52 기준선 위 종가와 다음 검증된 거래일의 지지 여부를 관찰한다. 자동 매수 조건은 아니다. / 신선한 정규장 거래량가중평균가격 지지, 동시간대 상대거래량 1.2 이상, 상대강도지수 50 상회와 추세 개선을 확인한다. 현재 충족 여부는 미확인이다.","risk_condition_ko":"1,222.29 이하 하락, 2개 봉 확인 후 (정규장 5분봉 2개 연속 하회 후 되찾기 실패 확인) 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":933.19,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":926.2926636063299,"relative_volume":0.8306559744004258,"spread_bps":5.89221531226136,"day_high":935.16,"day_low":914.35,"execution_condition_ko":"917.05 회복·재시험 지지, 당일 거래량가중평균가격 상회, 동시간대 정규장 상대거래량 1.2 이상을 함께 관찰한다. 이는 감시 필터이며 현재 매수 승인이나 관측 사실이 아니다. / 942.02 위 종가 유지와 하락 동력 둔화는 단기 약세 재평가 조건이다. 961.85 회복 후에도 근거 있는 목표가격과 비용 후 보상·위험이 없으면 확대하지 않는다.","risk_condition_ko":"868.25 이하 하락, 종가 확인 후 (비교 가능한 정규장 거래량 증가와 종가까지 재회복 실패 확인) 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":395.25,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":392.0707949185249,"relative_volume":0.4103437891255803,"spread_bps":3.035976319384824,"day_high":395.57,"day_low":388.335,"execution_condition_ko":"실제 정규장 여부와 최신 가격·호가·거래량·거래량가중평균가격을 확인한다. 10:30 미국 동부시간은 최초 시험 진입 검토시각이며 만료나 자동 주문시각이 아니다. 다음 거래일도 확인 없이 지정하지 않는다. / 393.42와 갱신된 200일선 회복·재지지를 관찰한다. 상대거래량은 직전 20개 확인된 정규장의 동일 경과시점 평균 누적거래량 대비로 정의하고, 원자료가 없으면 충족으로 판정하지 않는다.","risk_condition_ko":"393.42 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":338.6,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":336.33782254599254,"relative_volume":0.4077739626602,"spread_bps":1.772002362669884,"day_high":339.24,"day_low":332.29,"execution_condition_ko":"거래일과 거래 가능 상태를 확인하고 새로운 정규장 5분봉·당일 거래량가중평균가격·동일 경과시간 상대거래량을 확보한다. 제공된 장전 상대거래량은 대체 자료로 쓰지 않는다. / 330.80 지지와 328.58 무효화 기준을 관찰하되 일시적 장중 하회와 확인된 이탈을 구별한다.","risk_condition_ko":"335.2 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":221.72,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":220.19603002951894,"relative_volume":0.4982992195409167,"spread_bps":0.9020792927702961,"day_high":222.16,"day_low":217.66,"execution_condition_ko":"최신 제시 시각은 2026-10-21T06:04:30.925468-04:00이다. 미국 동부시각 05:45 지연 관측은 현재 호가를 입증하지 못한다. 거래 달력·실제 장 상태·거래정지·체결 가능한 호가를 별도로 확인한다. / 미국 동부시각 10:30은 최초 검토 가능 시각이며 만료시각이 아니다. 확인된 주문 만료시각은 없으며 날짜를 임의로 이월하지 않는다.","risk_condition_ko":"212.77 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":216.78,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":216.44831586430843,"relative_volume":0.4500620410967562,"spread_bps":0.46130780763422463,"day_high":216.94,"day_low":215.825,"execution_condition_ko":"215.00~215.16 정규장 지지, 거래량가중평균가격 회복, 검증된 동시간대 상대거래량 1.2 이상과 215.20 부근 실제 체결가의 비용 후 손익비를 함께 확인한다. / 216.30 초과 정규장 5분봉 마감과 재시험 유지 여부를 관찰한다. 돌파 확인만으로 진입하지 않고 손절·목표·비용을 재산정한다.","risk_condition_ko":"215 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":226.21,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":226.14953781138124,"relative_volume":0.30658974014211315,"spread_bps":1.7677995315327726,"day_high":227.13,"day_low":224.19,"execution_condition_ko":"거래일·세션·거래정지 여부·최신 시세와 새 유효기간을 확인한다. 10:30은 최초 검토 가능 시각이지 만료가 아니며, 제공된 기한이 이미 지났다는 증거도 없다. / 227.28 위 5분봉 두 개 연속 마감, 성공적 재시험, 당일 거래량가중평균가격 지지 및 동일 시각 대비 거래량 1.2배 이상을 확인한다.","risk_condition_ko":"221.56 이하 하락, 거래량 조건 확인 후 (매도 거래량 증가를 동반한 지속적 하향 이탈) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":105.04,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":105.34690692201086,"relative_volume":0.40066843660753054,"spread_bps":0.9519729639669575,"day_high":105.86,"day_low":104.66,"execution_condition_ko":"104.31–104.80에서 저점 상승과 지지 회복을 확인한다. 단순 도달은 진입 신호가 아니다. / 102.86–103.31 시험 후 103.31 회복·재시험을 관찰한다. 실제 진입가는 103.40 이하이면서 비용 차감 후 손익비 기준을 충족해야 한다.","risk_condition_ko":"102.86 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":283.18,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":284.4784981532988,"relative_volume":0.36162492790460604,"spread_bps":3.178695675209064,"day_high":288.9999,"day_low":282.155,"execution_condition_ko":"상방 관찰: 291.40 돌파 후 유지 또는 성공적 재시험, 세션 거래량가중평균가격 지지, 같은 경과시간 기준 상대거래량 1.2 이상을 확인하고 손익비를 다시 산출한다. / 지지 관찰: 282.59–285.00에서 완성된 두 개의 15분봉 반전·유지와 이후 거래량가중평균가격 회복이 필요하다. 가격 접촉만으로 매수하지 않는다.","risk_condition_ko":"282.59 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":177.46,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":177.4145251121314,"relative_volume":0.38440079267821736,"spread_bps":1.1269510339765487,"day_high":178.14,"day_low":176.15,"execution_condition_ko":"173.60–175.15에서 높아진 저점과 재시험을 확인하고 175.15 위 연속 5분봉 2개 종가, 신선한 정규장 거래량가중평균가격 지지, 동시간대 상대거래량 1.2 이상을 요구한다. 첫 보상 평가에는 179.30을 사용하며 지지선 접촉만으로 매수하지 않는다. / 180.26 위 연속 5분봉 2개 종가와 성공적 재시험을 감시한다. 추가 상승 목표와 구조적 손절가가 독립적으로 검증되지 않으면 돌파만으로 매수하지 않는다.","risk_condition_ko":"173.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":996.805,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":993.8178217092959,"relative_volume":0.2826269183559274,"spread_bps":2.6082158800219784,"day_high":997.62,"day_low":988.47,"execution_condition_ko":"977.24–982.64에서 매도 거래량 감소와 지지 재시험을 관찰하되, 963 보호와 1000 저항을 사용할 때 실제 진입가에 주당비용을 더한 값이 977.80 이하여야 한다. 확인 후 가격이 이를 넘으면 진입하지 않는다. / 1008.37 위 연속 두 개의 5분봉 마감, 지지 재시험, 정규장 거래량가중평균가격 상회 및 동시간대 상대거래량 1.2 이상을 관찰한다. 기존 991 보호 예시로는 돌파 매수가 적격하지 않다.","risk_condition_ko":"977.24 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"UNH","display_name":"UNH","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":415.52,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":417.0378686058808,"relative_volume":0.2941051508168582,"spread_bps":6.258424802618691,"day_high":421.47,"day_low":415.0,"execution_condition_ko":"408.28–414.12에서 단순 접촉이 아니라 매도 압력 둔화, 반등과 지지 유지가 확인되는지 관찰한다. / 422.40 위 연속 2개 5분 봉 종가, 성공적인 재시험, 정규장 거래량가중평균가격 지지 및 동일 시각 상대거래량 1.2 이상을 확인한다. 이는 재평가 조건이지 매수 허가는 아니다.","risk_condition_ko":"422.4 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"SNPS","display_name":"Synopsys","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":455.77,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":455.8283097196931,"relative_volume":0.21470882202253871,"spread_bps":8.55610280486571,"day_high":459.71,"day_low":451.69,"execution_condition_ko":"거래 일정과 정지 여부, 최신 체결·호가·호가 차이, 완성된 5분 봉, 당일 거래량가중평균가격과 동일 경과시간 상대거래량을 먼저 확인한다. / 441.09–445.67 지지 방어 후 452와 454.58–454.63 재탈환·재시험을 관찰한다. 상대거래량 1.2 이상은 제안 기준이지 관측된 수치가 아니다.","risk_condition_ko":"441.09 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"SCCO","display_name":"SCCO","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":196.56,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":196.22279038213017,"relative_volume":0.9049537003761355,"spread_bps":6.104384983211728,"day_high":202.46,"day_low":190.69,"execution_condition_ko":"거래일 달력과 실제 거래 상태, 최신 정규장 시세를 확인한다. 지연된 장전 197.32와 보고된 장전 고점만으로 지지 이탈이나 돌파를 판단하지 않는다. / 196.44–197.21 지지 유지, 당일 거래량가중평균가격 회복과 동시간대 상대거래량 1.2 이상을 확인한다. 일별 거래량가중이동평균 202.38을 당일 거래량가중평균가격으로 대체하지 않는다.","risk_condition_ko":"196.44 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"TXN","display_name":"Texas Instruments","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":288.615,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":284.92391850843717,"relative_volume":0.8506518236817565,"spread_bps":4.850836769342239,"day_high":289.27,"day_low":277.37,"execution_condition_ko":"272.01-273.59 방어를 관찰한다. 지지선 접촉만으로 매수하거나 이탈 후 물타기하지 않는다. / 280.52 회복, 283.13 통과, 284.47 안착을 순서대로 확인하고 실제 진입·손절·목표의 손익 구조를 다시 계산한다.","risk_condition_ko":"272.01 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":409.035,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":407.71972262229355,"relative_volume":0.3769421636233189,"spread_bps":1.711344994926918,"day_high":409.5299,"day_low":404.1,"execution_condition_ko":"실제 거래일·정규장 운영·거래정지 여부와 최신 호가·5분봉·정규장 거래량가중평균가격·동일 경과시간 상대거래량을 확인한다. 현재 시계만으로 거래 상태나 조건 충족을 추정하지 않는다. / 402.61~404.74에서 높아지는 저점과 404.74 회복, 또는 398.01~399.75에서 별도의 반등과 399.75 회복을 확인한다. 단순 접촉은 매수 신호가 아니다.","risk_condition_ko":"402.61 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":542.38,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":542.1897382266905,"relative_volume":0.4217679048460973,"spread_bps":2.5812161215402494,"day_high":543.34,"day_low":539.25,"execution_condition_ko":"2026-10-21T06:28:07.133248-04:00은 미국 동부시간 10:30 진입 검토 개시 시각 이전이다. 10:30은 만료가 아니며, 이 시계 정보만으로 거래일이나 실행 조건을 확정하지 않는다. / 최신 제공 장중봉은 미국 동부시간 2026-10-20 15:55이다. 현재 거래일의 시세와 실제 거래 일정을 먼저 확인한다.","risk_condition_ko":"533.5 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":623.355,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":622.1525013111057,"relative_volume":0.32239408651801976,"spread_bps":6.738868832732816,"day_high":624.6599,"day_low":617.4,"execution_condition_ko":"거래 일정·실적 일정·최신 가격·포트폴리오 한도와 자료 신뢰성을 확인한다. 실제 한도 초과가 드러나면 초과 노출을 위험 감축한다. / 최초 검토 시각 이후 624.29 위 완료된 5분봉, 성공적인 재확인, 당일 거래량가중평균가격 지지와 동일시각 상대거래량 1.2 이상을 점검한다. 현재 충족 여부는 미확인이다.","risk_condition_ko":"602.57 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":93.57,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":93.84991582481817,"relative_volume":0.07408006666835819,"spread_bps":3.2056419297965637,"day_high":95.3,"day_low":93.11,"execution_condition_ko":"거래일 달력·정규장과 거래정지 상태·신선한 실행 가능 호가·스프레드·당일 거래량가중평균가격을 검증한다. / 92.45–93.01에서 5분봉 회복과 성공적인 재시험을 확인한다. 단순 접촉은 매수 신호가 아니다.","risk_condition_ko":"92.45 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":157.66,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":157.9832799720613,"relative_volume":0.45608133617850755,"spread_bps":1.2684721253256948,"day_high":158.6728,"day_low":157.41,"execution_condition_ko":"위험 대응 조건: 156.53 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"156.53 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"AMT","display_name":"AMT","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":179.1,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":180.2427531794381,"relative_volume":0.30926461227485336,"spread_bps":7.816862088218111,"day_high":183.78,"day_low":178.815,"execution_condition_ko":"위험 대응 조건: 179 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"179 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":196.9,"market_data_asof":"2026-10-21T13:51:00-04:00","session_vwap":195.88226298585647,"relative_volume":0.6783022576140958,"spread_bps":7.619047619046465,"day_high":197.83,"day_low":184.0,"execution_condition_ko":"위험 대응 조건: 197.91 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"197.91 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-21T14:01:00-04:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-22T01:17:35.913396+09:00",
  "as_of": "2026-10-21T16:12:50+00:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
