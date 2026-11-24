"""Run the fixed two-market study from point-in-time inputs through paired ledgers."""
from bisect import bisect_right
from calendar import monthrange
from collections import Counter
from datetime import date, datetime, timedelta, timezone
import json
import math
from pathlib import Path
import re
from zoneinfo import ZoneInfo

from tradingagents.atomic_io import atomic_write_bytes, atomic_write_json, interprocess_file_lock
from tradingagents.backtest import _digest
from tradingagents.calendar_access import get_exchange_calendar
from tradingagents.dataflows.market_policy import aware_datetime
from tradingagents.eval.decision_scores import daily_bar_available_at
from tradingagents.report_html import render_report_html
from tradingagents.scheduled.market_calendar import is_supplemental_market_holiday

from .quant_policy import propose_weights
from .research_comparison import compare_market_benchmarks
from .research_lean import export_tape
from .research_ledger import BENCHMARKS, CORE_WEIGHTS, INITIAL_NAV, RateHistory, actual_shares, replay
from .research_sources import FB_RENAME, KR_HOLDINGS, SEC_HOLDINGS, UNIVERSE, collect_sources

_ZONES = {"KR": "Asia/Seoul", "US": "America/New_York"}
_CALENDAR = {"KR": "XKRX", "US": "XNYS"}
_HOLDOUT = "2026-01-01"
_START = "2020-01-01"
_UNIVERSE_AT = {"US": "2019-11-30T00:00:00-05:00", "KR": "2019-10-08T00:00:00+09:00"}
_POLICY = {
    "version": "2019-index-top-five-v1", "budget_core": .70, "budget_satellite": .20, "cash_floor": .10,
    "asset_cap": .70, "trend_window": 200, "momentum_window": 126, "volatility_window": 63,
    "annual_volatility_target": .20, "maximum_stale_days": 7, "satellite_limit": 2,
    "factor_weights": {"quality": .60, "strength": .40}, "cost_version": "krw-retail-scenario-v1",
}


def research_sessions(cutoff):
    schedules = {}
    for market, name in _CALENDAR.items():
        upper = (cutoff.astimezone(ZoneInfo(_ZONES[market])).date() + timedelta(days=21)).isoformat()
        calendar = get_exchange_calendar(name, start="2016-12-01", end=upper)
        schedules[market] = {
            label.date().isoformat(): (calendar.session_open(label).to_pydatetime(),
                                       calendar.session_close(label).to_pydatetime())
            for label in calendar.sessions_in_range("2017-01-01", upper)
            if not is_supplemental_market_holiday(market=market, session_date=label.date())
        }
    return schedules


def completed_days(schedules, cutoff):
    return {market: max(day for day, (_, close) in days.items()
                        if daily_bar_available_at(market, day, close) <= cutoff)
            for market, days in schedules.items()}


def _filing_events(rows, market, sessions):
    zone = ZoneInfo(_ZONES[market])
    sessions = sorted(sessions)
    result = []
    for row in rows:
        try:
            filed = date.fromisoformat(row["filed"])
            period = date.fromisoformat(row["period_end"])
            if period > filed or (not row.get("unresolved_revision") and not math.isfinite(row["roa"])):
                continue
            accepted = aware_datetime(row.get("accepted_at"))
            if market == "US":
                if accepted is None or row.get("source") != "SEC" or accepted.astimezone(zone).date() < period:
                    continue
                filed = max(filed, accepted.astimezone(zone).date())
            elif row.get("source") != "OpenDART":
                continue
        except (KeyError, TypeError, ValueError):
            continue
        pos = bisect_right(sessions, filed.isoformat())
        if pos < len(sessions):
            result.append((sessions[pos], row))
    return result


def _profit_at(vintages, day):
    eligible = [(known, row) for known, row in vintages
                if known <= day and (date.fromisoformat(day) - date.fromisoformat(row["period_end"])).days <= 560]
    if not eligible:
        return None
    rank = max((row["period_end"], known, row.get("accepted_at", "")) for known, row in eligible)
    selected = [(known, row) for known, row in eligible if (row["period_end"], known, row.get("accepted_at", "")) == rank]
    if any(row.get("unresolved_revision") for _, row in selected) or len({row["roa"] for _, row in selected}) != 1:
        return None  # Same availability clock, conflicting filing values.
    return min(selected, key=lambda item: item[1]["id"])


