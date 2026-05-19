# Hojoki — Project Vision

## The Book

**"Думки у Ретрітній Хатинці"** is a Ukrainian translation of *Hōjōki* (方丈記) — a 12th-century Japanese prose poem by Kamo no Chōmei. The text meditates on impermanence, disaster, and the search for stillness through voluntary simplicity. This translation by Artem Onuchin renders the text from Matthew Stavros's English translation into contemporary Ukrainian, accompanied by a translator's preface and original poetry.

The book is intimate in scale and contemplative in tone. Its design should reflect that: unhurried, spacious, typographically precise.

---

## Publication Formats

The project produces three outputs from a single edited source:

| Format | Tool | Purpose |
|--------|------|---------|
| HTML | Pandoc | Web reading — clean, readable on any screen |
| EPUB | Pandoc | E-reader devices and apps |
| PDF | Typst | Printed book — fully designed layout |

The HTML and EPUB share a pipeline and a common CSS foundation. The PDF is a separate, design-intensive pipeline in Typst that allows full typographic control suited to a printed poetry book.

---

## Two Pipelines

### Web & E-book (Pandoc)
Source Markdown is converted by Pandoc using custom HTML templates and CSS. The web version is a standalone HTML file suitable for reading in a browser. The EPUB version follows the same stylesheet with minor adaptations for e-reader constraints.

### Print (Typst)
The PDF is composed in Typst — a modern typesetting system that compiles to PDF directly. Typst source files are plain text stored in Git. The print layout handles book-specific requirements:
- All chapters begin on a recto (right-hand, odd-numbered) page
- Chapter opening pages have no running header
- Recto pages carry the chapter title in the running header
- Verso pages carry the book title in the running header
- Poetry stanzas have precise vertical spacing
- Endnotes rather than footnotes
- Custom fonts and ornamental elements

---

## Pre-Production Phases

Before any layout work begins, the source text must go through editorial and typographic preparation. This work is shared between both pipelines.

### Phase 1 — Editing
- Proofread for spelling and grammatical mistakes
- Review punctuation throughout
- Check consistency of proper names and transliterations

### Phase 2 — Endnotes
- Identify all passages that benefit from annotation: historical references, Buddhist terminology, place names, poetic allusions
- Compose endnote text for each identified passage
- Number and integrate endnote markers into the source

### Phase 3 — Photo & Illustration Preparation
- Scope TBD: may include author portrait, historical imagery, maps, or decorative elements
- Originals stored in `assets/images/originals/` (high-res, not committed if oversized)
- Processed exports in `assets/images/processed/` sized per format (screen vs. print resolution)

### Phase 4 — Typography Pass (shared)
This pass cleans and prepares the Markdown source so that both pipelines receive correct typographic input:
- **Dashes**: replace hyphens used as dashes with proper em-dashes (—) or en-dashes (–)
- **Quotation marks**: replace straight quotes with typographic curly quotes (" " ' ')
- **Non-breaking spaces**: insert non-breaking spaces where line breaks would be semantically wrong (e.g., before em-dash, after single-letter prepositions)
- **Headers**: convert ALL CAPS headings to title case or sentence case with proper formatting
- **Line breaks in poetry**: ensure consistent stanza break conventions throughout

---

## Assets

### Fonts
Custom typefaces are stored in `assets/fonts/`. Each font family includes all necessary weights and styles. Web fonts (WOFF2) for HTML/EPUB and desktop fonts (OTF/TTF) for Typst are kept in separate subdirectories.

### Images
All source imagery lives in `assets/images/originals/`. Processed versions exported for each format target live in `assets/images/processed/`. Large original files may be tracked via Git LFS or kept outside the repository.

### Cover
Cover artwork and any cover layout source files live in `assets/cover/`.

---

## Directory Structure

```
hojoki/
│
├── VISION.md                        ← this document
├── LICENSE                          ← CC BY-NC 4.0
├── README.md
├── Makefile                         ← top-level: build all / clean
│
├── source/
│   ├── raw/
│   │   └── hojoki.source.txt        ← original import from Google Docs
│   └── hojoki.md                    ← clean, production-ready Markdown
│
├── assets/
│   ├── fonts/
│   │   ├── web/                     ← WOFF2 for HTML and EPUB
│   │   └── print/                   ← OTF/TTF for Typst
│   ├── images/
│   │   ├── originals/               ← high-res source files
│   │   └── processed/               ← sized exports per format
│   └── cover/                       ← cover art and layout source
│
├── web/                             ← HTML pipeline (Pandoc)
│   ├── Makefile
│   ├── template.html                ← Pandoc HTML5 template
│   └── css/
│       └── style.css
│
├── epub/                            ← EPUB pipeline (Pandoc)
│   ├── Makefile
│   ├── metadata.yaml
│   └── css/
│       └── style.css
│
├── print/                           ← Print PDF pipeline (Typst)
│   ├── Makefile
│   ├── main.typ                     ← entry point
│   └── template/
│       ├── layout.typ               ← page geometry, headers, footers
│       ├── typography.typ           ← fonts, sizes, spacing
│       └── components.typ           ← chapter headings, stanzas, endnotes
│
└── build/                           ← generated outputs (gitignored)
    ├── hojoki.html
    ├── hojoki.epub
    └── hojoki.pdf
```

---

## Design Principles

- **Restraint over decoration** — the text carries the weight; design should not compete with it
- **Consistent whitespace** — generous margins and leading suited to meditative reading
- **Typography as meaning** — font and spacing choices should evoke the quietness of the subject matter
- **Single source of truth** — all content lives in `source/hojoki.md`; both pipelines read from it
