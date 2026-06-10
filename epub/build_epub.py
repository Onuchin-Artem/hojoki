#!/usr/bin/env python3
"""Build the EPUB 3 edition of «Думки у ретрітній хатинці» from source/*.md.

Pure-Python (no pandoc): EPUB twin of print/tools/build_body.py and
web/build_web.py — same sources, same marker semantics (see
EPUB_REQUIREMENTS_v2.md). Whitespace is carried over verbatim: NBSP (U+00A0),
em-dash (U+2014) and the ʼ apostrophe are never normalised; the only
transformation is the idempotent " —" -> NBSP+"—" (as nbsp() in print).

  source/hojoki.md     -> front matter + title + 15 verse chapters
  source/footnotes.md  -> «Примітки» endnotes (lemma quotes dropped; «Джерела»
                          omitted — web-only, like print)
  source/captions.md   -> photo-section descriptions (хатинка, Амітабга)
  source/colophon.md   -> colophon
  assets/…             -> optimised JPEGs, WOFF2 fonts, cover

Output: build/hojoki.epub (single file, overwritten each build).
The build fails unless epubcheck reports 0 errors.

Run from anywhere:  python3 epub/build_epub.py
"""
import datetime
import html
import pathlib
import re
import shutil
import subprocess
import sys
import zipfile

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
STAGE = BUILD / "epub-src"          # expanded container, kept for inspection
OEBPS = STAGE / "OEBPS"

BOOK_UUID = "5639a7c5-e551-4c05-a92a-ed0de2fb8b1f"   # stable edition id — do not regenerate

# back-cover description from the print edition (print/cover.typ), verse omitted
DESCRIPTION = ("Класичний твір японської літератури, написаний 1212 року. "
               "Монах-самітник згадує страждання, лиха і втрати, які випали на "
               "його власне життя. Попри це він знаходить спокій у самотньому "
               "житті, опорі на себе, єднанні з природою і зосередженні на "
               "духовній практиці.")

SIG_OPENERS = ("Артем Онучін", "Написано монахом")

# epub-only line breaks in the signature, same as the web's SIG_BREAKS
# (source stays one line for print)
SIG_BREAKS = {"написано під час роботи над перекладом": "написано під час роботи\nнад перекладом"}

# ── shared text helpers ───────────────────────────────────────────────────────

def nbsp(s):
    """NBSP before em-dash; idempotent (existing NBSP are left alone)."""
    return s.replace(" —", " —")

def strip_breaks(line):
    """Print hard-break artefacts (' \\' mid-line) -> reflow space."""
    return re.sub(r"\s*\\\s*", " ", line).strip()

def inline(s):
    """Inline markdown -> XHTML. Escapes markup; NBSP survive html.escape."""
    s = html.escape(s, quote=False)
    s = nbsp(s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)            # links -> text (print parity)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    return s

# ── parse source/hojoki.md ────────────────────────────────────────────────────

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

def parse_verse(body):
    """Blocks: ('stanza', lines, indent, hang, gap_before) — print markers
    `---`/`===`/`~Nmm` are page geometry and are dropped; bare `~` is the one
    semantic gap; `>`/`>Nem` indents the next stanza; `>>` hangs it."""
    blocks, cur = [], []
    indent, hang, gap = None, None, False
    def flush():
        nonlocal cur, indent, hang, gap
        if cur:
            blocks.append(("stanza", cur, indent, hang, gap))
            cur, indent, hang, gap = [], None, None, False
    for raw in body:
        s = raw.strip()
        if s == "":
            flush(); continue
        if s == "~":                                   # semantic gap after the stanza
            flush(); gap = True; continue
        if s == "---" or s == "===" or re.fullmatch(r"~\s*[\d.]+\s*(em|mm|pt|cm)?", s):
            flush(); continue                          # print-only markers
        mh = re.fullmatch(r">>\s*([\d.]+em)?", s)
        if mh:
            flush(); hang = mh.group(1) or "2em"; continue
        mi = re.fullmatch(r">\s*([\d.]+em)?", s)
        if mi:
            flush(); indent = mi.group(1) or "2em"; continue
        cur.append(s)
    flush()
    return blocks

