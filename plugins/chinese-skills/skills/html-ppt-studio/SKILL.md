---
name: html-ppt-studio
description: HTML PPT 编辑工作室：生成可编辑和演示的 HTML PPT，支持图片包装、浏览器编辑状态与导出。 Create, edit, present, and export high-end HTML presentation decks. Use with Codex, Hermes, Claude Code, Cursor, or any file-capable coding agent when the user wants web PPT / HTML slides / editable presentations from outlines, approved images, PPT/PDF assets, browser edits, or saved edit-state files.
license: MIT
---

## 中文名称与用法

**中文名称：** HTML PPT 编辑工作室

**用途：** 生成可编辑和演示的 HTML PPT，支持图片包装、浏览器编辑状态与导出。

**调用示例：** 使用 $chinese-skills:html-ppt-studio 把这些确认好的页面图片包装成可演示的 HTML PPT。

上游：https://github.com/HZMLJX/html-ppt-studio 。固定快照：`b56a5d0d5aa7ea521da86d3fe02d667c694a7920`。原许可随包保留。

技能资源路径以当前加载的 SKILL.md 所在目录为准，不假定用户目录或缓存版本。软件和生成服务凭据由使用者按任务配置。


# HTML PPT Studio

## Overview

Create editable HTML-format presentations that feel like high-end web data stories, research reports, or investor briefings. The default workflow treats user-provided images as already approved page visuals, then builds a fast HTML shell with navigation, animation, editing, presenter view, and durable saved edits.

This skill is intentionally not a full PowerPoint clone. It supports the small set of editing operations that make HTML decks practical: text edits, moving/resizing elements, inserting prepared page visuals, inserting/deleting/copying/reordering pages, simple object insertion, undo/redo for common edits, and saving those edits so later agent/model-driven changes build on the user's exact manual version.

The core reason to include editing mode is WYSIWYG precision and token efficiency. Direct manual edits should behave close to normal PowerPoint habits and should not call a model. In-page AI modification must be scoped to the current slide by default and handled by a local edit service with visible task status. Whole-deck or complex changes should return to the chat workflow.

This repository is agent-compatible rather than Codex-only. Codex can load this file directly as a skill; Hermes, Claude Code, Cursor, or another coding agent can use the same instructions by reading `SKILL.md` and the referenced files. The required capability is not a specific model provider, but the ability to read/write local files, run scripts, modify HTML/CSS/JS, and verify browser output.

## Required References

Before generating or modifying a deck, read the relevant references:

- Always read `references/design-rules.md`; these rules have the highest priority.
- Read `references/runtime-modes.md` when creating a new deck, upgrading a deck, adding/removing presenter/editor/export capabilities, or explaining speed/token tradeoffs.
- For a new deck, read `references/style-scene-options.md` only when the user has not supplied a clear style, example, target deck, or specific page request.
- For browser-editable decks or "执行修改", read `references/editing-workflow.md`.
- For presenter view, screen projection, dual-window playback, or timer behavior, read `references/presenter-view.md`.
- Read `references/image2-workflow.md` only when the user explicitly asks to generate new images, rewrite image prompts, or use image2. Do not load it merely because the deck contains images.
- For non-Codex agents, read the matching adapter guide in `adapters/` when available. If no adapter exists, follow the generic rules in this file.

Use `scripts/validate_html_ppt.py` after creating or changing an HTML deck when feasible, but choose the lightest verification that matches the risk.

For a pure image deck or a folder of approved 16:9 slide images, prefer `scripts/build_image_deck.py` before hand-writing HTML. It creates a fixed-stage dark web PPT shell and avoids spending tokens reconstructing image contents.

For editable style selection, reuse the local preset library in `assets/style-presets/manifest.json` and its real page preview images. Do not browse, search, or generate new style thumbnails unless the user explicitly asks for new styles. Each preset includes a page-style preview, recommended skill, generation prompt, and preview source.

## Runtime Strategy

Separate slide content from reusable local runtimes:

- Fast Draft Mode: generate slide content quickly with basic navigation and page marks. Use this for initial creation and visual direction checks.
- Formal Presentation Mode: add presenter view, notes, timer, clicker/keyboard support, clean audience window, and export entry. Use this for meetings, classes, and finished talks.
- Full Editing Mode: keep all Formal Presentation features and add WYSIWYG editing, thumbnails, thermometer page rail, page operations, local save/sync, and current-slide page generation. Use this for precise revisions.

