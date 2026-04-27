from .contract_builder import build_execution_contract

__all__ = [
    "build_execution_contract",
    "evaluate_execution_state",
    "render_execution_summary_markdown",
    "render_execution_update_markdown",
    "collect_event_signals",
    "find_selective_rerun_targets",
]


def __getattr__(name: str):
    if name == "evaluate_execution_state":
        from .overlay import evaluate_execution_state

        return evaluate_execution_state
    if name in {"render_execution_summary_markdown", "render_execution_update_markdown"}:
        from .reporting import render_execution_summary_markdown, render_execution_update_markdown

        return {
            "render_execution_summary_markdown": render_execution_summary_markdown,
            "render_execution_update_markdown": render_execution_update_markdown,
        }[name]
    if name in {"collect_event_signals", "find_selective_rerun_targets"}:
        from .selective_rerun import collect_event_signals, find_selective_rerun_targets

        return {
            "collect_event_signals": collect_event_signals,
            "find_selective_rerun_targets": find_selective_rerun_targets,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