def parse_prose(body):
    paras, cur = [], []
    for raw in body:
        if raw.strip() in ("", "---"):
            if cur:
                paras.append(" ".join(cur)); cur = []
        else:
            cur.append(strip_breaks(raw))
    if cur:
        paras.append(" ".join(cur))
    return paras

def split_signature(body):
    """Trailing author/monk colophon -> (poem_lines, [signature blocks])."""
    idx = next((i for i, l in enumerate(body)
                if any(l.strip().startswith(o) for o in SIG_OPENERS)), None)
    if idx is None:
        return body, []
    blocks, cur = [], []
    for l in body[idx:]:
        if l.strip() == "":
            if cur:
                blocks.append(cur); cur = []
        else:
            cur.append(l.strip())
    if cur:
        blocks.append(cur)
    return body[:idx], blocks

# ── endnotes ──────────────────────────────────────────────────────────────────

def note_order(src_text):
    order = []
    for m in re.finditer(r"\[\^([^\]]+)\]", src_text):
        if m.group(1) not in order:
            order.append(m.group(1))
    return order

def parse_footnotes():
    """{key: [html blocks]} — lemma quote dropped, «Джерела» omitted."""
    raw = (ROOT / "source/footnotes.md").read_text(encoding="utf-8")
    notes_src = re.split(r"(?m)^#\s+Джерела\s*$", raw)[0]
    notes = {}
    matches = list(re.finditer(r"(?m)^\[\^([^\]]+)\]:[ \t]?(.*)$", notes_src))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(notes_src)
        block = m.group(2) + notes_src[m.end():end]
        text = "\n".join(re.sub(r"^[ \t]{1,4}", "", l) for l in block.splitlines())
        q = re.match(r"\s*\*(.+?)\*", text, flags=re.DOTALL)   # leading *…* lemma
        if q:
            text = text[q.end():]
        notes[m.group(1)] = md_blocks(text)
    return notes

def md_blocks(text):
    """Markdown body -> XHTML <p>/<ul>; `---` (print page split) = block break."""
    out, para, lst = [], [], []
    def flush_para():
        if para:
            out.append("<p>%s</p>" % inline(strip_breaks(" ".join(para)))); para.clear()
    def flush_list():
        if lst:
            out.append("<ul>%s</ul>" % "".join(
                "<li>%s</li>" % inline(strip_breaks(x)) for x in lst)); lst.clear()
    for ln in text.splitlines():
        s = ln.strip()
        if s in ("", "---"):
            flush_para(); flush_list()
        elif re.match(r"^-\s+", s):
            flush_para(); lst.append(re.sub(r"^-\s+", "", s))
        else:
            flush_list(); para.append(s)
    flush_para(); flush_list()
    return out

# ── captions ──────────────────────────────────────────────────────────────────

def parse_captions():
    raw = (ROOT / "source/captions.md").read_text(encoding="utf-8")
    blocks, cur_name, cur = {}, None, []
    for ln in raw.splitlines():
        m = re.match(r"^\*\*«([^»]+)»\*\*\s*$", ln.strip())
        if m:
            if cur_name:
                blocks[cur_name] = parse_prose(cur)
            cur_name, cur = m.group(1), []
        elif cur_name is not None:
            cur.append(ln)
    if cur_name:
        blocks[cur_name] = parse_prose(cur)
    return blocks

# ── XHTML rendering ───────────────────────────────────────────────────────────

