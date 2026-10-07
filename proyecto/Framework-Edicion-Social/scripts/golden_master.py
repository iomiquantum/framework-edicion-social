#!/usr/bin/env python3
"""Register and compare golden-master artifacts without rendering them.

The registry locks raw content hashes plus stable, automatically observed
metadata. Comparison is read-only and reports missing, hash-drift and
metadata-drift states independently.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path


ENTRY_ID_PATTERN = re.compile(r"^GM-[A-Z0-9_-]+$")
REGISTRY_ID_PATTERN = re.compile(r"^GOLDEN-MASTER-[A-Z0-9_-]+$")
KINDS = {"video", "audio", "image", "json", "document", "binary"}
VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}
AUDIO_SUFFIXES = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".tif", ".tiff"}
DOCUMENT_SUFFIXES = {".md", ".txt", ".pdf", ".docx", ".html", ".csv"}


def sha256(path: Path | str):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def infer_kind(path: Path):
    suffix = path.suffix.lower()
    if suffix in VIDEO_SUFFIXES:
        return "video"
    if suffix in AUDIO_SUFFIXES:
        return "audio"
    if suffix in IMAGE_SUFFIXES:
        return "image"
    if suffix == ".json":
        return "json"
    if suffix in DOCUMENT_SUFFIXES:
        return "document"
    return "binary"


def _fraction(value):
    if not value or value == "0/0":
        return None
    try:
        result = float(Fraction(value))
    except (ValueError, ZeroDivisionError):
        return None
    return round(result, 6)


def _ffprobe_metadata(path: Path):
    executable = shutil.which("ffprobe")
    if not executable:
        return {}
    command = [
        executable,
        "-v",
        "error",
        "-show_entries",
        "format=duration,format_name:stream=codec_type,codec_name,width,height,avg_frame_rate,sample_rate,channels",
        "-of",
        "json",
        str(path),
    ]
    try:
        completed = subprocess.run(command, check=True, capture_output=True, text=True)
        document = json.loads(completed.stdout)
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError):
        return {}

    metadata = {}
    format_info = document.get("format", {})
    if format_info.get("format_name"):
        metadata["container"] = format_info["format_name"]
    try:
        duration = float(format_info.get("duration"))
    except (TypeError, ValueError):
        duration = None
    if duration is not None and duration >= 0:
        metadata["duration_s"] = round(duration, 6)

    video_stream = next((item for item in document.get("streams", []) if item.get("codec_type") == "video"), None)
    audio_stream = next((item for item in document.get("streams", []) if item.get("codec_type") == "audio"), None)
    if video_stream:
        if isinstance(video_stream.get("width"), int):
            metadata["width"] = video_stream["width"]
        if isinstance(video_stream.get("height"), int):
            metadata["height"] = video_stream["height"]
        fps = _fraction(video_stream.get("avg_frame_rate"))
        if fps is not None:
            metadata["fps"] = fps
        if video_stream.get("codec_name"):
            metadata["video_codec"] = video_stream["codec_name"]
    if audio_stream:
        if audio_stream.get("codec_name"):
            metadata["audio_codec"] = audio_stream["codec_name"]
        try:
            sample_rate = int(audio_stream.get("sample_rate"))
        except (TypeError, ValueError):
            sample_rate = None
        if sample_rate:
            metadata["sample_rate_hz"] = sample_rate
        if isinstance(audio_stream.get("channels"), int):
            metadata["channels"] = audio_stream["channels"]
    return metadata


def inspect_artifact(path: Path | str, kind="auto"):
    path = Path(path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    resolved_kind = infer_kind(path) if kind == "auto" else kind
    if resolved_kind not in KINDS:
        raise ValueError(f"unsupported kind {resolved_kind!r}")
    mime_type, _ = mimetypes.guess_type(path.name)
    metadata = {
        "size_bytes": path.stat().st_size,
        "extension": path.suffix.lower(),
        "mime_type": mime_type,
    }
    if resolved_kind in {"video", "audio", "image"}:
        metadata.update(_ffprobe_metadata(path))
    elif resolved_kind == "json":
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            metadata.update({"json_type": "invalid", "document_schema_version": None})
        else:
            if isinstance(document, dict):
                json_type = "object"
                schema_version = document.get("schema_version")
            elif isinstance(document, list):
                json_type = "array"
                schema_version = None
            else:
                json_type = type(document).__name__
                schema_version = None
            metadata.update(
                {
                    "json_type": json_type,
                    "document_schema_version": str(schema_version) if schema_version is not None else None,
                }
            )
    return resolved_kind, metadata


def new_registry(registry_id="GOLDEN-MASTER-REGISTRY"):
    if not REGISTRY_ID_PATTERN.fullmatch(registry_id):
        raise ValueError(f"invalid registry id {registry_id!r}")
    return {
        "schema_version": "1.0.0",
        "registry_id": registry_id,
        "hash_algorithm": "sha256",
        "entries": [],
        "updated_at": None,
    }


def load_registry(path: Path | str, *, registry_id="GOLDEN-MASTER-REGISTRY", create=False):
    path = Path(path)
    if not path.exists():
        if create:
            return new_registry(registry_id)
        raise FileNotFoundError(path)
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("hash_algorithm") != "sha256" or not isinstance(document.get("entries"), list):
        raise ValueError("invalid golden-master registry")
    return document


def _stored_reference_path(artifact_path: Path, registry_path: Path):
    try:
        return str(artifact_path.relative_to(registry_path.parent.resolve()))
    except ValueError:
        return str(artifact_path)


def register_artifact(
    registry,
    registry_path,
    artifact_path,
    *,
    entry_id,
    label,
    kind="auto",
    source_id=None,
    notes="",
    registered_at=None,
    replace=False,
):
    if not ENTRY_ID_PATTERN.fullmatch(entry_id):
        raise ValueError(f"invalid golden-master entry id {entry_id!r}")
    artifact_path = Path(artifact_path).expanduser().resolve()
    registry_path = Path(registry_path).expanduser().resolve()
    resolved_kind, metadata = inspect_artifact(artifact_path, kind)
    existing = next((index for index, item in enumerate(registry["entries"]) if item.get("id") == entry_id), None)
    if existing is not None and not replace:
        raise ValueError(f"entry {entry_id} already exists; pass replace=True to update it")
    timestamp = registered_at or utc_now()
    entry = {
        "id": entry_id,
        "label": label,
        "kind": resolved_kind,
        "reference_path": _stored_reference_path(artifact_path, registry_path),
        "content_sha256": sha256(artifact_path),
        "metadata": metadata,
        "source_id": source_id,
        "notes": notes,
        "registered_at": timestamp,
    }
    if existing is None:
        registry["entries"].append(entry)
    else:
        registry["entries"][existing] = entry
    registry["entries"].sort(key=lambda item: item["id"])
    registry["updated_at"] = timestamp
    return entry


def write_registry(path: Path | str, registry):
    path = Path(path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _resolve_reference(entry, registry_path, root=None):
    reference = Path(entry["reference_path"])
    if reference.is_absolute():
        return reference
    base = Path(root).expanduser().resolve() if root else Path(registry_path).expanduser().resolve().parent
    return (base / reference).resolve()


def compare_registry(registry, registry_path, *, entry_ids=None, root=None):
    wanted = set(entry_ids or [])
    known = {item.get("id") for item in registry.get("entries", [])}
    unknown = sorted(wanted - known)
    if unknown:
        raise ValueError(f"unknown golden-master ids: {', '.join(unknown)}")
    entries = [item for item in registry.get("entries", []) if not wanted or item.get("id") in wanted]
    comparisons = []
    for entry in entries:
        path = _resolve_reference(entry, registry_path, root)
        if not path.is_file():
            comparisons.append(
                {
                    "id": entry["id"],
                    "status": "missing",
                    "path": str(path),
                    "expected_sha256": entry["content_sha256"],
                    "actual_sha256": None,
                    "metadata_differences": [],
                }
            )
            continue
        actual_hash = sha256(path)
        _, actual_metadata = inspect_artifact(path, entry["kind"])
        metadata_differences = []
        for key, expected in entry.get("metadata", {}).items():
            actual = actual_metadata.get(key)
            if actual != expected:
                metadata_differences.append({"field": key, "expected": expected, "actual": actual})
        hash_matches = actual_hash == entry["content_sha256"]
        metadata_matches = not metadata_differences
        if hash_matches and metadata_matches:
            status = "match"
        elif not hash_matches and not metadata_matches:
            status = "hash_and_metadata_mismatch"
        elif not hash_matches:
            status = "hash_mismatch"
        else:
            status = "metadata_mismatch"
        comparisons.append(
            {
                "id": entry["id"],
                "status": status,
                "path": str(path),
                "expected_sha256": entry["content_sha256"],
                "actual_sha256": actual_hash,
                "metadata_differences": metadata_differences,
            }
        )
    counts = {
        "total": len(comparisons),
        "match": sum(item["status"] == "match" for item in comparisons),
        "mismatch": sum(item["status"] != "match" for item in comparisons),
    }
    return {
        "schema_version": "1.0.0",
        "registry_id": registry.get("registry_id"),
        "hash_algorithm": "sha256",
        "counts": counts,
        "status": "match" if counts["mismatch"] == 0 else "mismatch",
        "comparisons": comparisons,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    register_parser = subparsers.add_parser("register", help="Hash and register one reference artifact")
    register_parser.add_argument("--registry", required=True)
    register_parser.add_argument("--registry-id", default="GOLDEN-MASTER-REGISTRY")
    register_parser.add_argument("--id", required=True)
    register_parser.add_argument("--file", required=True)
    register_parser.add_argument("--label", required=True)
    register_parser.add_argument("--kind", default="auto", choices=["auto", *sorted(KINDS)])
    register_parser.add_argument("--source-id")
    register_parser.add_argument("--notes", default="")
    register_parser.add_argument("--registered-at")
    register_parser.add_argument("--replace", action="store_true")

    compare_parser = subparsers.add_parser("compare", help="Compare files to locked hashes and metadata")
    compare_parser.add_argument("--registry", required=True)
    compare_parser.add_argument("--id", action="append", default=[])
    compare_parser.add_argument("--root", help="Override the base directory for relative reference paths")
    compare_parser.add_argument("--json", action="store_true")

    args = parser.parse_args()
    try:
        if args.command == "register":
            registry_path = Path(args.registry).expanduser().resolve()
            registry = load_registry(registry_path, registry_id=args.registry_id, create=True)
            entry = register_artifact(
                registry,
                registry_path,
                args.file,
                entry_id=args.id,
                label=args.label,
                kind=args.kind,
                source_id=args.source_id,
                notes=args.notes,
                registered_at=args.registered_at,
                replace=args.replace,
            )
            write_registry(registry_path, registry)
            print(json.dumps(entry, ensure_ascii=False, indent=2))
            return 0

        registry_path = Path(args.registry).expanduser().resolve()
        report = compare_registry(
            load_registry(registry_path),
            registry_path,
            entry_ids=args.id,
            root=args.root,
        )
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(
                f"GOLDEN MASTER {report['status'].upper()}: "
                f"{report['counts']['match']}/{report['counts']['total']} match"
            )
            for item in report["comparisons"]:
                print(f"- {item['id']}: {item['status']} [{item['path']}]")
        return 0 if report["status"] == "match" else 1
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"golden-master error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
