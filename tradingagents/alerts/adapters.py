from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

import requests


class AlertEventType(str, Enum):
    NEW_CONSENSUS_BUY = "NEW_CONSENSUS_BUY"
    NEW_HARD_CONFLICT = "NEW_HARD_CONFLICT"
    STOP_LOSS_TRIGGERED = "STOP_LOSS_TRIGGERED"
    REDUCE_RISK_TRIGGERED = "REDUCE_RISK_TRIGGERED"
    PILOT_READY = "PILOT_READY"
    CLOSE_CONFIRM_READY = "CLOSE_CONFIRM_READY"
    MISSED_OPPORTUNITY_DETECTED = "MISSED_OPPORTUNITY_DETECTED"


class AlertAdapter(Protocol):
    def send_portfolio_summary(self, report: Any) -> None: ...
    def send_action_alert(self, action: Any) -> None: ...


class ConsoleAlertAdapter:
    def send_portfolio_summary(self, report: Any) -> None:
        print(_format_summary(report))

    def send_action_alert(self, action: Any) -> None:
        print(_format_action(action))


class MarkdownFileAlertAdapter:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def send_portfolio_summary(self, report: Any) -> None:
        self._append(_format_summary(report))

    def send_action_alert(self, action: Any) -> None:
        self._append(_format_action(action))

    def _append(self, content: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        previous = self.path.read_text(encoding="utf-8") if self.path.exists() else ""
        self.path.write_text(previous + ("\n\n" if previous else "") + content, encoding="utf-8")


class TelegramAlertAdapter:
    def __init__(self, *, bot_token: str | None = None, chat_id: str | None = None, timeout_seconds: float = 5.0):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.timeout_seconds = timeout_seconds

    def send_portfolio_summary(self, report: Any) -> None:
        self._send(_format_summary(report))

    def send_action_alert(self, action: Any) -> None:
        self._send(_format_action(action))

    def _send(self, text: str) -> None:
        if not self.bot_token or not self.chat_id:
            return
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        requests.post(url, json={"chat_id": self.chat_id, "text": text}, timeout=self.timeout_seconds)


def _format_summary(report: Any) -> str:
    run_id = _get(report, "run_id") or _get(report, "snapshot_id") or "portfolio"
    actions = _get(report, "actions") or []
    return f"TradingAgents summary {run_id}: {len(actions)} action(s). Alerts are advisory only and never place orders."


def _format_action(action: Any) -> str:
    ticker = _get(action, "canonical_ticker") or _get(action, "ticker") or "-"
    action_now = _get(action, "action_now") or _get(action, "action") or "-"
    risk_action = _get(action, "risk_action") or "-"
    return f"{ticker}: {action_now} / risk {risk_action}. Confirm in TradingAgents before execution."


def _get(value: Any, key: str) -> Any:
    if isinstance(value, dict):
        return value.get(key)
    return getattr(value, key, None)
