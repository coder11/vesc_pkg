VESC_TOOL ?= vesc_tool
PYTHON ?= python3

BUILD_DIR = build
GUI_SOURCES := $(shell find gui -type f -name '*.qml' ! -name 'ui.bundle.qml')

all: $(BUILD_DIR)/balance_ex.vescpkg

.FORCE:

$(BUILD_DIR)/README.gen.md: README.md version .FORCE
	@mkdir -p $(BUILD_DIR)
	cp $< $@
	VERSION=$$(cat version); \
	sed -i "s/{{VERSION}}/$$VERSION/g" $@

$(BUILD_DIR)/ui.gen.qml: gui/ui.bundle.qml version .FORCE
	@mkdir -p $(BUILD_DIR)
	cp $< $@
	VERSION=$$(cat version); \
	sed -i "s/{{VERSION}}/$$VERSION/g" $@

$(BUILD_DIR)/balance_ex.vescpkg: balance_ex $(BUILD_DIR)/README.gen.md $(BUILD_DIR)/ui.gen.qml package.lisp .FORCE
	@mkdir -p $(BUILD_DIR)
	@cp pkgdesc.qml $(BUILD_DIR)/pkgdesc.qml
	@cp package.lisp $(BUILD_DIR)/package.lisp
	cd $(BUILD_DIR) && $(VESC_TOOL) --buildPkgFromDesc pkgdesc.qml --testPkgDesc 'custom:test' --testPkgDesc 'vesc:test'

generate-qml-bundle: $(GUI_SOURCES) python/bundle_qml.py
	$(PYTHON) python/bundle_qml.py gui/ui.qml gui/ui.bundle.qml

generate-settings:
	$(PYTHON) python/generate_settings.py

balance_ex:
	$(MAKE) -C $@ BUILD_DIR=../$(BUILD_DIR)/balance_ex

clean:
	rm -rf $(BUILD_DIR)
	$(MAKE) -C balance_ex clean BUILD_DIR=../$(BUILD_DIR)/balance_ex

dev-ui:
	qmlscene gui/ui.dev.qml

test-python:
	$(PYTHON) -m unittest discover -s python -p 'test_*.py'

.PHONY: all clean balance_ex generate-qml-bundle generate-settings dev-ui test-python .FORCE
