# Runtime Modes

The skill should separate slide content from reusable local runtimes. This is the main strategy for speed and token efficiency.

## Core Principle

Do not regenerate the full presenter, editor, thumbnail, export, and save-service code for every deck. Generate slide content quickly, then attach or upgrade to a reusable runtime when the user needs more capability.

Default architecture:

```text
slide content layer + reusable local runtime + optional local edit/export service
```

## Mode 1: Fast Draft Mode

Purpose:

- Create or review the visual/content direction quickly.
- Spend the fewest tokens.
- Avoid loading heavy editor/export/presenter code.

Includes:

- Fixed 16:9 stage.
- Keyboard navigation.
- Basic page marks.
- Light animation.
- Clean HTML preview.

Does not include by default:

- Presenter view.
- Full WYSIWYG editing.
- Export workflow.
- Thumbnail/page-management runtime.
- Local save service.

User-facing explanation:

```text
当前是“极速初稿模式”：用于快速生成和预览页面，速度最快、token 最低。适合确认内容和视觉方向。
下一步可升级为：
1. 正式演示模式：增加演示者视图、备注、计时器、翻页笔支持和导出。
2. 完整编辑模式：在正式演示模式基础上增加所见即所得编辑、缩略图、温度计页码、页面管理和保存同步。
```

How to enter next mode:

- User says or clicks: `升级为正式演示模式`.
- User says or clicks: `进入完整编辑模式`.

## Mode 2: Formal Presentation Mode

Purpose:

- Use the deck in real meetings, training, lectures, or public talks.
- Preserve polished playback while avoiding full editor overhead.

Includes:

- Everything in Fast Draft Mode.
- Full-screen playback.
- Presenter view.
- Speaker notes.
- Elapsed timer.
- Current/next navigation.
- Audience window with clean slide-only output.
- Presenter/audience synchronized page changes.
- Keyboard and clicker/page-turner support through ArrowRight, ArrowLeft, PageDown, PageUp, and common remote-key equivalents.
- Do not use Space for slide navigation. Space conflicts with text editing, Chinese IME confirmation, focused buttons, notes fields, and browser accessibility behavior.
- Export entry for clean HTML, PDF, and PPTX when the local export service is available.

Does not include by default:

- Heavy WYSIWYG editing panels.
- Drag/resize object editor.
- Thumbnail page-management editing unless explicitly requested.

User-facing explanation:

```text
当前是“正式演示模式”：适合定稿后演讲和会议使用，包含演示者视图、备注、计时器、翻页笔支持和干净观众窗口。
如果还需要直接改文字、图片、页面顺序或保存网页编辑，请升级为“完整编辑模式”。
```

How to enter next mode:

- User says or clicks: `进入完整编辑模式`.
- User says or clicks: `开启编辑`.

## Mode 3: Full Editing Mode

Purpose:

- Make precise WYSIWYG changes quickly.
- Reduce repeated natural-language modification cycles.
- Persist browser edits so the agent can update only changed slides later.

Includes:

- Everything in Formal Presentation Mode.
- Left-side edit entry outside the slide stage.
- Right-side thumbnail rail and thermometer/page rail.
- Text editing.
- Object/image selection, move, resize, replace, and stable button-based fallbacks when pointer drag is unreliable.
- Page operations: insert above/below, delete, duplicate, reorder, recompute page numbers.
- Current-slide page generation input.
- Status/task window.
- Durable save to `deck-state.json`, `edits.json`, or rewritten HTML through a local edit service.
- Export workflow that hides editor chrome.

Editing levels:

- Direct WYSIWYG edits: no model call.
- Current-slide page generation/AI modification: local service sends only the current slide or explicit changed slide set.
- Global complex changes: return to chat.

User-facing explanation:

```text
当前是“完整编辑模式”：适合精修页面。普通改字、移动、缩放、换图、删页和排序不调用模型；页面生成默认只处理当前页；全局复杂修改请回到对话框。
保存后刷新仍应看到最新内容。
```

## Upgrade Rules

- Never remove capabilities the user already explicitly asked to preserve when upgrading modes.
- Upgrading from Fast Draft to Formal Presentation must preserve all slide content and visual design.
- Upgrading from Formal Presentation to Full Editing must preserve presenter view, notes, timer, audience sync, keyboard/clicker navigation, export entry, thumbnails, and page marks.
- Downgrading/exporting to a clean presentation should remove editor chrome but preserve presenter features if the user requests an演示版本.
- If a requested capability needs the local service and it is not installed/running, say so clearly and provide the next action instead of pretending the feature works.

## Local Dependency Strategy

Install heavier dependencies once per skill/workspace, not per deck. The generated deck should import or reference reusable runtime files where possible.

Reasonable optional dependencies:

- `playwright`: browser verification, screenshots, clean PDF export.
- `pptxgenjs`: PPTX generation.
- `express` or a similarly small server: local save/export service.
- `sharp`: thumbnails and image processing.
- `sortablejs`: thumbnail drag sorting.
- `interactjs` or `moveable`: object move/resize when a full editor is required.
- `html-to-image`: thumbnail or slide image generation.
- `jszip`: package/export bundles.

Avoid making these dependencies mandatory for Fast Draft Mode. Fast Draft should still work as a single HTML file.

## Mode Choice Prompt

When creating or upgrading a deck, show a concise mode explanation if the mode is unclear:

```text
请选择运行模式：
A. 极速初稿模式：最快，token 最低，只用于确认页面内容和视觉方向。
B. 正式演示模式：适合开会和授课，包含演示者视图、备注、计时器、翻页笔和导出。
C. 完整编辑模式：包含正式演示能力，并增加所见即所得编辑、缩略图、温度计页码、页面管理、保存同步。

可先用 A 快速生成，确认后升级到 B 或 C。升级不会重做页面内容，只增加本地运行时能力。
```
