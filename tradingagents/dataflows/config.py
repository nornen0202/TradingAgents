from copy import deepcopy
from contextlib import contextmanager
from contextvars import Context, ContextVar, copy_context
from typing import Any, Dict, Optional

import tradingagents.default_config as default_config

# Use default config but allow it to be overridden
_config: Optional[Dict] = None
_run_config: ContextVar[Optional[Dict]] = ContextVar("tradingagents_run_config", default=None)


def initialize_config():
    """Initialize the configuration with default values."""
    global _config
    if _config is None:
        _config = deepcopy(default_config.DEFAULT_CONFIG)


def _deep_merge_dicts(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    merged = deepcopy(base)
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge_dicts(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def set_config(config: Dict):
    """Update the configuration with custom values."""
    global _config
    if _config is None:
        _config = deepcopy(default_config.DEFAULT_CONFIG)
    _config = _deep_merge_dicts(_config, config)


def get_config() -> Dict:
    """Get the current configuration."""
    scoped = _run_config.get()
    if scoped is not None:
        return deepcopy(scoped)
    if _config is None:
        initialize_config()
    return deepcopy(_config)


@contextmanager
def run_config(config: Dict):
    """Bind a complete run's settings without inheriting another run's overrides.

    LangGraph carries context variables into its analyst and tool workers.
    Resetting the token also restores the caller's settings after a failed run.
    """
    token = _run_config.set(_deep_merge_dicts(default_config.DEFAULT_CONFIG, config))
    try:
        yield
    finally:
        _run_config.reset(token)


def run_config_context(config: Dict) -> Context:
    """Create a private context for a stream that yields back to its caller."""
    context = copy_context()
    context.run(_run_config.set, _deep_merge_dicts(default_config.DEFAULT_CONFIG, config))
    return context


# Initialize with default config
initialize_config()
