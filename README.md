# freeconstitution.org

The U.S. Constitution in plain English, built for young adults and neurodivergent readers.
Free, no ads, no accounts, no tracking. A Hope for Americans project.

## What's in this folder

```
public/     the finished website. This is what Vercel serves. Already built.
content/    all the words (markdown + YAML). Edit these to change the site.
static/     design (css), behavior (js), fonts, share images
scripts/    build.py (makes public/ from content/) and check_content.py
STYLE.md    the writing rules every page follows
vercel.json tells Vercel to serve public/ with no build step
```

## Deploy (no terminal needed)

`public/` is already built, so Vercel only has to serve files.

**Vercel settings** (Project → Settings → Build & Deployment):
- Framework Preset: **Other**
- Build Command: leave empty
- Output Directory: **public**

`vercel.json` sets these too.

**Uploading through the GitHub website** (it takes at most 100 files per upload). Upload in three batches, keeping the folder structure:
1. `content/`, `scripts/`, and the root files (`README.md`, `STYLE.md`, `CHANGELOG.md`, `vercel.json`): about 95 files
2. `static/` and `public/static/`: about 88 files
3. Everything else in `public/`: about 97 files

Or use the free **GitHub Desktop** app: drag this folder in and commit once.

Optional cleanup in the repo: these old files are no longer used and can be deleted: `content/content/`, `content/amendments/amendments.json`, `content/articles/articles.json`, `content/situations/situations.json`, `static/js/prefs.js`, `public/static/js/prefs.js`.

## Changing words later

1. Edit the file in `content/` (for example `content/amendments/4.md` or `content/insights/amendment-4.yml`).
2. Rebuild `public/` with `python3 scripts/build.py` (needs Python 3 and `pip install pyyaml`). If you don't use a terminal, ask Claude to rebuild it.

The build stops and says what's wrong if:
- a "Phrase by phrase" quote doesn't match the original text exactly
- any internal link points to a page that doesn't exist

## How each page is built

- **Amendment page** order: the one-line version · Plain English (original one tap away) · Phrase by phrase · Picture it · What this means for you · Myth check · Go deeper (the scene, back then, words that changed, who argued what, key cases, history, actively contested) · Quick check · If this is happening to you · How this page was made.
- **Display settings** (the `D` key): text size, line spacing, font (Atkinson Hyperlegible, Lexend, Serif), page color (light, sepia, dark), depth (Quick, Standard, Deep), and focus mode (`G`).
- **Situation cards** start with the exact words to say, then do and don't. They work offline after you open them once, and can be printed as a wallet card.
- **Progress, paths and settings** are saved in the reader's browser only.

## Accuracy

This site has not been reviewed by a lawyer, and it says so on every page.
- The original text comes from the National Archives and is never edited.
- Legal claims cite the Supreme Court case and year.
- Every page went through an independent fact-check pass (October 2026).
- Things to re-check after big Supreme Court decisions: `contested:` lists in amendment files, the 2nd Amendment page (AR-15 cases pending), the immigration card, and the hotline numbers before each election.

Corrections link: set `CONTACT_URL` at the top of `scripts/build.py`. It currently points to hopeforamericans.net.
