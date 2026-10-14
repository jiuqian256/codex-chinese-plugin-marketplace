#!/usr/bin/env python3
"""Detect changed slide ids from an editable HTML deck state payload."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EXPLICIT_KEYS = (
    "changedSlides",
    "dirtySlides",
    "modifiedSlides",
    "insertedSlides",
    "deletedSlides",
)

EDIT_LIST_KEYS = (
    "edits",
    "operations",
    "changes",
    "textEdits",
    "geometryEdits",
    "imageEdits",
    "elementEdits",
)


def collect_slide_ids(value: Any, out: set[str]) -> None:
    if isinstance(value, str):
        out.add(value)
    elif isinstance(value, list):
        for item in value:
            collect_slide_ids(item, out)
    elif isinstance(value, dict):
        for key in ("slideId", "slide", "id"):
            raw = value.get(key)
            if isinstance(raw, str) and raw:
                out.add(raw)


def detect(payload: dict[str, Any]) -> dict[str, Any]:
    changed: set[str] = set()
    evidence: list[str] = []
    global_change = False

    for key in EXPLICIT_KEYS:
        if key in payload:
            before = set(changed)
            collect_slide_ids(payload[key], changed)
            if changed != before:
                evidence.append(key)

    for key in EDIT_LIST_KEYS:
        edits = payload.get(key)
        if not isinstance(edits, list):
            continue
        for edit in edits:
            if not isinstance(edit, dict):
                continue
            if edit.get("scope") == "global" or edit.get("slideId") == "global":
                global_change = True
                continue
            before = set(changed)
            collect_slide_ids(edit, changed)
            if changed != before and key not in evidence:
                evidence.append(key)

    if payload.get("slideOrderChanged") or payload.get("themeChanged") or payload.get("navigationChanged"):
        global_change = True

    return {
        "changedSlides": sorted(changed),
        "globalChange": global_change,
        "evidence": evidence,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect changed slide ids from deck-state JSON.")
    parser.add_argument("json_file", help="Path to deck-state.json or edits.json")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    path = Path(args.json_file).expanduser().resolve()
    payload = json.loads(path.read_text(encoding="utf-8"))
    result = detect(payload)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        slides = ", ".join(result["changedSlides"]) or "(none detected)"
        print(f"Changed slides: {slides}")
        print(f"Global change: {result['globalChange']}")
        if result["evidence"]:
            print(f"Evidence: {', '.join(result['evidence'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
