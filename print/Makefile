TYPST ?= typst
FONTS  = ../assets/fonts/print
SRC    = main.typ
OUT    = ../build/hojoki.pdf

.PHONY: all watch
all:
	@mkdir -p ../build
	$(TYPST) compile --root .. --font-path $(FONTS) $(SRC) $(OUT)

watch:
	$(TYPST) watch --root .. --font-path $(FONTS) $(SRC) $(OUT)
