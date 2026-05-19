# Думки у Ретрітній Хатинці

Ukrainian translation of *Hōjōki* (方丈記) by Kamo no Chōmei.  
Translated by Artem Onuchin.

See [VISION.md](VISION.md) for project structure and goals.

## Outputs

| Format | Pipeline |
|--------|----------|
| HTML | Pandoc |
| EPUB | Pandoc |
| PDF | Typst |

## Build

```bash
make all       # build all formats
make web       # HTML only
make epub      # EPUB only
make print     # PDF only
make clean     # remove build/
```

## License

[CC BY-NC 4.0](LICENSE) © 2026 Artem Onuchin
