// Typographic tokens for the print PDF — see STYLE.md

// Colors
#let ink       = rgb("#252120")  // primary text
#let red       = rgb("#e46340")  // chapter + running header
#let grey      = rgb("#646161")  // credit line
#let photo-bg  = rgb("#e8e6dc")  // photo-page background

// Fonts
#let sans  = "Arsenal"             // body — verses and prose
#let serif = "Cormorant Garamond"  // book title on title pages

// Body text defaults
#let body-rules(doc) = {
  set text(font: sans, size: 11pt, fill: ink, lang: "uk")
  set par(leading: 0.9em, spacing: 2em, justify: false)
  // global rule: Latin-script runs (foreign names) set in italic
  show regex("[A-Za-zÀ-ÿĀ-ſ]+(?:[ -][A-Za-zÀ-ÿĀ-ſ]+)*"): it => text(style: "italic", it)
  doc
}
