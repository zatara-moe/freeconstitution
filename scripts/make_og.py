#!/usr/bin/env python3
"""Make share images (1200x630) for every main page into static/og/.
Run after content changes: python3 scripts/make_og.py
Needs: pip install pillow pyyaml fonttools brotli
"""
import io
import re
import sys
from pathlib import Path

import yaml
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
C = ROOT / "content"
OUT = ROOT / "static" / "og"
FONTS = ROOT / "static" / "fonts"
OUT.mkdir(parents=True, exist_ok=True)

ORD = {1: "1st", 2: "2nd", 3: "3rd"}
def nth(n): return ORD.get(n if n < 20 else n % 10, f"{n}th") if not 11 <= n <= 13 else f"{n}th"
ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII"}

def ttf(name, size):
    data = TTFont(str(FONTS / name))
    data.flavor = None
    buf = io.BytesIO(); data.save(buf); buf.seek(0)
    return ImageFont.truetype(buf, size)

def F(kind, size):
    return ttf({"bold": "atkinson-hyperlegible-next-latin-700-normal.woff2",
                "reg": "atkinson-hyperlegible-next-latin-400-normal.woff2",
                "serif": "source-serif-4-latin-600-normal.woff2"}[kind], size)

PAPER, NAVY, INK, SOFT, RED, GOLD, PAPER2 = "#fbf8f0", "#14283f", "#17191f", "#3c424d", "#9b2c24", "#7a5a12", "#f4eee0"

def wrap(d, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def card(path, kicker, title, line, accent=NAVY):
    im = Image.new("RGB", (1200, 630), PAPER)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 1200, 88], fill=NAVY)
    d.rounded_rectangle([48, 20, 96, 68], radius=10, fill="#f7f1e3")
    d.text((60, 14), "f", font=F("serif", 44), fill="#1f1b16")
    d.ellipse([84, 54, 92, 62], fill="#b85436")
    d.text((116, 26), "Free Constitution", font=F("bold", 34), fill=PAPER)
    d.rectangle([0, 88, 10, 560], fill=RED)
    d.text((64, 128), kicker.upper(), font=F("bold", 26), fill=GOLD)
    size = 76
    while True:
        tf = F("bold", size)
        tl = wrap(d, title, tf, 1070)
        if len(tl) <= 2 or size <= 52: break
        size -= 6
    y = 172
    for l in tl[:3]:
        d.text((64, y), l, font=tf, fill=INK); y += int(size * 1.15)
    y += 18
    lf = F("reg", 34)
    for l in wrap(d, line, lf, 1060)[:3]:
        d.text((64, y), l, font=lf, fill=SOFT); y += 46
    d.rectangle([0, 560, 1200, 630], fill=PAPER2)
    d.text((64, 578), "freeconstitution.org  ·  Plain English  ·  Free, no ads", font=F("reg", 28), fill=SOFT)
    im.save(OUT / path, quality=86, optimize=True)

def load_md(p):
    m = re.match(r"^---\n(.*?)\n---\n", p.read_text(encoding="utf-8"), re.S)
    return yaml.safe_load(m.group(1)) if m else {}

def ins(stem):
    p = C / "insights" / f"{stem}.yml"
    return yaml.safe_load(p.read_text()) if p.exists() else {}

def short(s, n=150):
    s = re.sub(r"\*", "", s or "")
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + "…"

n_made = 0
for n in range(1, 28):
    i = ins(f"amendment-{n}")
    card(f"amendment-{n}.jpg", f"Amendment {n} of 27" + (" · Bill of Rights" if n <= 10 else ""),
         f"{nth(n)} Amendment: {i.get('subject', '')}", short(i.get("one_line"))); n_made += 1
for n in range(1, 8):
    i = ins(f"article-{n}")
    card(f"article-{n}.jpg", f"Article {ROMAN[n]} of VII", f"Article {ROMAN[n]}: {i.get('subject', '')}", short(i.get("one_line"))); n_made += 1
for p in sorted((C / "situations").glob("*.md")):
    f = load_md(p)
    card(f"situation-{f['slug']}.jpg", "Know your rights", f.get("h1") or f["title"], short(f.get("summary")), RED); n_made += 1
card("home.jpg", "Know your rights", "The U.S. Constitution in plain English", "Every amendment explained simply, plus what to say when police stop you, at school, online, and at the polls."); n_made += 1
card("bill-of-rights.jpg", "The first ten amendments · 1791", "The Bill of Rights in plain English", "Speech, religion, guns, searches, silence, a fair trial, and more. Each one explained simply."); n_made += 1
card("situation-default.jpg", "Know your rights", "What to say when it matters", "Pocket cards for police stops, searches, school, work, protests, voting, and more."); n_made += 1
card("amendment-default.jpg", "The Constitution", "Every amendment, explained simply", "The original words, a plain-English version, and what each one means for you."); n_made += 1
card("preamble.jpg", "The Constitution · 1787", "The Preamble, explained", short(ins("preamble").get("one_line"))); n_made += 1
card("declaration.jpg", "Founding document · 1776", "The Declaration of Independence in plain English", short(ins("declaration").get("one_line"))); n_made += 1
card("paths.jpg", "Guided paths", "Learn your rights, one short step at a time", "Your rights in 10 minutes, getting pulled over, rights at school, first-time voter, and more."); n_made += 1
card("timeline.jpg", "1776 to today", "The Constitution timeline", "When each amendment was added and the court cases that shaped what it means."); n_made += 1
card("words.jpg", "Glossary", "Legal words in plain English", "Probable cause, due process, equal protection, and 57 more terms, explained simply."); n_made += 1
print(f"Made {n_made} share images in {OUT}")
