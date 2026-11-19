# Embedded typefaces

[Geist](https://github.com/vercel/geist-font) — the site's own typeface — subset
to only the characters each graphic actually draws, and inlined into the SVGs as
base64 `@font-face`.

* **Geist Sans** sets the headings and the stat graphics.
* **Geist Mono** sets the ASCII portrait and the year map's character grid.
  Both bake in an advance width of exactly 0.600 em, which Geist Mono has
  (600/1000 units), so a viewer's narrower default monospace (Consolas is
  ≈0.55) can't squeeze them.

An external font URL cannot work here: these SVGs are loaded through `<img>`,
and a browser refuses to fetch subresources for an image document. A base64 data
URI is the only mechanism, and it keeps the page free of third-party requests.

| file | face | covers |
|---|---|---|
| `geistmono-ramp.woff2` | Mono 400 | the 13 ramp characters in `ascii.svg` |
| `geistmono-400.woff2` | Mono 400 | basic latin, for the year grid |
| `geistsans-400.woff2` | Sans 400 | basic latin, for the stat graphics |
| `geistsans-600.woff2` | Sans 600 | basic latin, for the stat graphics |
| `geistsans-head.woff2` | Sans 600 | printable ascii, for the section headings |

Licensed under the SIL Open Font License 1.1 — see `OFL.txt`.
