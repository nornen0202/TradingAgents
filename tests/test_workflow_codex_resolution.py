import ast
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml


def runtime_probes():
    result = []
    for filename in ("daily-codex-analysis.yml", "daily-youtube-reports.yml"):
        workflow = yaml.safe_load((Path(".github/workflows") / filename).read_text(encoding="utf-8"))
        for job in workflow["jobs"].values():
            for step in job.get("steps", []):
                if step.get("name") == "Resolve Codex runtime":
                    tree = ast.parse(step["run"])
                    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in {"usable", "test_codex_candidate"})
                    assert "AppData/Local/OpenAI/Codex/bin/*/codex.exe" in step["run"]
                    result.append((filename, function))
    return result


@pytest.mark.parametrize("filename,function", runtime_probes())
def test_runtime_skips_inaccessible_alias_and_timed_out_binary(filename, function):
    class Inaccessible:
        def is_file(self):
            raise PermissionError("Windows app alias is inaccessible")

    namespace = {"Path": lambda _: Inaccessible(), "subprocess": subprocess}
    exec(compile(ast.Module(body=[function], type_ignores=[]), filename, "exec"), namespace)
    probe = namespace[function.name]
    assert probe("alias.exe") is False
    namespace["Path"] = lambda _: SimpleNamespace(is_file=lambda: True)

    def timeout(*args, **kwargs):
        assert kwargs["timeout"] == 10
        raise subprocess.TimeoutExpired(args[0], 10)

    namespace["subprocess"] = SimpleNamespace(run=timeout, DEVNULL=-3, STDOUT=-2, SubprocessError=subprocess.SubprocessError)
    assert probe("hung.exe") is False
    namespace["subprocess"].run = lambda *args, **kwargs: SimpleNamespace(returncode=0)
    assert probe("versioned.exe") is True
