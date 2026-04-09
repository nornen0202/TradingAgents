from __future__ import annotations

import os
import re
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tradingagents.dataflows.config import get_config


class TranslationBackendError(RuntimeError):
    """Raised when the configured translation backend cannot serve a request."""


@dataclass(frozen=True)
class TranslationSettings:
    backend: str
    model: str
    model_path: str | None
    tokenizer_path: str | None
    device: str
    compute_type: str
    max_chunk_chars: int
    allow_llm_fallback: bool
    allow_large_model: bool


@dataclass(frozen=True)
class _BackendPreset:
    model_alias: str
    tokenizer_source: str
    source_language: str
    target_languages: dict[str, str]
    large_model: bool = False
    uses_target_prefix: bool = True


_NLLB_PRESET = _BackendPreset(
    model_alias="nllb-200-distilled-600m",
    tokenizer_source="facebook/nllb-200-distilled-600M",
    source_language="eng_Latn",
    target_languages={
        "english": "eng_Latn",
        "korean": "kor_Hang",
    },
)

_MADLAD_PRESET = _BackendPreset(
    model_alias="madlad-400-3b",
    tokenizer_source="google/madlad400-3b-mt",
    source_language="en",
    target_languages={
        "english": "en",
        "korean": "ko",
    },
    large_model=True,
    uses_target_prefix=False,
)

_BACKEND_PRESETS: dict[str, _BackendPreset] = {
    "nllb_ct2": _NLLB_PRESET,
    "madlad_ct2": _MADLAD_PRESET,
}

_TRANSLATOR_CACHE: dict[tuple[str, str, str], Any] = {}
_TOKENIZER_CACHE: dict[tuple[str, str], Any] = {}
_CACHE_LOCK = threading.Lock()
_CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
_LATIN_RE = re.compile(r"[A-Za-z]")


def get_translation_settings() -> TranslationSettings:
    config = get_config()
    translation_config = config.get("translation") or {}

    backend = str(translation_config.get("backend", "nllb_ct2")).strip().lower() or "nllb_ct2"
    default_model = _BACKEND_PRESETS.get(backend, _NLLB_PRESET).model_alias
    model = str(translation_config.get("model", default_model)).strip() or default_model

    return TranslationSettings(
        backend=backend,
        model=model.lower(),
        model_path=_optional_path(
            translation_config.get("model_path"),
            env_var="TRADINGAGENTS_TRANSLATION_MODEL_PATH",
        ),
        tokenizer_path=_optional_path(
            translation_config.get("tokenizer_path"),
            env_var="TRADINGAGENTS_TRANSLATION_TOKENIZER_PATH",
        ),
        device=str(
            translation_config.get(
                "device",
                os.getenv("TRADINGAGENTS_TRANSLATION_DEVICE", "auto"),
            )
        ).strip()
        or "auto",
        compute_type=str(translation_config.get("compute_type", "auto")).strip() or "auto",
        max_chunk_chars=max(400, int(translation_config.get("max_chunk_chars", 1800))),
        allow_llm_fallback=bool(translation_config.get("allow_llm_fallback", True)),
        allow_large_model=bool(
            translation_config.get(
                "allow_large_model",
                _env_truthy("TRADINGAGENTS_ALLOW_LARGE_TRANSLATION_MODEL"),
            )
        ),
    )


def should_skip_translation(content: str, language: str) -> bool:
    if not content:
        return True

    if language.strip().lower() != "korean":
        return False

    hangul_count = len(_HANGUL_RE.findall(content))
    if hangul_count < 8:
        return False

    latin_count = len(_LATIN_RE.findall(content))
    return hangul_count >= max(8, latin_count)


def translate_with_backend(content: str, language: str) -> str:
    if not content:
        return content

    settings = get_translation_settings()
    if settings.backend == "llm":
        raise TranslationBackendError("The translation backend is set to llm.")

    if settings.backend not in _BACKEND_PRESETS:
        raise TranslationBackendError(
            f"Unsupported translation backend '{settings.backend}'. "
            "Expected one of: llm, nllb_ct2, madlad_ct2."
        )

    preset = _BACKEND_PRESETS[settings.backend]
    if preset.large_model and not settings.allow_large_model:
        raise TranslationBackendError(
            "The MADLAD-400-3B backend is disabled by default because it is a large translation model. "
            "Set translation.allow_large_model=true or TRADINGAGENTS_ALLOW_LARGE_TRANSLATION_MODEL=1 "
            "after confirming the runner hardware can support it."
        )

    target_code = preset.target_languages.get(language.strip().lower())
    if not target_code:
        raise TranslationBackendError(
            f"Unsupported translation target language '{language}' for backend '{settings.backend}'."
        )

    chunks = _split_markdown_chunks(content, settings.max_chunk_chars)
    translated_chunks: list[str] = []
    for chunk in chunks:
        if not chunk or _is_code_fence_block(chunk):
            translated_chunks.append(chunk)
            continue
        translated_chunks.append(_translate_chunk(chunk, settings, preset, target_code))
    return "".join(translated_chunks)


