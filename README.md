# Думки у Ретрітній Хатинці

Ukrainian translation of *Hōjōki* (方丈記) by Kamo no Chōmei.  
Translated by Artem Onuchin.

See [VISION.md](VISION.md) for project structure and goals.

## Outputs

| Format | Pipeline | Output |
|--------|----------|--------|
| HTML | `web/build_web.py` (pure Python) | `web/index.html` + assets |
| EPUB | `epub/build_epub.py` (pure Python, epubcheck-gated) | `build/hojoki.epub` |
| PDF | Typst (`print/`) | `build/hojoki.pdf` |

## Prerequisites

Everything needed to build is either in the repo (sources, images, fonts) or
installable:

```bash
# PDF
brew install typst

# EPUB
pip3 install pillow          # image optimization
brew install epubcheck       # validation gate (needs Java)

# Web
pip3 install pillow

# optional: CMYK print targets (make -C print cmyk / cover)
brew install ghostscript

# optional: only to regenerate assets/fonts/web/*.woff2 from the print TTFs
pip3 install fonttools brotli
```

Fonts (Arsenal, Cormorant Garamond) are committed under `assets/fonts/` —
TTFs for print, WOFF2 for EPUB. Both families are licensed under the SIL Open
Font License (see `assets/fonts/OFL-*.txt`).

## Build

```bash
make all       # build all formats
make web       # HTML (also copies hojoki.pdf/epub into web/ for download links)
make epub      # EPUB (fails unless epubcheck reports 0 errors)
make print     # PDF
make clean     # remove build/
```

Build order note: `make web` refreshes the downloadable `web/hojoki.pdf` /
`web/hojoki.epub` from `build/`, so run `make print` / `make epub` first if
you want the site downloads updated.

## License

Text and photographs: [CC BY-NC 4.0](LICENSE) © 2026 Artem Onuchin.  
Fonts: SIL OFL 1.1 (Arsenal © Andrij Shevchenko; Cormorant © Christian Thalmann).
