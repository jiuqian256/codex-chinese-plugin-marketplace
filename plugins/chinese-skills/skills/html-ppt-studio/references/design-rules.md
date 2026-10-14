# Design Rules

These rules are the highest priority for `html-ppt-studio`.

## Visual Goal

Turn the user's text, images, tables, and data into a high-end HTML presentation or web PPT.

The target look is dark technology-finance data storytelling: high-end research report, investor briefing, WebGL-style data story, AI infrastructure or technology industry narrative. It should feel immersive, cinematic, and analytical, not like a traditional PowerPoint template.

## Canvas And Layout

- Use a fixed 16:9 stage. Prefer 1920x1080 authoring dimensions.
- Scale the whole stage to the viewport. Do not reflow slide contents responsively.
- Each slide should feel like a designed information poster.
- Build a clear hierarchy among title, subtitle, data, chart, annotation, source, and page number.
- Keep titles on one line whenever practical. Prefer layout changes, wider title areas, smaller but still readable type, or shorter user-approved wording before allowing unnecessary title wraps.
- Page numbers are derived runtime information, not decorative slide content. Keep only one visible page-number system on each slide, placed in the lower-right corner by default. Do not add page numbers in the upper header, upper-right corner, top center, inside thumbnails, or in multiple locations unless the user explicitly asks for a special layout.
- Do not add filler explanatory copy merely to fill space. Avoid vague course-like, audience-explaining, or process-sounding labels such as "以政府工作者可理解的方式...", "以政府可以理解的方式...", "理解来源", "看懂底座", "判断趋势", "统一语言", "进入工作流", "理解框架", or similar generic labels unless the user explicitly provides them as desired slide text. Use concise, content-bearing labels only.
- Reserve a playback-safe bottom area and avoid placing primary content too low. The optical center of major content should sit slightly above the mathematical center, especially for projected or browser-playback decks where bottom UI can cover content.
- Do not leave large unused top whitespace while dense content is pushed downward. If a slide feels low, reduce top chrome, move the content group upward, or split content rather than shrinking text.
- Use professional report elements: large numbers, fine grids, coordinate axes, separators, flow lines, Sankey-like flows, labels, footnotes, page numbers, and source notes.
- Do not create scrolling slides.
- Do not shrink dense content until unreadable. Split dense material into more slides.

## Section And Agenda Pages

- Agenda/title pages with a left summary and right vertical module list must balance visual weight: the left headline should be large enough to anchor the page, while right-side module titles should be strong but not dominate the whole canvas.
- Module list containers should be proportionate to their text. Avoid oversized pill borders around small labels or cramped text inside large glass panels.
- For dark technology-finance style, glass elements should look like restrained translucent surfaces: subtle border, inner highlight, low-opacity blue/cyan glow, and enough negative space. Avoid dead, flat gray blocks and avoid overly decorative neon.
- Use lively but controlled accent colors, such as cyan/blue with small warm orange highlights. The page should feel active and analytical, not gloomy or noisy.

## Language And Metadata Discipline

- Do not add decorative English metadata unless it is directly required by the user's content, brand, source, or page function.
- Avoid filler labels such as "County AI Course", "Intelligence Infrastructure", "Agenda Map", "Five Modules", "Practical Orientation", "Dark Tech Finance HTML Deck", or English translations/subtitles that do not add information.
- If the deck is Chinese-facing, default all visible text to Chinese unless the user explicitly asks for bilingual or English labels.
- Metadata, footers, labels, and page marks must carry real information: date, source, section number, organization name, page number, or user-provided keywords. If a label is only decorative, repeats information already visible elsewhere, explains the audience instead of the content, or sounds like an internal planning note, omit it.

## Image Treatment

- Except for software screenshots, webpage screenshots, app UI, or operation demos, do not place images inside generic picture frames, white cards, rounded containers, or decorative borders.
- Images should integrate into the visual composition: full-screen background, semi-transparent texture, cropped mask, floating evidence, chart-side proof, or structural element.
- Software screenshots may keep a restrained window/device feel.
- Avoid screenshot-collage pages. If many screenshots are needed, turn them into an evidence wall, timeline, flow, or annotated sequence.

## Tables And Charts

- Do not paste ordinary tables.
- Convert table content into visual modules: ranking, matrix, KPI tower, comparison bars, flow diagram, timeline, annotated chart, metric wall, or quadrant.
- Charts must have real labels, units, and visual emphasis.
- Avoid Excel default styling.
- If numbers are not supplied, do not invent precise numeric claims. Use qualitative scales or ask for data.

## Animation

Animations should feel like web interaction and data visualization, not PowerPoint fly-ins.

Prefer:

- Fade and subtle position shifts.
- Line drawing.
- Number count-up.
- Chart growth.
- Flow-line expansion.
- Group stagger.
- Subtle background breathing.

Requirements:

- Animation must support comprehension.
- Include keyboard left/right navigation.
- Include `prefers-reduced-motion`.
- Avoid decorative motion that distracts from the message.

## Default Style Keywords

- Dark background.
- Low-saturation black-blue or carbon black.
- Warm orange or red for risk, emphasis, or inflection.
- Fine grid.
- Subtle glow.
- Financial research report feel.
- AI infrastructure and technology industry narrative.
- Advanced but restrained.

## Prohibited Patterns

- Traditional PPT template look.
- Large white card backgrounds.
- Every image inside rounded rectangles.
- Piles of equal-width cards.
- Cheap gradients.
- Default HTML tables.
- Software manual pages.
- Random screenshot collage.
- Cartoon visual tone unless the user explicitly requests it.
