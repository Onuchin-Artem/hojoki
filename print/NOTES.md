# Print pipeline — implementation notes & resume guide

Working log for the Typst PDF. Authoritative *design* decisions live in
[`../STYLE.md`](../STYLE.md) and [`STRUCTURE.md`](STRUCTURE.md); this file records the
*implementation* state, exact values, toolchain, and what's left to do.

## Toolchain

- **Typst 0.14.2** (`brew install typst`).
- Build: `make -C print` → `build/hojoki.pdf` (uses `--font-path ../assets/fonts/print`).
- Page previews: `typst compile --font-path assets/fonts/print --ppi 200 print/main.typ "build/preview-{p}.png"`.
- Live preview while tuning: `make -C print watch`.

## Fonts

- **Body:** Arsenal (free, OFL) — Regular/Bold/Italic/BoldItalic. Covers Ukrainian Cyrillic
  with true italics; also on Canva. (Replaced the original commercial idea, Garet.)
- **Titles:** Cormorant Garamond (free, OFL) — has Cyrillic. Currently the **variable** file
  (Typst warns variable fonts aren't fully supported and renders one default weight).
  **TODO:** drop in **static** Cormorant Garamond weights for deliberate title weight.
- Font files live in `assets/fonts/print/` — **gitignored**, so not in the repo. To set up a
  fresh checkout, fetch the TTFs from Google Fonts (`google/fonts` repo: `ofl/arsenal`,
  `ofl/cormorantgaramond`) into that folder.

## Layout values (locked) — see STYLE.md for rationale

- Trim **B6 125 × 176 mm**. Margins **inner 19 / outer 26 / top 32 / bottom 40 mm**
  (Van de Graaf canon, gutter-adjusted). `header-ascent: 22mm`, `footer-descent: 20mm`.
- Body: Arsenal 11.5 pt, `leading: 0.9em`, strophe `spacing: 2em`, ragged-left.
- Running header: recto only, chapter title, Arsenal italic 9 pt red, centered.
- Folio: both sides, Arsenal 8.5 pt black, centered, trailing dot.
- Chapter: opens recto, title left-aligned bold red 18 pt, `v(6mm)` above / `v(13mm)` below.
- Strophes are unbreakable blocks; **page breaks placed by hand** in the source.
- Prose justified + hyphenated (`lang: "uk"`, `hyphenate: true`); verse ragged.
- Global show rule: Latin-script runs → italic.
- Photo box **85 × 113 mm, `fit: cover`**, vertically centered, gutter-biased, 14 mm inner;
  background `#e8e6dc`; no header/folio. Recto photo identical on every spread; verso mirrors.

## File map

- `main.typ` — entry point. **In progress:** currently only «Пролог» (validates the engine).
- `template/typography.typ` — colors, fonts, body defaults, unbreakable-strophe rule,
  Latin-italic rule.
- `template/layout.typ` — page engine: geometry, recto-only running header + folio with
  per-page suppression (`_no-head` / `_no-folio` state), `book()` wrapper, `chapter()`.
- `template/components.typ` — `credit()` so far. **TODO:** `prose()`, `photo-spread()`,
  `diptych()`, title pages.
- `_preview-photos.typ` — reference preview of all three photo spreads (the validated photo
  system). To be folded into `components.typ`.

## Done

- Engine: page geometry, recto/verso folio, recto-only running header, per-page suppression.
- Chapter opening (recto start, high left title, hand page breaks, unbreakable strophes).
- Body verse rendering validated on «Пролог».
- Text policy: prose justified+hyphenated, verse ragged, Latin-italic global rule.
- Photo system validated (uniform box, gutter bias, single spreads + symmetric diptych).

## TODO (resume here)

1. Bake `prose()`, `photo-spread(name, desc, img)`, `diptych(left, right)`, and the title
   pages into `template/components.typ` (photo pages = two B6 pages, grey fill, header/folio
   suppressed via the layout state helpers).
2. Front matter: half-title, full title page, colophon (from `source/colophon.md`), foreword,
   acknowledgments, poem «Зречення» — none carry a running header.
3. Port the full body from `source/hojoki.md` with **manual** line breaks (NBSP before em-dash,
   `ʼ` apostrophe) and **manual** page breaks; no strophe split across pages.
4. Place photo spreads: retreat house (front matter), Amitābha (before «Моя маленька хатинка»),
   back-matter diptych (clouds + monks). Captions from `source/captions.md`.
5. Closing «…тиша» page with the author colophon-signature (italic, smaller).
6. Endnotes from `source/footnotes.md` — **each endnote begins on a new page**; then table of
   contents and the ensō calligraphy page.
7. Swap in **static** Cormorant Garamond weights; set the title-page weight deliberately.
8. Build `build/hojoki.pdf` and walk through page by page.
