#!/usr/bin/env python3
"""
freeconstitution.org, build script
Generates the complete static site from markdown content.
Outputs to /public/

Usage: python3 scripts/build.py
"""

import re
import shutil
from datetime import date
from html import escape
from pathlib import Path

import yaml

# ============================================================
# Paths
# ============================================================
ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
PUBLIC = ROOT / "public"

SITE_URL = "https://freeconstitution.org"
SITE_NAME = "Free Constitution"
TAGLINE = "Read your Constitution. Know your rights."

# ============================================================
# Jump points, the homepage rail
# ============================================================
# Each question links straight to the section that answers it.
# href anchors are validated against generated pages at the end
# of the build, so a renamed heading fails loudly, not silently.
JUMP_POINTS = [
    {
        "q": "Can police search my phone?",
        "href": "/amendments/4/#what-this-means-for-you",
        "where": "Fourth Amendment",
    },
    {
        "q": "Do I have to answer police questions?",
        "href": "/situations/being-questioned-by-police/",
        "where": "Situation card",
    },
    {
        "q": "What are my rights at a protest?",
        "href": "/situations/at-a-protest/",
        "where": "Situation card",
    },
    {
        "q": "Who is a citizen by birth?",
        "href": "/amendments/14/#what-this-means-for-you",
        "where": "Fourteenth Amendment",
    },
    {
        "q": "Do police need a warrant to enter my home?",
        "href": "/situations/searched-by-police/",
        "where": "Situation card",
    },
    {
        "q": "Can I be turned away from voting?",
        "href": "/situations/turned-away-from-voting/",
        "where": "Situation card",
    },
    {
        "q": "Can the government take my property?",
        "href": "/amendments/5/#what-this-means-for-you",
        "where": "Fifth Amendment",
    },
    {
        "q": "Can the government limit what guns I own?",
        "href": "/amendments/2/#what-this-means-for-you",
        "where": "Second Amendment",
    },
]

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

# ============================================================
# Markdown, small converter for the subset this content uses
# ============================================================

def slugify(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


def inline_md(text):
    """Inline markdown on an already HTML-escaped string."""
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2">\1</a>',
        text,
    )
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return text


def md_to_html(md):
    """Convert the markdown subset used in /content to HTML.
    Headings get id anchors so jump points can deep link.
    Returns (html, anchors) where anchors is the set of ids created."""
    lines = md.split("\n")
    out = []
    anchors = set()
    para = []
    in_list = False
    in_quote = False

    def close_para():
        if para:
            out.append("<p>" + inline_md(escape("\n".join(para)).replace("\n", " ")) + "</p>")
            para.clear()

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    def close_quote():
        nonlocal in_quote
        if in_quote:
            out.append("</blockquote>")
            in_quote = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("### "):
            close_para(); close_list(); close_quote()
            text = stripped[4:]
            anchor = slugify(text)
            anchors.add(anchor)
            out.append(f'<h3 id="{anchor}">{inline_md(escape(text))}</h3>')
        elif stripped.startswith("## "):
            close_para(); close_list(); close_quote()
            text = stripped[3:]
            anchor = slugify(text)
            anchors.add(anchor)
            out.append(f'<h2 id="{anchor}">{inline_md(escape(text))}</h2>')
        elif stripped.startswith("> "):
            close_para(); close_list()
            if not in_quote:
                out.append("<blockquote>")
                in_quote = True
            out.append("<p>" + inline_md(escape(stripped[2:])) + "</p>")
        elif stripped.startswith("- "):
            close_para(); close_quote()
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append("<li>" + inline_md(escape(stripped[2:])) + "</li>")
        elif stripped == "---":
            close_para(); close_list(); close_quote()
            out.append("<hr>")
        elif stripped == "":
            close_para(); close_list(); close_quote()
        else:
            close_list(); close_quote()
            para.append(stripped)

    close_para(); close_list(); close_quote()
    return "\n".join(out), anchors


def load_md(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.DOTALL)
    if not m:
        return {}, raw
    front = yaml.safe_load(m.group(1)) or {}
    return front, m.group(2)


