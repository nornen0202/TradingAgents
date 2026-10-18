"""Bounded Korean/English condition drafts compiled to the existing safe DSL.

This is an intentionally explicit grammar, not an LLM or generated Python. A
draft is usable only when the *entire* request is understood. Vague thresholds,
unsupported indicators, periods and unit conflicts require clarification. The
caller must show the normalized rules before saving/using the resulting DSL.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
from typing import Any

from .conditions import NUMERIC_FIELDS, TEXT_FIELDS, validate_condition


COMPILER_VERSION = "explicit-condition-v1"
SUPPORTED_EXAMPLES = [
    "거래대금 100억원 이상 그리고 전일 대비 거래량 1.5배 이상 그리고 거래정지 제외",
    "(daily change >= 3% or gap >= 2%) and not halted",
    'market = US and trading value >= 10 million USD',
]

# Alias order matters: longer/more specific phrases win. All field names are
# also accepted explicitly, so users can see exactly which stored datum is used.
_ALIASES = {
    "open": ("시가", "open price"),
    "high": ("고가", "high price"),
    "low": ("저가", "low price"),
    "close": ("종가", "close price", "closing price"),
    "prev_close": ("전일 종가", "previous close"),
    "volume": ("거래량", "volume"),
    "prev_volume": ("전일 거래량", "previous volume"),
    "trading_value": ("거래대금", "trading value", "traded value", "turnover"),
    "market_cap": ("시가총액", "market cap", "market capitalization"),
    "volume_ratio_to_market_avg": ("시장평균 대비 거래량", "market volume ratio"),
    "volume_ratio": ("전일 대비 거래량", "거래량 배수", "volume ratio"),
    "daily_change_pct": ("일간 상승률", "일간 등락률", "등락률", "daily change", "daily change pct"),
    "gap_pct": ("갭 상승률", "갭률", "갭", "gap pct", "gap"),
    "close_strength": ("종가 강도", "종가강도", "close strength"),
    "high_52w": ("52주 최고가", "52 week high"),
    "sector_rank": ("섹터 순위", "sector rank"),
    "sector_leadership_score": ("섹터 주도 점수", "sector leadership score"),
    "risk_reward_ratio": ("손익비", "risk reward ratio"),
    "stop_loss_pct": ("손절률", "stop loss pct"),
    "trigger_score": ("트리거 점수", "trigger score"),
    "agent_fit_score": ("에이전트 적합 점수", "agent fit score"),
    "final_score": ("최종 점수", "final score"),
    "ticker": ("종목코드", "티커", "ticker"),
    "market": ("시장", "market"),
    "sector": ("섹터", "업종", "sector"),
    "trigger_type": ("트리거 유형", "trigger type"),
    "halted": ("거래정지", "halted", "trading halt"),
}
_LABELS = {field: aliases[0] for field, aliases in _ALIASES.items()}
_OP_LABELS = {"gte": "≥", "gt": ">", "lte": "≤", "lt": "<", "eq": "=", "ne": "≠"}
_OPS = {
    ">=": "gte", "≥": "gte", "이상": "gte", "at least": "gte", "no less than": "gte",
    "<=": "lte", "≤": "lte", "이하": "lte", "at most": "lte", "no more than": "lte",
    ">": "gt", "초과": "gt", "over": "gt", "above": "gt", "greater than": "gt", "more than": "gt",
    "<": "lt", "미만": "lt", "under": "lt", "below": "lt", "less than": "lt",
    "==": "eq", "=": "eq", "같음": "eq", "equals": "eq", "equal to": "eq",
    "!=": "ne", "≠": "ne", "다름": "ne", "not equal to": "ne",
}
_OP_RE = "|".join(re.escape(op) for op in sorted(_OPS, key=len, reverse=True))
_MONEY = {"open", "high", "low", "close", "prev_close", "trading_value", "market_cap", "high_52w"}
_PERCENT = {"daily_change_pct", "gap_pct", "stop_loss_pct"}
_RATIO = {"volume_ratio", "volume_ratio_to_market_avg", "risk_reward_ratio"}
_SCALES = {"": 1, "k": 1_000, "thousand": 1_000, "천": 1_000,
           "만": 10_000, "m": 1_000_000, "million": 1_000_000,
           "억": 100_000_000, "b": 1_000_000_000, "billion": 1_000_000_000,
           "조": 1_000_000_000_000, "trillion": 1_000_000_000_000}
_NUMBER = r"[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
_VALUE_RE = re.compile(
    rf"(?P<number>{_NUMBER})\s*(?P<scale>thousand|million|billion|trillion|천|만|억|조|[kmb])?\s*"
    r"(?P<unit>krw|usd|원|달러|\$|%|퍼센트|배|x|주|shares?)?", re.IGNORECASE,
)


class _Clarification(ValueError):
    pass


def _field_prefix(text: str) -> tuple[str, str]:
    aliases = [(alias, field) for field, names in _ALIASES.items() for alias in (*names, field)]
    for alias, field in sorted(aliases, key=lambda item: len(item[0]), reverse=True):
        if text.casefold().startswith(alias.casefold()):
            rest = text[len(alias):]
            # Do not reinterpret "volume average ..." or "market capitalization"
            # as a shorter field followed by unexplained trailing material.
            if rest and alias[-1].isascii() and alias[-1].isalnum() and rest[0].isalnum():
                continue
            return field, re.sub(r"^\s*(?:은|는|이|가|is\b)\s*", "", rest, count=1, flags=re.IGNORECASE).strip()
    raise _Clarification(f"지원하지 않는 조건입니다: {text!r}. 표시된 필드와 명시적인 수치를 사용해 주세요.")


def _comparison(rest: str) -> tuple[str, str]:
    prefix = re.fullmatch(rf"({_OP_RE})\s*(.+)", rest, flags=re.IGNORECASE)
    suffix = re.fullmatch(rf"(.+?)\s*({_OP_RE})", rest, flags=re.IGNORECASE)
    if prefix:
        return _OPS[prefix[1].casefold()], prefix[2].strip()
    if suffix:
        return _OPS[suffix[2].casefold()], suffix[1].strip()
    raise _Clarification("비교 기준이 필요합니다. 예: '거래량 배수 1.5배 이상', 'daily change >= 3%'.")


def _numeric_value(field: str, raw: str, markets: set[str]) -> int | float:
    match = _VALUE_RE.fullmatch(raw)
    if match is None:
        raise _Clarification(f"{_LABELS[field]}의 수치·단위·기간을 해석할 수 없습니다: {raw!r}.")
    number = float(match["number"].replace(",", ""))
    scale, unit = (match["scale"] or "").casefold(), (match["unit"] or "").casefold()
    number *= _SCALES[scale]
    if not math.isfinite(number) or abs(number) > 1e18:
        raise _Clarification("조건의 수치는 유한한 값이며 절대값 10^18 이하여야 합니다.")
    if field in _MONEY:
        if unit not in {"", "krw", "원", "usd", "달러", "$"}:
            raise _Clarification(f"{_LABELS[field]}에는 금액 단위(KRW/원 또는 USD/달러)가 필요합니다.")
        if unit in {"krw", "원"}:
            markets.add("KR")
        elif unit in {"usd", "달러", "$"}:
            markets.add("US")
        elif not markets:
            raise _Clarification(f"{_LABELS[field]}의 통화를 알 수 없습니다. 시장을 선택하거나 KRW/USD를 적어 주세요.")
    elif field in _PERCENT:
        if unit not in {"", "%", "퍼센트"} or scale:
            raise _Clarification(f"{_LABELS[field]}는 퍼센트 값으로 적어 주세요. 예: 3% (0.03이 아님).")
    elif field == "close_strength":
        if scale or unit not in {"", "%", "퍼센트"}:
            raise _Clarification("종가 강도는 0~1 또는 0~100%로 적어 주세요.")
        number /= 100 if unit else 1
        if not 0 <= number <= 1:
            raise _Clarification("종가 강도 범위는 0~1입니다. 75%는 0.75로 변환됩니다.")
    elif field in _RATIO:
        if scale or unit not in {"", "배", "x"}:
            raise _Clarification(f"{_LABELS[field]}는 배수로 적어 주세요. 예: 1.5배.")
    elif field in {"volume", "prev_volume"}:
        if unit not in {"", "주", "share", "shares"}:
            raise _Clarification("거래량의 단위는 주/shares입니다. 전일 대비 배수는 '거래량 배수'를 사용해 주세요.")
    elif unit or scale:
        raise _Clarification(f"{_LABELS[field]}는 단위 없는 수치로 적어 주세요.")
    if field not in _PERCENT and number < 0:
        raise _Clarification(f"{_LABELS[field]}에는 음수를 사용할 수 없습니다.")
    return int(number) if number.is_integer() else number


def _atom(text: str, markets: set[str]) -> dict[str, Any]:
    field, rest = _field_prefix(text)
    if field == "halted":
        if rest.casefold() in {"제외", "아님", "아닌", "false", "= false", "== false"}:
            return {"field": field, "op": "eq", "value": False}
        if rest.casefold() in {"", "true", "= true", "== true"}:
            return {"field": field, "op": "eq", "value": True}
        raise _Clarification("거래정지는 '거래정지 제외', 'not halted' 또는 'halted = true/false'로 적어 주세요.")
    op, raw = _comparison(rest)
    if field in NUMERIC_FIELDS:
        return {"field": field, "op": op, "value": _numeric_value(field, raw, markets)}
    if field in TEXT_FIELDS:
        if op not in {"eq", "ne"}:
            raise _Clarification("문자 조건은 = 또는 != 비교만 지원합니다.")
        if raw.startswith(('"', "'")):
            if len(raw) < 3 or raw[-1] != raw[0] or raw[0] in raw[1:-1]:
                raise _Clarification("문자 값의 따옴표를 확인해 주세요.")
            raw = raw[1:-1]
        if not raw or len(raw) > 200 or any(char in raw for char in '<>={}[];'):
            raise _Clarification("문자 조건에 사용할 정확한 값을 적어 주세요.")
        if field == "market":
            raw = {"한국": "KR", "국내": "KR", "미국": "US"}.get(raw, raw.upper())
            if raw not in {"KR", "US"}:
                raise _Clarification("현재 지원하는 시장은 KR(한국)과 US(미국)입니다.")
        return {"field": field, "op": op, "value": raw}
    raise _Clarification("지원하지 않는 필드입니다.")


def _tokenize(text: str) -> list[str]:
    # Quotes preserve text values containing operators, commas or parentheses.
    parts = re.split(r'''("[^"\n]*"|'[^'\n]*'|\(|\)|&&|\|\||\bAND\b|\bOR\b|\bNOT\b(?!\s+equal\s+to)|그리고|또는|혹은|아니면|\s+및\s+)''', text, flags=re.IGNORECASE)
    tokens: list[str] = []
    atom = ""
    operators = {"and": "AND", "&&": "AND", "그리고": "AND", "및": "AND",
                 "or": "OR", "||": "OR", "또는": "OR", "혹은": "OR", "아니면": "OR", "not": "NOT"}
    for part in parts:
        if not part:
            continue
        stripped = part.strip()
        token = operators.get(stripped.casefold(), stripped if stripped in {"(", ")"} else None)
        if token:
            if atom.strip():
                tokens.append(atom.strip())
            tokens.append(token)
            atom = ""
        else:
            atom += part
    if atom.strip():
        tokens.append(atom.strip())
    if len(tokens) > 200:
        raise _Clarification("한 번에 최대 100개 조건까지 입력해 주세요.")
    return tokens


def _describe(node: dict[str, Any]) -> str:
    if "all" in node or "any" in node:
        key = "all" if "all" in node else "any"
        separator = " 그리고 " if key == "all" else " 또는 "
        return "(" + separator.join(_describe(child) for child in node[key]) + ")"
    if "not" in node:
        return "아님: " + _describe(node["not"])
    field, value = node["field"], node["value"]
    label = _LABELS[field]
    if field == "volume_ratio":
        label = "전일 대비 거래량 배수 (현재 거래량 ÷ 전일 거래량)"
    elif field == "volume_ratio_to_market_avg":
        label = "시장평균 대비 거래량 배수"
    suffix = "%" if field in _PERCENT else "배" if field in _RATIO else ""
    formatted = f"{value:,}" if type(value) in (int, float) else str(value)
    return f"{label} [{field}] {_OP_LABELS[node['op']]} {formatted}{suffix}"


def compile_condition_text(text: str, *, market: str | None = None) -> dict[str, Any]:
    """Return a complete safe draft, or one explicit clarification without a DSL.

    The compiler never fetches data, selects securities, writes configuration or
    places orders. ``market`` is an explicit user selection; money is expressed
    in that market's local quote currency. Explicit contradictory currency
    suffixes fail closed. AND binds more tightly than OR; use parentheses to
    show grouping. Missing input data remains unknown under the existing DSL.
    """
    if not isinstance(text, str) or len(text) > 4000:
        raise ValueError("Condition text must be a string of at most 4000 characters")
    if market is not None and market not in {"KR", "US"}:
        raise ValueError("market must be KR, US or None")
    result: dict[str, Any] = {
        "compiler_version": COMPILER_VERSION, "input_text": text,
        "status": "needs_clarification", "condition": None, "normalized_rules": [],
        "issues": [], "assumptions": [], "scope_market": market,
        "supported_examples": SUPPORTED_EXAMPLES.copy(),
        "limitations": ["명시적인 필드·수치·비교만 지원합니다. 미지원 지표·기간은 자동으로 추정하지 않습니다.",
                        "이 결과는 조건 초안입니다. 저장·적용 전 정규화된 조건을 확인해 주세요.",
                        "AND는 OR보다 먼저 계산합니다. 혼합 조건은 괄호로 의도를 표시해 주세요.",
                        "지표 값이 없거나 유효하지 않으면 조건을 충족한 것으로 간주하지 않습니다."],
    }
    markets = {market} if market else set()
    try:
        tokens, cursor = _tokenize(text.strip()), 0
        if not tokens:
            raise _Clarification("조건을 입력해 주세요. '거래량이 충분한 종목'에는 구체적인 비교 수치가 필요합니다.")

        def primary(depth: int) -> dict[str, Any]:
            nonlocal cursor
            if depth > 8:
                raise _Clarification("조건 괄호 깊이는 8단계 이하여야 합니다.")
            if cursor >= len(tokens):
                raise _Clarification("연결어 뒤의 조건이 비어 있습니다.")
            current = tokens[cursor]
            cursor += 1
            if current == "NOT":
                return {"not": primary(depth + 1)}
            if current == "(":
                node = expression(depth + 1)
                if cursor >= len(tokens) or tokens[cursor] != ")":
                    raise _Clarification("닫는 괄호가 필요합니다.")
                cursor += 1
                return node
            if current in {"AND", "OR", ")"}:
                raise _Clarification("조건과 연결어의 순서 또는 괄호를 확인해 주세요.")
            return _atom(current, markets)

        def conjunction(depth: int) -> dict[str, Any]:
            nonlocal cursor
            items = [primary(depth)]
            while cursor < len(tokens) and tokens[cursor] == "AND":
                cursor += 1
                items.append(primary(depth))
            return items[0] if len(items) == 1 else {"all": items}

        def expression(depth: int) -> dict[str, Any]:
            nonlocal cursor
            items = [conjunction(depth)]
            while cursor < len(tokens) and tokens[cursor] == "OR":
                cursor += 1
                items.append(conjunction(depth))
            return items[0] if len(items) == 1 else {"any": items}

        tree = expression(0)
        if cursor != len(tokens):
            raise _Clarification("인식하지 못한 문장이나 괄호가 남아 있습니다. 조건 사이에 그리고/또는를 적어 주세요.")
        if len(markets) > 1:
            raise _Clarification("선택한 시장과 금액 통화가 충돌합니다. KR은 원/KRW, US는 달러/USD를 사용합니다.")
        scope = next(iter(markets)) if markets else None
        if scope:
            tree = {"all": [{"field": "market", "op": "eq", "value": scope}, tree]}
        tree = validate_condition(tree)
        result.update(status="compiled", condition=tree, scope_market=scope,
                      normalized_rules=[_describe(tree)])
        if scope:
            result["normalized_rules"].append(f"금액은 {'KRW(원)' if scope == 'KR' else 'USD(달러)'} 기준이며 통화 변환을 하지 않습니다.")
    except (_Clarification, ValueError) as exc:
        result["issues"] = [str(exc)]
    return result


def main(argv: list[str] | None = None) -> int:
    """Compile/inspect a draft; an optional file contains only the validated DSL."""
    parser = argparse.ArgumentParser(description="Draft explicit Korean/English scanner conditions safely")
    parser.add_argument("--text", required=True)
    parser.add_argument("--market", choices=("KR", "US"))
    parser.add_argument("--output", type=Path, help="Save compiled DSL only; unsupported requests never write a file")
    args = parser.parse_args(argv)
    try:
        result = compile_condition_text(args.text, market=args.market)
        if args.output and result["status"] == "compiled":
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result["condition"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0 if result["status"] == "compiled" else 2
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
