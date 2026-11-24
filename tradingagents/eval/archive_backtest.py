"""Replay original scheduled judgments through the CLI's two scorecards."""
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import hashlib
from importlib.metadata import version
import json
import math
from pathlib import Path
import re
from uuid import uuid4
from zoneinfo import ZoneInfo

import pandas as pd

from tradingagents.atomic_io import atomic_write_json
from tradingagents.backtest import _day, _digest, _published_data, _rating, _write_outputs
from tradingagents.dataflows.integrity import safe_symbol, session_date
from tradingagents.dataflows.market_policy import aware_datetime
from tradingagents.dataflows.vendor_exceptions import VendorInputError
from tradingagents.decision_provenance import research_origin
from tradingagents.eval.decision_scores import aggregate, evaluation_sessions, score_decision, yahoo_bars
from tradingagents.scheduled.strategy_research_sources import _decision, _read

MARKETS = {"KR": ("Asia/Seoul", "069500.KS"), "US": ("America/New_York", "SPY")}
_RUN = re.compile(r"\d{8}T\d{6}_[A-Za-z0-9_-]+")
_LEGACY_GRADES = {"REDUCE": "UNDERWEIGHT", "AVOID": "NO_TRADE", "RESEARCH": "REVIEW"}
_GRADES = {"BUY", "OVERWEIGHT", "HOLD", "UNDERWEIGHT", "SELL", "NO_TRADE", "REVIEW", *_LEGACY_GRADES}


def _run_ids(root, start, end):
    # Run IDs carry the start clock. Pad for midnight, deployments and runs
    # that wrap the requested first day. The actual row clock controls inclusion.
    first, last = start - timedelta(days=7), end + timedelta(days=2)
    for folder in [root, *(root / str(year) for year in range(first.year, last.year + 1))]:
        for path in sorted(folder.iterdir()) if folder.is_dir() else ():
            if _RUN.fullmatch(path.name) and first.strftime("%Y%m%d") <= path.name[:8] <= last.strftime("%Y%m%d"):
                yield path.name, path


