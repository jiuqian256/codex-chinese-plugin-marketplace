# Editable HTML Deck Workflow

The core purpose of browser editing is WYSIWYG: let users make precise slide changes directly on the page, reduce ambiguous natural-language back-and-forth, and reduce token usage by making changed slides explicit. Edits must become durable source, not temporary display state.

Editable HTML decks should preserve normal PowerPoint-like habits where practical: users should be able to select an object, edit text, move/resize visual elements, manage pages, save changes, and receive clear feedback that the change has actually taken effect.

Full Editing Mode must be layered on top of Formal Presentation Mode. Do not add editing by replacing or removing presenter view, notes, timer, clicker navigation, audience sync, export entry, thumbnails, thermometer page rail, or page marks that the user has asked to preserve.

## Editing Levels

Use three distinct editing levels. Do not blur their responsibilities.

### Level 1: Direct WYSIWYG Editing, No Model

Use this for ordinary manual edits:

- Change text.
- Move or resize text, images, and simple objects.
- Replace or paste an image.
- Add, delete, duplicate, or reorder pages.
- Adjust simple style controls exposed by the editor.

These edits must not call a model. They should be saved by the local deck edit service to real source state such as `index.html`, `deck-state.json`, or `edits.json`. This is the fastest path and should be the default way to handle small layout/content tweaks.

### Level 2: In-Page AI Modification, Local Service Scoped

Use this when the user types an instruction inside the deck page itself.

- The instruction is scoped to the current slide by default.
- Send only the current slide state, or the explicit changed slide set, to the model whenever possible.
- The local service owns the request queue, writes the returned result to durable source, and reports status back to the deck UI.
- Do not let a current-slide instruction silently expand into unrelated pages.
- If a request needs more than the current slide, ask for confirmation or route it to Level 3.

This level exists to avoid scope creep, long runtimes, and unnecessary token use.

### Level 3: Global Or Complex Modification, Conversation-Driven

Use the chat/conversation for broad changes:

- Whole-deck style changes.
- Chapter restructuring.
- Cross-slide consistency rewrites.
- New content generation across multiple pages.
- Repairs that require inspecting shared CSS, scripts, export logic, or the full slide data model.

The page UI may provide a button or message that tells the user to return to the chat for this class of change. Do not attempt large global transformations through a small per-slide input box.

## Editable Features To Support

Keep the editor small:

- Provide one clear edit entry on the presentation page. Clicking it should open an edit hub with separate mode buttons instead of mixing all tools together.
- The edit hub should separate common use cases: quick text edit, object/image edit, page management, AI page-level modification, save/sync, and exit edit mode.
- Select text and edit it.
- Select image/text elements and move them through explicit handles or stable keyboard increments.
- Resize selected elements with handles or keyboard increments.
- Paste or insert images.
- Replace an existing selected image through paste, double-click file picker, or an explicit replace action when feasible.
- Insert simple text, image, or video reference objects on the current slide.
- Insert a blank slide above or below the selected thumbnail.
- Copy or duplicate the selected slide.
- Delete a slide.
- Drag thumbnails to reorder slides.
- Save edits.
- Export a clean standalone HTML file with editor-only controls removed.
- Undo/redo common edit operations.

Avoid full design-tool scope such as complex shape libraries, arbitrary layer effects, or complete PPT clone behavior unless the user explicitly asks.

## Persistence Contract

Every editable deck must have at least one durable save mechanism:

1. Save to `deck-state.json` or `edits.json` next to `index.html`.
2. Or rewrite a generated `index.edited.html`.
3. Or expose a downloadable JSON/HTML that the agent can ingest.

Local-only visual changes are not enough. Browser state in memory or localStorage is only a cache.

Exiting edit mode must be treated as a save-and-commit boundary. When the user clicks the edit entry again to leave edit mode, this means they accept the current manual edits. Persist the latest state first, then exit edit mode only after the save succeeds. While saving, show an explicit "saving, do not close or switch files" status and temporarily block conflicting controls such as playback, presenter view, export, and edit toggles.

When the user leaves edit mode, opens playback, opens presenter view, or starts export, persist the latest state first. The persisted state is then the source of truth for the current browser session, exported HTML/PDF/PPTX paths, and future agent edits. If the local service cannot write the state file, keep the user in edit mode, show an explicit failure, and do not imply the edit has become durable.

