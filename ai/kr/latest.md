# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-22T03:10:57.727205+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261022T120917_local-freshness-kr-overlay",
  "producer_finished_at": "2026-10-22T12:09:46.323812+09:00",
  "analysis_run_id": "20261022T050013_local-scheduler-kr-full",
  "analysis_completed_at": "2026-10-22T07:34:14.045585+09:00",
  "analysis_trade_date_oldest": "2026-10-21",
  "analysis_trade_date_latest": "2026-10-21",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-22T12:09:00+09:00",
  "market_data_latest_at": "2026-10-22T12:09:00+09:00",
  "market_data_status": "FRESH"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-22T12:01:40.894599+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-22T12:01:40.894599+09:00",
    "run_started_at": "2026-10-22T12:01:14.589093+09:00",
    "run_finished_at": "2026-10-22T12:01:44.897033+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 8545710,
    "total_unrealized_pnl_krw": -6398526,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 9522362
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1248000,
      "market_value_krw": 2496000,
      "unrealized_pnl_krw": -2939000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 216250,
      "market_value_krw": 2162500,
      "unrealized_pnl_krw": -1161351
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 302500,
      "market_value_krw": 1512500,
      "unrealized_pnl_krw": -562143
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 165200,
      "market_value_krw": 660800,
      "unrealized_pnl_krw": -314200
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 495500,
      "market_value_krw": 495500,
      "unrealized_pnl_krw": -657500
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 17620,
      "market_value_krw": 317160,
      "unrealized_pnl_krw": -251155
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 66000,
      "market_value_krw": 198000,
      "unrealized_pnl_krw": -102000
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 195200,
      "market_value_krw": 195200,
      "unrealized_pnl_krw": -178967
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 177300,
      "market_value_krw": 177300,
      "unrealized_pnl_krw": -105034
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 132300,
      "market_value_krw": 132300,
      "unrealized_pnl_krw": -40000
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 43550,
      "market_value_krw": 87100,
      "unrealized_pnl_krw": -31100
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 62700,
      "market_value_krw": 62700,
      "unrealized_pnl_krw": -50231
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 48650,
      "market_value_krw": 48650,
      "unrealized_pnl_krw": -5850
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":165600.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":165778.69330341782,"relative_volume":1.4188135270119726,"spread_bps":6.0368246302444915,"day_high":169200.0,"day_low":162500.0,"execution_condition_ko":"위험 대응 조건: 154,200 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"154,200 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":132200.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":135954.17878908178,"relative_volume":1.4532764031516838,"spread_bps":7.567158531971245,"day_high":140800.0,"day_low":130000.0,"execution_condition_ko":"위험 대응 조건: 127,000 이하 하락, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"127,000 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":495500.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":496130.74990551145,"relative_volume":0.5922948350847058,"spread_bps":10.085728693898135,"day_high":503000.0,"day_low":491000.0,"execution_condition_ko":"267260.KS의 실제 거래일·세션·현재가 시각·거래정지·변동성완화장치·호가단위를 먼저 검증 / 506500 돌파·재시험 지지와 당일 거래량가중평균가격 상회, 동일 경과시간 기준 상대거래량 1.2 이상을 확인하되 손익비 미달이면 계속 대기","risk_condition_ko":"485,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":302000.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":309319.44686032354,"relative_volume":0.4537022525284865,"spread_bps":16.542597187758478,"day_high":315500.0,"day_low":301000.0,"execution_condition_ko":"원공시의 표시통화·단위·기간·공개 시점·주식 기준과 예탁증서 비율 적용 여부를 확인하고 현금흐름표 이익 출발점 불일치를 조정한다. / 계좌 총비중 3%와 종목 손실예산 0.25% 초과 여부를 먼저 확인한다. 초과분 축소는 저항 구간 도달과 독립적으로 집행한다.","risk_condition_ko":"331,500 이상 도달, 장중 확인 시 (매도에는 상대거래량 하한을 적용하지 않는다.) 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":177400.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":177809.1337896383,"relative_volume":0.6653100527998003,"spread_bps":5.635390250774866,"day_high":179300.0,"day_low":176300.0,"execution_condition_ko":"035420.KS의 실제 거래 일정과 신선한 정규장 자료를 확보하고 181,800원·183,300원의 회복 및 재확인, 동일 거래일 거래량가중평균가 지지와 시간대 보정 상대거래량을 점검한다. / 185,000원 상회 종가, 갱신된 20거래일 평균 대비 1.2배 이상의 하루 거래량, 다음 실제 거래일의 지지를 관찰한다. 통과하더라도 매수 경제성과 별도 승인 여부를 다시 판단한다.","risk_condition_ko":"177,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":62700.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":62877.95028539011,"relative_volume":0.5967495367912395,"spread_bps":15.936254980079681,"day_high":63900.0,"day_low":62200.0,"execution_condition_ko":"61500~62600원 방어 구간의 유지와 이탈 후 회복 능력을 관찰한다. 64800원 회복만으로 매수하지 않는다. / 65600원·66400원·66600원 매물 소화를 확인한다. 66600원 지지 전환은 약세 판단의 재검토 신호이지 현재 매수 주문이 아니다.","risk_condition_ko":"64,800 이상 도달, 장중 확인 시 리스크 축소 · 추가 조건 확인 필요: 세 분석가 모두 저항대 도달 자체와 저항 실패를 구분했다. 약한 반등 거래량과 가격 거부 또는 돌파 후 회복 실패가 확인될 때 감축한다.","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":17680.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":17542.381936200065,"relative_volume":0.6022266147678574,"spread_bps":5.654509471303364,"day_high":17720.0,"day_low":17280.0,"execution_condition_ko":"010140.KS 실제 거래일·정규장 운영·거래정지 여부와 타임스탬프가 있는 최신 가격·호가·거래량 확보. / 010140.KS 17170~17270원 지지 후보대 유지 또는 이탈 후 재탈환 실패 확인.","risk_condition_ko":"17,170 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":43450.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":44023.424300988125,"relative_volume":0.42053539143458646,"spread_bps":11.500862564692351,"day_high":45300.0,"day_low":43100.0,"execution_condition_ko":"43,050~43,250에서 실제 방어·회복을 관찰하되 가격 접촉만으로 매수하지 않는다. / 45,700~46,400 반등 이후의 회복 실패를 추가 감축 신호로 감시한다. 현재 가격이 구간 아래라는 사실만으로 새 실패 신호를 선언하지 않는다.","risk_condition_ko":"43,050 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":1244000.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":1270910.4214231188,"relative_volume":0.7020552955000452,"spread_bps":8.041817450743867,"day_high":1297000.0,"day_low":1239000.0,"execution_condition_ko":"000660.KS의 1329000~1332000원 돌파·재시험 지지, 신선한 당일 거래량가중평균가격 상회와 동일 시간대 상대거래량 1.2배 이상을 관찰한다. 충족돼도 현재 계획에서는 매수가 발동하지 않는다. / 000660.KS의 1402000원 종가 회복·후속 지지 후 1467000원까지의 비용 후 손익비와 근거 있는 손절폭을 다시 계산한다. 추세 판단 개선과 신규 매수 승인을 구분한다.","risk_condition_ko":"1,254,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":216250.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":220611.19013348676,"relative_volume":0.616254049914962,"spread_bps":23.121387283236995,"day_high":226000.0,"day_low":215000.0,"execution_condition_ko":"실제 거래일·정규장 일정·거래 가능 상태·최신 체결시각·봉 간격을 먼저 확인한다. 전일 20:00 지연 자료와 산식 미확인 상대거래량 18.24는 현재 진입 신호로 사용하지 않는다. / 228000원 돌파·재지지, 230500~233500원 회복, 당일 거래량가중평균가격 상회와 검증된 동일 시간대 누적 상대거래량 1.2 이상을 관찰한다. 충족만으로 자동 매수하지 않는다.","risk_condition_ko":"217,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":194400.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":197863.81816655665,"relative_volume":0.8706447114493419,"spread_bps":5.145356315924878,"day_high":202500.0,"day_low":193600.0,"execution_condition_ko":"042700.KS 최신 정규장 자료에서 212000원 돌파·재지지, 당일 거래량가중평균가격 상회, 검증된 동시간대 상대거래량 1.2배 이상 확인. 1.2배는 제안 기준이지 관측값이 아니다. / 042700.KS 197400~198000원 지지 유지와 이탈 후 회복 여부 확인. 추가 하방 참고 구간은 190800~192200원이며 구조적 손절 기준은 187500원이다.","risk_condition_ko":"197,400 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":65900.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":66426.81406691346,"relative_volume":0.43331346121037556,"spread_bps":15.186028853454822,"day_high":67800.0,"day_low":65600.0,"execution_condition_ko":"058470.KQ 원문 접수 시각과 재무통화·단위·기간·주식 기준 확인 및 요약·분기 자료 충돌 해소 / 실제 정규거래 세션, 최신 체결·호가, 당일 거래량가중평균가격과 동시간대 상대거래량 검증","risk_condition_ko":"66,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":48500.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":49417.9902112443,"relative_volume":0.7504396441175929,"spread_bps":10.31459515214028,"day_high":51100.0,"day_low":48350.0,"execution_condition_ko":"403870.KQ의 51,900 회복과 52,800~52,900 돌파·재지지를 신선한 정규장 자료로 확인한다. / 55,000~55,300 회복과 거래량 확대가 낮아지는 고점 구조를 개선하는지 확인하고, 첫 유효 저항까지 비용 후 손익비를 다시 계산한다.","risk_condition_ko":"51,881 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"064400.KS","display_name":"LG CNS","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":73600.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":73718.40266419438,"relative_volume":2.295320827653015,"spread_bps":13.596193065941536,"day_high":74800.0,"day_low":71400.0,"execution_condition_ko":"실제 거래일·정규장·거래정지 상태·최신 체결 시각을 먼저 확인한다. 현재 보유 유지 판단을 당일 지지 확인으로 오해하지 않는다. / 71000~71600원 지지와 71600원 회복 또는 72800원 돌파·재시험을 관찰한다. 새로운 구조적 손절과 현실적인 첫 저항 기준의 비용 후 보상/위험이 부족하면 거래를 건너뛴다.","risk_condition_ko":"71,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"396300.KQ","display_name":"396300","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":10180.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":10292.754853237959,"relative_volume":0.9284764165972048,"spread_bps":9.818360333824252,"day_high":10880.0,"day_low":9920.0,"execution_condition_ko":"396300.KQ의 11,140원 요약값과 마지막 분봉 11,410원 차이를 대조하고 최신 호가를 확보한다. 요청한 5분봉 대신 반환된 1분봉을 그대로 사용하지 말고 완성된 5분봉을 검증한다. / 실제 거래일·휴장·단축거래 여부, 거래 가능 상태, 공식 시장경보, 호가 차이·잔량, 당일 거래량가중평균가격과 동일 경과시간 기준 상대거래량을 확인한다.","risk_condition_ko":"11,250 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"131290.KQ","display_name":"티에스이","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":261000.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":267944.0322829648,"relative_volume":0.9993863644654145,"spread_bps":19.138755980861244,"day_high":285500.0,"day_low":258000.0,"execution_condition_ko":"제공된 기준시계는 2026-10-22T06:52:15.581419+09:00이다. 실제 거래일·정규장 일정·거래정지·호가 최신성을 별도로 확인한다. 10:30은 향후 시험 매수의 최초 활성화 하한이지 만료시각이 아니다. 확인된 주문 만료시각은 없으며 다음 세션으로 임의 이월하지 않는다. / 요청한 5분봉과 제공된 1분봉, 요약 가격·거래량의 불일치를 해소한다. 전일 야간 지연 자료를 제외하고 실제 정규장 5분봉·거래량가중평균가격·시간대 보정 상대거래량을 확보한다.","risk_condition_ko":"258,000 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"003230.KS","display_name":"003230","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1239000.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":1244949.9918019348,"relative_volume":0.6831167899776693,"spread_bps":8.074283407347597,"day_high":1268000.0,"day_low":1231000.0,"execution_condition_ko":"거래소의 실제 거래일·정규장 상태·거래제한, 시각이 명시된 체결 가능 호가·호가차이·장중 거래량가중평균가격·동시간대 상대거래량을 확인한다. 요청한 봉 주기와 반환된 봉 주기의 불일치도 먼저 해소한다. / 1216000~1218000에서 같은 주기 정규장 봉 두 개의 저점 상승, 장중 거래량가중평균가격 회복, 동시간대 상대거래량 1.2 이상을 관찰한다. 이 조건만으로 진입하지 않고 저항과 손익비를 다시 검증한다.","risk_condition_ko":"1,216,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"018260.KS","display_name":"삼성SDS","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":211500.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":212691.699787797,"relative_volume":3.869001775530236,"spread_bps":23.668639053254438,"day_high":218000.0,"day_low":198000.0,"execution_condition_ko":"202656원 단기 평균선과 203901원 거래량가중이동평균의 최신 값을 재계산하고 회복 여부를 확인한다. 203901원은 장중 거래량가중평균가격이 아니다. / 205500원 돌파·재지지, 장중 거래량가중평균가격 상회, 과거 동일 시간대 대비 상대거래량 1.2 이상을 확인한다. 위험 축소 사유와 비용 차감 보상·위험까지 개선되어야 매수 계획을 새로 수립한다.","risk_condition_ko":"194,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"014950.KQ","display_name":"014950","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":7770.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":8286.36502309769,"relative_volume":0.8149649623719617,"spread_bps":38.58520900321543,"day_high":8690.0,"day_low":7730.0,"execution_condition_ko":"014950.KQ의 기준 시계는 2026-10-22T06:12:43.986537+09:00이다. 10:30 한국시간은 최초 시범진입 검토시각이지 만료나 자동 활성화 시각이 아니다. 정규장 운영일·휴장·조기폐장·거래정지·시장경보를 별도로 확인한다. 검증된 만료가 없어 주문 활성화나 다음 세션 이월을 선언하지 않는다. / 014950.KQ의 신선한 호가·스프레드·실제 5분봉·세션 거래량가중평균가격·동일시간대 상대거래량을 확보한다. 전일 거래량 2.41배를 당일 상대거래량으로 대체하지 않는다.","risk_condition_ko":"7,977 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"373220.KS","display_name":"LG에너지솔루션","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":398500.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":397108.0136272669,"relative_volume":0.979293234179595,"spread_bps":12.539184952978058,"day_high":409000.0,"day_low":391500.0,"execution_condition_ko":"373220.KS의 원공시 영향·최신 재무여력·보유 집중도·거래 가능 상태를 먼저 확인한다. 중립·보수 분석가의 의견대로 잔여 노출 점검과 재진입 준비를 병행한다. / 373220.KS의 402500~405700원 지지 회복 후 검증된 연속 5분봉 두 개의 유지, 당일 거래량가중평균가격 상회, 동일 경과시간 상대거래량 1.2 이상을 관찰한다. 모두 제안 필터이며 관측된 신호가 아니다.","risk_condition_ko":"402,500 이하 하락, 종가 확인 후 (확정 종가 하회와 일봉 거래량 증가를 함께 확인) 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010950.KS","display_name":"S-Oil","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":140600.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":140427.95589595713,"relative_volume":1.3714892626206432,"spread_bps":14.224751066856332,"day_high":149200.0,"day_low":137200.0,"execution_condition_ko":"010950.KS의 거래일과 거래 상태를 확인하고 일관된 최신 정규장 호가·봉·당일 거래량가중평균가격·동일 시간대 거래량 기준을 확보한다. / 142200–144000의 회복과 재시험 지지를 관찰한다. 단순 접촉은 매수 신호가 아니다. 137800의 미회복 이탈은 손절 전환 조건이다.","risk_condition_ko":"151,135 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":195000.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":194513.34057112777,"relative_volume":0.7717963477606415,"spread_bps":5.126890540886952,"day_high":196300.0,"day_low":192600.0,"execution_condition_ko":"033780.KS가 196400원을 초과 돌파·재지지하고 장중 거래량가중평균가격과 상대거래량 조건을 충족하면 첫 진입 검토 우선순위를 높인다. 단순 저항 접근은 매수 신호가 아니다. / 033780.KS의 189400~190900원 방어, 하락 거래량 축소와 반등 체결 증가를 감시한다. 190900원 초과 종가 회복 전에는 전체 목표비중 진입을 검토하지 않는다.","risk_condition_ko":"189,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":135400.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":134786.75135820944,"relative_volume":0.36731688726668416,"spread_bps":7.382798080472499,"day_high":136400.0,"day_low":132500.0,"execution_condition_ko":"제공된 실행시각 2026-10-22T06:53:48.534012+09:00만으로 거래일·정규장·가격 신선도를 확정하지 않는다. 전일 야간 지연 표시, 1분·5분 봉과 요약가격·거래량 불일치를 먼저 해소한다. / 10:30은 확인된 거래일의 시험 매수 재검토 개시시각이지 만료시각이 아니다. 주문 유효기간은 미확인이므로 새 만료일을 만들거나 다음 거래일로 자동 이월하지 않는다.","risk_condition_ko":"134,600 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":197900.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":195397.61505409135,"relative_volume":1.147343365374042,"spread_bps":5.051780752715333,"day_high":198400.0,"day_low":191200.0,"execution_condition_ko":"068270.KS: 거래일·정규장 상태·거래 제한·호가 시각·스프레드·5분봉 집계와 전체 보유 집중도를 먼저 확인한다. / 068270.KS: 195,100~196,800원 방어, 저점 상승과 거래량가중평균가 회복을 관찰한다. 동시간대 상대거래량 1.2 이상은 제안된 매수 조건이지 이미 충족된 관측치가 아니다.","risk_condition_ko":"195,100 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"000100.KS","display_name":"000100","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":85200.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":84075.85726637917,"relative_volume":1.380739028222642,"spread_bps":11.743981209630064,"day_high":86500.0,"day_low":82800.0,"execution_condition_ko":"위험 대응 조건: 88,500 이상 도달, 2개 봉 확인 후 이익실현성 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"88,500 이상 도달, 2개 봉 확인 후 이익실현성 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":145100.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":143791.40998555525,"relative_volume":1.1902529415664116,"spread_bps":13.783597518952446,"day_high":151100.0,"day_low":140400.0,"execution_condition_ko":"위험 대응 조건: 160,900 이상 도달, 2개 봉 확인 후 리스크 축소 · 추가 조건 확인 필요: 제공된 분석의 159,600–160,900원 저항 구간에서 거부가 확인되면 초기 축소의 미집행분에 활용한다. 필수 매도 가격이나 이익 실현 목표가 아니며, 해당 가격을 기다리느라 축소를 미루지 않는다. (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"160,900 이상 도달, 2개 봉 확인 후 리스크 축소 · 추가 조건 확인 필요: 제공된 분석의 159,600–160,900원 저항 구간에서 거부가 확인되면 초기 축소의 미집행분에 활용한다. 필수 매도 가격이나 이익 실현 목표가 아니며, 해당 가격을 기다리느라 축소를 미루지 않는다.","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"018880.KS","display_name":"018880","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":3760.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":3767.452572649647,"relative_volume":0.46737315062058904,"spread_bps":13.30671989354624,"day_high":3865.0,"day_low":3725.0,"execution_condition_ko":"위험 대응 조건: 3,775 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"3,775 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"079650.KQ","display_name":"079650","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":7160.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":7307.191355397173,"relative_volume":0.3738141176272035,"spread_bps":56.100981767180926,"day_high":7645.0,"day_low":7010.0,"execution_condition_ko":"위험 대응 조건: 7,320 이하 하락, 2개 봉 확인 후 (실제 거래가 있는 연속 두 개의 5분봉 종가가 7320 미만이고 회복하지 못할 때) 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"7,320 이하 하락, 2개 봉 확인 후 (실제 거래가 있는 연속 두 개의 5분봉 종가가 7320 미만이고 회복하지 못할 때) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"011200.KS","display_name":"011200","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":22800.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":22683.386033374765,"relative_volume":0.7618727008397932,"spread_bps":21.953896816684964,"day_high":23200.0,"day_low":22450.0,"execution_condition_ko":"위험 대응 조건: 22,850 이하 하락, 종가 확인 후 (방어적 매도에는 거래량 확인을 필수로 요구하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"22,850 이하 하락, 종가 확인 후 (방어적 매도에는 거래량 확인을 필수로 요구하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":529000.0,"market_data_asof":"2026-10-22T12:09:00+09:00","session_vwap":536875.6924788472,"relative_volume":1.0838974620041142,"spread_bps":18.885741265344667,"day_high":554000.0,"day_low":526000.0,"execution_condition_ko":"위험 대응 조건: 526,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"526,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T12:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-22T11:01:08.594199+09:00",
  "as_of": "2026-10-22T11:00:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
