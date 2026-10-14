#!/usr/bin/env python3
"""Download only the changed / added files from the remote skill mirror.

Convention:
  remote layout mirrors local layout under update_source/:
    <update_source>/updates.json
    <update_source>/manifest.json
    <update_source>/files/<path>          (eg files/SKILL.md, files/templates/foo/intro.md)

The remote SHOULD also expose a per-file mirror at /files/. If the source is a
git remote (git+https://...#branch), this script does ``git clone --depth 1``
and then copies the requested files. Plain HTTP(S) sources do per-file GETs.

Steps:
  1. Run check_update.py to compute (added, modified, removed) and the target version.
  2. For each added/modified file: download into <skill_root>/<path>, creating dirs.
  3. For each removed file: delete from <skill_root>/<path>.
  4. Write the new latest_version to VERSION and replace local updates.json
     with the remote copy so the deltas are accurate next time.
  5. Sanity-check sha256 against remote manifest.json if present.

Usage:
    python3 apply_update.py [--dry-run]
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_version(v: str) -> tuple[int, int, int]:
    parts = [int(x) for x in v.strip().split(".")]
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])  # type: ignore[return-value]


def fetch_json(source: str, sub: str) -> dict:
    url = source.rstrip("/") + "/" + sub.lstrip("/")
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_bytes(source: str, sub: str) -> bytes:
    url = source.rstrip("/") + "/" + sub.lstrip("/")
    with urllib.request.urlopen(url, timeout=120) as resp:
        return resp.read()


def collect_delta(remote_hist: list[dict], local_version: str):
    added, modified, removed = set(), set(), set()
    for entry in remote_hist:
        if parse_version(entry["version"]) <= parse_version(local_version):
            continue
        added |= set(entry.get("added", []))
        modified |= set(entry.get("modified", []))
        removed |= set(entry.get("removed", []))
    added -= removed
    modified -= removed
    return added, modified, removed


def http_apply(root: Path, source: str, remote_updates: dict, dry_run: bool) -> int:
    local_version = (root / "VERSION").read_text(encoding="utf-8").strip()
    added, modified, removed = collect_delta(remote_updates.get("history", []), local_version)
    target_version = remote_updates["latest_version"]

    if not (added or modified or removed):
        print(f"OK   Nothing to do (local={local_version}, remote={target_version}).")
        return 0

    print(f"PLAN Update {local_version} -> {target_version}")
    print(f"     +{len(added)} added | ~{len(modified)} modified | -{len(removed)} removed")
    if dry_run:
        for f in sorted(added):    print(f"     +  {f}")
        for f in sorted(modified): print(f"     ~  {f}")
        for f in sorted(removed):  print(f"     -  {f}")
        return 0

    remote_manifest = {}
    try:
        remote_manifest = fetch_json(source, "manifest.json")
    except Exception as exc:
        print(f"WARN Could not fetch remote manifest.json ({exc}); skipping sha256 check")

    for f in sorted(added | modified):
        dest = root / f
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = fetch_bytes(source, f"files/{f}")
        except urllib.error.URLError as exc:
            print(f"ERR  fetch {f}: {exc}", file=sys.stderr)
            return 3
        dest.write_bytes(data)
        if remote_manifest and "files" in remote_manifest and f in remote_manifest["files"]:
            want = remote_manifest["files"][f].get("sha256")
            if want and want != sha256_file(dest):
                print(f"ERR  sha256 mismatch on {f}", file=sys.stderr)
                return 4
        print(f"OK   wrote {f}")

    for f in sorted(removed):
        dest = root / f
        if dest.exists():
            dest.unlink()
            print(f"OK   removed {f}")

    (root / "VERSION").write_text(target_version + "\n", encoding="utf-8")
    (root / "updates.json").write_text(
        json.dumps(remote_updates, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nDONE updated to {target_version}")
    return 0


def git_apply(root: Path, source: str, dry_run: bool) -> int:
    # source format: git+https://...#branch
    spec = source[4:]
    if "#" in spec:
        url, branch = spec.split("#", 1)
    else:
        url, branch = spec, "main"
    with tempfile.TemporaryDirectory(prefix="skillupd_") as td:
        # Clone with LFS smudge disabled so the initial clone is fast even if
        # the remote tracks many large LFS files (e.g. 17 PPTX × 30+ MB each).
        # We will pull only the LFS files we actually need afterwards.
        env = os.environ.copy()
        env["GIT_LFS_SKIP_SMUDGE"] = "1"
        subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", branch, url, td],
            check=True, env=env,
        )
        clone = Path(td)
        remote_updates = json.loads((clone / "updates.json").read_text(encoding="utf-8"))
        local_version = (root / "VERSION").read_text(encoding="utf-8").strip()
        added, modified, removed = collect_delta(remote_updates.get("history", []), local_version)
        target_version = remote_updates["latest_version"]

        if not (added or modified or removed):
            print(f"OK   Nothing to do (local={local_version}, remote={target_version}).")
            return 0

        print(f"PLAN Update {local_version} -> {target_version}")
        if dry_run:
            for f in sorted(added):    print(f"     +  {f}")
            for f in sorted(modified): print(f"     ~  {f}")
            for f in sorted(removed):  print(f"     -  {f}")
            return 0

        # Selectively materialize LFS-tracked files that the delta needs.
        # Since v1.0.6 templates are plain git blobs (no LFS), so this is
        # usually a no-op; we still support LFS in case a future revision
        # re-introduces it. Skip entirely when the clone has no LFS filter.
        clone_attrs = (clone / ".gitattributes")
        repo_uses_lfs = (
            clone_attrs.exists()
            and "filter=lfs" in clone_attrs.read_text(encoding="utf-8", errors="ignore")
        )
        lfs_targets = sorted(
            f for f in (added | modified) if f.endswith(".pptx")
        ) if repo_uses_lfs else []
        if lfs_targets:
            print(f"     fetching {len(lfs_targets)} LFS file(s) selectively…")
            include_arg = ",".join(lfs_targets)
            try:
                subprocess.run(
                    ["git", "lfs", "pull", "--include", include_arg, "--exclude", ""],
                    cwd=clone, check=True,
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("WARN git-lfs unavailable; falling back to full smudge.",
                      file=sys.stderr)
                subprocess.run(
                    ["git", "checkout", "HEAD", "--", *lfs_targets],
                    cwd=clone, check=False,
                )

        for f in sorted(added | modified):
            src = clone / f
            dst = root / f
            if not src.exists():
                print(f"WARN remote missing {f}", file=sys.stderr)
                continue
            # Detect LFS pointer that wasn't materialized (still a tiny text
            # file with "version https://git-lfs.github.com/spec/v1" header).
            if src.stat().st_size < 1024:
                head = src.read_bytes()[:64]
                if head.startswith(b"version https://git-lfs"):
                    print(f"WARN {f} is still an LFS pointer; skipping (size={src.stat().st_size}).",
                          file=sys.stderr)
                    continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"OK   wrote {f}")
        for f in sorted(removed):
            dst = root / f
            if dst.exists():
                dst.unlink()
                print(f"OK   removed {f}")
        (root / "VERSION").write_text(target_version + "\n", encoding="utf-8")
        (root / "updates.json").write_text(
            json.dumps(remote_updates, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\nDONE updated to {target_version}")
        return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = args.skill_root
    local_updates = json.loads((root / "updates.json").read_text(encoding="utf-8"))
    source = local_updates.get("update_source")
    if not source:
        print("ERR  updates.json -> update_source is unset; cannot apply update.",
              file=sys.stderr)
        return 1

    try:
        if source.startswith("git+"):
            return git_apply(root, source, args.dry_run)
        else:
            remote_updates = fetch_json(source, "updates.json")
            return http_apply(root, source, remote_updates, args.dry_run)
    except Exception as exc:
        print(f"ERR  {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
