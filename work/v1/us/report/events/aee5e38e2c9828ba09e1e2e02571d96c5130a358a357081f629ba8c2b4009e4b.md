# 미국 투자 브리핑 | 조건부 연구와 실행 관문

- 보고서 작성: 2026-10-14T23:17:35.205900+09:00
- 원분석 기준 거래일: 2026-10-13~2026-10-13 (ET)
- 시세 관측: 2026-10-14T10:00:00-04:00~2026-10-14T10:05:00-04:00 (최고령 17.6분)
- 계좌 기준: 2026-10-14T23:06:59.954932+09:00
- 분석 시도: 20261014T175403_local-scheduler-us-full / SUCCESS; 완료 분석: 20261014T175403_local-scheduler-us-full / success
- 별도 overlay 생산: 20261014T230400_local-scheduler-us-overlay_only / 2026-10-14T23:07:06.085154+09:00; 패킷 유효시각: 2026-10-14T10:30:00-04:00
- 세션 US:2026-10-14 · 모드 CONDITIONAL · event us:af4ce4c4d018454cff94d2b168fd5cb4 · 소스 OK · 조건부 관찰; 실시간 주문 관문 미통과

원분석 논지와 현재 실행 가능성은 별개입니다. 제공된 시세는 지연된 조건부 관측이며 주문 가능 호가, 중단 상태, 계좌 위험을 실시간 확인해야 합니다. 게시 시각은 입력 자료의 시각을 갱신하지 않습니다.

## 지금 볼 것
### MPWR · Monolithic Power Systems
원분석 HOLD / REDUCE_RISK · 실행 WAIT_FOR_TRIGGER. 전술 보유분 20% 감축 계획의 조건과 현재 위험을 우선 재검증. 발동 점검: 원분석 BREAKOUT $1322.4·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증. 무효화 점검: 원분석 STOP_LOSS $1283.81·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증. 가격 관측 2026-10-14T10:00:00-04:00; 행 유효 2026-10-14T10:30:00-04:00.

### CEG · CEG
원분석 HOLD / HOLD · 실행 WAIT_FOR_TRIGGER. 외부 근거를 공식 자료로 대조하고 신규 배정은 보류. 발동 점검: 원분석 PULLBACK $286.4·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증. 무효화 점검: 원분석 STOP_LOSS $280.16·close 확인; 세부 원문 조건 및 거래량·위험한도 재검증. 가격 관측 2026-10-14T10:05:00-04:00; 행 유효 2026-10-14T10:35:00-04:00.

### NVDA · NVIDIA
원분석 HOLD / HOLD · 실행 WAIT_FOR_TRIGGER. 외부 근거를 공식 자료로 대조하고 신규 배정은 보류. 발동 점검: 원분석 PULLBACK $224.9·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증. 무효화 점검: 원분석 TRIM $231.55·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증. 가격 관측 2026-10-14T10:00:00-04:00; 행 유효 2026-10-14T10:30:00-04:00.

## 커버리지 영수증
생산 COMPLETE: 보유 14개 모두 전송, 필수 관심 27개 모두 전송, 분석 30/30 성공. 관심목록과 보유의 중복은 하나의 전략 행으로 표시합니다. 신규 탐색 후보는 0개입니다.
COVERAGE_RECEIPT {"event_id":"us:af4ce4c4d018454cff94d2b168fd5cb4","status":"COMPLETE","holdings":{"expected":14,"missing_count":0,"missing":[]},"watchlist":{"expected":27,"missing_count":0,"missing":[],"all_rendered":true},"analysis":{"total":30,"successful":30,"failed":0,"failed_tickers":[]},"response_scanner_limit":10}

