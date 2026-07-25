"""
Renders a terminal-style "system info" panel as a self-typing SVG.

Usage:
    python tools\\render_panel.py            # writes sysinfo.svg, animated
    set PREVIEW=1
    python tools\\render_panel.py            # writes sysinfo.svg, static (cmd.exe)

    # PowerShell equivalent:
    $env:PREVIEW = "1"; python tools\\render_panel.py

Writes:
    sysinfo.svg
"""
import os
from pathlib import Path

# Edit these to describe what you're actually doing right now
ROWS = [
    ("role", "Software Engineer"),
    ("focus", "Distributed Systems"),
    ("stack", "Go . Rust . Postgres"),
    ("now", "Building a job-queue from scratch"),
]

ACCENT_COLOR = "#4dabf7"
BG_COLOR = "#0d1117"
HEADER_COLOR = "#161b22"
WIDTH = 460
ROW_HEIGHT = 34
HEADER_HEIGHT = 40
ROW_DELAY_S = 0.35


def escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_panel(preview: bool, output_path: str = "sysinfo.svg"):
    height = HEADER_HEIGHT + len(ROWS) * ROW_HEIGHT + 20

    parts = [
        f'<svg viewBox="0 0 {WIDTH} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="monospace" font-size="15px">',
        f'<rect width="{WIDTH}" height="{height}" rx="8" fill="{BG_COLOR}" '
        f'stroke="#30363d"/>',
        f'<rect width="{WIDTH}" height="{HEADER_HEIGHT}" rx="8" fill="{HEADER_COLOR}"/>',
        '<circle cx="20" cy="20" r="6" fill="#ff5f56"/>',
        '<circle cx="40" cy="20" r="6" fill="#ffbd2e"/>',
        '<circle cx="60" cy="20" r="6" fill="#27c93f"/>',
        f'<text x="{WIDTH - 16}" y="26" fill="#8b949e" text-anchor="end">sysinfo</text>',
    ]

    for i, (label, value) in enumerate(ROWS):
        y = HEADER_HEIGHT + 26 + i * ROW_HEIGHT
        line = escape(f"{label:<7}: {value}")
        opacity_attr = "1" if preview else "0"
        text = (
            f'<text x="20" y="{y}" fill="{ACCENT_COLOR}" xml:space="preserve" '
            f'opacity="{opacity_attr}">{line}'
        )
        if not preview:
            begin = round(i * ROW_DELAY_S, 3)
            text += (
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{begin}s" dur="0.4s" fill="freeze"/>'
            )
        text += "</text>"
        parts.append(text)

    parts.append("</svg>")
    Path(output_path).write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    render_panel(preview=os.environ.get("PREVIEW") == "1")