# ============================================================
# Shared chrome
# ============================================================

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500&'
    'family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap" rel="stylesheet">'
)


MOBILE_NAV = """<nav class="mobile-nav" aria-label="Quick navigation">
  <div class="mobile-nav-row">
    <a href="/#rights-now">
      <svg viewBox="0 0 24 24"><path d="M12 22s-8-4.5-8-11V5l8-3 8 3v6c0 6.5-8 11-8 11z"/></svg>
      Rights
    </a>
    <a href="/situations/">
      <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
      Situations
    </a>
    <a href="/#amendments">
      <svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
      Amendments
    </a>
    <a href="/about/">
      <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
      About
    </a>
  </div>
</nav>"""

BACK_TO_TOP = """<button class="back-to-top" aria-label="Back to top">
  <svg viewBox="0 0 24 24"><polyline points="18 15 12 9 6 15"/></svg>
</button>"""


def page_shell(title, description, body, canonical, extra_head=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{SITE_URL}{canonical}">
<link rel="icon" href="/static/favicon.svg" type="image/svg+xml">
{FONTS}
<link rel="stylesheet" href="/static/css/site.css">
{extra_head}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-row">
    <a class="wordmark" href="/">Free<span> </span>Constitution</a>
    <nav class="site-nav" aria-label="Main">
      <a href="/#rights-now">Your rights</a>
      <a href="/situations/">Situations</a>
      <a href="/#amendments">Amendments</a>
      <a href="/#articles">Articles</a>
      <a href="/about/">About</a>
    </nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="foot-tag">The whole document, open to anyone.</div>
  <p class="hfa-madein">Made with <span class="hfa-heart" aria-hidden="true">&hearts;</span> in Flagstaff</p>
  <div class="hfa-rule"></div>
  <div class="hfa-mark">A <a href="https://hopeforamericans.net">Hope for Americans</a> tool</div>
  <div class="hfa-vision">free to use, the way the web used to be</div>
</footer>
{MOBILE_NAV}
{BACK_TO_TOP}
<script src="/static/js/prefs.js" defer></script>
</body>
</html>"""


def reading_controls():
    return """<div class="reading-controls" data-prefs hidden>
  <span class="rc-label">Text size</span>
  <button type="button" data-size-down aria-label="Smaller text">A&minus;</button>
  <button type="button" data-size-up aria-label="Larger text">A+</button>
  <button type="button" data-theme-toggle aria-pressed="false">Dark page</button>
</div>"""


def not_legal_advice():
    return ('<p class="legal-note">This page explains the law in plain language. '
            'It is not legal advice for your specific situation. '
            'If you need legal help, contact a lawyer or your state\'s ACLU affiliate.</p>')


def section_chips(anchors_in_order):
    labels = {
        "verbatim": "Verbatim",
        "plain-english": "Plain English",
        "what-this-means-for-you": "What this means for you",
        "about": "About",
    }
    chips = [f'<a href="#{a}">{labels[a]}</a>' for a in anchors_in_order if a in labels]
    if not chips:
        return ""
    return '<nav class="section-chips" aria-label="On this page">' + "".join(chips) + "</nav>"


def sticky_section_bar(short_title, anchors_in_order):
    """A fixed bar that appears when you scroll past the section chips.
    Shows which section you are in and lets you jump to any other."""
    labels = {
        "verbatim": "Verbatim",
        "plain-english": "Plain English",
        "what-this-means-for-you": "For you",
        "about": "About",
        "what-you-can-say": "Say this",
        "the-law-you-are-citing": "The law",
        "quick-limits": "Limits",
        "if-you-are-arrested": "Arrested",
    }
    chips = []
    for a in anchors_in_order:
        if a in labels:
            chips.append(f'<a href="#{a}" data-section="{a}">{labels[a]}</a>')
    if not chips:
        return ""
    return (
        '<nav class="sticky-sections" aria-label="Section navigation">'
        f'<span class="sticky-title">{escape(short_title)}</span>'
        + "".join(chips) +
        '</nav>'
    )


def fmt_date(d):
    if not d:
        return ""
    if isinstance(d, str):
        d = date.fromisoformat(d)
    return d.strftime("%B %-d, %Y")


def write(path, html):
    full = PUBLIC / path.lstrip("/")
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(html, encoding="utf-8")


# ============================================================
# Load all content
# ============================================================

def load_collection(folder, sort_key):
    items = []
    for p in sorted((CONTENT / folder).glob("*.md")):
        front, body = load_md(p)
        if not front.get("type"):
            continue
        html, anchors = md_to_html(body)
        items.append({"front": front, "html": html, "anchors": anchors})
    items.sort(key=sort_key)
    return items


# ============================================================
# Page builders
# ============================================================

PAGE_ANCHORS = {}  # url -> set of anchors, for jump point validation


def render_amendment(a, prev_a, next_a):
    f = a["front"]
    n = f["number"]
    ordinal = ORDINALS[n]
    part = "Bill of Rights" if f.get("part_of") == "bill-of-rights" else "Amendment"
    eyebrow_bits = [f"Amendment {n} of 27"]
    if f.get("part_of") == "bill-of-rights":
        eyebrow_bits.append("Bill of Rights")
    ratified = fmt_date(f.get("ratified"))

    contested = f.get("contested") or []
    contested_html = ""
    if contested:
        lis = "".join(f"<li>{escape(c)}</li>" for c in contested)
        contested_html = (
            '<aside class="contested"><h2 id="actively-contested">Actively contested</h2>'
            "<p>Courts are still arguing about parts of this amendment. Current open questions include:</p>"
            f"<ul>{lis}</ul></aside>"
        )

    related = f.get("related_situations") or []
    related_html = ""
    if related:
        links = "".join(
            f'<a class="related-card" href="/situations/{slug}/">{escape(SITUATION_TITLES.get(slug, slug))}</a>'
            for slug in related
        )
        related_html = f'<section class="related"><h2>If this is happening to you</h2><div class="related-row">{links}</div></section>'

    nav_bits = []
    if prev_a:
        pn = prev_a["front"]["number"]
        nav_bits.append(f'<a class="pager prev" href="/amendments/{pn}/"><span>Previous</span>{ORDINALS[pn]} Amendment</a>')
    else:
        nav_bits.append("<span></span>")
    if next_a:
        nn = next_a["front"]["number"]
        nav_bits.append(f'<a class="pager next" href="/amendments/{nn}/"><span>Next</span>{ORDINALS[nn]} Amendment</a>')
    pager = '<nav class="pager-row" aria-label="Amendments">' + "".join(nav_bits) + "</nav>"

    ordered = [x for x in ["verbatim", "plain-english", "what-this-means-for-you", "about"] if x in a["anchors"]]

    sticky = sticky_section_bar(f"{ORDINALS[n]} Amend.", ordered)
    body = f"""{sticky}<article class="doc wrap">
  <p class="breadcrumb"><a href="/">Home</a> / <a href="/#amendments">Amendments</a></p>
  <p class="eyebrow">{" &middot; ".join(eyebrow_bits)}{f' &middot; <span class="ratified">ratified {ratified}</span>' if ratified else ""}</p>
  <h1>{escape(f["title"])}</h1>
  {section_chips(ordered)}
  {reading_controls()}
  <div class="doc-body" data-reading>
  {a["html"]}
  </div>
  {contested_html}
  {related_html}
  {not_legal_advice()}
  {pager}
</article>"""
    url = f"/amendments/{n}/"
    PAGE_ANCHORS[url] = a["anchors"]
    write(f"{url}index.html", page_shell(
        f"{f['title']} | {SITE_NAME}",
        f"The {ordinal} Amendment, verbatim and in plain English, with what it means for you.",
        body, url))
    return url


def render_article(art, prev_a, next_a):
    f = art["front"]
    n = f["number"]
    raw_title = f["title"]
    if " — " in raw_title:
        _, name = raw_title.split(" — ", 1)
    else:
        name = raw_title
    ratified = fmt_date(f.get("ratified"))

    nav_bits = []
    if prev_a:
        pn = prev_a["front"]["number"]
        nav_bits.append(f'<a class="pager prev" href="/articles/{pn}/"><span>Previous</span>Article {ROMAN[pn]}</a>')
    else:
        nav_bits.append("<span></span>")
    if next_a:
        nn = next_a["front"]["number"]
        nav_bits.append(f'<a class="pager next" href="/articles/{nn}/"><span>Next</span>Article {ROMAN[nn]}</a>')
    pager = '<nav class="pager-row" aria-label="Articles">' + "".join(nav_bits) + "</nav>"

    ordered = [x for x in ["verbatim", "plain-english", "what-this-means-for-you", "about"] if x in art["anchors"]]

    sticky = sticky_section_bar(f"Art. {ROMAN[n]}", ordered)
    body = f"""{sticky}<article class="doc wrap">
  <p class="breadcrumb"><a href="/">Home</a> / <a href="/#articles">Articles</a></p>
  <p class="eyebrow">Article {ROMAN[n]} of VII{f' &middot; <span class="ratified">ratified {ratified}</span>' if ratified else ""}</p>
  <h1>{escape(name)}</h1>
  {section_chips(ordered)}
  {reading_controls()}
  <div class="doc-body" data-reading>
  {art["html"]}
  </div>
  {not_legal_advice()}
  {pager}
</article>"""
    url = f"/articles/{n}/"
    PAGE_ANCHORS[url] = art["anchors"]
    write(f"{url}index.html", page_shell(
        f"Article {ROMAN[n]}, {name} | {SITE_NAME}",
        f"Article {ROMAN[n]} of the Constitution, verbatim and in plain English.",
        body, url))
    return url


def render_situation(s):
    f = s["front"]
    slug = f["slug"]
    minutes = max(1, round((f.get("reading_time_seconds") or 60) / 60))
    related = f.get("related_amendments") or []
    related_html = ""
    if related:
        links = "".join(
            f'<a class="related-card" href="/amendments/{n}/">{ORDINALS[n]} Amendment</a>'
            for n in related
        )
        related_html = f'<section class="related"><h2>The law behind this card</h2><div class="related-row">{links}</div></section>'

    sit_ordered = [x for x in ["what-you-can-say", "the-law-you-are-citing", "quick-limits", "if-you-are-arrested"] if x in s["anchors"]]
    sticky = sticky_section_bar(f["title"], sit_ordered)

    body = f"""{sticky}<article class="doc wrap situation">
  <p class="breadcrumb"><a href="/">Home</a> / <a href="/situations/">Situations</a></p>
  <p class="eyebrow">Situation card &middot; {minutes} minute read</p>
  <h1>{escape(f["title"])}</h1>
  <p class="lede">{escape(f.get("summary", ""))}</p>
  {reading_controls()}
  <div class="doc-body" data-reading>
  {s["html"]}
  </div>
  {related_html}
  {not_legal_advice()}
</article>"""
    url = f"/situations/{slug}/"
    PAGE_ANCHORS[url] = s["anchors"]
    write(f"{url}index.html", page_shell(
        f"{f['title']} | {SITE_NAME}",
        f.get("summary", ""), body, url))
    return url


def render_situations_index(situations):
    cards = ""
    for s in situations:
        f = s["front"]
        cards += f"""<a class="sit-card" href="/situations/{f["slug"]}/">
  <h2>{escape(f["title"])}</h2>
  <p>{escape(f.get("summary", ""))}</p>
  <span class="sit-go">Read the card</span>
</a>"""
    body = f"""<section class="wrap">
  <p class="breadcrumb"><a href="/">Home</a> / Situations</p>
  <h1>Situations</h1>
  <p class="lede">Pocket cards for moments when knowing your rights matters. Each one tells you what you can say, the law you are citing, and where the limits are.</p>
  <div class="sit-grid">{cards}</div>
  {not_legal_advice()}
</section>"""
    url = "/situations/"
    write(f"{url}index.html", page_shell(
        f"Situations | {SITE_NAME}",
        "Pocket cards for moments when knowing your rights matters.",
        body, url))
    return url


def render_simple(front, html, anchors, url, kind_eyebrow=None, note=False):
    f = front
    eyebrow = f'<p class="eyebrow">{kind_eyebrow}</p>' if kind_eyebrow else ""
    body = f"""<article class="doc wrap">
  <p class="breadcrumb"><a href="/">Home</a></p>
  {eyebrow}
  <h1>{escape(f["title"])}</h1>
  {reading_controls()}
  <div class="doc-body" data-reading>
  {html}
  </div>
  {not_legal_advice() if note else ""}
</article>"""
    PAGE_ANCHORS[url] = anchors
    write(f"{url}index.html", page_shell(
        f"{f['title']} | {SITE_NAME}",
        f.get("summary", f["title"]), body, url))
    return url


def render_home(amendments, articles, situations):
    # Jump rail
    rail = ""
    for jp in JUMP_POINTS:
        rail += f"""<a class="jump" href="{jp["href"]}">
  <span class="jump-q">{escape(jp["q"])}</span>
  <span class="jump-where">{escape(jp["where"])} &rarr;</span>
</a>"""

    # Situations
    sits = ""
    for s in situations:
        f = s["front"]
        sits += f"""<a class="sit-card" href="/situations/{f["slug"]}/">
  <h3>{escape(f["title"])}</h3>
  <p>{escape(f.get("summary", ""))}</p>
  <span class="sit-go">Read the card</span>
</a>"""

    # Amendments grid, Bill of Rights first
    bor = ""
    rest = ""
    for a in amendments:
        n = a["front"]["number"]
        cell = f"""<a class="amend-cell" href="/amendments/{n}/">
  <span class="num">{n}</span>
  <span class="title">{ORDINALS[n]}</span>
</a>"""
        if n <= 10:
            bor += cell
        else:
            rest += cell

    # Articles
    arts = ""
    for art in articles:
        n = art["front"]["number"]
        raw_title = art["front"]["title"]
        name = raw_title.split(" — ", 1)[1] if " — " in raw_title else raw_title
        arts += f"""<a class="article-row" href="/articles/{n}/">
  <span class="num">Article {ROMAN[n]}</span>
  <span class="title">{escape(name)}</span>
</a>"""

    body = f"""<section class="hero wrap">
  <a href="https://hopeforamericans.net" class="hfa-eyebrow">
    <span class="hfa-eyebrow-mark" aria-hidden="true"><svg viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="9" stroke-linecap="round"><path d="M40 34Q40 24 50 24Q60 24 60 34L60 78"/></svg></span>
    <span>A Hope for Americans project</span>
  </a>
  <h1>The Constitution<span class="dot">.</span></h1>
  <p class="lede">{TAGLINE}</p>
  <p class="sublede">The full text. A plain-English version. Short cards for situations where it matters. Free. No accounts. No ads.</p>
</section>

<section id="rights-now" class="wrap rail-section">
  <h2>Your rights, asked a lot right now</h2>
  <p class="section-lede">Questions people are searching this year. Each one jumps to the exact section that answers it.</p>
  <div class="jump-rail">{rail}</div>
</section>

<section id="situations" class="wrap">
  <h2>Situations</h2>
  <p class="section-lede">Pocket cards for moments when knowing your rights matters.</p>
  <div class="sit-grid">{sits}</div>
</section>

<section id="amendments" class="wrap">
  <h2>Amendments</h2>
  <p class="section-lede">The 27 changes ratified since 1791. The first ten are the Bill of Rights.</p>
  <h3 class="grid-label">Bill of Rights, 1791</h3>
  <div class="amend-grid">{bor}</div>
  <h3 class="grid-label">Later amendments, 1795 to 1992</h3>
  <div class="amend-grid">{rest}</div>
</section>

<section id="articles" class="wrap">
  <h2>Articles</h2>
  <p class="section-lede">The seven articles of the original Constitution, ratified 1788. Start with the <a href="/preamble/">Preamble</a>.</p>
  <div class="article-list">{arts}</div>
</section>

<section id="declaration" class="wrap declaration-block">
  <h2>The Declaration of Independence</h2>
  <p class="section-lede">Not part of the Constitution. The founding statement the Constitution was later written to put into practice.</p>
  <a class="cta" href="/declaration/">Read the Declaration</a>
</section>"""
    write("/index.html", page_shell(
        f"{SITE_NAME}, {TAGLINE}",
        "A free, ad-free, account-free reference for the United States Constitution. Verbatim text plus plain-English explanations.",
        body, "/"))


def render_404():
    body = """<section class="wrap doc">
  <h1>Page not found</h1>
  <p class="lede">That page is not here. The Constitution still is.</p>
  <p><a class="cta" href="/">Back to the front page</a></p>
</section>"""
    write("/404.html", page_shell(f"Page not found | {SITE_NAME}", "Page not found.", body, "/404.html"))


# ============================================================
# Build
# ============================================================

def main():
    global SITUATION_TITLES

    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    PUBLIC.mkdir()
    shutil.copytree(STATIC, PUBLIC / "static")

    amendments = load_collection("amendments", lambda x: x["front"]["number"])
    articles = load_collection("articles", lambda x: x["front"]["number"])
    situations = load_collection("situations", lambda x: x["front"]["title"])

    SITUATION_TITLES = {s["front"]["slug"]: s["front"]["title"] for s in situations}

    urls = ["/"]

    for i, a in enumerate(amendments):
        prev_a = amendments[i - 1] if i > 0 else None
        next_a = amendments[i + 1] if i < len(amendments) - 1 else None
        urls.append(render_amendment(a, prev_a, next_a))

    for i, art in enumerate(articles):
        prev_a = articles[i - 1] if i > 0 else None
        next_a = articles[i + 1] if i < len(articles) - 1 else None
        urls.append(render_article(art, prev_a, next_a))

    for s in situations:
        urls.append(render_situation(s))
    urls.append(render_situations_index(situations))

    # Standalone documents
    pre_front, pre_body = load_md(CONTENT / "preamble.md")
    h, anc = md_to_html(pre_body)
    urls.append(render_simple(pre_front, h, anc, "/preamble/", "The Constitution &middot; ratified September 17, 1787"))

    dec_front, dec_body = load_md(CONTENT / "declaration.md")
    h, anc = md_to_html(dec_body)
    urls.append(render_simple(dec_front, h, anc, "/declaration/", "Founding document &middot; adopted July 4, 1776"))

    about_front, about_body = load_md(CONTENT / "about.md")
    h, anc = md_to_html(about_body)
    urls.append(render_simple(about_front, h, anc, "/about/"))

    src_front, src_body = load_md(CONTENT / "sources.md")
    h, anc = md_to_html(src_body)
    urls.append(render_simple(src_front, h, anc, "/sources/"))

    render_home(amendments, articles, situations)
    render_404()

    # robots, sitemap, llms.txt
    write("/robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in sorted(set(urls)):
        sm.append(f"  <url><loc>{SITE_URL}{u}</loc></url>")
    sm.append("</urlset>")
    write("/sitemap.xml", "\n".join(sm))
    write("/llms.txt", (
        f"# {SITE_NAME}\n\n{TAGLINE}\n\n"
        "A free, ad-free, account-free reference for the United States Constitution. "
        "Verbatim text from the National Archives plus a plain-English layer.\n\n"
        "Not legal advice.\n"
    ))

    # Validate jump points
    problems = []
    for jp in JUMP_POINTS:
        href = jp["href"]
        if "#" in href:
            page, anchor = href.split("#")
            if page not in PAGE_ANCHORS:
                problems.append(f"missing page: {page}")
            elif anchor not in PAGE_ANCHORS[page]:
                problems.append(f"missing anchor #{anchor} on {page}")
        else:
            if not (PUBLIC / href.lstrip("/") / "index.html").exists():
                problems.append(f"missing page: {href}")
    if problems:
        print("JUMP POINT PROBLEMS:")
        for p in problems:
            print("  -", p)
        raise SystemExit(1)

    print(f"Built {len(urls) + 2} pages to {PUBLIC}")
    print("All jump points verified.")


if __name__ == "__main__":
    main()
