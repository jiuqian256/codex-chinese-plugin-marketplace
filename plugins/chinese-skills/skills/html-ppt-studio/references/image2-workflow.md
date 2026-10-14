# Prepared Image And Image2 Workflow

Default assumption: if the user provides images, screenshots, or a pure-image PPT/PDF, those visuals are already authored and approved. Use them directly. Do not call image2, regenerate images, or redesign their content unless the user explicitly asks.

This reference is only for explicit image-generation or image-prompt work.

## When To Recommend Image2

Recommend image2 only when:

- The user asks to generate, redraw, or improve a visual.
- The user wants a highly designed conceptual chart or scene.
- A single page needs a polished poster-like visual.
- Recreating the design manually in HTML would take too long.
- The user can express the desired visual better by pasting an image than by describing coordinates.
- A required page visual is missing.

Do not use image2 for:

- Text-heavy pages that need frequent editing.
- Tables or charts that must update from data.
- Screenshots that must preserve exact UI details unless doing a deliberate redesign.

## Workflow

1. If the image already exists, use it directly as the source of truth.
2. If a new image is explicitly requested, write or run the image prompt.
3. User selects the preferred generated image.
4. User pastes selected image into the editable deck page.
5. User saves deck edits.
6. User submits "执行修改".
7. The executing agent reads saved state and incorporates the pasted image into the durable deck.

## Page Image Guidelines

- Use 16:9 images for full-page visual slides.
- Use transparent PNG when the image should float over dark HTML background.
- Use high resolution, ideally at least 1920x1080.
- Keep important text in HTML when it may need later edits.
- If the generated image contains text, verify spelling and alignment before accepting it.
- For already approved images, avoid reinterpreting their contents. Preserve aspect ratio, avoid cropping important content, and add only minimal HTML chrome or overlays.

## Prompt Pattern

```
Create a 16:9 high-end technology-finance research report visual.
Topic: [slide topic].
Audience: [audience].
Style: dark carbon black background, fine grid, restrained glow, warm orange emphasis, cinematic data story.
Composition: [timeline / flow / matrix / system diagram / evidence wall].
Text language: [Chinese/English].
Avoid cartoon style, generic PPT cards, cheap gradients, and default tables.
```

## Integration Rule

When a generated page image is used as a major visual, do not wrap it in a white card or rounded picture frame. Integrate it as a full-bleed, masked, floating, or evidence-layer element.