## 보유·관심 전략 30종목
|순위|종목·역할|원분석 논지/계획|현재 실행|진입 확인·무효화 점검|신뢰도|외부 근거|
|---:|---|---|---|---|---:|---|
|1|MPWR Monolithic Power Systems · 보유|HOLD / NONE / REDUCE_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 BREAKOUT $1322.4·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 STOP_LOSS $1283.81·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.55|직접 일치 없음|
|2|CEG CEG · 관심|HOLD / NONE / STARTER_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $286.4·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 STOP_LOSS $280.16·close 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.55|youtube:ILs31CN-_VA|
|3|NVDA NVIDIA · 보유|HOLD / NONE / NONE|WAIT_FOR_TRIGGER|원분석 PULLBACK $224.9·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 TRIM $231.55·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.58|youtube:lD0frse8o_U, youtube:PbYewoijHjE, youtube:4q1LijREraU, youtube:Mm-GvdfCgGc, prism:stock_ai_agent:16058|
|4|AMD Advanced Micro Devices · 관심|HOLD / NONE / STARTER_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $594.24·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 INVALIDATION $570.6·close 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.60|youtube:PbYewoijHjE, youtube:4q1LijREraU, youtube:1nGvSpFUXvg|
|5|AVGO Broadcom · 보유|HOLD / NONE / ADD_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 BREAKOUT $360.69·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 STOP_LOSS $335.2·close 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.55|youtube:lD0frse8o_U, youtube:deJpw1Q8hm0, youtube:e3ebAvQ-3yY, youtube:oCdGN001nZk|
|6|META Meta Platforms · 관심|HOLD / NONE / STARTER_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $734.33·intraday 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 INVALIDATION $711.68·close 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.61|youtube:lD0frse8o_U, youtube:PbYewoijHjE, youtube:deJpw1Q8hm0|
|7|AAPL Apple · 보유|HOLD / NONE / NONE|WAIT_FOR_TRIGGER|원분석 PULLBACK $337.38·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 INVALIDATION $325.81·close 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.63|youtube:PbYewoijHjE, youtube:gknGDs_po98|
|8|TSM Taiwan Semiconductor Manufacturing · 보유|HOLD / NONE / ADD_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 BREAKOUT $445.5·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 INVALIDATION $433.38·close 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.56|youtube:btxXzulHHAY|
|9|SGOV iShares 0-3 Month Treasury Bond ETF · 보유|HOLD / NONE / ADD_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $100.5·intraday 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 STOP_LOSS $100.53·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.60|직접 일치 없음|
|10|GEV GE Vernova · 보유|HOLD / NONE / ADD_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $992.49·intraday 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 INVALIDATION $963.29·next_day 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.58|직접 일치 없음|
|11|AMZN Amazon · 보유|HOLD / NONE / ADD_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $254.06·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 STOP_LOSS $242.42·close 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.57|직접 일치 없음|
|12|LLY Eli Lilly · 보유|HOLD / NONE / ADD_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $1143·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 STOP_LOSS $1113·close 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.57|직접 일치 없음|
|13|GOOGL Alphabet · 보유|HOLD / NONE / ADD_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $346.53·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 STOP_LOSS $335.51·close 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.56|직접 일치 없음|
|14|RSP RSP · 보유|HOLD / NONE / ADD_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $212.21·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 STOP_LOSS $207.16·close 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.60|직접 일치 없음|
|15|ETN Eaton · 보유|HOLD / NONE / ADD_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $420·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 INVALIDATION $417·close 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.54|직접 일치 없음|
|16|GLDM SPDR Gold MiniShares Trust · 보유|HOLD / NONE / NONE|WAIT_FOR_TRIGGER|원분석 BREAKOUT $83.11·volume_confirmed 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 INVALIDATION $80.75·close 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.65|직접 일치 없음|
|17|DELL Dell Technologies · 보유|HOLD / NONE / NONE|WAIT_FOR_TRIGGER|원분석 PULLBACK $568.51·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 STOP_LOSS $548.4·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.56|직접 일치 없음|
|18|SPYM SPYM · 관심|HOLD / NONE / STARTER_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $91.1·intraday 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 STOP_LOSS $90.4·intraday 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.64|직접 일치 없음|
|19|V V · 관심|HOLD / NONE / STARTER_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $390.69·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 STOP_LOSS $384.5·intraday 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.64|직접 일치 없음|
|20|CVX CVX · 관심|HOLD / NONE / STARTER_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $215.95·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 INVALIDATION $210.89·close 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.62|직접 일치 없음|
|21|XOM XOM · 관심|HOLD / NONE / STARTER_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $172.3·intraday 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 STOP_LOSS $168.8·intraday 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.62|직접 일치 없음|
|22|SHEL SHEL · 관심|HOLD / NONE / STARTER_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $102.47·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 STOP_LOSS $101.27·close 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.61|직접 일치 없음|
|23|ABBV ABBV · 관심|HOLD / NONE / STARTER_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $271.35·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 INVALIDATION $260.08·close 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.60|직접 일치 없음|
|24|AMT AMT · 관심|HOLD / NONE / STARTER_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $177.88·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 STOP_LOSS $175.02·intraday 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.60|직접 일치 없음|
|25|DDOG Datadog · 관심|HOLD / NONE / STARTER_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $277.65·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 STOP_LOSS $269.38·close 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.60|직접 일치 없음|
|26|PG PG · 관심|HOLD / NONE / STARTER_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $149.7·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 STOP_LOSS $147.5·intraday 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.60|직접 일치 없음|
|27|NU NU · 관심|HOLD / NONE / STARTER_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $15.2·close 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 STOP_LOSS $14.43·close 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.59|직접 일치 없음|
|28|MDT MDT · 관심|HOLD / NONE / STARTER_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $90.2·intraday 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 STOP_LOSS $89.27·close 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.57|직접 일치 없음|
|29|GOOG GOOG · 관심|HOLD / NONE / STARTER_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $343·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 STOP_LOSS $337.5·intraday 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.55|직접 일치 없음|
|30|WELL WELL · 관심|HOLD / NONE / STARTER_IF_TRIGGERED|WAIT_FOR_TRIGGER|원분석 PULLBACK $228.63·two_bar 확인; 세부 원문 조건 및 거래량·위험한도 재검증; 원분석 STOP_LOSS $222.8·intraday 확인; 세부 원문 조건 및 거래량·위험한도 재검증|0.54|직접 일치 없음|

