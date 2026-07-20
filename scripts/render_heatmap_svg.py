"""Render data/contributions.json as an animated terminal-style heatmap SVG.

Diagonal line-after-line reveal via CSS keyframes; plays once and freezes.
"""

import json
import os
from datetime import date
from pathlib import Path

STATIC = os.environ.get("STATIC") == "1"

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BG = "#0d1117"
BORDER = "#30363d"
TEXT = "#8b949e"
BRIGHT = "#c9d1d9"
GREEN = "#39d353"

CELL = 12
GAP = 3
PITCH = CELL + GAP
LEFT = 32
TOP = 38
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def color_for(day):
    level = min(day["level"], 4)
    if day["count"] >= 20:
        return PALETTE[5]
    return PALETTE[level]


def main():
    payload = json.loads(DATA.read_text())
    days = payload["days"]
    stats = payload["stats"]

    weeks = []
    week = [None] * 7
    for day in days:
        weekday = (date.fromisoformat(day["date"]).weekday() + 1) % 7
        if weekday == 0 and any(cell is not None for cell in week):
            weeks.append(week)
            week = [None] * 7
        week[weekday] = day
    if any(cell is not None for cell in week):
        weeks.append(week)

    n_weeks = len(weeks)
    width = LEFT + n_weeks * PITCH + 14
    height = TOP + 7 * PITCH + 58

    cells = []
    month_labels = []
    seen_months = set()
    for wi, wk in enumerate(weeks):
        for di, day in enumerate(wk):
            if day is None:
                continue
            d = date.fromisoformat(day["date"])
            if d.day <= 7 and d.month not in seen_months and wi < n_weeks - 1:
                seen_months.add(d.month)
                month_labels.append(
                    f'<text x="{LEFT + wi * PITCH}" y="{TOP - 10}" class="lbl">{MONTHS[d.month - 1]}</text>'
                )
            delay = (wi + di) * 14
            cells.append(
                f'<rect class="c" x="{LEFT + wi * PITCH}" y="{TOP + di * PITCH}" '
                f'width="{CELL}" height="{CELL}" rx="2.5" fill="{color_for(day)}" '
                f'style="animation-delay:{delay}ms"><title>{day["date"]}: {day["count"]}</title></rect>'
            )

    day_labels = "".join(
        f'<text x="{LEFT - 8}" y="{TOP + di * PITCH + CELL - 2}" class="lbl" text-anchor="end">{name}</text>'
        for di, name in ((1, "M"), (3, "W"), (5, "F"))
    )

    legend_x = width - 14 - 5 * PITCH - 74
    legend = [f'<text x="{legend_x - 8}" y="{height - 18}" class="lbl" text-anchor="end">Less</text>']
    for i, color in enumerate(PALETTE[:5]):
        legend.append(
            f'<rect x="{legend_x + i * PITCH}" y="{height - 28}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}"/>'
        )
    legend.append(f'<text x="{legend_x + 5 * PITCH + 6}" y="{height - 18}" class="lbl">More</text>')

    best = stats["best_day"]
    sep = f'<tspan fill="{BORDER}">  |  </tspan>'
    footer = (
        f'<text x="{LEFT}" y="{height - 18}" class="stats">'
        f'<tspan fill="{GREEN}">{stats["total"]}</tspan> contributions{sep}'
        f'longest <tspan fill="{GREEN}">{stats["longest_streak"]}d</tspan>{sep}'
        f'current <tspan fill="{GREEN}">{stats["current_streak"]}d</tspan>{sep}'
        f'best <tspan fill="{GREEN}">{best["count"]}</tspan>'
        f"</text>"
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="GitHub contribution heatmap">
  <style>
    .lbl {{ font: 10px 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace; fill: {TEXT}; }}
    .stats {{ font: 11px 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace; fill: {BRIGHT}; }}
    .c {{ opacity: {1 if STATIC else 0}; animation: {"none" if STATIC else "pop 0.45s ease-out forwards"}; }}
    @keyframes pop {{
      0%   {{ opacity: 0; transform: translateY(-6px); }}
      60%  {{ opacity: 1; }}
      100% {{ opacity: 1; transform: translateY(0); }}
    }}
    @media (prefers-reduced-motion: reduce) {{ .c {{ animation: none; opacity: 1; }} }}
  </style>
  <rect width="{width}" height="{height}" rx="8" fill="{BG}" stroke="{BORDER}"/>
  {"".join(month_labels)}
  {day_labels}
  {"".join(cells)}
  {"".join(legend)}
  {footer}
</svg>
"""
    OUT.write_text(svg)
    print(f"Wrote {OUT} ({width}x{height}, {n_weeks} weeks)")


if __name__ == "__main__":
    main()
