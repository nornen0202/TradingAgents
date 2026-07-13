from __future__ import annotations

from typing import Any, Callable, Sequence

from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool


def normalize_tools_for_codex(
    tools: Sequence[dict[str, Any] | type | Callable | BaseTool],
) -> list[dict[str, Any]]:
    """Normalize LangChain tool definitions into OpenAI-style schemas."""
    normalized: list[dict[str, Any]] = []
    for tool in tools:
        normalized.append(convert_to_openai_tool(tool, strict=True))
    return normalized


def build_plain_response_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "answer": {"type": "string"},
        },
        "required": ["answer"],
        "additionalProperties": False,
    }


def build_tool_response_schema(
    tool_schemas: Sequence[dict[str, Any]],
    *,
    allow_final: bool = True,
) -> dict[str, Any]:
    tool_items_schema = _tool_items_schema(tool_schemas)
    if not allow_final:
        return {
            "type": "object",
            "properties": {
                "mode": {"const": "tool_calls", "type": "string"},
                "content": {"type": "string"},
                "tool_calls": {
                    "type": "array",
                    "minItems": 1,
                    "items": tool_items_schema,
                },
            },
            "required": ["mode", "content", "tool_calls"],
            "additionalProperties": False,
        }

    return {
        "type": "object",
        "properties": {
            "mode": {
                "type": "string",
                "enum": ["final", "tool_calls"],
            },
            "content": {"type": "string"},
            "tool_calls": {
                "type": "array",
                "items": tool_items_schema,
            },
        },
        "required": ["mode", "content", "tool_calls"],
        "additionalProperties": False,
    }


def _tool_items_schema(tool_schemas: Sequence[dict[str, Any]]) -> dict[str, Any]:
    if len(tool_schemas) == 1:
        return _tool_call_variant(tool_schemas[0])

    # Keep every argument payload inside the strict output schema. Encoding the
    # payload as an arbitrary JSON string lets malformed suffixes pass the outer
    # schema and fail only after the model response reaches the host parser.
    return {
        "anyOf": [_tool_call_variant(tool_schema) for tool_schema in tool_schemas],
    }


def _tool_call_variant(tool_schema: dict[str, Any]) -> dict[str, Any]:
    function = tool_schema.get("function", {})
    parameters = function.get("parameters") or {"type": "object", "properties": {}}
    return {
        "type": "object",
        "properties": {
            "name": {
                "const": function["name"],
                "type": "string",
            },
            "arguments": parameters,
        },
        "required": ["name", "arguments"],
        "additionalProperties": False,
    }