## 시세·미시구조 관측
|종목|가격·관측시각|VWAP / RVOL|feed·spread·중단 상태|행 유효시각|
|---|---|---|---|---|
|MPWR|$1271.45 · 2026-10-14T10:00:00-04:00|1285.6703510926566 / 0.6306179863780663|지연 285.0초; spread 8.045837841215567bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:30:00-04:00|
|CEG|$282.99 · 2026-10-14T10:05:00-04:00|286.9843874421211 / 1.0742095835953835|지연 6.0초; spread 31.149922125196195bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:35:00-04:00|
|NVDA|$224.645 · 2026-10-14T10:00:00-04:00|225.42497539054142 / 0.9522983461364591|지연 285.0초; spread 1.3281682346418469bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:30:00-04:00|
|AMD|$588 · 2026-10-14T10:00:00-04:00|588.4623712479809 / 1.044991884108225|지연 290.0초; spread 10.005850878904306bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:30:00-04:00|
|AVGO|$350.02 · 2026-10-14T10:00:00-04:00|351.0427280657221 / 1.0315442515504836|지연 275.0초; spread 3.9734347505262866bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:30:00-04:00|
|META|$749.84 · 2026-10-14T10:05:00-04:00|753.5741808924297 / 1.051862161904238|지연 0.0초; spread 3.458688624905098bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:35:00-04:00|
|AAPL|$345.265 · 2026-10-14T10:00:00-04:00|345.39975564932513 / 1.4059486320511865|지연 275.0초; spread 1.7312020312771152bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:30:00-04:00|
|TSM|$437.86 · 2026-10-14T10:00:00-04:00|438.89393436425166 / 0.825900645108865|지연 290.0초; spread 7.283155427088631bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:30:00-04:00|
|SGOV|$100.53 · 2026-10-14T10:00:00-04:00|100.53547734878867 / 1.5854497228184776|지연 289.0초; spread 0.9946784701850218bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:30:00-04:00|
|GEV|$964.02 · 2026-10-14T10:00:00-04:00|975.2089515623836 / 0.916132996032376|지연 280.0초; spread 30.210706879336854bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:30:00-04:00|
|AMZN|$257.52 · 2026-10-14T10:00:00-04:00|258.4970549206321 / 1.0560508682781318|지연 275.0초; spread 1.9274136036856533bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:30:00-04:00|
|LLY|$1212.67 · 2026-10-14T10:00:00-04:00|1202.7558298674358 / 1.2113952600342055|지연 285.0초; spread 6.362558409525509bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:30:00-04:00|
|GOOGL|$354.71 · 2026-10-14T10:00:00-04:00|356.67417770457104 / 1.445484228578264|지연 280.0초; spread 2.7859809438909773bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:30:00-04:00|
|RSP|$211.555 · 2026-10-14T10:00:00-04:00|212.25810538896093 / 1.4722835491988755|지연 285.0초; spread 0.4710648420750833bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:30:00-04:00|
|ETN|$417.88 · 2026-10-14T10:00:00-04:00|421.43294306989606 / 1.185864497961379|지연 280.0초; spread 25.58514166587797bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:30:00-04:00|
|GLDM|$80.88 · 2026-10-14T10:00:00-04:00|81.12116645413913 / 0.6700180128579684|지연 280.0초; spread 1.2329696072998109bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:30:00-04:00|
|DELL|$529.33 · 2026-10-14T10:00:00-04:00|534.8809653614345 / 1.9094281720835853|지연 275.0초; spread 27.080904201302413bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:30:00-04:00|
|SPYM|$91.015 · 2026-10-14T10:05:00-04:00|91.2354129721454 / 0.8372035607936925|지연 0.0초; spread 1.0947506705337902bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:35:00-04:00|
|V|$394.2 · 2026-10-14T10:00:00-04:00|393.9015967262448 / 0.7932072638089284|지연 295.0초; spread 1.778884639330966bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:30:00-04:00|
|CVX|$219.73 · 2026-10-14T10:05:00-04:00|219.77204154287318 / 0.7139123503206123|지연 4.0초; spread 3.640666241922841bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:35:00-04:00|
|XOM|$175.2 · 2026-10-14T10:05:00-04:00|175.0430266932166 / 0.43527914889150504|지연 5.0초; spread 4.001715020724402bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:35:00-04:00|
|SHEL|$103.175 · 2026-10-14T10:05:00-04:00|103.51531123119368 / 0.7537532505861644|지연 8.0초; spread 0.9677263269952209bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:35:00-04:00|
|ABBV|$281.785 · 2026-10-14T10:05:00-04:00|279.4914231845492 / 0.4015121610361012|지연 1.0초; spread 8.217660824982339bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:35:00-04:00|
|AMT|$177.945 · 2026-10-14T10:05:00-04:00|177.72551019356965 / 0.346235830878373|지연 8.0초; spread 9.01713255184832bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:35:00-04:00|
|DDOG|$282.45 · 2026-10-14T10:00:00-04:00|281.60062467237464 / 0.2999448407941299|지연 291.0초; spread 25.056907412961817bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:30:00-04:00|
|PG|$155.034 · 2026-10-14T10:00:00-04:00|154.9210897607532 / 0.7155584468798551|지연 295.0초; spread 5.826562651733624bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:30:00-04:00|
|NU|$14.945 · 2026-10-14T10:05:00-04:00|15.163919469048233 / 0.42657917907195747|지연 0.0초; spread 6.607201850016376bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:35:00-04:00|
|MDT|$92.595 · 2026-10-14T10:00:00-04:00|92.73059884080004 / 0.7870743810798451|지연 294.0초; spread 4.3215211754529bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:30:00-04:00|
|GOOG|$350.174 · 2026-10-14T10:05:00-04:00|352.6500883213088 / 1.3651050252760877|지연 4.0초; spread 4.226125910377316bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:35:00-04:00|
|WELL|$229.68 · 2026-10-14T10:00:00-04:00|230.51286709805873 / 0.14360103755274806|지연 294.0초; spread 23.061024692701018bp; halt unknown, LULD not_available_by_provider, 뉴스 not_available_by_provider|2026-10-14T10:30:00-04:00|

