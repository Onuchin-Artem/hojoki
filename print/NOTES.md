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
- Body: Arsenal **11 pt**, `leading: 0.9em`, strophe `spacing: 2em`, ragged-left.
- Front & back matter: **10 pt** (1 pt smaller, so each section fits one page); margins inner 19 /
  outer 18 / top 14 / bottom 25; section titles **centered**, bold red **14 pt**, tight 3.5 mm gap,
  text begins high; prose `spacing: 1.2em`. **Back matter uses the same rules as front matter.**
- Running header: recto only, chapter title, Arsenal italic 9 pt red, centered.
- Folio: both sides, Arsenal 8.5 pt black, centered, trailing dot.
- Chapter: opens recto, title left-aligned bold red 18 pt, `v(6mm)` above / `v(13mm)` below.
- Strophes are unbreakable blocks; **page breaks placed by hand** in the source.
- Prose justified + hyphenated (`lang: "uk"`, `hyphenate: true`); verse ragged.
- Global show rule: Latin-script runs → italic.
- Photo box **85 × 113 mm, `fit: cover`**, vertically centered, gutter-biased, 14 mm inner;
  background `#e8e6dc`; no header/folio. Recto photo identical on every spread; verso mirrors.

## File map

- `main.typ` — entry point: front matter (inline) → `#include "body.typ"` → back matter
  (diptych, `#include "endnotes.typ"`, «Зміст» ToC from `_toc` state, ensō).
- `template/typography.typ` — colors, fonts, body defaults, Latin-italic global rule.
- `template/layout.typ` — page engine. **Headers/folio are query-driven** (`<chap>` metadata
  markers), NOT live state — state read in a header resolves a page late and showed the wrong
  chapter title on openings. `chapter(title, restart:false)`; `restart:true` on the first
  chapter restarts the folio at 1. `_toc` state feeds the table of contents.
- `template/components.typ` — `prose()`, `verse()` (unbreakable strophes), `fm-heading()`,
  `credit()` (signature), `photo-page()` / `photo-desc()` / `photo-spread()` / `diptych()`,
  `endnote-ref()` (superscript) / `endnote(n, body)`.
- `body.typ`, `endnotes.typ` — **generated** (do not hand-edit). Regenerate with the tools below.
- `tools/build_body.py` — `source/hojoki.md` → `body.typ` (chapters+verse, NBSP, `[^x]` →
  `#endnote-ref(n)`, Amitābha spread before «Моя маленька хатинка», closing signature).
- `tools/build_endnotes.py` — `source/footnotes.md` → `endnotes.typ` (numbered, each on its own
  page; **/Джерела** list). Numbering follows body first-appearance order.

Rebuild: `python3 print/tools/build_body.py && python3 print/tools/build_endnotes.py && make -C print`

## Done

- **Whole book renders** → `build/hojoki.pdf` (~114 pp): front matter, all 15 chapters,
  Amitābha spread, diptych, endnotes, «Зміст», ensō.
- Query-driven recto running header (correct chapter title; suppressed on openings/verso/front matter).
- Folio restarts at 1 on «Пролог» (footer shows `counter(page)`, not the physical page).
- Endnotes numbered, italic lemma + justified prose, each on a new page; superscript refs in body.
- Photo system (uniform box, gutter bias, single spreads + symmetric diptych) in components.

## TODO (resume here) — tuning pass

1. **Closing signature** lands on its own recto instead of the foot of the «тиша» verso —
   Typst won't seat the block after «тиша» in the tight bottom margin. Needs a page-bottom
   placement that doesn't overflow (the obvious `place(bottom)` anchors to the flow line).
2. **Blank pages show a folio** (auto-inserted recto/verso blanks). Suppress folio/header on blanks.
3. **Hand-placed verse page breaks** — currently auto-flow; place breaks deliberately per the
   user's wishes (no stranded lines, logical stanza boundaries).
4. Front-matter / back-matter polish; revisit per-section as we go.
5. Swap in **static** Cormorant Garamond weights; set the title-page weight deliberately.
