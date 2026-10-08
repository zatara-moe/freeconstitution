# Changelog

## v3.1 — October 7, 2026: what happens next, and the official civics test
### What happens next (`/what-happens-next/`)
- Three step-by-step guides: **a traffic stop** (7 steps), **after an arrest** (7 steps), and **Election Day** (7 steps).
- Each step shows "Step 1 of 7", a time, what usually happens, what you can do, a line to say, and a link to the law.
- They open one step at a time, with Back and Next and "Show all steps". They work without JavaScript, and `#step-3` links work.
- Linked from Being questioned, Searched, Communicating with police, First-time voter, Turned away from voting, the "Getting pulled over" path, and the footer.
- An independent fact-check found 9 issues, and all are fixed. Examples:
  - The right to a free lawyer depends on whether you are actually sent to jail (Scott, Shelton).
  - The 48-hour review is for arrests without a warrant (McLaughlin).
  - A request for a lawyer must be clear (Davis), and silence has to be said out loud (Berghuis).
  - Provisional ballots are guaranteed in federal elections only, and may not count at the wrong polling place.
  - A warning that noncitizen voting is a federal crime.
  - Refusing to sign a ticket can lead to arrest in some states.

### Citizenship test: matched to the official PDF
- The official USCIS PDF was opened and read in full, and every question and answer matches it.
- Juneteenth is back in Q126, and Q118's full answer is restored. Q48 "Secretary of War (Defense)" is confirmed.
- The list is grouped by the official sections (American government, American history, symbols and holidays).
- New notes: answer with the official serving on the day of your interview, and 65/20 applicants may take the test in the language of their choice.

## v3.0 — October 7, 2026: Spanish meanings, citizenship test, turning 18
The third release from the October 7 gap review, using only work we can do and check ourselves.

### Spanish
- **"Ver en español"** on all 13 situation cards. Each say-this line shows its Spanish meaning underneath. English stays the line to say or show, so a translation slip can't change what an officer hears. The choice is remembered on the device and also shows in Show on screen and the printed wallet card.
- A blind back-translation by a separate reviewer caught 5 must-fix issues, all fixed. The worst: "Por favor, pase…" (which can read as "please come in") became "Por favor, deslice la orden…".
- The right-to-silence line is now the same on every card: "I am exercising my right to remain silent." The Spanish is always "Ejerzo mi derecho a guardar silencio."
- The detained card now warns: if you fear going back to your country, talk to a lawyer before you contact your consulate.

### Citizenship test practice (`/citizenship-test/`)
- All 128 questions of the 2025 USCIS civics test, with the official answers and a 65/20 filter.
- A 20-question practice run (10 for 65/20) with "Hear the question", "I knew it / Not yet", a score against the pass mark, and "Practice the ones you missed". Nothing is saved.
- The full list works without JavaScript, and answers that change point to uscis.gov/citizenship/testupdates.
- The list was checked word for word against the official USCIS PDF and is grouped by the official sections. Answers about current officials say to use the person serving on the day of your interview. 65/20 applicants can take the test in the language of their choice.
- The Founding documents tour path ends with the practice page.

### New pages
- **I just turned 18** (`/turning-18/`): voting, Selective Service (including immigrant men and the planned automatic sign-up), jury duty.
- **I got a jury summons** (situation card, with Spanish): who can serve, postponing, job protection, and what to do if you're not a citizen.
- **Who the Constitution covers** (`/who-it-covers/`): state action, with a table of private actors and the laws that may still protect you.
- **Make your voice heard** (`/your-voice/`): contacting officials, public meetings, federal rule comments, petitions. It includes a protest caution for noncitizens.
- Two new paths: **I just turned 18** and **Make your voice heard**.
- An independent fact-check found 7 issues, and all are fixed. Examples: age discrimination law covers only people 40 and older, the 13th Amendment's crime exception, automatic Selective Service sign-up, and the protest caution.

### Under the hood
- Markdown tables now render on any page, as stacked rows on phones.
- The sentence check reads table cells on their own.
- 102 pages and 62 share images. The cache version was bumped.

## v2.5 — October 7, 2026: rights for everyone, and access
The second release from the October 7 gap review.

