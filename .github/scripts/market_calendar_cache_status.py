"""Only publish a daily Actions cache after today's KR result is confirmed."""
from __future__ import annotations

from datetime import datetime
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tradingagents.scheduled.automation_calendar import (
    SEOUL, _cache_was_fetched_on, _load_cache, _resolve_cache_path, _status_from_cache,
)


def cache_ready(now: datetime) -> bool:
    day = now.astimezone(SEOUL).date()
    payload = _load_cache(_resolve_cache_path(None))
    return _cache_was_fetched_on(payload, day) and _status_from_cache(payload, day) is not None


def main() -> int:
    ready = cache_ready(datetime.now(SEOUL))
    output = os.getenv("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as stream:
            stream.write(f"fresh={str(ready).lower()}\n")
    print(f"Official calendar cache ready: {ready}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
