// Typographic tokens for the print PDF — see STYLE.md

// Colors
#let ink       = rgb("#252120")  // primary text
#let red       = rgb("#e46340")  // chapter + running header
#let grey      = rgb("#646161")  // credit line
#let photo-bg  = rgb("#e8e6dc")  // photo-page background

// Fonts
#let sans  = "Arsenal"             // body — verses and prose
#let serif = "Cormorant Garamond"  // book title on title pages

// Body text defaults + Ukrainian micro-typography (applies book-wide).
#let body-rules(doc) = {
  set text(font: sans, size: 11pt, fill: ink, lang: "uk")
  set par(leading: 0.9em, spacing: 2em, justify: false)
  // line-breaking costs: strongly discourage a short last line / lone hyphenated
  // fragment (runt), reduce hyphenation, avoid widows/orphans.
  set text(costs: (hyphenation: 100%, runt: 1000%, widow: 500%, orphan: 500%))

  // Foreign (Latin-script) names → italic.
  show regex("[A-Za-zÀ-ÿĀ-ſ]+(?:[ -][A-Za-zÀ-ÿĀ-ſ]+)*"): it => text(style: "italic", it)

  // Ukrainian typography: short prepositions/conjunctions must not be left at a
  // line end — glue them to the next word with a non-breaking space.
  show regex(" (?:[вузіаійоВУЗІАЙО]|та|до|на|по|за|із|зі|що|як|бо|чи|не|Та|До|На|По|За|Із|Зі|Що|Як|Бо|Чи|Не) "): it => it.text.slice(0, it.text.len() - 1) + "\u{00A0}"
  // NBSP before an em-dash (so it never starts a line).
  show regex(" —"): it => "\u{00A0}—"
  // keep the author's name together (no break inside «Камо но Тьомей/Тьомея»).
  show regex("Камо но Тьоме[йя]"): it => it.text.replace(" ", "\u{00A0}")

  doc
}
