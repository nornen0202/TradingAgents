"""Mirror a hash-verified public Pages snapshot, atomically; never read archives/accounts."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE = "https://nornen0202.github.io/TradingAgents/ai"
API = "https://api.github.com/repos/nornen0202/TradingAgents"
BRANCH = "public-context"
FILES = {f"{market}/latest.{extension}" for market in ("kr", "us") for extension in ("md", "txt", "json")}


def fetch(url: str) -> bytes:
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
    for _ in range(2):
        first = fetch(f"{BASE}/manifest.json")
        manifest = json.loads(first)
        files = {name: fetch(f"{BASE}/{name}") for name in sorted(FILES)}
        if first != fetch(f"{BASE}/manifest.json"):
            continue
        validate_snapshot(manifest, files)
        files["manifest.json"] = first
        return manifest, files
    raise ValueError("Pages changed during snapshot fetch; mirror not updated")


def api(path: str, method: str = "GET", payload: dict | None = None):
    token = os.environ["GH_TOKEN"]
    data = json.dumps(payload).encode() if payload is not None else None
    request = Request(API + path, data=data, method=method, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
        "Content-Type": "application/json", "X-GitHub-Api-Version": "2022-11-28",
    })
    with urlopen(request, timeout=30) as response:
        return json.load(response)


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
            print("Mirror already at this or a newer snapshot; no update")
            return
    tree = api("/git/trees", "POST", {"tree": [
        {"path": name, "mode": "100644", "type": "blob", "content": content.decode("utf-8")}
        for name, content in sorted(files.items())
    ]})
    commit = api("/git/commits", "POST", {
        "message": f"Public research snapshot {manifest['generated_at']}",
        "tree": tree["sha"], "parents": [head] if head else [],
    })
    if head:
        # No force: a concurrent advance cannot be silently overwritten.
        api(f"/git/refs/heads/{BRANCH}", "PATCH", {"sha": commit["sha"], "force": False})
    else:
        api("/git/refs", "POST", {"ref": f"refs/heads/{BRANCH}", "sha": commit["sha"]})
    if api(f"/git/ref/heads/{BRANCH}")["object"]["sha"] != commit["sha"]:
        raise ValueError("Mirror ref verification failed")
    print(f"Verified public mirror commit {commit['sha']}")


if __name__ == "__main__":
    publish()
