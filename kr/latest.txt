# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-19T01:48:59.518801+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261019T104025_pre-report-kr-overlay",
  "producer_finished_at": "2026-10-19T10:42:44.039016+09:00",
  "analysis_run_id": "20261019T044510_local-scheduler-kr-full",
  "analysis_completed_at": "2026-10-19T07:03:43.718255+09:00",
  "analysis_trade_date_oldest": "2026-10-16",
  "analysis_trade_date_latest": "2026-10-16",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-19T10:40:00+09:00",
  "market_data_latest_at": "2026-10-19T10:41:00+09:00",
  "market_data_status": "FRESH"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-19T10:42:40.719183+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-19T10:42:40.719183+09:00",
    "run_started_at": "2026-10-19T10:40:25.752011+09:00",
    "run_finished_at": "2026-10-19T10:42:44.039016+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 8674060,
    "total_unrealized_pnl_krw": -6270176,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 9650712
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1237000,
      "market_value_krw": 2474000,
      "unrealized_pnl_krw": -2961000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 217000,
      "market_value_krw": 2170000,
      "unrealized_pnl_krw": -1153851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 327500,
      "market_value_krw": 1637500,
      "unrealized_pnl_krw": -437143
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 160000,
      "market_value_krw": 640000,
      "unrealized_pnl_krw": -335000
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 507000,
      "market_value_krw": 507000,
      "unrealized_pnl_krw": -646000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 17820,
      "market_value_krw": 320760,
      "unrealized_pnl_krw": -247555
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
      "current_price_krw": 180800,
      "market_value_krw": 180800,
      "unrealized_pnl_krw": -101534
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 130600,
      "market_value_krw": 130600,
      "unrealized_pnl_krw": -41700
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 45250,
      "market_value_krw": 90500,
      "unrealized_pnl_krw": -27700
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 64400,
      "market_value_krw": 64400,
      "unrealized_pnl_krw": -48531
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 51700,
      "market_value_krw": 51700,
      "unrealized_pnl_krw": -2800
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":508000.0,"market_data_asof":"2026-10-19T10:40:00+09:00","session_vwap":499443.70349322486,"relative_volume":1.4368250822497388,"spread_bps":19.704433497536943,"day_high":512000.0,"day_low":485000.0,"execution_condition_ko":"위험 대응 조건: 487,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"487,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:50:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":68200.0,"market_data_asof":"2026-10-19T10:40:00+09:00","session_vwap":68289.28759772236,"relative_volume":1.0309731924715153,"spread_bps":14.652014652014651,"day_high":70100.0,"day_low":67000.0,"execution_condition_ko":"위험 대응 조건: 67,900 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"67,900 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:50:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":1245000.0,"market_data_asof":"2026-10-19T10:40:00+09:00","session_vwap":1234324.960325055,"relative_volume":1.7789743349866878,"spread_bps":8.028904054596548,"day_high":1264000.0,"day_low":1208000.0,"execution_condition_ko":"기준 시각은 2026-10-19T04:58:15.423251+09:00이다. 이 시각은 실제 정규장 여부나 거래 가능성을 입증하지 않는다. 한국시간 10:30은 향후 시험매수 검토의 가장 이른 시각이지 만료시각이 아니다. 활성 진입계획과 확정된 만료시각은 없다. / 1238000~1247000원 지지와 1332000원 회복을 관찰한다. 향후 매수 재평가에는 당일 거래량가중평균가격 지지와 비교 가능한 동시간대 상대거래량 1.2 이상이 필요하다. 산식이 검증되지 않은 27.11은 사용하지 않는다.","risk_condition_ko":"1,238,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"지금 실행 검토 가능","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:50:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":328500.0,"market_data_asof":"2026-10-19T10:40:00+09:00","session_vwap":331942.1790193958,"relative_volume":1.1829322460309415,"spread_bps":15.20912547528517,"day_high":339000.0,"day_low":325000.0,"execution_condition_ko":"거래소 달력·거래 가능 상태·최신 시세 타임스탬프·당일 거래량가중평균가격·검증된 5분봉을 확보한다. 과거 1분봉과 산식 불명의 상대거래량 27.01은 진입 확인에서 제외한다. / 331500원 회복, 337000원 돌파·재시험 지지와 동시간대 상대거래량 1.2 이상을 관찰한다. 2026-10-16 상승률 9.23%와 일일 거래량 약 1.35배는 현재 매수조건 충족을 대신하지 않는다.","risk_condition_ko":"298,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:50:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":160800.0,"market_data_asof":"2026-10-19T10:40:00+09:00","session_vwap":156465.55502284394,"relative_volume":1.7061336773247537,"spread_bps":6.2208398133748055,"day_high":161200.0,"day_low":150000.0,"execution_condition_ko":"판단 시계는 2026-10-19T04:58:16.212441+09:00이며 일봉 기준일은 2026-10-16이다. 실제 거래일·정규장·휴장 또는 단축장·거래정지·호가 신선도는 별도 확인이 필요하다. 시계만으로 주문 가능 상태나 지지 이탈을 판단하지 않는다. / 165600원 돌파·재시험 지지, 신선한 당일 거래량가중평균가격 상회, 동시간대 상대거래량 1.2배 이상을 관찰한다. 유효한 첫 저항까지 비용·슬리피지·갭 여유 반영 후 보상/위험 2배 이상이어야 신규 진입을 재평가한다. 비율을 맞추려고 손절을 임의로 좁히거나 첫 저항을 무시하지 않는다.","risk_condition_ko":"153,900 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:50:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":203500.0,"market_data_asof":"2026-10-19T10:40:00+09:00","session_vwap":203670.69631983055,"relative_volume":1.4525489347522658,"spread_bps":24.600246002460025,"day_high":210000.0,"day_low":198700.0,"execution_condition_ko":"211500원 돌파·재지지, 당일 거래량가중평균가격 상회와 동일 시간대 상대거래량 1.2 이상을 관찰하되 단독 매수 신호로 사용하지 않는다. / 213500~217500원 반등 실패와 228580~231500원 회복 실패를 구분해 확인하고 잔여 전술 비중을 축소한다.","risk_condition_ko":"190,800 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:50:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":180700.0,"market_data_asof":"2026-10-19T10:40:00+09:00","session_vwap":178133.59118451245,"relative_volume":0.8557415617039366,"spread_bps":5.535566011624688,"day_high":180800.0,"day_low":175100.0,"execution_condition_ko":"판단 시각은 2026-10-19T05:15:03.126355+09:00이며 연구일과 일치한다. 하지만 거래일·휴장·단축장 여부, 실제 정규장 상태, 호가 시각과 실행 가능성을 별도로 확인해야 한다. / 일봉 기준일은 2026-10-16이다. 2026-10-16T20:00:00+09:00의 장중 자료, 설명되지 않은 상대거래량 20.06, 요청과 반환 주기의 불일치는 당일 매수 확인에서 제외한다.","risk_condition_ko":"174,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:50:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":64500.0,"market_data_asof":"2026-10-19T10:40:00+09:00","session_vwap":63105.98854321743,"relative_volume":1.1661095384140838,"spread_bps":15.515903801396432,"day_high":64800.0,"day_low":62000.0,"execution_condition_ko":"거래소 일정·세션·봉 시각·호가 신선도를 먼저 확인한다. 과거 1분봉을 당일 5분봉 확인으로 대체하지 않는다. / 66400원 돌파·재시험 지지, 당일 거래대금가중평균가격 상회와 동일 경과시간 상대거래량 1.2 이상을 함께 관찰한다. 이는 제안된 재평가 기준이지 관측된 매수 신호가 아니다.","risk_condition_ko":"63,300 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:50:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":52000.0,"market_data_asof":"2026-10-19T10:40:00+09:00","session_vwap":52874.49726134585,"relative_volume":1.6855674459179437,"spread_bps":19.249278152069298,"day_high":55000.0,"day_low":51300.0,"execution_condition_ko":"403870.KQ의 실제 거래일·정규장·거래 가능 상태와 최신 호가, 정확한 5분봉, 당일 거래량가중평균가격 및 동시간대 상대거래량을 검증한다. / 50300~50924원 지지 재시험을 관찰하되 실제 체결가격과 가장 가까운 유효 저항으로 순손익비를 다시 계산한다. 55300원 돌파만으로는 매수하지 않는다.","risk_condition_ko":"50,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:50:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":217750.0,"market_data_asof":"2026-10-19T10:40:00+09:00","session_vwap":213187.6817413772,"relative_volume":1.4174834967847492,"spread_bps":22.962112514351322,"day_high":219500.0,"day_low":206500.0,"execution_condition_ko":"005930.KS의 정규장 달력·거래 가능 상태·최신 호가·거래량가중평균가격·동일 시간대 상대거래량을 먼저 확인한다. 215,500원은 2026-10-16 종가이고 과거 217,000원은 현재가가 아니다. / 222,500원 돌파·재시험 지지와 저점 상승은 관찰만 한다. 비용 후 보상/위험이 부족하면 소액 거래라도 매수하지 않는다.","risk_condition_ko":"221,500 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:50:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":17850.0,"market_data_asof":"2026-10-19T10:40:00+09:00","session_vwap":17783.856827097457,"relative_volume":1.3431255725341202,"spread_bps":5.603810591202018,"day_high":17950.0,"day_low":17670.0,"execution_condition_ko":"19100원 돌파와 18900~19100원 재시험 지지, 당일 거래량가중평균가격 상회 및 검증 가능한 거래량 확대를 함께 관찰한다. 이는 매수 승인과 다르다. / 17910~18110원에서 저점 상승과 반등 거래량을 확인하되 단순 지지 접촉만으로 매수하지 않는다.","risk_condition_ko":"17,910 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:50:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":131250.0,"market_data_asof":"2026-10-19T10:40:00+09:00","session_vwap":129108.14546560774,"relative_volume":1.5510666095616341,"spread_bps":7.6190476190476195,"day_high":133400.0,"day_low":124100.0,"execution_condition_ko":"353200.KS의 실제 거래일·휴장·조기종료 여부와 최신 정규장 체결시각을 확인한다. 제공된 2026-10-19T05:37:20.800188+09:00은 판단시계일 뿐 세션이나 시세 신선도의 증거가 아니다. 10:30은 향후 소규모 최초 매수 검토의 시작시각이지 만료시각이 아니다. 유효기한은 미설정이며 만료나 다음 거래일 이월을 추정하지 않는다. / 353200.KS의 131700원은 2026-10-16 일봉 참고 종가이고 128300원은 지연 가격이다. 어느 값도 현재가로 사용하지 않으며 가격 차이의 정규장·시간외 기준을 대사한다.","risk_condition_ko":"134,000 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:50:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":45350.0,"market_data_asof":"2026-10-19T10:40:00+09:00","session_vwap":44528.397479333245,"relative_volume":0.9413422685783635,"spread_bps":11.031439602868176,"day_high":45700.0,"day_low":43250.0,"execution_condition_ko":"거래소 달력·정규장 상태·실제 시세시각·봉 간격·호가·거래량 정의와 기존 축소 체결 여부를 먼저 확인한다. / 47,000 회복은 관찰 신호로만 사용하고 47,750 회복·재시험 지지와 당일 거래량가중평균가격 상회를 구분해 확인한다.","risk_condition_ko":"47,718 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:50:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"SELL","strategy_ko":"매도·청산 검토","last_price":191700.0,"market_data_asof":"2026-10-19T10:40:00+09:00","session_vwap":191685.1984625619,"relative_volume":1.28754393460093,"spread_bps":5.217845030002609,"day_high":193800.0,"day_low":189400.0,"execution_condition_ko":"위험 대응 조건: 185,700 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"185,700 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"투자 근거 무효화","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:50:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":136100.0,"market_data_asof":"2026-10-19T10:41:00+09:00","session_vwap":137221.38001851208,"relative_volume":0.7376448995667322,"spread_bps":7.350238882763691,"day_high":139600.0,"day_low":135300.0,"execution_condition_ko":"090430.KS의 실제 거래일·세션·거래가능 상태와 최신 체결시각을 확인한다. 제공 장중자료는 2026-10-16 기준이며 요청한 5분봉과 반환된 1분봉이 불일치한다. / 135400~135900원 저점 형성 후 135900원 회복 또는 139900원 돌파·재지지를 관찰한다. 검증된 연속 5분봉 2개, 당일 거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상을 요구한다.","risk_condition_ko":"135,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:51:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":576000.0,"market_data_asof":"2026-10-19T10:41:00+09:00","session_vwap":550753.1979591026,"relative_volume":3.7892226543374234,"spread_bps":17.346053772766695,"day_high":579000.0,"day_low":510000.0,"execution_condition_ko":"006400.KS의 판단 기준시각은 2026-10-19T06:11:43.461950+09:00이며 가격 기준은 2026-10-16 종가 530000원이다. 시계만으로 거래일·정규장 운영·호가 신선도나 진입 조건 충족을 인정하지 않는다. / 522000~526000원 재시험 뒤 526000원 회복, 당일 거래량가중평균가 상회, 반등 거래량 증가와 검증된 상대거래량 1.2 이상을 함께 관찰한다. 모두 충족해도 현재 매수 허가는 아니다.","risk_condition_ko":"522,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:51:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"105560.KS","display_name":"105560","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":159400.0,"market_data_asof":"2026-10-19T10:41:00+09:00","session_vwap":158684.6539884931,"relative_volume":1.031635076387133,"spread_bps":6.271558482282847,"day_high":160200.0,"day_low":156700.0,"execution_condition_ko":"실제 거래소 달력과 정규장 운영, 동기화된 최신 가격, 매수·매도 호가 차이와 잔량을 먼저 확인한다. / 159000–160000원, 156400–156700원, 154500–155400원의 지지 여부와 하회 종가를 감시한다.","risk_condition_ko":"162,800 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:51:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"086790.KS","display_name":"086790","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":120700.0,"market_data_asof":"2026-10-19T10:41:00+09:00","session_vwap":121216.07017803422,"relative_volume":1.1271114522706365,"spread_bps":8.281573498964804,"day_high":123800.0,"day_low":119400.0,"execution_condition_ko":"최신 거래 상태·정규장 호가·실제 5분봉·당일 거래량가중평균가격·동일 시간대 상대거래량을 먼저 확인한다. / 125600원 위 5분봉 마감과 재시험 지지, 당일 거래량가중평균가격 상회, 동일 시간대 상대거래량 1.2 이상을 함께 관찰한다. 과거 일거래량 배수로 현재 상대거래량을 대체하지 않는다.","risk_condition_ko":"121,600 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:51:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"007810.KS","display_name":"코리아써키트","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":62900.0,"market_data_asof":"2026-10-19T10:40:00+09:00","session_vwap":62240.18601932619,"relative_volume":0.8648377450259387,"spread_bps":15.885623510722795,"day_high":64000.0,"day_low":60000.0,"execution_condition_ko":"최신 거래 캘린더·정규장 체결·호가를 먼저 확인한다. 64,800원은 2026-10-16 종가이지 오늘 가격이 아니다. 간격·가격 불일치가 있는 당시 야간 자료로 현재 조건 충족을 판정하지 않는다. / 63,300원 방어 → 65,600원 회복 → 68,000원 돌파·재시험 지지를 관찰한다. 거래량가중평균가격 위 유지와 동일 경과시간 상대거래량 1.2 이상은 재평가 조건이지 자동 매수 신호가 아니다.","risk_condition_ko":"63,300 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:50:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"396300.KQ","display_name":"396300","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":8670.0,"market_data_asof":"2026-10-19T10:41:00+09:00","session_vwap":9054.839342163583,"relative_volume":4.954385622962763,"spread_bps":11.54068090017311,"day_high":9500.0,"day_low":8510.0,"execution_condition_ko":"396300.KQ의 2026-10-16 종가 9,010원·8,950원·8,830원의 충돌을 원자료로 대조한다. 평균하거나 서로 대체하지 않는다. / 실제 시각이 2026-10-16T20:00:00+09:00인 자료를 교체한다. 늦은 수집시각은 최신 시세를 뜻하지 않으며 1분봉은 완료된 5분봉 확인을 대신하지 못한다.","risk_condition_ko":"9,180 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:51:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010950.KS","display_name":"S-Oil","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":155700.0,"market_data_asof":"2026-10-19T10:41:00+09:00","session_vwap":154809.78186933804,"relative_volume":0.7500466949216469,"spread_bps":6.4246707356248,"day_high":157000.0,"day_low":151300.0,"execution_condition_ko":"제공 판단시각 2026-10-19T06:09:33.105263+09:00은 최초 검토시각 10:30 이전이다. 그러나 실제 거래일·정규장 운영·거래정지 상태와 최신 체결은 별도 확인해야 한다. 10:30은 만료시각이 아니며 확인된 주문 만료는 없다. / 가격·기술지표 기준일은 2026-10-16이다. 장중자료의 2026-10-16 20:00 표기는 시간대와 실제 체결시각을 확인하고, 요청 5분봉과 반환 1분봉의 불일치를 해소한다. 수집시각을 체결시각으로 사용하지 않는다.","risk_condition_ko":"152,700 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:51:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"018880.KS","display_name":"018880","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":3855.0,"market_data_asof":"2026-10-19T10:41:00+09:00","session_vwap":3812.156327868423,"relative_volume":0.8747099017514796,"spread_bps":12.961762799740765,"day_high":3885.0,"day_low":3710.0,"execution_condition_ko":"3727~3780원 지지, 높아지는 저점, 3780원 재회복, 완료된 5분봉 두 개의 지지, 당일 거래량가중평균가격 상회와 검증된 동시간대 상대거래량 1.2 이상을 함께 관찰한다. 가격 접촉만으로 매수하지 않는다. / 3888.1~3955원 회복은 초기 개선 신호로만 본다. 4015~4085원 저항 통과 전에는 박스권 돌파로 판단하지 않는다.","risk_condition_ko":"3,630 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:51:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":158900.0,"market_data_asof":"2026-10-19T10:40:00+09:00","session_vwap":155408.99165175715,"relative_volume":1.4350405600536744,"spread_bps":6.295247088448222,"day_high":160600.0,"day_low":148800.0,"execution_condition_ko":"최종 판단 시각은 2026-10-19T06:03:18.214745+09:00이다. 토론의 이전 시각 대신 이를 사용한다. 거래일·실제 정규장·시세 시각·호가 유동성·거래 제한은 별도 확인한다. 2026-10-16 종가는 현재 실행가격이 아니다. / 10:30은 검증된 정규장에서 최초 진입 검토를 시작할 수 있는 시각이지 만료시각이 아니다. 확인된 주문 유효기간이 없으므로 만료나 다음 거래일 자동 연장을 추정하지 않는다.","risk_condition_ko":"149,000 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"지금 실행 검토 가능","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:50:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"131290.KQ","display_name":"티에스이","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":280000.0,"market_data_asof":"2026-10-19T10:41:00+09:00","session_vwap":279790.1357383804,"relative_volume":1.6628458917896887,"spread_bps":17.84121320249777,"day_high":296000.0,"day_low":267500.0,"execution_condition_ko":"위험 대응 조건: 263,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"263,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:51:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"036930.KQ","display_name":"주성엔지니어링","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":203000.0,"market_data_asof":"2026-10-19T10:41:00+09:00","session_vwap":203654.40809141687,"relative_volume":1.4691778240168116,"spread_bps":24.66091245376079,"day_high":210000.0,"day_low":199200.0,"execution_condition_ko":"위험 대응 조건: 199,100 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"199,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:51:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"051900.KS","display_name":"051900","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":270500.0,"market_data_asof":"2026-10-19T10:40:00+09:00","session_vwap":273663.95277048927,"relative_volume":0.8386118950470003,"spread_bps":18.467220683287163,"day_high":278000.0,"day_low":270000.0,"execution_condition_ko":"위험 대응 조건: 268,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"268,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:50:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"373220.KS","display_name":"LG에너지솔루션","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":425000.0,"market_data_asof":"2026-10-19T10:41:00+09:00","session_vwap":414633.77304532763,"relative_volume":2.609373956895105,"spread_bps":11.771630370806356,"day_high":426000.0,"day_low":394000.0,"execution_condition_ko":"위험 대응 조건: 395,500 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"395,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"지금 실행 검토 가능","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:51:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"018260.KS","display_name":"삼성SDS","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":200500.0,"market_data_asof":"2026-10-19T10:41:00+09:00","session_vwap":196374.45050780658,"relative_volume":0.9588968089166863,"spread_bps":24.968789013732835,"day_high":201500.0,"day_low":192800.0,"execution_condition_ko":"위험 대응 조건: 194,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"194,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:51:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"011790.KS","display_name":"011790","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":95200.0,"market_data_asof":"2026-10-19T10:40:00+09:00","session_vwap":93722.00986801043,"relative_volume":2.3274413729704344,"spread_bps":10.509721492380452,"day_high":96900.0,"day_low":88600.0,"execution_condition_ko":"위험 대응 조건: 90,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"90,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:50:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"452190.KQ","display_name":"452190","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":5120.0,"market_data_asof":"2026-10-19T10:41:00+09:00","session_vwap":5069.3594723834085,"relative_volume":0.2074451719521157,"spread_bps":39.138943248532286,"day_high":5200.0,"day_low":4830.0,"execution_condition_ko":"위험 대응 조건: 4,790 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"4,790 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-19T10:51:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-19T10:47:30.266448+09:00",
  "as_of": "2026-10-19T10:40:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
