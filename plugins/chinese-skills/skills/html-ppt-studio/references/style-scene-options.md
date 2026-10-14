# Style And Scene Options

Use visual choices only when the user's style or scene is unclear, or when the user explicitly asks for options. The goal is to let the user react to images or preview cards, not to abstract labels.

## How To Present Choices

When needed, generate or show a small preview board with 3-5 style cards and 3-5 scene cards. Each card should look like a plausible first slide from the deck, not a diagnostic UI.

Do not call image generation for style previews unless the user explicitly requests image-based previews. Prefer compact HTML preview cards when previews are necessary.

Do not write internal labels such as "style option" on the preview slide itself. Put labels in the surrounding message.

Skip this reference path when the user already supplied a clear style, example, target deck, or specific page request.

## Default Style Set

Use these as starting choices. Adapt names to the user's language.

1. Dark Research Terminal
   - Dark carbon background, thin grids, mono metadata, warm orange risk accents.
   - Best for AI infrastructure, finance, policy research, industrial strategy.

2. Apple Keynote Tech
   - Clean black or deep gray, large restrained typography, one strong visual per page.
   - Best for public talks, executive briefings, product narratives.

3. Swiss Data Report
   - Precise grid, hard alignment, minimal colors, strong data hierarchy.
   - Best for government reports, strategy summaries, industry analysis.

4. Cinematic AI Infrastructure
   - Full-bleed imagery, dim overlays, glowing network lines, dramatic chapter beats.
   - Best for keynote-style training or technology vision decks.

5. Light Institutional Brief
   - Light background, technical blue/gray palette, strict report layout.
   - Best when dark slides are not acceptable for the organization.

## Common Scene Set

1. Government training and briefing.
2. County or municipal policy explanation.
3. Industry research or investment memo.
4. Enterprise internal training.
5. Product launch or demo day.
6. Public keynote or conference talk.
7. Technical workshop or hands-on tutorial.

## Preview Prompt Pattern

When generating preview images or cards, use:

```
Create a single 16:9 HTML presentation preview page for: [topic].
Audience: [audience].
Style: [style choice].
Scene: [scene choice].
It should look like a high-end web data story / research report, not a normal PowerPoint template.
Use real words from the user's topic; no lorem ipsum; no "preview" label.
```

## Selection Rule

After showing choices, ask the user to pick:

- One style.
- One scene.
- Density: speaker-led or reading-first.

If the user wants to proceed immediately, choose the most suitable default and state the assumption.
