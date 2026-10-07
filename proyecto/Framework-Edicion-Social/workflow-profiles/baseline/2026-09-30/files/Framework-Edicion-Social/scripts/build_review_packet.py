#!/usr/bin/env python3
"""Build a hash-bound JSON/HTML review console for one rendered video.

The command is read-only by default and prints the packet to stdout. It writes
``review-packet.json`` and ``review.html`` only when ``--out`` and ``--write``
are supplied together. All inputs and outputs must remain inside an explicit
project root; symlink destinations and mismatched render manifests fail closed.
The packet coordinates editorial review only; it never replaces the separately
verified SHA-256-bound approval receipt required for delivery.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import os
import re
import stat
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote


SCRIPT_DIR = Path(__file__).resolve().parent
FRAMEWORK_ROOT = SCRIPT_DIR.parent
DEFAULT_SCHEMA = FRAMEWORK_ROOT / "schemas/review-packet.schema.json"
DEFAULT_REVIEW_DECISION_SCHEMA = FRAMEWORK_ROOT / "schemas/review-decision.schema.json"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from change_impact import (  # noqa: E402
    DependencyMapError,
    calculate_impact,
    validate_dependency_map,
)
from schema_validation import (  # noqa: E402
    UnsupportedSchemaKeyword,
    validate_document,
)


SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")
VIDEO_ID_PATTERN = re.compile(r"^VIDEO-[0-9]{2,3}$")
CHANGE_ID_PATTERN = re.compile(r"^CHANGE-[0-9]{3,4}$")
RESOLUTION_PATTERN = re.compile(r"^[0-9]+x[0-9]+$")
LAYER_STATES = {"current", "reused", "new", "modified"}
DECISIONS = {"pending", "approved", "changes_requested", "rejected"}


class ReviewPacketError(ValueError):
    """An input, binding, path, or review instruction is unsafe or invalid."""


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _absolute(path):
    return Path(os.path.abspath(os.fspath(Path(path).expanduser())))


def _inside(path, root):
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def validate_project_root(path):
    root = _absolute(path)
    if root.is_symlink():
        raise ReviewPacketError(f"project root cannot be a symlink: {root}")
    if not root.is_dir():
        raise ReviewPacketError(f"project root is not a directory: {root}")
    return root.resolve(strict=True)


def safe_input_path(root, value, label):
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = _absolute(candidate)
    if candidate.is_symlink():
        raise ReviewPacketError(f"{label} cannot be a symlink: {candidate}")
    try:
        resolved = candidate.resolve(strict=True)
    except FileNotFoundError as error:
        raise ReviewPacketError(f"{label} does not exist: {candidate}") from error
    if not _inside(resolved, root):
        raise ReviewPacketError(f"{label} escapes project root: {candidate}")
    try:
        mode = resolved.stat().st_mode
    except OSError as error:
        raise ReviewPacketError(f"cannot inspect {label}: {resolved}: {error}") from error
    if not stat.S_ISREG(mode):
        raise ReviewPacketError(f"{label} is not a regular file: {resolved}")
    return resolved


def safe_output_directory(root, value):
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = _absolute(candidate)
    if not _inside(candidate, root):
        raise ReviewPacketError(f"output directory escapes project root: {candidate}")

    probe = candidate
    missing = []
    while not probe.exists():
        missing.append(probe.name)
        if probe == root or probe.parent == probe:
            break
        probe = probe.parent
    if probe.is_symlink():
        raise ReviewPacketError(f"output directory traverses a symlink: {probe}")
    try:
        resolved_probe = probe.resolve(strict=True)
    except FileNotFoundError as error:
        raise ReviewPacketError(f"cannot resolve output parent: {probe}") from error
    if not _inside(resolved_probe, root):
        raise ReviewPacketError(f"output directory escapes project root through a symlink: {candidate}")
    if candidate.exists():
        if candidate.is_symlink() or not candidate.is_dir():
            raise ReviewPacketError(f"output path must be a non-symlink directory: {candidate}")
    return candidate


def project_relative(path, root):
    return path.resolve(strict=True).relative_to(root).as_posix()


def load_json(path, label, expected=None):
    try:
        with path.open(encoding="utf-8") as handle:
            value = json.load(handle)
    except json.JSONDecodeError as error:
        raise ReviewPacketError(f"{label} is not valid JSON: {error}") from error
    if expected is not None and not isinstance(value, expected):
        expected_name = getattr(expected, "__name__", str(expected))
        raise ReviewPacketError(f"{label} must be a JSON {expected_name}")
    return value


def load_json_fingerprinted(path, label, expected=None):
    """Read, parse, and fingerprint the exact stable bytes used as an input."""
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise ReviewPacketError(f"{label} is not a regular file: {path}")
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            payload = handle.read()
        after = os.fstat(descriptor)
        stable_identity = (before.st_dev, before.st_ino) == (after.st_dev, after.st_ino)
        stable_metadata = (
            before.st_size == after.st_size
            and before.st_mtime_ns == after.st_mtime_ns
            and before.st_ctime_ns == after.st_ctime_ns
            and len(payload) == after.st_size
        )
        if not stable_identity or not stable_metadata:
            raise ReviewPacketError(f"{label} changed while it was being read: {path}")
        try:
            value = json.loads(payload.decode("utf-8"))
        except UnicodeDecodeError as error:
            raise ReviewPacketError(f"{label} is not valid UTF-8: {error}") from error
        except json.JSONDecodeError as error:
            raise ReviewPacketError(f"{label} is not valid JSON: {error}") from error
        if expected is not None and not isinstance(value, expected):
            expected_name = getattr(expected, "__name__", str(expected))
            raise ReviewPacketError(f"{label} must be a JSON {expected_name}")
        return value, {
            "sha256": hashlib.sha256(payload).hexdigest(),
            "size_bytes": len(payload),
        }
    finally:
        os.close(descriptor)


def file_fingerprint(path):
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise ReviewPacketError(f"file is not regular: {path}")
        digest = hashlib.sha256()
        total = 0
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
                total += len(chunk)
        after = os.fstat(descriptor)
        stable_identity = (before.st_dev, before.st_ino) == (after.st_dev, after.st_ino)
        stable_metadata = (
            before.st_size == after.st_size
            and before.st_mtime_ns == after.st_mtime_ns
            and before.st_ctime_ns == after.st_ctime_ns
            and total == after.st_size
        )
        if not stable_identity or not stable_metadata:
            raise ReviewPacketError(f"file changed while it was being fingerprinted: {path}")
        return {"sha256": digest.hexdigest(), "size_bytes": total}
    finally:
        os.close(descriptor)


def _finite_number(value, label, *, minimum=None, exclusive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ReviewPacketError(f"{label} must be a finite number")
    numeric = float(value)
    if minimum is not None:
        invalid = numeric <= minimum if exclusive else numeric < minimum
        if invalid:
            relation = "greater than" if exclusive else "at least"
            raise ReviewPacketError(f"{label} must be {relation} {minimum}")
    return numeric


def validate_render_manifest(manifest, manifest_path, render_path, render_fingerprint, project_id, video_id, root):
    if not isinstance(manifest, dict):
        raise ReviewPacketError("render manifest must be a JSON object")
    if manifest.get("video_id") not in (None, video_id):
        raise ReviewPacketError("render manifest video_id does not match requested video")
    if manifest.get("project_id") not in (None, project_id):
        raise ReviewPacketError("render manifest project_id does not match requested project")
    output = manifest.get("output")
    if not isinstance(output, dict):
        raise ReviewPacketError("render manifest must contain an output object")

    declared_path = output.get("path")
    if not isinstance(declared_path, str) or not declared_path.strip():
        raise ReviewPacketError("render manifest output.path must be non-empty")
    manifest_render = safe_input_path(root, manifest_path.parent / declared_path, "manifest output.path")
    if manifest_render != render_path:
        raise ReviewPacketError("render manifest output.path does not resolve to --render")

    declared_hash = output.get("sha256")
    if not isinstance(declared_hash, str) or SHA256_PATTERN.fullmatch(declared_hash) is None:
        raise ReviewPacketError("render manifest output.sha256 must be a lowercase SHA-256")
    if declared_hash != render_fingerprint["sha256"]:
        raise ReviewPacketError("render manifest SHA-256 does not match the render")
    declared_size = output.get("size_bytes")
    if isinstance(declared_size, bool) or not isinstance(declared_size, int) or declared_size < 1:
        raise ReviewPacketError("render manifest output.size_bytes must be a positive integer")
    if declared_size != render_fingerprint["size_bytes"]:
        raise ReviewPacketError("render manifest size does not match the render")

    duration = _finite_number(output.get("duration_s"), "output.duration_s", minimum=0, exclusive=True)
    fps = _finite_number(output.get("fps"), "output.fps", minimum=0, exclusive=True)
    resolution = output.get("resolution")
    if not isinstance(resolution, str) or RESOLUTION_PATTERN.fullmatch(resolution) is None:
        raise ReviewPacketError("render manifest output.resolution must use WIDTHxHEIGHT")
    metadata = {
        "duration_s": duration,
        "resolution": resolution,
        "fps": fps,
        "video_codec": _optional_string(output.get("video_codec"), "output.video_codec"),
        "audio_codec": _optional_string(output.get("audio_codec"), "output.audio_codec"),
        "color": _optional_string(output.get("color"), "output.color"),
    }
    return metadata


def _optional_string(value, label):
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ReviewPacketError(f"{label} must be null or a non-empty string")
    return value.strip()


def extract_beats(manifest, blueprint, duration):
    source = "blueprint" if blueprint is not None else "manifest"
    if blueprint is not None:
        raw_beats = blueprint.get("beats") if isinstance(blueprint, dict) else None
    else:
        review = manifest.get("review") if isinstance(manifest.get("review"), dict) else {}
        raw_beats = review.get("beats", manifest.get("beats"))
    if not isinstance(raw_beats, list) or not raw_beats:
        raise ReviewPacketError("at least one traceable beat is required in --blueprint or the manifest")

    beats = []
    seen = set()
    for index, raw in enumerate(raw_beats):
        if not isinstance(raw, dict):
            raise ReviewPacketError(f"beat[{index}] must be an object")
        beat_id = raw.get("id")
        if not isinstance(beat_id, str) or not beat_id.strip() or beat_id in seen:
            raise ReviewPacketError(f"beat[{index}].id must be a unique non-empty string")
        seen.add(beat_id)
        start = _finite_number(raw.get("start_s"), f"beat[{index}].start_s", minimum=0)
        end = _finite_number(raw.get("end_s"), f"beat[{index}].end_s", minimum=0, exclusive=True)
        if end <= start:
            raise ReviewPacketError(f"beat[{index}] must end after it starts")
        if end > duration + 0.05:
            raise ReviewPacketError(f"beat[{index}] extends beyond the render duration")
        role = raw.get("narrative_role", raw.get("role"))
        if not isinstance(role, str) or not role.strip():
            raise ReviewPacketError(f"beat[{index}] requires narrative_role or role")
        label = raw.get("narrative_job", raw.get("label", raw.get("on_screen", beat_id)))
        if not isinstance(label, str) or not label.strip():
            raise ReviewPacketError(f"beat[{index}] requires a non-empty label")
        beats.append(
            {
                "id": beat_id.strip(),
                "role": role.strip(),
                "label": label.strip(),
                "start_s": round(start, 3),
                "end_s": round(end, 3),
                "reference_frame_s": round((start + end) / 2, 3),
                "review_tags": [],
                "source": source,
            }
        )

    beats.sort(key=lambda item: (item["start_s"], item["end_s"], item["id"]))
    for previous, current in zip(beats, beats[1:]):
        if current["start_s"] < previous["end_s"] - 0.001:
            raise ReviewPacketError(f"beats overlap: {previous['id']} and {current['id']}")

    middle = min(beats, key=lambda item: abs(item["reference_frame_s"] - duration / 2))
    for beat in beats:
        role = beat["role"].casefold()
        tags = []
        if role == "hook":
            tags.append("hook")
        if beat is middle:
            tags.append("middle")
        if role in {"bridge", "contrast", "transition", "critical_transition"}:
            tags.append("critical_transition")
        if role == "cta":
            tags.append("cta")
        beat["review_tags"] = tags
    return beats


def validate_blueprint_identity(blueprint, project_id, video_id):
    if not isinstance(blueprint, dict):
        raise ReviewPacketError("blueprint must be a JSON object")
    if blueprint.get("project_id") not in (None, project_id):
        raise ReviewPacketError("blueprint project_id does not match requested project")
    if blueprint.get("video_id") not in (None, video_id):
        raise ReviewPacketError("blueprint video_id does not match requested video")


def parse_changes(document, duration, dependency_map):
    if document is None:
        raw_changes = []
    elif isinstance(document, list):
        raw_changes = document
    elif isinstance(document, dict) and set(document) == {"changes"} and isinstance(document["changes"], list):
        raw_changes = document["changes"]
    else:
        raise ReviewPacketError("changes JSON must be an array or an object containing only a changes array")

    layer_ids = {layer["id"] for layer in dependency_map["layers"]}
    result = []
    seen = set()
    for index, raw in enumerate(raw_changes):
        if not isinstance(raw, dict):
            raise ReviewPacketError(f"changes[{index}] must be an object")
        allowed = {"id", "start_s", "end_s", "layer", "element", "element_id", "instruction"}
        unknown = set(raw) - allowed
        if unknown:
            raise ReviewPacketError(f"changes[{index}] has unknown fields: {', '.join(sorted(unknown))}")
        required = {"id", "start_s", "end_s", "layer", "instruction"}
        missing = required - set(raw)
        if missing:
            raise ReviewPacketError(f"changes[{index}] is missing: {', '.join(sorted(missing))}")
        if ("element" in raw) == ("element_id" in raw):
            raise ReviewPacketError(f"changes[{index}] requires exactly one of element or element_id")
        change_id = raw["id"]
        if not isinstance(change_id, str) or CHANGE_ID_PATTERN.fullmatch(change_id) is None:
            raise ReviewPacketError(f"changes[{index}].id must match CHANGE-NNN")
        if change_id in seen:
            raise ReviewPacketError(f"duplicate change id: {change_id}")
        seen.add(change_id)
        start = _finite_number(raw["start_s"], f"changes[{index}].start_s", minimum=0)
        end = _finite_number(raw["end_s"], f"changes[{index}].end_s", minimum=0, exclusive=True)
        if end <= start:
            raise ReviewPacketError(f"changes[{index}] must end after it starts")
        if end > duration + 0.001:
            raise ReviewPacketError(f"changes[{index}] extends beyond the render duration")
        layer = raw["layer"]
        if not isinstance(layer, str) or layer not in layer_ids:
            raise ReviewPacketError(f"changes[{index}].layer is not a dependency-map layer: {layer!r}")
        element = raw.get("element_id", raw.get("element"))
        instruction = raw["instruction"]
        if not isinstance(element, str) or not element.strip():
            raise ReviewPacketError(f"changes[{index}] element must be non-empty")
        if not isinstance(instruction, str) or not instruction.strip():
            raise ReviewPacketError(f"changes[{index}].instruction must be non-empty")
        result.append(
            {
                "id": change_id,
                "start_s": round(start, 3),
                "end_s": round(end, 3),
                "layer": layer,
                "element_id": element.strip(),
                "instruction": instruction.strip(),
                "reference_frame_s": round((start + end) / 2, 3),
                "status": "open",
            }
        )
    return sorted(result, key=lambda item: (item["start_s"], item["end_s"], item["id"]))


def empty_impact(dependency_map, generated_at):
    return {
        "changed": [],
        "invalidated_layers": [],
        "invalidated_artifacts": [],
        "heavy_layers": [],
        "unaffected_layers": [layer["id"] for layer in dependency_map["layers"]],
        "computed_at": generated_at,
    }


def build_layers(dependency_map, manifest, changes, impact):
    review = manifest.get("review") if isinstance(manifest.get("review"), dict) else {}
    declared = review.get("layer_states", {})
    if not isinstance(declared, dict):
        raise ReviewPacketError("manifest review.layer_states must be an object")
    known = {layer["id"] for layer in dependency_map["layers"]}
    unknown = set(declared) - known
    if unknown:
        raise ReviewPacketError(f"manifest declares unknown layer states: {', '.join(sorted(unknown))}")
    for layer_id, state in declared.items():
        if state not in LAYER_STATES:
            raise ReviewPacketError(f"manifest layer state for {layer_id} is invalid: {state!r}")

    direct = {item["layer"] for item in changes}
    invalidated = {item["id"] for item in impact["invalidated_layers"]} - direct
    result = []
    for layer in dependency_map["layers"]:
        layer_id = layer["id"]
        state = declared.get(layer_id, "current")
        if layer_id in invalidated:
            state = "invalidated"
        if layer_id in direct:
            state = "modified"
        result.append(
            {
                "id": layer_id,
                "description": layer["description"],
                "heavy": layer["heavy"],
                "state": state,
            }
        )
    return result


def build_preview_plan(changes, impact, duration, handle_s):
    handle = _finite_number(handle_s, "preview handle", minimum=0)
    if handle > 3:
        raise ReviewPacketError("preview handle cannot exceed 3 seconds")
    if not changes:
        return {
            "strategy": "no_changes",
            "partial_review_previews_allowed": False,
            "final_delivery_requires_full_encode": False,
            "handle_s": round(handle, 3),
            "ranges": [],
            "rationale": "No hay cambios estructurados; no se prescribe un nuevo preview ni un render.",
        }

    ranges = []
    for change in changes:
        start = max(0.0, change["start_s"] - handle)
        end = min(duration, change["end_s"] + handle)
        if ranges and start <= ranges[-1]["end_s"] + 0.001:
            current = ranges[-1]
            current["end_s"] = round(max(current["end_s"], end), 3)
            current["change_ids"].append(change["id"])
            if change["layer"] not in current["layers"]:
                current["layers"].append(change["layer"])
        else:
            ranges.append(
                {
                    "id": "",
                    "start_s": round(start, 3),
                    "end_s": round(end, 3),
                    "reference_frame_s": change["reference_frame_s"],
                    "change_ids": [change["id"]],
                    "layers": [change["layer"]],
                    "recommended_output": "partial_review_preview",
                }
            )
    for index, item in enumerate(ranges, 1):
        item["id"] = f"PREVIEW-{index:02d}"

    invalidated_layers = {item["id"] for item in impact["invalidated_layers"]}
    full_encode = "render" in invalidated_layers
    if full_encode:
        strategy = "partial_then_full"
        rationale = (
            "Validar primero los rangos parciales; al aprobar los cambios, la entrega final requiere "
            "una codificación completa porque la capa render quedó invalidada."
        )
    else:
        strategy = "partial_only_for_review"
        rationale = (
            "Los rangos parciales bastan para revisar este impacto; el mapa no invalida la capa render."
        )
    return {
        "strategy": strategy,
        "partial_review_previews_allowed": True,
        "final_delivery_requires_full_encode": full_encode,
        "handle_s": round(handle, 3),
        "ranges": ranges,
        "rationale": rationale,
    }


def extract_findings(manifest):
    findings = {"technical": [], "semantic": [], "variety": []}
    review = manifest.get("review") if isinstance(manifest.get("review"), dict) else {}
    declared = review.get("findings", {})
    if not isinstance(declared, dict):
        raise ReviewPacketError("manifest review.findings must be an object")
    unknown = set(declared) - set(findings)
    if unknown:
        raise ReviewPacketError(f"manifest review.findings has unknown categories: {', '.join(sorted(unknown))}")
    for category, values in declared.items():
        if not isinstance(values, list) or not all(isinstance(value, str) and value.strip() for value in values):
            raise ReviewPacketError(f"manifest review.findings.{category} must be an array of non-empty strings")
        findings[category] = [value.strip() for value in values]

    qa = manifest.get("qa")
    if isinstance(qa, dict):
        for key, value in sorted(qa.items()):
            is_error_count = key.endswith("_errors") and isinstance(value, int) and not isinstance(value, bool) and value > 0
            is_failed_state = isinstance(value, str) and value.casefold() in {"fail", "failed", "error"}
            if is_error_count or is_failed_state:
                note = f"QA {key}: {value}"
                if note not in findings["technical"]:
                    findings["technical"].append(note)
    return findings


def validate_review_decision(decision, schema_path=DEFAULT_REVIEW_DECISION_SCHEMA):
    schema = load_json(Path(schema_path), "review decision schema", dict)
    try:
        errors = validate_document(decision, schema)
    except UnsupportedSchemaKeyword as error:
        raise ReviewPacketError(f"unsupported review decision schema: {error}") from error
    if errors:
        raise ReviewPacketError(
            "review decision does not match review-decision.schema.json: " + "; ".join(errors)
        )


def input_reference(path, fingerprint, root):
    if path is None:
        return None
    return {
        "path": project_relative(path, root),
        "sha256": fingerprint["sha256"],
    }


def verify_packet_bindings(packet, root):
    """Fail when any file that materially shaped a packet has drifted."""
    references = [
        ("render", packet["render"], True),
        ("source manifest", packet["source_manifest"], False),
        ("dependency map", packet["inputs"]["dependency_map"], False),
        ("creative blueprint", packet["inputs"]["blueprint"], False),
        ("changes JSON", packet["inputs"]["changes"], False),
        ("review decision", packet["inputs"]["review_decision"], False),
    ]
    previous = packet.get("comparison", {}).get("previous")
    if previous is not None:
        references.append(("previous render", previous, True))

    for label, reference, check_size in references:
        if reference is None:
            continue
        path = safe_input_path(root, reference["path"], label)
        fingerprint = file_fingerprint(path)
        if fingerprint["sha256"] != reference["sha256"]:
            raise ReviewPacketError(f"{label} drifted after the packet was built")
        if check_size and fingerprint["size_bytes"] != reference["size_bytes"]:
            raise ReviewPacketError(f"{label} size drifted after the packet was built")
    return True


def build_decisions(decision, decision_path, manifest_hash, render_path, project_id, changes, root):
    pending = {"status": "pending", "evidence_reference": None}
    result = {
        "video": dict(pending),
        "assets": dict(pending),
        "template_family": dict(pending),
        "series_default": dict(pending),
    }
    if decision is None:
        return result
    if not isinstance(decision, dict):
        raise ReviewPacketError("review decision must be a JSON object")
    validate_review_decision(decision)
    if decision.get("project_id") != project_id:
        raise ReviewPacketError("review decision project_id does not match requested project")
    artifact = decision.get("review_artifact")
    if not isinstance(artifact, str) or Path(artifact).name != render_path.name:
        raise ReviewPacketError("review decision does not name the current render artifact")
    declared_manifest_hash = decision.get("source_manifest_sha256")
    if declared_manifest_hash != manifest_hash:
        raise ReviewPacketError("review decision is not bound to the current source manifest")
    status = decision.get("overall_decision")
    if status not in DECISIONS:
        raise ReviewPacketError("review decision has an unsupported overall_decision")
    review_id = decision.get("review_id")
    if not isinstance(review_id, str) or not review_id.strip():
        raise ReviewPacketError("review decision requires a non-empty review_id")
    if status == "approved" and changes:
        raise ReviewPacketError("an approved review decision cannot be combined with new requested changes")
    if status == "changes_requested" and not changes:
        raise ReviewPacketError("a changes_requested review decision requires structured requested changes")
    evidence = f"{project_relative(decision_path, root)}#{review_id.strip()}"
    result["video"] = {"status": status, "evidence_reference": evidence}
    return result


def build_comparison(previous_path, root, current_fingerprint):
    if previous_path is None:
        return {"enabled": False, "relation": "not_requested", "previous": None}
    previous_fingerprint = file_fingerprint(previous_path)
    return {
        "enabled": True,
        "relation": "identical" if previous_fingerprint["sha256"] == current_fingerprint["sha256"] else "different",
        "previous": {
            "path": project_relative(previous_path, root),
            "sha256": previous_fingerprint["sha256"],
            "size_bytes": previous_fingerprint["size_bytes"],
        },
    }


def schema_errors(packet, schema_path=DEFAULT_SCHEMA):
    schema = load_json(Path(schema_path), "review packet schema", dict)
    try:
        return validate_document(packet, schema)
    except UnsupportedSchemaKeyword as error:
        raise ReviewPacketError(f"unsupported review packet schema: {error}") from error


def build_packet(
    *,
    root,
    render_path,
    manifest_path,
    dependency_map_path,
    project_id,
    video_id,
    blueprint_path=None,
    changes_path=None,
    previous_render_path=None,
    review_decision_path=None,
    preview_handle_s=0.75,
    generated_at=None,
):
    if not isinstance(project_id, str) or not project_id.strip():
        raise ReviewPacketError("project_id must be non-empty")
    if not isinstance(video_id, str) or VIDEO_ID_PATTERN.fullmatch(video_id) is None:
        raise ReviewPacketError("video_id must match VIDEO-NN")
    generated_at = generated_at or utc_now()

    render_fingerprint = file_fingerprint(render_path)
    manifest, manifest_fingerprint = load_json_fingerprinted(
        manifest_path, "render manifest", dict
    )
    metadata = validate_render_manifest(
        manifest,
        manifest_path,
        render_path,
        render_fingerprint,
        project_id,
        video_id,
        root,
    )

    dependency_map, dependency_map_fingerprint = load_json_fingerprinted(
        dependency_map_path, "dependency map", dict
    )
    try:
        validate_dependency_map(dependency_map)
    except DependencyMapError as error:
        raise ReviewPacketError(str(error)) from error
    if dependency_map["project_id"] not in ("", project_id):
        raise ReviewPacketError("dependency map project_id does not match requested project")

    blueprint = None
    blueprint_fingerprint = None
    if blueprint_path is not None:
        blueprint, blueprint_fingerprint = load_json_fingerprinted(
            blueprint_path, "creative blueprint", dict
        )
        validate_blueprint_identity(blueprint, project_id, video_id)
    beats = extract_beats(manifest, blueprint, metadata["duration_s"])

    changes_fingerprint = None
    if changes_path is not None:
        changes_document, changes_fingerprint = load_json_fingerprinted(
            changes_path, "changes JSON"
        )
    else:
        changes_document = None
    changes = parse_changes(changes_document, metadata["duration_s"], dependency_map)
    if changes:
        try:
            impact = calculate_impact(dependency_map, [item["layer"] for item in changes])
        except DependencyMapError as error:
            raise ReviewPacketError(str(error)) from error
        impact.pop("schema_version", None)
        impact.pop("project_id", None)
    else:
        impact = empty_impact(dependency_map, generated_at)

    decision = None
    review_decision_fingerprint = None
    if review_decision_path is not None:
        decision, review_decision_fingerprint = load_json_fingerprinted(
            review_decision_path, "review decision", dict
        )
    decisions = build_decisions(
        decision,
        review_decision_path,
        manifest_fingerprint["sha256"],
        render_path,
        project_id,
        changes,
        root,
    )

    packet = {
        "schema_version": "1.0.0",
        "packet_id": f"RP-{video_id}-{render_fingerprint['sha256'][:12].upper()}",
        "project_id": project_id.strip(),
        "video_id": video_id,
        "generated_at": generated_at,
        "render": {
            "path": project_relative(render_path, root),
            "sha256": render_fingerprint["sha256"],
            "size_bytes": render_fingerprint["size_bytes"],
            "metadata": metadata,
        },
        "source_manifest": {
            "path": project_relative(manifest_path, root),
            "sha256": manifest_fingerprint["sha256"],
        },
        "inputs": {
            "dependency_map": input_reference(
                dependency_map_path, dependency_map_fingerprint, root
            ),
            "blueprint": input_reference(blueprint_path, blueprint_fingerprint, root),
            "changes": input_reference(changes_path, changes_fingerprint, root),
            "review_decision": input_reference(
                review_decision_path, review_decision_fingerprint, root
            ),
        },
        "comparison": build_comparison(previous_render_path, root, render_fingerprint),
        "beats": beats,
        "layers": build_layers(dependency_map, manifest, changes, impact),
        "requested_changes": changes,
        "impact": impact,
        "preview_plan": build_preview_plan(
            changes,
            impact,
            metadata["duration_s"],
            preview_handle_s,
        ),
        "findings": extract_findings(manifest),
        "decisions": decisions,
        "governance": {
            "purpose": "editorial_review_coordination",
            "review_decision_replaces_approval_receipt": False,
            "approval_authority": "approval_receipt_only",
            "notice": (
                "Este paquete coordina la revisión editorial. Una decisión de revisión aprobada "
                "no sustituye el recibo de aprobación independiente ligado por SHA-256 que se "
                "exige para entregar."
            ),
        },
    }
    errors = schema_errors(packet)
    if errors:
        raise ReviewPacketError("generated packet failed schema validation: " + "; ".join(errors))
    verify_packet_bindings(packet, root)
    return packet


def atomic_write_text(path, content):
    destination = _absolute(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.is_symlink():
        raise ReviewPacketError(f"refusing to replace symlink destination: {destination}")
    descriptor = None
    temporary = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
        )
        temporary = Path(temporary_name)
        with os.fdopen(descriptor, "w", encoding="utf-8", closefd=True) as handle:
            descriptor = None
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        if destination.is_symlink():
            raise ReviewPacketError(f"refusing to replace symlink destination: {destination}")
        os.replace(temporary, destination)
        temporary = None
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _format_seconds(value):
    minutes, seconds = divmod(float(value), 60)
    return f"{int(minutes):02d}:{seconds:06.3f}"


def _badge_list(values):
    if not values:
        return '<span class="muted">ninguno</span>'
    return " ".join(f'<span class="badge">{html.escape(str(value))}</span>' for value in values)


def render_html(packet, output_directory, root):
    render_path = root / packet["render"]["path"]
    relative_media = os.path.relpath(render_path, output_directory)
    media_url = html.escape(quote(Path(relative_media).as_posix(), safe="/._-"), quote=True)
    render_hash = html.escape(packet["render"]["sha256"])
    video_id = html.escape(packet["video_id"])
    governance_notice = html.escape(packet["governance"]["notice"])

    beat_rows = []
    for beat in packet["beats"]:
        beat_rows.append(
            "<tr>"
            f"<td><button class=\"seek\" data-time=\"{beat['reference_frame_s']}\">{html.escape(beat['id'])}</button></td>"
            f"<td>{html.escape(beat['role'])}</td>"
            f"<td>{html.escape(beat['label'])}</td>"
            f"<td>{_format_seconds(beat['start_s'])}–{_format_seconds(beat['end_s'])}</td>"
            f"<td>{_badge_list(beat['review_tags'])}</td>"
            "</tr>"
        )

    layer_rows = []
    for layer in packet["layers"]:
        layer_rows.append(
            "<tr>"
            f"<td><code>{html.escape(layer['id'])}</code></td>"
            f"<td>{html.escape(layer['description'])}</td>"
            f"<td><span class=\"state {html.escape(layer['state'])}\">{html.escape(layer['state'])}</span></td>"
            f"<td>{'sí' if layer['heavy'] else 'no'}</td>"
            "</tr>"
        )

    change_rows = []
    for change in packet["requested_changes"]:
        change_rows.append(
            "<tr>"
            f"<td>{html.escape(change['id'])}</td>"
            f"<td><button class=\"seek\" data-time=\"{change['reference_frame_s']}\">{_format_seconds(change['start_s'])}–{_format_seconds(change['end_s'])}</button></td>"
            f"<td><code>{html.escape(change['layer'])}</code></td>"
            f"<td>{html.escape(change['element_id'])}</td>"
            f"<td>{html.escape(change['instruction'])}</td>"
            "</tr>"
        )
    if not change_rows:
        change_rows.append('<tr><td colspan="5" class="muted">Sin cambios solicitados en este paquete.</td></tr>')

    preview_rows = []
    for preview in packet["preview_plan"]["ranges"]:
        preview_rows.append(
            "<tr>"
            f"<td>{html.escape(preview['id'])}</td>"
            f"<td><button class=\"seek\" data-time=\"{preview['reference_frame_s']}\">{_format_seconds(preview['start_s'])}–{_format_seconds(preview['end_s'])}</button></td>"
            f"<td>{_badge_list(preview['change_ids'])}</td>"
            f"<td>{_badge_list(preview['layers'])}</td>"
            "</tr>"
        )
    if not preview_rows:
        preview_rows.append('<tr><td colspan="4" class="muted">No se necesita preview parcial.</td></tr>')

    finding_sections = []
    for category in ("technical", "semantic", "variety"):
        values = packet["findings"][category]
        items = "".join(f"<li>{html.escape(value)}</li>" for value in values) or '<li class="muted">sin hallazgos declarados</li>'
        finding_sections.append(f"<div><h3>{html.escape(category)}</h3><ul>{items}</ul></div>")

    decision_rows = []
    for scope, decision in packet["decisions"].items():
        evidence = decision["evidence_reference"] or "—"
        decision_rows.append(
            "<tr>"
            f"<td>{html.escape(scope)}</td>"
            f"<td><span class=\"state {html.escape(decision['status'])}\">{html.escape(decision['status'])}</span></td>"
            f"<td>{html.escape(evidence)}</td>"
            "</tr>"
        )

    previous = packet["comparison"]["previous"]
    comparison_text = "No solicitado"
    if previous is not None:
        comparison_text = f"{packet['comparison']['relation']}: {previous['path']} · {previous['sha256']}"

    layers_json = json.dumps([layer["id"] for layer in packet["layers"]], ensure_ascii=False).replace("<", "\\u003c")
    duration_json = json.dumps(packet["render"]["metadata"]["duration_s"])
    html_document = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self' file: data:; media-src 'self' file: data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'">
  <title>Revisión {video_id}</title>
  <style>
    :root {{ color-scheme: dark; --bg:#0b0d12; --panel:#151923; --ink:#f4f6fb; --muted:#9aa4b5; --line:#2a3140; --accent:#8d7cff; --warn:#ffcf66; }}
    * {{ box-sizing:border-box }} body {{ margin:0; background:var(--bg); color:var(--ink); font:15px/1.5 system-ui,sans-serif }}
    main {{ width:min(1180px,94vw); margin:32px auto 80px }} h1,h2,h3 {{ line-height:1.15 }} h2 {{ margin-top:0 }}
    .grid {{ display:grid; grid-template-columns:minmax(280px,420px) 1fr; gap:20px; align-items:start }}
    .panel {{ background:var(--panel); border:1px solid var(--line); border-radius:18px; padding:18px; margin-bottom:18px }}
    .sticky {{ position:sticky; top:18px }} video {{ width:100%; border-radius:12px; background:#000; max-height:72vh }}
    code {{ overflow-wrap:anywhere }} .hash {{ color:#bac2ff; font-size:12px }} .muted {{ color:var(--muted) }}
    table {{ width:100%; border-collapse:collapse }} th,td {{ border-bottom:1px solid var(--line); padding:10px 8px; text-align:left; vertical-align:top }}
    button,.button {{ background:var(--accent); color:#fff; border:0; border-radius:8px; padding:7px 10px; cursor:pointer }}
    .badge,.state {{ display:inline-block; padding:2px 7px; border:1px solid var(--line); border-radius:999px; font-size:12px; margin:1px }}
    .modified,.invalidated,.changes_requested {{ color:var(--warn) }}
    form {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px }} label {{ display:grid; gap:4px }}
    label.wide {{ grid-column:1/-1 }} input,select,textarea {{ width:100%; color:var(--ink); background:#0f131b; border:1px solid var(--line); border-radius:8px; padding:9px }}
    .findings {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px }}
    @media (max-width:850px) {{ .grid {{ grid-template-columns:1fr }} .sticky {{ position:static }} .findings {{ grid-template-columns:1fr }} }}
  </style>
</head>
<body><main>
  <h1>Revisión {video_id}</h1>
  <p class="muted">Paquete <code>{html.escape(packet['packet_id'])}</code> · generado {html.escape(packet['generated_at'])}</p>
  <div class="grid">
    <aside class="panel sticky">
      <video id="review-video" controls preload="metadata" src="{media_url}"></video>
      <p><strong>{html.escape(packet['render']['path'])}</strong></p>
      <p class="hash"><strong>SHA-256</strong><br>{render_hash}</p>
      <p>{packet['render']['metadata']['resolution']} · {packet['render']['metadata']['fps']} fps · {_format_seconds(packet['render']['metadata']['duration_s'])}</p>
      <p><strong>Comparación:</strong><br>{html.escape(comparison_text)}</p>
    </aside>
    <section>
      <div class="panel"><h2>Beats trazables</h2><table><thead><tr><th>Beat</th><th>Rol</th><th>Trabajo</th><th>Tiempo</th><th>Revisión</th></tr></thead><tbody>{''.join(beat_rows)}</tbody></table></div>
      <div class="panel"><h2>Capas e impacto</h2><table><thead><tr><th>Capa</th><th>Descripción</th><th>Estado</th><th>Pesada</th></tr></thead><tbody>{''.join(layer_rows)}</tbody></table></div>
      <div class="panel"><h2>Cambios estructurados</h2><table><thead><tr><th>ID</th><th>Tiempo</th><th>Capa</th><th>Elemento</th><th>Instrucción</th></tr></thead><tbody>{''.join(change_rows)}</tbody></table></div>
      <div class="panel"><h2>Previews parciales</h2><p>{html.escape(packet['preview_plan']['rationale'])}</p><table><thead><tr><th>Preview</th><th>Rango</th><th>Cambios</th><th>Capas</th></tr></thead><tbody>{''.join(preview_rows)}</tbody></table></div>
      <div class="panel"><h2>Hallazgos</h2><div class="findings">{''.join(finding_sections)}</div></div>
      <div class="panel"><h2>Decisiones separadas</h2><p class="muted">{governance_notice}</p><table><thead><tr><th>Alcance</th><th>Estado</th><th>Evidencia</th></tr></thead><tbody>{''.join(decision_rows)}</tbody></table></div>
      <div class="panel">
        <h2>Crear solicitud de cambio</h2>
        <p class="muted">Este formulario no altera el paquete. Exporta un <code>changes.json</code> para reconstruirlo con trazabilidad.</p>
        <form id="change-form">
          <label>Inicio (s)<input name="start_s" type="number" min="0" step="0.001" required></label>
          <label>Fin (s)<input name="end_s" type="number" min="0" step="0.001" required></label>
          <label>Capa<select name="layer" required></select></label>
          <label>Elemento<input name="element_id" required></label>
          <label class="wide">Instrucción<textarea name="instruction" rows="3" required></textarea></label>
          <label class="wide"><button type="submit">Descargar changes.json</button></label>
        </form>
      </div>
    </section>
  </div>
</main>
<script>
  const video = document.getElementById('review-video');
  document.querySelectorAll('.seek').forEach(button => button.addEventListener('click', () => {{ video.currentTime = Number(button.dataset.time); video.play(); }}));
  const layers = {layers_json}; const duration = {duration_json}; const select = document.querySelector('[name="layer"]');
  layers.forEach(layer => {{ const option=document.createElement('option'); option.value=layer; option.textContent=layer; select.appendChild(option); }});
  document.getElementById('change-form').addEventListener('submit', event => {{
    event.preventDefault(); const data=new FormData(event.currentTarget); const start=Number(data.get('start_s')); const end=Number(data.get('end_s'));
    if (!Number.isFinite(start) || !Number.isFinite(end) || start < 0 || end <= start || end > duration) {{ alert('Rango inválido para este video.'); return; }}
    const payload={{changes:[{{id:'CHANGE-001',start_s:start,end_s:end,layer:String(data.get('layer')),element_id:String(data.get('element_id')).trim(),instruction:String(data.get('instruction')).trim()}}]}};
    const link=document.createElement('a'); link.href=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)+'\\n'],{{type:'application/json'}})); link.download='changes.json'; link.click(); URL.revokeObjectURL(link.href);
  }});
</script>
</body></html>
"""
    return html_document


