#!/usr/bin/env python3
"""Generate the web edition of «Думки у ретрітній хатинці» from source/*.md.

Web twin of print/tools/build_body.py: same source, same marker semantics
(Typst is the source of truth), but the target is a single self-contained
semantic HTML page for screen reading, not print.

  source/hojoki.md     -> front matter (prose/verse/signature) + body (verse)
  source/footnotes.md  -> 10 notes (italic lemma + dry prose)  [второй голос]
  source/captions.md   -> illustration-block descriptions (хатинка, Амітабга)
  build/_front.png      -> entry-screen cover (design with 方丈記 calligraphy)
  assets/images/...     -> responsive WebP+JPEG variants under web/assets/img/

NBSP (U+00A0) are authored in the source — we read/write UTF-8 and never
collapse them. Verse line breaks are preserved verbatim; prose reflows.

Run from anywhere:  python3 web/build_web.py [--stage 1|2]
"""
import re, html, json, pathlib, argparse, shutil
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "web"
IMGDIR = OUT / "assets" / "img"

DONATE_URL = "https://savelife.in.ua/donate"
CONTACT_EMAIL = "onuchinart@gmail.com"
# find-replace placeholders, filled once hosting is set up:
PLAUSIBLE_DOMAIN = "{{PLAUSIBLE_DOMAIN}}"
CF_BEACON_TOKEN = "{{CF_BEACON_TOKEN}}"
SITE_URL = "{{SITE_URL}}"

DESCRIPTION = ("Український переклад «Ходзьокі» (方丈記) Камо но Тьомея — "
               "медитація XIII століття про непостійність, самоту й спокій. "
               "Переклад з англійської Артема Онучіна.")

# Endnote order = first appearance across the whole body (matches build_body.py).
NOTE_ORDER = [
    "era-angen", "maro-palace", "war-omens", "siddham-a", "chomei-biography",
    "amitabha", "samantabhadra-acala", "instruments-poets", "plants-walks",
    "vimalakirti-chandapandaka",
]

# Chapters emitted per stage (None = all). Stage 1 is the review prototype.
STAGE1_CHAPTERS = {"Пролог", "Пожежа в епоху Анґен"}
def norm(t):  # titles carry authored NBSP — compare space-insensitively
    return t.replace("\xa0", " ")
def in_stage1(t):
    return norm(t) in STAGE1_CHAPTERS

# ── transliteration → stable, meaningful anchor ids ──────────────────────────
_TR = {
    "а":"a","б":"b","в":"v","г":"h","ґ":"g","д":"d","е":"e","є":"ie","ж":"zh",
    "з":"z","и":"y","і":"i","ї":"i","й":"i","к":"k","л":"l","м":"m","н":"n",
    "о":"o","п":"p","р":"r","с":"s","т":"t","у":"u","ф":"f","х":"kh","ц":"ts",
    "ч":"ch","ш":"sh","щ":"shch","ь":"","ю":"iu","я":"ia","ʼ":"","’":"","'":"",
}
def slug(s):
    s = s.strip().lower()
    out = "".join(_TR.get(c, c) for c in s)
    out = re.sub(r"[^a-z0-9]+", "-", out).strip("-")
    return out or "x"

# bind the author's name with NBSP so «Камо но Тьомей/Тьомея» never wraps
def bind_names(s):
    s = s.replace("Камо но Тьоме", "Камо но Тьоме")
    s = s.replace("Артем Онучін", "Артем Онучін")
    return s

