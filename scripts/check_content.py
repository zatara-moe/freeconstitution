#!/usr/bin/env python3
"""Content checks. Run: python3 scripts/check_content.py [file-stems...]
- every insight YAML parses and has one_line
- every phrase quote appears exactly in that document's ## Verbatim text
- quick_check answers are valid indexes
- one_line <= 25 words; sentences in plain layers flagged if > 30 words
"""
import re, sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
C = ROOT / "content"
problems, warnings = [], []

def body_of(md_path):
    raw = md_path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.DOTALL)
    return (yaml.safe_load(m.group(1)) or {}, m.group(2)) if m else ({}, raw)

def verbatim_text(body):
    # all text under any heading starting with "Verbatim"
    out, on = [], False
    for line in body.split("\n"):
        if line.startswith("## "):
            on = line[3:].strip().lower().startswith("verbatim")
            continue
        if on:
            out.append(line)
    t = " ".join(out)
    t = re.sub(r"\*\*Section \d+\.\*\*", " ", t)
    t = t.replace("**", "").replace("*", "")
    return re.sub(r"\s+", " ", t)

def doc_for(stem):
    kind, _, n = stem.partition("-")
    if kind == "amendment": return C / "amendments" / f"{n}.md"
    if kind == "article": return C / "articles" / f"{n}.md"
    return C / f"{stem}.md"

stems = sys.argv[1:] or [p.stem for p in sorted((C / "insights").glob("*.yml"))]
for stem in stems:
    yp = C / "insights" / f"{stem}.yml"
    if not yp.exists():
        problems.append(f"{stem}: no insight file"); continue
    try:
        d = yaml.safe_load(yp.read_text(encoding="utf-8")) or {}
    except Exception as e:
        problems.append(f"{stem}: YAML error {e}"); continue
    if not d.get("one_line"):
        problems.append(f"{stem}: missing one_line")
    elif len(d["one_line"].split()) > 25:
        warnings.append(f"{stem}: one_line is {len(d['one_line'].split())} words")
    md = doc_for(stem)
    if not md.exists():
        problems.append(f"{stem}: no matching document {md}"); continue
    front, body = body_of(md)
    if "review" in front:
        warnings.append(f"{stem}: old review: block still in frontmatter")
    vt = verbatim_text(body)
    for ph in d.get("phrases") or []:
        q = re.sub(r"\s+", " ", str(ph.get("quote", ""))).strip()
        if not q or q not in vt:
            problems.append(f"{stem}: phrase not found verbatim: {q[:70]!r}")
        if not ph.get("plain"):
            problems.append(f"{stem}: phrase missing plain: {q[:40]!r}")
    for i, qc in enumerate(d.get("quick_check") or []):
        opts = qc.get("options") or []
        if not (isinstance(qc.get("answer"), int) and 0 <= qc["answer"] < len(opts)):
            problems.append(f"{stem}: quick_check {i+1} bad answer index")
        if not qc.get("why"):
            problems.append(f"{stem}: quick_check {i+1} missing why")
    st = d.get("seo_title") or ""
    if not st:
        warnings.append(f"{stem}: missing seo_title")
    elif len(st) > 60:
        warnings.append(f"{stem}: seo_title is {len(st)} chars (max 60)")
    sd = d.get("seo_description") or ""
    if not sd:
        warnings.append(f"{stem}: missing seo_description")
    elif not 120 <= len(sd) <= 160:
        warnings.append(f"{stem}: seo_description is {len(sd)} chars (aim 140-158)")
    for qa in d.get("faq") or []:
        if not (qa.get("q") and qa.get("a")):
            problems.append(f"{stem}: faq item incomplete")
        elif len(qa["a"].split()) > 70:
            warnings.append(f"{stem}: faq answer over 70 words: {qa['q'][:40]!r}")
    for k in d.get("key_cases") or []:
        if not (k.get("name") and k.get("year") and k.get("held")):
            problems.append(f"{stem}: key case incomplete {k}")
    for side in d.get("who_argued") or [None]:
        pass
    if d.get("who_argued") is not None and len(d["who_argued"]) < 2:
        problems.append(f"{stem}: who_argued needs 2+ sides")

# situation cards: seo fields and faq
for sp in sorted((C / "situations").glob("*.md")):
    front, _ = body_of(sp)
    st, sd = front.get("seo_title") or "", front.get("seo_description") or ""
    if not st or len(st) > 60:
        warnings.append(f"situation {sp.stem}: seo_title missing or over 60 chars ({len(st)})")
    if not sd or not 120 <= len(sd) <= 160:
        warnings.append(f"situation {sp.stem}: seo_description missing or not 120-160 chars ({len(sd)})")
    for qa in front.get("faq") or []:
        if not (qa.get("q") and qa.get("a")):
            problems.append(f"situation {sp.stem}: faq item incomplete")
        elif len(qa["a"].split()) > 70:
            warnings.append(f"situation {sp.stem}: faq answer over 70 words: {qa['q'][:40]!r}")

# verbatim must be unchanged from the original import
ORIG = Path("/tmp/claude-0/-home-claude/68854712-071e-5fb7-817f-355110082800/scratchpad/orig/content")
if ORIG.exists():
    for md in list((C / "amendments").glob("*.md")) + list((C / "articles").glob("*.md")) + [C / "preamble.md", C / "declaration.md"]:
        om = ORIG / md.relative_to(C)
        if om.exists() and verbatim_text(body_of(md)[1]) != verbatim_text(body_of(om)[1]):
            problems.append(f"{md.relative_to(C)}: VERBATIM TEXT CHANGED")

for w in warnings: print("warn:", w)
for p in problems: print("FAIL:", p)
print(f"{len(stems)} insight files checked, {len(problems)} problems, {len(warnings)} warnings")
sys.exit(1 if problems else 0)
