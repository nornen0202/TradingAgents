# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-10-01T01:29:58.170000+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20261001T095551_github-actions-overlay-kr",
  "producer_finished_at": "2026-10-01T09:59:03.706294+09:00",
  "analysis_run_id": "20261001T051750_github-actions-kr",
  "analysis_completed_at": "2026-10-01T07:24:53.603805+09:00",
  "analysis_trade_date_oldest": "2026-09-30",
  "analysis_trade_date_latest": "2026-09-30",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-10-01T09:56:00+09:00",
  "market_data_latest_at": "2026-10-01T09:56:00+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-10-01T09:59:01.244346+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 10920110,
    "total_unrealized_pnl_krw": -4024126,
    "settled_cash_krw": 976652,
    "available_cash_krw": 976652,
    "buying_power_krw": 976652,
    "total_equity_krw": 11896762
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1784000,
      "market_value_krw": 3568000,
      "unrealized_pnl_krw": -1867000
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
      "current_price_krw": 360000,
      "market_value_krw": 1800000,
      "unrealized_pnl_krw": -274643
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 200000,
      "market_value_krw": 800000,
      "unrealized_pnl_krw": -175000
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 653000,
      "market_value_krw": 653000,
      "unrealized_pnl_krw": -500000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 19370,
      "market_value_krw": 348660,
      "unrealized_pnl_krw": -219655
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 261750,
      "market_value_krw": 261750,
      "unrealized_pnl_krw": -112417
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 75000,
      "market_value_krw": 225000,
      "unrealized_pnl_krw": -75000
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 191100,
      "market_value_krw": 191100,
      "unrealized_pnl_krw": -91234
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 133400,
      "market_value_krw": 133400,
      "unrealized_pnl_krw": -38900
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 52600,
      "market_value_krw": 105200,
      "unrealized_pnl_krw": -13000
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 82300,
      "market_value_krw": 82300,
      "unrealized_pnl_krw": -30631
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 66700,
      "market_value_krw": 66700,
      "unrealized_pnl_krw": 12200
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":200000.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":200382.92632688253,"relative_volume":1.9277277817501772,"spread_bps":24.968789013732835,"day_high":204000.0,"day_low":198700.0,"execution_condition_ko":"위험 대응 조건: 199,864 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"199,864 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":66400.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":65697.46113569451,"relative_volume":4.644217015871055,"spread_bps":15.071590052750565,"day_high":67000.0,"day_low":63000.0,"execution_condition_ko":"위험 대응 조건: 66,000 이상 도달, 장중 확인 시 이익실현성 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"66,000 이상 도달, 장중 확인 시 이익실현성 축소","decision_state_ko":"지금 실행 검토 가능","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":133500.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":132334.72135055694,"relative_volume":1.5993770032996708,"spread_bps":7.487832272557095,"day_high":135000.0,"day_low":129800.0,"execution_condition_ko":"위험 대응 조건: 132,500 이상 도달, 장중 확인 시 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"132,500 이상 도달, 장중 확인 시 리스크 축소","decision_state_ko":"지금 실행 검토 가능","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":262000.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":262606.5290997912,"relative_volume":2.8310509405156257,"spread_bps":19.10219675262655,"day_high":269500.0,"day_low":254000.0,"execution_condition_ko":"042700.KS의 실제 거래 가능 정규장과 신선한 시세·호가·거래량 확인 / 257000원 돌파 후 261309원 상회, 같은 시간대 상대거래량 1.2배 이상 및 당일 거래량가중평균가격 유지","risk_condition_ko":"247,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":268000.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":266370.9286974085,"relative_volume":1.2498466878660193,"spread_bps":18.63932898415657,"day_high":268500.0,"day_low":264500.0,"execution_condition_ko":"005930.KS 정규장 여부와 최신 가격·거래량가중평균가·시간대가 맞는 상대거래량 확인 / 276,000원 회복 후 284,601~285,500원 돌파와 종가 확인","risk_condition_ko":"266,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":52500.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":52057.27340083972,"relative_volume":3.3245489279736544,"spread_bps":19.065776930409914,"day_high":52800.0,"day_low":50100.0,"execution_condition_ko":"083450.KQ의 검증된 정규장에서 53,400원 위 가격 유지·거래량가중평균가 상회·동시간대 상대거래량 1.2배 이상 / 53,200~53,400원 저항에서 재거부 여부","risk_condition_ko":"50,600 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":360000.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":362680.65582491073,"relative_volume":0.8085285516903171,"spread_bps":13.89854065323141,"day_high":367500.0,"day_low":359000.0,"execution_condition_ko":"373,000원 돌파는 관찰하되 단독 매수 신호로 사용하지 않음 / 375,525원 회복·거래량가중평균가 상회·상대거래량 1.2 이상 동시 확인","risk_condition_ko":"359,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":75000.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":75057.0664072002,"relative_volume":1.8075416522639312,"spread_bps":13.3422281521014,"day_high":75700.0,"day_low":73100.0,"execution_condition_ko":"75,500~75,579원 저항 회복 / 77,500원 위 종가와 검증된 비교 기준 대비 상대 거래량 1.2배 이상","risk_condition_ko":"71,200 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":82100.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":82302.90520707592,"relative_volume":2.326872377815673,"spread_bps":12.187690432663011,"day_high":84000.0,"day_low":81300.0,"execution_condition_ko":"83,260원 10일선 종가 회복 / 86,100~86,500원 회복과 상대거래량 1.2 이상 및 검증된 당일 거래량가중평균가 유지","risk_condition_ko":"78,646 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":1781000.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":1766059.0964059504,"relative_volume":1.0363247145749845,"spread_bps":5.613247263541959,"day_high":1783000.0,"day_low":1749000.0,"execution_condition_ko":"확인된 정규장에서 1,824,000원 회복, 실시간 거래량가중평균가격 상회 및 상대 거래량 1.2배 이상 / 상대 거래량 1.2배 이상으로 1,935,000원 위 마감 후 다음 확인된 거래일 지지","risk_condition_ko":"1,671,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":653000.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":649500.483784268,"relative_volume":1.7011707410559913,"spread_bps":15.32567049808429,"day_high":660000.0,"day_low":643000.0,"execution_condition_ko":"최신 정규장 체결로 681,000원과 693,000원 회복 확인 / 700,345원과 706,579원의 거래량 동반 종가 회복, 유효한 당일 거래량가중평균가격 및 비용 반영 보상 대비 위험 재평가","risk_condition_ko":"658,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":19390.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":19496.53694720882,"relative_volume":1.5164729037081603,"spread_bps":5.155968032998196,"day_high":19810.0,"day_low":19350.0,"execution_condition_ko":"20,200~20,301원 회복 시 신선한 가격·거래량·장중 거래량가중평균가격 및 비용 반영 이익 대 손실 비율 재검증 / 20,301원 위 종가와 전일 기준 20일 평균의 1.2배인 3,876,912주 이상 거래량 확인","risk_condition_ko":"19,650 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":191300.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":191889.26305450106,"relative_volume":1.2660131544597315,"spread_bps":5.228758169934641,"day_high":193700.0,"day_low":191200.0,"execution_condition_ko":"035420.KS의 실제 정규장 여부·시세 시각·거래량·당일 거래량가중평균가격 확인 / 196500원 돌파 후 198678원·201097원 유지와 시간대 보정 상대거래량 1.2 이상","risk_condition_ko":"192,800 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"033780.KS","display_name":"033780","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":176900.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":176919.98002995507,"relative_volume":0.6381464665487424,"spread_bps":5.654509471303364,"day_high":178000.0,"day_low":175700.0,"execution_condition_ko":"033780.KS의 178,200~179,700원 저항 재시험과 179,700원 초과 종가 / 175,300원 및 173,000원 지지 여부","risk_condition_ko":"173,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"332570.KQ","display_name":"332570","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":8730.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":8790.560760430064,"relative_volume":1.3319541931293508,"spread_bps":11.448196908986834,"day_high":8970.0,"day_low":8690.0,"execution_condition_ko":"2026-10-01 실제 거래일 여부와 시각이 확인된 정규장 시세·거래량 확보 / 9,190원 유지, 동시간대 비교 상대거래량 1.2 이상, 비용·갭을 반영한 손익비 재검토","risk_condition_ko":"8,610 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"128940.KS","display_name":"128940","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":502000.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":497867.14119390346,"relative_volume":0.5872775129142854,"spread_bps":19.940179461615152,"day_high":504000.0,"day_low":493500.0,"execution_condition_ko":"128940.KS의 520,000원 회복은 관찰 신호로만 취급 / 검증된 525,655원 상향 종가와 다음 실제 거래일 지지 확인","risk_condition_ko":"486,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"055550.KS","display_name":"055550","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":103900.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":104599.25168536113,"relative_volume":1.8925984052210074,"spread_bps":9.629272989889262,"day_high":106300.0,"day_low":103500.0,"execution_condition_ko":"검증된 정규장 종가 107,550원 초과와 상대거래량 1.2 이상 / 다음 거래일 107,550원 유지 및 108,800원·111,187원 회복","risk_condition_ko":"108,800 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"088350.KS","display_name":"088350","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":5250.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":5271.685602048023,"relative_volume":0.8859521792403736,"spread_bps":19.029495718363464,"day_high":5350.0,"day_low":5220.0,"execution_condition_ko":"신선한 정규장 가격의 5,320원 및 갱신된 50일 평균 시험 / 상대거래량 1.2배 이상과 당일 거래량가중평균가를 동반한 5,487.8~5,550원 회복","risk_condition_ko":"5,320 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"486510.KQ","display_name":"486510","is_held":false,"strategy_code":"WAIT_CLOSE","strategy_ko":"종가 확인 후 판단","last_price":18800.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":18607.030100779473,"relative_volume":0.6401440136329954,"spread_bps":5.320563979781857,"day_high":19460.0,"day_low":17230.0,"execution_condition_ko":"486510.KQ의 2026-09-30 거래소 일봉으로 19,100원과 14,900원 충돌 확인 / 실제 정규장 가격·거래량·호가 차이·거래량가중평균가격 확인","risk_condition_ko":"19,100 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족, 종가 확인 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"010950.KS","display_name":"S-Oil","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":155400.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":157290.55791843883,"relative_volume":0.6879061640608147,"spread_bps":6.43293663557414,"day_high":162000.0,"day_low":154200.0,"execution_condition_ko":"정규장 일정·현재 호가·당일 거래량가중평균가격·동일 시간대 거래량 기준 검증 / 165900원 위 종가와 상대 거래량 1.2 이상, 다음 거래일 164800~165900원 지지","risk_condition_ko":"155,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"000810.KS","display_name":"000810","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":624000.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":628500.2268945697,"relative_volume":0.47973879082369814,"spread_bps":32.05128205128205,"day_high":636000.0,"day_low":621000.0,"execution_condition_ko":"644,440원 회복 / 652,183~655,758원 위 유지와 동시간대 최근 20거래일 대비 상대거래량 1.2 이상","risk_condition_ko":"626,000 이하 하락, 종가 확인 후 (거래량 증가 동반) 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"180640.KS","display_name":"180640","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":132300.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":132549.0970131975,"relative_volume":0.7182022027257142,"spread_bps":7.555723460521345,"day_high":134800.0,"day_low":131100.0,"execution_condition_ko":"10월 1일 실제 정규장 여부, 실시간 호가·거래량·장중 가중평균가격 확인 / 137922~138870원 회복과 동시간대 상대 거래량 1.2 이상, 이후 140500원 확인","risk_condition_ko":"129,595 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":510000.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":508419.77007276955,"relative_volume":1.0137517382108305,"spread_bps":19.62708537782139,"day_high":514000.0,"day_low":503000.0,"execution_condition_ko":"실제 정규 거래일 및 신선한 호가·거래량 확인 / 528,000원 유지, 당일 거래량가중평균가격 상회, 동일 시각대 상대거래량 1.2 이상","risk_condition_ko":"505,000 이하 하락, 다음 거래일 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":145600.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":147242.25237673149,"relative_volume":0.8314828453002743,"spread_bps":13.745704467353953,"day_high":149900.0,"day_low":145100.0,"execution_condition_ko":"위험 대응 조건: 144,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"144,100 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"062040.KS","display_name":"062040","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":205000.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":205208.32785764974,"relative_volume":0.9983086512245136,"spread_bps":24.42002442002442,"day_high":208500.0,"day_low":203000.0,"execution_condition_ko":"위험 대응 조건: 208,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"208,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"009150.KS","display_name":"삼성전기","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":1485000.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":1476565.8067881865,"relative_volume":1.6245747499883616,"spread_bps":6.736274840013472,"day_high":1495000.0,"day_low":1462000.0,"execution_condition_ko":"위험 대응 조건: 1,499,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"1,499,000 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":136400.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":137556.07144918336,"relative_volume":0.615956260238216,"spread_bps":7.334066740007334,"day_high":139300.0,"day_low":136300.0,"execution_condition_ko":"위험 대응 조건: 135,700 이하 하락, 거래량 조건 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"135,700 이하 하락, 거래량 조건 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"047040.KS","display_name":"047040","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":17700.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":17726.522279997684,"relative_volume":1.7661804741904734,"spread_bps":5.648121999435189,"day_high":18200.0,"day_low":17440.0,"execution_condition_ko":"위험 대응 조건: 17,150 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"17,150 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"000150.KS","display_name":"두산","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":1390000.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":1393037.258402546,"relative_volume":1.1098147924442587,"spread_bps":14.398848092152628,"day_high":1412000.0,"day_low":1379000.0,"execution_condition_ko":"위험 대응 조건: 1,361,000 이하 하락, 종가 확인 후 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"1,361,000 이하 하락, 종가 확인 후 리스크 축소","decision_state_ko":"실행 조건 감시 중","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
```

```json
{"ticker":"105560.KS","display_name":"105560","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":166200.0,"market_data_asof":"2026-10-01T09:56:00+09:00","session_vwap":167743.9259078594,"relative_volume":2.4391296579193926,"spread_bps":6.018657839301836,"day_high":169300.0,"day_low":166000.0,"execution_condition_ko":"위험 대응 조건: 167,800 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"167,800 이하 하락, 종가 확인 후 신규 진입 보류·보유 위험 대응 계획 재확인","decision_state_ko":"실행 조건 감시 중","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-10-01T10:26:00+09:00"}}
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
