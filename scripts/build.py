#!/usr/bin/env python3
"""
freeconstitution.org build script
Generates the complete static site from /content into /public.

Usage:  python3 scripts/build.py
Needs:  Python 3.9+ and PyYAML (pip install pyyaml)

The build fails loudly if:
  - a "Phrase by phrase" quote does not match the original text exactly
  - an internal link points at a page that does not exist
"""

import json
import re
import shutil
import subprocess
import sys
from datetime import date
from html import escape
from pathlib import Path

import yaml

# ============================================================
# Settings
# ============================================================
ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
PUBLIC = ROOT / "public"

SITE_URL = "https://freeconstitution.org"
SITE_NAME = "Free Constitution"
TAGLINE = "Know your rights. In plain English."
CONTACT_URL = "https://hopeforamericans.net"   # where "Found a mistake?" points
ASSET_V = "20261001b"                           # bump to bust browser caches
TODAY = date.today()
WPM = 200                                      # reading speed used for "About N min"

ORDINALS = {
    1: "First", 2: "Second", 3: "Third", 4: "Fourth", 5: "Fifth",
    6: "Sixth", 7: "Seventh", 8: "Eighth", 9: "Ninth", 10: "Tenth",
    11: "Eleventh", 12: "Twelfth", 13: "Thirteenth", 14: "Fourteenth",
    15: "Fifteenth", 16: "Sixteenth", 17: "Seventeenth", 18: "Eighteenth",
    19: "Nineteenth", 20: "Twentieth", 21: "Twenty-first",
    22: "Twenty-second", 23: "Twenty-third", 24: "Twenty-fourth",
    25: "Twenty-fifth", 26: "Twenty-sixth", 27: "Twenty-seventh",
}
ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII"}
ARTICLE_NAMES = {
    1: "Congress", 2: "The President", 3: "The courts", 4: "The states",
    5: "Changing the Constitution", 6: "The supreme law", 7: "Approving the Constitution",
}

# Homepage "What's going on?" buttons
FINDER = [
    ("shield", "Police are asking me questions", "/situations/being-questioned-by-police/"),
    ("search", "Police want to search me", "/situations/searched-by-police/"),
    ("school", "Something happened at school", "/situations/at-school/"),
    ("phone", "I posted something online", "/situations/posting-online/"),
    ("work", "Something happened at work", "/situations/at-work/"),
    ("camera", "I want to record police", "/situations/recording-police/"),
    ("ballot", "I'm voting for the first time", "/situations/first-time-voter/"),
    ("megaphone", "I'm going to a protest", "/situations/at-a-protest/"),
]

# Homepage "Questions people are asking"
JUMP_POINTS = [
    ("Can police search my phone?", "/amendments/4/", "Fourth Amendment"),
    ("Can my school punish me for a post?", "/situations/posting-online/", "Situation card"),
    ("Do I have to answer police questions?", "/situations/being-questioned-by-police/", "Situation card"),
    ("Who is a citizen by birth?", "/amendments/14/", "Fourteenth Amendment"),
    ("Can an app ban me for what I say?", "/amendments/1/", "First Amendment"),
    ("Can the government take my property?", "/amendments/5/", "Fifth Amendment"),
]

# ============================================================
# Icons (24x24, stroke). Keep it small and consistent.
# ============================================================
ICONS = {
    "shield": '<path d="M12 22s-8-4.5-8-11V5l8-3 8 3v6c0 6.5-8 11-8 11z"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    "school": '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c3 2.5 9 2.5 12 0v-5"/>',
    "phone": '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
    "work": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13h18"/>',
    "camera": '<path d="M15 10l5-3v10l-5-3z"/><rect x="3" y="6" width="12" height="12" rx="2"/>',
    "ballot": '<rect x="4" y="11" width="16" height="10" rx="1"/><path d="M8 11V4h8v7M10 7.5l1.5 1.5L14 6"/>',
    "megaphone": '<path d="M3 11v2a1 1 0 0 0 1 1h3l6 4V6L7 10H4a1 1 0 0 0-1 1z"/><path d="M17 9a4 4 0 0 1 0 6"/>',
    "home": '<path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/>',
    "car": '<path d="M5 17h14M5 17v2M19 17v2M4 13l2-6h12l2 6v4H4z"/><circle cx="8" cy="14" r="1"/><circle cx="16" cy="14" r="1"/>',
    "scales": '<path d="M12 3v18M7 21h10M5 7h14M5 7l-3 7a3 3 0 0 0 6 0zM19 7l-3 7a3 3 0 0 0 6 0z"/>',
    "columns": '<path d="M3 21h18M4 10h16M12 3l9 5H3zM6 10v8M10 10v8M14 10v8M18 10v8"/>',
    "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',
    "flag": '<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>',
    "book": '<path d="M4 4h6a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H4zM20 4h-6a3 3 0 0 0-3 3"/><path d="M20 4v14h-7"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "check": '<path d="M5 12l5 5L20 7"/>',
    "x": '<path d="M6 6l12 12M18 6L6 18"/>',
    "right": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "left": '<path d="M19 12H5M11 6l-6 6 6 6"/>',
    "text": '<path d="M4 20l5-14h2l5 14M6.5 14h7M17 20v-6.5a2.5 2.5 0 0 1 5 0V20M17 16.5h5"/>',
    "eye": '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "bulb": '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-4 10.5c.7.7 1 1.5 1 2.5h6c0-1 .3-1.8 1-2.5A6 6 0 0 0 12 3z"/>',
    "quote": '<path d="M7 7h4v4c0 3-2 5-4 6M15 7h4v4c0 3-2 5-4 6"/>',
    "help": '<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6V14M12 17.5v.01"/>',
    "list": '<path d="M9 6h11M9 12h11M9 18h11M4 6h.01M4 12h.01M4 18h.01"/>',
    "layers": '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/>',
    "lifebuoy": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/><path d="M5.6 5.6l3.6 3.6M14.8 14.8l3.6 3.6M18.4 5.6l-3.6 3.6M9.2 14.8l-3.6 3.6"/>',
    "printer": '<path d="M6 9V3h12v6M6 18H4v-7h16v7h-2"/><rect x="6" y="14" width="12" height="7"/>',
    "download": '<path d="M12 3v12M7 10l5 5 5-5M4 21h16"/>',
    "expand": '<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/>',
    "map": '<path d="M9 4L3 6v14l6-2 6 2 6-2V4l-6 2z"/><path d="M9 4v14M15 6v14"/>',
    "timeline": '<path d="M12 2v20"/><circle cx="12" cy="6" r="2"/><circle cx="12" cy="13" r="2"/><path d="M14 6h6M4 13h6M14 19h5"/>',
    "brain": '<path d="M9 4a3 3 0 0 0-3 3 3 3 0 0 0-2 5 3 3 0 0 0 2 5 3 3 0 0 0 6 1V4.5A2.5 2.5 0 0 0 9 4zM15 4a3 3 0 0 1 3 3 3 3 0 0 1 2 5 3 3 0 0 1-2 5 3 3 0 0 1-6 1"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.01"/>',
    "alert": '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18v.01"/>',
    "menu": '<path d="M4 6h16M4 12h16M4 18h16"/>',
    "up": '<path d="M6 15l6-6 6 6"/>',
    "words": '<path d="M4 6h10M4 12h7M4 18h10"/><path d="M15 15l3-8 3 8M16 13h4"/>',
}


MARK_SVG = ('<svg class="wm-svg" viewBox="0 0 64 64" aria-hidden="true" focusable="false">'
            '<rect width="64" height="64" rx="14" fill="#1E3A5F"/>'
            '<path d="M17 10H38L47 19V54H17Z" fill="#F7F1E3"/><path d="M38 10V19H47Z" fill="#D9CDB0"/>'
            '<polygon points="32.00,23.00 34.59,30.44 42.46,30.60 36.18,35.36 38.47,42.90 32.00,38.40 25.53,42.90 27.82,35.36 21.54,30.60 29.41,30.44" fill="#9B2C24"/>'
            '</svg>')


def icon(name, cls="ic"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
            f'{ICONS.get(name, ICONS["info"])}</svg>')


# ============================================================
# Glossary term linking
# ============================================================
class Terms:
    SKIP = {"a", "h1", "h2", "h3", "h4", "button", "blockquote", "code", "summary", "q", "dt"}

    def __init__(self, items):
        self.items = []
        for it in items:
            slug = slugify(it["term"])
            forms = [it["term"]] + list(it.get("aliases") or [])
            forms = sorted({f.lower() for f in forms if f}, key=len, reverse=True)
            alt = "|".join(re.escape(f).replace(r"\ ", r"\s+").replace("\\-", "[-\\s]") for f in forms)
            rx = re.compile(r"(?<![\w-])(" + alt + r")(?:s|es)?(?![\w-])", re.I)
            self.items.append({"slug": slug, "term": it["term"], "rx": rx,
                               "def": it["def"], "see": it.get("see") or "/words/"})
        self.items.sort(key=lambda x: len(x["term"]), reverse=True)

    def link(self, html, used):
        if not html:
            return html
        parts = re.split(r"(<[^>]+>)", html)
        depth = 0
        out = []
        for part in parts:
            if part.startswith("<"):
                m = re.match(r"<(/?)([a-zA-Z0-9]+)", part)
                if m and m.group(2).lower() in self.SKIP and not part.endswith("/>"):
                    depth += -1 if m.group(1) else 1
                    depth = max(depth, 0)
                out.append(part)
                continue
            if depth or not part.strip():
                out.append(part)
                continue
            segs = [part]
            for it in self.items:
                if it["slug"] in used:
                    continue
                for i, s in enumerate(segs):
                    if not isinstance(s, str):
                        continue
                    mm = it["rx"].search(s)
                    if mm:
                        a = (f'<a class="term" href="/words/#{it["slug"]}" data-def="{escape(it["def"])}" '
                             f'data-see="{escape(it["see"])}">{mm.group(0)}</a>')
                        segs[i:i + 1] = [s[:mm.start()], (a,), s[mm.end():]]
                        used.add(it["slug"])
                        break
            out.append("".join(x[0] if isinstance(x, tuple) else x for x in segs))
        return "".join(out)


TERMS = None  # set in main()


# ============================================================
# Markdown (the small subset our content uses)
# ============================================================
def slugify(text):
    text = re.sub(r"<[^>]+>", "", str(text))
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


def inline_md(text):
    """Inline markdown on an already HTML-escaped string."""
    def link(m):
        label, href = m.group(1), m.group(2)
        ext = href.startswith("http")
        attrs = ' rel="noopener"' if ext else ""
        return f'<a href="{href}"{attrs}>{label}</a>'
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"<em>([^<]*(?: v\. | Cases)[^<]*)</em>", r'<em class="case">\1</em>', text)
    return text


def md(s):
    """Inline markdown for short YAML strings."""
    return inline_md(escape(str(s or "")))


def md_to_html(src, h_offset=0):
    lines = src.split("\n")
    out, para = [], []
    state = {"list": None, "quote": False}

    def close_para():
        if para:
            out.append("<p>" + inline_md(escape(" ".join(para))) + "</p>")
            para.clear()

    def close_list():
        if state["list"]:
            out.append(f"</{state['list']}>")
            state["list"] = None

    def close_quote():
        if state["quote"]:
            out.append("</blockquote>")
            state["quote"] = False

    for line in lines:
        s = line.strip()
        m_ol = re.match(r"^(\d+)\.\s+(.*)$", s)
        if s.startswith("#### ") or s.startswith("### ") or s.startswith("## "):
            close_para(); close_list(); close_quote()
            level = len(s.split(" ")[0])
            text = s[level + 1:]
            lv = min(level + h_offset, 6)
            out.append(f'<h{lv} id="{slugify(text)}">{inline_md(escape(text))}</h{lv}>')
        elif s.startswith("> "):
            close_para(); close_list()
            if not state["quote"]:
                out.append("<blockquote>")
                state["quote"] = True
            out.append("<p>" + inline_md(escape(s[2:])) + "</p>")
        elif s.startswith("- "):
            close_para(); close_quote()
            if state["list"] != "ul":
                close_list()
                out.append("<ul>")
                state["list"] = "ul"
            out.append("<li>" + inline_md(escape(s[2:])) + "</li>")
        elif m_ol:
            close_para(); close_quote()
            if state["list"] != "ol":
                close_list()
                out.append("<ol>")
                state["list"] = "ol"
            out.append("<li>" + inline_md(escape(m_ol.group(2))) + "</li>")
        elif s == "---":
            close_para(); close_list(); close_quote()
        elif s == "":
            close_para(); close_list(); close_quote()
        else:
            close_list(); close_quote()
            para.append(s)
    close_para(); close_list(); close_quote()
    return "\n".join(out)


def load_md(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.DOTALL)
    if not m:
        return {}, raw
    return (yaml.safe_load(m.group(1)) or {}), m.group(2)


def split_h2(body):
    """[(heading, markdown)] for each ## section, in order."""
    out, cur, buf = [], None, []
    for line in body.split("\n"):
        if line.startswith("## "):
            if cur is not None:
                out.append((cur, "\n".join(buf).strip()))
            cur, buf = line[3:].strip(), []
        else:
            buf.append(line)
    if cur is not None:
        out.append((cur, "\n".join(buf).strip()))
    return out


