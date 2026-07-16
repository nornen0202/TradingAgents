from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from .telegram import (
    AtomicNotificationLedger,
    DEFAULT_FAILURE_INCIDENT_COOLDOWN_MINUTES,
    GitHubActionsClient,
    NotificationError,
    TelegramBotClient,
    compose_notification,
    notification_event_key,
    notification_incident_key,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect workflows and send TradingAgents Telegram notifications.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect")
    _add_upstream_arguments(inspect_parser)
    inspect_parser.add_argument("--github-output", type=Path)

    notify_parser = subparsers.add_parser("notify")
    _add_upstream_arguments(notify_parser)
    notify_parser.add_argument("--archive-dir", type=Path, required=True)
    notify_parser.add_argument("--ledger-path", type=Path, required=True)
    notify_parser.add_argument(
        "--public-base-url",
        default="https://nornen0202.github.io/TradingAgents",
    )
    notify_parser.add_argument("--dry-run", action="store_true")
    notify_parser.add_argument("--cards-only", action="store_true")
    notify_parser.add_argument(
        "--failure-incident-cooldown-minutes",
        type=int,
        default=DEFAULT_FAILURE_INCIDENT_COOLDOWN_MINUTES,
    )
    return parser


def _add_upstream_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repository", default=os.getenv("GITHUB_REPOSITORY", ""))
    parser.add_argument("--upstream-run-id", type=int, required=True)


def _inspect(args: argparse.Namespace) -> dict[str, Any]:
    token = os.getenv("GH_TOKEN", "") or os.getenv("GITHUB_TOKEN", "")
    context = GitHubActionsClient(repository=args.repository, token=token).inspect_run(args.upstream_run_id)
    if args.github_output:
        outputs = {
            "workflow_name": context["workflow_name"],
            "conclusion": context["conclusion"],
            "should_notify": str(bool(context["should_notify"])).lower(),
            "reason": context["reason"],
        }
        with args.github_output.open("a", encoding="utf-8") as handle:
            for key, value in outputs.items():
                handle.write(f"{key}={value}\n")
    return context


def _notify(args: argparse.Namespace) -> dict[str, Any]:
    token = os.getenv("GH_TOKEN", "") or os.getenv("GITHUB_TOKEN", "")
    context = GitHubActionsClient(repository=args.repository, token=token).inspect_run(args.upstream_run_id)
    if not context["should_notify"]:
        return {"status": "SKIP", "reason": context["reason"], "upstream_run_id": args.upstream_run_id}

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_NOTIFICATION_CHAT_ID", "")
    chunks, buttons, composition = compose_notification(
        context,
        archive_dir=args.archive_dir,
        public_base_url=args.public_base_url,
        cards_only=args.cards_only,
    )
    if not chunks:
        return {
            "status": "SKIP",
            "reason": "no_private_action_cards",
            "upstream_run_id": args.upstream_run_id,
        }
    event_key = notification_event_key(
        repository=args.repository,
        upstream_run_id=args.upstream_run_id,
        conclusion=context["conclusion"],
        chat_id=chat_id,
    )
    if args.cards_only:
        event_key = f"{event_key}-cards"
    incident_key = ""
    if not args.cards_only:
        incident_key = notification_incident_key(
            repository=args.repository,
            failure_fingerprint=str(context.get("failure_fingerprint") or ""),
            chat_id=chat_id,
        )
    if args.dry_run:
        return {
            "status": "DRY_RUN",
            "event_key": event_key,
            "chunk_count": len(chunks),
            "chunk_lengths": [len(chunk) for chunk in chunks],
            "button_count": sum(len(row) for row in buttons),
            "incident_key": incident_key or None,
            **composition,
        }

    client = TelegramBotClient(bot_token=bot_token, chat_id=chat_id)
    if _requires_private_chat(buttons, cards_only=args.cards_only):
        client.ensure_private_chat()
    ledger = AtomicNotificationLedger(args.ledger_path)
    receipt_metadata = {
        "repository": args.repository,
        "upstream_run_id": args.upstream_run_id,
        "workflow_name": context["workflow_name"],
        "conclusion": context["conclusion"],
        **composition,
    }
    result = ledger.deliver(
        event_key=event_key,
        chunks=chunks,
        buttons=buttons,
        sender=lambda text, keyboard: client.send_message(text, buttons=keyboard),
        receipt_metadata=receipt_metadata,
        incident_key=incident_key or None,
        incident_cooldown_seconds=max(
            0,
            int(args.failure_incident_cooldown_minutes),
        )
        * 60,
    )
    return {**result, "chunk_count": len(chunks), **composition}


def _requires_private_chat(
    buttons: list[list[dict[str, str]]],
    *,
    cards_only: bool,
) -> bool:
    _ = buttons
    return cards_only


def main() -> int:
    args = _parser().parse_args()
    try:
        result = _inspect(args) if args.command == "inspect" else _notify(args)
    except NotificationError as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, ensure_ascii=False))
        return 2
    # Result objects intentionally contain no bot token, chat ID, message body,
    # or personal strategy URL.
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
