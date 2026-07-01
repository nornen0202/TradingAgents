from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from .prism_models import PrismExternalSignal, PrismIngestionResult, PrismSignalAction, PrismSourceKind
from .prism_normalize import (
    canonicalize_ticker,
    coerce_float,
    coerce_unit_interval,
    json_safe,
    normalize_market_with_warnings,
    payload_hash,
)


DEFAULT_TELEGRAM_CHANNEL = "stock_ai_agent"
DEFAULT_PUBLIC_PREVIEW_URL = "https://t.me/s/stock_ai_agent"
TELEGRAM_SOURCE_TAG = "telegram_stock_ai_agent"


@dataclass(frozen=True)
class PrismTelegramDocument:
    filename: str | None = None
    url: str | None = None
    size_text: str | None = None
    size_bytes: int | None = None
    mime_type: str | None = None
    local_path: str | None = None
    text_summary: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "url": self.url,
            "size_text": self.size_text,
            "size_bytes": self.size_bytes,
            "mime_type": self.mime_type,
            "local_path": self.local_path,
            "text_summary": self.text_summary,
        }


@dataclass(frozen=True)
class PrismTelegramMessage:
    message_id: str
    channel: str = DEFAULT_TELEGRAM_CHANNEL
    url: str | None = None
    posted_at: datetime | None = None
    text: str = ""
    documents: tuple[PrismTelegramDocument, ...] = tuple()
    photos: tuple[str, ...] = tuple()
    raw: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self, *, include_private_paths: bool = True) -> dict[str, Any]:
        documents = []
        for document in self.documents:
            payload = document.to_dict()
            if not include_private_paths:
                payload.pop("local_path", None)
            documents.append(payload)
        return {
            "message_id": self.message_id,
            "channel": self.channel,
            "url": self.url,
            "posted_at": self.posted_at.isoformat() if self.posted_at else None,
            "text": self.text,
            "documents": documents,
            "photos": list(self.photos),
            "raw": json_safe(dict(self.raw)),
        }


@dataclass(frozen=True)
class PrismTelegramCollection:
    enabled: bool
    ok: bool
    source_kind: PrismSourceKind
    source: str | None
    ingested_at: datetime = field(default_factory=lambda: datetime.now().astimezone())
    messages: tuple[PrismTelegramMessage, ...] = tuple()
    warnings: tuple[str, ...] = tuple()

    def to_dict(self, *, include_private_paths: bool = True) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "ok": self.ok,
            "source_kind": self.source_kind.value,
            "source": self.source,
            "ingested_at": self.ingested_at.isoformat(),
            "messages": [
                message.to_dict(include_private_paths=include_private_paths) for message in self.messages
            ],
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class PrismTelegramRuntimeConfig:
    enabled: bool = False
    mode: str = "public_preview"
    channel: str = DEFAULT_TELEGRAM_CHANNEL
    public_preview_url: str | None = None
    lookback_minutes: int = 180
    max_messages: int = 50
    timeout_seconds: float = 8.0
    max_payload_bytes: int = 5_000_000
    download_pdfs: bool = False
    private_archive_dir: str | Path | None = None
    state_path: str | Path | None = None
    session_path: str | Path | None = None
    session_string: str | None = None
    api_id: str | int | None = None
    api_hash: str | None = None
    bot_token: str | None = None
    max_pdf_bytes: int = 20_000_000
    fallback_to_public_preview: bool = True


@dataclass(frozen=True)
class _TickerMention:
    ticker: str
    display_name: str | None
    context: str


def runtime_config_from_any(value: Any, *, default_market: str | None = None) -> PrismTelegramRuntimeConfig:
    telegram = value
    if value is None:
        return PrismTelegramRuntimeConfig()
    prism = getattr(value, "prism", None) or getattr(value, "prism_dashboard", None)
    if prism is not None:
        telegram = getattr(prism, "telegram", None)
    if telegram is None:
        return PrismTelegramRuntimeConfig()
    return PrismTelegramRuntimeConfig(
        enabled=_bool_attr(telegram, "enabled", False),
        mode=str(getattr(telegram, "mode", "public_preview") or "public_preview").strip().lower(),
        channel=normalize_channel(getattr(telegram, "channel", DEFAULT_TELEGRAM_CHANNEL)),
        public_preview_url=_optional_text(getattr(telegram, "public_preview_url", None)),
        lookback_minutes=max(0, int(getattr(telegram, "lookback_minutes", 180) or 0)),
        max_messages=max(1, int(getattr(telegram, "max_messages", 50) or 50)),
        timeout_seconds=max(1.0, float(getattr(telegram, "timeout_seconds", 8.0) or 8.0)),
        max_payload_bytes=max(1024, int(getattr(telegram, "max_payload_bytes", 5_000_000) or 5_000_000)),
        download_pdfs=_bool_attr(telegram, "download_pdfs", False),
        private_archive_dir=getattr(telegram, "private_archive_dir", None),
        state_path=getattr(telegram, "state_path", None),
        session_path=getattr(telegram, "session_path", None),
        session_string=_optional_text(getattr(telegram, "session_string", None)),
        api_id=getattr(telegram, "api_id", None),
        api_hash=_optional_text(getattr(telegram, "api_hash", None)),
        bot_token=_optional_text(getattr(telegram, "bot_token", None)),
        max_pdf_bytes=max(1024, int(getattr(telegram, "max_pdf_bytes", 20_000_000) or 20_000_000)),
        fallback_to_public_preview=_bool_attr(telegram, "fallback_to_public_preview", True),
    )