def sec(sections, name):
    for h, m in sections:
        if h.lower() == name.lower():
            return m
    return ""


def plain_text(html):
    t = re.sub(r"<[^>]+>", " ", html)
    t = t.replace("&amp;", "&").replace("&quot;", '"').replace("&#x27;", "'")
    return re.sub(r"\s+", " ", t).strip()


def minutes_for(*texts):
    words = sum(len(plain_text(t).split()) for t in texts if t)
    return max(1, round(words / WPM))


def load_insight(stem):
    p = CONTENT / "insights" / f"{stem}.yml"
    return (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.exists() else {}


def load_yaml(name):
    p = CONTENT / name
    return (yaml.safe_load(p.read_text(encoding="utf-8")) or []) if p.exists() else []


# ============================================================
# Page registry (minutes, titles), used by paths and search
# ============================================================
PAGES = {}        # url -> {"title", "minutes", "kind", "summary", "text", "icon"}
WRITTEN = set()   # urls written


def register(url, title, kind, minutes=None, summary="", text="", icon_name="", quick=None):
    PAGES[url] = {"title": title, "kind": kind, "minutes": minutes, "summary": summary,
                  "text": text, "icon": icon_name, "quick": quick or minutes}


def write(url_or_path, html):
    p = url_or_path
    if p.endswith("/"):
        p += "index.html"
    full = PUBLIC / p.lstrip("/")
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(html, encoding="utf-8")
    if url_or_path.endswith("/") or url_or_path.endswith(".html"):
        WRITTEN.add(url_or_path)


def fmt_date(d):
    if not d:
        return ""
    if isinstance(d, str):
        try:
            d = date.fromisoformat(d)
        except ValueError:
            return d
    return d.strftime("%B %-d, %Y")


def year_of(d):
    return str(d)[:4] if d else ""


# ============================================================
# Shared chrome
# ============================================================
def head(title, description, canonical, og_image, og_type, jsonld, robots="index, follow, max-image-preview:large, max-snippet:-1"):
    full_url = f"{SITE_URL}{canonical}"
    jld = f'<script type="application/ld+json">{json.dumps(jsonld)}</script>' if jsonld else ""
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{full_url}">
<meta name="robots" content="{robots}">
<meta name="author" content="Hope for Americans">
<meta name="theme-color" content="#14283f">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{full_url}">
<meta property="og:image" content="{SITE_URL}{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{escape(title)}">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(title)}">
<meta name="twitter:description" content="{escape(description)}">
<meta name="twitter:image" content="{SITE_URL}{og_image}">
<link rel="icon" href="/static/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="preload" href="/static/fonts/atkinson-hyperlegible-next-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/static/css/site.css?v={ASSET_V}">
<script>
/* Apply saved reading settings before first paint (no flash). Nothing leaves the device. */
(function(){{try{{var p=JSON.parse(localStorage.getItem("fc-display")||"{{}}"),d=document.documentElement;
d.classList.add("js");["size","spacing","font","theme","depth"].forEach(function(k){{if(p[k])d.setAttribute("data-"+k,p[k]);}});
if(p.focus)d.setAttribute("data-focus","on");}}catch(e){{document.documentElement.classList.add("js");}}}})();
</script>
{jld}"""


def header_html():
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-row">
    <a class="wordmark" href="/" aria-label="Free Constitution, home"><span class="wm-mark">{MARK_SVG}</span><span class="wm-text">Free Constitution</span></a>
    <nav class="site-nav" aria-label="Main">
      <a href="/situations/">Situations</a>
      <a href="/amendments/">Amendments</a>
      <a href="/articles/">Articles</a>
      <a href="/paths/">Paths</a>
    </nav>
    <div class="header-tools">
      <button type="button" class="tool-btn" data-open-search aria-label="Search (press /)">{icon("search")}<span class="tool-label">Search</span></button>
      <button type="button" class="tool-btn" data-open-display aria-label="Reading settings (press D)">{icon("text")}<span class="tool-label">Reading</span></button>
    </div>
  </div>
</header>"""


STAR_RING = '<svg class="star-ring" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><polygon points="32.0,4.0 32.9,6.8 35.8,6.8 33.5,8.5 34.4,11.2 32.0,9.5 29.6,11.2 30.5,8.5 28.2,6.8 31.1,6.8"/><polygon points="43.2,6.7 44.1,9.5 47.0,9.5 44.6,11.2 45.5,14.0 43.2,12.3 40.8,14.0 41.7,11.2 39.3,9.5 42.3,9.5"/><polygon points="51.8,14.4 52.6,17.1 55.6,17.1 53.2,18.8 54.1,21.6 51.8,19.9 49.4,21.6 50.3,18.8 47.9,17.1 50.9,17.1"/><polygon points="55.8,25.1 56.7,27.9 59.6,27.9 57.3,29.6 58.2,32.3 55.8,30.6 53.5,32.3 54.4,29.6 52.0,27.9 54.9,27.9"/><polygon points="54.4,36.5 55.3,39.3 58.2,39.3 55.9,41.0 56.8,43.7 54.4,42.0 52.1,43.7 53.0,41.0 50.6,39.3 53.5,39.3"/><polygon points="47.9,46.0 48.8,48.7 51.7,48.7 49.4,50.4 50.3,53.2 47.9,51.5 45.6,53.2 46.5,50.4 44.1,48.7 47.0,48.7"/><polygon points="37.7,51.3 38.6,54.1 41.5,54.1 39.2,55.8 40.1,58.5 37.7,56.8 35.4,58.5 36.3,55.8 33.9,54.1 36.8,54.1"/><polygon points="26.3,51.3 27.2,54.1 30.1,54.1 27.7,55.8 28.6,58.5 26.3,56.8 23.9,58.5 24.8,55.8 22.5,54.1 25.4,54.1"/><polygon points="16.1,46.0 17.0,48.7 19.9,48.7 17.5,50.4 18.4,53.2 16.1,51.5 13.7,53.2 14.6,50.4 12.3,48.7 15.2,48.7"/><polygon points="9.6,36.5 10.5,39.3 13.4,39.3 11.0,41.0 11.9,43.7 9.6,42.0 7.2,43.7 8.1,41.0 5.8,39.3 8.7,39.3"/><polygon points="8.2,25.1 9.1,27.9 12.0,27.9 9.6,29.6 10.5,32.3 8.2,30.6 5.8,32.3 6.7,29.6 4.4,27.9 7.3,27.9"/><polygon points="12.2,14.4 13.1,17.1 16.1,17.1 13.7,18.8 14.6,21.6 12.2,19.9 9.9,21.6 10.8,18.8 8.4,17.1 11.4,17.1"/><polygon points="20.8,6.7 21.7,9.5 24.7,9.5 22.3,11.2 23.2,14.0 20.8,12.3 18.5,14.0 19.4,11.2 17.0,9.5 19.9,9.5"/></svg>'


def footer_html():
    return f"""<footer class="site-footer">
  <div class="wrap">
    <nav class="foot-nav" aria-label="More">
      <a href="/bill-of-rights/">Bill of Rights</a><a href="/timeline/">Timeline</a><a href="/words/">Words</a><a href="/memorize/">Know it by heart</a>
      <a href="/full-text/">Full text</a><a href="/preamble/">Preamble</a><a href="/declaration/">Declaration</a>
      <a href="/about/">About</a><a href="/sources/">Sources</a>
    </nav>
    <p class="foot-legal">Plain-language explanations, not legal advice. Not reviewed by a lawyer. <a href="/about/">How we check our work</a>.</p>
    <p class="foot-updated">Last updated {fmt_date(TODAY)}</p>
    <div class="hfa">
      {STAR_RING}
      <p class="hfa-mark">A Hope for Americans tool &middot; free to use, the way the web used to be</p>
      <p class="hfa-more"><a class="text-link" href="https://hopeforamericans.net">More free tools from Hope for Americans {icon("right")}</a></p>
      <p class="hfa-madein">Made in Flagstaff, Arizona</p>
    </div>
  </div>
</footer>"""


def mobile_nav():
    items = [("home", "Home", "/"), ("shield", "Situations", "/situations/"),
             ("map", "Paths", "/paths/"), ("book", "Browse", "/amendments/")]
    links = "".join(f'<a href="{h}">{icon(i)}<span>{l}</span></a>' for i, l, h in items)
    return (f'<nav class="mobile-nav" aria-label="Quick navigation"><div class="mobile-nav-row">{links}'
            f'<button type="button" data-open-search>{icon("search")}<span>Search</span></button></div></nav>')


def radio_group(name, legend, options, hint=""):
    opts = "".join(
        f'<label class="seg"><input type="radio" name="{name}" value="{v}"><span>{l}</span></label>'
        for v, l in options)
    h = f'<p class="hint">{hint}</p>' if hint else ""
    return f'<fieldset class="setting"><legend>{legend}</legend>{h}<div class="segs">{opts}</div></fieldset>'


def dialogs():
    display = f"""<dialog id="display-dialog" class="sheet" aria-labelledby="display-title">
  <div class="sheet-head"><h2 id="display-title">{icon("text")} Reading settings</h2>
  <button type="button" class="icon-btn" data-close aria-label="Close">{icon("x")}</button></div>
  <form class="settings" data-display-form>
    {radio_group("size", "Larger type", [("s", "Small"), ("m", "Medium"), ("l", "Large"), ("xl", "Extra large")])}
    {radio_group("spacing", "More space between lines", [("normal", "Normal"), ("roomy", "More space")])}
    {radio_group("font", "Easy-read letters", [("hyper", "Hyperlegible"), ("lexend", "Lexend"), ("serif", "Serif")], "Hyperlegible and Lexend are designed to be easier to read.")}
    <fieldset class="setting"><legend>Focus (hide the menus)</legend><p class="hint">Only the reading stays on screen.</p>
    <button type="button" class="btn btn-quiet" data-toggle-focus>{icon("eye")} Turn on focus</button></fieldset>
    {radio_group("theme", "Night mode", [("light", "Day"), ("sepia", "Sepia"), ("dark", "Night")])}
    {radio_group("depth", "How much to show", [("quick", "Quick"), ("standard", "Standard"), ("deep", "Deep")], "Quick shows the short version. Deep opens everything.")}
    <p class="hint keys">Keys: <kbd>/</kbd> search &middot; <kbd>D</kbd> reading settings &middot; <kbd>T</kbd> night mode &middot; <kbd>G</kbd> focus</p>
    <p class="hint">Saved on this device only.</p>
  </form>
</dialog>"""
    search = f"""<dialog id="search-dialog" class="sheet sheet-search" aria-labelledby="search-title">
  <div class="sheet-head"><h2 id="search-title" class="vh">Search</h2>
  <label class="search-field">{icon("search")}<span class="vh">Search the Constitution</span>
  <input type="search" data-search-input placeholder="Try: phone search, vote, speech at school" autocomplete="off" enterkeyhint="search"></label>
  <button type="button" class="icon-btn" data-close aria-label="Close">{icon("x")}</button></div>
  <div class="search-results" data-search-results aria-live="polite"></div>
</dialog>"""
    extras = f"""<div id="term-pop" class="term-pop" role="dialog" aria-modal="false" hidden><p class="term-def"></p><a class="term-more" href="/words/">More in Words</a><button type="button" class="icon-btn term-close" aria-label="Close">{icon("x")}</button></div>
<div id="path-bar" class="path-bar" hidden></div>
<button type="button" class="focus-exit" data-toggle-focus hidden>{icon("eye")} Exit focus mode</button>
<button type="button" class="back-to-top" aria-label="Back to top">{icon("up")}</button>"""
    return display + search + extras


ORG = {"@type": "Organization", "@id": "https://hopeforamericans.net/#org", "name": "Hope for Americans",
       "url": "https://hopeforamericans.net", "logo": f"{SITE_URL}/static/mark-512.png",
       "address": {"@type": "PostalAddress", "addressLocality": "Flagstaff", "addressRegion": "AZ", "addressCountry": "US"}}
CRUMBS = []


def seo_title(t):
    """Add the brand only when the whole title still fits in about 60 characters."""
    return t if len(t) + len(SITE_NAME) + 3 > 62 or SITE_NAME in t else f"{t} | {SITE_NAME}"


def seo_desc(text, extra=""):
    t = re.sub(r"\s+", " ", plain_text(md(text)) + (" " + extra if extra else "")).strip()
    if len(t) <= 158:
        return t
    cut = t[:157].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + "…"


def article_ld(url, headline, description, image, about=None):
    d = {"@type": "Article", "@id": f"{SITE_URL}{url}#article", "headline": headline[:110], "description": description,
         "url": f"{SITE_URL}{url}", "mainEntityOfPage": f"{SITE_URL}{url}", "image": f"{SITE_URL}{image}",
         "inLanguage": "en-US", "isAccessibleForFree": True, "dateModified": TODAY.isoformat(),
         "author": {"@id": ORG["@id"]}, "publisher": {"@id": ORG["@id"]},
         "isPartOf": {"@id": f"{SITE_URL}/#website"}}
    if about:
        d["about"] = about
    return d


