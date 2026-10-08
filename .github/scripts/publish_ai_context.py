"""Mirror a hash-verified public Pages snapshot, atomically; never read archives/accounts."""
from __future__ import annotations

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

BASE = "https://nornen0202.github.io/TradingAgents/ai"
API = "https://api.github.com/repos/nornen0202/TradingAgents"
BRANCH = "public-context"
FILES = {f"{market}/latest.{extension}" for market in ("kr", "us") for extension in ("md", "txt", "json")}


def fetch(url: str) -> bytes:
    # Stable Pages URLs can serve a coherent old snapshot despite no-cache.
    # Give every read (including the second manifest) a fresh CDN cache key.
    url = f"{url}{'&' if '?' in url else '?'}snapshot_read={uuid4().hex}"
    with urlopen(Request(url, headers={"Cache-Control": "no-cache", "User-Agent": "TradingAgents-Public-Reader"}), timeout=30) as response:
        return response.read(600_001)


def timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed > datetime.now(timezone.utc):
        raise ValueError("Invalid publication timestamp")
    return parsed


def validate_snapshot(manifest: dict, files: dict[str, bytes]) -> None:
    if manifest.get("schema") != "tradingagents.ai-context/v1" or set(manifest.get("files", {})) != FILES or set(files) != FILES:
        raise ValueError("Unexpected public mirror file set")
    timestamp(manifest["generated_at"])
    for name, content in files.items():
        entry = manifest["files"][name]
        if len(content) > 250_000 or len(content) != entry["bytes"] or hashlib.sha256(content).hexdigest() != entry["sha256"]:
            raise ValueError(f"Public snapshot integrity failure: {name}")
        stamp = json.loads(content)["generated_at"] if name.endswith(".json") else manifest["generated_at"] if f"문서 생성: {manifest['generated_at']}" in content.decode("utf-8") else None
        if stamp != manifest["generated_at"]:
            raise ValueError("Mixed public snapshot generation")


def download_snapshot() -> tuple[dict, dict[str, bytes]]:
    for attempt in range(3):
        try:
            first = fetch(f"{BASE}/manifest.json")
            manifest = json.loads(first)
            files = {name: fetch(f"{BASE}/{name}") for name in sorted(FILES)}
            if first != fetch(f"{BASE}/manifest.json"):
                raise ValueError("Pages changed during snapshot fetch; mirror not updated")
            validate_snapshot(manifest, files)
        except (ValueError, URLError, TimeoutError) as exc:
            # A manifest can stay stable while an edge serves an older child
            # file. Discard the entire download; never relax its hash checks.
            if isinstance(exc, HTTPError) and exc.code not in {429, 500, 502, 503, 504}:
                raise
            if attempt == 2:
                raise
            print(f"::warning::Public snapshot inconsistent or temporarily unavailable; retry {attempt + 2}/3")
            time.sleep((2, 5)[attempt])
            continue
        files["manifest.json"] = first
        return manifest, files
    raise RuntimeError("Public snapshot retry budget exhausted")


def api(path: str, method: str = "GET", payload: dict | None = None):
    token = os.environ["GH_TOKEN"]
    data = json.dumps(payload).encode() if payload is not None else None
    request = Request(API + path, data=data, method=method, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
        "Content-Type": "application/json", "X-GitHub-Api-Version": "2022-11-28",
    })
    # Git objects are content-addressed and ref updates remain non-forcing.
    # Replay the identical request on transient failures, retaining all snapshot
    # validation and the final ref verification in publish().
    for attempt in range(4):
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except HTTPError as exc:
            if exc.code not in {429, 500, 502, 503, 504} or attempt == 3:
                raise
            delay = (1, 3, 7)[attempt]
            if exc.code == 429:
                try:
                    delay = min(30, max(delay, float(exc.headers.get("Retry-After", delay))))
                except (AttributeError, TypeError, ValueError):
                    pass
            print(f"::warning::Public mirror API HTTP {exc.code}; retry {attempt + 2}/4")
        except (URLError, TimeoutError):
            if attempt == 3:
                raise
            delay = (1, 3, 7)[attempt]
            print(f"::warning::Public mirror API connection unavailable; retry {attempt + 2}/4")
        time.sleep(delay)


def publish() -> None:
    manifest, files = download_snapshot()
    head = None
    try:
        head = api(f"/git/ref/heads/{BRANCH}")["object"]["sha"]
    except HTTPError as exc:
        if exc.code != 404:
            raise
    if head:
        import base64
        old = json.loads(base64.b64decode(api(f"/contents/manifest.json?ref={head}")["content"]))
        if timestamp(old["generated_at"]) >= timestamp(manifest["generated_at"]):
            print("Mirror already at this or a newer snapshot; no update; "
                  f"public_generated_at={manifest['generated_at']} "
                  f"mirror_generated_at={old['generated_at']}")
            return
    tree = api("/git/trees", "POST", {"tree": [
        {"path": name, "mode": "100644", "type": "blob", "content": content.decode("utf-8")}
        for name, content in sorted(files.items())
    ]})
    commit = api("/git/commits", "POST", {
        "message": f"Public research snapshot {manifest['generated_at']}",
        "tree": tree["sha"], "parents": [head] if head else [],
    })
    # A second commit can name the immutable data commit without a self-hash
    # cycle. Advance the public ref only after BOTH commits exist atomically.
    snapshot_sha = commit["sha"]
    discovery = render_discovery(snapshot_sha, manifest, files["manifest.json"])
    discovery_tree = api("/git/trees", "POST", {"base_tree": tree["sha"], "tree": [
        {"path": "discovery.txt", "mode": "100644", "type": "blob", "content": discovery},
    ]})
    commit = api("/git/commits", "POST", {
        "message": f"Public snapshot discovery {manifest['generated_at']}",
        "tree": discovery_tree["sha"], "parents": [snapshot_sha],
    })
    if head:
        # No force: a concurrent advance cannot be silently overwritten.
        api(f"/git/refs/heads/{BRANCH}", "PATCH", {"sha": commit["sha"], "force": False})
    else:
        api("/git/refs", "POST", {"ref": f"refs/heads/{BRANCH}", "sha": commit["sha"]})
    if api(f"/git/ref/heads/{BRANCH}")["object"]["sha"] != commit["sha"]:
        raise ValueError("Mirror ref verification failed")
    print(f"Verified public mirror commit {commit['sha']}")


def render_discovery(snapshot_sha: str, manifest: dict, manifest_bytes: bytes) -> str:
    import re
    if not re.fullmatch(r"[0-9a-f]{40}", snapshot_sha):
        raise ValueError("Invalid immutable snapshot commit")
    root = f"https://raw.githubusercontent.com/nornen0202/TradingAgents/{snapshot_sha}"
    return "\n".join([
        "TradingAgents public input discovery v1",
        f"generated_at: {manifest['generated_at']}",
        f"snapshot_commit: {snapshot_sha}",
        "This is a cacheable pointer, not proof of current branch HEAD or current account/quotes.",
        "Reject future/missing timestamps; check age and all source clocks independently.",
        f"manifest_sha256: {hashlib.sha256(manifest_bytes).hexdigest()}",
        f"manifest_bytes: {len(manifest_bytes)}",
        f"manifest_url: {root}/manifest.json",
        *[f"{market}_{ext}_url: {root}/{market}/latest.{ext}"
          for market in ("kr", "us") for ext in ("txt", "json")],
        "",
    ])


if __name__ == "__main__":
    publish()
