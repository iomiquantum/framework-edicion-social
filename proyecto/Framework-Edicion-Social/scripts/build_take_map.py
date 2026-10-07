#!/usr/bin/env python3
"""Compile one word-timestamp transcript into a marker/take map."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path


NUMBER_WORDS = {
    "uno": 1, "una": 1, "un": 1, "dos": 2, "tres": 3, "cuatro": 4,
    "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize(text):
    text = unicodedata.normalize("NFD", str(text).lower())
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return re.sub(r"[^a-z0-9]+", "", text)


def number(token):
    token = normalize(token)
    if token.isdigit():
        return int(token)
    return NUMBER_WORDS.get(token)


def load_words(path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    words = raw.get("words", raw) if isinstance(raw, dict) else raw
    normalized = []
    for index, item in enumerate(words):
        if not isinstance(item, dict):
            continue
        text = item.get("text", item.get("word", ""))
        start = item.get("start")
        end = item.get("end")
        if text and start is not None and end is not None:
            normalized.append({"index": index, "text": str(text), "token": normalize(text), "start": float(start), "end": float(end)})
    return normalized, raw


def marker_type(window):
    tokens = [item["token"] for item in window]
    if "fin" in tokens and ("sesion" in tokens or "grabacion" in tokens):
        end_offset = max(tokens.index("fin"), tokens.index("sesion") if "sesion" in tokens else tokens.index("grabacion"))
        return "session_end", {"end_offset": end_offset}
    corrected = [index for index, token in enumerate(tokens) if token.startswith("correg")]
    if len(corrected) >= 2 and "ultima" in tokens and "frase" in tokens:
        end_offset = max(corrected[1], tokens.index("ultima"), tokens.index("frase"))
        return "replace_previous_phrase", {"end_offset": end_offset}
    approved = [index for index, token in enumerate(tokens) if token.startswith("aprobad")]
    discarded = [index for index, token in enumerate(tokens) if token.startswith("descart") or token == "error"]
    if len(approved) >= 2:
        return "approved", {"end_offset": approved[1]}
    if len(discarded) >= 2:
        return "discarded", {"end_offset": discarded[1]}
    if "video" in tokens and "toma" in tokens:
        video_pos = tokens.index("video")
        take_pos = tokens.index("toma")
        video_number = number(tokens[video_pos + 1]) if video_pos + 1 < len(tokens) else None
        take_number = number(tokens[take_pos + 1]) if take_pos + 1 < len(tokens) else None
        has_start_keyword = "inicio" in tokens
        start_pos = tokens.index("inicio") if has_start_keyword else take_pos + 1
        if video_pos < take_pos <= start_pos and video_number is not None and take_number is not None:
            return "take_start", {
                "video_number": video_number,
                "take_number": take_number,
                "end_offset": start_pos,
                "protocol_variant": "compact_v1" if has_start_keyword else "missing_inicio_keyword",
            }
    return "unknown", {"end_offset": len(window) - 1}


def detect_markers(words):
    starts = [index for index, word in enumerate(words) if word["token"] == "marcador"]
    markers = []
    for marker_index, start in enumerate(starts):
        next_start = starts[marker_index + 1] if marker_index + 1 < len(starts) else len(words)
        window = words[start:min(next_start, start + 16)]
        kind, details = marker_type(window)
        end_offset = details.pop("end_offset")
        marker_words = window[:end_offset + 1]
        confidence = 0.0 if kind == "unknown" else 1.0
        if details.get("protocol_variant") == "missing_inicio_keyword":
            confidence = 0.9
        markers.append({
            "kind": kind,
            "start_s": window[0]["start"],
            "end_s": marker_words[-1]["end"],
            "raw": " ".join(item["text"] for item in marker_words),
            "confidence": confidence,
            **details,
        })
    return markers


def compile_takes_with_diagnostics(markers, transcript_end):
    takes = []
    active = None
    orphan_decisions = []
    seen_take_ids = set()
    for marker in markers:
        if marker["kind"] == "take_start":
            if active:
                active["decision"] = {"status": "ambiguous_unclosed", "marker_start_s": None, "marker_end_s": None}
                active["candidate_range"]["end_s"] = marker["start_s"]
                takes.append(active)
            video_id = f"VIDEO-{marker['video_number']:02d}"
            take_id = f"{video_id}-TAKE-{marker['take_number']:02d}"
            warnings = []
            if marker.get("protocol_variant") == "missing_inicio_keyword":
                warnings.append("start_marker_missing_inicio_keyword")
            if take_id in seen_take_ids:
                warnings.append("duplicate_take_id")
            seen_take_ids.add(take_id)
            active = {
                "take_id": take_id,
                "video_id": video_id,
                "take_number": marker["take_number"],
                "start_marker": marker,
                "candidate_range": {"start_s": marker["end_s"], "end_s": None},
                "decision": {"status": "open", "marker_start_s": None, "marker_end_s": None},
                "corrections": [],
                "warnings": warnings
            }
        elif marker["kind"] == "replace_previous_phrase":
            if not active:
                continue
            active["corrections"].append({
                "operation": "replace_previous_phrase",
                "status": "pending_audio_review",
                "marker_start_s": marker["start_s"],
                "marker_end_s": marker["end_s"],
                "raw": marker["raw"],
                "target_range": {
                    "start_s": None,
                    "end_s": marker["start_s"]
                },
                "replacement_range": {
                    "start_s": marker["end_s"],
                    "end_s": None
                },
                "review_rule": "Locate the complete previous phrase and the complete replacement by listening; do not rely on ASR punctuation alone."
            })
        elif marker["kind"] in {"approved", "discarded"}:
            if not active:
                orphan_decisions.append(marker)
                continue
            active["candidate_range"]["end_s"] = marker["start_s"]
            active["decision"] = {
                "status": marker["kind"],
                "marker_start_s": marker["start_s"],
                "marker_end_s": marker["end_s"],
                "raw": marker["raw"]
            }
            takes.append(active)
            active = None
        elif marker["kind"] == "session_end" and active:
            active["candidate_range"]["end_s"] = marker["start_s"]
            active["decision"] = {"status": "ambiguous_unclosed", "marker_start_s": marker["start_s"], "marker_end_s": marker["end_s"]}
            takes.append(active)
            active = None
    if active:
        active["candidate_range"]["end_s"] = transcript_end
        active["decision"] = {"status": "ambiguous_unclosed", "marker_start_s": None, "marker_end_s": None}
        takes.append(active)
    return takes, orphan_decisions


def compile_takes(markers, transcript_end):
    """Backward-compatible take list used by callers and tests."""
    takes, _ = compile_takes_with_diagnostics(markers, transcript_end)
    return takes


def find_orphan_corrections(markers, takes):
    attached = {
        correction["marker_start_s"]
        for take in takes
        for correction in take.get("corrections", [])
    }
    return [
        marker for marker in markers
        if marker["kind"] == "replace_previous_phrase" and marker["start_s"] not in attached
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transcript", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--source-sha256", default="")
    parser.add_argument("--fps", type=float, default=30)
    parser.add_argument("--audio-stream-index", type=int)
    parser.add_argument("--language", default="es")
    parser.add_argument("--engine", default="unknown")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    transcript_path = Path(args.transcript).expanduser().resolve()
    source_path = Path(args.source).expanduser().resolve()
    out_path = Path(args.out).expanduser().resolve()
    words, _ = load_words(transcript_path)
    if not words:
        raise SystemExit("Transcript contains no normalized word timestamps")
    markers = detect_markers(words)
    takes, orphan_decisions = compile_takes_with_diagnostics(markers, words[-1]["end"])
    orphan_corrections = find_orphan_corrections(markers, takes)

    by_video = {}
    for take in takes:
        by_video.setdefault(take["video_id"], []).append(take)
    videos = []
    multiple = []
    for video_id in sorted(by_video):
        video_takes = by_video[video_id]
        approved = [take for take in video_takes if take["decision"]["status"] == "approved"]
        selected = approved[0]["take_id"] if len(approved) == 1 else None
        if len(approved) > 1:
            multiple.append(video_id)
        videos.append({"video_id": video_id, "selected_take_id": selected, "takes": video_takes})

    statuses = [take["decision"]["status"] for take in takes]
    duplicate_take_ids = sorted(
        take["take_id"] for take in takes if "duplicate_take_id" in take.get("warnings", [])
    )
    now = datetime.now(timezone.utc).isoformat()
    result = {
        "schema_version": "1.1.0",
        "project_id": args.project_id,
        "source": {
            "id": args.source_id,
            "path": str(source_path),
            "sha256": args.source_sha256 or "",
            "fps": args.fps,
            "audio_stream_index": args.audio_stream_index
        },
        "transcript": {
            "path": str(transcript_path),
            "sha256": sha256(transcript_path),
            "language": args.language,
            "engine": args.engine,
            "word_timestamps": True
        },
        "marker_protocol": "compact_v2",
        "videos": videos,
        "qa": {
            "marker_count": len(markers),
            "unknown_markers": [marker for marker in markers if marker["kind"] == "unknown"],
            "orphan_decision_markers": orphan_decisions,
            "orphan_correction_markers": orphan_corrections,
            "correction_markers": sum(len(take.get("corrections", [])) for take in takes),
            "unresolved_corrections": [
                {"take_id": take["take_id"], **correction}
                for take in takes
                for correction in take.get("corrections", [])
                if correction.get("status") != "resolved"
            ],
            "approved_takes": statuses.count("approved"),
            "discarded_takes": statuses.count("discarded"),
            "ambiguous_takes": sum(status.startswith("ambiguous") for status in statuses),
            "multiple_approved_videos": multiple,
            "duplicate_take_ids": duplicate_take_ids,
            "human_review_required": True,
            "human_review_completed": False,
            "notes": []
        },
        "generated_at": now,
        "updated_at": now
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"take map: {out_path} ({len(videos)} videos, {len(takes)} takes, {len(markers)} markers)")


if __name__ == "__main__":
    main()
