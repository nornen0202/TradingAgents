from __future__ import annotations

import importlib.util
import base64
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from tradingagents.scheduled.ai_context import build_ai_context, render_context
from tradingagents.scheduled.decision_bundle import _execution_condition

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("publish_ai_context", ROOT / ".github/scripts/publish_ai_context.py")
mirror = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mirror)


def test_reader_projection_does_not_publish_private_identifiers(tmp_path):
    account = {"status": "available", "as_of": "2026-07-10T10:00:00Z",
               "account_id": "SECRET", "pending_orders": [{"id": "SECRET"}],
               "summary": {"available_cash_krw": None, "broker_response": "SECRET"},
               "positions": [{"ticker": "NVDA", "quantity": 2, "account_no": "SECRET"}]}
    strategy = {"freshness_receipt": {"analysis_completed_at": "2026-07-09T10:00:00Z"},
                "rows": [{"ticker": "NVDA", "portfolio_action": {"account_id": "SECRET"},
                          "quality": {"row_valid_until": "2026-07-10T10:30:00Z"}}]}
    text = render_context("us", strategy, account, {}, generated_at="2026-07-11T00:00:00Z")
    assert "SECRET" not in text
    assert "2026-07-09T10:00:00Z" in text
    assert '"available_cash_krw": null' in text
    assert "2026-07-10T10:30:00Z" in text
    assert "null은 미확인이지 0" in text


def test_reader_empty_inputs_are_unknown_and_manifest_is_atomic(tmp_path):
    manifest = build_ai_context(tmp_path, now=datetime(2026, 7, 11, tzinfo=timezone.utc))
    files = {name: (tmp_path / "ai" / name).read_bytes() for name in mirror.FILES}
    mirror.validate_snapshot(manifest, files)
    assert '"status": null' in files["kr/latest.md"].decode()
    corrupted = dict(files, **{"kr/latest.md": files["kr/latest.md"] + b"x"})
    with pytest.raises(ValueError, match="integrity"):
        mirror.validate_snapshot(manifest, corrupted)
    with pytest.raises(ValueError, match="file set"):
        mirror.validate_snapshot(manifest, {**files, "private.json": b"secret"})


@pytest.mark.parametrize("stamp", ["2026-07-11T00:00:00", "2099-01-01T00:00:00Z"])
def test_mirror_rejects_invalid_publication_clock(stamp):
    with pytest.raises(ValueError):
        mirror.timestamp(stamp)


def test_mirror_retries_mixed_deployment_but_never_publishes_it(monkeypatch, tmp_path):
    manifest = build_ai_context(tmp_path, now=datetime(2026, 7, 11, tzinfo=timezone.utc))
    encoded = json.dumps(manifest).encode()
    calls = []
    def fetch(url):
        calls.append(url)
        if url.endswith("manifest.json"):
            return encoded if len(calls) % (len(mirror.FILES) + 2) == 1 else encoded + b" "
        return (tmp_path / "ai" / url.split("/ai/")[1]).read_bytes()
    monkeypatch.setattr(mirror, "fetch", fetch)
    with pytest.raises(ValueError, match="changed"):
        mirror.download_snapshot()
    assert len(calls) == 2 * (len(mirror.FILES) + 2)


def test_sell_condition_cannot_inherit_buy_trigger():
    candidate = {"trigger_conditions": ["1935000 돌파 AND RVOL 1.2"],
                 "invalidation_conditions": ["1832000 이탈 시 손절"]}
    for code in ("SELL", "REDUCE", "AVOID"):
        result = _execution_condition(context={}, candidate=candidate, action={}, strategy_code=code)
        assert "1832000" in result
        assert "1935000" not in result
        assert "RVOL 1.2" not in result
    assert "1935000" in _execution_condition(context={}, candidate=candidate, action={}, strategy_code="BUY_NOW")


def test_both_prompts_require_current_evidence_and_recovery():
    for market in ("kr", "us"):
        text = (ROOT / "Docs" / f"prompts_{market}_for_chatgpt.md").read_text(encoding="utf-8")
        for fragment in (f"/ai/{market}/latest.txt", f"/public-context/{market}/latest.txt",
                         "현재 개인화 전략에 재사용하지", "계좌 최대낙폭이 아니며",
                         "조회 실패를 생산 중단으로 단정하지", "AND/OR", "가상 추가자금 5개안"):
            assert fragment in text


def test_held_rows_require_explicitly_published_account_membership():
    strategy = {"rows": [{"ticker": "SECRET", "is_held": True},
                         {"ticker": "PUBLIC", "is_held": True}]}
    text = render_context("kr", strategy, {"positions": [{"ticker": "PUBLIC"}]}, {}, generated_at="x")
    assert "SECRET" not in text
    assert "PUBLIC" in text


