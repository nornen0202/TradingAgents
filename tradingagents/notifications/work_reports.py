"""Notify verified report publications independently of producer completeness."""
from __future__ import annotations

from datetime import datetime, timezone
import re
from urllib.request import Request, urlopen
from uuid import uuid4

from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock
from tradingagents.work.runtime import validate_work_report
from .telegram import NotificationError


def canonical(archive, market, digest, *, now):
    from .local import read, timestamp
    if market not in {"kr", "us"} or not re.fullmatch(r"[0-9a-f]{64}", str(digest)):
        raise NotificationError("Invalid report notification binding.")
    path = archive / "work-reports" / market / "events" / f"{digest}.json"
    report = read(path)
    validate_work_report(report)
    if report["surface"] != market or report["report_sha256"] != digest:
        raise NotificationError("Canonical report binding changed.")
    published = timestamp(report["published_at"])
    draft = report["structured_report"]
    generated = timestamp(draft["generated_at"])
    if not generated <= published <= now:
        raise NotificationError("Report publication clock is invalid.")
    if draft.get("as_of") is not None and timestamp(draft["as_of"]) > generated:
        raise NotificationError("Report observation is future dated.")
    return report, path


def queue_completed(archive, state, *, now=None, publication_locked=False):
    if publication_locked:
        return _queue_locked(archive, state, now=now)
    try:
        with interprocess_file_lock(state / "publish.lock", timeout=0):
            return _queue_locked(archive, state, now=now)
    except TimeoutError:
        return


def _queue_locked(archive, state, *, now=None):
    from .local import queue, read
    now = now or datetime.now(timezone.utc)
    if read(state / "publication.json").get("status") != "DELIVERY_VERIFIED":
        return
    errors = []
    # Bootstrap only the two published latest reports, never the historical
    # archive. Each subsequent report hash has its own persistent outbox key.
    for market in ("kr", "us"):
        health = {"checked_at": now.isoformat(), "notification_status": "CHECKED"}
        try:
            path = state / "site/work/v1" / market / "report/latest.json"
            if path.is_file():
                current = read(path)
                report, source = canonical(archive, market, current.get("report_sha256"), now=now)
                if path.read_bytes() != source.read_bytes():
                    raise NotificationError("Published report differs from its canonical event.")
                queue(state, {"kind": "work_report", "market": market,
                              "event_id": report["event_id"], "report_sha256": report["report_sha256"],
                              "finished_at": report["published_at"]})
        except Exception as exc:
            errors.append(type(exc).__name__)
            health.update(notification_status="PENDING", error_type=type(exc).__name__)
        atomic_write_json(state / "notifications/health" / f"work-report-{market}.json", health)
    if errors:
        raise NotificationError("Report notification preparation pending: " + ",".join(errors))


def verify_report_live(site, relative):
    from tradingagents.local_automation import PUBLIC_BASE
    path = site / relative
    request = Request(f"{PUBLIC_BASE}/{relative}?verify={uuid4().hex}", headers={"Cache-Control": "no-cache"})
    with urlopen(request, timeout=30) as response:
        return response.read(path.stat().st_size + 1) == path.read_bytes()


def compose(event, archive, state):
    from .local import PUBLICATION_LOCK_TIMEOUT_SECONDS, read
    from tradingagents.local_automation import PUBLIC_BASE, verify_live
    market, digest = event.get("market"), event.get("report_sha256")
    report, source = canonical(archive, market, digest, now=datetime.now(timezone.utc))
    if event.get("event_id") != report["event_id"] or event.get("finished_at") != report["published_at"]:
        raise NotificationError("Report notification event changed.")
    relative = f"work/v1/{market}/report/events/{digest}"
    # A newer latest report must not change the destination of a queued notice.
    # Revalidate immutable JSON and readable HTML at send time, under the same
    # lock as the publisher. A push, ACK or queue receipt alone is insufficient.
    with interprocess_file_lock(state / "publish.lock", timeout=PUBLICATION_LOCK_TIMEOUT_SECONDS):
        site = state / "site"
        if (read(state / "publication.json").get("status") != "DELIVERY_VERIFIED"
                or (site / f"{relative}.json").read_bytes() != source.read_bytes()
                or not verify_live(site)
                or not all(verify_report_live(site, name) for name in (
                    f"{relative}.json", f"{relative}.html", "strategy.html", "mobile/strategy.html"))):
            raise NotificationError("Report Pages delivery is not verified.")
    draft = report["structured_report"]
    coverage = draft.get("coverage_receipt") or {}
    freshness = (draft.get("source_summary") or {}).get("freshness_receipt") or {}
    status = "전체 범위 확인" if coverage.get("complete") is True else "부분 분석·범위 미확인"
    lines = [f"TradingAgents {market.upper()} 투자 브리핑 배포 완료",
             f"보고서 작성: {draft['generated_at']}", f"게시: {report['published_at']}",
             f"자료 기준: {draft.get('as_of') or '미확인'}",
             f"범위: {status} · 보고서 수록 {len(draft.get('strategies') or [])}종목"]
    if freshness.get("analysis_completed_at"):
        lines.append(f"원분석 완료: {freshness['analysis_completed_at']}")
    missing = sorted({str(ticker) for key in (
        "missing_holding_tickers", "missing_watchlist_tickers", "missing_analysis_tickers", "failed_tickers")
        for ticker in (coverage.get(key) or [])})
    if missing:
        lines.append("누락·실패 종목: " + ", ".join(missing[:30]) + (" 외 (보고서 참조)" if len(missing) > 30 else ""))
    lines.extend(["기존 원분석을 정리한 조건부 투자 계획입니다. 게시가 시세 갱신이나 새 전체 분석 완료를 뜻하지 않습니다.",
                  "지연 자료·부분 분석도 표시된 기준시각과 범위로 제공합니다. 주문 전 현재 가격과 조건을 확인하세요."])
    buttons = [[{"text": "이번 브리핑 (PC·모바일)", "url": f"{PUBLIC_BASE}/{relative}.html"}],
               [{"text": "PC 전략", "url": f"{PUBLIC_BASE}/strategy.html?market={market}"},
                {"text": "모바일 전략", "url": f"{PUBLIC_BASE}/mobile/strategy.html?market={market}"}]]
    return "\n".join(lines), buttons, {"conclusion": "success", "surfaces": [market],
        "report_event_id": report["event_id"], "report_sha256": digest, "report_published_at": report["published_at"]}