def _judgments(archive, start, end, cutoff):
    root = (archive / "runs").resolve()
    if not root.is_dir():
        raise ValueError("Archive has no runs directory.")
    inventory = Counter()
    sources = []
    judgments = {}
    for run_id, path in _run_ids(root, start, end):
        if "overlay" in run_id.lower():
            inventory["오버레이 실행"] += 1
            continue
        if not path.resolve().is_relative_to(root):
            inventory["아카이브 경로 검증 실패 실행"] += 1
            continue
        manifest, raw = _read(path / "run.json")
        if not manifest:
            inventory["완료 원장 없음"] += 1
            continue
        mode, _ = research_origin(manifest, {})
        if mode == "overlay_only":
            inventory["오버레이 실행"] += 1
            continue
        market = str((manifest.get("settings") or {}).get("market") or "").upper()
        if market not in MARKETS:
            inventory["시장 미확인 실행"] += 1
            continue
        started, ended = (aware_datetime(manifest.get(field)) for field in ("started_at", "finished_at"))
        if (manifest.get("run_id") != run_id or started is None or ended is None or not started <= ended <= cutoff
                or manifest.get("status") not in {"success", "partial_failure", "partial", "degraded"}):
            inventory["완료 시각·원장 미확인 실행"] += 1
            continue
        inventory["원분석·재시도 실행"] += 1
        sources.append({"run_id": run_id, "market": market, "manifest_sha256": hashlib.sha256(raw).hexdigest()})
        zone = ZoneInfo(MARKETS[market][0])
        finalization = (manifest.get("research_recovery") or {}).get("finalization_only") is True
        for row in manifest.get("tickers", []):
            if not isinstance(row, dict):
                inventory["판단 형식 결측"] += 1
                continue
            kind, _ = research_origin(manifest, row)
            if kind == "overlay_only":
                inventory["오버레이 행"] += 1
                continue
            if kind == "reused_full" or finalization:
                inventory["재시도에서 복사·재발행된 행"] += 1
                continue
            finished = aware_datetime(row.get("finished_at"))
            if finished is None:
                inventory["원판단 완료 시각 결측"] += 1
                continue
            day = finished.astimezone(zone).date()
            if not start <= day <= end or finished > cutoff:
                continue
            if row.get("status") != "success":
                inventory["판단 생성 실패 행"] += 1
                continue
            decision = _decision(row)
            began = aware_datetime(row.get("started_at"))
            try:
                reference = _day(row["trade_date"])
            except (KeyError, ValueError):
                reference = None
            if (not isinstance(decision, dict) or decision.get("rating") not in _GRADES
                    or reference is None or reference > day or began is None or not started <= began <= finished <= ended
                    or "decision_unvalidated" in (row.get("quality_flags") or [])
                    or (row.get("metrics") or {}).get("llm_fallback_calls")):
                inventory["원판단·아티팩트 검증 실패 행"] += 1
                continue
            try:
                ticker = safe_symbol(row["ticker"])
            except (KeyError, VendorInputError):
                inventory["티커 결측·형식 오류"] += 1
                continue
            if market == "KR" and re.fullmatch(r"\d{6}", ticker):
                # A bare code has no historical KOSPI/KOSDAQ qualification.
                inventory["거래소 접미사 결측 행"] += 1
                continue
            rating = decision["rating"]
            key = market, ticker, finished
            judgment = {
                "market": market, "ticker": ticker, "source": run_id, "rating": _rating(_LEGACY_GRADES.get(rating, rating)),
                "original_rating": rating, "entry_action": decision.get("entry_action"),
                "conditional_entry_action": decision.get("conditional_entry_action"),
                "decision_date": day.isoformat(), "analysis_date": row.get("analysis_date"),
                "price_reference_date": reference.isoformat(), "executed_at": finished.isoformat(),
                "original_decision_sha256": _digest(decision),
                "retry_new_judgment": bool(manifest.get("research_recovery")),
            }
            if key in judgments:
                if judgments[key] and judgment["original_decision_sha256"] == judgments[key]["original_decision_sha256"]:
                    inventory["동일 원판단 중복"] += 1
                else:
                    inventory["동일 완료 시각 판단 충돌"] += 1
                    judgments[key] = None
            else:
                judgments[key] = judgment
    rows = [judgment for _, judgment in sorted(judgments.items()) if judgment is not None]
    inventory["채택 원판단"] = len(rows)
    inventory["재시도에서 새로 완료된 원판단"] = sum(row["retry_new_judgment"] for row in rows)
    return rows, dict(inventory), sources


def _price_panel(symbol, first, last, fetch):
    try:
        frame = fetch(symbol, first, last)
    except (OSError, RuntimeError, ValueError, TypeError, KeyError) as exc:
        return {"error": type(exc).__name__}
    if not isinstance(frame, pd.DataFrame) or not {"Open", "Close"}.issubset(frame):
        return {"bars": []}
    rows = []
    for label, opening, close in zip(frame.index, frame["Open"], frame["Close"]):
        day = session_date(label)
        if pd.isna(day) or not first <= day.date().isoformat() <= last:
            continue
        prices = []
        for value in (opening, close):
            try:
                number = float(value)
                prices.append(number if math.isfinite(number) and number > 0 else None)
            except (TypeError, ValueError, OverflowError):
                prices.append(None)
        rows.append([day.date().isoformat(), *prices])
    return {"bars": rows}


def _groups(rows):
    groups = defaultdict(list)
    for row in rows:
        for market in ("전체", row["market"]):
            for month in ("전체", row["decision_date"][:7]):
                for rating in ("전체", row["rating"]):
                    groups[market, month, rating].append(row)
    return [{"market": market, "month": month, "rating": rating,
             **{key: aggregate(values, key) for key in ("direction", "new_exposure")}}
            for (market, month, rating), values in sorted(groups.items())]


