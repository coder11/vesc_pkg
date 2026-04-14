# Demo Resource Audio

QML-only demo that embeds audio files in several formats as Qt resources (`.rcc`) and plays them back using `QtMultimedia.MediaPlayer`.

The package bundles five short synthesized sounds in WAV, OGG Vorbis, and FLAC to demonstrate that different audio codecs work from embedded resources:

| Sound | File | Format | Description |
|-------|------|--------|-------------|
| Beep | `beep.wav` | WAV | 440 Hz sine, 0.3 s |
| Alert | `alert.ogg` | OGG | 880 → 660 Hz sweep, 0.3 s |
| Chime | `chime.flac` | FLAC | C5-E5-G5 arpeggio, 0.6 s |
| Warning | `warning.wav` | WAV | 220 Hz double pulse, 0.5 s |
| Click | `click.ogg` | OGG | 1 kHz burst, 50 ms |

No LispBM script and no native code are included.

## How it works

1. `resources.qrc` lists every file under `audio-res/`.
2. `make` compiles the `.qrc` into a binary `resources.rcc` using the Qt `rcc` tool.
3. `pkgdesc.qml` declares `pkgRcc: "resources.rcc"`, so `vesc_tool --buildPkgFromDesc` embeds the blob.
4. At install time VESC Tool registers the `.rcc` in memory; files appear under `qrc:/vesc_pkg/`.
5. `ui.qml` uses `MediaPlayer { source: "qrc:/vesc_pkg/audio-res/…" }` to play each track.

## Regenerating audio samples

The audio files are committed to the repo, but you can regenerate them (requires `ffmpeg` for OGG/FLAC conversion):

```sh
python3 gen_samples.py
```

## Building

```sh
make            # needs rcc (Qt) and vesc_tool on PATH
make clean
```
