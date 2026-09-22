# 모의투자 연결: 사용자는 신청과 세 항목 입력만

Windows에서 간편 등록 화면을 열면 공식 신청 페이지로 이동하고, 발급받은 정보를 저장·점검할 수 있다. 실거래 주문이나 모의 매매 주문을 보내는 화면이 아니다.

## 1. 모의계좌가 없다면 발급

[한국투자증권 모의투자 안내](https://securities.koreainvestment.com/main/research/virtual/_static/TF07da010000.jsp)에서 **모의투자안내**를 눌러 연결되는 공식 모의투자 페이지로 이동한다. 이미 계좌가 있다면 이 단계를 건너뛴다.

로그인·본인인증과 신청 완료는 사용자가 처리한다. 새 실계좌 개설이나 기존 계좌로의 입금은 이번 작업의 요구사항이 아니다. 홈페이지가 추가 자격 요건을 안내하면 해당 안내를 확인한다.

## 2. 그 모의계좌에 KIS Developers 신청

[KIS Developers 서비스 신청](https://securities.koreainvestment.com/main/customer/systemdown/RestAPIService.jsp)을 연다. 로그인 후 **모의투자 계좌**를 선택해 신청한다. 실계좌용 키가 이미 있어도 모의투자용 키는 별도다. 본인인증·약관 확인 및 동의는 직접 진행한다. 화면 배치는 변경될 수 있다.

완료 화면에서 모의투자용 **App Key**, **App Secret**, **계좌번호 전체 10자리(앞 8자리 + 뒤 상품코드 2자리)**를 확인한다. 공식 [현재 설정 안내](https://github.com/koreainvestment/open-trading-api#34-kis-open-api-신청-및-설정)와 [신청 절차 설명](https://github.com/koreainvestment/open-trading-api/blob/main/legacy/README.md)을 근거로 정리했다. 신청이 이미 끝났다면 재신청하지 않고 기존 정보를 사용한다.

## 3. 간편 등록 화면에 세 항목 붙여넣기

준비된 **TradingAgents 모의투자 연결** 바로가기를 실행한다. 다른 PC/체크아웃에서는 프로젝트 환경 준비 후 `tools/setup_kis_demo.ps1` 또는 `python tools/setup_kis_demo.py`로 열 수 있다.

1. 모의투자 App Key
2. 모의투자 App Secret
3. 모의계좌번호 전체 10자리 — 하이픈이 있어도 된다.

**저장하고 연결 확인**을 누르면 완료된다. 계좌를 8자리와 2자리로 나누거나 설정 파일을 수정할 필요가 없다. 이미 저장했다면 **저장된 정보로 다시 확인**을 사용한다. 키를 채팅에 전달하지 않는다.

| 결과 | 의미 / 처리 |
|---|---|
| 연결 확인 완료 | 인증·잔고·당일 주문 조회 성공. 다음 작업은 계좌 대사이며 매매 검증 완료를 뜻하지 않는다 |
| 저장됐지만 연결 미확인 | 모의계좌와 API 신청이 완료됐는지, 실계좌 키를 잘못 입력하지 않았는지 확인한 후 다시 점검 |
| 저장 정보를 열 수 없음 | 다른 Windows 사용자/PC이거나 파일이 손상됐을 수 있다. 현재 사용자로 재등록 |

저장 위치는 현재 Windows 사용자의 `%LOCALAPPDATA%\TradingAgents\kis-demo.dpapi`다. 내용은 Windows 사용자용으로 암호화된다. 조회 점검 결과는 같은 폴더의 `kis-demo-readiness.json`에 키·계좌번호 없이 남는다. 암호화 파일이 존재하면 기존 환경변수/JSON의 모의 설정보다 우선 사용한다. 실계좌 설정은 변경하지 않는다.

현재 방식은 REST 조회와 향후 모의 주문에 필요한 최소 입력이다. 추후 개인 체결 알림 WebSocket을 연결할 때는 HTS ID 등이 추가로 필요할 수 있다. 같은 키로 여러 프로그램을 동시에 실행하지 않고, 연결 확인 후에는 여기서 조회 성공 여부만 알려주면 후속 계좌 대사를 진행할 수 있다.
