from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from .packet import (
    PROMPT_CONTRACTS,
    SURFACES,
    WORK_REPORT_SCHEMA,
    WORK_SCHEMA,
    build_surface_packet,
    prompt_path,
    seal_packet,
)
from .runtime import validate_packet, validate_work_report


def build_work_site(
    *,
    site_dir: Path,
    archive_dir: Path,
    public_base_url: str = "",
) -> dict[str, Any]:
    root = Path(site_dir) / "work" / "v1"
    if root.exists():
        shutil.rmtree(root)
    (root / "prompts").mkdir(parents=True, exist_ok=True)
    base = str(public_base_url or "").strip().rstrip("/")
    packet_archive = Path(archive_dir) / "work-public" / "v1"
    index: dict[str, Any] = {
        "schema": WORK_SCHEMA,
        "streams": {},
    }

    for surface in SURFACES:
        source_prompt = prompt_path(surface)
        target_prompt = root / "prompts" / source_prompt.name
        shutil.copy2(source_prompt, target_prompt)
        packet = _fit_packet_budget(
            build_surface_packet(surface, archive_dir=archive_dir, public=True),
            max_chars=180_000,
        )
        validate_packet(packet, max_chars=180_000)
        if not _is_safe_public_packet(packet, surface=surface):
            raise ValueError(f"Refusing to publish unsafe public Work packet: {surface}")
        packet_bytes = (json.dumps(packet, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        packet_sha = hashlib.sha256(packet_bytes).hexdigest()
        event_name = _safe_name(str(packet["event_id"])) + ".json"
        archived_event_path = packet_archive / surface / "events" / event_name
        if archived_event_path.exists() and archived_event_path.read_bytes() != packet_bytes:
            raise ValueError(f"Immutable public Work event collision: {surface}/{event_name}")
        _write_bytes(archived_event_path, packet_bytes)
        events_root = root / surface / "events"
        cache_path = archived_event_path.parent.parent / "public-cache-v2.json"
        approved = _load_public_cache(cache_path, surface=surface)
        approved[event_name] = packet_sha
        safe_events = _latest_safe_event_files(
            archived_event_path.parent,
            surface=surface,
            approved_sha256=approved,
            limit=120,
        )
        for prior in safe_events:
            _write_bytes(events_root / prior.name, prior.read_bytes())
        _write_json(
            cache_path,
            {
                "schema": "tradingagents.work-public-cache/v2",
                "surface": surface,
                "events": {prior.name: hashlib.sha256(prior.read_bytes()).hexdigest() for prior in safe_events},
            },
        )
        _write_bytes(root / surface / "latest.json", packet_bytes)

        prefix = f"{base}/work/v1" if base else "/work/v1"
        status = {
            "schema": WORK_SCHEMA,
            "surface": surface,
            "event_id": packet["event_id"],
            "source_sha256": packet["source_sha256"],
            "packet_sha256": packet_sha,
            "prompt_contract_version": PROMPT_CONTRACTS[surface],
            "prompt_sha256": packet["prompt_sha256"],
            "skill_sha256": packet["skill_sha256"],
            "task_manifest_sha256": packet["task_manifest_sha256"],
            "workflow_contract_sha256": packet["workflow_contract_sha256"],
            "status_url": f"{prefix}/{surface}/status.json",
            "latest_url": f"{prefix}/{surface}/latest.json",
            "event_url": f"{prefix}/{surface}/events/{event_name}",
            "prompt_url": f"{prefix}/prompts/{source_prompt.name}",
            "source_health": (packet.get("body") or {}).get("source_health"),
            "report_mode": (packet.get("body") or {}).get("report_mode"),
        }
        report_status = _publish_latest_report(
            root=root,
            archive_dir=Path(archive_dir),
            surface=surface,
            url_prefix=prefix,
        )
        if report_status:
            status["integrated_report"] = report_status
        _write_json(root / surface / "status.json", status)
        index["streams"][surface] = status

    _write_json(root / "index.json", index)
    _write_bytes(Path(site_dir) / "work" / "index.html", _work_report_index_html().encode("utf-8"))
    return index


def _publish_latest_report(
    *,
    root: Path,
    archive_dir: Path,
    surface: str,
    url_prefix: str,
) -> dict[str, Any]:
    latest_source = archive_dir / "work-reports" / surface / "latest.json"
    if not latest_source.is_file():
        return {}
    try:
        report = json.loads(latest_source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid latest Work report for {surface}: {exc}") from exc
    if not isinstance(report, dict):
        raise ValueError(f"Invalid latest Work report for {surface}: expected object")
    validate_work_report(report)
    if report.get("schema") != WORK_REPORT_SCHEMA or report.get("surface") != surface:
        raise ValueError(f"Latest Work report binding mismatch: {surface}")
    report_sha = str(report["report_sha256"])
    content_source = archive_dir / "work-reports" / surface / "events" / f"{report_sha}.json"
    if not content_source.is_file() or content_source.read_bytes() != latest_source.read_bytes():
        raise ValueError(f"Latest Work report is not backed by its content-addressed event: {surface}")
    target_root = root / surface / "report"
    _write_bytes(target_root / "events" / f"{report_sha}.json", content_source.read_bytes())
    _write_bytes(target_root / "latest.json", latest_source.read_bytes())
    return {
        "schema": WORK_REPORT_SCHEMA,
        "report_id": report.get("report_id"),
        "report_sha256": report_sha,
        "event_id": report.get("event_id"),
        "source_sha256": report.get("source_sha256"),
        "published_at": report.get("published_at"),
        "latest_url": f"{url_prefix}/{surface}/report/latest.json",
        "event_url": f"{url_prefix}/{surface}/report/events/{report_sha}.json",
    }


def _fit_packet_budget(packet: dict[str, Any], *, max_chars: int) -> dict[str, Any]:
    fitted = json.loads(json.dumps(packet, ensure_ascii=False))
    body = fitted.get("body") if isinstance(fitted.get("body"), dict) else {}
    events = body.get("events") if isinstance(body.get("events"), list) else None
    omitted = 0
    while events and len(json.dumps(fitted, ensure_ascii=False, indent=2)) > max_chars:
        events.pop()
        omitted += 1
        coverage = body.get("coverage") if isinstance(body.get("coverage"), dict) else {}
        coverage["transmitted_events"] = len(events)
        coverage["truncated"] = True
        coverage["omitted_due_to_packet_budget"] = omitted
        body["coverage"] = coverage
        fitted = seal_packet(str(packet.get("surface") or ""), body=body)
        body = fitted["body"]
        events = body.get("events") if isinstance(body.get("events"), list) else None
    return fitted


def _latest_safe_event_files(
    path: Path,
    *,
    surface: str,
    approved_sha256: dict[str, str],
    limit: int,
) -> list[Path]:
    """Return current-contract public events and purge unsafe legacy packets.

    ``work-public`` predates the public/private split and is persistent across
    Pages rebuilds.  Copying its files verbatim can therefore re-publish a
    legacy market packet containing portfolio membership or account actions.
    A packet is retained only when it was approved by the v2 cache ledger,
    is sealed by the current contract, and satisfies the current public
    recovery shape.  The first v2 build consequently removes all unproven
    legacy events.  Invalid files are deleted from the public-event cache; the
    private run archive is not modified.
    """

    if not path.exists():
        return []
    candidates = [candidate for candidate in path.glob("*.json") if candidate.is_file()]
    candidates.sort(key=lambda candidate: candidate.stat().st_mtime_ns, reverse=True)
    safe: list[Path] = []
    for candidate in candidates:
        try:
            candidate_sha = hashlib.sha256(candidate.read_bytes()).hexdigest()
        except OSError:
            candidate_sha = ""
        try:
            packet = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            packet = None
        if (
            approved_sha256.get(candidate.name) == candidate_sha
            and isinstance(packet, dict)
            and _is_safe_public_packet(packet, surface=surface)
        ):
            if len(safe) < max(1, int(limit)):
                safe.append(candidate)
            continue
        try:
            candidate.unlink()
        except OSError as exc:
            raise RuntimeError(f"Could not purge unsafe public Work event {candidate}: {exc}") from exc
    return safe


def _load_public_cache(path: Path, *, surface: str) -> dict[str, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict):
        return {}
    if payload.get("schema") != "tradingagents.work-public-cache/v2" or payload.get("surface") != surface:
        return {}
    events = payload.get("events") if isinstance(payload.get("events"), dict) else {}
    return {
        str(name): str(digest)
        for name, digest in events.items()
        if str(name).endswith(".json") and len(str(digest)) == 64
    }


_PRIVATE_MARKET_PACKET_KEYS = {
    "account",
    "account_id",
    "account_no",
    "account_number",
    "action_if_triggered",
    "action_now",
    "actions",
    "average_cost",
    "avg_price",
    "cash_available",
    "cash_balance",
    "cost_basis",
    "current_weight",
    "delta_krw",
    "delta_krw_if_triggered",
    "delta_krw_now",
    "holding",
    "holdings",
    "is_held",
    "is_owned",
    "market_value",
    "portfolio",
    "portfolio_relative_action",
    "position_metrics",
    "position_size",
    "position_value",
    "private_portfolio_overlay",
    "quantity",
    "shares",
    "target_value",
    "target_weight",
    "target_weight_if_triggered",
    "target_weight_now",
}


def _is_safe_public_packet(packet: dict[str, Any], *, surface: str) -> bool:
    """Verify integrity, current contract, and market privacy before publish."""

    if str(packet.get("surface") or "") != surface:
        return False
    try:
        validate_packet(packet, max_chars=180_000)
    except Exception:
        return False
    body = packet.get("body") if isinstance(packet.get("body"), dict) else {}
    expected = seal_packet(surface, body=body)
    if set(packet) != set(expected) or any(packet.get(key) != expected.get(key) for key in expected):
        return False
    if surface not in {"kr", "us"}:
        return True
    if _contains_private_market_key(body):
        return False
    current = body.get("current") if isinstance(body.get("current"), dict) else {}
    bundle = current.get("bundle") if isinstance(current.get("bundle"), dict) else {}
    if bundle:
        scope = bundle.get("transmission_scope") if isinstance(bundle.get("transmission_scope"), dict) else {}
        quality = bundle.get("quality") if isinstance(bundle.get("quality"), dict) else {}
        if scope.get("public_recovery_only") is not True:
            return False
        if scope.get("portfolio_membership_omitted") is not True:
            return False
        if quality.get("portfolio_membership_omitted") is not True:
            return False
    coverage = current.get("universe_coverage") if isinstance(current.get("universe_coverage"), dict) else {}
    if coverage and coverage.get("portfolio_coverage_details_omitted") is not True:
        return False
    return True


def _contains_private_market_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).strip().lower() in _PRIVATE_MARKET_PACKET_KEYS:
                return True
            if _contains_private_market_key(item):
                return True
    elif isinstance(value, list):
        return any(_contains_private_market_key(item) for item in value)
    return False


def _safe_name(value: str) -> str:
    return "".join(character if character.isalnum() or character in "._-" else "-" for character in value)[:160]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_bytes(path, (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def _write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _work_report_index_html() -> str:
    """Return a responsive, dependency-free viewer for public Work reports."""

    return r"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="index,follow">
  <meta name="description" content="TradingAgents ChatGPT Work KR·US·YouTube·PRISM 종합 분석 리포트">
  <title>ChatGPT Work 종합 분석 | TradingAgents</title>
  <style>
    :root { color-scheme: dark; --bg:#07111f; --panel:#0e1c2f; --line:#263a52; --text:#eef6ff; --muted:#a9bdd2; --accent:#62d6ff; --good:#6ee7b7; }
    * { box-sizing:border-box; }
    body { margin:0; background:linear-gradient(145deg,#06101d,#0b1a2a 55%,#0b1324); color:var(--text); font:16px/1.58 system-ui,-apple-system,"Segoe UI",sans-serif; }
    a { color:var(--accent); }
    header, main { width:min(1120px,calc(100% - 32px)); margin:auto; }
    header { padding:42px 0 22px; }
    .eyebrow { color:var(--good); font-size:.78rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }
    h1 { margin:.35rem 0 .45rem; font-size:clamp(1.85rem,5vw,3.2rem); line-height:1.08; }
    .lede, .status, .meta { color:var(--muted); }
    nav, .tabs { display:flex; gap:8px; flex-wrap:wrap; margin-top:18px; }
    nav a, button, .raw-link { border:1px solid var(--line); border-radius:999px; background:#102239; color:var(--text); padding:9px 14px; text-decoration:none; font:inherit; font-weight:700; cursor:pointer; }
    button[aria-selected="true"] { color:#03111b; background:var(--accent); border-color:var(--accent); }
    main { padding-bottom:56px; }
    .panel { margin-top:18px; padding:clamp(18px,4vw,30px); border:1px solid var(--line); border-radius:20px; background:rgba(14,28,47,.94); box-shadow:0 18px 55px rgba(0,0,0,.22); }
    .report-head { display:flex; justify-content:space-between; gap:18px; align-items:flex-start; }
    h2 { margin:0; font-size:clamp(1.35rem,3.5vw,2rem); }
    .meta { margin:.45rem 0 0; font-size:.92rem; }
    .summary { margin:20px 0; padding:16px; border-left:4px solid var(--accent); background:#0a1728; border-radius:0 12px 12px 0; }
    .top-actions { display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:10px; margin:14px 0 24px; padding:0; list-style:none; }
    .top-actions li { border:1px solid var(--line); border-radius:14px; padding:13px; background:#0a1728; white-space:pre-wrap; }
    details { border-top:1px solid var(--line); padding-top:18px; }
    summary { cursor:pointer; font-weight:800; }
    pre { margin:14px 0 0; padding:16px; overflow-wrap:anywhere; white-space:pre-wrap; border-radius:14px; background:#050c16; color:#d9e8f6; font:14px/1.62 ui-monospace,SFMono-Regular,Consolas,monospace; }
    .error { color:#ffb4b4; }
    [hidden] { display:none !important; }
    @media (max-width:640px) {
      header, main { width:min(100% - 20px,1120px); }
      header { padding-top:26px; }
      nav a, button, .raw-link { flex:1 1 auto; text-align:center; }
      .report-head { display:block; }
      .raw-link { display:inline-block; margin-top:14px; }
      .panel { border-radius:16px; }
    }
  </style>
</head>
<body>
  <header>
    <div class="eyebrow">Public · PC·모바일 공용</div>
    <h1>ChatGPT Work 종합 분석</h1>
    <p class="lede">KR·US 종목 분석과 YouTube·PRISM 근거를 Work가 다시 종합한 공개 리포트입니다. 보고서 시점과 현재 주문 가능성은 구분해서 확인하세요.</p>
    <nav aria-label="주요 리포트">
      <a href="../strategy.html?market=kr">PC 투자 전략</a>
      <a href="../mobile/strategy.html?market=kr">모바일 투자 전략</a>
      <a href="../youtube/">YouTube 분석</a>
      <a href="../prism-telegram/">PRISM 분석</a>
    </nav>
  </header>
  <main>
    <div class="tabs" role="tablist" aria-label="Work 분석 종류">
      <button type="button" data-surface="kr" role="tab">KR 종합 전략</button>
      <button type="button" data-surface="us" role="tab">US 종합 전략</button>
      <button type="button" data-surface="youtube" role="tab">YouTube 종합</button>
      <button type="button" data-surface="prism" role="tab">PRISM 종합</button>
    </div>
    <p id="status" class="status" aria-live="polite">리포트를 불러오는 중입니다.</p>
    <section id="report" class="panel" hidden>
      <div class="report-head">
        <div><h2 id="title"></h2><p id="meta" class="meta"></p></div>
        <a id="raw" class="raw-link" href="#">AI·원문 JSON</a>
      </div>
      <div id="summary" class="summary" hidden></div>
      <section id="actions-wrap" hidden><h3>핵심 제안</h3><ol id="actions" class="top-actions"></ol></section>
      <details open><summary>전체 Work 리포트</summary><pre id="markdown"></pre></details>
    </section>
  </main>
  <script>
  (() => {
    const surfaces = new Set(['kr','us','youtube','prism']);
    const buttons = [...document.querySelectorAll('[data-surface]')];
    const status = document.getElementById('status');
    const report = document.getElementById('report');
    const title = document.getElementById('title');
    const meta = document.getElementById('meta');
    const raw = document.getElementById('raw');
    const summary = document.getElementById('summary');
    const actionsWrap = document.getElementById('actions-wrap');
    const actions = document.getElementById('actions');
    const markdown = document.getElementById('markdown');
    const labels = {kr:'KR 종합 전략',us:'US 종합 전략',youtube:'YouTube 종합',prism:'PRISM 종합'};

    function localTime(value) {
      if (!value) return '시각 정보 없음';
      const parsed = new Date(value);
      return Number.isNaN(parsed.getTime()) ? String(value) : new Intl.DateTimeFormat('ko-KR', {dateStyle:'full',timeStyle:'medium',timeZone:'Asia/Seoul'}).format(parsed);
    }
    function plain(value) {
      if (value == null) return '';
      if (typeof value === 'string' || typeof value === 'number') return humanize(String(value));
      if (Array.isArray(value)) return value.map(plain).filter(Boolean).join(' · ');
      if (typeof value === 'object') {
        const keys = ['ticker','display_name','action','stance','readiness','summary','rationale','reason','thesis'];
        const picked = keys.map((key) => value[key]).filter((item) => item != null).map(plain).filter(Boolean);
        return picked.length ? picked.join(' · ') : humanize(JSON.stringify(value, null, 2));
      }
      return String(value);
    }
    function humanize(value) {
      const replacements = new Map([
        ['BLOCKED_STALE','주문 전 실시간 재확인'],['BLOCKED_INCOMPLETE','필수 데이터 재확인'],
        ['NEEDS_LIVE_RECHECK','주문 전 실시간 재확인'],['WAIT_FOR_TRIGGER','조건 충족 대기'],
        ['READY_NOW','현재 조건 확인됨'],['MARKET_CLOSED','개장 후 재확인'],
        ['DATA_OUTAGE','데이터 복구 후 재확인'],['RESEARCH_ONLY','분석 참고 전용'],
        ['NO_ENTRY','신규 진입 보류'],['IMMEDIATE','현재 조건 확인됨'],
        ['COMPLETE','전체 분석 완료'],['DEGRADED','일부 데이터 재확인'],
        ['RESEARCH','분석 참고'],['AVOID','매수 보류'],['WATCH','관찰'],['HOLD','보유'],
        ['STALE','시세 만료'],['MIXED','현재·과거 자료 혼합'],['OK','정상'],
        ['BUY','매수 검토'],['ADD','추가 매수 검토'],['SELL','매도 검토'],['REDUCE','비중 축소'],
        ['confidence','신뢰도'],['sizing','비중 조절'],['execution','실행 판단'],['thesis','투자 논지'],
        ['analysis','분석'],['current','현재'],['run','실행 회차'],['event','이벤트'],
        ['live recheck','실시간 재확인'],['packet','분석 자료'],
        ['RVOL','상대거래량(RVOL)'],['VWAP','거래량가중평균가격(VWAP)'],
      ]);
      let text = String(value || '');
      for (const [machine, investor] of replacements) {
        text = text.replace(new RegExp(`(^|[^A-Z0-9_])${machine}(?=$|[^A-Z0-9_])`, 'g'), (_, prefix) => `${prefix}${investor}`);
      }
      return text;
    }
    function topActionText(item, strategies) {
      const ticker = String((item || {}).ticker || '').trim();
      const strategy = strategies.find((candidate) => String(candidate.ticker || '').trim() === ticker) || {};
      const thesis = strategy.thesis && typeof strategy.thesis === 'object' ? strategy.thesis : {};
      const condition = Array.isArray(thesis.entry_conditions) ? thesis.entry_conditions[0] : thesis.entry_conditions;
      return [ticker, thesis.stance, condition, (item || {}).readiness].map(plain).filter(Boolean).join(' · ');
    }
    async function load(surface) {
      buttons.forEach((button) => button.setAttribute('aria-selected', String(button.dataset.surface === surface)));
      status.classList.remove('error');
      status.textContent = `${labels[surface]} 리포트를 불러오는 중입니다.`;
      report.hidden = true;
      const url = `v1/${surface}/report/latest.json`;
      try {
        const response = await fetch(url, {cache:'no-store', credentials:'omit'});
        if (!response.ok) throw new Error('아직 공개된 Work 리포트가 없습니다.');
        const payload = await response.json();
        const structured = payload.structured_report && typeof payload.structured_report === 'object' ? payload.structured_report : {};
        title.textContent = humanize(structured.title || labels[surface]);
        const asOf = structured.as_of || structured.generated_at;
        meta.textContent = `분석 기준 ${localTime(asOf)} · Work 게시 ${localTime(payload.published_at)}`;
        raw.href = url;
        const summaryText = plain(structured.summary);
        summary.textContent = summaryText;
        summary.hidden = !summaryText;
        const topActions = Array.isArray(structured.top_actions) ? structured.top_actions : [];
        const strategies = Array.isArray(structured.strategies) ? structured.strategies : [];
        actions.replaceChildren(...topActions.map((item) => {
          const li = document.createElement('li');
          li.textContent = topActionText(item, strategies);
          return li;
        }));
        actionsWrap.hidden = topActions.length === 0;
        markdown.textContent = humanize(payload.report_markdown || JSON.stringify(structured, null, 2));
        status.textContent = `${labels[surface]} · 공개 리포트 로드 완료`;
        report.hidden = false;
        const next = new URL(location.href);
        next.searchParams.set('surface', surface);
        history.replaceState(null, '', next);
      } catch (error) {
        status.classList.add('error');
        status.textContent = error instanceof Error ? error.message : '리포트를 불러오지 못했습니다.';
      }
    }
    buttons.forEach((button) => button.addEventListener('click', () => load(button.dataset.surface)));
    const requested = new URLSearchParams(location.search).get('surface') || 'kr';
    load(surfaces.has(requested) ? requested : 'kr');
  })();
  </script>
</body>
</html>
"""