XHTML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="uk" lang="uk">
<head>
<title>{title}</title>
<link rel="stylesheet" type="text/css" href="css/style.css"/>
</head>
<body{body_attrs}>
{content}
</body>
</html>
"""

def page(title, content, body_class="", epub_type=""):
    attrs = ""
    if body_class:
        attrs += ' class="%s"' % body_class
    if epub_type:
        attrs += ' epub:type="%s"' % epub_type
    out = XHTML.format(title=html.escape(title), body_attrs=attrs, content=content)
    if body_class:   # mirror the class on <html> so page bg fills the full page
        out = out.replace('xml:lang="uk" lang="uk">',
                          'xml:lang="uk" lang="uk" class="%s">' % body_class, 1)
    return out

class Refs:
    """Footnote markers -> noteref anchors; remembers which file holds each."""
    def __init__(self, order):
        self.order = order
        self.location = {}        # key -> chapter file
        self.current_file = None
    def sub(self, text):
        def repl(m):
            key = m.group(1)
            n = self.order.index(key) + 1
            self.location.setdefault(key, self.current_file)
            return ('<a class="noteref" epub:type="noteref" role="doc-noteref" '
                    'id="fnref-%d" href="notes.xhtml#fnbody-%d" aria-label="Примітка %d">%d</a>'
                    % (n, n, n, n))
        return re.sub(r"\[\^([^\]]+)\]", repl, text)

def render_verse(blocks, refs):
    out = ['<div class="verse">']
    for kind, lines, indent, hang, gap in blocks:
        cls = "stanza"
        style = ""
        if gap:
            cls += " after-gap"
        if indent:
            cls += " indent"
            style = ' style="margin-left:%s"' % indent
        if hang:
            cls += " hang"
            style = ' style="padding-left:%s;text-indent:-%s"' % (hang, hang)
        lns = "".join('<span class="line">%s</span>' % refs.sub(inline(l))
                      for l in lines)
        out.append('<p class="%s"%s>%s</p>' % (cls, style, lns))
    out.append("</div>")
    return "\n".join(out)

def render_credit(blocks):
    def lines(b):
        for l in b:
            for a, c in SIG_BREAKS.items():
                l = l.replace(a, c)
            yield from l.split("\n")
    inner = "".join(
        "<p>%s</p>" % "".join('<span class="line">%s</span>' % inline(l) for l in lines(b))
        for b in blocks)
    return '<div class="credit">%s</div>' % inner

def figure_html(name, img, alt, paras):
    cap = ""
    if name or paras:
        desc = "".join("<p>%s</p>" % inline(p) for p in paras)
        cap = ('<figcaption><p class="fig-name">«%s»</p>'
               '<div class="fig-desc">%s</div></figcaption>'
               % (html.escape(name), desc))
    return ('<figure class="illus"><img src="img/%s" alt="%s"/>%s</figure>'
            % (img, html.escape(alt, quote=True), cap))

# ── images ────────────────────────────────────────────────────────────────────

def optimize_jpeg(src, dst, long_side=1600, quality=82):
    img = Image.open(src).convert("RGB")
    w, h = img.size
    scale = long_side / max(w, h)
    if scale < 1:
        img = img.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
    img.save(dst, "JPEG", quality=quality, optimize=True, progressive=True)
    return img.size

def make_cover(src, dst):
    img = Image.open(src).convert("RGB")
    scale = min(1600 / img.width, 2560 / img.height, 1)
    if scale < 1:
        img = img.resize((round(img.width * scale), round(img.height * scale)),
                         Image.LANCZOS)
    img.save(dst, "JPEG", quality=84, optimize=True, progressive=True)

def make_enso(src, dst, width=900):
    """Ink-on-white scan -> transparent PNG (alpha from luminance), so the ensō
    sits on the fixed light page with no white box (same trick as the web)."""
    e = Image.open(src).convert("L")
    h = round(e.height * width / e.width)
    e = e.resize((width, h), Image.LANCZOS)
    alpha = e.point(lambda l: max(0, min(255, int((250 - l) * 1.4))))
    out = Image.merge("LA", (e.point(lambda l: min(l, 60)), alpha))
    out.save(dst, "PNG", optimize=True)

# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = """/* «Думки у ретрітній хатинці» — EPUB edition. GENERATED by epub/build_epub.py. */

@font-face {
  font-family: "Arsenal";
  font-weight: normal; font-style: normal; font-display: swap;
  src: url("../fonts/Arsenal-Regular.woff2") format("woff2");
}
@font-face {
  font-family: "Arsenal";
  font-weight: bold; font-style: normal; font-display: swap;
  src: url("../fonts/Arsenal-Bold.woff2") format("woff2");
}
@font-face {
  font-family: "Arsenal";
  font-weight: normal; font-style: italic; font-display: swap;
  src: url("../fonts/Arsenal-Italic.woff2") format("woff2");
}
@font-face {
  font-family: "Cormorant Garamond";
  font-weight: 500; font-style: normal; font-display: swap;
  src: url("../fonts/CormorantGaramond-Medium.woff2") format("woff2");
}

