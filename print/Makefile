TYPST ?= typst
FONTS  = ../assets/fonts/print
SRC    = main.typ
OUT    = ../build/hojoki.pdf
PRINT_OUT = ../build/hojoki-print.pdf
PROOF_OUT = ../build/hojoki-proof.pdf
CMYK_OUT  = ../build/hojoki-print-cmyk.pdf
BLEED ?= 3.175mm   # Mixam interior bleed = 0.125"
GS ?= gs

.PHONY: all print proof cmyk both watch
# Screen / review PDF — trim size, no bleed.
all:
	@mkdir -p ../build
	$(TYPST) compile --root .. --font-path $(FONTS) $(SRC) $(OUT)

# Print-ready interior for upload — adds bleed, NO crop marks (Mixam trims to page size).
print:
	@mkdir -p ../build
	$(TYPST) compile --root .. --font-path $(FONTS) --input bleed=$(BLEED) $(SRC) $(PRINT_OUT)

# Proof copy — bleed + trim/crop marks, to eyeball trim & bleed. Do NOT upload this one.
proof:
	@mkdir -p ../build
	$(TYPST) compile --root .. --font-path $(FONTS) --input bleed=$(BLEED) --input marks=true $(SRC) $(PROOF_OUT)

# CMYK conversion of the bleed interior via Ghostscript (Typst outputs RGB).
# Keeps full image resolution; review the result before upload (reds/greys can shift).
cmyk: print
	$(GS) -q -dBATCH -dNOPAUSE -dSAFER \
	  -sDEVICE=pdfwrite \
	  -dProcessColorModel=/DeviceCMYK \
	  -sColorConversionStrategy=CMYK \
	  -dDownsampleColorImages=false -dDownsampleGrayImages=false -dDownsampleMonoImages=false \
	  -dAutoRotatePages=/None -dCompatibilityLevel=1.6 \
	  -o $(CMYK_OUT) $(PRINT_OUT)

both: all print

watch:
	$(TYPST) watch --root .. --font-path $(FONTS) $(SRC) $(OUT)
