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
    prepare.add_argument("--refresh-market", action="store_true",
                         help="Require new broker quotes and a VALID account before preparing KR/US.")
    prepare.add_argument("--report-policy", choices=("investor", "execution"),
                         help="Default: investor plans; --refresh-market alone retains strict execution preparation.")
    prepare.add_argument("--producer-state-dir", type=Path, default=Path(".runtime/local-automation"))
    prepare.add_argument("--report-context-v1", action="store_true",
                         help="Explicitly opt KR/US into sealed prior-ACK and public readiness context.")

    publish = subparsers.add_parser("publish")
    publish.add_argument("--surface", required=True, choices=("kr", "us", "youtube", "prism"))
    publish.add_argument("--event-id", required=True)
    publish.add_argument("--source-sha256", required=True)
    publish.add_argument("--markdown-file", required=True, type=Path)
    publish.add_argument("--structured-file", required=True, type=Path)
    publish.add_argument("--archive-dir", type=Path)
    publish.add_argument("--historical", action="store_true",
                         help="Archive a bound, non-executable past market draft without advancing latest or ACK state.")

    draft = subparsers.add_parser("draft-investor", help="Write a source-bound investor draft without model/API calls.")
    draft.add_argument("--packet-file", required=True, type=Path)
    draft.add_argument("--markdown-file", required=True, type=Path)
    draft.add_argument("--structured-file", required=True, type=Path)

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

    verify_public = subparsers.add_parser("verify-public")
    verify_public.add_argument("--surface", required=True, choices=("kr", "us"))

    args = parser.parse_args()
    if args.command == "verify-public":
        from .public_delivery import prepare_public_delivery
        try:
            result = prepare_public_delivery(args.surface)
        except (ValueError, OSError, KeyError, TypeError) as exc:
            print(json.dumps({"status": "UNVERIFIED", "error": str(exc), "personalized_input": None}))
            return 2
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "VERIFIED_CURRENT_INPUT" else 2
    runtime = WorkRuntime(args.runtime_dir)
    try:
        if args.command == "prepare":
            investor = args.surface in {"kr", "us"} and (
                args.report_policy == "investor" or (args.report_policy is None and not args.refresh_market))
            if investor and args.refresh_market:
                raise WorkRuntimeError("Use --report-policy investor without --refresh-market; execution refresh is a separate operation")
            if args.refresh_market:
                from .pre_report import prepare_market_report
                result = prepare_market_report(runtime, args.surface,
                    producer_state_dir=args.producer_state_dir, archive_dir=args.archive_dir,
                    youtube_archive_dir=args.youtube_archive_dir, prism_archive_dir=args.prism_archive_dir,
                    report_context_v1=args.report_context_v1)
            else:
                result = runtime.prepare(
                    args.surface,
                    archive_dir=args.archive_dir,
                    youtube_archive_dir=args.youtube_archive_dir,
                    prism_archive_dir=args.prism_archive_dir,
                    report_context_v1=args.report_context_v1,
                    investor_report=investor,
                )
        elif args.command == "draft-investor":
            from .investor_draft import write_investor_draft
            result = write_investor_draft(args.packet_file, args.markdown_file, args.structured_file)
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
                historical=args.historical,
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
    return 2 if result.get("status") in {"FRESH_INPUT_UNAVAILABLE", "CALENDAR_UNVERIFIED"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
