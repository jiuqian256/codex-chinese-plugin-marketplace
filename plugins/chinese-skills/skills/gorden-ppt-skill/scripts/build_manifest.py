#!/usr/bin/env python3
"""Rebuild manifest.json with sha256 of every tracked file.

Tracked = everything in the skill root, EXCLUDING:
  - .work/, .duplicates/, __pycache__/, .DS_Store, hidden dirs
  - manifest.json itself
  - VERSION (kept tracked separately by content)
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path


EXCLUDE_DIRS = {".work", "__pycache__", ".git", ".idea", ".vscode", ".duplicates"}
EXCLUDE_FILES = {".DS_Store", "manifest.json"}


def is_excluded_file(name: str) -> bool:
    if name in EXCLUDE_FILES:
        return True
    if name.startswith("~$"):  # PowerPoint/Office lock files
        return True
    return False


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_files(root: Path):
    for p in sorted(root.rglob("*")):
        if p.is_dir():
            continue
        rel_parts = p.relative_to(root).parts
        if any(part in EXCLUDE_DIRS or part.startswith(".") for part in rel_parts[:-1]):
            continue
        if is_excluded_file(p.name):
            continue
        yield p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parent.parent)
    ap.add_argument("--version-tag", default=None,
                    help="If set, every newly-added entry's last_modified is recorded as this version")
    args = ap.parse_args()

    root = args.skill_root
    version = args.version_tag or (root / "VERSION").read_text(encoding="utf-8").strip()
    manifest_path = root / "manifest.json"

    old = {}
    if manifest_path.exists():
        old = json.loads(manifest_path.read_text(encoding="utf-8")).get("files", {})

    files: dict[str, dict] = {}
    for p in iter_files(root):
        rel = str(p.relative_to(root))
        sha = sha256_file(p)
        prev = old.get(rel, {})
        entry = {
            "sha256": sha,
            "size": p.stat().st_size,
            "version_added": prev.get("version_added", version),
            "last_modified": version if prev.get("sha256") != sha else prev.get("last_modified", version),
        }
        files[rel] = entry

    manifest = {
        "$schema": "ppt-skill-manifest/v1",
        "skill_name": "ppt-builder",
        "version": version,
        "file_count": len(files),
        "files": files,
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote {manifest_path} (version={version}, files={len(files)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
