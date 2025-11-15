VESC_TOOL ?= vesc_tool

all: balance_ex.vescpkg

balance_ex.vescpkg: balance_ex
	$(VESC_TOOL) --buildPkgFromDesc pkgdesc.qml --testPkgDesc 'custom:test' --testPkgDesc 'vesc:test'

balance_ex:
	$(MAKE) -C $@

clean:
	rm -f balance_ex.vescpkg
	$(MAKE) -C balance_ex clean

.PHONY: all clean balance_ex
