#!/usr/bin/env python3
"""Check whether the local skill is up to date with the remote.

Reads:
  - <skill_root>/VERSION         current local version
  - <skill_root>/updates.json    update_source + history
  - remote updates.json          fetched from update_source/updates.json

Logic:
  1. If update_source is null/empty -> print "Update source unset" and exit 0.
  2. Otherwise GET <update_source>/updates.json (or git clone shallow if git+ URL).
  3. Compare remote.latest_version with local VERSION.
  4. If same -> "Up to date".
  5. If remote has newer versions, traverse remote.history from local version → latest,
     collect union of added/modified files and list them.

This script *does not* download files; it just reports what would change. Use
``apply_update.py`` to actually fetch/replace.
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path


def parse_version(v: str) -> tuple[int, int, int]:
    parts = [int(x) for x in v.strip().split(".")]
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])  # type: ignore[return-value]


def fetch_remote_updates(source: str) -> dict:
    if source.startswith("git+"):
        return _fetch_remote_updates_git(source)
    url = source.rstrip("/") + "/updates.json"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _fetch_remote_updates_git(source: str) -> dict:
    """For git+ sources: do a tiny shallow + blobless clone, read updates.json.

    LFS smudging is disabled so we don't pull large binary assets just to
    look at version metadata.
    """
    spec = source[4:]
    if "#" in spec:
        url, branch = spec.split("#", 1)
    else:
        url, branch = spec, "main"
    with tempfile.TemporaryDirectory(prefix="skillchk_") as td:
        env = os.environ.copy()
        env["GIT_LFS_SKIP_SMUDGE"] = "1"
        subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", branch,
             "--filter=blob:none", "--no-checkout", url, td],
            check=True,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # Only check out updates.json (and nothing else)
        subprocess.run(
            ["git", "checkout", "HEAD", "--", "updates.json"],
            cwd=td, check=True, env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return json.loads((Path(td) / "updates.json").read_text(encoding="utf-8"))


def collect_delta(remote_hist: list[dict], local_version: str) -> tuple[set[str], set[str], set[str]]:
    """Return (added, modified, removed) as union of versions newer than local."""
    local = parse_version(local_version)
    added: set[str] = set()
    modified: set[str] = set()
    removed: set[str] = set()
    for entry in remote_hist:
        if parse_version(entry["version"]) <= local:
            continue
        for f in entry.get("added", []):
            added.add(f)
        for f in entry.get("modified", []):
            modified.add(f)
        for f in entry.get("removed", []):
            removed.add(f)
    # Files added then later removed should appear only in removed
    removed_ones = removed.copy()
    added -= removed_ones
    modified -= removed_ones
    return added, modified, removed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    root = args.skill_root
    version_file = root / "VERSION"
    updates_file = root / "updates.json"

    if not version_file.exists() or not updates_file.exists():
        print("ERR  Cannot find VERSION or updates.json; this skill folder looks incomplete.",
              file=sys.stderr)
        return 2

    local_version = version_file.read_text(encoding="utf-8").strip()
    local_updates = json.loads(updates_file.read_text(encoding="utf-8"))
    source = local_updates.get("update_source")

    if not source:
        if not args.quiet:
            print("INFO Update source unset; skipping update check.")
            print(f"     Local version: {local_version}")
            print("     To enable updates, set updates.json -> update_source.")
        return 0

    try:
        remote = fetch_remote_updates(source)
    except (urllib.error.URLError, json.JSONDecodeError,
            subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"WARN Could not fetch remote updates ({exc}); using local copy.", file=sys.stderr)
        return 0

    remote_latest = remote.get("latest_version") or local_version
    if parse_version(remote_latest) <= parse_version(local_version):
        print(f"OK   Up to date (local={local_version}, remote={remote_latest}).")
        return 0

    added, modified, removed = collect_delta(remote.get("history", []), local_version)
    print(f"NEW  Update available: {local_version} -> {remote_latest}")
    print(f"     +{len(added)} added | ~{len(modified)} modified | -{len(removed)} removed")
    if added:
        print("\n     Added files:")
        for f in sorted(added):
            print(f"       + {f}")
    if modified:
        print("\n     Modified files:")
        for f in sorted(modified):
            print(f"       ~ {f}")
    if removed:
        print("\n     Removed files:")
        for f in sorted(removed):
            print(f"       - {f}")
    print(f"\n     To apply: python3 scripts/apply_update.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
