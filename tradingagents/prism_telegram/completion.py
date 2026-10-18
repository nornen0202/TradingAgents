"""Interpret collection completion without treating absent ticker signals as failure."""
from __future__ import annotations


def collection_complete(manifest: dict) -> bool:
    summary = manifest.get("summary")
    if not isinstance(summary, dict):
        return False
    messages = summary.get("messages")
    warnings = summary.get("warnings")
    if type(messages) is not int or messages < 0 or type(warnings) is not int:
        return False
    if warnings == 0:
        return not manifest.get("warnings")
    # The producer adds this informational warning only after successful
    # collection of messages that yielded no ticker-level signals. Unknown or
    # mixed warnings still require diagnosis, even when status says success.
    return (messages > 0 and warnings == 1
            and manifest.get("warnings") == ["telegram_no_ticker_level_signals_found"]
            and type(summary.get("signals")) is int and summary["signals"] == 0)
