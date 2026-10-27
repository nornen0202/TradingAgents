# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-27T02:24:07.426333+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261027T112058_local-freshness-kr-overlay",
  "producer_finished_at": "2026-10-27T11:21:45.412729+09:00",
  "analysis_run_id": "20261027T050051_local-scheduler-kr-full",
  "analysis_completed_at": "2026-10-27T08:02:30.648772+09:00",
  "analysis_trade_date_oldest": "2026-10-26",
  "analysis_trade_date_latest": "2026-10-26",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-27T11:21:00+09:00",
  "market_data_latest_at": "2026-10-27T11:21:00+09:00",
  "market_data_status": "FRESH"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-27T11:02:00.183386+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-27T11:02:00.183386+09:00",
    "run_started_at": "2026-10-27T11:01:24.665938+09:00",
    "run_finished_at": "2026-10-27T11:02:08.975421+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 8650020,
    "total_unrealized_pnl_krw": -6294216,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 9626672
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1360000,
      "market_value_krw": 2720000,
      "unrealized_pnl_krw": -2715000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 223250,
      "market_value_krw": 2232500,
      "unrealized_pnl_krw": -1091351
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 280500,
      "market_value_krw": 1402500,
      "unrealized_pnl_krw": -672143
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 161700,
      "market_value_krw": 646800,
      "unrealized_pnl_krw": -328200
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 466000,
      "market_value_krw": 466000,
      "unrealized_pnl_krw": -687000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 16740,
      "market_value_krw": 301320,
      "unrealized_pnl_krw": -266995
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 193600,
      "market_value_krw": 193600,
      "unrealized_pnl_krw": -180567
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 62400,
      "market_value_krw": 187200,
      "unrealized_pnl_krw": -112800
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 176100,
      "market_value_krw": 176100,
      "unrealized_pnl_krw": -106234
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 129600,
      "market_value_krw": 129600,
      "unrealized_pnl_krw": -42700
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 43600,
      "market_value_krw": 87200,
      "unrealized_pnl_krw": -31000
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 60400,
      "market_value_krw": 60400,
      "unrealized_pnl_krw": -52531
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 46800,
      "market_value_krw": 46800,
      "unrealized_pnl_krw": -7700
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":462500.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":465848.6666352379,"relative_volume":1.0425775456943271,"spread_bps":10.804970286331713,"day_high":472500.0,"day_low":456000.0,"execution_condition_ko":"267260.KS의 실제 거래일·정규장 운영·거래정지와 실적 발표시각·결과를 먼저 확인한다. 날짜와 런타임만으로 거래 가능 여부나 발표 완료를 판단하지 않는다. / 267260.KS의 전일 종가·지연 요약 447000원, 마지막 제공 봉 443500원, 별도 시간외 보도 441500원을 구분한다. 어느 것도 당일 정규장 443000원 이탈을 입증하지 않는다.","risk_condition_ko":"443,000 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":222500.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":223525.51552942573,"relative_volume":1.0099155923604408,"spread_bps":22.44668911335578,"day_high":225500.0,"day_low":221500.0,"execution_condition_ko":"2026-10-27T05:19:17.009328+09:00은 판단시각이며 실제 거래일·정규장·최신 호가·체결 가능성을 확정하지 않는다. 거래소 일정과 자료 신선도를 별도로 확인한다. / 216000원 돌파·재시험 지지, 당일 거래량가중평균가격 상회, 비교 가능한 동시간대 누적 상대거래량 1.2 이상을 감시한다. 충족만으로 현재 매수 차단을 해제하지 않는다.","risk_condition_ko":"203,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":277000.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":282150.3193309459,"relative_volume":0.802589001959418,"spread_bps":18.066847335140018,"day_high":290000.0,"day_low":276000.0,"execution_condition_ko":"실제 거래소 일정·세션·거래정지·호가 신선도와 기업행사 조정 기준을 확인한다. / 원공시의 공개시각·회계기간·표시통화·단위·주당 기준과 예탁증서 환산 적용 여부를 확인하고 현금흐름표 분류 불일치를 해소한다. 잠정 성장 수치와 부정적 현금전환 수치를 동일하게 검증한다.","risk_condition_ko":"275,000 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":192700.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":194106.05200667432,"relative_volume":1.417492161561714,"spread_bps":5.190760446405398,"day_high":196000.0,"day_low":191000.0,"execution_condition_ko":"182000~182100원 방어, 190500~192200원 회복 시도, 199900~205300원 저항에서의 지속성을 관찰한다. 중립적 분석가가 지적했듯 감시 근거를 독립적인 매수 근거로 중복 계산하지 않는다. / 공격적 분석가의 이동평균 수렴확산 지표 개선과 상대강도지수 괴리 후보는 관찰 대상으로만 둔다. 거래량이 20일 평균의 약 0.723배라는 사실은 매수 유입이나 매도 종료를 입증하지 않는다.","risk_condition_ko":"182,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":175550.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":175582.79449087108,"relative_volume":1.1017491831976292,"spread_bps":5.696382796923953,"day_high":178700.0,"day_low":174400.0,"execution_condition_ko":"170900~171900원 지지 후보의 유지·이탈·회복을 최신 정규장 자료로 구분한다. 현재 지지 붕괴를 기정사실화하지 않는다. / 175400~176700원과 182900~185000원은 단순 도달이 아니라 저항 거부·돌파 유지 실패 여부를 확인해 추가 감축을 판단한다.","risk_condition_ko":"170,900 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":128700.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":131063.46491131673,"relative_volume":1.6471129607136896,"spread_bps":7.766990291262136,"day_high":134600.0,"day_low":125400.0,"execution_condition_ko":"353200.KS의 실제 거래일·정규장·거래정지 여부와 최신 호가·봉 시각·간격을 먼저 검증 / 116000~116100 저점대와 118672 중기 평균 재시험·회복 관찰; 지지 유지만으로 추가 매수하지 않음","risk_condition_ko":"116,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":59700.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":59755.48394468361,"relative_volume":0.8477934080284696,"spread_bps":16.736401673640167,"day_high":60500.0,"day_low":58600.0,"execution_condition_ko":"034020.KS 판단시계는 2026-10-27T10:34:57.503715+09:00이다. 마지막 가격 관측 2026-10-27T10:16:52+09:00은 약 18분 전 자료이며, 당시 표시 지연 52초를 현재 신선도로 사용하지 않는다. / 034020.KS 현재 정규장 여부, 휴장·조기종료·거래정지·변동성 완화장치 상태와 신선한 호가·완료봉·거래량가중평균가격을 확인한다. 시계만으로 세션이나 진입 조건 충족을 확정하지 않는다.","risk_condition_ko":"59,500 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":1358000.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":1363477.9844731342,"relative_volume":1.1964543963616825,"spread_bps":7.366482504604051,"day_high":1381000.0,"day_low":1345000.0,"execution_condition_ko":"새 정규장 자료의 거래일·시각·봉 간격·호가 신선도와 당일 거래량가중평균가격을 검증한다. / 1329000원과 1341000원 회복·재시험 지지, 당일 거래량가중평균가격 상회, 동일 경과시간 상대거래량 1.2 이상을 관찰한다. 일간 거래량의 20일 평균 대비 비율로 장중 상대거래량을 대체하지 않는다.","risk_condition_ko":"1,267,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":160800.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":161225.9406789407,"relative_volume":0.9601889937920582,"spread_bps":6.2208398133748055,"day_high":162500.0,"day_low":157300.0,"execution_condition_ko":"010120.KS의 실제 정규장 일정·거래상태·최신 호가 시각과 152500원/152900원 종가 불일치를 확인한다. / 원공시 공개시점·통화·단위·기간·주식 기준 및 주식예탁증서 해당 여부를 검증한다. 동일 공급자 기반 자료를 독립 검증으로 세지 않는다.","risk_condition_ko":"150,000 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":62100.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":62405.012348655895,"relative_volume":0.7610110071238854,"spread_bps":16.090104585679807,"day_high":63500.0,"day_low":60800.0,"execution_condition_ko":"62300~62800원 지지와 62800원 재회복, 63500원 돌파·재지지, 64200원 회복을 단계적으로 관찰한다. 중립 분석가의 제안대로 약세 확신을 먼저 재평가할 수 있으나 이 신호만으로 매수를 활성화하지 않는다. / 상대거래량 0.89배의 산식과 시간대 비교 기준을 검증한다. 1.2배는 향후 심사 기준이며 현재 충족 사실이 아니다.","risk_condition_ko":"62,300 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":16610.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":16613.306567532698,"relative_volume":1.3915964212285168,"spread_bps":6.018657839301836,"day_high":16770.0,"day_low":16410.0,"execution_condition_ko":"010140.KS의 최신 정규장 가격·실제 거래일·거래 가능 상태와 계좌 보유·상관 노출을 확인한다. 지연 시세로 당일 진입·지지 이탈 조건 충족을 판정하지 않는다. / 16090원 방어와 높아지는 저점, 16450원 회복·재시험을 확인한다. 상대강도지수 28.57과 평균 대비 거래량 78.7%는 바닥·매집·매도 소진의 증거가 아니다.","risk_condition_ko":"16,090 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":46550.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":46865.583906772576,"relative_volume":1.1954448910632722,"spread_bps":10.746910263299302,"day_high":47550.0,"day_low":46100.0,"execution_condition_ko":"403870.KQ 거래일·거래정지·새 공시·최신 정규장 가격과 거래량을 확인한다. 과거 거래량 0 관측을 현재 거래로 해석하지 않는다. / 47100원 회복·재지지, 당일 거래량가중평균가격 상회와 동시간대 상대거래량 1.2배 이상을 관찰한다. 이는 재검토 조건이지 매수 주문이 아니다.","risk_condition_ko":"47,042.75 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":43600.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":43642.993302817114,"relative_volume":1.1596556689406794,"spread_bps":22.93577981651376,"day_high":44350.0,"day_low":41400.0,"execution_condition_ko":"거래 달력과 실제 세션을 확인하고 시간대가 명확한 신선한 체결·호가·세션 거래량가중평균가격·동시간대 거래량을 확보한다. / 40300원과 39275원의 방어, 41700~42350원 초기 회복 구간의 회복·유지를 관찰한다. 접촉만으로 매수하지 않는다.","risk_condition_ko":"42,061.5 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":509000.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":501383.90578362247,"relative_volume":1.2886699115133053,"spread_bps":19.62708537782139,"day_high":519000.0,"day_low":484500.0,"execution_condition_ko":"471500~478555원 재시험 이후 저점 상승과 490500원 회복을 관찰한다. 지지 접촉이나 거래량 감소만으로 매수하지 않는다. / 최소 재무 검증 후 504000원 돌파·재시험, 정규장 5분봉 2개 지지, 당일 거래량가중평균가격 상회와 동일시각 상대거래량 1.2배 이상이면 시험매수를 별도 재평가한다. 현재 조건부 매수는 아니다.","risk_condition_ko":"510,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"064400.KS","display_name":"LG CNS","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":76000.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":75001.12765356617,"relative_volume":1.9750519243007831,"spread_bps":13.166556945358789,"day_high":76200.0,"day_low":73200.0,"execution_condition_ko":"기준 판단시각은 2026-10-27T06:49:52.812385+09:00이다. 이 시각만으로 거래일·정규장 상태·휴장 여부·호가 신선도·주문 만료를 확정하지 않는다. 10:30은 최초 시범 검토 가능 시각이지 만료가 아니며 주문을 다음 거래일로 자동 이월하지 않는다. / 064400.KS의 신선한 호가·실제 5분봉·세션 거래량가중평균가격을 확보하고 요약 가격과 차트 가격·봉 간격 불일치를 해소한다. 일봉 거래량가중이동평균을 장중 기준으로 대체하지 않는다.","risk_condition_ko":"71,200 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"018880.KS","display_name":"018880","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":3705.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":3705.546747612729,"relative_volume":0.45740153556606167,"spread_bps":13.50438892640108,"day_high":3740.0,"day_low":3635.0,"execution_condition_ko":"판단 기준시각은 2026-10-27T07:15:59.255623+09:00이다. 이 시각만으로 거래일·정규장·단축장 여부나 호가 신선도를 확정하지 않는다. 현재 확인 가능한 신규 host 도구 결과는 없다. / 일봉 기준은 2026-10-26이다. 장중자료 기준시각은 2026-10-26 20:00:00으로 제시됐으나 요약 3,605원과 마지막 봉 3,610원이 다르다. 시간대·봉 주기·최신 체결·호가를 재확인하며 제공 상대거래량 0을 당일 거래 부진으로 해석하지 않는다.","risk_condition_ko":"3,540 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"411080.KQ","display_name":"411080","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":7460.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":7260.614435010856,"relative_volume":3.8998242091121833,"spread_bps":13.395847287340924,"day_high":7640.0,"day_low":6670.0,"execution_condition_ko":"실제 거래일·정규장 상태·시장경보와 신선한 가격·호가·거래량·장중 거래량가중평균가격을 우선 확인한다. / 6400원 또는 약 6560원 재지지와 회복 거래량을 관찰한다. 이것만으로 매수하지 않는다.","risk_condition_ko":"6,400 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":137800.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":138472.4076358847,"relative_volume":0.6248617024792216,"spread_bps":7.259528130671506,"day_high":140200.0,"day_low":136300.0,"execution_condition_ko":"135300–136200 지지 여부를 신선한 정규장 자료로 확인한다. 실패는 추가 위험축소 신호이며 저가매수 신호가 아니다. / 142200 상회 종가, 갱신된 비교 기준 대비 상대거래량 1.2 이상, 성공적인 재시험을 관찰한다. 충족해도 재무 근거와 비용 반영 보상을 재평가할 뿐 자동매수하지 않는다.","risk_condition_ko":"140,010 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"028050.KS","display_name":"028050","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":62300.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":62303.57799597778,"relative_volume":2.7015035571267823,"spread_bps":16.038492381716118,"day_high":63900.0,"day_low":60100.0,"execution_condition_ko":"57700~58000원에서 조정 거래량 감소 후 저점 상승·가격 회복·당일 거래량가중평균가격 회복 확인 / 61300원 위 실제 완성 5분봉 안착·재시험 지지와 검증된 동시간대 상대거래량 1.2 이상 확인","risk_condition_ko":"57,700 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"036460.KS","display_name":"036460","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":36800.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":36348.25625368949,"relative_volume":1.2142276352962906,"spread_bps":13.577732518669382,"day_high":36850.0,"day_low":35900.0,"execution_condition_ko":"판단시계 2026-10-27T07:35:56.816349+09:00는 거래일·개장·시세 신선도의 증거가 아니다. 당일 거래 캘린더·거래상태·최신 정규장 호가를 먼저 검증한다. 현재 매수 만료시각은 설정되지 않았다. / 일봉 기준은 2026-10-26이다. 제공된 야간 지연 자료의 차트 35850원과 요약 36050원이 불일치하므로 이를 현재가나 당일 손절 발동 증거로 쓰지 않는다.","risk_condition_ko":"35,500 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":190600.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":191041.92655431502,"relative_volume":1.0595034591157724,"spread_bps":10.498687664041995,"day_high":193300.0,"day_low":189100.0,"execution_condition_ko":"068270.KS의 공식 거래 가능 상태와 신선한 체결·호가·실제 봉 주기를 먼저 확인한다. / 187308~188844원 부근 지지 형성 뒤 190000원 재회복 또는 191045원 회복·재시험을 감시한다. 단순 지지대 접촉은 매수 조건이 아니다.","risk_condition_ko":"187,308 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":185800.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":187123.29562151042,"relative_volume":1.0809003688237893,"spread_bps":5.380683346785042,"day_high":189800.0,"day_low":185600.0,"execution_condition_ko":"위험 대응 조건: 186,700 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"186,700 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"000100.KS","display_name":"000100","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":80600.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":80974.6203618117,"relative_volume":0.8072888886754019,"spread_bps":12.414649286157665,"day_high":81800.0,"day_low":80200.0,"execution_condition_ko":"위험 대응 조건: 81,000 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"81,000 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"009150.KS","display_name":"삼성전기","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":1203000.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":1207616.563041165,"relative_volume":1.9317764304613079,"spread_bps":8.309098462816785,"day_high":1234000.0,"day_low":1167000.0,"execution_condition_ko":"위험 대응 조건: 1,092,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"1,092,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"131290.KQ","display_name":"티에스이","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":257000.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":258372.1601307987,"relative_volume":0.9524226071344839,"spread_bps":19.43634596695821,"day_high":265000.0,"day_low":253000.0,"execution_condition_ko":"위험 대응 조건: 235,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"235,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"003230.KS","display_name":"003230","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":1127000.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":1135231.6694015027,"relative_volume":0.9037371513409823,"spread_bps":8.87705281846427,"day_high":1153000.0,"day_low":1117000.0,"execution_condition_ko":"위험 대응 조건: 1,099,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"1,099,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"207940.KS","display_name":"207940","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":1368000.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":1391876.2115757407,"relative_volume":1.2679195089241702,"spread_bps":7.307270734380709,"day_high":1438000.0,"day_low":1364000.0,"execution_condition_ko":"위험 대응 조건: 1,475,000 이상 도달, 2개 봉 확인 후 이익실현성 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"1,475,000 이상 도달, 2개 봉 확인 후 이익실현성 축소","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"067290.KQ","display_name":"067290","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":2345.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":2345.522404460213,"relative_volume":0.497366869864615,"spread_bps":21.299254526091588,"day_high":2375.0,"day_low":2315.0,"execution_condition_ko":"위험 대응 조건: 2,270 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"2,270 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"079650.KQ","display_name":"079650","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":7110.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":7178.392515404938,"relative_volume":0.418629137293594,"spread_bps":42.28329809725159,"day_high":7400.0,"day_low":6920.0,"execution_condition_ko":"위험 대응 조건: 6,700 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"6,700 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"011200.KS","display_name":"011200","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":22450.0,"market_data_asof":"2026-10-27T11:21:00+09:00","session_vwap":22588.289734714668,"relative_volume":0.5481728309798275,"spread_bps":22.246941045606228,"day_high":22800.0,"day_low":22450.0,"execution_condition_ko":"위험 대응 조건: 22,100 이하 하락, 종가 확인 후 (확인된 지지선 이탈에는 거래량 증가를 필수로 요구하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"22,100 이하 하락, 종가 확인 후 (확인된 지지선 이탈에는 거래량 증가를 필수로 요구하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","data_status_ko":"현재 세션 데이터 사용 가능","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":true,"data_ready":true,"action_ready":false,"action_status":"NO_EXECUTION_ACTION","current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-27T11:23:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-26T13:49:41.455565+09:00",
  "as_of": "2026-10-26T13:48:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
