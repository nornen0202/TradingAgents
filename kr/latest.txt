# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-20T00:04:26.123857+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261020T090007_local-freshness-kr-overlay",
  "producer_finished_at": "2026-10-20T09:01:37.872148+09:00",
  "analysis_run_id": "20261020T044511_local-scheduler-kr-full",
  "analysis_completed_at": "2026-10-20T06:50:32.590683+09:00",
  "analysis_trade_date_oldest": "2026-10-19",
  "analysis_trade_date_latest": "2026-10-19",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-20T09:01:00+09:00",
  "market_data_latest_at": "2026-10-20T09:01:00+09:00",
  "market_data_status": "FRESH"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-20T09:01:34.552895+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-20T09:01:34.552895+09:00",
    "run_started_at": "2026-10-20T09:00:07.896629+09:00",
    "run_finished_at": "2026-10-20T09:01:37.872148+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 8732780,
    "total_unrealized_pnl_krw": -6211456,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 9709432
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1253000,
      "market_value_krw": 2506000,
      "unrealized_pnl_krw": -2929000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 218000,
      "market_value_krw": 2180000,
      "unrealized_pnl_krw": -1143851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 325000,
      "market_value_krw": 1625000,
      "unrealized_pnl_krw": -449643
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
      "current_price_krw": 513000,
      "market_value_krw": 513000,
      "unrealized_pnl_krw": -640000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 18060,
      "market_value_krw": 325080,
      "unrealized_pnl_krw": -243235
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 206500,
      "market_value_krw": 206500,
      "unrealized_pnl_krw": -167667
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 68800,
      "market_value_krw": 206400,
      "unrealized_pnl_krw": -93600
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 184400,
      "market_value_krw": 184400,
      "unrealized_pnl_krw": -97934
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 132400,
      "market_value_krw": 132400,
      "unrealized_pnl_krw": -39900
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 44950,
      "market_value_krw": 89900,
      "unrealized_pnl_krw": -28300
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 65000,
      "market_value_krw": 65000,
      "unrealized_pnl_krw": -47931
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 52300,
      "market_value_krw": 52300,
      "unrealized_pnl_krw": -2200
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":64700.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":65147.258706889246,"relative_volume":0.7927659186230083,"spread_bps":15.444015444015443,"day_high":65600.0,"day_low":64600.0,"execution_condition_ko":"위험 대응 조건: 69,400 이하 하락, 장중 확인 시 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"69,400 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":133500.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":133951.93803375357,"relative_volume":0.6822067352222821,"spread_bps":30.00750187546887,"day_high":135000.0,"day_low":133100.0,"execution_condition_ko":"353200.KS의 당일 거래일·정규장·거래정지·시장경보·마지막 체결 시각을 확인하고 요청한 5분봉과 반환된 1분봉의 불일치를 해소한다. / 137900~140500 회복·재시험 지지, 신선한 정규장 거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상을 함께 확인한다. 충족해도 순보상/위험 2 미만이면 대기한다.","risk_condition_ko":"137,900 이하 하락, 2개 봉 확인 후 (가격 실패 확인; 거래량 증가를 기다리지 않음) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":1253000.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":1263727.0361552516,"relative_volume":0.7712747363737111,"spread_bps":7.984031936127744,"day_high":1267000.0,"day_low":1252000.0,"execution_condition_ko":"1238000~1247000의 재회복·유지와 저점 상승을 최신 정규장에서 확인한다. 이미 일시 이탈한 구간이므로 확정 지지로 간주하지 않는다. / 1277000 돌파·재시험 지지, 정규장 거래량가중평균가격 상회와 동일 시간대 상대거래량 1.2 이상을 확인한다. 이 조건만으로 매수하지 않는다.","risk_condition_ko":"1,208,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":511000.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":513864.5869043538,"relative_volume":0.3828173162826299,"spread_bps":19.58863858961802,"day_high":518000.0,"day_low":508000.0,"execution_condition_ko":"534,000 돌파·재시험, 신선한 거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상을 확인하되 가까운 543,000 저항까지 비용 차감 보상·위험비가 2배 미만이면 건너뛴다. 543,000의 지지 전환 등 구조 개선 시 별도 매수 판단을 갱신한다. / 485,000 및 473,500 이탈·회복 실패와 계좌 손실예산 초과 여부를 확인한다. 신규 진입보다 기존 노출의 축소·손절을 우선한다.","risk_condition_ko":"485,000 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":217500.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":219293.57126688297,"relative_volume":0.8158893674993734,"spread_bps":22.962112514351322,"day_high":219500.0,"day_low":217500.0,"execution_condition_ko":"먼저 거래일·정규장 운영·거래정지·신선한 호가·실제 오분봉과 기존 보유 위험 한도를 확인한다. / 222500원 돌파·재시험은 관찰 신호이며 자동 매수가 아니다.","risk_condition_ko":"219,500 이상 도달, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":326500.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":324457.0408163265,"relative_volume":0.15465824315810872,"spread_bps":61.34969325153374,"day_high":327000.0,"day_low":323500.0,"execution_condition_ko":"278470.KS의 공식 거래일·정규장 개장시각·거래정지 여부·최신 호가 및 봉 시각을 먼저 확인한다. / 328900~331500원 회복 구간과 322500~325500원 반등 방어 구간의 유지 여부를 확인한다.","risk_condition_ko":"322,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":208000.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":209789.8848035348,"relative_volume":0.6356628208469719,"spread_bps":24.009603841536613,"day_high":211000.0,"day_low":208000.0,"execution_condition_ko":"212000원과 217500~218500원 회복·재시험 지지를 관찰한다. 218500원은 과거 야간자료 고가이므로 정규장 기준으로 재검증한다. / 227800~231500원 지지 전환, 상대강도지수 50 회복과 여러 거래일의 이동평균 수렴·확산 히스토그램 개선을 확인한다. 제공된 상대강도지수 41.41과 음의 히스토그램은 아직 추세 전환을 확증하지 않는다.","risk_condition_ko":"197,400 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":183700.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":182460.05107925524,"relative_volume":0.3743544675418361,"spread_bps":5.445140212360468,"day_high":183800.0,"day_low":181600.0,"execution_condition_ko":"한국거래소의 당일 정규장 운영 여부와 타임스탬프가 있는 신선한 가격·체결·거래량을 먼저 확인한다. / 183800 돌파·재지지, 185450 회복, 실제 당일 거래량가중평균가격 유지와 동일 시간대 상대거래량 1.2 이상을 확인한다.","risk_condition_ko":"183,266 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":161300.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":162262.50504398355,"relative_volume":0.5200919132654078,"spread_bps":6.2015503875969,"day_high":163300.0,"day_low":161000.0,"execution_condition_ko":"010120.KS의 결정 기준 시각은 2026-10-20T04:59:31.609339+09:00이고 일봉 가격 기준일은 2026-10-19다. 거래일·휴장·조기종료 달력, 정규장 여부, 호가 시각과 봉 간격은 별도 확인해야 한다. 이 시계만으로 실제 세션이나 진입 조건 충족을 단정하지 않는다. / 010120.KS의 2026-10-19 20:00 지연 가격 166600원, 해당 야간 거래량가중평균가격 및 산식 미확인 상대거래량 20.12배는 현재 정규장 실행 근거에서 제외한다.","risk_condition_ko":"173,100 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":68800.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":69198.83011911514,"relative_volume":0.26696265248519063,"spread_bps":14.524328249818446,"day_high":69500.0,"day_low":68800.0,"execution_condition_ko":"신선한 정규장 자료로 66100~67000원 지지 유지와 저점 상승을 확인한다. 지지 미이탈을 수요 회복으로 해석하지 않는다. / 70100~70800원과 71700~72700원 회복·재지지, 상대강도지수 50 회복 및 이동평균 수렴·확산 지표 막대값의 음수 폭 축소를 함께 확인한다.","risk_condition_ko":"70,564 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":18060.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":18094.51583357898,"relative_volume":0.3021379917658586,"spread_bps":5.535566011624688,"day_high":18140.0,"day_low":17990.0,"execution_condition_ko":"판단 시각은 2026-10-20T04:59:16.924359+09:00이고 일봉 가격 기준일은 2026-10-19이다. 실제 거래일·정규장 여부, 거래 중단, 호가 시각과 봉 주기를 별도로 확인한다. 시계만으로 당일 진입·감축 조건 충족을 판단하지 않는다. / 18990원 돌파·재지지, 최신 정규장 거래량가중평균가격 상회와 동시간대 상대거래량 1.2배 이상을 관찰한다. 1.2배는 실행 기준이지 현재 관측값이 아니다. 가까운 저항까지 비용 차감 보상/위험 2배가 안 나오면 돌파해도 신규 진입을 보류한다.","risk_condition_ko":"18,790 이상 도달, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":52500.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":52567.286349574635,"relative_volume":0.47520064984515775,"spread_bps":38.095238095238095,"day_high":52900.0,"day_low":52200.0,"execution_condition_ko":"51,300 및 50,300~50,600 지지 유지, 높아지는 저점과 거래량가중평균가격 회복 / 55,000~55,300 돌파 후 지지 전환과 동시간대 상대거래량 1.2 이상","risk_condition_ko":"50,300 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":45050.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":45514.19512195122,"relative_volume":0.13533072684152936,"spread_bps":22.172949002217294,"day_high":45700.0,"day_low":45050.0,"execution_condition_ko":"083450.KQ의 실제 거래일·정규세션·거래정지 여부와 당일 시세 타임스탬프를 확인한다. 기준 시각 2026-10-20T05:29:16.578817+09:00만으로 거래 가능 상태나 진입 조건 충족을 판단하지 않는다. 10:30은 최초 시험 진입 검토 시각이지 만료시각이 아니며 다음 세션으로 임의 이월하지 않는다. / 2026-10-19T20:00:00+09:00의 지연 가격 46,700원과 별도 세션 거래량가중평균가격 44,961.54원, 산식 불명확한 상대거래량 14.45배는 당일 진입 신호에서 제외한다. 일봉 거래량의 제공 20일 평균 대비 약 0.72배도 장중 동시간대 상대거래량과 구분한다.","risk_condition_ko":"43,250 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":193500.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":191992.15518296414,"relative_volume":0.67933254808111,"spread_bps":15.49186676994578,"day_high":193800.0,"day_low":190900.0,"execution_condition_ko":"판단 시각은 2026-10-20T06:00:02.417412+09:00이며 일봉 기준일은 2026-10-19다. 실제 거래일·정규장 상태·시세 신선도는 확인되지 않았다. 10:30은 가장 이른 재검토 기준일 뿐 주문 활성화나 만료 시각이 아니다. 승인된 조건부 주문과 유효기간은 없다. / 요약가격 193,100원과 지연된 마지막 봉 190,700원의 불일치, 요청한 5분봉 대신 제공된 1분봉, 누락된 거래량 가중평균가격과 사용할 수 없는 거래량 자료를 해결한다.","risk_condition_ko":"189,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":160900.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":160255.4098904746,"relative_volume":0.1449757924589492,"spread_bps":6.2131096613855235,"day_high":161400.0,"day_low":159600.0,"execution_condition_ko":"154,400~156,000원 눌림 후 정규장 저점 형성, 156,000원 회복·지지와 매도 거래량 둔화를 관찰한다. 가격 도달만으로 매수하지 않는다. / 165,400원 초과의 연속 2개 5분봉 종가·되돌림 지지, 당일 거래량가중평균가격 상회, 동일 시간대 상대거래량 1.2 이상을 확인한다. 손익비와 별도 승인 없이는 주문하지 않는다.","risk_condition_ko":"154,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"396300.KQ","display_name":"396300","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":10100.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":9770.669371849992,"relative_volume":3.0498017218208755,"spread_bps":9.896091044037606,"day_high":10150.0,"day_low":9470.0,"execution_condition_ko":"396300.KQ의 오늘 거래 가능 여부와 신선한 정규장 5분봉을 확인한다. 기존 공급자료는 요청과 달리 1분봉을 반환했고 요약가격과 마지막 봉 가격도 불일치했다. / 396300.KQ의 9500원 돌파·재시험, 동시간대 상대거래량 1.2 이상과 거래량가중평균가격 지지를 관찰한다. 매수 검토 전 근거 있는 상단 목표와 비용 후 손익비 2 이상을 확보한다.","risk_condition_ko":"9,120 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":138400.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":137315.4597233523,"relative_volume":0.13761511549200203,"spread_bps":57.971014492753625,"day_high":138800.0,"day_low":136800.0,"execution_condition_ko":"090430.KS 135300–136000 지지구간에서 매도 압력이 약해지고 136000 위에서 마감한 연속 2개 완성 5분봉, 실시간 정규장 거래량가중평균가격 지지, 동일 경과시간 상대거래량 1.2 이상을 확인한다. 이는 재검토 조건이지 매수 승인이 아니다. / 090430.KS 140000 돌파 후 139100–140000 재시험 지지와 140000 재회복을 확인하되 142000까지의 제한된 보상을 다시 계산한다.","risk_condition_ko":"135,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"105560.KS","display_name":"105560","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":160600.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":160591.2023653088,"relative_volume":1.0937880754462244,"spread_bps":6.2285892245406425,"day_high":161000.0,"day_low":159900.0,"execution_condition_ko":"기존 105560.KS 보유량·순자산·은행업 노출·현금과 갭 위험을 먼저 확인한다. 한도 초과가 확인되면 가격 지지와 무관하게 초과 위험을 줄인다. / 2026-10-20의 실제 거래일·정규장과 최신 체결시각을 확인한다. 요약가 162700과 마지막 분봉 160700의 불일치 및 반환 간격 오류를 해결한다.","risk_condition_ko":"159,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"131290.KQ","display_name":"티에스이","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":275000.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":274540.03079291765,"relative_volume":0.2258824020393755,"spread_bps":18.198362147406733,"day_high":276500.0,"day_low":274000.0,"execution_condition_ko":"131290.KQ의 일관된 시각표시 시세, 실제 거래일정·거래상태·호가차·잔량·완성된 5분봉·거래량가중평균가격을 확인한다. / 261000-267500을 새로 시험한 뒤 267500 재회복, 완성된 5분봉 2개의 저점 상승, 동시간대 상대거래량 1.2 이상을 확인한다.","risk_condition_ko":"261,148 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"010950.KS","display_name":"S-Oil","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":154800.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":153641.21608980355,"relative_volume":0.3253947961183962,"spread_bps":19.398642095053347,"day_high":155200.0,"day_low":153300.0,"execution_condition_ko":"010950.KS의 151300~153700원 시험 후 저점 상승과 156200원 회복, 세션 거래량가중평균가격 상회, 동시간대 상대거래량 1.2 이상을 함께 확인한다. 충족만으로 자동 매수하지 않는다. / 159000원 회복 후 160600원 재시험의 지지 전환을 감시한다. 158200~159000원 및 162200~162500원 저항과 비용·변동성을 반영한 잔여 손익비가 부족하면 진입하지 않는다.","risk_condition_ko":"150,200 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"018260.KS","display_name":"삼성SDS","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":202000.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":200795.66210045663,"relative_volume":0.4048059149722736,"spread_bps":49.62779156327544,"day_high":202500.0,"day_low":199800.0,"execution_condition_ko":"018260.KS의 최신 정규장 자료로 205500~206000원 회복, 실제 5분봉 돌파 종가와 후속 재시험 지지를 확인한다. / 동일 경과시간 누적 상대거래량 1.2 이상과 당일 거래량가중평균가격 상회를 확인한다. 1.2는 운용 기준이지 관측값이 아니다.","risk_condition_ko":"200,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"018880.KS","display_name":"018880","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":3925.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":3945.927767119112,"relative_volume":0.26973780487591065,"spread_bps":12.746972594008922,"day_high":3960.0,"day_low":3915.0,"execution_condition_ko":"판단 시계는 2026-10-20T06:04:32.104895+09:00이며 가격 기준은 2026-10-19 완료 일봉이다. 실제 거래일·정규장·거래정지·시장경보·호가와 시세 타임스탬프는 별도로 확인한다. / 10:30은 최초 재심사 가능 시각이지 자동 매수나 만료시각이 아니다. 확인된 주문 만료시각은 없으며 다음 거래일로 자동 이월하지 않는다.","risk_condition_ko":"3,815 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"036460.KS","display_name":"036460","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":36300.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":36329.98348017621,"relative_volume":0.28562676870169185,"spread_bps":68.54009595613434,"day_high":36450.0,"day_low":36300.0,"execution_condition_ko":"거래일·정규장 상태·거래소 시각·호가 지연·일관된 봉 간격·매수매도 호가·거래량가중평균가격을 먼저 검증한다. / 35850~36150원에서 매도 거래량 감소 후 반등과 거래량가중평균가격 회복을 관찰하되 가격 접촉만으로 매수하지 않는다.","risk_condition_ko":"35,850 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"051900.KS","display_name":"051900","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":276000.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":273483.71335504885,"relative_volume":0.21286516863670954,"spread_bps":18.13236627379873,"day_high":276000.0,"day_low":270500.0,"execution_condition_ko":"051900.KS 거래일·정규장 일정·거래정지·시장경보·실적 일정을 확인하고 최신 호가·스프레드·체결·거래량가중평균가격을 확보한다. 전일 야간 지연 자료, 거래량과 상대거래량의 0값, 일봉 거래량가중이동평균을 당일 신호의 대체값으로 쓰지 않는다. / 051900.KS 270000~272000원 지지 시험 후 272000원 회복, 거래량가중평균가격 지지와 동일 시간대 상대거래량 1.2 이상을 관찰한다. 비용 후 보상 대비 위험 2배가 별도로 확보돼야 진입 재검토가 가능하다.","risk_condition_ko":"263,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"011200.KS","display_name":"011200","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":23550.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":23499.1168559474,"relative_volume":0.4238085135353369,"spread_bps":21.208907741251327,"day_high":23600.0,"day_low":23300.0,"execution_condition_ko":"결정 시각은 2026-10-20T05:43:52.347505+09:00이다. 제안된 현지 10:30은 가장 이른 소규모 진입 검토 시각이지 만료가 아니다. 거래일 달력, 정규장 운영 여부와 거래상태를 별도 확인하며 검증되지 않은 기한을 다음 거래일로 이월하지 않는다. / 오래되고 불일치하는 장중 자료를 완료된 정규장 5분봉, 당일 거래량가중평균가격, 체결 가능한 호가·스프레드와 동시간대 상대거래량으로 교체한다. 보고된 거래량 0을 매수세 부재로 해석하지 않는다.","risk_condition_ko":"22,800 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"068270.KS","display_name":"068270","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":198250.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":197034.81595092025,"relative_volume":0.7965807607627498,"spread_bps":10.080645161290322,"day_high":198400.0,"day_low":195600.0,"execution_condition_ko":"기준 시계는 2026-10-20T05:45:11.129590+09:00이며 가격 기준은 2026-10-19 일봉이다. 거래일 달력·실제 정규장 상태·최신 체결 시각·실제 5분봉을 별도 확인한다. 10:30은 최초 검토시각이지 만료시각이 아니며 검증된 만료시각은 없다. / 194000~195500원에서 하락 거래 감소와 반등을 관찰하되 실제 가격·보호가격·중간 저항·청산 경로·비용으로 손익비를 다시 계산한다.","risk_condition_ko":"199,300 이상 도달, 2개 봉 확인 후 이익실현성 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":589000.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":587444.8711928083,"relative_volume":1.3165969070218575,"spread_bps":16.99235344095157,"day_high":592000.0,"day_low":582000.0,"execution_condition_ko":"600000원 돌파·재시험 지지 또는 554000~558000원 지지 후 558000원 회복을 최신 정규장 자료로 확인한다. / 554000원과 526000원 종가 이탈은 누적 위험 감축, 503000원 이탈은 기술 전술 청산 기준으로 관리한다.","risk_condition_ko":"554,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"373220.KS","display_name":"LG에너지솔루션","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":426000.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":426374.7009018958,"relative_volume":0.5707097631496708,"spread_bps":11.730205278592376,"day_high":430500.0,"day_low":425000.0,"execution_condition_ko":"위험 대응 조건: 428,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"428,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"086790.KS","display_name":"086790","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":123100.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":123474.51420029896,"relative_volume":0.5852970152695592,"spread_bps":16.246953696181965,"day_high":123700.0,"day_low":122500.0,"execution_condition_ko":"위험 대응 조건: 125,600 이하 하락, 장중 확인 시 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"125,600 이하 하락, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

```json
{"ticker":"036930.KQ","display_name":"주성엔지니어링","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":207000.0,"market_data_asof":"2026-10-20T09:01:00+09:00","session_vwap":208180.79091494845,"relative_volume":0.39028859131688975,"spread_bps":24.183796856106408,"day_high":209500.0,"day_low":205000.0,"execution_condition_ko":"위험 대응 조건: 195,628 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"195,628 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"현재 세션 조건부 데이터, 주문 전 호가·상태 재확인","reference_strategy":{"strategy_code":null,"strategy_ko":null,"decision_state_ko":null,"market_data_asof":null},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-10-20T09:11:00+09:00","expired_at_build":false,"provider_limitations":[],"provider_blockers":null}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-19T14:43:50.029520+09:00",
  "as_of": "2026-10-19T14:40:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
