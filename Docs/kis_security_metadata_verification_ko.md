# KIS 현재 상품 메타데이터의 수집·시점 경계

공식 상품기본정보 API의 GET `search-info`/`CTPF1702R`만 명시적 real 데이터
클라이언트에 추가한다. 고정 매개변수는 `PRDT_TYPE_CD`(NAS512/NYS513/AMS529),
`PDNO`다. demo에서 real로 우회하지 않으며 계좌·주문 허용 목록은 변경하지 않는다.

공식 근거:
- [KIS 공식 요청 예제](https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/overseas_stock/search_info/search_info.py)
- [KIS 공식 출력 필드](https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/overseas_stock/search_info/chk_search_info.py)

현재 응답은 실제 요청 시작·응답 완료의 aware UTC 시각과 원문을 보존한다.
분석용 후보 추출은 명시적 `analysis_as_of`보다 수집 완료가 늦으면 거절한다.
상장일이나 공급자 마지막 수신시각을 과거 가용시각으로 사용하지 않는다.
빈/오류/복수 응답, 시각 누락·오류·미래, 유효하지 않은 날짜·ISIN 체크섬,
미래 상장일, 통화 및 요청 봉투 오류를 외부 API 없는 Mock으로 검증한다.
가격·세금 등 동적 필드는 후보 출력에서 제외한다.

후보의 issuer_binding_verified/first_regular_listing_verified/
historical_identity_verified/price_history_shortening_authorized는 모두 false다.
공급자 거래소 코드의 의미와 발행사·증권 종류·안정 식별자의 연결은 별도 검증이
필요하다. 이 변경은 GEV 상장 전 이력 계약을 해결했다고 선언하지 않으며,
5년 이력·지표 최소 관측·원천 고정·원래 승인·연구 예산·주문 정책을 변경하지 않는다.
수집 시각 이전의 동일증권 연결 또는 정규 최초 상장 증거로 자동 등록하지 않는다.

실제 응답과 운영 경로 검증은 배포 이후 별도 증거다. 단위 검사 통과만으로
데이터 회복·연구·승인·체결·비용 평가가 완료됐다고 표시하지 않는다.
