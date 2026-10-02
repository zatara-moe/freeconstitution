# Insight files

One YAML file per document: `amendment-<n>.yml`, `article-<n>.yml`, `preamble.yml`, `declaration.yml`.
The build reads them and lays the page out in a fixed order. Every field is optional except `one_line`.
Read STYLE.md first. Quote YAML strings that contain a colon.

```yaml
one_line: >-          # 25 words or fewer. The single most useful thing to know.
  Police generally need a warrant, your consent, or a legal exception to search you or your things.
subject: Search and seizure     # 2–5 words, shown in the header and on the grid
content_note: null    # one sentence heads-up before hard history, or null
scene:                # "The scene": who, when, why. 2–4 sentences.
  when: "1791"
  text: >-
    ...
phrases:              # "Phrase by phrase". 3–8 rows. `quote` must appear EXACTLY in the ## Verbatim text.
  - quote: "secure in their persons, houses, papers, and effects"
    plain: "You, your home, your documents, and your things are protected."
picture_it: >-        # Everyday example, second person, 2–4 sentences. Shown as "Example. Not legal advice."
  ...
myths:                # "Myth check". 1–3 items. Things young people commonly believe.
  - myth: "..."
    fact: "..."
words_changed:        # "Words that changed". 1–3 items. Old words whose meaning shifted or needs explaining.
  - word: "papers"
    then: "..."
    now: "..."
back_then: >-         # 2–4 sentences on what the writers were reacting to.
  ...
who_argued:           # optional. 2+ sides, each in its own strongest terms.
  - side: "Federalists"
    view: "..."
key_cases:            # 0–5 cases, oldest first. Only real Supreme Court cases; `held` = one sentence.
  - name: "Riley v. California"
    year: 2014
    held: "Police generally need a warrant to search the phone of someone they arrest."
quick_check:          # 2–3 questions, 3 options each, `answer` = index of the right option (0-based).
  - q: "..."
    options: ["...", "...", "..."]
    answer: 0
    why: "..."
sections:             # ARTICLES ONLY: a one-line version for each numbered section.
  1: "Congress makes federal laws. It has two parts: the Senate and the House."
```

## Body markdown (`content/amendments/<n>.md` etc.)
- Keep `## Verbatim`, `## Plain English`, `## What this means for you` (if present), `## About`.
- Inside "What this means for you", split into short cards with `### Card title` (2–5 cards, each 1–3 short paragraphs).
- Remove the old `review:` block from frontmatter.
