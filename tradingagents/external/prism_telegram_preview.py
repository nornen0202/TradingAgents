from __future__ import annotations

import re
from datetime import datetime
from html import unescape
from typing import Any
from urllib.parse import urljoin

import requests
from parsel import Selector

from .prism_models import PrismIngestionResult, PrismSourceKind
from .prism_telegram_common import (
    PrismTelegramCollection,
    PrismTelegramDocument,
    PrismTelegramMessage,
    PrismTelegramRuntimeConfig,
    filter_messages_by_lookback,
    messages_to_ingestion,
    normalize_channel,
    public_preview_url_for_channel,
)


def load_telegram_public_preview(
    config: PrismTelegramRuntimeConfig | Any,
    *,
    default_market: str | None = None,
) -> PrismIngestionResult:
    collection = collect_public_preview_messages(config)
    return messages_to_ingestion(collection, default_market=default_market)


def collect_public_preview_messages(config: PrismTelegramRuntimeConfig | Any) -> PrismTelegramCollection:
    cfg = config if isinstance(config, PrismTelegramRuntimeConfig) else PrismTelegramRuntimeConfig()
    channel = normalize_channel(cfg.channel)
    url = public_preview_url_for_channel(channel, cfg.public_preview_url)
    ingested_at = datetime.now().astimezone()
    if not cfg.enabled:
        return PrismTelegramCollection(
            enabled=False,
            ok=True,
            source_kind=PrismSourceKind.TELEGRAM_PUBLIC_PREVIEW,
            source=url,
            ingested_at=ingested_at,
        )
    try:
        html_text = _fetch_preview_html(
            url,
            timeout_seconds=cfg.timeout_seconds,
            max_payload_bytes=cfg.max_payload_bytes,
        )
        messages = parse_public_preview_html(html_text, channel=channel, source_url=url)
        filtered = filter_messages_by_lookback(
            messages,
            now=ingested_at,
            lookback_minutes=cfg.lookback_minutes,
        )[: cfg.max_messages]
    except Exception as exc:
        return PrismTelegramCollection(
            enabled=True,
            ok=False,
            source_kind=PrismSourceKind.TELEGRAM_PUBLIC_PREVIEW,
            source=url,
            ingested_at=ingested_at,
            warnings=(f"telegram_public_preview_unavailable:{exc}",),
        )
    return PrismTelegramCollection(
        enabled=True,
        ok=True,
        source_kind=PrismSourceKind.TELEGRAM_PUBLIC_PREVIEW,
        source=url,
        ingested_at=ingested_at,
        messages=tuple(filtered),
        warnings=tuple() if filtered else ("telegram_public_preview_no_messages",),
    )


def parse_public_preview_html(
    html_text: str,
    *,
    channel: str = "stock_ai_agent",
    source_url: str = "https://t.me/s/stock_ai_agent",
) -> tuple[PrismTelegramMessage, ...]:
    selector = Selector(text=html_text or "")
    nodes = selector.css(".tgme_widget_message_wrap .js-widget_message, .tgme_widget_message.js-widget_message")
    messages: list[PrismTelegramMessage] = []
    for node in nodes:
        data_post = node.attrib.get("data-post", "")
        message_id = _message_id(data_post, channel=channel)
        if not message_id:
            continue
        posted_at = _parse_datetime(node.css("time::attr(datetime)").get())
        message_url = node.css(".tgme_widget_message_date::attr(href)").get()
        if not message_url:
            message_url = f"https://t.me/{normalize_channel(channel)}/{message_id}"
        text_html = node.css(".tgme_widget_message_text").get() or ""
        text = _html_to_text(text_html)
        documents = tuple(_documents(node, base_url=source_url))
        photos = tuple(_photos(node))
        messages.append(
            PrismTelegramMessage(
                message_id=message_id,
                channel=normalize_channel(channel),
                url=urljoin("https://t.me/", message_url),
                posted_at=posted_at,
                text=text,
                documents=documents,
                photos=photos,
                raw={"data_post": data_post},
            )
        )
    messages.sort(key=lambda item: int(item.message_id) if item.message_id.isdigit() else 0, reverse=True)
    return tuple(messages)


def _fetch_preview_html(url: str, *, timeout_seconds: float, max_payload_bytes: int) -> str:
    response = requests.get(url, timeout=timeout_seconds, stream=True)
    response.raise_for_status()
    content_type = str(response.headers.get("content-type") or "").lower()
    if content_type and "html" not in content_type and "text/" not in content_type:
        raise ValueError(f"unsupported_content_type:{content_type}")
    chunks: list[bytes] = []
    total = 0
    for chunk in response.iter_content(chunk_size=65536):
        total += len(chunk)
        if total > max_payload_bytes:
            raise ValueError(f"payload_too_large:{total}>{max_payload_bytes}")
        chunks.append(chunk)
    return b"".join(chunks).decode(response.encoding or "utf-8", errors="replace")


def _message_id(data_post: str, *, channel: str) -> str | None:
    text = str(data_post or "").strip()
    if "/" not in text:
        return None
    prefix, message_id = text.split("/", 1)
    if normalize_channel(prefix) != normalize_channel(channel):
        return None
    message_id = message_id.strip()
    return message_id or None


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _html_to_text(html_text: str) -> str:
    if not html_text:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", html_text, flags=re.IGNORECASE)
    text = re.sub(r"</p\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    lines = [re.sub(r"[ \t\f\v]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def _documents(node: Selector, *, base_url: str) -> list[PrismTelegramDocument]:
    documents: list[PrismTelegramDocument] = []
    for document in node.css(".tgme_widget_message_document_wrap"):
        filename = _clean_text(document.css(".tgme_widget_message_document_title::text").get())
        size_text = _clean_text(document.css(".tgme_widget_message_document_extra::text").get())
        url = document.attrib.get("href")
        documents.append(
            PrismTelegramDocument(
                filename=filename,
                url=urljoin(base_url, url) if url else None,
                size_text=size_text,
                mime_type="application/pdf" if filename and filename.lower().endswith(".pdf") else None,
            )
        )
    return documents


def _photos(node: Selector) -> list[str]:
    photos: list[str] = []
    for photo in node.css(".tgme_widget_message_photo_wrap"):
        style = photo.attrib.get("style", "")
        match = re.search(r"url\(['\"]?(?P<url>[^'\")]+)", style)
        if match:
            photos.append(match.group("url"))
    return photos


def _clean_text(value: str | None) -> str | None:
    text = " ".join(str(value or "").split())
    return text or None
