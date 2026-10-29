"""Credential-free local outbox connected to the existing Telegram workflow.

Only the trusted main workflow receives bot credentials. Dispatch acceptance is
not delivery: the shared host records the Telegram message receipt separately.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from itertools import islice
from pathlib import Path
from zoneinfo import ZoneInfo

from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock
from .telegram import AtomicNotificationLedger, NotificationError, TelegramBotClient

REPOSITORY = "nornen0202/TradingAgents"
WORKFLOW = "tradingagents-mobile-notifications.yml"
SCHEMA = "tradingagents.local-notification/v1"
# A publisher can build/push and verify Pages propagation while holding its
# lane. Leave room for that normal work within notify_local's ten-minute limit.
PUBLICATION_LOCK_TIMEOUT_SECONDS = 300


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else {}


def timestamp(value):
    try:
        result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if result.tzinfo is None:
            raise ValueError
        return result
    except ValueError:
        raise NotificationError("Local notification timestamp is invalid.") from None


def event_id(event):
    return hashlib.sha256(json.dumps(event, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def queue(state, event):
    event = {"schema": SCHEMA, **event}
    key = event_id(event)
    path = state / "notifications" / "events" / f"{key}.json"
    if not path.exists():
        atomic_write_json(path, event)
    return key


def queue_failure(state, *, stage, source_key, error_type, finished_at):
    # Exception text, native stderr, paths and credentials never enter the outbox.
    for path in (state / "notifications" / "events").glob("*.json"):
        try:
            event = read(path)
            if not isinstance(event, dict):
                continue
        except (OSError, ValueError):
            continue
        if (event.get("kind"), event.get("stage"), event.get("source_key"), event.get("error_type")) == (
                "failure", stage, source_key, error_type):
            return path.stem
    return queue(state, {"kind": "failure", "stage": stage, "source_key": source_key,
                         "error_type": error_type, "finished_at": finished_at})


def _local_market_producer(manifest, archive=None, *, now=None):
    settings = manifest.get("settings") or {}
    market = str(settings.get("market", "")).lower()
    label = str(manifest.get("label", ""))
    if market not in {"kr", "us"}:
        return False
    if archive is not None and "manual" in label.lower():
        from tradingagents.scheduled.research_recovery import verified_completed_recovery
        return verified_completed_recovery(archive, manifest, now=now or datetime.now(timezone.utc))
    # Work's read-only freshness barrier is a real overlay producer. Its
    # completion still requires exact published lineage and live verification;
    # this does not turn a Work ACK into a notification event.
    return label.startswith("local-scheduler-") or (
        settings.get("run_mode") == "overlay_only"
        and label == f"pre-report-{market}-overlay"
    )


def published_strategy_covers(manifest, strategy):
    """Bind a completion to the strategy bytes that verify_live checks.

    A previous snapshot can still be DELIVERY_VERIFIED while the next producer
    finishes. Its status alone says nothing about that new run's publication.
    Full research remains covered when a later overlay explicitly resolves its
    analysis lineage to that same completed run.
    """
    market = str((manifest.get("settings") or {}).get("market", "")).lower()
    payload = (strategy.get("markets") or {}).get(market) or {}
    freshness = payload.get("freshness_receipt") or {}
    run_id, finished = manifest.get("run_id"), manifest.get("finished_at")
    if (payload.get("run_id") == run_id
            and freshness.get("producer_run_id") == run_id
            and freshness.get("producer_finished_at") == finished):
        return True
    completed = payload.get("latest_completed_analysis") or {}
    return ((manifest.get("settings") or {}).get("run_mode", "full") == "full"
            and freshness.get("analysis_lineage_status") == "RESOLVED"
            and freshness.get("analysis_run_id") == run_id
            and completed.get("run_id") == run_id
            and completed.get("status") == "success"
            and completed.get("finished_at") == finished)


def queue_completed(archive, state, *, now=None, publication_locked=False):
    if publication_locked:
        return _queue_completed_locked(archive, state, now=now)
    try:
        with interprocess_file_lock(state / "publish.lock", timeout=0):
            return _queue_completed_locked(archive, state, now=now)
    except TimeoutError:
        return


def _queue_completed_locked(archive, state, *, now=None):
    now = now or datetime.now(ZoneInfo("Asia/Seoul"))
    publication = read(state / "publication.json")
    if publication.get("status") != "DELIVERY_VERIFIED":
        return
    strategy = read(state / "site" / "mobile" / "strategy.json")
    marker_path = state / "notifications" / "enabled.json"
    marker = read(marker_path)
    if not marker:
        marker = {"started_at": now.isoformat()}
        atomic_write_json(marker_path, marker)
    marker_started = timestamp(marker["started_at"])
    scan_started = time.perf_counter()
    def completion(path):
        try:
            return _completion_event(read(path), archive, strategy, marker_started, now), 0
        except (OSError, ValueError, TypeError, KeyError, AttributeError, NotificationError):
            return None, 1
    invalid = scanned = 0
    paths = iter((archive / "runs").glob("*/*/run.json"))
    # A serial scan held the publication lock for over a minute on the live
    # removable-volume archive. Bound in-flight originals to four, keep every
    # validation and its fixed cutoff, and write the outbox in original order.
    with ThreadPoolExecutor(max_workers=4) as workers:
        while batch := list(islice(paths, 4)):
            for event, corrupt in workers.map(completion, batch):
                scanned += 1
                invalid += corrupt
                if event:
                    queue(state, event)
    atomic_write_json(state / "notifications/health/market_sources.json", {
        "notification_status": "DEGRADED" if invalid else "CHECKED",
        "invalid_manifests": invalid, "scanned_manifests": scanned,
        "scan_seconds": round(time.perf_counter() - scan_started, 3), "checked_at": now.isoformat()})


def _completion_event(manifest, archive, strategy, marker_started, now):
    if not isinstance(manifest, dict):
        raise ValueError("Invalid manifest")
    if manifest.get("status") != "success":
        return None
    summary, settings = manifest.get("summary") or {}, manifest.get("settings") or {}
    if (summary.get("failed_tickers") != 0 or summary.get("total_tickers", 0) <= 0
            or summary.get("total_tickers") != summary.get("successful_tickers")
            or ((manifest.get("active_universe") or {}).get("coverage") or {}).get("complete") is not True):
        return None
    started, finished = timestamp(manifest.get("started_at")), timestamp(manifest.get("finished_at"))
    if finished < started or finished > now or now - finished > timedelta(hours=24):
        return None
    if not _local_market_producer(manifest, archive, now=now):
        return None
    if settings.get("run_mode", "full") != "full" and finished < marker_started:
        return None
    if not published_strategy_covers(manifest, strategy):
        return None
    return {"kind": "success", "run_id": manifest["run_id"], "market": str(settings["market"]).lower(),
            "finished_at": manifest["finished_at"]}


def reconcile(state, *, now=None, runner=subprocess.run, completions_allowed=True):
    now = now or datetime.now(timezone.utc)
    root = state / "notifications"
    with interprocess_file_lock(root / "dispatch.lock", timeout=0):
        for path in sorted((root / "events").glob("*.json")):
            try:
                _reconcile_event(state, path, now=now, runner=runner, completions_allowed=completions_allowed)
            except (OSError, ValueError, TypeError, KeyError, NotificationError) as exc:
                atomic_write_json(root / "health" / f"event-{path.stem}.json", {
                    "notification_status": "PENDING", "error_type": type(exc).__name__,
                    "checked_at": now.isoformat()})


def _reconcile_event(state, path, *, now, runner, completions_allowed):
    root = state / "notifications"
    key = path.stem
    result = read(root / "results" / f"{key}.json")
    receipt_path = root / "dispatches" / f"{key}.json"
    receipt = read(receipt_path)
    if result.get("status") in {"SENT", "NOOP"} and result.get("local_event_id") == key:
        status = ("POLICY_SKIPPED" if result.get("reason") in {
            "INCIDENT_COOLDOWN", "SUPERSEDED_BY_VERIFIED_PUBLICATION"} else "DELIVERY_VERIFIED")
        if receipt.get("status") != status:
            atomic_write_json(receipt_path, {**receipt, "status": status, "result": result})
        return
    if read(path).get("kind") in {"success", "advisory_success"} and (not completions_allowed or read(
            state / "publication.json").get("status") != "DELIVERY_VERIFIED"):
        # Preserve attempts while the known prerequisite is pending.
        # Failure notifications remain independent of Pages health.
        return
    if int(receipt.get("attempts", 0)) >= 3:
        return
    if receipt.get("dispatched_at") and now - timestamp(receipt["dispatched_at"]) < timedelta(minutes=15):
        return
    # A workflow still owns this event even after its dispatch cooldown.
    history = runner(["gh", "run", "list", "--repo", REPOSITORY, "--workflow", WORKFLOW,
                      "--limit", "100", "--json", "databaseId,displayTitle,status,conclusion"],
                     capture_output=True, text=True, check=True, timeout=30)
    matches = [r for r in json.loads(history.stdout) if f"[local={key}]" in r["displayTitle"]]
    if any(r["status"] != "completed" for r in matches):
        return
    # Successful workflow without a Telegram receipt must be diagnosed,
    # rather than automatically retransmitted as a new success.
    if any(r["conclusion"] == "success" for r in matches) and not result:
        atomic_write_json(receipt_path, {**receipt, "status": "MISSING_DELIVERY_RECEIPT"})
        return
    attempt = max(int(receipt.get("attempts", 0)), len(matches)) + 1
    if attempt > 3:
        return
    atomic_write_json(receipt_path, {"status": "DISPATCHING", "attempts": attempt,
                                    "dispatched_at": now.isoformat()})
    sent = runner(["gh", "workflow", "run", WORKFLOW, "--repo", REPOSITORY, "--ref", "main",
                   "-f", f"local_event_id={key}"], capture_output=True, text=True, check=False, timeout=30)
    atomic_write_json(receipt_path, {"status": "DISPATCH_ACCEPTED" if sent.returncode == 0 else "DISPATCH_FAILED",
                                    "attempts": attempt, "dispatched_at": now.isoformat()})

def reconcile_safely(archive, state, *, publication_locked=False, discover_completions=True):
    from .advisory import queue_completed as queue_advisory_completed
    # One unavailable advisory/API must not starve independent failures or
    # already queued market completions of their notification dispatch.
    def health(stage, exc=None):
        payload = {"notification_stage": stage, "notification_status": "PENDING" if exc else "CHECKED",
                   "checked_at": datetime.now(timezone.utc).isoformat()}
        if exc:
            payload["error_type"] = type(exc).__name__
            print(json.dumps(payload))
        # A diagnostic write failure must not turn a delivery failure into a
        # research/publisher failure. CHECKED means reconciliation, not delivery.
        try:
            atomic_write_json(state / "notifications" / "health" / f"{stage}.json", payload)
        except OSError:
            pass

    discovery = (("market_queue", queue_completed), ("advisory_queue", queue_advisory_completed)) if discover_completions else ()
    for stage, prepare in discovery:
        try:
            prepare(archive, state, publication_locked=publication_locked)
            health(stage)
        except Exception as exc:
            health(stage, exc)
    try:
        if publication_locked:
            reconcile(state)
        else:
            try:
                with interprocess_file_lock(state / "publish.lock", timeout=0):
                    reconcile(state)
            except TimeoutError:
                # The old verified receipt may remain while its owner rebuilds.
                # Do not dispatch a completion into that known lock contention.
                reconcile(state, completions_allowed=False)
        health("dispatch")
    except Exception as exc:
        # Notification transport cannot terminate successful research/publication.
        health("dispatch", exc)


def compose(event, archive, state):
    if event.get("kind") == "advisory_success":
        from .advisory import compose as compose_advisory
        return compose_advisory(event, archive, state)
    if event.get("kind") == "failure":
        if event.get("stage") not in {"launcher", "preflight", "analysis", "publish"}:
            raise NotificationError("Unknown local failure stage.")
        if not re.fullmatch(r"[A-Za-z0-9_]+", str(event.get("error_type", ""))):
            raise NotificationError("Unsafe local diagnostic.")
        lines = ["TradingAgents 자동화 실패", f"단계: {event['stage']}",
                 f"확인 시각: {event['finished_at']}", f"오류 분류: {event['error_type']}"]
        if event["error_type"] == "LocalStorageHeadroomError":
            # Explain the known class without exposing exception text, native
            # output, local paths or credentials through the public outbox.
            lines.extend([
                "원인: 분석 저장 드라이브의 여유 공간이 부족하거나 드라이브에 접근할 수 없습니다.",
                "확인 항목: 분석 데이터·실행 상태·LLM 작업 공간의 실제 저장 드라이브 연결과 각각 4 GiB 이상의 여유 공간.",
            ])
        lines.append("분석·배포 완료로 처리하지 않았습니다. 운영 점검에서 원인과 재시도 한도를 확인합니다.")
        return "\n".join(lines), [], {"conclusion": "failure"}
    if event.get("kind") != "success" or event.get("market") not in {"kr", "us"}:
        raise NotificationError("Unknown local notification event.")
    run_id = event.get("run_id", "")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", run_id):
        raise NotificationError("Invalid local run identity.")
    paths = list((archive / "runs").glob(f"*/{run_id}/run.json"))
    if len(paths) != 1:
        raise NotificationError("Canonical local analysis is unavailable.")
    manifest = read(paths[0])
    summary = manifest.get("summary") or {}
    settings = manifest.get("settings") or {}
    if (manifest.get("status") != "success" or summary.get("failed_tickers") != 0
            or summary.get("total_tickers", 0) <= 0
            or summary.get("total_tickers") != summary.get("successful_tickers")
            or str(settings.get("market", "")).lower() != event["market"]
            or manifest.get("finished_at") != event["finished_at"]
            or not ((manifest.get("active_universe") or {}).get("coverage") or {}).get("complete")
            or not _local_market_producer(manifest, archive)):
        raise NotificationError("Canonical local analysis did not complete successfully.")
    # Verify the actual site again in the credential-owning workflow, not merely
    # the scheduler's earlier push/dispatch receipt.
    from tradingagents.local_automation import verify_live
    # Share the publisher's lane lock so a rebuild cannot change the site
    # between source-lineage validation and the byte-for-byte live check.
    with interprocess_file_lock(state / "publish.lock", timeout=PUBLICATION_LOCK_TIMEOUT_SECONDS):
        publication = read(state / "publication.json")
        strategy = read(state / "site" / "mobile" / "strategy.json")
        if publication.get("status") != "DELIVERY_VERIFIED" or not verify_live(state / "site"):
            raise NotificationError("Local Pages delivery is not verified for this analysis run.")
        if not published_strategy_covers(manifest, strategy):
            successor = verified_overlay_successor(manifest, strategy, archive, event["market"])
            if successor:
                return "", [], {"conclusion": "skipped", "reason": "SUPERSEDED_BY_VERIFIED_PUBLICATION",
                                "superseded_by_run_id": successor}
            raise NotificationError("Local Pages delivery is not verified for this analysis run.")
    market = event["market"]
    overlay = settings.get("run_mode", "full") == "overlay_only"
    title = "시세·계좌 갱신 완료" if overlay else "투자 분석 완료"
    detail = ("기존 연구를 재사용한 갱신이며 새로운 전체 분석 완료가 아닙니다.\n"
              if overlay else "")
    text = (f"TradingAgents {market.upper()} {title}\n"
            f"완료 시각: {event['finished_at']}\n"
            f"종목: {summary['successful_tickers']}/{summary['total_tickers']} {'갱신' if overlay else '분석'} 성공 · 실패 0\n"
            f"{detail}공개 전략 데이터 반영을 확인했습니다.\n"
            "분석 방향과 실제 주문 가능 여부는 별개입니다. 최신 시세·계좌·위험 조건을 재확인하세요.")
    base = "https://nornen0202.github.io/TradingAgents"
    buttons = [[{"text": f"{market.upper()} 모바일 전략", "url": f"{base}/mobile/strategy.html?market={market}"}]]
    return text, buttons, {"conclusion": "success", "run_ids": [run_id], "surfaces": [market]}


def verified_overlay_successor(manifest, strategy, archive, market):
    """Never replay an obsolete refresh; full research notices remain required."""
    if (manifest.get("settings") or {}).get("run_mode") != "overlay_only":
        return None
    current = (strategy.get("markets") or {}).get(market) or {}
    run_id = current.get("run_id", "")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", run_id):
        return None
    paths = list((archive / "runs").glob(f"*/{run_id}/run.json"))
    if len(paths) != 1:
        return None
    newer = read(paths[0])
    summary, settings = newer.get("summary") or {}, newer.get("settings") or {}
    if (newer.get("run_id") != run_id or newer.get("status") != "success"
            or str(settings.get("market", "")).lower() != market
            or settings.get("run_mode") != "overlay_only"
            or summary.get("total_tickers", 0) <= 0
            or summary.get("successful_tickers") != summary.get("total_tickers")
            or summary.get("failed_tickers") != 0
            or not ((newer.get("active_universe") or {}).get("coverage") or {}).get("complete")
            or not published_strategy_covers(newer, strategy)):
        return None
    finished = timestamp(newer.get("finished_at"))
    if not (timestamp(manifest["finished_at"]) < finished <= datetime.now(timezone.utc)
            and timestamp(newer.get("started_at")) <= finished):
        return None
    return run_id


def notify(key, archive, state, *, dry_run=False):
    if not re.fullmatch(r"[0-9a-f]{64}", key):
        raise NotificationError("Invalid local notification identity.")
    event = read(state / "notifications" / "events" / f"{key}.json")
    if event.get("schema") != SCHEMA or event_id(event) != key:
        raise NotificationError("Local notification outbox binding is invalid.")
    if timestamp(event.get("finished_at")) > datetime.now(timezone.utc) + timedelta(minutes=5):
        raise NotificationError("Local notification is future dated.")
    text, buttons, metadata = compose(event, archive, state)
    if dry_run:
        return {"status": "DRY_RUN", "local_event_id": key, "characters": len(text), **metadata}
    if metadata.get("reason") == "SUPERSEDED_BY_VERIFIED_PUBLICATION":
        previous = read(state / "notifications" / "results" / f"{key}.json")
        if previous.get("status") in {"SENT", "NOOP"} and previous.get("local_event_id") == key:
            return previous
        result = {"status": "NOOP", "local_event_id": key, "message_ids": [], **metadata,
                  "workflow_run_id": os.getenv("GITHUB_RUN_ID"),
                  "verified_at": datetime.now(timezone.utc).isoformat()}
        atomic_write_json(state / "notifications" / "results" / f"{key}.json", result)
        return result
    client = TelegramBotClient(bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
                               chat_id=os.getenv("TELEGRAM_NOTIFICATION_CHAT_ID", ""))
    client.ensure_private_chat()
    recipient = hashlib.sha256(client.chat_id.encode()).hexdigest()[:16]
    incident = None
    if event["kind"] == "failure":
        incident = hashlib.sha256(f"{event['stage']}:{event['source_key']}:{event['error_type']}:{recipient}".encode()).hexdigest()
    result = AtomicNotificationLedger(state / "notifications" / "telegram-ledger.json").deliver(
        event_key=f"local:{key}:{recipient}", chunks=[text], buttons=buttons,
        sender=lambda message, keyboard: client.send_message(message, buttons=keyboard),
        receipt_metadata={"repository": REPOSITORY, "workflow_name": "Local Automation", **metadata},
        incident_key=incident, incident_cooldown_seconds=6 * 3600,
    )
    result.update(local_event_id=key, workflow_run_id=os.getenv("GITHUB_RUN_ID"), verified_at=datetime.now(timezone.utc).isoformat())
    if event["kind"] == "advisory_success":
        result.update({field: metadata[field] for field in (
            "upstream_run_id", "upstream_run_attempt", "upstream_conclusion",
            "publication_recovered", "publication_verified_at", "source_sha256",
        ) if field in metadata})
    atomic_write_json(state / "notifications" / "results" / f"{key}.json", result)
    return result
