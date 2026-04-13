VESC_TOOL ?= vesc_tool
RCC       ?= rcc

all: demo_resource_data.vescpkg

resources.rcc: resources.qrc $(wildcard resources/*)
	$(RCC) --binary resources.qrc -o resources.rcc

demo_resource_data.vescpkg: pkgdesc.qml README.md ui.qml resources.rcc
	$(VESC_TOOL) --buildPkgFromDesc pkgdesc.qml

clean:
	rm -f resources.rcc demo_resource_data.vescpkg

.PHONY: all clean
