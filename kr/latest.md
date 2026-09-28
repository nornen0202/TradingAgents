# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-09-28T18:25:23.695317+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20260928T145549_github-actions-overlay-kr",
  "producer_finished_at": "2026-09-28T14:56:28.294069+09:00",
  "analysis_run_id": "20260928T050548_github-actions-kr",
  "analysis_completed_at": "2026-09-28T07:21:24.610166+09:00",
  "analysis_trade_date_oldest": "2026-09-23",
  "analysis_trade_date_latest": "2026-09-23",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-09-28T14:56:00+09:00",
  "market_data_latest_at": "2026-09-28T14:56:15.533380+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-09-28T14:56:41.649975+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 10998900,
    "total_unrealized_pnl_krw": -3945336,
    "settled_cash_krw": 975902,
    "available_cash_krw": 975902,
    "buying_power_krw": 975902,
    "total_equity_krw": 11974802
  },
  "positions": [
    {
      "ticker": "000660.KS",
      "name": "SK하이닉스",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 2717500,
      "current_price_krw": 1783000,
      "market_value_krw": 3566000,
      "unrealized_pnl_krw": -1869000
    },
    {
      "ticker": "005930.KS",
      "name": "삼성전자",
      "quantity": 10.0,
      "sellable_quantity": 10.0,
      "average_cost_krw": 332385,
      "current_price_krw": 271750,
      "market_value_krw": 2717500,
      "unrealized_pnl_krw": -606351
    },
    {
      "ticker": "278470.KS",
      "name": "에이피알",
      "quantity": 5.0,
      "sellable_quantity": 5.0,
      "average_cost_krw": 414928,
      "current_price_krw": 368500,
      "market_value_krw": 1842500,
      "unrealized_pnl_krw": -232143
    },
    {
      "ticker": "010120.KS",
      "name": "LS ELECTRIC",
      "quantity": 4.0,
      "sellable_quantity": 4.0,
      "average_cost_krw": 243750,
      "current_price_krw": 203000,
      "market_value_krw": 812000,
      "unrealized_pnl_krw": -163000
    },
    {
      "ticker": "267260.KS",
      "name": "HD현대일렉트릭",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 1153000,
      "current_price_krw": 693000,
      "market_value_krw": 693000,
      "unrealized_pnl_krw": -460000
    },
    {
      "ticker": "010140.KS",
      "name": "삼성중공업",
      "quantity": 18.0,
      "sellable_quantity": 18.0,
      "average_cost_krw": 31573,
      "current_price_krw": 20100,
      "market_value_krw": 361800,
      "unrealized_pnl_krw": -206515
    },
    {
      "ticker": "042700.KS",
      "name": "한미반도체",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 374167,
      "current_price_krw": 234500,
      "market_value_krw": 234500,
      "unrealized_pnl_krw": -139667
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 71400,
      "market_value_krw": 214200,
      "unrealized_pnl_krw": -85800
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 197200,
      "market_value_krw": 197200,
      "unrealized_pnl_krw": -85134
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 123900,
      "market_value_krw": 123900,
      "unrealized_pnl_krw": -48400
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 49350,
      "market_value_krw": 98700,
      "unrealized_pnl_krw": -19500
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
      "current_price_krw": 56000,
      "market_value_krw": 56000,
      "unrealized_pnl_krw": 1500
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"SELL","strategy_ko":"매도·청산 검토","last_price":1783000.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":1794251.5011411721,"relative_volume":0.8904601229669494,"spread_bps":5.60695262125035,"day_high":1840000.0,"day_low":1769000.0,"execution_condition_ko":"위험 대응 조건: 1,832,000 이탈 시 손절 조건 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"1,832,000 이탈 시 손절 조건","decision_state_ko":"투자 근거 무효화","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":235000.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":239313.88843061164,"relative_volume":0.47652399752941016,"spread_bps":21.253985122210413,"day_high":245000.0,"day_low":234000.0,"execution_condition_ko":"위험 대응 조건: 239,000 이탈 시 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"239,000 이탈 시 리스크 축소","decision_state_ko":"실행 조건 감시 중","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":71500.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":72505.44507152935,"relative_volume":0.6951809848066064,"spread_bps":13.995801259622112,"day_high":74300.0,"day_low":71200.0,"execution_condition_ko":"058470.KQ 최신 정규장 가격·거래량·장중 거래량가중평균가격 확인 / 77,500원 초과 종가 및 일일 거래량 1,795,192주 이상 확인","risk_condition_ko":"71,500 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":123900.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":125250.28461586709,"relative_volume":1.4699129794824466,"spread_bps":8.074283407347597,"day_high":129100.0,"day_low":121400.0,"execution_condition_ko":"353200.KS의 상충하는 2026-09-23 종가를 거래소 기록과 대조하고 최신 시세 확인 / 상대 거래량 1.2 이상, 일일 거래량 1578412주 초과를 동반한 종가 120700 상회","risk_condition_ko":"117,053 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":20050.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":20210.486475915397,"relative_volume":0.6160402340786713,"spread_bps":24.906600249066003,"day_high":20550.0,"day_low":20050.0,"execution_condition_ko":"최신 주가·거래량과 2026-09-27~28 보도 이후 가격 반응 확인 / 20,200원 및 19,900원 지지 여부 확인","risk_condition_ko":"19,900 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":694000.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":696660.87816408,"relative_volume":0.8225392165520229,"spread_bps":14.419610670511895,"day_high":709000.0,"day_low":689000.0,"execution_condition_ko":"현재 가격·거래량·실시간 거래량가중평균가격·공시 확인 / 720,000~723,000원 회복 후 727,403원 돌파와 상대 거래량 1.2배 이상","risk_condition_ko":"698,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":368500.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":369533.10930861335,"relative_volume":0.5656171640628359,"spread_bps":13.577732518669382,"day_high":377500.0,"day_low":364500.0,"execution_condition_ko":"2026-09-23 이후 최신 종가로 357000원·350500원 지지 여부 확인 / 373500원 회복 시 거래량과 379518~381500원 저항 돌파 여부 관찰","risk_condition_ko":"350,500 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":49250.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":49660.91886437965,"relative_volume":0.7692572049329164,"spread_bps":10.147133434804667,"day_high":50400.0,"day_low":48800.0,"execution_condition_ko":"최신 가격·거래량·호가 스프레드·공시 확인 / 50,100원 위 종가와 실제 거래량 106,762주 이상","risk_condition_ko":"48,300 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":271500.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":276142.2243865724,"relative_volume":1.076610208027434,"spread_bps":18.39926402943882,"day_high":285500.0,"day_low":271000.0,"execution_condition_ko":"최신 종가·장중 가격·거래량·거래량가중평균가격 확보 / 2026-09-29 배당락 조건·확정 배당액 확인과 가격선 재설정","risk_condition_ko":"276,500 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":56000.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":56091.08755808097,"relative_volume":0.7607807515549969,"spread_bps":17.84121320249777,"day_high":57200.0,"day_low":54800.0,"execution_condition_ko":"403870.KQ의 53,763~54,326원 지지 재확인, 당일 거래량가중평균가격 회복 및 상대 거래량 1.2배 / 56,556원 상향 마감과 약 177만 주 이상 거래 후 57,600원 돌파 확인","risk_condition_ko":"53,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":81500.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":82031.60806464302,"relative_volume":0.49388015614359737,"spread_bps":12.26241569589209,"day_high":83000.0,"day_low":80900.0,"execution_condition_ko":"현재 시세 확인 후 85,057원 회복, 86,100원 돌파, 87,049원 상향 안착 여부 / 80,500원 지지선 검사와 이탈 시 78,052원·76,986원 확인","risk_condition_ko":"80,500 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":203000.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":204738.12665441624,"relative_volume":0.6546074022651353,"spread_bps":24.600246002460025,"day_high":209500.0,"day_low":201000.0,"execution_condition_ko":"010120.KS의 새로운 가격·거래량·거래량가중평균가와 상대 거래량 확보 / 199158~203000원 구간의 거래량 동반 회복","risk_condition_ko":"199,158 이탈 시 전략 재평가","decision_state_ko":"실행 조건 감시 중","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":197200.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":198382.10815351852,"relative_volume":0.9362995695865278,"spread_bps":5.069708491761723,"day_high":200500.0,"day_low":194300.0,"execution_condition_ko":"035420.KS의 최신 가격·거래량과 실제 보유 비중 확인 / 201600 위 종가와 상대 거래량 1.2배 이상이면 손익비를 다시 평가","risk_condition_ko":"194,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"108490.KQ","display_name":"로보티즈","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":283500.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":290775.1300340545,"relative_volume":0.4614694263894198,"spread_bps":17.6522506619594,"day_high":300000.0,"day_low":282000.0,"execution_condition_ko":"현재 가격·거래량·기업행위와 2026-09-23 이후 공시 확인 / 현재 자료로 재산출한 10일 지수이동평균 및 거래량가중 평균 회복","risk_condition_ko":"297,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":534000.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":532912.5405620578,"relative_volume":0.784344190037861,"spread_bps":18.744142455482663,"day_high":540000.0,"day_low":524000.0,"execution_condition_ko":"006400.KS의 최신 한국거래소 가격·거래량·당일 거래량가중평균가와 기존 보유 비중 확인 / 529000원 회복 후 상대거래량 1.2 이상으로 535794원 위 마감","risk_condition_ko":"510,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"298040.KS","display_name":"효성중공업","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":2780000.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":2809604.834574901,"relative_volume":0.9863033930645837,"spread_bps":3.597769382982551,"day_high":2925000.0,"day_low":2771000.0,"execution_condition_ko":"위험 대응 조건: 2,828,000 이탈 시 전략 재평가 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"2,828,000 이탈 시 전략 재평가","decision_state_ko":"실행 조건 감시 중","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":157600.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":157737.95303674074,"relative_volume":0.9660481289854977,"spread_bps":6.343165239454487,"day_high":161200.0,"day_low":147600.0,"execution_condition_ko":"096770.KS의 153500원 돌파 및 갱신된 최근 5거래일 평균 대비 1.2배 이상 거래량을 동반한 종가 확인 / 144617원 또는 141200원 지지 후 반등 확인","risk_condition_ko":"141,200 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"062040.KS","display_name":"062040","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":200000.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":203828.39774707492,"relative_volume":0.63084154990409,"spread_bps":24.968789013732835,"day_high":210000.0,"day_low":199900.0,"execution_condition_ko":"새 종가 215,000원 초과 및 검증한 상대 거래량 1.2배 이상 / 200,000~201,700원 지지 구간 유지 여부","risk_condition_ko":"200,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"105560.KS","display_name":"105560","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":174000.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":173631.44679510736,"relative_volume":0.6401689072904763,"spread_bps":5.745475438092503,"day_high":175200.0,"day_low":170200.0,"execution_condition_ko":"105560.KS의 최신 시세·거래량·당일 거래량가중평균가격과 포트폴리오 비중 갱신 / 172300~171336원 부근에서 지지와 비용 차감 후 기대수익 대비 위험 개선 확인","risk_condition_ko":"171,336 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"000810.KS","display_name":"000810","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":662000.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":655339.4171464774,"relative_volume":0.5693066344398162,"spread_bps":15.117157974300833,"day_high":668000.0,"day_low":642000.0,"execution_condition_ko":"656000~664000원 구간 위 종가 회복 / 상대 거래량 1.2배 이상을 동반한 705000원 위 종가","risk_condition_ko":"642,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"051900.KS","display_name":"051900","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":290500.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":291718.48045336665,"relative_volume":0.8671634521889775,"spread_bps":17.196904557179707,"day_high":299000.0,"day_low":286000.0,"execution_condition_ko":"051900.KS의 현재 시세·거래량·당일 거래량가중평균가격·거래비용 갱신 / 298050~300000원 회복 및 304500원 위 거래량 동반 종가","risk_condition_ko":"283,476 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"128940.KS","display_name":"128940","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":500000.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":505367.28315608256,"relative_volume":0.5529491990571744,"spread_bps":10.005002501250624,"day_high":521000.0,"day_low":498500.0,"execution_condition_ko":"128940.KS 최신 시세와 장중 거래량·거래량가중평균가격 확보 / 525,437원과 534,000원 회복 후 540,000원 위 거래량 동반 종가 확인","risk_condition_ko":"498,500 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"055550.KS","display_name":"055550","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":111300.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":110630.52369682626,"relative_volume":0.7717141881450795,"spread_bps":8.98876404494382,"day_high":112200.0,"day_low":108800.0,"execution_condition_ko":"055550.KS의 최신 종가·장중 거래량가중평균가·비교 가능 거래량·이동평균 갱신 / 2분기 실적 공개일과 반복 가능한 이익·신용건전성·자본비율 확인","risk_condition_ko":"109,100 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"180640.KS","display_name":"180640","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":140200.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":141250.11014263076,"relative_volume":0.8247886903609296,"spread_bps":7.135212272565108,"day_high":143800.0,"day_low":139300.0,"execution_condition_ko":"180640.KS의 최신 시세·거래량·거래량가중평균가격 확인 / 143500원 상향 종가와 84065주 초과 거래량 및 다음 거래일 지지","risk_condition_ko":"136,900 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"032830.KS","display_name":"032830","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":296000.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":294881.57308619976,"relative_volume":0.9664353645742478,"spread_bps":16.9061707523246,"day_high":302000.0,"day_low":289000.0,"execution_condition_ko":"최신 정규장에서 304000원 돌파, 실시간 거래량가중평균가격 상회 및 같은 시각 기준 상대 거래량 1.2 이상 / 304000원 위 종가와 약 310000주를 웃도는 하루 거래량","risk_condition_ko":"278,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

```json
{"ticker":"088350.KS","display_name":"088350","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":5790.0,"market_data_asof":"2026-09-28T14:56:00+09:00","session_vwap":5800.282094795429,"relative_volume":0.4972402725708181,"spread_bps":17.25625539257981,"day_high":5900.0,"day_low":5620.0,"execution_condition_ko":"088350.KS의 9월 23일 이후 가격·거래량 갱신 / 5874원 위 종가와 일일 거래량 3425000주 초과","risk_condition_ko":"5,535 이탈 시 전략 재평가","decision_state_ko":"데이터 확인 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"RECHECK_REQUIRED","generated_in_current_run":true,"row_valid_until":"2026-09-28T15:26:00+09:00"}}
```

## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음
```json
{
  "published_at": "2026-09-28T14:47:49.387176+09:00",
  "as_of": "2026-09-28T13:56:00+09:00",
  "markdown_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.md",
  "readable_url": "https://nornen0202.github.io/TradingAgents/work/v1/kr/report/latest.html"
}
```
