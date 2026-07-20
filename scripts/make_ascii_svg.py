"""Generate haaris-ascii.svg — a block-letter ASCII banner in a terminal window.

Each row is clipped and revealed left-to-right with staggered SMIL animation,
playing once and freezing (per the guide's design principles).
"""

import os
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "haaris-ascii.svg"
STATIC = os.environ.get("STATIC") == "1"

FONT_BITS = {
    "H": ["10001", "10001", "11111", "10001", "10001"],
    "A": ["01110", "10001", "11111", "10001", "10001"],
    "R": ["11110", "10001", "11110", "10100", "10010"],
    "I": ["11111", "00100", "00100", "00100", "11111"],
    "S": ["01111", "10000", "01110", "00001", "11110"],
    "D": ["11110", "10001", "10001", "10001", "11110"],
    "Q": ["01110", "10001", "10001", "10010", "01101"],
}

BG = "#0d1117"
BORDER = "#30363d"
GRAY = "#c9d1d9"
DIM = "#8b949e"
GREEN = "#39d353"
BLUE = "#58a6ff"

W = 370
PAD = 18
TITLEBAR = 30
LINE_H = 13
FONT_SIZE = 9


def banner(word):
    rows = []
    for r in range(5):
        row = "  ".join(
            "".join("@@" if bit == "1" else "  " for bit in FONT_BITS[ch][r]) for ch in word
        )
        rows.append(row)
    return rows


def main():
    ramp = " .`:-=+*cs#%@"
    ramp_line = (ramp + ramp[::-1]).strip()
    ramp_line = (ramp_line * 4)[:52]

    lines = [
        ("$ ./whoami --render", GREEN),
        ("", GRAY),
        *[(row, GRAY) for row in banner("HAARIS")],
        ("", GRAY),
        *[(row, GRAY) for row in banner("SADIQ")],
        ("", GRAY),
        (ramp_line, "#484f58"),
        ("", GRAY),
        ("> mechatronics engineering", BLUE),
        ("> @ university of waterloo", BLUE),
        ("> building where hw meets sw", DIM),
        ("", GRAY),
        ("[@@@@@@@@@@@@@@@@@@@@] 100% loaded", GREEN),
    ]

    height = TITLEBAR + PAD + len(lines) * LINE_H + PAD
    text_w = W - 2 * PAD
    max_len = max(len(text) for text, _ in lines)
    parts = []
    clips = []
    for i, (text, color) in enumerate(lines):
        if not text:
            continue
        text = text.ljust(max_len)
        y = TITLEBAR + PAD + (i + 1) * LINE_H - 3
        clip_ref = ""
        if not STATIC:
            begin = 0.15 + i * 0.09
            clips.append(
                f'<clipPath id="row{i}"><rect x="0" y="{y - LINE_H}" width="0" height="{LINE_H + 4}">'
                f'<animate attributeName="width" from="0" to="{W}" begin="{begin:.2f}s" dur="0.35s" fill="freeze"/>'
                f"</rect></clipPath>"
            )
            clip_ref = f' clip-path="url(#row{i})"'
        parts.append(
            f'<text x="{PAD}" y="{y}" class="mono" fill="{color}" xml:space="preserve" '
            f'textLength="{text_w}" lengthAdjust="spacingAndGlyphs"{clip_ref}>{text}</text>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" width="{W}" height="{height}" role="img" aria-label="Haaris Sadiq ASCII banner">
  <style>
    .mono {{ font: {FONT_SIZE}px 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace; white-space: pre; }}
    .title {{ font: 10px 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace; fill: {DIM}; }}
  </style>
  <defs>{"".join(clips)}</defs>
  <rect width="{W}" height="{height}" rx="8" fill="{BG}" stroke="{BORDER}"/>
  <line x1="1" y1="{TITLEBAR}" x2="{W - 1}" y2="{TITLEBAR}" stroke="{BORDER}"/>
  <circle cx="20" cy="{TITLEBAR / 2}" r="4.5" fill="#ff5f56"/>
  <circle cx="38" cy="{TITLEBAR / 2}" r="4.5" fill="#ffbd2e"/>
  <circle cx="56" cy="{TITLEBAR / 2}" r="4.5" fill="#27c93f"/>
  <text x="{W / 2}" y="{TITLEBAR / 2 + 3.5}" class="title" text-anchor="middle">haaris@github: ~/banner</text>
  {"".join(parts)}
</svg>
"""
    OUT.write_text(svg)
    print(f"Wrote {OUT} ({W}x{height})")


if __name__ == "__main__":
    main()
