# Changelog

## v2.5 — October 19, 2026: card copy written to fit
- Rewrote every card's text to a set length so each group reads as a set: one-line titles, two-line descriptions, no single word left alone on a line. Checked at ten screen widths from 360px to 1440px.
- New `card:` and `card_title:` fields for situation cards and `short:` for paths. Page headings and search descriptions are unchanged.
- "What's going on?" buttons use short labels that match the situation card names, one line each. One column on phones, like Hope for Americans.
- Shorter questions on the homepage, and short names for the Bill of Rights and articles grids (for example "Due process", "Making changes").
- Columns are added later on mid-size screens, so cards never get too narrow for their text.
- `scripts/check_card_lines.mjs` re-runs the line check after copy changes.

## v2.4 — October 19, 2026: one card style, no decorative icons
- Every card on the site now uses one style that matches Hope for Americans: a small gold label, a bold title, and a short line of text. Situation cards, paths, amendments, articles, sections, and questions all line up the same way.
- Removed the decorative icons from cards and headings (shields, lightbulbs, stars, clocks). Icons that do a job stay: search, display, close, and the check and X on Do and Don't.
- "What's going on?" choices are simple bordered buttons, like "Help me choose" on Hope for Americans.
- Read pages show "Read" in the card label instead of a hidden check mark.
- Homepage: the Preamble joins the articles row (two even rows of four). Card groups and "see all" links have more breathing room.
- Article pages no longer repeat the subtitle when it matches the title ("Congress / Congress").

## v2.3 — October 19, 2026: wider layout, matched to Hope for Americans
- One 64rem container for the header and every page, so content lines up with the logo (same pattern as hopeforamericans.net). Reading text stays at a comfortable line length.
- Reading pages (amendments, articles, situation cards, Preamble, Declaration) get an "On this page" side list on wide screens. It highlights the section you are reading and hides in focus mode.
- Homepage hero is two columns on wide screens: the headline and search on the left, "If police stop you, say this" on the right. On phones the situation buttons come first.
- Wider grids: situation cards, paths, questions and articles in two columns; the Bill of Rights in five columns on the homepage.
- Header mark is now the same drawing as the favicon (the red dot no longer drops below the box).
- Fixed: "say this" cards were unreadable when a phone was set to dark mode.
- Fixed: the Next button could push the page sideways on small phones.

## v2.1 — October 1, 2026: search and AI-answer optimization
- Search-shaped titles and descriptions on all 91 pages, all within length limits. Example: "4th Amendment Explained: Search and Seizure in Plain English".
- 245 new "Common questions" answers across amendments, articles, situation cards, the Preamble, the Declaration and the Bill of Rights. All were fact-checked; 30 fixes were made before release.
- New Bill of Rights page (`/bill-of-rights/`), a high-volume search topic.
- Clearer page headings on situation cards ("Can ICE enter my home? Your rights at the door"). The homepage heading now includes "the Constitution in plain English".
- Structured data on every page: Article, FAQPage, BreadcrumbList, Organization, WebSite with search, DefinedTermSet, and ItemList.
- 53 new share images that use the page title.
- `robots.txt` names AI crawlers. `/llms.txt` was expanded and `/llms-full.txt` added. Utility pages are set to noindex, and the sitemap was cleaned up.
- `vercel.json` adds 92 short-link redirects (for example `/4th-amendment` and `/know-your-rights`).
- Removed the vote count for *Trump v. Barbara*, because sources disagree on how to count it. Pages now state the holding only.

## v2.0 — October 1, 2026: rebuilt for neurodivergent and young adult readers

### Trust and accuracy
- About and Sources now say plainly that the site has not been reviewed by a lawyer, and explain how it is checked instead. Removed the false claims of attorney review, the broken `/notes` link, and the "open source" claim.
- Every page has a "How this page was made" box, a "Last updated" date, and a corrections link.
- The 14th Amendment page is updated for *Trump v. Barbara* (June 30, 2026) and its incorporation wording error is fixed. Added *Rahimi* (2024), *Tinker* (1969), *Mahanoy* (2021), and *Louisiana v. Callais* (2026).
- An independent fact-check pass made 36 corrections across all pages.
- Removed the stale duplicate content folder and leftover Eleventy files.

### New page design
- Plain English comes first. The original 1787/1791 text is one tap away.
- Every page has: The one-line version, Phrase by phrase, Picture it, What this means for you (cards), Myth check, Go deeper, and Quick check.
- Articles I–IV are split into one page per section (21 new pages).
- Readable typography: Atkinson Hyperlegible Next by default, with Lexend or Serif options. Fonts are self-hosted.
- Display settings: text size, line spacing, font, page color (light, sepia, dark), depth (Quick, Standard, Deep), and focus mode. Keyboard keys: `/` `D` `T` `G`.
- Tap any underlined legal word to see a definition. The 60-term glossary is at /words/.
- Heads-up notes appear before hard history (slavery, "Indians not taxed").

### New ways in
- Homepage "What's going on?" finder with 8 situations, plus search across everything.
- 10 situation cards (6 new): at school, posting online, at work, recording police, first-time voter, immigration agents at the door.
- Each card starts with a 10-second "say this" box and has Show on screen, Save to phone, and Print wallet card buttons, plus do and don't lists.
- 9 guided paths with a step bar and progress.
- A timeline from 1776 to today, drawn to scale.
- Know it by heart: memorize practice with Read, First letters, and Put in order modes.
- The full original text on one page.
- Offline support: situation cards work without internet after the first visit.
- Progress, "pick up where you left off", and read checkmarks, all stored on the device only.

### Checks
- The build fails if a quote doesn't match the original text, or if any internal link is broken.
- No WCAG 2.1 AA violations (axe) across key pages in light, sepia, and dark.
