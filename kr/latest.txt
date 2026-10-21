# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-21T15:30:22.045720+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261021T152511_local-freshness-kr-overlay",
  "producer_finished_at": "2026-10-21T15:28:04.341752+09:00",
  "analysis_run_id": "20261021T044513_local-scheduler-kr-full",
  "analysis_completed_at": "2026-10-21T07:07:20.515277+09:00",
  "analysis_trade_date_oldest": "2026-10-20",
  "analysis_trade_date_latest": "2026-10-20",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-21T15:27:00+09:00",
  "market_data_latest_at": "2026-10-21T15:27:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-21T15:28:00.731138+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-21T15:28:00.731138+09:00",
    "run_started_at": "2026-10-21T15:25:11.071049+09:00",
    "run_finished_at": "2026-10-21T15:28:04.341752+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 8802960,
    "total_unrealized_pnl_krw": -6141276,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 9779612
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1296000,
      "market_value_krw": 2592000,
      "unrealized_pnl_krw": -2843000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 222500,
      "market_value_krw": 2225000,
      "unrealized_pnl_krw": -1098851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 318000,
      "market_value_krw": 1590000,
      "unrealized_pnl_krw": -484643
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 165800,
      "market_value_krw": 663200,
      "unrealized_pnl_krw": -311800
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 496000,
      "market_value_krw": 496000,
      "unrealized_pnl_krw": -657000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 17670,
      "market_value_krw": 318060,
      "unrealized_pnl_krw": -250255
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 203000,
      "market_value_krw": 203000,
      "unrealized_pnl_krw": -171167
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 67300,
      "market_value_krw": 201900,
      "unrealized_pnl_krw": -98100
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 179000,
      "market_value_krw": 179000,
      "unrealized_pnl_krw": -103334
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 131800,
      "market_value_krw": 131800,
      "unrealized_pnl_krw": -40500
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 44300,
      "market_value_krw": 88600,
      "unrealized_pnl_krw": -29600
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 63500,
      "market_value_krw": 63500,
      "unrealized_pnl_krw": -49431
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 50900,
      "market_value_krw": 50900,
      "unrealized_pnl_krw": -3600
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":222500.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":222483.89748261275,"relative_volume":0.7716273375320912,"spread_bps":22.246941045606228,"day_high":228000.0,"day_low":217000.0,"execution_condition_ko":"위험 대응 조건: 204,500 이하 하락, 종가 확인 후 손절 조건 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"204,500 이하 하락, 종가 확인 후 손절 조건","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":496000.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":495294.9714547864,"relative_volume":0.6187650184282794,"spread_bps":19.940179461615152,"day_high":506500.0,"day_low":485500.0,"execution_condition_ko":"위험 대응 조건: 473,500 이하 하락, 2개 봉 확인 후 (보호적 매도에는 최소 거래량 조건을 적용하지 않는다.) 손절 조건 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"473,500 이하 하락, 2개 봉 확인 후 (보호적 매도에는 최소 거래량 조건을 적용하지 않는다.) 손절 조건","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":17670.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":17623.94839879732,"relative_volume":0.8044385589915239,"spread_bps":22.535211267605636,"day_high":17840.0,"day_low":17170.0,"execution_condition_ko":"위험 대응 조건: 17,210 이하 하락, 종가 확인 후 손절 조건 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"17,210 이하 하락, 종가 확인 후 손절 조건","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":179000.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":179491.37978787022,"relative_volume":0.4870171865278957,"spread_bps":16.63432215137233,"day_high":180700.0,"day_low":177700.0,"execution_condition_ko":"위험 대응 조건: 177,000 이하 하락, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"177,000 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":203000.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":202033.04293617528,"relative_volume":0.7615100028287218,"spread_bps":24.42002442002442,"day_high":207000.0,"day_low":197700.0,"execution_condition_ko":"거래소 일정·거래정지 여부·정규장 구분과 신선한 가격·호가·거래량을 먼저 확인한다. 2026-10-20까지의 자료를 2026-10-21 진입 확인으로 사용하지 않는다. / 197400~198000원 방어, 저점 상승과 당일 거래량가중평균가 회복을 함께 관찰한다. 지지 방어만으로 진입하지 않는다.","risk_condition_ko":"187,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":165800.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":163280.95684932373,"relative_volume":1.637586926149186,"spread_bps":29.62962962962963,"day_high":168500.0,"day_low":154200.0,"execution_condition_ko":"010120.KS의 적용 거래일정·거래상태·시각 표시 체결 가능 가격·정규장 거래량가중평균가격·정확한 5분봉을 확보한다. / 149200–150000 방어, 저점 상승과 158600 회복을 관찰한다. 2026-10-21 충족 여부는 미확인이다.","risk_condition_ko":"149,200 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"지금 실행 검토 가능","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":131800.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":131881.9666560268,"relative_volume":0.7442281056903943,"spread_bps":7.572889057175312,"day_high":136500.0,"day_low":127000.0,"execution_condition_ko":"판단 시각은 2026-10-21T05:37:48.578994+09:00이고 가격 기준일은 2026-10-20이다. 실제 거래일·정규장 운영·최신 호가·실제 5분봉과 거래량 산식을 별도 확인한다. / 353200.KS의 136900원 회복 후 연속 5분봉 두 개의 재시험 지지, 당일 거래량가중평균가 상회와 동일 시간대 상대거래량 1.2 이상을 확인한다. 현재 충족 관측치는 없다.","risk_condition_ko":"130,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":67300.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":67694.70733621751,"relative_volume":0.4479845938284758,"spread_bps":14.869888475836431,"day_high":69700.0,"day_low":66700.0,"execution_condition_ko":"판단 기준시각은 2026-10-21T05:19:54.555350+09:00이고 가격 근거는 2026-10-20 완료 일봉이다. 실제 거래일·정규장·거래정지·최신 호가와 봉 간격을 별도로 확인해야 한다. / 70,626~71,700 회복·재시험 지지, 당일 거래량가중평균가격 상회, 검증된 동시간대 상대거래량 1.2 이상을 함께 관찰한다. 이는 재심사 조건이지 현재 매수 승인이 아니다.","risk_condition_ko":"66,100 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":63500.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":63734.79518354265,"relative_volume":0.5845611363875938,"spread_bps":15.735641227380016,"day_high":64800.0,"day_low":62600.0,"execution_condition_ko":"공식 거래일·정규장 운영·호가 시각·실제 봉 간격을 먼저 확인한다. 런타임 날짜만으로 거래 가능 상태를 확정하지 않는다. 10:30은 확인된 거래일의 관찰 개시 기준이며 주문 만료시각이 아니다. / 61500~61800원 방어 후 63300~64600원 회복·재시험을 관찰한다. 과매도나 하락폭만으로 안전마진을 인정하지 않는다.","risk_condition_ko":"61,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":44300.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":44638.54836500185,"relative_volume":0.7863213713971352,"spread_bps":11.29305477131564,"day_high":46400.0,"day_low":43800.0,"execution_condition_ko":"실제 거래일과 거래정지 여부, 시각이 일치하는 정규장 가격·거래량·호가차이·거래량가중평균가격을 확인한다. 보유량과 순자산도 확보해 기술적 매도신호와 별개로 위험예산 준수 여부를 판정한다. / 43,250과 43,050을 감시하고 43,000은 정규장 지지로 단정하지 않는다. 44,800–45,850 반등 실패와 갱신된 200일 평균선 회복 실패도 별도로 점검한다.","risk_condition_ko":"43,050 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1296000.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":1290920.666736711,"relative_volume":1.0625020363249296,"spread_bps":7.642338555598013,"day_high":1329000.0,"day_low":1254000.0,"execution_condition_ko":"000660.KS 최신 정규장 자료에서 1183000~1208000원 후보 지지 방어와 저점 상승을 확인한다. 지지 방어만으로 매수하지 않는다. / 000660.KS 1262000~1290000원 회복과 되돌림 지지, 당일 거래량가중평균가격 상회, 동시간대 상대거래량 1.2배 이상을 확인하고 새로운 지지 기준으로 손익비를 다시 계산한다.","risk_condition_ko":"1,183,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":318000.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":317796.1054339102,"relative_volume":0.5497822540683512,"spread_bps":15.39645881447267,"day_high":325500.0,"day_low":307000.0,"execution_condition_ko":"최신 정규장 자료로 307000 지지와 기준 종가 310000 회복 여부를 확인한다. / 329500 위 완성 5분봉 2개, 재시험 지지, 당일 정규장 거래량가중평균가격 상회와 검증된 동일 시간대 상대거래량 1.2배 이상을 관찰한다. 충족해도 현재 계획에서는 자동 매수하지 않는다.","risk_condition_ko":"307,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":50900.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":51246.45147715596,"relative_volume":0.7561344725448638,"spread_bps":19.665683382497544,"day_high":52800.0,"day_low":49900.0,"execution_condition_ko":"실제 정규장 일정·휴장·단축장·거래정지와 최신 공시를 확인하고 신선한 가격·거래량가중평균가격·동시간대 거래량을 확보한다. / 51595~51600원을 동일한 이동평균 확인구간으로 취급한다. 5원 차이를 독립 신호로 사용해 반복 매매하지 않는다. 회복·되눌림과 52900원 종가 돌파는 재평가 신호이지 매수 주문이 아니다.","risk_condition_ko":"51,595 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"086790.KS","display_name":"086790","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":121100.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":121564.23226849684,"relative_volume":0.8458556254225679,"spread_bps":8.206811653672547,"day_high":124800.0,"day_low":120100.0,"execution_condition_ko":"위험 대응 조건: 125,600 이상 도달, 장중 확인 시 (매도 위험관리에 최소 상대거래량 조건을 적용하지 않는다.) 리스크 축소 · 추가 조건 확인 필요: 제공된 기술 분석의 124550–125600원 저항 구간에서 신선한 정규장 자료로 거부 또는 회복·유지 실패가 확인될 때 적용한다. 단순 접촉이나 현재 확인되지 않은 실패를 매도 신호로 간주하지 않는다. (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"125,600 이상 도달, 장중 확인 시 (매도 위험관리에 최소 상대거래량 조건을 적용하지 않는다.) 리스크 축소 · 추가 조건 확인 필요: 제공된 기술 분석의 124550–125600원 저항 구간에서 신선한 정규장 자료로 거부 또는 회복·유지 실패가 확인될 때 적용한다. 단순 접촉이나 현재 확인되지 않은 실패를 매도 신호로 간주하지 않는다.","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"396300.KQ","display_name":"396300","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":11110.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":10909.973606672325,"relative_volume":2.588232490204456,"spread_bps":8.956560680698612,"day_high":11690.0,"day_low":9690.0,"execution_condition_ko":"위험 대응 조건: 10,000 이상 도달, 장중 확인 시 이익실현성 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"10,000 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"지금 실행 검토 가능","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"051900.KS","display_name":"051900","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":271500.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":272286.2449134097,"relative_volume":0.3643900400816862,"spread_bps":18.467220683287163,"day_high":276500.0,"day_low":270500.0,"execution_condition_ko":"위험 대응 조건: 282,000 이하 하락, 장중 확인 시 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"282,000 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"지금 실행 검토 가능","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"373220.KS","display_name":"LG에너지솔루션","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":409500.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":412675.86496999476,"relative_volume":0.7712405123220184,"spread_bps":12.084592145015106,"day_high":420000.0,"day_low":404500.0,"execution_condition_ko":"위험 대응 조건: 422,000 이하 하락, 장중 확인 시 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"422,000 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"지금 실행 검토 가능","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003230.KS","display_name":"003230","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1254000.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":1272918.6797167847,"relative_volume":1.1291507367203022,"spread_bps":15.785319652722968,"day_high":1289000.0,"day_low":1239000.0,"execution_condition_ko":"003230.KS의 거래일·정규장 상태·거래정지 여부, 최신 체결시각, 호가·스프레드와 실제 5분봉을 먼저 확인한다. 제공된 2026-10-20 종가 1221000원은 현재 실행 가격이 아니다. / 1208000~1218000원 시험 후 회복·유지, 당일 거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상을 관찰한다. 이 조건만으로 부족한 손익비가 개선되지는 않는다.","risk_condition_ko":"1,191,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"036460.KS","display_name":"036460","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":36100.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":36268.905402350814,"relative_volume":0.6146499891348209,"spread_bps":41.40786749482402,"day_high":36700.0,"day_low":35900.0,"execution_condition_ko":"36000~36200원 또는 35850~35950원에서 최신 정규장 5분봉 두 개의 지지 회복·유지, 당일 거래량가중평균가격 상회와 동시간대 상대거래량 1.5 이상 확인. / 36750~37000원 저항 회복과 37250원 돌파·재지지·종가 유지 확인. 가까운 저항 기준 비용 차감 후 보상·위험 비율 검증 전 추격하지 않는다.","risk_condition_ko":"35,850 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":193800.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":194703.67317873257,"relative_volume":0.6889020547986276,"spread_bps":15.317845289762573,"day_high":196400.0,"day_low":193500.0,"execution_condition_ko":"033780.KS의 실제 KRX 거래일·정규장·정지 여부와 시세 신선도를 확인한다. 2026-10-21자 신청 관련 보도의 발행시점이 보고서 간 달라 판단시각 이전 공개 여부도 재확인한다. / 189400~191000원에서 매도 거래량 감소 후 연속 5분봉 상승 저점·지지 회복·거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상을 관찰한다. 관측만으로 매수 승인하지 않는다.","risk_condition_ko":"189,400 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000100.KS","display_name":"000100","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":86600.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":87140.44776158647,"relative_volume":1.3308833333734151,"spread_bps":11.527377521613833,"day_high":88500.0,"day_low":85800.0,"execution_condition_ko":"실제 정규장·휴장·거래정지 여부와 호가 타임스탬프를 확인하고 86,200과 85,200의 가격 불일치 및 봉 간격 오류를 해소한다. / 85,300 방어, 실제 5분봉 두 개의 저점 상승, 당일 거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상을 확인한다. 이 조건만으로 자동 매수하지 않는다.","risk_condition_ko":"85,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"018880.KS","display_name":"018880","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":3840.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":3859.7604468034046,"relative_volume":0.5062938503020005,"spread_bps":13.029315960912053,"day_high":3970.0,"day_low":3790.0,"execution_condition_ko":"거래소 달력·정규장 여부·거래 상태·호가 시각을 확인한다. 오래된 2026-10-20 20:00 한국시간 자료의 상세 마지막 가격 3890과 일별 요약 3905의 차이 및 실제 5분봉 여부를 대조한다. 오래된 거래량 0을 수요 부재로 해석하지 않는다. / 3830–3860 지지 시험 후 연속된 새로운 5분봉 두 개가 3860 위에서 마감하는지 확인한다. 3895–3905 회복은 추가 증거이며 지지선 접촉만으로 매수하지 않는다.","risk_condition_ko":"3,750 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"011200.KS","display_name":"011200","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":23400.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":23298.214654526244,"relative_volume":0.7770709877924026,"spread_bps":21.52852529601722,"day_high":23750.0,"day_low":22900.0,"execution_condition_ko":"011200.KS의 2026-10-21 실제 거래일·휴장·단축장 여부와 최신 정규장 호가·봉 시각을 확인한다. 거래자가 지적한 요약가 23450원과 마지막 봉 23250원의 불일치, 요청한 5분봉 대신 반환된 1분봉 문제를 해소한다. / 기존 보유수량·취득가·현금·업종 집중도·채택 손절을 확인하고 종목 5%, 해운업 10%, 전술 계획손실 0.5% 한도를 점검한다. 초과 확인 시 필요한 만큼 위험 감축하며 자금 마련 목적의 매도로 분류하지 않는다.","risk_condition_ko":"22,600 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":197000.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":198140.9556976208,"relative_volume":1.1526201879877933,"spread_bps":5.049229992426155,"day_high":203500.0,"day_low":196800.0,"execution_condition_ko":"195100~196000원 지지·재회복을 신선한 정규장 5분봉, 당일 거래량가중평균가격, 동일 경과시간 상대거래량 1.2 이상으로 확인한다. 단순 가격 도달은 매수 신호가 아니다. / 202000원 초과 종가와 거래량 확인 후 재시험 지지를 관찰한다. 203000원 진입·195000원 방어 예시는 210500원까지 비용 전 약 0.94배여서 그대로 추격하지 않는다.","risk_condition_ko":"195,100 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"131290.KQ","display_name":"티에스이","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":272000.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":274515.85225599236,"relative_volume":0.5977864025699491,"spread_bps":36.83241252302026,"day_high":287500.0,"day_low":262000.0,"execution_condition_ko":"위험 대응 조건: 258,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"258,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":154100.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":152646.541180261,"relative_volume":0.9395566869139096,"spread_bps":25.74002574002574,"day_high":156900.0,"day_low":143000.0,"execution_condition_ko":"위험 대응 조건: 148,100 이하 하락, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"148,100 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":135200.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":135938.31861170594,"relative_volume":0.5004407934726622,"spread_bps":7.323324789454412,"day_high":139700.0,"day_low":134600.0,"execution_condition_ko":"위험 대응 조건: 135,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"135,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"122350.KQ","display_name":"122350","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1635.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":1628.9988585789015,"relative_volume":0.21198890180217778,"spread_bps":6.114338122898196,"day_high":1666.0,"day_low":1600.0,"execution_condition_ko":"위험 대응 조건: 1,612 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"1,612 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"105560.KS","display_name":"105560","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":159900.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":161406.25652755535,"relative_volume":0.7837072265763797,"spread_bps":36.65241295051924,"day_high":164500.0,"day_low":159000.0,"execution_condition_ko":"위험 대응 조건: 159,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"159,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":552000.0,"market_data_asof":"2026-10-21T15:27:00+09:00","session_vwap":558355.287341995,"relative_volume":1.0124305049376248,"spread_bps":17.937219730941703,"day_high":574000.0,"day_low":547000.0,"execution_condition_ko":"위험 대응 조건: 526,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"526,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-21T15:27:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-21T15:37:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-21T14:47:34.830079+09:00",
  "as_of": "2026-10-21T14:44:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
