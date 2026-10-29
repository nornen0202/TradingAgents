"""A useful source-bound fallback when model synthesis is unavailable or slow."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from tradingagents.dataflows.market_policy import aware_datetime

from .runtime import WorkRuntimeError, validate_packet, _validate_report_draft, _validate_report_packet_coverage


def _text(value) -> str:
    if value is None or value == "":
        return "산출 없음"
    if isinstance(value, list):
        return " / ".join(_text(item) for item in value) or "산출 없음"
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _identity(ticker):
    return str(ticker).upper().removesuffix(".KS").removesuffix(".KQ")


def _time_label(value):
    clock = aware_datetime(value)
    return clock.astimezone(ZoneInfo("Asia/Seoul")).strftime("%m/%d %H:%M KST") if clock else "확인 불가"


def compose_investor_draft(packet: dict, *, now: datetime) -> tuple[str, dict]:
    validate_packet(packet)
    body = packet["body"]
    policy = body.get("publication_policy") or {}
    if policy.get("profile") != "investor":
        raise WorkRuntimeError("draft-investor requires a packet prepared with --report-policy investor")
    current = body.get("current") or {}
    freshness = current.get("freshness_receipt") or {}
    coverage = current.get("universe_coverage") or {}
    context = body.get("supporting_context") or {}
    rows = (current.get("bundle") or {}).get("strategy_table") or []
    if not rows:
        raise WorkRuntimeError("No investor strategies are available")
    matches = {}
    for source in ("youtube", "prism"):
        payload = context.get(source) or {}
        if payload.get("source_health") != "OK":
            continue
        for event in payload.get("events") or []:
            for ticker in (event.get("relevance") or {}).get("matched_tickers") or []:
                matches.setdefault(_identity(ticker), []).append({
                    "source": source, "event_key": event["event_key"], "affected_field": "research_priority",
                    "direction": "REVIEW", "reason": "관련 외부 자료 도착: 후속 검토 우선순위에 반영. 이 기본 보고서는 원분석의 방향·신뢰도를 재평가하지 않음.",
                    "execution_gate_override": False})
    # The ordering highlights risk reduction without treating it as a new buy.
    rows = sorted(rows, key=lambda row: (
        {"RISK_REDUCTION": 0, "ENTRY_REVIEW": 1, "MONITOR": 2}.get(row["investment_plan"]["purpose"], 3),
        row.get("display_priority") or 0))
    strategies = []
    for rank, row in enumerate(rows, 1):
        thesis = deepcopy(row.get("thesis") or {})
        plan = deepcopy(row["investment_plan"])
        thesis.setdefault("horizon", "원분석 기간 미지정; 표시된 검토일까지 재평가")
        if thesis.get("confidence") is None:
            thesis["confidence"] = 0.0
            thesis["confidence_note"] = "원분석 신뢰도 미제공"
        thesis["invalidation_action"] = thesis.get("invalidation_action") or "무효화·축소 조건을 먼저 확인하고 계획을 재평가"
        thesis["position_sizing"] = thesis.get("position_sizing") or "수량 산출 없음; 현재 보유·현금·위험 한도로 결정"
        if not thesis.get("entry_conditions") or not thesis.get("invalidation_conditions"):
            thesis["data_needed_reason"] = thesis.get("data_needed_reason") or "원분석에 진입 또는 무효화 조건이 없어 자동 보충하지 않음"
        strategy = {
            "ticker": row["ticker"], "display_name": row.get("display_name"), "rank": rank,
            "portfolio_role": row.get("portfolio_role") or "watchlist",
            "thesis": thesis, "investment_plan": plan, "execution": deepcopy(row["execution"]),
            "source_contributions": [{"source": "tradingagents", "direction": "MAINTAIN",
                                      "reason": "날짜가 검증된 원분석을 그대로 전달", "execution_gate_override": False}],
        }
        matched = matches.get(_identity(row["ticker"]), [])
        strategy["source_contributions"].extend(matched)
        if matched:
            thesis["research_priority"] = "관련 외부 자료 후속 검토 우선"
        elif matches:
            strategy["no_relevant_evidence_reason"] = "전송된 정상 외부 자료 중 이 종목과 연결된 항목 없음"
        strategies.append(strategy)
    market = "미국" if packet["surface"] == "us" else "국내"
    draft = {
        "binding": {key: packet[key] for key in ("surface", "event_id", "source_sha256")},
        "title": f"{market} 투자 계획 — 가격 구간과 위험 관리",
        "generated_at": now.isoformat(), "as_of": freshness.get("market_data_oldest_at"),
        "source_health": body.get("source_health"), "report_mode": "INVESTOR_PLAN",
        "summary": "시세 지연·휴장과 관계없이 원분석의 투자 방향, 가격 구간, 검토 기간, 축소·매도 조건을 제공합니다.",
        "top_actions": [], "strategies": strategies, "coverage_receipt": coverage,
        "model_receipt": body.get("model_provenance", {}),
        "source_summary": {
            "publication_policy": policy, "freshness_receipt": freshness,
            "analysis_receipt": current.get("analysis_receipt"),
            "external_evidence_receipt": context.get("receipt_contract"),
            "composition": "DETERMINISTIC_SOURCE_PROJECTION_NO_NEW_MODEL_SYNTHESIS",
            **({"report_context_receipt": body["report_context"]} if "report_context" in body else {}),
        },
        "next_checkpoint": "종목별 검토일 또는 새 실적·공시·무효화 발생 시 재평가. 주문 검증은 실제 거래 시 별도 수행.",
    }
    labels = {"BUY": "조건부 매수", "HOLD": "보유·관찰", "REDUCE": "비중 축소", "SELL": "매도", "AVOID": "신규 진입 회피", "RESEARCH": "자료 확인"}
    risks = {"NONE": "별도 축소 신호 없음", "HOLD": "보유 유지", "REDUCE_RISK": "위험 축소", "STOP_LOSS": "손실 제한",
             "EXIT": "청산 검토", "TAKE_PROFIT": "분할 이익 실현", "TRIM_TO_FUND": "자금 재배분"}
    confirmations = {"close": "종가 확인", "next_day": "다음 거래일 확인", "two_bar": "원분석의 2개 봉 확인",
                     "intraday": "장중 확인", "volume_confirmed": "거래량 확인"}
    statuses = {"CONDITIONAL_PLAN": "조건부 계획", "REVIEW_REQUIRED": "재검토 필요", "DATA_NEEDED": "자료 확인 필요"}
    lines = [f"# {draft['title']}", "", "원분석을 정리한 기본 보고서입니다. 새로운 분석·시세 조회는 수행하지 않았습니다.", "",
             "## 먼저 볼 계획", ""]
    for strategy in strategies[:3]:
        plan = strategy["investment_plan"]
        zones = plan["price_zones"]
        focus = next((z for z in zones if z["level_type"] in {"STOP_LOSS", "INVALIDATION", "TRIM"}), zones[0] if zones else None)
        zone_text = f" · 우선 확인 {focus['low']:g}–{focus['high']:g}" if focus else ""
        lines.append(f"- **{strategy['ticker']} · {risks.get(plan['risk_action'], plan['risk_action']) if plan['purpose'] == 'RISK_REDUCTION' else labels.get(plan['stance'], plan['stance'])}**: {statuses[plan['status']]}{zone_text} · 검토일 {_time_label(plan['review_window']['review_by'])}")
    missing = {key: value for key, value in coverage.items()
               if ('missing' in key or 'failed' in key or key == 'analysis_failures') and value}
    if missing:
        lines.extend(["", "## 누락·실패 범위", "", _text(missing)])
    lines.extend(["", "## 자료 기준", "",
                  f"작성 {_time_label(now)} · 원분석 {_time_label(freshness.get('analysis_completed_at'))}", "",
                  f"시세 {_time_label(freshness.get('market_data_oldest_at'))} ~ {_time_label(freshness.get('market_data_latest_at'))} · 계좌 {_time_label(freshness.get('account_as_of'))}", "",
                  f"분석 거래일 {_text(freshness.get('analysis_trade_date_oldest'))} ~ {_text(freshness.get('analysis_trade_date_latest'))}. 발행이 원자료를 갱신하지 않습니다.", "",
                  "검토일은 재평가 기한이며 주문 유효기간이 아닙니다. 새 실적·공시나 무효화가 먼저 발생하면 바로 재검토합니다."])
    lines.extend(["", "## 종목별 조건과 가격 범위", ""])
    for strategy in strategies:
        plan, thesis = strategy["investment_plan"], strategy["thesis"]
        lines.extend([f"### {strategy['ticker']} · {_text(strategy.get('display_name'))} — {labels.get(plan['stance'], plan['stance'])}", "",
                      f"{statuses[plan['status']]} · 원분석 {_time_label(plan['analysis_as_of'])} · 검토일 {_time_label(plan['review_window']['review_by'])}", ""])
        if plan["price_zones"]:
            lines.extend(["| 가격 구간 | 용도 | 확인 기준 | 근거 |", "|---|---|---|---|"])
            for zone in plan["price_zones"]:
                price = f"{zone['low']:g}" if zone['low'] == zone['high'] else f"{zone['low']:g}–{zone['high']:g}"
                basis = "원분석 구간" if zone['basis'] == 'SOURCE_RANGE' else "원분석 가격선" if zone['basis'] == 'SOURCE_LEVEL' else "정책상 1% 검토 여유폭; 주문 허용폭 아님"
                lines.append(f"| {price} {_text(zone.get('currency')) if zone.get('currency') else ''} | {_text(zone['label']).replace('|', '/')} | {confirmations.get(zone['confirmation'], _text(zone['confirmation']))} | {basis} |")
        else:
            lines.append("검증된 숫자 구간이 없어 임의 가격을 제안하지 않습니다.")
        lines.extend(["", f"**진입·유지 조건:** {_text(thesis.get('entry_conditions'))}", "",
                      f"**무효화·축소 조건:** {_text(thesis.get('invalidation_conditions'))}", "",
                      f"**조건 훼손 시:** {_text(thesis.get('invalidation_action'))}", "",
                      f"**규모:** {_text(thesis.get('position_sizing'))}", "",
                      f"**거래 전 확인:** {_text(plan['before_acting'])}", ""])
        if plan["excluded_levels"]:
            lines.extend(["일부 가격선 또는 조건의 근거가 불완전해 재검토가 필요합니다. 확정된 주문 조건으로 사용하지 않습니다.", ""])
        if plan.get("source_trigger_valid_until"):
            lines.extend([f"원래 주문 트리거 유효시각: {plan['source_trigger_valid_until']} (검토 기간과 별개이며 자동 연장되지 않음)", ""])
    lines.extend(["## 다음 확인", "", draft["next_checkpoint"], "",
                  "COVERAGE_RECEIPT " + json.dumps(coverage, ensure_ascii=False, separators=(",", ":")), "",
                  'MOBILE_HANDOFF {"owner":"external_github_notification_pipeline","status":"PENDING_EXTERNAL_VERIFICATION","work_sent_notification":false}'])
    _validate_report_draft(draft, surface=packet["surface"], event_id=packet["event_id"], source_sha256=packet["source_sha256"])
    _validate_report_packet_coverage(draft, packet, now=now)
    return "\n".join(lines), draft


def write_investor_draft(packet_path: Path, markdown_path: Path, structured_path: Path) -> dict:
    try:
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        markdown, draft = compose_investor_draft(packet, now=datetime.now().astimezone())
        for path in (markdown_path, structured_path):
            path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(markdown, encoding="utf-8")
        structured_path.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")
    except (OSError, ValueError) as exc:
        raise WorkRuntimeError(f"Could not compose investor report: {type(exc).__name__}") from exc
    return {"status": "DRAFTED", "event_id": packet["event_id"], "markdown_path": str(markdown_path.resolve()),
            "structured_path": str(structured_path.resolve()), "published": False}
