// Reusable content components for the print PDF.

#import "typography.typ": *

// Grey italic credit / signature — after a verse or at the end of a poem.
// Smaller than body, centered (STYLE.md).
#let credit(body) = {
  set text(font: sans, size: 7.5pt, style: "italic", fill: grey)
  align(center, body)
}

// Justified prose with Ukrainian hyphenation (foreword, descriptions, endnotes).
// Prose paragraphs use tighter leading/spacing than verse and may break across pages.
#let prose(body) = {
  set par(justify: true, leading: 0.72em, spacing: 1.2em)
  set text(hyphenate: true)
  body
}

// Verse: each strophe is an unbreakable block (never split across a page).
#let verse(body) = {
  show par: it => block(it, breakable: false)
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
    set par(leading: 0.95em, spacing: 1.3em, justify: true)
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
#let endnote-ref(n) = super(text(fill: red, weight: "medium")[#str(n)])

// One endnote (back matter): bold red number, then the note as justified prose.
#let endnote(n, body) = {
  text(font: sans, weight: "bold", size: 12pt, fill: red)[#(str(n) + ".")]
  v(2mm)
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