Presenter notes are part of the same persistence contract. Notes edited in presenter view must be saved to the local state file, preferably keyed by stable `slideId`, and restored after closing and reopening the deck. Do not store notes only in the active textarea, page index, or localStorage cache.

For local HTML decks, prefer a tiny local edit service over fake in-page save buttons. The service should write `deck-state.json` next to the canonical `index.html` and, when a separate served copy exists, write the same file next to the served `index.html`. The executing agent must read this state file before applying any later user request.

## Edit Entry And Status Feedback

Editable decks should feel closer to normal PPT editing habits:

- Keep a compact "编辑" entry visible outside or near the slide stage without covering important content.
- Prefer placing the edit entry in an outer side rail, not on top of slide content. If the current viewport leaves no safe outer margin, shift or resize the slide stage so the edit menu remains outside the 16:9 page.
- Full Editing Mode must show a clear runtime badge such as `C 完整编辑模式` so the user always knows whether they are in A/B/C mode. This badge is a status reminder, not a button: keep it visually distinct from playback/edit controls, avoid borders or button-like chrome, keep the text on one line, and place it outside the 16:9 slide stage without overlapping the control rail.
- After entering edit mode, show a small mode hub rather than exposing every tool at once.
- Mode buttons should be explicit:
  - `文字编辑`: edit existing text slots and simple text boxes.
  - `图片/对象`: move, resize, replace, or delete images and freeform objects.
  - `页面管理`: insert, delete, duplicate, or reorder slides.
  - `页面生成` or `AI修改`: submit a page-level instruction, ideally scoped to the current slide by default.
  - `风格`: choose a preset style and choose whether it applies only to the current slide or the whole deck.
  - `保存同步`: persist edits to the real deck source or edit-state file.
  - `退出编辑`: return to clean playback.
- The active mode button should be visually distinct.
- Mode buttons must have a visible effect on the deck. Do not implement buttons that only change status text. For example, text mode should make text slots editable or visibly selectable, object mode should highlight/select movable objects, page mode should expose page operations or a clear page-management state, and AI mode should show the current-slide input area.
- Only one editing function may be active at a time. If the user clicks another edit mode or a runtime action such as export, presenter view, or playback while an edit mode is active, auto-save the current mode state when possible, close the current mode, then open the requested mode. Do not leave edit, export, presenter, page-generation, or style panels active simultaneously.
- Object/image mode must provide real controls for selected images or objects: move, resize, replace when feasible, and delete. If pointer drag is unstable, use button-based movement and scaling as the reliable fallback.
- Page-level AI generation and style selection should use a bottom workbench outside the 16:9 stage when screen space allows. The slide may move slightly upward, but the input panel must not cover important slide content.
- The style workbench should contain locally preconfigured visual style cards, not text-only descriptions. Use `assets/style-presets/manifest.json` and its real page preview images as the default local library. The preview should look like an actual finished PPT/HTML slide page, not an abstract icon or simplified schematic. Selecting a style records the style id, recommended skill, generation prompt, and scope: current slide or global.
- Style presets must be installed with the skill so the deck can show visual choices immediately. Do not spend tokens searching for style references or generating style thumbnails during ordinary deck edits.
- Menu width should fit its labels and avoid large empty horizontal padding. Keep button sizes visually consistent across the edit hub.
- Thumbnail page operations must follow the confirmed pattern: in normal/playback state, thumbnails and the thermometer page rail are visible but page-operation controls are hidden; after clicking edit, each thumbnail exposes compact insert-up and insert-down controls, plus a delete `X` in the upper-right corner. Do not use a third inline delete button between up/down controls.
- Thumbnail previews must render the actual slide page rather than blank placeholders or rough cards. Do not show source/title text inside each thumbnail; keep spacing compact, with only a small page-number badge when needed. Implement each thumbnail as a container with child buttons, not as a button containing other buttons, so the upper-right delete `X` reliably deletes that whole slide.
- Thumbnail insert, delete, and reorder operations must update the same slide-order state used by the stage, page numbers, thumbnails, thermometer rail, presenter preview, and export. Dragging thumbnails to reorder pages should be enabled only in edit mode. After exiting edit mode, the updated order should remain effective in the current deck session and in any saved/exported state.
- Every save or AI-submit action must produce visible status feedback on the page:
  - queued/submitted
  - saving
  - processing
  - success
  - failure with a short actionable reason