def test_mirror_never_rolls_back_or_writes_unapproved_paths(monkeypatch, tmp_path):
    manifest = build_ai_context(tmp_path, now=datetime(2026, 7, 11, tzinfo=timezone.utc))
    files = {name: (tmp_path / "ai" / name).read_bytes() for name in mirror.FILES}
    files["manifest.json"] = json.dumps(manifest).encode()
    monkeypatch.setattr(mirror, "download_snapshot", lambda: (manifest, files))
    calls = []
    def api(path, method="GET", payload=None):
        calls.append((path, method, payload))
        if path.startswith("/git/ref/heads/"):
            return {"object": {"sha": "old"}}
        if path.startswith("/contents/"):
            return {"content": base64.b64encode(json.dumps({**manifest, "generated_at": "2026-07-12T00:00:00Z"}).encode())}
        pytest.fail("A stale snapshot must not write Git objects")
    monkeypatch.setattr(mirror, "api", api)
    mirror.publish()
    assert all(method == "GET" for _, method, _ in calls)


def test_mirror_commits_only_allowlisted_files_without_force(monkeypatch, tmp_path):
    manifest = build_ai_context(tmp_path, now=datetime(2026, 7, 11, tzinfo=timezone.utc))
    files = {name: (tmp_path / "ai" / name).read_bytes() for name in mirror.FILES}
    files["manifest.json"] = json.dumps(manifest).encode()
    monkeypatch.setattr(mirror, "download_snapshot", lambda: (manifest, files))
    calls = []
    def api(path, method="GET", payload=None):
        calls.append((path, method, payload))
        if path.startswith("/git/ref/heads/"):
            return {"object": {"sha": "b" * 40 if any(m == "PATCH" for _, m, _ in calls) else "old"}}
        if path.startswith("/contents/"):
            return {"content": base64.b64encode(json.dumps({**manifest, "generated_at": "2026-07-10T00:00:00Z"}).encode())}
        if path == "/git/trees":
            if "base_tree" not in payload:
                assert set(item["path"] for item in payload["tree"]) == mirror.FILES | {"manifest.json"}
                return {"sha": "tree"}
            assert payload["base_tree"] == "tree"
            assert [item["path"] for item in payload["tree"]] == ["discovery.txt"]
            text = payload["tree"][0]["content"]
            assert f"snapshot_commit: {'a' * 40}" in text
            assert manifest["generated_at"] in text
            assert "/public-context/" not in text
            return {"sha": "discovery-tree"}
        if path == "/git/commits":
            if payload["tree"] == "tree":
                assert payload["parents"] == ["old"]
                return {"sha": "a" * 40}
            assert payload["parents"] == ["a" * 40]
            return {"sha": "b" * 40}
        assert path == "/git/refs/heads/public-context" and payload["force"] is False
        assert payload["sha"] == "b" * 40
        return {}
    monkeypatch.setattr(mirror, "api", api)
    mirror.publish()


def test_discovery_contains_no_account_values_and_rejects_bad_sha():
    manifest = {"generated_at": "2026-07-11T00:00:00Z", "private": "SECRET"}
    raw = json.dumps(manifest).encode()
    text = mirror.render_discovery("a" * 40, manifest, raw)
    assert "SECRET" not in text
    assert "manifest_sha256:" in text and f"manifest_bytes: {len(raw)}" in text
    assert "not proof of current branch HEAD" in text
    for value in ("old", "../main", "a" * 41):
        with pytest.raises(ValueError, match="Invalid immutable"):
            mirror.render_discovery(value, manifest, raw)


def test_discovery_failure_never_advances_public_ref(monkeypatch, tmp_path):
    manifest = build_ai_context(tmp_path, now=datetime(2026, 7, 11, tzinfo=timezone.utc))
    files = {name: (tmp_path / "ai" / name).read_bytes() for name in mirror.FILES}
    files["manifest.json"] = json.dumps(manifest).encode()
    monkeypatch.setattr(mirror, "download_snapshot", lambda: (manifest, files))
    def api(path, method="GET", payload=None):
        assert method != "PATCH", "Partial discovery publication must not advance the ref"
        if path.startswith("/git/ref/heads/"):
            return {"object": {"sha": "old"}}
        if path.startswith("/contents/"):
            return {"content": base64.b64encode(json.dumps({**manifest, "generated_at": "2026-07-10T00:00:00Z"}).encode())}
        if path == "/git/trees":
            if "base_tree" in payload:
                raise OSError("Discovery write failed")
            return {"sha": "tree"}
        if path == "/git/commits":
            return {"sha": "a" * 40}
        pytest.fail(f"Unexpected API mutation: {path}")
    monkeypatch.setattr(mirror, "api", api)
    with pytest.raises(OSError, match="Discovery write failed"):
        mirror.publish()
