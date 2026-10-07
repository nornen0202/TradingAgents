"""Validated selections for runs with no terminal or interactive prompts."""

from __future__ import annotations

import datetime as dt
import re
from typing import Any, Mapping

from cli.models import AnalystType
from tradingagents.agents.utils.instrument_resolver import resolve_instrument


def unattended_selections(flags: Mapping[str, Any], defaults: Mapping[str, Any]) -> dict[str, Any]:
    """Resolve explicit flags over configured defaults before starting any work."""
    ticker = str(flags.get("ticker") or "").strip().upper()
    # Symbols are also directory components. Preserve exchange/index syntax,
    # but reject path traversal, Windows devices, control codes and Rich markup.
    if (not re.fullmatch(r"[A-Z0-9^][A-Z0-9.^=_-]{0,63}", ticker)
            or ticker.endswith(".") or ".." in ticker
            or re.fullmatch(r"(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", ticker)):
        raise ValueError("--ticker must be a valid symbol, for example NVDA, BRK-B or 005930.KS")
    try:
        ticker = resolve_instrument(ticker).normalized_symbol
    except ValueError as exc:
        raise ValueError("--ticker is not supported by the instrument resolver; use a US ticker or Korean stock code") from exc
    date = str(flags.get("date") or "").strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise ValueError("--date is required in YYYY-MM-DD format")
    try:
        analysis_date = dt.date.fromisoformat(date)
    except ValueError as exc:
        raise ValueError("--date must be a valid calendar date") from exc
    if analysis_date > dt.date.today():
        raise ValueError("--date cannot be in the future")
    names = str(flags.get("analysts") or "market,social,news,fundamentals").split(",")
    names = ["social" if name.strip().lower() == "sentiment" else name.strip().lower() for name in names]
    if any(name not in {item.value for item in AnalystType} for name in names):
        raise ValueError("--analysts must contain market, social (or sentiment), news, fundamentals")
    analysts = [item for item in AnalystType if item.value in names]
    depth = flags.get("depth")
    depth = int(defaults.get("max_debate_rounds", 2) if depth is None else depth)
    if depth < 1:
        raise ValueError("--depth must be at least 1")
    provider = str(flags.get("provider") or defaults.get("llm_provider", "codex")).strip().lower()
    if not re.fullmatch(r"[a-z][a-z0-9_-]*", provider):
        raise ValueError("--provider must be a provider identifier")
    if provider != str(defaults.get("llm_provider", "codex")).lower():
        if not flags.get("quick_model") or not flags.get("deep_model"):
            raise ValueError("Changing --provider requires --quick-model and --deep-model for that provider")
    overrides = {}
    for tier in ("quick", "deep", "output"):
        selected_provider = flags.get(f"{tier}_provider")
        selected_model = flags.get(f"{tier}_model")
        if selected_provider:
            selected_provider = str(selected_provider).strip().lower()
            if not re.fullmatch(r"[a-z][a-z0-9_-]*", selected_provider):
                raise ValueError(f"--{tier}-provider must be a provider identifier")
            if selected_provider != provider and not selected_model:
                raise ValueError(f"--{tier}-provider requires --{tier}-model when it differs from --provider")
            overrides[f"{tier}_think_provider"] = selected_provider
    if flags.get("parallel_analysts") is not None:
        overrides["parallel_analysts"] = flags["parallel_analysts"]
    if flags.get("results_dir") is not None:
        overrides["results_dir"] = str(flags["results_dir"])
    if flags.get("output_model"):
        overrides["output_think_llm"] = flags["output_model"]
    elif provider == str(defaults.get("llm_provider", "codex")).lower():
        overrides["output_think_llm"] = defaults.get("output_think_llm") or defaults.get("quick_think_llm")
    if flags.get("depth") is None:
        overrides["max_risk_discuss_rounds"] = defaults.get("max_risk_discuss_rounds", depth)
    return {
        "ticker": ticker, "analysis_date": date, "analysts": analysts,
        "research_depth": depth, "llm_provider": provider,
        "backend_url": defaults.get("backend_url") if provider == defaults.get("llm_provider") else None,
        "shallow_thinker": flags.get("quick_model") or defaults.get("quick_think_llm"),
        "deep_thinker": flags.get("deep_model") or defaults.get("deep_think_llm"),
        "output_language": flags.get("language") or defaults.get("output_language", "English"),
        **{key: defaults.get(key) for key in ("google_thinking_level", "openai_reasoning_effort", "anthropic_effort", "codex_reasoning_effort")},
        "config_overrides": overrides,
    }
