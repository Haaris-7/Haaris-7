"""Generate photo-ascii.svg — ASCII portrait from source-photo.png.

Follows the guide's pipeline: composite the background-removed photo onto
white, boost contrast, downsample to a character grid, and map brightness to
a density ramp. Rows reveal top-to-bottom with staggered SMIL clips, playing
once and freezing. Set STATIC=1 for a frozen frame.
"""

import os
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source-photo.png"
OUT = ROOT / "photo-ascii.svg"
STATIC = os.environ.get("STATIC") == "1"

RAMP = " .`:-=+*cs#%@"

BG = "#0d1117"
BORDER = "#30363d"
GRAY = "#c9d1d9"
DIM = "#8b949e"
GREEN = "#39d353"

W = 370
PAD = 14
TITLEBAR = 30
COLS = 150
LINE_H = 4.7
FONT_SIZE = 4.3
ROWS = 72
TOP_CROP_FRACTION = 0.04


def to_grid():
    rgba = Image.open(SRC).convert("RGBA")
    alpha = rgba.getchannel("A")
    white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    img = Image.alpha_composite(white, rgba).convert("L")
    img = ImageOps.autocontrast(img, cutoff=1)

    text_w = W - 2 * PAD
    cell_aspect = LINE_H / (text_w / COLS)
    crop_w = img.width
    crop_h = min(img.height, int(crop_w * ROWS * cell_aspect / COLS))
    y0 = min(int(img.height * TOP_CROP_FRACTION), img.height - crop_h)
    box = (0, y0, crop_w, y0 + crop_h)
    img = img.crop(box).resize((COLS, ROWS), Image.LANCZOS)
    alpha = alpha.crop(box).resize((COLS, ROWS), Image.LANCZOS)

    lines = []
    for row in range(ROWS):
        chars = []
        for col in range(COLS):
            if alpha.getpixel((col, row)) < 32:
                chars.append(" ")
                continue
            brightness = img.getpixel((col, row))
            idx = max(2, int((brightness / 255) ** 0.7 * (len(RAMP) - 1)))
            chars.append(RAMP[idx])
        lines.append("".join(chars))
    return lines


def main():
    lines = to_grid()
    text_w = W - 2 * PAD
    height = round(TITLEBAR + PAD + len(lines) * LINE_H + PAD + 22)

    parts = []
    clips = []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        y = TITLEBAR + PAD + (i + 1) * LINE_H - 1
        clip_ref = ""
        if not STATIC:
            begin = 0.1 + i * 0.03
            clips.append(
                f'<clipPath id="prow{i}"><rect x="0" y="{y - LINE_H}" width="0" height="{LINE_H + 3}">'
                f'<animate attributeName="width" from="0" to="{W}" begin="{begin:.3f}s" dur="0.3s" fill="freeze"/>'
                f"</rect></clipPath>"
            )
            clip_ref = f' clip-path="url(#prow{i})"'
        parts.append(
            f'<text x="{PAD}" y="{y}" class="px" xml:space="preserve" '
            f'textLength="{text_w}" lengthAdjust="spacingAndGlyphs"{clip_ref}>{line}</text>'
        )

    caption_y = height - PAD
    parts.append(
        f'<text x="{W / 2}" y="{caption_y}" class="cap" text-anchor="middle">'
        f'<tspan fill="{GREEN}">$</tspan> render --subject haaris --ramp "{RAMP.strip()}"</text>'
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" width="{W}" height="{height}" role="img" aria-label="ASCII portrait of Haaris Sadiq">
  <style>
    .px {{ font: {FONT_SIZE}px 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace; fill: {GRAY}; }}
    .cap {{ font: 8.5px 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace; fill: {DIM}; }}
    .title {{ font: 10px 'JetBrains Mono', 'SFMono-Regular', Consolas, monospace; fill: {DIM}; }}
  </style>
  <defs>{"".join(clips)}</defs>
  <rect width="{W}" height="{height}" rx="8" fill="{BG}" stroke="{BORDER}"/>
  <line x1="1" y1="{TITLEBAR}" x2="{W - 1}" y2="{TITLEBAR}" stroke="{BORDER}"/>
  <circle cx="20" cy="{TITLEBAR / 2}" r="4.5" fill="#ff5f56"/>
  <circle cx="38" cy="{TITLEBAR / 2}" r="4.5" fill="#ffbd2e"/>
  <circle cx="56" cy="{TITLEBAR / 2}" r="4.5" fill="#27c93f"/>
  <text x="{W / 2}" y="{TITLEBAR / 2 + 3.5}" class="title" text-anchor="middle">haaris@github: ~/portrait</text>
  {"".join(parts)}
</svg>
"""
    OUT.write_text(svg)
    print(f"Wrote {OUT} ({W}x{height}, {len(lines)} rows)")


if __name__ == "__main__":
    main()
