"""Download one pinned, public safetensors checkpoint; never execute model code."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import time

import requests

OUT = Path(__file__).resolve().parents[1]
CACHE = Path.home() / ".cache/codex-audio-perceptual/2026-10-01/models/qwen2.5-omni-7b-4bit"
REPO = "giangndm/qwen2.5-omni-7b-mlx-4bit"
REVISION = "cc80234b9ea0dc4461ad15a4c45e76d85b703b03"


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    global CACHE, REPO, REVISION
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["qwen", "gemma"], default="qwen")
    args = parser.parse_args()
    if args.model == "gemma":
        CACHE = CACHE.parent / "gemma-4-e2b-4bit"
        REPO = "mlx-community/gemma-4-E2B-it-4bit"
        REVISION = "238767527555cb75a05732a84dff5d6ba0dd6809"
    started = time.monotonic()
    session = requests.Session()
    meta_response = session.get(
        f"https://huggingface.co/api/models/{REPO}/revision/{REVISION}?blobs=true",
        timeout=30,
    )
    meta_response.raise_for_status()
    meta = meta_response.json()
    assert meta["sha"] == REVISION
    CACHE.mkdir(parents=True, exist_ok=True)
    (OUT / f"modelo/metadata-hf-{args.model}.json").write_text(json.dumps(meta, indent=2) + "\n")
    receipt = {"repo": REPO, "revision": REVISION, "cache": str(CACHE),
               "license_base": "Apache-2.0 (Qwen/Qwen2.5-Omni-7B/LICENSE)" if args.model == "qwen" else "Gemma 4 terms/base model card; quantization card retains gemma tag",
               "remote_model_code": False, "files": []}
    for entry in meta["siblings"]:
        name = entry["rfilename"]
        if name == ".gitattributes":
            continue
        target = CACHE / name
        expected = entry.get("size")
        remaining = 0 if target.exists() and target.stat().st_size == expected else expected
        if shutil.disk_usage(CACHE).free < remaining + 4 * 1024**3:
            raise RuntimeError("Insufficient disk headroom; retain at least 4 GiB.")
        if remaining:
            print(f"Downloading {name}: {expected} bytes", flush=True)
            url = f"https://huggingface.co/{REPO}/resolve/{REVISION}/{name}"
            partial = target.with_suffix(target.suffix + ".partial")
            with session.get(url, stream=True, timeout=(30, 180)) as response:
                response.raise_for_status()
                with partial.open("wb") as f:
                    downloaded = 0
                    last_report = time.monotonic()
                    for chunk in response.iter_content(4 * 1024 * 1024):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if time.monotonic() - last_report > 25:
                            print(f"{name}: {downloaded / 1024**2:.0f} MiB", flush=True)
                            last_report = time.monotonic()
            assert partial.stat().st_size == expected, (name, expected, partial.stat().st_size)
            partial.replace(target)
        sha = digest(target)
        lfs = entry.get("lfs", {})
        expected_sha = lfs.get("oid", lfs.get("sha256"))
        if expected_sha:
            assert sha == expected_sha, (name, sha, expected_sha)
        receipt["files"].append({"name": name, "bytes": target.stat().st_size,
                                 "sha256": sha, "upstream_sha256": expected_sha})
    receipt.update({"completed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "elapsed_seconds": time.monotonic() - started,
                    "free_gib_after": shutil.disk_usage(CACHE).free / 1024**3})
    (OUT / f"modelo/descarga-{args.model}.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({k: receipt[k] for k in ["repo", "revision", "elapsed_seconds", "free_gib_after"]}), flush=True)


if __name__ == "__main__":
    main()
