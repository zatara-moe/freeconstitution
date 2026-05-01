# Search

Search is provided by [Pagefind](https://pagefind.app), a static-site search
library that builds a search index at deploy time. It runs entirely in the
browser. No server, no tracking, no third-party calls.

## Install (one-time)

```
npm install -g pagefind
```

## Build search index

After running `python build.py`, run Pagefind against `dist/`:

```
pagefind --site dist
```

This writes `/dist/pagefind/` containing the search index and the default UI.

## Use in templates

To add search to any page, include this in the template (typically inside
`base.html` near the header or in a dedicated `/search/` page):

```html
<link rel="stylesheet" href="/pagefind/pagefind-ui.css">
<script src="/pagefind/pagefind-ui.js" defer></script>
<div id="search"></div>
<script>
  window.addEventListener("DOMContentLoaded", function () {
    new PagefindUI({ element: "#search", showImages: false });
  });
</script>
```

## Excluding content

To exclude a section from search results, add `data-pagefind-ignore` to the
element in the template. For example, the review-footer is excluded by default
since it contains metadata, not content.
