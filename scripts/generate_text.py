#!/usr/bin/env python3
"""Draw the README's prose as SVGs, so every word is set in Geist Sans.

GitHub renders README text in its own font and offers no way to change it, so
the only way to put the site's typeface on the bio, project blurbs, lists and
links is to draw them as images. This is a one-off generator (the content is
static, unlike scripts/generate_stats.py): edit the CONTENT section, run

    pip install fonttools brotli
    python3 scripts/generate_text.py

and commit the t-*.svg files it writes next to the README.

Lines are wrapped by measuring real glyph advances from the embedded subset.
Links can't live inside an <img>, so each linked item is its own image and the
README wraps it in an <a>.
"""
import base64
import os
import re

from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONTS = os.path.join(HERE, "fonts")

SANS = ("GeistSans,ui-sans-serif,system-ui,-apple-system,"
        "&apos;Segoe UI&apos;,Roboto,Helvetica,Arial,sans-serif")
WIDTH = 620
FS = 14
LH = 22
PAD = 2

# same ink as the stat graphics
LIGHT = dict(body="#424a53", dim="#6e7681")
DARK = dict(body="#e6edf3", dim="#8b949e")

_adv = {}


def adv(weight):
    if weight not in _adv:
        f = TTFont(os.path.join(FONTS, f"geistsans-text-{weight}.woff2"))
        cm, hm, upm = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
        _adv[weight] = {chr(c): hm[g][0] / upm for c, g in cm.items()}
    return _adv[weight]


def width(text, weight=400, size=FS):
    a = adv(weight)
    return sum(a.get(c, 0.6) for c in text) * size