def _terms(stamp, source):
    return {"known_at": stamp.isoformat(), "effective_at": stamp.isoformat(), "source": source}


def _price_terms(bars, days, market, day, currency):
    # The factor windows expect contiguous regular sessions, even across suspensions.
    dates = list(days)
    position = dates.index(day)
    required = max(_POLICY["trend_window"], _POLICY["momentum_window"] + 1, _POLICY["volatility_window"] + 1)
    sample = dates[max(0, position - required + 1):position + 1]
    if len(sample) != required or any(label not in bars for label in sample):
        return []
    value = 1.0
    result = []
    for index, label in enumerate(sample):
        bar = bars[label]
        if index:
            value *= (bar["close"] + bar["dividend"]) * bar["split"] / bars[sample[index - 1]]["close"]
        _, close = days[label]
        result.append({"effective_at": close.isoformat(),
                       "known_at": daily_bar_available_at(market, label, close).isoformat(),
                       "source": "Yahoo reconstructed total return", "price": value,
                       "basis": "total_return", "currency": currency})
    return result


def _without_unverified_revisions(vintages, receipts, market):
    """A newer correction can make the previous statement inapplicable."""
    verified = {(row["id"], row["period_end"]) for row in vintages}
    markers = []
    for receipt in receipts:
        if market == "US" and receipt.get("form") == "10-K/A":
            marker = {"id": receipt.get("accessionNumber"), "period_end": receipt.get("reportDate"),
                      "filed": receipt.get("filingDate"), "accepted_at": receipt.get("acceptanceDateTime"),
                      "source": "SEC"}
        elif market == "KR":
            label = receipt.get("report_nm", "")
            m = re.search(r"정정\]\s*사업보고서\s*\((\d{4})\.(0[1-9]|1[0-2])\)", label)
            raw = receipt.get("rcept_dt", "")
            if not m or not re.fullmatch(r"\d{8}", raw):
                continue
            year, month = map(int, m.groups())
            marker = {"id": receipt.get("rcept_no"), "period_end": date(year, month, monthrange(year, month)[1]).isoformat(),
                      "filed": f"{raw[:4]}-{raw[4:6]}-{raw[6:]}", "source": "OpenDART"}
        else:
            continue
        if marker["id"] and (marker["id"], marker["period_end"]) not in verified:
            markers.append(marker | {"unresolved_revision": True})
    return [*vintages, *markers]


def _decisions(plan, schedules, bars, vintages, receipts, end):
    actions = {arm: {} for arm in ("quant_only", "spy_hold", "kospi200_hold", "monthly_80_20")}
    decisions = []
    for market, cohort in UNIVERSE.items():
        days = schedules[market]
        currency = "USD" if market == "US" else "KRW"
        policy = dict(_POLICY, currency=currency, frozen_at=plan["recorded_at"], core=[cohort["benchmark"]],
                      satellite=list(cohort["satellites"]), minimum_turnover=1e6 if market == "US" else 1e9)
        timelines = {
            symbol: _filing_events(_without_unverified_revisions(vintages.get(symbol, []), receipts.get(symbol, []), market),
                                   market, days)
            for symbol in policy["satellite"]
        }
        past = None
        for day, (opening, _) in days.items():
            if day < _START or day > end or past is None or day[:7] == past[:7]:
                past = day
                continue
            cutoff = opening - timedelta(microseconds=1)
            history = {}
            selected = {}
            for symbol in (*policy["core"], *policy["satellite"]):
                closes = _price_terms(bars[symbol], days, market, past, currency)
                if not closes:
                    continue
                last = datetime.fromisoformat(closes[-1]["known_at"])
                if last > cutoff:
                    continue
                history[symbol] = {
                    "security": {"eligible": True, "currency": currency,
                                 **_terms(datetime.fromisoformat(_UNIVERSE_AT[market]), "2019-09-30 ETF disclosure")},
                    "closes": closes,
                    "liquidity": {"turnover": bars[symbol][past]["turnover"], **_terms(last, "Yahoo daily OHLCV")},
                }
                if symbol in timelines:
                    filing = _profit_at(timelines[symbol], past)
                    if filing is None:
                        continue
                    available, fact = filing
                    known_at = days[available][0]
                    momentum = closes[-1]["price"] / closes[-1 - policy["momentum_window"]]["price"] - 1
                    history[symbol]["factors"] = {
                        "quality": {"value": math.tanh(fact["roa"] / .08), **_terms(known_at, f'{fact["source"]}:{fact["id"]}')},
                        "strength": {"value": math.tanh(momentum / .30), **_terms(last, "Yahoo total return momentum")},
                    }
                    selected[symbol] = {"available_session": available, "known_at": known_at.isoformat(), **fact}
            proposal = propose_weights(policy, history, analysis_as_of=cutoff.isoformat(), historical_replay=True)
            key = market, day
            sleeve = CORE_WEIGHTS[market]
            actions["quant_only"][key] = {symbol: sleeve * weight for symbol, weight in proposal["quant_only"]["weights"].items()}
            actions["monthly_80_20"][key] = {BENCHMARKS[market]: sleeve}
            baseline = "spy_hold" if market == "US" else "kospi200_hold"
            if not actions[baseline]:
                actions[baseline][key] = {BENCHMARKS[market]: 1.0}
            decisions.append({"market": market, "open_session": day, "prior_session": past, "fill_eligible_at": opening.isoformat(),
                              "filings": selected, "scaled_targets": actions["quant_only"][key], **proposal})
            past = day
    return actions, sorted(decisions, key=lambda item: item["fill_eligible_at"])