def faq_ld(items):
    if not items:
        return None
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": plain_text(md(q["a"]))}}
        for q in items]}


def page_shell(title, description, body, url, og_image="/static/og/home.jpg",
               og_type="website", jsonld=None, page_title=None, body_class="", robots=None):
    global CRUMBS
    pt = escape(page_title or title.split(" | ")[0])
    graph = []
    for item in (jsonld if isinstance(jsonld, list) else [jsonld]):
        if not item:
            continue
        item = dict(item)
        item.pop("@context", None)
        graph.extend(item["@graph"] if "@graph" in item else [item])
    if CRUMBS:
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": f"{SITE_URL}{h or url}"} for i, (n, h) in enumerate(CRUMBS)]})
    CRUMBS = []
    if graph and not any(g.get("@type") == "Organization" for g in graph):
        graph.append(ORG)
    jsonld = {"@context": "https://schema.org", "@graph": graph} if graph else None
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{head(title, description, url, og_image, og_type, jsonld, robots or "index, follow, max-image-preview:large, max-snippet:-1")}
</head>
<body class="{body_class}" data-page="{escape(url)}" data-page-title="{pt}">
{header_html()}
<main id="main" tabindex="-1">
{body}
</main>
{footer_html()}
{mobile_nav()}
{dialogs()}
<script src="/static/js/app.js?v={ASSET_V}" defer></script>
</body>
</html>"""


# ============================================================
# Components
# ============================================================
def crumbs(*pairs, url=None):
    global CRUMBS
    CRUMBS = [("Home", "/")] + [(label, href or url or "") for label, href in pairs]
    bits = ['<a href="/">Home</a>']
    for label, href in pairs:
        bits.append(f'<a href="{href}">{escape(label)}</a>' if href else f'<span aria-current="page">{escape(label)}</span>')
    return '<nav class="crumbs" aria-label="Breadcrumb">' + '<span aria-hidden="true">›</span>'.join(bits) + "</nav>"


def doc_head(kicker, title, subject, minutes, crumb_html, icon_name="book"):
    sub = f'<p class="subject">{escape(subject)}</p>' if subject else ""
    return f"""<header class="doc-head">
  {crumb_html}
  <p class="kicker">{icon(icon_name)}<span>{kicker}</span></p>
  <h1>{escape(title)}</h1>
  {sub}
  <p class="meta">{icon("clock")}<span>About {minutes} min</span><span class="read-flag" data-read-flag hidden>{icon("check")} Read</span></p>
</header>"""


def one_line_html(ins, label="The one-line version"):
    if not ins.get("one_line"):
        return ""
    return (f'<section class="one-line" aria-label="{label}"><p class="label">{icon("star")}{label}</p>'
            f'<p class="one-line-text">{md(ins["one_line"])}</p></section>')


def heads_up(ins):
    note = ins.get("content_note")
    if not note:
        return ""
    return f'<aside class="heads-up">{icon("info")}<p><strong>Heads-up.</strong> {md(note)}</p></aside>'


def layer(id_, title, icon_name, inner, cls="", tag=""):
    t = f'<p class="tag">{tag}</p>' if tag else ""
    return (f'<section class="layer {cls}" id="{id_}" aria-labelledby="{id_}-h">'
            f'<h2 id="{id_}-h"><span>{title}</span></h2>{t}{inner}</section>')


def plain_and_original(plain_html, verbatim_html, orig_label, used, id_="plain-english", title="Plain English"):
    """`title` becomes the H2, e.g. "The Fourth Amendment in plain English"."""
    linked = TERMS.link(plain_html, used)
    inner = f"""<div class="compare" data-compare>
  <div class="plain-col">{linked}</div>
  <div class="orig-col" id="{id_}-original">
    <p class="label">{icon("quote")}{escape(orig_label)}</p>
    <div class="verbatim">{verbatim_html}</div>
  </div>
</div>
<button type="button" class="btn btn-quiet orig-toggle" data-orig-toggle aria-controls="{id_}-original" aria-expanded="false" hidden>{icon("quote")}<span>Show the original</span></button>"""
    return layer(id_, title, "book", inner)


def phrases_html(ins):
    rows = ins.get("phrases") or []
    if not rows:
        return ""
    items = "".join(
        f'<div class="phrase"><dt><q>{escape(r["quote"])}</q></dt><dd>{md(r["plain"])}</dd></div>'
        for r in rows)
    return layer("phrase-by-phrase", "Phrase by phrase", "list", f'<dl class="phrases">{items}</dl>', "depth-std")


def picture_html(ins):
    if not ins.get("picture_it"):
        return ""
    return layer("picture-it", "Picture it", "bulb", f'<p class="picture-text">{md(ins["picture_it"])}</p>',
                 "picture depth-std", "Example. Not legal advice.")


def cards_html(markdown, used):
    """'What this means for you' split into ### cards."""
    if not markdown:
        return ""
    parts = re.split(r"^### (.+)$", markdown, flags=re.M)
    intro = parts[0].strip()
    out = []
    if intro:
        out.append(f'<div class="cards-intro">{TERMS.link(md_to_html(intro), used)}</div>')
    cards = []
    for i in range(1, len(parts), 2):
        title, body = parts[i].strip(), parts[i + 1].strip()
        cards.append(f'<article class="card"><h3>{md(title)}</h3>{TERMS.link(md_to_html(body), used)}</article>')
    if cards:
        out.append(f'<div class="cards">{"".join(cards)}</div>')
    return layer("what-this-means-for-you", "What this means for you", "shield", "".join(out), "depth-std")


def myths_html(ins):
    items = ins.get("myths") or []
    if not items:
        return ""
    rows = "".join(
        f'<div class="myth"><p class="myth-q"><span class="pill pill-myth">Myth</span>{md(m["myth"])}</p>'
        f'<p class="myth-a"><span class="pill pill-fact">Fact</span>{md(m["fact"])}</p></div>'
        for m in items)
    return layer("myth-check", "Myth check", "help", rows)


def faq_html(items, used=None):
    if not items:
        return ""
    rows = "".join(f'<div class="faq"><h3>{md(q["q"])}</h3><p>{md(q["a"])}</p></div>' for q in items)
    return layer("common-questions", "Common questions", "search", rows)


def fold(title, inner, open_deep=True):
    attr = " data-deep-open" if open_deep else ""
    return f'<details class="fold"{attr}><summary><span>{title}</span>{icon("right", "ic chev")}</summary><div class="fold-body">{inner}</div></details>'


def deeper_html(ins, about_html="", contested=None, extra_folds=""):
    folds = []
    sc = ins.get("scene")
    if sc and sc.get("text"):
        when = f' &middot; {escape(str(sc.get("when")))}' if sc.get("when") else ""
        folds.append(fold(f"The scene{when}", f"<p>{md(sc['text'])}</p>"))
    if ins.get("back_then"):
        folds.append(fold("Back then", f"<p>{md(ins['back_then'])}</p>"))
    wc = ins.get("words_changed") or []
    if wc:
        rows = "".join(
            f'<div class="word-row"><dt>&ldquo;{escape(w["word"])}&rdquo;</dt>'
            f'<dd><p><span class="pill">Then</span>{md(w.get("then"))}</p><p><span class="pill pill-now">Now</span>{md(w.get("now"))}</p></dd></div>'
            for w in wc)
        folds.append(fold("Words that changed", f'<dl class="words-changed">{rows}</dl>'))
    wa = ins.get("who_argued") or []
    if wa:
        rows = "".join(f'<div class="side"><h4>{md(s["side"])}</h4><p>{md(s["view"])}</p></div>' for s in wa)
        folds.append(fold("Who argued what", f'<div class="sides">{rows}</div>'))
    kc = ins.get("key_cases") or []
    if kc:
        rows = "".join(
            f'<li><span class="case-year">{escape(str(k["year"]))}</span><div><p class="case-name"><em class="case">{escape(k["name"])}</em></p><p>{md(k["held"])}</p></div></li>'
            for k in kc)
        folds.append(fold("Key cases", f'<ol class="cases">{rows}</ol>'))
    if about_html:
        folds.append(fold("More history and context", about_html))
    if contested:
        lis = "".join(f"<li>{md(c)}</li>" for c in contested)
        folds.append(fold("Actively contested",
                          f"<p>Courts are still deciding parts of this. Open questions include:</p><ul>{lis}</ul>"))
    folds.append(extra_folds)
    folds = [f for f in folds if f]
    if not folds:
        return ""
    return layer("go-deeper", "Go deeper", "layers", "".join(folds), "depth-std deeper")


def quiz_html(ins):
    qs = ins.get("quick_check") or []
    if not qs:
        return ""
    out = []
    for i, q in enumerate(qs):
        opts = "".join(
            f'<button type="button" class="qc-opt" data-i="{j}">{md(o)}</button>' for j, o in enumerate(q["options"]))
        out.append(f'<fieldset class="qc" data-answer="{q["answer"]}"><legend>{i + 1}. {md(q["q"])}</legend>'
                   f'<div class="qc-opts">{opts}</div><p class="qc-why" hidden aria-live="polite">{md(q["why"])}</p></fieldset>')
    return layer("quick-check", "Quick check", "check", "".join(out), "", "Just for you. Nothing is saved.")


def related_situations_html(slugs, situations_by_slug):
    cards = []
    for s in slugs or []:
        f = situations_by_slug.get(s)
        if not f:
            continue
        cards.append(f'<a class="mini-card" href="/situations/{s}/">{icon(f.get("icon", "shield"))}<span>{escape(f["title"])}</span>{icon("right", "ic go")}</a>')
    if not cards:
        return ""
    return layer("if-this-is-happening", "If this is happening to you", "lifebuoy", f'<div class="mini-cards">{"".join(cards)}</div>')


def accuracy_note(source_url=None, kind="page"):
    src = f' Original text from the <a href="{source_url}" rel="noopener">National Archives</a>.' if source_url else ""
    return f"""<aside class="accuracy">
  <p class="label">{icon("info")}How this page was made</p>
  <p>{src.strip()} Plain-language parts written by Hope for Americans and fact-checked against the text and the Supreme Court cases named. <strong>Not reviewed by a lawyer. Not legal advice.</strong> Last updated {fmt_date(TODAY)}.</p>
  <p><a href="{CONTACT_URL}" rel="noopener">Spot a mistake? Tell us.</a> &middot; <a href="/about/">How we check our work</a></p>
</aside>"""


def pager(prev, nxt):
    """prev/next = (label, sublabel, href) or None"""
    def one(p, cls, ic, word):
        if not p:
            return "<span></span>"
        return (f'<a class="pager {cls}" href="{p[2]}">{icon(ic) if cls == "prev" else ""}'
                f'<span><span class="pager-word">{word}</span><span class="pager-label">{escape(p[0])}</span></span>'
                f'{icon(ic) if cls == "next" else ""}</a>')
    return (f'<nav class="pager-row" aria-label="Next and previous">{one(prev, "prev", "left", "Previous")}'
            f'{one(nxt, "next", "right", "Next")}</nav><div id="page-end" aria-hidden="true"></div>')


# ============================================================
# Page builders
# ============================================================
SITUATIONS = {}   # slug -> front


def render_amendment(a, prev_a, next_a, all_ins):
    f, body = a["front"], a["body"]
    n = f["number"]
    ins = all_ins[n]
    S = split_h2(body)
    used = set()
    verb_md, plain_md = sec(S, "Verbatim"), sec(S, "Plain English")
    meaning_md, about_md = sec(S, "What this means for you"), sec(S, "About")
    verb_html, plain_html = md_to_html(verb_md, 1), md_to_html(plain_md, 1)
    about_html = TERMS.link(md_to_html(about_md, 1), used)
    yr = year_of(f.get("ratified"))
    part = " &middot; Bill of Rights" if n <= 10 else ""
    mins = minutes_for(ins.get("one_line"), plain_html, md_to_html(meaning_md),
                       " ".join(p["plain"] for p in ins.get("phrases") or []),
                       " ".join(m["myth"] + " " + m["fact"] for m in ins.get("myths") or []))
    url = f"/amendments/{n}/"
    title = f"{ORDINALS[n]} Amendment"
    subject = ins.get("subject", "")
    body_html = f"""<article class="doc wrap">
{doc_head(f"Amendment {n} of 27{part} &middot; {yr}", title, subject, mins, crumbs(("Amendments", "/amendments/"), (str(n), None)), "scales")}
{heads_up(ins)}
{one_line_html(ins)}
{plain_and_original(plain_html, verb_html, f"Original text, {yr}", used, title=f"The {title} in plain English")}
{phrases_html(ins)}
{picture_html(ins)}
{cards_html(meaning_md, used)}
{myths_html(ins)}
{faq_html(ins.get("faq"))}
{deeper_html(ins, about_html, f.get("contested"))}
{quiz_html(ins)}
{related_situations_html(f.get("related_situations"), SITUATIONS)}
{accuracy_note(f.get("source_url"))}
{pager((f"{ORDINALS[prev_a]} Amendment", "", f"/amendments/{prev_a}/") if prev_a else None,
       (f"{ORDINALS[next_a]} Amendment", "", f"/amendments/{next_a}/") if next_a else None)}
</article>"""
    desc = ins.get("seo_description") or seo_desc(f"The {title} in plain English: {ins.get('one_line', '')}")
    stitle = ins.get("seo_title") or f"{title}: {subject} in Plain English"
    og = f"/static/og/amendment-{n}.jpg"
    jld = [article_ld(url, stitle, desc, og, {"@type": "Legislation", "name": f"{title} to the United States Constitution",
                                               "alternateName": f"Amendment {n}", "legislationIdentifier": f"U.S. Const. amend. {roman_num(n)}"}),
           faq_ld(ins.get("faq"))]
    write(url, page_shell(seo_title(stitle), desc, body_html, url, og_image=og, og_type="article", jsonld=jld, page_title=title))
    register(url, f"{title}: {subject}" if subject else title, "Amendment", mins, ins.get("one_line", ""),
             " ".join([subject, plain_text(plain_html), plain_text(md_to_html(meaning_md))] + [q["q"] + " " + q["a"] for q in ins.get("faq") or []]), "scales",
             quick=minutes_for(ins.get("one_line"), plain_html, " ".join(m["myth"] + " " + m["fact"] for m in ins.get("myths") or [])))
    return url


