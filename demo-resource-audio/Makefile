VESC_TOOL ?= vesc_tool
RCC       ?= rcc

all: demo_resource_audio.vescpkg

resources.rcc: resources.qrc $(wildcard audio-res/*)
	$(RCC) --binary resources.qrc -o resources.rcc

demo_resource_audio.vescpkg: pkgdesc.qml README.md ui.qml resources.rcc
	$(VESC_TOOL) --buildPkgFromDesc pkgdesc.qml

clean:
	rm -f resources.rcc demo_resource_audio.vescpkg

.PHONY: all clean
