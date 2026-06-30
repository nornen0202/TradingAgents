from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from time import perf_counter
from typing import Any, Callable
from zoneinfo import ZoneInfo

from tradingagents.external.prism_telegram import load_telegram_prism_signals
from tradingagents.external.prism_telegram_bot import collect_bot_api_messages
from tradingagents.external.prism_telegram_common import (
    PrismTelegramCollection,
    PrismTelegramMessage,
    messages_to_ingestion,
    public_message_payload,
)
from tradingagents.external.prism_telegram_preview import collect_public_preview_messages
from tradingagents.external.prism_telegram_user import collect_user_session_messages
from tradingagents.prism_telegram.config import (
    PrismTelegramDailyConfig,
    load_prism_telegram_config,
    with_prism_telegram_overrides,
)
from tradingagents.prism_telegram.site import build_prism_telegram_site


CollectionFetcher = Callable[[PrismTelegramDailyConfig], PrismTelegramCollection]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect PRISM Telegram messages and publish static report pages.")
    parser.add_argument("--config", default="config/prism_telegram_daily.toml", help="Path to PRISM Telegram TOML config.")
    parser.add_argument("--archive-dir", help="Override archive directory.")
    parser.add_argument("--site-dir", help="Override generated site output directory.")
    parser.add_argument("--site-only", action="store_true", help="Only rebuild /prism-telegram from archived runs.")
    parser.add_argument("--mode", choices=("public_preview", "user_session", "mtproto", "telethon"), help="Collection mode.")
    parser.add_argument("--channel", help="Telegram channel username, with or without @.")
    parser.add_argument("--lookback-minutes", type=int, help="Lookback window in minutes.")
    parser.add_argument("--max-messages", type=int, help="Maximum messages to process.")
    parser.add_argument("--download-pdfs", action="store_true", help="Download PDF media in user-session mode.")
    parser.add_argument("--publish", dest="publish", action="store_true", default=True, help="Build public site after run.")
    parser.add_argument("--no-publish", dest="publish", action="store_false", help="Skip public site build after run.")
    args = parser.parse_args(argv)

    config = with_prism_telegram_overrides(
        load_prism_telegram_config(args.config),
        archive_dir=args.archive_dir,
        site_dir=args.site_dir,
        mode=args.mode,
        channel=args.channel,
        lookback_minutes=args.lookback_minutes,
        max_messages=args.max_messages,
        download_pdfs=True if args.download_pdfs else None,
    )

    if args.site_only:
        manifests = build_prism_telegram_site(config.storage.archive_dir, config.storage.site_dir, config.site)
        print(f"Rebuilt PRISM Telegram site at {config.storage.site_dir / 'prism-telegram'} from {len(manifests)} archived run(s).")
        return 0

    manifest = execute_prism_telegram_run(config, publish=args.publish)
    summary = manifest.get("summary") or {}
    print(
        f"Completed PRISM Telegram run {manifest['run_id']} with status {manifest['status']} "
        f"({summary.get('messages', 0)} messages / {summary.get('signals', 0)} signals)."
    )
    return 0


def execute_prism_telegram_run(
    config: PrismTelegramDailyConfig,
    *,
    publish: bool = True,
    collection_fetcher: CollectionFetcher | None = None,
) -> dict[str, Any]:
    tz = ZoneInfo("Asia/Seoul")
    started_at = datetime.now(tz)
    timer_start = perf_counter()
    run_id = f"prism_telegram_{started_at.strftime('%Y%m%d_%H%M%S')}"
    run_dir = config.storage.archive_dir / "runs" / started_at.strftime("%Y") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    collection = collection_fetcher(config) if collection_fetcher else _collect(config)
    ingestion = messages_to_ingestion(collection, default_market=None)
    message_items = _write_message_artifacts(run_dir, collection, ingestion.signals)
    manifest = {
        "version": 1,
        "run_id": run_id,
        "status": "success" if collection.ok else "partial_failure",
        "source": {
            "mode": config.source.mode,
            "channel": config.source.channel,
            "download_pdfs": config.source.download_pdfs,
            "source_kind": collection.source_kind.value,
            "source": collection.source,
        },
        "started_at": started_at.isoformat(),
        "finished_at": datetime.now(tz).isoformat(),
        "duration_seconds": round(perf_counter() - timer_start, 3),
        "summary": {
            "messages": len(collection.messages),
            "signals": len(ingestion.signals),
            "warnings": len(collection.warnings) + len(ingestion.warnings),
        },
        "warnings": list(dict.fromkeys([*collection.warnings, *ingestion.warnings])),
        "messages": message_items,
        "artifacts": {
            "collection_json": "collection.json",
            "signals_json": "signals.json",
        },
        "source_policy": {
            "raw_pdf_published": False,
            "raw_private_paths_published": False,
            "public_artifacts": ["message_pages", "feed.json"],
        },
    }
    _write_json(run_dir / "collection.json", collection.to_dict(include_private_paths=False))
    _write_json(run_dir / "signals.json", ingestion.signals_dict())
    _write_json(run_dir / "prism_telegram_run.json", manifest)
    _write_json(config.storage.archive_dir / "latest-prism-telegram-run.json", manifest)
    _write_state(config, manifest, collection)
    if publish:
        build_prism_telegram_site(config.storage.archive_dir, config.storage.site_dir, config.site)
    return manifest


