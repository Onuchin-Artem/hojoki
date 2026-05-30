// Print PDF entry point.
// In progress: front matter + «Пролог» (to validate front-matter layout).

#import "template/layout.typ": *
#import "template/typography.typ": *
#import "template/components.typ": *

#show: book

// ── Front matter ───────────────────────────────────────────────────────────
// No running header, no folio anywhere in front matter (running starts at the
// first chapter). Front matter uses tighter margins (~30% smaller than the body).
#set page(margin: (inside: 19mm, outside: 18mm, top: 14mm, bottom: 25mm))
#set text(size: 10pt)  // front matter 1pt smaller than body so each section fits one page

// p1 R — half-title (title only, sans, one line, top-aligned)
#align(center, text(font: sans, size: 20pt, fill: ink)[Думки у ретрітній хатинці])

// p2 V blank → p3 R — full title page
#pagebreak(to: "odd")
#v(1fr)
#align(center, text(font: sans, size: 13pt, fill: grey)[Камо но Тьомей])
#v(2fr)
#align(center, text(font: serif, size: 28pt, fill: ink)[
  Думки у ретрітній \
  хатинці
])
#v(3fr)
#align(center, text(font: sans, size: 10.5pt, fill: grey)[
  Переклад з англійської \
  Артем Онучін
])
#v(1fr)

// p4 V — colophon (after the title page): title at top; body bottom-aligned to the
// text-margin line (matching «Передмова»); © below it, still inside the text area
// (the 25 mm bottom margin gives it folio-like clearance — no footer needed).
#pagebreak()
#block(width: 100%, height: 100%)[
  #set align(left)
  #set text(font: sans, fill: ink)
  #set par(leading: 0.75em, spacing: 0.85em, justify: false)

  #text(size: 6.5pt, fill: grey)[Камо но Тьомей] \
  #text(size: 8pt)[Думки у ретрітній хатинці]

  #v(1fr)  // push the body to the foot; title stays at the top

  #set text(size: 6pt)
  #set par(leading: 0.7em, spacing: 1.5em)  // empty-line gaps between logical blocks

  Переклад з англійської: Артем Онучін \
  з дозволу автора англомовного видання

  Англомовне видання: \
  Kamo no Chōmei. Hōjōki: \
  A Buddhist Reflection on Solitude, Imperfection and Transcendence. \
  Translated and annotated by Matthew Stavros. \
  Tokyo: Tuttle Publishing, 2024

  Редагування: Анна Ігнатова \
  Фотографії та каліграфія: Артем Онучін \
  Знято в ретрітному центрі Garchen Buddhist Institute

  Контакт: onuchinart\@gmail.com

  Видання поширюється на умовах ліцензії \
  Creative Commons Attribution-NonCommercial 4.0 International \
  (CC BY-NC 4.0)

  #v(2.5em)
  #align(center, text(size: 6pt)[© Артем Онучін, 2026])
  #v(2.3mm)  // align the license block's bottom with «Передмова»'s last line; © falls just below
]

// p5 R — foreword
#pagebreak(to: "odd")
#fm-heading("Передмова")
#prose[
  У буддизмі правильна мотивація\u{00A0}— фундамент практики, \
  її найважливіша частина.

  Зокрема, розвивають зречення\u{00A0}— мотивацію відвернутися від турбот самсари до спокою нірвани. Щоб розвити в собі зречення, практики буддизму медитують на непостійність, страждання самсари, цінність присвячення себе практиці, і закон причинно-наслідкових звʼязків. Саме ці теми розкриває класичний текст, переклад якого я для вас\u{00A0}представляю.

  Ходзьокі\u{00A0}— Думки у ретрітній хатинці\u{00A0}— це поема, яку написав Камо но Тьомей у тринадцятому столітті в Японії. Проте вона відчувається дуже актуальною і сучасною, особливо для українців. Відчуття кінця світу, яке так багато людей проживають зараз,\u{00A0}— воно було саме таким#linebreak(justify: true)
  і за життя автора.

  Дійсно, світ при всій своїй непостійності ніскільки \
  не змінюється.

  Тим важливіше послання цієї поеми\u{00A0}— заклик до спокою, до зосередження на практиці, до слідування Шляхом.

  Я щиро бажаю, щоб в Україні розквітала справжня практика Дгарми і були всі умови для неї. Я присвячую свій переклад саме цьому.
]

// p6 V — acknowledgments
#pagebreak()
#fm-heading("Подяка")
#prose[
  #set par(spacing: 2em)  // poetry-style stanza gaps between paragraphs
  Дякую Метью Ставросу за чудовий англійський переклад, з якого я працював. Я зустрів його книжку в книгарні, відкрив на випадковій сторінці\u{00A0}— і відтоді ось уже шість місяців щоденно до неї повертаюсь. Робота над цим текстом стала для мене справжньою практикою.

  Дякую Ані Ігнатовій за вичитку, відгуки \
  і за те, що ти є в моєму житті.

  Дякую усім моїм Вчителям Дгарми. \
  Завдяки їхній доброті моє зречення поглиблюється.

  Дякую ЗСУ за те, що Україна досі існує.
]

