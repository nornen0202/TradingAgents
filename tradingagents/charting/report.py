"""Integrated archive report: candles, execution reasons, events and verification.

The renderer consumes execution decisions; it does not calculate buy eligibility.
"""
from __future__ import annotations

import html
import json
from collections import Counter, defaultdict
from pathlib import Path

from .bars import finite, instant, validate_bars
from .indicators import anchored_vwap, volume_profile


def _load(path, *, list_allowed=False):
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
        return value if isinstance(value, dict) or (list_allowed and isinstance(value, list)) else {}
    except (OSError, ValueError):
        return {}


def _checkpoint_payloads(directory, stem):
    """Read both current and historical checkpoint filenames without trusting names as clocks."""
    checkpoint_dir = directory / "execution" / "checkpoints"
    paths = {directory / f"{stem}.json"}
    paths.update(checkpoint_dir.glob(f"{stem}_*.json"))
    paths.update(checkpoint_dir.glob(f"*_{stem}.json"))
    payloads, seen = [], set()
    for path in sorted(paths):
        payload = _load(path)
        identity = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        if payload and identity not in seen:
            seen.add(identity)
            payloads.append(payload)
    return payloads


def _snapshot_visible(payload, cutoff):
    # A later repackaging cannot introduce its contents into an earlier frame.
    # Legacy snapshots without container clocks retain only individually dated bars.
    clock_fields = ("ingested_at", "observed_at", "published_at", "evaluated_at", "asof", "asof_utc", "asof_local")
    clocks = [instant(payload[key]) for key in clock_fields if payload.get(key) is not None]
    return all(clock is not None and clock <= cutoff for clock in clocks)


def _latest_execution(directory, cutoff, ticker):
    candidates = []
    for payload in _checkpoint_payloads(directory, "execution_update"):
        evaluated = instant(payload.get("execution_asof") or payload.get("evaluated_at") or payload.get("asof"))
        ingested = instant(payload.get("ingested_at"))
        matches = not payload.get("ticker") or str(payload["ticker"]).upper() == str(ticker).upper()
        if matches and evaluated is not None and ingested is not None and evaluated <= ingested <= cutoff:
            candidates.append(((ingested, evaluated), payload))
    if not candidates:
        return {}
    last = max(key for key, _ in candidates)
    peers = [payload for key, payload in candidates if key == last]
    fields = ("decision_state", "decision_now", "reason_codes", "execution_asof", "market_data_asof", "valid_until")
    # A same-clock disagreement is not a verifiable revision; do not pick by filename.
    identities = {json.dumps({key: payload[key] for key in fields if key in payload}, sort_keys=True) for payload in peers}
    return peers[0] if len(identities) == 1 else {}


def _bar_vintages(records, cutoff):
    """Latest observed vintage per candle; same-observation conflicts remain excluded."""
    vintages, rejected = defaultdict(list), Counter()
    for raw, from_micro in records:
        checked = validate_bars([raw], analysis_as_of=cutoff)
        rejected.update(checked["rejected"])
        for bar in checked["bars"]:
            vintages[(instant(bar["timestamp"]), bar["interval"])].append((bar, from_micro))
    selected, micro_used = [], False
    value_fields = ("open", "high", "low", "close", "volume", "session_id")
    for key in sorted(vintages):
        peers = vintages[key]
        latest = max(instant(bar["observed_at"]) for bar, _ in peers)
        peers = [(bar, source) for bar, source in peers if instant(bar["observed_at"]) == latest]
        signatures = {tuple(bar[field] for field in value_fields) for bar, _ in peers}
        if len(signatures) != 1:
            rejected["conflicting_duplicate"] += len(peers)
            continue
        bar, from_micro = max(peers, key=lambda pair: (instant(pair[0]["available_at"]), pair[1]))
        selected.append(bar)
        micro_used = micro_used or from_micro
    return {"bars": selected, "rejected": dict(rejected), "micro_used": micro_used}


