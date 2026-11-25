"""Publish aggregate autotrader observations without copying the private dashboard."""

from contextlib import closing
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import Callable

from tradingagents.atomic_io import atomic_write_bytes

PUBLIC_SCHEMA = "tradingagents.autotrader-public/v1"
PUBLIC_FILES = ("dashboard_data.json", "us_dashboard_data.json", "index.html")
MARKETS = ("KR", "US")
PAPER_SCOPES = {"shadow": "local_simulation", "kis_vts": "broker_paper"}
COUNTS = {
    "queued_candidates": "제출 전 대기 후보",
    "accepted_pending_fill_confirmation": "접수 기록 · 체결 여부 미확인",
    "confirmed_unfilled": "브로커에서 확인한 미체결",
    "confirmed_fills": "브로커에서 확인한 체결",
    "submission_unknown": "접수 결과 미확인",
    "not_accepted": "접수되지 않음",
    "simulated_matches": "로컬 모의 체결",
    "simulated_round_trip_samples": "로컬 모의 청산 표본",
}


def _market_payload(conn, market, mode, generated_at):
    scope = PAPER_SCOPES.get(mode)
    payload = {
        "schema": PUBLIC_SCHEMA,
        "market": market,
        "generated_at": generated_at,
        "scope": scope,
        "observation_status": "ledger_unavailable" if scope else "unavailable",
        **dict.fromkeys(COUNTS),
    }
    if conn is None:
        return payload

    queued = conn.execute(
        "SELECT COUNT(*) FROM autotrader_pending_entries WHERE market=? AND mode=? AND status='QUEUED'",
        (market, mode),
    ).fetchone()[0]
    orders = dict(conn.execute(
        "SELECT status, COUNT(*) FROM autotrader_order_intents WHERE market=? AND mode=? GROUP BY status",
        (market, mode),
    ))
    payload.update(
        observation_status="observed" if orders else "no_order_samples",
        queued_candidates=queued,
        submission_unknown=orders.get("SUBMITTING", 0) + orders.get("UNKNOWN", 0),
        not_accepted=orders.get("FAILED", 0),
    )
    if mode == "shadow":
        payload["simulated_matches"] = orders.get("SUBMITTED", 0)
        payload["simulated_round_trip_samples"] = conn.execute(
            "SELECT COUNT(*) FROM autotrader_trades WHERE market=? AND mode='shadow'",
            (market,),
        ).fetchone()[0]
    else:
        # The current broker intent table records submission receipts. Its
        # SUBMITTED status and locally inferred positions/closures cannot
        # establish that an order filled or that it remained unfilled.
        payload["accepted_pending_fill_confirmation"] = orders.get("SUBMITTED", 0)
    return payload


def _public_payloads(db_path: Path, mode: str | None):
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if mode in PAPER_SCOPES and db_path.is_file():
        try:
            with closing(sqlite3.connect(f"{db_path.resolve().as_uri()}?mode=ro", uri=True, timeout=2)) as conn:
                conn.execute("BEGIN")
                return tuple(_market_payload(conn, market, mode, generated_at) for market in MARKETS)
        except sqlite3.Error:
            # The publisher can report unavailable evidence without initializing
            # or repairing the broker/strategy ledger.
            pass
    return tuple(_market_payload(None, market, mode, generated_at) for market in MARKETS)


