# freeconstitution.org

A free, ad-free, account-free reference for the United States Constitution. Verbatim text plus plain-English explanations, designed to read clearly to anyone — including readers who are not lawyers, who learned English as a second language, or whose brains work differently from the assumptions academic writing tends to make.

## Stack

- **Eleventy** (static site generator) — Node.js
- **Nunjucks** templates
- **Markdown + YAML frontmatter** for content
- **Vercel** for hosting (zero config)

## Local development

Requires Node.js 18+.

```
npm install
npm run dev
```

Visit `http://localhost:8080`. The server auto-rebuilds on file changes.

## Build

```
npm run build
```

Output goes to `_site/`.

## Project layout

```
src/
├── _data/site.js            ← site title, tagline
├── _includes/               ← Nunjucks layouts
│   ├── base.njk
│   ├── amendment.njk
│   ├── article.njk
│   ├── situation.njk
│   ├── preamble.njk
│   ├── declaration.njk
│   └── page.njk
├── content/
│   ├── amendments/1.md … 27.md
│   ├── articles/1.md … 7.md
│   ├── situations/*.md
│   ├── preamble.md
│   ├── declaration.md
│   ├── about.md
│   └── sources.md
├── css/site.css
├── js/prefs.js
├── favicon.svg
├── robots.txt
├── index.njk                ← homepage
└── situations.njk           ← situations index
```

## Editorial process

See `PROCESS.md` for the full editorial governance documentation.
