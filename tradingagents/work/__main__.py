from __future__ import annotations

import argparse
import json
from pathlib import Path

from .runtime import WorkRuntime, WorkRuntimeError


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare and acknowledge TradingAgents ChatGPT Work events.")
    parser.add_argument("--runtime-dir", type=Path, default=Path(".runtime/chatgpt-work"))
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("--surface", required=True, choices=("kr", "us", "youtube", "prism"))
    prepare.add_argument("--archive-dir", type=Path)
    prepare.add_argument("--youtube-archive-dir", type=Path)
    prepare.add_argument("--prism-archive-dir", type=Path)

    acknowledge = subparsers.add_parser("ack")
    acknowledge.add_argument("--surface", required=True, choices=("kr", "us", "youtube", "prism"))
    acknowledge.add_argument("--event-id", required=True)
    acknowledge.add_argument("--status", default="rendered")

    recover = subparsers.add_parser("recover")
    recover.add_argument("--surface", required=True, choices=("kr", "us", "youtube", "prism"))
    recover.add_argument("--event-id", required=True)
    recover.add_argument("--source-sha256", required=True)
    recover.add_argument("--state-revision", type=int)

    status = subparsers.add_parser("status")
    status.add_argument("--surface", choices=("kr", "us", "youtube", "prism"))

    args = parser.parse_args()
    runtime = WorkRuntime(args.runtime_dir)
    try:
        if args.command == "prepare":
            result = runtime.prepare(
                args.surface,
                archive_dir=args.archive_dir,
                youtube_archive_dir=args.youtube_archive_dir,
                prism_archive_dir=args.prism_archive_dir,
            )
        elif args.command == "ack":
            result = runtime.acknowledge(args.surface, args.event_id, status=args.status)
        elif args.command == "recover":
            result = runtime.recover(
                args.surface,
                args.event_id,
                args.source_sha256,
                state_revision=args.state_revision,
            )
        else:
            result = runtime.status(args.surface)
    except WorkRuntimeError as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
