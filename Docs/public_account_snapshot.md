# 공개 계좌 스냅샷

Daily Codex Analysis가 KIS 읽기 전용 계좌 스냅샷을 만든 뒤 GitHub Pages 전체 사이트를 재빌드할 때, `[site].publish_account_snapshot = true`이면 별도 공개 계좌 페이지를 함께 생성한다.

- 사람용 페이지: `https://nornen0202.github.io/TradingAgents/account/`
- 앱·AI용 JSON: `https://nornen0202.github.io/TradingAgents/account/public.json`
- AI 탐색 안내: `https://nornen0202.github.io/TradingAgents/account/llms.txt`
- JSON 스키마 식별자: `tradingagents.public-account-snapshot/v1`

페이지와 JSON은 국내(`markets.kr`)와 해외(`markets.us`)의 최신 유효 스냅샷을 분리한다. 보유 종목, 수량, 매도 가능 수량, 평균단가, 현재가, 매입금액, 평가금액, 평가손익, 수익률, 현금·총 평가액 요약을 게시한다. KIS 계좌 어댑터가 금액을 원화로 정규화하므로 금액 필드에는 `_krw` 접미사를 사용한다.

공개 변환기는 원본 `account_snapshot.json`을 그대로 복사하지 않는다. 계좌번호, 고객 식별정보, 스냅샷 ID, 미체결 주문, 현금 진단 원문, 브로커 응답은 공개 산출물에서 제외한다. 계좌 현황 공개가 필요 없는 배포에서는 `publish_account_snapshot = false`를 유지한다.
