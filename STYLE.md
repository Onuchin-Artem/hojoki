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
| Chapter header | Arsenal (sans) | bold, **left-aligned** | 18 pt | red `#e46340` |
| Running header (recto only) | Arsenal (sans) | italic | 9 pt | red `#e46340` |
| Credit (after a verse / end of poem) | Arsenal (sans) | italic | smaller than body | grey `#646161` |
| Photo name | Arsenal (sans) | bold, right-aligned | 12.5 pt | red `#e46340` |
| Page number (folio) | Arsenal (sans) | — | 8.5 pt | black |

### Running header & folio (print)

- **Recto only.** The running header (chapter title) appears on **recto pages only**;
  verso pages carry **no** running header (the book title is not repeated). The folio
  appears on **both** verso and recto.
- **Placement:** running header centered at the top, set ~22 mm into the top margin
  (`header-ascent`) so it sits high and well clear of the trim; folio centered at the bottom.
- **Folio format:** the page number is followed by a dot — e.g. `53.`
- **Begins at the first chapter** «Пролог» (start of the main body). Front matter — foreword,
  acknowledgments, the poem «Зречення», title pages, descriptions — carries **no** running header.
- **Omitted on:** blank pages, chapter-title (opening) pages, and photo spreads.
  (The folio keeps counting internally but is not printed on photo spreads.)

### Body page metrics (print)

- **Trim:** B6 — 125 × 176 mm.
- **Margins (Van de Graaf canon, gutter-adjusted):** inner 19 / outer 26 / top 32 / bottom 40 mm.
  Outer > inner, bottom > top — generous, grounded, classic.
- **Header/footer placement:** `header-ascent` 22 mm (high, clear of trim); `footer-descent` 20 mm.
- **Body:** Arsenal 11 pt, leading 0.9em, **strophe spacing 2em**, top-aligned on ordinary
  pages. Special pages (chapter openings, «Зречення», closing «…тиша», title pages) are
  vertically centered.
- **Folio:** centered at the bottom, with a trailing dot.

### Verse & spacing control (print)

The print layout is hand-tuned, not auto-flowed. Specifically:

- **No accidental line breaks in verses.** A verse line that is too long for the
  measure is broken manually at a chosen point — never left to auto-wrap.
- **Logical page breaks.** Where a chapter spans pages, the break falls at a
  sensible point between stanzas. No stranded single lines (widows/orphans), no
  "flying rows."
- **Deliberate vertical space.** Title pages and illustration/photo pages are
  individually designed, with the amount of whitespace chosen by hand.

### Chapter openings (print)

- Every chapter **begins on a recto**.
- Chapter title: **left-aligned**, Arsenal **bold**, 18 pt, red `#e46340`. Left alignment
  echoes the cover and places the title near the gutter (centre of the open spread).
- Title sits **high** on the page (~6 mm below the text-block top), with a ~13 mm gap to the
  first stanza. **No running header** on the opening page.
- **Page breaks are placed by hand** (e.g. «Пролог» page 1 ends on «Вони — як люди і їхні
  оселі.»). **Stanzas never split across a page** — each strophe is an unbreakable block.

### Front matter & back matter (print)

Front matter (half-title, full title, colophon, foreword, acknowledgments, «Зречення»,
second title) and **back matter** (endnotes, table of contents, calligraphy) share one
set of rules, distinct from the body:

- **Font:** 10 pt — 1 pt smaller than the 11 pt body, so each text section fits a single page.
- **Margins:** inner **19** (gutter matched to the body) / outer **18** / top **14** /
  bottom **25** mm — tighter than the body; text begins high.
- **Section titles:** **centered**, Arsenal bold **14 pt** red — smaller than chapter titles —
  sitting at the top with a tight ~3.5 mm gap to the text. No running header in front matter.
- **Prose:** justified + hyphenated, paragraph spacing **1.2em**.
- **Half-title:** title only, serif (Cormorant Garamond) ~20 pt, **one line, top-aligned**.
- **Colophon:** centered, designed — the book title kept readable (11 pt bold), everything
  else **7 pt** with empty-line gaps between logical blocks.
- **Signature / credit** (end of a poem): Arsenal italic **7.5 pt** grey, **centered**, kept as
  one unbreakable block close to the verse, with an empty line before the year.

### Text alignment & hyphenation

- **Verse:** ragged-left, **no** justification. Line breaks are meaningful and set by hand
  (NBSP before em-dash, `ʼ` apostrophe — see TYPOGRAPHY.md).
- **Prose** (photo descriptions, foreword, acknowledgments, endnotes): **justified with
  automatic hyphenation** (Ukrainian patterns) to keep word spacing even.
- **Global rule:** runs of Latin-script text (foreign names — Garchen Buddhist Institute,
  Hōjōki, Matthew Stavros…) are set in **italic** automatically.

### Photo spreads (print)

- **Background:** light grey `#e8e6dc`, full page, on every photo page. **No** running header,
  **no** printed folio (the folio keeps counting internally).
- **Uniform photo box:** every photo is placed in one identical box — **85 × 113 mm,
  `fit: cover`** — vertically centred, shifted toward the gutter (outer margin > inner), with
  a safe **14 mm** inner margin. The recto photo sits in the **same place on every spread**;
  the verso photo is its mirror. (3 photos are portrait; retreat-hut is landscape, so the
  uniform box crops it to a centre slice — accepted for consistency.)
- **Single-photo spread** (retreat house; Amitābha): verso = description, recto = image.
  Description upright, justified + hyphenated, vertically centred; name «…» bold red 12.5 pt,
  right-aligned (toward the gutter).
- **Diptych** (back matter — clouds + monks): both pages images, **equal box, mirror-symmetric**,
  no text; sized by equal height so top and bottom edges align.
