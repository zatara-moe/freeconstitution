"""Sentence-length check (STYLE.md: never more than 25 words).
Plain-language text only: the original 1787/1791 text, long verbatim quotes and
case names are not counted against the limit. Run alone: python3 scripts/check_sentences.py .
"""
import glob, re, sys, yaml

LIMIT = 25
SKIPK = {"verbatim", "quote", "seo_title", "seo_description", "href", "value", "label"}
# "U.S." ends a sentence when the next word starts one (a capital that is not part of a name like "U.S. Senators").
US_END = re.compile(r"U\.S\.(?=\s+(?:Do|Don't|It|This|That|They|You|We|He|She|If|In|The|A|An|Ask|Call|See)\b)")
ABBR = re.compile(r"\b(U\.S|v|St|Mr|Mrs|Dr|No|Jr|Inc|Co)\.")
# A word in a case name: "Loan", "Farmers'", "Co.", "B.L.". Longer words may not end in a period,
# so a name never runs across the end of a sentence.
NAMEWORD = r"(?:[A-Z][a-z]?\.(?:[A-Z]\.)*|[A-Z][\w'&-]*|of|&)"
CASE = re.compile(r"(?<![\w.])\*?" + NAMEWORD + r"(?:\s+" + NAMEWORD + r")*\s+v\.\s+" + NAMEWORD + r"(?:\s+" + NAMEWORD + r")*\*?")
SPLIT = re.compile(r"(?<=[.!?])[\"”)]?\s+")


def sents(t):
    t = re.sub(r"\s*\|\s*", "\n", t)  # each table cell is read on its own
    t = re.sub(r'"[^"\n]{60,}?"', "QUOTE", t)  # long verbatim quotes count as one word
    t = CASE.sub("CASE", t)  # a case name reads as one name, not many words
    t = US_END.sub("US.", t)
    t = ABBR.sub(lambda m: m.group(1) + "․", t)
    for line in t.split("\n"):
        for s in SPLIT.split(line):
            s2 = re.sub(r"[#*]", "", s).strip(" -")
            if len(s2.split()) > LIMIT:
                yield s2.replace("․", ".")


def walk(o, f, out, k=""):
    if isinstance(o, dict):
        for kk, v in o.items():
            walk(v, f, out, kk)
    elif isinstance(o, list):
        for v in o:
            walk(v, f, out, k)
    elif isinstance(o, str) and k not in SKIPK:
        for s in sents(o):
            out.append((f, k, s))


def find_long(root):
    out = []
    for f in sorted(glob.glob(root + "/content/**/*.md", recursive=True)):
        t = open(f, encoding="utf-8").read()
        parts = t.split("---", 2)
        if len(parts) < 3:
            continue
        body = re.sub(r"## Verbatim.*?(?=\n## |\Z)", "", parts[2], flags=re.S)
        body = re.sub(r"^>.*$", "", body, flags=re.M)
        for s in sents(body):
            out.append((f, "body", s))
        fm = yaml.safe_load(parts[1]) or {}
        for x in fm.get("faq", []) or []:
            for s in sents(x.get("a", "")):
                out.append((f, "faq", s))
    for f in sorted(glob.glob(root + "/content/insights/*.yml")) + [root + "/content/next.yml"]:
        walk(yaml.safe_load(open(f, encoding="utf-8")), f, out)
    return out


if __name__ == "__main__":
    res = find_long(sys.argv[1] if len(sys.argv) > 1 else ".")
    for f, k, s in res:
        print(f.split("content/")[1], "|", k, "|", len(s.split()), "|", s)
    print(len(res), file=sys.stderr)
