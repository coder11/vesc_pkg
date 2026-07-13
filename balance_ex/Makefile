VESC_TOOL ?= vesc_tool
PYTHON ?= python3

BUILD_DIR = build
GUI_SOURCES := $(shell find gui -type f -name '*.qml')

all: $(BUILD_DIR)/balance_ex.vescpkg versioned-pkg

.FORCE:

$(BUILD_DIR)/README.gen.md: README.md version .FORCE
	@mkdir -p $(BUILD_DIR)
	cp $< $@
	VERSION=$$(cat version); \
	GIT_HASH=$$(git rev-parse --short HEAD); \
	sed -i "s/{{VERSION}}/$$VERSION/g" $@; \
	sed -i "s/{{GIT_HASH}}/$$GIT_HASH/g" $@

$(BUILD_DIR)/ui.gen.qml: $(GUI_SOURCES) python/bundle_qml.py version .FORCE
	@mkdir -p $(BUILD_DIR)
	VERSION=$$(cat version); \
	GIT_HASH=$$(git rev-parse --short HEAD); \
	$(PYTHON) python/bundle_qml.py gui/ui.qml $@ \
		--define VERSION=$$VERSION \
		--define GIT_HASH=$$GIT_HASH

$(BUILD_DIR)/balance_ex.vescpkg: balance_ex $(BUILD_DIR)/README.gen.md $(BUILD_DIR)/ui.gen.qml package.lisp .FORCE
	@mkdir -p $(BUILD_DIR)
	@cp pkgdesc.qml $(BUILD_DIR)/pkgdesc.qml
	@cp package.lisp $(BUILD_DIR)/package.lisp
	cd $(BUILD_DIR) && $(VESC_TOOL) --buildPkgFromDesc pkgdesc.qml --testPkgDesc 'custom:test' --testPkgDesc 'vesc:test'

versioned-pkg: $(BUILD_DIR)/balance_ex.vescpkg version .FORCE
	@VERSION=$$(cat version | tr -d '\n'); \
	GIT_HASH=$$(git rev-parse --short HEAD); \
	cp $(BUILD_DIR)/balance_ex.vescpkg $(BUILD_DIR)/balance_ex.v$$VERSION-$$GIT_HASH.vescpkg

balance_ex:
	$(MAKE) -C $@ BUILD_DIR=../$(BUILD_DIR)/balance_ex

clean:
	rm -rf $(BUILD_DIR)
	$(MAKE) -C balance_ex clean BUILD_DIR=../$(BUILD_DIR)/balance_ex

test-ui:
	qmlscene gui/ui.test.qml

test-python:
	$(PYTHON) -m unittest discover -s python -p 'test_*.py'

.PHONY: all clean balance_ex versioned-pkg test-ui test-python .FORCE
