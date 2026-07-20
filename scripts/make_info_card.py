"""Generate info-card.svg — a neofetch-style terminal info card.

Rows fade and slide in line-by-line with a stagger; plays once and freezes.
Set STATIC=1 for a frozen frame with no animation.
"""

import os
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

BG = "#0d1117"
BORDER = "#30363d"
BRIGHT = "#c9d1d9"
DIM = "#8b949e"
GREEN = "#39d353"
BLUE = "#58a6ff"
PURPLE = "#bc8cff"
ORANGE = "#ffa657"
RED = "#ff7b72"
YELLOW = "#e3b341"
CYAN = "#76e3ea"

W = 490
PAD = 20
TITLEBAR = 30
LINE_H = 22
KEY_W = 118

ROWS = [
    ("header", "haaris@github", None),
    ("rule", "", None),
    ("kv", "study", "Mechatronics Engineering @ UWaterloo"),
    ("kv", "now", "Fullstack apps · AI agents · Robotics"),
    ("kv", "team", "WATonomous — autonomous driving"),
    ("kv", "langs", "Python · C++ · TypeScript · Java"),
    ("kv", "web", "React · Next.js · FastAPI · Node.js"),
    ("kv", "robotics", "ROS2 · OpenCV · PyTorch"),
    ("kv", "infra", "Docker · Azure · Vercel · PostgreSQL"),
    ("kv", "certs", "IBM Data Analysis · IBM Optimization"),
    ("kv", "site", "haarissadiq.dev — work in progress"),
    ("kv", "linkedin", "in/haaris-sadiq"),
    ("kv", "x", "@s_haaris25714"),
    ("rule", "", None),
    ("palette", "", None),
]

KEY_COLORS = {
    "study": BLUE,
    "now": GREEN,
    "team": PURPLE,
    "langs": ORANGE,
    "web": CYAN,
    "robotics": RED,
    "infra": YELLOW,
    "certs": BLUE,
    "site": GREEN,
    "linkedin": PURPLE,
    "x": CYAN,
}

PALETTE = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, BRIGHT]


def main():
    height = TITLEBAR + PAD + len(ROWS) * LINE_H + PAD - 4
    parts = []
    for i, (kind, key, value) in enumerate(ROWS):
        y = TITLEBAR + PAD + (i + 1) * LINE_H - 8
        anim = "" if STATIC else f' style="animation-delay:{0.15 + i * 0.12:.2f}s"'
        cls = "row static" if STATIC else "row"

        if kind == "header":
            parts.append(
                f'<text x="{PAD}" y="{y}" class="mono {cls}"{anim}>'
                f'<tspan fill="{GREEN}">{key}</tspan><tspan fill="{DIM}"> — mechatronics · fullstack · ai</tspan></text>'
            )
        elif kind == "rule":
            parts.append(
                f'<g class="{cls}"{anim}><line x1="{PAD}" y1="{y - 5}" x2="{W - PAD}" y2="{y - 5}" stroke="{BORDER}"/></g>'
            )
        elif kind == "palette":
            sw = 24
            blocks = "".join(
                f'<rect x="{PAD + j * (sw + 4)}" y="{y - 14}" width="{sw}" height="12" rx="2" fill="{c}"/>'
                for j, c in enumerate(PALETTE)
            )
            parts.append(f'<g class="{cls}"{anim}>{blocks}</g>')
        else:
            parts.append(
                f'<text x="{PAD}" y="{y}" class="mono {cls}"{anim}>'
                f'<tspan fill="{KEY_COLORS.get(key, BLUE)}">{key}</tspan>'
                f'<tspan x="{PAD + KEY_W}" fill="{BRIGHT}">{value}</tspan></text>'
            )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" width="{W}" height="{height}" role="img" aria-label="Haaris Sadiq info card">
  <style>
    .mono {{ font: 12px 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace; }}
    .title {{ font: 10px 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace; fill: {DIM}; }}
    .row {{ opacity: 0; animation: rise 0.5s ease-out forwards; }}
    .row.static {{ opacity: 1; animation: none; }}
    @keyframes rise {{
      from {{ opacity: 0; transform: translateX(-10px); }}
      to   {{ opacity: 1; transform: translateX(0); }}
    }}
    @media (prefers-reduced-motion: reduce) {{ .row {{ animation: none; opacity: 1; }} }}
  </style>
  <rect width="{W}" height="{height}" rx="8" fill="{BG}" stroke="{BORDER}"/>
  <line x1="1" y1="{TITLEBAR}" x2="{W - 1}" y2="{TITLEBAR}" stroke="{BORDER}"/>
  <circle cx="20" cy="{TITLEBAR / 2}" r="4.5" fill="#ff5f56"/>
  <circle cx="38" cy="{TITLEBAR / 2}" r="4.5" fill="#ffbd2e"/>
  <circle cx="56" cy="{TITLEBAR / 2}" r="4.5" fill="#27c93f"/>
  <text x="{W / 2}" y="{TITLEBAR / 2 + 3.5}" class="title" text-anchor="middle">haaris@github: ~/info</text>
  {"".join(parts)}
</svg>
"""
    OUT.write_text(svg)
    print(f"Wrote {OUT} ({W}x{height})")


if __name__ == "__main__":
    main()
