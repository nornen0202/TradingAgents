"""Verify the separate production-order contract using local fixture evidence."""

import argparse
import json
from pathlib import Path
import re

from tradingagents.execution.broker_adapter import Account, Intent
from tradingagents.execution.kis_live_readiness import MODE, MarketUsage, preview


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, required=True, help="A separate kis-live-readiness directory")
    parser.add_argument("--fixture", type=Path, required=True, help="Local isolated order evidence")
    options = parser.parse_args(argv)
    try:
        with options.fixture.open("rb") as stream:
            raw = stream.read(128_001)
        if len(raw) > 128_000:
            raise ValueError("LIVE_INPUT_INVALID")
        data = json.loads(raw.decode("utf-8-sig"))
        if not isinstance(data, dict) or data.get("evidence_scope") != "ISOLATED_FIXTURE":
            raise ValueError("LIVE_FIXTURE_REQUIRED")
        result = preview(options.state_dir.resolve(), Intent(**data["intent"]), account=Account(**data["account"]),
                         usage=MarketUsage(**data["usage"]), quote=data["quote"], session=data["session"], now=data["now"])
        request = result.pop("fixture_request")
        result["destination"] = {key: request[key] for key in ("host", "path", "tr_id")}
    except (AttributeError, KeyError, OSError, TypeError, ValueError) as exc:
        code = str(exc)
        result = {"mode": MODE, "evidence_scope": "ISOLATED_FIXTURE", "status": "BLOCKED", "live_order_requests": 0,
                  "error_code": code if re.fullmatch(r"LIVE_[A-Z_]+", code) else "LIVE_INPUT_INVALID"}
    print(json.dumps(result, ensure_ascii=True))
    return 0 if result["status"] == "CONTRACT_READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
