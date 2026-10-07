"""Speech-in-mixture estimates and calibration; no creative approval or voice processing."""
import datetime
import hashlib
import json
import math
from pathlib import Path
import subprocess
import time
import warnings

import numpy as np
from pystoi import stoi
from scipy import signal
import soundfile as sf

OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parents[2]
BANK = ROOT / "Framework-Edicion-Social/research/prueba-mezcla-voz-2026-09-30"
FFMPEG = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
FS = 48000


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_audio(path):
    if path.suffix == ".wav":
        data, rate = sf.read(path, dtype="float32", always_2d=True)
        assert rate == FS
    else:
        result = subprocess.run([FFMPEG, "-v", "error", "-i", str(path),
                                 "-f", "f32le", "-ac", "2", "-ar", str(FS), "pipe:1"],
                                check=True, capture_output=True)
        data = np.frombuffer(result.stdout, dtype="<f4").reshape(-1, 2)
    assert np.isfinite(data).all()
    return data.mean(axis=1).astype(np.float64)


def db_rms(x):
    return float(10 * np.log10(np.mean(x*x) + 1e-20))


def indices(ref16, test16):
    with warnings.catch_warnings(record=True) as caught:
        a = float(stoi(ref16, test16, 16000, extended=False))
        b = float(stoi(ref16, test16, 16000, extended=True))
    assert np.isfinite([a, b]).all()
    return {"stoi": a, "estoi": b, "warnings": [str(w.message) for w in caught]}


def get_items():
    items = []
    for row in json.loads((BANK / "manifest.json").read_text()):
        stem = BANK / "renders/v2" / row["id"]
        items.append({"id": row["id"] + "-primera", "piece": row["id"],
                      "duration_s": row["duration_s"],
                      "voice": Path(str(stem) + "-voz-sola.wav"),
                      "mix": Path(str(stem) + "-mezcla.m4a"),
                      "music": Path(str(stem) + "-musica.wav"),
                      "sfx": Path(str(stem) + "-efectos.wav")})
    for row in json.loads((BANK / "variantes-largas/manifest.json").read_text()):
        p = BANK / "variantes-largas" / row["id"] / row["variant"]
        items.append({"id": row["id"] + "-" + row["variant"], "piece": row["id"],
                      "duration_s": row["duration_s"],
                      "voice": BANK / "renders/v2" / (row["id"] + "-voz-sola.wav"),
                      "mix": p / "mezcla.m4a", "music": p / "musica.wav", "sfx": p / "efectos.wav"})
    return items


def spectral_relation(voice, music, sfx):
    """Third-octave relationships, not a validated masking/audibility model."""
    matrices = []
    for data in [voice, music, sfx]:
        freq, clock, z = signal.stft(data, FS, nperseg=2048, noverlap=1024, boundary=None)
        matrices.append(abs(z)**2)
    centers = [250, 400, 630, 1000, 1600, 2500, 4000, 6300]
    out = []
    for center in centers:
        selected = (freq >= center / 2**(1/6)) & (freq <= center * 2**(1/6))
        energy = [m[selected].sum(axis=0) for m in matrices]
        active = energy[0] > max(1e-10, np.percentile(energy[0], 75) * .02)
        for role, e in zip(["music", "sfx"], energy[1:]):
            # Residual/no-source frames do not become masking claims.
            valid = active & (e > 1e-14)
            ratio = 10*np.log10((e[valid]+1e-20)/(energy[0][valid]+1e-20))
            out.append({"center_hz": center, "role": role,
                        "active_frames": int(valid.sum()),
                        "relative_db_p50": float(np.median(ratio)) if len(ratio) else None,
                        "relative_db_p95": float(np.percentile(ratio, 95)) if len(ratio) else None,
                        "frames_above_voice": int((ratio > 0).sum())})
    return out