# ── inline markdown → HTML (preserves NBSP; html.escape leaves U+00A0 alone) ──
def inline(s):
    s = html.escape(s, quote=False)
    s = bind_names(s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
               lambda m: '<a href="%s" rel="noopener">%s</a>' % (html.escape(m.group(2), quote=True), m.group(1)),
               s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    return s

def strip_breaks(line):
    """Print hard-break artefacts (' \\' and trailing two-space) -> reflow space."""
    return re.sub(r"\s*\\\s*", " ", line).strip()

# ── responsive image variants (WebP + JPEG) ──────────────────────────────────
def responsive(src, base, widths, quality=78):
    """Write <base>-<w>.{webp,jpg} for each width ≤ source width; return picture dict."""
    IMGDIR.mkdir(parents=True, exist_ok=True)
    img = Image.open(src).convert("RGB")
    sizes = sorted({w for w in widths if w <= img.width} | {min(img.width, max(widths))})
    made = []
    for w in sizes:
        h = round(img.height * w / img.width)
        rim = img.resize((w, h), Image.LANCZOS)
        rim.save(IMGDIR / f"{base}-{w}.jpg", "JPEG", quality=quality, optimize=True, progressive=True)
        rim.save(IMGDIR / f"{base}-{w}.webp", "WEBP", quality=quality, method=6)
        made.append(w)
    return {"base": base, "widths": made, "w": img.width, "h": img.height}

def picture(pic, alt, sizes, cls="", eager=False):
    base, widths = pic["base"], pic["widths"]
    webp = ", ".join(f"assets/img/{base}-{w}.webp {w}w" for w in widths)
    jpg  = ", ".join(f"assets/img/{base}-{w}.jpg {w}w"  for w in widths)
    last = widths[-1]
    loading = "" if eager else ' loading="lazy" decoding="async"'
    clsattr = f' class="{cls}"' if cls else ""
    return (
        f'<picture{clsattr}>'
        f'<source type="image/webp" srcset="{webp}" sizes="{sizes}">'
        f'<img src="assets/img/{base}-{last}.jpg" srcset="{jpg}" sizes="{sizes}" '
        f'width="{pic["w"]}" height="{pic["h"]}" alt="{html.escape(alt, quote=True)}"{loading}>'
        f'</picture>'
    )

# ════════════════════════════════════════════════════════════════════════════
# Parse source/hojoki.md  →  front-matter sections + body chapters
# ════════════════════════════════════════════════════════════════════════════
SRC = (ROOT / "source/hojoki.md").read_text(encoding="utf-8").splitlines()

def split_sections(lines):
    """Yield (title, attrs, body_lines) per `# Heading` block."""
    title, attrs, buf = None, "", []
    for raw in lines:
        m = re.match(r"^#\s+(.*)$", raw)
        if m:
            if title is not None:
                yield title, attrs, buf
            head = m.group(1)
            am = re.search(r"\{([^}]*)\}", head)
            attrs = am.group(1) if am else ""
            title = re.sub(r"\s*\{[^}]*\}", "", head).strip()
            buf = []
        elif title is not None:
            buf.append(raw)
    if title is not None:
        yield title, attrs, buf

# footnote refs in body text → superscript anchors (numbering = NOTE_ORDER)
def num_of(key):
    return NOTE_ORDER.index(key) + 1 if key in NOTE_ORDER else 0

def refs(text):
    def sub(m):
        n = num_of(m.group(1))
        return (f'<a class="fnref" id="fnref-{n}" href="#fn-{n}" role="doc-noteref" '
                f'aria-label="Примітка {n}">{n}</a>')
    return re.sub(r"\[\^([^\]]+)\]", sub, text)

# ── verse parser: stanzas, line breaks, `>2em` indent, `~`/`---` gaps ─────────
def parse_verse(body):
    """Return list of blocks: ('stanza',[lines],indent) | ('gap',em) | ('rest',) ."""
    blocks, cur, indent = [], [], None
    def flush():
        nonlocal cur, indent
        if cur:
            blocks.append(("stanza", cur, indent))
            cur, indent = [], None
    for raw in body:
        s = raw.strip()
        if s == "":
            flush(); continue
        # Bare `~` = intentional extra gap (an empty paragraph) — kept.
        if s == "~":
            flush(); blocks.append(("space",)); continue
        # `~Nmm` etc. = print last-page alignment skips, and `---`/`===` pagebreaks
        # — ignored on the web (no pages).
        if s == "---" or re.fullmatch(r"~\s*[\d.]+\s*(em|mm|pt|cm)?", s) or s == "===":
            flush(); continue
        if re.fullmatch(r">\s*([\d.]+em)?", s):
            flush()
            mm = re.search(r"([\d.]+)em", s)
            indent = float(mm.group(1)) if mm else 2.0
            continue
        cur.append(s)
    flush()
    return blocks

def render_verse(blocks):
    out = ['<div class="verse">']
    for b in blocks:
        if b[0] == "space":
            out.append('<p class="verse-space" aria-hidden="true"></p>')
        elif b[0] == "stanza":
            _, lines, indent = b
            cls = "stanza" + (" indent" if indent else "")
            st = "" if not indent else f' style="--indent:{indent}em"'
            lns = "".join(f'<span class="line">{refs(inline(strip_breaks(l)))}</span>' for l in lines)
            out.append(f'<p class="{cls}"{st}>{lns}</p>')
    out.append("</div>")
    return "\n".join(out)

def parse_prose(body):
    paras, cur = [], []
    for raw in body:
        if raw.strip() == "":
            if cur: paras.append(" ".join(cur)); cur = []
        else:
            cur.append(strip_breaks(raw))
    if cur: paras.append(" ".join(cur))
    return paras

# ── front matter: Передмова, Подяка (prose); Зречення (verse + signature) ─────
SIG_OPENERS = ("Артем Онучін", "Написано монахом")

def split_signature(body):
    """Return (poem_lines, signature_blocks). Signature = trailing author colophon."""
    idx = None
    for i, l in enumerate(body):
        if any(l.strip().startswith(o) for o in SIG_OPENERS):
            idx = i; break
    if idx is None:
        return body, []
    poem = body[:idx]
    sig_raw = [l for l in body[idx:]]
    # signature blocks separated by blank lines
    blocks, cur = [], []
    for l in sig_raw:
        if l.strip() == "":
            if cur: blocks.append("\n".join(x.strip() for x in cur)); cur = []  # keep `\` breaks
        else:
            cur.append(l)
    if cur: blocks.append("\n".join(x.strip() for x in cur))
    return poem, blocks

# web-only line breaks in the signature (source stays one line for print)
SIG_BREAKS = {"написано під час роботи над перекладом": "написано під час роботи\nнад перекладом"}

def render_signature(blocks):
    def fmt(b):  # manual `\` breaks and source newlines → <br>
        for a, c in SIG_BREAKS.items():
            b = b.replace(a, c)
        parts = [p.strip() for p in re.split(r"\s*\\\s*|\n", b) if p.strip()]
        return "<br>".join(inline(p) for p in parts)
    inner = "".join(f"<p>{fmt(b)}</p>" for b in blocks)
    return f'<div class="signature">{inner}</div>'

# ════════════════════════════════════════════════════════════════════════════
# Parse source/footnotes.md  →  {id: html}  (+ «Джерела» appendix)
# ════════════════════════════════════════════════════════════════════════════
def parse_footnotes():
    raw = (ROOT / "source/footnotes.md").read_text(encoding="utf-8")
    # cut the «# Джерела» appendix off the notes
    parts = re.split(r"^#\s+Джерела\s*$", raw, maxsplit=1, flags=re.M)
    notes_src = parts[0]
    notes = {}
    pat = re.compile(r"^\[\^([^\]]+)\]:[ \t]?(.*)$", re.M)
    matches = list(pat.finditer(notes_src))
    for i, m in enumerate(matches):
        key = m.group(1)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(notes_src)
        block = m.group(2) + notes_src[m.end():end]   # slice already starts with the line-1 newline
        # dedent: strip leading indentation that markdown uses for the note body
        lines = [re.sub(r"^[ \t]{1,4}", "", ln) for ln in block.splitlines()]
        notes[key] = md_to_html(lines, first_is_lemma=True)
    sources = md_to_html(merge_japanesewiki(parts[1]).splitlines()) if len(parts) > 1 else ""
    return notes, sources

def merge_japanesewiki(md):
    """Web-only: move the japanesewiki (Gissha) link into the first list (translator's
    source notes) and drop its separate «Окремий ресурс» heading. Source stays as-is."""
    lines = md.splitlines()
    gi = next((i for i, l in enumerate(lines) if "japanesewiki.com" in l), None)
    if gi is None:
        return md
    gissha = lines.pop(gi)
    lines = [l for l in lines if "Окремий ресурс" not in l]
    wiki = next((i for i, l in enumerate(lines) if l.strip().startswith("Вікіпедія")), len(lines))
    ins = next((i + 1 for i in range(wiki - 1, -1, -1) if lines[i].strip().startswith("-")), 0)
    lines.insert(ins, gissha)
    return "\n".join(lines)

def md_to_html(lines, first_is_lemma=False):
    out, para, lst, first = [], [], [], True
    def flush_para():
        nonlocal para, first
        if not para: return
        is_lemma = first and first_is_lemma and para[0].lstrip().startswith("*")
        if is_lemma:
            # verse quote — keep its original line breaks (join with <br>)
            txt = inline("\n".join(strip_breaks(x) for x in para)).replace("\n", "<br>\n")
            out.append(f'<p class="lemma">{txt}</p>')
        else:
            out.append(f"<p>{inline(strip_breaks(' '.join(para)))}</p>")
        para, first = [], False
    def flush_list():
        nonlocal lst
        if lst:
            items = "".join(f"<li>{inline(strip_breaks(x))}</li>" for x in lst)
            out.append(f"<ul>{items}</ul>"); lst = []
    for ln in lines:
        s = ln.strip()
        if s == "":
            flush_para(); flush_list()
        elif s == "---":
            flush_para(); flush_list()   # page break in source — ignored on web (no pages)
        elif re.match(r"^-\s+", s):
            flush_para()
            lst.append(re.sub(r"^-\s+", "", s))
        else:
            flush_list(); para.append(s)
    flush_para(); flush_list()
    return "\n".join(out)

# ════════════════════════════════════════════════════════════════════════════
# Captions (illustration blocks)
# ════════════════════════════════════════════════════════════════════════════
def parse_captions():
    raw = (ROOT / "source/captions.md").read_text(encoding="utf-8")
    blocks = {}
    cur_name, cur = None, []
    for ln in raw.splitlines():
        m = re.match(r"^\*\*«([^»]+)»\*\*\s*$", ln.strip())
        if m:
            if cur_name: blocks[cur_name] = parse_prose(cur)
            cur_name, cur = m.group(1), []
        elif cur_name is not None:
            cur.append(ln)
    if cur_name: blocks[cur_name] = parse_prose(cur)
    return blocks

def figure(name, pic, alt, paras, eager=False):
    desc = "".join(f"<p>{inline(p)}</p>" for p in paras)
    img = picture(pic, alt, "360px", cls="fig-img", eager=eager)
    return (
        f'<figure class="illus" id="{slug(name)}">'
        f'{img}'
        f'<figcaption><h3 class="fig-name">«{html.escape(name)}»</h3>'
        f'<div class="prose">{desc}</div></figcaption>'
        f'</figure>'
    )

# ════════════════════════════════════════════════════════════════════════════
# Build
# ════════════════════════════════════════════════════════════════════════════
def donate(label, location, cls):
    return (f'<a class="{cls}" href="{DONATE_URL}" target="_blank" rel="noopener" '
            f'data-loc="{location}">{label}</a>')

def support_block(location):
    return (
        f'<section class="support" aria-label="Підтримка проєкту">'
        f'<p class="support-text">Ця книжка безкоштовна. Якщо вона була вам цінною, '
        f'ви можете підтримати тих, хто захищає Україну.</p>'
        f'<p class="support-links">{donate("Підтримати ЗСУ", location, "btn")}'
        f'<a class="contact" href="mailto:{CONTACT_EMAIL}">Написати перекладачу</a></p>'
        f'</section>'
    )

def breath():
    return '<div class="breath" role="presentation" aria-hidden="true"></div>'

def write_llms_txt():
    """GEO: a machine-readable summary for generative engines."""
    txt = f"""# Думки у ретрітній хатинці (Hōjōki / 方丈記)

> Ukrainian translation of Kamo no Chōmei's «Hōjōki» (方丈記, 1212), a classical
> Japanese Buddhist reflection on impermanence, solitude, and peace.
> Translated from English into Ukrainian by Artem Onuchin.

- Title (uk): Думки у ретрітній хатинці
- Original work: 方丈記 (Hōjōki), Kamo no Chōmei, 1212
- Author: Камо но Тьомей (Kamo no Chōmei)
- Translator: Артем Онучін (Artem Onuchin)
- Editor: Анна Ігнатова (Anna Ihnatova)
- Source edition: Kamo no Chōmei, *Hōjōki: A Buddhist Reflection on Solitude,
  Imperfection and Transcendence*, trans. Matthew Stavros, Tuttle Publishing, 2024
- Language: Ukrainian (uk)
- License: Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0)
- Significance: second complete Ukrainian translation of Hōjōki; the first from
  English, and the first in 92 years (after Stepan Levynskyi, Lviv, 1934)
- Contact: {CONTACT_EMAIL}
- URL: {SITE_URL}

## Structure
Front matter (foreword, gratitude, the poem «Зречення»), a prologue and 15 verse
chapters, 10 endnotes, and a colophon.

## Citation
Attribute the translation to Артем Онучін and the original to Камо но Тьомей.
Reuse under CC BY-NC 4.0 (non-commercial, with attribution).
"""
    (OUT / "llms.txt").write_text(txt, encoding="utf-8")

def build(stage):
    sections = list(split_sections(SRC))
    # front matter = before {.book-title}; body = after
    bt = next(i for i, s in enumerate(sections) if "book-title" in s[1])
    front = sections[:bt]
    book_title = sections[bt][0]
    body = sections[bt + 1:]
    captions = parse_captions()
    notes, sources = parse_footnotes()

    # images -------------------------------------------------------------------
    P = ROOT / "assets/images/processed"
    cover_pic = responsive(ROOT / "assets/cover/front-cover.jpg", "cover", [560, 900, 1300], quality=84)
    hut_pic = responsive(P / "retreat-hut.jpeg", "retreat-hut", [480, 800, 1200])
    if stage == 2:
        amitabha_pic = responsive(P / "Amitabha.jpeg", "amitabha", [480, 800, 1200])
        clouds_pic = responsive(P / "Clouds.jpeg", "clouds", [480, 800, 1200])
        monks_pic = responsive(P / "Monks.jpeg", "monks", [480, 800, 1200])
        enso_pic = responsive(P / "ensho.jpg", "enso", [420, 760])

    H = []
    H.append('<article class="book">')

    # 1. cover (entry screen) --------------------------------------------------
    cover_img = picture(cover_pic,
        "Обкладинка книги «Думки у ретрітній хатинці» з каліграфією 方丈記 (Ходзьокі)",
        "100vw", cls="cover-img", eager=True)
    H.append(f'<header class="cover" id="top">{cover_img}</header>')

    # 2+3. support block + inline contents toggle (one row) --------------------
    toc = []   # contents lists chapters + Примітки only (not front matter)
    for t, a, b in body:
        if stage == 1 and not in_stage1(t):
            continue
        toc.append((t, slug(t)))
    toc.append(("Примітки", "notes"))
    items = "".join(f'<li><a href="#{i}">{html.escape(t)}</a></li>' for t, i in toc)
    H.append(
        '<section class="support" id="contents" aria-label="Підтримка і зміст">'
        '<p class="support-text">Ця книжка безкоштовна. Якщо вона була вам цінною, '
        'ви можете підтримати тих, хто захищає Україну.</p>'
        '<div class="support-links">'
        + donate("Підтримати ЗСУ", "after-cover", "btn")
        + '<a class="contact" href="hojoki.pdf" download>PDF</a>'
        + '<a class="contact" href="hojoki.epub" download>EPUB</a>'
        + f'<a class="contact" href="mailto:{CONTACT_EMAIL}">Написати перекладачу</a>'
        + f'<details class="toc"><summary>Зміст</summary><ol>{items}</ol></details>'
        + '</div></section>')

    # 4–6. front-matter sections ----------------------------------------------
    for t, a, b in front:
        sid = slug(t)
        if t == "Зречення":
            poem, sig = split_signature(b)
            H.append(f'<section class="chapter renunciation" id="{sid}">'
                     f'<h2>{html.escape(t)}</h2>'
                     f'{render_verse(parse_verse(poem))}'
                     f'{render_signature(sig)}</section>')
        else:
            paras = "".join(f"<p>{inline(p)}</p>" for p in parse_prose(b))
            H.append(f'<section class="prose-section" id="{sid}">'
                     f'<h2>{html.escape(t)}</h2>'
                     f'<div class="prose">{paras}</div></section>')

    # 7. title page ------------------------------------------------------------
    H.append(f'<header class="title-page" id="{slug(book_title)}">'
             f'<p class="title-author">{bind_names("Камо но Тьомей")}</p>'
             f'<h1>{html.escape(book_title)}</h1>'
             f'<p class="title-translator">{bind_names("Переклад з англійської — Артем Онучін")}</p>'
             f'</header>')

    # 8. retreat-hut illustration ---------------------------------------------
    hut = captions.get("Ретрітна хатинка", [])
    H.append(figure("Ретрітна хатинка", hut_pic,
                    "Ретрітна хатинка в центрі Garchen Buddhist Institute серед пагорбів Арізони",
                    hut))

    # 9. body chapters ---------------------------------------------------------
    # (Breathing pauses dropped — sections flow with their own padding.)
    for idx, (t, a, b) in enumerate(body):
        if stage == 1 and not in_stage1(t):
            continue
        # Амітабга illustration before «Моя маленька хатинка»
        if stage == 2 and norm(t) == "Моя маленька хатинка":
            H.append(figure("Амітабга", amitabha_pic,
                            "Статуя Будди Амітабги в ретрітному центрі Garchen Buddhist Institute",
                            captions.get("Амітабга", [])))
        poem, sig = split_signature(b)   # trailing «Написано монахом …» → colophon-signature
        sig_html = render_signature(sig) if sig else ""
        H.append(f'<section class="chapter" id="{slug(t)}">'
                 f'<h2>{html.escape(t)}</h2>{render_verse(parse_verse(poem))}{sig_html}</section>')

    # 10. diptych (Clouds + Monks, no captions) --------------------------------
    if stage == 2:
        H.append('<figure class="diptych" aria-label="Хмари і монахи">'
                 + picture(clouds_pic, "Хмари над горами Тояма", "(max-width: 700px) 90vw, 330px", cls="dip-img")
                 + picture(monks_pic, "Монахи на ретріті", "(max-width: 700px) 90vw, 330px", cls="dip-img")
                 + '</figure>')

    # 11. notes (always present) + «Джерела» -----------------------------------
    note_items = []
    used = [k for k in NOTE_ORDER if (stage == 2 or k in {"era-angen"})]
    for k in used:
        n = num_of(k)
        back = (f'<a class="fn-back" href="#fnref-{n}" aria-label="Повернутися до тексту">'
                f'↩ повернутися</a>')
        note_items.append(
            f'<li class="note" id="fn-{n}"><span class="note-num">{n}</span>'
            f'<div class="note-body">{notes[k]}{back}</div></li>')
    sources_block = (f'<details class="sources"><summary>Джерела</summary>{sources}</details>'
                     if (stage == 2 and sources) else "")
    H.append(f'<section class="notes" id="notes" aria-label="Примітки">'
             f'<h2>Примітки</h2><ol class="note-list">{"".join(note_items)}</ol>'
             f'{sources_block}</section>')

    # 12. colophon -------------------------------------------------------------
    if stage == 2:
        credits = [
            "Переклад з англійської — Артем Онучін, з дозволу автора англомовного видання.",
            "Англомовне видання: Kamo no Chōmei. *Hōjōki: A Buddhist Reflection on Solitude, "
            "Imperfection and Transcendence*. Translated and annotated by Matthew Stavros. "
            "Tokyo: Tuttle Publishing, 2024.",
            "Редагування — Анна Ігнатова.",
            "Фотографії та каліграфія — Артем Онучін. Знято в ретрітному центрі "
            "Garchen Buddhist Institute.",
            "Це другий повний український переклад «Ходзьокі» — перший з англійської "
            "і перший за 92 роки, після перекладу Степана Левинського (Львів, 1934).",
        ]
        license_p = ("Видання поширюється на умовах ліцензії Creative Commons «Зазначення "
                     "авторства — Некомерційна — 4.0 Міжнародна» "
                     "([CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)).")
        colo_list = '<ul>' + "".join(f"<li>{inline(c)}</li>" for c in credits) + '</ul>'
        colo_tail = f'<p>{inline(license_p)}</p><p>© Артем Онучін, 2026.</p>'
        H.append(f'<section class="colophon prose-section" id="colophon" aria-label="Колофон">'
                 f'<h2>Колофон</h2><div class="prose">{colo_list}{colo_tail}</div></section>')

        # 13. ensō — final element, nothing after it
        H.append('<div class="enso" aria-label="Енсо">'
                 + picture(enso_pic, "Енсо — каліграфічне коло", "320px", cls="enso-img")
                 + '</div>')

    H.append('</article>')

    # floating marginalia box (desktop) + back-to-top
    H.append('<aside id="margin-box" class="marginalia" hidden role="note"></aside>')
    H.append(f'{donate("Підтримати ЗСУ", "corner", "donate-corner")}')

    body_html = "\n".join(H)
    cover_jpg = f"assets/img/{cover_pic['base']}-{cover_pic['widths'][-1]}.jpg"
    og_image = f"{SITE_URL}/{cover_jpg}"

    # GEO: schema.org Book/CreativeWork
    ld = {
        "@context": "https://schema.org",
        "@type": "Book",
        "name": "Думки у ретрітній хатинці",
        "alternateName": "Hōjōki / 方丈記",
        "inLanguage": "uk",
        "url": SITE_URL,
        "image": og_image,
        "author": {"@type": "Person", "name": "Камо но Тьомей", "alternateName": "Kamo no Chōmei"},
        "translator": {"@type": "Person", "name": "Артем Онучін"},
        "editor": {"@type": "Person", "name": "Анна Ігнатова"},
        "datePublished": "2026",
        "license": "https://creativecommons.org/licenses/by-nc/4.0/",
        "description": DESCRIPTION,
        "isBasedOn": {
            "@type": "Book",
            "name": "Hōjōki: A Buddhist Reflection on Solitude, Imperfection and Transcendence",
            "author": {"@type": "Person", "name": "Kamo no Chōmei"},
            "translator": {"@type": "Person", "name": "Matthew Stavros"},
            "publisher": {"@type": "Organization", "name": "Tuttle Publishing"},
            "datePublished": "2024",
        },
        "exampleOfWork": {"@type": "Book", "name": "方丈記 (Hōjōki)", "dateCreated": "1212"},
    }
    jsonld_tag = ('<script type="application/ld+json">'
                  + json.dumps(ld, ensure_ascii=False) + '</script>')
    cf_beacon = ('<script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
                 'data-cf-beacon=\'{"token": "' + CF_BEACON_TOKEN + '"}\'></script>')

    page = PAGE.format(
        body=body_html, css="style.css", plausible=PLAUSIBLE_DOMAIN, donate=DONATE_URL,
        description=html.escape(DESCRIPTION, quote=True), og_image=og_image,
        site_url=SITE_URL, jsonld=jsonld_tag, cf_beacon=cf_beacon,
    )
    (OUT / "index.html").write_text(page, encoding="utf-8")
    write_llms_txt()
    print(f"index.html written (stage {stage}); notes: {len(used)}; chapters: "
          f"{sum(1 for t,_,_ in body if stage==2 or in_stage1(t))}")

# ── HTML shell ───────────────────────────────────────────────────────────────
PAGE = """<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Думки у ретрітній хатинці — Камо но Тьомей</title>
<meta name="description" content="{description}">
<meta property="og:type" content="book">
<meta property="og:locale" content="uk_UA">
<meta property="og:site_name" content="Думки у ретрітній хатинці">
<meta property="og:title" content="Думки у ретрітній хатинці — Камо но Тьомей">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{site_url}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{site_url}">
{jsonld}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Arsenal:ital,wght@0,400;0,700;1,400;1,700&family=Cormorant+Garamond:wght@500&display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Arsenal:ital,wght@0,400;0,700;1,400;1,700&family=Cormorant+Garamond:wght@500&display=swap">
<link rel="stylesheet" href="{css}">
<script defer data-domain="{plausible}" src="https://plausible.io/js/script.tagged-events.js"></script>
{cf_beacon}
</head>
<body>
{body}
<script>
(function() {{
  // Donate-click custom event (Plausible, cookieless). Works for all donate links.
  document.addEventListener('click', function(e) {{
    var a = e.target.closest('a[href="{donate}"]');
    if (!a) return;
    if (window.plausible) window.plausible('Donate', {{props: {{location: a.dataset.loc || 'unknown'}}}});
  }}, true);

  // Footnotes: desktop → floating marginalia next to the line; mobile → jump.
  var DESKTOP = window.matchMedia('(min-width: 980px)');
  var box = document.getElementById('margin-box');
  var openRef = null;
  function noteHtml(n) {{
    var li = document.getElementById('fn-' + n);
    if (!li) return '';
    var body = li.querySelector('.note-body').cloneNode(true);
    var lem = body.querySelector('.lemma');   // quote lives in the appendix only
    if (lem) lem.remove();
    var back = body.querySelector('.fn-back');
    if (back) back.remove();
    return body.innerHTML;
  }}
  function closeBox() {{ box.hidden = true; openRef = null; }}
  function openBox(ref) {{
    var n = ref.getAttribute('href').replace('#fn-', '');
    box.innerHTML = noteHtml(n);
    box.hidden = false;
    var r = ref.getBoundingClientRect();
    var col = ref.closest('.verse, .prose');
    var right = col ? col.getBoundingClientRect().right : r.right;
    box.style.top = (window.scrollY + r.top) + 'px';
    box.style.left = (window.scrollX + right + 24) + 'px';
    openRef = ref;
  }}
  document.addEventListener('click', function(e) {{
    var ref = e.target.closest('.fnref');
    if (ref) {{
      if (!DESKTOP.matches) return;            // mobile: let the anchor jump
      e.preventDefault();
      if (openRef === ref) {{ closeBox(); }} else {{ openBox(ref); }}
      return;
    }}
    if (!box.hidden && !e.target.closest('#margin-box')) closeBox();
  }});
  window.addEventListener('resize', function() {{ if (!box.hidden && openRef) openBox(openRef); }});

  // Subtle fade-in on scroll — single allowed motion; respects reduced-motion.
  if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches && 'IntersectionObserver' in window) {{
    document.body.classList.add('reveal-on');
    var io = new IntersectionObserver(function(entries) {{
      entries.forEach(function(en) {{ if (en.isIntersecting) {{ en.target.classList.add('shown'); io.unobserve(en.target); }} }});
    }}, {{rootMargin: '0px 0px -8% 0px'}});
    document.querySelectorAll('.chapter, .prose-section, .illus, .notes, .toc, .support').forEach(function(el) {{ io.observe(el); }});
  }}

  // Corner donate button: quiet down past the cover.
  var corner = document.querySelector('.donate-corner');
  if (corner) window.addEventListener('scroll', function() {{
    corner.classList.toggle('dim', window.scrollY > window.innerHeight * 0.6);
  }}, {{passive: true}});
}})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=int, default=1, choices=(1, 2))
    build(ap.parse_args().stage)
