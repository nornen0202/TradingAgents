# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-09-30T22:45:30.590469+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261001T051750_github-actions-kr",
  "producer_finished_at": "2026-10-01T07:39:45.515394+09:00",
  "analysis_run_id": "20261001T051750_github-actions-kr",
  "analysis_completed_at": "2026-10-01T07:24:53.603805+09:00",
  "analysis_trade_date_oldest": "2026-09-30",
  "analysis_trade_date_latest": "2026-09-30",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": null,
  "market_data_latest_at": null,
  "market_data_status": "MISSING"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-01T07:25:06.193064+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 10953800,
    "total_unrealized_pnl_krw": -3990436,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 11930452
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1776000,
      "market_value_krw": 3552000,
      "unrealized_pnl_krw": -1883000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 268500,
      "market_value_krw": 2685000,
      "unrealized_pnl_krw": -638851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 366000,
      "market_value_krw": 1830000,
      "unrealized_pnl_krw": -244643
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 205000,
      "market_value_krw": 820000,
      "unrealized_pnl_krw": -155000
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 662000,
      "market_value_krw": 662000,
      "unrealized_pnl_krw": -491000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 19700,
      "market_value_krw": 354600,
      "unrealized_pnl_krw": -213715
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 256500,
      "market_value_krw": 256500,
      "unrealized_pnl_krw": -117667
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 73400,
      "market_value_krw": 220200,
      "unrealized_pnl_krw": -79800
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 193700,
      "market_value_krw": 193700,
      "unrealized_pnl_krw": -88634
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 132500,
      "market_value_krw": 132500,
      "unrealized_pnl_krw": -39800
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 51000,
      "market_value_krw": 102000,
      "unrealized_pnl_krw": -16200
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 81600,
      "market_value_krw": 81600,
      "unrealized_pnl_krw": -31331
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 63700,
      "market_value_krw": 63700,
      "unrealized_pnl_krw": 9200
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"005930.KS 정규장 여부와 최신 가격·거래량가중평균가·시간대가 맞는 상대거래량 확인 / 276,000원 회복 후 284,601~285,500원 돌파와 종가 확인","risk_condition_ko":"266,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"최신 정규장 체결로 681,000원과 693,000원 회복 확인 / 700,345원과 706,579원의 거래량 동반 종가 회복, 유효한 당일 거래량가중평균가격 및 비용 반영 보상 대비 위험 재평가","risk_condition_ko":"658,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"10월 1일 장 상태, 실시간 가격·거래량가중평균가격·동시간대 거래량 확인 / 133550 돌파 및 상대 거래량 1.2 이상 유지","risk_condition_ko":"132,500 이상 도달, 장중 확인 시 리스크 축소","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"20,200~20,301원 회복 시 신선한 가격·거래량·장중 거래량가중평균가격 및 비용 반영 이익 대 손실 비율 재검증 / 20,301원 위 종가와 전일 기준 20일 평균의 1.2배인 3,876,912주 이상 거래량 확인","risk_condition_ko":"19,650 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"확인된 정규장 종가 214500원 초과 및 거래량 388917주 초과 / 다음 실제 거래일의 214500원 유지 또는 회복과 218500원 돌파 여부","risk_condition_ko":"199,864 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"75,500~75,579원 저항 회복 / 77,500원 위 종가와 검증된 비교 기준 대비 상대 거래량 1.2배 이상","risk_condition_ko":"71,200 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"035420.KS의 실제 정규장 여부·시세 시각·거래량·당일 거래량가중평균가격 확인 / 196500원 돌파 후 198678원·201097원 유지와 시간대 보정 상대거래량 1.2 이상","risk_condition_ko":"192,800 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"정규장 66,000원 위 안착과 비교 가능한 상대거래량 1.2 이상 확인 / 61,000~60,300원 지지와 거래량 회복 확인","risk_condition_ko":"66,000 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"042700.KS의 실제 거래 가능 정규장과 신선한 시세·호가·거래량 확인 / 257000원 돌파 후 261309원 상회, 같은 시간대 상대거래량 1.2배 이상 및 당일 거래량가중평균가격 유지","risk_condition_ko":"247,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"083450.KQ의 검증된 정규장에서 53,400원 위 가격 유지·거래량가중평균가 상회·동시간대 상대거래량 1.2배 이상 / 53,200~53,400원 저항에서 재거부 여부","risk_condition_ko":"50,600 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"373,000원 돌파는 관찰하되 단독 매수 신호로 사용하지 않음 / 375,525원 회복·거래량가중평균가 상회·상대거래량 1.2 이상 동시 확인","risk_condition_ko":"359,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"83,260원 10일선 종가 회복 / 86,100~86,500원 회복과 상대거래량 1.2 이상 및 검증된 당일 거래량가중평균가 유지","risk_condition_ko":"78,646 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"확인된 정규장에서 1,824,000원 회복, 실시간 거래량가중평균가격 상회 및 상대 거래량 1.2배 이상 / 상대 거래량 1.2배 이상으로 1,935,000원 위 마감 후 다음 확인된 거래일 지지","risk_condition_ko":"1,671,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"검증된 정규장에서 151500원 돌파, 동시간대 상대거래량 1.2 이상 및 당일 거래량가중평균가격 상회 확인 / 156400~156860원 저항 구간의 거래량 동반 종가 돌파 확인","risk_condition_ko":"144,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"033780.KS의 178,200~179,700원 저항 재시험과 179,700원 초과 종가 / 175,300원 및 173,000원 지지 여부","risk_condition_ko":"173,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"062040.KS","display_name":"062040","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-10-01 정규장 여부와 시각이 확인된 가격·거래량·장중 거래량 가중 평균가격 확보 / 215000원 돌파 시 동일 시각 상대 거래량 1.2 이상 확인 후 215758원과 225000원 저항 평가","risk_condition_ko":"208,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"055550.KS","display_name":"055550","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"검증된 정규장 종가 107,550원 초과와 상대거래량 1.2 이상 / 다음 거래일 107,550원 유지 및 108,800원·111,187원 회복","risk_condition_ko":"108,800 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"090430.KS의 실제 정규장 운영 여부와 신선한 호가·체결·동시간대 거래량 확인 / 142,029~142,298원 회복과 143,700원 돌파, 상대거래량 1.2배 이상 확인","risk_condition_ko":"135,700 이하 하락, 거래량 조건 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"332570.KQ","display_name":"332570","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-10-01 실제 거래일 여부와 시각이 확인된 정규장 시세·거래량 확보 / 9,190원 유지, 동시간대 비교 상대거래량 1.2 이상, 비용·갭을 반영한 손익비 재검토","risk_condition_ko":"8,610 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"128940.KS","display_name":"128940","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"128940.KS의 520,000원 회복은 관찰 신호로만 취급 / 검증된 525,655원 상향 종가와 다음 실제 거래일 지지 확인","risk_condition_ko":"486,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"000150.KS","display_name":"두산","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"확인된 정규장에서 1,390,931~1,404,000원 회복, 유효한 당일 거래량가중평균가격 상회 및 동시간대 상대거래량 1.2 이상 확인 / 1,404,000원 위 정규장 종가와 실제 익거래일 초반 지지 또는 재돌파 확인","risk_condition_ko":"1,361,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"047040.KS","display_name":"047040","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-09-30의 17,740원과 17,770원 차이를 공식 종가로 확인 / 확인된 정규장에서 18,260원 및 18,318원 회복, 장중 거래량가중평균가격 상회, 상대거래량 1.2 이상","risk_condition_ko":"17,150 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"105560.KS","display_name":"105560","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"167800~168165원 지지와 정규장 거래량 안정 확인 / 170885원 회복과 거래량가중평균가격 상회 및 같은 시각 기준 상대거래량 1.2 이상 확인","risk_condition_ko":"167,800 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"000810.KS","display_name":"000810","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"644,440원 회복 / 652,183~655,758원 위 유지와 동시간대 최근 20거래일 대비 상대거래량 1.2 이상","risk_condition_ko":"626,000 이하 하락, 종가 확인 후 (거래량 증가 동반) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"088350.KS","display_name":"088350","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"신선한 정규장 가격의 5,320원 및 갱신된 50일 평균 시험 / 상대거래량 1.2배 이상과 당일 거래량가중평균가를 동반한 5,487.8~5,550원 회복","risk_condition_ko":"5,320 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"180640.KS","display_name":"180640","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"10월 1일 실제 정규장 여부, 실시간 호가·거래량·장중 가중평균가격 확인 / 137922~138870원 회복과 동시간대 상대 거래량 1.2 이상, 이후 140500원 확인","risk_condition_ko":"129,595 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"009150.KS","display_name":"삼성전기","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"2026-10-01의 실제 정규장 여부와 009150.KS의 시각이 표시된 신규 시세 확인 / 1,579,000~1,587,000원 돌파 여부와 정제된 20일 평균 대비 거래량 확인","risk_condition_ko":"1,499,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"486510.KQ","display_name":"486510","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"486510.KQ의 2026-09-30 거래소 일봉으로 19,100원과 14,900원 충돌 확인 / 실제 정규장 가격·거래량·호가 차이·거래량가중평균가격 확인","risk_condition_ko":"19,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"010950.KS","display_name":"S-Oil","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"정규장 일정·현재 호가·당일 거래량가중평균가격·동일 시간대 거래량 기준 검증 / 165900원 위 종가와 상대 거래량 1.2 이상, 다음 거래일 164800~165900원 지지","risk_condition_ko":"155,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"DATA_CHECK","strategy_ko":"데이터 확인 전 대기","last_price":null,"market_data_asof":null,"session_vwap":null,"relative_volume":null,"spread_bps":null,"day_high":null,"day_low":null,"execution_condition_ko":"실제 정규 거래일 및 신선한 호가·거래량 확인 / 528,000원 유지, 당일 거래량가중평균가격 상회, 동일 시각대 상대거래량 1.2 이상","risk_condition_ko":"505,000 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"-","quality_at_build":{"execution_ready":false,"current_execution_promotion":null,"generated_in_current_run":false,"row_valid_until":null}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-09-30T18:21:50.160711+09:00",
  "as_of": "2026-09-30T14:56:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
