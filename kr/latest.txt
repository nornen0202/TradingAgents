# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-09-30T20:03:24.661285+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20260930T145600_github-actions-overlay-kr",
  "producer_finished_at": "2026-09-30T15:07:03.700807+09:00",
  "analysis_run_id": "20260930T081017_github-actions-kr",
  "analysis_completed_at": "2026-09-30T10:43:22.634373+09:00",
  "analysis_trade_date_oldest": "2026-09-29",
  "analysis_trade_date_latest": "2026-09-29",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-09-30T14:56:00+09:00",
  "market_data_latest_at": "2026-09-30T14:56:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-09-30T15:07:34.542646+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 10966130,
    "total_unrealized_pnl_krw": -3978106,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 11942782
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1781000,
      "market_value_krw": 3562000,
      "unrealized_pnl_krw": -1873000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 269500,
      "market_value_krw": 2695000,
      "unrealized_pnl_krw": -628851
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 364500,
      "market_value_krw": 1822500,
      "unrealized_pnl_krw": -252143
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 205500,
      "market_value_krw": 822000,
      "unrealized_pnl_krw": -153000
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 661000,
      "market_value_krw": 661000,
      "unrealized_pnl_krw": -492000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 19710,
      "market_value_krw": 354780,
      "unrealized_pnl_krw": -213535
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 255500,
      "market_value_krw": 255500,
      "unrealized_pnl_krw": -118667
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 73500,
      "market_value_krw": 220500,
      "unrealized_pnl_krw": -79500
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 193100,
      "market_value_krw": 193100,
      "unrealized_pnl_krw": -89234
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
      "current_price_krw": 81550,
      "market_value_krw": 81550,
      "unrealized_pnl_krw": -31381
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
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":73400.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":73915.50482585163,"relative_volume":0.6901449723987334,"spread_bps":13.614703880190605,"day_high":75500.0,"day_low":72600.0,"execution_condition_ko":"058470.KQ의 현재 정규장 시세·거래량·거래량가중평균가격 및 보유 위험 확인 / 75,000~77,500원 저항 구간의 거래량 반응","risk_condition_ko":"70,700 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":51000.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":51821.81125630841,"relative_volume":1.4628695822560533,"spread_bps":19.62708537782139,"day_high":53400.0,"day_low":50600.0,"execution_condition_ko":"2026-09-30 장중 가격·거래량가중평균가격·상대거래량 검증 / 상대거래량 1.2 이상을 동반한 53,400원 위 종가","risk_condition_ko":"50,400 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":205500.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":206119.6734441015,"relative_volume":0.5084905374036508,"spread_bps":24.360535931790498,"day_high":209500.0,"day_low":203500.0,"execution_condition_ko":"219500원 상향 종가와 거래량 379200주 이상, 이후 다음 거래일 지지 여부 / 201500원부터 199600원까지의 지지 구간 시험","risk_condition_ko":"199,600 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":364500.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":364663.33918157045,"relative_volume":0.6717180238715992,"spread_bps":13.726835964310226,"day_high":373000.0,"day_low":359000.0,"execution_condition_ko":"365066원·367292원 회복 후 372500원 시험 / 379049원 초과 종가와 거래량 약 194000주 이상, 다음 거래일 지지","risk_condition_ko":"358,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":270500.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":271128.7765093168,"relative_volume":0.7693051926622614,"spread_bps":18.501387604070306,"day_high":276000.0,"day_low":267500.0,"execution_condition_ko":"285,500원 초과 종가와 20,864,376주 초과 거래량 / 266,000~268,700원 지지 구간의 실제 반등","risk_condition_ko":"266,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":662000.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":675524.6822073791,"relative_volume":2.7970664975961195,"spread_bps":15.117157974300833,"day_high":693000.0,"day_low":658000.0,"execution_condition_ko":"693,000원 위 일봉 종가 회복 / 709,000원 위 일봉 종가와 상대거래량 1.2 이상","risk_condition_ko":"670,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":19710.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":19906.98995293086,"relative_volume":0.9487161821483158,"spread_bps":5.07227998985544,"day_high":20200.0,"day_low":19650.0,"execution_condition_ko":"상대 거래량 1.2배 이상을 동반한 20,250원 위 일일 종가 / 20,435원 위 일일 종가 이후 다음 거래일 20,250원 지지","risk_condition_ko":"19,160 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":132500.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":131264.333509825,"relative_volume":0.8361561767928993,"spread_bps":7.538635506973238,"day_high":133550.0,"day_low":128000.0,"execution_condition_ko":"130300원 초과 종가와 일간 거래량 1523919주 이상, 이어지는 거래일의 가격 지지 / 123300원 또는 121400~121500원에서 지지 확인","risk_condition_ko":"130,300 이상 도달, 장중 확인 시 리스크 축소","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":63700.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":63594.888782617854,"relative_volume":1.6114307505536054,"spread_bps":15.686274509803921,"day_high":66000.0,"day_low":60100.0,"execution_condition_ko":"상대거래량 1.2 이상을 동반한 61,500원 초과 일간 종가 / 60,300원 재시험 후 일간 종가 지지와 다음 거래일 유지","risk_condition_ko":"60,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":81500.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":81337.77786554472,"relative_volume":0.45731521765124067,"spread_bps":12.277470841006751,"day_high":82200.0,"day_low":80300.0,"execution_condition_ko":"034020.KS가 82,000원 위에서 당일 거래량 가중 평균가격을 웃돌고 동시간대 상대 거래량이 1.2배 이상인지 확인 / 82,000원 위 종가와 일 거래량 2,146,662주 초과 여부, 다음 거래일 첫 30~60분 지지 또는 재돌파 확인","risk_condition_ko":"78,408 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":1790000.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":1794966.8053326735,"relative_volume":0.8099131704806316,"spread_bps":5.585032113934655,"day_high":1824000.0,"day_low":1773000.0,"execution_condition_ko":"000660.KS의 1,804,000원 초과 종가와 3,238,000주 초과 거래량 / 다음 거래일 1,804,000원과 당일 거래량가중평균가격 지지","risk_condition_ko":"1,690,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":193100.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":194338.48646501332,"relative_volume":0.616945102574354,"spread_bps":5.177323323841574,"day_high":196500.0,"day_low":192800.0,"execution_condition_ko":"200500원 위 종가와 697389주 초과 거래량은 자동 매수가 아닌 재평가 신호 / 202357원 회복과 다음 거래일 200500원 지지","risk_condition_ko":"193,200 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":256500.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":253234.6884983564,"relative_volume":0.5988429779811824,"spread_bps":19.51219512195122,"day_high":256500.0,"day_low":247000.0,"execution_condition_ko":"042700.KS의 최신 정규장 가격과 거래량 확인 / 258000원 초과 종가와 744200주 이상 거래량, 다음 거래일 지지 여부","risk_condition_ko":"240,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족, 종가 확인 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"007660.KS","display_name":"이수페타시스","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":114800.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":116163.48145378247,"relative_volume":0.8131879198494495,"spread_bps":8.707009142359599,"day_high":118900.0,"day_low":114100.0,"execution_condition_ko":"119,800원 초과 종가와 일일 거래량 929,301주 초과 여부 / 확인된 돌파 다음 거래일 첫 30~60분의 119,800원 및 당일 거래량가중평균가 유지 여부","risk_condition_ko":"112,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"000150.KS","display_name":"두산","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":1368000.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":1381088.1395475015,"relative_volume":0.49740116427404796,"spread_bps":7.312614259597806,"day_high":1404000.0,"day_low":1364000.0,"execution_condition_ko":"1,361,000원 지지 여부 / 1,399,000원 회복 뒤 1,413,000원 상향 돌파, 상대 거래량 1.2배 이상 및 당일 거래량가중평균가격 상회 여부","risk_condition_ko":"1,361,000 이하 하락, 2개 봉 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"009150.KS","display_name":"삼성전기","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":1517000.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":1530337.6116211168,"relative_volume":0.7730923592456934,"spread_bps":6.5897858319604605,"day_high":1579000.0,"day_low":1508000.0,"execution_condition_ko":"1,587,000원 초과 일봉 마감과 거래량 908,255주 이상 / 다음 거래일 1,587,000원 유지 또는 재돌파와 당일 거래량가중평균가격 회복","risk_condition_ko":"1,493,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":515000.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":514696.07658539736,"relative_volume":0.566747047372166,"spread_bps":19.398642095053347,"day_high":525000.0,"day_low":510000.0,"execution_condition_ko":"006400.KS의 505,000원 종가 지지 여부 / 521,000원 회복은 관찰하되 단독 매수 신호로 사용하지 않음","risk_condition_ko":"505,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":149100.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":149244.55803023413,"relative_volume":0.42003913525597636,"spread_bps":6.704659738518271,"day_high":151500.0,"day_low":146000.0,"execution_condition_ko":"144100~144570원 지지 및 146705원 회복을 당일 거래량가중평균가격·상대거래량과 함께 확인 / 149200원 위 거래량 동반 종가와 다음 거래일 유지 여부","risk_condition_ko":"144,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":138800.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":138843.56634208886,"relative_volume":1.2580071099357526,"spread_bps":7.207207207207207,"day_high":143700.0,"day_low":135700.0,"execution_condition_ko":"149400원 위 종가와 250000주 이상 거래, 이후 다음 거래일 지지 또는 재돌파 / 140200~141100원 구간에서 지지와 거래량 동반 반등 확인","risk_condition_ko":"140,200 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"128940.KS","display_name":"128940","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":499500.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":502293.00911158253,"relative_volume":0.6214547440340505,"spread_bps":10.005002501250624,"day_high":517000.0,"day_low":486000.0,"execution_condition_ko":"2026-09-29 이후 가격·거래량을 확인하고 520000원 초과 종가와 126975주 초과 거래량 감시 / 다음 거래일 520000원 유지, 525125원 확인 및 528000~534000원 저항 돌파 여부","risk_condition_ko":"490,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":176500.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":176993.03180215866,"relative_volume":0.9215429581262667,"spread_bps":5.667327854916407,"day_high":179700.0,"day_low":175700.0,"execution_condition_ko":"179000원 초과 종가와 277200주 초과 거래량 / 다음 거래일 첫 30~60분에 178800~179000원 유지 또는 회복","risk_condition_ko":"175,300 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"062040.KS","display_name":"062040","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":213500.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":211625.6197919479,"relative_volume":0.8960804845461264,"spread_bps":23.446658851113714,"day_high":215000.0,"day_low":208000.0,"execution_condition_ko":"10:30 이후 215,000원 초과·당일 거래량가중평균가 상회·예상 상대거래량 1.0 이상 여부 / 215,000원 위 종가와 거래량 272,056주 이상, 다음 거래일 첫 30~60분 안착 또는 재돌파","risk_condition_ko":"199,800 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"086790.KS","display_name":"086790","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":129900.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":130680.3533664291,"relative_volume":1.057018190610217,"spread_bps":7.695267410542517,"day_high":135700.0,"day_low":128600.0,"execution_condition_ko":"135,500~136,700원 회복 구간과 거래량 증가 / 136,700원 위 종가 및 다음 거래일 지지","risk_condition_ko":"132,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"055550.KS","display_name":"055550","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":106300.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":107437.53845077188,"relative_volume":0.9712909205719167,"spread_bps":9.411764705882353,"day_high":110800.0,"day_low":105500.0,"execution_condition_ko":"111800원 회복 후 112200원 돌파 여부 / 113300원 위 종가와 거래량 1110000주 이상, 이후 지지 재확인","risk_condition_ko":"108,800 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"093370.KS","display_name":"093370","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":15030.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":15033.741877234908,"relative_volume":2.51450675131944,"spread_bps":6.655574043261232,"day_high":15500.0,"day_low":14140.0,"execution_condition_ko":"14,520원 위 종가와 거래량 2,931,423주 이상 / 13,950~13,968원 지지와 회복 여부","risk_condition_ko":"13,610 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"000810.KS","display_name":"000810","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":629000.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":637401.099677159,"relative_volume":0.5569325291259467,"spread_bps":15.885623510722795,"day_high":660000.0,"day_low":626000.0,"execution_condition_ko":"000810.KS의 642,000~646,000원 지지와 거래량 동반 반등 종가 / 000810.KS의 668,000원 상회 종가, 상대거래량 1.2배 이상 및 다음 거래일 지지","risk_condition_ko":"642,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
```

```json
{"ticker":"105560.KS","display_name":"105560","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":168850.0,"market_data_asof":"2026-09-30T14:56:00+09:00","session_vwap":170297.4226775051,"relative_volume":0.7553122251674355,"spread_bps":5.922416345869114,"day_high":173600.0,"day_low":167800.0,"execution_condition_ko":"174935원 회복 후 175702원 거래량 동반 돌파 여부 / 다음 거래일 첫 30~60분 동안 175702원 유지 여부","risk_condition_ko":"170,200 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-30T15:26:00+09:00"}}
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
