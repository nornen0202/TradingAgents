from __future__ import annotations

from urllib.parse import unquote


KPUNCH_CHANNEL_ID = "UCOB62fKRT7b73X7tRxMuN2g"
KPUNCH_DISPLAY_NAME = "박종훈의 지식한방"
USER_PRIMARY_HANDLES = ("@kpunch", "@sosumonkey")


def canonical_youtube_channel_name(
    channel: object,
    *,
    channel_id: object = "",
    source_url: object = "",
) -> str:
    """Return the stable investor-facing name for known YouTube identities."""

    raw_name = str(channel or "").strip()
    normalized_name = raw_name.casefold()
    normalized_id = str(channel_id or "").strip()
    normalized_source = f"{unquote(str(source_url or '')).strip().rstrip('/').casefold()}/"
    if (
        normalized_id == KPUNCH_CHANNEL_ID
        or "/@kpunch/" in normalized_source
        or normalized_name in {"jisik-hanbang", "지식한방", KPUNCH_DISPLAY_NAME.casefold()}
    ):
        return KPUNCH_DISPLAY_NAME
    return raw_name


def is_user_primary_youtube_source(source_url: object) -> bool:
    normalized = f"{unquote(str(source_url or '')).strip().rstrip('/').casefold()}/"
    return any(f"/{handle.casefold()}/" in normalized for handle in USER_PRIMARY_HANDLES)


def is_user_primary_youtube_identity(
    channel: object,
    *,
    channel_id: object = "",
    source_url: object = "",
) -> bool:
    if is_user_primary_youtube_source(source_url):
        return True
    canonical = canonical_youtube_channel_name(
        channel,
        channel_id=channel_id,
        source_url=source_url,
    ).casefold()
    return canonical in {KPUNCH_DISPLAY_NAME.casefold(), "소수몽키"}