/* left-aligned everywhere, never justified, never hyphenated */
body {
  font-family: "Arsenal", sans-serif;
  line-height: 1.55;
  text-align: left;
  hyphens: none; -webkit-hyphens: none; -epub-hyphens: none;
  adobe-hyphenate: none;
  margin: 0; padding: 0.3em 0.5em;
  orphans: 2; widows: 2;
}
h1, h2, p { text-align: left; }

/* section/chapter headers: Arsenal bold red, left */
h2.section-title {
  font-family: "Arsenal", sans-serif;
  font-weight: bold;
  font-size: 1.5em;
  color: #e46340;
  margin: 1.2em 0 1.3em;
}

/* poem: the larger of the three body sizes */
.verse { font-size: 0.95em; }       /* poem: 11.4pt at the 12pt default */
.stanza {
  break-inside: avoid; page-break-inside: avoid;
  margin: 0 0 1.4em;
}
.stanza .line { display: block; }
.after-gap { margin-top: 3.4em; }     /* the one semantic `~` gap (~2em extra) */

/* prose (front/back matter): 2pt smaller than the poem
   one size for ALL front/back matter (foreword, gratitude, notes, colophon,
   photo captions): 0.70em = 8.4pt at the 12pt default */
.prose, ol.note-list, .fig-desc, nav#toc ol { font-size: 0.70em; }
.renunciation .verse { font-size: 0.70em; }   /* «Зречення» reads at matter size */
/* …and its title matches the other front-matter titles (1.5em × 0.70) */
.renunciation .section-title { font-size: 1.05em; }
.prose p { margin: 0 0 0.9em; }

/* author signature / credit: smaller, italic, grey, right */
.credit {
  margin-top: 2.5em;
  font-size: 0.625em;               /* 7.5pt at the 12pt default */
  font-style: italic;
  color: #646161;
  text-align: right;
}
.credit p { text-align: right; margin: 0 0 1em; }
.credit .line { display: block; }

