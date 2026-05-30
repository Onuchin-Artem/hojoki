// Page engine for the print PDF — geometry, recto/verso headers, folio.
// See print/STRUCTURE.md for the rules this implements.
//
// Headers/folios are driven by QUERYING chapter markers (not live state), because
// state read inside a header resolves as of the previous page boundary — which
// makes chapter-opening pages show the wrong/previous title.

#import "typography.typ": *

#let book-title = "Думки у ретрітній хатинці"
#let _toc = state("toc", ())  // (title, page) for the table of contents

#let book(body) = {
  set page(
    width: 125mm,
    height: 176mm,
    margin: (inside: 19mm, outside: 26mm, top: 32mm, bottom: 40mm),
    header-ascent: 22mm,
    footer-descent: 20mm,
    header: context {
      let pg = here().page()
      let prior = query(<chap>).filter(m => m.location().page() <= pg)
      if prior.len() == 0 { return }                      // front matter — no header
      if prior.last().location().page() == pg { return }  // chapter-opening page — no header
      if not calc.odd(pg) { return }                      // running header on recto only
      set text(font: sans, size: 9pt, style: "italic", fill: red)
      align(center)[#prior.last().value]
    },
    footer: context {
      let pg = here().page()
      let prior = query(<chap>).filter(m => m.location().page() <= pg)
      if prior.len() == 0 { return }                      // front matter — no folio
      set text(font: sans, size: 8.5pt, fill: black)
      align(center)[#(str(counter(page).get().first()) + ".")]  // logical folio (restarts at 1)
    },
  )
  show: body-rules
  body
}

// --- chapter ---------------------------------------------------------------
// Opens on a recto; title left-aligned, sitting high; no running header on the
// opening page. `restart: true` on the first chapter restarts the folio at 1.
#let chapter(title, restart: false) = {
  pagebreak(to: "odd", weak: true)
  if restart { counter(page).update(1) }
  [#metadata(title)<chap>]                       // marker for header + opening detection
  context {
    let p = counter(page).get().first()
    _toc.update(t => t + ((title: title, page: p),))
  }
  v(6mm)
  let ta = sys.inputs.at("title-align", default: "left")
  align(if ta == "center" { center } else { left },
        text(font: sans, weight: "bold", size: 18pt, fill: red, title))
  v(13mm)
}
