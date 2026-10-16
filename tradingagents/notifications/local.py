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
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock
from .telegram import AtomicNotificationLedger, NotificationError, TelegramBotClient

REPOSITORY = "nornen0202/TradingAgents"
WORKFLOW = "tradingagents-mobile-notifications.yml"
SCHEMA = "tradingagents.local-notification/v1"


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
        event = read(path)
        if (event.get("kind"), event.get("stage"), event.get("source_key"), event.get("error_type")) == (
                "failure", stage, source_key, error_type):
            return path.stem
    return queue(state, {"kind": "failure", "stage": stage, "source_key": source_key,
                         "error_type": error_type, "finished_at": finished_at})


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


def queue_completed(archive, state, *, now=None):
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
    for path in (archive / "runs").glob("*/*/run.json"):
        manifest = read(path)
        settings = manifest.get("settings") or {}
        market = str(settings.get("market", "")).lower()
        if market not in {"kr", "us"} or not str(manifest.get("label", "")).startswith("local-scheduler-"):
            continue
        if manifest.get("status") != "success" or (manifest.get("summary") or {}).get("failed_tickers") != 0:
            continue
        started, finished = timestamp(manifest["started_at"]), timestamp(manifest["finished_at"])
        if finished < started or finished > now or now - finished > timedelta(hours=24):
            continue
        # Bootstrap the current daily result; never replay old overlay notices.
        if settings.get("run_mode", "full") != "full" and finished < timestamp(marker["started_at"]):
            continue
        if not published_strategy_covers(manifest, strategy):
            continue
        queue(state, {"kind": "success", "run_id": manifest["run_id"], "market": market,
                      "finished_at": manifest["finished_at"]})


def reconcile(state, *, now=None, runner=subprocess.run):
    now = now or datetime.now(timezone.utc)
    root = state / "notifications"
    with interprocess_file_lock(root / "dispatch.lock", timeout=0):
        for path in sorted((root / "events").glob("*.json")):
            key = path.stem
            result = read(root / "results" / f"{key}.json")
            receipt_path = root / "dispatches" / f"{key}.json"
            receipt = read(receipt_path)
            if result.get("status") in {"SENT", "NOOP"} and result.get("local_event_id") == key:
                status = "POLICY_SKIPPED" if result.get("reason") == "INCIDENT_COOLDOWN" else "DELIVERY_VERIFIED"
                if receipt.get("status") != status:
                    atomic_write_json(receipt_path, {**receipt, "status": status, "result": result})
                continue
            if int(receipt.get("attempts", 0)) >= 3:
                continue
            if receipt.get("dispatched_at") and now - timestamp(receipt["dispatched_at"]) < timedelta(minutes=15):
                continue
            # A workflow still owns this event even after its dispatch cooldown.
            history = runner(["gh", "run", "list", "--repo", REPOSITORY, "--workflow", WORKFLOW,
                              "--limit", "100", "--json", "databaseId,displayTitle,status,conclusion"],
                             capture_output=True, text=True, check=True, timeout=30)
            matches = [r for r in json.loads(history.stdout) if f"[local={key}]" in r["displayTitle"]]
            if any(r["status"] != "completed" for r in matches):
                continue
            # Successful workflow without a Telegram receipt must be diagnosed,
            # rather than automatically retransmitted as a new success.
            if any(r["conclusion"] == "success" for r in matches) and not result:
                atomic_write_json(receipt_path, {**receipt, "status": "MISSING_DELIVERY_RECEIPT"})
                continue
            attempt = max(int(receipt.get("attempts", 0)), len(matches)) + 1
            if attempt > 3:
                continue
            atomic_write_json(receipt_path, {"status": "DISPATCHING", "attempts": attempt,
                                            "dispatched_at": now.isoformat()})
            sent = runner(["gh", "workflow", "run", WORKFLOW, "--repo", REPOSITORY, "--ref", "main",
                           "-f", f"local_event_id={key}"], capture_output=True, text=True, check=False, timeout=30)
            atomic_write_json(receipt_path, {"status": "DISPATCH_ACCEPTED" if sent.returncode == 0 else "DISPATCH_FAILED",
                                            "attempts": attempt, "dispatched_at": now.isoformat()})


def reconcile_safely(archive, state, *, publication_locked=False):
    from .advisory import queue_completed as queue_advisory_completed
    # One unavailable advisory/API must not starve independent failures or
    # already queued market completions of their notification dispatch.
    for prepare in (queue_completed, queue_advisory_completed):
        try:
            if prepare is queue_advisory_completed:
                prepare(archive, state, publication_locked=publication_locked)
            else:
                prepare(archive, state)
        except Exception as exc:
            print(json.dumps({"notification_status": "PENDING", "error_type": type(exc).__name__}))
    try:
        reconcile(state)
    except Exception as exc:
        # Notification transport cannot terminate successful research/publication.
        print(json.dumps({"notification_status": "PENDING", "error_type": type(exc).__name__}))


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
                 f"확인 시각: {event['finished_at']}", f"오류 분류: {event['error_type']}",
                 "분석·배포 완료로 처리하지 않았습니다. 운영 점검에서 원인과 재시도 한도를 확인합니다."]
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
            or not str(manifest.get("label", "")).startswith("local-scheduler-")):
        raise NotificationError("Canonical local analysis did not complete successfully.")
    # Verify the actual site again in the credential-owning workflow, not merely
    # the scheduler's earlier push/dispatch receipt.
    from tradingagents.local_automation import verify_live
    # Share the publisher's lane lock so a rebuild cannot change the site
    # between source-lineage validation and the byte-for-byte live check.
    with interprocess_file_lock(state / "publish.lock", timeout=30):
        publication = read(state / "publication.json")
        strategy = read(state / "site" / "mobile" / "strategy.json")
        if (publication.get("status") != "DELIVERY_VERIFIED"
                or not published_strategy_covers(manifest, strategy)
                or not verify_live(state / "site")):
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
    atomic_write_json(state / "notifications" / "results" / f"{key}.json", result)
    return result
