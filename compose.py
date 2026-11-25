#!/usr/bin/env python3
"""Compose the news-image-20261125 front page from the generated base art.

Adds a masthead with the date and a two-line headline strip at the foot of
each of the five picture panels. All text is drawn with DejaVu Sans Bold,
so it is guaranteed legible. Output: entry.png, 1024x1024, <= 1 MiB.
"""
from PIL import Image, ImageDraw, ImageFont

SRC = "/home/hatch/workspace/projects-gratis/news-image-20261125/media-generation-news-image-20261125-base-0-063afc43-7f57-494c-8858-27ada5c99f70.png"
OUT = "/home/hatch/workspace/projects-gratis/news-image-20261125/entry.png"

W, H = 1024, 1024
MASTHEAD_H = 118
CREAM = (242, 236, 221)
NAVY = (20, 33, 61)
RED = (178, 34, 34)

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

base = Image.open(SRC).convert("RGB")
bw, bh = base.size
bg = base.getpixel((5, 5))


def differs(px):
    # paper-grain cream background is bright; panels are dark navy art
    return (px[0] + px[1] + px[2]) < 560


# --- detect panel rectangles: row bands where non-background pixels appear ---
small = base.resize((400, 400))
spix = small.load()
rows_with = [any(differs(spix[x, y]) for x in range(400)) for y in range(400)]
bands = []
in_band = False
for y, v in enumerate(rows_with):
    if v and not in_band:
        start = y
        in_band = True
    elif not v and in_band:
        bands.append((start, y - 1))
        in_band = False
if in_band:
    bands.append((start, 399))
# merge bands closer than 6 px, keep the 3 largest
merged = []
for s, e in bands:
    if merged and s - merged[-1][1] <= 6:
        merged[-1] = (merged[-1][0], e)
    else:
        merged.append((s, e))
bands = sorted(merged, key=lambda b: b[1] - b[0], reverse=True)[:3]
bands.sort()

panels = []
for (y0, y1) in bands:
    cols_with = [any(differs(spix[x, y]) for y in range(y0, y1 + 1)) for x in range(400)]
    runs = []
    in_run = False
    for x, v in enumerate(cols_with):
        if v and not in_run:
            start = x
            in_run = True
        elif not v and in_run:
            runs.append((start, x - 1))
            in_run = False
    if in_run:
        runs.append((start, 399))
    runs = [r for r in runs if r[1] - r[0] > 20]
    for (x0, x1) in runs:
        panels.append((x0, y0, x1, y1))
panels.sort(key=lambda p: (p[1], p[0]))
print("detected panels (400px grid):", panels)
assert len(panels) == 5, f"expected 5 panels, got {len(panels)}"

# scale from 400-grid to final canvas: art area is W x (H - MASTHEAD_H)
AW, AH = W, H - MASTHEAD_H
scale_x = AW / 400.0
scale_y = AH / 400.0

art = base.resize((AW, AH), Image.LANCZOS)
canvas = Image.new("RGB", (W, H), CREAM)
canvas.paste(art, (0, MASTHEAD_H))

draw = ImageDraw.Draw(canvas, "RGBA")

# --- masthead ---
f_small = ImageFont.truetype(BOLD, 26)
f_date = ImageFont.truetype(BOLD, 52)
f_rule = ImageFont.truetype(REG, 20)

title1 = "THE WORLD IN ONE DAY"
tw = draw.textlength(title1, font=f_small)
draw.text(((W - tw) / 2, 12), title1, font=f_small, fill=RED)
date = "WEDNESDAY, 25 NOVEMBER 2026"
dw = draw.textlength(date, font=f_date)
draw.text(((W - dw) / 2, 44), date, font=f_date, fill=NAVY)
draw.rectangle([40, MASTHEAD_H - 12, W - 40, MASTHEAD_H - 8], fill=RED)

# --- headline strips, one per panel, in reading order ---
# panels sorted top-to-bottom, left-to-right: 0 hack, 1 huawei, 2 riyadh, 3 ship, 4 ebola
headlines = [
    ("SPIES HACKED", "CIA and ODNI hit by cyber breach"),
    ("HUAWEI GUILTY", "US jury: stole trade secrets"),
    ("RIYADH TOWER HIT", "Houthi drone wounds 11"),
    ("RUSSIAN WARSHIP SUNK", "Ukraine claims strike off Libya"),
    ("EBOLA EVACUATION", "WHO pulls staff out of Congo fighting"),
]
f_head = ImageFont.truetype(BOLD, 25)
f_sub = ImageFont.truetype(REG, 19)

STRIP_H = 62
for (x0, y0, x1, y1), (head, sub) in zip(panels, headlines):
    px0 = int(x0 * scale_x)
    px1 = int((x1 + 1) * scale_x)
    py1 = int(MASTHEAD_H + (y1 + 1) * scale_y)
    py0 = py1 - STRIP_H
    draw.rectangle([px0, py0, px1, py1], fill=NAVY + (228,))
    draw.text((px0 + 12, py0 + 6), head, font=f_head, fill=(255, 255, 255))
    draw.text((px0 + 12, py0 + 35), sub, font=f_sub, fill=(220, 222, 230))

canvas.save(OUT, "PNG", optimize=True)
import os
print("saved", OUT, os.path.getsize(OUT), "bytes,", canvas.size)
