"""Feed portfolio weights and market events into a dedicated local LEAN Launcher."""
from collections import defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess

from tradingagents.atomic_io import atomic_write_bytes, atomic_write_json

from .research_ledger import market_events

_JSON_COMMENTS = re.compile(r'("(?:[^"\\]|\\.)*")|//[^\r\n]*|/\*.*?\*/', re.DOTALL)


def export_tape(root, sessions, bars, fx, targets, holdings, start, end):
    root.mkdir(parents=True, exist_ok=True)
    buffers = defaultdict(list)
    events, last_marks = market_events(sessions, start, end)
    for instant, day, market, opening in events:
        arms = {}
        for name, assets in holdings.items():
            arms[name] = {
                "bars": {symbol: bars[symbol][day] for symbol, area in assets.items()
                         if area == market and day in bars[symbol]},
                "targets": targets[name].get((market, day)) if opening else None,
            }
        row = {"day": day, "market": market, "open": opening, "fx": fx.at(instant),
               "mark": not opening and instant == last_marks[day], "arms": arms}
        buffers[instant.strftime("%Y%m")].append(
            instant.strftime("%Y%m%d %H%M%S") + "," + json.dumps(row, separators=(",", ":"), allow_nan=False))
    for month, rows in buffers.items():
        atomic_write_bytes(root / f"{month}.csv", ("\n".join(rows) + "\n").encode())


def compare_reference(curves, receipts):
    expected = {(row["day"], arm): (row["nav"], row["fill_count"])
                for arm, daily in curves.items() for row in daily}
    actual = {}
    for receipt in receipts:
        key = receipt["day"], receipt["arm"]
        if key in actual:
            raise ValueError(f"Duplicate LEAN portfolio mark {key}.")
        actual[key] = (receipt["nav"], receipt["fills"])
    if actual.keys() != expected.keys():
        raise ValueError(f"Missing {len(expected.keys() - actual.keys())} and extra "
                         f"{len(actual.keys() - expected.keys())} LEAN marks.")
    difference = 0.0
    for key, (nav, fills) in expected.items():
        other, other_fills = actual[key]
        if fills != other_fills or not math.isclose(nav, other, rel_tol=1e-12, abs_tol=.0001):
            raise ValueError(f"{key}: reference NAV {nav}, fills {fills}, LEAN NAV {other}, fills {other_fills}.")
        difference = max(difference, abs(nav - other))
    return {"lean_backtest_executed": True, "daily_portfolio_marks": len(expected),
            "max_nav_difference_krw": difference, "scope": "LEAN data clock and independent custom fills and account ledger"}


def run_lean(root, lean_root, dotnet):
    root, lean_root, dotnet = Path(root).resolve(), Path(lean_root).resolve(), Path(dotnet).resolve()
    report = json.loads((root / "study.json").read_bytes())
    curves = json.loads((root / "independent-ledger.json").read_bytes())["curves"]
    if not (root / "lean-tape").is_dir():
        raise ValueError("Run the research phase to produce the LEAN event tape.")
    tool = Path(__file__).with_name("ResearchReplay.cs")
    source = lean_root / "Algorithm.CSharp" / tool.name
    project = lean_root / "Launcher" / "QuantConnect.Lean.Launcher.csproj"
    if not dotnet.is_file() or not project.is_file() or not (lean_root / "Launcher" / "config.json").is_file():
        raise ValueError("Expected a dedicated LEAN checkout and a compatible dotnet SDK.")
    if source.exists() and source.read_bytes() != tool.read_bytes():
        raise ValueError("The dedicated LEAN checkout already has a different replay algorithm.")
    shutil.copyfile(tool, source)
    env = os.environ | {"NUGET_PACKAGES": str(root.parent / "lean-nuget"),
                        "DOTNET_CLI_HOME": str(root.parent / "lean-dotnet-home"),
                        "DOTNET_CLI_TELEMETRY_OPTOUT": "1", "TA_RESEARCH_LEAN_TAPE": str(root / "lean-tape"),
                        "TA_RESEARCH_LEAN_END": report["periods"]["전체"]["end"],
                        "TA_RESEARCH_LEAN_RESULT": str(root / "lean-nav.jsonl")}
    with (root / "lean-build.log").open("wb") as log:
        built = subprocess.run([str(dotnet), "build", str(project), "--nologo", "-v", "minimal"],
                               cwd=lean_root, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=900)
    if built.returncode:
        raise ValueError(f"LEAN build exit {built.returncode}. See {root / 'lean-build.log'}.")
    launch = project.parent / "bin" / "Debug"
    algorithm = launch / "QuantConnect.Algorithm.CSharp.dll"
    base_config = (project.parent / "config.json").read_text(encoding="utf-8-sig")
    config = json.loads(_JSON_COMMENTS.sub(lambda match: match[1] or "", base_config))
    config.update({"algorithm-type-name": "ResearchReplay", "algorithm-language": "CSharp",
                   "algorithm-location": str(algorithm), "environment": "backtesting",
                   "data-folder": str(lean_root / "Data"), "live-mode": False,
                   "results-destination-folder": str(root / "lean-engine")})
    path = root / "lean-config.json"
    atomic_write_json(path, config)
    with (root / "lean-engine.log").open("wb") as log:
        status = subprocess.run([str(dotnet), str(launch / "QuantConnect.Lean.Launcher.dll"), "--config", str(path)],
                                cwd=launch, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=900)
    if status.returncode:
        raise ValueError(f"LEAN Launcher exit {status.returncode}. See {root / 'lean-engine.log'}.")
    with (root / "lean-nav.jsonl").open(encoding="utf-8") as file:
        result = compare_reference(curves, map(json.loads, file))
    checksum = hashlib.sha256()
    for month in sorted((root / "lean-tape").glob("*.csv")):
        checksum.update(month.name.encode())
        checksum.update(month.read_bytes())
    result.update(plan_sha256=report["plan_sha256"], tape_sha256=checksum.hexdigest(),
                  algorithm_sha256=hashlib.sha256(tool.read_bytes()).hexdigest())
    output = root / "lean-reconciliation.json"
    atomic_write_json(output, result)
    return output
