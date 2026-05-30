// Throwaway preview: all three photo spreads, one per page (each an open 2×B6 spread).
// Every photo uses one identical box (same width AND height), fit: cover.
// The recto photo sits in exactly the same place on all three spreads.
#set page(width: 250mm, height: 176mm, margin: 0pt, fill: rgb("#e8e6dc"))
#set text(font: "Arsenal", lang: "uk")

#let PW = 85mm
#let PH = 113mm
#let inner = 14mm

#let img(path) = image(path, width: PW, height: PH, fit: "cover")

#let recto-photo(path) = block(width: 125mm, height: 176mm, inset: (left: inner))[
  #align(left + horizon, img(path))
]
#let verso-photo(path) = block(width: 125mm, height: 176mm, inset: (right: inner))[
  #align(right + horizon, img(path))
]
#let verso-desc(name, body) = block(width: 125mm, height: 176mm, inset: (left: 20mm, right: 13mm, y: 22mm))[
  #set text(size: 10.5pt, fill: rgb("#252120"), hyphenate: true)
  #set par(leading: 0.95em, spacing: 1.3em, justify: true)
  #show regex("[A-Za-zÀ-ÿĀ-ſ]+(?:[ -][A-Za-zÀ-ÿĀ-ſ]+)*"): it => text(style: "italic", it)
  #v(1fr)
  #align(right, text(weight: "bold", size: 12.5pt, fill: rgb("#e46340"))[#name])
  #v(1.4em)
  #body
  #v(1fr)
]

// 1 — retreat house
#grid(columns: (125mm, 125mm),
  verso-desc("«Ретрітна хатинка»")[
    На фотографії зображена ретрітна хатинка в буддійському центрі Garchen Buddhist Institute серед пагорбів Арізони. У таких хатинках сучасні йогіни роблять трирічні ретріти, у яких вони усамітнюються і присвячують себе практиці. Розмір такої хатинки\u{00A0}— три на три метри, саме як ходзьо, ретрітна хатинка самого Камо но Тьомея.

    Ця поема\u{00A0}— це думки, які автор записав у своїй хатинці. Цілком імовірно, що сучасні йогіни можуть мати схожі думки.
  ],
  recto-photo("/assets/images/processed/retreat-hut.jpeg"),
)
#pagebreak()

// 2 — Amitabha
#grid(columns: (125mm, 125mm),
  verso-desc("«Амітабга»")[
    На фото зображена статуя Будди Амітабги в ретрітному центрі Garchen Buddhist Institute.

    Камо но Тьомей був практиком буддизму Чистих Земель\u{00A0}— школи, що зосереджується на зреченні і відданості Будді Амітабзі. Її послідовники вірять: якщо постійно повертати розум до нього і повторювати імʼя Будди, можна переродитися в Чистій Землі Блаженства\u{00A0}— місці без страждання, найкраще пристосованому для практики.
  ],
  recto-photo("/assets/images/processed/Amitabha.jpeg"),
)
#pagebreak()

// 3 — diptych
#grid(columns: (125mm, 125mm),
  verso-photo("/assets/images/processed/Clouds.jpeg"),
  recto-photo("/assets/images/processed/Monks.jpeg"),
)
