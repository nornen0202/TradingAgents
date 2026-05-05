from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any


EXPECTED_BENCHMARKS = {
    "kr": ("KOSPI", "KOSDAQ"),
    "us": ("SPY", "QQQ"),
}

SENSITIVE_PATTERNS = (
    re.compile(r"\b\d{8}-\d{2}\b"),
    re.compile(r"\bODNO[-_A-Z0-9]*\b", re.IGNORECASE),
    re.compile(r"\bkis_\d{8}-\d{2}\b", re.IGNORECASE),
)

SENSITIVE_LITERAL_ENV_NAMES = (
    "KIS_ACCOUNT_NO",
    "KIS_Developers_ACCOUNT_NO",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify a public account performance site artifact.")
    parser.add_argument("--site-dir", required=True, help="Generated static site directory.")
    parser.add_argument("--market", required=True, choices=sorted(EXPECTED_BENCHMARKS), help="kr or us.")
    parser.add_argument("--run-label", help="Expected scheduled run label.")
    args = parser.parse_args()

    site_dir = Path(args.site_dir).resolve()
    expected = EXPECTED_BENCHMARKS[args.market]
    run = _select_run(site_dir=site_dir, market=args.market, run_label=args.run_label)
    run_id = str(run.get("run_id") or "").strip()
    _assert(run_id, "Selected run is missing run_id.")

    summary = run.get("summary") if isinstance(run.get("summary"), dict) else {}
    settings = run.get("settings") if isinstance(run.get("settings"), dict) else {}
    portfolio = run.get("portfolio") if isinstance(run.get("portfolio"), dict) else {}
    account_performance = portfolio.get("account_performance") if isinstance(portfolio.get("account_performance"), dict) else {}
    _assert(settings.get("run_mode") == "portfolio_only", f"{run_id} was not generated with run_mode=portfolio_only.")
    _assert(int(summary.get("total_tickers") or 0) == 0, f"{run_id} unexpectedly ran ticker analysis.")
    _assert(str(portfolio.get("status") or "") != "failed", f"{run_id} portfolio pipeline failed: {portfolio}")
    _assert(account_performance.get("enabled") is True, f"{run_id} account performance is not enabled.")
    _assert(str(account_performance.get("status") or "") != "failed", f"{run_id} account performance failed.")

    html_path = site_dir / "runs" / run_id / "portfolio.html"
    html = _read_text(html_path)
    required_fragments = (
        "계좌 성과 vs 지수/ETF",
        "실제 계좌 수익률",
        "복잡하게 운용한 프리미엄",
        "단순 기간 수익률 비교",
        "동일 현금흐름 시뮬레이션",
        "종목별 기여도",
        "매매 비용",
        "데이터 품질",
        "account_performance_public.json",
        "account_performance_chart_data.json",
        "account_performance_report.md",
        *expected,
    )
    for fragment in required_fragments:
        _assert(fragment in html, f"{html_path} is missing {fragment!r}.")
    _assert("account_snapshot.json" not in html, f"{html_path} links account_snapshot.json.")
    _assert_no_sensitive_text(html, html_path)

    download_dir = site_dir / "downloads" / run_id / "portfolio"
    public_json = download_dir / "account_performance_public.json"
    chart_json = download_dir / "account_performance_chart_data.json"
    report_md = download_dir / "account_performance_report.md"
    for path in (public_json, chart_json, report_md):
        _assert(path.exists(), f"Expected public artifact is missing: {path}")

    public_payload = _read_json(public_json)
    chart_payload = _read_json(chart_json)
    _assert(tuple(public_payload.get("benchmarks") or ()) == expected, f"Unexpected benchmarks in {public_json}.")
    _assert(str(public_payload.get("market_scope") or "").lower() == args.market, f"Unexpected market_scope in {public_json}.")
    _assert(str(public_payload.get("public_sanitization") or "") == "mask_identifiers", "Public sanitization mode changed.")
    _assert_no_sensitive_text(json.dumps(public_payload, ensure_ascii=False), public_json)
    _assert_no_sensitive_text(json.dumps(chart_payload, ensure_ascii=False), chart_json)

    quality = public_payload.get("data_quality") if isinstance(public_payload.get("data_quality"), dict) else {}
    _assert("snapshot_count" in quality, f"{public_json} is missing data_quality.snapshot_count.")
    _assert("ledger_event_count" in quality, f"{public_json} is missing data_quality.ledger_event_count.")
    _assert("benchmark_provider" in quality, f"{public_json} is missing data_quality.benchmark_provider.")

    periods = public_payload.get("periods") if isinstance(public_payload.get("periods"), list) else []
    if periods:
        for period in periods:
            if not isinstance(period, dict):
                continue
            simple = {str(item.get("benchmark")) for item in period.get("simple_benchmarks", []) if isinstance(item, dict)}
            if simple:
                _assert(set(expected).issubset(simple), f"{public_json} period {period.get('period')} is missing benchmark comparisons.")
    else:
        warnings = [str(item) for item in quality.get("warnings", []) if str(item)]
        _assert(
            any("snapshot_history_insufficient" in item or "period_partial" in item for item in warnings),
            f"{public_json} has no periods but did not explain the partial data quality.",
        )

    sanitized_snapshot = download_dir / "account_snapshot.json"
    if sanitized_snapshot.exists():
        snapshot_text = _read_text(sanitized_snapshot)
        _assert_no_sensitive_text(snapshot_text, sanitized_snapshot)
        _assert("***MASKED***" in snapshot_text, f"{sanitized_snapshot} did not mask public identifiers.")

    print(
        "Verified account performance site:",
        json.dumps(
            {
                "run_id": run_id,
                "market": args.market.upper(),
                "benchmarks": list(expected),
                "portfolio_status": portfolio.get("status"),
                "account_performance_status": account_performance.get("status"),
                "site": str(html_path),
            },
            ensure_ascii=False,
        ),
    )


def _select_run(*, site_dir: Path, market: str, run_label: str | None) -> dict[str, Any]:
    feed = _read_json(site_dir / "feed.json")
    runs = feed.get("runs") if isinstance(feed.get("runs"), list) else []
    expected_market = market.upper()
    candidates: list[dict[str, Any]] = []
    for run in runs:
        if not isinstance(run, dict):
            continue
        settings = run.get("settings") if isinstance(run.get("settings"), dict) else {}
        if settings.get("run_mode") != "portfolio_only":
            continue
        if run_label and run.get("label") != run_label:
            continue
        if str(settings.get("market") or "").upper() != expected_market:
            continue
        candidates.append(run)
    candidates.sort(key=lambda item: str(item.get("started_at") or ""), reverse=True)
    _assert(candidates, f"No portfolio_only {expected_market} run found in {site_dir / 'feed.json'}.")
    return candidates[0]


def _read_json(path: Path) -> dict[str, Any]:
    _assert(path.exists(), f"Missing JSON file: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AssertionError(f"Invalid JSON in {path}: {exc}") from exc
    _assert(isinstance(payload, dict), f"Expected object JSON in {path}.")
    return payload


def _read_text(path: Path) -> str:
    _assert(path.exists(), f"Missing file: {path}")
    return path.read_text(encoding="utf-8")


def _assert_no_sensitive_text(value: str, path: Path) -> None:
    for env_name in SENSITIVE_LITERAL_ENV_NAMES:
        literal = str(os.environ.get(env_name) or "").strip()
        if literal:
            _assert(literal not in value, f"{path} leaked the raw {env_name} value.")
    for pattern in SENSITIVE_PATTERNS:
        match = pattern.search(value)
        _assert(match is None, f"{path} leaked sensitive identifier matching {pattern.pattern!r}.")


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


if __name__ == "__main__":
    main()