- Status feedback must make it obvious whether a change is only temporary, saved locally, or persisted to the real deck source.
- Success and failure notices for submitted edits must remain visible until the user explicitly confirms/dismisses them. Do not auto-hide completion notices in a way that lets the user miss the result.
- Users may submit an edit on one slide, then switch to another slide and continue editing while the previous request is still processing. The status system must keep per-slide task identity so the completion notice says which slide succeeded or failed.
- A submitted task should include at least: task id, slide id, slide number at submission time, submitted instruction or action summary, status, timestamp, and result/error message.
- The UI should provide a compact task/status window or queue. It may be docked outside the slide stage or in a non-invasive overlay, but it must not cover important slide content.
- The task/status window should support multiple pending page-level tasks. Each completed task should require user confirmation before being removed from the visible list.
- For direct manual edits, saving should not call a model. It should only persist changed state and refresh the current view.
- For AI page-level edits, send only the current slide or explicit changed slide set when possible.
- If a deck is a lightweight preview and does not include the local edit service, the edit hub must say so clearly instead of pretending that save succeeded.

The saved state should include:

- Deck title and build id.
- Slide order.
- Slide ids.
- Changed slide ids, preferably as `changedSlides` or `dirtySlides`.
- Inserted slides.
- Deleted slides.
- Text content changes.
- Element positions and sizes in 1920x1080 coordinates.
- Image sources, filenames, or embedded data URLs.
- Z-index/layer order when relevant.
- Notes/speaker notes when relevant.
- Notes should be stored by stable slide id, for example `"notes": { "s07": "..." }`, not by visible page number.

When single-file portability is more important than file size, pasted/local images may be stored as data URLs. When file size matters, write image assets next to the deck and store relative paths in the saved state. In both modes, record the image dimensions and placement explicitly.

## Changed-Slide Detection

To improve speed and reduce token usage, every save should make changed pages explicit.

Preferred state fields:

```json
{
  "changedSlides": ["s05", "s09"],
  "insertedSlides": ["s48"],
  "deletedSlides": ["s12"],
  "slideOrderChanged": false
}
```

If explicit fields are not available, compute changed slides from per-element edits:

- Text edit: changed slide = the edited element's `slideId`.
- Geometry edit: changed slide = the moved/resized element's `slideId`.
- Image paste/replace: changed slide = the image element's `slideId`.
- Slide insertion/deletion/reorder: changed slide set = inserted/deleted slide ids plus neighboring slides whose page numbers or transitions may change.
- Global theme/navigation/export changes: mark as `global`, then avoid touching slide content unless needed.

When operating as the agent, announce or log the target slide set before editing:

```text
Changed slides detected: s05, s09. I will only update these slide sections plus shared CSS if required.
```

Use `scripts/detect_changed_slides.py` when the state payload is JSON and the changed slide set is not obvious.

## Page Number Reconciliation

Page numbers are derived from the current slide order. Do not trust page marks copied from a previous HTML snapshot after an insert, delete, or thumbnail reorder.

After any page operation:

- Recompute the total from the actual slide DOM or slide data model.
- Rewrite every visible slide page mark to `NN / total` in current order.
- Rebuild thumbnail labels and right-side rail page buttons from the same order.
- Update presenter jump dropdowns, page-number inputs, current/total counters, and slide metadata numbers.
- Run this reconciliation before browser save, HTML export, PDF export, and PPTX/XML export so persisted files match what the user sees.

Use deck-scoped slide queries. If thumbnails clone slide DOM, never build the slide list with a global `document.querySelectorAll(".slide")`; use a dedicated deck root and `:scope > .slide` or an equivalent direct-child query so thumbnails are not counted as real slides.

## PDF Export

For integrated HTML decks, prefer high-fidelity screenshot PDF export over browser print.

Browser `window.print()` normally prints only the currently visible slide in single-page web-app decks, and it can lose content from iframes, animation initial states, canvas/WebGL, filters, responsive scripts, or base64 asset timing. Do not use browser print as the default export path for complex integrated decks.

