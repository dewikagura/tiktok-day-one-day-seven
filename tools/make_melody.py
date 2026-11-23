#!/usr/bin/env python3
"""Generate a short cheerful chiptune loop for the STAR HOP video.

Pure Python (no numpy): 16-bit PCM WAV, 44100 Hz mono, 24 seconds.
Melody: C-major pentatonic eighth-note arpeggio at 132 BPM, soft bass
underneath. Deterministic.
"""
import math
import struct
import wave

SR = 44100
DUR = 24.0
EIGHTH = 60.0 / 132 / 2  # ~0.227 s

# frequencies (Hz) for the pentatonic ladder
N = {
    "C3": 130.81, "F3": 174.61, "G3": 196.00, "A3": 220.00,
    "C5": 523.25, "D5": 587.33, "E5": 659.25, "G5": 783.99,
    "A5": 880.00, "C6": 1046.50, "D6": 1174.66, "E6": 1318.51,
}

# 16-eighth pattern, repeated; None = rest
PATTERN = ["C5", "E5", "G5", "A5", "G5", "E5", "D5", "E5",
           "C5", "E5", "G5", "C6", "A5", "G5", "E5", "D5"]
BASS = ["C3", "C3", "F3", "G3"]  # one bass note per 8 eighths


def note_samples(freq, start, length, vol):
    out = []
    n = int(length * SR)
    for i in range(n):
        t = i / SR
        env = math.exp(-3.0 * t / length)  # decay over the note
        s = math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(4 * math.pi * freq * t)
        out.append(vol * env * s)
    return out


def main():
    total = int(DUR * SR)
    mix = [0.0] * total
    n_eighths = int(DUR / EIGHTH)
    for k in range(n_eighths):
        name = PATTERN[k % len(PATTERN)]
        if name is None:
            continue
        start = k * EIGHTH
        s = note_samples(N[name], start, EIGHTH * 0.95, 0.32)
        off = int(start * SR)
        for i, v in enumerate(s):
            if off + i < total:
                mix[off + i] += v
    # bass: one note per 8 eighths
    for bar in range(n_eighths // 8 + 1):
        name = BASS[bar % len(BASS)]
        start = bar * 8 * EIGHTH
        s = note_samples(N[name], start, 8 * EIGHTH, 0.18)
        off = int(start * SR)
        for i, v in enumerate(s):
            if off + i < total:
                mix[off + i] += v
    # gentle fade out over the last second
    fade = int(SR * 1.0)
    for i in range(fade):
        mix[total - fade + i] *= (1.0 - i / fade)
    peak = max(abs(v) for v in mix) or 1.0
    scale = 0.85 / peak
    frames = b"".join(struct.pack("<h", int(max(-1.0, min(1.0, v * scale)) * 32767))
                      for v in mix)
    with wave.open("melody.wav", "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(frames)
    print(f"wrote melody.wav: {DUR}s, peak {peak:.2f}, scaled to 0.85")


if __name__ == "__main__":
    main()
