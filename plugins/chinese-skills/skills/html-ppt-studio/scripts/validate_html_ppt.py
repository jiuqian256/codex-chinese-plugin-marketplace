#!/usr/bin/env python3
"""Lightweight checks for html-ppt-studio generated decks."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def check_html(path: Path) -> dict:
    html = path.read_text(encoding="utf-8", errors="replace")
    lower = html.lower()
    errors: list[str] = []
    warnings: list[str] = []

    if not re.search(r"1920\s*px|1920[,:\s]", html) or not re.search(r"1080\s*px|1080[,:\s]", html):
        if "aspect-ratio" not in lower or "16" not in html or "9" not in html:
            errors.append("No clear 1920x1080 or 16:9 stage contract found.")

    if 'class="slide' not in html and "class='slide" not in html:
        errors.append("No .slide sections found.")

    if "keydown" not in lower or ("arrowright" not in lower and "arrowleft" not in lower):
        warnings.append("Keyboard navigation was not detected.")

    if "prefers-reduced-motion" not in lower:
        warnings.append("prefers-reduced-motion support was not detected.")

    if "<table" in lower:
        warnings.append("HTML table detected. Ensure it is intentional and visually redesigned.")

    if "contenteditable" not in lower and "data-edit-id" not in lower and "edit-mode" not in lower:
        warnings.append("Editable deck hooks were not detected.")

    if "localstorage" in lower and not re.search(r"deck-state|edits\.json|edited\.html|save", lower):
        warnings.append("localStorage detected without an obvious durable save path.")

    if re.search(r"display\s*:\s*none", lower):
        warnings.append("display:none detected. Make sure slide switching cannot be overridden by layout styles.")

    has_presenter = "presenter" in lower or "speaker" in lower or "演示者" in html or "演讲者" in html
    if has_presenter:
        if not re.search(r"timer|elapsed|clock|计时|已讲|用时", lower):
            warnings.append("Presenter view detected, but no timer/elapsed-time UI was detected.")
        if not re.search(r"broadcastchannel|postmessage|localstorage|hashchange|storage", lower):
            warnings.append("Presenter view detected, but no audience/presenter sync mechanism was detected.")
        if "audience" not in lower and "projection" not in lower and "投屏" not in html and "观众" not in html:
            warnings.append("Presenter view detected, but no explicit clean audience/projection mode was detected.")

    return {
        "file": str(path),
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an HTML PPT deck.")
    parser.add_argument("html", help="Path to index.html or another HTML deck")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    path = Path(args.html).expanduser().resolve()
    if not path.exists():
        result = {"file": str(path), "ok": False, "errors": ["File not found."], "warnings": []}
    else:
        result = check_html(path)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"File: {result['file']}")
        print(f"OK: {result['ok']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARN: {warning}")

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
