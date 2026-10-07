#!/usr/bin/env python3
"""Build and query a deterministic, provenance-aware media asset index.

The index deliberately distinguishes three operations:

* exact-content deduplication, which is proven by SHA-256;
* semantic ranking, which uses declared text metadata only; and
* fatigue warnings, which are advisory and never silently block a candidate.

It does not calculate perceptual image similarity and never labels semantic
matches as visually similar.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "1.0.0"
SCRIPT_DIR = Path(__file__).resolve().parent
FRAMEWORK_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from schema_validation import load_json as load_schema_json  # noqa: E402
from schema_validation import validate_document  # noqa: E402


DEFAULT_CATALOG = FRAMEWORK_ROOT / "library/catalog.json"
ASSET_INDEX_SCHEMA = FRAMEWORK_ROOT / "schemas/asset-index.schema.json"

MEDIA_EXTENSIONS = {
    ".aac",
    ".avif",
    ".cube",
    ".flac",
    ".gif",
    ".jpeg",
    ".jpg",
    ".m4a",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp3",
    ".mp4",
    ".ogg",
    ".png",
    ".svg",
    ".wav",
    ".webm",
    ".webp",
}

KNOWN_TYPES = {
    "bgm",
    "icon",
    "image",
    "logo",
    "lut",
    "motion_preset",
    "sfx",
    "transition",
    "typographic_overlay",
    "video",
    "voice",
    "unknown",
}

STATUS_PRIORITY = {
    "rejected": 5,
    "deprecated": 4,
    "approved": 3,
    "provisional": 2,
    "unknown": 1,
}

SOURCE_PRIORITY = {
    "framework_catalog": 50,
    "project_manifest": 40,
    "asset_lock": 35,
    "media_use_manifest": 30,
    "explicit_folder": 10,
}

REUSE_STRICTNESS = {
    "do_not_reuse": 5,
    "exact_match_only": 4,
    "limited": 3,
    "rotate": 2,
    "unlimited": 1,
    "unclassified": 0,
}

DEFAULT_COOLDOWN_BY_TYPE = {
    "bgm": 3,
    "icon": 1,
    "image": 2,
    "logo": 0,
    "lut": 1,
    "motion_preset": 2,
    "sfx": 1,
    "transition": 2,
    "typographic_overlay": 2,
    "video": 2,
    "voice": 0,
    "unknown": 1,
}

IGNORED_DIRECTORY_NAMES = {".git", "node_modules", "__pycache__"}
VIDEO_SEQUENCE_RE = re.compile(r"(?:^|[^A-Z0-9])VIDEO[-_ ]?0*([0-9]{1,4})(?:$|[^A-Z0-9])", re.I)
TOKEN_RE = re.compile(r"[a-z0-9]+")
DATE_TIME_RE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})$"
)
STOPWORDS = {
    "a",
    "al",
    "and",
    "con",
    "de",
    "del",
    "el",
    "en",
    "for",
    "la",
    "las",
    "los",
    "of",
    "para",
    "por",
    "the",
    "un",
    "una",
    "y",
}


class AssetIndexError(ValueError):
    """Raised when an input would make the asset index untrustworthy."""


def _json_load(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise AssetIndexError(f"Cannot read JSON {path}: {error}") from error


def _jsonl_load(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError as error:
                    raise AssetIndexError(
                        f"Invalid JSONL {path}:{line_number}: {error}"
                    ) from error
                if not isinstance(value, dict):
                    raise AssetIndexError(f"{path}:{line_number} must contain an object")
                records.append(value)
    except OSError as error:
        raise AssetIndexError(f"Cannot read JSONL {path}: {error}") from error
    return records


def _parse_datetime(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not DATE_TIME_RE.fullmatch(value):
        raise AssetIndexError(f"{label} must be an RFC 3339 date-time")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise AssetIndexError(f"{label} must be a valid RFC 3339 date-time") from error
    return parsed.astimezone(timezone.utc)


def _canonical_datetime(
    value: Any, label: str, *, allow_legacy_date: bool = False
) -> str | None:
    if value is None:
        return None
    if allow_legacy_date and isinstance(value, str) and re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value
    ):
        try:
            parsed_date = date.fromisoformat(value)
        except ValueError as error:
            raise AssetIndexError(f"{label} must be a valid calendar date") from error
        return datetime.combine(
            parsed_date, datetime.min.time(), tzinfo=timezone.utc
        ).isoformat().replace("+00:00", "Z")
    return _parse_datetime(value, label).isoformat().replace("+00:00", "Z")


def _latest_datetime(values: Iterable[str]) -> str | None:
    parsed = [(_parse_datetime(value, "last_used_at"), value) for value in values]
    if not parsed:
        return None
    return max(parsed, key=lambda pair: pair[0])[0].isoformat().replace("+00:00", "Z")


def validate_index_document(index: Any) -> None:
    errors = validate_document(index, load_schema_json(ASSET_INDEX_SCHEMA))
    if errors:
        raise AssetIndexError("Invalid asset index: " + "; ".join(errors))


def _lexical_absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _is_within(path: Path, boundary: Path) -> bool:
    try:
        path.relative_to(boundary)
        return True
    except ValueError:
        return False


def _assert_no_symlink_chain(boundary: Path, candidate: Path, *, require_exists: bool = True) -> Path:
    """Return a lexical absolute path after containment and symlink checks.

    System ancestors above ``boundary`` are outside this function's trust
    boundary; every component at or below the boundary is checked.
    """

    boundary_abs = _lexical_absolute(boundary)
    candidate_abs = _lexical_absolute(candidate)
    if not _is_within(candidate_abs, boundary_abs):
        raise AssetIndexError(f"Path escapes its allowed root: {candidate_abs} not in {boundary_abs}")
    if not boundary_abs.exists():
        raise AssetIndexError(f"Allowed root does not exist: {boundary_abs}")
    if boundary_abs.is_symlink():
        raise AssetIndexError(f"Symlink roots are not allowed: {boundary_abs}")

    current = boundary_abs
    relative = candidate_abs.relative_to(boundary_abs)
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise AssetIndexError(f"Symlink paths are not allowed: {current}")
        if not current.exists():
            if require_exists:
                raise AssetIndexError(f"Path does not exist: {current}")
            break

    if require_exists and not candidate_abs.exists():
        raise AssetIndexError(f"Path does not exist: {candidate_abs}")
    if candidate_abs.exists():
        resolved_boundary = boundary_abs.resolve(strict=True)
        resolved_candidate = candidate_abs.resolve(strict=True)
        if not _is_within(resolved_candidate, resolved_boundary):
            raise AssetIndexError(f"Resolved path escapes its allowed root: {candidate_abs}")
    return candidate_abs


def _safe_input(path: Path | str, *, directory: bool | None = None) -> Path:
    candidate = _lexical_absolute(Path(path))
    boundary = candidate if candidate.is_dir() else candidate.parent
    checked = _assert_no_symlink_chain(boundary, candidate)
    if directory is True and not checked.is_dir():
        raise AssetIndexError(f"Expected directory: {checked}")
    if directory is False and not checked.is_file():
        raise AssetIndexError(f"Expected regular file: {checked}")
    return checked


def _safe_member(boundary: Path, value: str | Path, *, regular_file: bool = True) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = boundary / candidate
    checked = _assert_no_symlink_chain(boundary, candidate)
    if regular_file and not checked.is_file():
        raise AssetIndexError(f"Expected regular file: {checked}")
    return checked


def _safe_output(project_root: Path, output: Path | str) -> Path:
    output_path = _lexical_absolute(Path(output))
    root = _safe_input(project_root, directory=True)
    if not _is_within(output_path, root):
        raise AssetIndexError(f"Output must stay inside project root: {output_path}")
    parent = output_path.parent
    # Only create a missing suffix below the first verified existing parent.
    existing = parent
    while not existing.exists() and existing != root:
        existing = existing.parent
    _assert_no_symlink_chain(root, existing)
    if existing != parent:
        relative = parent.relative_to(existing)
        current = existing
        for part in relative.parts:
            current = current / part
            current.mkdir()
            if current.is_symlink():
                raise AssetIndexError(f"Symlink output directory is not allowed: {current}")
    _assert_no_symlink_chain(root, parent)
    if output_path.exists() and (output_path.is_symlink() or not output_path.is_file()):
        raise AssetIndexError(f"Output is not a safe regular file: {output_path}")
    return output_path


def _safe_project_input(
    project_root: Path, path: Path | str, *, directory: bool
) -> Path:
    """Validate an input that is required to stay inside the project root."""

    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = project_root / candidate
    checked = _assert_no_symlink_chain(project_root, candidate)
    if directory and not checked.is_dir():
        raise AssetIndexError(f"Expected directory: {checked}")
    if not directory and not checked.is_file():
        raise AssetIndexError(f"Expected regular file: {checked}")
    return checked


def _safe_catalog_input(project_root: Path, path: Path | str) -> Path:
    """Allow catalogs only from the project or the installed framework tree."""

    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = project_root / candidate
    candidate = _lexical_absolute(candidate)
    framework_root = _lexical_absolute(FRAMEWORK_ROOT)
    for boundary in (project_root, framework_root):
        if _is_within(candidate, boundary):
            checked = _assert_no_symlink_chain(boundary, candidate)
            if not checked.is_file():
                raise AssetIndexError(f"Expected catalog file: {checked}")
            return checked
    raise AssetIndexError(
        "Catalog must be inside the project root or installed framework root; "
        f"choose a common --project-root for external catalogs: {candidate}"
    )


def _atomic_write_json(path: Path, value: Any) -> None:
    payload = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_name = handle.name
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    finally:
        if temporary_name and Path(temporary_name).exists():
            Path(temporary_name).unlink()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _tokens(value: str) -> set[str]:
    return {token for token in TOKEN_RE.findall(_normalize_text(value)) if token not in STOPWORDS}


def _unique_strings(values: Iterable[Any]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not isinstance(value, str):
            continue
        cleaned = " ".join(value.split())
        if not cleaned:
            continue
        key = cleaned.casefold()
        if key not in seen:
            seen.add(key)
            result.append(cleaned)
    return result


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def _display_path(path: Path, project_root: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()


def _infer_type(path: Path, declared: Any = None) -> str:
    if isinstance(declared, str):
        normalized = declared.casefold().replace("-", "_")
        aliases = {
            "audio": "sfx",
            "music": "bgm",
            "photo": "image",
            "graphic": "image",
            "typography": "typographic_overlay",
        }
        normalized = aliases.get(normalized, normalized)
        if normalized in KNOWN_TYPES:
            return normalized
    suffix = path.suffix.casefold()
    haystack = " ".join(part.casefold() for part in path.parts[-4:])
    if suffix == ".cube":
        return "lut"
    if suffix in {".mp4", ".mov", ".m4v", ".mkv", ".webm"}:
        return "video"
    if suffix in {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"}:
        if any(word in haystack for word in ("music", "bgm", "bed", "musica")):
            return "bgm"
        if any(word in haystack for word in ("voice", "voiceover", "narration", "voz")):
            return "voice"
        return "sfx"
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif", ".svg"}:
        if "logo" in haystack:
            return "logo"
        if "icon" in haystack:
            return "icon"
        if any(word in haystack for word in ("typographic", "lettering", "type_", "type-")):
            return "typographic_overlay"
        return "image"
    return "unknown"


def _normalize_status(item: dict[str, Any], default: str) -> str:
    status = item.get("status")
    approval = item.get("approval") if isinstance(item.get("approval"), dict) else {}
    if (
        approval.get("editorial_status") == "rejected"
        or approval.get("user_approval_status") == "explicit_rejected"
        or item.get("user_approval_status") == "explicit_rejected"
    ):
        return "rejected"
    if approval.get("reuse_status") == "ineligible":
        return "rejected"
    if status in {"approved", "provisional", "deprecated", "rejected"}:
        return status
    catalog_status = item.get("catalog_status")
    if catalog_status in {"approved", "provisional", "deprecated", "rejected"}:
        return catalog_status
    return default


def _video_sequence(value: str) -> int | None:
    match = VIDEO_SEQUENCE_RE.search(value)
    return int(match.group(1)) if match else None


def _verified_hash(path: Path, declared: Any, source_ref: str) -> str:
    actual = sha256_file(path)
    if declared is not None:
        if not isinstance(declared, str) or not re.fullmatch(r"[a-f0-9]{64}", declared):
            raise AssetIndexError(f"Invalid declared SHA-256 for {source_ref}")
        if declared != actual:
            raise AssetIndexError(
                f"Hash mismatch for {source_ref}: declared {declared}, actual {actual}"
            )
    return actual


def _make_record(
    *,
    path: Path,
    project_root: Path,
    source_kind: str,
    source_ref: str,
    item: dict[str, Any],
    default_status: str,
    declared_hash: Any = None,
) -> dict[str, Any]:
    asset_type = _infer_type(path, item.get("type"))
    description = item.get("description") if isinstance(item.get("description"), str) else path.stem
    asset_id = item.get("id") or item.get("resource_id") or item.get("source_asset_id")
    reuse = item.get("reuse") if isinstance(item.get("reuse"), dict) else {}
    provenance = item.get("provenance") if isinstance(item.get("provenance"), dict) else {}
    used_in = _unique_strings(_strings(reuse.get("used_in")) + _strings(item.get("used_in")))
    sequences = [sequence for value in used_in if (sequence := _video_sequence(value)) is not None]
    return {
        "source_kind": source_kind,
        "source_priority": SOURCE_PRIORITY[source_kind],
        "source_ref": source_ref,
        "source_asset_id": asset_id if isinstance(asset_id, str) and asset_id.strip() else None,
        "path": _display_path(path, project_root),
        "sha256": _verified_hash(path, declared_hash, f"{source_ref}:{asset_id or path.name}"),
        "bytes": path.stat().st_size,
        "format": path.suffix.casefold().lstrip(".") or "unknown",
        "type": asset_type,
        "name": item.get("name") if isinstance(item.get("name"), str) else path.stem,
        "description": description,
        "semantic_tags": _unique_strings(
            _strings(item.get("semantic_tags"))
            + _strings(item.get("tags"))
            + _strings(item.get("style_tags"))
        ),
        "intent_phrases": _unique_strings(
            _strings(item.get("best_for"))
            + _strings(item.get("best_use"))
            + _strings(item.get("prompt"))
        ),
        "avoid_for": _unique_strings(
            _strings(item.get("avoid_for")) + _strings(item.get("avoid_when"))
        ),
        "status": _normalize_status(item, default_status),
        "provenance": provenance,
        "technical": item.get("technical") if isinstance(item.get("technical"), dict) else {},
        "reuse_policy": reuse.get("policy") if reuse.get("policy") in REUSE_STRICTNESS else "unclassified",
        "cooldown_videos": reuse.get("cooldown_videos")
        if isinstance(reuse.get("cooldown_videos"), int)
        and not isinstance(reuse.get("cooldown_videos"), bool)
        and reuse.get("cooldown_videos") >= 0
        else None,
        "usage_count": reuse.get("usage_count")
        if isinstance(reuse.get("usage_count"), int)
        and not isinstance(reuse.get("usage_count"), bool)
        and reuse.get("usage_count") >= 0
        else 0,
        "used_in": used_in,
        "last_used_at": _canonical_datetime(
            reuse.get("last_used_at"),
            f"reuse.last_used_at for {source_ref}:{asset_id or path.name}",
            allow_legacy_date=True,
        ),
        "last_used_sequence": max(sequences) if sequences else None,
        "raw_approval": item.get("approval") if isinstance(item.get("approval"), dict) else {},
    }


def _catalog_records(path: Path, project_root: Path) -> list[dict[str, Any]]:
    document = _json_load(path)
    if not isinstance(document, dict) or not isinstance(document.get("assets"), list):
        raise AssetIndexError(f"Catalog must contain an assets array: {path}")
    records = []
    for index, item in enumerate(document["assets"]):
        if not isinstance(item, dict) or not isinstance(item.get("file"), str):
            raise AssetIndexError(f"Invalid asset at {path}:assets[{index}]")
        media_path = _safe_member(path.parent, item["file"])
        records.append(
            _make_record(
                path=media_path,
                project_root=project_root,
                source_kind="framework_catalog",
                source_ref=_display_path(path, project_root),
                item=item,
                default_status="unknown",
                declared_hash=item.get("sha256"),
            )
        )
    return records


def _media_use_records(path: Path, project_root: Path) -> list[dict[str, Any]]:
    items = _jsonl_load(path)
    media_project_root = path.parent.parent if path.parent.name == ".media" else path.parent
    records = []
    for index, item in enumerate(items):
        if not isinstance(item.get("path"), str):
            raise AssetIndexError(f"Missing path at {path}:{index + 1}")
        media_path = _safe_member(media_project_root, item["path"])
        records.append(
            _make_record(
                path=media_path,
                project_root=project_root,
                source_kind="media_use_manifest",
                source_ref=_display_path(path, project_root),
                item=item,
                default_status="provisional",
                declared_hash=item.get("sha256"),
            )
        )
    return records


def _project_manifest_records(path: Path, project_root: Path) -> list[dict[str, Any]]:
    document = _json_load(path)
    if not isinstance(document, dict):
        raise AssetIndexError(f"Manifest must contain an object: {path}")

    if isinstance(document.get("resources"), list):
        source_kind = "project_manifest"
        resource_items = [(item, path.parent) for item in document["resources"]]
    elif isinstance(document.get("videos"), list):
        source_kind = "asset_lock"
        resource_items = []
        for video_index, video in enumerate(document["videos"]):
            if not isinstance(video, dict) or not isinstance(video.get("resources"), list):
                raise AssetIndexError(f"Invalid videos[{video_index}] in {path}")
            resource_items.extend((item, path.parent) for item in video["resources"])
    elif isinstance(document.get("assets"), list):
        source_kind = "project_manifest"
        resource_items = [(item, path.parent) for item in document["assets"]]
    else:
        raise AssetIndexError(f"Unsupported manifest structure: {path}")

    records = []
    for index, pair in enumerate(resource_items):
        item, base = pair
        if not isinstance(item, dict):
            raise AssetIndexError(f"Invalid resource {index} in {path}")
        file_value = item.get("file") or item.get("project_file") or item.get("path")
        if not isinstance(file_value, str):
            raise AssetIndexError(f"Resource {index} has no file/path in {path}")
        media_path = _safe_member(base, file_value)
        declared_hash = item.get("sha256") or item.get("project_sha256")
        records.append(
            _make_record(
                path=media_path,
                project_root=project_root,
                source_kind=source_kind,
                source_ref=_display_path(path, project_root),
                item=item,
                default_status="provisional",
                declared_hash=declared_hash,
            )
        )
    return records


def _folder_records(path: Path, project_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for current_root, directory_names, file_names in os.walk(path, followlinks=False):
        root_path = Path(current_root)
        safe_directories = []
        for name in sorted(directory_names):
            child = root_path / name
            if name in IGNORED_DIRECTORY_NAMES:
                continue
            if child.is_symlink():
                raise AssetIndexError(f"Symlink directory found in explicit asset root: {child}")
            safe_directories.append(name)
        directory_names[:] = safe_directories
        for name in sorted(file_names):
            media_path = root_path / name
            if media_path.is_symlink():
                raise AssetIndexError(f"Symlink file found in explicit asset root: {media_path}")
            if media_path.suffix.casefold() not in MEDIA_EXTENSIONS:
                continue
            _assert_no_symlink_chain(path, media_path)
            records.append(
                _make_record(
                    path=media_path,
                    project_root=project_root,
                    source_kind="explicit_folder",
                    source_ref=_display_path(path, project_root),
                    item={},
                    default_status="unknown",
                )
            )
    return records


def discover_media_use_manifests(project_root: Path) -> list[Path]:
    manifests: list[Path] = []
    for current_root, directory_names, file_names in os.walk(project_root, followlinks=False):
        root_path = Path(current_root)
        safe_directories = []
        for name in sorted(directory_names):
            child = root_path / name
            if name in IGNORED_DIRECTORY_NAMES:
                continue
            if child.is_symlink():
                # Discovery ignores untrusted branches. Explicit roots fail closed.
                continue
            safe_directories.append(name)
        directory_names[:] = safe_directories
        if root_path.name == ".media" and "manifest.jsonl" in file_names:
            manifest = root_path / "manifest.jsonl"
            _assert_no_symlink_chain(project_root, manifest)
            manifests.append(manifest)
    return sorted(set(manifests), key=lambda value: value.as_posix())


def _load_usage_events(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    if path.suffix.casefold() == ".jsonl":
        events = _jsonl_load(path)
    else:
        document = _json_load(path)
        if not isinstance(document, dict) or not isinstance(document.get("events"), list):
            raise AssetIndexError("Usage history JSON must contain an events array")
        events = document["events"]
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise AssetIndexError(f"Usage event {index} must be an object")
        event_id = event.get("event_id")
        if not isinstance(event_id, str) or not event_id.strip():
            raise AssetIndexError(f"Usage event {index} needs event_id")
        if event_id in seen:
            raise AssetIndexError(f"Duplicate usage event_id: {event_id}")
        seen.add(event_id)
        locators = [
            key
            for key in ("asset_id", "sha256", "path")
            if isinstance(event.get(key), str) and event[key].strip()
        ]
        if len(locators) != 1:
            raise AssetIndexError(
                f"Usage event {event_id} must provide exactly one of asset_id, sha256 or path"
            )
        if "sha256" in locators and not re.fullmatch(r"[a-f0-9]{64}", event["sha256"]):
            raise AssetIndexError(f"Usage event {event_id} has invalid sha256")
        video_id = event.get("video_id")
        if not isinstance(video_id, str) or not re.fullmatch(r"VIDEO-[0-9]{2,4}", video_id):
            raise AssetIndexError(f"Usage event {event_id} has invalid video_id")
        sequence = event.get("video_sequence")
        if (
            not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1
        ):
            raise AssetIndexError(f"Usage event {event_id} has invalid video_sequence")
        used_at = event.get("used_at")
        if not isinstance(used_at, str) or not DATE_TIME_RE.fullmatch(used_at):
            raise AssetIndexError(f"Usage event {event_id} has invalid used_at")
        canonical_used_at = _canonical_datetime(
            used_at, f"Usage event {event_id} used_at"
        )
        if not isinstance(event.get("role"), str) or not event["role"].strip():
            raise AssetIndexError(f"Usage event {event_id} has invalid role")
        normalized_event = dict(event)
        normalized_event["used_at"] = canonical_used_at
        normalized.append(normalized_event)
    return normalized


def _select_primary(records: list[dict[str, Any]]) -> dict[str, Any]:
    return sorted(
        records,
        key=lambda record: (
            -record["source_priority"],
            -STATUS_PRIORITY[record["status"]],
            record["source_asset_id"] is None,
            record["source_asset_id"] or "",
            record["path"],
        ),
    )[0]


def _strictest_reuse(records: list[dict[str, Any]]) -> str:
    return max(
        (record["reuse_policy"] for record in records),
        key=lambda value: REUSE_STRICTNESS[value],
    )


def _worst_status(records: list[dict[str, Any]]) -> str:
    unsafe = [record["status"] for record in records if record["status"] in {"rejected", "deprecated"}]
    if unsafe:
        return max(unsafe, key=lambda status: STATUS_PRIORITY[status])
    return max((record["status"] for record in records), key=lambda status: STATUS_PRIORITY[status])


def _usage_matches(event: dict[str, Any], asset: dict[str, Any]) -> bool:
    if "asset_id" in event:
        return event["asset_id"] == asset["asset_id"] or event["asset_id"] in asset["source_asset_ids"]
    if "sha256" in event:
        return event["sha256"] == asset["sha256"]
    if "path" in event:
        return event["path"] in asset["locations"]
    return False


def _merge_group(records: list[dict[str, Any]]) -> dict[str, Any]:
    primary = _select_primary(records)
    # media-use IDs such as ``sfx_001`` are project-local. Namespace them by
    # manifest so that indexing several projects cannot create a false global
    # identity collision. Governed catalog/project IDs remain stable as-is.
    source_ids = sorted(
        {
            (
                f"{record['source_ref']}::{record['source_asset_id']}"
                if record["source_kind"] == "media_use_manifest"
                else record["source_asset_id"]
            )
            for record in records
            if record["source_asset_id"]
        }
    )
    stable_id_records = [
        record
        for record in records
        if record["source_asset_id"] and record["source_kind"] != "media_use_manifest"
    ]
    stable_primary = _select_primary(stable_id_records) if stable_id_records else None
    asset_id = (
        stable_primary["source_asset_id"]
        if stable_primary is not None
        else f"AUTO-{primary['type'].upper()}-{primary['sha256'][:12].upper()}"
    )
    declared_cooldowns = [record["cooldown_videos"] for record in records if record["cooldown_videos"] is not None]
    cooldown = max(declared_cooldowns) if declared_cooldowns else DEFAULT_COOLDOWN_BY_TYPE[primary["type"]]
    last_dates = {record["last_used_at"] for record in records if record["last_used_at"]}
    last_sequences = [record["last_used_sequence"] for record in records if record["last_used_sequence"] is not None]
    used_in = sorted({value for record in records for value in record["used_in"]})
    declared_usage_count = max(record["usage_count"] for record in records)

    return {
        "asset_id": asset_id,
        "source_asset_ids": source_ids,
        "name": primary["name"],
        "type": primary["type"],
        "format": primary["format"],
        "sha256": primary["sha256"],
        "bytes": primary["bytes"],
        "status": _worst_status(records),
        "description": primary["description"],
        "semantic_tags": sorted(
            {value for record in records for value in record["semantic_tags"]}, key=str.casefold
        ),
        "intent_phrases": sorted(
            {value for record in records for value in record["intent_phrases"]}, key=str.casefold
        ),
        "avoid_for": sorted(
            {value for record in records for value in record["avoid_for"]}, key=str.casefold
        ),
        "locations": sorted({record["path"] for record in records}),
        "metadata": {
            "technical": primary["technical"],
            "approval": primary["raw_approval"],
        },
        "provenance_records": [
            {
                "source_kind": record["source_kind"],
                "source_ref": record["source_ref"],
                "source_asset_id": record["source_asset_id"],
                "path": record["path"],
                "details": record["provenance"],
            }
            for record in sorted(
                records,
                key=lambda value: (-value["source_priority"], value["source_ref"], value["path"]),
            )
        ],
        "reuse": {
            "policy": _strictest_reuse(records),
            "cooldown_videos": cooldown,
            "cooldown_enforcement": "advisory_non_blocking",
        },
        "usage": {
            "usage_count": max(declared_usage_count, len(used_in)),
            "used_in": used_in,
            "last_used_at": _latest_datetime(last_dates),
            "last_used_sequence": max(last_sequences) if last_sequences else None,
            "events": [],
        },
    }


def _attach_usage_events(assets: list[dict[str, Any]], events: list[dict[str, Any]]) -> None:
    for event in events:
        matches = [asset for asset in assets if _usage_matches(event, asset)]
        if len(matches) != 1:
            raise AssetIndexError(
                f"Usage event {event['event_id']} matched {len(matches)} assets; expected exactly one"
            )
        asset = matches[0]
        compact = {
            "event_id": event["event_id"],
            "video_id": event.get("video_id"),
            "video_sequence": event.get("video_sequence"),
            "used_at": event.get("used_at"),
            "role": event.get("role", "unspecified"),
            "family": event.get("family"),
        }
        asset["usage"]["events"].append(compact)

    for asset in assets:
        usage = asset["usage"]
        usage["events"].sort(key=lambda event: (event.get("video_sequence") or 0, event["event_id"]))
        if usage["events"]:
            usage["usage_count"] = max(usage["usage_count"], len(usage["events"]))
            video_ids = {event.get("video_id") for event in usage["events"] if event.get("video_id")}
            usage["used_in"] = sorted(set(usage["used_in"]) | video_ids)
            sequences = [event["video_sequence"] for event in usage["events"] if event.get("video_sequence")]
            if sequences:
                usage["last_used_sequence"] = max(
                    (
                        [usage["last_used_sequence"]]
                        if usage["last_used_sequence"] is not None
                        else []
                    )
                    + sequences
                )
            dates = [event["used_at"] for event in usage["events"] if event.get("used_at")]
            if dates:
                usage["last_used_at"] = _latest_datetime(
                    ([usage["last_used_at"]] if usage["last_used_at"] is not None else [])
                    + dates
                )


def _validate_unique_ids(assets: list[dict[str, Any]]) -> None:
    owner: dict[str, str] = {}
    for asset in assets:
        for asset_id in [asset["asset_id"], *asset["source_asset_ids"]]:
            previous = owner.get(asset_id)
            if previous is not None and previous != asset["sha256"]:
                raise AssetIndexError(
                    f"Asset id {asset_id} points to multiple hashes: {previous}, {asset['sha256']}"
                )
            owner[asset_id] = asset["sha256"]


def build_index(
    *,
    project_root: Path | str,
    catalogs: Iterable[Path | str] = (),
    manifests: Iterable[Path | str] = (),
    roots: Iterable[Path | str] = (),
    usage_history: Path | str | None = None,
    discover_media_use: bool = True,
    generated_at: str | None = None,
) -> dict[str, Any]:
    root = _safe_input(Path(project_root), directory=True)
    catalog_paths = [_safe_catalog_input(root, Path(path)) for path in catalogs]
    manifest_paths = [
        _safe_project_input(root, Path(path), directory=False) for path in manifests
    ]
    explicit_roots = [
        _safe_project_input(root, Path(path), directory=True) for path in roots
    ]
    if discover_media_use:
        manifest_paths.extend(discover_media_use_manifests(root))
    manifest_paths = sorted(set(manifest_paths), key=lambda value: value.as_posix())

    usage_path = (
        _safe_project_input(root, Path(usage_history), directory=False)
        if usage_history
        else None
    )
    records: list[dict[str, Any]] = []
    for path in sorted(set(catalog_paths), key=lambda value: value.as_posix()):
        records.extend(_catalog_records(path, root))
    for path in manifest_paths:
        if path.suffix.casefold() == ".jsonl":
            records.extend(_media_use_records(path, root))
        else:
            records.extend(_project_manifest_records(path, root))
    for path in sorted(set(explicit_roots), key=lambda value: value.as_posix()):
        records.extend(_folder_records(path, root))

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record["sha256"]].append(record)
    assets = [_merge_group(grouped[digest]) for digest in sorted(grouped)]
    _validate_unique_ids(assets)
    _attach_usage_events(assets, _load_usage_events(usage_path))
    assets.sort(key=lambda asset: (asset["type"], asset["asset_id"], asset["sha256"]))

    duplicate_groups = []
    for asset in assets:
        if len(asset["locations"]) > 1:
            duplicate_groups.append(
                {
                    "sha256": asset["sha256"],
                    "canonical_asset_id": asset["asset_id"],
                    "locations": asset["locations"],
                    "proof": "exact_sha256",
                }
            )

    timestamp = generated_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    if not isinstance(timestamp, str) or not DATE_TIME_RE.fullmatch(timestamp):
        raise AssetIndexError(f"generated_at must be an RFC 3339 date-time: {timestamp!r}")
    try:
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except (TypeError, ValueError) as error:
        raise AssetIndexError(f"generated_at must be an RFC 3339 date-time: {timestamp!r}") from error

    status_counts = Counter(asset["status"] for asset in assets)
    type_counts = Counter(asset["type"] for asset in assets)
    index = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": timestamp,
        "scope": {
            "project_root": root.as_posix(),
            "catalogs": [_display_path(path, root) for path in sorted(set(catalog_paths))],
            "manifests": [_display_path(path, root) for path in manifest_paths],
            "explicit_roots": [_display_path(path, root) for path in sorted(set(explicit_roots))],
            "usage_history": _display_path(usage_path, root) if usage_path else None,
        },
        "capabilities": {
            "exact_content_deduplication": True,
            "semantic_metadata_ranking": True,
            "perceptual_visual_similarity": False,
            "similarity_notice": (
                "Semantic scores use declared text metadata only. No perceptual visual similarity "
                "was measured; only identical SHA-256 values prove exact-content duplication."
            ),
        },
        "fatigue_policy": {
            "mode": "advisory_non_blocking",
            "unit": "videos_since_last_use",
            "unknown_recency_behavior": "warn_without_excluding",
            "default_cooldowns": dict(sorted(DEFAULT_COOLDOWN_BY_TYPE.items())),
        },
        "summary": {
            "asset_count": len(assets),
            "source_record_count": len(records),
            "exact_duplicate_group_count": len(duplicate_groups),
            "status_counts": dict(sorted(status_counts.items())),
            "type_counts": dict(sorted(type_counts.items())),
        },
        "assets": assets,
        "exact_duplicate_groups": duplicate_groups,
    }
    validate_index_document(index)
    return index


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return _parse_datetime(value, "usage.last_used_at").date()


def _recency_score(
    asset: dict[str, Any], current_video_sequence: int | None, as_of: date | None
) -> tuple[float, dict[str, Any], list[str]]:
    usage = asset["usage"]
    cooldown = asset["reuse"]["cooldown_videos"]
    last_sequence = usage.get("last_used_sequence")
    last_date = _parse_date(usage.get("last_used_at"))
    warnings: list[str] = []
    fatigue = {
        "status": "clear",
        "cooldown_videos": cooldown,
        "last_used_sequence": last_sequence,
        "videos_since_last_use": None,
        "blocking": False,
    }
    if usage.get("usage_count", 0) == 0:
        fatigue["status"] = "unused"
        return 6.0, fatigue, warnings

    if current_video_sequence is not None and last_sequence is not None:
        distance = current_video_sequence - last_sequence
        fatigue["videos_since_last_use"] = distance
        if distance <= 0:
            fatigue["status"] = "sequence_conflict"
            warnings.append("usage_sequence_is_not_before_current_video")
            return -12.0, fatigue, warnings
        if distance <= cooldown:
            fatigue["status"] = "within_cooldown"
            warnings.append("advisory_cooldown_active")
            return -10.0, fatigue, warnings
        fatigue["status"] = "clear"
        return min(6.0, 2.0 + float(distance - cooldown)), fatigue, warnings

    if as_of is not None and last_date is not None:
        age_days = (as_of - last_date).days
        if age_days < 0:
            fatigue["status"] = "date_conflict"
            warnings.append("last_used_at_is_after_query_date")
            return -4.0, fatigue, warnings
        fatigue["status"] = "cooldown_not_evaluable"
        warnings.append("cooldown_in_videos_needs_sequence_context")
        return min(4.0, age_days / 7.0), fatigue, warnings

    fatigue["status"] = "cooldown_not_evaluable"
    warnings.append("cooldown_recency_unknown")
    return 0.0, fatigue, warnings


def _avoidance_assessment(
    phrases: Iterable[str], query_tokens: set[str], normalized_intent: str
) -> tuple[list[str], list[str]]:
    """Return hard constraints and partial-token warnings from declared metadata.

    A complete declared avoid phrase (or all of its meaningful tokens) present in
    the query is treated as incompatible. A weaker overlap is penalized and
    surfaced for human review rather than silently ignored.
    """

    incompatible: list[str] = []
    partial_terms: set[str] = set()
    for phrase in phrases:
        normalized_phrase = _normalize_text(phrase).strip()
        phrase_tokens = _tokens(phrase)
        if not normalized_phrase or not phrase_tokens:
            continue
        if normalized_phrase in normalized_intent or phrase_tokens <= query_tokens:
            incompatible.append(phrase)
        else:
            partial_terms.update(query_tokens & phrase_tokens)
    return sorted(set(incompatible), key=str.casefold), sorted(partial_terms)


def query_index(
    index: dict[str, Any],
    *,
    intent: str,
    asset_type: str | None = None,
    current_video_sequence: int | None = None,
    as_of: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    validate_index_document(index)
    if not isinstance(intent, str) or not intent.strip():
        raise AssetIndexError("intent cannot be empty")
    if asset_type is not None and asset_type not in KNOWN_TYPES - {"unknown"}:
        raise AssetIndexError(f"Unknown asset type: {asset_type}")
    if current_video_sequence is not None and (
        not isinstance(current_video_sequence, int)
        or isinstance(current_video_sequence, bool)
        or current_video_sequence < 1
    ):
        raise AssetIndexError("current_video_sequence must be a positive integer")
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100:
        raise AssetIndexError("limit must be between 1 and 100")
    try:
        query_date = date.fromisoformat(as_of) if as_of else None
    except (TypeError, ValueError) as error:
        raise AssetIndexError("as_of must be an ISO calendar date") from error
    query_tokens = _tokens(intent)
    normalized_intent = _normalize_text(" ".join(intent.split()))
    results: list[dict[str, Any]] = []
    exclusions = Counter()
    exclusion_details: list[dict[str, Any]] = []

    for asset in index.get("assets", []):
        status = asset.get("status")
        if status in {"rejected", "deprecated"}:
            exclusions[status] += 1
            continue
        if asset.get("reuse", {}).get("policy") == "do_not_reuse":
            exclusions["do_not_reuse"] += 1
            continue
        if asset_type is not None and asset.get("type") != asset_type:
            exclusions["type_mismatch"] += 1
            continue

        avoid_constraints, avoid_overlap = _avoidance_assessment(
            asset.get("avoid_for", []), query_tokens, normalized_intent
        )
        if avoid_constraints:
            exclusions["avoid_for_incompatible"] += 1
            exclusion_details.append({
                "asset_id": asset["asset_id"],
                "reason": "declared_avoid_for_matches_query",
                "matched_constraints": avoid_constraints,
                "blocking": True,
            })
            continue

        tag_tokens = _tokens(" ".join(asset.get("semantic_tags", [])))
        intent_tokens = _tokens(" ".join(asset.get("intent_phrases", [])))
        descriptive_tokens = _tokens(
            f"{asset.get('name', '')} {asset.get('description', '')}"
        )
        matched_tags = sorted(query_tokens & tag_tokens)
        matched_intents = sorted(query_tokens & intent_tokens)
        matched_description = sorted(query_tokens & descriptive_tokens)
        semantic_score = (
            len(matched_tags) * 8.0
            + len(matched_intents) * 6.0
            + len(matched_description) * 3.0
        )
        phrase_match = any(
            normalized_intent in _normalize_text(phrase)
            or _normalize_text(phrase) in normalized_intent
            for phrase in asset.get("intent_phrases", [])
            if len(_normalize_text(phrase)) >= 4
        )
        if phrase_match:
            semantic_score += 20.0
        if semantic_score <= 0:
            exclusions["no_semantic_match"] += 1
            continue

        type_score = 12.0 if asset_type is not None else 0.0
        status_score = {"approved": 8.0, "provisional": 3.0, "unknown": 0.0}.get(status, 0.0)
        recency_score, fatigue, warnings = _recency_score(
            asset, current_video_sequence, query_date
        )
        avoidance_score = -15.0 * min(2, len(avoid_overlap))
        if avoid_overlap:
            warnings.append("avoid_for_partial_match_review_required")
        total = semantic_score + type_score + status_score + recency_score + avoidance_score
        results.append(
            {
                "asset_id": asset["asset_id"],
                "type": asset["type"],
                "status": status,
                "sha256": asset["sha256"],
                "locations": asset["locations"],
                "score": round(total, 4),
                "score_breakdown": {
                    "semantic_metadata": round(semantic_score, 4),
                    "requested_type": type_score,
                    "approval_status": status_score,
                    "recency": round(recency_score, 4),
                    "avoid_for": avoidance_score,
                },
                "matched_terms": {
                    "semantic_tags": matched_tags,
                    "intent_phrases": matched_intents,
                    "name_or_description": matched_description,
                    "phrase_match": phrase_match,
                },
                "avoidance": {
                    "action": "penalized" if avoid_overlap else "clear",
                    "matched_constraints": [],
                    "overlap_terms": avoid_overlap,
                    "blocking": False,
                },
                "fatigue": fatigue,
                "warnings": warnings,
                "selection_policy": "candidate_only_requires_human_semantic_judgment",
            }
        )

    results.sort(key=lambda result: (-result["score"], result["asset_id"], result["sha256"]))
    return {
        "schema_version": SCHEMA_VERSION,
        "query": {
            "intent": " ".join(intent.split()),
            "type": asset_type,
            "current_video_sequence": current_video_sequence,
            "as_of": as_of,
            "limit": limit,
        },
        "method": {
            "ranking": "deterministic_declared_metadata",
            "perceptual_visual_similarity_measured": False,
            "auto_reuse": False,
            "avoid_for_policy": (
                "Exclude complete declared incompatibilities; penalize partial token overlap "
                "and require human review."
            ),
            "notice": (
                "Candidates are ranked from declared metadata and recency. They are not proof of "
                "visual similarity and are never selected automatically."
            ),
        },
        "excluded": dict(sorted(exclusions.items())),
        "exclusion_details": sorted(
            exclusion_details, key=lambda item: (item["asset_id"], item["reason"])
        ),
        "result_count": min(limit, len(results)),
        "results": results[:limit],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    build = commands.add_parser("build", help="Build an asset index from governed inputs")
    build.add_argument("--project-root", required=True, type=Path)
    build.add_argument("--catalog", action="append", type=Path, default=[])
    build.add_argument("--manifest", action="append", type=Path, default=[])
    build.add_argument("--root", action="append", type=Path, default=[])
    build.add_argument("--usage-history", type=Path)
    build.add_argument("--no-discover-media-use", action="store_true")
    build.add_argument("--generated-at")
    build.add_argument("--out", required=True, type=Path)

    query = commands.add_parser("query", help="Rank reusable candidates from an existing index")
    query.add_argument("--project-root", required=True, type=Path)
    query.add_argument("--index", required=True, type=Path)
    query.add_argument("--intent", required=True)
    query.add_argument("--type", choices=sorted(KNOWN_TYPES - {"unknown"}))
    query.add_argument("--current-video-sequence", type=int)
    query.add_argument("--as-of")
    query.add_argument("--limit", type=int, default=10)
    query.add_argument("--out", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        project_root = _safe_input(args.project_root, directory=True)
        if args.command == "build":
            catalogs = args.catalog or [DEFAULT_CATALOG]
            index = build_index(
                project_root=project_root,
                catalogs=catalogs,
                manifests=args.manifest,
                roots=args.root,
                usage_history=args.usage_history,
                discover_media_use=not args.no_discover_media_use,
                generated_at=args.generated_at,
            )
            output = _safe_output(project_root, args.out)
            _atomic_write_json(output, index)
            print(
                f"OK: {index['summary']['asset_count']} assets, "
                f"{index['summary']['exact_duplicate_group_count']} exact duplicate groups -> {output}"
            )
            return 0

        index_path = _safe_member(project_root, args.index)
        index = _json_load(index_path)
        report = query_index(
            index,
            intent=args.intent,
            asset_type=args.type,
            current_video_sequence=args.current_video_sequence,
            as_of=args.as_of,
            limit=args.limit,
        )
        if args.out:
            output = _safe_output(project_root, args.out)
            _atomic_write_json(output, report)
            print(f"OK: {report['result_count']} candidates -> {output}")
        else:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except (AssetIndexError, OSError, ValueError, TypeError, KeyError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
