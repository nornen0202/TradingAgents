# KIS 모의 서버 연결과 주문 운용

2026-10-18 기준. 기존 실계좌 조회 `portfolio/kis.py`는 읽기 전용으로 유지한다.
이 문서의 KIS VTS는 로컬 `PaperBroker`의 가상 원장과 다른 증권사 모의 서버다.
자동 실계좌 주문 경로는 제공하지 않는다.

## 사용자가 확인하는 상태

- `readiness`: 접속정보 존재 여부만 점검한다. 네트워크와 주문 전송이 없다.
- `probe`: 전용 모의 인증, 잔고, 당일 주문 조회만 수행한다. 조회 성공을 주문·체결 검증 성공으로 표현하지 않는다.
- `ACKNOWLEDGED`: 증권사 모의 서버가 주문번호를 돌려줬다. 아직 체결이 아니다.
- `OPEN` / `PARTIAL` / `FILLED`: 모의 서버의 누적 주문체결 조회로 확인한 미체결·부분체결·전량체결이다.
- 취소 요청의 `ACKNOWLEDGED`: 취소 접수다. 후속 조회의 `CANCELLED`가 취소 확인이다.
- `UNKNOWN`: 전송 뒤 응답 유실 등 접수가 불명확하다. 재시작해도 같은 주문을 다시 전송하지 않는다. 다른 신규 주문도 차단하고 증권사 기록과 수동 대사를 요구한다.

`FILLED` 누적 관측만으로 정확한 개별 체결 시각·수수료·결제 완료를 만들어내지 않는다.
당일 조회의 `ord_tmd`는 **주문 시각**이다. 실제 실행 시각으로 재사용하지 않는다.
따라서 통합 성과 원장에는 우선 `mode=demo` 의도와 누적 관측을 보관한다.
검증된 개별 체결·비용·확인·결제 증거가 별도로 들어온 경우에만 `import_demo_fill`로
정산된 `mode=demo` 체결을 추가한다. `actual` 성과로 분류하지 않는다.

## 실제 전송 경계

`execution/kis_paper.py`의 `KisPaperBroker`가 기존 `KisDemoClient`와 `DemoOrderJournal`을 재사용한다.
호스트는 `https://openapivts.koreainvestment.com:29443`으로 고정되어 있다.
일반 증권 계좌 상품 `01`, 국내 6자리 종목의 현금 지정가 주문만 허용한다.
대체 호스트·리디렉션·실계좌 ID·자동 HTTP 재시도·실계좌 인증정보 대체를 허용하지 않는다.

실전용 `KIS_*`와 별개인 `KIS_DEMO_APP_KEY`, `KIS_DEMO_APP_SECRET`,
`KIS_DEMO_ACCOUNT_NO`, `KIS_DEMO_PRODUCT_CODE`를 기존 보호 설정에 등록한다.
인증정보를 명령 인자나 주문 JSON에 넣지 않는다. 상세 등록은
[기존 모의투자 안내](kis_demo_quickstart_ko.md)를 따른다.

주문 정책은 해당 원장에 고정한다. 종목·한도를 바꾸려면 새 이름의 원장으로 별도 실험을 시작한다.
기본값은 종목별 명시 허용목록, 주문당 10만원, 하루 매수 30만원, 하루 3건이며 실운용 추천값을 뜻하지 않는다.
호출부의 `paper_enabled=True` 또는 CLI `--paper-enabled`가 없으면 전송하지 않는다.

모든 주문은 다음을 다시 확인한다.

1. 현재 KRX 달력이 확인한 정규장이고 장 종료 이전이다. 달력 실패나 주말·휴장에는 전송하지 않는다.
2. 기존 실행 엔진의 `STARTER_NOW`·`ADD_NOW` 또는 `REDUCE_NOW`·`EXIT_NOW`와 주문 방향이 일치한다.
3. 판단·시세·계좌 시각이 시간대 명시, 미래 아님, 생성 이전 수신 아님, 최대 120초 미만이다.
4. 시세는 같은 종목의 실행 준비된 KIS 정규장 원화 시세다. 지정가는 호가 단위 및 관측가 대비 기본 1% 범위다.
5. 계좌는 같은 VTS 계좌의 완전한 잔고다. 매수는 `VTTC8908R`의 **미수 없는 매수금액·수량**을 사용한다.
6. 수량·지정가는 양의 정수다. 현금 하한·종목 집중·기존 미체결 예약액·일일 한도를 함께 확인한다.
7. 위험 축소 매도는 매수 여력·현금 하한·매수 집중도 조건과 분리하되, 매도 가능 보유수량과 이미 예약한 매도수량을 넘지 않는다.

명령행 주문은 입력 파일에서 계좌 잔고를 받지 않고 전송 직전 모의 서버에서 잔고와 매수가능을 조회한다.
시세와 실행 판단은 원래 관측 시각을 보존한 기존 실행 산출물로 제공해야 한다. 과거 분석의 시각을 현재로 바꾸면 안 된다.
로컬 가격 파일만으로 모의 서버 접속·체결을 검증했다고 표현하지 않는다.

## 명령

