#!/usr/bin/env python3
"""Original deterministic social-edit SFX. Python standard library only.

Render with: python3 generate_sfx.py
All oscillators/envelopes/noise are synthesized here; no sampled media.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import random
import struct
import wave

SR = 48000
ROOT = Path(__file__).resolve().parent
TAU = math.tau


def noise(count: int, seed: int, cutoff_start: float, cutoff_end: float) -> list[float]:
    rng = random.Random(seed)
    low = previous = high = 0.0
    result = []
    for i in range(count):
        p = i / max(1, count - 1)
        cutoff = cutoff_start * (cutoff_end / cutoff_start) ** p
        a = 1 - math.exp(-TAU * cutoff / SR)
        low += a * (rng.uniform(-1, 1) - low)
        high = 0.985 * (high + low - previous)
        previous = low
        result.append(high)
    return result


def airy_in() -> list[float]:
    n = int(.44 * SR)
    airy = noise(n, 101, 900, 5500)
    return [airy[i] * math.sin(math.pi * i / (n - 1)) ** 2.6 for i in range(n)]


def soft_whoosh() -> list[float]:
    n = int(.30 * SR)
    airy = noise(n, 202, 5600, 1400)
    out = []
    phase = 0.0
    for i in range(n):
        t = i / SR
        p = i / (n - 1)
        phase += TAU * (300 - 165 * p) / SR
        envelope = math.sin(math.pi * p) ** 2
        out.append(envelope * (.75 * airy[i] + .035 * math.sin(phase)))
    return out


def ui_tick() -> list[float]:
    n = int(.085 * SR)
    airy = noise(n, 303, 5800, 1700)
    return [(1 - math.exp(-(i / SR) / .0006)) * math.exp(-(i / SR) / .010)
            * (.24 * math.sin(TAU * 1750 * i / SR) + .44 * airy[i])
            for i in range(n)]


def soft_pop() -> list[float]:
    out = []
    phase = 0.0
    for i in range(int(.16 * SR)):
        t = i / SR
        phase += TAU * (400 + 620 * math.exp(-t / .018)) / SR
        envelope = (1 - math.exp(-t / .0012)) * math.exp(-t / .024)
        out.append(envelope * (math.sin(phase) + .08 * math.sin(phase * 2)))
    return out


def low_accent() -> list[float]:
    n = int(.34 * SR)
    airy = noise(n, 505, 2100, 650)
    out = []
    phase = 0.0
    for i in range(n):
        t = i / SR
        phase += TAU * (105 + 90 * math.exp(-t / .033)) / SR
        envelope = (1 - math.exp(-t / .0015)) * math.exp(-t / .048)
        # Audible harmonic on small phone speakers, without a sub-bass boom.
        out.append(envelope * (.65 * math.sin(phase) + .20 * math.sin(phase * 2))
                   + .1 * airy[i] * math.exp(-t / .012))
    return out


def notes(duration: float, events: list[tuple[float, float, float]]) -> list[float]:
    out = [0.0] * int(duration * SR)
    for start, frequency, decay in events:
        offset = int(start * SR)
        for i in range(offset, len(out)):
            t = (i - offset) / SR
            envelope = (1 - math.exp(-t / .0025)) * math.exp(-t / decay)
            out[i] += envelope * (math.sin(TAU * frequency * t)
                                  + .075 * math.sin(TAU * 2 * frequency * t))
    return out


def sequence() -> list[float]:
    return notes(.50, [(0, 660, .040), (.105, 825, .040), (.21, 990, .048)])


def loop_return() -> list[float]:
    # Last note returns to the first pitch: semantic cue for repetition.
    return notes(.48, [(0, 740, .042), (.13, 988, .032), (.26, 740, .042)])


def resolve() -> list[float]:
    return notes(.84, [(0, 440, .13), (.075, 660, .14), (.125, 880, .12)])


PACK = [
    ('01_airy_in', airy_in, -12, 'Aparición de un diagrama o concepto'),
    ('02_soft_whoosh', soft_whoosh, -12, 'Cambio narrativo o desplazamiento gráfico'),
    ('03_ui_tick', ui_tick, -10, 'Un nodo o marca puntual'),
    ('04_soft_pop', soft_pop, -10, 'Una palabra o elemento clave'),
    ('05_low_accent', low_accent, -12, 'Un único énfasis de mayor peso'),
    ('06_sequence', sequence, -14, 'Diagrama de secuencia de tres pasos'),
    ('07_loop_return', loop_return, -14, 'Retorno o repetición visual'),
    ('08_resolve', resolve, -15, 'Cierre de idea con respiración'),
]


def render(name: str, samples: list[float], peak_db: float, purpose: str) -> dict:
    # Remove DC and fade endpoints to eliminate discontinuities.
    mean = sum(samples) / len(samples)
    fade = int(.002 * SR)
    samples = [(value - mean) * min(1, i / fade, (len(samples) - 1 - i) / fade)
               for i, value in enumerate(samples)]
    target = 10 ** (peak_db / 20)
    gain = target / max(abs(value) for value in samples)
    samples = [value * gain for value in samples]
    data = bytearray()
    rng = random.Random(name)  # TPDF dither at 24-bit quantization, ~-144 dBFS.
    for value in samples:
        quantized = round(value * 8388607 + rng.random() - rng.random())
        quantized = min(8388607, max(-8388608, quantized))
        data.extend(struct.pack('<i', quantized)[:3])
    path = ROOT / (name + '.wav')
    with wave.open(str(path), 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(3)
        wav.setframerate(SR)
        wav.writeframes(data)
    rms = math.sqrt(sum(value * value for value in samples) / len(samples))
    return {'file': path.name, 'duration_seconds': round(len(samples) / SR, 3),
            'sample_rate': SR, 'bit_depth': 24, 'channels': 1,
            'peak_dbfs': peak_db, 'rms_dbfs': round(20 * math.log10(rms), 2),
            'purpose': purpose, 'provenance': 'Original procedural synthesis; generate_sfx.py',
            'license': 'CC0-1.0 (to the extent rights exist)'}


def main() -> None:
    manifest = {'version': '1.0.0', 'created': '2026-09-23',
                'pack': 'Social Essentials Original',
                'mix_guidance': {
                    'hyperframes_data_volume_start_range': [0.35, 0.5],
                    'hard_max_without_specific_review': 1.0,
                    'groups': ['voiceover', 'music', 'sfx'],
                    'music_voice_carve_strength_reference': 0.8,
                    'required_audits': ['headphones_or_monitors', 'phone_speaker'],
                    'note': ('Starting values only. The historical 1.05-1.75 range is retired; '
                             'final levels require voice intelligibility, tonal-balance, clipping '
                             'and true-peak checks.'),
                },
                'files': [render(name, factory(), peak, purpose)
                          for name, factory, peak, purpose in PACK]}
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