def calibrate(item):
    # Unlabelled filenames avoid leaking expected condition to the audio-language model.
    voice, music, fx = [read_audio(item[k])[:12*FS] for k in ["voice", "music", "sfx"]]
    music *= 10**((db_rms(voice)-db_rms(music))/20)
    fx *= 10**((db_rms(voice)-db_rms(fx))/20)
    raw = {
        "voice_only": voice,
        "music_only": music,
        "silence": np.zeros_like(voice),
        "balanced": voice + music*.1 + fx*.03,
        "music_masks": voice + music*2.0 + fx*.03,
        "effects_masks": voice + music*.1 + fx*2.0,
        "no_voice": music*.1 + fx*.03,
        "clipped_voice": np.clip(voice, -.018, .018),
    }
    # A shared constant prevents clipping in additive controls and preserves voice comparisons.
    common_gain = min(1., .90/max(float(abs(a).max()) for a in raw.values()))
    manifest = []
    voice16 = signal.resample_poly(voice*common_gain, 1, 3)
    for condition, data in raw.items():
        data = data*common_gain
        code = hashlib.sha256(("audio-cal-20261001:"+condition).encode()).hexdigest()[:12]
        path = OUT / "calibracion" / (code + ".wav")
        data16 = signal.resample_poly(data, 1, 3).astype(np.float32)
        sf.write(path, data16, 16000, subtype="FLOAT")
        scores = indices(voice16, data16)
        manifest.append({"code": code, "condition": condition, "path": str(path),
                         "sha256": sha(path), "common_gain": common_gain,
                         "sample_rate": 16000, "duration_s": len(data16)/16000,
                         "peak": float(abs(data16).max()), **scores})
    (OUT / "calibracion/manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    by = {r["condition"]: r for r in manifest}
    checks = {
        "dry_reference_near_one": by["voice_only"]["estoi"] > .999,
        "music_excess_lowers_estimate": by["balanced"]["estoi"] > by["music_masks"]["estoi"]+.05,
        "effects_excess_lowers_estimate": by["balanced"]["estoi"] > by["effects_masks"]["estoi"]+.05,
        "missing_voice_lowers_estimate": by["balanced"]["estoi"] > by["no_voice"]["estoi"]+.2,
    }
    approved_scope = {k: v for k, v in checks.items() if k != "effects_excess_lowers_estimate"}
    (OUT / "calibracion/validacion-indices.json").write_text(json.dumps({
        "checks": checks, "speech_music_scope_pass": all(approved_scope.values()),
        "all_capabilities_pass": all(checks.values()), "human_listener": False,
        "excluded": ["Global SFX masking/distraction/audibility; sparse transients failed the predeclared sensitivity control."],
        "limits": "Directional sensitivity on these controls only; no MOS, universal cutoff or creative ranking."}, indent=2)+"\n")
    assert all(approved_scope.values()), approved_scope
    return manifest


def main():
    started = time.monotonic()
    items = get_items()
    calibrate(next(i for i in items if i["id"] == "largo-53-A"))
    report = []
    for item in items:
        voice = read_audio(item["voice"])
        mix = read_audio(item["mix"])
        music, fx = read_audio(item["music"]), read_audio(item["sfx"])
        assert abs(len(voice)-len(mix))/FS < .050
        n = min(map(len, [voice, mix, music, fx]))
        voice, mix, music, fx = [a[:n] for a in [voice, mix, music, fx]]
        voice16, mix16 = [signal.resample_poly(a, 1, 3) for a in [voice, mix]]
        windows = []
        for start in np.arange(0, n/FS-3.99, 2):
            a, b = round(start*16000), round((start+4)*16000)
            windows.append({"start_s": float(start), "end_s": float(start+4),
                            **indices(voice16[a:b], mix16[a:b]),
                            "voice_dbfs": db_rms(voice16[a:b]),
                            "mix_dbfs": db_rms(mix16[a:b])})
        whole = indices(voice16, mix16)
        pathinfo = {k: {"path": str(item[k]), "sha256": sha(item[k])} for k in ["voice", "mix", "music", "sfx"]}
        result = {"id": item["id"], "piece": item["piece"], "duration_s": item["duration_s"],
                  "inputs": pathinfo, "aac_extra_samples": len(read_audio(item["mix"]))-n,
                  "mono_policy": "(L+R)/2; perceptual proxy excludes stereo perception",
                  "whole": whole, "windows": windows,
                  "estoi_p10": float(np.percentile([w["estoi"] for w in windows], 10)),
                  "lowest_windows": sorted(windows, key=lambda x: x["estoi"])[:5],
                  "band_relationships": spectral_relation(voice, music, fx)}
        report.append(result)
        print(item["id"], round(whole["estoi"], 4), "worst", round(min(w["estoi"] for w in windows),4), flush=True)
        (OUT / "evidencia/indices.json").write_text(json.dumps({
            "engine": "pystoi 0.4.1", "speech_native_rate": FS, "analysis_rate": 16000,
            "window_s": 4, "hop_s": 2, "items": report,
            "interpretation": "Estimated speech intelligibility relative to this exact voice. Not probability, attention, emotional fit, human approval or proof of SFX audibility.",
            "elapsed_seconds": time.monotonic()-started,
            "updated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }, indent=2)+"\n")


if __name__ == "__main__":
    main()
