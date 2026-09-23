# GPT-6 Sol 기본 모델 전환 (2026-09-23)

프로젝트의 현재 실행 기본 모델을 `gpt-5.6-sol`에서 `gpt-6-sol`로 전환했다. 적용 대상은 대화형 분석의 quick/deep/output, 국내·미국 예약 분석의 quick/deep/output/writer/judge, YouTube 영상 분석과 일일 종합, 포트폴리오 행동 판정, GitHub Actions 실행 설정, 로컬 ChatGPT Work 작업 매니페스트다. CLI 모델 목록과 검증기에도 새 모델을 등록했다.

기존 reasoning effort는 역할별로 유지한다. 예약 분석은 quick/writer=`high`, deep/judge=`xhigh`, output=`medium`이고, YouTube는 quick/synthesis=`high`, deep=`xhigh`, output=`medium`이다. GPT-6 Sol의 공식 모델 ID와 지원 reasoning 수준은 [OpenAI 모델 문서](https://developers.openai.com/api/docs/models/gpt-6-sol)에서 확인할 수 있다. 기존 `gpt-5.6-sol`은 과거 실행 기록과 명시적 선택의 호환성을 위해 모델 목록에 남긴다.

설정 파일의 모델 이름을 바꾸는 것만으로 외부에 이미 등록된 작업이 자동 변경되지는 않는다. 로컬 ChatGPT Work 작업을 별도로 등록해 사용 중이면 `config/chatgpt_work_tasks.json`에 맞춰 해당 작업의 모델을 업데이트해야 한다. CI는 정적 설정과 단위 테스트를 검증하며, 실제 Codex 계정에서 모델을 호출할 수 있는지는 실행 전 preflight가 확인한다.
