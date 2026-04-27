from .config import ScheduledAnalysisConfig, load_scheduled_config

__all__ = [
    "ScheduledAnalysisConfig",
    "build_site",
    "execute_scheduled_run",
    "load_scheduled_config",
    "main",
]


def __getattr__(name: str):
    if name in {"execute_scheduled_run", "main"}:
        from .runner import execute_scheduled_run, main

        return {"execute_scheduled_run": execute_scheduled_run, "main": main}[name]
    if name == "build_site":
        from .site import build_site

        return build_site
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