def _public_json(payload: dict) -> bytes:
    return (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("ascii")


def _render_public_dashboard(kr: dict, us: dict) -> bytes:
    def section(data, name):
        labels = {"observed": "주문 기록 있음", "no_order_samples": "제출 주문 표본 없음",
                  "ledger_unavailable": "관측 자료 없음", "unavailable": "공개 관측 자료 없음"}
        scopes = {"broker_paper": "브로커 모의", "local_simulation": "로컬 모의", None: "모의 범위 미표시"}
        rows = []
        for key, label in COUNTS.items():
            value = data[key]
            text = "확인 자료 없음" if value is None else f"{value}건"
            if key == "simulated_round_trip_samples" and value == 0:
                text = "표본 없음"
            rows.append(f"<tr><th scope='row'>{label}</th><td>{text}</td></tr>")
        return (f"<section><h2>{name}</h2><p>{scopes[data['scope']]} · {labels[data['observation_status']]}</p>"
                f"<table>{''.join(rows)}</table></section>")

    return f"""<!doctype html>
<html lang="ko">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TradingAgents 모의 자동매매 관측</title>
<style>
body {{font: 1rem/1.6 system-ui, sans-serif; max-width: 48rem; margin: 2rem auto; padding: 0 1rem}}
th,td {{text-align: left; padding: .4rem 1rem .4rem 0; border-bottom: 1px solid #ccc}}
</style>
<h1>TradingAgents 모의 자동매매 관측</h1>
<p>게시용 집계 시각 <time>{kr['generated_at']}</time></p>
{section(kr, "한국")}
{section(us, "미국")}
</html>
""".encode("utf-8")


def build_public_autotrader_dashboard(archive_dir: Path, site_dir: Path, *, mode: str | None) -> Path:
    """Generate the three public files from a read-only, market-scoped SQLite snapshot."""
    kr, us = _public_payloads(Path(archive_dir) / "paper" / "autotrader.sqlite", mode)
    target = Path(site_dir) / "autotrader"
    target.mkdir(parents=True, exist_ok=True)
    for name, payload in zip(PUBLIC_FILES[:2], (kr, us), strict=True):
        atomic_write_bytes(target / name, _public_json(payload))
    index = target / "index.html"
    atomic_write_bytes(index, _render_public_dashboard(kr, us))
    return index


def _validated_public_json(raw: bytes, expected_market: str) -> dict:
    data = json.loads(raw)
    fields = {"schema", "market", "generated_at", "scope", "observation_status", *COUNTS}
    if not isinstance(data, dict) or data.keys() != fields:
        raise ValueError("Unexpected autotrader publication fields")
    timestamp = datetime.fromisoformat(data["generated_at"])
    if (data["schema"] != PUBLIC_SCHEMA or data["market"] != expected_market
            or timestamp.tzinfo != timezone.utc or data["generated_at"] != timestamp.isoformat(timespec="seconds")
            or data["scope"] not in (*PAPER_SCOPES.values(), None)
            or data["observation_status"] not in {"observed", "no_order_samples", "ledger_unavailable", "unavailable"}
            or any(value is not None and (type(value) is not int or value < 0) for value in (data[k] for k in COUNTS))
            or raw != _public_json(data)):
        raise ValueError("Unexpected autotrader publication content")
    if (data["scope"] is None) != (data["observation_status"] == "unavailable"):
        raise ValueError("Unexpected autotrader observation scope")
    observed = data["observation_status"] in {"observed", "no_order_samples"}
    exposed_counts = set()
    if observed:
        exposed_counts.update({"queued_candidates", "submission_unknown", "not_accepted"})
        if data["scope"] == "local_simulation":
            exposed_counts.update({"simulated_matches", "simulated_round_trip_samples"})
        elif data["scope"] == "broker_paper":
            exposed_counts.add("accepted_pending_fill_confirmation")
        else:
            raise ValueError("Unexpected autotrader observation scope")
    if exposed_counts != {key for key in COUNTS if data[key] is not None}:
        raise ValueError("Unexpected autotrader observation counts")
    return data


def verify_public_autotrader_files(paths: list[str], read_bytes: Callable[[str], bytes]) -> dict[str, dict[str, str | int]]:
    """Verify and fingerprint the exact artifacts. An absent dashboard is allowed."""
    if not paths:
        return {}
    expected = [f"autotrader/{name}" for name in PUBLIC_FILES]
    if sorted(paths) != sorted(expected):
        raise ValueError("Unexpected autotrader publication paths")
    try:
        contents = {path: read_bytes(path) for path in expected}
        kr, us = (_validated_public_json(contents[path], market)
                  for path, market in zip(expected[:2], MARKETS, strict=True))
        if kr["generated_at"] != us["generated_at"] or contents[expected[-1]] != _render_public_dashboard(kr, us):
            raise ValueError("Unexpected autotrader publication HTML or generation")
    except (ValueError, TypeError):
        raise ValueError("Unsafe autotrader publication artifacts") from None
    return {path: {"sha256": sha256(data).hexdigest(), "size": len(data)} for path, data in contents.items()}
