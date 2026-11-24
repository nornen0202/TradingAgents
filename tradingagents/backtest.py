"""Evaluate independent stock decisions in a resumable, private backtest run."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from importlib.metadata import version
import hashlib
import json
import math
from pathlib import Path
import re
from uuid import uuid4
from zoneinfo import ZoneInfo

from tradingagents.agents.utils.instrument_resolver import resolve_instrument
from tradingagents.atomic_io import atomic_write_bytes, atomic_write_json, interprocess_file_lock
from tradingagents.dataflows.config import run_config
from tradingagents.dataflows.integrity import safe_symbol
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.eval.decision_scores import SCHEMA, TERMINAL_SCORES, aggregate, score_decision, settlement_complete
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.portfolio.context import normalize_portfolio

ANALYSTS = ("market", "social", "news", "fundamentals")
_UPSTREAM_LOG = "tradingagents.upstream-memory-log/v1"
_COMPAT_DIRECTIONS = {"Buy": 1, "Overweight": 1, "Underweight": -1, "Sell": -1}
_COMPAT_DEFAULT_WINDOW = "the configured window"
_UPSTREAM_REVIEW = "REVIEW"
_UPSTREAM_RATINGS = {*_COMPAT_DIRECTIONS, "Hold", _UPSTREAM_REVIEW}
_RATING = {"매수": "BUY", "비중확대": "OVERWEIGHT", "비중 확대": "OVERWEIGHT", "보유": "HOLD",
           "비중축소": "UNDERWEIGHT", "비중 축소": "UNDERWEIGHT", "매도": "SELL", "검토": "REVIEW"}
_KO = {code: name for name, code in _RATING.items()}
_REPORT_KEYS = {"company_of_interest", "instrument_profile", "input_instrument", "trade_date", "analysis_date",
    "market_report", "sentiment_report", "news_report", "fundamentals_report", "investment_debate_state",
    "trader_investment_plan", "risk_debate_state", "investment_plan", "final_trade_decision", "decision_artifact_id"}
_STATUS = {"PENDING": "미성숙", "SCORED": "채점", "REVIEW": "검토 보류", "NO_DIRECTION": "방향 제외",
    "NO_NEW_EXPOSURE": "신규 노출 없음", "ASSET_PRICE_MISSING": "종목 가격 결측",
    "BENCHMARK_PRICE_MISSING": "벤치마크 가격 결측", "ASSET_PROVIDER_FAILURE": "종목 공급자 오류",
    "BENCHMARK_PROVIDER_FAILURE": "벤치마크 공급자 오류", "DECISION_FAILURE": "판단 생성 실패",
    "SETTLEMENT_FAILURE": "결과 대사 오류", "AVAILABLE": "대조 가능"}


@dataclass
class BacktestResult:
    run_id: str
    log_path: Path
    cells_run: int = 0
    skipped: int = 0
    failures: list = field(default_factory=list)
    settlement_failures: list = field(default_factory=list)


@dataclass
class RatingScore:
    count: int
    hit_rate: float | None
    mean_alpha: float | None


@dataclass
class BacktestSummary:
    resolved: int
    pending: int
    by_rating: dict[str, RatingScore]
    unscored: int = 0
    holding: str = ""
    data: dict = field(default_factory=dict)

    def render(self):
        if self.data.get("schema") == _UPSTREAM_LOG:
            lines = ["# 보존된 원본 백테스트", f"정산 / 대기 / 보류: {self.resolved} / {self.pending} / {self.unscored}"]
            for rating, score in self.by_rating.items():
                hit = "방향 제외" if score.hit_rate is None else f"{score.hit_rate:.1%}"
                lines.append(f"- {rating}: {score.count}건, 방향 {hit}, 시장 대비 평균 {score.mean_alpha:+.2%}")
            lines.append(f"정산 기록의 기간: {self.holding}")
            return "\n".join(lines) + "\n"
        if self.data.get("schema") != SCHEMA:
            return "이전 저장 결과 · 원자료 확인이 필요한 성과입니다."
        return render_summary(self.data)


def _day(text):
    try:
        value = date.fromisoformat(text)
    except (TypeError, ValueError) as exc:
        raise ValueError("Use YYYY-MM-DD dates.") from exc
    if value.isoformat() != text:
        raise ValueError("Use YYYY-MM-DD dates.")
    return value


def iter_grid(start_date, end_date, every_n_days=1):
    start, end = _day(start_date), _day(end_date)
    if every_n_days < 1 or end < start:
        raise ValueError("Check the positive date interval and ordered bounds.")
    end = min(date.today(), end)
    return [(start + timedelta(days=i)).isoformat() for i in range(0, (end - start).days + 1, every_n_days)]


def _read(path):
    return json.loads(path.read_bytes())


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str, allow_nan=False).encode()).hexdigest()


def _sessions_and_instruments(tickers, dates, config):
    with run_config(config):
        profiles = {}
        for ticker in tickers:
            profile = resolve_instrument(ticker)
            if profile.country not in {"KR", "US"}:
                raise ValueError("Backtest requires an exchange-supported US or KR stock.")
            profiles[profile.primary_symbol] = profile
    return profiles, sorted({ _day(value).isoformat() for value in dates })


def _safe_report(path, state, config, analysts):
    from tradingagents.reporting import save_report_bundle
    return save_report_bundle(state, state["company_of_interest"], path,
                              language=config.get("output_language", "Korean"),
                              settings={**config, "analysts": analysts})


def _rating(value):
    text = str(value).strip()
    grade = _RATING.get(text, text.upper())
    return grade if grade in {
        "BUY", "OVERWEIGHT", "HOLD", "UNDERWEIGHT", "SELL", "NO_TRADE", "REVIEW"} else "REVIEW"


def _not_scored(status):
    return {name: {"status": status} for name in ("direction", "new_exposure")}


def _failed_settlement(previous):
    failed = _not_scored("SETTLEMENT_FAILURE")
    for name, score in previous.items():
        if score["status"] not in TERMINAL_SCORES:
            failed[name] = {**score, "status": "SETTLEMENT_FAILURE"}
        elif name == "new_exposure" and score["status"] == "SCORED" and score.get("benchmark_status") != "AVAILABLE":
            failed[name] = {**score, "benchmark_status": "SETTLEMENT_FAILURE"}
        else:
            failed[name] = score
    return failed


def _published_data(rows, manifest):
    directions = aggregate(rows, "direction")
    exposures = aggregate(rows, "new_exposure")
    by_rating = {}
    for grade in sorted({row["rating"] for row in rows if row["rating"]}):
        same = [row for row in rows if row["rating"] == grade]
        recorded = [row["direction"]["alpha"] for row in same if "alpha" in row["direction"]]
        by_rating[grade] = {"direction": aggregate(same, "direction"),
                            "new_exposure": aggregate(same, "new_exposure"),
                            "mean_alpha": sum(recorded) / len(recorded) if recorded else None}
    return {"schema": SCHEMA, "manifest": manifest, "records": rows, "direction": directions,
            "new_exposure": exposures, "by_rating": by_rating,
            "metrics": {"hit_rate": exposures["hit_rate"], "active_count": exposures["scored"],
                        "sample_count": exposures["scored"] + exposures["statuses"].get("NO_NEW_EXPOSURE", 0),
                        "excluded_count": len(rows) - exposures["scored"] - exposures["statuses"].get("NO_NEW_EXPOSURE", 0)}}


def _fraction(value):
    rate = "해당 없음" if value["hit_rate"] is None else f'{value["hit_rate"]:.1%}'
    return f'{value["hits"]}/{value["scored"]} ({rate})'


def _reasons(value):
    items = [f"{_STATUS.get(code, code)} {count}" for code, count in value["statuses"].items() if code != "SCORED"]
    items += [f"{_STATUS.get(code, code)} {count}" for code, count in value["benchmark_statuses_for_scored"].items()
              if code != "AVAILABLE"]
    return ", ".join(items) or "없음"


def _upstream_alpha(text):
    try:
        value = float(text.strip().rstrip("%")) / 100
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def _upstream_log_outcomes(raw):
    """Read only complete records written in the upstream memory-log format."""
    try:
        text = raw.decode("utf-8").replace("\r\n", "\n")
    except UnicodeDecodeError:
        return None
    blocks = text.split("\n\n<!-- ENTRY_END -->\n\n")
    if len(blocks) < 2 or blocks[-1].strip():
        return None
    outcomes = []
    for block in blocks[:-1]:
        tag, _, body = block.strip().partition("\n")
        if not (tag.startswith("[") and tag.endswith("]") and body.lstrip("\n").partition("\n")[0] == "DECISION:"):
            return None
        fields = [field.strip() for field in tag[1:-1].split("|")]
        if len(fields) not in {4, 6, 7}:
            return None
        day, ticker, rating, outcome = fields[:4]
        try:
            _day(day)
            if len(fields) == 7:
                marker, _, known_on = fields[6].partition(":")
                if marker != "resolved" or _day(known_on) < _day(day):
                    return None
        except ValueError:
            return None
        if rating not in _UPSTREAM_RATINGS or not re.fullmatch(r"[A-Za-z0-9^][A-Za-z0-9.^=/_-]{0,39}", ticker):
            return None
        pending = outcome == "pending"
        if pending != (len(fields) == 4):
            return None
        alpha = None if pending else _upstream_alpha(fields[4])
        holding = None if pending else fields[5]
        outcomes.append((rating, alpha, holding))
    return outcomes


def _compat_summary(outcomes, data):
    resolved = {}
    pending = unscored = 0
    windows = set()
    for rating, alpha, holding in outcomes:
        if rating == _UPSTREAM_REVIEW:
            unscored += 1
        elif alpha is None:
            pending += 1
        else:
            resolved.setdefault(rating.title(), []).append(alpha)
            if holding and holding.endswith("d"):
                windows.add(f"{holding[:-1]} trading days")
    by_rating = {}
    for rating, alphas in resolved.items():
        direction = _COMPAT_DIRECTIONS.get(rating)
        count = len(alphas)
        hits = sum(alpha * direction > 0 for alpha in alphas) if direction else None
        by_rating[rating] = RatingScore(count, hits / count if hits is not None else None, sum(alphas) / count)
    return BacktestSummary(sum(map(len, resolved.values())), pending, by_rating, unscored,
                           ", ".join(sorted(windows)) or _COMPAT_DEFAULT_WINDOW, data)


def _summarize_evaluation(data):
    window = f'{data["manifest"]["holding"]}d'
    # Upstream compatibility counts only stored decisions. Grid failures without a
    # judgment still appear in the scorecards' target count and failure reasons.
    outcomes = ((row["rating"], row["direction"].get("alpha"), window) for row in data["records"] if row["rating"])
    return _compat_summary(outcomes, data)


def render_summary(data):
    doc = data["manifest"]
    holding, fee = doc["holding"], doc["fee_bps"]
    d, n = data["direction"], data["new_exposure"]
    compat = _summarize_evaluation(data)
    lines = ["# 판단 성과 비교", "", "| 관점 | 적중 / 채점 | 평가 대상 | 보류·제외·비교 결측 |",
             "| --- | --- | --- | --- |", f'| 시장 대비 방향 | {_fraction(d)} | {d["target"]} | {_reasons(d)} |',
             f'| 신규 현금 노출 | {_fraction(n)} | {n["target"]} | {_reasons(n)} |', "",
             "| 등급 | 시장 대비 방향 적중 / 채점 | 신규 노출 순이익 / 채점 | 시장 대비 평균 |",
             "| --- | --- | --- | --- |"]
    for grade, score in data["by_rating"].items():
        alpha = "해당 없음" if score["mean_alpha"] is None else f'{score["mean_alpha"]:+.2%}'
        lines.append(f'| {_KO.get(grade, grade)} ({grade}) | {_fraction(score["direction"])} | '
                     f'{_fraction(score["new_exposure"])} | {alpha} |')
    if doc.get("source") == "scheduled_archive":
        inventory = doc["archive_inventory"]
        lines.extend([
            "", f'- 판단 완료일 범위 {doc["start"]} ~ {doc["end"]}, 정산 마감 {doc["settlement_cutoff"]}',
            '- 판단 완료 시각보다 늦은 첫 정규장 시가를 기준으로 세션을 선택합니다. 거래일은 시장 현지 날짜입니다.',
            '- 신규 노출은 BUY/OVERWEIGHT 등급과 STARTER/ADD 신규 진입 판단이 모두 기록된 행에 적용합니다.',
            '- 신규 노출 적중은 비용 차감 후 수익이 양수인 비율입니다. 상대수익은 비교 가격이 있는 행에서 산출합니다.',
            f"- 아카이브 조회 집계 {', '.join(f'{key} {count:,}건' for key, count in sorted(inventory.items()))}",
            "", "| 시장 / 판단월 / 등급 | 대상 | 방향 적중 / 채점 | 방향 보류·결측 | 신규 노출 적중 / 채점 | 신규 노출 보류·결측 | 방향 상대수익 | 신규 평균 순수익 | 신규 평균 거래비용 | 신규 평균 상대수익 |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ])
        for group in data["archive_groups"]:
            direction, exposure = group["direction"], group["new_exposure"]

            def mean(score, field):
                value = score["means"].get(field)
                return "–" if value is None else f'{value:+.2%} (n={score["mean_denominators"][field]})'

            lines.append(
                f'| {group["market"]} / {group["month"]} / {group["rating"]} | {direction["target"]} | '
                f'{_fraction(direction)} | {_reasons(direction)} | {_fraction(exposure)} | {_reasons(exposure)} | '
                f'{mean(direction, "alpha")} | {mean(exposure, "strategy_return")} | '
                f'{mean(exposure, "transaction_cost")} | {mean(exposure, "excess_return")} |'
            )
    lines.extend(["", f"- 판단 정산 / 대기 / 보류 (원본 집계): {compat.resolved} / {compat.pending} / {compat.unscored}",
                  f'- 시장 대비 방향은 첫 적격 세션 종가부터 {holding}거래일 후 종가까지 비교합니다. '
                  '상대수익을 0.1%p 단위로 기록해 등급 방향을 평가합니다.',
                  f'- 신규 현금 노출은 다음 세션 시가부터 제{holding}세션 종가까지 평가합니다. '
                  f'BUY 100%, OVERWEIGHT 50%를 반영하며 편도 비용은 {fee:g}bp입니다.',
                  '- 벤치마크는 같은 시장의 정확한 거래일을 사용합니다. 시각을 확인할 수 없는 과거 가격 빈티지, '
                  '세금, 실제 체결과 시장충격은 이 표의 검증 범위에서 제외합니다.', "",
                  "| 종목 / 벤치마크 | 판단일 / 실행시각 | 원판단·출처 | 방향 세션 / 상대수익 | 신규노출 세션 / 순수익 |",
                  "| --- | --- | --- | --- | --- |"])
    for row in data["records"]:
        def period(key):
            score = row[key]
            reason = _STATUS.get(score["status"], score["status"])
            value = score.get("alpha") if key == "direction" else score.get("strategy_return")
            shown = reason if value is None else f"{value:+.2%}"
            return f'{score.get("entry_session", "–")} → {score.get("exit_session", "–")} ({shown})'
        provenance = {"ANALYZED": " · 신규 분석", "REUSED": " · 기존 판단 재사용"}.get(row.get("progress_source"), "")
        lines.append(f'| {row["ticker"]} / {row.get("benchmark", "–")} | {row["decision_date"]} / {row["executed_at"] or "–"} | '
                     f'{row["rating"] or "–"} · {row["source"]}{provenance} | {period("direction")} | {period("new_exposure")} |')
    return "\n".join(lines) + "\n"


def _write_outputs(root, data):
    from tradingagents.report_html import render_report_html
    atomic_write_json(root / "evaluation.json", data)
    markdown = render_summary(data)
    atomic_write_bytes(root / "evaluation.ko.md", markdown.encode("utf-8"))
    html = render_report_html(markdown, title="판단 성과 비교", language="Korean")
    atomic_write_bytes(root / "evaluation.ko.html", html.encode("utf-8"))


def run_backtest(tickers, dates, config, asset_type="stock", portfolio=None, selected_analysts=ANALYSTS,
                 run_id=None, progress=None, *, holding_period=None, benchmark_symbol=None,
                 transaction_cost_bps=10.0, as_of=None, provider=None):
    if asset_type != "stock":
        raise ValueError("This fork has only the stock graph; asset_type must be 'stock'.")
    config = {**DEFAULT_CONFIG, **config}
    holding = config.get("holding_period_days", 5) if holding_period is None else holding_period
    if type(holding) is not int or not 1 <= holding <= 100 or not math.isfinite(transaction_cost_bps) or transaction_cost_bps < 0:
        raise ValueError("Use 1–100 sessions and a finite nonnegative per-side cost.")
    cutoff = as_of or datetime.now(timezone.utc)
    if cutoff.tzinfo is None or cutoff.utcoffset() is None:
        raise ValueError("Settlement cutoff must be timezone-aware.")
    analysts = list(selected_analysts)
    profiles, days = _sessions_and_instruments(tickers, dates, config)
    if not profiles or not days:
        raise ValueError("The backtest needs at least one ticker and date.")
    if any(_day(days[-1]) > cutoff.astimezone(ZoneInfo(profile.timezone)).date() for profile in profiles.values()):
        raise ValueError("Backtest cannot analyze a future exchange-local date.")
    benchmark = config.get("benchmark_ticker") if benchmark_symbol is None else benchmark_symbol
    bench = {}
    with run_config(config):
        benchmark_profile = resolve_instrument(benchmark) if benchmark is not None else None
        for ticker, profile in profiles.items():
            if benchmark_profile and benchmark_profile.country != profile.country:
                raise ValueError("An explicit benchmark must belong to the stock's exchange market.")
            if benchmark_profile:
                bench[ticker] = safe_symbol(benchmark_profile.yahoo_symbol or benchmark_profile.primary_symbol)
            else:
                bench[ticker] = "069500.KS" if profile.country == "KR" else "SPY"
        scope = normalize_portfolio(portfolio)
    identity = {"schema": SCHEMA, "inputs": sorted(profiles), "dates": days, "holding": holding,
                "benchmark": bench, "fee_bps": transaction_cost_bps, "asset_type": asset_type,
                "exchange_calendar_version": version("exchange-calendars"),
                "graph_and_portfolio_sha256": _digest([config, analysts, scope]),
                "price_source": "adjusted_daily_history"}
    if run_id is None:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid4().hex[:10]
    if not isinstance(run_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", run_id):
        raise ValueError("Invalid backtest run identifier.")
    root = (Path(config["results_dir"]) / "backtest").resolve() / run_id
    root.mkdir(parents=True, exist_ok=True)
    if root.resolve() != root:
        raise ValueError("Backtest run directory must be private and direct.")
    result = BacktestResult(run_id, root / "evaluation.json")
    rows = []
    graph = None
    with interprocess_file_lock(root / "run.lock", timeout=0):
        meta = root / "run.json"
        if meta.exists() and _read(meta) != identity:
            raise ValueError("Parameters differ from the existing run. Choose another run_id.")
        if not meta.exists():
            atomic_write_json(meta, identity)
        clock_path = root / "settlement-clock.json"
        if clock_path.exists() and cutoff < datetime.fromisoformat(_read(clock_path)["cutoff"]):
            raise ValueError("Settlement cutoff regressed. Use a separate run.")
        atomic_write_json(clock_path, {"cutoff": cutoff.isoformat()})
        private_config = {**config, "results_dir": str(root / "graph"), "data_cache_dir": str(root / "cache"),
                          "point_in_time_strict": True, "memory_dir": None, "checkpoint_enabled": False}
        try:
            cells = [(ticker, day) for day in days for ticker in profiles]
            for index, (ticker, day) in enumerate(cells, 1):
                profile = profiles[ticker]
                cell = root / "cells" / safe_symbol(ticker) / day
                decision_file = cell / "decision.json"
                scores = cell / "scores.json"
                attempt = cell / "attempts" / uuid4().hex[:12]
                if decision_file.exists():
                    recorded = _read(decision_file)
                    result.skipped += 1
                    progress_source = "REUSED"
                else:
                    progress_source = "ANALYZED"
                    if progress:
                        progress(index, len(cells), ticker, day)
                    try:
                        if graph is None:
                            graph = TradingAgentsGraph(config=private_config, selected_analysts=analysts)
                        if scope is None:
                            state, signal = graph.propagate(ticker, day)
                        else:
                            state, signal = graph.propagate(ticker, day, portfolio=scope)
                        if state.get("company_of_interest") != ticker or state.get("trade_date") != day:
                            raise ValueError("Decision identity differs from the task.")
                        recorded = {"rating": _rating(signal), "executed_at": datetime.now(timezone.utc).isoformat(),
                                    "state": {key: state[key] for key in _REPORT_KEYS if key in state}}
                        atomic_write_json(decision_file, recorded)
                        result.cells_run += 1
                    except Exception as exc:
                        error = type(exc).__name__
                        atomic_write_json(attempt / "error.json", {"stage": "decision", "error_type": error})
                        result.failures.append((ticker, day, error))
                        rows.append({"ticker": ticker, "decision_date": day, "executed_at": None, "rating": None,
                                     "source": "FULL_FAILED", **_not_scored("DECISION_FAILURE")})
                        continue
                if not (cell / "report-ready.json").exists():
                    try:
                        report = _safe_report(attempt / "reports", recorded["state"], config, analysts)
                        atomic_write_json(cell / "report-ready.json", {"path": str(report.relative_to(cell))})
                    except Exception as exc:
                        atomic_write_json(attempt / "report-error.json", {"error_type": type(exc).__name__})
                        result.settlement_failures.append((ticker, f"{day}: report {type(exc).__name__}"))
                prior = _read(scores) if scores.exists() else {}
                if settlement_complete(prior):
                    measured = prior
                else:
                    try:
                        measured = score_decision(ticker=profile.yahoo_symbol or ticker, market=profile.country,
                            decision_date=day, rating=recorded["rating"], benchmark=bench[ticker], holding=holding,
                            fee_bps=transaction_cost_bps, as_of=cutoff, previous=prior,
                            **({"provider": provider} if provider else {}))
                    except Exception as exc:
                        atomic_write_json(attempt / "settlement-error.json", {"error_type": type(exc).__name__})
                        measured = _failed_settlement(prior)
                    atomic_write_json(attempt / "settlement.json", {"cutoff": cutoff.isoformat(), "scores": measured})
                    atomic_write_json(scores, measured)
                for name, score in measured.items():
                    for key in ("status", "benchmark_status"):
                        status = score.get(key, "")
                        if status.endswith("FAILURE"):
                            result.settlement_failures.append((ticker, f"{day}: {name} {status}"))
                rows.append({"ticker": ticker, "decision_date": day, "executed_at": recorded["executed_at"],
                             "rating": recorded["rating"], "source": "FULL", "progress_source": progress_source,
                             "benchmark": bench[ticker], **measured})
        finally:
            if graph is not None:
                graph.close()
        _write_outputs(root, _published_data(rows, identity))
    return result


def summarize(source: BacktestResult | str | Path) -> BacktestSummary:
    """Summarize a fork evaluation or a preserved upstream memory log."""
    is_result = isinstance(source, BacktestResult)
    path = source.log_path if is_result else Path(source)
    if path.is_dir():
        path = path / "evaluation.json"
    if not path.is_file():
        if is_result:
            return _compat_summary((), {"schema": _UPSTREAM_LOG})
        raise FileNotFoundError(path)
    raw = path.read_bytes()
    try:
        data = json.loads(raw)
    except (UnicodeError, json.JSONDecodeError):
        outcomes = _upstream_log_outcomes(raw)
        if outcomes is not None:
            return _compat_summary(outcomes, {"schema": _UPSTREAM_LOG})
        data = {"schema": "legacy/unverified"}
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        return BacktestSummary(0, 0, {}, holding=_COMPAT_DEFAULT_WINDOW, data=data if isinstance(data, dict) else {})
    return _summarize_evaluation(data)