def roman_num(n):
    vals = [(10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]
    out = ""
    for v, r in vals:
        while n >= v:
            out += r; n -= v
    return out


def split_article(body):
    """Return (sections list [(n, title, verbatim_md, plain_md)], verbatim_md, plain_md)."""
    S = split_h2(body)
    v, p = sec(S, "Verbatim"), sec(S, "Plain English")
    vparts = re.split(r"(?m)^(?=\*\*Section \d+\.\*\*)", v)
    vparts = [x.strip() for x in vparts if x.strip().startswith("**Section")]
    pparts = re.split(r"(?m)^### Section (\d+)\s*[—–-]\s*(.+)$", p)
    psecs = []
    for i in range(1, len(pparts), 3):
        psecs.append((int(pparts[i]), pparts[i + 1].strip(), pparts[i + 2].strip()))
    out = []
    for i, (num, title, pm) in enumerate(psecs):
        vm = vparts[i] if i < len(vparts) else ""
        out.append((num, title, vm, pm))
    return out, v, p, S


def render_article(art, prev_n, next_n):
    f, body = art["front"], art["body"]
    n = f["number"]
    ins = load_insight(f"article-{n}")
    secs, v, p, S = split_article(body)
    used = set()
    about_html = TERMS.link(md_to_html(sec(S, "About"), 1), used)
    yr = year_of(f.get("ratified"))
    name = ARTICLE_NAMES[n]
    url = f"/articles/{n}/"
    title = f"Article {ROMAN[n]}: {name}"
    sec_urls = []
    if secs:
        one_lines = ins.get("sections") or {}
        cards = []
        total = 0
        for num, stitle, vm, pm in secs:
            smins = minutes_for(md_to_html(pm))
            total += smins
            surl = f"/articles/{n}/section-{num}/"
            sec_urls.append(surl)
            ol = one_lines.get(num) or one_lines.get(str(num)) or ""
            cards.append(f'<a class="sec-card" href="{surl}" data-progress-url="{surl}"><span class="sec-num">§{num}</span>'
                         f'<span class="sec-body"><span class="sec-title">{escape(stitle)}</span><span class="sec-line">{md(ol)}</span>'
                         f'<span class="sec-min">{icon("clock")}{smins} min</span></span>{icon("check", "ic done")}</a>')
        main_block = layer("sections", f"The {len(secs)} sections", "list",
                           f'<p class="tag">One section at a time. Tap to read.</p><div class="sec-cards">{"".join(cards)}</div>')
        mins = max(2, minutes_for(ins.get("one_line"), " ".join(r["plain"] for r in ins.get("phrases") or [])) + 1)
        start_btn = f'<p><a class="btn btn-primary" href="{sec_urls[0]}">Start with Section 1 {icon("right")}</a></p>'
    else:
        main_block = plain_and_original(md_to_html(p, 1), md_to_html(v, 1), f"Original text, {yr}", used)
        mins = minutes_for(ins.get("one_line"), md_to_html(p))
        start_btn = ""
    body_html = f"""<article class="doc wrap">
{doc_head(f"Article {ROMAN[n]} of VII &middot; {yr}", title, ins.get("subject", ""), mins, crumbs(("Articles", "/articles/"), (f"Article {ROMAN[n]}", None)), "columns")}
{heads_up(ins)}
{one_line_html(ins)}
{start_btn}
{main_block}
{phrases_html(ins)}
{picture_html(ins)}
{myths_html(ins)}
{faq_html(ins.get("faq"))}
{deeper_html(ins, about_html, f.get("contested"))}
{quiz_html(ins)}
{accuracy_note(f.get("source_url"))}
{pager((f"Article {ROMAN[prev_n]}", "", f"/articles/{prev_n}/") if prev_n else ("Preamble", "", "/preamble/"),
       (f"Article {ROMAN[next_n]}", "", f"/articles/{next_n}/") if next_n else ("First Amendment", "", "/amendments/1/"))}
</article>"""
    desc = ins.get("seo_description") or seo_desc(f"Article {ROMAN[n]} of the Constitution ({name}) in plain English. {ins.get('one_line', '')}")
    stitle = ins.get("seo_title") or f"{title} in Plain English"
    og = f"/static/og/article-{n}.jpg"
    jld = [article_ld(url, stitle, desc, og, {"@type": "Legislation", "name": f"Article {ROMAN[n]} of the United States Constitution",
                                               "legislationIdentifier": f"U.S. Const. art. {ROMAN[n]}"}), faq_ld(ins.get("faq"))]
    write(url, page_shell(seo_title(stitle), desc, body_html, url, og_image=og, og_type="article", jsonld=jld, page_title=f"Article {ROMAN[n]}"))
    register(url, title, "Article", mins, ins.get("one_line", ""), " ".join([name, plain_text(md_to_html(p))]), "columns")

    # one page per section
    for i, (num, stitle, vm, pm) in enumerate(secs):
        surl = sec_urls[i]
        used_s = set()
        ol = (ins.get("sections") or {}).get(num) or (ins.get("sections") or {}).get(str(num)) or ""
        smins = minutes_for(md_to_html(pm))
        prev_s = (f"Section {secs[i - 1][0]}: {secs[i - 1][1]}", "", sec_urls[i - 1]) if i > 0 else (f"Article {ROMAN[n]} overview", "", url)
        next_s = (f"Section {secs[i + 1][0]}: {secs[i + 1][1]}", "", sec_urls[i + 1]) if i < len(secs) - 1 else \
                 ((f"Article {ROMAN[next_n]}", "", f"/articles/{next_n}/") if next_n else ("First Amendment", "", "/amendments/1/"))
        vm_clean = re.sub(r"^\*\*Section \d+\.\*\*\s*", "", vm)
        sbody = f"""<article class="doc wrap">
{doc_head(f"Article {ROMAN[n]} &middot; Section {num} of {len(secs)}", stitle, f"Article {ROMAN[n]}: {name}", smins, crumbs(("Articles", "/articles/"), (f"Article {ROMAN[n]}", url), (f"Section {num}", None)), "columns")}
{heads_up(ins) if (num == 2 and n in (1, 4)) or (num == 9 and n == 1) else ""}
{f'<section class="one-line"><p class="label">{icon("star")}The one-line version</p><p class="one-line-text">{md(ol)}</p></section>' if ol else ""}
{plain_and_original(md_to_html(pm, 1), md_to_html(vm_clean, 1), f"Original text, {yr}", used_s, title=f"Section {num} in plain English")}
<div class="sec-progress" aria-label="Sections in this article">{"".join(f'<a href="{u}" class="{"on" if j == i else ""}" aria-label="Section {secs[j][0]}">{secs[j][0]}</a>' for j, u in enumerate(sec_urls))}</div>
{accuracy_note(f.get("source_url"))}
{pager(prev_s, next_s)}
</article>"""
        sdesc = seo_desc(f"Article {ROMAN[n]}, Section {num} of the U.S. Constitution in plain English: {ol}", "Original text and a simple explanation.")
        small = {"a", "an", "and", "the", "of", "to", "in", "on", "for", "by", "or", "at", "is", "are", "they"}
        tt = " ".join(w if (i and w.lower() in small) else w[:1].upper() + w[1:] for i, w in enumerate(stitle.split()))
        st = f"Article {ROMAN[n]}, Section {num} Explained: {tt}"
        if len(st) > 60:
            st = f"Art. {ROMAN[n]}, Sec. {num} Explained: {tt}"
        jld = article_ld(surl, st, sdesc, f"/static/og/article-{n}.jpg",
                         {"@type": "Legislation", "name": f"Article {ROMAN[n]}, Section {num} of the United States Constitution"})
        write(surl, page_shell(seo_title(st), sdesc, sbody, surl, og_image=f"/static/og/article-{n}.jpg",
                               og_type="article", jsonld=jld, page_title=f"Article {ROMAN[n]}, Section {num}"))
        register(surl, f"Article {ROMAN[n]}, Section {num}: {stitle}", "Article section", smins, ol,
                 plain_text(md_to_html(pm)), "columns")
    return url


def render_preamble():
    f, body = load_md(CONTENT / "preamble.md")
    ins = load_insight("preamble")
    S = split_h2(body)
    used = set()
    plain_html = md_to_html(sec(S, "Plain English"), 1)
    about_html = TERMS.link(md_to_html(sec(S, "About"), 1), used)
    mins = minutes_for(ins.get("one_line"), plain_html, " ".join(r["plain"] for r in ins.get("phrases") or []))
    url = "/preamble/"
    body_html = f"""<article class="doc wrap">
{doc_head("The Constitution &middot; 1787", "The Preamble", ins.get("subject", "Why the Constitution exists"), mins, crumbs(("Preamble", None)), "flag")}
{one_line_html(ins)}
{plain_and_original(plain_html, md_to_html(sec(S, "Verbatim"), 1), "Original text, 1787", used, title="The Preamble in plain English")}
{phrases_html(ins)}
{picture_html(ins)}
{myths_html(ins)}
{faq_html(ins.get("faq"))}
{deeper_html(ins, about_html)}
{quiz_html(ins)}
<p class="inline-cta"><a class="btn btn-quiet" href="/memorize/#preamble">{icon("brain")} Learn it by heart</a></p>
{accuracy_note(f.get("source_url"))}
{pager(None, ("Article I: Congress", "", "/articles/1/"))}
</article>"""
    desc = ins.get("seo_description") or "The Preamble to the U.S. Constitution in plain English, phrase by phrase."
    stitle = ins.get("seo_title") or "The Preamble in Plain English"
    jld = [article_ld(url, stitle, desc, "/static/og/preamble.jpg", {"@type": "Legislation", "name": "Preamble to the United States Constitution"}),
           faq_ld(ins.get("faq"))]
    write(url, page_shell(seo_title(stitle), desc, body_html, url, og_image="/static/og/preamble.jpg", og_type="article",
                          jsonld=jld, page_title="The Preamble"))
    register(url, "The Preamble", "Preamble", mins, ins.get("one_line", ""), plain_text(plain_html), "flag")


def render_declaration():
    f, body = load_md(CONTENT / "declaration.md")
    ins = load_insight("declaration")
    S = split_h2(body)
    used = set()
    blocks, about_bits, all_plain = [], [], []
    for h, m in S:
        if h.lower().startswith("verbatim"):
            continue
        if h.lower().startswith("plain english"):
            part = h.split("—", 1)[1].strip() if "—" in h else "Text"
            vm = next((mm for hh, mm in S if hh.lower().startswith("verbatim") and hh.endswith(part)), "")
            pid = "part-" + slugify(part)
            ph = md_to_html(m, 1)
            all_plain.append(ph)
            blocks.append(plain_and_original(ph, md_to_html(vm, 1), "Original text, 1776", used, pid, part))
        else:
            about_bits.append(fold(escape(h), TERMS.link(md_to_html(m, 1), used)))
    mins = minutes_for(ins.get("one_line"), *all_plain)
    url = "/declaration/"
    body_html = f"""<article class="doc wrap">
{doc_head("Founding document &middot; July 4, 1776", "The Declaration of Independence", ins.get("subject", "Why the colonies broke away"), mins, crumbs(("Declaration", None)), "flag")}
<aside class="heads-up">{icon("info")}<p><strong>Not part of the Constitution.</strong> The Declaration is not law. It explains why the country was founded, 11 years before the Constitution.</p></aside>
{heads_up(ins)}
{one_line_html(ins)}
{"".join(blocks)}
{phrases_html(ins)}
{picture_html(ins)}
{myths_html(ins)}
{faq_html(ins.get("faq"))}
{deeper_html(ins, "", None, "".join(about_bits))}
{quiz_html(ins)}
{accuracy_note("https://www.archives.gov/founding-docs/declaration-transcript")}
{pager(None, ("The Preamble", "", "/preamble/"))}
</article>"""
    desc = ins.get("seo_description") or "The Declaration of Independence in plain English, with the original text one tap away."
    stitle = ins.get("seo_title") or "The Declaration of Independence in Plain English"
    jld = [article_ld(url, stitle, desc, "/static/og/declaration.jpg", {"@type": "CreativeWork", "name": "Declaration of Independence", "dateCreated": "1776-07-04"}),
           faq_ld(ins.get("faq"))]
    write(url, page_shell(seo_title(stitle), desc, body_html, url, og_image="/static/og/declaration.jpg", og_type="article",
                          jsonld=jld, page_title="The Declaration of Independence"))
    register(url, "The Declaration of Independence", "Founding document", mins, ins.get("one_line", ""),
             " ".join(plain_text(x) for x in all_plain), "flag")


def render_situation(s, prev_s, next_s):
    f, body = s["front"], s["body"]
    slug = f["slug"]
    url = f"/situations/{slug}/"
    used = set()
    S = split_h2(body)
    ten = f.get("ten_second") or []
    ten_html = "".join(f"<li>{md(t)}</li>" for t in ten)
    note = f'<p class="ten-note">{md(f.get("ten_second_note"))}</p>' if f.get("ten_second_note") else ""
    do = "".join(f"<li>{icon('check')}<span>{md(x)}</span></li>" for x in f.get("do") or [])
    dont = "".join(f"<li>{icon('x')}<span>{md(x)}</span></li>" for x in f.get("dont") or [])
    sections, law = [], ""
    for h, m in S:
        if h.lower().startswith("the law you are citing"):
            law = fold("The law you are citing", md_to_html(m, 1), open_deep=True)
            continue
        hid = slugify(h)
        sections.append(f'<section class="sit-sec" id="{hid}"><h2>{escape(h)}</h2>{TERMS.link(md_to_html(m, 1), used)}</section>')
    helps = ""
    if f.get("help"):
        items = []
        for h in f["help"]:
            href = h.get("href") or ""
            val = escape(h.get("value") or "")
            inner = f'<a href="{escape(href)}" rel="noopener">{val}</a>' if href else val
            items.append(f'<li><span class="help-label">{escape(h["label"])}</span><span class="help-val">{inner}</span></li>')
        helps = layer("get-help", "Get help", "lifebuoy", f'<ul class="help-list">{"".join(items)}</ul>')
    varies = f'<aside class="heads-up">{icon("map")}<p><strong>Depends on your state.</strong> {md(f["state_varies"])}</p></aside>' if f.get("state_varies") else ""
    rel = f.get("related_amendments") or []
    rel_html = ""
    if rel:
        links = "".join(f'<a class="mini-card" href="/amendments/{n}/">{icon("scales")}<span>{ORDINALS[n]} Amendment</span>{icon("right", "ic go")}</a>' for n in rel)
        rel_html = layer("the-law-behind-this", "The law behind this card", "scales", f'<div class="mini-cards">{links}</div>')
    mins = minutes_for(" ".join(ten), " ".join(f.get("do") or []), " ".join(f.get("dont") or []), md_to_html(body))
    wallet = escape(json.dumps({"title": f["title"], "lines": ten}))
    body_html = f"""<article class="doc wrap situation">
{doc_head("Situation card &middot; Know your rights", f.get("h1") or f["title"], f.get("summary", ""), mins, crumbs(("Know your rights", "/situations/"), (f["title"], None)), f.get("icon", "shield"))}
<section class="ten-second" aria-labelledby="ten-h" data-wallet="{wallet}">
  <p class="label" id="ten-h">{icon("clock")}The 10-second version: say this</p>
  <ol class="ten-lines">{ten_html}</ol>
  {note}
  <div class="ten-actions">
    <button type="button" class="btn btn-light" data-show-screen>{icon("expand")} Show on screen</button>
    <button type="button" class="btn btn-light" data-save-offline>{icon("download")} Save to phone</button>
    <button type="button" class="btn btn-light" data-print-wallet>{icon("printer")} Print wallet card</button>
  </div>
  <p class="save-status" data-save-status aria-live="polite" hidden></p>
</section>
<section class="dodont" aria-label="Do and don't">
  <div class="do"><h2>{icon("check")}Do</h2><ul>{do}</ul></div>
  <div class="dont"><h2>{icon("x")}Don't</h2><ul>{dont}</ul></div>
</section>
{varies}
{"".join(sections)}
{faq_html(f.get("faq"))}
{f'<section class="layer depth-std">{law}</section>' if law else ""}
{helps}
{rel_html}
{accuracy_note()}
{pager((prev_s["front"]["title"], "", f"/situations/{prev_s['front']['slug']}/") if prev_s else ("All situations", "", "/situations/"),
       (next_s["front"]["title"], "", f"/situations/{next_s['front']['slug']}/") if next_s else ("All situations", "", "/situations/"))}
</article>
<div class="screen-mode" data-screen-mode hidden role="dialog" aria-modal="true" aria-label="{escape(f['title'])}: say this">
  <button type="button" class="screen-close" data-screen-close>{icon("x")} Close</button>
  <ol>{ten_html}</ol>
</div>"""
    desc = f.get("seo_description") or seo_desc(f.get("summary", ""))
    stitle = f.get("seo_title") or f"{f['title']}: Know Your Rights"
    og = f"/static/og/situation-{slug}.jpg"
    jld = [article_ld(url, stitle, desc, og), faq_ld(f.get("faq"))]
    write(url, page_shell(seo_title(stitle), desc, body_html, url, og_image=og, og_type="article", jsonld=jld,
                          page_title=f["title"], body_class="is-situation"))
    register(url, f.get("h1") or f["title"], "Situation", mins, desc, " ".join([desc, " ".join(ten), plain_text(md_to_html(body))] + [q["q"] + " " + q["a"] for q in f.get("faq") or []]),
             f.get("icon", "shield"))
    return url


def sit_card(f):
    return (f'<a class="sit-card" href="/situations/{f["slug"]}/" data-progress-url="/situations/{f["slug"]}/">'
            f'<span class="sit-ic">{icon(f.get("icon", "shield"))}</span>'
            f'<span class="sit-body"><span class="sit-title">{escape(f["title"])}</span>'
            f'<span class="sit-sum">{escape(f.get("summary", ""))}</span>'
            f'<span class="sit-min">{icon("clock")}{PAGES.get("/situations/" + f["slug"] + "/", {}).get("minutes", 2)} min</span></span>'
            f'{icon("right", "ic go")}</a>')


def render_situations_index(situations):
    cards = "".join(sit_card(s["front"]) for s in situations)
    url = "/situations/"
    body = f"""<section class="wrap page">
  {crumbs(("Know your rights", None))}
  <h1>Know your rights: what to say when it matters</h1>
  <p class="lede">Pocket cards for the moments when your rights matter: police stops, searches, school, posting online, work, protests, voting, and immigration agents. Each card starts with exactly what to say, then what to do and not do.</p>
  <p class="hint">{icon("download")} Every card works offline after you open it once.</p>
  <div class="sit-grid">{cards}</div>
  <p class="legal-note">These cards explain the law in general. They are not legal advice and have not been reviewed by a lawyer.</p>
</section>"""
    items = [{"@type": "ListItem", "position": i + 1, "url": f"{SITE_URL}/situations/{x['front']['slug']}/", "name": x["front"].get("h1") or x["front"]["title"]}
             for i, x in enumerate(situations)]
    jld = {"@type": "CollectionPage", "name": "Know your rights: situation cards", "url": f"{SITE_URL}{url}",
           "mainEntity": {"@type": "ItemList", "itemListElement": items}}
    write(url, page_shell("Know Your Rights: What to Say to Police, at School & More",
                          "Plain-English know-your-rights cards: what to say if police question or search you, and your rights at school, online, at work, at protests, and voting.",
                          body, url, og_image="/static/og/situation-default.jpg", page_title="Know your rights", jsonld=jld))
    register(url, "Situation cards", "Index", 1, "What to say when it matters.", "", "shield")


def amend_cell(n, subject):
    u = f"/amendments/{n}/"
    return (f'<a class="amend-cell" href="{u}" data-progress-url="{u}"><span class="num">{n}</span>'
            f'<span class="amend-info"><span class="title">{ORDINALS[n]}</span><span class="subject">{escape(subject)}</span></span>'
            f'{icon("check", "ic done")}</a>')


def render_amendments_index(amendments, all_ins):
    bor = "".join(amend_cell(a["front"]["number"], all_ins[a["front"]["number"]].get("subject", "")) for a in amendments if a["front"]["number"] <= 10)
    rest = "".join(amend_cell(a["front"]["number"], all_ins[a["front"]["number"]].get("subject", "")) for a in amendments if a["front"]["number"] > 10)
    url = "/amendments/"
    body = f"""<section class="wrap page">
  {crumbs(("Amendments", None))}
  <h1>All 27 amendments, explained</h1>
  <p class="lede">Every change added to the Constitution since 1787, in plain English. The first ten are the <a href="/bill-of-rights/">Bill of Rights</a>.</p>
  <p class="progress-line" data-progress-count data-of="27" data-prefix="/amendments/" hidden></p>
  <h2 class="grid-label">Bill of Rights, 1791</h2>
  <div class="amend-grid">{bor}</div>
  <h2 class="grid-label">Later amendments, 1795 to 1992</h2>
  <div class="amend-grid">{rest}</div>
</section>"""
    items = [{"@type": "ListItem", "position": a["front"]["number"], "url": f"{SITE_URL}/amendments/{a['front']['number']}/",
              "name": f"{ORDINALS[a['front']['number']]} Amendment: {all_ins[a['front']['number']].get('subject', '')}"} for a in amendments]
    jld = {"@type": "CollectionPage", "name": "All 27 amendments to the U.S. Constitution", "url": f"{SITE_URL}{url}",
           "mainEntity": {"@type": "ItemList", "itemListElement": items}}
    write(url, page_shell("All 27 Amendments Explained in Plain English | Free Constitution",
                          "All 27 amendments to the U.S. Constitution explained in plain English, from free speech and the Bill of Rights to voting rights and term limits.",
                          body, url, og_image="/static/og/amendment-default.jpg", page_title="Amendments", jsonld=jld))
    register(url, "All 27 amendments", "Index", 1, "", "", "scales")


BOR_FAQ = [
    {"q": "What is the Bill of Rights in simple terms?",
     "a": "It is the first ten amendments to the U.S. Constitution. They list freedoms the government cannot take away, like free speech, freedom of religion, protection from unreasonable searches, and the right to a fair trial."},
    {"q": "What are the 10 amendments in the Bill of Rights?",
     "a": "1st: religion, speech, press, assembly, petition. 2nd: keep and bear arms. 3rd: no forced housing of soldiers. 4th: no unreasonable searches. 5th: due process and the right to silence. 6th: a fair criminal trial and a lawyer. 7th: juries in civil cases. 8th: no excessive bail or cruel punishment. 9th: other rights exist. 10th: powers kept by states and people."},
    {"q": "When was the Bill of Rights ratified?",
     "a": "December 15, 1791. That day, Virginia's approval gave the amendments the three-fourths of states they needed to become part of the Constitution. Two other amendments Congress proposed with them were not ratified at that time."},
    {"q": "Who wrote the Bill of Rights?",
     "a": "James Madison drafted it. He drew on state declarations of rights, especially Virginia's, written by George Mason. Congress revised Madison's proposals and sent 12 amendments to the states in 1789. Ten were approved."},
    {"q": "Why was the Bill of Rights added to the Constitution?",
     "a": "To win support for the new Constitution. Anti-Federalists feared a strong national government would trample personal freedoms. Supporters promised to add a list of rights after ratification, and Madison followed through in 1789."},
    {"q": "Does the Bill of Rights apply to states?",
     "a": "Mostly, yes, today. At first it limited only the federal government (Barron v. Baltimore, 1833). Through the 14th Amendment, the Supreme Court has applied most of its protections to states and cities. This is called incorporation."},
]


def render_bill_of_rights(amendments, all_ins):
    url = "/bill-of-rights/"
    used = set()
    rows = "".join(
        f'<a class="sec-card" href="/amendments/{n}/" data-progress-url="/amendments/{n}/"><span class="sec-num">{n}</span>'
        f'<span class="sec-body"><span class="sec-title">{ORDINALS[n]} Amendment: {escape(all_ins[n].get("subject", ""))}</span>'
        f'<span class="sec-line">{md(all_ins[n].get("one_line", ""))}</span></span>{icon("check", "ic done")}</a>'
        for n in range(1, 11))
    why = TERMS.link(md_to_html(
        "The original Constitution of 1787 set up the government but listed few personal rights. Many Americans, called Anti-Federalists, would not support it without a list of rights.\n\n"
        "James Madison drafted amendments in 1789. Congress sent 12 to the states. Ten were ratified on December 15, 1791. One of the other two became the 27th Amendment in 1992."), used)
    who = TERMS.link(md_to_html(
        "At first, the Bill of Rights limited only the federal government. The Supreme Court said so in *Barron v. Baltimore* (1833).\n\n"
        "After the 14th Amendment (1868), the Court applied most of the Bill of Rights to state and local governments too, one right at a time. This is called incorporation. "
        "The Bill of Rights still does not limit private companies, stores, or employers."), used)
    body = f"""<article class="doc wrap">
{doc_head("The first ten amendments &middot; 1791", "The Bill of Rights in plain English", "What each of the first ten amendments protects", 4,
          crumbs(("Amendments", "/amendments/"), ("Bill of Rights", None)), "scales")}
<section class="one-line"><p class="label">{icon("star")}The one-line version</p><p class="one-line-text">The Bill of Rights is the first ten amendments to the Constitution. Ratified in 1791, it protects freedoms like speech, religion, and a fair trial from the government.</p></section>
{layer("the-ten", "The ten amendments at a glance", "list", f'<div class="sec-cards">{rows}</div>')}
{layer("why-it-was-added", "Why it was added", "flag", why)}
{layer("who-it-protects-you-from", "Who it protects you from", "shield", who)}
{faq_html(BOR_FAQ)}
{accuracy_note("https://www.archives.gov/founding-docs/bill-of-rights-transcript")}
{pager(("All 27 amendments", "", "/amendments/"), ("First Amendment", "", "/amendments/1/"))}
</article>"""
    desc = "The Bill of Rights in plain English: what each of the first ten amendments protects, why it was added in 1791, and whether it applies to your state."
    jld = [article_ld(url, "The Bill of Rights in Plain English", desc, "/static/og/bill-of-rights.jpg",
                      {"@type": "Legislation", "name": "Bill of Rights", "legislationIdentifier": "U.S. Const. amends. I-X"}), faq_ld(BOR_FAQ)]
    write(url, page_shell("The Bill of Rights in Plain English: All 10 Amendments", desc, body, url,
                          og_image="/static/og/bill-of-rights.jpg", og_type="article", jsonld=jld, page_title="The Bill of Rights"))
    register(url, "The Bill of Rights", "Bill of Rights", 4, "The first ten amendments, explained.",
             " ".join(q["q"] + " " + q["a"] for q in BOR_FAQ).lower() + " bill of rights first ten amendments", "scales")


def render_articles_index(articles):
    rows = ""
    for art in articles:
        n = art["front"]["number"]
        ins = load_insight(f"article-{n}")
        u = f"/articles/{n}/"
        rows += (f'<a class="article-row" href="{u}" data-progress-url="{u}"><span class="num">Article {ROMAN[n]}</span>'
                 f'<span class="art-body"><span class="title">{escape(ARTICLE_NAMES[n])}</span>'
                 f'<span class="sit-sum">{md(ins.get("one_line", ""))}</span></span>{icon("right", "ic go")}</a>')
    url = "/articles/"
    body = f"""<section class="wrap page">
  {crumbs(("Articles", None))}
  <h1>The 7 articles of the Constitution, explained</h1>
  <p class="lede">Seven articles, approved in 1788. They set up the government. Start with the <a href="/preamble/">Preamble</a>, the one-sentence mission statement.</p>
  <div class="article-list">{rows}</div>
  <p><a class="btn btn-quiet" href="/full-text/">{icon("book")} Read the whole Constitution on one page</a></p>
</section>"""
    write(url, page_shell("The 7 Articles of the Constitution Explained Simply",
                          "The seven articles of the U.S. Constitution in plain English: Congress, the President, the courts, the states, amendments, and the supreme law.",
                          body, url, page_title="Articles"))
    register(url, "The seven articles", "Index", 1, "", "", "columns")


def path_minutes(p):
    """Time for the short version of each step (Quick depth)."""
    return sum(PAGES.get(s["href"].split("#")[0], {}).get("quick") or 2 for s in p["steps"])


def render_paths(paths):
    cards = ""
    for p in paths:
        m = path_minutes(p)
        cards += (f'<a class="path-card" href="/paths/{p["slug"]}/" data-path-card="{p["slug"]}">'
                  f'<span class="path-ic">{icon(p.get("icon", "map"))}</span>'
                  f'<span class="path-body"><span class="path-title">{escape(p["title"])}</span>'
                  f'<span class="sit-sum">{escape(p["blurb"])}</span>'
                  f'<span class="path-meta">{icon("clock")}{m} min &middot; {len(p["steps"])} steps<span class="path-prog" data-path-prog></span></span></span>'
                  f'{icon("right", "ic go")}</a>')
    url = "/paths/"
    body = f"""<section class="wrap page">
  {crumbs(("Paths", None))}
  <h1>Paths</h1>
  <p class="lede">Short guided routes through the Constitution. Each step is one page. Your progress stays on this device.</p>
  <div class="path-grid">{cards}</div>
</section>"""
    write(url, page_shell("Learn Your Rights Step by Step: Guided Paths | Free Constitution",
                          "Short guided reading paths: your rights in 10 minutes, getting pulled over, rights at school, first-time voter, and how the government works.",
                          body, url, og_image="/static/og/paths.jpg", page_title="Paths"))
    register(url, "Paths", "Index", 1, "", "", "map")
    for p in paths:
        steps = ""
        for i, s in enumerate(p["steps"]):
            href = s["href"]
            pg = PAGES.get(href.split("#")[0], {})
            sep = "&" if "?" in href else "?"
            steps += (f'<li class="step" data-progress-url="{href.split("#")[0]}"><a href="{href}{sep}path={p["slug"]}">'
                      f'<span class="step-n">{i + 1}</span><span class="step-body"><span class="step-label">{escape(s["label"])}</span>'
                      f'<span class="step-why">{escape(s["why"])}</span>'
                      f'<span class="step-meta">{escape(pg.get("title", ""))} &middot; {pg.get("quick") or 2} min</span></span>'
                      f'{icon("check", "ic done")}</a></li>')
        first = p["steps"][0]["href"]
        sep = "&" if "?" in first else "?"
        purl = f"/paths/{p['slug']}/"
        pbody = f"""<section class="wrap page">
  {crumbs(("Paths", "/paths/"), (p["title"], None))}
  <p class="kicker">{icon(p.get("icon", "map"))}<span>Path &middot; {len(p["steps"])} steps &middot; about {path_minutes(p)} min</span></p>
  <h1>{escape(p["title"])}</h1>
  <p class="lede">{escape(p["blurb"])}</p>
  <p><a class="btn btn-primary" href="{first}{sep}path={p['slug']}" data-path-start="{p['slug']}">Start the path {icon("right")}</a></p>
  <ol class="steps">{steps}</ol>
  <div class="path-done" data-path-done hidden>{icon("star")}<p><strong>Path finished.</strong> Nice work. Try another path or take a Quick check on any page.</p></div>
</section>"""
        pdesc = seo_desc(f"{p['blurb']} {len(p['steps'])} short steps, about {path_minutes(p)} minutes, in plain English. Free, no account needed.")
        write(purl, page_shell(seo_title(f"{p['title']}: Guided Path"), pdesc, pbody, purl, og_image="/static/og/paths.jpg", page_title=p["title"]))
        register(purl, p["title"], "Path", path_minutes(p), p["blurb"], " ".join(s["label"] + " " + s["why"] for s in p["steps"]), "map")


def render_timeline(events):
    def yr(e):
        return int(str(e["date"])[:4])
    lo, hi = 1770, 2030
    W, H = 1000, 170
    X = lambda y: 30 + (y - lo) / (hi - lo) * (W - 60)
    ticks = "".join(
        f'<line x1="{X(y):.1f}" x2="{X(y):.1f}" y1="104" y2="118" class="tl-tick"/><text x="{X(y):.1f}" y="152" class="tl-tl">{y}</text>'
        for y in range(1800, 2030, 50))
    dots = ""
    rows_by_kind = {"founding": 30, "event": 52, "amendment": 74, "case": 92}
    for e in events:
        dots += f'<circle cx="{X(yr(e)):.1f}" cy="{rows_by_kind.get(e["kind"], 60)}" r="9" class="tl-dot k-{e["kind"]}"><title>{yr(e)}: {escape(e["title"])}</title></circle>'
    svg = (f'<svg class="tl-scale" viewBox="0 0 {W} {H}" role="img" aria-label="Timeline from 1776 to 2026, drawn to scale">'
           f'<line x1="30" x2="{W - 30}" y1="111" y2="111" class="tl-axis"/>{ticks}{dots}</svg>')
    eras = [("Founding", 1770, 1791), ("A new country", 1792, 1860), ("Civil War and Reconstruction", 1861, 1877),
            ("A growing nation", 1878, 1945), ("Civil rights era", 1946, 1979), ("Modern era", 1980, 2030)]
    kinds = {"founding": "Founding", "amendment": "Amendment", "case": "Court case", "event": "Event"}
    blocks = ""
    for name, a, b in eras:
        evs = [e for e in events if a <= yr(e) <= b]
        if not evs:
            continue
        items = ""
        for e in evs:
            d = str(e["date"])
            when = fmt_date(d) if len(d) == 10 else d
            items += (f'<li class="tl-item k-{e["kind"]}" data-kind="{e["kind"]}"><span class="tl-date">{escape(when)}</span>'
                      f'<span class="tl-body"><span class="pill pill-{e["kind"]}">{kinds.get(e["kind"], "")}</span>'
                      f'<a href="{e["href"]}" class="tl-title">{md(e["title"])}</a><span class="tl-line">{md(e["line"])}</span></span></li>')
        blocks += f'<section class="tl-era"><h2>{escape(name)} <span class="tl-range">{a if a > 1770 else 1776}&ndash;{b if b < 2030 else "today"}</span></h2><ol class="tl-list">{items}</ol></section>'
    filt = "".join(f'<label class="seg"><input type="radio" name="tlk" value="{v}"{" checked" if v == "all" else ""}><span>{l}</span></label>'
                   for v, l in [("all", "All"), ("amendment", "Amendments"), ("case", "Court cases"), ("founding", "Founding")])
    url = "/timeline/"
    body = f"""<section class="wrap page">
  {crumbs(("Timeline", None))}
  <h1>Timeline</h1>
  <p class="lede">250 years of the Constitution: when each part was added and the court cases that shaped what it means.</p>
  <figure class="tl-figure">{svg}<figcaption><span class="key k-founding"></span>Founding <span class="key k-amendment"></span>Amendments <span class="key k-case"></span>Court cases <span class="key k-event"></span>Events &middot; drawn to scale</figcaption></figure>
  <fieldset class="setting tl-filter"><legend>Show</legend><div class="segs">{filt}</div></fieldset>
  {blocks}
</section>"""
    write(url, page_shell("U.S. Constitution Timeline: 1776 to Today | Free Constitution",
                          "A timeline of the U.S. Constitution from 1776 to today: the founding, when all 27 amendments were ratified, and landmark Supreme Court cases.",
                          body, url, og_image="/static/og/timeline.jpg", page_title="Timeline"))
    register(url, "Timeline", "Timeline", 4, "From 1776 to today.", " ".join(e["title"] + " " + e["line"] for e in events), "timeline")


def render_words(gloss):
    by_letter = {}
    for g in sorted(gloss, key=lambda x: x["term"].lower()):
        by_letter.setdefault(g["term"][0].upper(), []).append(g)
    nav = "".join(f'<a href="#letter-{L}">{L}</a>' for L in by_letter)
    blocks = ""
    for L, items in by_letter.items():
        rows = []
        for g in items:
            see = g.get("see")
            link = f'<a href="{see}">See where it matters {icon("right")}</a>' if see and see != "/words/" else ""
            rows.append(f'<div class="word" id="{slugify(g["term"])}"><dt>{escape(g["term"])}</dt><dd><p>{md(g["def"])}</p>{link}</dd></div>')
        dl = "".join(rows)
        blocks += f'<section class="letter" id="letter-{L}"><h2>{L}</h2><dl class="words">{dl}</dl></section>'
    url = "/words/"
    body = f"""<section class="wrap page">
  {crumbs(("Words", None))}
  <h1>Words</h1>
  <p class="lede">Legal words in plain English. On any page, tap an underlined word to see its meaning.</p>
  <nav class="letters" aria-label="Jump to letter">{nav}</nav>
  {blocks}
</section>"""
    terms = [{"@type": "DefinedTerm", "name": g["term"], "description": g["def"], "url": f"{SITE_URL}/words/#{slugify(g['term'])}"} for g in gloss]
    jld = {"@type": "DefinedTermSet", "name": "Constitution glossary", "url": f"{SITE_URL}{url}", "hasDefinedTerm": terms}
    write(url, page_shell("Constitution Glossary: Legal Terms in Plain English",
                          "Plain-English definitions of 60 legal terms in the Constitution: probable cause, due process, equal protection, Miranda warnings, and more.",
                          body, url, og_image="/static/og/words.jpg", page_title="Words", jsonld=jld))
    register(url, "Words", "Glossary", 3, "Legal words in plain English.", "", "words")


def render_memorize(items):
    data = json.dumps(items)
    cards = ""
    for it in items:
        cards += f"""<section class="mem" id="{it['slug']}" data-mem="{it['slug']}">
  <h2>{escape(it['title'])}</h2>
  <p class="hint">{escape(it['why'])} From <a href="{it['source']}">{escape(it['source_label'])}</a>.</p>
  <div class="segs mem-modes" role="tablist" aria-label="Practice mode">
    <button type="button" class="seg-btn on" data-mode="read" role="tab" aria-selected="true">Read</button>
    <button type="button" class="seg-btn" data-mode="letters" role="tab" aria-selected="false">First letters</button>
    <button type="button" class="seg-btn" data-mode="order" role="tab" aria-selected="false">Put in order</button>
  </div>
  <div class="mem-stage" data-stage aria-live="polite"><p>{escape(" ".join(it['chunks']))}</p></div>
</section>"""
    url = "/memorize/"
    body = f"""<section class="wrap page">
  {crumbs(("Know it by heart", None))}
  <h1>Know it by heart</h1>
  <p class="lede">Practice a few lines worth remembering. Read it, try it with only first letters, then put it in order. Nothing is saved.</p>
  {cards}
  <script type="application/json" id="mem-data">{data}</script>
</section>"""
    write(url, page_shell("Memorize the Preamble and First Amendment | Free Constitution",
                          "Memorize the Preamble, the First Amendment, the five freedoms, and the three sentences to say to police, with first-letter and put-in-order practice.",
                          body, url, page_title="Know it by heart"))
    register(url, "Know it by heart", "Practice", 5, "Memorize the Preamble, the five freedoms, and more.", "", "brain")


def render_full_text(amendments, articles):
    pre_f, pre_b = load_md(CONTENT / "preamble.md")
    parts = [f'<section id="preamble"><h2>Preamble</h2><div class="verbatim">{md_to_html(sec(split_h2(pre_b), "Verbatim"), 1)}</div></section>']
    toc = ['<a href="#preamble">Preamble</a>']
    for art in articles:
        n = art["front"]["number"]
        v = sec(split_h2(art["body"]), "Verbatim")
        parts.append(f'<section id="article-{n}"><h2>Article {ROMAN[n]} <a class="small-link" href="/articles/{n}/">plain English</a></h2><div class="verbatim">{md_to_html(v, 1)}</div></section>')
        toc.append(f'<a href="#article-{n}">Art. {ROMAN[n]}</a>')
    for a in amendments:
        n = a["front"]["number"]
        v = sec(split_h2(a["body"]), "Verbatim")
        parts.append(f'<section id="amendment-{n}"><h2>Amendment {n} <a class="small-link" href="/amendments/{n}/">plain English</a></h2><div class="verbatim">{md_to_html(v, 1)}</div></section>')
        toc.append(f'<a href="#amendment-{n}">{n}</a>')
    url = "/full-text/"
    body = f"""<section class="wrap page fulltext">
  {crumbs(("Full text", None))}
  <h1>The whole Constitution</h1>
  <p class="lede">The complete original text on one page, from the National Archives. For the plain-English version, tap "plain English" next to any part.</p>
  <nav class="toc" aria-label="Jump to">{"".join(toc)}</nav>
  {"".join(parts)}
  {accuracy_note("https://www.archives.gov/founding-docs/constitution-transcript")}
</section>"""
    write(url, page_shell("Full Text of the U.S. Constitution and All 27 Amendments",
                          "Read the complete original text of the U.S. Constitution, the Preamble, all seven articles, and all 27 amendments on one page, from the National Archives.",
                          body, url, page_title="Full text"))
    register(url, "The whole Constitution (original text)", "Full text", 45, "Every word of the original on one page.", "", "book")


def render_simple(name, url):
    f, body = load_md(CONTENT / f"{name}.md")
    html = md_to_html(body, 0)
    page = f"""<article class="doc wrap prose-page">
  {crumbs((f["title"], None))}
  <h1>{escape(f["title"])}</h1>
  <p class="lede">{escape(f.get("summary", ""))}</p>
  <div class="prose">{html}</div>
</article>"""
    write(url, page_shell(seo_title(f.get("seo_title") or f["title"]), f.get("seo_description") or f.get("summary", f["title"]), page, url, page_title=f["title"]))
    register(url, f["title"], "Page", minutes_for(html), f.get("summary", ""), plain_text(html), "info")


def render_search_page():
    url = "/search/"
    body = f"""<section class="wrap page">
  {crumbs(("Search", None))}
  <h1>Search</h1>
  <label class="search-field big">{icon("search")}<span class="vh">Search the Constitution</span>
  <input type="search" data-search-input data-search-inline placeholder="Try: phone search, vote, speech at school" autocomplete="off"></label>
  <div class="search-results" data-search-results data-search-inline-results aria-live="polite"></div>
</section>"""
    write(url, page_shell(f"Search | {SITE_NAME}", "Search the Constitution, amendments, situation cards, and legal words.", body, url, page_title="Search", robots="noindex, follow"))


def render_offline():
    url = "/offline/"
    body = f"""<section class="wrap page">
  <h1>You're offline</h1>
  <p class="lede">This page isn't saved on your phone yet. Situation cards you've opened before still work.</p>
  <p><a class="btn btn-primary" href="/situations/">Open situation cards</a></p>
</section>"""
    write(url, page_shell(f"Offline | {SITE_NAME}", "You're offline.", body, url, page_title="Offline", robots="noindex, follow"))


def render_home(amendments, articles, situations, paths, all_ins, events):
    finder = "".join(f'<a class="finder-btn" href="{h}">{icon(i)}<span>{escape(l)}</span></a>' for i, l, h in FINDER)
    rail = "".join(f'<a class="jump" href="{h}"><span class="jump-q">{escape(q)}</span><span class="jump-where">{escape(w)} {icon("right")}</span></a>'
                   for q, h, w in JUMP_POINTS)
    pcards = ""
    for p in paths[:4]:
        pcards += (f'<a class="path-card" href="/paths/{p["slug"]}/" data-path-card="{p["slug"]}"><span class="path-ic">{icon(p.get("icon", "map"))}</span>'
                   f'<span class="path-body"><span class="path-title">{escape(p["title"])}</span><span class="sit-sum">{escape(p["blurb"])}</span>'
                   f'<span class="path-meta">{icon("clock")}{path_minutes(p)} min &middot; {len(p["steps"])} steps<span class="path-prog" data-path-prog></span></span></span>{icon("right", "ic go")}</a>')
    bor = "".join(amend_cell(a["front"]["number"], all_ins[a["front"]["number"]].get("subject", "")) for a in amendments if a["front"]["number"] <= 10)
    arts = "".join(f'<a class="article-row compact" href="/articles/{art["front"]["number"]}/" data-progress-url="/articles/{art["front"]["number"]}/"><span class="num">Art. {ROMAN[art["front"]["number"]]}</span><span class="title">{escape(ARTICLE_NAMES[art["front"]["number"]])}</span>{icon("right", "ic go")}</a>' for art in articles)
    # mini timeline strip
    marks = [e for e in events if e["kind"] in ("founding", "amendment")]
    lo, hi = 1770, 2030
    strip = "".join(f'<span class="strip-dot k-{e["kind"]}" style="left:{(int(str(e["date"])[:4]) - lo) / (hi - lo) * 100:.1f}%"></span>' for e in marks)
    body = f"""<div class="hero-band">
<section class="hero wrap">
  <a href="https://hopeforamericans.net" class="hfa-eyebrow">A Hope for Americans project</a>
  <h1>Know your rights.<br><span class="accent">The Constitution in plain English.</span></h1>
  <p class="lede">The whole U.S. Constitution and all 27 amendments, explained one short page at a time. Free, no ads, no account.</p>
  <h2 class="finder-q" id="finder-q">What's going on?</h2>
  <button type="button" class="hero-search" data-open-search>{icon("search")}<span>Search: phone search, voting, speech at school&hellip;</span></button>
  <div class="finder" aria-labelledby="finder-q">{finder}</div>
  <p class="finder-more"><a href="/situations/">All situation cards {icon("right")}</a></p>
</section>
</div>

<section class="wrap home-sec" id="resume" hidden></section>

<section class="wrap home-sec">
  <a class="doc-line" href="/preamble/"><span class="doc-words">We the People of the United States, in Order to form a more perfect Union&hellip;</span><span class="doc-src">The Preamble, 1787 &middot; Read it in plain English {icon("right")}</span></a>
</section>

<section class="wrap home-sec">
  <h2 class="sec-title">Questions people are asking</h2>
  <div class="jump-rail">{rail}</div>
</section>

<section class="wrap home-sec">
  <h2 class="sec-title">Paths</h2>
  <p class="sec-lede">Short guided routes. Each step is one page.</p>
  <div class="path-grid">{pcards}</div>
  <p><a class="text-link" href="/paths/">All {len(paths)} paths {icon("right")}</a></p>
</section>

<section class="wrap home-sec">
  <h2 class="sec-title">250 years in one line</h2>
  <a class="strip" href="/timeline/" aria-label="Open the timeline"><span class="strip-line"></span>{strip}<span class="strip-l">1776</span><span class="strip-r">Today</span></a>
  <p><a class="text-link" href="/timeline/">Open the timeline {icon("right")}</a></p>
</section>

<section class="wrap home-sec" id="browse">
  <h2 class="sec-title">The Bill of Rights</h2>
  <p class="sec-lede">The first ten amendments, 1791. <a href="/bill-of-rights/">The Bill of Rights explained</a>.</p>
  <div class="amend-grid">{bor}</div>
  <p><a class="text-link" href="/amendments/">All 27 amendments {icon("right")}</a></p>
  <h2 class="sec-title">The original seven articles</h2>
  <div class="article-list">{arts}</div>
  <div class="more-row">
    <a class="mini-card" href="/preamble/">{icon("flag")}<span>The Preamble</span>{icon("right", "ic go")}</a>
    <a class="mini-card" href="/declaration/">{icon("flag")}<span>Declaration of Independence</span>{icon("right", "ic go")}</a>
    <a class="mini-card" href="/memorize/">{icon("brain")}<span>Know it by heart</span>{icon("right", "ic go")}</a>
    <a class="mini-card" href="/words/">{icon("words")}<span>Words, explained</span>{icon("right", "ic go")}</a>
  </div>
</section>"""
    jld = [{"@type": "WebSite", "@id": f"{SITE_URL}/#website", "url": f"{SITE_URL}/", "name": SITE_NAME,
            "alternateName": "freeconstitution.org", "inLanguage": "en-US",
            "description": "The U.S. Constitution and all 27 amendments in plain English, with know-your-rights situation cards.",
            "publisher": {"@id": ORG["@id"]},
            "potentialAction": {"@type": "SearchAction", "target": {"@type": "EntryPoint", "urlTemplate": f"{SITE_URL}/search/?q={{search_term_string}}"},
                                "query-input": "required name=search_term_string"}},
           {"@type": "WebPage", "@id": f"{SITE_URL}/#webpage", "url": f"{SITE_URL}/", "name": "The U.S. Constitution in plain English",
            "isPartOf": {"@id": f"{SITE_URL}/#website"}, "about": {"@type": "Legislation", "name": "Constitution of the United States"},
            "dateModified": TODAY.isoformat()}, ORG]
    write("/", page_shell("U.S. Constitution in Plain English | Know Your Rights",
                          "The U.S. Constitution and all 27 amendments explained in plain English, plus what to say if police stop you, at school, online, and at the polls. Free.",
                          body, "/", jsonld=jld, page_title="Home", body_class="is-home"))


def render_404():
    body = f"""<section class="wrap page">
  <h1>Page not found</h1>
  <p class="lede">That page isn't here. The Constitution still is.</p>
  <p><a class="btn btn-primary" href="/">Go to the front page</a> <button type="button" class="btn btn-quiet" data-open-search>{icon("search")} Search</button></p>
</section>"""
    write("/404.html", page_shell(f"Page not found | {SITE_NAME}", "Page not found.", body, "/404.html", page_title="Not found", robots="noindex, follow"))


# ============================================================
# Support files
# ============================================================
def write_support(amendments, situations, paths, gloss):
    # search index
    idx = []
    for u, p in PAGES.items():
        if p["kind"] == "Index":
            continue
        idx.append({"u": u, "t": p["title"], "k": p["kind"], "s": plain_text(md(p["summary"]))[:200],
                    "x": p["text"].lower()[:4000], "i": p["icon"]})
    for g in gloss:
        idx.append({"u": f"/words/#{slugify(g['term'])}", "t": g["term"], "k": "Word", "s": g["def"], "x": g["def"].lower(), "i": "words"})
    write("/search-index.json", json.dumps(idx, separators=(",", ":")))
    # paths data for the path bar
    pdata = {p["slug"]: {"t": p["title"], "s": [{"h": s["href"].split("#")[0], "l": s["label"]} for s in p["steps"]]} for p in paths}
    write("/paths.json", json.dumps(pdata, separators=(",", ":")))

    # service worker: offline for situation cards and anything you've opened
    core = ["/", "/situations/", "/offline/", f"/static/css/site.css?v={ASSET_V}", f"/static/js/app.js?v={ASSET_V}",
            "/static/fonts/atkinson-hyperlegible-next-latin-400-normal.woff2",
            "/static/fonts/atkinson-hyperlegible-next-latin-700-normal.woff2",
            "/static/favicon.svg"] + [f"/situations/{s['front']['slug']}/" for s in situations]
    write("/sw.js", f"""/* Free Constitution offline support. Caches pages you open on this device only. */
const V = "fc-{ASSET_V}";
const CORE = {json.dumps(core)};
self.addEventListener("install", e => {{
  e.waitUntil(caches.open(V).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
}});
self.addEventListener("activate", e => {{
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim()));
}});
self.addEventListener("fetch", e => {{
  const r = e.request;
  if (r.method !== "GET" || new URL(r.url).origin !== location.origin) return;
  if (r.mode === "navigate") {{
    e.respondWith(fetch(r).then(res => {{ const copy = res.clone(); caches.open(V).then(c => c.put(r, copy)); return res; }})
      .catch(() => caches.match(r).then(m => m || caches.match("/offline/"))));
    return;
  }}
  e.respondWith(caches.match(r).then(m => m || fetch(r).then(res => {{
    if (res.ok) {{ const copy = res.clone(); caches.open(V).then(c => c.put(r, copy)); }}
    return res;
  }})));
}});
""")
    write("/manifest.webmanifest", json.dumps({
        "name": SITE_NAME, "short_name": "Free Const.", "start_url": "/", "display": "standalone",
        "background_color": "#fbf8f0", "theme_color": "#14283f",
        "description": "The U.S. Constitution in plain English, with know-your-rights cards.",
        "icons": [
            {"src": "/static/favicon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any"},
            {"src": "/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"},
            {"src": "/static/mark-512.png", "sizes": "512x512", "type": "image/png"}
        ]}, indent=1))

    bots = ["Googlebot", "Bingbot", "Applebot", "Applebot-Extended", "Google-Extended", "GPTBot", "OAI-SearchBot",
            "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Perplexity-User", "DuckAssistBot"]
    robots = "# Free Constitution welcomes search engines and AI answer engines.\nUser-agent: *\nAllow: /\nDisallow: /search/\nDisallow: /offline/\n\n"
    robots += "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots)
    robots += f"Sitemap: {SITE_URL}/sitemap.xml\n"
    write("/robots.txt", robots)
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in sorted(x for x in WRITTEN if x.endswith("/") and x not in ("/offline/", "/search/")):
        pr = "1.0" if u == "/" else ("0.9" if u.startswith("/situations/") or u in ("/bill-of-rights/", "/amendments/") else "0.7")
        sm.append(f"  <url><loc>{SITE_URL}{u}</loc><lastmod>{TODAY.isoformat()}</lastmod><priority>{pr}</priority></url>")
    sm.append("</urlset>")
    write("/sitemap.xml", "\n".join(sm))

    amend_lines = "\n".join(
        f"- [{ORDINALS[a['front']['number']]} Amendment]({SITE_URL}/amendments/{a['front']['number']}/): "
        f"{PAGES['/amendments/%d/' % a['front']['number']]['summary']}" for a in amendments)
    sit_lines = "\n".join(f"- [{s['front']['title']}]({SITE_URL}/situations/{s['front']['slug']}/): {s['front'].get('summary', '')}" for s in situations)
    paths_lines = "\n".join(f"- [{p['title']}]({SITE_URL}/paths/{p['slug']}/): {p['blurb']}" for p in paths)
    write("/llms.txt", f"""# Free Constitution

> The U.S. Constitution and all 27 amendments in plain English, plus know-your-rights cards for police stops, searches, school, posting online, work, protests, voting, and immigration agents.

freeconstitution.org is free, with no ads, accounts, or tracking. It is published by Hope for Americans, a nonprofit civic-tech project in Flagstaff, Arizona. Every amendment page has: a one-line summary, the plain-English version, the original text (National Archives), a phrase-by-phrase explanation, what it means for you, myths vs. facts, common questions, key Supreme Court cases, and what is still contested.

## How to cite
- Cite the specific page URL. Plain-language text is CC BY 4.0: credit "Free Constitution (freeconstitution.org)".
- Legal claims name the Supreme Court case and year. The site is not legal advice and has not been reviewed by a lawyer.
- Last updated {TODAY.isoformat()}. Full plain-English text of every page: {SITE_URL}/llms-full.txt

## Know your rights (situation cards)
{sit_lines}

## Amendments
- [The Bill of Rights (Amendments 1–10)]({SITE_URL}/bill-of-rights/)
{amend_lines}

## The original Constitution
- [Preamble]({SITE_URL}/preamble/)
{chr(10).join(f"- [Article {ROMAN[n]}: {ARTICLE_NAMES[n]}]({SITE_URL}/articles/{n}/)" for n in range(1, 8))}
- [Declaration of Independence]({SITE_URL}/declaration/)
- [Full original text]({SITE_URL}/full-text/)

## Guided paths
{paths_lines}

## Reference
- [Glossary of legal terms]({SITE_URL}/words/)
- [Timeline, 1776 to today]({SITE_URL}/timeline/)
- [About and how we check accuracy]({SITE_URL}/about/)
- [Sources]({SITE_URL}/sources/)
""")
    # llms-full.txt: the plain-English answer layer of every main page, for AI answer engines
    full = [f"# Free Constitution — full plain-English text\n\nSource: {SITE_URL} · Updated {TODAY.isoformat()} · CC BY 4.0 · Not legal advice; not reviewed by a lawyer.\n"]
    for s_ in situations:
        f = s_["front"]
        full.append(f"\n## {f.get('h1') or f['title']}\nURL: {SITE_URL}/situations/{f['slug']}/\n\n{f.get('summary', '')}\n\nWhat to say:\n"
                    + "\n".join(f"- {t}" for t in f.get("ten_second") or [])
                    + "\n\nDo:\n" + "\n".join(f"- {t}" for t in f.get("do") or [])
                    + "\n\nDon't:\n" + "\n".join(f"- {t}" for t in f.get("dont") or [])
                    + ("\n\nCommon questions:\n" + "\n".join(f"Q: {q['q']}\nA: {q['a']}" for q in f.get("faq") or []) if f.get("faq") else ""))
    full.append(f"\n## The Bill of Rights\nURL: {SITE_URL}/bill-of-rights/\n\n" + "\n".join(f"Q: {q['q']}\nA: {q['a']}" for q in BOR_FAQ))
    for a in amendments:
        n = a["front"]["number"]
        i_ = load_insight(f"amendment-{n}")
        plain = sec(split_h2(a["body"]), "Plain English")
        full.append(f"\n## {ORDINALS[n]} Amendment: {i_.get('subject', '')}\nURL: {SITE_URL}/amendments/{n}/\nRatified: {a['front'].get('ratified', '')}\n\n"
                    f"In one line: {i_.get('one_line', '')}\n\nPlain English: {plain_text(md_to_html(plain))}\n"
                    + ("\nMyths vs. facts:\n" + "\n".join(f"- Myth: {m['myth']} Fact: {m['fact']}" for m in i_.get("myths") or []) if i_.get("myths") else "")
                    + ("\n\nKey cases:\n" + "\n".join(f"- {k['name']} ({k['year']}): {k['held']}" for k in i_.get("key_cases") or []) if i_.get("key_cases") else "")
                    + ("\n\nCommon questions:\n" + "\n".join(f"Q: {q['q']}\nA: {q['a']}" for q in i_.get("faq") or []) if i_.get("faq") else ""))
    for n in range(1, 8):
        i_ = load_insight(f"article-{n}")
        secs = i_.get("sections") or {}
        full.append(f"\n## Article {ROMAN[n]}: {ARTICLE_NAMES[n]}\nURL: {SITE_URL}/articles/{n}/\n\nIn one line: {i_.get('one_line', '')}\n"
                    + ("\nSections:\n" + "\n".join(f"- Section {k}: {v}" for k, v in secs.items()) if secs else "")
                    + ("\n\nCommon questions:\n" + "\n".join(f"Q: {q['q']}\nA: {q['a']}" for q in i_.get("faq") or []) if i_.get("faq") else ""))
    for stem, name, u in (("preamble", "The Preamble", "/preamble/"), ("declaration", "The Declaration of Independence", "/declaration/")):
        i_ = load_insight(stem)
        full.append(f"\n## {name}\nURL: {SITE_URL}{u}\n\nIn one line: {i_.get('one_line', '')}\n"
                    + ("\nCommon questions:\n" + "\n".join(f"Q: {q['q']}\nA: {q['a']}" for q in i_.get("faq") or []) if i_.get("faq") else ""))
    write("/llms-full.txt", "\n".join(full) + "\n")

    # vercel.json (repo root): serve public/, short URLs people type, cache rules
    redirects = [{"source": "/know-your-rights", "destination": "/situations/", "permanent": True},
                 {"source": "/glossary", "destination": "/words/", "permanent": True},
                 {"source": "/constitution", "destination": "/full-text/", "permanent": True},
                 {"source": "/the-bill-of-rights", "destination": "/bill-of-rights/", "permanent": True}]
    for n in range(1, 28):
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10 if n not in (11, 12, 13) else 0, "th")
        for alias in (f"/{n}{suffix}-amendment", f"/amendment-{n}", f"/{ORDINALS[n].lower()}-amendment"):
            redirects.append({"source": alias, "destination": f"/amendments/{n}/", "permanent": True})
    for n in range(1, 8):
        redirects.append({"source": f"/article-{n}", "destination": f"/articles/{n}/", "permanent": True})
    vercel = {"framework": None, "buildCommand": "", "outputDirectory": "public", "trailingSlash": True,
              "redirects": redirects,
              "headers": [{"source": "/sw.js", "headers": [{"key": "Cache-Control", "value": "no-cache"}]},
                          {"source": "/static/fonts/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
                          {"source": "/static/og/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=604800"}]}]}
    (ROOT / "vercel.json").write_text(json.dumps(vercel, indent=2) + "\n", encoding="utf-8")