def normalize_channel(value: Any) -> str:
    text = str(value or DEFAULT_TELEGRAM_CHANNEL).strip()
    text = text.removeprefix("https://t.me/s/").removeprefix("https://t.me/").removeprefix("@")
    text = text.split("/", 1)[0].split("?", 1)[0].strip()
    return text or DEFAULT_TELEGRAM_CHANNEL


def looks_like_pdf_document(filename: str | None, mime_type: str | None) -> bool:
    name = str(filename or "").strip().lower()
    mime = str(mime_type or "").strip().lower().split(";", 1)[0]
    return name.endswith(".pdf") or mime == "application/pdf"


def public_preview_url_for_channel(channel: str, configured_url: str | None = None) -> str:
    if configured_url and configured_url.strip():
        return configured_url.strip()
    return f"https://t.me/s/{normalize_channel(channel)}"


def messages_to_ingestion(
    collection: PrismTelegramCollection,
    *,
    default_market: str | None = None,
) -> PrismIngestionResult:
    signals: list[PrismExternalSignal] = []
    warnings: list[str] = list(collection.warnings)
    seen: set[tuple[str, str, str | None, str | None]] = set()
    for message in collection.messages:
        for signal in message_to_signals(
            message,
            default_market=default_market,
            source_kind=collection.source_kind,
            source=message.url or collection.source,
            ingested_at=collection.ingested_at,
        ):
            key = (
                signal.canonical_ticker.upper(),
                signal.signal_action.value,
                signal.trigger_type,
                signal.source_asof.isoformat() if signal.source_asof else None,
            )
            if key in seen:
                continue
            seen.add(key)
            signals.append(signal)
    if collection.ok and not signals and collection.messages:
        warnings.append("telegram_no_ticker_level_signals_found")
    return PrismIngestionResult(
        enabled=collection.enabled,
        ok=collection.ok,
        source_kind=collection.source_kind,
        source=collection.source,
        ingested_at=collection.ingested_at,
        signals=signals,
        warnings=list(dict.fromkeys(warnings)),
        raw_payload_hash=payload_hash(collection.to_dict(include_private_paths=False)),
    )


def message_to_signals(
    message: PrismTelegramMessage,
    *,
    default_market: str | None = None,
    source_kind: PrismSourceKind = PrismSourceKind.TELEGRAM_PUBLIC_PREVIEW,
    source: str | None = None,
    ingested_at: datetime | None = None,
) -> list[PrismExternalSignal]:
    action = _infer_action(message)
    trigger_type = _infer_trigger_type(message)
    confidence = _infer_confidence(message)
    current_price = _first_price(message.text)
    stop_loss = _first_named_price(message.text, ("Stop Loss", "손절가", "Stop"))
    target = _first_named_price(message.text, ("Target", "목표가"))
    risk_reward = _first_metric(message.text, r"R/R\s*:\s*([0-9]+(?:\.[0-9]+)?)")
    win_rate = _first_metric(message.text, r"Trigger Win Rate\s*:\s*([0-9]+(?:\.[0-9]+)?)%")
    mentions = _ticker_mentions(message)
    signals: list[PrismExternalSignal] = []
    seen: set[str] = set()
    for mention in mentions:
        ticker = canonicalize_ticker(mention.ticker, display_name=mention.display_name, market=default_market)
        if not ticker:
            continue
        canonical = ticker.upper()
        if canonical in seen:
            continue
        seen.add(canonical)
        row_warnings: list[str] = []
        market, market_warnings = normalize_market_with_warnings(
            None,
            ticker=canonical,
            default_market=default_market,
        )
        row_warnings.extend(market_warnings)
        signals.append(
            PrismExternalSignal(
                canonical_ticker=canonical,
                display_name=mention.display_name,
                market=market,  # type: ignore[arg-type]
                source_kind=source_kind,
                source_path_or_url=source or message.url,
                source_asof=message.posted_at,
                ingested_at=ingested_at or datetime.now().astimezone(),
                signal_action=action,
                trigger_type=trigger_type,
                trigger_score=confidence,
                composite_score=confidence,
                confidence=confidence,
                risk_reward_ratio=risk_reward,
                stop_loss_price=stop_loss,
                target_price=target,
                current_price=current_price,
                win_rate_30d_by_trigger=win_rate / 100.0 if win_rate is not None else None,
                rationale=_short_text(message.text, 900),
                tags=_signal_tags(message, trigger_type),
                raw={
                    "telegram_message": message.to_dict(include_private_paths=False),
                    "mention_context": mention.context,
                },
                warnings=row_warnings,
            )
        )
    return signals


