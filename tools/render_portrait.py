"""
Converts assets/photo-ready.png into a self-drawing monochrome ASCII SVG.

Usage:
    python tools\\render_portrait.py

Writes:
    portrait.svg
"""
from pathlib import Path

import numpy as np
from PIL import Image

GLYPHS = " '.,:;~+*xXO#"   # light/empty -> dense/dark
ACCENT_COLOR = "#4dabf7"
BG_COLOR = "#0d1117"
CELL_W, CELL_H = 8, 14      # px per character cell
COLS = 70                   # character grid width; rows derive from image aspect ratio
ROW_DELAY_MS = 40           # stagger between each row starting its reveal


def image_to_ascii_rows(image_path: str, cols: int = COLS):
    img = Image.open(image_path).convert("L")
    w, h = img.size
    aspect_correct = 0.55  # character cells are taller than they are wide
    rows = max(1, int((h / w) * cols * aspect_correct))
    img = img.resize((cols, rows))
    pixels = np.array(img)

    ascii_rows = []
    for row in pixels:
        line = ""
        for value in row:
            idx = int((255 - int(value)) / 255 * (len(GLYPHS) - 1))
            line += GLYPHS[idx]
        ascii_rows.append(line)
    return ascii_rows


def escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_svg(rows, output_path: str = "portrait.svg"):
    cols = max(len(r) for r in rows)
    width = cols * CELL_W
    height = len(rows) * CELL_H

    parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="monospace" font-size="{CELL_H}px">',
        f'<rect width="{width}" height="{height}" fill="{BG_COLOR}"/>',
    ]

    for i, line in enumerate(rows):
        y = (i + 1) * CELL_H
        clip_id = f"clip{i}"
        begin = round(i * ROW_DELAY_MS / 1000, 3)
        parts.append(f'<clipPath id="{clip_id}">')
        parts.append(f'  <rect x="0" y="{i * CELL_H}" width="0" height="{CELL_H}">')
        parts.append(
            f'    <animate attributeName="width" from="0" to="{width}" '
            f'begin="{begin}s" dur="0.6s" fill="freeze" calcMode="spline" '
            f'keySplines="0.2 0 0.2 1"/>'
        )
        parts.append("  </rect>")
        parts.append("</clipPath>")
        parts.append(
            f'<text x="0" y="{y}" fill="{ACCENT_COLOR}" xml:space="preserve" '
            f'clip-path="url(#{clip_id})">{escape(line)}</text>'
        )

    parts.append("</svg>")
    Path(output_path).write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    rows = image_to_ascii_rows("assets/photo-ready.png")
    render_svg(rows)
