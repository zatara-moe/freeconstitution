# Changelog

## v2.3 — October 1, 2026: family identity
Brings Free Constitution into the Hope for Americans family style, keeping it American and civic. See BRAND.md.

- **New mark: the page.** A parchment page with a folded corner and a red star, on a navy tile. It replaces the "f." in the header, the favicons, the home-screen icon, the share images and the search-engine logo (new `mark.svg` and `mark-512.png`).
- **Fixed:** the red dot of the old "f." mark fell below its tile on every page.
- **Name in Source Serif 4,** as DLC and Luther's World set theirs. Letter-spacing removed.
- **Red has one job:** careful (Don't, Myth check, wrong answers). Section icons, numbers, phrase arrows, founding events and letter headings are now navy. The focus ring is navy with a paper halo, and light on the header.
- **Upright text:** no italics anywhere. Case names are bold court gold (201 across the site); other emphasis is bold. The italic font files were removed.
- **Reading settings use the family names:** Larger type · More space between lines · Easy-read letters · Focus (hide the menus) · Night mode, then How much to show. On desktop the button reads "Reading".
- **Filled cards:** no borders or shadows on finder tiles, cards, phrases and jump links. Section headings no longer carry icons.
- **The document as the image:** the homepage shows the Preamble's opening line large, linking to the Preamble page.
- **Footer and About:** 13-star seal, plus "More free tools from Hope for Americans". The About page now links to Hope for Americans instead of Free Scripture. No faith-site links remain.
- **Share images:** all 53 regenerated with a sentence-case label, a navy rule and the new mark.
- The cache version was bumped, so returning visitors get the new styles and the offline cache refreshes.

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
