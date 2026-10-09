"""Run production and publication in independent local lanes without Actions.

The launcher supplies an immutable checkout and persistent archive/state paths.
No workflow dispatch, Actions artifacts, or hosted gates are required.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "nornen0202/TradingAgents"
PUBLIC_BASE = "https://nornen0202.github.io/TradingAgents"


def script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / ".github" / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read_json(path, default=None):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def prepare_environment():
    from tradingagents.dataflows.api_keys import get_api_key

    for name in ("KIS_APP_KEY", "KIS_APP_SECRET", "KIS_ACCOUNT_NO", "KIS_PRODUCT_CODE"):
        value = get_api_key(name)
        if value:
            os.environ.setdefault(name, value)
    os.environ["TRADINGAGENTS_KIS_MARKET_CALENDAR_ENABLED"] = "1"
    os.environ["TRADINGAGENTS_RECOVERY_SOURCE"] = "local_scheduler"
    os.environ["TRADINGAGENTS_CODEX_ALLOW_MODEL_FALLBACK"] = "0"
    os.environ["TRADINGAGENTS_CODEX_PREFLIGHT_ALLOW_MODEL_FALLBACK"] = "0"


def github_active_writers():
    """Drain already admitted Actions writers before changing backend ownership.

    Read failures fail closed. This is a transition interlock, not a dispatch
    dependency: once authority is local and the old writers have drained, the
    scheduler never needs the Actions API again.
    """
    result = subprocess.run(["gh", "api", f"repos/{REPOSITORY}/actions/runs?per_page=100"],
                            capture_output=True, text=True, check=True, timeout=30)
    allow = {"daily-codex-analysis.yml", "intraday-overlay-refresh.yml", "work-report-pages-refresh.yml",
             "daily-youtube-reports.yml", "daily-prism-telegram-reports.yml", "account-portfolio-report-verify.yml"}
    payload = json.loads(result.stdout)
    # Do not infer absence from a truncated first page.
    if len(payload["workflow_runs"]) == 100:
        result = subprocess.run(["gh", "api", "--paginate", f"repos/{REPOSITORY}/actions/runs?per_page=100&status=in_progress"],
                                capture_output=True, text=True, check=True, timeout=60)
        decoder, text, runs = json.JSONDecoder(), result.stdout.strip(), []
        while text:
            page, end = decoder.raw_decode(text)
            runs.extend(page["workflow_runs"])
            text = text[end:].lstrip()
        # Waiting/queued writers also need draining. Check each live status.
        for status in ("queued", "waiting", "pending", "requested"):
            result = subprocess.run(["gh", "api", "--paginate", f"repos/{REPOSITORY}/actions/runs?per_page=100&status={status}"],
                                    capture_output=True, text=True, check=True, timeout=60)
            text = result.stdout.strip()
            while text:
                page, end = decoder.raw_decode(text)
                runs.extend(page["workflow_runs"])
                text = text[end:].lstrip()
    else:
        runs = payload["workflow_runs"]
    active = []
    for run in runs:
        if (run.get("status") == "completed" or run.get("head_branch") != "main"
                or (run.get("head_repository") or {}).get("full_name") != REPOSITORY
                or run.get("path", "").split("@")[0].split("/")[-1] not in allow):
            continue
        # A never-admitted run can retain stale 'queued' API metadata after
        # GitHub's queue window. It owns no producer or deployment job. Never
        # apply this exemption to an in-progress run or a run with any jobs.
        created = datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
        if run.get("status") == "queued" and created.tzinfo and datetime.now(timezone.utc) - created > timedelta(hours=24):
            jobs = json.loads(subprocess.check_output(["gh", "api", f"repos/{REPOSITORY}/actions/runs/{run['id']}/jobs?per_page=1"],
                                                     text=True, timeout=30))
            if jobs.get("total_count") == 0 and jobs.get("jobs") == []:
                print(json.dumps({"status": "EXPIRED_UNSTARTED_QUEUE", "run_id": run["id"]}))
                continue
        active.append(int(run["id"]))
    return active


def drain_actions(state, *, dry_run=False):
    marker = state / "actions-drained.json"
    if marker.exists():
        return []
    if not dry_run:
        backend = subprocess.check_output(["gh", "api", f"repos/{REPOSITORY}/actions/variables/TRADINGAGENTS_AUTOMATION_BACKEND",
                                           "--jq", ".value"], text=True, timeout=30).strip()
        if backend != "local":
            raise ValueError("Set repository automation authority to local before draining Actions")
    active = github_active_writers()
    if not active and not dry_run:
        atomic_write_json(marker, {"drained_at": datetime.now(timezone.utc).isoformat()})
    return active


def completed_target(manifest, target):
    """Gate on completed research coverage, independently of delivery status."""
    from tradingagents.scheduled.runner import _manifest_is_complete_overlay_baseline

    settings = manifest.get("settings") or {}
    mode = "full" if target.workflow_file == "daily-codex-analysis.yml" else "overlay_only"
    if str(settings.get("market", "")).lower() != target.inputs["profile"] or settings.get("run_mode", "full") != mode:
        return False
    if mode == "full" and settings.get("analysis_mode", "full") != "full":
        return False
    try:
        started = datetime.fromisoformat(manifest["started_at"].replace("Z", "+00:00"))
        finished = datetime.fromisoformat(manifest["finished_at"].replace("Z", "+00:00"))
    except (KeyError, TypeError, ValueError):
        return False
    if started.tzinfo is None or finished.tzinfo is None or finished < started or started < target.window_start_kst:
        return False
    if mode == "full":
        return _manifest_is_complete_overlay_baseline(
            manifest, market=target.inputs["profile"], requested_tickers=None, required_holding_tickers=None,
        )
    return manifest.get("status") == "success" and int((manifest.get("summary") or {}).get("failed_tickers", 0)) == 0


def run_due(archive, state, *, now=None, dry_run=False):
    from tradingagents.scheduled.automation_calendar import automated_market_session_status
    from tradingagents.scheduled.runner import _iter_run_manifests_desc

    now = now or datetime.now(ZoneInfo("Asia/Seoul"))
    watchdog = script("scheduled_actions_watchdog")
    targets = watchdog.due_targets(now, market_status_resolver=automated_market_session_status)
    manifests = [m for m, _ in _iter_run_manifests_desc(archive)]
    decisions = []
    for target in targets:
        if target.workflow_file not in {"daily-codex-analysis.yml", "intraday-overlay-refresh.yml"}:
            continue
        if any(completed_target(m, target) for m in manifests):
            decisions.append({"target": target.name, "status": "RESEARCH_COMPLETE"})
            continue
        # Budget is per market/session, including Friday US work after KST midnight.
        key = hashlib.sha256(f"{target.name}:{target.window_start_kst.isoformat()}".encode()).hexdigest()
        receipt_path = state / "attempts" / f"{key}.json"
        receipt = read_json(receipt_path, {})
        attempts = int(receipt.get("attempts", 0))
        last = receipt.get("started_at")
        if attempts >= target.max_failed_attempts or (last and now - datetime.fromisoformat(last) < timedelta(minutes=60)):
            decisions.append({"target": target.name, "status": "RETRY_BUDGET_OR_COOLDOWN"})
            continue
        decisions.append({"target": target.name, "status": "DUE"})
        if dry_run:
            continue
        atomic_write_json(receipt_path, {"target": target.name, "attempts": attempts + 1, "started_at": now.isoformat(), "status": "STARTED"})
        profile = target.inputs["profile"]
        config = ROOT / "config" / ("scheduled_analysis_korea.toml" if profile == "kr" else "scheduled_analysis.toml")
        mode = "full" if target.workflow_file == "daily-codex-analysis.yml" else "overlay_only"
        if mode == "full":
            preflight(config)
        args = [sys.executable, "-u", "-m", "tradingagents.scheduled", "--config", str(config),
                "--archive-dir", str(archive), "--run-mode", mode, "--skip-site-build", "--strict",
                "--label", f"local-scheduler-{profile}-{mode}"]
        if mode == "full":
            args.append("--disable-execution-refresh")
        result = subprocess.run(args, cwd=ROOT, check=False, timeout=12 * 3600)
        atomic_write_json(receipt_path, {"target": target.name, "attempts": attempts + 1, "started_at": now.isoformat(),
                                       "finished_at": datetime.now(timezone.utc).isoformat(), "exit_code": result.returncode})
        # Re-evaluate calendars and archives on the next tick, after a long run.
        break
    return decisions


def preflight(config_path):
    from tradingagents.scheduled.config import load_scheduled_config
    from tradingagents.llm_clients.codex_preflight import run_codex_preflight

    config = load_scheduled_config(config_path)
    for model in set(getattr(config.llm, f"{role}_model") for role in ("deep", "quick", "output", "writer", "judge")):
        result = run_codex_preflight(model=model, codex_binary=config.llm.codex_binary, request_timeout=60,
                                    workspace_dir=config.llm.codex_workspace_dir, cleanup_threads=True, fallback_models=())
        if result.fallback_used or result.resolved_model != model:
            raise ValueError("Local preflight did not select the configured exact model")
    os.environ["TRADINGAGENTS_CODEX_PREFLIGHT_OK"] = "1"


def archive_fingerprint(archive):
    digest = hashlib.sha256()
    # Finished manifests and final Work publications are the durable outbox.
    # Incomplete ticker output never makes an unchanged report look delivered.
    roots = {"research": archive,
             "youtube": Path(os.getenv("TRADINGAGENTS_YOUTUBE_ARCHIVE_DIR") or archive / "youtube-archive"),
             "prism": Path(os.getenv("TRADINGAGENTS_PRISM_TELEGRAM_ARCHIVE_DIR") or archive / "prism-telegram-archive")}
    for label, root in roots.items():
        paths = list((root / "runs").rglob("manifest.json"))
        if label == "research":
            paths += list((root / "work-reports").glob("*/latest.json"))
        for path in sorted(paths):
            digest.update(f"{label}:{path.relative_to(root).as_posix()}".encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def git_run(args, *, input=None, env=None):
    result = subprocess.run(["git", *args], input=input, env=env, capture_output=True, text=True, check=False, timeout=180)
    if result.returncode:
        raise RuntimeError("Publication Git operation failed: " + result.stderr.strip()[:300])
    return result.stdout.strip()


def push_site(site, state):
    """Publish only generated public output, with a non-forcing branch advance."""
    if not (site / "index.html").is_file() or not (site / "pages-snapshot.json").is_file():
        raise ValueError("Site is incomplete")
    for path in site.rglob("*"):
        if path.is_symlink() or any(part in {".git", "portfolio-private", ".env", "api_keys.json"} for part in path.relative_to(site).parts):
            raise ValueError("Unexpected private or linked publication input")
        if path.suffix.lower() in {".sqlite", ".db", ".session", ".pem"}:
            raise ValueError("Unexpected private publication file")
    (site / ".nojekyll").write_bytes(b"")
    bare = state / "pages.git"
    if not bare.exists():
        git_run(["init", "--bare", str(bare)])
        git_run([f"--git-dir={bare}", "remote", "add", "fork", f"https://github.com/{REPOSITORY}.git"])
    prefix = [f"--git-dir={bare}"]
    remote = git_run([*prefix, "ls-remote", "fork", "refs/heads/gh-pages"])
    head = remote.split()[0] if remote else None
    if head:
        git_run([*prefix, "fetch", "fork", "refs/heads/gh-pages"])
        # Guard against rollback at the branch itself, even if the CDN is behind.
        live = json.loads(git_run([*prefix, "show", f"{head}:pages-snapshot.json"]))
        candidate = read_json(site / "pages-snapshot.json")
        if not script("pages_snapshot").should_deploy(candidate, live)[0]:
            raise ValueError("Publication superseded at the Pages branch")
    env = {**os.environ, "GIT_INDEX_FILE": str(state / "pages.index"),
           "GIT_AUTHOR_NAME": "TradingAgents local automation", "GIT_AUTHOR_EMAIL": "automation@users.noreply.github.com",
           "GIT_COMMITTER_NAME": "TradingAgents local automation", "GIT_COMMITTER_EMAIL": "automation@users.noreply.github.com"}
    git_run([*prefix, "read-tree", "--empty"], env=env)
    # Generated artifacts are verified byte-for-byte against Pages. Windows
    # autocrlf must not rewrite their bytes when staging the publication tree.
    git_run(["-c", "core.autocrlf=false", "-C", str(site), *prefix, f"--work-tree={site}", "add", "--all", "."], env=env)
    tree = git_run([*prefix, "write-tree"], env=env)
    commit = git_run([*prefix, "commit-tree", tree, *(["-p", head] if head else [])], input="Local public report snapshot\n", env=env)
    git_run([*prefix, "push", "fork", f"{commit}:refs/heads/gh-pages"])
    return commit


def verify_live(site):
    snapshot = script("pages_snapshot").fetch_live_snapshot(PUBLIC_BASE)
    if snapshot != read_json(site / "pages-snapshot.json"):
        return False
    # Check exact report and strategy bytes; a successful push is not delivery.
    for relative in ("mobile/strategy.json", "work/v1/kr/report/latest.json", "work/v1/us/report/latest.json"):
        path = site / relative
        if path.is_file():
            from urllib.request import Request, urlopen
            from uuid import uuid4
            request = Request(f"{PUBLIC_BASE}/{relative}?verify={uuid4().hex}", headers={"Cache-Control": "no-cache"})
            with urlopen(request, timeout=30) as response:
                if response.read(path.stat().st_size + 1) != path.read_bytes():
                    return False
    return True


def ensure_branch_pages(state):
    settings = json.loads(subprocess.check_output(["gh", "api", f"repos/{REPOSITORY}/pages"], text=True, timeout=30))
    if settings.get("build_type") == "legacy" and settings.get("source") == {"branch": "gh-pages", "path": "/"}:
        return
    backup = state / "previous-pages.json"
    if not backup.exists():
        atomic_write_json(backup, settings)
    payload = {"build_type": "legacy", "source": {"branch": "gh-pages", "path": "/"}}
    subprocess.run(["gh", "api", "--method", "PUT", f"repos/{REPOSITORY}/pages", "--input", "-"],
                   input=json.dumps(payload), text=True, check=True, timeout=30)
    settings = json.loads(subprocess.check_output(["gh", "api", f"repos/{REPOSITORY}/pages"], text=True, timeout=30))
    if settings.get("build_type") != "legacy" or settings.get("source") != payload["source"]:
        raise ValueError("Independent Pages publishing source was not applied")


def publish(archive, state, runtime_dir, *, rebuild=False):
    fingerprint = archive_fingerprint(archive)
    receipt_path = state / "publication.json"
    receipt = read_json(receipt_path, {})
    site = state / "site"
    if receipt.get("fingerprint") == fingerprint and receipt.get("status") == "DELIVERY_VERIFIED" and not rebuild:
        complete_handoffs(site, runtime_dir, receipt)
        return receipt
    if receipt.get("fingerprint") != fingerprint or not receipt.get("commit") or rebuild:
        from tradingagents.scheduled.config import load_scheduled_config
        from tradingagents.scheduled.site import build_site

        config = load_scheduled_config(ROOT / "config" / "scheduled_analysis.toml")
        build_site(archive, site, config.site)
        # Preserve exact Work hashes and existing reference-only lineage rules.
        verifier = script("verify_work_pages_handoff")
        for market in ("kr", "us"):
            report = read_json(archive / "work-reports" / market / "latest.json")
            if report:
                binding = {"surface": market, "event_id": report["event_id"], "report_sha256": report["report_sha256"]}
                verifier.verify_latest_report(archive, **binding)
                verifier.verify_built_site(site, **binding)
        revision = git_run(["-C", str(ROOT), "rev-parse", "HEAD"]) if (ROOT / ".git").exists() else os.environ["TRADINGAGENTS_SOURCE_SHA"]
        script("pages_snapshot").create_snapshot(site, repository=REPOSITORY, workflow="Local Automation",
                                                run_id=time.time_ns() // 1_000_000, run_attempt=1, commit_sha=revision,
                                                require_strategy_payload=True)
        live = script("pages_snapshot").fetch_live_snapshot(PUBLIC_BASE)
        if not script("pages_snapshot").should_deploy(read_json(site / "pages-snapshot.json"), live)[0]:
            raise ValueError("Publication would roll back the live site")
        commit = push_site(site, state)
        receipt = {"status": "PAGES_PENDING", "fingerprint": fingerprint, "commit": commit, "pushed_at": datetime.now(timezone.utc).isoformat()}
        atomic_write_json(receipt_path, receipt)
    ensure_branch_pages(state)
    # The public AI mirror is also independent of Actions/Pages edge availability.
    mirror = script("publish_ai_context")
    if not receipt.get("mirror_verified"):
        previous_token = os.environ.get("GH_TOKEN")
        os.environ["GH_TOKEN"] = previous_token or subprocess.check_output(["gh", "auth", "token"], text=True).strip()
        try:
            files = {name: (site / "ai" / name).read_bytes() for name in mirror.FILES | {"manifest.json"}}
            mirror.publish((json.loads(files["manifest.json"]), files))
        finally:
            if previous_token is None:
                os.environ.pop("GH_TOKEN", None)
            else:
                os.environ["GH_TOKEN"] = previous_token
        receipt["mirror_verified"] = True
        atomic_write_json(receipt_path, receipt)
    if verify_live(site):
        receipt.update(status="DELIVERY_VERIFIED", verified_at=datetime.now(timezone.utc).isoformat(), public_url=PUBLIC_BASE)
        atomic_write_json(receipt_path, receipt)
        complete_handoffs(site, runtime_dir, receipt)
    return receipt


def complete_handoffs(site, runtime_dir, publication):
    for path in (runtime_dir / "handoffs").glob("*/*.json"):
        receipt = read_json(path)
        if receipt.get("status") != "LOCAL_PUBLISH_PENDING":
            continue
        report = read_json(site / "work" / "v1" / receipt["surface"] / "report" / "latest.json", {})
        if report.get("event_id") == receipt.get("event_id") and report.get("report_sha256") == receipt.get("report_sha256"):
            receipt.update(status="DELIVERY_VERIFIED", external_delivery_verified=True,
                           verified_at=publication["verified_at"], publication_commit=publication["commit"])
            atomic_write_json(path, receipt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run-due", "publish"))
    parser.add_argument("--archive-dir", type=Path, required=True)
    parser.add_argument("--state-dir", type=Path, required=True)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()
    args.archive_dir = args.archive_dir.resolve()
    args.state_dir = args.state_dir.resolve()
    args.runtime_dir = args.runtime_dir.resolve()
    args.state_dir.mkdir(parents=True, exist_ok=True)
    prepare_environment()
    lane_acquired = False
    try:
        with interprocess_file_lock(args.state_dir / f"{args.command}.lock", timeout=0):
            lane_acquired = True
            active = drain_actions(args.state_dir, dry_run=args.dry_run)
            if active:
                print(json.dumps({"status": "DRAINING_ACTIONS_WRITERS", "run_ids": active}))
                return 0
            if args.command == "run-due":
                result = run_due(args.archive_dir, args.state_dir, dry_run=args.dry_run)
            elif args.dry_run:
                result = {"fingerprint": archive_fingerprint(args.archive_dir), "status": "DRY_RUN"}
            else:
                result = publish(args.archive_dir, args.state_dir, args.runtime_dir, rebuild=args.rebuild)
            print(json.dumps(result, ensure_ascii=False))
    except TimeoutError:
        if lane_acquired:
            raise
        print(json.dumps({"status": "LANE_ALREADY_RUNNING"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
