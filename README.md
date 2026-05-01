# Free Constitution

A free, ad-free, account-free reference site for the U.S. Constitution. The full original text from the National Archives, alongside a careful plain-English version, plus quick references for situations where you might need to know your rights.

**Domain:** freeconstitution.org
**Tagline:** Read your Constitution. Know your rights.
**Audience:** Anyone who reads outside the legal-academic register, with particular attention to neurodivergent readers.

## Project structure

```
freeconstitution/
├── content/                Source content files (Markdown + YAML frontmatter)
│   ├── preamble.md
│   ├── declaration.md
│   ├── articles/           Articles I-VII
│   ├── amendments/         Amendments 1-27
│   └── situations/         Pocket-reference cards
├── templates/              Jinja2 HTML templates
├── static/                 CSS, fonts, search assets
├── reviewers/              Reviewer profiles (YAML)
├── build.py                Build script
├── PROCESS.md              Editorial governance and review procedures
└── dist/                   Built site (generated, not in git)
```

## Building the site

```bash
pip install --break-system-packages markdown pyyaml jinja2
python build.py
```

The build reads files from `content/` and writes static HTML to `dist/`. Pagefind runs at deploy time to generate the search index.

## Editorial principles

The full editorial methodology is in `PROCESS.md`. Brief version:

1. **Verbatim text is the authority.** Plain-English is commentary on the text, never a replacement.
2. **Plain-English preserves textual ambiguity** rather than resolving it. (The Second Amendment is the canonical example.)
3. **Three layers per rights amendment**: verbatim, plain-English, "What this means for you."
4. **One layer for structural amendments and Articles**: verbatim, plain-English, About.
5. **Literal language over figurative** throughout, for neurodivergent readers and ESL readers.
6. **Predictable structure** — every page is in the same order with the same headings.
7. **The architecture stays calm.** Stress is the user's, not the site's.

## Source

The verbatim text is from the U.S. National Archives literal-print transcripts:
- https://www.archives.gov/founding-docs/constitution-transcript
- https://www.archives.gov/founding-docs/bill-of-rights-transcript
- https://www.archives.gov/founding-docs/amendments-11-27
- https://www.archives.gov/founding-docs/declaration-transcript

## License

Verbatim text: U.S. government works, public domain.
Plain-English versions, "What this means for you" cards, and "About" cards: CC BY-SA 4.0. Attribution required; modifications must be shared under the same license.
Code: MIT.