def _read(path):
    return json.loads(path.read_bytes())


def _write_report(root, result):
    names = {"quant_only": "퀀트", "spy_hold": "SPY 보유", "kospi200_hold": "KODEX 200 보유", "monthly_80_20": "SPY 80% · KODEX 200 20%"}
    lines = ["# 한미 장기 퀀트 비교", "",
             f'- {result["phase"]} · 평가 승인 시각 {result["as_of"]}',
             f'- 시세 종료일 {result["actual_data_end"]}. 회계 통화 KRW, 최초 1억원, 외부 입출금 0원.',
             "- 2019년 9월 말 공개 자료의 시장별 상위 5개 종목을 고정했습니다. 80/20은 미국 80%, 한국 20%로 각 시장 첫 정규장 시가에 월별 조정합니다.",
             "- 배당은 배당락일의 원천징수 후 채권으로 기록합니다. 양도세 추정액과 미수 배당은 주문 가용 현금에서 제외합니다.",
             "- 검증 가능한 당시 LLM veto는 0건입니다. 모든 월간 목표비중은 당시 가용 입력으로 재구성한 퀀트 판단입니다.",
             "- 후향적으로 지정한 기간입니다. 2026 구간은 사후에 미사용으로 지정한 연구 내부 평가 구간입니다.",
             "- KODEX 200 원주가에는 KIS, 나머지 시세·배당·분할·USD/KRW에는 Yahoo를 사용합니다. USD/KRW는 관측일 이틀 뒤 UTC 00시부터 씁니다.",
             "- 과거 시점의 가격 빈티지와 정확한 배당 지급일은 확인되지 않았습니다.",
             "", "| 기간 | 전략 | 비용 후 수익 | 최대낙폭 | 샤프 (무위험 0) | 거래건수 | 거래비용(원) |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for label, window in result["periods"].items():
        for arm, metrics in window["arms"].items():
            costs = metrics["costs_krw"]
            trading = sum(costs[key] for key in ("commission", "slippage", "fx_cost", "sell_levy"))
            sharpe = metrics["sharpe_rf_zero"]
            lines.append(f'| {label} ({window["start"]}~{window["end"]}, {window["sessions"]}일) | {names[arm]} | '
                         f'{metrics["net_time_weighted_return"]:+.2%} | {metrics["max_drawdown"]:.2%} | '
                         f'{sharpe:.2f} | {costs["fill_count"]} | {trading:,.0f} |' if sharpe is not None else
                         f'| {label} | {names[arm]} | {metrics["net_time_weighted_return"]:+.2%} | '
                         f'{metrics["max_drawdown"]:.2%} | – | {costs["fill_count"]} | {trading:,.0f} |')
    lines.extend(["", "| 기간 | 비교 기준 | 누적 순수익 차이 | 일별 초과수익, 20일 블록 95% 구간 |",
                  "| --- | --- | --- | --- |"])
    for label, window in result["periods"].items():
        for arm, values in window["paired"].items():
            interval = values["paired_block_bootstrap_daily_95pct"]
            ci = "–" if interval is None else f"{interval[0]:+.4%} ~ {interval[1]:+.4%}"
            lines.append(f'| {label} | {names[arm]} | {values["compound_net_excess"]:+.2%}p | '
                         f'{values["mean_paired_daily_excess"]:+.4%} ({ci}) |')
    lines.extend(["", "| 종목 | 일봉 관측 / 필요 | 연간 공시 | 재무팩터 사용 가능 월 | 목표 포함 월 |",
                  "| --- | --- | --- | --- | --- |"])
    for symbol, counts in result["coverage"].items():
        lines.append(f'| {symbol} | {counts["bars"]}/{counts["expected_bars"]} | {counts["annual_accessions"]} | '
                     f'{counts["factor_months"]} | {counts["target_months"]} |')
    lines.extend(["", f'- 시세 결측 시 마지막 관측값으로 표시한 보유 세션 {sum(map(len, result["held_mark_gaps"].values()))}건',
                  f'- 공시 원본 조회 결측 {len(result["source_gaps"])}건. 시장별 상위 5개 밖의 편입·교체·상장폐지 성과는 추정 범위 밖입니다.',
                  f'- KODEX 200 가격·기업행위 대조 결과 {result["kr_benchmark_source"]}',
                  "- 매매 수수료 10bp, 슬리피지 10bp, USD 환전 10bp, 연도별 KOSPI 종목 매도세, 배당 원천징수 및 미국주식 양도세 충당금이 포함됩니다.",
                  "- 비용·세율은 가정한 한국 거주 소액 투자자의 연구 시나리오입니다. 자산종류와 연도별 레코드는 JSON과 체결 장부에 있습니다.",
                  "- 승격과 모의 운영 목표비중은 승인 대기 상태입니다.", "",
                  f"[미국 2019 보유내역]({SEC_HOLDINGS}) · [한국 2019 PDF]({KR_HOLDINGS}) · [FB 종목코드 변경 공시]({FB_RENAME})"])
    md = "\n".join(lines) + "\n"
    atomic_write_json(root / "study.json", result)
    atomic_write_bytes(root / "study.ko.md", md.encode("utf-8"))
    atomic_write_bytes(root / "study.ko.html", render_report_html(md, title="한미 장기 퀀트 비교", language="Korean").encode("utf-8"))


def run_research(root: Path, as_of, phase):
    cutoff = aware_datetime(as_of)
    if cutoff is None or cutoff > datetime.now(timezone.utc) or cutoff.date() < date(2026, 1, 1):
        raise ValueError("Use a completed, timezone-aware 2026 cutoff.")
    root.mkdir(parents=True, exist_ok=True)
    with interprocess_file_lock(root / "research.lock", timeout=0):
        plan_path = root / "research-plan.json"
        frozen = {"parameters": _POLICY, "start": _START, "holdout_start": _HOLDOUT, "initial_krw": INITIAL_NAV,
                  "market_mix": CORE_WEIGHTS, "cashflow": 0, "as_of": cutoff.isoformat(), "universe": UNIVERSE,
                  "study_folds": {"development": "2020-2022", "walk_forward": ["2023", "2024", "2025"]},
                  "trained_parameters": False, "real_time_preregistration": False, "paired_block": 20,
                  "bootstrap_resamples": 1000, "bootstrap_seed": 20261125}
        if not plan_path.exists():
            atomic_write_json(plan_path, {**frozen, "recorded_at": datetime.now(timezone.utc).isoformat()})
        plan = _read(plan_path)
        if {key: value for key, value in plan.items() if key != "recorded_at"} != frozen:
            raise ValueError("The recorded study plan differs. Use a separate output directory.")
        all_sessions = research_sessions(cutoff)
        expected_end = completed_days(all_sessions, cutoff)
        if phase == "collect":
            data = collect_sources(root / "long-inputs", cutoff, expected_end)
            return root / "long-inputs" / "market-inputs.json", {"gaps": data["gaps"]}
        data_path = root / "long-inputs" / "market-inputs.json"
        data = _read(data_path)
        if data["identity"] != {"as_of": cutoff.isoformat(), "final_days": expected_end, "universe": UNIVERSE}:
            raise ValueError("Collected inputs belong to another cutoff or universe.")
        if phase == "holdout":
            prior = _read(root / "study" / "study.json")
            if prior["plan_sha256"] != _digest(plan) or prior["phase"] != "study":
                raise ValueError("Complete the pre-holdout run with this plan first.")
        bars = {symbol: actual_shares(rows) for symbol, rows in data["prices"].items()}
        ends = {market: max(day for day in bars[benchmark] if day <= expected_end[market] and day in all_sessions[market])
                for market, benchmark in BENCHMARKS.items()}
        ends = {market: min(day, "2025-12-31") if phase == "study" else day for market, day in ends.items()}
        end = max(ends.values())
        sessions = {market: {day: clocks for day, clocks in schedule.items() if day <= ends[market]}
                    for market, schedule in all_sessions.items()}
        for market, benchmark in BENCHMARKS.items():
            gaps = [day for day in sessions[market] if _START <= day and day not in bars[benchmark]]
            if gaps:
                raise ValueError(f"Benchmark {benchmark} lacks expected sessions: {', '.join(gaps)}")
        actions, decisions = _decisions(plan, sessions, bars, data["vintages"], data["receipts"], end)
        holdings = {"quant_only": {symbol: market for market, cohort in UNIVERSE.items()
                                   for symbol in (cohort["benchmark"], *cohort["satellites"])},
                    "spy_hold": {"SPY": "US"}, "kospi200_hold": {"069500.KS": "KR"},
                    "monthly_80_20": {"SPY": "US", "069500.KS": "KR"}}
        fx = RateHistory(data["fx"])
        curves, accounts, gaps = replay(sessions, bars, fx, actions, holdings, _START, end)
        windows = {"전체": (_START, end), "초기 연구": (_START, "2022-12-31"),
                   "순차 평가": ("2023-01-01", "2025-12-31")}
        for year in range(2020, date.fromisoformat(end).year + 1):
            windows[str(year)] = f"{year}-01-01", min(end, f"{year}-12-31")
        periods = {name: compare_market_benchmarks(curves, INITIAL_NAV, start, finish, uncertainty=True)
                   for name, (start, finish) in windows.items()}
        if phase == "holdout":
            if prior["weights_sha256"] != _digest([item for item in decisions if item["open_session"] < _HOLDOUT]):
                raise ValueError("Revealing the holdout changed a pre-holdout target.")
            for year in ("2020", "2021", "2022", "2023", "2024", "2025"):
                if prior["periods"][year] != periods[year]:
                    raise ValueError("Revealing the holdout changed a pre-holdout result.")
        coverage = {}
        for market, cohort in UNIVERSE.items():
            for symbol in (cohort["benchmark"], *cohort["satellites"]):
                active = [day for day in sessions[market] if _START <= day <= ends[market]]
                rows = [decision for decision in decisions if decision["market"] == market]
                coverage[symbol] = {"bars": sum(day in bars[symbol] for day in active),
                                    "expected_bars": len(active),
                                    "annual_accessions": sum(row.get("rcept_dt", row.get("filingDate", "")).replace("-", "")
                                                             <= ends[market].replace("-", "") for row in data["receipts"].get(symbol, [])),
                                    "factor_months": sum(symbol in decision["filings"] for decision in rows),
                                    "target_months": sum(symbol in decision["scaled_targets"] for decision in rows)}
        report = {"phase": phase, "as_of": cutoff.isoformat(), "plan_sha256": _digest(plan), "actual_data_end": ends,
                  "periods": periods, "coverage": coverage, "source_gaps": data["gaps"], "held_mark_gaps": gaps,
                  "weights_sha256": _digest(decisions), "kr_benchmark_source": data.get("kr_benchmark_source", {}),
                  "decision_exclusions": dict(Counter(reason for decision in decisions
                                                      for reason in decision["rejected_evidence"].values())),
                  "veto_count": 0, "veto_evidence": "absent", "no_order_authority": True}
        output = root / phase
        output.mkdir(exist_ok=True)
        atomic_write_json(output / "weights.json", decisions)
        atomic_write_json(output / "independent-ledger.json", {
            "curves": curves, "fills": {key: account.fills for key, account in accounts.items()},
            "corporate_actions": {key: account.actions for key, account in accounts.items()},
        })
        export_tape(output / "lean-tape", sessions, bars, fx, actions, holdings, _START, end)
        _write_report(output, report)
        return output / "study.json", report
