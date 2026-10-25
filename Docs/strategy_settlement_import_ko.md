# 정상 전략의 비용·정산 근거 연결

2026-10-25 기준, 정상 전략 평가의 `actual_cost`와 `net_pnl`은 증권사 모의 주문 조회만으로 알 수 없었다. 누적 체결 대금이 확인되어도 정산된 개별 체결·양방향 수수료·세금·환전/기타 비용을 알 수 없기 때문이다. 기존 코드는 별도 명시적 체결 import가 있어도 정상 전략 평가에 연결하지 않았다.

## 공식 자료에서 확인한 범위

한국투자증권 공식 [국내 기간별손익일별합산조회 예제](https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/inquire_period_profit/inquire_period_profit.py)는 `TTTC8708R`과 일자·종목·계좌 범위를 사용한다. [출력 매핑](https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/inquire_period_profit/chk_inquire_period_profit.py)에 수수료·제세금·정산금액 필드가 있지만 일별/기간 합계가 특정 정상 전략 주문의 비용을 증명하지는 않는다. [해외 기간별매매손익 예제](https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/overseas_stock/inquire_period_profit/inquire_period_profit.py)는 `TTTS3039R`, 거래통화와 원화/외화 구분을 사용한다. 이 공개 코드 열람으로 모의 서버 지원이나 모의 계좌의 개별 주문 비용·정산 제공을 확인하지 못했다. **상태는 미확인**이며, 미지원이라고 단정하지 않는다.

모의 비용 API를 실전 호스트로 우회하는 기능은 없다. 계좌·일별 비용을 거래대금 비율로 배분하지 않으며, 사용자가 알려준 요율이나 10/30/50bp 민감도도 실제 청구 비용으로 승격하지 않는다.

## 검토된 원본을 입력하는 경로

`tradingagents.execution.strategy_settlement.import_strategy_settlement(broker, document, source_bytes=...)`는 기존 **모의** broker와 정상 전략 원장만 사용한다. HTTP 요청·주문·취소·새 계좌 생성은 수행하지 않는다. 이 함수의 호출은 실제 원본을 검토한 운영자가 맡으며, 정규 시세 생산자가 비용을 추정해 자동 호출하지 않는다.

`document.schema`는 `tradingagents.strategy-settlement/v1`이다. 필수 입력은 다음과 같다.

- `environment=demo`, 시장, 거래통화, 기존 계좌 scope, 정상 전략 intent ID와 원래 ACK의 broker order ID.
- `revision_id`, 첫 원본의 `previous_revision_id=null` 또는 현재 최신 정산 revision ID.
- `attribution=ORDER_EXECUTION`, `cost_coverage=ALL_COMPONENTS_IN_TRADING_CURRENCY`.
- `source.kind=KIS_DEMO_SETTLEMENT_DOCUMENT`, **원본 바이트의 SHA256**, 증권사 정산 문서의 `available_at`과 실제 로컬 수집 `observed_at`. 문서 가용 ≤ 로컬 관측 ≤ 검토 ≤ import 순서이며, 로컬 수집/검토 시각으로 원래 문서 가용 시각을 대체하지 않는다. 각 체결의 정산 시각도 문서 가용 시각 이전이어야 한다. 원본은 원장에 그대로 보존된다.
- `review.approved=true`, 검토자 식별값, 실제 검토 시각 및 `corrections_checked_through`. 검토자는 원본의 진위·페이지 완전성·개별 체결 귀속·항목 누락 여부를 독립적으로 확인해야 한다. 플래그 하나가 문서 진위를 자동 증명하지는 않는다.
- 각 실제 증권사 incremental fill의 ID, 수량, 가격, 체결·확인·정산 시각과 `commission`, `tax`, `fx_cost`, `other_cost`, 통화. 0도 원본에서 확인한 명시 값이어야 하며 누락을 0으로 바꾸지 않는다. 미국 비용이 원화로만 확인되거나 환전 비용/환산 근거가 불완전하면 이 USD 계약을 충족하지 않는다.

