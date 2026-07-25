"""
Renders assets/contributions.json as an animated grid SVG that reveals
column by column (week by week), with a legend and a stats footer.

Usage:
    python tools\\render_graph.py

Writes:
    graph.svg
"""
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

LEVELS = ["#1a1a2e", "#16537e", "#1c7ed6", "#4dabf7", "#a5d8ff"]
BG_COLOR = "#0d1117"
CELL = 12
GAP = 3
COLUMN_DELAY_S = 0.05


def load_weeks(data_path: str = "assets/contributions.json"):
    payload = json.loads(Path(data_path).read_text(encoding="utf-8"))
    days = payload["days"]
    stats = payload["stats"]

    weeks = defaultdict(dict)  # week_index -> {weekday: level}
    first_date = datetime.fromisoformat(days[0]["date"])
    # align so weekday 0 = Sunday, matching GitHub's own calendar layout
    start_offset = (first_date.weekday() + 1) % 7

    for i, day in enumerate(days):
        pos = i + start_offset
        week_index = pos // 7
        weekday = pos % 7
        weeks[week_index][weekday] = day["level"]

    return weeks, stats


def render_svg(weeks, stats, output_path: str = "graph.svg"):
    num_weeks = max(weeks.keys()) + 1
    width = num_weeks * (CELL + GAP) + GAP
    height = 7 * (CELL + GAP) + GAP + 50  # extra room for legend + stats line

    parts = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="monospace" font-size="12px">',
        f'<rect width="{width}" height="{height}" fill="{BG_COLOR}"/>',
    ]

    for week in range(num_weeks):
        x = GAP + week * (CELL + GAP)
        begin = round(week * COLUMN_DELAY_S, 3)
        for weekday in range(7):
            y = GAP + weekday * (CELL + GAP)
            level = weeks.get(week, {}).get(weekday, 0)
            color = LEVELS[level]
            parts.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{color}" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{begin}s" dur="0.3s" fill="freeze"/>'
                f"</rect>"
            )

    legend_y = height - 34
    parts.append(f'<text x="{GAP}" y="{legend_y}" fill="#8b949e">Less</text>')
    for i, color in enumerate(LEVELS):
        lx = GAP + 40 + i * (CELL + GAP)
        parts.append(
            f'<rect x="{lx}" y="{legend_y - 10}" width="{CELL}" height="{CELL}" '
            f'rx="2" fill="{color}"/>'
        )
    label_x = GAP + 40 + len(LEVELS) * (CELL + GAP) + 6
    parts.append(f'<text x="{label_x}" y="{legend_y}" fill="#8b949e">More</text>')

    summary = (
        f'{stats["total_contributions"]} contributions - '
        f'{stats["current_streak"]}d current streak - '
        f'{stats["longest_streak"]}d longest - busiest day: {stats["busiest_day"]}'
    )
    parts.append(f'<text x="{GAP}" y="{height - 8}" fill="#8b949e">{summary}</text>')

    parts.append("</svg>")
    Path(output_path).write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    weeks, stats = load_weeks()
    render_svg(weeks, stats)
