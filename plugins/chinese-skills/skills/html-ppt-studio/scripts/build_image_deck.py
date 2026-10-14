#!/usr/bin/env python3
"""Build a fast image-first editable HTML deck.

This script is intentionally dependency-free. It treats provided images as
approved slide artwork and adds only a lightweight HTML presentation shell.
"""

from __future__ import annotations

import argparse
import html
import shutil
from pathlib import Path


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def find_images(paths: list[str]) -> list[Path]:
    images: list[Path] = []
    for raw in paths:
      path = Path(raw).expanduser()
      if path.is_dir():
        images.extend(sorted(p for p in path.iterdir() if p.suffix.lower() in IMAGE_EXTS))
      elif path.suffix.lower() in IMAGE_EXTS:
        images.append(path)
    return images


def build_html(title: str, images: list[Path], asset_names: list[str]) -> str:
    slides = []
    total = len(images)
    for i, (src, asset) in enumerate(zip(images, asset_names), start=1):
        alt = html.escape(src.stem.replace("-", " ").replace("_", " "))
        slides.append(f'''      <section class="slide" data-slide-id="s{i:02d}">
        <img class="slide-art edit-draggable" data-edit-id="s{i:02d}-image-1" src="assets/{html.escape(asset)}" alt="{alt}" />
        <div class="page-mark">{i:02d} / {total}</div>
      </section>''')
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      --bg: #03070c;
      --ink: #f4f7fb;
      --muted: rgba(225, 232, 242, .62);
      --line: rgba(130, 165, 210, .16);
      --blue: #3e7cff;
      --red: #ef3348;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ width: 100%; height: 100%; margin: 0; overflow: hidden; background: var(--bg); }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif; color: var(--ink); }}
    .deck-viewport {{ position: fixed; inset: 0; overflow: hidden; background: radial-gradient(circle at 18% 8%, rgba(62,124,255,.18), transparent 28%), #03070c; }}
    .deck-stage {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; transform-origin: 0 0; overflow: hidden; background: #05080d; }}
    .deck-stage::before {{ content: ""; position: absolute; inset: 0; pointer-events: none; z-index: 20; background-image: linear-gradient(90deg, rgba(112,149,197,.06) 1px, transparent 1px), linear-gradient(0deg, rgba(112,149,197,.06) 1px, transparent 1px); background-size: 80px 80px; mix-blend-mode: screen; }}
    .slide {{ position: absolute; inset: 0; width: 1920px; height: 1080px; opacity: 0; visibility: hidden; pointer-events: none; overflow: hidden; background: #05080d; transition: opacity .45s ease, transform .6s ease; transform: translateY(10px) scale(.995); }}
    .slide.active {{ opacity: 1; visibility: visible; pointer-events: auto; transform: translateY(0) scale(1); z-index: 2; }}
    .slide-art {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: contain; background: #05080d; }}
    .page-mark {{ position: absolute; right: 74px; bottom: 42px; z-index: 25; font: 700 18px ui-monospace, SFMono-Regular, Menlo, monospace; color: rgba(244,247,251,.55); letter-spacing: .08em; text-shadow: 0 2px 16px rgba(0,0,0,.45); }}
    .hud {{ position: fixed; left: 50%; bottom: 18px; transform: translateX(-50%); z-index: 100; display: flex; gap: 10px; align-items: center; padding: 8px 12px; border: 1px solid rgba(255,255,255,.12); border-radius: 999px; background: rgba(5,8,13,.72); backdrop-filter: blur(18px); color: var(--muted); font: 700 13px ui-monospace, Menlo, monospace; }}
    .hud button {{ width: 34px; height: 30px; border: 0; border-radius: 999px; color: var(--ink); background: rgba(255,255,255,.1); cursor: pointer; }}
    .progress {{ position: fixed; left: 0; right: 0; bottom: 0; height: 3px; z-index: 101; background: rgba(255,255,255,.08); }}
    .progress span {{ display: block; height: 100%; width: 0; background: linear-gradient(90deg, var(--blue), var(--red)); transition: width .35s ease; }}
    @media (prefers-reduced-motion: reduce) {{ * {{ transition-duration: .01ms !important; animation-duration: .01ms !important; }} }}
    @media print {{
      html, body {{ overflow: visible; background: #fff; }}
      .deck-viewport, .deck-stage {{ position: static; width: auto; height: auto; transform: none !important; }}
      .slide {{ position: relative; opacity: 1 !important; visibility: visible !important; transform: none !important; page-break-after: always; break-after: page; }}
      .hud, .progress {{ display: none !important; }}
    }}
  </style>
</head>
<body>
  <div class="deck-viewport">
    <main class="deck-stage" id="deckStage">
{chr(10).join(slides)}
    </main>
  </div>
  <div class="hud"><button id="prevBtn">‹</button><span id="count">1 / {total}</span><button id="nextBtn">›</button></div>
  <div class="progress"><span id="progress"></span></div>
  <script>
    const slides = Array.from(document.querySelectorAll(".slide"));
    let current = Math.max(0, Math.min(Number(new URLSearchParams(location.search).get("slide") || 1) - 1, slides.length - 1));
    const count = document.getElementById("count");
    const progress = document.getElementById("progress");
    function show(index) {{
      current = Math.max(0, Math.min(index, slides.length - 1));
      slides.forEach((slide, i) => slide.classList.toggle("active", i === current));
      count.textContent = `${{current + 1}} / ${{slides.length}}`;
      progress.style.width = `${{((current + 1) / slides.length) * 100}}%`;
      history.replaceState(null, "", `?slide=${{current + 1}}`);
    }}
    function next() {{ show(current + 1); }}
    function prev() {{ show(current - 1); }}
    document.getElementById("nextBtn").onclick = next;
    document.getElementById("prevBtn").onclick = prev;
    document.addEventListener("keydown", (event) => {{
      if (["INPUT", "TEXTAREA", "SELECT"].includes(event.target?.tagName)) return;
      if (["ArrowRight", "PageDown", " "].includes(event.key)) {{ event.preventDefault(); next(); }}
      if (["ArrowLeft", "PageUp"].includes(event.key)) {{ event.preventDefault(); prev(); }}
      if (event.key === "Home") show(0);
      if (event.key === "End") show(slides.length - 1);
    }});
    function scaleStage() {{
      const stage = document.getElementById("deckStage");
      const box = document.querySelector(".deck-viewport").getBoundingClientRect();
      const scale = Math.min(box.width / 1920, box.height / 1080);
      stage.style.transform = `translate(${{(box.width - 1920 * scale) / 2}}px, ${{(box.height - 1080 * scale) / 2}}px) scale(${{scale}})`;
    }}
    addEventListener("resize", scaleStage);
    scaleStage();
    show(current);
  </script>
</body>
</html>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an HTML PPT from approved slide images.")
    parser.add_argument("inputs", nargs="+", help="Image files or folders")
    parser.add_argument("--title", default="HTML PPT", help="Deck title")
    parser.add_argument("--out", required=True, help="Output folder")
    args = parser.parse_args()

    images = find_images(args.inputs)
    if not images:
        raise SystemExit("No image files found.")

    out = Path(args.out).expanduser()
    assets = out / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    names: list[str] = []
    for i, src in enumerate(images, start=1):
        name = f"slide-{i:02d}{src.suffix.lower()}"
        shutil.copy2(src, assets / name)
        names.append(name)
    (out / "index.html").write_text(build_html(args.title, images, names), encoding="utf-8")
    print(out / "index.html")


if __name__ == "__main__":
    main()
