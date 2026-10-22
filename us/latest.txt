# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-22T14:57:11.580162+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261022T235555_local-freshness-us-overlay",
  "producer_finished_at": "2026-10-22T23:56:40.602169+09:00",
  "analysis_run_id": "20261021T175015_local-scheduler-us-full",
  "analysis_completed_at": "2026-10-21T21:13:33.227411+09:00",
  "analysis_trade_date_oldest": "2026-10-20",
  "analysis_trade_date_latest": "2026-10-20",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-22T14:55:16+00:00",
  "market_data_latest_at": "2026-10-22T14:55:16+00:00",
  "market_data_status": "FRESH"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-22T23:46:58.908322+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-22T23:46:58.908322+09:00",
    "run_started_at": "2026-10-22T23:46:31.704336+09:00",
    "run_finished_at": "2026-10-22T23:47:07.575652+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23390605,
    "total_market_value_krw": 22843977,
    "total_unrealized_pnl_krw": -546628,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 106199,
    "total_equity_krw": 23926867
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 540366,
      "current_price_krw": 551056,
      "market_value_krw": 6612680,
      "unrealized_pnl_krw": 128281
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 289628,
      "current_price_krw": 286858,
      "market_value_krw": 3155438,
      "unrealized_pnl_krw": -30479
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 420089,
      "current_price_krw": 433411,
      "market_value_krw": 2600471,
      "unrealized_pnl_krw": 79937
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 264684,
      "current_price_krw": 283034,
      "market_value_krw": 1698204,
      "unrealized_pnl_krw": 110097
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1861982,
      "current_price_krw": 1557435,
      "market_value_krw": 1557435,
      "unrealized_pnl_krw": -304547
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 550609,
      "current_price_krw": 485066,
      "market_value_krw": 1455200,
      "unrealized_pnl_krw": -196628
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 133228,
      "current_price_krw": 133378,
      "market_value_krw": 1200405,
      "unrealized_pnl_krw": 1353
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1458765,
      "current_price_krw": 1107415,
      "market_value_krw": 1107415,
      "unrealized_pnl_krw": -351350
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 361084,
      "current_price_krw": 455150,
      "market_value_krw": 910300,
      "unrealized_pnl_krw": 188132
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1406370,
      "current_price_krw": 1729777,
      "market_value_krw": 754295,
      "unrealized_pnl_krw": 141026
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 656394,
      "current_price_krw": 600173,
      "market_value_krw": 600173,
      "unrealized_pnl_krw": -56221
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 564165,
      "current_price_krw": 431867,
      "market_value_krw": 431867,
      "unrealized_pnl_krw": -132298
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 134907,
      "current_price_krw": 106384,
      "market_value_krw": 425538,
      "unrealized_pnl_krw": -114090
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 344417,
      "current_price_krw": 334556,
      "market_value_krw": 334556,
      "unrealized_pnl_krw": -9861
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":414.1,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":419.6010742806611,"relative_volume":0.7685928718951897,"spread_bps":3.6221822440620906,"day_high":421.9099,"day_low":413.78,"execution_condition_ko":"위험 대응 조건: 415.5 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"415.5 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":451.17,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":461.1263436884122,"relative_volume":0.8256737290188778,"spread_bps":17.283020540204575,"day_high":473.01,"day_low":450.71,"execution_condition_ko":"위험 대응 조건: 439.5 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"439.5 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":212.7548,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":215.99472433292595,"relative_volume":0.9851932293152186,"spread_bps":0.4700683949523739,"day_high":218.88,"day_low":212.5611,"execution_condition_ko":"위험 대응 조건: 212.77 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"212.77 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":326.99,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":328.3963242662215,"relative_volume":0.9692030895740377,"spread_bps":1.2233164107902765,"day_high":331.43,"day_low":326.39,"execution_condition_ko":"위험 대응 조건: 335.51 이하 하락, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"335.51 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":252.195,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":254.16072062378154,"relative_volume":1.2727662507336,"spread_bps":1.9826714515142203,"day_high":258.36,"day_low":251.4,"execution_condition_ko":"위험 대응 조건: 256.07 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"256.07 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":344.14,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":344.63789629836043,"relative_volume":0.7476992392167626,"spread_bps":1.7434258317594733,"day_high":347.28,"day_low":342.28,"execution_condition_ko":"판단시각은 2026-10-21T05:08:00.624809-04:00이다. 2026-10-21 04:50 미동부 관측은 지연된 분석용 장전 자료이며 실행 가능한 현재 시세나 정규장 지지 이탈을 입증하지 않는다. / 실제 거래일·휴장 및 조기폐장 일정·거래정지·현재 호가를 확인한다. 10:30은 정규장 시험 진입의 개시 하한이지 만료시각이 아니며 활성 주문창이나 조건부 매수 만료는 설정되지 않았다.","risk_condition_ko":"338.7 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":100.625,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":100.62613354557747,"relative_volume":1.0989622852243117,"spread_bps":0.9937888198748726,"day_high":100.63,"day_low":100.62,"execution_condition_ko":"실행 시각 2026-10-21T06:17:21.473484-04:00보다 최초 검토 시각 2026-10-21T10:30:00-04:00은 뒤다. 이는 만료시각이나 주문 실행 조건 충족을 뜻하지 않는다. 거래일과 정규장 운영 여부를 별도로 확인한다. / 발행사 자료, 보유 규모, 현금 의무, 결제 일정, 최신 호가와 동시점 순자산가치를 확보하고 조정주가 및 이동평균 불일치를 해소한다. 시간대가 없는 자료 시각이나 당일 날짜만으로 실행 시점 이전 공개를 인정하지 않는다.","risk_condition_ko":"100.59 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":1172.7,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":1207.5502592710177,"relative_volume":1.3631971025250667,"spread_bps":20.871046746883767,"day_high":1230.415,"day_low":1172.1,"execution_condition_ko":"1287.72 회복 후 최신 값으로 갱신한 1303.52 기준선 위 종가와 다음 검증된 거래일의 지지 여부를 관찰한다. 자동 매수 조건은 아니다. / 신선한 정규장 거래량가중평균가격 지지, 동시간대 상대거래량 1.2 이상, 상대강도지수 50 상회와 추세 개선을 확인한다. 현재 충족 여부는 미확인이다.","risk_condition_ko":"1,222.29 이하 하락, 2개 봉 확인 후 (정규장 5분봉 2개 연속 하회 후 되찾기 실패 확인) 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":829.96,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":854.4452347235384,"relative_volume":1.9494584811927498,"spread_bps":14.217038759503893,"day_high":901.0,"day_low":829.02,"execution_condition_ko":"917.05 회복·재시험 지지, 당일 거래량가중평균가격 상회, 동시간대 정규장 상대거래량 1.2 이상을 함께 관찰한다. 이는 감시 필터이며 현재 매수 승인이나 관측 사실이 아니다. / 942.02 위 종가 유지와 하락 동력 둔화는 단기 약세 재평가 조건이다. 961.85 회복 후에도 근거 있는 목표가격과 비용 후 보상·위험이 없으면 확대하지 않는다.","risk_condition_ko":"868.25 이하 하락, 종가 확인 후 (비교 가능한 정규장 거래량 증가와 종가까지 재회복 실패 확인) 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":366.52,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":369.66677895880986,"relative_volume":1.10557982880695,"spread_bps":13.09471846355353,"day_high":380.65,"day_low":364.34,"execution_condition_ko":"실제 정규장 여부와 최신 가격·호가·거래량·거래량가중평균가격을 확인한다. 10:30 미국 동부시간은 최초 시험 진입 검토시각이며 만료나 자동 주문시각이 아니다. 다음 거래일도 확인 없이 지정하지 않는다. / 393.42와 갱신된 200일선 회복·재지지를 관찰한다. 상대거래량은 직전 20개 확인된 정규장의 동일 경과시점 평균 누적거래량 대비로 정의하고, 원자료가 없으면 충족으로 판정하지 않는다.","risk_condition_ko":"393.42 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":323.66,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":327.57576393581706,"relative_volume":0.8599119006125956,"spread_bps":2.471118799035772,"day_high":330.82,"day_low":323.49,"execution_condition_ko":"거래일과 거래 가능 상태를 확인하고 새로운 정규장 5분봉·당일 거래량가중평균가격·동일 경과시간 상대거래량을 확보한다. 제공된 장전 상대거래량은 대체 자료로 쓰지 않는다. / 330.80 지지와 328.58 무효화 기준을 관찰하되 일시적 장중 하회와 확인된 이탈을 구별한다.","risk_condition_ko":"335.2 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":80.3,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":80.24339603185675,"relative_volume":0.9222579673388102,"spread_bps":1.2452524749399307,"day_high":80.665,"day_low":79.985,"execution_condition_ko":"판단시각은 2026-10-21T05:34:39.100833-04:00이다. 보고된 미 동부시간 05:15 관측은 219초 지연된 정규장 이전 자료이므로 현재 체결조건을 입증하지 않는다. 거래일·정규장 운영시간·거래정지 여부와 최신 호가를 별도로 확인한다. / 2026-10-21T10:30:00-04:00은 제안된 가장 이른 재평가 시점으로 판단시각보다 뒤다. 만료시각이나 자동 매수 시각이 아니며, 현재 조건부 매수와 만료시각은 없다. 다음 거래일로 자동 이월하지 않는다.","risk_condition_ko":"80.57 이하 하락, 거래량 조건 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":1307.4963,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":1298.0803238603137,"relative_volume":0.8751456346926991,"spread_bps":7.950158620952976,"day_high":1309.58,"day_low":1275.1,"execution_condition_ko":"제공된 판단 시각은 2026-10-21T05:53:11.015831-04:00이다. 05:35 미국 동부시간 자료는 지연된 장전 분석용이다. 거래일·휴장·조기폐장·거래정지·신선한 실행 호가와 실제 정규장 봉을 별도 확인한다. / 1260.17–1275.88에서 지지를 유지하는 두 5분봉 종가, 높아지는 저점, 정규장 거래량가중평균가격 회복과 동시간대 상대거래량 1.2 이상을 관찰한다. 확인되더라도 기대수익 조건을 별도로 충족해야 한다.","risk_condition_ko":"1,260.17 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":216.625,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":216.3959671248715,"relative_volume":1.4338137240223572,"spread_bps":0.923275782475386,"day_high":217.04,"day_low":215.7,"execution_condition_ko":"215.00~215.16 정규장 지지, 거래량가중평균가격 회복, 검증된 동시간대 상대거래량 1.2 이상과 215.20 부근 실제 체결가의 비용 후 손익비를 함께 확인한다. / 216.30 초과 정규장 5분봉 마감과 재시험 유지 여부를 관찰한다. 돌파 확인만으로 진입하지 않고 손절·목표·비용을 재산정한다.","risk_condition_ko":"215 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"UNH","display_name":"UNH","is_held":false,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":424.75,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":421.9101029622696,"relative_volume":0.5563544069736431,"spread_bps":1.883106183649556,"day_high":424.9,"day_low":417.13,"execution_condition_ko":"위험 대응 조건: 422.4 이상 도달, 장중 확인 시 이익실현성 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"422.4 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"지금 실행 검토 가능","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":284.49,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":283.7017440960597,"relative_volume":0.8753629948081927,"spread_bps":4.570464253695764,"day_high":285.3399,"day_low":278.01,"execution_condition_ko":"상방 관찰: 291.40 돌파 후 유지 또는 성공적 재시험, 세션 거래량가중평균가격 지지, 같은 경과시간 기준 상대거래량 1.2 이상을 확인하고 손익비를 다시 산출한다. / 지지 관찰: 282.59–285.00에서 완성된 두 개의 15분봉 반전·유지와 이후 거래량가중평균가격 회복이 필요하다. 가격 접촉만으로 매수하지 않는다.","risk_condition_ko":"282.59 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":165.7,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":165.20168370065275,"relative_volume":2.458254233613465,"spread_bps":5.4319944472947705,"day_high":166.72,"day_low":161.78,"execution_condition_ko":"최신 정규장 가격, 거래일정·거래정지 여부, 공식 실적 발표 시각과 보고기간을 확보한다. 제공된 06:35 관측값 158.22는 지연된 장전 자료이므로 실행 신호로 사용하지 않는다. / 160 위 완료된 5분봉 두 개, 성공적인 재시험, 실시간 거래량가중평균가격 지지와 동시간대 상대거래량 1.2 이상을 확인한다.","risk_condition_ko":"156.53 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"AMT","display_name":"AMT","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":181.625,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":179.4511451239358,"relative_volume":0.7866977960443227,"spread_bps":8.811543121488963,"day_high":182.07,"day_low":177.2,"execution_condition_ko":"AMT의 실제 거래일·정규장 시간·거래 가능 상태·신선한 호가·스프레드를 먼저 확인한다. 현재 장중 조건 충족 여부는 미확인이다. / 180.00~181.30에서 하락 거래량 감소 후 181.30 및 정규장 거래량가중평균가격 회복을 관찰한다.","risk_condition_ko":"179 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1010.83,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":1006.8399287663602,"relative_volume":0.6754413136510098,"spread_bps":2.5722200237434794,"day_high":1011.25,"day_low":1001.23,"execution_condition_ko":"977.24–982.64에서 매도 거래량 감소와 지지 재시험을 관찰하되, 963 보호와 1000 저항을 사용할 때 실제 진입가에 주당비용을 더한 값이 977.80 이하여야 한다. 확인 후 가격이 이를 넘으면 진입하지 않는다. / 1008.37 위 연속 두 개의 5분봉 마감, 지지 재시험, 정규장 거래량가중평균가격 상회 및 동시간대 상대거래량 1.2 이상을 관찰한다. 기존 991 보호 예시로는 돌파 매수가 적격하지 않다.","risk_condition_ko":"977.24 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":95.145,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":94.50618234134758,"relative_volume":0.11107379329831094,"spread_bps":4.2038885969528375,"day_high":95.275,"day_low":93.12,"execution_condition_ko":"거래일 달력·정규장과 거래정지 상태·신선한 실행 가능 호가·스프레드·당일 거래량가중평균가격을 검증한다. / 92.45–93.01에서 5분봉 회복과 성공적인 재시험을 확인한다. 단순 접촉은 매수 신호가 아니다.","risk_condition_ko":"92.45 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":200.565,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":199.67441751672416,"relative_volume":0.41006481513663656,"spread_bps":3.4899663467541617,"day_high":200.74,"day_low":197.0,"execution_condition_ko":"PM 198.85~199.68 시험 후 199.68 위 연속 5분봉 2개, 재시험 지지, 최신 정규장 거래량가중평균가격 상회와 검증된 상대거래량 1.2 이상. / PM 눌림 진입은 첫 저항 203.03까지 비용 후 보상·위험 1.5 이상인지 확인한다. 205.79나 210.45로 목표를 멀리 옮겨 비율을 맞추지 않는다.","risk_condition_ko":"197.91 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":627.01,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":624.854421045592,"relative_volume":0.8596772913723171,"spread_bps":9.887726460831919,"day_high":628.01,"day_low":623.88,"execution_condition_ko":"거래 일정·실적 일정·최신 가격·포트폴리오 한도와 자료 신뢰성을 확인한다. 실제 한도 초과가 드러나면 초과 노출을 위험 감축한다. / 최초 검토 시각 이후 624.29 위 완료된 5분봉, 성공적인 재확인, 당일 거래량가중평균가격 지지와 동일시각 상대거래량 1.2 이상을 점검한다. 현재 충족 여부는 미확인이다.","risk_condition_ko":"602.57 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":410.6,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":410.2610020644877,"relative_volume":0.7911781147014636,"spread_bps":4.869853173927914,"day_high":411.7499,"day_low":407.28,"execution_condition_ko":"실제 거래일·정규장 운영·거래정지 여부와 최신 호가·5분봉·정규장 거래량가중평균가격·동일 경과시간 상대거래량을 확인한다. 현재 시계만으로 거래 상태나 조건 충족을 추정하지 않는다. / 402.61~404.74에서 높아지는 저점과 404.74 회복, 또는 398.01~399.75에서 별도의 반등과 399.75 회복을 확인한다. 단순 접촉은 매수 신호가 아니다.","risk_condition_ko":"402.61 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"BRK-B","display_name":"BRK-B","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":545.8,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":544.5701535612546,"relative_volume":0.5715367263396679,"spread_bps":2.5650421399777645,"day_high":546.34,"day_low":542.01,"execution_condition_ko":"2026-10-21T06:28:07.133248-04:00은 미국 동부시간 10:30 진입 검토 개시 시각 이전이다. 10:30은 만료가 아니며, 이 시계 정보만으로 거래일이나 실행 조건을 확정하지 않는다. / 최신 제공 장중봉은 미국 동부시간 2026-10-20 15:55이다. 현재 거래일의 시세와 실제 거래 일정을 먼저 확인한다.","risk_condition_ko":"533.5 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":224.11,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":226.5371379347475,"relative_volume":0.5890859348944698,"spread_bps":4.015078851686333,"day_high":228.835,"day_low":224.11,"execution_condition_ko":"거래일·세션·거래정지 여부·최신 시세와 새 유효기간을 확인한다. 10:30은 최초 검토 가능 시각이지 만료가 아니며, 제공된 기한이 이미 지났다는 증거도 없다. / 227.28 위 5분봉 두 개 연속 마감, 성공적 재시험, 당일 거래량가중평균가격 지지 및 동일 시각 대비 거래량 1.2배 이상을 확인한다.","risk_condition_ko":"221.56 이하 하락, 거래량 조건 확인 후 (매도 거래량 증가를 동반한 지속적 하향 이탈) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":104.81,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":105.67555813511552,"relative_volume":0.5833041195627839,"spread_bps":0.9541529507184882,"day_high":106.63,"day_low":104.79,"execution_condition_ko":"104.31–104.80에서 저점 상승과 지지 회복을 확인한다. 단순 도달은 진입 신호가 아니다. / 102.86–103.31 시험 후 103.31 회복·재시험을 관찰한다. 실제 진입가는 103.40 이하이면서 비용 차감 후 손익비 기준을 충족해야 한다.","risk_condition_ko":"102.86 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":175.835,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":177.36436558279522,"relative_volume":0.4148941813828295,"spread_bps":2.8434132332458337,"day_high":180.31,"day_low":175.72,"execution_condition_ko":"173.60–175.15에서 높아진 저점과 재시험을 확인하고 175.15 위 연속 5분봉 2개 종가, 신선한 정규장 거래량가중평균가격 지지, 동시간대 상대거래량 1.2 이상을 요구한다. 첫 보상 평가에는 179.30을 사용하며 지지선 접촉만으로 매수하지 않는다. / 180.26 위 연속 5분봉 2개 종가와 성공적 재시험을 감시한다. 추가 상승 목표와 구조적 손절가가 독립적으로 검증되지 않으면 돌파만으로 매수하지 않는다.","risk_condition_ko":"173.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"TXN","display_name":"Texas Instruments","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":279.53,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":283.18548964734214,"relative_volume":1.4737877989311485,"spread_bps":6.07957085382062,"day_high":286.54,"day_low":278.75,"execution_condition_ko":"272.01-273.59 방어를 관찰한다. 지지선 접촉만으로 매수하거나 이탈 후 물타기하지 않는다. / 280.52 회복, 283.13 통과, 284.47 안착을 순서대로 확인하고 실제 진입·손절·목표의 손익 구조를 다시 계산한다.","risk_condition_ko":"272.01 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"SNPS","display_name":"Synopsys","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":434.33,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":436.96990297024865,"relative_volume":0.49367632791337357,"spread_bps":17.027935017718466,"day_high":444.05,"day_low":432.94,"execution_condition_ko":"위험 대응 조건: 441.09 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"441.09 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"SCCO","display_name":"SCCO","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":183.7519,"market_data_asof":"2026-10-22T14:55:16+00:00","session_vwap":187.01403760095593,"relative_volume":1.3685102539624234,"spread_bps":10.879025239337937,"day_high":190.75,"day_low":183.69,"execution_condition_ko":"위험 대응 조건: 196.44 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"196.44 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:57:16+00:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
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
