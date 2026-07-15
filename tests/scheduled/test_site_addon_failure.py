from __future__ import annotations

from pathlib import Path

import pytest

from tradingagents.scheduled.site import (
    _build_prism_telegram_site_addon,
    _build_youtube_site_addon,
)


@pytest.mark.parametrize(
    ("module_name", "builder_name", "addon", "message"),
    (
        (
            "tradingagents.youtube.site",
            "build_youtube_site",
            _build_youtube_site_addon,
            "required YouTube report site add-on",
        ),
        (
            "tradingagents.prism_telegram.site",
            "build_prism_telegram_site",
            _build_prism_telegram_site_addon,
            "required PRISM Telegram report site add-on",
        ),
    ),
)
def test_required_site_addon_failure_is_not_swallowed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    module_name: str,
    builder_name: str,
    addon,
    message: str,
) -> None:
    module = __import__(module_name, fromlist=[builder_name])

    def fail(*_args, **_kwargs):
        raise ValueError("synthetic add-on failure")

    monkeypatch.setattr(module, builder_name, fail)

    with pytest.raises(RuntimeError, match=message) as exc_info:
        addon(archive_dir=tmp_path / "archive", site_dir=tmp_path / "site")

    assert isinstance(exc_info.value.__cause__, ValueError)
