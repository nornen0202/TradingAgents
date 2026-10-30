from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

import pytest

from tests.test_investor_publication import source, AT
from tradingagents import local_automation
from tradingagents.notifications import local, work_reports
from tradingagents.notifications.telegram import NotificationError
from tradingagents.work.investor_draft import compose_investor_draft
from tradingagents.work.runtime import WorkRuntime
from tradingagents.work.site import _publish_latest_report


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def prepared(tmp_path, monkeypatch, *, partial=True, revised=False):
    archive, state = tmp_path / "archive", tmp_path / "state"
    source(archive, partial=partial)
    now = datetime.now(timezone.utc) - timedelta(minutes=2)
    runtime = WorkRuntime(tmp_path / "runtime")
    ready = runtime.prepare("us", archive_dir=archive, now=now, investor_report=True)
    packet = json.loads(Path(ready["packet_path"]).read_text(encoding="utf-8"))
    markdown, draft = compose_investor_draft(packet, now=now)
    if revised:
        markdown += "\n추가 통찰: 원분석의 가격 구간과 검토일을 함께 확인합니다.\n"
    published = runtime.publish("us", ready["event_id"], ready["source_sha256"], archive_dir=archive,
                                report_markdown=markdown, structured_report=draft, now=now)
    report = local.read(Path(published["report_path"]))
    _publish_latest_report(root=state / "site/work/v1", archive_dir=archive, surface="us", url_prefix="/work/v1")
    write(state / "publication.json", {"status": "DELIVERY_VERIFIED"})
    monkeypatch.setattr(local_automation, "verify_live", lambda _: True)
    monkeypatch.setattr(work_reports, "verify_report_live", lambda *_: True)
    return archive, state, report


@pytest.mark.parametrize("partial", [False, True])
@pytest.mark.parametrize("revised", [False, True])
def test_delayed_partial_and_revised_reports_send_once(tmp_path, monkeypatch, partial, revised):
    archive, state, report = prepared(tmp_path, monkeypatch, partial=partial, revised=revised)
    sent = []
    class Client:
        chat_id = "123"
        def __init__(self, **kwargs): pass
        def ensure_private_chat(self): pass
        def send_message(self, message, *, buttons):
            sent.append((message, buttons))
            return 456
    monkeypatch.setattr(local, "TelegramBotClient", Client)
    for _ in range(2):
        work_reports.queue_completed(archive, state)
    events = list((state / "notifications/events").glob("*.json"))
    assert len(events) == 1
    result = local.notify(events[0].stem, archive, state)
    assert result["status"] == "SENT" and result["message_ids"] == [456]
    assert result["report_sha256"] == report["report_sha256"]
    local.notify(events[0].stem, archive, state)
    assert len(sent) == 1
    text, buttons = sent[0]
    assert AT.date().isoformat() in text  # Original delayed source clock, never retimed.
    assert "시세 갱신이나 새 전체 분석 완료를 뜻하지 않습니다" in text
    assert report["report_sha256"] in buttons[0][0]["url"]
    assert "PC 전략" in str(buttons) and "모바일 전략" in str(buttons)
    if partial:
        assert "부분 분석" in text and "AMD" in text


@pytest.mark.parametrize("status", ["BUILDING", "PAGES_PENDING", "BUILD_FAILED"])
def test_unverified_publication_neither_queues_nor_sends(tmp_path, monkeypatch, status):
    archive, state, report = prepared(tmp_path, monkeypatch)
    work_reports.queue_completed(archive, state)
    path = next((state / "notifications/events").glob("*.json"))
    write(state / "publication.json", {"status": status})
    work_reports.queue_completed(archive, state)
    with pytest.raises(NotificationError, match="not verified"):
        local.notify(path.stem, archive, state, dry_run=True)
    local.reconcile(state, runner=lambda *a, **k: pytest.fail("must not dispatch"))
    assert len(list((state / "notifications/events").glob("*.json"))) == 1


