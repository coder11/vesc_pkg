VESC_TOOL ?= vesc_tool

BUILD_DIR = build

all: $(BUILD_DIR)/balance_ex.vescpkg

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

$(BUILD_DIR)/balance_ex.vescpkg: balance_ex $(BUILD_DIR)/README.gen.md $(BUILD_DIR)/ui.gen.qml .FORCE
	@mkdir -p $(BUILD_DIR)
	@cp pkgdesc.qml $(BUILD_DIR)/pkgdesc.qml
	@sed -i 's|property string pkgLisp: "balance.lisp"|property string pkgLisp: "balance_ex/balance.lisp"|g' $(BUILD_DIR)/pkgdesc.qml
	cd $(BUILD_DIR) && $(VESC_TOOL) --buildPkgFromDesc pkgdesc.qml --testPkgDesc 'custom:test' --testPkgDesc 'vesc:test'
	@VERSION=$$(cat version | tr -d '\n'); \
	GIT_HASH=$$(git rev-parse --short HEAD); \
	cp $(BUILD_DIR)/balance_ex.vescpkg $(BUILD_DIR)/balance_ex.v$$VERSION-$$GIT_HASH.vescpkg

balance_ex:
	$(MAKE) -C $@ BUILD_DIR=../$(BUILD_DIR)/balance_ex

clean:
	rm -rf $(BUILD_DIR)
	$(MAKE) -C balance_ex clean BUILD_DIR=../$(BUILD_DIR)/balance_ex

.PHONY: all clean balance_ex .FORCE
