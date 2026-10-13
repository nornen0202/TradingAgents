# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-13T13:55:45.929406+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261013T132402_local-scheduler-kr-overlay_only",
  "producer_finished_at": "2026-10-13T13:26:33.241927+09:00",
  "analysis_run_id": "20261012T055403_local-scheduler-kr-full",
  "analysis_completed_at": "2026-10-12T09:07:17.272511+09:00",
  "analysis_trade_date_oldest": "2026-10-08",
  "analysis_trade_date_latest": "2026-10-08",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-13T13:24:00+09:00",
  "market_data_latest_at": "2026-10-13T13:24:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-13T13:26:29.533367+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "latest_attempt": {
    "status": "VALID",
    "account_as_of": "2026-10-13T13:26:29.533367+09:00",
    "run_started_at": "2026-10-13T13:24:02.747380+09:00",
    "run_finished_at": "2026-10-13T13:26:33.241927+09:00",
    "selected_for_public_account": true
  },
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 9191590,
    "total_unrealized_pnl_krw": -5752646,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 10168242
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1442000,
      "market_value_krw": 2884000,
      "unrealized_pnl_krw": -2551000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 230750,
      "market_value_krw": 2307500,
      "unrealized_pnl_krw": -1016351
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 281000,
      "market_value_krw": 1405000,
      "unrealized_pnl_krw": -669643
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 178100,
      "market_value_krw": 712400,
      "unrealized_pnl_krw": -262600
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
      "current_price_krw": 17705,
      "market_value_krw": 318690,
      "unrealized_pnl_krw": -249625
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 79200,
      "market_value_krw": 237600,
      "unrealized_pnl_krw": -62400
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 225500,
      "market_value_krw": 225500,
      "unrealized_pnl_krw": -148667
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
      "current_price_krw": 143700,
      "market_value_krw": 143700,
      "unrealized_pnl_krw": -28600
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 53100,
      "market_value_krw": 106200,
      "unrealized_pnl_krw": -12000
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 69300,
      "market_value_krw": 69300,
      "unrealized_pnl_krw": -43631
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 59600,
      "market_value_krw": 59600,
      "unrealized_pnl_krw": 5100
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1446000.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":1483612.4562648274,"relative_volume":1.5955988341086562,"spread_bps":6.91323885240235,"day_high":1554000.0,"day_low":1445000.0,"execution_condition_ko":"위험 대응 조건: 1,678,000 이하 하락, 종가 확인 후 손절 조건 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"1,678,000 이하 하락, 종가 확인 후 손절 조건","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":53300.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":53011.54548424917,"relative_volume":0.9990170421517032,"spread_bps":18.779342723004696,"day_high":54700.0,"day_low":51400.0,"execution_condition_ko":"위험 대응 조건: 54,400 이하 하락, 종가 확인 후 손절 조건 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"54,400 이하 하락, 종가 확인 후 손절 조건","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":230750.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":234215.20603563555,"relative_volume":1.4074234703033925,"spread_bps":21.668472372697725,"day_high":244000.0,"day_low":228000.0,"execution_condition_ko":"위험 대응 조건: 257,000 이하 하락, 2개 봉 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"257,000 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":282000.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":297335.2499705148,"relative_volume":4.524220284351264,"spread_bps":17.71479185119575,"day_high":331500.0,"day_low":281000.0,"execution_condition_ko":"위험 대응 조건: 356,500 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"356,500 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":78700.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":77120.59497320527,"relative_volume":0.9663088757707587,"spread_bps":12.698412698412698,"day_high":79200.0,"day_low":75200.0,"execution_condition_ko":"위험 대응 조건: 84,300 이하 하락, 종가 확인 후 (거래량 조건 없음) 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"84,300 이하 하락, 종가 확인 후 (거래량 조건 없음) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":225000.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":223750.40023656486,"relative_volume":1.3886507066170755,"spread_bps":22.197558268590456,"day_high":237000.0,"day_low":216000.0,"execution_condition_ko":"위험 대응 조건: 252,000 이하 하락, 다음 거래일 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"252,000 이하 하락, 다음 거래일 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":143400.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":140473.7137768949,"relative_volume":1.0249853819338723,"spread_bps":6.975933031042902,"day_high":146800.0,"day_low":136000.0,"execution_condition_ko":"위험 대응 조건: 158,200 이상 도달, 장중 확인 시 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"158,200 이상 도달, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":59400.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":59349.49610000405,"relative_volume":0.895345020103082,"spread_bps":16.849199663016005,"day_high":61600.0,"day_low":57400.0,"execution_condition_ko":"위험 대응 조건: 66,900 이상 도달, 2개 봉 확인 후 (상승 거래량 둔화 또는 매도 거래량 확대를 보조 확인) 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"66,900 이상 도달, 2개 봉 확인 후 (상승 거래량 둔화 또는 매도 거래량 확대를 보조 확인) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":177900.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":177211.99522877313,"relative_volume":1.618114854301247,"spread_bps":5.61955605507165,"day_high":182500.0,"day_low":173100.0,"execution_condition_ko":"010120.KS의 가격 제공자 간 종가 차이·분할 조정·호가단위를 대사하고 실제 거래일과 신선한 정규장 봉·호가·거래량가중평균가격을 확인한다. / 192,100~195,500원에서 저점 갱신 중단과 재시험 지지를 관찰한다. 지지 접촉 자체는 매수 신호가 아니다.","risk_condition_ko":"200,854 이하 하락, 2개 봉 확인 후 (위험 축소에는 매수용 상대거래량 하한을 적용하지 않는다.) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":547000.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":546768.6267182435,"relative_volume":1.1409805349481852,"spread_bps":18.264840182648403,"day_high":567000.0,"day_low":531000.0,"execution_condition_ko":"실제 거래일·정규장 운영·거래정지·시장경보와 최신 시세·호가 시각을 확인하고 계좌 손실예산·집중도를 먼저 점검한다. / 596,000원 유지, 623,000~628,000원 회복·재시험, 643,000원 매물 흡수 여부를 관찰한다. 관찰선 도달은 자동 매수 지시가 아니다.","risk_condition_ko":"596,000 이하 하락, 종가 확인 후 (거래량 미확인을 지지 유지의 증거로 해석하지 않는다.) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":17650.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":17508.093763211124,"relative_volume":1.5037000319044358,"spread_bps":5.664117813650524,"day_high":17840.0,"day_low":17210.0,"execution_condition_ko":"010140.KS 실제 거래일·세션·최신 체결시각·매수매도 호가·스프레드·거래량과 정상적인 세션 거래량가중평균가격을 우선 확인한다. / 18,850원 재시험, 19,160원 재탈환 실패와 18,440원 거래량 동반 이탈을 우선 감시한다. 위험한도 위반은 별도 감축 사유다.","risk_condition_ko":"18,440 이하 하락, 거래량 조건 확인 후 (비교 가능한 거래량 기준 대비 증가를 동반한 하향 이탈 확인) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":175200.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":174923.8219272189,"relative_volume":1.1879635513570777,"spread_bps":5.706134094151213,"day_high":177400.0,"day_low":173200.0,"execution_condition_ko":"035420.KS의 실제 거래일·세션·최신 체결·호가·잔량·스프레드·거래정지 여부부터 확인한다. 제공된 2026-10-08 20:00 자료와 비정상적인 거래량가중평균가격 670110558.30원은 실행 근거에서 제외한다. / 가격 기준일 2026-10-08과 판단일 2026-10-12를 구분하고 2026-10-11 뉴스가 과거 종가에 반영됐다고 가정하지 않는다.","risk_condition_ko":"183,100 이하 하락, 2개 봉 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":69400.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":68859.67405789917,"relative_volume":1.2723259136239036,"spread_bps":14.398848092152628,"day_high":70600.0,"day_low":67300.0,"execution_condition_ko":"034020.KS의 실제 거래일 달력, 최신 정규장 가격·호가 시각, 정상 장중 거래량가중평균가격과 검증된 동시간대 누적 상대거래량을 확보한다. / 75200 방어와 78700~79800 회복 실패를 구분한다. 지지 접촉만으로 매수하지 않으며 위험 축소와 손절 신호를 우선 감시한다.","risk_condition_ko":"78,700 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"018880.KS","display_name":"018880","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":3720.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":3737.988884258771,"relative_volume":1.0640099672292938,"spread_bps":13.43183344526528,"day_high":3860.0,"day_low":3630.0,"execution_condition_ko":"위험 대응 조건: 3,878.83 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"3,878.83 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010950.KS","display_name":"S-Oil","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":157700.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":155653.66924561374,"relative_volume":0.6530392228168894,"spread_bps":6.34719136781974,"day_high":159200.0,"day_low":152700.0,"execution_condition_ko":"위험 대응 조건: 162,000 이하 하락, 종가 확인 후 (확정 종가 이탈 시 거래량 증가를 추가로 요구하지 않음) 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"162,000 이하 하락, 종가 확인 후 (확정 종가 이탈 시 거래량 증가를 추가로 요구하지 않음) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"010580.KS","display_name":"010580","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":2040.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":2062.1922616276097,"relative_volume":0.14429563671473253,"spread_bps":48.899755501222494,"day_high":2150.0,"day_low":1994.0,"execution_condition_ko":"위험 대응 조건: 2,200 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"2,200 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"SELL","strategy_ko":"매도·청산 검토","decision_state_ko":"투자 근거 무효화","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"066570.KS","display_name":"LG전자","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":174900.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":175267.18918800147,"relative_volume":1.53350652375933,"spread_bps":5.719187875321705,"day_high":182000.0,"day_low":170800.0,"execution_condition_ko":"판단시각은 2026-10-12T07:21:18.610412+09:00이다. 실제 거래일·정규장·휴장·정지 여부와 최신 체결시각은 미확인이다. 장중 자료 표기 2026-10-08 20:00은 당일 조건 판단에 사용하지 않는다. 검증된 만료시각이 없으므로 만료나 다음 세션 연장을 선언하지 않는다. / 197,100~198,800원 지지 방어와 완결된 5분봉의 재시험 저점 유지, 210,956~212,788원 회복을 관찰한다. 정상 거래량가중평균가격과 상대거래량은 별도로 확보하며 1.2는 관측값이 아닌 제안 기준이다.","risk_condition_ko":"197,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"128940.KS","display_name":"128940","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":452000.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":456239.4709794063,"relative_volume":1.0564148335017434,"spread_bps":44.29678848283499,"day_high":470000.0,"day_low":444000.0,"execution_condition_ko":"128940.KS의 실제 거래일·정규장 상태·시장경보·타임스탬프가 있는 최신 시세와 호가부터 확인한다. 제공 판단 시각 2026-10-12T08:07:16.940031+09:00은 연구일과 일치하지만 세션이나 조건 충족을 증명하지 않는다. / 475,000원 지지·저점 상승과 492,500~499,000원 회복·재시험을 관찰한다. 이어 505,000~509,500원 회복과 지지 전환을 확인하되 가격 접촉만으로 주문하지 않는다.","risk_condition_ko":"475,000 이하 하락, 거래량 조건 확인 후 (신선한 정규장 자료에서 하회 거래 지속과 매도 거래량 증가 확인) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"095340.KQ","display_name":"ISC","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":180000.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":180841.4052669919,"relative_volume":0.7912192464769905,"spread_bps":11.117287381878821,"day_high":187400.0,"day_low":174600.0,"execution_condition_ko":"095340.KQ의 실제 거래일·정규장 상태·거래정지·변동성 완화 상태와 시각이 검증된 호가·체결·5분봉을 확보한다. 199,400원은 현재가가 아니라 2026-10-08 종가다. / 197,500~199,900원 방어, 204,000~205,300원 회복, 207,000원 돌파·재지지를 구분한다. 감시 신호는 매수 주문이 아니며 위험축소 판단 해소와 손익비 재검증이 필요하다.","risk_condition_ko":"199,900 이하 하락, 종가 확인 후 (거래량 부족만으로 위험축소를 미루지 않는다.) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"105560.KS","display_name":"105560","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":160200.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":159335.3720634771,"relative_volume":0.9725236028383342,"spread_bps":6.2441461130190445,"day_high":161900.0,"day_low":156400.0,"execution_condition_ko":"105560.KS 실제 거래일·세션, 최신 체결·호가·스프레드·거래량 시각과 보유량·순자산·집중도를 확인한다. 한도 내 보유 유지와 축소 필요량을 구분하는 선행 조건이다. / 105560.KS 162800원 안정, 166400원 회복 및 165300~166400원 재시험에서 저점 상승을 관찰한다. 이는 관찰 조건이지 자동 매수 조건이 아니다.","risk_condition_ko":"162,800 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":129900.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":129359.61713453752,"relative_volume":0.6760630357190262,"spread_bps":7.701193685021178,"day_high":131100.0,"day_low":128100.0,"execution_condition_ko":"당일 거래소 정규장 일정, 최신 실제 체결 시각, 정상적인 세션 거래량가중평균가격과 동일시간 누적 상대거래량을 확보한다. 제공 자료의 비정상 값 1041408087.5는 제외하며 거래량가중이동평균 139731원을 세션 평균가격으로 대체하지 않는다. / 계좌 순자산·실제 보유수량·업종 집중도를 확인하여 비중 5%와 계획 손실 0.5% 한도 초과 여부를 먼저 판정한다.","risk_condition_ko":"137,900 이하 하락, 2개 봉 확인 후 (위험 축소에는 최소 상대거래량 조건을 적용하지 않음) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000150.KS","display_name":"두산","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":1135000.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":1151238.0837099203,"relative_volume":0.8702687618212307,"spread_bps":17.62114537444934,"day_high":1198000.0,"day_low":1108000.0,"execution_condition_ko":"거래소 달력·정규장·거래정지 여부·최신 봉 시각·호가를 별도로 확인한다. 2026-10-08 분봉과 거래량 0·비정상 거래량가중평균가격은 현재 신호에서 제외한다. / 1,325,000원 시험 후 저점 상승·재상회, 또는 1,408,000원 돌파 후 재시험 지지를 완료된 5분봉 두 개로 확인한다. 이는 재평가 조건이지 매수 승인 자체가 아니다.","risk_condition_ko":"1,325,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"402340.KS","display_name":"402340","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":869000.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":883784.2063092776,"relative_volume":1.8127812287079115,"spread_bps":11.500862564692351,"day_high":943000.0,"day_low":858000.0,"execution_condition_ko":"402340.KS의 거래소 일정, 최신 정규장 체결·호가, 정상 거래량가중평균가격, 동시간대 상대거래량 및 계좌 위험을 확보한다. / 1,050,000원 지지 실패는 보유 위험 축소 조건, 1,060,000원 회복·재시험은 관찰 조건으로 구분한다.","risk_condition_ko":"1,050,000 이하 하락, 2개 봉 확인 후 (위험 축소에는 상대거래량 최저 조건을 적용하지 않는다.) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","decision_state_ko":"조건 충족, 종가 확인 대기","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":180400.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":179951.35321229836,"relative_volume":0.9597121896424932,"spread_bps":5.544774050457444,"day_high":181000.0,"day_low":177700.0,"execution_condition_ko":"033780.KS의 최신 가격 시각, 거래일 달력, 정규장 여부, 거래정지·시장경보 및 체결 유동성을 검증한다. 판단 시각 2026-10-12T07:50:43.237953+09:00은 세션이나 가격 신선도를 입증하지 않는다. 2026-10-08 가격을 현재가로 사용하지 않는다. / 175,200~175,300원 회복·재시험 또는 180,800원 돌파·재시험, 정상 세션 거래량가중평균가격 상회와 동시간대 상대거래량 1.2 이상을 관찰한다. 순보상·위험 기준이 미달하면 계속 대기한다.","risk_condition_ko":"174,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"373220.KS","display_name":"LG에너지솔루션","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":402000.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":386527.2165891591,"relative_volume":1.3209246469227534,"spread_bps":12.445550715619166,"day_high":402000.0,"day_low":377000.0,"execution_condition_ko":"한국거래소 거래일·정규장 상태·거래정지·변동성완화장치 발동 여부, 최신 체결시각·호가·실제 보유자료를 먼저 확인한다. / 393,800~397,000원 재시험 후 저점 상승과 397,000원 위 연속 2개 5분봉 마감을 관찰한다.","risk_condition_ko":"386,500 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"062040.KS","display_name":"062040","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":205000.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":205491.6966154486,"relative_volume":1.1561962893055773,"spread_bps":24.360535931790498,"day_high":214500.0,"day_low":199800.0,"execution_condition_ko":"위험 대응 조건: 215,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"215,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":153000.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":149855.80341736646,"relative_volume":0.7034582343670017,"spread_bps":6.533812479581836,"day_high":153800.0,"day_low":143000.0,"execution_condition_ko":"위험 대응 조건: 152,200 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"152,200 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"000810.KS","display_name":"000810","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":611000.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":609530.9874574577,"relative_volume":1.441202703654089,"spread_bps":16.35322976287817,"day_high":622000.0,"day_low":595000.0,"execution_condition_ko":"위험 대응 조건: 607,000 이하 하락, 2개 봉 확인 후 (방어 매도에는 거래량 증가나 거래량가중평균가격 조건을 요구하지 않는다.) 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"607,000 이하 하락, 2개 봉 확인 후 (방어 매도에는 거래량 증가나 거래량가중평균가격 조건을 요구하지 않는다.) 리스크 축소","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"조건 충족 전 대기","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"180640.KS","display_name":"180640","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":128400.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":128933.95484966946,"relative_volume":1.0960834105174893,"spread_bps":15.58846453624318,"day_high":132200.0,"day_low":126500.0,"execution_condition_ko":"위험 대응 조건: 128,700 이하 하락, 종가 확인 후 (축소에 거래량 증가를 요구하지 않음) 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"128,700 이하 하락, 종가 확인 후 (축소에 거래량 증가를 요구하지 않음) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":550500.0,"market_data_asof":"2026-10-13T13:24:00+09:00","session_vwap":524753.9652300883,"relative_volume":1.7746660227964026,"spread_bps":18.1653042688465,"day_high":552000.0,"day_low":511000.0,"execution_condition_ko":"위험 대응 조건: 560,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"560,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","data_status_ko":"시세 유효기간 만료","reference_strategy":{"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","decision_state_ko":"실행 조건 감시 중","market_data_asof":"2026-10-13T13:24:00+09:00"},"quality_at_build":{"execution_ready":false,"current_execution_promotion":"BLOCKED","generated_in_current_run":true,"row_valid_until":"2026-10-13T13:54:00+09:00","expired_at_build":true,"provider_limitations":[],"provider_blockers":["work_packet_row_expired"]}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-10-13T16:06:10.095446+09:00",
  "as_of": "2026-10-13T13:24:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
