# US microstructure execution remediation

검토일: 2026-06-27 KST

## 확인된 문제

1. ChatGPT 답변은 `chatgpt_execution_context.json`을 열었다고 했지만, 공개 US overlay context의 `last_price`, `session_vwap`, `relative_volume`, `spread_bps`, `execution_strength` 값을 구조화해 사용하지 못하고 “확인 불가”로 처리했다.
2. 해당 context의 문제는 핵심 필드 부재가 아니라 `generated_in_current_run=false`, `freshness_class=PRIOR_SESSION_BACKFILL`, `execution_eligibility=HISTORICAL_REFERENCE_ONLY`인 오래된 백필이었다.
3. US LULD, Reg SHO, news halt 상태는 provider 미지원(`not_available_by_provider`)으로 들어오는데, 이를 정상 확인과 구분해야 한다.
4. Alpaca IEX 또는 delayed SIP feed, 추정 execution strength, stale Massive/Polygon 계열 데이터는 as-of 참고에는 유용하지만 execution-grade NBBO/SIP 확인으로 승격하면 안 된다.
5. US 프롬프트에는 KR 프롬프트처럼 `asof_execution_gate`와 “JSON microstructure 값을 1순위로 쓰되 현재 무료/검색 시세와 분리”하는 규칙이 부족했다.

## 적용한 보완

- `chatgpt_execution_context.json`의 `asof_execution_gate`에 provider limitation과 status recheck 요구를 추가한다.
- `status_unavailable:luld_status`, `status_unavailable:news_halt_status`, `feed_limited:*`가 있으면 `current_execution_promotion=RECHECK_REQUIRED`로 남긴다.
- US 프롬프트는 TradingAgents microstructure JSON의 핵심 필드를 “확인 불가”로 버리지 말고, historical/backfill이면 과거 as-of 값으로 표기하도록 보강했다.
- Overlay follow-up 프롬프트도 `asof_execution_gate`, provider limitation, 무료/검색 시세와 overlay as-of 값의 분리를 필수로 반영하도록 보강했다.

## 최소비용 데이터 전략

| 선택지 | 월 비용 | 해결 범위 | 한계 | 판단 |
|---|---:|---|---|---|
| 현재 KIS overseas + yfinance fallback | 0원 | 기본 현재가, 일부 분봉/거래량, 백필 보조 | US execution-grade NBBO, LULD/news halt, SIP coverage 부족 | 단독 실행에는 부족 |
| Alpaca Basic | 0달러 | IEX 기반 제한적 실시간, 개발/테스트 | 전체 시장 NBBO/SIP가 아니며 latest 15분 제한/coverage 한계 | 테스트용 |
| Alpaca Algo Trader Plus | 99달러/월 | CTA/UTP SIP 기반 전체 US stock exchange coverage, websocket unlimited | LULD/news halt 전용 상태까지 별도 확인 필요 | 개인 자동화의 1순위 유료 후보 |
| Massive Stocks Advanced | 199달러/월 | 실시간 US stocks, NBBO/trades, 긴 히스토리, 높은 coverage | 비용이 Alpaca보다 높음, 계정 entitlement 확인 필요 | Alpaca로 부족하면 2순위 |
| Databento Standard + EQUS.MINI | 199달러/월 | live top-of-book/trades, no exchange license fees, usage 관리 용이 | 현재 코드에 통합 경로 없음, derived BBO라 SIP/NBBO와 동일하지 않음 | 새 vendor 통합을 감수할 때 Massive 대안 |
| Nasdaq Basic/direct feeds | per-user/firm fee는 낮게 시작 가능하나 계약/분배 절차 필요 | Nasdaq BBO/Last Sale, halt/emergency status 등 직접 피드 | 직접 feed 계약·인프라·승인 절차가 무거움 | 상업/재배포 또는 기관형 운영일 때만 |

## 권장 작업 순서

1. 무료 경로에서는 US as-of 값을 반드시 “과거/지연/백필”로 분리하고 현재 실행 가능으로 승격하지 않는다.
2. 유료 사용이 가능하면 최소비용으로 Alpaca Algo Trader Plus를 우선 검토한다. 현재 코드의 `ALPACA_DATA_FEED=sip` 경로와 잘 맞는다.
3. 더 강한 NBBO/trade coverage가 필요하면 Massive Stocks Advanced를 추가 또는 대체 원천으로 둔다.
4. 새 vendor 통합 비용을 감수할 수 있고 exchange license/reporting 부담을 최소화하려면 Databento EQUS.MINI를 Massive 대안으로 검토한다.
5. LULD/news halt/Reg SHO 상태는 provider 미지원이면 별도 공식/브로커 확인 checklist로 남긴다.
6. 직접 재배포·상업용 실시간 데이터가 필요할 때만 Nasdaq Basic/CTA/UTP/CT Plan 계열 직접 계약을 검토한다.

## 성공 기준

- US context 티커 항목에 `asof_execution_gate.provider_limitations`가 표시된다.
- core fields가 있으면 `core_fields_present=true`로 표시되고, stale/backfill이면 “값 있음 + 현재 승격 불가”로 해석된다.
- provider status 미지원 또는 feed limitation이 있으면 `current_execution_promotion=RECHECK_REQUIRED`다.
- 프롬프트 답변은 US as-of 실행표에서 historical 값을 누락하지 않고, 현재 장중 실행표에서는 실시간 재확인 조건으로 분리한다.

## 참고 링크

- Alpaca Market Data API: https://docs.alpaca.markets/us/docs/about-market-data-api
- Alpaca data provider 설명: https://alpaca.markets/support/data-provider-alpaca
- Massive pricing: https://massive.com/pricing
- Databento pricing: https://databento.com/pricing
- Databento US Equities Mini: https://databento.com/docs/venues-and-datasets/equs-mini
- Databento live data license fees: https://databento.com/docs/portal/live-data
- Nasdaq Basic data product: https://www.nasdaqtrader.com/TraderNews.aspx?id=dn2009-019
- CT Plan transition notice: https://nasdaqtrader.com/TraderNews.aspx?id=UTP2025-24
