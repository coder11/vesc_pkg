VESC_TOOL ?= vesc_tool

BUILD_DIR = build

all: $(BUILD_DIR)/balance_ex.vescpkg versioned-pkg

.FORCE:

$(BUILD_DIR)/README.gen.md: README.md version .FORCE
	@mkdir -p $(BUILD_DIR)
	cp $< $@
	VERSION=$$(cat version); \
	GIT_HASH=$$(git rev-parse --short HEAD); \
	sed -i "s/{{VERSION}}/$$VERSION/g" $@; \
	sed -i "s/{{GIT_HASH}}/$$GIT_HASH/g" $@

$(BUILD_DIR)/ui.gen.qml: ui.qml version .FORCE
	@mkdir -p $(BUILD_DIR)
	cp $< $@
	VERSION=$$(cat version); \
	GIT_HASH=$$(git rev-parse --short HEAD); \
	sed -i "s/{{VERSION}}/$$VERSION/g" $@; \
	sed -i "s/{{GIT_HASH}}/$$GIT_HASH/g" $@

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

.PHONY: all clean balance_ex versioned-pkg .FORCE