For integrating existing HTML decks, use the principle: preserve slide content, replace the runtime shell. Do not keep one full deck nested inside another full deck as the final result. Preserve source slide visuals, CSS animations, charts, images, and in-slide scripts when practical, but strip or hide source deck chrome such as playback buttons, edit panels, presenter panes, thumbnails, page rails, duplicate page numbers, and saved editing state. The final file should have exactly one unified `html-ppt-studio` runtime for playback, presenter view, editing entry, thumbnails, thermometer page rail, page numbers, and export.

When inserting pages from existing HTML files into an integrated deck, adapt the source file to the unified runtime instead of flattening or rewriting the source page. Preserve the source HTML structure, CSS, assets, animations, and in-slide scripts where practical; strip only source deck chrome that conflicts with the unified shell. Insert pages by the current actual slide order, then recompute slide order, page numbers, thumbnail labels, thermometer rail, presenter counts, and manifest totals from the resulting deck state. Avoid fixed-position deletion or insertion code that becomes wrong after pages are added or removed; prefer stable source ids, slide ids, and explicit insertion anchors.

When an integrated deck must preserve source HTML pages inside iframes, do not implement navigation by rewriting one iframe's `srcdoc` on every slide change. That causes reload flashes, stale-frame display, and default-slide jumps in some browsers. Use persistent per-slide frames or DOM layers instead: create/cache each slide container once, then switch visibility with an active class. Inside embedded source decks, force exactly one target slide visible at a time; disable source slide transition during integration and hide non-target slides with `display:none` to avoid fade-through remnants.

For embedded or saved-state slide HTML, keep the authored inner page as a fixed 1920x1080 stage and let the outer iframe/window/container scale that stage proportionally. Do not "fix" clipping by forcing the inner authored page to `100vw/100vh` with `transform:none`; that can turn blank margins into enlarged crop. The stable pattern is: inner slide owns the 1920x1080 design coordinate system, outer viewport performs fit-to-container scaling and centering.

When the user wants both speed and full capability, default to Fast Draft for first generation, then offer explicit upgrade actions. Upgrading should attach local runtime capability without regenerating slide content.

## Workflow

### 1. Detect Task

- New deck: user gives topic, outline, text, images, table, data, or scenario.
- Revise existing deck: user gives an HTML file/link or asks to adjust current deck.
- Execute browser edits: user says "执行修改", "保存网页编辑", or asks whether manual web edits took effect.
- Export/debug: user asks for PDF/PPTX/HTML output or print/export fidelity.

### 2. Start With Workflow Choice

Before generating a new deck or converting assets, ask for a workflow only when the user's path is unclear. If the user gives a specific page count, page type, existing assets, style, or direct modification request, proceed directly using the lowest-cost path that satisfies it.

Show this concise choice prompt:

```text
为保证效果并减少 token 消耗，默认认为你提供的图片/PPT 截图/image2 页面图已经是满意成稿，我不会再重绘或重新设计图片。

请选择制作路径：
A. 已有满意图片/PPT 快路径（推荐）：直接把图片做成 HTML PPT，只加导航、页码、演示者模式、编辑覆盖层，速度最快、token 最低。
B. 先生成 HTML 初稿，再由你插入 image2 图片：适合还没有全部页面图，需要边做边改。
C. 全 DOM 可编辑版本：文字图表尽量 HTML 化，后期可改性强，但耗时和 token 高。
D. 需要新图/重绘图片：才调用 image2 或生成图片提示词。
```

Default to A when the user provides a pure-image PPT/PDF, existing slide images, screenshots, or says the visuals are already satisfactory. Use `scripts/build_image_deck.py` for A whenever possible.

When the runtime mode is unclear, also explain the three runtime modes in one short prompt:

```text
请选择运行模式：
A. 极速初稿模式：最快，token 最低，只用于确认页面内容和视觉方向。
B. 正式演示模式：适合开会和授课，包含演示者视图、备注、计时器、翻页笔和导出。
C. 完整编辑模式：包含正式演示能力，并增加所见即所得编辑、缩略图、温度计页码、页面管理、保存同步。

可先用 A 快速生成，确认后升级到 B 或 C。升级不会重做页面内容，只增加本地运行时能力。
```

### 3. Start With Visual Choices

For a new deck with an unclear style, first show the user visual choices instead of asking only abstract style words:

