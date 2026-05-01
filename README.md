# freeconstitution.org

A free, ad-free, account-free reference for the United States Constitution.

## Stack

- Eleventy (Node.js static site generator)
- Nunjucks templates
- Markdown + YAML frontmatter for content
- Vercel for hosting (zero config)

## Local development

Requires Node.js 18+.

```
npm install
npm run dev
```

Visit http://localhost:8080.

## Build

```
npm run build
```

Output goes to `_site/`.

## Project layout

```
content/        — markdown content
layouts/        — Nunjucks templates
data/           — site-wide data (title, tagline)
css/            — stylesheets
js/             — client scripts
index.njk       — homepage
situations.njk  — situations index
```

## Editorial process

See PROCESS.md.
