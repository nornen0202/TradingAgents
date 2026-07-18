from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from .prism_models import PrismIngestionResult, PrismSourceKind
from .prism_telegram_common import (
    PrismTelegramCollection,
    PrismTelegramDocument,
    PrismTelegramMessage,
    PrismTelegramRuntimeConfig,
    extract_pdf_text_summary,
    filter_messages_by_lookback,
    looks_like_pdf_document,
    messages_to_ingestion,
    normalize_channel,
)


def load_telegram_bot_api(
    config: PrismTelegramRuntimeConfig | Any,
    *,
    default_market: str | None = None,
) -> PrismIngestionResult:
    collection = collect_bot_api_messages(config)
    return messages_to_ingestion(collection, default_market=default_market)


def collect_bot_api_messages(config: PrismTelegramRuntimeConfig | Any) -> PrismTelegramCollection:
    cfg = config if isinstance(config, PrismTelegramRuntimeConfig) else PrismTelegramRuntimeConfig()
    ingested_at = datetime.now().astimezone()
    if not cfg.enabled:
        return PrismTelegramCollection(
            enabled=False,
            ok=True,
            source_kind=PrismSourceKind.TELEGRAM_BOT_API,
            source=_source(cfg),
            ingested_at=ingested_at,
        )
    token = _first_text(cfg.bot_token, os.getenv("TELEGRAM_BOT_TOKEN"))
    if not token:
        return _failed_collection(cfg, ingested_at, "telegram_bot_token_missing")
    try:
        updates = _get_updates(token, cfg)
        messages = _messages_from_updates(updates, cfg, token=token)
        filtered = filter_messages_by_lookback(messages, now=ingested_at, lookback_minutes=cfg.lookback_minutes)
        _write_state(cfg, updates)
    except Exception as exc:
        return _failed_collection(cfg, ingested_at, f"telegram_bot_api_failed:{exc}")
    return PrismTelegramCollection(
        enabled=True,
        ok=True,
        source_kind=PrismSourceKind.TELEGRAM_BOT_API,
        source=_source(cfg),
        ingested_at=ingested_at,
        messages=tuple(filtered[: cfg.max_messages]),
        warnings=tuple() if filtered else ("telegram_bot_api_no_updates",),
    )


def _get_updates(token: str, cfg: PrismTelegramRuntimeConfig) -> list[dict[str, Any]]:
    offset = _state_offset(cfg)
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    payload: dict[str, Any] = {
        "timeout": 0,
        "limit": max(1, min(int(cfg.max_messages or 50), 100)),
        "allowed_updates": ["message", "channel_post"],
    }
    if offset is not None:
        payload["offset"] = offset
    response = requests.post(url, json=payload, timeout=cfg.timeout_seconds)
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(data.get("description") or "getUpdates returned ok=false")
    result = data.get("result") or []
    return [item for item in result if isinstance(item, dict)]


def _messages_from_updates(
    updates: list[dict[str, Any]],
    cfg: PrismTelegramRuntimeConfig,
    *,
    token: str,
) -> list[PrismTelegramMessage]:
    channel = normalize_channel(cfg.channel)
    messages: list[PrismTelegramMessage] = []
    for update in updates:
        raw_message = update.get("channel_post") or update.get("message")
        if not isinstance(raw_message, dict):
            continue
        chat = raw_message.get("chat") if isinstance(raw_message.get("chat"), dict) else {}
        username = normalize_channel(chat.get("username") or channel)
        if channel and username != channel:
            continue
        message_id = str(raw_message.get("message_id") or "")
        if not message_id:
            continue
        posted_at = _date_from_unix(raw_message.get("date"))
        text = str(raw_message.get("text") or raw_message.get("caption") or "")
        document = _document(raw_message, cfg, token=token, channel=channel)
        messages.append(
            PrismTelegramMessage(
                message_id=message_id,
                channel=channel,
                url=f"https://t.me/{channel}/{message_id}",
                posted_at=posted_at,
                text=text,
                documents=tuple([document] if document else []),
                raw={
                    "update_id": update.get("update_id"),
                    "message_id": raw_message.get("message_id"),
                    "chat_username": username,
                },
            )
        )
    messages.sort(key=lambda item: int(item.message_id) if item.message_id.isdigit() else 0, reverse=True)
    return messages


