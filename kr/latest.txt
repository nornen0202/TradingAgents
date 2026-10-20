# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-20T01:04:49.704558+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261020T100007_local-freshness-kr-overlay",
  "producer_finished_at": "2026-10-20T10:01:43.426546+09:00",
  "analysis_run_id": "20261020T044511_local-scheduler-kr-full",
  "analysis_completed_at": "2026-10-20T06:50:32.590683+09:00",
  "analysis_trade_date_oldest": "2026-10-19",
  "analysis_trade_date_latest": "2026-10-19",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-20T10:01:00+09:00",
  "market_data_latest_at": "2026-10-20T10:01:00+09:00",
  "market_data_status": "FRESH"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-20T10:01:39.905926+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-20T10:01:39.905926+09:00",
    "run_started_at": "2026-10-20T10:00:07.832525+09:00",
    "run_finished_at": "2026-10-20T10:01:43.426546+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 8433720,
    "total_unrealized_pnl_krw": -6510516,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 9410372
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1210000,
      "market_value_krw": 2420000,
      "unrealized_pnl_krw": -3015000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 213000,
      "market_value_krw": 2130000,
      "unrealized_pnl_krw": -1193851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 310500,
      "market_value_krw": 1552500,
      "unrealized_pnl_krw": -522143
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 152400,
      "market_value_krw": 609600,
      "unrealized_pnl_krw": -365400
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 483000,
      "market_value_krw": 483000,
      "unrealized_pnl_krw": -670000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 17540,
      "market_value_krw": 315720,
      "unrealized_pnl_krw": -252595
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 68100,
      "market_value_krw": 204300,
      "unrealized_pnl_krw": -95700
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 202500,
      "market_value_krw": 202500,
      "unrealized_pnl_krw": -171667
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 178900,
      "market_value_krw": 178900,
      "unrealized_pnl_krw": -103434
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 135400,
      "market_value_krw": 135400,
      "unrealized_pnl_krw": -36900
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 43950,
      "market_value_krw": 87900,
      "unrealized_pnl_krw": -30300
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 63200,
      "market_value_krw": 63200,
      "unrealized_pnl_krw": -49731
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 50700,
      "market_value_krw": 50700,
      "unrealized_pnl_krw": -3800
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"SELL","strategy_ko":"매도·청산 검토","last_price":1209000.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":1228665.8568308915,"relative_volume":1.9220355341707183,"spread_bps":8.26787928896238,"day_high":1267000.0,"day_low":1201000.0,"execution_condition_ko":"위험 대응 조건: 1,208,000 이하 하락, 종가 확인 후 손절 조건 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"1,208,000 이하 하락, 종가 확인 후 손절 조건","decision_state_ko":"투자 근거 무효화","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"SELL","strategy_ko":"매도·청산 검토","last_price":43900.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":44384.6629046629,"relative_volume":0.7044823521895782,"spread_bps":34.14911781445646,"day_high":45700.0,"day_low":43500.0,"execution_condition_ko":"위험 대응 조건: 43,250 이하 하락, 종가 확인 후 손절 조건 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"43,250 이하 하락, 종가 확인 후 손절 조건","decision_state_ko":"투자 근거 무효화","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":63200.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":64136.81881840051,"relative_volume":1.4090790946794545,"spread_bps":15.83531274742676,"day_high":65600.0,"day_low":63000.0,"execution_condition_ko":"위험 대응 조건: 69,400 이하 하락, 장중 확인 시 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"69,400 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"지금 실행 검토 가능","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":17540.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":17792.507658321225,"relative_volume":1.7951807698302327,"spread_bps":17.08914839077186,"day_high":18140.0,"day_low":17510.0,"execution_condition_ko":"위험 대응 조건: 18,790 이상 도달, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"18,790 이상 도달, 2개 봉 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":50600.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":51378.151943207915,"relative_volume":1.1664565844549948,"spread_bps":19.743336623889437,"day_high":52900.0,"day_low":50200.0,"execution_condition_ko":"위험 대응 조건: 50,300 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"50,300 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":135500.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":134249.31771378647,"relative_volume":2.3493377925711614,"spread_bps":7.382798080472499,"day_high":137800.0,"day_low":130000.0,"execution_condition_ko":"353200.KS의 당일 거래일·정규장·거래정지·시장경보·마지막 체결 시각을 확인하고 요청한 5분봉과 반환된 1분봉의 불일치를 해소한다. / 137900~140500 회복·재시험 지지, 신선한 정규장 거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상을 함께 확인한다. 충족해도 순보상/위험 2 미만이면 대기한다.","risk_condition_ko":"137,900 이하 하락, 2개 봉 확인 후 (가격 실패 확인; 거래량 증가를 기다리지 않음) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":213000.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":215441.5242388047,"relative_volume":1.3822739963791248,"spread_bps":23.501762632197416,"day_high":219500.0,"day_low":211500.0,"execution_condition_ko":"먼저 거래일·정규장 운영·거래정지·신선한 호가·실제 오분봉과 기존 보유 위험 한도를 확인한다. / 222500원 돌파·재시험은 관찰 신호이며 자동 매수가 아니다.","risk_condition_ko":"219,500 이상 도달, 2개 봉 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":202000.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":205310.6314710275,"relative_volume":1.6642396524450118,"spread_bps":24.72187886279357,"day_high":211000.0,"day_low":201000.0,"execution_condition_ko":"212000원과 217500~218500원 회복·재시험 지지를 관찰한다. 218500원은 과거 야간자료 고가이므로 정규장 기준으로 재검증한다. / 227800~231500원 지지 전환, 상대강도지수 50 회복과 여러 거래일의 이동평균 수렴·확산 히스토그램 개선을 확인한다. 제공된 상대강도지수 41.41과 음의 히스토그램은 아직 추세 전환을 확증하지 않는다.","risk_condition_ko":"197,400 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":483000.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":495691.414263304,"relative_volume":1.3721689740728964,"spread_bps":10.357327809425167,"day_high":518000.0,"day_low":481500.0,"execution_condition_ko":"534,000 돌파·재시험, 신선한 거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상을 확인하되 가까운 543,000 저항까지 비용 차감 보상·위험비가 2배 미만이면 건너뛴다. 543,000의 지지 전환 등 구조 개선 시 별도 매수 판단을 갱신한다. / 485,000 및 473,500 이탈·회복 실패와 계좌 손실예산 초과 여부를 확인한다. 신규 진입보다 기존 노출의 축소·손절을 우선한다.","risk_condition_ko":"485,000 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":311000.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":319418.61703079427,"relative_volume":1.1142194107172505,"spread_bps":16.06425702811245,"day_high":329500.0,"day_low":310500.0,"execution_condition_ko":"278470.KS의 공식 거래일·정규장 개장시각·거래정지 여부·최신 호가 및 봉 시각을 먼저 확인한다. / 328900~331500원 회복 구간과 322500~325500원 반등 방어 구간의 유지 여부를 확인한다.","risk_condition_ko":"322,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":179100.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":181276.36910207817,"relative_volume":1.26719996996988,"spread_bps":5.585032113934655,"day_high":185000.0,"day_low":178600.0,"execution_condition_ko":"한국거래소의 당일 정규장 운영 여부와 타임스탬프가 있는 신선한 가격·체결·거래량을 먼저 확인한다. / 183800 돌파·재지지, 185450 회복, 실제 당일 거래량가중평균가격 유지와 동일 시간대 상대거래량 1.2 이상을 확인한다.","risk_condition_ko":"183,266 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":152300.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":156457.2753579983,"relative_volume":2.555663689531912,"spread_bps":6.563833278634722,"day_high":163300.0,"day_low":151800.0,"execution_condition_ko":"010120.KS의 결정 기준 시각은 2026-10-20T04:59:31.609339+09:00이고 일봉 가격 기준일은 2026-10-19다. 거래일·휴장·조기종료 달력, 정규장 여부, 호가 시각과 봉 간격은 별도 확인해야 한다. 이 시계만으로 실제 세션이나 진입 조건 충족을 단정하지 않는다. / 010120.KS의 2026-10-19 20:00 지연 가격 166600원, 해당 야간 거래량가중평균가격 및 산식 미확인 상대거래량 20.12배는 현재 정규장 실행 근거에서 제외한다.","risk_condition_ko":"173,100 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":68100.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":68880.45629891567,"relative_volume":0.9688601729232009,"spread_bps":14.695077149155033,"day_high":69800.0,"day_low":67600.0,"execution_condition_ko":"신선한 정규장 자료로 66100~67000원 지지 유지와 저점 상승을 확인한다. 지지 미이탈을 수요 회복으로 해석하지 않는다. / 70100~70800원과 71700~72700원 회복·재지지, 상대강도지수 50 회복 및 이동평균 수렴·확산 지표 막대값의 음수 폭 축소를 함께 확인한다.","risk_condition_ko":"70,564 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"SELL","strategy_ko":"매도·청산 검토","last_price":198400.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":199016.17374517376,"relative_volume":3.3389756823662804,"spread_bps":5.041593143433325,"day_high":202000.0,"day_low":195600.0,"execution_condition_ko":"위험 대응 조건: 199,300 이상 도달, 2개 봉 확인 후 이익실현성 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"199,300 이상 도달, 2개 봉 확인 후 이익실현성 축소","decision_state_ko":"투자 근거 무효화","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"396300.KQ","display_name":"396300","is_held":false,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":10910.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":10731.662698365253,"relative_volume":9.606826199222406,"spread_bps":9.170105456212745,"day_high":11250.0,"day_low":9470.0,"execution_condition_ko":"위험 대응 조건: 9,120 이상 도달, 장중 확인 시 이익실현성 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"9,120 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"지금 실행 검토 가능","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"086790.KS","display_name":"086790","is_held":false,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":124100.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":123946.52615201709,"relative_volume":1.251217849807605,"spread_bps":8.054772452678213,"day_high":125300.0,"day_low":122500.0,"execution_condition_ko":"위험 대응 조건: 125,600 이하 하락, 장중 확인 시 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"125,600 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"지금 실행 검토 가능","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":194700.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":193945.23398003716,"relative_volume":1.214695684379121,"spread_bps":5.137426149499101,"day_high":195500.0,"day_low":190900.0,"execution_condition_ko":"판단 시각은 2026-10-20T06:00:02.417412+09:00이며 일봉 기준일은 2026-10-19다. 실제 거래일·정규장 상태·시세 신선도는 확인되지 않았다. 10:30은 가장 이른 재검토 기준일 뿐 주문 활성화나 만료 시각이 아니다. 승인된 조건부 주문과 유효기간은 없다. / 요약가격 193,100원과 지연된 마지막 봉 190,700원의 불일치, 요청한 5분봉 대신 제공된 1분봉, 누락된 거래량 가중평균가격과 사용할 수 없는 거래량 자료를 해결한다.","risk_condition_ko":"189,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"131290.KQ","display_name":"티에스이","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":264500.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":268820.4041422287,"relative_volume":1.1962434259698624,"spread_bps":56.550424128180964,"day_high":276500.0,"day_low":262500.0,"execution_condition_ko":"131290.KQ의 일관된 시각표시 시세, 실제 거래일정·거래상태·호가차·잔량·완성된 5분봉·거래량가중평균가격을 확인한다. / 261000-267500을 새로 시험한 뒤 267500 재회복, 완성된 5분봉 2개의 저점 상승, 동시간대 상대거래량 1.2 이상을 확인한다.","risk_condition_ko":"261,148 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"373220.KS","display_name":"LG에너지솔루션","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":419000.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":423046.4019681542,"relative_volume":1.9264779430442533,"spread_bps":11.940298507462687,"day_high":432000.0,"day_low":417000.0,"execution_condition_ko":"373220.KS 거래일 달력·세션·최신 가격 시각·봉 간격·거래량을 확인하고 가격 및 봉 간격 불일치 해소 / 433000원 돌파와 428000~433000원 재지지, 거래량가중평균가격 상회 및 동시간대 상대거래량 1.2 이상 확인","risk_condition_ko":"428,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"018880.KS","display_name":"018880","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":3935.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":3924.204366515196,"relative_volume":1.6088885299150375,"spread_bps":12.714558169103624,"day_high":4050.0,"day_low":3860.0,"execution_condition_ko":"판단 시계는 2026-10-20T06:04:32.104895+09:00이며 가격 기준은 2026-10-19 완료 일봉이다. 실제 거래일·정규장·거래정지·시장경보·호가와 시세 타임스탬프는 별도로 확인한다. / 10:30은 최초 재심사 가능 시각이지 자동 매수나 만료시각이 아니다. 확인된 주문 만료시각은 없으며 다음 거래일로 자동 이월하지 않는다.","risk_condition_ko":"3,815 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":137700.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":139506.9158845024,"relative_volume":0.9861979114329553,"spread_bps":7.26480203414457,"day_high":141900.0,"day_low":136800.0,"execution_condition_ko":"090430.KS 135300–136000 지지구간에서 매도 압력이 약해지고 136000 위에서 마감한 연속 2개 완성 5분봉, 실시간 정규장 거래량가중평균가격 지지, 동일 경과시간 상대거래량 1.2 이상을 확인한다. 이는 재검토 조건이지 매수 승인이 아니다. / 090430.KS 140000 돌파 후 139100–140000 재시험 지지와 140000 재회복을 확인하되 142000까지의 제한된 보상을 다시 계산한다.","risk_condition_ko":"135,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"105560.KS","display_name":"105560","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":162700.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":161770.67269773537,"relative_volume":2.383551017228295,"spread_bps":6.148170919151552,"day_high":163300.0,"day_low":159900.0,"execution_condition_ko":"기존 105560.KS 보유량·순자산·은행업 노출·현금과 갭 위험을 먼저 확인한다. 한도 초과가 확인되면 가격 지지와 무관하게 초과 위험을 줄인다. / 2026-10-20의 실제 거래일·정규장과 최신 체결시각을 확인한다. 요약가 162700과 마지막 분봉 160700의 불일치 및 반환 간격 오류를 해결한다.","risk_condition_ko":"159,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"036460.KS","display_name":"036460","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":36200.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":36400.549855172074,"relative_volume":1.0125121322592463,"spread_bps":13.840830449826989,"day_high":36800.0,"day_low":36000.0,"execution_condition_ko":"거래일·정규장 상태·거래소 시각·호가 지연·일관된 봉 간격·매수매도 호가·거래량가중평균가격을 먼저 검증한다. / 35850~36150원에서 매도 거래량 감소 후 반등과 거래량가중평균가격 회복을 관찰하되 가격 접촉만으로 매수하지 않는다.","risk_condition_ko":"35,850 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"051900.KS","display_name":"051900","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":276500.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":279515.5648267009,"relative_volume":1.6947527157803988,"spread_bps":18.099547511312217,"day_high":284500.0,"day_low":270500.0,"execution_condition_ko":"051900.KS 거래일·정규장 일정·거래정지·시장경보·실적 일정을 확인하고 최신 호가·스프레드·체결·거래량가중평균가격을 확보한다. 전일 야간 지연 자료, 거래량과 상대거래량의 0값, 일봉 거래량가중이동평균을 당일 신호의 대체값으로 쓰지 않는다. / 051900.KS 270000~272000원 지지 시험 후 272000원 회복, 거래량가중평균가격 지지와 동일 시간대 상대거래량 1.2 이상을 관찰한다. 비용 후 보상 대비 위험 2배가 별도로 확보돼야 진입 재검토가 가능하다.","risk_condition_ko":"263,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"011200.KS","display_name":"011200","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":23500.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":23477.370844328634,"relative_volume":1.0874424039715385,"spread_bps":21.299254526091588,"day_high":23850.0,"day_low":23200.0,"execution_condition_ko":"결정 시각은 2026-10-20T05:43:52.347505+09:00이다. 제안된 현지 10:30은 가장 이른 소규모 진입 검토 시각이지 만료가 아니다. 거래일 달력, 정규장 운영 여부와 거래상태를 별도 확인하며 검증되지 않은 기한을 다음 거래일로 이월하지 않는다. / 오래되고 불일치하는 장중 자료를 완료된 정규장 5분봉, 당일 거래량가중평균가격, 체결 가능한 호가·스프레드와 동시간대 상대거래량으로 교체한다. 보고된 거래량 0을 매수세 부재로 해석하지 않는다.","risk_condition_ko":"22,800 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":580000.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":584456.6976723286,"relative_volume":3.060647224998388,"spread_bps":17.25625539257981,"day_high":595000.0,"day_low":575000.0,"execution_condition_ko":"600000원 돌파·재시험 지지 또는 554000~558000원 지지 후 558000원 회복을 최신 정규장 자료로 확인한다. / 554000원과 526000원 종가 이탈은 누적 위험 감축, 503000원 이탈은 기술 전술 청산 기준으로 관리한다.","risk_condition_ko":"554,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":151200.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":156324.71474212687,"relative_volume":1.4930638757021983,"spread_bps":6.6115702479338845,"day_high":162100.0,"day_low":151100.0,"execution_condition_ko":"위험 대응 조건: 154,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"154,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010950.KS","display_name":"S-Oil","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":143700.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":147904.89642809718,"relative_volume":2.8545398086582323,"spread_bps":6.9565217391304355,"day_high":156100.0,"day_low":143600.0,"execution_condition_ko":"위험 대응 조건: 150,200 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"150,200 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"018260.KS","display_name":"삼성SDS","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":198800.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":200719.83420699745,"relative_volume":1.1951523348281774,"spread_bps":5.031446540880503,"day_high":204500.0,"day_low":198000.0,"execution_condition_ko":"위험 대응 조건: 200,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"200,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"036930.KQ","display_name":"주성엔지니어링","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":201500.0,"market_data_asof":"2026-10-20T10:01:00+09:00","session_vwap":201823.16779836238,"relative_volume":1.347596888937407,"spread_bps":24.783147459727385,"day_high":209500.0,"day_low":198600.0,"execution_condition_ko":"위험 대응 조건: 195,628 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"195,628 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-20T10:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-19T14:43:50.029520+09:00",
  "as_of": "2026-10-19T14:40:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
