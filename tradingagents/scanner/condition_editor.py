"""Offline condition editor and scanner: ``python -m ...condition_editor --help``."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .conditions import EXAMPLE_CONDITION, FIELDS, validate_condition
from .prism_like_scanner import run_prism_like_scanner


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Edit validated scanner conditions and scan a local dated snapshot")
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create", help="Create a compound condition; values use JSON syntax")
    create.add_argument("--output", required=True, type=Path)
    create.add_argument("--match", choices=("all", "any"), default="all")
    create.add_argument("--rule", nargs=3, action="append", metavar=("FIELD", "OP", "JSON_VALUE"))
    create.add_argument("--example", action="store_true")
    check = sub.add_parser("validate")
    check.add_argument("condition", type=Path)
    sub.add_parser("fields", help="Show the allowlisted fields")
    scan = sub.add_parser("scan", help="Run existing PRISM scanner without external API calls")
    scan.add_argument("--condition", required=True, type=Path)
    scan.add_argument("--ohlcv", required=True, type=Path)
    scan.add_argument("--as-of", required=True)
    scan.add_argument("--market", choices=("KR", "US"), default="KR")
    scan.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "fields":
            print("\n".join(sorted(FIELDS)))
            return 0
        if args.command == "create":
            if args.example and args.rule:
                raise ValueError("Choose --example or --rule")
            tree = EXAMPLE_CONDITION if args.example else {
                args.match: [{"field": field, "op": op, "value": json.loads(value)} for field, op, value in (args.rule or [])]
            }
            condition = validate_condition(tree)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(condition, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(str(args.output))
            return 0
        condition = validate_condition(json.loads(args.condition.read_text(encoding="utf-8")))
        if args.command == "validate":
            print(json.dumps(condition, ensure_ascii=False, indent=2))
        else:
            result = run_prism_like_scanner(ohlcv_path=args.ohlcv, asof=args.as_of, market=args.market,
                                           condition=condition, output_path=args.output)
            print(json.dumps({"output": str(args.output), "candidates": len(result.candidates),
                              "warnings": result.warnings}, ensure_ascii=False))
        return 0
    except (ValueError, TypeError, OSError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
