from __future__ import annotations

import argparse
from getpass import getpass
import os
from pathlib import Path
from typing import Any


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create an authenticated Telethon session for the PRISM Telegram collector."
    )
    parser.add_argument("--api-id", default=os.getenv("TELEGRAM_API_ID"), help="Telegram API ID.")
    parser.add_argument("--api-hash", default=os.getenv("TELEGRAM_API_HASH"), help="Telegram API hash.")
    parser.add_argument("--phone", default=os.getenv("TELEGRAM_PHONE"), help="Telegram account phone number.")
    parser.add_argument(
        "--session-path",
        default=os.getenv("TELEGRAM_SESSION_PATH"),
        help="Write a persistent Telethon .session file instead of printing a StringSession.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print the generated StringSession value. Ignored when --session-path is used.",
    )
    args = parser.parse_args(argv)

    api_id = _required_int(args.api_id, "TELEGRAM_API_ID")
    api_hash = _required_text(args.api_hash, "TELEGRAM_API_HASH")

    try:
        from telethon import TelegramClient  # type: ignore
        from telethon.sessions import StringSession  # type: ignore
    except Exception as exc:
        print(f"Telethon is required. Install with: python -m pip install -e .[telegram]\n{exc}")
        return 2

    if args.session_path:
        session_path = Path(args.session_path).expanduser()
        session_path.parent.mkdir(parents=True, exist_ok=True)
        session: Any = str(session_path)
    else:
        session = StringSession()

    client = TelegramClient(session, api_id, api_hash)
    try:
        if args.phone:
            client.start(phone=args.phone, password=_prompt_password)
        else:
            client.start(password=_prompt_password)
        if args.session_path:
            print(f"Authorized Telegram user session at {Path(args.session_path).expanduser()}.")
            return 0
        session_string = client.session.save()
    finally:
        client.disconnect()

    if args.quiet:
        print(session_string)
    else:
        print("TELEGRAM_SESSION_STRING:")
        print(session_string)
        print()
        print("Store this value as a GitHub Actions secret named TELEGRAM_SESSION_STRING.")
    return 0


def _required_text(value: str | None, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise SystemExit(f"{name} is required. Pass --{name.lower().replace('_', '-')} or set {name}.")
    return text


def _required_int(value: str | None, name: str) -> int:
    text = _required_text(value, name)
    try:
        return int(text)
    except ValueError as exc:
        raise SystemExit(f"{name} must be an integer.") from exc


def _prompt_password() -> str:
    return getpass("Telegram 2FA password: ")


if __name__ == "__main__":
    raise SystemExit(main())
