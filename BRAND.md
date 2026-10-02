# Free Constitution brand

Free Constitution is part of the Hope for Americans family. It shares one skeleton with Digital Lutheran Church, Luther's World and Free Scripture, so readers never have to relearn how to read or where things are. It keeps its own colour, mark and voice face. It uses **none** of the faith sites' pictures (no rose, book or cross), and its footer links to Hope for Americans only, so it reads as a civic site to schools and legal-aid partners.

## American, without taking sides
The American feel comes from the document itself: parchment, the 1787 serif, federal navy and the 13 stars of 1777. No flag stripes, eagles or bright red-white-blue. These read as partisan to many young readers, and STYLE.md promises neutrality.

## The mark: the page
A parchment page with a folded corner and a heritage-red star, on a federal-navy tile. It pairs with Free Scripture's open book: a book for Scripture, a page for the Constitution.

| File | Use |
|---|---|
| `static/favicon.svg` | Browser tab and header. Small version: star only, no text lines. Lighter tile in dark mode. |
| `static/mark.svg` | Large version with three text lines. 48px and up. |
| `static/mark-512.png` | Search engines (Organization logo) and the app manifest. |
| `static/apple-touch-icon.png` | Home-screen icon (180px, square; the phone rounds the corners). |

- Under 32px, always use the small version.
- Never recolour the star or put the mark on red.
- The header mark is inline SVG (`MARK_SVG` in `scripts/build.py`).

## Name
"Free Constitution" is set in **Source Serif 4 semibold**, with no letter-spacing. DLC and Luther's World set their names the same way.

## Colour
| Token | Hex | Job |
|---|---|---|
| Federal navy `--navy` | #1E3A5F | Buttons, links, icons, current tab, numbers, focus ring |
| Deep navy `--header` | #14283F | Header, the "say this" card |
| Parchment `--paper` | #FBF8F0 | Page |
| Heritage red `--red` | #9B2C24 | **One job: careful.** Don't lists, Myth check, wrong answers, heads-up notes |
| Court gold `--gold` | #7A5A12 | Supreme Court cases (case names, timeline) |
| Green `--green` | #2C6A39 | Do lists, right answers |

Red never decorates. If something isn't a warning, it is navy. Keep the navy deep and greyish so the site stays distinct from Free Scripture's lapis.

## Type
- **Atkinson Hyperlegible Next** for everything people read and tap (family rule 1).
- **Source Serif 4** only for the original 1787/1791 text, the site name, and "the document as the image" (the large Preamble line on the homepage).
- Sentence case and no tracking everywhere, share images included.
- No italics anywhere. Emphasis is bold; case names are bold court gold.

## Shapes
- 14px corners.
- Cards are filled (`--paper-2`, or the light fill on the homepage band) with no border or shadow. The Do / Don't boxes keep their outline because they are warnings.
- Icons: the finder tiles and the bottom bar keep their icons, in navy, for fast scanning. Section headings have no icons.

## Graphic devices
- **The document as the image:** one verbatim line, large, in Source Serif 4, upright. Used for the Preamble line on the homepage.
- **The 13-star ring:** the footer seal only. Never a progress meter or a reward.
- **Timeline 1776–today**, drawn to scale.

## Reading settings (family "Aa" names)
Larger type · More space between lines · Easy-read letters · Focus (hide the menus) · Night mode, then Free Constitution's extra: How much to show. Keys: `/` search · `D` reading settings · `T` night mode · `G` focus.