/* title page — centred vertically (flex+vh; older readers fall back to top) */
.title-page {
  height: 92vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.title-author { font-size: 1.25em; color: #e46340; margin: 0 0 0.6em; }
h1.book-title {
  font-family: "Cormorant Garamond", serif;
  font-weight: 500;
  font-size: 2.3em;
  line-height: 1.15;
  color: #252120;
  margin: 0 0 0.8em;
}
.title-translator { font-size: 0.95em; color: #646161; text-align: right; margin: 1.4em 0 0; }

/* cover */
body.cover-page { margin: 0; padding: 0; text-align: center; }
.cover-figure { margin: 0; padding: 0; text-align: center; }
.cover-figure img { max-width: 100%; max-height: 100%; }

/* toc page */
nav#toc ol { list-style: none; padding-left: 0; }
nav#toc li { margin: 0.35em 0; }
nav#toc a { text-decoration: none; color: inherit; }

/* photo sections: transparent page bg (reader theme shows through);
   the illustration block is framed with a border instead */
body.photo { padding: 0 1em 1.2em; }
/* top gap lives on the figure, not body padding — Books strips body padding */
body.photo > .illus { margin-top: 5%; }
.illus {
  margin: 0 0 2em;
  text-align: center;
  border: 1px solid #8c8880;
  padding: 1.2em 1em;
}
/* photo: 75% of page width; height cap 70vh — Books' page content area is
   ~80-85% of the window that vh measures, so 70vh ≈ 85% of the real page.
   Higher caps make the photo overflow and get sliced across pages. */
.illus img {
  max-width: 75%; max-height: 70vh; width: auto; height: auto;
  break-inside: avoid; page-break-inside: avoid;
}
.illus { break-inside: avoid; page-break-inside: avoid; }
/* diptych: no frame; each photo on its own page, vertically centred */
.dip-page {
  height: 75vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
.dip-page + .dip-page { break-before: page; page-break-before: always; }
.dip-page .illus { border: none; padding: 0; margin: 0; }
.dip-page .illus img { max-height: 65vh; }
.illus figcaption { margin-top: 1em; text-align: left; }
.fig-name {
  font-weight: bold;
  color: #e46340;
  text-align: right;
  margin: 0.6em 0 1em;
}
.fig-desc p { margin: 0 0 0.9em; }

/* endnotes */
.noteref {
  font-size: 0.72em;
  vertical-align: super;
  line-height: 0;
  text-decoration: none;
}
ol.note-list { padding-left: 1.6em; }
li.note { margin: 0 0 1.6em; }
li.note p { margin: 0 0 0.8em; }
li.note ul { margin: 0 0 0.8em; padding-left: 1.2em; }
a.fn-back { text-decoration: none; }

/* colophon */
.colophon p { margin: 0 0 0.9em; }
.colophon .line { display: block; }
.colophon .cc-badge { margin-top: 1.6em; }
.colophon .cc-badge img { height: 1.6em; width: auto; }

/* ensō: transparent PNG ink on the reader's own page background */
body.enso-page { text-align: center; }
.enso-fig { margin: 30% 0 0; text-align: center; }
.enso-fig img { width: 55%; max-width: 100%; height: auto; }
"""

# ── container / package files ─────────────────────────────────────────────────

CONTAINER_XML = """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""

def build():
    src_text = (ROOT / "source/hojoki.md").read_text(encoding="utf-8")
    sections = list(split_sections(src_text.splitlines()))
    bt = next(i for i, s in enumerate(sections) if "book-title" in s[1])
    front = sections[:bt]
    book_title = sections[bt][0]
    body = sections[bt + 1:]
    captions = parse_captions()
    order = note_order(src_text)
    notes = parse_footnotes()
    refs = Refs(order)

    missing = [k for k in order if k not in notes]
    if missing:
        sys.exit("missing footnote definitions: %s" % missing)

    # staging dirs -------------------------------------------------------------
    if STAGE.exists():
        shutil.rmtree(STAGE)
    for d in ("css", "fonts", "img"):
        (OEBPS / d).mkdir(parents=True)
    (STAGE / "META-INF").mkdir()
    (STAGE / "mimetype").write_text("application/epub+zip", encoding="ascii")
    (STAGE / "META-INF/container.xml").write_text(CONTAINER_XML, encoding="utf-8")
    (OEBPS / "css/style.css").write_text(CSS, encoding="utf-8")

    # fonts ----------------------------------------------------------------------
    fonts = sorted((ROOT / "assets/fonts/web").glob("*.woff2"))
    if not fonts:
        sys.exit("no WOFF2 fonts in assets/fonts/web — convert them first")
    for f in fonts:
        shutil.copy2(f, OEBPS / "fonts" / f.name)
    # OFL requires shipping the license with the embedded fonts
    font_licenses = sorted((ROOT / "assets/fonts").glob("OFL-*.txt"))
    for lic in font_licenses:
        shutil.copy2(lic, OEBPS / "fonts" / lic.name)

    # images ---------------------------------------------------------------------
    P = ROOT / "assets/images/processed"
    make_cover(ROOT / "assets/cover/front-cover.jpg", OEBPS / "img/cover.jpg")
    for src, dst in [("retreat-hut.jpeg", "retreat-hut.jpg"),
                     ("Amitabha.jpeg", "amitabha.jpg"),
                     ("Clouds.jpeg", "clouds.jpg"),
                     ("Monks.jpeg", "monks.jpg")]:
        optimize_jpeg(P / src, OEBPS / "img" / dst)
    make_enso(P / "ensho.jpg", OEBPS / "img/enso.png")
    shutil.copy2(P / "by-nc.png", OEBPS / "img/by-nc.png")

    # documents -------------------------------------------------------------------
    docs = []      # (filename, title, xhtml, in_toc)

    docs.append(("cover.xhtml", "Обкладинка", page(
        "Думки у ретрітній хатинці",
        '<figure class="cover-figure"><img src="img/cover.jpg" '
        'alt="Обкладинка книги «Думки у ретрітній хатинці» з каліграфією Ходзьокі"/></figure>',
        body_class="cover-page", epub_type="cover"), False))

    docs.append(("nav.xhtml", "Зміст", None, False))   # placeholder, written below

    # front matter
    for t, a, b in front:
        if t == "Зречення":
            poem, sig = split_signature(b)
            content = ('<section epub:type="frontmatter" class="renunciation">'
                       '<h2 class="section-title">%s</h2>%s%s</section>'
                       % (html.escape(t), render_verse(parse_verse(poem), refs),
                          render_credit(sig)))
            docs.append(("renunciation.xhtml", t, page(t, content), False))
        else:
            paras = "".join("<p>%s</p>" % inline(p) for p in parse_prose(b))
            fname = {"Передмова": "foreword.xhtml", "Подяка": "gratitude.xhtml"}[t]
            content = ('<section epub:type="frontmatter" class="prose">'
                       '<h2 class="section-title">%s</h2>%s</section>'
                       % (html.escape(t), paras))
            docs.append((fname, t, page(t, content), False))

    # title page
    docs.append(("titlepage.xhtml", book_title, page(book_title,
        '<section class="title-page" epub:type="titlepage">'
        '<p class="title-author">Камо но Тьомей</p>'
        '<h1 class="book-title">%s</h1>'
        '<p class="title-translator">Переклад з англійської — Артем Онучін</p>'
        '</section>' % html.escape(book_title)), False))

    # retreat-hut photo section
    docs.append(("photo-hut.xhtml", "«Ретрітна хатинка»", page(
        "«Ретрітна хатинка»",
        figure_html("Ретрітна хатинка", "retreat-hut.jpg",
                    "Ретрітна хатинка в центрі Garchen Buddhist Institute серед пагорбів Арізони",
                    captions.get("Ретрітна хатинка", [])),
        body_class="photo"), False))

    # body chapters (Амітабга photo section before «Моя маленька хатинка»)
    for i, (t, a, b) in enumerate(body, start=1):
        fname = "ch%02d.xhtml" % i
        if t.replace(" ", " ") == "Моя маленька хатинка":
            docs.append(("photo-amitabha.xhtml", "«Амітабга»", page(
                "«Амітабга»",
                figure_html("Амітабга", "amitabha.jpg",
                            "Статуя Будди Амітабги в ретрітному центрі Garchen Buddhist Institute",
                            captions.get("Амітабга", [])),
                body_class="photo"), False))
        refs.current_file = fname
        poem, sig = split_signature(b)
        content = ('<section epub:type="chapter">'
                   '<h2 class="section-title">%s</h2>%s%s</section>'
                   % (html.escape(t), render_verse(parse_verse(poem), refs),
                      render_credit(sig) if sig else ""))
        docs.append((fname, t, page(t, content), True))

    # diptych (no captions — like print)
    docs.append(("photo-diptych.xhtml", "Хмари і монахи", page(
        "Хмари і монахи",
        '<div class="dip-page">%s</div><div class="dip-page">%s</div>' % (
            figure_html("", "clouds.jpg", "Хмари над горами", []),
            figure_html("", "monks.jpg", "Монахи на ретріті", [])),
        body_class="photo"), False))

    # endnotes
    items = []
    for n, key in enumerate(order, start=1):
        back_to = refs.location.get(key, "ch01.xhtml")
        back = ('<p><a class="fn-back" epub:type="backlink" role="doc-backlink" '
                'href="%s#fnref-%d">↩ повернутися до тексту</a></p>' % (back_to, n))
        # role="doc-endnote" is deprecated in DPUB-ARIA 1.1 — epub:type alone
        # noterefs target the inner note-body div, so reader popups (Books/Kobo)
        # show only the note text; the backlink stays outside it = appendix-only
        items.append('<li class="note" id="fn-%d" epub:type="endnote">'
                     '<div class="note-body" id="fnbody-%d">%s</div>%s</li>'
                     % (n, n, "".join(notes[key]), back))
    notes_content = ('<section epub:type="backmatter endnotes" role="doc-endnotes">'
                     '<h2 class="section-title">Примітки</h2>'
                     '<ol class="note-list">%s</ol></section>' % "".join(items))
    if re.search(r"[぀-ヿ一-鿿]", notes_content):
        sys.exit("Japanese kana/kanji found in notes — project standard forbids them")
    docs.append(("notes.xhtml", "Примітки", page("Примітки", notes_content), False))

    # colophon — line breaks are authored design, keep them (blank line = block gap)
    colo_blocks, cur = [], []
    for ln in (ROOT / "source/colophon.md").read_text(encoding="utf-8").splitlines():
        if ln.strip() == "":
            if cur:
                colo_blocks.append(cur); cur = []
        else:
            cur.append(ln.strip())
    if cur:
        colo_blocks.append(cur)
    colo = "".join(
        "<p>%s</p>" % "".join('<span class="line">%s</span>' % inline(l) for l in b)
        for b in colo_blocks)
    colo += ('<p class="cc-badge"><img src="img/by-nc.png" alt="CC BY-NC 4.0"/></p>')
    docs.append(("colophon.xhtml", "Колофон", page(
        "Колофон",
        '<section class="colophon prose" epub:type="backmatter colophon">'
        '<h2 class="section-title">Колофон</h2>%s</section>' % colo), False))

    # ensō — final page
    docs.append(("enso.xhtml", "Енсо", page(
        "Енсо",
        '<figure class="enso-fig"><img src="img/enso.png" alt="Енсо — каліграфічне коло"/></figure>',
        body_class="enso-page"), False))

    # nav.xhtml: visible TOC = chapters only, starting with «Пролог».
    # bodymatter landmark points at the cover so readers open the book there
    # (departure from §5 of the requirements — user's call, 2026-06-10)
    toc_items = "".join('<li><a href="%s">%s</a></li>' % (f, html.escape(t))
                        for f, t, x, in_toc in docs if in_toc)
    nav_content = (
        '<nav epub:type="toc" role="doc-toc" id="toc">'
        '<h2 class="section-title">Зміст</h2><ol>%s</ol></nav>\n'
        '<nav epub:type="landmarks" hidden="hidden"><h2>Орієнтири</h2><ol>'
        '<li><a epub:type="cover" href="cover.xhtml">Обкладинка</a></li>'
        '<li><a epub:type="toc" href="nav.xhtml">Зміст</a></li>'
        '<li><a epub:type="bodymatter" href="cover.xhtml">Початок</a></li>'
        '</ol></nav>' % toc_items)
    docs[1] = ("nav.xhtml", "Зміст", page("Зміст", nav_content), False)

    for fname, t, xhtml, _ in docs:
        (OEBPS / fname).write_text(xhtml, encoding="utf-8")

    # NCX (legacy nav) ----------------------------------------------------------
    navpoints = "".join(
        '<navPoint id="np-%d" playOrder="%d"><navLabel><text>%s</text></navLabel>'
        '<content src="%s"/></navPoint>'
        % (n, n, html.escape(t), f)
        for n, (f, t, x, in_toc) in enumerate(
            [d for d in docs if d[3]], start=1))
    ncx = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="uk">'
           '<head><meta name="dtb:uid" content="urn:uuid:%s"/>'
           '<meta name="dtb:depth" content="1"/>'
           '<meta name="dtb:totalPageCount" content="0"/>'
           '<meta name="dtb:maxPageNumber" content="0"/></head>'
           '<docTitle><text>Думки у ретрітній хатинці</text></docTitle>'
           '<navMap>%s</navMap></ncx>' % (BOOK_UUID, navpoints))
    (OEBPS / "toc.ncx").write_text(ncx, encoding="utf-8")

    # OPF -------------------------------------------------------------------------
    modified = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest, spine = [], []
    for n, (fname, t, x, _) in enumerate(docs):
        props = ' properties="nav"' if fname == "nav.xhtml" else ""
        iid = "doc-%s" % fname.replace(".xhtml", "")
        manifest.append('<item id="%s" href="%s" media-type="application/xhtml+xml"%s/>'
                        % (iid, fname, props))
        spine.append('<itemref idref="%s"/>' % iid)
    manifest.append('<item id="css" href="css/style.css" media-type="text/css"/>')
    manifest.append('<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>')
    manifest.append('<item id="cover-img" href="img/cover.jpg" media-type="image/jpeg" properties="cover-image"/>')
    for img in sorted((OEBPS / "img").iterdir()):
        if img.name == "cover.jpg":
            continue
        mt = "image/png" if img.suffix == ".png" else "image/jpeg"
        manifest.append('<item id="img-%s" href="img/%s" media-type="%s"/>'
                        % (img.stem.replace(".", "-"), img.name, mt))
    for f in fonts:
        manifest.append('<item id="font-%s" href="fonts/%s" media-type="font/woff2"/>'
                        % (f.stem.lower().replace(".", "-"), f.name))
    for lic in font_licenses:
        manifest.append('<item id="lic-%s" href="fonts/%s" media-type="text/plain"/>'
                        % (lic.stem.lower(), lic.name))

    opf = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" '
           'unique-identifier="uid" xml:lang="uk">\n'
           '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
           '<dc:identifier id="uid">urn:uuid:%s</dc:identifier>\n'
           '<dc:title>Думки у ретрітній хатинці</dc:title>\n'
           '<dc:language>uk</dc:language>\n'
           '<dc:creator id="aut">Камо но Тьомей</dc:creator>\n'
           '<meta refines="#aut" property="role" scheme="marc:relators">aut</meta>\n'
           '<dc:contributor id="trl">Артем Онучін</dc:contributor>\n'
           '<meta refines="#trl" property="role" scheme="marc:relators">trl</meta>\n'
           '<dc:description>%s</dc:description>\n'
           '<dc:rights>© Артем Онучін, 2026. CC BY-NC 4.0</dc:rights>\n'
           '<dc:date>2026</dc:date>\n'
           '<meta property="dcterms:modified">%s</meta>\n'
           '<meta name="cover" content="cover-img"/>\n'
           '<meta property="schema:accessMode">textual</meta>\n'
           '<meta property="schema:accessMode">visual</meta>\n'
           '<meta property="schema:accessModeSufficient">textual,visual</meta>\n'
           '<meta property="schema:accessModeSufficient">textual</meta>\n'
           '<meta property="schema:accessibilityFeature">tableOfContents</meta>\n'
           '<meta property="schema:accessibilityFeature">structuralNavigation</meta>\n'
           '<meta property="schema:accessibilityHazard">none</meta>\n'
           '<meta property="schema:accessibilitySummary">'
           'Поетичний текст із змістом, наскрізною навігацією та примітками '
           'з двосторонніми посиланнями.</meta>\n'
           '</metadata>\n'
           '<manifest>\n%s\n</manifest>\n'
           '<spine toc="ncx">\n%s\n</spine>\n'
           '</package>\n'
           % (BOOK_UUID, html.escape(DESCRIPTION), modified,
              "\n".join(manifest), "\n".join(spine)))
    (OEBPS / "content.opf").write_text(opf, encoding="utf-8")

    # zip ---------------------------------------------------------------------------
    BUILD.mkdir(exist_ok=True)
    out = BUILD / "hojoki.epub"
    with zipfile.ZipFile(out, "w") as z:
        z.write(STAGE / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
        for p in sorted(STAGE.rglob("*")):
            if p.is_file() and p.name != "mimetype":
                z.write(p, p.relative_to(STAGE).as_posix(),
                        compress_type=zipfile.ZIP_DEFLATED)
    # epubcheck — the build is good only at 0 errors --------------------------------
    res = subprocess.run(["epubcheck", str(out)], capture_output=True, text=True)
    print(res.stdout.strip())
    if res.returncode != 0:
        print(res.stderr.strip(), file=sys.stderr)
        sys.exit("epubcheck FAILED — see messages above")

    size = out.stat().st_size / 1024 / 1024
    print("OK: build/%s (%.1f MB)" % (out.name, size))

if __name__ == "__main__":
    build()
