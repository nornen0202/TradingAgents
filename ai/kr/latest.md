# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-23T05:41:39.452452+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261023T143017_local-scheduler-kr-overlay_only",
  "producer_finished_at": "2026-10-23T14:31:04.152034+09:00",
  "analysis_run_id": "20261022T050013_local-scheduler-kr-full",
  "analysis_completed_at": "2026-10-22T07:34:14.045585+09:00",
  "analysis_trade_date_oldest": "2026-10-21",
  "analysis_trade_date_latest": "2026-10-21",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-23T14:30:00+09:00",
  "market_data_latest_at": "2026-10-23T14:30:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-23T14:30:57.935590+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-23T14:30:57.935590+09:00",
    "run_started_at": "2026-10-23T14:30:17.032854+09:00",
    "run_finished_at": "2026-10-23T14:31:04.152034+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 8293340,
    "total_unrealized_pnl_krw": -6650896,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 9269992
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1258000,
      "market_value_krw": 2516000,
      "unrealized_pnl_krw": -2919000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 212500,
      "market_value_krw": 2125000,
      "unrealized_pnl_krw": -1198851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 281500,
      "market_value_krw": 1407500,
      "unrealized_pnl_krw": -667143
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
      "current_price_krw": 464000,
      "market_value_krw": 464000,
      "unrealized_pnl_krw": -689000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 16830,
      "market_value_krw": 302940,
      "unrealized_pnl_krw": -265375
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 188700,
      "market_value_krw": 188700,
      "unrealized_pnl_krw": -185467
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 61000,
      "market_value_krw": 183000,
      "unrealized_pnl_krw": -117000
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 172700,
      "market_value_krw": 172700,
      "unrealized_pnl_krw": -109634
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 122900,
      "market_value_krw": 122900,
      "unrealized_pnl_krw": -49400
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 42150,
      "market_value_krw": 84300,
      "unrealized_pnl_krw": -33900
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 59100,
      "market_value_krw": 59100,
      "unrealized_pnl_krw": -53831
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 47600,
      "market_value_krw": 47600,
      "unrealized_pnl_krw": -6900
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":154900.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":150857.05081626098,"relative_volume":1.4206381689713745,"spread_bps":6.457862447529867,"day_high":155900.0,"day_low":147000.0,"execution_condition_ko":"위험 대응 조건: 154,200 이하 하락, 종가 확인 후 손절 조건 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"154,200 이하 하락, 종가 확인 후 손절 조건","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":281500.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":286241.29126937373,"relative_volume":0.6933731329074693,"spread_bps":17.77777777777778,"day_high":294500.0,"day_low":279000.0,"execution_condition_ko":"위험 대응 조건: 331,500 이상 도달, 장중 확인 시 (매도에는 상대거래량 하한을 적용하지 않는다.) 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"331,500 이상 도달, 장중 확인 시 (매도에는 상대거래량 하한을 적용하지 않는다.) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1257000.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":1221440.7981488595,"relative_volume":0.9534848116207109,"spread_bps":7.958615200955034,"day_high":1263000.0,"day_low":1171000.0,"execution_condition_ko":"000660.KS의 1329000~1332000원 돌파·재시험 지지, 신선한 당일 거래량가중평균가격 상회와 동일 시간대 상대거래량 1.2배 이상을 관찰한다. 충족돼도 현재 계획에서는 매수가 발동하지 않는다. / 000660.KS의 1402000원 종가 회복·후속 지지 후 1467000원까지의 비용 후 손익비와 근거 있는 손절폭을 다시 계산한다. 추세 판단 개선과 신규 매수 승인을 구분한다.","risk_condition_ko":"1,254,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":464000.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":458922.55472481984,"relative_volume":0.9586093158077527,"spread_bps":10.770059235325794,"day_high":473000.0,"day_low":448500.0,"execution_condition_ko":"267260.KS의 실제 거래일·세션·현재가 시각·거래정지·변동성완화장치·호가단위를 먼저 검증 / 506500 돌파·재시험 지지와 당일 거래량가중평균가격 상회, 동일 경과시간 기준 상대거래량 1.2 이상을 확인하되 손익비 미달이면 계속 대기","risk_condition_ko":"485,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":212750.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":209085.01557515774,"relative_volume":0.7977639358010467,"spread_bps":23.501762632197416,"day_high":214500.0,"day_low":203500.0,"execution_condition_ko":"실제 거래일·정규장 일정·거래 가능 상태·최신 체결시각·봉 간격을 먼저 확인한다. 전일 20:00 지연 자료와 산식 미확인 상대거래량 18.24는 현재 진입 신호로 사용하지 않는다. / 228000원 돌파·재지지, 230500~233500원 회복, 당일 거래량가중평균가격 상회와 검증된 동일 시간대 누적 상대거래량 1.2 이상을 관찰한다. 충족만으로 자동 매수하지 않는다.","risk_condition_ko":"217,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":188900.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":187165.69178768527,"relative_volume":0.9787056937502409,"spread_bps":5.298013245033113,"day_high":191100.0,"day_low":182100.0,"execution_condition_ko":"042700.KS 최신 정규장 자료에서 212000원 돌파·재지지, 당일 거래량가중평균가격 상회, 검증된 동시간대 상대거래량 1.2배 이상 확인. 1.2배는 제안 기준이지 관측값이 아니다. / 042700.KS 197400~198000원 지지 유지와 이탈 후 회복 여부 확인. 추가 하방 참고 구간은 190800~192200원이며 구조적 손절 기준은 187500원이다.","risk_condition_ko":"197,400 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":172650.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":173340.2603983436,"relative_volume":0.6088470452496068,"spread_bps":5.7920648711265565,"day_high":175400.0,"day_low":171900.0,"execution_condition_ko":"035420.KS의 실제 거래 일정과 신선한 정규장 자료를 확보하고 181,800원·183,300원의 회복 및 재확인, 동일 거래일 거래량가중평균가 지지와 시간대 보정 상대거래량을 점검한다. / 185,000원 상회 종가, 갱신된 20거래일 평균 대비 1.2배 이상의 하루 거래량, 다음 실제 거래일의 지지를 관찰한다. 통과하더라도 매수 경제성과 별도 승인 여부를 다시 판단한다.","risk_condition_ko":"177,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":122800.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":121178.91431972169,"relative_volume":0.6459537316366657,"spread_bps":8.146639511201629,"day_high":126700.0,"day_low":116000.0,"execution_condition_ko":"거래소 달력·거래 가능 여부·현재 호가 시각·정규장 5분봉 집계와 기존 매도 실행 내역을 먼저 확인한다. 오래된 자료의 가격·거래량 불일치를 해소한다. / 136000–136500원 회복과 재시험 성공을 관찰하되 자동 매수로 연결하지 않는다.","risk_condition_ko":"127,000 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":61000.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":60764.04470079308,"relative_volume":0.7055977300185042,"spread_bps":16.380016380016382,"day_high":62800.0,"day_low":59600.0,"execution_condition_ko":"058470.KQ 정규장 64000원 및 62800~63100원 지지 확인; 실패 시 60700~61100원 관찰하되 자동 저가매수 금지 / 058470.KQ 67800원과 당일 거래량가중평균가격 회복·재지지는 초기 개선 관찰이며 단독 매수 신호가 아님","risk_condition_ko":"62,800 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":59000.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":58780.36135737045,"relative_volume":0.9832002576739494,"spread_bps":16.963528413910094,"day_high":60000.0,"day_low":57700.0,"execution_condition_ko":"034020.KS의 검증된 정규장에서 63900원 돌파·재지지, 세션 거래량가중평균가격 상회, 동시간대 누적 상대거래량 1.2 이상을 확인한다. 이는 재평가 조건이며 관측된 신호나 매수 지시가 아니다. / 034020.KS의 66600원과 실행일 갱신 10일 지수이동평균 회복, 상대강도지수 30 상회 유지 및 다음 실제 거래일 지지 확인을 확대 판단에 사용한다. 기준일 지수이동평균 67303원은 동적 참고값이다.","risk_condition_ko":"61,050 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":16830.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":16638.286369854584,"relative_volume":0.7753094481817475,"spread_bps":5.943536404160475,"day_high":16870.0,"day_low":16450.0,"execution_condition_ko":"010140.KS 실제 거래일·정규장 운영·거래정지 여부와 타임스탬프가 있는 최신 가격·호가·거래량 확보. / 010140.KS 17170~17270원 지지 후보대 유지 또는 이탈 후 재탈환 실패 확인.","risk_condition_ko":"17,170 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":47550.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":46834.82931224815,"relative_volume":0.5943524646111927,"spread_bps":10.520778537611783,"day_high":48100.0,"day_low":45650.0,"execution_condition_ko":"403870.KQ의 51,900 회복과 52,800~52,900 돌파·재지지를 신선한 정규장 자료로 확인한다. / 55,000~55,300 회복과 거래량 확대가 낮아지는 고점 구조를 개선하는지 확인하고, 첫 유효 저항까지 비용 후 손익비를 다시 계산한다.","risk_condition_ko":"51,881 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":42100.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":41027.01723999954,"relative_volume":0.6506157553664821,"spread_bps":11.869436201780415,"day_high":42500.0,"day_low":39275.0,"execution_condition_ko":"43,050~43,250에서 실제 방어·회복을 관찰하되 가격 접촉만으로 매수하지 않는다. / 45,700~46,400 반등 이후의 회복 실패를 추가 감축 신호로 감시한다. 현재 가격이 구간 아래라는 사실만으로 새 실패 신호를 선언하지 않는다.","risk_condition_ko":"43,050 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":188700.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":191518.99703061246,"relative_volume":1.0798623324179188,"spread_bps":5.3008216273522395,"day_high":194600.0,"day_low":188600.0,"execution_condition_ko":"위험 대응 조건: 189,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"189,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"064400.KS","display_name":"LG CNS","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":72800.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":72749.82455608576,"relative_volume":1.3651801831578296,"spread_bps":13.745704467353953,"day_high":73700.0,"day_low":71200.0,"execution_condition_ko":"실제 거래일·정규장·거래정지 상태·최신 체결 시각을 먼저 확인한다. 현재 보유 유지 판단을 당일 지지 확인으로 오해하지 않는다. / 71000~71600원 지지와 71600원 회복 또는 72800원 돌파·재시험을 관찰한다. 새로운 구조적 손절과 현실적인 첫 저항 기준의 비용 후 보상/위험이 부족하면 거래를 건너뛴다.","risk_condition_ko":"71,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"018260.KS","display_name":"삼성SDS","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":214500.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":210779.57810559316,"relative_volume":2.264662162590671,"spread_bps":23.33722287047841,"day_high":216000.0,"day_low":200000.0,"execution_condition_ko":"202656원 단기 평균선과 203901원 거래량가중이동평균의 최신 값을 재계산하고 회복 여부를 확인한다. 203901원은 장중 거래량가중평균가격이 아니다. / 205500원 돌파·재지지, 장중 거래량가중평균가격 상회, 과거 동일 시간대 대비 상대거래량 1.2 이상을 확인한다. 위험 축소 사유와 비용 차감 보상·위험까지 개선되어야 매수 계획을 새로 수립한다.","risk_condition_ko":"194,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"014950.KQ","display_name":"014950","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":7330.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":7668.141735653574,"relative_volume":0.635973784105667,"spread_bps":40.84411164057182,"day_high":8190.0,"day_low":7060.0,"execution_condition_ko":"014950.KQ의 기준 시계는 2026-10-22T06:12:43.986537+09:00이다. 10:30 한국시간은 최초 시범진입 검토시각이지 만료나 자동 활성화 시각이 아니다. 정규장 운영일·휴장·조기폐장·거래정지·시장경보를 별도로 확인한다. 검증된 만료가 없어 주문 활성화나 다음 세션 이월을 선언하지 않는다. / 014950.KQ의 신선한 호가·스프레드·실제 5분봉·세션 거래량가중평균가격·동일시간대 상대거래량을 확보한다. 전일 거래량 2.41배를 당일 상대거래량으로 대체하지 않는다.","risk_condition_ko":"7,977 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"373220.KS","display_name":"LG에너지솔루션","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":383000.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":381764.44580938254,"relative_volume":0.736739603460209,"spread_bps":13.04631441617743,"day_high":387500.0,"day_low":373500.0,"execution_condition_ko":"373220.KS의 원공시 영향·최신 재무여력·보유 집중도·거래 가능 상태를 먼저 확인한다. 중립·보수 분석가의 의견대로 잔여 노출 점검과 재진입 준비를 병행한다. / 373220.KS의 402500~405700원 지지 회복 후 검증된 연속 5분봉 두 개의 유지, 당일 거래량가중평균가격 상회, 동일 경과시간 상대거래량 1.2 이상을 관찰한다. 모두 제안 필터이며 관측된 신호가 아니다.","risk_condition_ko":"402,500 이하 하락, 종가 확인 후 (확정 종가 하회와 일봉 거래량 증가를 함께 확인) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010950.KS","display_name":"S-Oil","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":130900.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":130832.26734790874,"relative_volume":1.3239166573773498,"spread_bps":7.636502481863307,"day_high":137000.0,"day_low":128600.0,"execution_condition_ko":"010950.KS의 거래일과 거래 상태를 확인하고 일관된 최신 정규장 호가·봉·당일 거래량가중평균가격·동일 시간대 거래량 기준을 확보한다. / 142200–144000의 회복과 재시험 지지를 관찰한다. 단순 접촉은 매수 신호가 아니다. 137800의 미회복 이탈은 손절 전환 조건이다.","risk_condition_ko":"151,135 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"396300.KQ","display_name":"396300","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":9230.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":9437.966435997887,"relative_volume":0.523619791768092,"spread_bps":10.840108401084011,"day_high":10060.0,"day_low":8940.0,"execution_condition_ko":"위험 대응 조건: 11,250 이상 도달, 장중 확인 시 이익실현성 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"11,250 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000100.KS","display_name":"000100","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":84900.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":84984.72789837497,"relative_volume":1.3517796911166418,"spread_bps":11.785503830288745,"day_high":86300.0,"day_low":83200.0,"execution_condition_ko":"위험 대응 조건: 88,500 이상 도달, 2개 봉 확인 후 이익실현성 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"88,500 이상 도달, 2개 봉 확인 후 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"131290.KQ","display_name":"티에스이","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":251500.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":245128.18870837573,"relative_volume":0.5580572806571756,"spread_bps":19.860973187686195,"day_high":253500.0,"day_low":235000.0,"execution_condition_ko":"위험 대응 조건: 258,000 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"258,000 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":128700.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":130891.73785822465,"relative_volume":0.4800979181208528,"spread_bps":23.33722287047841,"day_high":134000.0,"day_low":128400.0,"execution_condition_ko":"위험 대응 조건: 134,600 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"134,600 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":136900.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":137065.60496641076,"relative_volume":0.5523802619936888,"spread_bps":14.619883040935672,"day_high":140200.0,"day_low":135300.0,"execution_condition_ko":"위험 대응 조건: 160,900 이상 도달, 2개 봉 확인 후 리스크 축소 · 추가 조건 확인 필요: 제공된 분석의 159,600–160,900원 저항 구간에서 거부가 확인되면 초기 축소의 미집행분에 활용한다. 필수 매도 가격이나 이익 실현 목표가 아니며, 해당 가격을 기다리느라 축소를 미루지 않는다. (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"160,900 이상 도달, 2개 봉 확인 후 리스크 축소 · 추가 조건 확인 필요: 제공된 분석의 159,600–160,900원 저항 구간에서 거부가 확인되면 초기 축소의 미집행분에 활용한다. 필수 매도 가격이나 이익 실현 목표가 아니며, 해당 가격을 기다리느라 축소를 미루지 않는다.","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"018880.KS","display_name":"018880","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":3680.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":3691.267665356126,"relative_volume":0.38146455446601046,"spread_bps":13.596193065941536,"day_high":3760.0,"day_low":3605.0,"execution_condition_ko":"위험 대응 조건: 3,775 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"3,775 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"079650.KQ","display_name":"079650","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":7410.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":7194.429756495724,"relative_volume":0.5143017206512113,"spread_bps":13.50438892640108,"day_high":7500.0,"day_low":6700.0,"execution_condition_ko":"위험 대응 조건: 7,320 이하 하락, 2개 봉 확인 후 (실제 거래가 있는 연속 두 개의 5분봉 종가가 7320 미만이고 회복하지 못할 때) 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"7,320 이하 하락, 2개 봉 확인 후 (실제 거래가 있는 연속 두 개의 5분봉 종가가 7320 미만이고 회복하지 못할 때) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"003230.KS","display_name":"003230","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1224000.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":1230446.3321162376,"relative_volume":1.0341636626363546,"spread_bps":8.173273395995096,"day_high":1252000.0,"day_low":1215000.0,"execution_condition_ko":"위험 대응 조건: 1,216,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"1,216,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"011200.KS","display_name":"011200","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":22500.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":22635.76248578369,"relative_volume":0.5015149637295553,"spread_bps":44.34589800443459,"day_high":22950.0,"day_low":22100.0,"execution_condition_ko":"위험 대응 조건: 22,850 이하 하락, 종가 확인 후 (방어적 매도에는 거래량 확인을 필수로 요구하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"22,850 이하 하락, 종가 확인 후 (방어적 매도에는 거래량 확인을 필수로 요구하지 않는다.) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":194500.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":193219.4307373839,"relative_volume":0.8850693561339549,"spread_bps":5.140066820868672,"day_high":195300.0,"day_low":190400.0,"execution_condition_ko":"위험 대응 조건: 195,100 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"195,100 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":486500.0,"market_data_asof":"2026-10-23T14:30:00+09:00","session_vwap":489033.6174493091,"relative_volume":1.1810582252661588,"spread_bps":10.272213662044171,"day_high":509000.0,"day_low":475000.0,"execution_condition_ko":"위험 대응 조건: 526,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"526,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-23T14:30:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-23T14:32:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
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
