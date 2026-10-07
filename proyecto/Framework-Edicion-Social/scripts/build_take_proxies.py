#!/usr/bin/env python3
"""Create accurate lightweight proxies for approved ranges in a take-map."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def run(command):
    subprocess.run(command, check=True)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe(path):
    completed = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration:stream=index,codec_type,codec_name,width,height,sample_rate,channels",
            "-of", "json", str(path)
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def verify_proxy(path, expected_duration):
    metadata = probe(path)
    streams = metadata.get("streams", [])
    if not any(stream.get("codec_type") == "video" for stream in streams):
        raise SystemExit(f"Proxy has no video stream: {path}")
    if not any(stream.get("codec_type") == "audio" for stream in streams):
        raise SystemExit(f"Proxy has no audio stream: {path}")
    actual_duration = float(metadata.get("format", {}).get("duration", 0))
    tolerance = max(0.25, expected_duration * 0.005)
    if abs(actual_duration - expected_duration) > tolerance:
        raise SystemExit(
            f"Proxy duration mismatch for {path}: expected {expected_duration:.3f}s, got {actual_duration:.3f}s"
        )
    return metadata, actual_duration


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--take-map", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--include-all-approved", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--max-dimension", type=int, default=1280)
    args = parser.parse_args()

    map_path = Path(args.take_map).expanduser().resolve()
    project = Path(args.project).expanduser().resolve()
    take_map = json.loads(map_path.read_text(encoding="utf-8"))
    source = Path(take_map["source"]["path"])
    audio_index = take_map["source"].get("audio_stream_index")
    if not source.is_file():
        raise SystemExit(f"Source not found: {source}")
    if audio_index is None:
        raise SystemExit("audio_stream_index must be selected by listening before proxy creation")
    if not take_map.get("qa", {}).get("human_review_completed"):
        raise SystemExit("take-map human review is not complete; set qa.human_review_completed=true after checking markers")

    outputs = []
    for video in take_map.get("videos", []):
        approved = [take for take in video.get("takes", []) if take.get("decision", {}).get("status") == "approved"]
        selected_take_id = video.get("selected_take_id")
        if not args.include_all_approved:
            if len(approved) > 1 and not selected_take_id:
                raise SystemExit(
                    f"{video['video_id']} has multiple approved takes and no selected_take_id; review the map or use --include-all-approved"
                )
            if selected_take_id:
                approved = [take for take in approved if take["take_id"] == selected_take_id]
                if not approved:
                    raise SystemExit(
                        f"{video['video_id']} selected_take_id is not an approved take: {selected_take_id}"
                    )
        for take in approved:
            start = float(take["candidate_range"]["start_s"])
            end = float(take["candidate_range"]["end_s"])
            if end <= start:
                raise SystemExit(f"Invalid range for {take['take_id']}: {start}..{end}")
            video_dir = project / video["video_id"] / "source"
            video_dir.mkdir(parents=True, exist_ok=True)
            proxy = video_dir / f"{take['take_id'].lower()}-proxy.mp4"
            range_file = video_dir / f"{take['take_id'].lower()}-source-range.json"
            duration = end - start
            if proxy.exists() and not args.force:
                print(f"skip existing: {proxy}")
            else:
                coarse = max(0.0, start - 2.0)
                fine = start - coarse
                scale = f"scale={args.max_dimension}:{args.max_dimension}:force_original_aspect_ratio=decrease:force_divisible_by=2"
                partial = proxy.with_name(f"{proxy.stem}.partial{proxy.suffix}")
                command = [
                    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-ss", f"{coarse:.6f}", "-i", str(source),
                    "-ss", f"{fine:.6f}", "-t", f"{duration:.6f}",
                    "-map", "0:v:0", "-map", f"0:{audio_index}",
                    "-vf", scale, "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
                    str(partial)
                ]
                run(command)
                verify_proxy(partial, duration)
                partial.replace(proxy)
                print(f"proxy: {proxy}")
            proxy_probe, proxy_duration = verify_proxy(proxy, duration)
            range_data = {
                "schema_version": "1.0.0",
                "video_id": video["video_id"],
                "take_id": take["take_id"],
                "proxy": str(proxy),
                "original_source": str(source),
                "original_source_sha256": take_map["source"].get("sha256", ""),
                "source_in_s": start,
                "source_out_s": end,
                "duration_s": end - start,
                "audio_stream_index": audio_index,
                "proxy_sha256": sha256(proxy),
                "proxy_duration_s": proxy_duration,
                "proxy_streams": proxy_probe.get("streams", []),
                "verification_status": "pass",
                "proxy_is_editing_only": True,
                "final_render_must_use_original": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            range_file.write_text(json.dumps(range_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            outputs.append(range_data)

    manifest = map_path.parent / f"{map_path.stem}-proxy-manifest.json"
    manifest.write_text(json.dumps({"schema_version": "1.0.0", "outputs": outputs}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"proxy manifest: {manifest} ({len(outputs)} outputs)")


if __name__ == "__main__":
    main()
