// Page engine for the print PDF — geometry, recto/verso headers, folio.
// See print/STRUCTURE.md for the rules this implements.

#import "typography.typ": *

#let book-title = "Думки у ретрітній хатинці"

// --- internal state --------------------------------------------------------
#let _chap     = state("chap", "")       // current chapter title (recto header)
#let _running  = state("running", false) // running header active? (off in front matter)
#let _no-head  = state("no-head", ())    // pages with no running header
#let _no-folio = state("no-folio", ())   // pages with no printed folio

// record the current page into a page-set state
#let _mark(st) = context {
  let p = here().page()
  st.update(s => if s.contains(p) { s } else { s + (p,) })
}

// --- document wrapper ------------------------------------------------------
#let book(body) = {
  set page(
    width: 125mm,
    height: 176mm,
    margin: (inside: 19mm, outside: 26mm, top: 32mm, bottom: 40mm),
    header-ascent: 22mm,
    footer-descent: 20mm,
    header: context {
      let p = here().page()
      if not _running.get() { return }
      if not calc.odd(p) { return }          // running header on recto only
      if _no-head.get().contains(p) { return }
      set text(font: sans, size: 9pt, style: "italic", fill: red)
      align(center)[#_chap.get()]
    },
    footer: context {
      let p = here().page()
      if not _running.get() { return }
      if _no-folio.get().contains(p) { return }
      set text(font: sans, size: 8.5pt, fill: black)
      align(center)[#(str(p) + ".")]
    },
  )
  show: body-rules
  body
}

// --- chapter ---------------------------------------------------------------
// Opens on a recto, 1/3 page of space above the title, 1/3 between title and
// text. No running header on the opening page. Running headers begin here.
#let chapter(title) = {
  pagebreak(to: "odd", weak: true)
  _running.update(true)
  _chap.update(title)
  _mark(_no-head)
  v(6mm)
  let ta = sys.inputs.at("title-align", default: "left")
  align(if ta == "center" { center } else { left },
        text(font: sans, weight: "bold", size: 18pt, fill: red, title))
  v(13mm)
}