// p7 R — poem «Зречення»
#pagebreak(to: "odd")
#fm-heading("Зречення")
#verse[
  Спочатку зречення було для мене страхом і тугою. \
  Я шукав собі точки опори \
  і дивився, як вони всі розсипалися й танули на очах.

  Потім я бачив зречення як процес дорослішання. \
  Я грався в іграшки самсари, \
  і з часом їхній чар і мій інтерес до них стиралися.

  Тепер я бачу зречення як бажання спокою. \
  Я ясно бачу, що щастя неможливо знайти ніде, \
  крім як усередині. \
  Все, що я хочу,\u{00A0}— це відвернутися від ілюзорного світу.
]

#v(12mm)
#block(width: 100%, {
  set text(font: sans, size: 6.5pt, style: "italic", fill: grey)
  set par(leading: 0.7em, spacing: 1em, justify: false)
  pad(right: 7mm, align(right)[
    Артем Онучін

    написано під час роботи \
    над перекладом «Думки у ретрітній хатинці»

    2026
  ])
})

// p8 V — blank
// p9 R — second title page (author + title only)
#pagebreak(to: "odd")
#v(1fr)
#align(center, text(font: sans, size: 12pt, fill: grey)[Камо но Тьомей])
#v(1.5fr)
#align(center, text(font: serif, size: 26pt, fill: ink)[
  Думки у ретрітній \
  хатинці
])
#v(2fr)

// p10 V + p11 R — retreat-house photo spread (grey background, no header/folio)
#pagebreak()
#page(fill: photo-bg, margin: 0pt, header: none, footer: none)[
  #block(width: 100%, height: 100%, inset: (left: 26mm, right: 14mm, y: 24mm))[
    #set text(font: sans, size: 10.5pt, fill: ink, hyphenate: true)
    #set par(leading: 0.95em, spacing: 1.3em, justify: true)
    #v(1fr)
    #align(right, text(weight: "bold", size: 12.5pt, fill: red)[«Ретрітна хатинка»])
    #v(1.4em)
    На фотографії зображена ретрітна хатинка в буддійському центрі Garchen Buddhist Institute серед пагорбів Арізони. У таких хатинках сучасні йогини роблять трирічні ретріти, у яких вони усамітнюються і присвячують себе практиці. Розмір такої хатинки\u{00A0}— три на три метри, саме як ходзьо, ретрітна хатинка самого Камо но Тьомея.

    Ця поема\u{00A0}— це думки, які автор записав у своїй хатинці. Цілком імовірно, що сучасні йогини можуть мати \
  схожі думки.
    #v(1fr)
  ]
]
#page(fill: photo-bg, margin: 0pt, header: none, footer: none)[
  #block(width: 100%, height: 100%, inset: (left: 14mm))[
    #align(left + horizon, image("/assets/images/processed/retreat-hut.jpeg", width: 85mm, height: 113mm, fit: "cover"))
  ]
]

// ── Main body ──────────────────────────────────────────────────────────────
// Full canon margins, 11 pt. Folio restarts at 1 on «Пролог» (in chapter()).
#set page(margin: (inside: 19mm, outside: 26mm, top: 32mm, bottom: 40mm))
#set text(size: 11pt)

#include "body.typ"

// ── Back matter ──────────────────────────────────────────────────────────────
// Same rules as front matter: 10 pt, tight margins, centered titles.
#set page(margin: (inside: 19mm, outside: 18mm, top: 14mm, bottom: 25mm))
#set text(size: 10pt)

// Blank recto (breathing space after «тиша») → clouds (V) + monks (R) diptych
#pagebreak(to: "odd")
#diptych("/assets/images/processed/Clouds.jpeg", "/assets/images/processed/Monks.jpeg")

// Endnotes — begin on a recto; each note on its own page
#pagebreak(to: "odd")
#include "endnotes.typ"

// Table of contents
#pagebreak(to: "odd")
#fm-heading("Зміст")
#context {
  let rows = ()
  for e in _toc.get() {
    rows.push(e.title)
    rows.push(text(fill: grey)[#e.page])
  }
  grid(columns: (1fr, auto), column-gutter: 8pt, row-gutter: 0.9em, ..rows)
}

// ensō calligraphy — final verso
#pagebreak()
#page(header: none, footer: none,
  align(center + horizon, image("/assets/images/processed/ensho.jpg", height: 70mm)))