기존 owner·ACK·원주문 body/TR/거래소·불변 수량/가격·정상 전략 소유권·공유 paper lock을 대조한다. 각 incremental fill의 누적 수량과 대금이 기존 브로커 관측의 같은 체크포인트에 정확히 일치해야 한다. 마지막 누적 체결 전체를 덮지 않는 부분 입력은 완전한 정산으로 인정하지 않는다. 별도 검증 왕복·수동 주문은 정상 전략에 채택하지 않는다.

## 정정과 과거 조회

`strategy_settlement_sources`, `strategy_settlements`, `strategy_settlement_bindings`는 UPDATE/DELETE를 거부한다. 같은 revision/같은 입력 재호출은 no-op이고, 다른 입력의 ID 재사용·부모 분기·뒤로 간 원본 시각·다른 주문으로 fill ID 이동은 거절한다. 비용 정정은 이전 기록을 보존한 채 최신 부모를 지정하는 전체 주문 snapshot으로 추가한다. 이미 알려진 체결의 수량·가격·체결/확인 시각 변경은 이 비용 import만으로 처리하지 못하며, 증권사 대사를 먼저 해결해야 한다.

평가에는 기준 시각까지 실제 수집된 revision만 반영한다. 나중 비용 정정이 과거 성과를 소급 변경하지 않는다. import 당시 원장의 owner, 정상 전략 원문·불변 terms, broker 요청 body/TR, ACK/fingerprint와 검증된 누적 관측·대사·이슈 이력 prefix를 별도로 고정한다. 비용을 읽을 때 이 고정 원본과 현재 원장을 다시 비교한다. 원래 ACK/body/TR이나 기존 관측이 바뀌거나 없어지면 비용을 인정하지 않는다. 새 관측은 기준 시각 필터 후 기존 prefix를 보존하는 추가만 허용하므로 나중 부분 체결이 이전 cutoff의 비용을 바꾸지 않는다.

`reconciliation_issues`는 현재 주문을 엄격하게 차단하는 기존 가변 상태다. 이것을 과거 시점의 이슈 상태로 사용하지 않는다. 공통 모의 저널은 원래 SET/CLEAR 위치에서 기존 broker clock으로 `reconciliation_issue_history`를 append-only 기록한다. 관측·수집 시각과 이전 전이의 hash를 보존하며, 같은 SET/같은 원인 반복은 새 행을 만들지 않는다. 검증된 원래 KR/US 대사 경로만 CLEAR를 기록하고 현재 테이블에서 지운다. 시계가 역행하거나 기록에 실패하면 현재 주문 차단을 없애지 않는다.

`strategy_settlement_evidence(..., historical=False)`의 기본 현재 평가는 현재 활성 이슈를 계속 차단한다. 명시적 `historical=True`는 평가 cutoff까지 가용한 dated 전이만 선택한다. 따라서 이후 SET은 과거의 확인된 CLEAR를 바꾸지 않고, 이후 CLEAR도 이슈가 활성화되어 있던 과거 시점을 정상으로 만들지 않는다. 전체 append-only chain의 끝과 현재 가변 상태가 불일치하면 날짜 없는 변경 또는 훼손으로 간주해 보수적으로 미검증 처리한다.

기존 날짜 없는 활성 이슈를 처음 발견하면 `LEGACY_UNKNOWN`으로 원래 시작 시점 미상을 보존한다. 처음 본 시각을 발생 시각으로 소급하거나 미래 SET으로 가정하지 않는다. 이런 이력은 이전 cutoff도 미검증으로 남기며, 나중 실제 CLEAR가 과거를 정상화하지 않는다. 원래 대사로 CLEAR가 관측된 이후의 상태만 새롭게 확인한다. schema와 전이는 정상 broker 초기화/원래 import·writer에서만 생성한다. 읽기 전용 조회는 DDL이나 상태 수정을 하지 않는다.

읽기 검증 함수는 일반 JSON status가 아닌 해당 원장 조회에서 만든 내부 읽기전용 객체를 반환한다. 이 객체는 정확한 주문 관측 목록·시장·평가 cutoff에 묶이며, 내용 조회로 얻은 dict/list는 별도 사본이다. `COMPLETE_REVIEWED_IMPORT` 문자열을 가진 임의 dict나 저장된 화면 JSON을 다시 넘겨 실제 비용을 주장할 수 없다. API/UI도 원장에서 다시 검증한 평가만 사용해야 한다. 이는 JSON 경계의 상태 위조를 차단하는 내부 계약이며, 동일 Python 프로세스의 악성 코드를 방어하는 보안 경계라는 뜻은 아니다.

