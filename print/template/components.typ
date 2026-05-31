// Reusable content components for the print PDF.

#import "typography.typ": *

// Grey italic credit / signature — after a verse or at the end of a poem.
// Smaller than body, centered (STYLE.md).
#let credit(body) = {
  set text(font: sans, size: 7.5pt, style: "italic", fill: grey)
  align(center, body)
}

// Prose: justified with hyphenation + optimized line-breaking. Typst leaves the last
// (short) line of each paragraph flush-left automatically, so short lines aren't stretched.
#let prose(body) = {
  set par(justify: true, linebreaks: "optimized", leading: 0.72em, spacing: 1.2em)
  set text(hyphenate: true)
  // never split a paragraph across pages; <live> tags every page it lands on as
  // content (so continuation pages also get a folio + running header).
  show par: it => block(breakable: false)[#metadata(none)<live>#it]
  body
}

// Verse: each strophe is an unbreakable block (never split across a page).
// The <live> marker (inside the block) tags the strophe's page as content, so
// the running header/folio appears there but not on parity-filler blanks.
#let verse(body) = {
  show par: it => block(breakable: false)[#metadata(none)<live>#it]
  body
}

// ── Photo pages (grey background, no header/folio) ──────────────────────────
// A single photo page; `side` = "recto" (image toward the left/gutter) or
// "verso" (toward the right/gutter). Uniform box 85×113 mm, fit cover.
#let photo-page(img, side: "recto") = {
  let al  = if side == "verso" { right } else { left }
  let ins = if side == "verso" { (right: 14mm) } else { (left: 14mm) }
  page(fill: photo-bg, margin: 0pt, header: none, footer: none,
    block(width: 100%, height: 100%, inset: ins,
      align(al + horizon, image(img, width: 85mm, height: 113mm, fit: "cover"))))
}

// Description page (verso): bold red right-aligned name + justified body, centered.
#let photo-desc(name, body) = page(fill: photo-bg, margin: 0pt, header: none, footer: none,
  block(width: 100%, height: 100%, inset: (left: 26mm, right: 14mm, y: 24mm), {
    set text(font: sans, size: 10pt, fill: ink, hyphenate: true)
    set par(leading: 0.95em, spacing: 1.3em, justify: true, linebreaks: "optimized")
    v(1fr)
    align(right, text(weight: "bold", size: 12.5pt, fill: red)[#name])
    v(1.4em)
    body
    v(1fr)
  }))

// Single-photo spread: description (verso) + image (recto).
#let photo-spread(name, img, body) = {
  photo-desc(name, body)
  photo-page(img, side: "recto")
}

// Diptych: two images, mirror-symmetric (verso + recto), no text.
#let diptych(left-img, right-img) = {
  photo-page(left-img, side: "verso")
  photo-page(right-img, side: "recto")
}

// ── Endnotes ────────────────────────────────────────────────────────────────
// In-body reference: small red superscript number.
#let endnote-ref(n) = super(text(fill: grey, weight: "medium")[#str(n)])

// The quoted lemma at the head of an endnote — a verse excerpt from the poem.
// Grey italic, ragged (line breaks preserved by the source).
#let fn-quote(body) = {
  set text(style: "italic", fill: grey)
  set par(leading: 0.9em, justify: false)
  body
}

// One endnote (back matter): bold red number, the quoted lemma as a grey verse,
// then the note as justified prose.
#let endnote(n, lemma, body) = {
  [#metadata(none)<live>]                          // tag the endnote's page as content
  [#metadata(n)<note>]                             // note number, for the running header
  set text(size: 9pt)                              // footnotes 1pt smaller so more fit one page
  text(font: sans, weight: "bold", size: 12pt, fill: red)[#(str(n) + ".")]
  v(1mm)
  fn-quote(lemma)
  v(0.8em)
  // discourage hyphenation (fewer lone fragments) + short last lines, per front-matter rules
  set text(costs: (hyphenation: 400%, runt: 2000%))
  prose(body)
}

// Front-matter section heading — same look as a chapter title, but it does NOT
// turn on the running header or force a recto (the caller controls the page).
// Front-matter section heading — centered, smaller than a chapter title, sits
// high with a tight gap to the text (distinct from chapter openings).
#let fm-heading(title) = {
  align(center, text(font: sans, weight: "bold", size: 14pt, fill: red, title))
  v(3.5mm)
}

// Back-matter section heading — like a chapter title (left, bold red 18 pt) but
// without the chapter's deep top/below drop; sits at the top of the text block.
#let section-heading(title) = {
  align(left, text(font: sans, weight: "bold", size: 18pt, fill: red, title))
  v(8mm)
}
