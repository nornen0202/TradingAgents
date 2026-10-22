# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-22T05:12:36.456289+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261022T141025_local-freshness-kr-overlay",
  "producer_finished_at": "2026-10-22T14:10:57.884608+09:00",
  "analysis_run_id": "20261022T050013_local-scheduler-kr-full",
  "analysis_completed_at": "2026-10-22T07:34:14.045585+09:00",
  "analysis_trade_date_oldest": "2026-10-21",
  "analysis_trade_date_latest": "2026-10-21",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-22T14:10:00+09:00",
  "market_data_latest_at": "2026-10-22T14:10:00+09:00",
  "market_data_status": "FRESH"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-22T14:01:38.979632+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-22T14:01:38.979632+09:00",
    "run_started_at": "2026-10-22T14:01:14.156070+09:00",
    "run_finished_at": "2026-10-22T14:01:43.091388+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 8409800,
    "total_unrealized_pnl_krw": -6534436,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 9386452
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1222000,
      "market_value_krw": 2444000,
      "unrealized_pnl_krw": -2991000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 214750,
      "market_value_krw": 2147500,
      "unrealized_pnl_krw": -1176351
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 295500,
      "market_value_krw": 1477500,
      "unrealized_pnl_krw": -597143
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 161600,
      "market_value_krw": 646400,
      "unrealized_pnl_krw": -328600
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 490000,
      "market_value_krw": 490000,
      "unrealized_pnl_krw": -663000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 17400,
      "market_value_krw": 313200,
      "unrealized_pnl_krw": -255115
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 65400,
      "market_value_krw": 196200,
      "unrealized_pnl_krw": -103800
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 194100,
      "market_value_krw": 194100,
      "unrealized_pnl_krw": -180067
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 176700,
      "market_value_krw": 176700,
      "unrealized_pnl_krw": -105634
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 129300,
      "market_value_krw": 129300,
      "unrealized_pnl_krw": -43000
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 42400,
      "market_value_krw": 84800,
      "unrealized_pnl_krw": -33400
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 61800,
      "market_value_krw": 61800,
      "unrealized_pnl_krw": -51131
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 48300,
      "market_value_krw": 48300,
      "unrealized_pnl_krw": -6200
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":292000.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":302224.47681846045,"relative_volume":0.6886324654636548,"spread_bps":17.13796058269066,"day_high":315500.0,"day_low":291500.0,"execution_condition_ko":"위험 대응 조건: 331,500 이상 도달, 장중 확인 시 (매도에는 상대거래량 하한을 적용하지 않는다.) 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"331,500 이상 도달, 장중 확인 시 (매도에는 상대거래량 하한을 적용하지 않는다.) 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":161200.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":164912.5232542403,"relative_volume":1.1826927065704482,"spread_bps":6.205398696866273,"day_high":169200.0,"day_low":160600.0,"execution_condition_ko":"위험 대응 조건: 154,200 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"154,200 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":129100.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":135003.06965364513,"relative_volume":1.04559616774472,"spread_bps":7.748934521503293,"day_high":140800.0,"day_low":128200.0,"execution_condition_ko":"위험 대응 조건: 127,000 이하 하락, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"127,000 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":61800.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":62628.706623835176,"relative_volume":0.5353478929863763,"spread_bps":16.194331983805668,"day_high":63900.0,"day_low":61600.0,"execution_condition_ko":"위험 대응 조건: 64,800 이상 도달, 장중 확인 시 리스크 축소 · 추가 조건 확인 필요: 세 분석가 모두 저항대 도달 자체와 저항 실패를 구분했다. 약한 반등 거래량과 가격 거부 또는 돌파 후 회복 실패가 확인될 때 감축한다. (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"64,800 이상 도달, 장중 확인 시 리스크 축소 · 추가 조건 확인 필요: 세 분석가 모두 저항대 도달 자체와 저항 실패를 구분했다. 약한 반등 거래량과 가격 거부 또는 돌파 후 회복 실패가 확인될 때 감축한다.","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":490500.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":494524.27207221685,"relative_volume":0.5940693574884979,"spread_bps":10.198878123406425,"day_high":503000.0,"day_low":488000.0,"execution_condition_ko":"267260.KS의 실제 거래일·세션·현재가 시각·거래정지·변동성완화장치·호가단위를 먼저 검증 / 506500 돌파·재시험 지지와 당일 거래량가중평균가격 상회, 동일 경과시간 기준 상대거래량 1.2 이상을 확인하되 손익비 미달이면 계속 대기","risk_condition_ko":"485,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":17400.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":17535.94808932506,"relative_volume":0.5299644069092401,"spread_bps":5.748778384593273,"day_high":17720.0,"day_low":17280.0,"execution_condition_ko":"010140.KS 실제 거래일·정규장 운영·거래정지 여부와 타임스탬프가 있는 최신 가격·호가·거래량 확보. / 010140.KS 17170~17270원 지지 후보대 유지 또는 이탈 후 재탈환 실패 확인.","risk_condition_ko":"17,170 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":1220000.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":1253026.6520129745,"relative_volume":0.6866907549282569,"spread_bps":8.193363375665712,"day_high":1297000.0,"day_low":1204000.0,"execution_condition_ko":"000660.KS의 1329000~1332000원 돌파·재시험 지지, 신선한 당일 거래량가중평균가격 상회와 동일 시간대 상대거래량 1.2배 이상을 관찰한다. 충족돼도 현재 계획에서는 매수가 발동하지 않는다. / 000660.KS의 1402000원 종가 회복·후속 지지 후 1467000원까지의 비용 후 손익비와 근거 있는 손절폭을 다시 계산한다. 추세 판단 개선과 신규 매수 승인을 구분한다.","risk_condition_ko":"1,254,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":214250.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":218826.34863238782,"relative_volume":0.5417393723785916,"spread_bps":23.33722287047841,"day_high":226000.0,"day_low":213500.0,"execution_condition_ko":"실제 거래일·정규장 일정·거래 가능 상태·최신 체결시각·봉 간격을 먼저 확인한다. 전일 20:00 지연 자료와 산식 미확인 상대거래량 18.24는 현재 진입 신호로 사용하지 않는다. / 228000원 돌파·재지지, 230500~233500원 회복, 당일 거래량가중평균가격 상회와 검증된 동일 시간대 누적 상대거래량 1.2 이상을 관찰한다. 충족만으로 자동 매수하지 않는다.","risk_condition_ko":"217,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":194500.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":196150.61961286148,"relative_volume":0.8167815870723261,"spread_bps":5.142710208279763,"day_high":202500.0,"day_low":190700.0,"execution_condition_ko":"042700.KS 최신 정규장 자료에서 212000원 돌파·재지지, 당일 거래량가중평균가격 상회, 검증된 동시간대 상대거래량 1.2배 이상 확인. 1.2배는 제안 기준이지 관측값이 아니다. / 042700.KS 197400~198000원 지지 유지와 이탈 후 회복 여부 확인. 추가 하방 참고 구간은 190800~192200원이며 구조적 손절 기준은 187500원이다.","risk_condition_ko":"197,400 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":176500.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":177512.88171999433,"relative_volume":0.6108432556366158,"spread_bps":5.667327854916407,"day_high":179300.0,"day_low":176300.0,"execution_condition_ko":"035420.KS의 실제 거래 일정과 신선한 정규장 자료를 확보하고 181,800원·183,300원의 회복 및 재확인, 동일 거래일 거래량가중평균가 지지와 시간대 보정 상대거래량을 점검한다. / 185,000원 상회 종가, 갱신된 20거래일 평균 대비 1.2배 이상의 하루 거래량, 다음 실제 거래일의 지지를 관찰한다. 통과하더라도 매수 경제성과 별도 승인 여부를 다시 판단한다.","risk_condition_ko":"177,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":65500.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":66033.00932416874,"relative_volume":0.40445345052739845,"spread_bps":30.53435114503817,"day_high":67800.0,"day_low":64800.0,"execution_condition_ko":"058470.KQ 원문 접수 시각과 재무통화·단위·기간·주식 기준 확인 및 요약·분기 자료 충돌 해소 / 실제 정규거래 세션, 최신 체결·호가, 당일 거래량가중평균가격과 동시간대 상대거래량 검증","risk_condition_ko":"66,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":48900.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":48766.58677422277,"relative_volume":0.8237257364112042,"spread_bps":10.21972406745018,"day_high":51100.0,"day_low":47350.0,"execution_condition_ko":"403870.KQ의 51,900 회복과 52,800~52,900 돌파·재지지를 신선한 정규장 자료로 확인한다. / 55,000~55,300 회복과 거래량 확대가 낮아지는 고점 구조를 개선하는지 확인하고, 첫 유효 저항까지 비용 후 손익비를 다시 계산한다.","risk_condition_ko":"51,881 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":42300.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":43474.87628184514,"relative_volume":0.44412633109654126,"spread_bps":11.813349084465445,"day_high":45300.0,"day_low":42100.0,"execution_condition_ko":"43,050~43,250에서 실제 방어·회복을 관찰하되 가격 접촉만으로 매수하지 않는다. / 45,700~46,400 반등 이후의 회복 실패를 추가 감축 신호로 감시한다. 현재 가격이 구간 아래라는 사실만으로 새 실패 신호를 선언하지 않는다.","risk_condition_ko":"43,050 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"064400.KS","display_name":"LG CNS","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":73200.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":73632.63145664388,"relative_volume":1.8399906297872122,"spread_bps":13.651877133105803,"day_high":74800.0,"day_low":71400.0,"execution_condition_ko":"실제 거래일·정규장·거래정지 상태·최신 체결 시각을 먼저 확인한다. 현재 보유 유지 판단을 당일 지지 확인으로 오해하지 않는다. / 71000~71600원 지지와 71600원 회복 또는 72800원 돌파·재시험을 관찰한다. 새로운 구조적 손절과 현실적인 첫 저항 기준의 비용 후 보상/위험이 부족하면 거래를 건너뛴다.","risk_condition_ko":"71,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"396300.KQ","display_name":"396300","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":10010.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":10259.14244978806,"relative_volume":0.6512627395216339,"spread_bps":9.995002498750624,"day_high":10880.0,"day_low":9890.0,"execution_condition_ko":"396300.KQ의 11,140원 요약값과 마지막 분봉 11,410원 차이를 대조하고 최신 호가를 확보한다. 요청한 5분봉 대신 반환된 1분봉을 그대로 사용하지 말고 완성된 5분봉을 검증한다. / 실제 거래일·휴장·단축거래 여부, 거래 가능 상태, 공식 시장경보, 호가 차이·잔량, 당일 거래량가중평균가격과 동일 경과시간 기준 상대거래량을 확인한다.","risk_condition_ko":"11,250 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"131290.KQ","display_name":"티에스이","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":259500.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":265092.5514712581,"relative_volume":0.9072271954478223,"spread_bps":19.249278152069298,"day_high":285500.0,"day_low":257000.0,"execution_condition_ko":"제공된 기준시계는 2026-10-22T06:52:15.581419+09:00이다. 실제 거래일·정규장 일정·거래정지·호가 최신성을 별도로 확인한다. 10:30은 향후 시험 매수의 최초 활성화 하한이지 만료시각이 아니다. 확인된 주문 만료시각은 없으며 다음 세션으로 임의 이월하지 않는다. / 요청한 5분봉과 제공된 1분봉, 요약 가격·거래량의 불일치를 해소한다. 전일 야간 지연 자료를 제외하고 실제 정규장 5분봉·거래량가중평균가격·시간대 보정 상대거래량을 확보한다.","risk_condition_ko":"258,000 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"018260.KS","display_name":"삼성SDS","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":208000.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":211837.20987822997,"relative_volume":3.052069125092185,"spread_bps":24.067388688327316,"day_high":218000.0,"day_low":198000.0,"execution_condition_ko":"202656원 단기 평균선과 203901원 거래량가중이동평균의 최신 값을 재계산하고 회복 여부를 확인한다. 203901원은 장중 거래량가중평균가격이 아니다. / 205500원 돌파·재지지, 장중 거래량가중평균가격 상회, 과거 동일 시간대 대비 상대거래량 1.2 이상을 확인한다. 위험 축소 사유와 비용 차감 보상·위험까지 개선되어야 매수 계획을 새로 수립한다.","risk_condition_ko":"194,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"014950.KQ","display_name":"014950","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":7580.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":8211.567740798457,"relative_volume":0.5631527349479102,"spread_bps":26.350461133069828,"day_high":8690.0,"day_low":7550.0,"execution_condition_ko":"014950.KQ의 기준 시계는 2026-10-22T06:12:43.986537+09:00이다. 10:30 한국시간은 최초 시범진입 검토시각이지 만료나 자동 활성화 시각이 아니다. 정규장 운영일·휴장·조기폐장·거래정지·시장경보를 별도로 확인한다. 검증된 만료가 없어 주문 활성화나 다음 세션 이월을 선언하지 않는다. / 014950.KQ의 신선한 호가·스프레드·실제 5분봉·세션 거래량가중평균가격·동일시간대 상대거래량을 확보한다. 전일 거래량 2.41배를 당일 상대거래량으로 대체하지 않는다.","risk_condition_ko":"7,977 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"373220.KS","display_name":"LG에너지솔루션","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":394750.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":397047.98742340406,"relative_volume":0.762290888150432,"spread_bps":12.66624445851805,"day_high":409000.0,"day_low":391500.0,"execution_condition_ko":"373220.KS의 원공시 영향·최신 재무여력·보유 집중도·거래 가능 상태를 먼저 확인한다. 중립·보수 분석가의 의견대로 잔여 노출 점검과 재진입 준비를 병행한다. / 373220.KS의 402500~405700원 지지 회복 후 검증된 연속 5분봉 두 개의 유지, 당일 거래량가중평균가격 상회, 동일 경과시간 상대거래량 1.2 이상을 관찰한다. 모두 제안 필터이며 관측된 신호가 아니다.","risk_condition_ko":"402,500 이하 하락, 종가 확인 후 (확정 종가 하회와 일봉 거래량 증가를 함께 확인) 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010950.KS","display_name":"S-Oil","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":139700.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":140254.97041048494,"relative_volume":1.202989489576478,"spread_bps":7.160759040458289,"day_high":149200.0,"day_low":137200.0,"execution_condition_ko":"010950.KS의 거래일과 거래 상태를 확인하고 일관된 최신 정규장 호가·봉·당일 거래량가중평균가격·동일 시간대 거래량 기준을 확보한다. / 142200–144000의 회복과 재시험 지지를 관찰한다. 단순 접촉은 매수 신호가 아니다. 137800의 미회복 이탈은 손절 전환 조건이다.","risk_condition_ko":"151,135 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":194300.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":194621.43713123826,"relative_volume":0.7785925482136347,"spread_bps":5.148005148005147,"day_high":196300.0,"day_low":192600.0,"execution_condition_ko":"033780.KS가 196400원을 초과 돌파·재지지하고 장중 거래량가중평균가격과 상대거래량 조건을 충족하면 첫 진입 검토 우선순위를 높인다. 단순 저항 접근은 매수 신호가 아니다. / 033780.KS의 189400~190900원 방어, 하락 거래량 축소와 반등 체결 증가를 감시한다. 190900원 초과 종가 회복 전에는 전체 목표비중 진입을 검토하지 않는다.","risk_condition_ko":"189,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":195500.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":195664.26107116736,"relative_volume":0.9800427660548612,"spread_bps":5.116398055768739,"day_high":198400.0,"day_low":191200.0,"execution_condition_ko":"068270.KS: 거래일·정규장 상태·거래 제한·호가 시각·스프레드·5분봉 집계와 전체 보유 집중도를 먼저 확인한다. / 068270.KS: 195,100~196,800원 방어, 저점 상승과 거래량가중평균가 회복을 관찰한다. 동시간대 상대거래량 1.2 이상은 제안된 매수 조건이지 이미 충족된 관측치가 아니다.","risk_condition_ko":"195,100 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"000100.KS","display_name":"000100","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":84000.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":84275.75199045465,"relative_volume":1.231662943111527,"spread_bps":11.911852293031567,"day_high":86500.0,"day_low":82800.0,"execution_condition_ko":"위험 대응 조건: 88,500 이상 도달, 2개 봉 확인 후 이익실현성 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"88,500 이상 도달, 2개 봉 확인 후 이익실현성 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":133700.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":134682.9153236242,"relative_volume":0.3087899801486081,"spread_bps":7.482229704451926,"day_high":136400.0,"day_low":132500.0,"execution_condition_ko":"위험 대응 조건: 134,600 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"134,600 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":143500.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":143894.05469549503,"relative_volume":0.9106284332108305,"spread_bps":13.927576601671309,"day_high":151100.0,"day_low":140400.0,"execution_condition_ko":"위험 대응 조건: 160,900 이상 도달, 2개 봉 확인 후 리스크 축소 · 추가 조건 확인 필요: 제공된 분석의 159,600–160,900원 저항 구간에서 거부가 확인되면 초기 축소의 미집행분에 활용한다. 필수 매도 가격이나 이익 실현 목표가 아니며, 해당 가격을 기다리느라 축소를 미루지 않는다. (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"160,900 이상 도달, 2개 봉 확인 후 리스크 축소 · 추가 조건 확인 필요: 제공된 분석의 159,600–160,900원 저항 구간에서 거부가 확인되면 초기 축소의 미집행분에 활용한다. 필수 매도 가격이나 이익 실현 목표가 아니며, 해당 가격을 기다리느라 축소를 미루지 않는다.","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"018880.KS","display_name":"018880","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":3740.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":3761.2752058512174,"relative_volume":0.3786894640052062,"spread_bps":13.377926421404682,"day_high":3865.0,"day_low":3720.0,"execution_condition_ko":"위험 대응 조건: 3,775 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"3,775 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"079650.KQ","display_name":"079650","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":7030.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":7262.547667520723,"relative_volume":0.2739210189365715,"spread_bps":28.449502133712663,"day_high":7645.0,"day_low":7000.0,"execution_condition_ko":"위험 대응 조건: 7,320 이하 하락, 2개 봉 확인 후 (실제 거래가 있는 연속 두 개의 5분봉 종가가 7320 미만이고 회복하지 못할 때) 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"7,320 이하 하락, 2개 봉 확인 후 (실제 거래가 있는 연속 두 개의 5분봉 종가가 7320 미만이고 회복하지 못할 때) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"003230.KS","display_name":"003230","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":1232000.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":1240146.8602630927,"relative_volume":0.6808921957057039,"spread_bps":8.120178643930167,"day_high":1268000.0,"day_low":1224000.0,"execution_condition_ko":"위험 대응 조건: 1,216,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"1,216,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"011200.KS","display_name":"011200","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":22600.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":22674.83644767315,"relative_volume":0.6163505729971467,"spread_bps":22.099447513812155,"day_high":23200.0,"day_low":22450.0,"execution_condition_ko":"위험 대응 조건: 22,850 이하 하락, 종가 확인 후 (방어적 매도에는 거래량 확인을 필수로 요구하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"22,850 이하 하락, 종가 확인 후 (방어적 매도에는 거래량 확인을 필수로 요구하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":519000.0,"market_data_asof":"2026-10-22T14:10:00+09:00","session_vwap":532909.1341303296,"relative_volume":0.8964403360552932,"spread_bps":19.249278152069298,"day_high":554000.0,"day_low":518000.0,"execution_condition_ko":"위험 대응 조건: 526,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"526,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-22T14:12:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-22T14:05:33.672832+09:00",
  "as_of": "2026-10-22T14:04:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