## 평가와 남은 기준

정상 전략의 **모든 양수 체결 주문**에 완전한 동일통화 비용·정산 증거가 있을 때만 `COMPLETE_REVIEWED_IMPORT`, `fees_known=true`, `settlement_known=true`가 된다. 이때 `actual_cost`는 확인한 체결의 실제 비용 합계, `net_pnl`은 기존 비용 전 평가손익에서 이 비용을 뺀 값이다. 열린 포지션의 미래 매도 비용은 포함하지 않는다. 실제 체결 시각·수량을 이용하는 FIFO는 매수/매도 비용을 청산 수량에 배분해 `realized_actual_cost`, `realized_net_pnl`을 제공한다. 동일 계좌의 다른 모드/전략 거래는 섞지 않는다.

한쪽 비용·세금·환전·통화·정산·귀속이 빠지면 `actual_cost`와 `net_pnl`은 계속 null이다. 기존 단순 `cost`만 가진 legacy lifecycle 체결도 전체 비용 커버리지를 증명하지 못하므로 자동 채택하지 않는다. `actual_cost_basis=OPERATOR_REVIEWED_EXECUTION_SETTLEMENT_IMPORT`는 운영자의 원본 검토 경로라는 뜻이며 API가 독립적으로 제공·검증했다는 뜻이 아니다.

코드와 오프라인 fixture의 성공은 운영 계좌의 비용 수집 성공이나 실투자 준비 완료가 아니다. 실제 정상 BUY/SELL, 실제 비용·정산 원본, 관측 기간·반복 표본·슬리피지·낙폭·기간 외 검증은 별도 필요하다. 실계좌 주문과 실제 투자 자동 전환은 항상 비활성이다.

## 화면과 API 검증

정상 화면 서버는 기존 state-dir의 `kis-strategy` 원장 경로를 별도로 설정받는다. 독립 화면 CLI는 `--strategy-ledgers`로 이미 있는 정상 전략 원장 디렉터리를 지정할 수 있다. HTTP 요청으로 원장 경로를 바꿀 수 없다. 원장 설정이 없거나 파일·시각·주문이 맞지 않으면 cached JSON의 COMPLETE 표시나 비용 숫자만으로 실제 비용을 표시하지 않는다.

API는 고정 시장 원장을 mode=ro/query_only로 열고 같은 기준 시각의 전체 평가와 마지막 100개 주문을 다시 구성한다. 캐시의 표시 주문 전체와 집계·가용 시각을 대조한다. 관측·수집·최초 체결·가용 시각이 모두 없고 양쪽 수량과 대금이 정확히0인 주문에 한해서만, 캐시의 접수·조건 차단·거절·미전송 상태와 과거 재구성의 UNKNOWN 차이를 허용한다. 이 새 미체결 주문 때문에 다른 확정 체결의 비용을 지우지 않는다. 주문 식별·조건·키 집합·시각·취소 상태와 관측된 체결 상태는 여전히 엄격 대조한다. 원장·계좌 범위·증권사 ID·원문·검토자 식별자는 API에 노출하지 않는다. 연결 핸들은 정상·오류 모두 즉시 닫는다. 현재 기본 rollback-journal 원장을 지원하며 활성 journal 또는 WAL/SHM이 있으면 선택적인 비용 조회를 보류한다. 원본을 복구하거나 immutable=1로 우회하지 않는다.

비용 원문을 검증했어도 열린 보유분의 평가 시세를 원장만으로 재현할 수 없으면 화면의 전체 순손익은 null이다. 확인된 실제 비용과 순서가 증명된 청산 FIFO 비용·실현 순손익만 표시할 수 있다. 과거 성과 행에 현재 비용을 소급해 붙이지 않는다. 상단은 시장별 정상 체결·왕복 표본, 첫 차단 이유, 다음 확인과 담당을 먼저 보여주고 상세 근거는 펼쳐 볼 수 있게 했다. 조회 오류가 나면 이전 요약을 현재 상태로 남기지 않는다.
