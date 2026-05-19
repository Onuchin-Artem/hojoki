SOURCE = source/hojoki.md
BUILD  = build

.PHONY: all web epub print clean

all: web epub print

web:
	$(MAKE) -C web

epub:
	$(MAKE) -C epub

print:
	$(MAKE) -C print

clean:
	rm -rf $(BUILD)/*