def run_archive_backtest(archive, start, end, output, *, holding, fee_bps, as_of=None,
                         run_id=None, price_snapshot=None, fetch=yahoo_bars):
    start, end = _day(start), _day(end)
    now = datetime.now(timezone.utc)
    cutoff = now if as_of is None else aware_datetime(as_of)
    if cutoff is None or cutoff > now or start > end or end > cutoff.astimezone(ZoneInfo("Asia/Seoul")).date():
        raise ValueError("Use ordered dates and a non-future timezone-aware settlement cutoff.")
    if not 1 <= holding <= 100 or not math.isfinite(fee_bps) or fee_bps < 0:
        raise ValueError("Use 1–100 sessions and a finite nonnegative per-side cost.")
    run_id = run_id or f'archive-{now:%Y%m%dT%H%M%S}-{uuid4().hex[:8]}'
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", run_id):
        raise ValueError("Invalid backtest run identifier.")
    rows, inventory, sources = _judgments(Path(archive), start, end, cutoff)
    identity = {"source": "Yahoo adjusted OHLC", "first": start.isoformat(), "cutoff": cutoff.isoformat(),
                "last_by_market": {market: (cutoff.astimezone(ZoneInfo(zone)).date() - timedelta(days=1)).isoformat()
                                   for market, (zone, _) in MARKETS.items()}}
    panels = {}
    frames = {}
    if price_snapshot:
        prior = json.loads(Path(price_snapshot).read_bytes())
        if prior["identity"] != identity or prior["panels_sha256"] != _digest(prior["panels"]):
            raise ValueError("Price snapshot dates, cutoff or digest differ.")
        panels = prior["panels"]

    def prices(symbol, first, last):
        if symbol not in frames:
            if symbol not in panels:
                if price_snapshot:
                    raise KeyError("Price symbol absent from replay snapshot")
                panels[symbol] = _price_panel(symbol, identity["first"], identity["last_by_market"][market], fetch)
            panel = panels[symbol]
            if "error" in panel:
                raise RuntimeError(f'Price fetch failed: {panel["error"]}')
            frames[symbol] = pd.DataFrame(panel["bars"], columns=["Date", "Open", "Close"]).set_index("Date").astype(float)
        return frames[symbol]

    for row in rows:
        market, day = row["market"], row["decision_date"]
        _, benchmark = MARKETS[market]
        published = aware_datetime(row["executed_at"])
        slots = evaluation_sessions(market, day, holding + 1, published_at=published)
        ticker = row["ticker"].replace(".", "-") if market == "US" else row["ticker"]
        row["benchmark"], row["price_symbol"] = benchmark, ticker
        row.update(score_decision(
            ticker=ticker, market=market, decision_date=day, rating=row["rating"], benchmark=benchmark, holding=holding,
            fee_bps=fee_bps, as_of=cutoff, provider=prices, sessions=lambda *_: slots,
            exposure_allowed=row["entry_action"] in {"STARTER", "ADD"},
        ))
    manifest = {"source": "scheduled_archive", "start": start.isoformat(), "end": end.isoformat(),
                "settlement_cutoff": cutoff.isoformat(), "holding": holding, "fee_bps": fee_bps,
                "archive_inventory": inventory, "exchange_calendar_version": version("exchange-calendars"),
                "price_panels_sha256": _digest(panels), "archive_manifests_sha256": _digest(sources)}
    data = _published_data(rows, manifest) | {"archive_groups": _groups(rows)}
    root = Path(output) / "backtest" / run_id
    root.mkdir(parents=True, exist_ok=False)
    atomic_write_json(root / "archive-inputs.json", sources)
    atomic_write_json(root / "price-inputs.json", {"identity": identity, "panels": panels, "panels_sha256": _digest(panels)})
    _write_outputs(root, data)
    return root / "evaluation.json", data
