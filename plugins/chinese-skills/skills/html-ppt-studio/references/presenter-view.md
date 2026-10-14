# Presenter View And Projection

Use this reference when generating or revising decks that need live presenting, presenter notes, screen projection, dual-window playback, or timer behavior.

Presenter view is part of Formal Presentation Mode and must remain available when a deck is upgraded to Full Editing Mode, unless the user explicitly asks for a clean non-presenter export.

## Required Behavior

- Audience view shows only the clean 16:9 slide stage.
- Presenter view shows presenter-only UI: current slide preview, optional next slide preview, notes, controls, thumbnails, and elapsed time.
- Presenter view must not be only a same-window overlay. It must support a separate presenter window and a separate clean audience window so external projection does not expose notes, timers, or controls.
- Entering presenter view should open a clean audience window automatically when possible. If the browser blocks popups, show a clear prompt telling the user to allow popups or click the audience-window button.
- Speaker notes must be editable in presenter view. A read-only notes block is not sufficient for live presenting.
- Speaker notes must be durable, not temporary textarea state. Store notes in the same persisted deck state used by browser editing, keyed by stable `slideId` rather than by the current page index. Typing in the notes field should mark that slide dirty and trigger a local save or debounced autosave; closing presenter view, switching modes, exporting, or reopening the deck must restore the last saved notes from the local state file.
- Presenter view navigation and audience view navigation must stay synchronized.
- Editor UI must never appear in the audience projection.
- Timer must appear only in presenter view.
- If the user enters audience/fullscreen playback from the normal deck and exits with `Esc`, restore the normal UI state immediately: side controls, edit entry, thumbnails, and page rail must reappear without requiring a browser refresh.

## Presenter Preview Rendering

Presenter preview must use the same slide rendering path as normal playback and audience playback.

Required pattern:

- Build slide HTML from the latest persisted state first, including `deck-state.json`, `slideOrder`, `slideHtmlOverrides`, text edits, object geometry, and notes.
- Pass the stable `slideId` into the same renderer used by the main stage and audience window. Do not call a separate `currentSrcdoc()` or presenter-only renderer that only knows the current page index.
- If a slide is embedded with `iframe.srcdoc`, create the srcdoc from the saved-state slide source for that `slideId`, not from stale HTML snapshots.
- Keep the preview iframe or preview container at `width:100%; height:100%; transform:none`.
- Let the inner 16:9 slide stage handle its own proportional fit. Do not apply a second outer `transform: scale(...)` to an already responsive iframe.

This prevents the common bug where the audience window is correct but the presenter preview is cropped or shows an old slide version.

## 16:9 Scaling Rule

The stable layout rule for HTML slides is:

```text
inner authored slide: fixed 1920x1080 coordinate system
outer viewport/frame: proportional scale and center
```

Do not force an authored 1920x1080 slide to become `100vw/100vh` with `transform:none` merely to remove margins. That often turns a small/blank-margin problem into enlarged clipping. Preserve the inner design coordinate system and scale the outer container.

## External Screen Workflow

The intended live-use workflow is:

1. Set the operating system display mode to extended display, not mirrored display.
2. Open presenter view on the speaker's computer.
3. Move the clean audience window to the external screen or projector.
4. Fullscreen the audience window, not the presenter window.
5. Keep notes, timer, and controls only in the presenter's local window.

If the computer is in mirrored display mode, presenter view cannot hide notes from the audience because both screens show the same window. In that case, tell the user to switch to extended display or use the clean audience window for sharing.

## Audience Fullscreen Prompt

Browsers do not allow ordinary web pages to hide the address bar or enter fullscreen without a user gesture. Use the low-cost solution by default:

- In audience mode, show a restrained "进入全屏放映" button or equivalent click prompt.
- On click, call `document.documentElement.requestFullscreen()`.
- Hide the prompt once fullscreen is active.
- If fullscreen fails, tell the user to press the browser/system fullscreen shortcut.
- Do not show this prompt in presenter mode, edit mode, print output, or PDF/screenshot export.

