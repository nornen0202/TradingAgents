"""Admit a completed fresh operator identity repair without rewriting research."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tradingagents.scheduled.operator_admission import (
    certify_operator_research,
    certify_integrity_recovery,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-dir", type=Path, required=True)
    parser.add_argument("--state-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--target-key", required=True)
    parser.add_argument("--integrity-correction", action="store_true")
    args = vars(parser.parse_args())
    correction = args.pop("integrity_correction")
    result = (certify_integrity_recovery if correction else certify_operator_research)(
        **args
    )
    print(
        json.dumps(
            {
                "status": "CERTIFIED",
                "baseline_eligible": result.get("baseline_eligible"),
                "evidence": result["evidence"],
            }
        )
    )


if __name__ == "__main__":
    main()
