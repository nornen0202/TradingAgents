from pathlib import Path
from unittest.mock import patch

import pytest

from tradingagents.llm_clients.codex_app_server import (
    CodexAppServerSession, CodexAppServerStorageError,
)
from tradingagents.llm_clients.codex_preflight import run_codex_preflight


@pytest.mark.parametrize("as_path", [True, False])
def test_preflight_accepts_workflow_workspace(tmp_path, as_path):
    workspace = tmp_path / "preflight"
    value = workspace if as_path else str(workspace)
    with patch("tradingagents.llm_clients.codex_preflight.resolve_codex_binary", return_value="codex"), \
         patch.object(CodexAppServerSession, "start"), \
         patch.object(CodexAppServerSession, "account_read", return_value={"account": {"type": "chatgpt"}}), \
         patch.object(CodexAppServerSession, "model_list", return_value={"data": [{"id": "fixture-model"}]}), \
         patch.object(CodexAppServerSession, "close"):
        result = run_codex_preflight(codex_binary="codex", model="fixture-model",
                                    request_timeout=1, workspace_dir=value, cleanup_threads=True)
    assert result.resolved_model == "fixture-model"


def test_path_normalization_keeps_control_character_rejection():
    with patch("tradingagents.llm_clients.codex_preflight.resolve_codex_binary", return_value="codex"):
        with pytest.raises(CodexAppServerStorageError, match="invalid"):
            run_codex_preflight(codex_binary="codex", model="fixture-model", request_timeout=1,
                                workspace_dir=Path("unsafe\x09workspace"), cleanup_threads=True)
