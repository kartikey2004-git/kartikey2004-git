# Embedded typeface

[Geist Sans](https://github.com/vercel/geist-font) — the site's own typeface —
subset to only the characters each graphic actually draws, and inlined into the
SVGs as base64 `@font-face`.

An external font URL cannot work here: these SVGs are loaded through `<img>`,
and a browser refuses to fetch subresources for an image document. A base64 data
URI is the only mechanism, and it keeps the page free of third-party requests.

The portrait and the year map are character grids set in a proportional face, so
each glyph carries its own `x` coordinate; the layout doesn't depend on the font.

| file | weight | covers |
|---|---|---|
| `geistsans-ramp.woff2` | 400 | the 13 ramp characters in `ascii.svg` |
| `geistsans-400.woff2` | 400 | basic latin, for the stat graphics |
| `geistsans-600.woff2` | 600 | basic latin, for the stat graphics |
| `geistsans-head.woff2` | 600 | printable ascii, for the section headings |
| `geistsans-text-400.woff2` | 400 | latin plus ’ · • – —, for the prose SVGs (`t-*.svg`) |
| `geistsans-text-600.woff2` | 600 | the same, for names and labels |

Licensed under the SIL Open Font License 1.1 — see `OFL.txt`.
