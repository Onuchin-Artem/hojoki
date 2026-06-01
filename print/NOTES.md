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
- Global show rules (in `body-rules`): Latin-script runs → italic; **Ukrainian NBSP** —
  short prepositions/conjunctions (в, у, з, і, а, й, о, та, до, на, по, за, із, зі, що, як,
  бо, чи, не…) glued to the next word, and NBSP before em-dashes. Applies book-wide (prose
  + verse, front + back matter). Source `\u{00A0}` before em-dashes is still fine (no double).
- Line-break **costs** (`set text(costs:)`): hyphenation **100%** (normal — was 2000%, which
  killed hyphenation and made lines loose), runt 1000%, widow/orphan 500%.
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

## Front-matter tuning pass (in progress) — what's settled

Working **page-by-page with the user**, who dictates exact line breaks; render each page and
show it before moving on. Workflow: per page `typst compile --root . --font-path
assets/fonts/print --pages N --ppi 220 main.typ build/x.png` **and** the matching `.pdf` —
always regenerate PNG + PDF from the *same* source state (mismatched states confused the user).
For spreads: `python3 tools/spreads.py FIRST LAST 200`.

**Line-break rules the user wants (apply everywhere):**
- Prefer **full-width justified** prose with hyphenation on. Use a manual break only where the
  user asks, at the exact word they name.
- A **bare `\`** is `linebreak(justify: false)`: it leaves the preceding line *ragged/short*
  (not stretched). Use it when the user wants that line **left-aligned**.
- **`#linebreak(justify: true)`** forces the break *and* stretches the preceding line to the
  margin. Use it when the preceding line is word-rich enough that a full line looks clean.
- The user chooses per line: justify the break only if the line stretches cleanly; otherwise
  left-align (e.g. «Дійсно… ніскільки» is left; «…воно було саме таким» is justified).
- Never split the author's name — global rule `Камо но Тьоме[йя]` already NBSP-glues it.
- Avoid one-word last lines: NBSP-glue the last two words instead of forcing a manual break.

**Pages done (p1–p11 = all front matter; `build/front-matter.pdf`):**
- **Передмова (p5):** para 1 break after «практики,» (bare `\`); «розкриває» reflow; para 3
  «…воно було саме таким» uses `linebreak(justify:true)`; «Дійсно… ніскільки» bare `\`.
- **Подяка (p6):** `prose[]` but with `#set par(spacing: 2em)` for **poetry-style stanza gaps**;
  couplets («…відгуки», «…Дгарми.») left-aligned via bare `\`.
- **Зречення (p7):** verse line broken after «ніде,». **Signature** rebuilt: not `credit()` but
  an inline `block` → `pad(right: 7mm, align(right)[…])`, sans **6.5 pt** italic grey, right-edge
  aligned to the poem's right margin (manual 7 mm inset; tied to this page's geometry). **Reuse
  this exact signature style for the body's closing «Написано монахом Ренʼіном…» credit.**
- **Colophon (p4):** bottom spacer reduced `13mm → 2.3mm` so the license block's bottom lines up
  with «Передмова»'s last line; © falls just below (verified on the p4|p5 spread, aligned ±1 px).
- **Text change (both `source/hojoki.md` + `main.typ`):** teacher list replaced with
  «Дякую усім моїм Вчителям Дгарми. Завдяки їхній доброті моє зречення поглиблюється.»
  (`source/hojoki.md` is the canonical input for pandoc/epub/web — currently empty scaffolds.)

See memory `manual-linebreak-justify` for the `\` vs `linebreak(justify:true)` rule.

## TODO (resume here)

1. **Front matter:** essentially done (p1–11). Title pages (p3, p9) still use **serif Cormorant**
   while the half-title (p1) is sans — user hasn't decided whether to unify.
2. **Back matter next**, then the body (user's order: front → back → body). Back matter =
   diptych, endnotes (each on own page), «Зміст» ToC, ensō. Apply the same line-break rules.
3. **Body closing signature** — reuse the p7 signature style (6.5 pt, right-aligned to poem edge).
4. **Closing signature** — DONE: «Написано монахом Ренʼіном…» on its own page, `credit()` now
   right-aligned, pushed to the page foot via `#pagebreak()` + `#v(1fr)` (in build_body.py).
5. **Blank pages show a folio** — suppress folio/header on auto-inserted blanks.
6. **Body chapter pass (IN PROGRESS)** — going chapter by chapter with the user, placing page
   breaks and line breaks by meaning/rhythm. Markers added to `source/hojoki.md`, consumed by
   `build_body.py` (regenerate with it):
   - `---` (own line, between stanzas) → `#pagebreak()`.
   - `~`   (own line) → empty paragraph (extra vertical gap, `#v(2em)`).
   - `===` (own line) → page break + vertically centre everything to the chapter's end (`#v(1fr)`
     before and after) — used to centre a chapter's last page.
   - Line splits/merges are done by editing the verse lines directly in `source/hojoki.md`
     (Python substring edits — beware NBSP after short prepositions; exact `==` match fails).
   - In-body reference numbers are **grey** now.
   Done: **Пролог** (breaks after «Вони — як люди…» and «що живуть у них»), **Пожежа**
   (tercet+empty-paragraph open, several line splits, «Більшість»+«Стільки» same page,
   «Будь-що» centred last page).
