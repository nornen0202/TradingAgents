from __future__ import annotations

import asyncio
import os
import re
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

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


def load_telegram_user_session(
    config: PrismTelegramRuntimeConfig | Any,
    *,
    default_market: str | None = None,
) -> PrismIngestionResult:
    collection = collect_user_session_messages(config)
    return messages_to_ingestion(collection, default_market=default_market)


def collect_user_session_messages(config: PrismTelegramRuntimeConfig | Any) -> PrismTelegramCollection:
    cfg = config if isinstance(config, PrismTelegramRuntimeConfig) else PrismTelegramRuntimeConfig()
    ingested_at = datetime.now().astimezone()
    if not cfg.enabled:
        return PrismTelegramCollection(
            enabled=False,
            ok=True,
            source_kind=PrismSourceKind.TELEGRAM_USER_SESSION,
            source=_source(cfg),
            ingested_at=ingested_at,
        )
    try:
        return asyncio.run(_collect_user_session_messages_async(cfg, ingested_at=ingested_at))
    except RuntimeError as exc:
        if "asyncio.run() cannot be called" not in str(exc):
            return _failed_collection(cfg, ingested_at, f"telegram_user_session_failed:{exc}")
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(_collect_user_session_messages_async(cfg, ingested_at=ingested_at))
        except Exception as inner:
            return _failed_collection(cfg, ingested_at, f"telegram_user_session_failed:{inner}")
        finally:
            loop.close()
    except Exception as exc:
        return _failed_collection(cfg, ingested_at, f"telegram_user_session_failed:{exc}")


async def _collect_user_session_messages_async(
    cfg: PrismTelegramRuntimeConfig,
    *,
    ingested_at: datetime,
) -> PrismTelegramCollection:
    try:
        from telethon import TelegramClient  # type: ignore
        from telethon.sessions import StringSession  # type: ignore
    except Exception as exc:
        return _failed_collection(cfg, ingested_at, f"telethon_unavailable:{exc}")

    api_id = _first_text(cfg.api_id, os.getenv("TELEGRAM_API_ID"))
    api_hash = _first_text(cfg.api_hash, os.getenv("TELEGRAM_API_HASH"))
    if not api_id or not api_hash:
        return _failed_collection(cfg, ingested_at, "telegram_api_credentials_missing")
    try:
        api_id_int = int(api_id)
    except (TypeError, ValueError):
        return _failed_collection(cfg, ingested_at, "telegram_api_id_invalid")

    session_string = _first_text(cfg.session_string, os.getenv("TELEGRAM_SESSION_STRING"))
    session_path = _first_text(cfg.session_path, os.getenv("TELEGRAM_SESSION_PATH"))
    if session_string:
        session: Any = StringSession(session_string)
    else:
        session = str(Path(session_path or ".runtime/telegram-stock-ai-agent").expanduser())

    client = TelegramClient(session, api_id_int, api_hash)
    await client.connect()
    try:
        if not await client.is_user_authorized():
            return _failed_collection(cfg, ingested_at, "telegram_user_session_not_authorized")
        messages = await _iter_channel_messages(client, cfg, ingested_at=ingested_at)
    finally:
        await client.disconnect()

    filtered = filter_messages_by_lookback(messages, now=ingested_at, lookback_minutes=cfg.lookback_minutes)
    return PrismTelegramCollection(
        enabled=True,
        ok=True,
        source_kind=PrismSourceKind.TELEGRAM_USER_SESSION,
        source=_source(cfg),
        ingested_at=ingested_at,
        messages=tuple(filtered[: cfg.max_messages]),
        warnings=tuple() if filtered else ("telegram_user_session_no_messages",),
    )


async def _iter_channel_messages(client: Any, cfg: PrismTelegramRuntimeConfig, *, ingested_at: datetime) -> list[PrismTelegramMessage]:
    channel = normalize_channel(cfg.channel)
    entity = await client.get_entity(channel)
    messages: list[PrismTelegramMessage] = []
    cutoff = ingested_at - timedelta(minutes=cfg.lookback_minutes) if cfg.lookback_minutes > 0 else None
    async for message in client.iter_messages(entity, limit=cfg.max_messages):
        posted_at = message.date
        if posted_at is not None and posted_at.tzinfo is None:
            posted_at = posted_at.replace(tzinfo=timezone.utc)
        if cutoff is not None and posted_at is not None and posted_at.astimezone(ingested_at.tzinfo) < cutoff:
            continue
        documents = tuple(await _documents_for_message(client, message, cfg, channel=channel))
        messages.append(
            PrismTelegramMessage(
                message_id=str(message.id),
                channel=channel,
                url=f"https://t.me/{channel}/{message.id}",
                posted_at=posted_at,
                text=str(getattr(message, "raw_text", None) or getattr(message, "message", None) or ""),
                documents=documents,
                photos=tuple(),
                raw={
                    "id": message.id,
                    "grouped_id": str(getattr(message, "grouped_id", "") or ""),
                    "views": getattr(message, "views", None),
                },
            )
        )
    return messages


async def _documents_for_message(
    client: Any,
    message: Any,
    cfg: PrismTelegramRuntimeConfig,
    *,
    channel: str,
) -> list[PrismTelegramDocument]:
    file_info = getattr(message, "file", None)
    if file_info is None:
        return []
    filename = _first_text(getattr(file_info, "name", None), getattr(file_info, "title", None))
    mime_type = _first_text(getattr(file_info, "mime_type", None))
    size_bytes = getattr(file_info, "size", None)
    document = PrismTelegramDocument(
        filename=filename,
        url=f"https://t.me/{channel}/{message.id}",
        size_bytes=int(size_bytes) if isinstance(size_bytes, int) else None,
        mime_type=mime_type,
    )
    if not cfg.download_pdfs:
        return [document]
    if not looks_like_pdf_document(filename, mime_type):
        return [document]
    if document.size_bytes is not None and document.size_bytes > cfg.max_pdf_bytes:
        return [replace(document, text_summary={"status": "skipped", "warning": "telegram_pdf_too_large"})]
    target_dir = _private_archive_dir(cfg) / channel / str(message.id)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / _safe_filename(filename or f"{message.id}.pdf")
    try:
        downloaded = await client.download_media(message, file=str(target_path))
    except Exception as exc:
        return [replace(document, text_summary={"status": "failed", "warning": f"telegram_pdf_download_failed:{exc}"})]
    local_path = str(downloaded or target_path)
    summary = extract_pdf_text_summary(local_path)
    return [replace(document, local_path=local_path, text_summary=summary)]


def _private_archive_dir(cfg: PrismTelegramRuntimeConfig) -> Path:
    configured = _first_text(cfg.private_archive_dir, os.getenv("PRISM_TELEGRAM_PRIVATE_ARCHIVE_DIR"))
    return Path(configured or ".runtime/prism-telegram-private").expanduser()


def _failed_collection(
    cfg: PrismTelegramRuntimeConfig,
    ingested_at: datetime,
    warning: str,
) -> PrismTelegramCollection:
    return PrismTelegramCollection(
        enabled=True,
        ok=False,
        source_kind=PrismSourceKind.TELEGRAM_USER_SESSION,
        source=_source(cfg),
        ingested_at=ingested_at,
        warnings=(warning,),
    )


def _source(cfg: PrismTelegramRuntimeConfig) -> str:
    return f"telegram:user_session:@{normalize_channel(cfg.channel)}"


def _first_text(*values: Any) -> str | None:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return None


def _safe_filename(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9가-힣_. -]+", "_", str(value or "")).strip(" .")
    return text[:160] or "telegram.pdf"
