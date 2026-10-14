# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-14T02:11:09.920229+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261014T110630_local-scheduler-kr-overlay_only",
  "producer_finished_at": "2026-10-14T11:08:41.434906+09:00",
  "analysis_run_id": "20261014T102112_local-scheduler-kr-full-finalization",
  "analysis_completed_at": "2026-10-14T09:03:19.265122+09:00",
  "analysis_trade_date_oldest": "2026-10-13",
  "analysis_trade_date_latest": "2026-10-13",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-14T11:07:00+09:00",
  "market_data_latest_at": "2026-10-14T11:07:00+09:00",
  "market_data_status": "FRESH"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-14T11:08:37.839681+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-14T11:08:37.839681+09:00",
    "run_started_at": "2026-10-14T11:06:30.982756+09:00",
    "run_finished_at": "2026-10-14T11:08:41.434906+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 9390710,
    "total_unrealized_pnl_krw": -5553526,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 10367362
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1476000,
      "market_value_krw": 2952000,
      "unrealized_pnl_krw": -2483000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 238000,
      "market_value_krw": 2380000,
      "unrealized_pnl_krw": -943851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 287000,
      "market_value_krw": 1435000,
      "unrealized_pnl_krw": -639643
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 178600,
      "market_value_krw": 714400,
      "unrealized_pnl_krw": -260600
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 547000,
      "market_value_krw": 547000,
      "unrealized_pnl_krw": -606000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 19245,
      "market_value_krw": 346410,
      "unrealized_pnl_krw": -221905
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 77800,
      "market_value_krw": 233400,
      "unrealized_pnl_krw": -66600
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 223000,
      "market_value_krw": 223000,
      "unrealized_pnl_krw": -151167
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 181800,
      "market_value_krw": 181800,
      "unrealized_pnl_krw": -100534
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 146900,
      "market_value_krw": 146900,
      "unrealized_pnl_krw": -25400
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 51500,
      "market_value_krw": 103000,
      "unrealized_pnl_krw": -15200
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 69600,
      "market_value_krw": 69600,
      "unrealized_pnl_krw": -43331
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 58200,
      "market_value_krw": 58200,
      "unrealized_pnl_krw": 3700
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":58300.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":59241.92311392018,"relative_volume":1.338507928194058,"spread_bps":17.167381974248926,"day_high":61600.0,"day_low":57400.0,"execution_condition_ko":"위험 대응 조건: 57,400 이하 하락, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"57,400 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":51500.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":52301.15010503645,"relative_volume":1.1934592108201678,"spread_bps":19.398642095053347,"day_high":54100.0,"day_low":50900.0,"execution_condition_ko":"위험 대응 조건: 52,950 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"52,950 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":1476000.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":1469800.4885173247,"relative_volume":1.4154561179211789,"spread_bps":6.7727734507280735,"day_high":1497000.0,"day_low":1451000.0,"execution_condition_ko":"000660.KS의 실제 거래일·정상 세션·거래 제한·최신 체결시각·호가·거래량·유효한 세션 거래량가중평균가격을 확인한다. 전일 20:00 시세, 거래량 0 및 비정상 평균가격은 실행 근거에서 제외한다. / 기준시각 2026-10-14T06:09:26.976617+09:00은 향후 소액진입 검토 시각 10:30보다 이르다. 10:30은 최초 검토 가능 시각이지 만료가 아니며 현재 활성 매수계획은 없다. 이 시계만으로 거래일·세션·조건 충족을 인정하거나 날짜를 이월하지 않는다.","risk_condition_ko":"1,425,000 이하 하락, 종가 확인 후 (손절에 거래량 증가를 요구하지 않는다.) 리스크 축소","decision_state_ko":"지금 실행 검토 가능","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":287500.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":278431.98633829365,"relative_volume":2.852330248752132,"spread_bps":34.84320557491289,"day_high":287500.0,"day_low":266500.0,"execution_condition_ko":"실제 거래일·정규장·거래정지 여부와 최신 가격·호가·체결량을 먼저 검증한다. 전일 봉으로 표시된 장중 자료, 거래량 0, 비정상 거래량가중평균가격은 실행 판단에서 제외한다. / 279000원 방어, 저점 상승, 재하락 시 매도 압력 둔화와 321500~331500원 회복·재시험은 관찰 강화 조건이지 자동 매수 조건이 아니다.","risk_condition_ko":"279,000 이하 하락, 종가 확인 후 (위험축소에 거래량 증가를 필수로 요구하지 않는다.) 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":548000.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":549961.4629389686,"relative_volume":1.7910041052405399,"spread_bps":18.264840182648403,"day_high":564000.0,"day_low":537000.0,"execution_condition_ko":"267260.KS의 실제 거래일·정규장 상태, 최신 호가·체결·스프레드·거래량 및 정상 세션 거래량가중평균가격 확보가 실행 검토의 선행 조건이다. / 267260.KS의 531,000 재시험에서 저점 상승과 매도 압력 둔화를 확인한다. 단순 접촉이나 아래꼬리만으로 지지를 확정하지 않는다.","risk_condition_ko":"531,000 이하 하락, 2개 봉 확인 후 (손절에 거래량 하한을 요구하지 않는다.) 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":19270.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":18803.379854647435,"relative_volume":2.2795275336809975,"spread_bps":5.190760446405398,"day_high":19280.0,"day_low":17780.0,"execution_condition_ko":"010140.KS의 실제 거래 가능 상태, 최신 정규장 호가·체결·정상 거래량가중평균가격과 계좌 노출 확보. / 18,440원 위 연속 5분봉 두 개 마감, 재시험 지지, 동시간대 상대거래량 1.2배 이상은 재평가 신호다. 전일 일평균 대비 1.72배로 대체하지 않는다.","risk_condition_ko":"17,910 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"지금 실행 검토 가능","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":78100.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":78206.70339004685,"relative_volume":1.3284676594803229,"spread_bps":12.795905310300704,"day_high":80500.0,"day_low":76100.0,"execution_condition_ko":"058470.KQ 판단 시각은 2026-10-14T06:33:06.804616+09:00, 일봉 가격 기준일은 2026-10-13이다. 실제 거래일·정상 세션·휴장 또는 단축장 여부와 최신 시세·호가·거래량의 시각을 별도로 확인한다. / 058470.KQ의 77,600~78,100원 시험 후 회복, 시험 때 매도량 감소와 회복 때 참여 증가를 관찰한다. 80,700원 돌파를 이 지지 회복형의 동시 필수조건으로 삼지 않는다.","risk_condition_ko":"77,600 이하 하락, 종가 확인 후 (거래량 증가를 필수조건으로 두지 않는다.) 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":147300.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":147184.95906669414,"relative_volume":1.504573738564378,"spread_bps":20.387359836901123,"day_high":152000.0,"day_low":141100.0,"execution_condition_ko":"판단시각은 2026-10-14T06:59:31.190292+09:00이며 제공된 세계협정시 시각과 같은 순간이다. 제안된 10:30 최초 관찰시각 이전이지만 실제 거래일·정규장 운영·거래정지·시세 신선도는 미확인이다. 10:30은 만료시각이 아니며 확인된 주문 만료시각도 없어 다음 거래일로 자동 연장하지 않는다. / 142,400~144,100원 안정, 144,100원 회복·두 개 5분봉 재시험, 정상 거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상을 관찰한다. 기술 조건 충족만으로 현재의 손익비 미달이 해소되지는 않는다.","risk_condition_ko":"151,400 이상 도달, 장중 확인 시 (매도에 최소 상대거래량 조건 없음) 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":69500.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":69419.4443536477,"relative_volume":1.2691860867214577,"spread_bps":14.378145219266715,"day_high":70400.0,"day_low":68300.0,"execution_condition_ko":"structured price range conflict","risk_condition_ko":"67,300 이하 하락, 종가 확인 후 (추가 위험 축소에 거래량 증가를 필수로 요구하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"구조화 가격 구간 재확인 필요","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-14T11:07:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":["structured_price_range_conflict"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":237750.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":237535.01811080438,"relative_volume":1.1986298234173163,"spread_bps":21.03049421661409,"day_high":241500.0,"day_low":233000.0,"execution_condition_ko":"실제 KRX 거래일·정규장·거래정지 상태와 최신 호가·체결·거래량을 확인한다. 이전 야간 가격은 현재 매매 조건 충족의 증거가 아니다. / 228,000~230,100원 방어, 237,900원 초기 회복, 243,000원 기존 지지 회복, 244,000원 돌파·재시험을 관찰한다. 단순 가격 접촉은 매수 신호가 아니다.","risk_condition_ko":"243,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":178500.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":178652.84072204542,"relative_volume":1.5509882000061703,"spread_bps":11.198208286674133,"day_high":182200.0,"day_low":175600.0,"execution_condition_ko":"010120.KS의 173100원 유지, 183740원 회복·재시험 지지, 상대강도지수 40 회복과 이동평균 수렴·확산 지표의 음의 막대 축소를 관찰한다. 현재 매수 조건 충족으로 간주하지 않는다. / 188000원 재탈환과 192100~195500원 저항 통과를 확인한다. 202540원은 2026-10-13 거래량가중이동평균 참고값이며 고정 목표가가 아니다. 회복 후에도 진입가격 상승에 따른 손익비 악화를 다시 점검한다.","risk_condition_ko":"188,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":223000.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":225489.91906925818,"relative_volume":1.3815436724778551,"spread_bps":22.44668911335578,"day_high":231500.0,"day_low":220000.0,"execution_condition_ko":"제공된 결정 시각은 2026-10-14T06:35:02.062028+09:00이다. 이 시각만으로 실제 거래일·정규장 운영·거래정지·시장경보·변동성 완화장치 상태나 호가 신선도를 확정하지 않는다. 거래 가능 상태와 시세 타임스탬프를 먼저 확인한다. / 전일 20:00 야간 봉의 거래량 0과 비정상 거래량가중평균가격 986,427,009.44원은 진입 판단에서 제외한다. 유효한 당일 정규장 체결·호가·세션 거래량가중평균가격을 새로 확인해야 한다.","risk_condition_ko":"227,180 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":181900.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":181281.7390855948,"relative_volume":1.0544040843323164,"spread_bps":5.496015388843088,"day_high":183200.0,"day_low":178000.0,"execution_condition_ko":"035420.KS 결정시각은 2026-10-14T06:33:09.469024+09:00, 일봉 기준일은 2026-10-13이다. 실제 거래일·휴장·조기종료 여부, 정규장 상태, 현재 체결시각과 호가 유동성은 미검증이다. 이 시계만으로 당일 진입·매도 신호 발생을 선언하지 않는다. / 035420.KS의 179,500~180,500원 회복·재시험 유지, 저점 하락 중단, 상대강도지수 30 재돌파와 이동평균 수렴·확산 히스토그램 음의 폭 축소를 관찰한다. 전일 거래량의 20일 평균 대비 약 1.18배를 당일 동일 경과시간 상대거래량으로 대체하지 않는다.","risk_condition_ko":"180,500 이하 하락, 2개 봉 확인 후 (위험 축소에는 최소 상대거래량 조건을 적용하지 않음) 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010950.KS","display_name":"S-Oil","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":159200.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":159412.01890221174,"relative_volume":1.1605589599719388,"spread_bps":6.279434850863423,"day_high":166000.0,"day_low":156800.0,"execution_condition_ko":"010950.KS의 판단 기준은 2026-10-14T07:55:53.688721+09:00이고 일봉 가격 기준일은 2026-10-13이다. 실제 거래 캘린더·정규장 상태·거래정지 여부·최신 호가와 거래량은 별도 확인한다. / 010950.KS의 152700~154300 재시험 후 저점 상승, 지지 회복, 유효 세션 거래량가중평균가격 상회, 검증된 동시각 상대거래량 1.2 이상 및 비용 후 손익비 2 이상을 함께 확인한다.","risk_condition_ko":"152,700 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"018260.KS","display_name":"삼성SDS","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":204000.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":201474.6308858739,"relative_volume":0.9290271525270297,"spread_bps":24.539877300613497,"day_high":204500.0,"day_low":196000.0,"execution_condition_ko":"018260.KS의 실제 거래일·정규장 상태, 시각이 표시된 최신 호가, 매수·매도 호가 차이와 유효한 세션 거래량가중평균가격을 확보한다. / 194000~195500원 회복 후 높아진 저점의 재시험, 모멘텀 개선과 동일 시각 기준 상대거래량 1.2 이상을 관찰한다. 1.2는 제안 기준이지 관측값이 아니다.","risk_condition_ko":"193,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"018880.KS","display_name":"018880","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":3985.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":3970.109703254198,"relative_volume":2.414083614829706,"spread_bps":12.539184952978058,"day_high":4060.0,"day_low":3785.0,"execution_condition_ko":"3735원 방어 후 3740원 회복 또는 3675원 방어 후 3680원 회복을 최신 5분봉으로 확인한다. 회복 자체가 매수 허가는 아니다. / 깊은 눌림 이후에는 3735~3740원과 3790~3805원이 실제 저항으로 바뀌는지 확인하고 가장 가까운 유효 저항으로 손익비를 다시 계산한다.","risk_condition_ko":"3,880.73 이상 도달, 종가 확인 후 (위험 축소에 매수용 거래량 조건을 요구하지 않음) 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"095340.KQ","display_name":"ISC","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":177400.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":178251.82228960432,"relative_volume":1.4297958024901525,"spread_bps":5.635390250774866,"day_high":184500.0,"day_low":175000.0,"execution_condition_ko":"095340.KQ의 판단 기준 시각은 2026-10-14T08:35:51.466910+09:00이며 일봉 가격 기준일은 2026-10-13이다. 10:30은 제안된 최소 관찰시각이지 만료시각이 아니다. 실제 거래일·정규장 운영·신선한 체결·정상 거래량가중평균가격과 동시간대 비교 거래량은 별도 확인한다. 검증된 만료시각이 없어 다음 거래일로 주문을 자동 이월하지 않는다. / 095340.KQ의 179,300원·174,600원 지지 반응과 172,900원 종가 유지 여부를 관찰한다. 지지 접촉이나 장중 반등만으로 바닥을 확정하지 않는다.","risk_condition_ko":"179,300 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"105560.KS","display_name":"105560","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":160300.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":161618.10675385396,"relative_volume":1.6694955351796743,"spread_bps":6.236357966947303,"day_high":164700.0,"day_low":159500.0,"execution_condition_ko":"105560.KS의 실제 거래일·정규장 여부·거래정지·시장경보·최신 봉 시각·호가 간격·거래량과 계좌 노출을 확인한다. / 105560.KS의 162,800원 회복·재시험 지지, 두 개 5분봉 확인, 정상 당일 거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상을 감시한다. 충족만으로 자동매수하지 않는다.","risk_condition_ko":"160,300 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"180640.KS","display_name":"180640","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":126900.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":128075.53616128814,"relative_volume":0.7745218809947544,"spread_bps":7.889546351084812,"day_high":131500.0,"day_low":126600.0,"execution_condition_ko":"129000~129600 회복·유지와 저점 상승, 이어지는 132200 회복을 확인한다. 133500의 가까운 저항을 무시하지 않는다. / 135900 위 정규장 종가·재시험 지지, 상대강도지수 50 이상, 이동평균 수렴·확산 지표의 히스토그램 개선과 거래량 증가를 확인한다. 기초체력과 손익비 재심사는 별도다.","risk_condition_ko":"129,562 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"000810.KS","display_name":"000810","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":589000.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":596317.5195611116,"relative_volume":1.2625865534426877,"spread_bps":16.963528413910094,"day_high":613000.0,"day_low":585000.0,"execution_condition_ko":"000810.KS의 실제 거래소 일정·세션·거래정지·시장경보와 최신 정규장 가격·호가·체결량을 먼저 확인한다. / 607,000~612,000원 공방과 595,000원 방어를 관찰한다. 584,000~587,000원과 571,000원은 과거 가격 참고 수준이며 자동 매수선이나 확정 하락 목표가 아니다.","risk_condition_ko":"595,000 이하 하락, 종가 확인 후 (위험 축소에는 거래량 증가를 요구하지 않음) 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":181400.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":181476.98063315262,"relative_volume":0.9815024289818249,"spread_bps":5.5111600992008825,"day_high":183400.0,"day_low":179900.0,"execution_condition_ko":"033780.KS의 거래소 일정·거래정지·시장경보, 시각이 확인되는 실제 체결·호가, 정상적인 당일 거래량가중평균가격과 동시간대 비교 거래량을 확보한다. / 033780.KS의 177700~177900원 지지 후 회복과 동시간대 상대거래량 1.2 이상을 관찰한다. 첫 현실적 저항까지 비용 후 보상과 청산 시나리오가 정당화되지 않으면 시세가 정상이어도 매수 대기를 유지한다.","risk_condition_ko":"177,700 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":163300.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":162742.1936151037,"relative_volume":1.773783405633453,"spread_bps":6.125574272588055,"day_high":165000.0,"day_low":159800.0,"execution_condition_ko":"096770.KS의 최신 정규장 호가, 5분봉, 거래량가중평균가격, 호가차이·잔량, 같은 경과시간 기준 상대거래량 및 거래 상태를 확보한다. / 096770.KS의 150000–150800원과 152800–153143원 구간에서 매도 거래량 감소, 상단 위 두 차례 5분봉 마감과 재시험 성공을 관찰한다. 현재 목표·손절 구조로는 자동 매수하지 않는다.","risk_condition_ko":"150,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"지금 실행 검토 가능","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"062040.KS","display_name":"062040","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":216000.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":214857.9437347105,"relative_volume":1.2689929184227997,"spread_bps":23.228803716608596,"day_high":220000.0,"day_low":208500.0,"execution_condition_ko":"보유수량·순자산·현금·상관 업종 노출과 최신 실행 가능 가격을 확인한다. 실제 손실·집중도 한도 위반이 드러나면 지지선 이탈을 기다리지 않고 초과분을 감축한다. / 199800~205500원에서 지지 안정과 상승하는 5분봉 저점을 관찰한다. 2026-10-13의 아래꼬리는 과거 매수 반응이지 현재 지지 확인이 아니다.","risk_condition_ko":"199,800 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"지금 실행 검토 가능","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"373220.KS","display_name":"LG에너지솔루션","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":423000.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":419887.76189416694,"relative_volume":2.488344486930423,"spread_bps":11.813349084465445,"day_high":427000.0,"day_low":409000.0,"execution_condition_ko":"373220.KS의 실제 거래 가능 세션·휴장·조기종료·거래정지·변동성완화장치·시장경보와 최신 체결시각·호가부터 확인한다. 전일 야간 지연 자료, 거래량 0, 가격 범위와 맞지 않는 거래량가중평균가격은 진입 확인에서 제외한다. / 373220.KS의 385,400~386,100원 재시험과 386,100원 회복을 우선 관찰한다. 하락 거래량 감소·반등 체결 증가·실제 손익비 확인이 필요하며 단순 접촉은 매수 신호가 아니다.","risk_condition_ko":"385,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"지금 실행 검토 가능","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":591000.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":587263.4489633519,"relative_volume":3.7902496454452317,"spread_bps":16.93480101608806,"day_high":600000.0,"day_low":559000.0,"execution_condition_ko":"판단 기준은 2026-10-14T07:45:03.028649+09:00이고 가격 기준은 2026-10-13 일봉이다. 이 시각만으로 실제 거래 가능 세션이나 최신 가격을 확정하지 않는다. / 546000~550000 접근 후 550000 회복·재시험 지지, 정상 당일 거래량가중평균가격 상회, 같은 시간대 상대거래량 1.2 이상을 확인한다. 이 조건만으로 매수하지 않으며 비용 후 보상·위험 비율도 충족해야 한다.","risk_condition_ko":"546,000 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"지금 실행 검토 가능","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"222800.KQ","display_name":"심텍","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":143700.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":144767.71750577874,"relative_volume":1.647440320165185,"spread_bps":20.8695652173913,"day_high":151600.0,"day_low":139500.0,"execution_condition_ko":"위험 대응 조건: 154,900 이상 도달, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"154,900 이상 도달, 2개 봉 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"086790.KS","display_name":"086790","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":121900.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":122312.00279799114,"relative_volume":1.8454322046026457,"spread_bps":8.206811653672547,"day_high":124800.0,"day_low":120600.0,"execution_condition_ko":"위험 대응 조건: 126,900 이상 도달, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"126,900 이상 도달, 2개 봉 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"093370.KS","display_name":"093370","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":14370.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":14499.543305428188,"relative_volume":0.8447494089826977,"spread_bps":6.961364427427776,"day_high":15000.0,"day_low":13810.0,"execution_condition_ko":"위험 대응 조건: 14,240 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"14,240 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"475150.KS","display_name":"475150","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":44200.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":44187.927294345325,"relative_volume":0.6649238100952698,"spread_bps":11.305822498586771,"day_high":45900.0,"day_low":43300.0,"execution_condition_ko":"위험 대응 조건: 42,150 이하 하락, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"42,150 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010580.KS","display_name":"010580","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":2085.0,"market_data_asof":"2026-10-14T11:07:00+09:00","session_vwap":2148.7129231899767,"relative_volume":0.8453284804643451,"spread_bps":24.009603841536613,"day_high":2265.0,"day_low":2025.0,"execution_condition_ko":"위험 대응 조건: 1,994 이하 하락, 2개 봉 확인 후 (거래량 급증을 필수 조건으로 요구하지 않음) 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"1,994 이하 하락, 2개 봉 확인 후 (거래량 급증을 필수 조건으로 요구하지 않음) 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-14T11:37:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-14T10:40:37.794671+09:00",
  "as_of": "2026-10-13T13:24:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
