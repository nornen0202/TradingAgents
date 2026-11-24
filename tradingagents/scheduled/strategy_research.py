"""Build dated investment plans and compare their price clauses with observed data."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from tradingagents.dataflows.market_policy import aware_datetime
from tradingagents.schemas.decision import explicit_price_range_conflicts
from tradingagents.work.investor_policy import POLICY, _research_clock_errors

from .strategy_research_prices import CURRENCIES, ZONES, KisResearchCloses, market_days, positive, price_equal, validated_quote
from .strategy_research_sources import ResearchArchive, _identity, thesis_for

_STAGE_NAMES = (
    ("intraday_pilot_rule", "장중 확인"),
    ("close_confirm_rule", "정규장 종가 확인"),
    ("next_day_followthrough_rule", "다음 거래일 확인"),
    ("failed_breakout_rule", "돌파 실패·계획 철회"),
    ("trim_rule", "보유분 위험 대응"),
)
_RISK_LEVELS = {"TRIM", "STOP_LOSS", "INVALIDATION", "EXIT"}
_NO_VOLUME_RULE = {"", "불필요", "필수 아님", "해당 없음", "없음"}


def _close_records(raw, market, days, now):
    records = {}
    for day, bar in sorted((raw or {}).items()):
        window = days.get(day)
        event = aware_datetime(bar.get("event_at"))
        observed = aware_datetime(bar.get("observed_at"))
        if (window and bar.get("kind") == "REGULAR_CLOSE" and bar.get("source") == "KIS"
                and bar.get("currency") == CURRENCIES[market] and bar.get("adjustment") == "unadjusted"
                and bar.get("session") == day.isoformat() and positive(bar.get("price"))
                and event == window[1] and observed is not None and event + timedelta(minutes=5) <= observed <= now):
            records[day] = bar
    return records


def _basis_compatible(origin, closes, days, through, now):
    """Bridge adjusted analysis levels to raw observations via the original close."""
    if not origin:
        return False
    _, source, _, _, ref, analysis_at, chart = origin
    if chart.get("ticker") != source["ticker"] or chart.get("providers") not in (["kis"], ["yfinance"]):
        return False
    anchor_bars = [bar for bar in chart.get("bars", []) if bar.get("session_id") == ref.isoformat()
                   and bar.get("interval") == "1d"]
    if len(anchor_bars) != 1 or ref not in closes or ref not in days:
        return False
    anchor = anchor_bars[0]
    ingested = aware_datetime(anchor.get("observed_at"))
    if (aware_datetime(anchor.get("timestamp")) != days[ref][1] or ingested is None
            or not days[ref][1] <= ingested <= analysis_at or not price_equal(anchor.get("close"), closes[ref]["price"])):
        return False
    for day, (_, close) in days.items():
        if ref <= day <= through and close + timedelta(minutes=5) <= now:
            bar = closes.get(day) or {}
            checked = aware_datetime(bar.get("adjustment_checked_at"))
            if not (checked and close <= checked <= now and price_equal(bar.get("price"), bar.get("adjusted_close"))):
                return False
    return True


def _threshold(level):
    values = {key: level.get(key) if positive(level.get(key)) else None for key in ("price", "low", "high")}
    low, high = values["low"], values["high"]
    if ((level.get("low") is not None or level.get("high") is not None)
            and (low is None or high is None or low > high or values["price"] is not None and not low <= values["price"] <= high)):
        return None
    role = level.get("level_type")
    point = values["price"]
    source = level.get("source_text") or ""
    if role == "BREAKOUT" and (point or high):
        return ("AT_OR_ABOVE" if "이상" in source else "ABOVE" if "초과" in source else "ABOVE_UNSPECIFIED"), point or high, None
    if role in _RISK_LEVELS and point:
        if "이하" in source:
            return "AT_OR_BELOW", point, None
        if any(term in source for term in ("미만", "아래", "하회", "이탈", "밑", "하향")):
            return "BELOW", point, None
    if role in {"PULLBACK", "SUPPORT", "RESISTANCE"} and low is not None and high is not None:
        return "IN_RANGE", low, high
    return None


def _price_result(condition, value):
    op, low, high = condition
    if op == "IN_RANGE":
        return "MET" if low <= value <= high else "NOT_MET"
    if value == low:
        return "MET" if op.startswith("AT_OR_") else "BOUNDARY" if op == "ABOVE_UNSPECIFIED" else "NOT_MET"
    return "MET" if (value > low if "ABOVE" in op else value < low) else "NOT_MET"


def _compare(level, observation, *, currency, compatible, conflict, requirement=None):
    result = {"level": level, "status": "EVIDENCE_NEEDED"}
    confirmation = level.get("confirmation")
    if conflict:
        result["needed"] = "원문 가격과 구조화 가격의 불일치 해소"
    elif level.get("currency") not in (None, currency):
        result["needed"] = "원분석 가격선과 관측 가격의 통화 일치 확인"
    elif requirement:
        result["needed"] = requirement
    elif not observation:
        result["needed"] = {
            "close": "해당 거래일의 검증된 정규장 종가",
            "next_day": "1단계 확인 직후 실제 다음 거래일의 확정 종가",
            "intraday": "해당 정규장의 시각과 공급자가 확인된 장중 가격",
            "two_bar": "원분석에 지정된 간격으로 확정된 연속 두 개의 봉",
        }.get(confirmation, "원분석에 지정된 확인 종류와 관측값")
    elif not compatible:
        result["needed"] = "원분석 기준일 가격과 비수정 시세의 대조 및 기업행위 확인"
    elif _threshold(level) is None:
        result["needed"] = "가격선의 비교 방향·범위 또는 주어진 정성 확인 기준"
    else:
        threshold = _threshold(level)
        result.update(status=_price_result(threshold, observation["price"]), observation=observation,
                      operator=threshold[0])
        if result["status"] == "BOUNDARY":
            result["needed"] = "기준값과 같음 · 원문에서 등호 포함 여부 확인"
    return result


def _price_checks(thesis, closes, quote, days, now, *, currency, compatible, active):
    levels = (thesis.get("execution_levels") or {}).get("levels") or []
    levels = [level for level in levels if isinstance(level, dict)]
    start = aware_datetime(thesis.get("analysis_asof"))
    last_close = next(reversed(closes.values()), None)
    session_quote = quote if quote and quote["kind"] != "HISTORICAL_REGULAR_QUOTE" else None
    after_analysis = {day: bar for day, bar in closes.items() if aware_datetime(bar["event_at"]) >= start}
    deadline = aware_datetime(thesis.get("conditional_entry_valid_until"))
    eligible_closes = {day: bar for day, bar in after_analysis.items()
                       if deadline is None or aware_datetime(bar["event_at"]) <= deadline}
    primary = [level for level in levels if level.get("level_type") == "BREAKOUT"
               and level.get("confirmation") == "close" and _threshold(level)
               and not explicit_price_range_conflicts({"execution_levels": {"levels": [level]}})]
    results = []
    for index, level in enumerate(levels):
        stage = level.get("confirmation")
        conflict = bool(explicit_price_range_conflicts({"execution_levels": {"levels": [level]}}))
        observation = (session_quote if stage == "intraday" else
                       last_close if stage == "close" and level.get("level_type") in _RISK_LEVELS else
                       next(reversed(eligible_closes.values()), None) if stage == "close" else None)
        needed, next_day, first = None, None, None
        dependent_exit = (level.get("level_type") in _RISK_LEVELS and (
            level.get("reason_code") == "FAILED_BREAKOUT" or any(
                token in f"{level.get('label', '')} {level.get('source_text', '')}"
                for token in ("돌파 후", "돌파 뒤", "돌파 이후", "돌파 확인 뒤", "돌파가 확인된 뒤")
            )))
        if dependent_exit:
            needed = "대상이 되는 전술 편입과 선행 돌파의 정규장 종가를 확인한 뒤 이후 재마감 가격 확인"
        if stage == "next_day":
            preceding = [item for item in primary if item.get("confirmation_group") == level.get("confirmation_group")]
            # A numbered date and observation establish a possible next session.
            # Other clauses (e.g. volume, holding above support) retain original wording.
            if len(preceding) == 1 and compatible and active and preceding[0].get("currency") in (None, currency):
                first = next((day for day, bar in eligible_closes.items()
                              if _price_result(_threshold(preceding[0]), bar["price"]) == "MET"), None)
                if first is not None:
                    next_day = next((day for day in sorted(days) if day > first), None)
                    observation = eligible_closes.get(next_day)
            if not observation:
                needed = (f"{next_day.isoformat()} 정규장 확정 종가와 선행 조건 확인" if next_day else
                          "먼저 같은 조건의 돌파·회복 종가와 거래량 등 선행 조건 확인")
        checked = _compare(level, observation, currency=currency, compatible=compatible, conflict=conflict, requirement=needed)
        threshold = _threshold(level)
        if (stage == "close" and not dependent_exit and not observation and session_quote and threshold and compatible
                and not conflict and level.get("currency") in (None, currency)):
            checked["intraday_reference"] = {"observation": session_quote,
                                              "status": _price_result(threshold, session_quote["price"])}
        volume = str(level.get("volume_rule") or "").strip().rstrip(".")
        if volume not in _NO_VOLUME_RULE:
            checked["remaining_volume_rule"] = volume
        if stage == "close" and observation is None:
            next_close = next((day for day, (_, close) in days.items() if close >= max(now, start)), None)
            if next_close:
                checked["needed_session"] = next_close.isoformat()
        if next_day:
            checked["needed_session"] = next_day.isoformat()
        if first:
            checked["preceding_price_session"] = first.isoformat()
        checked.update(order=index + 1, group=level.get("confirmation_group"))
        results.append(checked)
    return results


def _entry_summary(thesis):
    signal = thesis.get("conditional_entry_action")
    initial = thesis.get("entry_action")
    if signal in {"STARTER", "ADD"} or initial in {"STARTER", "ADD"}:
        return "가격·후속 조건 충족 시 소액 신규 편입 검토" if "STARTER" in (signal, initial) else "가격·후속 조건 충족 시 추가 편입 검토"
    stance = thesis.get("stance")
    return {
        "BUY": "편입 후보 · 원분석 진입 조건 확인",
        "HOLD": "신규 편입 계획 없음 · 기존 논지 관찰",
        "REDUCE": "신규 편입 보류 · 회복 조건부터 확인",
        "SELL": "신규 편입 보류 · 계획 철회 또는 보유 축소 검토",
        "AVOID": "신규 편입 제외 · 회복 근거 재평가",
    }.get(stance, "가격·공시 자료 확보 후 재분석")


def _plan(row, thesis, origin, lineage, archive, quote, loader, now, base_days, observation_clock):
    market = archive.market
    start = aware_datetime(thesis.get("analysis_asof"))
    if _research_clock_errors(thesis, market=market, now=now):
        return {"status": "DATA_NEEDED", "headline": "판단 근거 확인 필요",
                "missing": ["원분석 완료 시각·가격 기준일 및 검증 가능한 종목별 판단"], "execution_authorized": False}
    local = now.astimezone(ZONES[market]).date()
    reference = origin[4] if origin else local - timedelta(days=10)
    until = aware_datetime(thesis.get("conditional_entry_valid_until"))
    malformed_deadline = bool(thesis.get("conditional_entry_valid_until")) and until is None
    through = max(local + timedelta(days=10), min(until.astimezone(ZONES[market]).date(), local + timedelta(days=60))) if until else local + timedelta(days=10)
    days = base_days if reference >= local - timedelta(days=10) and through == local + timedelta(days=10) else market_days(
        market, now, start=max(reference, local - timedelta(days=45)), through=through)
    quote = validated_quote(quote, market, days, now)
    raw = {}
    if loader and days:
        try:
            raw = loader(market, _identity(row["ticker"]), days, max(reference, local - timedelta(days=45)), now,
                         (quote or {}).get("exchange"))
        except (OSError, RuntimeError, ValueError):
            pass
    observed_by = observation_clock() if observation_clock else now
    closes = _close_records(raw, market, days, observed_by)
    latest_close = next(reversed(closes.values()), None)
    expected_close = max((day for day, (_, close) in days.items() if close + timedelta(minutes=5) <= now), default=None)
    latest_is_current = bool(latest_close and expected_close and latest_close["session"] == expected_close.isoformat())
    current_quote = quote if quote and quote["kind"] != "HISTORICAL_REGULAR_QUOTE" else None
    current = current_quote or (latest_close if latest_is_current else None)
    historical = None if current else (latest_close or quote)
    comparable_closes = closes if latest_is_current else {}
    if latest_is_current:
        view_close = {key: value for key, value in latest_close.items() if key != "adjusted_close"}
    else:
        view_close = None
    basis = bool(current and _basis_compatible(origin, closes, days, date.fromisoformat(current["session"]), observed_by))
    review = start + timedelta(days=POLICY["review_calendar_days"].get(thesis.get("horizon"), 7))
    expired = until is not None and now >= until
    checks = _price_checks(thesis, comparable_closes, quote, days, now, currency=CURRENCIES[market],
                           compatible=basis, active=not expired and not malformed_deadline)
    proof = thesis.get("source_coverage") or {}
    held = row.get("is_held") is True or row.get("universe_role") == "HOLDING"
    missing = []
    if not days:
        missing.append("거래소의 정규장·휴장 일정 확인")
    if not current:
        missing.append(f"{expected_close.isoformat()} 정규장 확정 종가 확인" if expected_close else "직전 완료 정규장의 확정 종가 확인")
    elif not basis:
        missing.append("원분석 기준일 종가와 관측 통화·수정 여부 대조 및 기업행위 확인")
    if (proof.get("get_disclosures") or {}).get("status") not in {"OBSERVED", "VERIFIED_ZERO"}:
        missing.append("원문 공시·발행사 발표와 게시 또는 접수 시각 확인")
    if malformed_deadline:
        missing.append("원래 조건부 신호의 시간대가 있는 만료 시각 확인")
    if not thesis.get("entry_conditions") or not thesis.get("invalidation_conditions"):
        missing.append("원분석 진입·무효화 조건 확인")
    if thesis.get("conditional_entry_action") in {"STARTER", "ADD"} and not until:
        missing.append("원래 조건부 신호의 만료 시각 확인")
    comparison_count = sum(check["status"] in {"MET", "NOT_MET", "BOUNDARY"} for check in checks)
    ordered_rules = [{"label": label, "text": (thesis.get("execution_levels") or {}).get(key)}
                     for key, label in _STAGE_NAMES if (thesis.get("execution_levels") or {}).get(key)]
    return {
        "status": "DATED_PLAN", "headline": _entry_summary(thesis), "thesis": thesis, "lineage": lineage,
        "holder_summary": ("보유분 감축·철회 조건 확인" if thesis.get("stance") in {"REDUCE", "SELL"}
                           or thesis.get("risk_action") in {"REDUCE_RISK", "STOP_LOSS", "EXIT", "TAKE_PROFIT", "TRIM_TO_FUND"}
                           else "보유 논지 유지 여부와 하방 기준 확인") if held else "현재 보고서에 보유 확인 없음 · 보유분 대응은 해당 보유자 기준",
        "ordered_rules": ordered_rules, "price_checks": checks, "observation": current, "completed_close": view_close,
        "last_observation": historical, "compared_price_count": comparison_count, "price_basis_verified": basis,
        "missing": missing, "review_by": review.isoformat(), "review_due": now >= review,
        "source_valid_until": thesis.get("conditional_entry_valid_until"), "source_expired": expired,
        "remaining_trading_days": (sum(now < close <= until for _, close in days.values())
                                   if until and days and until.astimezone(ZONES[market]).date() <= through else None),
        "evaluated_at": observed_by.isoformat(), "execution_authorized": False,
    }


def attach_research_plans(archive_dir, market_payload, *, now, refresh_prices=False, price_loader=None):
    market = market_payload["market"]
    if market not in ZONES or not market_payload["rows"]:
        return
    archive = ResearchArchive(archive_dir, market, now)
    selected = archive.latest(row["ticker"] for row in market_payload["rows"])
    quotes = archive.quotes(market_payload)
    days = market_days(market, now)
    observation_clock = None
    if refresh_prices and price_loader is None:
        price_loader = KisResearchCloses.configured()
        observation_clock = lambda: datetime.now(timezone.utc)
    for row in market_payload["rows"]:
        key = _identity(row["ticker"])
        attempt, origin = selected.get(key, (None, None))
        thesis = thesis_for(origin) if origin else row.get("thesis") or {}
        lineage = {"status": ("REUSED_FULL" if origin and attempt != origin[0] else
                              "FULL" if origin else "DATED_ARCHIVE_REFERENCE"),
                   "attempt_run_id": attempt, "origin_run_id": origin[0] if origin else thesis.get("analysis_run_id")}
        row["research_plan"] = _plan(row, thesis, origin, lineage, archive, quotes.get(key), price_loader, now, days,
                                     observation_clock)
