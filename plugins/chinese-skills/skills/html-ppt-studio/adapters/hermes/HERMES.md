# Hermes Adapter

Use this guide when running `html-ppt-studio` from Hermes or another local agent that can read files, edit code, and run commands.

## Required First Reads

For every task, read:

1. `SKILL.md`
2. `references/design-rules.md`

Then read only the references needed for the task:

- Editing or saved browser edits: `references/editing-workflow.md`
- Presenter view, projection, audience window, timer: `references/presenter-view.md`
- Runtime choice or speed/token tradeoffs: `references/runtime-modes.md`
- Style selection: `references/style-scene-options.md`
- New image generation or image prompts: `references/image2-workflow.md`

## Operating Contract

- Treat `deck-state.json` as the source of truth when it exists.
- If manual browser edits were saved, identify changed slides before changing files.
- Modify only affected slides unless the request is global.
- Do not regenerate approved image pages by default.
- Preserve presentation runtime features: playback, presenter view, clean audience window, notes, timer, thumbnails, page rail, save state, and export.
- Run validation or browser checks appropriate to the risk.

## Model Choice

Hermes may use any model provider. The model should be able to:

- Follow long instructions.
- Edit HTML/CSS/JavaScript reliably.
- Preserve existing code while making scoped changes.
- Work with local files and generated artifacts.

No OpenAI-specific API is required unless the selected model or image generator needs it.

## Suggested User Prompt

```text
Use html-ppt-studio. Read SKILL.md and the relevant references first.
If deck-state.json exists, treat it as authoritative.
Only modify the affected slides unless I ask for a global runtime change.
```
