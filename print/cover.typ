// Hardcover cover. Two layouts via `--input mode=`:
//   pages  (default) — 3 component pages: back, spine, front (each with full bleed)
//   spread           — one back·spine·front spread
//
// Front (front-cover.jpg) is finished artwork; back (back-cover.jpg) is the empty
// cream+brush background — the back text is set here in Typst.
//
// Inputs: --input spine=0.56in  --input bleed=0.8in  --input hinge=0.2in
//         --input coverw=125mm  --input coverh=176mm  --input front=…  --input back=…

#import "template/typography.typ": *

#let mode   = sys.inputs.at("mode", default: "pages")
#let spine  = eval(sys.inputs.at("spine",  default: "0.56in"))
#let cbleed = eval(sys.inputs.at("bleed",  default: "0.8in"))
#let hinge  = eval(sys.inputs.at("hinge",  default: "0.2in"))
#let coverw = eval(sys.inputs.at("coverw", default: "125mm"))
#let coverh = eval(sys.inputs.at("coverh", default: "176mm"))
#let front  = sys.inputs.at("front", default: "/assets/cover/front-cover.jpg")
#let back   = sys.inputs.at("back",  default: "/assets/cover/back-cover.jpg")

#let cream  = rgb("#f8f5ec")   // cover background; fills wrap/bleed
#let band   = rgb("#e9e6dd")   // beige band — sampled from the cover brush sweep
#let band-top = 0.345          // band (with feathered top) sits a bit higher; solid part ~42%
#let band-bot = eval(sys.inputs.at("bandbot", default: "1.020"))   // bottom fade finish (fraction of trim)

#set text(font: sans, fill: ink, lang: "uk")

// Spine brush — a strip cropped from the cover art's brush sweep, so the spine
// shows the SAME textured brush as the covers (a flat colour band looked pasted-on
// and didn't match). Fills the spine region; connects front↔spine↔back.
#let band-h = (band-bot - band-top) * coverh
// straight brush band on the spine, level with the cover brush — a horizontal
// slice of the cover's own brush (same image → matches texture & colour), with
// straight edges that survive spine/hinge trimming.
#let draw-band(x, w) = place(top + left, dx: x, dy: cbleed + band-top * coverh,
  image("/assets/cover/spine-band.png", width: w, height: band-h, fit: "stretch"))

// Back-cover text (set over the empty background), sized to one trim panel.
#let back-text = box(width: coverw, height: coverh, inset: (x: 19mm, top: 24mm, bottom: 13mm), {
  show regex(" —"): it => "\u{00A0}—"
  // glue short prepositions/conjunctions to the next word (e.g. «з природою»)
  show regex(" (?:[вузіаійоВУЗІАЙО]|та|до|на|по|за|із|зі|що|як|бо|чи|не|про|при|без|від|над|під|для|або|але|Та|До|На|По|За|Із|Зі|Що|Як|Бо|Чи|Не|Про|При|Без|Від|Над|Під|Для|Або|Але) "): it => it.text.slice(0, it.text.len() - 1) + "\u{00A0}"
  {
    set par(justify: true, linebreaks: "optimized", leading: 0.8em, spacing: 1.2em)
    set text(size: 10.5pt, hyphenate: false)   // blurb reads cleaner unhyphenated
    [#text(fill: red, weight: "bold")[Класичний твір японської літератури,] написаний 1212 року.
     Монах-самітник згадує страждання, лиха і втрати, які випали на його власне
     життя. Попри це він знаходить спокій у самотньому житті, опорі на себе,
     єднанні з природою і зосередженні на духовній практиці.]
  }
  v(2.4em)
  {
    set par(justify: false, leading: 0.9em, spacing: 1.5em)
    set text(size: 9.5pt, fill: grey, style: "italic")
    [Доми шістнадцяти панів і безліч інших згоріли. \
     Це — третя частина столиці. \
     Декілька тисяч чоловіків і жінок \
     загинули. \
     Безліч коней та інших тварин \
     померли.

     Будь-що ми робимо в нашому житті \
     не має жодного сенсу. \
     Проте тратити скарб і багатство на те, \
     щоб збудувати будинки \
     в цій небезпечній столиці — \
     це особлива дурниця.]
  }
  v(1fr)
  block(width: 100%, height: 4.2mm, {
    place(center + horizon, text(size: 8pt, fill: grey)[© Артем Онучін, 2026])
    place(right + horizon, image("/assets/images/processed/by-nc.png", height: 4.2mm))
  })
})

// title starts near the top of the spine (~11% down, per the marked line)
#let spine-title = box(width: spine, height: coverh, inset: (top: 19mm), align(center + top,
  rotate(90deg, reflow: true,
    text(font: serif, weight: 300, size: 13pt)[Думки у ретрітній хатинці])))

#if mode == "spread" {
  // ── One back·spine·front spread ─────────────────────────────────────────────
  let spread-w = 2 * coverw + 2 * hinge + spine + 2 * cbleed
  let spread-h = coverh + 2 * cbleed
  let spine-x = cbleed + coverw + hinge
  let front-x = cbleed + coverw + 2 * hinge + spine
  set page(width: spread-w, height: spread-h, margin: 0pt, fill: cream)
  if back != "" { place(top + left, dx: cbleed, dy: cbleed, image(back, width: coverw, height: coverh)) }
  if front != "" { place(top + left, dx: front-x, dy: cbleed, image(front, width: coverw, height: coverh)) }
  // straight brush band across the hinge+spine+hinge gap — connects the two covers
  draw-band(cbleed + coverw, 2 * hinge + spine)
  place(top + left, dx: spine-x, dy: cbleed, spine-title)
  place(top + left, dx: cbleed, dy: cbleed, back-text)
} else {
  // ── 3 component pages: front, spine, back (each full-bleed) ──────────────────
  let pw = coverw + 2 * cbleed
  let ph = coverh + 2 * cbleed
  // front
  page(width: pw, height: ph, margin: 0pt, fill: cream, {
    if front != "" { place(top + left, dx: cbleed, dy: cbleed, image(front, width: coverw, height: coverh)) }
  })
  // spine — straight brush band level with the covers, title on top
  page(width: spine + 2 * cbleed, height: ph, margin: 0pt, fill: cream, {
    draw-band(0mm, spine + 2 * cbleed)
    place(top + left, dx: cbleed, dy: cbleed, spine-title)
  })
  // back
  page(width: pw, height: ph, margin: 0pt, fill: cream, {
    if back != "" { place(top + left, dx: cbleed, dy: cbleed, image(back, width: coverw, height: coverh)) }
    place(top + left, dx: cbleed, dy: cbleed, back-text)
  })
}