def build_review(ticker_dir, *, analysis_as_of, anchor=None, lifecycle=None):
    directory = Path(ticker_dir)
    cutoff = instant(analysis_as_of)
    if cutoff is None:
        raise ValueError("analysis_as_of must include a timezone")
    capture = _load(directory / "chart_evidence.json")
    from tradingagents.dataflows.market_policy import source_use_policy
    ticker = capture.get("ticker") or directory.name
    capture_entitled = source_use_policy(capture.get("provider") or "local_archive", entitlement=capture.get("entitlement"))["allowed"]
    capture_rows = capture.get("bars") or []
    records = [(row, False) for row in capture_rows] if capture_entitled else []
    source_rejected = Counter()
    if not capture_entitled:
        source_rejected["source_not_entitled"] += len(capture_rows)
    for micro in _checkpoint_payloads(directory, "microstructure_snapshot"):
        if not _snapshot_visible(micro, cutoff):
            continue
        micro_rows = micro.get("chart_bars") or []
        micro_entitled = source_use_policy(micro.get("provider") or "local_archive", entitlement=micro.get("entitlement"))["allowed"]
        micro_matches = not micro.get("ticker") or str(micro["ticker"]).upper() == str(ticker).upper()
        if not micro_entitled or not micro_matches:
            source_rejected["source_not_entitled" if not micro_entitled else "ticker_mismatch"] += len(micro_rows)
            continue
        records.extend((row, True) for row in micro_rows)
    bars = _bar_vintages(records, cutoff)
    bars["rejected"] = dict(Counter(bars["rejected"]) + source_rejected)
    visible_execution = _latest_execution(directory, cutoff, ticker)
    contract = _load(directory / "execution_contract.json")
    analysis = _load(directory / "analysis.json")
    contract_known = instant(analysis.get("finished_at"))
    contract_ingested = instant(contract.get("ingested_at"))
    contract = contract if (contract_known is not None and contract_ingested is not None
                            and contract_known <= contract_ingested <= cutoff) else {}
    from tradingagents.dataflows.event_timeline import build_event_timeline
    events = _load(directory / "event_timeline.json")
    pack = _load(directory / "earnings_event_pack.json")
    records = events.get("records") or [version for event in events.get("events", [])
                                        for version in event.get("versions", [event])] or pack.get("event_records") or []
    timeline = build_event_timeline(records,
                                    analysis_as_of=cutoff)
    evidence = _load(directory / "evidence_ledger.json", list_allowed=True)
    items = evidence if isinstance(evidence, list) else evidence.get("evidence_items", evidence.get("items", []))
    verified, unverified = [], 0
    for item in items:
        if not isinstance(item, dict):
            unverified += 1
            continue
        known = instant(item.get("known_at"))
        published = instant(item.get("published_at"))
        observed = instant(item.get("observed_at"))
        refs = item.get("source_refs") or []
        allowed = all(isinstance(ref, dict) and source_use_policy(ref.get("provider"), entitlement=ref.get("entitlement"))["allowed"] for ref in refs)
        if item.get("provider"):
            allowed = allowed and source_use_policy(item["provider"], entitlement=item.get("entitlement"))["allowed"]
        kind = str(item.get("kind") or "inference").lower()
        if (known is not None and published is not None and observed is not None
                and published <= known <= observed <= cutoff and allowed and kind in {"fact", "inference"}):
            verified.append({"claim": str(item.get("claim", "")), "kind": kind,
                             "published_at": published.isoformat(), "known_at": known.isoformat(),
                             "observed_at": observed.isoformat(), "event_time": published.isoformat(),
                             "ingested_at": observed.isoformat(), "evaluated_at": cutoff.isoformat()})
        else:
            unverified += 1
    series = []
    for interval in sorted({bar["interval"] for bar in bars["bars"]}):
        subset = [bar for bar in bars["bars"] if bar["interval"] == interval]
        start = anchor or subset[0]["timestamp"]
        series.append({"interval": interval, "bars": subset,
                       "avwap": anchored_vwap(subset, anchor=start, analysis_as_of=cutoff),
                       "profile": volume_profile(subset, analysis_as_of=cutoff)})
    return {"schema": "tradingagents.integrated-review/v1", "ticker": ticker,
            "analysis_as_of": cutoff.isoformat(), "read_only": True, "broker_orders_sent": 0,
            "execution": {key: visible_execution[key] for key in ("decision_state", "decision_now", "reason_codes", "execution_asof", "market_data_asof", "valid_until") if key in visible_execution},
            "plan": {key: contract[key] for key in ("structured_levels", "breakout_trigger", "breakout_level", "pullback_buy_zone",
                                                    "invalidation_price", "invalid_if_close_below", "invalid_if_intraday_below",
                                                    "entry_valid_until") if key in contract},
            "evidence": verified, "unverified_evidence_count": unverified, "events": timeline,
            "series": series, "rejected_bars": bars["rejected"], "lifecycle": lifecycle or {},
            "public_display_allowed": capture.get("public_display_allowed") is True and capture_entitled and not bars["micro_used"]}