def _collect(config: PrismTelegramDailyConfig) -> PrismTelegramCollection:
    runtime = config.source.runtime_config()
    mode = runtime.mode
    if mode in {"user_session", "mtproto", "telethon"}:
        collection = collect_user_session_messages(runtime)
        if collection.ok or not runtime.fallback_to_public_preview:
            return collection
        preview = collect_public_preview_messages(runtime)
        return PrismTelegramCollection(
            enabled=True,
            ok=preview.ok,
            source_kind=preview.source_kind,
            source=preview.source,
            ingested_at=preview.ingested_at,
            messages=preview.messages,
            warnings=tuple(dict.fromkeys([*collection.warnings, *preview.warnings])),
        )
    if mode in {"bot_api", "bot"}:
        collection = collect_bot_api_messages(runtime)
        if collection.ok or not runtime.fallback_to_public_preview:
            return collection
        preview = collect_public_preview_messages(runtime)
        return PrismTelegramCollection(
            enabled=True,
            ok=preview.ok,
            source_kind=preview.source_kind,
            source=preview.source,
            ingested_at=preview.ingested_at,
            messages=preview.messages,
            warnings=tuple(dict.fromkeys([*collection.warnings, *preview.warnings])),
        )
    return collect_public_preview_messages(runtime)


def _write_message_artifacts(
    run_dir: Path,
    collection: PrismTelegramCollection,
    signals: list[Any],
) -> list[dict[str, Any]]:
    signals_by_message_id: dict[str, list[dict[str, Any]]] = {}
    for signal in signals:
        raw = signal.raw if isinstance(signal.raw, dict) else {}
        message = raw.get("telegram_message") if isinstance(raw.get("telegram_message"), dict) else {}
        message_id = str(message.get("message_id") or "")
        if message_id:
            signals_by_message_id.setdefault(message_id, []).append(signal.to_dict())

    items: list[dict[str, Any]] = []
    for message in collection.messages:
        message_dir = run_dir / "messages" / _safe_segment(message.message_id)
        message_dir.mkdir(parents=True, exist_ok=True)
        message_payload = public_message_payload(message)
        signal_payload = signals_by_message_id.get(message.message_id, [])
        _write_json(message_dir / "metadata.json", message_payload)
        _write_json(message_dir / "signals.json", {"signals": signal_payload})
        item = {
            "message_id": message.message_id,
            "posted_at": message.posted_at.isoformat() if message.posted_at else None,
            "url": message.url,
            "text_preview": _short_text(message.text, 220),
            "documents": [
                {key: value for key, value in document.to_dict().items() if key != "local_path"}
                for document in message.documents
            ],
            "signals_count": len(signal_payload),
            "metadata_path": _relative(message_dir / "metadata.json", run_dir),
            "signals_path": _relative(message_dir / "signals.json", run_dir),
        }
        items.append(item)
    return items


def _write_state(config: PrismTelegramDailyConfig, manifest: dict[str, Any], collection: PrismTelegramCollection) -> None:
    state_path = config.source.state_path
    if state_path is None:
        return
    max_message_id = None
    numeric_ids = [int(message.message_id) for message in collection.messages if str(message.message_id).isdigit()]
    if numeric_ids:
        max_message_id = max(numeric_ids)
    _write_json(
        Path(state_path),
        {
            "run_id": manifest.get("run_id"),
            "finished_at": manifest.get("finished_at"),
            "last_message_id": max_message_id,
            "messages": len(collection.messages),
        },
    )


def _relative(path: Path, run_dir: Path) -> str:
    return path.resolve().relative_to(run_dir.resolve()).as_posix()


def _safe_segment(value: str) -> str:
    text = "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in str(value or "").strip())
    return text.strip(".-")[:100] or "message"


def _short_text(value: Any, limit: int) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_json_safe(payload), ensure_ascii=False, indent=2), encoding="utf-8")


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, datetime):
        return value.isoformat()
    return value


if __name__ == "__main__":
    raise SystemExit(main())
