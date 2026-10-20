# TradingAgents US 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-20T04:35:51.600523+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/us/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261020T031010_pre-report-us-overlay",
  "producer_finished_at": "2026-10-20T03:12:04.918528+09:00",
  "analysis_run_id": "20261019T175010_local-scheduler-us-full",
  "analysis_completed_at": "2026-10-19T20:24:43.799959+09:00",
  "analysis_trade_date_oldest": "2026-10-16",
  "analysis_trade_date_latest": "2026-10-16",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-19T14:11:00-04:00",
  "market_data_latest_at": "2026-10-19T14:11:00-04:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-20T03:11:58.209621+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-20T03:11:58.209621+09:00",
    "run_started_at": "2026-10-20T03:10:10.709999+09:00",
    "run_finished_at": "2026-10-20T03:12:04.918528+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 14,
    "total_purchase_amount_krw": 23688834,
    "total_market_value_krw": 23686717,
    "total_unrealized_pnl_krw": -2117,
    "settled_cash_krw": 0,
    "available_cash_krw": 976652,
    "buying_power_krw": 107553,
    "total_equity_krw": 24770922
  },
  "positions": [
    {
      "ticker": "TSM",
      "name": "TSMC(ADR)",
      "quantity": 12.0,
      "sellable_quantity": 12.0,
      "average_cost_krw": 547256,
      "current_price_krw": 565841,
      "market_value_krw": 6790100,
      "unrealized_pnl_krw": 223026
    },
    {
      "ticker": "RSP",
      "name": "INVESCO S&P 500 EQUAL WEIGHT",
      "quantity": 11.0,
      "sellable_quantity": 11.0,
      "average_cost_krw": 293321,
      "current_price_krw": 286783,
      "market_value_krw": 3154619,
      "unrealized_pnl_krw": -71918
    },
    {
      "ticker": "GOOGL",
      "name": "알파벳 A",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 425445,
      "current_price_krw": 462188,
      "market_value_krw": 2773129,
      "unrealized_pnl_krw": 220458
    },
    {
      "ticker": "NVDA",
      "name": "엔비디아",
      "quantity": 6.0,
      "sellable_quantity": 6.0,
      "average_cost_krw": 268059,
      "current_price_krw": 291864,
      "market_value_krw": 1751187,
      "unrealized_pnl_krw": 142832
    },
    {
      "ticker": "MPWR",
      "name": "모놀리식 파워 시스템",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1885722,
      "current_price_krw": 1687611,
      "market_value_krw": 1687611,
      "unrealized_pnl_krw": -198111
    },
    {
      "ticker": "ETN",
      "name": "이턴 코퍼레이션",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 557629,
      "current_price_krw": 527113,
      "market_value_krw": 1581340,
      "unrealized_pnl_krw": -91549
    },
    {
      "ticker": "GEV",
      "name": "GE베르노바",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1477364,
      "current_price_krw": 1223611,
      "market_value_krw": 1223611,
      "unrealized_pnl_krw": -253753
    },
    {
      "ticker": "SGOV",
      "name": "ISHARES 0-3M TREASURY BOND",
      "quantity": 9.0,
      "sellable_quantity": 9.0,
      "average_cost_krw": 134926,
      "current_price_krw": 135032,
      "market_value_krw": 1215288,
      "unrealized_pnl_krw": 949
    },
    {
      "ticker": "AAPL",
      "name": "애플",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 365687,
      "current_price_krw": 461134,
      "market_value_krw": 922269,
      "unrealized_pnl_krw": 190894
    },
    {
      "ticker": "LLY",
      "name": "일라이 릴리",
      "quantity": 0.436065,
      "sellable_quantity": 0.436065,
      "average_cost_krw": 1424301,
      "current_price_krw": 1679758,
      "market_value_krw": 732483,
      "unrealized_pnl_krw": 111395
    },
    {
      "ticker": "DELL",
      "name": "델 테크놀로지스",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 664763,
      "current_price_krw": 612657,
      "market_value_krw": 612657,
      "unrealized_pnl_krw": -52106
    },
    {
      "ticker": "AVGO",
      "name": "브로드컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 571358,
      "current_price_krw": 450026,
      "market_value_krw": 450026,
      "unrealized_pnl_krw": -121332
    },
    {
      "ticker": "GLDM",
      "name": "SPDR GOLD MINISHARES TRUST",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 136627,
      "current_price_krw": 110130,
      "market_value_krw": 440521,
      "unrealized_pnl_krw": -105987
    },
    {
      "ticker": "AMZN",
      "name": "아마존닷컴",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 348809,
      "current_price_krw": 351876,
      "market_value_krw": 351876,
      "unrealized_pnl_krw": 3067
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"RSP","display_name":"RSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":213.6101,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":213.73793625771953,"relative_volume":0.46894364408251815,"spread_bps":0.46830730325196834,"day_high":214.61,"day_low":213.225,"execution_condition_ko":"실제 정규장 일정·거래 상태·최신 호가·발행 시각을 확인한다. 조건부 주문은 시차가 포함된 유효기한과 포트폴리오 입력값을 기록한 뒤에만 활성화한다. / 212.80~213.40에서 단순 접촉이 아닌 지지 회복, 완료된 5분 봉 2개, 당일 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상을 관찰한다.","risk_condition_ko":"210.95 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AAPL","display_name":"Apple","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":343.555,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":342.98140410624205,"relative_volume":0.5352986740546025,"spread_bps":0.5831923951706366,"day_high":346.0,"day_low":340.115,"execution_condition_ko":"실제 세션 달력, 거래정지 여부, 최신 정규장 호가·완료된 5분봉·거래량가중평균가격을 확보한다. / 348.15 돌파·재시험 지지와 검증된 동시간대 상대거래량 1.2 이상을 관찰한다. 충족하더라도 숫자 손절·목표·비용 후 손익비와 계좌 위험을 별도 심사한다.","risk_condition_ko":"337.67 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMZN","display_name":"Amazon","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":262.04,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":260.5526873781833,"relative_volume":0.981157089966489,"spread_bps":1.5246226558934464,"day_high":263.44,"day_low":255.22,"execution_condition_ko":"최신 판단 시각은 2026-10-19T05:05:50.485035-04:00이다. 거래일 확인을 전제로 한 최초 검토 후보 시각 2026-10-19T10:30:00-04:00보다 이르며, 이 시각은 만료시각이 아니다. 거래 캘린더와 정규장 일정은 아직 검증되지 않았다. / 253.85~255.60 회복과 257.08 지지를 관찰하고, 첫 저항 259.65~260.14 및 상단 저항 262.80~263.70까지 비용 후 보상위험비를 다시 계산한다. 현재 자료에는 263.70 위의 근거 있는 목표가 없다.","risk_condition_ko":"248.6 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GOOGL","display_name":"Alphabet","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":344.34,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":344.51831424624277,"relative_volume":0.3431761213386534,"spread_bps":1.7426662794075596,"day_high":346.58,"day_low":341.85,"execution_condition_ko":"339.08–340.56 부근의 실제 지지 여부를 새 정규장 자료로 확인한다. 과거 종가가 200일 평균보다 0.03 높았다는 사실이나 지지선 접촉만으로 방어 성공을 인정하지 않는다. / 339.08 미만 종가는 전술적 50% 감축, 335.51 미만 종가는 잔여 전술적 보유분 손절의 재확인 신호다. 실제 집중도 또는 계획손실 한도 초과는 별도의 즉시 위험 축소 사유다.","risk_condition_ko":"339.08 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SGOV","display_name":"iShares 0-3 Month Treasury Bond ETF","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":100.59,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":100.59399376544847,"relative_volume":0.8455300046126647,"spread_bps":0.9940851931001445,"day_high":100.6,"day_low":100.59,"execution_condition_ko":"중립 분석가의 제안대로 핵심 현금운용 경제성 평가와 전술적 돌파 거래를 분리한다. 경제성이 확인돼도 현재 감시 규칙이 자동 매수 승인으로 바뀌지는 않는다. / 보수적 분석가가 지적한 200일 평균 99.1467과 100.53595의 차이, 기준일 및 조정 여부를 해소한다. 불일치한 이동평균을 매수 근거로 사용하지 않는다.","risk_condition_ko":"100.57 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MPWR","display_name":"Monolithic Power Systems","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1256.84,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":1262.2682150458036,"relative_volume":0.5262545442904246,"spread_bps":19.26004659173162,"day_high":1283.59,"day_low":1236.255,"execution_condition_ko":"1260.24 돌파·재시험 지지는 재심사 신호일 뿐이다. 첫 저항까지 순보상/위험이 부족하면 매수하지 않는다. / 1300.17~1306.08 회복·유지 시 갱신된 지지와 다음 저항으로 손익비를 새로 계산한다. 더 높은 진입가 자체가 유리한 것은 아니다.","risk_condition_ko":"1,195 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GEV","display_name":"GE Vernova","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":911.325,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":921.5556725441354,"relative_volume":0.44228127500464903,"spread_bps":8.795751651951608,"day_high":939.0,"day_low":908.545,"execution_condition_ko":"실제 정규장 일정·거래정지 여부와 시각이 확인된 최신 호가·분봉·세션 거래량가중평균가·동시간대 상대거래량을 확보한다. 05:05의 지연 장전 가격 935.60은 회복 증거가 아니다. / 933.30 재시험 지지와 942~951 저항 돌파를 관찰하되 비용 차감 후 최소 보상 대비 위험 조건이 없으면 매수하지 않는다.","risk_condition_ko":"933.3 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TSM","display_name":"Taiwan Semiconductor Manufacturing","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":421.5,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":421.9480765844349,"relative_volume":0.5103172384336011,"spread_bps":2.379875770485322,"day_high":427.1599,"day_low":415.5001,"execution_condition_ko":"최신 판단시각은 2026-10-19T06:01:19.228848-04:00이다. 완료된 일별 가격은 2026-10-16 기준이며 신선한 정규장 진입 조건은 확인되지 않았다. 시계만으로 거래일·세션·호가 신선도를 확정하지 않는다. / 매도 위험 해소 후 423.66 회복·재시험, 정규장 거래량가중평균가격 지지와 동일 시각 기준 상대거래량 1.2 이상을 확인한다. 이 수치는 제안된 기준이며 관측값이 아니다.","risk_condition_ko":"407.13 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"DELL","display_name":"Dell Technologies","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":456.4,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":463.5965250472763,"relative_volume":0.4158468535478755,"spread_bps":15.80125532194993,"day_high":471.765,"day_low":455.06,"execution_condition_ko":"DELL 실제 거래일 운영과 거래 가능 상태, 최신 정규장 가격·거래량가중평균가격·동시간대 상대거래량을 확인한다. / 450.00 유지 여부와 473.50~482.00 반등 실패를 구분하고 이미 집행한 축소 물량을 대조한다.","risk_condition_ko":"513.26 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ETN","display_name":"Eaton","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":392.595,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":394.21615037639987,"relative_volume":0.8301582381282198,"spread_bps":9.968178507073224,"day_high":400.0,"day_low":390.72,"execution_condition_ko":"정규장에서 386.01–390.05 방어, 392.76 회복, 높아지는 5분 봉 저점, 당일 거래량가중평균가 유지와 동시간대 상대거래량 1.2 이상을 관찰한다. / 403.73 위 정규장 종가와 다음으로 확인된 거래일의 재시험 성공은 매수 재평가 계기이지 자동 주문이 아니다. 408.85–416.48 및 421.09–423.72 저항을 포함해 남은 보상 대비 위험을 다시 산정한다.","risk_condition_ko":"392.76 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AVGO","display_name":"Broadcom","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":335.105,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":337.0595856478595,"relative_volume":0.3959976016383841,"spread_bps":2.093896292307719,"day_high":340.2,"day_low":333.82,"execution_condition_ko":"공식 재무제표의 통화·단위·기간·주식 기준·예탁증서 전환 적용 여부를 확인하고 현금흐름·매출총이익 불일치를 대사한다. / 발표시각이 확인되는 공식 전망·경영진 설명·다음 실적 발표일을 확보한다.","risk_condition_ko":"334.61 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"LLY","display_name":"Eli Lilly","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1251.4,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":1249.8671753933315,"relative_volume":0.2597030259426895,"spread_bps":6.805253655823388,"day_high":1259.75,"day_low":1240.23,"execution_condition_ko":"검증된 정규장에서 미국 동부시간 10:30 이후 1230.66 위의 지지 봉 2개, 거래량가중평균가격 회복, 시간대 조정 상대거래량 1.2 이상을 확인한다. 첫 저항까지 비용 차감 후 보상·위험비 2 이상이어야 하며 1245.29 접촉만으로 매수하지 않는다. / 1251.25와 1257.03 회복은 구조 개선 신호지만 기존 보상·위험비 한도를 초과하는 매수를 정당화하지 않는다.","risk_condition_ko":"1,275.88 이상 도달, 2개 봉 확인 후 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"GLDM","display_name":"SPDR Gold MiniShares Trust","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":82.0465,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":82.022603702265,"relative_volume":0.28613711895997956,"spread_bps":1.219586560156731,"day_high":82.41,"day_low":81.815,"execution_condition_ko":"판단 기준 시각은 2026-10-19T05:21:44.319963-04:00이다. 거래일·휴장·조기폐장·거래정지·호가 시각과 유동성을 별도 확인한다. 지연된 05:05 장전 자료는 정규장 실행 근거가 아니다. / 미국 동부시간 10:30은 최초 재평가 가능 시각이지 만료가 아니다. 검증된 만료 시각이 없으며 임의로 다음 거래일로 이월하지 않는다.","risk_condition_ko":"80.57 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"NVDA","display_name":"NVIDIA","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":217.4016,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":217.5422711719334,"relative_volume":0.488107657364891,"spread_bps":0.9218289085550441,"day_high":219.62,"day_low":214.7,"execution_condition_ko":"원문 재무제표에서 표시 통화·단위·비교 기간·주식 및 주당이익 기준·예탁증서 적용 여부와 전환비율·발표 시각을 확인하고 연구 기준시점 안의 자료인지 점검한다. / 보수적 분석이 제시한 매출채권 증가율 약 54.9%와 현금 전환율 약 40.3%는 미검증 경고 지표로 조사한다. 회수기간·채권 연령·신용 조건과 투자 관련 이익 영향을 확인하기 전 회수 실패나 지급불능으로 해석하지 않는다.","risk_condition_ko":"212.85 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"HOLD","strategy_ko":"보유 유지","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"SHEL","display_name":"SHEL","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":105.505,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":105.4643674538594,"relative_volume":0.397138678845542,"spread_bps":2.841850992279746,"day_high":106.11,"day_low":104.965,"execution_condition_ko":"106.68 돌파 후 완료된 15분 봉 2개에 걸친 재시험 지지, 정규장 거래량가중평균가격 상회, 동일 시각 상대거래량 1.2 이상을 확인한다. 가격·거래량 확인만으로는 부족하며 독립적으로 검증된 순기대손익비가 최소 2배여야 한다. / 104.70–105.17 시험 후 105.17 회복과 높아지는 장중 저점을 확인한다. 104.70 아래 지속 거래가 없어야 하며 거래량가중평균가격과 거래 참여도 확인도 필요하다.","risk_condition_ko":"104.7 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"XOM","display_name":"XOM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":178.885,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":178.11047035416357,"relative_volume":0.3346713906511084,"spread_bps":2.2393908856786497,"day_high":179.3,"day_low":177.2337,"execution_condition_ko":"거래일 달력·정규장 여부·거래정지·최신 호가 시각·스프레드·정규장 거래량가중평균가격을 확인한다. / 173.60–175.15 지지 형성과 174.50 회복을 감시하되, 중립 분석가가 지적한 175.15 경고 해소 여부를 별도로 검증한다.","risk_condition_ko":"173.6 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MA","display_name":"MA","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":615.53,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":614.5599295286862,"relative_volume":0.37977290802755176,"spread_bps":4.063752143629255,"day_high":618.0,"day_low":608.5901,"execution_condition_ko":"실제 MA 보유량과 상관 노출부터 점검한다. 집중도·계획 손실·별도 갭 위험 한도 위반이 확인되면 가격 지지 여부와 무관하게 감축한다. / 거래일과 정규장 상태, 최신 호가 차이 0.10% 이하, 거래량가중평균가격 및 동시간대 상대거래량 1.2 이상 여부를 확인한다.","risk_condition_ko":"603.24 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"V","display_name":"V","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":403.215,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":402.11241312136474,"relative_volume":0.2919553364667156,"spread_bps":0.744278360106003,"day_high":403.792,"day_low":398.01,"execution_condition_ko":"404.74 상회 시 정규장 5분봉 종가, 지지 재시험, 당일 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상을 확인한다. 이후 보호청산가·검증된 목표·비용 차감 후 2:1 이상 기대손익비를 다시 판단한다. / 399.73–400.00 또는 395.26–397.19에서는 매도 압력 감소와 지지 회복을 요구한다. 가격 접촉만으로 매수하지 않는다.","risk_condition_ko":"395.26 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CVX","display_name":"CVX","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":224.92,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":223.8223743306795,"relative_volume":0.49174213015935087,"spread_bps":2.224347710034538,"day_high":225.67,"day_low":223.12,"execution_condition_ko":"거래일정·장 상태·거래정지 여부·최신 정규장 호가와 봉 자료·다음 실적발표 일정을 확인한다. 제공된 미국 동부시간 06:15 지연 장전 관측은 진입 확인으로 사용하지 않는다. / 미국 동부시간 10:30 이후 검증된 정규장에서 225.42 상단을 재검증하고 연속 5분봉 두 개의 상회 종가, 225.31–225.42 재시험 성공, 실시간 거래량가중평균가격 지지와 동시간대 상대거래량 1.2 이상을 확인한다.","risk_condition_ko":"220.41 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"AMT","display_name":"AMT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":182.0,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":182.8302766786802,"relative_volume":0.25155983799927495,"spread_bps":3.294711987259011,"day_high":186.0,"day_low":181.65,"execution_condition_ko":"제공된 2026-10-19T07:03:52.424482-04:00 기준 미 동부시간 10:30은 아직 도래하지 않은 최초 진입 검토 시각이지 만료 시각이 아니다. 거래일·휴장·조기종료·실제 장 상태는 별도 확인해야 한다. 주문 만료를 새로 만들거나 다음 거래일로 이월하지 않는다. / 호가·호가 차이·정규장 거래량가중평균가격·동시간대 상대거래량을 갱신한다. 상대거래량 1.2 이상은 제안된 기준이며 관찰값이 아니다.","risk_condition_ko":"176.42 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"COST","display_name":"Costco Wholesale","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":995.63,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":991.672835548814,"relative_volume":0.4467325184782839,"spread_bps":1.5043249341866962,"day_high":997.43,"day_low":985.01,"execution_condition_ko":"COST의 거래 일정·거래정지·최신 시세·정규장 5분봉·거래량가중평균가격·동일 시간대 상대거래량을 확보한다. / 977.24-982.00 시험 뒤 982.00 이상이면서 장중 거래량가중평균가격 위인 5분봉 종가 두 개를 확인한다. 순보상·위험비가 부족하면 계속 대기한다.","risk_condition_ko":"977.24 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PG","display_name":"PG","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":158.23,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":157.85743674424052,"relative_volume":0.37912047271027294,"spread_bps":1.2649421288982499,"day_high":158.42,"day_low":157.01,"execution_condition_ko":"156.53–157.56 지지와 회복을 관찰한다. 단순 접촉은 매수 신호가 아니며 이탈 확인은 위험축소 신호다. / 153.20–154.75에서 154.50 부근 반등을 감시한다. 151.90 손절과 159.98 저항 기준 순손익비 2.0 이상이 실제로 가능한지 확인한다.","risk_condition_ko":"156.53 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ABBV","display_name":"ABBV","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":284.335,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":284.8425139444785,"relative_volume":0.2856853739609481,"spread_bps":3.5156799324997445,"day_high":287.9299,"day_low":282.7,"execution_condition_ko":"281.75~283.00 시험 후 완성된 정규장 5분봉 2개가 283.00 이상에서 마감하고 당일 거래량가중평균가격을 유지하는지 확인한다. / 291.40 돌파·재지지, 동일 경과시간 대비 상대거래량 1.2 이상, 호가 간격 0.25% 이하와 근거 있는 상단 목표를 확인한다.","risk_condition_ko":"288.28 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"PM","display_name":"PM","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":202.935,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":202.37194743008507,"relative_volume":0.26839069584172126,"spread_bps":4.442141112016159,"day_high":203.2,"day_low":201.435,"execution_condition_ko":"201.69 방어와 199.30~200.50 시험 후 200.50 회복을 구분한다. / 205.79~205.99 저항과 다음 관측 저항 210.45를 확인한다. 205.99에서 210.45까지 차이 4.46만으로 매수 손익비가 충족되지는 않는다.","risk_condition_ko":"199.26 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MDT","display_name":"MDT","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":93.06,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":93.30320222146474,"relative_volume":0.47098158498886905,"spread_bps":1.0730189387848186,"day_high":94.8,"day_low":92.67,"execution_condition_ko":"93.96–94.26 시험 후 94.26 회복을 관찰하되, 정규장 5분봉 두 개와 거래량가중평균가격 상회가 확인되어도 손익비를 별도로 심사한다. / 91.79–93.01 시험 후 93.01 회복을 관찰한다. 93.01 진입·91.79 손절·95.45 저항은 비용 전 손익비가 정확히 2 대 1이므로 비용 차감 후 기준에는 미달한다.","risk_condition_ko":"91.79 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"MSFT","display_name":"Microsoft","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":534.02,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":532.9310772099685,"relative_volume":0.2078274262564021,"spread_bps":0.936812028665596,"day_high":535.5684,"day_low":528.4797,"execution_condition_ko":"실제 거래일·휴장 및 조기폐장 일정, 거래정지 여부, 호가와 가격의 최신성, 정규장 분봉 및 동시간대 상대거래량을 확인한다. 2026-10-19 06:35 미국 동부시간의 지연된 장전 자료는 진입 확인 자료가 아니다. / 제공된 기준시각 2026-10-19T06:51:27.735707-04:00은 미국 동부시간 10:30 검토 개시 전이다. 개시 시각은 만료가 아니며 현재 세션 상태나 조건 충족을 증명하지 않는다. 만료를 임의로 다음 거래일로 넘기지 않는다.","risk_condition_ko":"524.43 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"ITUB","display_name":"ITUB","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":9.445,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":9.458157043016794,"relative_volume":0.7646674802692438,"spread_bps":10.598834128245668,"day_high":9.61,"day_low":9.38,"execution_condition_ko":"거래 달력·거래정지·호가 시각을 확인하고 완료된 5분봉, 당일 거래량가중평균가격, 같은 시각 기준 비교 거래량을 확보한다. / 9.39 유지, 9.60 위에서 완료된 5분봉 2개, 9.55–9.60 재시험 성공, 당일 거래량가중평균가격 상회, 상대거래량 1.2 이상을 관찰한다. 기술 조건 충족만으로 매수하지 않는다.","risk_condition_ko":"9.39 이하 하락, 거래량 조건 확인 후 (새 정규장 이탈, 회복 실패와 매도 거래량 확대를 함께 확인) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"TXN","display_name":"Texas Instruments","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":276.2,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":276.00356597342653,"relative_volume":0.4309078610864887,"spread_bps":10.911074740862386,"day_high":283.12,"day_low":272.0701,"execution_condition_ko":"273.59~274.16에서 단순 접촉이 아니라 안정화와 높아진 저점을 확인한다. / 검증된 정규장에서 10:30 이후 282.24 및 실시간 거래량가중평균가격 위의 연속 2개 5분봉 종가와 동시간대 상대거래량 1.2 이상을 관찰한다. 현재 관측값이 아닌 제안된 조건이다.","risk_condition_ko":"272.3 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"META","display_name":"Meta Platforms","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":702.57,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":701.5232681934524,"relative_volume":0.5682286581800858,"spread_bps":0.7126720212100915,"day_high":708.7,"day_low":693.86,"execution_condition_ko":"위험 대응 조건: 711.68 이하 하락, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"711.68 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:execution_strength","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"CCC","display_name":"CCC","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":7.625,"market_data_asof":"2026-10-19T14:11:00-04:00","session_vwap":7.625091548861127,"relative_volume":2.9384898808051445,"spread_bps":13.114754098360375,"day_high":7.63,"day_low":7.61,"execution_condition_ko":"위험 대응 조건: 7.59 이하 하락, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"7.59 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"데이터 확인 전 대기","market_data_asof":"2026-10-19T14:11:00-04:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-19T14:21:00-04:00","expired_at_build":true,"provider_limitations":["status_unavailable:luld_status","status_unavailable:reg_sho_status","status_unavailable:news_halt_status","feed_limited:orderbook"],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-20T03:14:46.799081+09:00",
  "as_of": "2026-10-19T14:11:00-04:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/us/report/latest.html"
}
```
