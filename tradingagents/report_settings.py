"""Public, reproducible run settings without credentials or machine paths."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
import re
from typing import Any, Mapping


_SCALARS = (
    "llm_provider", "quick_think_provider", "deep_think_provider", "output_think_provider",
    "quick_think_llm", "deep_think_llm", "output_think_llm", "output_language",
    "max_debate_rounds", "max_risk_discuss_rounds", "max_recur_limit", "max_tokens",
    "market_country", "timezone", "enable_no_trade", "point_in_time_strict",
    "checkpoint_enabled", "parallel_analysts", "analyst_max_concurrency",
    "openai_reasoning_effort", "google_thinking_level", "anthropic_effort",
    "codex_reasoning_effort", "codex_quick_reasoning_effort",
    "codex_deep_reasoning_effort", "codex_output_reasoning_effort",
)
_VENDOR_CATEGORIES = {
    "core_stock_apis", "technical_indicators", "fundamental_data", "news_data",
    "macro_data", "disclosure_data", "social_data", "institutional_data",
}
_VENDOR_TOOLS = {
    "get_stock_data", "get_indicators", "get_fundamentals", "get_balance_sheet",
    "get_cashflow", "get_income_statement", "get_insider_transactions",
    "get_news", "get_company_news", "get_global_news", "get_macro_news",
    "get_macro_indicators", "get_disclosures", "get_social_sentiment",
}


def public_run_settings(settings: Mapping[str, Any] | None) -> dict[str, Any]:
    """Allowlist values; never serialize endpoints, paths, arbitrary objects or secrets.

    This is deliberately not a recursive dump with a secret-key denylist: new
    configuration fields must be reviewed before appearing in exported reports.
    """
    if settings is None:
        return {}
    try:
        package_version = version("tradingagents")
    except PackageNotFoundError:
        package_version = "unknown"
    result: dict[str, Any] = {"version": package_version}
    for key in _SCALARS:
        value = settings.get(key)
        if value is not None and isinstance(value, (str, bool, int)):
            result[key] = value
    if result.get("llm_provider"):
        for tier in ("quick", "deep", "output"):
            key = f"{tier}_think_provider"
            result[key] = result.get(key) or result["llm_provider"]
    analysts = settings.get("analysts")
    if isinstance(analysts, (list, tuple)):
        result["analysts"] = [
            str(item) for item in analysts
            if isinstance(item, str) and item in {"market", "social", "news", "fundamentals"}
        ]
    for key in ("data_vendors", "tool_vendors"):
        vendors = settings.get(key)
        if not isinstance(vendors, Mapping):
            continue
        # Vendor names are identifiers, never arbitrary nested connection options.
        result[key] = {
            name: value for name, value in vendors.items()
            if isinstance(name, str) and isinstance(value, str)
            and ((key == "data_vendors" and name in _VENDOR_CATEGORIES)
                 or (key == "tool_vendors" and name in _VENDOR_TOOLS))
            and re.fullmatch(r"[a-zA-Z0-9_, -]+", value)
        }
    return result
