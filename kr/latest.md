# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-15T18:15:35.540455+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261015T143355_local-scheduler-kr-overlay_only",
  "producer_finished_at": "2026-10-15T14:36:05.747827+09:00",
  "analysis_run_id": "20261015T090358_local-scheduler-kr-full",
  "analysis_completed_at": "2026-10-15T09:15:38.399670+09:00",
  "analysis_trade_date_oldest": "2026-10-14",
  "analysis_trade_date_latest": "2026-10-14",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-15T14:34:00+09:00",
  "market_data_latest_at": "2026-10-15T14:34:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-15T14:36:01.058188+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-15T14:36:01.058188+09:00",
    "run_started_at": "2026-10-15T14:33:55.040397+09:00",
    "run_finished_at": "2026-10-15T14:36:05.747827+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 8346470,
    "total_unrealized_pnl_krw": -6597766,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 9323122
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1254000,
      "market_value_krw": 2508000,
      "unrealized_pnl_krw": -2927000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 206250,
      "market_value_krw": 2062500,
      "unrealized_pnl_krw": -1261351
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 293500,
      "market_value_krw": 1467500,
      "unrealized_pnl_krw": -607143
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 152900,
      "market_value_krw": 611600,
      "unrealized_pnl_krw": -363400
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 480000,
      "market_value_krw": 480000,
      "unrealized_pnl_krw": -673000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 18090,
      "market_value_krw": 325620,
      "unrealized_pnl_krw": -242695
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 66900,
      "market_value_krw": 200700,
      "unrealized_pnl_krw": -99300
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 191900,
      "market_value_krw": 191900,
      "unrealized_pnl_krw": -182267
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 172400,
      "market_value_krw": 172400,
      "unrealized_pnl_krw": -109934
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 126300,
      "market_value_krw": 126300,
      "unrealized_pnl_krw": -46000
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
      "current_price_krw": 62400,
      "market_value_krw": 62400,
      "unrealized_pnl_krw": -50531
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 48950,
      "market_value_krw": 48950,
      "unrealized_pnl_krw": -5550
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":44250.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":45538.16013517053,"relative_volume":0.8820129298579504,"spread_bps":22.57336343115124,"day_high":47650.0,"day_low":44250.0,"execution_condition_ko":"위험 대응 조건: 49,800 이하 하락, 장중 확인 시 손절 조건 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"49,800 이하 하락, 장중 확인 시 손절 조건","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":206250.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":212524.17335262668,"relative_volume":1.6184551041656914,"spread_bps":24.242424242424242,"day_high":221500.0,"day_low":206000.0,"execution_condition_ko":"위험 대응 조건: 246,000 이하 하락, 장중 확인 시 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"246,000 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"지금 실행 검토 가능","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":127000.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":128541.80740885202,"relative_volume":1.019261646224186,"spread_bps":15.760441292356187,"day_high":138200.0,"day_low":121900.0,"execution_condition_ko":"위험 대응 조건: 145,000 이상 도달, 장중 확인 시 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"145,000 이상 도달, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":293500.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":290411.21314485726,"relative_volume":1.1885080299433644,"spread_bps":17.050298380221655,"day_high":301000.0,"day_low":278500.0,"execution_condition_ko":"278470.KS 실제 정규장·거래 가능 여부와 최신 체결·호가·거래량·세션 거래량가중평균가격 확보 / 278470.KS 300,500원 위 5분봉 종가·재시험 지지·돌파 거래량 증가와 재시험 매도 거래량 감소 확인","risk_condition_ko":"279,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":18075.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":18207.68019505975,"relative_volume":1.0195994705178346,"spread_bps":5.532503457814661,"day_high":18570.0,"day_low":17980.0,"execution_condition_ko":"18,410 돌파 후 완성된 5분봉 두 개의 재지지, 최신 당일 거래량가중평균가격 상회, 동일 시간대 거래량과 매수 체결 개선을 함께 확인한다. 이는 매수 승인이 아닌 재평가 조건이다. / 18,950 및 19,197.70~19,347.69 저항 회복을 관찰하고 19,570과 최신 50일 평균 유지로 확인 범위를 확장한다.","risk_condition_ko":"18,950 이상 도달, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1254000.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":1278131.802259237,"relative_volume":1.4796876664061551,"spread_bps":7.9776625448743514,"day_high":1332000.0,"day_low":1251000.0,"execution_condition_ko":"1,400,000~1,402,000 유지와 저점 갱신 중단을 관찰한다. 확정된 바닥으로 간주하지 않는다. / 갱신된 200일선과 1,458,000 회복·되돌림 지지 이후 1,497,000 위 종가 및 다음 거래일 지지를 확인한다.","risk_condition_ko":"1,400,000 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":152700.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":157938.66784440633,"relative_volume":1.5959277920629464,"spread_bps":6.546644844517186,"day_high":165600.0,"day_low":152500.0,"execution_condition_ko":"010120.KS 173100~174100 지지 유지, 179900~182500 초기 회복과 183600~184200 재시험을 구분해 관찰한다. 관찰가격 도달만으로 주문하지 않는다. / 010120.KS 193800~195500 및 200000~200900에서 반등 지속 또는 실패를 확인한다. 저항 도달 자체는 자동 이익 실현 신호가 아니다.","risk_condition_ko":"173,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":480500.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":493200.5165802344,"relative_volume":1.8399097208969812,"spread_bps":10.41124414367517,"day_high":523000.0,"day_low":479000.0,"execution_condition_ko":"267260.KS 최신 체결시각·호가·거래정지 및 실제 정규장 운영 여부 확인 / 531000원 유지, 저점 상승 및 상대강도지수 30 회복 관찰; 과매도만으로 바닥 판단 금지","risk_condition_ko":"531,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":66800.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":69350.54021883142,"relative_volume":0.8649979830219396,"spread_bps":14.958863126402393,"day_high":72700.0,"day_low":66700.0,"execution_condition_ko":"058470.KQ 최신 정규장 자료에서 75,000~75,300원 지지와 위험예산 준수 여부 확인. / 058470.KQ 79,700원 회복 및 79,200~79,700원 재시험 후 가까운 저항과 비용을 반영한 손익비 재산정. 목표 상향이나 부당하게 좁은 손절로 기준을 맞추지 않는다.","risk_condition_ko":"75,000 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":192400.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":196806.17575222548,"relative_volume":1.8395039444411487,"spread_bps":5.198856251624642,"day_high":205000.0,"day_low":191300.0,"execution_condition_ko":"042700.KS의 213500~216000원 방어와 저점 상승을 최신 정상 거래에서 확인한다. / 228000~231500원 회복·재시험 지지, 실제 장중 거래량가중평균가격 상회, 동일 시간대 상대거래량 1.2배 이상을 확인한다. 전일 일거래량 비율 1.14는 당일 상대거래량이 아니다.","risk_condition_ko":"228,178 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":172500.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":173736.12517011643,"relative_volume":1.2267741315719285,"spread_bps":5.798782255726297,"day_high":176100.0,"day_low":172000.0,"execution_condition_ko":"035420.KS 거래 가능 상태와 최신 정규장 5분봉·체결량·호가·세션 거래량가중평균가격을 먼저 확보한다. / 177,800~178,000원 지지 방어와 173,200원 재시험을 구분해 관찰한다.","risk_condition_ko":"177,800 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":48950.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":51031.552161507636,"relative_volume":1.0527624123344212,"spread_bps":10.21972406745018,"day_high":54100.0,"day_low":48800.0,"execution_condition_ko":"403870.KQ 56,000~56,100원 방어 후 57,400원 재돌파·재지지, 거래량가중평균가격 상회 및 동일 시간대 상대거래량 1.2 이상 / 403870.KQ 61,000~61,600원 회복, 62,700원 위 종가 및 다음 실제 거래일 재지지","risk_condition_ko":"56,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":62600.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":63914.62336098502,"relative_volume":1.1479554788426753,"spread_bps":15.987210231814547,"day_high":66300.0,"day_low":62500.0,"execution_condition_ko":"034020.KS의 최신 정규장 시세로 68,300원 및 67,300원 방어 확인 / 70,500~70,700원 회복·재시험과 71,200~71,500원 저항 통과 확인; 자동 매수 금지","risk_condition_ko":"67,300 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":539000.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":550324.0219549572,"relative_volume":1.8895119426038256,"spread_bps":18.535681186283597,"day_high":573000.0,"day_low":536000.0,"execution_condition_ko":"위험 대응 조건: 559,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"559,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"105560.KS","display_name":"105560","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":156500.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":157191.44295655508,"relative_volume":1.2287131909547058,"spread_bps":6.391818472355385,"day_high":159000.0,"day_low":154800.0,"execution_condition_ko":"판단 기준시각은 2026-10-15T07:28:31.810489+09:00이며 일봉 기준일은 2026-10-14다. 실제 거래일·휴장·조기종료·거래정지·최신 체결시각은 별도 확인해야 한다. / 10:30은 확인된 정규장의 최소 시험 진입 재평가 시각이지 활성화 또는 만료시각이 아니다. 유효한 진입 만료시각은 제공되지 않았다. 만료를 선언하거나 다음 거래일로 이월하지 않는다.","risk_condition_ko":"158,400 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"095340.KQ","display_name":"ISC","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":144600.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":151923.95196534533,"relative_volume":1.2007301732048539,"spread_bps":13.831258644536653,"day_high":166000.0,"day_low":144400.0,"execution_condition_ko":"판단 시각은 2026-10-15T07:38:40.769998+09:00이고 일별 가격 기준일은 2026-10-14다. 실제 거래일, 정규장 운영, 거래 상태와 시세 신선도는 별도 확인이 필요하다. / 공급된 기술 자료의 종가 174200과 하락률 5.17%를 기준 관찰값으로 사용한다. 뉴스의 하락률 5.50%와의 차이는 미해결이며 지연된 야간 가격으로 현재 조건을 판정하지 않는다.","risk_condition_ko":"170,400 이하 하락, 거래량 조건 확인 후 (매도 거래량 증가와 회복 실패 확인) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"452190.KQ","display_name":"452190","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":4835.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":4934.057989327212,"relative_volume":0.17002312017709026,"spread_bps":30.975735673722248,"day_high":5130.0,"day_low":4820.0,"execution_condition_ko":"452190.KQ의 실제 거래일·정규 세션·거래정지 여부·최신 체결 시각·호가·거래량·거래량가중평균가격을 확인한다. / 5,340 방어와 저점 상승, 5,600 회복을 관찰한다. 5,820~5,860 재지지 이후에도 첫 현실적 저항까지 비용 차감 보상/위험이 2 미만이면 매수하지 않는다.","risk_condition_ko":"5,340 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"088350.KS","display_name":"088350","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":4620.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":4668.506700434186,"relative_volume":0.726533547098695,"spread_bps":10.828370330265296,"day_high":4775.0,"day_low":4595.0,"execution_condition_ko":"판단 시각은 2026-10-15T07:28:21.777020+09:00이며 일별 가격 기준일은 2026-10-14다. 이 시각만으로 개장 여부나 거래 가능성을 판단하지 않는다. 거래일·정규장·거래정지·호가 시각·스프레드·잔량을 별도 확인한다. / 088350.KS의 4680 지지와 갱신된 장기 이동평균 방어, 4810 회복·재시험을 관찰한다. 당일 거래량가중평균가격 상회와 같은 경과 시간 대비 상대거래량 1.2배 이상을 확인한다. 과거 일일 거래량 1.49배는 이를 대신하지 않는다.","risk_condition_ko":"4,680 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"041190.KQ","display_name":"041190","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":4920.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":5083.892787983877,"relative_volume":0.5121987109512851,"spread_bps":10.167768174885612,"day_high":5330.0,"day_low":4905.0,"execution_condition_ko":"041190.KQ의 실제 거래일·정규장 운영, 최신 체결 시각·호가·당일 거래량가중평균가격·동일 시간대 상대거래량을 확인한다. / 5,450~5,515원 방어, 5,660~5,680원 회복, 5,825~5,850원 회복·재지지 순서와 각 단계의 비용 후 보상·위험을 관찰한다.","risk_condition_ko":"5,450 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"066570.KS","display_name":"LG전자","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":167600.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":168781.97233579843,"relative_volume":0.942902151834747,"spread_bps":5.96836765144733,"day_high":171500.0,"day_low":166100.0,"execution_condition_ko":"175,200원 종가 지지, 170,800원 하향 이탈 및 계좌 집중·갭 위험 변화. / 180,350~182,000원 회복·재시험과 184,500~184,700원 저항 소화. 단순 회복은 매수 승인 조건이 아니다.","risk_condition_ko":"175,200 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"069540.KQ","display_name":"069540","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":3885.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":3878.2901584880983,"relative_volume":0.44345076484042695,"spread_bps":12.8783000643915,"day_high":4085.0,"day_low":3740.0,"execution_condition_ko":"판단 기준 시각은 2026-10-15T07:41:02.373761+09:00이며 일봉 기준일은 2026-10-14다. 실제 거래일·세션·거래정지·시장경보·최신 체결 시각은 별도 확인이 필요하다. / 제공 장중 가격의 실제 시각은 2026-10-14 20:00이다. 이를 당일 가격으로 사용하거나 거래량 0·상대거래량 0을 수요 부재로 해석하지 않는다.","risk_condition_ko":"4,035 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":188700.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":188513.23484464115,"relative_volume":1.648228341298288,"spread_bps":5.3008216273522395,"day_high":191000.0,"day_low":184000.0,"execution_condition_ko":"033780.KS 실제 거래일·정규장·거래정지 상태와 시각이 있는 호가·체결·당일 거래량가중평균가격·동시간대 거래량을 확보한다. / 178,600~179,900원 접근에서는 방어 신호를 우선한다. 위험 축소 신호가 해소되고 179,900원 회복이 확인된 뒤에만 눌림 매수를 다시 검토한다.","risk_condition_ko":"179,900 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"지금 실행 검토 가능","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"373220.KS","display_name":"LG에너지솔루션","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":402000.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":403254.38340717496,"relative_volume":1.2667620927368637,"spread_bps":24.87562189054726,"day_high":412000.0,"day_low":396000.0,"execution_condition_ko":"위험 대응 조건: 409,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"409,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":154500.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":157714.17593003088,"relative_volume":1.0798798678529349,"spread_bps":6.474587245063128,"day_high":163000.0,"day_low":153000.0,"execution_condition_ko":"위험 대응 조건: 152,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"152,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"062040.KS","display_name":"062040","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":175200.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":180771.81133879744,"relative_volume":1.5884883527724936,"spread_bps":5.706134094151213,"day_high":197000.0,"day_low":174200.0,"execution_condition_ko":"위험 대응 조건: 206,500 이하 하락, 장중 확인 시 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"206,500 이하 하락, 장중 확인 시 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010950.KS","display_name":"S-Oil","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":157000.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":160297.07809200342,"relative_volume":0.9438945562440243,"spread_bps":6.367398917542184,"day_high":166100.0,"day_low":157000.0,"execution_condition_ko":"위험 대응 조건: 159,700 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"159,700 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"093370.KS","display_name":"093370","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":12050.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":12475.301952570393,"relative_volume":0.5501616814896622,"spread_bps":8.295313148071338,"day_high":13310.0,"day_low":12030.0,"execution_condition_ko":"위험 대응 조건: 13,330 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"13,330 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"018880.KS","display_name":"018880","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":3730.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":3741.5543985644417,"relative_volume":0.829869135907067,"spread_bps":13.41381623071764,"day_high":3840.0,"day_low":3670.0,"execution_condition_ko":"위험 대응 조건: 3,630 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"3,630 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"086790.KS","display_name":"086790","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":121400.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":121225.70684972621,"relative_volume":1.1471449458299354,"spread_bps":8.240626287597857,"day_high":122300.0,"day_low":118300.0,"execution_condition_ko":"위험 대응 조건: 119,400 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"119,400 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005935.KS","display_name":"005935","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":155400.0,"market_data_asof":"2026-10-15T14:34:00+09:00","session_vwap":159934.86772188314,"relative_volume":1.5230088219319757,"spread_bps":6.43707756678468,"day_high":166300.0,"day_low":155200.0,"execution_condition_ko":"위험 대응 조건: 170,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"170,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-15T14:34:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-15T15:04:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-15T14:57:29.701406+09:00",
  "as_of": "2026-10-15T14:34:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
