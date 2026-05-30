// Reusable content components for the print PDF.

#import "typography.typ": *

// Grey italic credit / signature — after a verse or at the end of a poem.
// Smaller than body, centered (STYLE.md).
#let credit(body) = {
  set text(font: sans, size: 7.5pt, style: "italic", fill: grey)
  block(breakable: false, align(center, body))
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

// Front-matter section heading — same look as a chapter title, but it does NOT
// turn on the running header or force a recto (the caller controls the page).
// Front-matter section heading — centered, smaller than a chapter title, sits
// high with a tight gap to the text (distinct from chapter openings).
#let fm-heading(title) = {
  align(center, text(font: sans, weight: "bold", size: 14pt, fill: red, title))
  v(3.5mm)
}