def face(weight):
    with open(os.path.join(FONTS, f"geistsans-text-{weight}.woff2"), "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return (f"@font-face{{font-family:GeistSans;font-style:normal;"
            f"font-weight:{weight};font-display:block;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# A run is (text, weight, cls); cls is "b" (body) or "d" (dim).
def wrap(runs, maxw, indent=0.0):
    """Greedy word wrap over styled runs -> list of lines of runs."""
    words = []                       # (text, weight, cls, width incl. space)
    for text, wt, cls in runs:
        for w in re.findall(r"\S+\s*", text):
            words.append((w, wt, cls))
    lines, cur, curw = [], [], 0.0
    for w, wt, cls in words:
        ww = width(w.rstrip(), wt)
        full = width(w, wt)
        if cur and curw + ww > maxw - indent:
            lines.append(cur)
            cur, curw = [], 0.0
        cur.append((w, wt, cls))
        curw += full
    if cur:
        lines.append(cur)
    return lines


def svg(w, h, body):
    css = (f"{face(400)}{face(600)}"
           f".b{{fill:{LIGHT['body']}}}.d{{fill:{LIGHT['dim']}}}"
           f"@media(prefers-color-scheme:dark){{"
           f".b{{fill:{DARK['body']}}}.d{{fill:{DARK['dim']}}}}}")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" fill="none" font-family="{SANS}" '
            f'font-size="{FS}"><style>{css}</style>{body}</svg>')


def text_el(x, y, runs, size=FS):
    spans = "".join(
        f'<tspan class="{cls}" font-weight="{wt}">{esc(t)}</tspan>'
        for t, wt, cls in runs)
    sz = "" if size == FS else f' font-size="{size}"'
    return f'<text xml:space="preserve" x="{x}" y="{y}"{sz}>{spans}</text>'


def block(paragraphs, name, w=WIDTH, gap=0):
    """paragraphs: list of dicts {runs, indent, bullet}. One SVG file."""
    out, y = [], PAD
    for pi, para in enumerate(paragraphs):
        y += para.get("before", gap if pi else 0)
        ind = para.get("indent", 0)
        for li, line in enumerate(wrap(para["runs"], w - 2 * PAD, ind)):
            y += LH
            base = y - 6
            if li == 0 and para.get("bullet"):
                out.append(text_el(PAD, base, [("•", 400, "d")]))
            out.append(text_el(PAD + ind, base,
                               [(t.rstrip() if k == len(line) - 1 else t, wt, c)
                                for k, (t, wt, c) in enumerate(line)]))
    h = y + PAD + 2
    path = os.path.join(ROOT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg(w, h, "".join(out)))
    print(f"{name}: {w}x{h}")


def line(text, name, wt=400, cls="b", size=FS, pad_l=0):
    """A single unwrapped line, sized to its own width (for links)."""
    w = int(width(text, wt, size) + 2 * PAD + pad_l) + 1
    h = int(size * 1.6) + 2 * PAD
    y = PAD + size * 1.2
    body = text_el(PAD + pad_l, f"{y:.1f}", [(text, wt, cls)], size)
    with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
        f.write(svg(w, h, body))
    print(f"{name}: {w}x{h}")


# ------------------------------------------------------------------ CONTENT

B, D = "b", "d"


def project(name, file, stack, desc):
    block([
        dict(runs=[(name + "  ", 600, B), ("·  ", 400, D), (stack, 400, D)]),
        dict(runs=[(desc, 400, B)], before=4),
    ], file)


line("Kartikey Bhatnagar | Engineer", "t-name.svg", 600, B, 20)

block([dict(runs=[(
    "Full-stack engineer. I like building systems from the ground up and "
    "understanding the trade-offs behind them. Most of my time is spent "
    "figuring out what’s happening underneath the abstractions especially "
    "when something breaks, needs to scale, or needs to become more reliable "
    "and fault-tolerant. I enjoy building the infrastructure around products "
    "just as much as building the products themselves.", 400, B)])], "t-bio.svg")

project("YSync", "t-ysync.svg", "WebSockets Redis IndexedDB Sequence CRDT",
        "Custom sequence CRDT for real-time collaborative editing. WebSocket "
        "sync with causal merging and presence broadcasting. Supports 50+ "
        "concurrent clients with <20ms propagation and zero data loss across "
        "offline conflicts.")
project("Kyron", "t-kyron.svg", "Octokit Inngest pgvector RAG",
        "Durable PR review pipeline via Inngest. Tree-sitter AST chunking, "
        "pgvector retrieval, Gemini review, and GitHub comments. End-to-end "
        "review under 45s for PRs <500 lines. Incremental indexing cuts "
        "embedding API calls by ~80%.")
project("SQLFlow", "t-sqlflow.svg", "PostgreSQL MongoDB Express.js Next.js",
        "Multitenant SQL sandbox with isolated PostgreSQL schemas. Dynamic "
        "schema provisioning, safe untrusted query execution, and "
        "type-normalized result grading. Dual-database architecture with "
        "TTL-based audit logs for bounded storage growth.")

STACK = [
    ("LANGUAGES", ["JavaScript", "TypeScript", "C++", "Python"]),
    ("DATA", ["MongoDB", "PostgreSQL", "SQL", "Redis"]),
    ("BACKEND & WEB", ["React", "Next.js", "Tailwind CSS", "Node.js",
                       "Express", "Prisma", "Firebase", "Supabase",
                       "Appwrite", "ShadCN", "Clerk", "Postman"]),
    ("DEVOPS & INFRASTRUCTURE", ["Vercel", "Netlify", "Render", "Git",
                                 "RabbitMQ", "Docker", "AWS"]),
    ("OBSERVABILITY", ["Prometheus", "Alertmanager", "Loki", "Tempo",
                       "OpenTelemetry", "ELK Stack", "k6"]),
]
paras = []
for label, items in STACK:
    paras.append(dict(runs=[(label, 600, B)], before=10))
    paras.append(dict(runs=[("     ".join(items), 400, B)]))
block(paras, "t-stack.svg")

block([dict(runs=[(t, 400, B)], indent=16, bullet=True) for t in (
    "Open to SDE-1 / Full-Stack engineering roles, especially backend and "
    "infrastructure.",
    "Sleep on Friday nights, no work over the weekend.",
    "2 AM is for building random ideas")], "t-currently.svg")

line("•  Building & Shipping", "t-days-1.svg")
line("•  Writing & Sharing Knowledge", "t-days-2.svg")
line("•  Listening to something", "t-days-3.svg")

for key, label in (("work", "work"), ("linkedin", "linkedin"),
                   ("github", "github"), ("email", "email"),
                   ("instagram", "instagram")):
    sep = "" if key == "work" else "·   "
    line(sep + label, f"t-link-{key}.svg", 400, D, pad_l=0 if key == "work" else 6)

line("Always building. Always learning. Always shipping", "t-tagline.svg",
     400, D, 12)
