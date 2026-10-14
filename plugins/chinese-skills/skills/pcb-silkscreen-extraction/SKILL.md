---
name: pcb-silkscreen-extraction
description: PCB 白色丝印提取：从电路板照片中提取白色文字、符号和轮廓，保持原坐标并使用纯黑背景。 Extract white silkscreen text, symbols, outlines, polarity marks, and legends from a PCB photograph onto a solid black background while preserving the original crop, perspective, and coordinates. Use when a user asks to isolate PCB white markings, make a black-and-white silkscreen reference image, or enlarge such an extraction without changing its content or layout.
---

## 中文名称与用法

**中文名称：** PCB 白色丝印提取

**用途：** 从电路板照片中提取白色文字、符号和轮廓，保持原坐标并使用纯黑背景。

**调用示例：** 使用 $chinese-skills:pcb-silkscreen-extraction 提取这张 PCB 照片上的白色丝印，保持原位置。

文中的 `<SKILL_DIR>` 指本次加载的 SKILL.md 所在目录；从实际技能路径解析，不假定用户目录、操作系统或插件缓存版本。脚本接收的项目路径和输出路径仍使用当前任务的实际路径。


# 电路板文字提取

Create a black-background PCB silkscreen reference from a supplied board image. Retain only the white printed markings and preserve their original locations.

## Workflow

1. Treat the supplied PCB photo as the edit target. Inspect it first when it is a local file.
2. Use image editing to isolate only white silkscreen: lettering, reference designators, symbols, component outlines, connector legends, polarity marks, and graphics.
3. Preserve the source image's crop, orientation, perspective, and all marking coordinates. Do not redraw, correct, add, remove, translate, rotate, or reposition any mark.
4. Replace all non-silkscreen content with uniform pure black (`#000000`): PCB substrate, traces, solder, components, connectors, holes, shadows, and surroundings.
5. Validate against the input. If markings are missing, invented, moved, or changed, iterate with a narrow correction prompt.
6. If the user asks for enlargement, reuse the approved extraction and use deterministic 2× pixel scaling. Do not use generative upscaling as the final file when exact content and coordinates must remain unchanged.

## Optimized edit prompt

Use this prompt, replacing bracketed items only when needed:

```text
Use case: precise-object-edit
Asset type: PCB silkscreen extraction
Input image: edit target

Create a same-crop, pixel-aligned black-background extraction of the PCB's white silkscreen only: white text, labels, symbols, outlines, polarity marks, connector legends, and printed graphics.

Preserve the original image orientation, crop, perspective, scale, and coordinates. Every retained white mark must stay at its original location.

Replace everything else with pure solid black (#000000): PCB substrate, copper traces, components, connectors, solder, holes, shadows, reflections, and the surrounding surface.

Constraints: Do not invent, redraw, move, sharpen, correct, translate, omit, or add lettering or symbols. Keep the retained markings white. No gray remnants, texture, watermark, or new details.
```

## Exact 2× enlargement

When requested, scale the approved black-background extraction to exactly twice its width and height with a deterministic resampler that preserves the original pixels. Use nearest-neighbor for black-and-white silkscreen. Save a new sibling file; do not overwrite the source unless explicitly requested. Confirm source and output dimensions.
