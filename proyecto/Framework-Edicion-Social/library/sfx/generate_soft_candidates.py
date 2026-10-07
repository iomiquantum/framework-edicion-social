#!/usr/bin/env python3
"""Deterministic, low-fatigue SFX candidates for review.

These files intentionally favor slower envelopes, low-pass noise, modest crest
levels and conservative peaks. They are candidates, not replacements, until the
user explicitly approves them.
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
OUT = ROOT / "candidates"
TAU = math.tau


def smooth_noise(
    count: int,
    seed: int,
    cutoff_start: float,
    cutoff_end: float,
    passes: int = 2,
) -> list[float]:
    """Cascaded time-varying low-pass noise with no bright transient."""
    rng = random.Random(seed)
    states = [0.0] * passes
    result = []
    for i in range(count):
        p = i / max(1, count - 1)
        cutoff = cutoff_start * (cutoff_end / cutoff_start) ** p
        coefficient = 1 - math.exp(-TAU * cutoff / SR)
        value = rng.uniform(-1, 1)
        for index in range(passes):
            states[index] += coefficient * (value - states[index])
            value = states[index]
        result.append(value)
    return result


def rounded_envelope(position: float, peak_at: float, attack_power: float = 1.7, release_power: float = 2.0) -> float:
    if position <= peak_at:
        phase = position / peak_at
        return math.sin(math.pi * phase / 2) ** attack_power
    phase = (position - peak_at) / (1 - peak_at)
    return math.cos(math.pi * phase / 2) ** release_power


def velvet_bloom() -> list[float]:
    n = int(0.58 * SR)
    texture = smooth_noise(n, 901, 430, 1350, passes=2)
    out = []
    phase = 0.0
    for i in range(n):
        p = i / (n - 1)
        phase += TAU * (235 + 90 * p) / SR
        envelope = rounded_envelope(p, 0.48, 2.0, 2.4)
        out.append(envelope * (0.94 * texture[i] + 0.018 * math.sin(phase)))
    return out


def warm_breath_lift() -> list[float]:
    n = int(0.72 * SR)
    texture = smooth_noise(n, 902, 330, 820, passes=3)
    out = []
    phase = 0.0
    for i in range(n):
        p = i / (n - 1)
        phase += TAU * (180 + 65 * p) / SR
        envelope = rounded_envelope(p, 0.58, 2.2, 2.6)
        out.append(envelope * (texture[i] + 0.012 * math.sin(phase)))
    return out


def fabric_swish() -> list[float]:
    n = int(0.52 * SR)
    texture = smooth_noise(n, 903, 1450, 430, passes=2)
    out = []
    phase = 0.0
    for i in range(n):
        p = i / (n - 1)
        phase += TAU * (165 - 45 * p) / SR
        envelope = rounded_envelope(p, 0.38, 1.8, 2.5)
        out.append(envelope * (texture[i] + 0.014 * math.sin(phase)))
    return out


def warm_slide() -> list[float]:
    n = int(0.44 * SR)
    texture = smooth_noise(n, 904, 920, 300, passes=3)
    out = []
    phase = 0.0
    for i in range(n):
        p = i / (n - 1)
        phase += TAU * (210 - 55 * p) / SR
        envelope = rounded_envelope(p, 0.34, 2.0, 2.8)
        out.append(envelope * (texture[i] + 0.010 * math.sin(phase)))
    return out


CANDIDATES = [
    (
        "entry_velvet_bloom_soft_v01",
        velvet_bloom,
        -22,
        "Entrada aterciopelada y cálida para revelar una idea sin ataque brillante.",
        "entry",
    ),
    (
        "entry_warm_breath_lift_soft_v01",
        warm_breath_lift,
        -24,
        "Elevación respirada, lenta y muy discreta para imágenes o conceptos contemplativos.",
        "entry",
    ),
    (
        "motion_fabric_swish_soft_v01",
        fabric_swish,
        -22,
        "Barrido tipo tela, redondeado y de poco brillo para desplazamientos gráficos.",
        "motion",
    ),
    (
        "motion_warm_slide_soft_v01",
        warm_slide,
        -24,
        "Deslizamiento cálido y corto para cambios de bloque debajo de la voz.",
        "motion",
    ),
]


def render(name: str, samples: list[float], peak_db: float, description: str, family: str) -> dict:
    mean = sum(samples) / len(samples)
    fade = int(0.010 * SR)
    samples = [
        (value - mean) * min(1.0, i / fade, (len(samples) - 1 - i) / fade)
        for i, value in enumerate(samples)
    ]
    target = 10 ** (peak_db / 20)
    gain = target / max(abs(value) for value in samples)
    samples = [value * gain for value in samples]
    rms = math.sqrt(sum(value * value for value in samples) / len(samples))
    data = bytearray()
    rng = random.Random(name)
    for value in samples:
        quantized = round(value * 8388607 + rng.random() - rng.random())
        quantized = min(8388607, max(-8388608, quantized))
        data.extend(struct.pack("<i", quantized)[:3])
    path = OUT / f"{name}.wav"
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(3)
        wav.setframerate(SR)
        wav.writeframes(data)
    return {
        "file": str(path.relative_to(ROOT)),
        "family": family,
        "duration_seconds": round(len(samples) / SR, 3),
        "sample_rate": SR,
        "bit_depth": 24,
        "channels": 1,
        "peak_dbfs": peak_db,
        "rms_dbfs": round(20 * math.log10(rms), 2),
        "description": description,
        "status": "provisional_pending_user_review",
        "provenance": "Original deterministic procedural synthesis; generate_soft_candidates.py",
        "license": "CC0-1.0 (to the extent rights exist)",
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": "1.0.0",
        "created": "2026-09-25",
        "pack": "Soft Transitions Candidates",
        "design_constraints": [
            "conservative peak level",
            "rounded attack and release",
            "low-pass texture with reduced high-frequency fatigue",
            "no samples or third-party recordings",
            "not eligible for automatic reuse until explicit approval",
        ],
        "files": [render(name, factory(), peak, description, family)
                  for name, factory, peak, description, family in CANDIDATES],
    }
    path = OUT / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