def _escape(value):
    return html.escape(str(value if value is not None else "확인 불가"))


def _candles(item, plan):
    bars = item["bars"][-180:]
    if not bars:
        return "<p>완료 시각과 관측 시각을 검증할 수 있는 봉이 없습니다.</p>"
    levels = []
    for level in plan.get("structured_levels") or []:
        if not isinstance(level, dict):
            continue
        for field in ("price", "low", "high"):
            value = finite(level.get(field))
            if value is not None and value > 0:
                levels.append((str(level.get("label") or level.get("level_type") or "계획"), value))
    for field, label in (("breakout_trigger", "돌파 기준"), ("breakout_level", "돌파 기준"),
                         ("invalidation_price", "무효화"), ("invalid_if_close_below", "종가 무효화"),
                         ("invalid_if_intraday_below", "장중 무효화")):
        value = finite(plan.get(field))
        if value is not None and value > 0:
            levels.append((label, value))
    zone = plan.get("pullback_buy_zone")
    if isinstance(zone, dict):
        for field, label in (("low", "눌림 계획 하단"), ("high", "눌림 계획 상단")):
            value = finite(zone.get(field))
            if value is not None and value > 0:
                levels.append((label, value))
    low = min([b["low"] for b in bars] + [v for _, v in levels])
    high = max([b["high"] for b in bars] + [v for _, v in levels])
    padding = (high - low) * 0.08 or high * 0.01
    low, high = low - padding, high + padding
    y = lambda price: 300 - (price - low) / (high - low) * 260
    step = 700 / len(bars)
    marks = []
    for index, bar in enumerate(bars):
        x = 58 + (index + 0.5) * step
        color = "#13785f" if bar["close"] >= bar["open"] else "#c53b51"
        marks.append(f'<g><title>{_escape(bar["timestamp"])} O {bar["open"]:g} H {bar["high"]:g} L {bar["low"]:g} C {bar["close"]:g} V {bar["volume"]:g}</title>'
                     f'<path d="M{x:.2f},{y(bar["high"]):.2f}V{y(bar["low"]):.2f}" stroke="{color}"/>'
                     f'<rect x="{x-step*.3:.2f}" y="{min(y(bar["open"]),y(bar["close"])):.2f}" width="{max(.8,step*.6):.2f}" height="{max(1,abs(y(bar["close"])-y(bar["open"]))):.2f}" fill="{color}"/></g>')
    vwap = {row["timestamp"]: row["value"] for row in item["avwap"]["series"] if row["value"] is not None}
    points = " ".join(f'{58+(i+.5)*step:.2f},{y(vwap[b["timestamp"]]):.2f}' for i,b in enumerate(bars) if b["timestamp"] in vwap)
    marks.append(f'<polyline points="{points}" fill="none" stroke="#395dd1" stroke-width="2"/>')
    for label, value in levels:
        marks.append(f'<path d="M58,{y(value):.2f}H758" stroke="#8d6137" stroke-dasharray="4 4"/><text x="60" y="{y(value)-3:.2f}" font-size="11">{_escape(label)} {value:g}</text>')
    marks.append(f'<text x="5" y="42" font-size="12">{high:.4g}</text><text x="5" y="300" font-size="12">{low:.4g}</text>')
    return ('<svg role="img" aria-label="가격 봉과 Anchored VWAP 및 계획 가격" viewBox="0 0 790 340">'
            + "".join(marks) + '</svg>'
            + f'<p>표시 {len(bars)}봉 · {_escape(bars[0]["timestamp"])} ~ {_escape(bars[-1]["timestamp"])}</p>')