Use a local export service for screenshot PDF:

1. Read the latest persisted slide state first.
2. Open the deck in clean audience/publish mode.
3. Render each slide in the current slide order at a fixed 16:9 viewport.
4. Wait briefly for page scripts, fonts, images, and animation reveal states.
5. Capture one screenshot per slide.
6. Compose screenshots into a static PDF.

This produces a non-editable, static PDF. That tradeoff is acceptable for high-fidelity sharing, printing, and archiving. HTML remains the primary artifact for animation and interaction.

Verify PDF export by checking:

- Current runtime slide count.
- Screenshot count.
- Generated PDF page count when feasible.

All three counts should match.

## Object Model And Locked Layout

Use two edit surfaces:

1. Locked content slots for authored deck content whose layout should stay intact.
2. Freeform objects for user-added or agent-added movable content.

Locked slots:

- Use stable identifiers such as `data-edit-slot`, `data-slot-type="text|image|metric|table-cell"`, and `data-slot-locked-layout="true"` when the page has a designed template or approved image-first layout.
- Slots may support text replacement, image replacement, rich-text formatting, undo/redo, save, and export cleanup.
- Slots should not get move/resize handles by default; this prevents users from accidentally breaking a carefully designed page.

Freeform objects:

- Put movable objects inside a dedicated edit layer such as `.slide-edit-layer`.
- Give every object a unique document-wide id such as `data-oid="s07-o03"` and a type such as `data-object-type="text|image|video|graphic"`.
- Each freeform object should have explicit move, resize, and delete controls. Do not use the object body itself as the drag handle for images or videos.
- Keep media internals non-draggable (`pointer-events: none` on the inner image/video where practical) and move the outer object frame.
- Use percentage-based left/top/width/height or stage-coordinate geometry consistently, and convert to the canonical save format on save/export.

Unlocking layout:

- If the user needs to reposition authored locked content, provide an explicit current-slide "unlock layout" or "convert to movable objects" operation.
- Unlocking should copy editable slots into freeform objects in the edit layer and should be undoable.
- Keep backgrounds, grids, axes, tick marks, decorative SVG paths, textures, animation wrappers, and pure layout containers locked.

## Interaction Model

Selection and movement:

- Support single selection by click.
- Support multi-select with Ctrl-click or Shift-click when implemented.
- Drag only from explicit move handles for image/video/reference objects. Text objects may allow body drag only when not editing text.
- Clicking blank slide area should clear selection without moving anything.

Resize:

- Provide visible corner handles and, when practical, side/bottom edge handles for image/video objects.
- Maintain aspect ratio for image/video by default unless the user intentionally drags a side handle or disables aspect lock.
- Provide button-based resize actions such as enlarge/shrink when pointer drag is unstable in the host browser.

Alignment:

- Lightweight snapping is useful and should stay optional: snap to slide center and other object edges/centers within a small threshold.
- Avoid snapping to outer slide edges by default; it causes unexpected jumps near boundaries.

History:

- Maintain undo/redo commands for `textEdit`, `moveObject`, `resizeObject`, `addObject`, `deleteObject`, `replaceMedia`, `copySlide`, `insertSlide`, `deleteSlide`, and `reorderSlides` when these actions exist.
- Pushing a new command should clear the redo stack.
- Keyboard shortcuts should be disabled while the user is typing in text fields or contenteditable regions, except text-native shortcuts.

Text formatting:

- A compact rich-text toolbar may include bold, italic, font family, font size/scale, and color.
- Toolbar controls should preserve the text selection where possible. Use `mousedown.preventDefault()` or equivalent so clicking toolbar buttons does not blur the text box before applying formatting.
- If full rich-text support is too costly, keep plain text editing stable and do not expose unreliable formatting controls.

## "执行修改" Agent Procedure

When the user asks to execute web edits:

1. Find the current HTML deck and latest saved edit-state file.
2. Inspect the saved state and confirm the user's expected changes are present.
3. If the saved state is missing, report the exact missing artifact and do not regenerate from an older deck.
4. Identify changed slide ids before reading or rewriting slide content.
5. Apply saved edits into the canonical source only for changed slides.
6. Then perform any new user-requested adjustments only for those slides, unless the request is explicitly global.
7. Preserve user manual edits unless directly superseded.
8. Update build id or cache-busting version.
9. Verify changed pages in a browser.

