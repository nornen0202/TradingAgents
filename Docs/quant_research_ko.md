# 한미 장기 퀀트 연구

기준일 이전에 공개된 자료로 월별 목표비중을 재현합니다. 사례 유니버스는 2019년 9월 말 SPY와 KODEX 200 자료에 기록된 자산 비중 상위 5개씩입니다. 시총이나 유동성을 기준으로 현재 시점에서 다시 고르지 않습니다. META의 이전 FB 코드는 동일 종목으로 이어집니다. [SPY 공식 보고서](https://www.sec.gov/Archives/edgar/data/884394/000119312519302203/d818891dn30d.htm), [KODEX 200 공식 자료](https://m.samsungfund.com/sheet/20191007/2ETF01_20190930.pdf), [FB 종목코드 변경 공시](https://www.sec.gov/Archives/edgar/data/1326801/000132680122000070/may312022-exhibit991.htm)

## 실행

```powershell
$research = 'G:\TradingAgentsData\quant-research-20261125'
$cutoff = '2026-11-25T04:42:27+09:00'
$env:TRADINGAGENTS_API_KEYS_PATH = 'C:\Projects\TradingAgents\config\api_keys.json'
tradingagents quant-research collect --as-of $cutoff --output-dir $research
tradingagents quant-research study --as-of $cutoff --output-dir $research
tradingagents quant-research holdout --as-of $cutoff --output-dir $research
tradingagents quant-research lean --output-dir "$research\holdout" --lean-root "$research\Lean" --dotnet "$research\dotnet10\dotnet.exe"
```

수집은 KIS 시세, Yahoo, OpenDART, SEC 공개 API를 사용합니다. SEC 요청에는 연락처가 포함된 식별자 및 OpenDART에는 API 키가 필요합니다. KIS는 원주가 모드로 투자 가능한 KOSPI200 추종 ETF의 전체 OHLCV를 가져옵니다. 미국과 한국 개별 종목의 Yahoo 일봉을 저장하고 분할·배당을 별도로 적용합니다. KODEX 200의 배당 관측도 Yahoo에서 가져오며 조회되지 않은 거래일을 보고서에 기록합니다. [KIS 공식 API 프로젝트](https://github.com/koreainvestment/open-trading-api), [OpenDART 공시 목록](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001), [OpenDART XBRL 원문](https://opendart.fss.or.kr/disclosureinfo/fnltt/xbrl/main.do), [SEC EDGAR API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)

SEC 연간 재무는 accession, 접수시각, 결산일 및 통화가 맞는 공시 원본과 연결합니다. 접수와 실제 공개 사이의 차이를 고려해 지역 기준 접수일과 공시일 중 늦은 날짜 이후 첫 거래일부터 적용합니다. DART 접수일만 확인되는 보고서도 다음 거래일부터 적용합니다. 정정 공시를 아직 사용할 수 없는 시점에는 이전 빈티지를 사용합니다. 정정의 원문 연결이 확인되지 않으면 그 시점부터 해당 기간의 재무 신호는 제외합니다.

후보 순위는 최근 공개된 연간 순이익/기말자산과 126일 모멘텀을 60/40으로 반영합니다. Core는 200일 추세와 126일 모멘텀을 사용하고, 63일 변동성으로 비중을 제한합니다. 현지 거래량과 정규장 시계열이 요건에 미달하면 목표 산출 입력에서 제외합니다. 시그널은 직전 정규장 종가까지의 자료에서 산출하고 월 첫 거래일 시가에 연구용 정수 수량을 계산합니다.

모든 포트폴리오는 초기 KRW 1억원, 외부 입출금 0원, 현금 수익률 0%를 사용합니다. SPY 보유와 KODEX 200 보유는 각 시장의 첫 거래 세션에 한 번 진입합니다. 80/20 비교는 SPY 80%와 KODEX 200 20%를 매달 두 시장의 첫 시가에 조정합니다. 시장 개장 순서와 남은 현금에 따라 정수주 비중에 차이가 날 수 있습니다. 세금, 거래비용, 슬리피지와 환전 비용을 같은 가정으로 계산합니다. 양도세 충당금과 확인된 배당채권을 장부에 반영합니다. 가용 현금은 배당 지급일을 입증할 때까지 늘리지 않습니다. [국세청 국내·국외주식 과세 설명](https://www.nts.go.kr/nts/na/ntt/selectNttInfo.do?nttSn=1350890)

2020–2022는 초기 연구 구간, 2023–2025는 사전 선택한 연 단위 순차 평가, 2026은 코드와 파라미터가 고정된 뒤 열린 연구 내부 평가 구간입니다. 이 실행은 훈련을 수행하지 않습니다. 2026 결과를 연 뒤에도 이전 구간 목표비중과 성과가 같은지 검사합니다. 과거 데이터에 대한 후향 연구이며 전체 시장의 상장폐지 수익과 재편입 이력은 수집 범위 밖입니다. 당시 저장한 LLM 거부 기록이 없어 veto 비교 성과는 산출하지 않습니다.

## 결과 확인

- `study.ko.html`과 `study.json`은 전체 및 연도별 수익률, 최대낙폭, 비용 후 샤프, 비교군별 수익률 차이, 20거래일 블록 신뢰구간을 담습니다.
- `weights.json`은 `analysis_as_of`, `fill_eligible_at`, `policy_hash`, `scaled_targets`, 선택된 공시를 포함합니다. `execution_authority`는 false입니다.
- `independent-ledger.json`은 종가 기준 NAV, 수수료, 슬리피지, 증권 매도세, 환전비용, 세금충당금, 체결 및 분할·배당 이벤트를 보존합니다.
- `lean-tape/`는 동일 입력 가격, 목표비중, 거래 세션을 저장합니다. LEAN Launcher의 사용자 정의 자료로 주입하고 C# 연구용 정수 수량 장부를 별도로 계산합니다. `lean-reconciliation.json`은 두 장부의 일별 NAV와 체결 수 일치를 확인합니다. LEAN의 브로커 모형과 실제 주문 체결은 이 대사의 범위 밖입니다. [QuantConnect 로컬 엔진](https://www.quantconnect.com/docs/v2/lean-engine/getting-started)
