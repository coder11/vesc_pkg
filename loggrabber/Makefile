VESC_TOOL ?= vesc_tool

all: loggrabber.vescpkg

loggrabber.vescpkg:
	$(VESC_TOOL) --buildPkgFromDesc pkgdesc.qml --testPkgDesc 'custom:vbms32' --testPkgDesc 'vesc:test'

clean:
	rm -f loggrabber.vescpkg

.PHONY: all clean
