#!/usr/bin/env python3
"""Render 'daniel' in every pyfiglet/Calligraphy font, filter to reasonable
sizes, and emit src/static/hero-fonts.json for the homepage cycler."""

import json
import sys
from pathlib import Path

import pyfiglet

WORD = "daniel"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "static" / "hero-fonts.json"

# size guardrails — fonts outside these don't fit the hero well
MIN_W, MAX_W = 14, 90
MIN_H, MAX_H = 3, 14


def render(name: str) -> dict | None:
    try:
        art = pyfiglet.figlet_format(WORD, font=name)
    except Exception:
        return None
    lines = art.rstrip("\n").split("\n")
    while lines and not lines[-1].strip():
        lines.pop()
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines:
        return None
    height = len(lines)
    width = max(len(l) for l in lines)
    if not (MIN_W <= width <= MAX_W and MIN_H <= height <= MAX_H):
        return None
    # crude noise filter: must have some block-density variance
    body = "\n".join(lines)
    non_space = sum(1 for c in body if c not in " \t\n")
    if non_space < width * height * 0.05:
        return None
    return {"name": name, "art": body, "w": width, "h": height}


def main() -> int:
    all_fonts = sorted(pyfiglet.FigletFont.getFonts())
    out = []
    for name in all_fonts:
        rec = render(name)
        if rec:
            out.append(rec)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, separators=(",", ":")))
    print(f"wrote {len(out)} fonts → {OUT}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
