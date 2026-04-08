import threading
from typing import Any, Dict, List, Union

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.messages import AIMessage


class StatsCallbackHandler(BaseCallbackHandler):
    """Callback handler that tracks LLM calls, tool calls, and token usage."""

    def __init__(self) -> None:
        super().__init__()
        self._lock = threading.Lock()
        self.llm_calls = 0
        self.tool_calls = 0
        self.tokens_in = 0
        self.tokens_out = 0
        self.tokens_available = False
        self.calls_by_model: Dict[str, int] = {}

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs: Any,
    ) -> None:
        """Increment LLM call counter when an LLM starts."""
        model_name = (
            kwargs.get("invocation_params", {}).get("model")
            or kwargs.get("model_name")
            or serialized.get("name")
            or "unknown"
        )
        with self._lock:
            self.llm_calls += 1
            self.calls_by_model[model_name] = self.calls_by_model.get(model_name, 0) + 1

    def on_chat_model_start(
        self,
        serialized: Dict[str, Any],
        messages: List[List[Any]],
        **kwargs: Any,
    ) -> None:
        """Increment LLM call counter when a chat model starts."""
        model_name = (
            kwargs.get("invocation_params", {}).get("model")
            or kwargs.get("model_name")
            or serialized.get("name")
            or "unknown"
        )
        with self._lock:
            self.llm_calls += 1
            self.calls_by_model[model_name] = self.calls_by_model.get(model_name, 0) + 1

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Extract token usage from LLM response."""
        try:
            generation = response.generations[0][0]
        except (IndexError, TypeError):
            return

        usage_metadata = None
        if hasattr(generation, "message"):
            message = generation.message
            if isinstance(message, AIMessage) and hasattr(message, "usage_metadata"):
                usage_metadata = message.usage_metadata
            if not usage_metadata and isinstance(message, AIMessage):
                response_metadata = getattr(message, "response_metadata", {}) or {}
                usage_metadata = response_metadata.get("token_usage")

        if usage_metadata:
            with self._lock:
                self.tokens_available = True
                self.tokens_in += usage_metadata.get("input_tokens", 0)
                self.tokens_out += usage_metadata.get("output_tokens", 0)

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        """Increment tool call counter when a tool starts."""
        with self._lock:
            self.tool_calls += 1

    def get_stats(self) -> Dict[str, Any]:
        """Return current statistics."""
        with self._lock:
            return {
                "llm_calls": self.llm_calls,
                "tool_calls": self.tool_calls,
                "tokens_in": self.tokens_in,
                "tokens_out": self.tokens_out,
                "tokens_available": self.tokens_available,
                "calls_by_model": dict(self.calls_by_model),
            }