def _translate_chunk(
    chunk: str,
    settings: TranslationSettings,
    preset: _BackendPreset,
    target_code: str,
) -> str:
    try:
        import ctranslate2
    except ImportError as exc:
        raise TranslationBackendError(
            "ctranslate2 is not installed. Install ctranslate2, sentencepiece, and transformers to use local translation."
        ) from exc

    try:
        from transformers import AutoTokenizer
    except ImportError as exc:
        raise TranslationBackendError(
            "transformers is not installed. Install transformers to use local translation tokenization."
        ) from exc

    model_path = settings.model_path
    if not model_path:
        raise TranslationBackendError(
            "No local CTranslate2 model path is configured. Set translation.model_path or "
            "TRADINGAGENTS_TRANSLATION_MODEL_PATH to a converted model directory."
        )

    tokenizer_source = settings.tokenizer_path or preset.tokenizer_source
    translator = _get_translator(
        ctranslate2,
        model_path=model_path,
        device=settings.device,
        compute_type=settings.compute_type,
    )
    tokenizer = _get_tokenizer(AutoTokenizer, tokenizer_source=tokenizer_source, preset=preset)

    if preset.uses_target_prefix:
        source_tokens = _encode_nllb_source(tokenizer, chunk, preset.source_language)
        results = translator.translate_batch(
            [source_tokens],
            target_prefix=[[target_code]],
            beam_size=2,
            max_batch_size=1,
        )
        hypotheses = results[0].hypotheses[0]
        decoded = _decode_hypothesis(tokenizer, hypotheses, drop_tokens={target_code})
        return decoded.strip() or chunk

    source_tokens = _encode_standard_source(tokenizer, f"<2{target_code}> {chunk}")
    results = translator.translate_batch(
        [source_tokens],
        beam_size=2,
        max_batch_size=1,
    )
    hypotheses = results[0].hypotheses[0]
    decoded = _decode_hypothesis(tokenizer, hypotheses, drop_tokens={f"<2{target_code}>"})
    return decoded.strip() or chunk


def _get_translator(ctranslate2_module: Any, *, model_path: str, device: str, compute_type: str) -> Any:
    cache_key = (model_path, device, compute_type)
    with _CACHE_LOCK:
        if cache_key not in _TRANSLATOR_CACHE:
            _TRANSLATOR_CACHE[cache_key] = ctranslate2_module.Translator(
                model_path,
                device=device,
                compute_type=compute_type,
                inter_threads=1,
                intra_threads=max(1, os.cpu_count() or 1),
            )
        return _TRANSLATOR_CACHE[cache_key]


def _get_tokenizer(auto_tokenizer: Any, *, tokenizer_source: str, preset: _BackendPreset) -> Any:
    cache_key = (tokenizer_source, preset.model_alias)
    with _CACHE_LOCK:
        if cache_key not in _TOKENIZER_CACHE:
            _TOKENIZER_CACHE[cache_key] = auto_tokenizer.from_pretrained(tokenizer_source)
        return _TOKENIZER_CACHE[cache_key]


def _encode_nllb_source(tokenizer: Any, chunk: str, source_language: str) -> list[str]:
    tokenizer.src_lang = source_language
    token_ids = tokenizer(chunk, add_special_tokens=True).input_ids
    return tokenizer.convert_ids_to_tokens(token_ids)


def _encode_standard_source(tokenizer: Any, chunk: str) -> list[str]:
    token_ids = tokenizer(chunk, add_special_tokens=True).input_ids
    return tokenizer.convert_ids_to_tokens(token_ids)


def _decode_hypothesis(tokenizer: Any, tokens: list[str], *, drop_tokens: set[str]) -> str:
    filtered_tokens = [
        token
        for token in tokens
        if token
        and token not in drop_tokens
        and token not in {"</s>", "<pad>"}
        and not token.startswith("<extra_id_")
    ]
    if not filtered_tokens:
        return ""
    token_ids = tokenizer.convert_tokens_to_ids(filtered_tokens)
    return tokenizer.decode(token_ids, skip_special_tokens=True)


def _split_markdown_chunks(content: str, max_chunk_chars: int) -> list[str]:
    if len(content) <= max_chunk_chars:
        return [content]

    chunks: list[str] = []
    current = ""
    in_code_fence = False
    for block in re.split(r"(\n\n+)", content):
        if not block:
            continue
        if "```" in block:
            in_code_fence = not in_code_fence

        if in_code_fence or len(block) > max_chunk_chars:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(_split_large_block(block, max_chunk_chars))
            continue

        candidate = f"{current}{block}"
        if current and len(candidate) > max_chunk_chars:
            chunks.append(current)
            current = block
        else:
            current = candidate

    if current:
        chunks.append(current)
    return chunks or [content]


def _split_large_block(block: str, max_chunk_chars: int) -> list[str]:
    if len(block) <= max_chunk_chars or _is_code_fence_block(block):
        return [block]

    pieces: list[str] = []
    current = ""
    for line in block.splitlines(keepends=True):
        candidate = f"{current}{line}"
        if current and len(candidate) > max_chunk_chars:
            pieces.append(current)
            current = line
        else:
            current = candidate
    if current:
        pieces.append(current)
    return pieces or [block]


def _is_code_fence_block(content: str) -> bool:
    stripped = content.strip()
    return bool(stripped and _CODE_FENCE_RE.fullmatch(stripped))


def _optional_path(value: object, *, env_var: str) -> str | None:
    if value is None or str(value).strip() == "":
        value = os.getenv(env_var)
    if value is None:
        return None
    text = os.path.expanduser(os.path.expandvars(str(value).strip()))
    if not text:
        return None
    return str(Path(text))


def _env_truthy(env_var: str) -> bool:
    return os.getenv(env_var, "").strip().lower() in {"1", "true", "yes", "on"}
