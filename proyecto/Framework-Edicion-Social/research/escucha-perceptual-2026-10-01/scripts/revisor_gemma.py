"""Independent local audio-model benchmark using the maintained MLX-VLM adapter."""
import argparse
import datetime
import gc
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from scipy import signal
import soundfile as sf
import mlx.core as mx
from mlx_vlm import load, generate
from mlx_vlm.prompt_utils import apply_chat_template

from revisor_audio_modelo import jobs, parse, PROMPT, OUT, read_audio

MODEL = Path.home() / ".cache/codex-audio-perceptual/2026-10-01/models/gemma-4-e2b-4bit"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["calibracion", "mezclas", "referencias"], required=True)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    targets = jobs(args.mode)
    if args.limit:
        targets = targets[:args.limit]
    dest = OUT / f"modelo/gemma-{args.mode}.json"
    previous = json.loads(dest.read_text()) if dest.exists() else {"results": []}
    done = {r["id"] for r in previous["results"] if r.get("parsed") is not None}
    pending = [j for j in targets if j["id"] not in done]
    if not pending:
        print("Requested reports complete.")
        return
    mx.set_cache_limit(128 * 1024**2)
    mx.set_memory_limit(7 * 1024**3)
    mx.random.seed(20261001)
    started = time.monotonic()
    print("Loading frozen Gemma4 audio model through MLX-VLM strict=True", flush=True)
    model, processor = load(str(MODEL), strict=True, trust_remote_code=False)
    formatted = apply_chat_template(processor, model.config, PROMPT, num_audios=1, enable_thinking=False)
    audit = {"engine": "Gemma4-E2B-it4bit / MLX-VLM0.7.4", "model": str(MODEL),
             "load_seconds": time.monotonic()-started, "temperature": 0,
             "seed": 20261001, "prompt": PROMPT, "formatted_prompt": formatted,
             "prompt_sha256": hashlib.sha256(PROMPT.encode()).hexdigest(),
             "human_listener": False, "no_transcript_or_metric_inputs": True,
             "strict_weights": True, "trust_remote_code": False,
             "inference_audio": "float32 mono16k derived from exact AAC; source untouched"}
    (OUT / "modelo/gemma-carga.json").write_text(json.dumps(audit, indent=2)+"\n")
    report = {**audit, "mode": args.mode, "results": previous["results"]}
    audio_cache = {}
    for job in pending:
        source = Path(job["input"])
        if source not in audio_cache:
            if args.mode == "calibracion":
                waveform, fs = sf.read(source, dtype="float32")
                assert fs == 16000
            else:
                waveform = signal.resample_poly(read_audio(source), 1, 3).astype(np.float32)
            audio_cache = {source: waveform}
        samples = audio_cache[source][round(job["start_s"]*16000):round(job["end_s"]*16000)].copy()
        assert np.isfinite(samples).all() and len(samples) >= 16000
        # Opaque path prevents filename labels from becoming evidence.
        digest = hashlib.sha256(samples.tobytes()).hexdigest()
        clip = OUT / "modelo" / (digest[:12] + ".wav")
        if not clip.exists():
            sf.write(clip, samples, 16000, subtype="FLOAT")
        started = time.monotonic()
        result = generate(model, processor, formatted, audio=[str(clip)],
                          max_tokens=240, temperature=0.0, enable_thinking=False,
                          seed=20261001, verbose=False)
        raw = result.text
        parsed = parse(raw)
        row = {**job, "input_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
               "waveform_sha256": digest, "clip": str(clip), "raw": raw, "parsed": parsed,
               "elapsed_seconds": time.monotonic()-started,
               "peak_model_memory_gib": mx.get_peak_memory()/1024**3,
               "utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
        report["results"].append(row)
        dest.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n")
        print(job["id"], json.dumps(parsed if parsed else raw, ensure_ascii=False), f"{row['elapsed_seconds']:.1f}s", flush=True)
        gc.collect()
        mx.clear_cache()


if __name__ == "__main__":
    main()