1. Offer 3-5 style directions using preview cards or image references.
2. Offer 3-5 usage scenarios such as government briefing, policy training, investor report, industry research, product launch, internal workshop, or public talk.
3. Let the user choose style and scenario. If the user already specified both, proceed without delay.

The default visual direction for this skill is dark technology-finance data storytelling. Only move away from it when the user clearly chooses another style.

Skip detailed style-choice prompting when the user gives a clear style, asks for a small batch of specific pages, chooses A, or supplies approved images with a clear benchmark style. In that case, preserve the provided visual direction and only ask for missing essentials such as title, order, or output folder.

### 4. Generate Initial Draft

Build a runnable HTML deck:

- Fixed 16:9 stage, preferably authored at 1920x1080.
- Keyboard left/right navigation, one lower-right page index, and hash or query-state support.
- Presenter view support with timer and synchronized audience view only when the user needs live delivery.
- Use a lightweight HTML deck by default for small page batches, previews, and first drafts. Include the full editable runtime only when the user asks for browser editing, saved manual edits, object movement/resizing, page operations, presenter workflow, export workflow, or "执行修改".
- Do not silently remove previously requested capabilities such as presenter view, thumbnails, thermometer page rail, export entry, notes, timer, or clicker navigation when revising or upgrading a deck.
- Slides are authored as semantic DOM elements, not one giant raster image, except for deliberate image2 page-visual pages.
- Tables are redesigned into visual modules rather than pasted as plain tables.
- Include reduced-motion support.
- Do not create extra upper page numbers, repeated page marks, decorative English headers, invented subtitles, or vague filler labels. Page numbers must be generated once from the actual slide order and shown in the lower-right by default. Chinese-facing decks should not include meaningless English translations or explanatory small text such as "以政府可以理解的方式...", "理解来源", or similar planning labels unless the user explicitly supplied them as slide content.

Default fast path for prepared images:

- Assume uploaded/pasted/provided page images are already visually approved unless the user says otherwise.
- Do not call image generation tools, rewrite the image content, or critique the image design by default.
- Use prepared images as full-slide or major-page visuals and add only the needed HTML shell: stage, page marks, navigation, presenter view, editable overlay hooks, and light animation.
- For image-first decks, keep surrounding DOM minimal. Prefer one image layer plus optional editable title/notes/annotations instead of reconstructing every visible object.
- Match the benchmark feel of the user's approved dark HTML examples: carbon-black stage, fine grid, analytical report hierarchy, restrained red/orange/blue/teal accents, smooth web-style reveal, and no traditional PPT template look.
- Do not add decorative English labels, fake metadata, or invented course/report headers unless the user supplied them or the page function requires them.

Only suggest image2 when the user asks for new visuals or when a required visual is missing.

### 5. Browser Editing Contract

Editable decks must implement a real persistence path:

- Browser edits must not live only in temporary DOM state or localStorage.
- Exiting edit mode is a required save-and-commit action. After the user deletes slides, reorders slides, edits text, changes notes, moves/resizes objects, or changes simple styling, clicking the edit button again to leave edit mode means the user accepts the current edited state. The deck must persist that latest state automatically before playback, presenter view, export, or further model-driven edits continue.
- Do not fake this save. While the save is running, show an explicit "saving, do not close or switch files" status and temporarily block conflicting controls. Exit edit mode only after the state file is written successfully. If persistence fails, keep the deck in edit mode, show a clear failure message, and do not claim the edit has become durable.
- Provide a save/export payload that can be read by the executing agent, such as `deck-state.json`, `edits.json`, or a rewritten `index.html`.
- The saved state must include slide order, inserted/deleted slides, text changes, image paths or embedded images, element positions, sizes, and z-index where relevant.
- The saved state must include changed slide identifiers, or enough before/after metadata for the agent to compute them.
- Presenter notes are saved state too. Store notes by stable `slideId`, not only by page index or active textarea contents. Notes input should autosave or mark the slide dirty, and closing presenter view, switching modes, exporting, or reopening the deck must preserve the latest note text.
- On later modification, read the saved edited state first. Treat it as authoritative over the original generated HTML.
- If the deck is served from a browser and needs durable edits, include or start a local edit service that writes the state file next to `index.html` and to the served copy. Do not display "saved" unless the state file was actually written, or clearly label the result as browser-only temporary cache.
- Treat page numbers as derived state, never as permanent authored content. After inserting, deleting, or reordering slides, recompute every visible page number from the actual slide order before saving, exporting, rendering thumbnails, or updating presenter controls.
- Editing must be separated into three levels: direct WYSIWYG edits without model calls, current-slide in-page AI modifications through the local service, and global/complex changes handled in the chat.
- The deck UI must include a clear status/task window for saves and in-page AI submissions. Submitted slide-level tasks may continue while the user edits another slide; completion or failure notices must identify the slide and remain visible until the user confirms/dismisses them.