def filter_messages_by_lookback(
    messages: Iterable[PrismTelegramMessage],
    *,
    now: datetime | None = None,
    lookback_minutes: int = 0,
) -> tuple[PrismTelegramMessage, ...]:
    if lookback_minutes <= 0:
        return tuple(messages)
    reference = now or datetime.now(timezone.utc).astimezone()
    start = reference - timedelta(minutes=lookback_minutes)
    result: list[PrismTelegramMessage] = []
    for message in messages:
        if message.posted_at is None:
            result.append(message)
            continue
        posted = _aware(message.posted_at, reference.tzinfo)
        if posted >= start:
            result.append(message)
    return tuple(result)


def extract_pdf_text_summary(path: str | Path, *, max_chars: int = 6000) -> dict[str, Any]:
    source = Path(path)
    if not source.exists():
        return {"status": "missing", "path": source.as_posix(), "text_chars": 0, "excerpt": ""}
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on optional extra
        return {
            "status": "unavailable",
            "path": source.as_posix(),
            "text_chars": 0,
            "excerpt": "",
            "warning": f"pypdf_unavailable:{exc}",
        }
    try:
        reader = PdfReader(str(source))
        chunks: list[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                chunks.append(text)
            if sum(len(chunk) for chunk in chunks) >= max_chars:
                break
        combined = _collapse_ws("\n".join(chunks))
    except Exception as exc:
        return {
            "status": "failed",
            "path": source.as_posix(),
            "text_chars": 0,
            "excerpt": "",
            "warning": f"pdf_extract_failed:{exc}",
        }
    return {
        "status": "ok" if combined else "empty",
        "path": source.as_posix(),
        "text_chars": len(combined),
        "excerpt": combined[:max_chars],
    }


def public_message_payload(message: PrismTelegramMessage) -> dict[str, Any]:
    payload = message.to_dict(include_private_paths=False)
    payload["text"] = _short_text(payload.get("text"), 1200)
    for document in payload.get("documents") or []:
        summary = document.get("text_summary") if isinstance(document, dict) else None
        if isinstance(summary, dict):
            summary.pop("path", None)
            summary["excerpt"] = _short_text(summary.get("excerpt"), 600)
    return payload


def _ticker_mentions(message: PrismTelegramMessage) -> tuple[_TickerMention, ...]:
    mentions: list[_TickerMention] = []
    for line in _message_lines(message.text):
        mention = _ticker_mention_from_line(line)
        if mention is not None:
            mentions.append(mention)
    for document in message.documents:
        mention = _ticker_mention_from_document(document)
        if mention is not None:
            mentions.append(mention)
        summary = document.text_summary or {}
        excerpt = summary.get("excerpt") if isinstance(summary, dict) else ""
        for line in _message_lines(str(excerpt or "")):
            mention = _ticker_mention_from_line(line)
            if mention is not None:
                mentions.append(mention)
    deduped: list[_TickerMention] = []
    seen: set[tuple[str, str | None]] = set()
    for mention in mentions:
        key = (mention.ticker.upper(), mention.display_name)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(mention)
    return tuple(deduped)


def _ticker_mention_from_line(line: str) -> _TickerMention | None:
    text = _collapse_ws(line)
    if not text:
        return None
    matches = list(re.finditer(r"\((?P<ticker>[A-Z][A-Z0-9.\-]{0,9}|\d{6})\)", text))
    if not matches:
        return None
    match = matches[-1]
    ticker = match.group("ticker").strip().upper()
    prefix = text[: match.start()].strip()
    prefix = re.sub(r"^[\-·•*\s🔸🚀🔨📊⚠️✅]+", "", prefix).strip()
    if ":" in prefix:
        left, right = prefix.split(":", 1)
        if any(marker in left.lower() for marker in ("portfolio adjustment", "매수 보류", "관심종목", "후보")):
            prefix = right.strip()
    display_name = prefix.rstrip("-:|").strip() or None
    if display_name and len(display_name) > 120:
        display_name = display_name[-120:].strip()
    return _TickerMention(ticker=ticker, display_name=display_name, context=text)


def _ticker_mention_from_document(document: PrismTelegramDocument) -> _TickerMention | None:
    filename = str(document.filename or "").strip()
    if not filename:
        return None
    match = re.match(r"^(?P<ticker>[A-Z][A-Z0-9.\-]{0,9}|\d{6})[_\-\s]+(?P<name>.+?)_(?:20\d{6}|19\d{6})", filename)
    if not match:
        match = re.match(r"^(?P<ticker>[A-Z][A-Z0-9.\-]{0,9}|\d{6})[_\-\s]+(?P<name>.+?)\.(?:pdf|PDF)$", filename)
    if not match:
        return None
    name = match.group("name").replace("_", " ").replace(",", ", ").strip()
    return _TickerMention(ticker=match.group("ticker").upper(), display_name=name or None, context=filename)


def _infer_action(message: PrismTelegramMessage) -> PrismSignalAction:
    text = message.text.lower()
    if "portfolio adjustment" in text or "stop loss" in text or "손절가" in text:
        return PrismSignalAction.STOP_LOSS
    if "매수 보류" in text or "결정: skip" in text or "decision: skip" in text:
        return PrismSignalAction.NO_ENTRY
    if "실시간 포트폴리오" in text or "current holdings" in text or "holdings list" in text:
        return PrismSignalAction.HOLD
    if "take profit" in text or "익절" in text or "이익실현" in text:
        return PrismSignalAction.TAKE_PROFIT
    if "시그널 얼럿" in text or "관심종목" in text or "o'neil" in text or "인사이트" in text:
        return PrismSignalAction.WATCH
    if "매수" in text and "보류" not in text:
        return PrismSignalAction.BUY
    if any(document.filename and document.filename.lower().endswith(".pdf") for document in message.documents):
        return PrismSignalAction.WATCH
    return PrismSignalAction.UNKNOWN


def _infer_trigger_type(message: PrismTelegramMessage) -> str:
    text = message.text.lower()
    if "portfolio adjustment" in text:
        return "telegram_portfolio_adjustment"
    if "매수 보류" in text or "decision: skip" in text:
        return "telegram_buy_skip"
    if "시그널 얼럿" in text:
        return "telegram_signal_alert"
    if "o'neil" in text:
        return "telegram_oneil_insight"
    if "실시간 포트폴리오" in text or "holdings list" in text:
        return "telegram_portfolio_snapshot"
    if any(document.filename and document.filename.lower().endswith(".pdf") for document in message.documents):
        return "telegram_pdf_report"
    return "telegram_message"


def _signal_tags(message: PrismTelegramMessage, trigger_type: str) -> tuple[str, ...]:
    tags = [TELEGRAM_SOURCE_TAG, trigger_type]
    if message.documents:
        tags.append("telegram_document")
    if any(document.filename and document.filename.lower().endswith(".pdf") for document in message.documents):
        tags.append("telegram_pdf")
    return tuple(dict.fromkeys(tags))


def _infer_confidence(message: PrismTelegramMessage) -> float | None:
    score = _first_metric(message.text, r"점수\s*:\s*([0-9]+(?:\.[0-9]+)?)")
    if score is None:
        score = _first_metric(message.text, r"(?:매수\s*)?Score\s*:\s*([0-9]+(?:\.[0-9]+)?)")
    if score is not None:
        return max(0.0, min(score if score <= 1.0 else score / 10.0, 1.0))
    return 0.45


def _first_price(text: str) -> float | None:
    return _first_named_price(text, ("현재가", "Current"))


def _first_named_price(text: str, labels: Iterable[str]) -> float | None:
    for label in labels:
        pattern = rf"{re.escape(label)}\s*[:：]?\s*\$?\s*([0-9][0-9,]*(?:\.[0-9]+)?)"
        number = _first_metric(text, pattern)
        if number is not None:
            return number
    return None


def _first_metric(text: str, pattern: str) -> float | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None
    return coerce_float(match.group(1))


def _message_lines(text: str) -> list[str]:
    raw = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    return [line.strip() for line in raw.split("\n") if line.strip()]


def _collapse_ws(value: Any) -> str:
    return re.sub(r"[ \t\f\v]+", " ", str(value or "")).strip()


def _short_text(value: Any, limit: int) -> str:
    text = _collapse_ws(value)
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


def _aware(value: datetime, tzinfo: Any) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    if tzinfo is not None:
        value = value.astimezone(tzinfo)
    return value


def _optional_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _bool_attr(value: Any, name: str, default: bool) -> bool:
    raw = getattr(value, name, default)
    if isinstance(raw, str):
        return raw.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(raw)
