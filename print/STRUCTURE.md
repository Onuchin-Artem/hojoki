# Book Structure Specification

This document defines the page-by-page layout of the book. Implementation tooling (LaTeX, Typst, InDesign, etc.) is out of scope here — this is the structural blueprint only.

## Conventions

- **R** = recto (right-hand page)
- **V** = verso (left-hand page)
- **Spread** = two facing pages visible when the book is open. A spread is the V of one leaf paired with the R of the next leaf.

**General rule:** every section begins on a recto (R) page.

## Front Matter

| Side | Content |
|------|---------|
| R | Title only — no author, no translator. Pure typography. |
| V | Blank |
| R | Full title page — author, title, translator. Typography-driven design (no graphics). |
| V | Colophon / license / copyright |
| R | Foreword |
| V | Acknowledgments |
| R | Poem "Зречення" (Renunciation) |
| V | Blank |
| R | Second title page — author + title only |
| V | Description: context for the translation choice "ретрітна хатинка"; the modern hōjō concept |
| R | Photograph of a modern retreat house |
| V | Blank |

## Main Body

**Chapter rules:**

- Every chapter begins on R.
- A 1/3 page vertical gap separates the chapter title from the start of the chapter text.
- A red running header (the **chapter title**) appears on **recto pages only**; verso pages carry no running header (the book title is not repeated). The folio appears on both.
- The running header is **omitted** on: blank pages, chapter title (opening) pages, and photo spreads.
- If a chapter ends on R, insert a blank V before the next chapter so the next chapter still opens on R.
- Page numbers continue across photo spreads but are **not printed** on them.

**Special insertion before the chapter "Моя маленька хатинка":**

| Side | Content |
|------|---------|
| V | Description: explanation of why Amitābha matters to the author |
| R | Photograph of Amitābha |

This is a photo spread — see "Photo Spread Rule" below.

**Last chapter — "ДОСВІТНЯ ТИША":**

The final chapter ends on V. The last word of the body text is **"тиша"** (silence). At the bottom of the same V page, set the author's colophon-signature in **italic, smaller font**:

> *Написано монахом Рен'іном у хатинці біля Тоями, приблизно в останній день третього місяця другого року епохи Кенр'яку.*

## Back Matter

| Side | Content |
|------|---------|
| R | Blank — intentional breathing space after "тиша" |
| V | Photograph of clouds — no caption |
| R | Photograph of monks — no caption |
| V | Blank |
| R | Endnotes (begin here; continue across following pages as needed). **Each endnote begins on a new page.** |
| R | Table of contents |
| V | Calligraphy "ocho" |

The clouds + monks pages form a diptych on a single spread — see "Diptych Rule" below.

## Layout Rules

### Photo Spread Rule

Every image is paired with its context on the **same spread**, so image and text are visible together when the book is open. Layout:

- **V (left)** = text / description — **upright** (not italic), smaller, **justified with hyphenation**, generous leading, vertically centred. The picture name is **bold, red, right-aligned** (toward the gutter).
- **R (right)** = image

Applies to:
1. Retreat house photo + description (front matter)
2. Amitābha photo + description (before "Моя маленька хатинка")

Typography on photo spreads:
- No running header
- No printed page numbers (numbering continues internally)
- Background tone uniform across all photo spreads: light grey **`#e8e6dc`**, full page.
- All photos share **one uniform box (85 × 113 mm, `fit: cover`)**, vertically centred, shifted toward the gutter (outer margin > inner; safe **14 mm** inner). The recto photo sits in the **same place on every spread**; the verso photo is its mirror. (3 photos are portrait, retreat-hut is landscape → the uniform box crops the landscape to a centre slice, accepted for consistency.)

### Diptych Rule

The clouds + monks pair in back matter follows the photo-spread principle (both pages on one spread) but with **no descriptive text** — both pages show only images. Clouds on V (left), monks on R (right). This is the only image-image spread in the book.

### Chapter Opening Rule

- Chapters always begin on R.
- The chapter title sits below 1/3 page of empty space at the top.
- No running header on chapter title pages.
- If the previous chapter ends on R, insert a blank V before the new chapter.
