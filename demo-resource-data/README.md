# Demo Resource Data

QML-only demo that shows how to embed and use Qt resources (`.rcc`) inside a VESC package.

The package bundles several resource types and displays them all from QML at runtime:

| Resource | File | What it demonstrates |
|----------|------|----------------------|
| SVG icons | `icon_battery.svg`, `icon_motor.svg`, `icon_settings.svg`, `icon_warning.svg` | Vector icons via `Image { source: "qrc:/vesc_pkg/..." }` |
| SVG logo | `logo_vesc.svg` | Larger vector graphic |
| PNG image | `sample_image.png` | Raster image from resources |
| Text file | `strings.txt` | Reading text with `XMLHttpRequest` against a `qrc:` URL |
| JSON data | `config.json` | Parsing structured data from an embedded file |

No LispBM script and no native code are included.

## How it works

1. `resources.qrc` lists every file under `resources/`.
2. `make` compiles the `.qrc` into a binary `resources.rcc` using the Qt `rcc` tool.
3. `pkgdesc.qml` declares `pkgRcc: "resources.rcc"`, so `vesc_tool --buildPkgFromDesc` embeds the blob.
4. At install time VESC Tool registers the `.rcc` in memory; files appear under `qrc:/vesc_pkg/`.
5. `ui.qml` loads icons, images, text, and JSON from that mount point.

## Building

```sh
make            # needs rcc (Qt) and vesc_tool on PATH
make clean
```