Keep edit tools limited and stable:

- Text edit.
- Move/resize image or text elements through explicit handles.
- Paste/insert/replace prepared images; local image data may be embedded as data URLs when single-file portability matters.
- Insert simple text/image/video reference objects on the current slide when the user needs to communicate layout intent.
- Insert/delete/copy/reorder slides.
- Save, export clean HTML, and support `Ctrl/Cmd+S` when feasible.
- Undo/redo for text, move, resize, add, delete, copy, reorder, and page operations when implemented.

Avoid building a broad design editor that slows every deck down.

When implementing page operations, update these surfaces together: slide page marks, thumbnail labels, right-side page rail, presenter jump controls, presenter current/total count, and any slide metadata array used for notes or titles.

Prefer a locked-layout plus freeform-object model:

- Author-approved page visuals, template backgrounds, grids, axes, decorative layers, and report chrome should remain locked unless the user explicitly asks to edit them.
- User-added or agent-added movable items should live in a dedicated edit layer with stable object ids.
- Native authored text or image areas may be edited as locked content slots when preserving layout fidelity matters.
- Only user-added/freeform objects need full move/resize handles by default; do not componentize every DOM node.
- If the user needs to freely reposition originally locked content, expose an explicit "unlock layout" operation for the current slide rather than silently making every element draggable.

### 6. "执行修改" Mode

When the user submits "执行修改":

1. Locate the latest persisted browser-edit state.
2. Verify that the user's manual edits are present before changing anything.
3. Identify the changed slides first. Use saved `changedSlides`, `dirtySlides`, inserted/deleted slide ids, or run `scripts/detect_changed_slides.py` on the saved edit-state payload.
4. Confirm the target slide set in the work log before modifying files.
5. Merge manual edits only for the changed slides into the HTML source or regenerate only those slide sections from the saved state.
6. Apply requested page-specific changes only to the affected slides. If a request is truly global, separate global shell changes such as CSS/theme/navigation from slide content changes.
7. Preserve manual slide order, inserted pages, pasted/prepared page visuals, and user-edited text unless the new request directly changes them.
8. Run validation and, when possible, browser screenshot checks on changed slides plus any global shell affected by the edit.
9. Return the exact URL/file path with cache-busting query string if served locally.

If the latest manual edits cannot be found, stop and explain the exact missing file/state instead of guessing from an older version.

### 7. Export Expectations

HTML is the primary editable artifact. PDF/PPTX exports are secondary:

- PDF export should capture browser presentation mode, not editor chrome.
- Prefer high-fidelity screenshot PDF export for integrated HTML decks, especially decks that contain iframes, animations, canvas/WebGL, base64 assets, or source pages with their own responsive scripts. Use a local export service to open the clean audience view, render each slide in the current persisted order, capture one 16:9 screenshot per slide, and compose those screenshots into a PDF.
- Browser print/PDF is acceptable only for simple print-ready DOM decks. Do not use browser `window.print()` as the default for integrated HTML decks; it often prints only the current SPA slide or loses iframe/animation/layout content.
- PDF export must include every slide in the current persisted slide order. Verify that the generated PDF page count equals the current slide count.
- PPTX export is acceptable as either editable text/shapes where practical or high-fidelity images when editability is less important. If the user requires editable PPTX, state the fidelity tradeoff before exporting.
- Never silently rename an XML/debug payload as `.pptx`.

### 8. Presenter View Expectations

When a deck includes presenter view:

