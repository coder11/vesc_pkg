VESC_TOOL ?= vesc_tool

all: demo_play_sound.vescpkg

demo_play_sound.vescpkg: pkgdesc.qml README.md ui.qml
	$(VESC_TOOL) --buildPkgFromDesc pkgdesc.qml

clean:
	rm -f demo_play_sound.vescpkg

.PHONY: all clean
