# freeconstitution.org

A free, ad-free, account-free reference for the United States Constitution.
Static site, same build pattern as freescripture.org.

## Stack

- Python build script, no framework
- Markdown + YAML frontmatter for content
- Output is a plain `public/` folder, host anywhere (Cloudflare Pages, Vercel)

## Build

```
python3 scripts/build.py
```

Requires Python 3 and PyYAML (`pip install pyyaml`).
Output goes to `public/`. The build validates every homepage jump point
against the generated section anchors and fails loudly if one breaks.

## Project layout

```
content/        markdown content (articles, amendments, situations, pages)
scripts/        build.py
static/         css, js, favicon (copied into public/static on build)
public/         generated site, this is what you deploy
```

## Editing the jump rail

The homepage "Your rights, asked a lot right now" questions live in
JUMP_POINTS at the top of scripts/build.py. Each entry is a question,
a link, and a source label. Rebuild after editing. If a link points at
a section that does not exist, the build stops and tells you which one.