### New pages
- **Rights for everyone, whatever your status** (`/everyone/`). A table of the Constitution's own words ("person", "the accused", "the people", "citizens") showing which rights cover everyone and which are for citizens only. Also covers *Plyler v. Doe*, the debate over "the people" (*Verdugo-Urquidez*, *Thuraissigiam*), and links to the immigration cards. It has a share image and FAQ data, and is linked from the homepage finder and the footer.
- **Autistic, Deaf, or anxious at a police stop** (situation card). Lines to say or show, the right to an interpreter under the ADA, what drivers still must show, voluntary license notes, and a MOEx link.
- **Immigration agents in public or at work** (situation card). Free to leave, papers rules for people 18 and older, public and private areas at work, Border Patrol checkpoints (*Martinez-Fuerte*), the name rule in some states, and *Noem v. Vasquez Perdomo* under "Still being decided".
- **If you or a family member is detained** (situation card):
  - Don't sign without a lawyer, and ask for your consulate.
  - Bond since 2025, where courts disagree.
  - No government-paid lawyer in immigration court (8 U.S.C. § 1362).
  - How to use the ICE Online Detainee Locator, and the A-number.
  - Fast-track deportation, and keeping proof of 2 years here.
- The homepage finder now has 10 doors, adding "I'm not a citizen" and "I'm autistic, Deaf, or anxious around police".

### New on every page
- **Listen.** It reads the one-line version, the Plain English, and the say-this lines aloud with the device's own voice. It is free, works offline, and stays hidden where a browser has no voice.
- **Practice saying it.** It is on every situation card and uses the Know it by heart engine: Read, First letters, Put in order. Nothing is saved.

### Checks
- An independent fact-check of the four new pages found 7 issues. All are fixed, including two changes in the law in 2025–26 (bond, and fast-track deportation).
- The sentence check now spots "U.S." at the end of a sentence.
- Glossary counts on the Words page and its share image now update by themselves (74 terms).
- 57 share images. The cache version was bumped.

## v2.4 — October 7, 2026: safety and accuracy
The first release from the October 7 gap review (young adults, neurodivergent readers, immigrants).

### Safety
- **Voting card: "If you are not a U.S. citizen."** Only citizens vote in federal and state elections. Don't register, don't vote, and don't tick "citizen" on any form, including at the DMV. Doing so can lead to deportation and block citizenship later (8 U.S.C. § 1227). The card also covers the few cities that allow local noncitizen voting, and people who may be citizens through a parent without knowing it. It adds a new Don't and a FAQ: "Can a green card holder vote?"
- **At school: "Every child can go to public school."** *Plyler v. Doe* (1982), plus a FAQ: "Can undocumented students go to public school?"
- **Immigration card:**
  - Ask about local rapid-response lines.
  - Decide who picks up your children, and tell the school.
  - New section: get help only from a lawyer or a DOJ-accredited representative, never a "notario".

### Laws that add to the Constitution (new box)
- At school: IDEA and Section 504, linking to Mama Shepherd's [IEP vs 504 plan](https://www.mamashepherd.com/school).
- At work: the ADA and reasonable accommodations, linking to MOEx's [Do I tell work?](https://ilovemoe.com/adults/work).
- Both are Hope for Americans sites with no faith focus. Free Constitution still links to no faith sites.

### Accuracy and plain language
- "Citizenship test basics" is now **"Founding documents tour"**. It was never the test itself; the blurb now points to the official USCIS study materials. The URL is unchanged.
- **14 new glossary words** (74 in all): accommodation, administrative warrant, asylum, deportation, disability, ICE, interpreter, judicial warrant, jury summons, lawful permanent resident, noncitizen, notario, Selective Service, state action.
- **23 long sentences rewritten** so that no plain-language sentence is over 25 words. Mostly on the 4th, 14th and 25th Amendment pages.

### Checks
- **New:** the build fails on any plain-language sentence over 25 words (`scripts/check_sentences.py`). The original text, long quotes and case names don't count toward the limit.
- **Fixed:** the check that the original National Archives text is unchanged pointed to a folder that no longer existed, so it had stopped running. It now compares against fingerprints in `scripts/verbatim.lock.json`, and it was break-tested.
- The cache version was bumped, so offline copies of the voting and immigration cards refresh.
- README has a review calendar: what to re-check, and when.

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
