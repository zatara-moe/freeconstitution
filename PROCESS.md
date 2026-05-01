# Editorial Process

This document describes how content on freeconstitution.org is written, reviewed, and updated. It exists to prevent editorial drift over years and to make the editorial choices visible to readers, contributors, and reviewers.

## Voice rules

These rules apply to every plain-English layer on the site.

1. **Drop archaic words, keep alive ones.** "Ordain" out, "establish" in. "Posterity" out, "the generations who come after us" in. "Insure" (in its old sense of *ensure*) out, "keep" or "ensure" in. Words like "abridge" and "infringe" are dead in modern English; "take away" and "violate" replace them.

2. **Don't drift into casual register.** Plain-English is not chat-English. Keep the seriousness of the document. The verb "establish" is alive; the verb "create" reads as casual.

3. **Prefer collective framings where the original is collective.** "The country," "the people," "the nation" — not "everyone" or "individuals" — when the original text is talking about the whole.

4. **Match the third-layer label to what the section does.** Rights amendments get "What this means for you." Structural sections get "About this Amendment" or "About Article [N]." The Preamble gets "About the Preamble."

5. **Repetition of consistent vocabulary beats synonym variation.** Civic reference is not literary writing. If "the government" is the right rendering, use it every time.

6. **Pronoun standard.** Second person ("you") for rights amendments where the text is talking to the reader. Third person ("the government," "Congress") for structural articles and amendments where the text is describing how government works.

7. **Prefer literal language over figurative.** No "long line of cases" — say "many cases." No "the framers wrestled with" — say "the framers debated." No "the Constitution's beating heart." Metaphors create cognitive overhead; literal language doesn't.

8. **Predictable structure within and across pages.** Every amendment page is in the same order: verbatim, plain-English, "What this means for you" (if applicable), "About this Amendment," footer. No surprises.

## When plain-English may add inline editorial commentary

Plain-English is otherwise a faithful restatement. The exception is sections where the verbatim text describes a system that was significantly modified by later amendments, where reading the verbatim alone would mislead a reader into thinking it is current law.

In these cases only, the plain-English layer may include an italicized "Note:" sentence explaining the modification. The places this rule applies in the current document:

- Article I, Section 2 (three-fifths clause modification by 13th and 14th Amendments)
- Article I, Section 3 (17th Amendment changing senator selection)
- Article I, Section 4 (20th Amendment changing congressional meeting date)
- Article I, Section 9 (slave trade clause expiration in 1808; 16th Amendment modifying direct tax rule)
- Article II, Section 1 (12th Amendment electoral procedure; 25th Amendment succession)
- Article III, Section 2 (11th Amendment limiting state lawsuits)
- Article IV, Section 2 (Fugitive Slave Clause voided by 13th Amendment)
- Article V (1808 limit on slave trade amendments expired)
- 14th Amendment, Section 2 (superseded in effect by 19th, 24th, 26th Amendments)
- 18th Amendment (repealed by 21st Amendment)

No new inline editorial notes may be added without review by at least one reviewer and a second reader. The list above is exhaustive as of the launch version.

## Review tiers

| Tier | Content | Required reviewers | Status at launch |
|---|---|---|---|
| 1 | Preamble + Bill of Rights (1-10) | Civil rights attorney + criminal defense attorney | Reviewed, signed, dated |
| 2 | 13th, 14th, 15th, 19th, 24th, 26th | Civil rights attorney | Reviewed, signed, dated |
| 3 | Articles I-VII | Constitutional law professor | Reviewed, signed, dated |
| 4 | 11, 12, 16-18, 20-23, 25, 27 | Constitutional law professor | Drafted, marked "Pending review" |
| 5 | Declaration of Independence | None required (historical, not law) | Drafted, no review needed |
| 6 | All Situations cards | Civil rights + criminal defense; immigration card requires immigration attorney additionally | Reviewed, signed, dated |

## Editorial workflow for changes

Once content is published, changes follow these rules:

1. **Verbatim text never changes.** It is from the National Archives and is fixed.

2. **Plain-English changes require:**
   - A second reader (named in the commit)
   - Signed git commit by the author
   - If the change is more than wording (e.g., affects meaning), re-review by the original tier reviewer

3. **"What this means for you" cards may need updating** as case law evolves. These changes require:
   - A second reader (named in the commit)
   - Signed git commit
   - Citation to the new case law that prompted the update

4. **"About" cards may be updated for accuracy or new historical context.** Same requirements as "What this means for you" cards.

5. **Situations cards** are the most operationally consequential. Changes require both a second reader and re-review by a relevant tier reviewer.

## Per-section review metadata

Every content file has a `review` block in its YAML frontmatter recording:

- The status of each layer (verified, reviewed, pending)
- The reviewer's name (when applicable)
- The date of last review

This metadata is rendered visibly on every page of the live site, so readers can see the review status of what they are reading.

## Authorship and contributions

All editorial commits to content files must be made by named individuals. Anonymous edits to plain-English content, "What this means for you" cards, "About" cards, or Situations cards are not accepted. Code contributions (build script, templates, styles) may follow ordinary open-source contribution practices.

The list of editorial contributors is maintained at `/about` on the live site.

## What this site does not do

The discipline of staying narrow is itself an editorial choice. The site explicitly does not:

- Offer interpretive commentary on what the founders "really meant"
- Take positions on contested constitutional questions (the 2nd Amendment, 14th Amendment Section 3, etc.)
- Provide legal advice for specific situations
- Host comments, accounts, or user-generated content
- Track readers, run ads, or monetize content
- Promote any organization, candidate, party, or cause

These are not arbitrary restrictions. They are what makes the site trustworthy across the political spectrum and durable over decades.
