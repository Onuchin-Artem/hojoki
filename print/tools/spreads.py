#!/usr/bin/env python3
"""Render PDF pages as book spreads (verso | recto). Page 1 stands alone (recto).

Usage: python3 print/tools/spreads.py FIRST LAST [PPI]
Outputs build/spreads/spread-NN.png (NN = left page number, or 01 for the lone first page).
"""
import sys, subprocess, pathlib
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
first, last = int(sys.argv[1]), int(sys.argv[2])
ppi = sys.argv[3] if len(sys.argv) > 3 else "170"
out = ROOT / "build/spreads"; tmp = ROOT / "build/_pg"
for d in (out, tmp):
    d.mkdir(parents=True, exist_ok=True)
for f in out.glob("*.png"): f.unlink()

subprocess.run([
    "typst", "compile", "--root", str(ROOT),
    "--font-path", str(ROOT / "assets/fonts/print"),
    "--pages", f"{first}-{last}", "--ppi", ppi,
    str(ROOT / "print/main.typ"), str(tmp / "p-{p}.png"),
], check=True)

def img(n):
    p = tmp / f"p-{n}.png"
    return Image.open(p).convert("RGB") if p.exists() else None

GUT = 28
def spread(name, left, right):
    if left is None and right is None: return
    ref = left or right
    blank = lambda: Image.new("RGB", ref.size, "white")
    left = left or blank(); right = right or blank()
    h = max(left.height, right.height); w = left.width + right.width + GUT
    c = Image.new("RGB", (w, h), "white")
    c.paste(left, (0, (h - left.height) // 2))
    c.paste(right, (left.width + GUT, (h - right.height) // 2))
    c.save(out / name); print("saved", name)

# page 1 alone on the right; then (verso even | recto odd) pairs
n = first
if first == 1:
    spread("spread-01.png", None, img(1)); n = 2
while n <= last:
    if n % 2 == 0:
        spread(f"spread-{n:02d}.png", img(n), img(n + 1) if n + 1 <= last else None); n += 2
    else:
        spread(f"spread-{n:02d}.png", None, img(n)); n += 1