# ============================================================
# Checks
# ============================================================
def check_links():
    problems = []
    for f in PUBLIC.rglob("*.html"):
        html = f.read_text(encoding="utf-8")
        for href in re.findall(r'href="(/[^"#?]*)', html):
            if href.startswith("/static/") or href in ("/manifest.webmanifest",):
                target = PUBLIC / href.lstrip("/")
                if not target.exists():
                    problems.append(f"{f.relative_to(PUBLIC)} -> {href}")
                continue
            t = PUBLIC / href.lstrip("/")
            if not (t.is_file() or (t / "index.html").exists()):
                problems.append(f"{f.relative_to(PUBLIC)} -> {href}")
    return sorted(set(problems))


# ============================================================
# Build
# ============================================================
def load_collection(folder, sort_key):
    items = []
    for p in sorted((CONTENT / folder).glob("*.md")):
        front, body = load_md(p)
        if front.get("type"):
            items.append({"front": front, "body": body})
    items.sort(key=sort_key)
    return items


def main():
    global TERMS
    # content checks first (phrase quotes must match the original)
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_content.py")], capture_output=True, text=True)
    print(r.stdout.strip().split("\n")[-1])
    if r.returncode != 0:
        print(r.stdout)
        raise SystemExit("Content check failed. Fix the problems above, then build again.")

    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    PUBLIC.mkdir()
    shutil.copytree(STATIC, PUBLIC / "static")
    # Copy root-level assets that browsers expect at the domain root
    for fname in ["favicon-32.png", "apple-touch-icon.png"]:
        src = STATIC / fname
        if src.exists():
            shutil.copy(src, PUBLIC / fname)

    gloss = load_yaml("glossary.yml")
    TERMS = Terms(gloss)
    paths = load_yaml("paths.yml")
    events = sorted(load_yaml("timeline.yml"), key=lambda e: str(e["date"]))
    mem = load_yaml("memorize.yml")

    amendments = load_collection("amendments", lambda x: x["front"]["number"])
    articles = load_collection("articles", lambda x: x["front"]["number"])
    situations = load_collection("situations", lambda x: (x["front"].get("order", 99), x["front"]["title"]))
    for s in situations:
        SITUATIONS[s["front"]["slug"]] = s["front"]
    all_ins = {a["front"]["number"]: load_insight(f"amendment-{a['front']['number']}") for a in amendments}

    nums = [a["front"]["number"] for a in amendments]
    for i, a in enumerate(amendments):
        render_amendment(a, nums[i - 1] if i else None, nums[i + 1] if i < len(nums) - 1 else None, all_ins)
    anums = [a["front"]["number"] for a in articles]
    for i, art in enumerate(articles):
        render_article(art, anums[i - 1] if i else None, anums[i + 1] if i < len(anums) - 1 else None)
    for i, s in enumerate(situations):
        render_situation(s, situations[i - 1] if i else None, situations[i + 1] if i < len(situations) - 1 else None)
    render_preamble()
    render_declaration()
    render_situations_index(situations)
    render_amendments_index(amendments, all_ins)
    render_bill_of_rights(amendments, all_ins)
    render_articles_index(articles)
    render_simple("about", "/about/")
    render_simple("sources", "/sources/")
    render_timeline(events)
    render_words(gloss)
    render_memorize(mem)
    render_full_text(amendments, articles)
    render_paths(paths)          # after the pages it points to, so minutes are known
    render_home(amendments, articles, situations, paths, all_ins, events)
    render_search_page()
    render_offline()
    render_404()
    write_support(amendments, situations, paths, gloss)

    # path steps and finder must point at real pages
    bad = check_links()
    if bad:
        print("BROKEN INTERNAL LINKS:")
        for b in bad[:60]:
            print("  -", b)
        raise SystemExit(1)
    print(f"Built {len(WRITTEN)} pages to {PUBLIC}. All internal links verified.")


if __name__ == "__main__":
    main()
