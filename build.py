#!/usr/bin/env python3
"""
freeconstitution.org build script.

Reads markdown content from content/, applies Jinja2 templates from templates/,
copies static assets from static/, and writes the finished site to dist/.

Usage:
    python build.py
    python build.py --watch   (rebuild on file changes; requires watchdog)

Dependencies:
    pip install markdown pyyaml jinja2

Optional:
    pip install watchdog       (for --watch mode)
    pip install pagefind       (for search index, called separately after build)
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
DIST = ROOT / "dist"

# ---------------------------------------------------------------------------
# Markdown setup
# ---------------------------------------------------------------------------

MD = markdown.Markdown(
    extensions=["extra", "smarty", "sane_lists"],
    output_format="html5",
)

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n(.*)$", re.DOTALL)


def parse_markdown(path: Path) -> tuple[dict, str]:
    """Read a markdown file with YAML frontmatter. Returns (metadata, html)."""
    raw = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(raw)
    if not match:
        raise ValueError(f"{path}: missing YAML frontmatter")
    meta = yaml.safe_load(match.group(1)) or {}
    body_md = match.group(2)
    MD.reset()
    body_html = MD.convert(body_md)
    sections = split_sections(body_md)
    return meta, body_html, sections


def split_sections(body_md: str) -> dict[str, str]:
    """Split body markdown by ## headings into a dict keyed by heading slug."""
    sections: dict[str, str] = {}
    current_key: str | None = None
    current_lines: list[str] = []
    for line in body_md.splitlines():
        if line.startswith("## "):
            if current_key is not None:
                sections[current_key] = render_section("\n".join(current_lines).strip())
            heading = line[3:].strip()
            current_key = slugify(heading)
            sections[f"{current_key}_heading"] = heading
            current_lines = []
        else:
            current_lines.append(line)
    if current_key is not None:
        sections[current_key] = render_section("\n".join(current_lines).strip())
    return sections


def render_section(text: str) -> str:
    MD.reset()
    return MD.convert(text)


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text).strip("_")
    return text


# ---------------------------------------------------------------------------
# Jinja2 setup
# ---------------------------------------------------------------------------

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES)),
    autoescape=select_autoescape(["html"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def format_date(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return value
    if isinstance(value, (date, datetime)):
        return value.strftime("%B %-d, %Y")
    return str(value)


def ordinal(n: int) -> str:
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


env.filters["format_date"] = format_date
env.filters["ordinal"] = ordinal


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def collect(folder: str) -> list[dict]:
    items = []
    folder_path = CONTENT / folder
    if not folder_path.exists():
        return items
    for path in sorted(folder_path.glob("*.md")):
        meta, html, sections = parse_markdown(path)
        meta["_path"] = path
        meta["_html"] = html
        meta["_sections"] = sections
        items.append(meta)
    return items


def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    # Copy static assets
    if STATIC.exists():
        shutil.copytree(STATIC, DIST, dirs_exist_ok=True)

    # Collect content
    amendments = collect("amendments")
    amendments.sort(key=lambda m: m.get("number", 0))

    articles = collect("articles")
    articles.sort(key=lambda m: m.get("number", 0))

    situations = collect("situations")
    situations.sort(key=lambda m: m.get("title", ""))

    # Site-wide context
    site = {
        "title": "freeconstitution.org",
        "tagline": "Read your Constitution. Know your rights.",
        "build_date": date.today().strftime("%B %-d, %Y"),
        "amendments": amendments,
        "articles": articles,
        "situations": situations,
    }

    # Homepage
    write_page("index.html", "homepage.html", site=site)

    # Preamble
    preamble_meta, preamble_html, preamble_sections = parse_markdown(CONTENT / "preamble.md")
    preamble_meta["_html"] = preamble_html
    preamble_meta["_sections"] = preamble_sections
    write_page("preamble/index.html", "preamble.html", site=site, item=preamble_meta)

    # Articles
    for article in articles:
        n = article["number"]
        write_page(
            f"articles/{n}/index.html",
            "article.html",
            site=site,
            item=article,
        )

    # Amendments
    for amendment in amendments:
        n = amendment["number"]
        write_page(
            f"amendments/{n}/index.html",
            "amendment.html",
            site=site,
            item=amendment,
        )

    # Situations
    for situation in situations:
        slug = situation["slug"]
        write_page(
            f"situations/{slug}/index.html",
            "situation.html",
            site=site,
            item=situation,
        )

    # Situations index
    write_page("situations/index.html", "situations_index.html", site=site)

    # Declaration
    decl_meta, decl_html, decl_sections = parse_markdown(CONTENT / "declaration.md")
    decl_meta["_html"] = decl_html
    decl_meta["_sections"] = decl_sections
    write_page("declaration/index.html", "declaration.html", site=site, item=decl_meta)

    # About + Sources
    for slug in ("about", "sources"):
        meta, html, sections = parse_markdown(CONTENT / f"{slug}.md")
        meta["_html"] = html
        meta["_sections"] = sections
        write_page(f"{slug}/index.html", "page.html", site=site, item=meta)

    print(f"Built {count_files(DIST)} files in {DIST}")


def write_page(out_path: str, template_name: str, **context):
    template = env.get_template(template_name)
    html = template.render(**context)
    target = DIST / out_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")


def count_files(path: Path) -> int:
    return sum(1 for _ in path.rglob("*") if _.is_file())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Build freeconstitution.org")
    parser.add_argument("--watch", action="store_true", help="Rebuild on file changes")
    args = parser.parse_args()

    build()

    if args.watch:
        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer
        except ImportError:
            print("watchdog not installed; install with: pip install watchdog", file=sys.stderr)
            return

        class RebuildHandler(FileSystemEventHandler):
            def on_any_event(self, event):
                if event.is_directory:
                    return
                if "/dist/" in event.src_path:
                    return
                print(f"Change detected: {event.src_path}")
                try:
                    build()
                except Exception as e:
                    print(f"Build failed: {e}", file=sys.stderr)

        observer = Observer()
        for d in (CONTENT, TEMPLATES, STATIC):
            observer.schedule(RebuildHandler(), str(d), recursive=True)
        observer.start()
        print("Watching for changes. Press Ctrl+C to stop.")
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