## Common Bugs To Prevent

- Image sticks to mouse after paste or resize.
- Integrating existing HTML decks by nesting the entire source deck, leaving duplicate playback/edit/presenter controls, thumbnails, page rails, or old saved edit state visible inside the final deck.
- Pasted images are inserted too small or without explicit width/height, making resizing feel broken.
- Replacing media creates duplicate invisible images or leaves stale file inputs in exported HTML.
- Text elements inherit drag styles such as `user-select: none`, making text deletion or selection unreliable.
- Resize handles are inserted inside `contenteditable` text nodes and interfere with Backspace/Delete.
- Empty text boxes cannot be removed after the user deletes all text.
- Image resizing depends on one small bottom-right handle, making it feel like resizing is broken. Prefer visible edge/corner handles or a clearly selectable bounding box.
- Image body drag creates sticky cursor or jumping. For pasted/reference images, clicking the image body should only select it. Move images through an explicit move handle, and provide button-based zoom controls such as enlarge/shrink/delete as a stable fallback to drag-resize.
- Text is flattened into a raster image when it should remain editable.
- Editor chrome appears in print/PDF.
- Editor-only upload buttons, resize handles, selected-state classes, file inputs, and debug controls remain in exported HTML.
- Thumbnail is a rough card rather than a true miniature of the slide.
- Thumbnail clones are counted as real slides because slide queries are global instead of deck-scoped.
- Sidebar overlaps or enters the 16:9 slide stage.
- Thumbnail panes show horizontal scrollbars or place delete buttons too close to scrollbars, causing accidental page deletion.
- Pressing letter keys inside an input triggers global shortcuts.
- Pressing Space while editing text or confirming Chinese IME triggers slide navigation. Do not bind Space to next/previous slide; reserve it for editing, form controls, buttons, and accessibility behavior.
- Timer keeps running while the presenter pauses to edit notes, text, images, or page order. Full Editing Mode should provide a visible pause/resume control for elapsed time.
- Page number floats in inconsistent locations.
- Manual edits are visible in browser but invisible to the executing agent because only localStorage changed.
- Presenter notes disappear after closing presenter view because they were only kept in a textarea or keyed by page index instead of stable `slideId`.
- Presenter preview crops while the audience window is correct because the preview uses a separate srcdoc/render path or applies an extra iframe scale.

For editable text, override drag CSS with text-friendly styles (`cursor: text`, `user-select: text`, normal touch action). Add resize handles only to media/free-image elements unless a non-intrusive external handle system is implemented. If a selected text element is empty and the user presses Backspace/Delete, remove the text box itself.

## Suggested DOM Contract

Use stable attributes:

```html
<section class="slide" data-slide-id="s07">
  <h2 data-edit-slot="s07-title" data-slot-type="text" data-slot-locked-layout="true">...</h2>
  <div class="slide-edit-layer" aria-hidden="true">
    <div class="slide-object" data-slide-object data-oid="s07-o01" data-object-type="image">
      <button type="button" class="slide-object-move" aria-label="Move object">Move</button>
      <button type="button" class="slide-object-delete" aria-label="Delete object">×</button>
      <button type="button" class="slide-object-resize" aria-label="Resize"></button>
      <div class="slide-object-graphic">
        <img src="images/reference.png" alt="" />
      </div>
    </div>
  </div>
</section>
```

Save element geometry in stage coordinates:

```json
{
  "slideId": "s07",
  "elementId": "s07-image-1",
  "x": 960,
  "y": 220,
  "w": 720,
  "h": 420,
  "z": 4
}
```

## Print And Export

When exporting PDF or screenshots:

- Hide editor menus, sidebars, toolbars, thumbnails, and input bars.
- Export only slide stage content.
- Use landscape 16:9.
- Prefer browser automation export over OS print dialog when possible.

When exporting clean HTML:

- Remove transient selection classes, resize handles generated at runtime if they can be regenerated, file inputs, upload buttons, debug panels, and temporary paste markers.
- Preserve stable edit metadata, slide order, notes, and saved object geometry unless the export is explicitly presentation-only.
- Ensure exported HTML runs standalone and does not depend on localStorage to reconstruct the current deck.