def _document(
    raw_message: dict[str, Any],
    cfg: PrismTelegramRuntimeConfig,
    *,
    token: str,
    channel: str,
) -> PrismTelegramDocument | None:
    raw = raw_message.get("document")
    if not isinstance(raw, dict):
        return None
    filename = _first_text(raw.get("file_name"))
    size = raw.get("file_size")
    document = PrismTelegramDocument(
        filename=filename,
        url=f"https://t.me/{channel}/{raw_message.get('message_id')}",
        size_bytes=int(size) if isinstance(size, int) else None,
        mime_type=_first_text(raw.get("mime_type")),
    )
    if not cfg.download_pdfs:
        return document
    if not looks_like_pdf_document(filename, document.mime_type):
        return document
    if document.size_bytes is not None and document.size_bytes > cfg.max_pdf_bytes:
        return PrismTelegramDocument(**{**document.to_dict(), "text_summary": {"status": "skipped", "warning": "telegram_pdf_too_large"}})
    file_id = _first_text(raw.get("file_id"))
    if not file_id:
        return document
    try:
        local_path = _download_file(token, file_id, cfg, filename=filename or f"{raw_message.get('message_id')}.pdf")
        summary = extract_pdf_text_summary(local_path)
        return PrismTelegramDocument(**{**document.to_dict(), "local_path": str(local_path), "text_summary": summary})
    except Exception as exc:
        return PrismTelegramDocument(**{**document.to_dict(), "text_summary": {"status": "failed", "warning": f"telegram_bot_pdf_download_failed:{exc}"}})


def _download_file(token: str, file_id: str, cfg: PrismTelegramRuntimeConfig, *, filename: str) -> Path:
    file_response = requests.post(
        f"https://api.telegram.org/bot{token}/getFile",
        json={"file_id": file_id},
        timeout=cfg.timeout_seconds,
    )
    file_response.raise_for_status()
    payload = file_response.json()
    if not payload.get("ok"):
        raise RuntimeError(payload.get("description") or "getFile returned ok=false")
    file_path = ((payload.get("result") or {}).get("file_path") or "").strip()
    if not file_path:
        raise RuntimeError("getFile returned no file_path")
    download_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
    response = requests.get(download_url, timeout=cfg.timeout_seconds, stream=True)
    response.raise_for_status()
    target_dir = _private_archive_dir(cfg)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / _safe_filename(filename)
    total = 0
    with target.open("wb") as handle:
        for chunk in response.iter_content(chunk_size=65536):
            total += len(chunk)
            if total > cfg.max_pdf_bytes:
                raise RuntimeError(f"telegram_bot_pdf_too_large:{total}>{cfg.max_pdf_bytes}")
            handle.write(chunk)
    return target


def _state_offset(cfg: PrismTelegramRuntimeConfig) -> int | None:
    path = _state_path(cfg)
    if path is None or not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    try:
        update_id = int(payload.get("last_update_id"))
    except (TypeError, ValueError):
        return None
    return update_id + 1


def _write_state(cfg: PrismTelegramRuntimeConfig, updates: list[dict[str, Any]]) -> None:
    path = _state_path(cfg)
    if path is None or not updates:
        return
    update_ids = [int(item["update_id"]) for item in updates if isinstance(item.get("update_id"), int)]
    if not update_ids:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"last_update_id": max(update_ids), "updated_at": datetime.now(timezone.utc).isoformat()}, ensure_ascii=False),
        encoding="utf-8",
    )


def _state_path(cfg: PrismTelegramRuntimeConfig) -> Path | None:
    raw = _first_text(cfg.state_path, os.getenv("PRISM_TELEGRAM_BOT_STATE_PATH"))
    return Path(raw).expanduser() if raw else None


def _private_archive_dir(cfg: PrismTelegramRuntimeConfig) -> Path:
    raw = _first_text(cfg.private_archive_dir, os.getenv("PRISM_TELEGRAM_PRIVATE_ARCHIVE_DIR"))
    return Path(raw or ".runtime/prism-telegram-private").expanduser()


def _failed_collection(
    cfg: PrismTelegramRuntimeConfig,
    ingested_at: datetime,
    warning: str,
) -> PrismTelegramCollection:
    return PrismTelegramCollection(
        enabled=True,
        ok=False,
        source_kind=PrismSourceKind.TELEGRAM_BOT_API,
        source=_source(cfg),
        ingested_at=ingested_at,
        warnings=(warning,),
    )


def _source(cfg: PrismTelegramRuntimeConfig) -> str:
    return f"telegram:bot_api:@{normalize_channel(cfg.channel)}"


def _date_from_unix(value: Any) -> datetime | None:
    try:
        return datetime.fromtimestamp(int(value), tz=timezone.utc)
    except (TypeError, ValueError, OSError):
        return None


def _first_text(*values: Any) -> str | None:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return None


def _safe_filename(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9가-힣_. -]+", "_", str(value or "")).strip(" .")
    return text[:160] or "telegram.pdf"
