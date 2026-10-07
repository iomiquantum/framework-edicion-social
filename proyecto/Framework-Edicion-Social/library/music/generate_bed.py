#!/usr/bin/env python3
"""Original seamless 8-bar technology bed, 114 BPM, synthesized without samples."""
from array import array
import json
import math
from pathlib import Path
import random
import struct
import wave

SR = 48000
BPM = 114
N = round(SR * 60 / BPM * 32)
DURATION = N / SR
ROOT = Path(__file__).resolve().parent
TAU = math.tau


def midi(note):
    return 440 * 2 ** ((note - 69) / 12)


def main():
    left = array('d', [0]) * N
    right = array('d', [0]) * N
    # Quiet suspended E-major color. Integer cycles across the entire file
    # ensure continuous phase at the wrap, including modulation.
    for index, note in enumerate([52, 59, 66, 68]):
        frequency = round(midi(note) * DURATION) / DURATION
        pan = [-.40, .40, -.18, .18][index]
        for i in range(N):
            p = i / N
            amplitude = .014 * (1 + .18 * math.cos(TAU * p + index))
            value = amplitude * math.sin(TAU * frequency * i / SR + index * .3)
            left[i] += value * math.sqrt((1 - pan) / 2)
            right[i] += value * math.sqrt((1 + pan) / 2)

    def event(beat, note, decay, amplitude, pan=0, bass=False):
        offset = round(beat * N / 32)
        frequency = midi(note)
        count = round(min(decay * 12, DURATION) * SR)
        for k in range(count):
            t = k / SR
            attack = .007 if bass else .012
            envelope = (1 - math.exp(-t / attack)) * math.exp(-t / decay)
            fundamental = math.sin(TAU * frequency * t)
            harmonic = .10 * math.sin(TAU * frequency * 2 * t)
            value = amplitude * envelope * (fundamental + harmonic)
            i = (offset + k) % N
            left[i] += value * math.sqrt((1 - pan) / 2)
            right[i] += value * math.sqrt((1 + pan) / 2)

    # Restrained half-time bass and sparse high plucks; no lead melody.
    for bar in range(8):
        event(bar * 4, 40 if bar % 4 < 2 else 47, .17, .16, bass=True)
        if bar % 2 == 0:
            event(bar * 4 + 2.5, 47, .12, .070, bass=True)
    for beat, note, pan in [(0.5, 64, -.28), (3, 71, .28),
                            (5.5, 66, .20), (7, 68, -.20),
                            (8.5, 64, -.28), (11, 71, .28),
                            (13.5, 68, .20), (15, 66, -.20),
                            (16.5, 64, -.28), (19, 71, .28),
                            (21.5, 66, .20), (23, 68, -.20),
                            (24.5, 64, -.28), (27, 71, .28),
                            (29.5, 68, .20), (31, 66, -.20)]:
        event(beat, note, .15, .044, pan)
        event(beat + .375, note, .11, .012, -pan)

    # Very soft high-pass noise marks on alternate half beats.
    rng = random.Random(114)
    for beat in [i + .5 for i in range(32)]:
        previous = high = 0
        offset = round(beat * N / 32)
        for k in range(int(.055 * SR)):
            t = k / SR
            raw = rng.uniform(-1, 1)
            high = .55 * (high + raw - previous)
            previous = raw
            envelope = (1 - math.exp(-t / .002)) * math.exp(-t / .007)
            value = .007 * high * envelope
            i = (offset + k) % N
            left[i] += value * .72
            right[i] += value * .68

    peak = max(max(abs(x) for x in left), max(abs(x) for x in right))
    gain = 10 ** (-18 / 20) / peak
    payload = bytearray()
    dither = random.Random('tech-pulse-original')
    energy = 0.0
    for i in range(N):
        for channel in (left, right):
            sample = channel[i] * gain
            energy += sample * sample
            value = round(sample * 8388607 + dither.random() - dither.random())
            payload.extend(struct.pack('<i', value)[:3])
    output = ROOT / 'tech_pulse_114bpm_8bars.wav'
    with wave.open(str(output), 'wb') as wav:
        wav.setnchannels(2)
        wav.setsampwidth(3)
        wav.setframerate(SR)
        wav.writeframes(payload)
    manifest = {'file': output.name, 'bpm': BPM, 'bars': 8, 'beats_per_bar': 4,
                'duration_seconds': DURATION, 'frames': N, 'sample_rate': SR,
                'bit_depth': 24, 'channels': 2, 'peak_dbfs': -18,
                'rms_dbfs': round(10 * math.log10(energy / (2 * N)), 2),
                'key': 'E major / suspended texture', 'loopable': True,
                'provenance': 'Original procedural synthesis; generate_bed.py',
                'license': 'CC0-1.0 (to the extent rights exist)',
                'wrap_step_dbfs': round(20 * math.log10(max(abs(left[-1]-left[0]),
                                                             abs(right[-1]-right[0])) * gain), 2)}
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
