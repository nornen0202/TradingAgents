from __future__ import annotations

import argparse
import json
from pathlib import Path

from .handoff import dispatch_pages_handoff
from .runtime import WorkRuntime, WorkRuntimeError


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare, publish, and acknowledge TradingAgents ChatGPT Work events."
    )
    parser.add_argument("--runtime-dir", type=Path, default=Path(".runtime/chatgpt-work"))
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("--surface", required=True, choices=("kr", "us", "youtube", "prism"))
    prepare.add_argument("--archive-dir", type=Path)
    prepare.add_argument("--youtube-archive-dir", type=Path)
    prepare.add_argument("--prism-archive-dir", type=Path)

    publish = subparsers.add_parser("publish")
    publish.add_argument("--surface", required=True, choices=("kr", "us", "youtube", "prism"))
    publish.add_argument("--event-id", required=True)
    publish.add_argument("--source-sha256", required=True)
    publish.add_argument("--markdown-file", required=True, type=Path)
    publish.add_argument("--structured-file", required=True, type=Path)
    publish.add_argument("--archive-dir", type=Path)

    acknowledge = subparsers.add_parser("ack")
    acknowledge.add_argument("--surface", required=True, choices=("kr", "us", "youtube", "prism"))
    acknowledge.add_argument("--event-id", required=True)
    acknowledge.add_argument("--status", default="rendered")

    handoff = subparsers.add_parser("handoff")
    handoff.add_argument("--surface", required=True, choices=("kr", "us"))
    handoff.add_argument("--event-id", required=True)
    handoff.add_argument("--report-sha256", required=True)
    handoff.add_argument("--repository", default="nornen0202/TradingAgents")
    handoff.add_argument("--ref", default="main")
    handoff.add_argument("--workflow", default="work-report-pages-refresh.yml")
    handoff.add_argument("--force", action="store_true")

    recover = subparsers.add_parser("recover")
    recover.add_argument("--surface", required=True, choices=("kr", "us", "youtube", "prism"))
    recover.add_argument("--event-id", required=True)
    recover.add_argument("--source-sha256", required=True)
    recover.add_argument("--report-sha256")
    recover.add_argument("--state-revision", type=int)
    recover.add_argument("--archive-dir", type=Path)

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
        elif args.command == "publish":
            try:
                report_markdown = args.markdown_file.read_text(encoding="utf-8")
                structured_report = json.loads(args.structured_file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise WorkRuntimeError(f"Could not read final Work report files: {exc}") from exc
            result = runtime.publish(
                args.surface,
                args.event_id,
                args.source_sha256,
                report_markdown=report_markdown,
                structured_report=structured_report,
                archive_dir=args.archive_dir,
            )
        elif args.command == "ack":
            result = runtime.acknowledge(args.surface, args.event_id, status=args.status)
        elif args.command == "handoff":
            result = dispatch_pages_handoff(
                runtime,
                surface=args.surface,
                event_id=args.event_id,
                report_sha256=args.report_sha256,
                repository=args.repository,
                ref=args.ref,
                workflow=args.workflow,
                force=args.force,
            )
        elif args.command == "recover":
            result = runtime.recover(
                args.surface,
                args.event_id,
                args.source_sha256,
                report_sha256=args.report_sha256,
                state_revision=args.state_revision,
                archive_dir=args.archive_dir,
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
