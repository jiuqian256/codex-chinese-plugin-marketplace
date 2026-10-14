# Generic Agent Adapter

This adapter is for Claude Code, Cursor, OpenCode, or another file-capable coding agent.

## Minimum Capabilities

The agent must be able to:

- Read Markdown instructions.
- Read and write local files.
- Modify HTML/CSS/JavaScript.
- Run local scripts.
- Optionally run browser automation for screenshots and PDF export.

## Task Routing

- New deck: read `SKILL.md`, `references/design-rules.md`, and optionally `references/runtime-modes.md`.
- Existing deck revision: read `SKILL.md`, `references/design-rules.md`, and inspect the target deck.
- Saved browser edits: read `references/editing-workflow.md` and `deck-state.json` before editing.
- Live presentation or projection: read `references/presenter-view.md`.
- Approved image deck: prefer `scripts/build_image_deck.py`.

## Non-Negotiable Rules

- Do not hide failed saves.
- Do not rely on localStorage alone for browser edits.
- Do not add duplicate page numbers.
- Do not add meaningless English metadata or decorative course labels.
- Do not break presenter/audience window separation.
- Do not rewrite the whole deck for a small slide-level change unless shared runtime code must change.
