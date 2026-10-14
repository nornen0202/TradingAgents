from .kis import KisApiError, KisClient, PortfolioConfigurationError, validate_kis_credentials


def __getattr__(name):
    # Calendar gates need the read-only KIS client without the research stack.
    if name in {"load_snapshot_for_profile", "run_portfolio_pipeline"}:
        from . import pipeline

        value = getattr(pipeline, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "KisApiError",
    "KisClient",
    "PortfolioConfigurationError",
    "load_snapshot_for_profile",
    "run_portfolio_pipeline",
    "validate_kis_credentials",
]
