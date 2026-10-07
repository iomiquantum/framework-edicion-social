"""Google YAMNet audio-event evidence. Scores are model activations, not human audibility."""
import csv
import hashlib
import json
from pathlib import Path
import time

from ai_edge_litert.interpreter import Interpreter
import numpy as np
from scipy import signal
import soundfile as sf

from evaluar_indices import OUT, ROOT, read_audio, get_items

CACHE = Path.home() / ".cache/codex-audio-perceptual/2026-10-01/models/yamnet"
WINDOW_SAMPLES = 15600
HOP = 7680
SPEC = {
    "speech_only": {"Speech_mean_min": .5, "Music_mean_max": .2},
    "music_only": {"Music_mean_min": .5, "Speech_mean_max": .2},
    "silence": {"Speech_mean_max": .2, "Music_mean_max": .2},
    "no_voice": {"Speech_mean_max": .2},
    "music_excess": "Music mean must increase by at least .15 over balanced control.",
    "excluded_predeclared": ["Audibility of sparse original SFX", "Emotional suitability", "Human intelligibility/MOS", "Exact fader dB or genre identity"]
}


def main():
    started = time.monotonic()
    (OUT / "calibracion/criterios-yamnet.json").write_text(json.dumps(SPEC, indent=2)+"\n")
    labels = [r["display_name"] for r in csv.DictReader((CACHE/"yamnet_class_map.csv").open())]
    assert len(labels) == 521
    interpreter = Interpreter(model_path=str(CACHE/"model.tflite"), num_threads=2)
    interpreter.allocate_tensors()
    input_id = interpreter.get_input_details()[0]["index"]
    output_id = interpreter.get_output_details()[0]["index"]
    targets = [{"id": r["code"], "group": "calibration", "condition": r["condition"], "input": r["path"]}
               for r in json.loads((OUT/"calibracion/manifest.json").read_text())]
    targets += [{"id": i["id"], "group": "mix", "input": str(i["mix"])} for i in get_items()]
    for n, path in enumerate(["65B73BD5-A22A-4DC4-A9C5-D132C7C03C04.MP4", "31DAFCE4-1F8C-452E-B66D-489909CDBF67.MP4"]):
        targets.append({"id": f"ref-{n+1}", "group": "reference", "input": str(Path.home()/"Downloads"/path)})
    first = json.loads((ROOT/"Framework-Edicion-Social/research/prueba-mezcla-voz-2026-09-30/manifest.json").read_text())
    for i in first:
        targets.append({"id": i["id"]+"-voice", "group": "voice",
                        "input": str(ROOT/"Framework-Edicion-Social/research/prueba-mezcla-voz-2026-09-30/renders/v2"/(i["id"]+"-voz-sola.wav"))})
    report = {"engine": "Google YAMNet float32 / LiteRT2.2.0 CPU2threads", "labels": labels,
              "sample_rate": 16000, "window_s": WINDOW_SAMPLES/16000, "hop_s": HOP/16000,
              "model_sha256": hashlib.sha256((CACHE/"model.tflite").read_bytes()).hexdigest(),
              "human_listener": False, "interpretation": "Model activations; neither calibrated human probabilities nor fader recommendations.",
              "results": []}
    (OUT/"evidencia/yamnet-scores").mkdir(exist_ok=True)
    for item in targets:
        path = Path(item["input"])
        if item["group"] == "calibration":
            audio, fs = sf.read(path, dtype="float32")
            assert fs == 16000
        else:
            audio = signal.resample_poly(read_audio(path), 1, 3).astype(np.float32)
        frames, clock = [], []
        for start in range(0, len(audio), HOP):
            sample = audio[start:start+WINDOW_SAMPLES]
            # The last window includes a padded end; explicitly marked for interpretation.
            if len(sample) < WINDOW_SAMPLES:
                sample = np.pad(sample, (0, WINDOW_SAMPLES-len(sample)))
            interpreter.set_tensor(input_id, sample.astype(np.float32))
            interpreter.invoke()
            scores = interpreter.get_tensor(output_id)[0]
            assert scores.shape == (521,) and np.isfinite(scores).all()
            frames.append(scores);clock.append(start/16000)
        matrix = np.array(frames)
        filename = OUT/"evidencia/yamnet-scores"/(item["id"]+".npz")
        np.savez_compressed(filename, scores=matrix, time_s=np.array(clock))
        means = matrix.mean(axis=0)
        headline = {name: {"mean": float(means[labels.index(name)]), "max": float(matrix[:,labels.index(name)].max())}
                    for name in ["Speech", "Music", "Silence"]}
        row = {**item, "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
               "duration_s": len(audio)/16000, "frame_count": len(frames), "scores_file": str(filename),
               "top_classes": [{"label":labels[i], "mean_activation":float(means[i])}
                               for i in np.argsort(means)[-8:][::-1]],
               "headline": headline, "final_window_zero_padded": True}
        report["results"].append(row)
        (OUT/"evidencia/yamnet.json").write_text(json.dumps(report, ensure_ascii=False,indent=2)+"\n")
        print(item["id"], [(r["label"],round(r["mean_activation"],3)) for r in row["top_classes"][:3]],flush=True)
    controls = {r["condition"]: r["headline"] for r in report["results"] if r["group"] == "calibration"}
    checks = {
        "voice_solo": controls["voice_only"]["Speech"]["mean"]>.5 and controls["voice_only"]["Music"]["mean"]<.2,
        "music_solo": controls["music_only"]["Music"]["mean"]>.5 and controls["music_only"]["Speech"]["mean"]<.2,
        "silence_no_invented_sources": controls["silence"]["Speech"]["mean"]<.2 and controls["silence"]["Music"]["mean"]<.2,
        "no_voice": controls["no_voice"]["Speech"]["mean"]<.2,
        "music_excess_sensitivity": controls["music_masks"]["Music"]["mean"]>controls["balanced"]["Music"]["mean"]+.15,
    }
    (OUT/"calibracion/validacion-yamnet.json").write_text(json.dumps({
        "checks": checks,"pass":all(checks.values()),"excluded":SPEC["excluded_predeclared"],
        "elapsed_seconds":time.monotonic()-started},indent=2)+"\n")
    print('CALIBRATION',checks,'elapsed_s',time.monotonic()-started,flush=True)


if __name__ == "__main__":
    main()