def test_live_report_or_readable_page_mismatch_prevents_send(tmp_path, monkeypatch):
    archive, state, _ = prepared(tmp_path, monkeypatch)
    work_reports.queue_completed(archive, state)
    path = next((state / "notifications/events").glob("*.json"))
    checks = []
    def verify(site, relative):
        with pytest.raises(TimeoutError):
            with local.interprocess_file_lock(state / "publish.lock", timeout=0):
                pytest.fail("publisher must stay locked")
        checks.append(relative)
        return not relative.endswith(".html")
    monkeypatch.setattr(work_reports, "verify_report_live", verify)
    with pytest.raises(NotificationError, match="not verified"):
        local.notify(path.stem, archive, state, dry_run=True)
    assert len(checks) == 2


def test_queued_report_keeps_original_link_when_latest_changes(tmp_path, monkeypatch):
    archive, state, report = prepared(tmp_path, monkeypatch)
    work_reports.queue_completed(archive, state)
    path = next((state / "notifications/events").glob("*.json"))
    # A later report does not rewrite the immutable source or destination.
    write(state / "site/work/v1/us/report/latest.json", {"report_sha256": "b" * 64})
    result = local.notify(path.stem, archive, state, dry_run=True)
    assert result["report_sha256"] == report["report_sha256"]


def test_distinct_revision_of_same_analysis_gets_its_own_notice(tmp_path, monkeypatch):
    archive, state, original = prepared(tmp_path, monkeypatch)
    work_reports.queue_completed(archive, state)
    runtime = WorkRuntime(tmp_path / "runtime")
    runtime.publish("us", original["event_id"], original["source_sha256"], archive_dir=archive,
                    report_markdown=original["report_markdown"] + "\n추가 검토: 가격 구간 재확인.\n",
                    structured_report=original["structured_report"], now=datetime.now(timezone.utc))
    _publish_latest_report(root=state / "site/work/v1", archive_dir=archive, surface="us", url_prefix="/work/v1")
    work_reports.queue_completed(archive, state)
    work_reports.queue_completed(archive, state)
    events = [local.read(p) for p in (state / "notifications/events").glob("*.json")]
    assert len(events) == 2
    assert len({e["report_sha256"] for e in events}) == 2
    assert {e["event_id"] for e in events} == {original["event_id"]}


@pytest.mark.parametrize("damage", ["source", "public", "missing", "future", "bad_clock", "no_clock"])
def test_invalid_or_missing_canonical_report_is_not_queued(tmp_path, monkeypatch, damage):
    archive, state, report = prepared(tmp_path, monkeypatch)
    canonical = archive / "work-reports/us/events" / f"{report['report_sha256']}.json"
    public = state / "site/work/v1/us/report/latest.json"
    if damage == "source":
        report["report_markdown"] += "tampered"
        write(canonical, report)
    elif damage == "public":
        public.write_text("{}", encoding="utf-8")
    elif damage == "missing":
        canonical.unlink()
    else:
        # published_at is deliberately outside the content hash; validate clocks too.
        report["published_at"] = {"future": "2099-01-01T00:00:00Z", "bad_clock": "bad", "no_clock": None}[damage]
        write(canonical, report)
        write(public, report)
    with pytest.raises(NotificationError):
        work_reports.queue_completed(archive, state)
    assert not list((state / "notifications/events").glob("*.json"))


def test_missing_report_is_a_quiet_noop(tmp_path):
    state = tmp_path / "state"
    write(state / "publication.json", {"status": "DELIVERY_VERIFIED"})
    work_reports.queue_completed(tmp_path / "archive", state)
    assert not list((state / "notifications/events").glob("*.json"))


def test_report_discovery_failure_does_not_starve_other_notifications(tmp_path, monkeypatch):
    from tradingagents.notifications import advisory
    calls = []
    monkeypatch.setattr(work_reports, "queue_completed", lambda *a, **k: (_ for _ in ()).throw(ValueError()))
    monkeypatch.setattr(local, "queue_completed", lambda *a, **k: calls.append("market"))
    monkeypatch.setattr(advisory, "queue_completed", lambda *a, **k: calls.append("advisory"))
    monkeypatch.setattr(local, "reconcile", lambda *a, **k: calls.append("dispatch"))
    local.reconcile_safely(tmp_path / "archive", tmp_path / "state")
    assert calls == ["market", "advisory", "dispatch"]
