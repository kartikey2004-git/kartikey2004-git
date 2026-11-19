#!/usr/bin/env python3
"""Inline the ramp subset of Geist Sans into ascii.svg.

The portrait is a one-off artifact — a photo pushed through a character ramp —
so unlike the stat graphics it isn't regenerated on a schedule. Run this after
ever rebuilding it.

Why it matters: every glyph is placed on the grid by its own x, so the layout is
font-independent, but inlining the font pins the look for everyone. An external font URL is not an option: the SVG is
loaded through <img>, and browsers refuse subresource fetches for image
documents.

Idempotent: running it twice changes nothing.
"""
import base64
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "fonts", "geistsans-ramp.woff2")
FAMILY = ("GeistSans,ui-sans-serif,system-ui,-apple-system,"
          "&apos;Segoe UI&apos;,Roboto,Helvetica,Arial,sans-serif")


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(HERE), "ascii.svg")
    with open(target, encoding="utf-8") as f:
        svg = f.read()

    if "GeistSans" in svg:
        print(f"{target}: already carries the font")
        return

    with open(FONT, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    rule = (f"@font-face{{font-family:GeistSans;font-style:normal;"
            f"font-weight:400;font-display:block;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")

    if "<style>" not in svg:
        raise SystemExit(f"{target}: no <style> block to extend")
    svg = svg.replace("<style>", f"<style>{rule}", 1)

    # point the whole document at the embedded face
    swapped, n = re.subn(r'font-family="[^"]*"', f'font-family="{FAMILY}"', svg)
    if not n:
        raise SystemExit(f"{target}: no font-family to replace")

    with open(target, "w", encoding="utf-8") as f:
        f.write(swapped)
    print(f"{target}: embedded {len(b64) // 1024} KB of base64 font")


if __name__ == "__main__":
    main()
