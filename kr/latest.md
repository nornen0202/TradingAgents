# TradingAgents KR 최신 공개 입력

schema: tradingagents.ai-context/v1
문서 생성: 2026-09-28T05:49:42.309054+00:00

이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. 원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. 휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. 빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. 현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.

통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. 종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.

## 원본 링크

- https://nornen0202.github.io/TradingAgents/account/public.json
- https://nornen0202.github.io/TradingAgents/mobile/strategy.json
- https://nornen0202.github.io/TradingAgents/work/v1/kr/status.json

## 원분석·시세 시각
```json
{
  "producer_run_id": "20260928T135606_github-actions-overlay-kr",
  "producer_finished_at": "2026-09-28T13:56:45.282340+09:00",
  "analysis_run_id": "20260928T050548_github-actions-kr",
  "analysis_completed_at": "2026-09-28T07:21:24.610166+09:00",
  "analysis_trade_date_oldest": "2026-09-23",
  "analysis_trade_date_latest": "2026-09-23",
  "analysis_lineage_status": "RESOLVED",
  "market_data_oldest_at": "2026-09-28T13:56:00+09:00",
  "market_data_latest_at": "2026-09-28T13:56:31.040274+09:00",
  "market_data_status": "STALE"
}
```

## 계좌 관측값 — 계좌번호·주문·인증정보 제외
```json
{
  "status": "available",
  "as_of": "2026-09-28T13:56:59.772359+09:00",
  "snapshot_health": "VALID",
  "currency": "KRW",
  "summary": {
    "position_count": 13,
    "total_purchase_amount_krw": 14944236,
    "total_market_value_krw": 11017500,
    "total_unrealized_pnl_krw": -3926736,
    "settled_cash_krw": 975902,
    "available_cash_krw": 975902,
    "buying_power_krw": 975902,
    "total_equity_krw": 11993402
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
      "current_price_krw": 272750,
      "market_value_krw": 2727500,
      "unrealized_pnl_krw": -596351
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
      "current_price_krw": 694000,
      "market_value_krw": 694000,
      "unrealized_pnl_krw": -459000
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
      "current_price_krw": 237500,
      "market_value_krw": 237500,
      "unrealized_pnl_krw": -136667
    },
    {
      "ticker": "058470.KQ",
      "name": "리노공업",
      "quantity": 3.0,
      "sellable_quantity": 3.0,
      "average_cost_krw": 100000,
      "current_price_krw": 72200,
      "market_value_krw": 216600,
      "unrealized_pnl_krw": -83400
    },
    {
      "ticker": "035420.KS",
      "name": "NAVER",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 282334,
      "current_price_krw": 197800,
      "market_value_krw": 197800,
      "unrealized_pnl_krw": -84534
    },
    {
      "ticker": "353200.KS",
      "name": "대덕전자",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 172300,
      "current_price_krw": 124400,
      "market_value_krw": 124400,
      "unrealized_pnl_krw": -47900
    },
    {
      "ticker": "083450.KQ",
      "name": "GST",
      "quantity": 2.0,
      "sellable_quantity": 2.0,
      "average_cost_krw": 59100,
      "current_price_krw": 49700,
      "market_value_krw": 99400,
      "unrealized_pnl_krw": -18800
    },
    {
      "ticker": "034020.KS",
      "name": "두산에너빌리티",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 112931,
      "current_price_krw": 81800,
      "market_value_krw": 81800,
      "unrealized_pnl_krw": -31131
    },
    {
      "ticker": "403870.KQ",
      "name": "HPSP",
      "quantity": 1.0,
      "sellable_quantity": 1.0,
      "average_cost_krw": 54500,
      "current_price_krw": 56200,
      "market_value_krw": 56200,
      "unrealized_pnl_krw": 1700
    }
  ]
}
```

## 종목별 원안과 조건 — 현재 재검증 필요

