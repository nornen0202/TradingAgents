from __future__ import annotations

from tradingagents.portfolio.performance.etf_alternatives import _DEFAULT_INSTRUMENTS, _DEFAULT_PORTFOLIOS

from .models import BenchmarkInstrument, BenchmarkPortfolioDefinition


def default_instruments() -> dict[str, dict[str, str]]:
    return {key: dict(value) for key, value in _DEFAULT_INSTRUMENTS.items()}


def default_portfolios() -> dict[str, dict[str, float]]:
    return {key: dict(value) for key, value in _DEFAULT_PORTFOLIOS.items()}


def default_instrument_models() -> tuple[BenchmarkInstrument, ...]:
    return tuple(
        BenchmarkInstrument(
            benchmark_id=key,
            display_name=str(value.get("label") or key),
            ticker=str(value.get("symbol") or ""),
            market="US" if str(value.get("currency") or "").upper() == "USD" else "KR",
            currency=str(value.get("currency") or "KRW").upper(),
            asset_class="ETF",
        )
        for key, value in _DEFAULT_INSTRUMENTS.items()
    )


def default_portfolio_definitions() -> tuple[BenchmarkPortfolioDefinition, ...]:
    instrument_by_id = {item.benchmark_id: item for item in default_instrument_models()}
    definitions: list[BenchmarkPortfolioDefinition] = []
    for key, weights in _DEFAULT_PORTFOLIOS.items():
        normalized = normalize_weights(weights)
        instruments = tuple(
            instrument_by_id[instrument_key]
            for instrument_key in normalized
            if instrument_key in instrument_by_id
        )
        definitions.append(
            BenchmarkPortfolioDefinition(
                benchmark_id=key,
                display_name=_portfolio_display_name(key),
                description="Same-cashflow ETF alternative benchmark",
                instruments=instruments,
                weights=normalized,
                rebalance_policy="cashflow_only",
            )
        )
    return tuple(definitions)


def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    parsed: dict[str, float] = {}
    for key, value in weights.items():
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if number > 0:
            parsed[str(key).upper()] = number
    total = sum(parsed.values())
    if total <= 0:
        return {}
    return {key: value / total for key, value in parsed.items()}


def _portfolio_display_name(key: str) -> str:
    labels = {
        "KOSPI200_100": "KOSPI200 ETF 100%",
        "KOSDAQ150_100": "KOSDAQ150 ETF 100%",
        "SP500_100": "S&P500 ETF 100%",
        "NASDAQ100_100": "Nasdaq100 ETF 100%",
        "BLENDED": "혼합 벤치마크",
    }
    return labels.get(key, key)
