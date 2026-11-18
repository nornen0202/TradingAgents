import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from tradingagents.llm_clients.codex_app_server import CodexAppServerSession


def main():
    parser = argparse.ArgumentParser(
        description="Verify model access and a fixed as-of cutoff on the research runner."
    )
    parser.add_argument("binary")
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    receipt = {
        "version": subprocess.check_output(
            [args.binary, "--version"], text=True
        ).strip(),
        "binary": args.binary,
        "turns": [],
    }
    roles = [
        ("gpt-6.2-sol", "medium"),
        ("gpt-6.2-astra", "high"),
        ("gpt-6.2-sol", "xhigh"),
    ]
    with tempfile.TemporaryDirectory() as workspace:
        session = CodexAppServerSession(
            codex_binary=args.binary,
            request_timeout=150,
            workspace_dir=workspace,
            cleanup_threads=True,
        )
        try:
            session.start()
            if not session.account_read().get("account"):
                raise RuntimeError("Runner is not authenticated")
            models = {model.get("model") for model in session.model_list()["data"]}
            for model, effort in roles:
                if model not in models:
                    raise RuntimeError(f"Missing requested model {model}")
                response = session.invoke(
                    prompt="Use only the supplied test record. Observations were 2026-11-16 value 17 and "
                    "2026-11-18 value 98. Return the last available value as of 2026-11-17.",
                    model=model,
                    reasoning_effort=effort,
                    summary=None,
                    personality=None,
                    output_schema={
                        "type": "object",
                        "properties": {"value": {"type": "integer"}},
                        "required": ["value"],
                        "additionalProperties": False,
                    },
                )
                if json.loads(response.final_text) != {"value": 17}:
                    raise RuntimeError(f"Cutoff test failed for {model} at {effort}")
                receipt["turns"].append(
                    {"model": model, "effort": effort, "observedValue": 17}
                )
        finally:
            session.close()
    args.receipt.write_text(json.dumps(receipt, indent=2), encoding="utf8")


if __name__ == "__main__":
    main()