def write_packet(output_directory, packet, root):
    verify_packet_bindings(packet, root)
    output_directory.mkdir(parents=True, exist_ok=True)
    packet_path = output_directory / "review-packet.json"
    html_path = output_directory / "review.html"
    for destination in (packet_path, html_path):
        if destination.is_symlink():
            raise ReviewPacketError(f"refusing to replace symlink destination: {destination}")
    packet_text = json.dumps(packet, ensure_ascii=False, indent=2) + "\n"
    html_text = render_html(packet, output_directory, root)
    atomic_write_text(packet_path, packet_text)
    atomic_write_text(html_path, html_text)
    return packet_path, html_path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--video-id", required=True)
    parser.add_argument("--render", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dependency-map", type=Path, required=True)
    parser.add_argument("--blueprint", type=Path)
    parser.add_argument("--changes", type=Path)
    parser.add_argument("--previous-render", type=Path)
    parser.add_argument("--review-decision", type=Path)
    parser.add_argument("--preview-handle", type=float, default=0.75)
    parser.add_argument("--out", type=Path, help="directory for review-packet.json and review.html")
    parser.add_argument("--write", action="store_true", help="explicitly allow writing both review artifacts")
    args = parser.parse_args(argv)

    try:
        if bool(args.out) != bool(args.write):
            raise ReviewPacketError("--out and --write must be supplied together")
        root = validate_project_root(args.project_root)
        render_path = safe_input_path(root, args.render, "render")
        manifest_path = safe_input_path(root, args.manifest, "render manifest")
        dependency_map_path = safe_input_path(root, args.dependency_map, "dependency map")
        blueprint_path = safe_input_path(root, args.blueprint, "creative blueprint") if args.blueprint else None
        changes_path = safe_input_path(root, args.changes, "changes JSON") if args.changes else None
        previous_render_path = safe_input_path(root, args.previous_render, "previous render") if args.previous_render else None
        review_decision_path = safe_input_path(root, args.review_decision, "review decision") if args.review_decision else None
        output_directory = safe_output_directory(root, args.out) if args.out else None

        packet = build_packet(
            root=root,
            render_path=render_path,
            manifest_path=manifest_path,
            dependency_map_path=dependency_map_path,
            project_id=args.project_id,
            video_id=args.video_id,
            blueprint_path=blueprint_path,
            changes_path=changes_path,
            previous_render_path=previous_render_path,
            review_decision_path=review_decision_path,
            preview_handle_s=args.preview_handle,
        )
        if output_directory is not None:
            write_packet(output_directory, packet, root)
        print(json.dumps(packet, ensure_ascii=False, indent=2))
        return 0
    except (ReviewPacketError, DependencyMapError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