```json
{"ticker":"000660.KS","display_name":"SK하이닉스","is_held":true,"strategy_code":"SELL","strategy_ko":"매도·청산 검토","last_price":1783000.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":1796038.9344909638,"relative_volume":0.9480225175717607,"spread_bps":5.60695262125035,"day_high":1840000.0,"day_low":1769000.0,"execution_condition_ko":"위험 대응 조건: 1,832,000 이탈 시 손절 조건 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"1,832,000 이탈 시 손절 조건","decision_state_ko":"투자 근거 무효화","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"042700.KS","display_name":"한미반도체","is_held":true,"strategy_code":"REDUCE","strategy_ko":"비중 축소 검토","last_price":238000.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":240202.03400328828,"relative_volume":0.4529703078977072,"spread_bps":21.03049421661409,"day_high":245000.0,"day_low":236500.0,"execution_condition_ko":"위험 대응 조건: 239,000 이탈 시 리스크 축소 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"239,000 이탈 시 리스크 축소","decision_state_ko":"실행 조건 감시 중","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"058470.KQ","display_name":"리노공업","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":72200.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":72696.09259618836,"relative_volume":0.6387311635095304,"spread_bps":13.840830449826989,"day_high":74300.0,"day_low":71800.0,"execution_condition_ko":"058470.KQ 최신 정규장 가격·거래량·장중 거래량가중평균가격 확인 / 77,500원 초과 종가 및 일일 거래량 1,795,192주 이상 확인","risk_condition_ko":"71,500 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"353200.KS","display_name":"대덕전자","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":124600.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":125326.90322992501,"relative_volume":1.6117597654715643,"spread_bps":8.028904054596548,"day_high":129100.0,"day_low":121400.0,"execution_condition_ko":"353200.KS의 상충하는 2026-09-23 종가를 거래소 기록과 대조하고 최신 시세 확인 / 상대 거래량 1.2 이상, 일일 거래량 1578412주 초과를 동반한 종가 120700 상회","risk_condition_ko":"117,053 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"010140.KS","display_name":"삼성중공업","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":20100.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":20248.415474635323,"relative_volume":0.577149710366641,"spread_bps":24.84472049689441,"day_high":20550.0,"day_low":20100.0,"execution_condition_ko":"최신 주가·거래량과 2026-09-27~28 보도 이후 가격 반응 확인 / 20,200원 및 19,900원 지지 여부 확인","risk_condition_ko":"19,900 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"267260.KS","display_name":"HD현대일렉트릭","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":694000.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":697352.6357488469,"relative_volume":0.8471079037767709,"spread_bps":14.398848092152628,"day_high":709000.0,"day_low":689000.0,"execution_condition_ko":"현재 가격·거래량·실시간 거래량가중평균가격·공시 확인 / 720,000~723,000원 회복 후 727,403원 돌파와 상대 거래량 1.2배 이상","risk_condition_ko":"698,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"278470.KS","display_name":"에이피알","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":368500.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":369652.362781972,"relative_volume":0.5787410605454448,"spread_bps":13.577732518669382,"day_high":377500.0,"day_low":364500.0,"execution_condition_ko":"2026-09-23 이후 최신 종가로 357000원·350500원 지지 여부 확인 / 373500원 회복 시 거래량과 379518~381500원 저항 돌파 여부 관찰","risk_condition_ko":"350,500 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"083450.KQ","display_name":"GST","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":49750.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":49676.27783819566,"relative_volume":0.8195110783575968,"spread_bps":10.055304172951232,"day_high":50400.0,"day_low":48800.0,"execution_condition_ko":"최신 가격·거래량·호가 스프레드·공시 확인 / 50,100원 위 종가와 실제 거래량 106,762주 이상","risk_condition_ko":"48,300 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"005930.KS","display_name":"삼성전자","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":272500.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":276688.7975385341,"relative_volume":1.1339230365271102,"spread_bps":18.331805682859763,"day_high":285500.0,"day_low":271500.0,"execution_condition_ko":"최신 종가·장중 가격·거래량·거래량가중평균가격 확보 / 2026-09-29 배당락 조건·확정 배당액 확인과 가격선 재설정","risk_condition_ko":"276,500 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"403870.KQ","display_name":"HPSP","is_held":true,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":56200.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":56039.17942468305,"relative_volume":0.7748706389492126,"spread_bps":17.77777777777778,"day_high":57200.0,"day_low":54800.0,"execution_condition_ko":"403870.KQ의 53,763~54,326원 지지 재확인, 당일 거래량가중평균가격 회복 및 상대 거래량 1.2배 / 56,556원 상향 마감과 약 177만 주 이상 거래 후 57,600원 돌파 확인","risk_condition_ko":"53,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"034020.KS","display_name":"두산에너빌리티","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":81800.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":82070.15369785846,"relative_volume":0.5271316786958214,"spread_bps":12.217470983506415,"day_high":83000.0,"day_low":80900.0,"execution_condition_ko":"현재 시세 확인 후 85,057원 회복, 86,100원 돌파, 87,049원 상향 안착 여부 / 80,500원 지지선 검사와 이탈 시 78,052원·76,986원 확인","risk_condition_ko":"80,500 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"010120.KS","display_name":"LS ELECTRIC","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":203000.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":205013.54322128254,"relative_volume":0.674866179070632,"spread_bps":24.600246002460025,"day_high":209500.0,"day_low":201000.0,"execution_condition_ko":"010120.KS의 새로운 가격·거래량·거래량가중평균가와 상대 거래량 확보 / 199158~203000원 구간의 거래량 동반 회복","risk_condition_ko":"199,158 이탈 시 전략 재평가","decision_state_ko":"실행 조건 감시 중","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"035420.KS","display_name":"NAVER","is_held":true,"strategy_code":"HOLD","strategy_ko":"보유 유지","last_price":197800.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":198495.20860416724,"relative_volume":0.9978889890207354,"spread_bps":5.0543340914834465,"day_high":200500.0,"day_low":194300.0,"execution_condition_ko":"035420.KS의 최신 가격·거래량과 실제 보유 비중 확인 / 201600 위 종가와 상대 거래량 1.2배 이상이면 손익비를 다시 평가","risk_condition_ko":"194,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"108490.KQ","display_name":"로보티즈","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":288000.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":293116.17299849755,"relative_volume":0.396308545903573,"spread_bps":17.37619461337967,"day_high":300000.0,"day_low":287750.0,"execution_condition_ko":"현재 가격·거래량·기업행위와 2026-09-23 이후 공시 확인 / 현재 자료로 재산출한 10일 지수이동평균 및 거래량가중 평균 회복","risk_condition_ko":"297,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"006400.KS","display_name":"삼성SDI","is_held":false,"strategy_code":"WAIT","strategy_ko":"조건 충족 전 대기","last_price":533000.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":532728.9167308175,"relative_volume":0.7794654247938504,"spread_bps":18.779342723004696,"day_high":540000.0,"day_low":524000.0,"execution_condition_ko":"006400.KS의 최신 한국거래소 가격·거래량·당일 거래량가중평균가와 기존 보유 비중 확인 / 529000원 회복 후 상대거래량 1.2 이상으로 535794원 위 마감","risk_condition_ko":"510,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"298040.KS","display_name":"효성중공업","is_held":false,"strategy_code":"AVOID","strategy_ko":"신규 매수 회피","last_price":2791000.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":2815099.921518265,"relative_volume":1.0088621446240957,"spread_bps":3.582303421099767,"day_high":2925000.0,"day_low":2771000.0,"execution_condition_ko":"위험 대응 조건: 2,828,000 이탈 시 전략 재평가 (매수 돌파·거래량 조건과 별도 판정)","risk_condition_ko":"2,828,000 이탈 시 전략 재평가","decision_state_ko":"실행 조건 감시 중","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"096770.KS","display_name":"096770","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":158100.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":157711.3479456791,"relative_volume":1.0404041325453741,"spread_bps":6.3271116735210375,"day_high":161200.0,"day_low":147600.0,"execution_condition_ko":"096770.KS의 153500원 돌파 및 갱신된 최근 5거래일 평균 대비 1.2배 이상 거래량을 동반한 종가 확인 / 144617원 또는 141200원 지지 후 반등 확인","risk_condition_ko":"141,200 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"062040.KS","display_name":"062040","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":201000.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":204620.32225555266,"relative_volume":0.602784071230173,"spread_bps":24.84472049689441,"day_high":210000.0,"day_low":201000.0,"execution_condition_ko":"새 종가 215,000원 초과 및 검증한 상대 거래량 1.2배 이상 / 200,000~201,700원 지지 구간 유지 여부","risk_condition_ko":"200,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"090430.KS","display_name":"090430","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":142300.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":142793.58596880702,"relative_volume":0.6293953972029269,"spread_bps":7.024938531787846,"day_high":144800.0,"day_low":141100.0,"execution_condition_ko":"090430.KS의 최신 가격·거래량·상대 거래량·거래량가중평균가격 확인 / 145000 회복은 초기 신호로만 판단","risk_condition_ko":"140,200 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"105560.KS","display_name":"105560","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":174100.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":173547.46942650902,"relative_volume":0.6720479562349967,"spread_bps":5.742176284811944,"day_high":175200.0,"day_low":170200.0,"execution_condition_ko":"105560.KS의 최신 시세·거래량·당일 거래량가중평균가격과 포트폴리오 비중 갱신 / 172300~171336원 부근에서 지지와 비용 차감 후 기대수익 대비 위험 개선 확인","risk_condition_ko":"171,336 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"000810.KS","display_name":"000810","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":662000.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":654345.6151622229,"relative_volume":0.5971695823389421,"spread_bps":15.094339622641508,"day_high":668000.0,"day_low":642000.0,"execution_condition_ko":"656000~664000원 구간 위 종가 회복 / 상대 거래량 1.2배 이상을 동반한 705000원 위 종가","risk_condition_ko":"642,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"051900.KS","display_name":"051900","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":290000.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":291916.5869708769,"relative_volume":0.884491788985699,"spread_bps":17.25625539257981,"day_high":299000.0,"day_low":286000.0,"execution_condition_ko":"051900.KS의 현재 시세·거래량·당일 거래량가중평균가격·거래비용 갱신 / 298050~300000원 회복 및 304500원 위 거래량 동반 종가","risk_condition_ko":"283,476 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"055550.KS","display_name":"055550","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":111100.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":110546.02978686546,"relative_volume":0.8054700539529175,"spread_bps":8.99685110211426,"day_high":112200.0,"day_low":108800.0,"execution_condition_ko":"055550.KS의 최신 종가·장중 거래량가중평균가·비교 가능 거래량·이동평균 갱신 / 2분기 실적 공개일과 반복 가능한 이익·신용건전성·자본비율 확인","risk_condition_ko":"109,100 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"180640.KS","display_name":"180640","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":141200.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":141298.7214755188,"relative_volume":0.8552163096984555,"spread_bps":7.079646017699115,"day_high":143800.0,"day_low":139300.0,"execution_condition_ko":"180640.KS의 최신 시세·거래량·거래량가중평균가격 확인 / 143500원 상향 종가와 84065주 초과 거래량 및 다음 거래일 지지","risk_condition_ko":"136,900 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"032830.KS","display_name":"032830","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":294500.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":294646.1149736778,"relative_volume":0.9543647304265928,"spread_bps":16.963528413910094,"day_high":302000.0,"day_low":289000.0,"execution_condition_ko":"최신 정규장에서 304000원 돌파, 실시간 거래량가중평균가격 상회 및 같은 시각 기준 상대 거래량 1.2 이상 / 304000원 위 종가와 약 310000주를 웃도는 하루 거래량","risk_condition_ko":"278,000 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
```

```json
{"ticker":"088350.KS","display_name":"088350","is_held":false,"strategy_code":"BUY_ON_CONFIRMATION","strategy_ko":"조건 확인 후 분할매수 검토","last_price":5840.0,"market_data_asof":"2026-09-28T13:56:00+09:00","session_vwap":5797.596952556875,"relative_volume":0.5098432095486882,"spread_bps":17.10863986313088,"day_high":5900.0,"day_low":5620.0,"execution_condition_ko":"088350.KS의 9월 23일 이후 가격·거래량 갱신 / 5874원 위 종가와 일일 거래량 3425000주 초과","risk_condition_ko":"5,535 이탈 시 전략 재평가","decision_state_ko":"조건 충족 전 대기","quality_at_build":{"execution_ready":false,"current_execution_promotion":"POSSIBLE","generated_in_current_run":true,"row_valid_until":"2026-09-28T14:26:00+09:00"}}
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