프로젝트 환경에서 실행한다. 아래 명령은 `readiness`와 `probe` 외에는 준비된 비공개 로컬 파일을 요구한다.

```powershell
python -m tools.kis_paper --output .runtime/kis-paper-readiness.json readiness
python -m tools.kis_paper --output .runtime/kis-paper-read-probe.json probe
python -m tools.kis_paper --output .runtime/kis-paper-receipt.json submit --journal .runtime/kis-paper.sqlite --policy .runtime/kis-paper-policy.json --input .runtime/kis-paper-order.json --paper-enabled
python -m tools.kis_paper --output .runtime/kis-paper-reconciled.json reconcile --journal .runtime/kis-paper.sqlite --policy .runtime/kis-paper-policy.json --intent-id <원래-의도-ID>
python -m tools.kis_paper --output .runtime/kis-paper-cancel-request.json cancel --journal .runtime/kis-paper.sqlite --policy .runtime/kis-paper-policy.json --intent-id <원래-의도-ID> --paper-enabled
python -m tools.kis_paper --output .runtime/kis-paper-status.json status --journal .runtime/kis-paper.sqlite --policy .runtime/kis-paper-policy.json
```

정책 예제는 `{"allowed_tickers":["005930"]}`처럼 종목 허용목록을 명시하며 나머지 한도는 기본값을 사용한다.
입력 주문은 정확히 `intent_id,ticker,side,quantity,limit_price,signal,quote` 일곱 필드를 갖는다.
의도 ID는 같은 추천·조건·계좌의 같은 주문에 계속 같은 값을 사용해야 한다.

```json
{
  "intent_id": "<분석과-실행조건에-연결된-고정-ID>",
  "ticker": "005930", "side": "BUY", "quantity": 1, "limit_price": 70000,
  "signal": {
    "signal_id": "<기존-추천의-고정-ID>", "ticker": "005930",
    "decision_now": "STARTER_NOW", "execution_ready": true,
    "available_at": "<원래-실행판단-시각>", "valid_until": "<원래-만료시각>"
  },
  "quote": {
    "ticker": "005930", "provider": "kis", "currency": "KRW",
    "session": "regular", "execution_ready": true, "instrument_type": "STOCK",
    "last_price": 70000, "observed_at": "<원래-시세관측-시각>",
    "ingested_at": "<실제-자료수신-시각>"
  }
}
```

이 JSON은 구조 설명용이며 실제 주문 지시가 아니다. 예제 가격·종목·수량을 현재 추천으로 해석하지 않는다.

## 장애와 검증

같은 의도는 같은 본문이면 저장된 접수를 반환하고, 다른 수량·가격·추천으로 재사용하면 거절한다.
네트워크 전송 전에 영속화하므로 강제 종료·응답 유실 뒤에도 중복 주문을 전송하지 않는다.
여러 로컬 실행기는 같은 원장 잠금을 공유해 현금 예약 검사와 전송을 직렬화한다.
전송 대기·인증 동안 유효시간이 지나면 전송 직전에 다시 확인한다.

조회 응답의 주문일·주문시각·종목·방향·수량·지정가를 기존 의도와 비교한다.
빈 응답·중복·미래·누락·잘못된 시각·이미 확인한 체결수량 감소는 미확인으로 차단한다.
다른 거래일의 DAY 주문 취소를 새 거래일에 전송하지 않는다.
공식 취소가능수량 조회 예제에는 모의 TR ID가 없어서 실계좌 조회로 대체하지 않는다.
모의 당일 주문 조회의 검증된 잔량으로 취소 요청을 보내고, 이후 증권사 취소 확인을 기다린다.

검증은 외부 API 없이 정상·빈·미래·누락·잘못된 시각, 호스트 격리, 접수/체결 구분,
부분체결·취소·재시작·응답 유실·중복·현금 예약·정산된 모의 체결 분류를 픽스처로 검사한다.
전용 접속정보가 없으면 서버 실증은 `MISSING_DEMO_SETTINGS`로 남긴다.
그 상태에서 인증·주문·부분체결·취소를 실제 서버로 검증했다고 보고하지 않는다.

## 공식 근거

2026-10-18에 한국투자증권 공식 저장소의 현재 예제를 읽어 경로·ID·수신 필드를 재확인했다.
구형 080x 예제와 혼용하지 않고 현재 `examples_llm`의 ID를 사용한다.

- [호스트·실전/모의 설정](https://github.com/koreainvestment/open-trading-api/blob/main/kis_devlp.yaml)
- [현금 지정가 주문: VTTC0012U·VTTC0011U](https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/order_cash/order_cash.py)
- [정정취소: VTTC0013U](https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/order_rvsecncl/order_rvsecncl.py)
- [당일 주문체결: VTTC0081R](https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/inquire_daily_ccld/inquire_daily_ccld.py)
- [매수가능: VTTC8908R·미수 없는 금액/수량](https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/inquire_psbl_order/inquire_psbl_order.py)
- [주문시각·누적 체결수량의 필드 정의](https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/inquire_daily_ccld/chk_inquire_daily_ccld.py)
- [실전 ID만 있는 취소가능수량 예제](https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/inquire_psbl_rvsecncl/inquire_psbl_rvsecncl.py)
