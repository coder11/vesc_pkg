VESC_TOOL ?= vesc_tool

all: balance_ex.vescpkg

README.gen.md: README.md version
	cp $< $@
	VERSION=$$(cat version); \
	GIT_HASH=$$(git rev-parse --short HEAD); \
	sed -i "s/{{VERSION}}/$$VERSION/g" $@; \
	sed -i "s/{{GIT_HASH}}/$$GIT_HASH/g" $@

ui.gen.qml: ui.qml version
	cp $< $@
	VERSION=$$(cat version); \
	GIT_HASH=$$(git rev-parse --short HEAD); \
	sed -i "s/{{VERSION}}/$$VERSION/g" $@; \
	sed -i "s/{{GIT_HASH}}/$$GIT_HASH/g" $@

balance_ex.vescpkg: balance_ex README.gen.md ui.gen.qml
	$(VESC_TOOL) --buildPkgFromDesc pkgdesc.qml --testPkgDesc 'custom:test' --testPkgDesc 'vesc:test'
	@mkdir -p build
	@VERSION=$$(cat version | tr -d '\n'); \
	GIT_HASH=$$(git rev-parse --short HEAD); \
	cp $@ build/balance_ex.v$$VERSION-$$GIT_HASH.vescpkg

balance_ex:
	$(MAKE) -C $@

clean:
	rm -f balance_ex.vescpkg README.gen.md ui.gen.qml
	$(MAKE) -C balance_ex clean

.PHONY: all clean balance_ex
