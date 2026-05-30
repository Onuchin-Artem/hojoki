# Visual Style — "Думки у ретрітній хатинці"

Visual design guidance for all three outputs (HTML, EPUB, PDF). The palette and
type choices below are derived from the cover design and should carry through
the whole book.

See [TYPOGRAPHY.md](TYPOGRAPHY.md) for character-level typographic rules
(dashes, quotes, apostrophes, non-breaking spaces) and [VISION.md](VISION.md)
for structure and design principles.

---

## Colors

| Token | Hex | Use |
|-------|-----|-----|
| Text | `#252120` | Primary text color — most of the body text |
| Red | `#e46340` | Some headers and the running header |
| Grey | `#646161` | Credit line after a verse / at the end of a poem |
| Light grey | `#e8e6dc` | Background for photo pages |

---

## Fonts

| Role | Family | Style | Use |
|------|--------|-------|-----|
| Body | Arsenal | sans-serif | Most of the text — verses and prose |
| Titles | Cormorant Garamond | serif | Book title on title pages |

Both are free (OFL) and cover Ukrainian Cyrillic with true italics. Arsenal is
also available in Canva, keeping cover and interior consistent. (Garet — a
commercial geometric sans — was the original idea; Arsenal replaced it as a free
Cyrillic-capable equivalent.)

---

## Print element styles (PDF)

| Element | Font | Style | Size | Color |
|---------|------|-------|------|-------|
| Title (book title, title pages) | Cormorant Garamond (serif) | — | large | text `#252120` |
| Chapter header | Arsenal (sans) | bold | — | red `#e46340` |
| Running header | Arsenal (sans) | italic | smaller than body | red `#e46340` |
| Credit (after a verse / end of poem) | Arsenal (sans) | italic | smaller than body | grey `#646161` |
| Page number (folio) | Arsenal (sans) | — | — | black |

### Running header & folio (print)

- **Placement:** running header centered at the top; folio (page number) centered at the bottom.
- **Folio format:** the page number is followed by a dot — e.g. `53.`
- **Begins at the first chapter** (start of the main body). Front matter — foreword,
  acknowledgments, the poem «Зречення», title pages, descriptions — carries **no**
  running header.
- **Omitted on:** blank pages, chapter-title (opening) pages, and illustration/photo
  spreads. (The folio keeps counting internally but is not printed on photo spreads.)
- Recto carries the **chapter title**; verso carries the **book title** «Думки у
  ретрітній хатинці».

### Verse & spacing control (print)

The print layout is hand-tuned, not auto-flowed. Specifically:

- **No accidental line breaks in verses.** A verse line that is too long for the
  measure is broken manually at a chosen point — never left to auto-wrap.
- **Logical page breaks.** Where a chapter spans pages, the break falls at a
  sensible point between stanzas. No stranded single lines (widows/orphans), no
  "flying rows."
- **Deliberate vertical space.** Title pages and illustration/photo pages are
  individually designed, with the amount of whitespace chosen by hand.
