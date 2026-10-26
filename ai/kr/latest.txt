# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-26T04:26:07.921492+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261026T131015_local-scheduler-kr-overlay_only",
  "producer_finished_at": "2026-10-26T13:10:55.973330+09:00",
  "analysis_run_id": "20261026T094055_local-scheduler-kr-full",
  "analysis_completed_at": "2026-10-26T10:05:44.814850+09:00",
  "analysis_trade_date_oldest": "2026-10-23",
  "analysis_trade_date_latest": "2026-10-23",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-26T13:10:00+09:00",
  "market_data_latest_at": "2026-10-26T13:10:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-26T13:10:49.674898+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-26T13:10:49.674898+09:00",
    "run_started_at": "2026-10-26T13:10:15.525741+09:00",
    "run_finished_at": "2026-10-26T13:10:55.973330+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 8345360,
    "total_unrealized_pnl_krw": -6598876,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 9322012
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1287000,
      "market_value_krw": 2574000,
      "unrealized_pnl_krw": -2861000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 214250,
      "market_value_krw": 2142500,
      "unrealized_pnl_krw": -1181351
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 282000,
      "market_value_krw": 1410000,
      "unrealized_pnl_krw": -664643
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 154900,
      "market_value_krw": 619600,
      "unrealized_pnl_krw": -355400
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 454000,
      "market_value_krw": 454000,
      "unrealized_pnl_krw": -699000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 16470,
      "market_value_krw": 296460,
      "unrealized_pnl_krw": -271855
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 186200,
      "market_value_krw": 186200,
      "unrealized_pnl_krw": -187967
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 60200,
      "market_value_krw": 180600,
      "unrealized_pnl_krw": -119400
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 175100,
      "market_value_krw": 175100,
      "unrealized_pnl_krw": -107234
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 120000,
      "market_value_krw": 120000,
      "unrealized_pnl_krw": -52300
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 41450,
      "market_value_krw": 82900,
      "unrealized_pnl_krw": -35300
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 58200,
      "market_value_krw": 58200,
      "unrealized_pnl_krw": -54731
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 45800,
      "market_value_krw": 45800,
      "unrealized_pnl_krw": -8700
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":120000.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":119182.56779637211,"relative_volume":0.5192803640507694,"spread_bps":8.329862557267806,"day_high":122000.0,"day_low":116100.0,"execution_condition_ko":"위험 대응 조건: 116,000 이하 하락, 종가 확인 후 손절 조건 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"116,000 이하 하락, 종가 확인 후 손절 조건","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1286000.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":1288125.247393083,"relative_volume":0.7038756021096078,"spread_bps":7.773027594247959,"day_high":1315000.0,"day_low":1267000.0,"execution_condition_ko":"000660.KS 거래일·정규장 여부, 거래 제한, 호가 신선도와 조정가격 비교 가능성을 먼저 확인한다. 현재 발동된 주문은 없다. / 1297000원 돌파와 1284000~1297000원 재시험, 현재 정규장의 거래량가중평균가격 및 동시간대 상대거래량을 관찰하되 새 매수 승인으로 간주하지 않는다.","risk_condition_ko":"1,223,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":454000.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":453958.91019983403,"relative_volume":0.7131997511685076,"spread_bps":11.007154650522839,"day_high":464500.0,"day_low":447500.0,"execution_condition_ko":"267260.KS의 실제 거래일·정규장·호가 시각·스프레드·거래량과 검증된 5분봉, 당일 거래량가중평균가격을 확인한다. / 483500원 회복·재지지, 당일 거래량가중평균가격 상회와 동시간대 누적 상대거래량 1.2 이상을 함께 관찰한다. 충족하더라도 현재 매수 주문이 활성화되지는 않는다.","risk_condition_ko":"448,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":214500.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":213592.26862462237,"relative_volume":0.6189566122265171,"spread_bps":23.33722287047841,"day_high":216000.0,"day_low":211500.0,"execution_condition_ko":"005930.KS 203500~204500원에서는 저점 회복과 높아지는 단기 저점을 관찰한다. 지지 가격 도달만으로 매수하지 않는다. / 005930.KS 215500~219500원 반등 저항 회복 실패는 전술 물량 위험 축소 조건이다. 양 끝 가격을 별개의 중복 매도 신호로 사용하지 않는다.","risk_condition_ko":"203,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":282500.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":281602.41866723506,"relative_volume":0.36101643510070636,"spread_bps":17.71479185119575,"day_high":286000.0,"day_low":275000.0,"execution_condition_ko":"신선한 정규장 자료로 281000원과 최신 거래량가중평균가격 회복·재시험 지지를 확인한다. 단순 통과는 매수 신호가 아니다. / 286000원 돌파·지지 전환과 산식이 검증된 동시간대 상대거래량 증가를 확인하고 가까운 저항까지 비용 차감 손익비를 재계산한다. 향후 매수 재평가 기준은 최소 2배이며 성공확률을 뜻하지 않는다.","risk_condition_ko":"275,000 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":186200.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":186343.95213500605,"relative_volume":0.6787197439872602,"spread_bps":5.372011818426,"day_high":191000.0,"day_low":183500.0,"execution_condition_ko":"거래일·정규장·거래정지 여부와 신선한 호가를 확인한다. 188500원은 2026-10-23 참고 종가이며 현재가가 아니다. 2026-10-25 보도의 가격 반응도 미확인이다. / 192200원 돌파·재시험 지지, 당일 거래량가중평균가격 상회와 동시간대 상대거래량 1.2배 이상을 함께 관찰한다. 1.2배는 제안 기준이며 산식 불명인 20.15배는 사용하지 않는다. 관찰 조건 충족만으로 현재 매수가 활성화되지 않는다.","risk_condition_ko":"182,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":175200.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":174011.11207634993,"relative_volume":0.6489379577119199,"spread_bps":5.709391949757351,"day_high":176700.0,"day_low":170900.0,"execution_condition_ko":"최신 정규장 가격으로 171900원과 171100원의 유지·이탈·회복을 구분한다. 핵심 지지 아래 다음 지지는 제공 자료로 확정할 수 없다. / 175400~176400원 회복과 재지지를 초기 개선 신호로 관찰하되 신규 매수를 자동 승인하지 않는다.","risk_condition_ko":"171,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":154900.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":154564.0967331546,"relative_volume":0.6224519236358956,"spread_bps":6.457862447529867,"day_high":157200.0,"day_low":150400.0,"execution_condition_ko":"147000~150000원 재시험 후 회복, 매도량 둔화와 당일 거래량가중평균가격 회복을 관찰한다. 접촉만으로 매수하지 않는다. / 157400원 돌파·재시험 지지를 확인하되 161400~164600원 가까운 저항까지의 비용 후 보상·위험이 2배 미만이면 진입하지 않는다.","risk_condition_ko":"147,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":60100.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":60306.60253398256,"relative_volume":0.35832996241261583,"spread_bps":16.62510390689942,"day_high":61600.0,"day_low":59300.0,"execution_condition_ko":"59600원 방어와 저점 상승을 확인한다. 지지 실패는 신규 매수 차단·손실 통제 조건이며 자동 저가매수 신호가 아니다. / 62800원 돌파·재지지, 신선한 당일 거래량가중평균가격 상회, 검증된 동시간 누적 상대거래량 1.2 이상을 관찰한다. 현재 손익비는 부족하므로 새 가격구조에서 비용 후 손익비를 다시 계산한다.","risk_condition_ko":"59,600 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":58100.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":58041.8828246461,"relative_volume":0.6025008262818685,"spread_bps":17.196904557179707,"day_high":59100.0,"day_low":57200.0,"execution_condition_ko":"판단 시각은 2026-10-26T05:27:58.760887+09:00이고 일봉 기준일은 2026-10-23이다. 이 시각만으로 정규장 일정·휴장 여부·거래 상태·시세 신선도를 확정하지 않는다. 최신 자료 확인이 우선이며 활성 조건부 주문이나 만료시각은 없다. / 마지막 장중 봉 표시는 2026-10-23 20:00이며 요청 5분봉과 반환 1분봉이 불일치한다. 과거 상대거래량 21.45와 거래량가중평균가격 58882.85원은 현재 신호에서 제외한다. 일거래량의 20일 평균 대비 약 1.07배도 매도 소진 확인은 아니다.","risk_condition_ko":"57,700 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":16470.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":16522.47149628348,"relative_volume":0.6585349160665698,"spread_bps":6.0698027314112295,"day_high":16820.0,"day_low":16340.0,"execution_condition_ko":"판단시계는 2026-10-26T05:04:50.114332+09:00이다. 이는 실제 개장·휴장·조기종료·호가 신선도를 증명하지 않으므로 거래일 달력, 거래구분, 체결시각, 봉 간격과 최신 호가를 별도로 확인한다. / 2026-10-23 야간자료, 약 56.8시간 지연됐다고 보고된 장중자료, 산식 미검증 상대거래량 18.31 및 과거 거래량가중평균가격은 당일 신호에서 제외한다.","risk_condition_ko":"16,450 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":45750.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":45897.20561089585,"relative_volume":0.4045847290113801,"spread_bps":10.922992900054615,"day_high":47100.0,"day_low":44950.0,"execution_condition_ko":"최신 호가 시각·실제 정규장·거래정지 여부와 완성 5분봉을 확보한다. 제공된 1분봉을 5분봉 확인으로 대체하지 않는다. / 갱신 거래량가중평균가격 위에서 46,973~47,100 회복·재시험 지지와 정의가 검증된 동일시각 상대거래량 1.2 이상을 관찰한다. 마지막 관측값 0.87과 제안 기준 1.2를 구분한다.","risk_condition_ko":"45,650 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":41500.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":41404.93957622067,"relative_volume":0.37133614188861774,"spread_bps":12.055455093429776,"day_high":42350.0,"day_low":40750.0,"execution_condition_ko":"판단 시계는 2026-10-26T05:53:19.580991+09:00이고 가격 기준일은 2026-10-23이다. 실제 거래일·정규장·주문 가능 상태와 체결·호가 신선도는 별도 확인한다. 세부 봉과 요약값이 불일치하는 지연 자료로 현재 조건을 판정하지 않는다. / 43,800 회복, 43,200~43,800 재시험 지지, 거래량가중평균가 상회, 동시간대 상대거래량 1.2 이상, 비용 차감 후 손익비 2배 이상과 계좌 위험여력을 함께 확인한다. 상대거래량 기준은 제안 운용규칙이며 일간 평균 대비 거래량과 혼용하지 않는다.","risk_condition_ko":"41,700 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003010.KS","display_name":"003010","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":8300.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":8651.965232830447,"relative_volume":1.671788119015792,"spread_bps":12.055455093429776,"day_high":9470.0,"day_low":8040.0,"execution_condition_ko":"003010.KS의 9140~9376.2원 접근 후 최신 5분봉 저점 안정·반등·거래량 회복을 관찰한다. 단순 접촉은 매수 신호가 아니다. / 10044.3원과 10350원 회복·재시험 이후 10450~10510원 및 10860원 공급 소화를 확인한다. 가격 회복과 유리한 매수 손익비는 별개다.","risk_condition_ko":"10,350 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":126400.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":126362.38263529909,"relative_volume":0.3671425608711491,"spread_bps":7.908264136022144,"day_high":130300.0,"day_low":124300.0,"execution_condition_ko":"최신 정규장 자료로 128100~128300원 방어와 130500~130600원 회복·재지지, 당일 거래량가중평균가격 상회를 확인한다. / 134100~134450원 저항대 돌파·종가 안착과 실제 다음 거래일 재지지를 확인한다. 가까운 저항까지 비용 후 보상·위험이 부족하면 계속 대기한다.","risk_condition_ko":"130,535 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"131290.KQ","display_name":"티에스이","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":245500.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":247001.75688625698,"relative_volume":0.5331337974401512,"spread_bps":20.42900919305414,"day_high":255000.0,"day_low":239500.0,"execution_condition_ko":"판단시각은 2026-10-26T06:44:31.206574+09:00이다. 연구일과 현지 날짜는 같지만 거래일·정규장 운영·최신 체결 시각은 별도 확인 대상이다. 10:30은 서울 시간 기준 최초 시험 진입 검토시각이지 만료시각이 아니다. 확인된 만료시한이 없어 다음 거래일로 연장하거나 주문을 활성화하지 않는다. / 제공된 가격 표시는 2026-10-23 20:00이며 시간대가 미확인이다. 요약가 257000원과 마지막 봉 252000원, 요청 5분봉과 반환 1분봉의 불일치를 해결한다. 현재 가격은 확인할 수 없다.","risk_condition_ko":"265,850 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"411080.KQ","display_name":"411080","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":6630.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":7025.097380947047,"relative_volume":3.8586035434474866,"spread_bps":30.120481927710845,"day_high":7390.0,"day_low":6400.0,"execution_condition_ko":"최신 시각이 표시된 가격, 호가차, 체결 유동성, 거래제한, 실제 정규장 운영 여부를 확인한다. 분석 완료만으로 매수 조건이 충족되지는 않는다. / 높아지는 저점과 6380–6420 및 6500–6560 회복·유지 여부를 관찰하고 가까운 저항까지의 비용 후 보상 대비 위험을 다시 계산한다.","risk_condition_ko":"5,954 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":189100.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":188864.50326894227,"relative_volume":0.6837085287695462,"spread_bps":10.576414595452142,"day_high":190500.0,"day_low":187000.0,"execution_condition_ko":"033780.KS 공식 거래일·정규장·휴장 여부와 최신 가격시각·호가·당일 5분봉을 확인한다. 이전 거래일 1분봉이나 지연자료의 거래량 0은 당일 신호로 쓰지 않는다. / 033780.KS 188200~188800원 방어 후 189400원 회복·유지, 당일 거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상을 관찰한다. 손익비 미달이면 매수하지 않는다.","risk_condition_ko":"188,200 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"036460.KS","display_name":"036460","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":36050.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":36064.745073949816,"relative_volume":0.7711940871840609,"spread_bps":13.86001386001386,"day_high":36700.0,"day_low":35800.0,"execution_condition_ko":"036460.KS 최신 가격과 실제 정규장, 거래정지 여부 및 계좌 위험한도를 먼저 확인한다. / 36050~36262원에서 매도 거래량 둔화, 재상승과 거래량가중평균가격 회복을 확인한다. 가격 도달만으로 매수하지 않는다.","risk_condition_ko":"35,550 이하 하락, 종가 확인 후 (거래량 증가를 필수 조건으로 두지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"064400.KS","display_name":"LG CNS","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":73800.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":73250.62531540693,"relative_volume":1.7152716440205014,"spread_bps":13.559322033898306,"day_high":74100.0,"day_low":71300.0,"execution_condition_ko":"거래일 달력·거래 상태와 실제 정규장을 확인하고 최신 체결가, 실제 5분봉, 해당 장 거래량가중평균가격, 동시간대 상대거래량, 호가차와 주문장 유동성을 확보한다. 과거 봉이나 장 시작 전 표시 거래량으로 오늘 조건을 판정하지 않는다. / 71,200~72,040원 지지 관찰과 72,040원 회복·재시험을 점검한다. 74,800~75,000원 저항 돌파도 별도로 관찰하되 현재 제시된 넓은 손절의 돌파 추격은 제외한다.","risk_condition_ko":"71,200 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"018880.KS","display_name":"018880","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":3630.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":3599.683189090641,"relative_volume":0.3444634934677209,"spread_bps":13.764624913971094,"day_high":3680.0,"day_low":3540.0,"execution_condition_ko":"원문 재무제표의 통화·단위·보고기간·공개시점·주식기준·해당 예탁증서 전환비율을 검증하고 차입 만기·약정·확약 신용한도를 확인한다. / 2026-10-23 20:00으로 표시된 지연 관찰값을 신선한 정규장 호가와 올바른 5분 봉으로 교체한다. 요약 거래량 0을 수요 부재로 해석하지 않는다.","risk_condition_ko":"3,600 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"011200.KS","display_name":"011200","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":22600.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":22446.749680085275,"relative_volume":0.3366476835388642,"spread_bps":22.148394241417495,"day_high":22800.0,"day_low":22100.0,"execution_condition_ko":"011200.KS의 연구일은 2026-10-26, 일별 가격 기준일은 2026-10-23이다. 실제 거래소 일정·정규장 여부·휴장 및 조기종료 여부와 신선한 호가를 확인한다. / 판단 시각 2026-10-26T06:17:37.872722+09:00에서 10:30은 가장 이른 검토 시각이지 만료가 아니다. 유효기한은 제공되지 않았으므로 만료나 다음 거래일 이월을 추정하지 않는다.","risk_condition_ko":"22,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":503000.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":487693.4106673045,"relative_volume":0.9616533404678976,"spread_bps":19.90049751243781,"day_high":504000.0,"day_low":471500.0,"execution_condition_ko":"위험 대응 조건: 503,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"503,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000100.KS","display_name":"000100","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":81900.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":83105.14168142514,"relative_volume":0.5220345990296957,"spread_bps":12.202562538133007,"day_high":84900.0,"day_low":81900.0,"execution_condition_ko":"위험 대응 조건: 81,779.57 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"81,779.57 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"009150.KS","display_name":"삼성전기","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1126000.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":1118058.2521994135,"relative_volume":0.5909121824846516,"spread_bps":8.884940026654819,"day_high":1137000.0,"day_low":1092000.0,"execution_condition_ko":"위험 대응 조건: 1,048,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"1,048,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":141300.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":139258.15469944535,"relative_volume":0.6149143248805433,"spread_bps":7.079646017699115,"day_high":142200.0,"day_low":136200.0,"execution_condition_ko":"위험 대응 조건: 139,760 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"139,760 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003230.KS","display_name":"003230","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1143000.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":1174440.319692536,"relative_volume":0.9772475334714363,"spread_bps":8.7527352297593,"day_high":1242000.0,"day_low":1137000.0,"execution_condition_ko":"위험 대응 조건: 1,215,000 이하 하락, 종가 확인 후 (위험 축소에 거래량 증가를 요구하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"1,215,000 이하 하락, 종가 확인 후 (위험 축소에 거래량 증가를 요구하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"396300.KQ","display_name":"396300","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":9410.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":9747.797580998635,"relative_volume":0.8153567234413673,"spread_bps":21.231422505307854,"day_high":10080.0,"day_low":9340.0,"execution_condition_ko":"위험 대응 조건: 8,720 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"8,720 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"079650.KQ","display_name":"079650","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":6930.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":7105.760752500571,"relative_volume":0.2518338565812918,"spread_bps":28.94356005788712,"day_high":7560.0,"day_low":6810.0,"execution_condition_ko":"위험 대응 조건: 7,070 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"7,070 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":188600.0,"market_data_asof":"2026-10-26T13:10:00+09:00","session_vwap":190697.2569961013,"relative_volume":0.8097411808764485,"spread_bps":5.303632988597189,"day_high":196900.0,"day_low":188000.0,"execution_condition_ko":"위험 대응 조건: 189,800 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"189,800 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-26T13:10:00+09:00"},"quality_at_build":{"execution_ready":false,"data_ready":false,"action_ready":false,"action_status":"DATA_RECHECK_REQUIRED","current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-26T13:12:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-22T14:48:57.208041+09:00",
  "as_of": "2026-10-22T14:47:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