def render_review(review, *, public=False, fragment=False):
    """Native SVG avoids runtime CDN/data dependencies and third-party chart code."""
    if public and not review.get("public_display_allowed"):
        return '<section class="section"><h2>차트·근거 통합 검토</h2><p>시계열 재배포 권한이 확인된 자료만 공개합니다. 원자료 차트와 거래 추적은 로컬 보관 보고서에서 확인하세요.</p></section>'
    charts = []
    for item in review["series"]:
        profile = item["profile"]
        profile_rows = "".join(f'<tr><td>{b["low"]:.4g}–{b["high"]:.4g}</td><td>{b["volume"]:,.1f}</td></tr>' for b in profile["bins"])
        charts.append(f'<details open><summary>{_escape(item["interval"])} 가격·계획</summary>{_candles(item, review["plan"])}'
                      '<p>파랑: Anchored VWAP (전형가격 × 봉 거래량 근사). 시간봉별 가격 조정 기준이 다를 수 있습니다.</p>'
                      f'<details><summary>Volume Profile 근사 · POC {_escape(profile["poc"])}</summary>'
                      '<p>각 봉의 저가~고가 구간에 거래량을 균등 배분합니다. 실제 가격별 체결량·호가 잔량을 뜻하지 않습니다.</p>'
                      f'<div class="scroll"><table><tr><th>가격 구간</th><th>추정 거래량</th></tr>{profile_rows}</table></div></details></details>')
    execution = review["execution"]
    reason = ", ".join(str(value) for value in execution.get("reason_codes", [])) or "기존 판단 기록 없음"
    events = review["events"].get("events", [])
    event_rows = "".join('<tr>' + ''.join(f'<td>{_escape(row.get(field))}</td>' for field in
                             ("title", "scheduled_at", "published_at", "first_seen_at", "observed_at", "is_amended", "version_id")) + '</tr>' for row in events)
    evidence = "".join(f'<li>{_escape(row["kind"])} · {_escape(row["claim"])} · {_escape(row["published_at"])}</li>' for row in review["evidence"])
    # Public research pages never expose private fills, journal outcomes or account balances.
    lifecycle = {} if public else review.get("lifecycle") or {}
    trace = _escape(json.dumps(lifecycle, ensure_ascii=False, indent=2)) if lifecycle else "연결된 체결·회고 기록 없음"
    body = f'''<section class="section integrated-review"><h2>{_escape(review["ticker"])} 차트·근거 통합 검토</h2>
<p>분석 기준: {_escape(review["analysis_as_of"])} · 읽기전용</p>
<p>기존 실행 판단: <strong>{_escape(execution.get("decision_state"))}</strong> · {_escape(reason)}</p>
<p>이 화면은 실행 판단을 읽습니다. 시세 신선도와 계좌·세션 점검 결과는 기존 실행 엔진을 따릅니다.</p>
<div class="chart-grid">{''.join(charts) or '<p>검증된 캔들 데이터 없음</p>'}</div>
<h3>이벤트 발표·정정 이력</h3><div class="scroll"><table><tr><th>이벤트</th><th>예정 시각</th><th>발표 시각</th><th>최초 감지</th><th>관측 시각</th><th>정정 여부</th><th>버전</th></tr>{event_rows}</table></div>
<p>발표 시각이 없는 DART 자료는 보존된 최초 감지 시각으로 구분하며, 이를 발표 시각으로 간주하지 않습니다. 평가 시각은 위 분석 기준과 같습니다.</p>
<h3>확인 사실·추론</h3><ul>{evidence}</ul><p>시각 미검증 근거 {review["unverified_evidence_count"]}건 제외</p>
<h3>신호 → 의도 → 체결 → 회고</h3><details><summary>연결 기록 확인</summary><pre>{trace}</pre></details></section>'''
    if fragment:
        return body
    return '<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TradingAgents 통합 검토</title><style>' + _STYLE + '</style><main>' + body + '</main></html>'


def main(argv=None):
    import argparse
    from .snapshot import get_replay_snapshot

    parser = argparse.ArgumentParser(description="Render the same point-in-time snapshot used by the local viewer")
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--ticker-dir", required=True, type=Path)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--anchor")
    parser.add_argument("--journal", type=Path, action="append", default=[])
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        snapshot = get_replay_snapshot(args.ticker, args.as_of, ticker_dir=args.ticker_dir,
                                       db_paths=args.journal, anchor=args.anchor)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(render_review(snapshot), encoding="utf-8")
        print(str(args.output))
        return 0
    except (ValueError, TypeError, KeyError, OSError) as exc:
        parser.error(str(exc))
    return 2


_STYLE = '''body{font:16px/1.65 system-ui,sans-serif;background:#f3f6fa;color:#172338;margin:0}main{max-width:1400px;margin:auto;padding:24px}section{background:white;padding:24px;border-radius:16px}h2{margin-top:0}svg{width:100%;height:auto}details{border:1px solid #dce3ed;padding:12px;border-radius:8px;margin:12px 0;min-width:0}summary{cursor:pointer;font-weight:650}table{border-collapse:collapse;width:100%}th,td{padding:8px;text-align:left;border-bottom:1px solid #ddd;overflow-wrap:anywhere}.scroll{overflow:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere}.chart-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,500px),1fr));gap:16px}@media(max-width:500px){main,section{padding:12px}}'''


if __name__ == "__main__":
    raise SystemExit(main())
