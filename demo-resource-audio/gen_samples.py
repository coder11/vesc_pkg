#!/usr/bin/env python3
"""Generate audio samples in WAV, OGG, and FLAC for the demo-resource-audio package.

WAV files are created with Python's `wave` module.  OGG and FLAC are produced
by converting the intermediate WAV through ffmpeg (must be on PATH).
"""

import math
import os
import struct
import subprocess
import tempfile
import wave

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio-res")
SAMPLE_RATE = 22050
os.makedirs(OUT_DIR, exist_ok=True)


def write_wav(path, samples, sample_rate=SAMPLE_RATE):
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"".join(struct.pack("<h", s) for s in samples))


def convert_wav(wav_path, out_path):
    subprocess.run(
        ["ffmpeg", "-y", "-i", wav_path, out_path],
        capture_output=True, check=True,
    )


def write_audio(name, ext, samples, sample_rate=SAMPLE_RATE):
    out = os.path.join(OUT_DIR, name + ext)
    if ext == ".wav":
        write_wav(out, samples, sample_rate)
    else:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            write_wav(tmp_path, samples, sample_rate)
            convert_wav(tmp_path, out)
        finally:
            os.unlink(tmp_path)
    return out


def sine_samples(freq, duration, volume=0.8, sample_rate=SAMPLE_RATE):
    n = int(sample_rate * duration)
    return [
        int(volume * 32767 * math.sin(2 * math.pi * freq * i / sample_rate))
        for i in range(n)
    ]


def apply_fade(samples, fade_ms=20, sample_rate=SAMPLE_RATE):
    fade_n = int(sample_rate * fade_ms / 1000)
    for i in range(min(fade_n, len(samples))):
        samples[i] = int(samples[i] * i / fade_n)
    for i in range(min(fade_n, len(samples))):
        samples[-(i + 1)] = int(samples[-(i + 1)] * i / fade_n)
    return samples


# ── Tracks (name, extension, samples) ──────────────────────────────

tracks = [
    ("beep",    ".wav",  apply_fade(sine_samples(440, 0.3))),
    ("alert",   ".ogg",  apply_fade(sine_samples(880, 0.15) + sine_samples(660, 0.15))),
    ("chime",   ".flac", apply_fade(
        sine_samples(523.25, 0.2, 0.6)
        + sine_samples(659.25, 0.2, 0.6)
        + sine_samples(783.99, 0.2, 0.6))),
    ("warning", ".wav",  apply_fade(
        sine_samples(220, 0.2)
        + [0] * int(SAMPLE_RATE * 0.1)
        + sine_samples(220, 0.2))),
    ("click",   ".ogg",  apply_fade(sine_samples(1000, 0.05), fade_ms=5)),
]

for name, ext, samples in tracks:
    path = write_audio(name, ext, samples)
    sz = os.path.getsize(path)
    print(f"  {os.path.basename(path):20s}  {sz:>6d} bytes")