## 근거·반대 근거와 다음 확인

- MPWR: 원분석은 중기 핵심 보유 논지를 유지하지만 신규 진입 손익비와 모멘텀이 약하다. 계좌 overlay의 전술분 위험축소 계획은 보유량과 실시간 호가 확인 전 주문이 아니다.
- CEG: 소수몽키 직접 언급은 연구 순위를 높였지만 계약 경제성과 현금흐름은 공식 자료 대조가 필요하다. 미검증 주장을 신뢰도나 매수 비중 상향에 쓰지 않았다.
- NVDA: YouTube의 AI/반도체 논거와 PRISM 보유 시뮬레이션이 함께 관측됐다. PRISM은 시뮬레이션 전용이고 원분석은 거래량·가격 구조 확인 전 신규 진입을 허용하지 않는다.
- 각 종목의 정본 thesis는 구조화 보고서에 원문 조건·무효화·기간·규모와 함께 보존했다. 최신 분석 시도와 완료 분석은 같은 실행이지만 별도 영수증으로 유지했다. 공시·거시·감성 source_coverage의 UNAVAILABLE/FALLBACK/뉴스 유래 상태를 검증 완료로 해석하지 않는다.
- 다음 checkpoint: 실시간 호가/체결, 계좌와 집중도, feed·spread, LULD·뉴스 halt, 원공시·실적 및 각 원분석 가격선을 다시 확인한다. 정성적 반증의 확인 날짜는 새로 가정하지 않는다.

MOBILE_HANDOFF {"owner":"external_github_notification_pipeline","status":"PENDING_EXTERNAL_VERIFICATION","work_sent_notification":false}