This keeps the deck browser-native and low-maintenance while still giving the audience a real full-screen presentation view after one click.

## Timer

Add elapsed-time information to the presenter view.

Recommended placement:

- Prefer the lower-right empty area below the current-slide preview, or a dedicated presenter control area. Do not overlay the timer on top of the slide preview content unless the slide area is guaranteed empty.
- Use a classic square digital clock treatment for decks where the presenter has enough blank space.
- Make the timer large enough to read at a glance, while still absent from the audience projection.

Timer behavior:

- Start when presenter mode opens or when the user clicks "Start".
- Pause/resume is required when a deck includes editing or presenter-note workflows. The speaker must be able to pause elapsed time while editing text, speaker notes, images, objects, or page order, then continue timing before resuming the presentation.
- Reset is optional.
- Do not show the timer in audience mode, exported PDF, or print output.

Keyboard behavior:

- Do not bind Space to slide navigation. Space is commonly used for Chinese IME confirmation, inserting spaces in editable text, focused buttons, and accessibility interactions.
- Use ArrowRight/ArrowLeft/PageDown/PageUp for keyboard navigation and map clicker keys to those events where possible.
- Global shortcuts must be disabled while focus is inside `input`, `textarea`, `contenteditable`, notes fields, or active edit controls.

## Dual-Window Sync

Use the simplest reliable sync mechanism available in a local single-browser deck:

1. `BroadcastChannel` named after the deck id, preferred for modern browsers.
2. `localStorage` event fallback.
3. `postMessage` when presenter opens the audience window itself.
4. URL hash/query as a visible fallback.

Minimum event payload:

```json
{
  "type": "slide-change",
  "deckId": "deck-id",
  "slideIndex": 8,
  "slideId": "s09",
  "source": "presenter"
}
```

Presenter navigation should publish slide changes. Audience view should subscribe and update its visible slide. If audience receives direct keyboard input, either ignore it or publish through the same channel so both windows remain aligned.

Implementation requirements:

- Use a stable `deckId` in the sync payload so multiple decks do not cross-talk.
- The presenter should publish on next/previous, thumbnail jump, keyboard navigation, and any programmatic `show(index)` call.
- Audience mode should hide or remove editor dock, export panel, presenter panel, notes, timer, debug labels, and side rails.
- Use `postMessage` when the presenter opened the audience window itself; use `BroadcastChannel` and `localStorage` as cross-window fallbacks in the same browser.

## Window Modes

Support clear modes:

- Normal view: slide stage plus minimal deck controls if needed.
- Audience view: slide stage only, no controls.
- Presenter view: presenter UI plus notes/timer, not intended for projection.
- Edit view: editing tools and thumbnails.

User-facing mode guidance:

```text
当前是“正式演示模式”：适合会议、授课和演讲。包含演示者视图、备注、计时器、翻页笔支持和干净观众窗口。
需要继续所见即所得修改时，可以进入“完整编辑模式”；进入编辑模式不应丢失演示者视图。
```

Mode can be selected with URL parameters:

```text
index.html?mode=audience
index.html?mode=presenter
index.html?mode=edit
```

Do not rely only on visual hiding if export/print is involved. Add print CSS that hides non-slide UI.

## Verification Checklist

- Open presenter view and audience view at the same time.
- Press next/previous in presenter view and confirm audience follows.
- Confirm entering presenter view creates or prompts for a separate audience window.
- Confirm presenter timer is visible in the presenter window lower-right area.
- Confirm timer pause/resume works while presenter notes or edit controls are active.
- Confirm audience view contains no notes, timer, editor controls, thumbnails, or sidebars.
- Confirm pressing Space in editable text, notes, or normal deck focus does not change slides.
- Confirm the audience fullscreen prompt appears only before fullscreen in audience mode, disappears after fullscreen, and is absent from PDF/export captures.
- Confirm page number and slide content match in both windows.
- On an external screen setup, confirm the audience/projector displays the audience window rather than the presenter window.
- Confirm exported PDF/print captures slide stage only.
