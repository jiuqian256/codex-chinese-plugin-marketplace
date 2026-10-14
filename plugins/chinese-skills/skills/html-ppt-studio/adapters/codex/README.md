# Codex Adapter

Codex can use `html-ppt-studio` directly as a skill.

## Install

Copy the repository folder into the Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R html-ppt-studio ~/.codex/skills/html-ppt-studio
```

Then restart Codex or reload skills.

## Trigger

Use prompts such as:

```text
使用 html-ppt-studio，生成一个可编辑、可演示的 HTML PPT。
```

or:

```text
使用 html-ppt-studio，读取 deck-state.json，只修改我手动编辑过的页面。
```

## Codex-Specific Rules

- Load `SKILL.md` first.
- Load only the relevant reference files for the current task.
- Prefer the bundled scripts for validation and image-deck wrapping.
- If browser edits exist, read `deck-state.json` before modifying HTML.
- Preserve the runtime unless the user explicitly asks to change playback, presenter, editing, or export behavior.