- The audience window must show only the clean slide stage, without notes, editor chrome, controls, thumbnails, timers, or debugging UI.
- The presenter window may show current slide, next/previous controls, speaker notes, thumbnails, and a timer.
- Presenter view must be implemented as a separate presenter window plus a separate clean audience window. Do not treat a same-window overlay with notes/timer as sufficient, because external projection or screen sharing can expose presenter-only information to the audience.
- When the user opens presenter view, open or prompt for a clean audience window such as `?mode=audience&slide=current`. The expected projection workflow is: use extended display mode, drag the audience window to the external screen, and keep the presenter window on the speaker's computer.
- Presenter preview must render from the same persisted slide source as normal/audience playback. If slide HTML is generated from saved state, pass the stable `slideId` through that same renderer; do not use a shortcut `currentSrcdoc()` path that bypasses `deck-state.json` or slide overrides.
- Presenter preview iframe/container should be `width:100%; height:100%; transform:none`. Let the slide's own 16:9 fit logic handle scaling. Do not apply a second outer transform on an already responsive iframe, or the presenter preview can crop while the audience window looks correct.
- Speaker notes must be editable and durable. Save notes by stable `slideId` into the same state file used by editing, and force-save or debounce-save before closing presenter view.
- Because browser security prevents a page from silently hiding the address bar, the clean audience window should include a low-cost "enter fullscreen presentation" affordance. Show a restrained button or click prompt only in audience mode; on click call `requestFullscreen()`, then hide the affordance. Hide it automatically during PDF export, print, and after fullscreen is active.
- Add elapsed-time information in the presenter view, preferably in an unused lower-right area.
- Provide pause/resume for the elapsed timer in presenter/editing workflows. In Full Editing Mode, the presenter may pause the timer while editing text, notes, images, or page order, then resume before continuing the talk.
- Presenter navigation must synchronize the audience window to the same slide.
- Audience navigation should either be disabled or routed through the same shared slide state to avoid desynchronization.
- Do not bind Space to slide navigation. Space is used by text editing, Chinese IME confirmation, form controls, and accessibility interactions; use ArrowRight/ArrowLeft/PageDown/PageUp and clicker-compatible keys instead.
- Use a shared state mechanism such as `BroadcastChannel`, `localStorage` event, `postMessage`, or URL hash/query updates, and choose the simplest one that works in a single-browser local deck.

## Quality Bar

- Verify that slides are visible, not blank, and not clipped.
- Verify that presenter and audience windows stay synchronized during next/previous navigation.
- Verify that audience projection is clean slide content only.
- Verify that presenter timer is visible in presenter view but absent from audience view.
- Verify that timer pause/resume works while editing and that Space does not change slides in edit fields, notes, text boxes, or normal deck focus.
- Check that editor sidebars do not invade the 16:9 slide stage.
- Check that thumbnails represent the real slide state.
- Check that pasted images do not stick to the mouse after placement.
- Check that text remains individually editable when it was authored as text.
- For significant deck changes, use browser screenshots on at least the changed slides.

Use tiered verification:

- Tiny text/content edits: run syntax or static validation only.
- Single-page visual edits: validate HTML and screenshot only the changed page when feasible.
- Small lightweight drafts of about 10 slides or fewer: run static validation plus one or two representative browser screenshots, unless the user asks for proof on every page or the shared layout system changed in a risky way.
- New decks, layout-system changes, presenter/export changes, and editing-runtime changes: run full validation and browser checks.
- Do not run browser automation, image generation, web search, plugin installs, or multi-page screenshots unless they materially reduce risk.

## Speed Rules

To keep revisions fast and low cost:

- Use the user's exact requested pages and content only.
- Do not add decorative labels, extra sections, fake metadata, invented English headers, or unrelated examples.
- Do not browse, search, generate images, install tools, or inspect unrelated files unless the user asks or correctness requires it.
- Prefer one self-contained HTML file with compact CSS/JS for small page batches.
- Keep animations CSS-only and minimal unless the slide needs data-driven animation.
- After any browser edit/save, first determine the changed slide ids and only load or rewrite those slide sections.
- Change only the pages affected by the user request.
- If the user edited slide 7, do not reread/regenerate the whole deck unless shared CSS, navigation, export, or data schema must change.
- Keep a structured slide data model or edit-state file when possible.
- Avoid rewriting a massive single HTML file for one small visual change unless necessary.
- Prefer compact CSS variables and reusable layout classes over repeated inline CSS.
- For prepared image decks, do not inspect or describe every visual detail unless needed. Treat image placement, sizing, slide order, and simple overlays as the main edit surface.
- Use image2 only on explicit request or when a required visual asset is missing. Existing images are accepted as the author's source of truth.
- For all-image decks, use the bundled image-deck builder or a similarly small template; avoid generating bespoke HTML for every page unless the user needs per-object editability.

## Open Source Notes

When packaging this skill for GitHub, include the root `README.md`, keep examples free of private API keys, and document how to set API keys through environment variables. The skill should work without hardcoding any local username or absolute project path.