7. **Last-page vertical alignment.**
   - **Verso-ends-chapter (RULE, apply now):** if a chapter's last page is a **verso (left)**,
     drop its text so the first line's cap-top matches the **facing recto chapter title**. The
     title sits at content-top +6 mm; cap-tops align at ~5.5 mm, but the user wants the verso
     **0.5 em lower** than the title → **`~7.4mm`**. Insert `---` then `~7.4mm` before the
     strophe that opens that verso page.
     Done: «Голод» (verso folio 32) ↔ «Землетрус» (recto folio 33).
   - **Recto-ends-chapter (DEFER — holistic pass):** centre? golden ratio? Decide **in spread
     view once all chapters are rendered together**. «Пожежа» last page is provisionally centred
     via `===`; revisit uniformly at the end.
8. Swap in **static** Cormorant Garamond weights; set the title-page weight deliberately.

## Print preparation — Mixam hardcover (B6) — DONE for interior

Vendor: **Mixam hardcover** (https://mixam.com/hardcoverbooks). Trim **B6 125 × 176 mm**.
Reviewed against Mixam's checklist (mixam.com/support/checklist).

- **Bleed** is parameterized via a Typst input: `bleed` (default `0mm`) in `typography.typ`,
  read with `--input bleed=3.175mm` (Mixam interior = 0.125"). Every page grows by 2·bleed and
  each margin by bleed (in `layout.typ` `book()` + the three `#set page(margin:)` in `main.typ`),
  so all content stays **trim-relative** while the full-bleed greys (photo pages, «Ретрітна
  хатинка» desc, diptych — `components.typ`; ensō `dy += bleed`) extend into the bleed.
- **Trim/crop marks**: `marks` input (default off), `--input marks=true` → `_crop-marks`
  overlay in `layout.typ` draws L-marks at the trim corners. **Proof only — never upload.**
- **Page count** padded to **120** (÷4 for signatures) via two `#pagebreak()` blank leaves
  between the endnotes and «Зміст» in `main.typ`.
- **CMYK**: Typst exports RGB; `make cmyk` runs **Ghostscript** (installed via brew) to convert
  the bleed PDF → DeviceCMYK. Our inks (`#252120`, `#e46340`, greys) are all CMYK mixes anyway,
  so no pure-K text to preserve. **Still colour-proof the reds/greys** before a full run.
- **Images**: all 872–1089 dpi at placed size (≫300), sRGB — convert cleanly.

**Build targets (`print/Makefile`):**
```
make -C print all     reading copy  -> build/hojoki.pdf            (trim, RGB)
make -C print print   bleed         -> build/hojoki-print.pdf      (RGB)
make -C print cmyk    bleed→CMYK    -> build/hojoki-print-cmyk.pdf (UPLOAD THIS)
make -C print proof   bleed+marks   -> build/hojoki-proof.pdf      (eyeball only)
```

**Cover — `print/cover.typ`** (front=`assets/cover/front-cover.jpg` finished art; back=
`assets/cover/back-cover.jpg` empty cream+brush, text set in Typst). `make -C print cover`
→ `build/cover.pdf`, **CMYK by default** (Typst RGB → Ghostscript). Two layouts:
`--input mode=pages` (default) = 3 component pages **front · spine · back**, each
165.64×216.64 mm (panel) / 54.86×216.64 mm (spine), 0.8″ bleed all sides;
`--input mode=spread` = one 315.02×216.64 mm spread. Spine = **0.56″** (`--input spine=`),
hinge 0.2″. A **solid** beige band (`#e9e6dd`, sampled from the cover brush) sits at
38–96% height across all panels so it connects front↔spine↔back — must stay solid
(a gradient gets rasterised low-res by the gs CMYK pass and Mixam flags it).

**Back-cover text** (set in `cover.typ`, NOT in `source/`; keep in sync by hand):
- Blurb (bold red lead + justified, hyphenation OFF): «**Класичний твір японської
  літератури,** написаний 1212 року. Монах-самітник згадує страждання, лиха і втрати, які
  випали на його власне життя. Попри це він знаходить спокій у самотньому житті, опорі на
  себе, єднанні з природою і зосередженні на духовній практиці.»
- Verse (italic grey, ragged) — an **excerpt condensed from «Пожежа»** (`hojoki.md` L182–187 +
  the chapter's closing strophe): «Доми шістнадцяти панів і безліч інших згоріли. / Це — третя
  частина столиці. / Декілька тисяч чоловіків і жінок / загинули. / Безліч коней та інших
  тварин / померли. // Будь-що ми робимо в нашому житті / не має жодного сенсу. / Проте
  тратити скарб і багатство на те, / щоб збудувати будинки / в цій небезпечній столиці — / це
  особлива дурниця.»  **⚠ duplicates body text** — if «Пожежа» changes, update this by hand.
- Bottom: «© Артем Онучін, 2026» centred + CC BY-NC badge (`by-nc.png`) right.
- Spine title: «Думки у ретрітній хатинці» (serif, light, bottom-to-top).

**Still TODO:** confirm geometry against **Mixam's downloaded cover template** (board overhang
may shift trim a few mm); spine width depends on 120 pp + paper. And a physical colour proof.
