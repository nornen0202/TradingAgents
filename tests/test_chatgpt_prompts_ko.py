from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPTS = (
    "prompts_kr_for_chatgpt.md",
    "prompts_us_for_chatgpt.md",
    "prompts_overlay_context_followup_for_chatgpt.md",
    "prompts_youtube_prism_context_followup_for_chatgpt.md",
)


def test_prompts_stay_compact_and_korean_action_first() -> None:
    for name in PROMPTS:
        text = (ROOT / "Docs" / name).read_text(encoding="utf-8")
        # Full scheduled prompts stay self-contained without an extra attachment.
        assert len(text) < 14_000, name
        assert "한국어" in text, name

    for name in ("prompts_kr_for_chatgpt.md", "prompts_us_for_chatgpt.md"):
        text = (ROOT / "Docs" / name).read_text(encoding="utf-8")
        assert "보유 유지" in text, name
        assert "종가 확인 후 판단" in text, name
        assert "웹 검색/심층 조사" in text, name
        assert "https://nornen0202.github.io/TradingAgents/index.html" in text, name
        assert "https://nornen0202.github.io/TradingAgents/llms.txt" in text, name
        assert "mobile/strategy.json" in text, name
        assert "mobile/public.json" in text, name
        assert "account/public.json" in text, name
        assert "파일을 직접 첨부하지 않고" in text, name
        assert "404" in text, name
        assert "프로젝트 원안" in text, name
        assert "최신 웹 검증" in text, name
        assert "`단기`" in text and "`중기`" in text and "`장기`" in text, name
        assert "모든 보유 종목" in text, name
        assert "모바일용 핵심 전략표" in text, name
        assert "종목별 상세 전략표" in text, name
        assert "| 종목 | 현재 행동 | 단기 조건 | 중장기 판단 | 위험/재확인 |" in text, name
        assert "추가 현금 투입 시나리오" in text, name
        assert "다른 계좌" in text, name
        assert "최소 4개" in text, name
        assert "최소 6개월" in text, name
        assert "현재 충족 여부·판정시각" in text, name
        assert "취소·재평가 조건" in text, name
        assert "같은 문구를 조건 없이 단독으로 쓰지 마라" in text, name
        assert "미완성 답변" in text, name
        assert "계좌 식별정보가 제거됐는가" in text, name
        assert "AVOID_OR_EXCLUDE" not in text, name
        assert "WAIT_CLOSE" not in text, name

    kr = (ROOT / "Docs" / "prompts_kr_for_chatgpt.md").read_text(encoding="utf-8")
    assert "DART" in kr
    assert "한국거래소/KIND" in kr
    assert "KOSPI/KOSDAQ" in kr

    us = (ROOT / "Docs" / "prompts_us_for_chatgpt.md").read_text(encoding="utf-8")
    assert "SEC EDGAR" in us
    assert "정규장, pre-market, after-hours" in us
    assert "USD/KRW" in us
    assert "최소 4개 시나리오를 USD와 KRW로" in us


def test_youtube_previous_day_fallback_is_explicitly_non_actionable() -> None:
    text = (ROOT / "Docs" / "prompts_youtube_prism_context_followup_for_chatgpt.md").read_text(
        encoding="utf-8"
    )
    assert "직전 KST 날짜" in text
    assert "실행 판단 상향 근거로 사용하지 않는다" in text


def test_scheduled_quality_contract_is_embedded_in_both_prompts() -> None:
    for market in ("kr", "us"):
        text = (ROOT / "Docs" / f"prompts_{market}_for_chatgpt.md").read_text(encoding="utf-8")
        assert text.count("## 프롬프트 시작") == 1
        assert text.count("## 프롬프트 끝") == 1
        body = text.split("## 프롬프트 시작", 1)[1].split("## 프롬프트 끝", 1)[0]
        for requirement in (
            "2026-09-18 v4",
            "조회 실패를 자료 부재나 악재로 단정하지 않는다",
            "이전 추천은 체결 사실이 아니다",
            "A 바로 다음에 E-1 모바일표",
            "0원+4개 양수 시나리오",
            "조건 완결 행 수/대상 행 수",
            "안전 제한·인증 요구는 우회하지 않는다",
            "예약·알림·모델 설정은 변경하지 않는다",
        ):
            assert requirement in body


def test_evidence_risk_and_review_requirements() -> None:
    for market in ("kr", "us"):
        text = (ROOT / "Docs" / f"prompts_{market}_for_chatgpt.md").read_text(encoding="utf-8")
        for requirement in (
            "적격 후보 0개", "부분 스크리닝", "순위 점수는 상승확률이 아니다",
            "완료된 봉과 진행 중인 봉", "현금흐름 → 기업가치",
            "가정을 표시한 조건부 수량", "실제 최대손실이나 체결 보장이 아니다",
            "백테스트 성과는 미산출", "생존편향", "시간순 검증",
            "실제 체결 기록이 있을 때만", "문제 위치 → 확인 근거 → 판단 영향 → 수정안",
            "최근 5회 완료 보고서", "기록이 없으면 미실시",
        ):
            assert requirement in text, (market, requirement)
    us = (ROOT / "Docs" / "prompts_us_for_chatgpt.md").read_text(encoding="utf-8")
    assert "13F는 분기말 보유공시" in us
    assert "당일 기관 순매수·실시간 자금 유입으로 해석하지 않는다" in us


def test_package_audit_controls_are_shared_and_self_contained() -> None:
    sections = []
    for market in ("kr", "us"):
        text = (ROOT / "Docs" / f"prompts_{market}_for_chatgpt.md").read_text(encoding="utf-8")
        body = text.split("## 프롬프트 시작", 1)[1].split("## 프롬프트 끝", 1)[0]
        sections.append(body.split("### 5-1.", 1)[1].split("### 6.", 1)[0])
        for requirement in (
            "가중치는 결과를 보기 전에 고정",
            "잔여 항목을 100점으로 재환산하지 않는다",
            "데이터 충족률", "별도 허용 없는 신용·공매도·레버리지·인버스·파생상품",
            "기존 보유의 위험·축소 검토는 생략하지 않는다",
            "정보 부족은 0주가 아니라 수량 산출 보류",
            "1회 주문한도 / 분할 전체 아이디어 투입한도 / 기존 보유 포함 종목한도",
            "예약액을 이중 차감하지 않는다", "나눠 주문해 한도를 우회하지 않는다",
            "낙폭한도를 거래별 손실예산으로 대체하지 않는다",
            "진입구간 상단 기준 수량·손익비", "확률 가중 기대수익이 아니다",
            "부분 익절 뒤 잔량 실패 경로", "독립 증거로 중복 계산하지 않는다",
            "컨센서스 확인 없이는 서프라이즈를 단정하지 않으며",
            "종가 신호의 같은 종가 체결", "배당 이중 계산을 금지한다",
            "R배수는 미산출", "일별 평가자산·입출금",
            "중대 오류가 해결되지 않으면 해당 행동을 보류",
            "추가입금 0원 기본안+서로 다른 양수 가상 예산 4개, 총 5개 이상",
            "확률(근거 없으면 미산출)", "신규 후보는 적격 0~5개",
            "(1+현지수익률)×(1+기준통화/외화 환율수익률)−1",
        ):
            assert requirement in body, (market, requirement)
        assert "소액·중간·확대의 가상 예산 4개" not in body
        assert "신규 후보는 상위 5개만" not in body
        assert "비용 차감 기대이익/계획손실" not in body
        assert "프롬프트 패키지를 첨부" not in body
    assert sections[0] == sections[1]
