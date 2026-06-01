TYPST ?= typst
FONTS  = ../assets/fonts/print
SRC    = main.typ
OUT    = ../build/hojoki.pdf
PRINT_OUT = ../build/hojoki-print.pdf
PROOF_OUT = ../build/hojoki-proof.pdf
CMYK_OUT  = ../build/hojoki-print-cmyk.pdf
COVER_OUT = ../build/cover.pdf
COVER_CMYK_OUT = ../build/cover-cmyk.pdf
BLEED ?= 3.175mm   # Mixam interior bleed = 0.125"
SPINE ?= 0.56in    # case-wrap spine width (from Mixam's order)
FRONT ?=           # front-cover artwork path, e.g. /assets/images/cover/front.jpg
GS ?= gs
# Ghostscript RGB->CMYK, max image quality: no downsampling, near-lossless JPEG
# (QFactor 0.1) with no chroma subsampling (HSamples/VSamples 1 1 1 1).
GS_CMYK = $(GS) -q -dBATCH -dNOPAUSE -dSAFER -sDEVICE=pdfwrite \
  -dProcessColorModel=/DeviceCMYK -sColorConversionStrategy=CMYK \
  -dDownsampleColorImages=false -dDownsampleGrayImages=false -dDownsampleMonoImages=false \
  -dAutoFilterColorImages=false -dColorImageFilter=/DCTEncode \
  -dAutoFilterGrayImages=false -dGrayImageFilter=/DCTEncode \
  -dAutoRotatePages=/None -dCompatibilityLevel=1.6
GS_Q = -c "<< /ColorImageDict << /QFactor 0.1 /Blend 1 /HSamples [1 1 1 1] /VSamples [1 1 1 1] >> /GrayImageDict << /QFactor 0.1 /Blend 1 /HSamples [1 1 1 1] /VSamples [1 1 1 1] >> >> setdistillerparams"

.PHONY: all print proof cmyk cover both watch
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
	$(GS_CMYK) -o $(CMYK_OUT) $(GS_Q) -f $(PRINT_OUT)

# Hardcover case-wrap cover spread (back · spine · front). Pass SPINE / FRONT:
#   make -C print cover SPINE=0.56in
# Output build/cover.pdf is CMYK by default (Typst RGB -> Ghostscript CMYK).
cover:
	@mkdir -p ../build
	$(TYPST) compile --root .. --font-path $(FONTS) --input spine=$(SPINE) \
	  $(if $(FRONT),--input front=$(FRONT),) cover.typ ../build/cover-rgb.pdf
	$(GS_CMYK) -o $(COVER_OUT) $(GS_Q) -f ../build/cover-rgb.pdf

both: all print

watch:
	$(TYPST) watch --root .. --font-path $(FONTS) $(SRC) $(OUT)
