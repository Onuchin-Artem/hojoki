// Page engine for the print PDF — geometry, recto/verso headers, folio.
// See print/STRUCTURE.md for the rules this implements.
//
// Headers/folios are driven by QUERYING chapter markers (not live state), because
// state read inside a header resolves as of the previous page boundary — which
// makes chapter-opening pages show the wrong/previous title.

#import "typography.typ": *

#let book-title = "Думки у ретрітній хатинці"
#let _toc = state("toc", ())  // (title, page) for the table of contents

// Marks a page as carrying real content. Placed in every verse strophe and
// endnote. Pages with no <live> and no <chap> are parity-filler blanks — the
// header/footer print nothing on them (blanks count toward pagination but show
// no folio, as in conventional book typesetting).
#let live-mark = [#metadata(none)<live>]
#let _has(label, pg) = query(label).filter(m => m.location().page() == pg).len() > 0

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
      let section = prior.last()
      if section.location().page() == pg { return }       // section-opening page — no header
      if not _has(<live>, pg) { return }                  // blank filler — no header
      set text(font: sans, size: 9pt, style: "italic", fill: red)
      if section.value == "Примітки" {
        // footnotes (rule differs from chapters): header on every content page —
        // «Примітки» where a note begins, «Примітки — N» where note N continues.
        let notes = query(<note>).filter(m => m.location().page() <= pg)
        let cont = notes.len() > 0 and notes.last().location().page() < pg
        align(center)[#(if cont { "Примітки\u{00A0}— " + str(notes.last().value) } else { "Примітки" })]
      } else {
        // body chapters: chapter title, recto only
        if not calc.odd(pg) { return }
        align(center)[#section.value]
      }
    },
    footer: context {
      let pg = here().page()
      let prior = query(<chap>).filter(m => m.location().page() <= pg)
      if prior.len() == 0 { return }                      // front matter — no folio
      if prior.last().value == "Зміст" { return }         // contents page — no folio
      // print a folio only on pages that carry content (skip parity-filler blanks)
      if not (_has(<live>, pg) or prior.last().location().page() == pg) { return }
      set text(font: sans, size: 8.5pt, fill: grey)
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
  pagebreak(to: "odd", weak: true)                 // open on a recto (filler blank carries no folio)
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
