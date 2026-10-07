#!/usr/bin/env python3
"""Evidence-based memory for a social-video series.

The module deliberately separates four questions:

* what was observed in an editable/render (fingerprint),
* what the series has explicitly decided (contract),
* what has been approved and compared (variety ledger), and
* whether a video is good (human creative review + technical QA elsewhere).

Similarity is only a repetition signal.  It never becomes a quality score and
never blocks a delivery.  A seed video is a reference, not a rule.  A candidate
locked/bounded dimension may become a default after two distinct approved
videos with artifact-bound passing technical QA support it, or an explicit
user instruction may promote it immediately.
Creative dimensions remain rotating/free, and three approvals trigger a
recalibration review instead of silently rewriting the contract.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import re
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

import approval_receipt as approval_receipts
from schema_validation import assert_supported_schema, validate_document


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = ROOT.parent.resolve()
SCHEMA_DIR = ROOT / "schemas"
FINGERPRINT_SCHEMA = SCHEMA_DIR / "series-fingerprint.schema.json"
CONTRACT_SCHEMA = SCHEMA_DIR / "series-contract.schema.json"
LEDGER_SCHEMA = SCHEMA_DIR / "series-variety-ledger.schema.json"

HEX_RE = re.compile(r"(?<![0-9A-Fa-f])#([0-9A-Fa-f]{6})(?![0-9A-Fa-f])")
FONT_RE = re.compile(r"font-family\s*:\s*([^;}]+)", re.IGNORECASE)
COMPOSITION_RE = re.compile(r'data-composition-id=["\']([^"\']+)["\']', re.IGNORECASE)
TRACK_KIND_RE = re.compile(r'data-track-kind=["\']([^"\']+)["\']', re.IGNORECASE)
AUDIO_TAG_RE = re.compile(r"<audio\b[^>]*>", re.IGNORECASE)
ID_RE = re.compile(r'\bid=["\']([^"\']+)["\']', re.IGNORECASE)
SRC_RE = re.compile(r'\bsrc=["\']([^"\']+)["\']', re.IGNORECASE)
SCALE_RE = re.compile(r"\bscale\s*:\s*([0-9]+(?:\.[0-9]+)?)")
EASE_RE = re.compile(r'''\bease\s*:\s*["']([^"']+)["']''')
VERSIONED_RENDER_RE = re.compile(r"manifest-render-v([0-9]+)\.json$")
SERIES_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
QA_ERROR_COUNTER_RE = re.compile(r"(?:^|_)errors?$")


class SeriesMemoryError(ValueError):
    """A user-facing contract, evidence, or command error."""


def _confined_path(
    path: Path | str,
    *,
    must_exist: bool = True,
    expect: str | None = None,
) -> Path:
    """Resolve a path inside the workspace without traversal or symlinks."""
    raw = Path(path).expanduser()
    if ".." in raw.parts:
        raise SeriesMemoryError(f"Path traversal is not allowed: {path}")
    candidate = raw if raw.is_absolute() else Path.cwd() / raw
    lexical = Path(os.path.abspath(candidate))
    try:
        relative = lexical.relative_to(WORKSPACE_ROOT)
    except ValueError as error:
        raise SeriesMemoryError(f"Path is outside the workspace: {path}") from error

    current = WORKSPACE_ROOT
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise SeriesMemoryError(f"Symlink paths are not allowed: {current}")
        if not current.exists():
            break
    resolved = lexical.resolve(strict=must_exist)
    try:
        resolved.relative_to(WORKSPACE_ROOT)
    except ValueError as error:
        raise SeriesMemoryError(f"Resolved path escapes the workspace: {path}") from error
    if expect == "file" and (not resolved.is_file() if must_exist else resolved.exists() and not resolved.is_file()):
        raise SeriesMemoryError(f"Expected a file path: {path}")
    if expect == "dir" and (not resolved.is_dir() if must_exist else resolved.exists() and not resolved.is_dir()):
        raise SeriesMemoryError(f"Expected a directory path: {path}")
    return resolved


def _stored_path(path: Path | str) -> str:
    resolved = _confined_path(path, must_exist=True, expect="file")
    return resolved.relative_to(WORKSPACE_ROOT).as_posix()


def _path_from_stored(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise SeriesMemoryError(f"Stored path must be workspace-relative and traversal-free: {path}")
    return _confined_path(WORKSPACE_ROOT / candidate, must_exist=True, expect="file")


def load_json(path: Path | str) -> dict[str, Any]:
    source = _confined_path(path, must_exist=True, expect="file")
    with source.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise SeriesMemoryError(f"Expected a JSON object: {path}")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def file_sha256(path: Path | str) -> str:
    digest = hashlib.sha256()
    source = _confined_path(path, must_exist=True, expect="file")
    with source.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(
    path: Path | str,
    value: Any,
    *,
    protected_paths: tuple[Path | str, ...] = (),
) -> None:
    target = _confined_path(path, must_exist=False, expect="file")
    for protected in protected_paths:
        protected_path = _confined_path(protected, must_exist=True)
        if target == protected_path:
            raise SeriesMemoryError(f"Output may not overwrite an input: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target = _confined_path(target, must_exist=False, expect="file")
    payload = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=target.parent,
        prefix=f".{target.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        handle.write(payload)
        temp_name = handle.name
    os.replace(temp_name, target)


def _validate_schema(value: dict[str, Any], schema_path: Path, label: str) -> None:
    schema = load_json(schema_path)
    assert_supported_schema(schema)
    errors = validate_document(value, schema)
    if errors:
        detail = "\n  - ".join(errors)
        raise SeriesMemoryError(f"{label} does not match {schema_path.name}:\n  - {detail}")


def _portable_path(path: Path | str) -> str:
    return _stored_path(path)


def _source_file(role: str, path: Path) -> dict[str, str]:
    return {"role": role, "path": _portable_path(path), "sha256": file_sha256(path)}


def _clean_video_id(raw: str) -> str:
    value = re.sub(r"[^A-Z0-9_-]+", "-", raw.upper()).strip("-")
    if not value:
        raise SeriesMemoryError("Could not derive a valid video id")
    return value


def _series_id(raw: Any) -> str:
    value = str(raw or "")
    if not SERIES_ID_RE.fullmatch(value):
        raise SeriesMemoryError(f"Invalid or missing series id: {raw!r}")
    return value


def _render_rank(path: Path) -> tuple[int, str]:
    match = VERSIONED_RENDER_RE.search(path.name)
    return (int(match.group(1)) if match else 0, path.name)


def discover_inputs(
    editable: Path,
    project_manifest: Path | None = None,
    render_manifest: Path | None = None,
) -> tuple[Path | None, Path | None, list[Path], Path | None]:
    editable = _confined_path(editable, must_exist=True, expect="dir")
    project_root = editable.parent

    if project_manifest is None:
        candidate = editable.parent / "manifest.json"
        project_manifest = candidate if candidate.is_file() else None
    else:
        project_manifest = _confined_path(project_manifest, must_exist=True, expect="file")
        try:
            project_manifest.relative_to(project_root)
        except ValueError as error:
            raise SeriesMemoryError("Project manifest must stay inside the editable project root") from error

    if render_manifest is None:
        candidates = sorted(editable.glob("manifest-render*.json"), key=_render_rank)
        render_manifest = candidates[-1] if candidates else None
    else:
        render_manifest = _confined_path(render_manifest, must_exist=True, expect="file")
        try:
            render_manifest.relative_to(editable)
        except ValueError as error:
            raise SeriesMemoryError("Render manifest must stay inside the editable directory") from error

    html_files = []
    for path in editable.rglob("*.html"):
        if "node_modules" in path.parts or ".git" in path.parts:
            continue
        html_files.append(_confined_path(path, must_exist=True, expect="file"))
    html_files.sort(key=lambda path: path.relative_to(editable).as_posix())
    config = editable / "hyperframes.json"
    config_path = _confined_path(config, must_exist=True, expect="file") if config.is_file() else None
    return project_manifest, render_manifest, html_files, config_path


def _nested(mapping: dict[str, Any], *keys: str) -> Any:
    value: Any = mapping
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def _put(fields: dict[str, Any], key: str, value: Any) -> None:
    if value is None:
        return
    if isinstance(value, (str, int, float, bool)) and not (
        isinstance(value, float) and not math.isfinite(value)
    ):
        fields[key] = value
    elif isinstance(value, list) and all(
        item is None or isinstance(item, (str, int, float, bool)) for item in value
    ):
        fields[key] = value


def _extract_html_traits(html_files: list[Path]) -> tuple[dict[str, list[str]], dict[str, Any]]:
    palette: set[str] = set()
    fonts: set[str] = set()
    composition_ids: set[str] = set()
    track_kinds: set[str] = set()
    audio_roles: set[str] = set()
    sfx_files: set[str] = set()
    camera_scales: set[str] = set()
    easing_tokens: set[str] = set()
    caption_track = False

    for path in html_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        palette.update(f"#{match.upper()}" for match in HEX_RE.findall(text))
        for declaration in FONT_RE.findall(text):
            for family in declaration.split(","):
                cleaned = family.strip().strip("\"'")
                if cleaned:
                    fonts.add(cleaned)
        composition_ids.update(COMPOSITION_RE.findall(text))
        track_kinds.update(value.strip().lower() for value in TRACK_KIND_RE.findall(text))
        for tag in AUDIO_TAG_RE.findall(text):
            id_match = ID_RE.search(tag)
            src_match = SRC_RE.search(tag)
            audio_id = id_match.group(1).lower() if id_match else "unnamed"
            audio_roles.add(audio_id)
            if "sfx" in audio_id or (src_match and "/sfx/" in src_match.group(1).lower()):
                if src_match:
                    sfx_files.add(Path(src_match.group(1)).name)
        camera_scales.update(f"{float(value):.4g}" for value in SCALE_RE.findall(text))
        easing_tokens.update(EASE_RE.findall(text))
        caption_track = caption_track or "captions" in text.lower()

    scene_ids = sorted(value for value in composition_ids if value.lower().startswith("scene"))
    traits = {
        "palette": sorted(palette),
        "font_families": sorted(fonts, key=str.lower),
        "scene_ids": scene_ids,
        "track_kinds": sorted(track_kinds),
        "audio_roles": sorted(audio_roles),
        "sfx_files": sorted(sfx_files),
        "camera_zoom_scales": sorted(camera_scales, key=float),
        "motion_eases": sorted(easing_tokens),
    }
    fields = {
        "structure.html_file_count": len(html_files),
        "structure.scene_count": len(scene_ids),
        "structure.caption_track_present": caption_track,
        "audio.sfx_event_count": len(sfx_files),
    }
    return traits, fields


def _receipt_evidence(
    receipt_path: Path | str,
    *,
    expected_series_id: str,
    expected_video_id: str,
    expected_status: str,
) -> tuple[dict[str, Any], dict[str, Any], Path]:
    resolved_receipt = _confined_path(receipt_path, must_exist=True, expect="file")
    receipt = load_json(resolved_receipt)
    artifact_raw = _nested(receipt, "artifact", "path")
    if not isinstance(artifact_raw, str) or not artifact_raw:
        raise SeriesMemoryError("Approval receipt lacks an artifact path")
    raw_path = Path(artifact_raw).expanduser()
    if ".." in raw_path.parts:
        raise SeriesMemoryError("Approval artifact path may not contain traversal")
    artifact_candidate = raw_path if raw_path.is_absolute() else resolved_receipt.parent / raw_path
    artifact_path = _confined_path(artifact_candidate, must_exist=True, expect="file")
    report = approval_receipts.verify_receipt(
        receipt,
        receipt_path=resolved_receipt,
        artifact_override=artifact_path,
    )
    if receipt.get("video_id") != expected_video_id:
        raise SeriesMemoryError("Approval receipt belongs to a different video")
    if receipt.get("project_id") != expected_series_id:
        raise SeriesMemoryError("Approval receipt belongs to a different series/project")
    decision_status = _nested(receipt, "decision", "status")
    if decision_status != expected_status:
        raise SeriesMemoryError(
            f"Approval receipt decision is {decision_status!r}, expected {expected_status!r}"
        )
    if expected_status == "approved" and not report["usable_as_approval"]:
        raise SeriesMemoryError("Approval receipt is not a verified explicit approval")
    if expected_status == "approved" and _nested(
        receipt, "decision", "scope", "whole_artifact"
    ) is not True:
        raise SeriesMemoryError("Series approval evidence must cover the whole artifact")
    if expected_status == "rejected" and (
        report["document_status"] != "valid"
        or report["artifact_status"] != "match"
        or report["binding_status"] != "match"
    ):
        raise SeriesMemoryError("Rejection receipt is not valid and artifact-bound")
    return receipt, report, artifact_path


def _technical_qa_evidence(
    render: dict[str, Any], render_path: Path | None
) -> dict[str, Any]:
    """Derive technical-QA evidence from a render manifest without trusting labels alone."""
    evidence = {
        "status": "unavailable",
        "evidence_path": None,
        "evidence_sha256": None,
        "artifact_sha256": None,
    }
    if render_path is None:
        return evidence

    resolved = _confined_path(render_path, must_exist=True, expect="file")
    evidence["evidence_path"] = _portable_path(resolved)
    evidence["evidence_sha256"] = file_sha256(resolved)
    artifact_sha = _nested(render, "output", "sha256")
    if isinstance(artifact_sha, str) and SHA256_RE.fullmatch(artifact_sha):
        evidence["artifact_sha256"] = artifact_sha

    qa = render.get("qa")
    if evidence["artifact_sha256"] is None or not isinstance(qa, dict):
        return evidence

    check = qa.get("hyperframes_check")
    counters = {
        key: value
        for key, value in qa.items()
        if isinstance(key, str) and QA_ERROR_COUNTER_RE.search(key.lower())
    }
    if check is None or not counters:
        return evidence
    counters_are_valid = all(
        isinstance(value, int) and not isinstance(value, bool) and value >= 0
        for value in counters.values()
    )
    explicit_failure = any(
        isinstance(value, str)
        and (
            value.strip().lower() in {"fail", "failed", "error"}
            or value.strip().lower().startswith(("fail_", "failed_", "error_"))
        )
        for value in qa.values()
    )
    paired_checks_complete = True
    for key, passed in qa.items():
        if not isinstance(key, str) or not key.endswith("_passed"):
            continue
        total_key = key[: -len("_passed")] + "_total"
        if total_key not in qa:
            continue
        total = qa[total_key]
        if (
            not isinstance(passed, int)
            or isinstance(passed, bool)
            or not isinstance(total, int)
            or isinstance(total, bool)
            or passed < 0
            or total < 0
            or passed != total
        ):
            paired_checks_complete = False
    evidence["status"] = (
        "pass"
        if check == "pass"
        and counters_are_valid
        and all(value == 0 for value in counters.values())
        and not explicit_failure
        and paired_checks_complete
        else "fail"
    )
    return evidence


def _fingerprint_payload(fingerprint: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(fingerprint)
    payload.pop("fingerprint_id", None)
    return payload


def expected_fingerprint_id(fingerprint: dict[str, Any]) -> str:
    video_id = _clean_video_id(str(fingerprint.get("video_id", "")))
    digest = canonical_sha256(_fingerprint_payload(fingerprint))
    return f"FP-{video_id}-{digest[:12].upper()}"


def extract_fingerprint(
    editable: Path | str,
    *,
    project_manifest: Path | str | None = None,
    render_manifest: Path | str | None = None,
    series_id: str | None = None,
    video_id: str | None = None,
    recorded_at: str | None = None,
    approval_status: str = "unreviewed",
    approval_ref: str | None = None,
    approval_receipt: Path | str | None = None,
    family_id: str | None = None,
    archetype_id: str | None = None,
    parent_fingerprint_id: str | None = None,
) -> dict[str, Any]:
    """Extract a deterministic, descriptive fingerprint from existing files."""
    editable_path = _confined_path(editable, must_exist=True, expect="dir")
    manifest_path = Path(project_manifest) if project_manifest is not None else None
    render_path = Path(render_manifest) if render_manifest is not None else None
    manifest_path, render_path, html_files, config_path = discover_inputs(
        editable_path, manifest_path, render_path
    )

    manifest = load_json(manifest_path) if manifest_path else {}
    render = load_json(render_path) if render_path else {}
    clean_series_id = _series_id(series_id or manifest.get("series_id") or manifest.get("project_id"))
    inferred_video_id = video_id or manifest.get("video_id") or render.get("video_id") or editable_path.parent.name
    clean_video_id = _clean_video_id(str(inferred_video_id))

    if approval_status not in {"unreviewed", "approved", "rejected"}:
        raise SeriesMemoryError(f"Unsupported approval status: {approval_status}")
    if approval_status == "unreviewed" and (approval_ref is not None or approval_receipt is not None):
        raise SeriesMemoryError("An unreviewed fingerprint cannot carry approval evidence")
    if approval_status != "unreviewed" and approval_receipt is None:
        raise SeriesMemoryError("Approved/rejected fingerprints require a verified receipt")
    if bool(family_id) != bool(archetype_id):
        raise SeriesMemoryError("family_id and archetype_id must be supplied together")

    source_files: list[dict[str, str]] = []
    if manifest_path:
        source_files.append(_source_file("project_manifest", manifest_path))
    if render_path:
        source_files.append(_source_file("render_manifest", render_path))
    for html_path in html_files:
        source_files.append(_source_file("editable_entry", html_path))
    if config_path:
        source_files.append(_source_file("hyperframes_config", config_path))
    if not source_files:
        raise SeriesMemoryError("No manifest, render manifest, HTML, or HyperFrames config was found")

    html_traits, html_fields = _extract_html_traits(html_files)
    fields: dict[str, Any] = {}
    fields.update(html_fields)
    _put(fields, "technical.aspect_ratio", _nested(manifest, "target", "aspect_ratio"))
    _put(fields, "technical.target_frame", _nested(manifest, "target", "frame"))
    _put(fields, "technical.language", _nested(manifest, "target", "language"))
    _put(fields, "edit.speed", _nested(render, "edit", "speed"))
    _put(fields, "edit.silence_removal", _nested(render, "edit", "silence_removal"))
    _put(fields, "output.duration_s", _nested(render, "output", "duration_s"))
    _put(fields, "output.resolution", _nested(render, "output", "resolution"))
    _put(fields, "output.fps", _nested(render, "output", "fps"))
    _put(fields, "output.video_codec", _nested(render, "output", "video_codec"))
    _put(fields, "output.audio_codec", _nested(render, "output", "audio_codec"))
    _put(fields, "output.color", _nested(render, "output", "color"))
    _put(fields, "audio.integrated_loudness_lufs", _nested(render, "output", "integrated_loudness_lufs"))
    _put(fields, "audio.true_peak_dbtp", _nested(render, "output", "true_peak_dbtp"))
    _put(fields, "audio.loudness_range_lu", _nested(render, "output", "loudness_range_lu"))
    _put(fields, "project.framework", _nested(render, "project", "framework"))
    _put(fields, "project.editable_layers", _nested(render, "project", "editable_layers"))
    template_id = render.get("template") or render.get("template_candidate")
    _put(fields, "creative.template_id", template_id)
    if family_id:
        _put(fields, "creative.family_id", family_id)
        _put(fields, "creative.archetype_id", archetype_id)

    resources = manifest.get("resources") if isinstance(manifest.get("resources"), list) else []
    resource_ids: set[str] = set()
    resource_types: set[str] = set()
    semantic_tags: set[str] = set()
    sfx_asset_ids: set[str] = set()
    visual_asset_ids: set[str] = set()
    for resource in resources:
        if not isinstance(resource, dict):
            continue
        asset_id = resource.get("id")
        asset_type = resource.get("type")
        if isinstance(asset_id, str):
            resource_ids.add(asset_id)
            if asset_type == "sfx" or asset_id.startswith("SFX-"):
                sfx_asset_ids.add(asset_id)
            if asset_type in {"image", "icon", "logo", "video"}:
                visual_asset_ids.add(asset_id)
        if isinstance(asset_type, str):
            resource_types.add(asset_type)
        tags = resource.get("semantic_tags") or resource.get("tags") or []
        if isinstance(tags, list):
            semantic_tags.update(str(tag) for tag in tags if isinstance(tag, str))

    traits = dict(html_traits)
    traits.update(
        {
            "resource_ids": sorted(resource_ids),
            "resource_types": sorted(resource_types),
            "semantic_tags": sorted(semantic_tags),
            "sfx_asset_ids": sorted(sfx_asset_ids),
            "visual_asset_ids": sorted(visual_asset_ids),
            "template_ids": [str(template_id)] if template_id else [],
        }
    )
    traits = {key: sorted(set(values)) for key, values in sorted(traits.items())}
    fields = dict(sorted(fields.items()))

    technical_qa = _technical_qa_evidence(render, render_path)

    receipt_path: Path | None = None
    receipt_sha: str | None = None
    approved_sha: str | None = None
    if approval_receipt is not None:
        receipt, receipt_report, _ = _receipt_evidence(
            approval_receipt,
            expected_series_id=clean_series_id,
            expected_video_id=clean_video_id,
            expected_status=approval_status,
        )
        receipt_path = _confined_path(approval_receipt, must_exist=True, expect="file")
        receipt_sha = file_sha256(receipt_path)
        receipt_id = receipt.get("receipt_id")
        if approval_ref is not None and approval_ref != receipt_id:
            raise SeriesMemoryError("approval_ref does not match the verified receipt id")
        approval_ref = receipt_id
        if approval_status == "approved":
            approved_sha = receipt_report["actual_artifact_sha256"]
            manifest_sha = _nested(render, "output", "sha256")
            if manifest_sha is not None and manifest_sha != approved_sha:
                raise SeriesMemoryError("Render manifest hash does not match the approved artifact")
            if technical_qa["status"] == "pass" and (
                technical_qa["artifact_sha256"] != approved_sha
            ):
                raise SeriesMemoryError(
                    "Technical QA evidence is not bound to the approved artifact"
                )
    family = None
    if family_id:
        family = {
            "family_id": family_id,
            "archetype_id": archetype_id,
            "parent_fingerprint_id": parent_fingerprint_id,
        }

    limitations = {
        "approval_is_never_inferred_from_take_markers",
        "fingerprint_is_descriptive_not_a_quality_score",
        "html_pattern_extraction_requires_semantic_human_review",
    }
    if not manifest_path:
        limitations.add("project_manifest_missing")
    if not render_path:
        limitations.add("render_manifest_missing")
    if not html_files:
        limitations.add("editable_html_missing")
    if approval_status == "approved" and approved_sha is None:
        limitations.add("approved_output_hash_missing")
    if technical_qa["status"] == "unavailable":
        limitations.add("technical_qa_evidence_unavailable")
    elif technical_qa["status"] == "fail":
        limitations.add("technical_qa_failed")

    payload: dict[str, Any] = {
        "schema_version": "1.0.0",
        "series_id": clean_series_id,
        "video_id": clean_video_id,
        "recorded_at": recorded_at or date.today().isoformat(),
        "approval": {
            "status": approval_status,
            "approval_ref": approval_ref,
            "approval_receipt_path": _portable_path(receipt_path) if receipt_path else None,
            "approval_receipt_sha256": receipt_sha,
            "approved_artifact_sha256": approved_sha,
        },
        "technical_qa": technical_qa,
        "family": family,
        "source_files": source_files,
        "fields": fields,
        "traits": traits,
        "limitations": sorted(limitations),
    }
    payload["fingerprint_id"] = expected_fingerprint_id(payload)
    ordered = {
        "schema_version": payload["schema_version"],
        "fingerprint_id": payload["fingerprint_id"],
        "series_id": payload["series_id"],
        "video_id": payload["video_id"],
        "recorded_at": payload["recorded_at"],
        "approval": payload["approval"],
        "technical_qa": payload["technical_qa"],
        "family": payload["family"],
        "source_files": payload["source_files"],
        "fields": payload["fields"],
        "traits": payload["traits"],
        "limitations": payload["limitations"],
    }
    validate_fingerprint(ordered)
    return ordered


def validate_fingerprint(fingerprint: dict[str, Any], *, verify_files: bool = True) -> None:
    _validate_schema(fingerprint, FINGERPRINT_SCHEMA, "Fingerprint")
    expected_id = expected_fingerprint_id(fingerprint)
    if fingerprint["fingerprint_id"] != expected_id:
        raise SeriesMemoryError(
            f"Fingerprint id/content mismatch: expected {expected_id}, got {fingerprint['fingerprint_id']}"
        )
    approval = fingerprint["approval"]
    receipt_fields = (
        approval["approval_ref"],
        approval["approval_receipt_path"],
        approval["approval_receipt_sha256"],
    )
    if approval["status"] == "unreviewed":
        if any(value is not None for value in receipt_fields) or approval["approved_artifact_sha256"] is not None:
            raise SeriesMemoryError("Unreviewed fingerprint carries approval evidence")
    elif not all(receipt_fields):
        raise SeriesMemoryError("Approved/rejected fingerprint lacks a verified decision receipt")
    if approval["status"] == "approved" and approval["approved_artifact_sha256"] is None:
        raise SeriesMemoryError("Approved fingerprint lacks an artifact SHA-256")
    if approval["status"] == "rejected" and approval["approved_artifact_sha256"] is not None:
        raise SeriesMemoryError("Rejected fingerprint cannot claim an approved artifact hash")

    technical_qa = fingerprint["technical_qa"]
    qa_fields = (
        technical_qa["evidence_path"],
        technical_qa["evidence_sha256"],
        technical_qa["artifact_sha256"],
    )
    if technical_qa["status"] == "pass" and not all(qa_fields):
        raise SeriesMemoryError("Passing technical QA lacks path/hash/artifact evidence")
    if technical_qa["evidence_path"] is None and any(
        value is not None for value in qa_fields[1:]
    ):
        raise SeriesMemoryError("Technical QA hashes require an evidence path")
    if (
        approval["status"] == "approved"
        and technical_qa["artifact_sha256"] is not None
        and technical_qa["artifact_sha256"] != approval["approved_artifact_sha256"]
    ):
        raise SeriesMemoryError("Technical QA evidence is not bound to the approved artifact")

    family = fingerprint["family"]
    field_family = fingerprint["fields"].get("creative.family_id")
    field_archetype = fingerprint["fields"].get("creative.archetype_id")
    if family is None:
        if field_family is not None or field_archetype is not None:
            raise SeriesMemoryError("Unassigned fingerprint carries duplicate family fields")
    elif (
        field_family != family["family_id"]
        or field_archetype != family["archetype_id"]
    ):
        raise SeriesMemoryError("Fingerprint family/archetype fields disagree with family metadata")

    source_paths: set[str] = set()
    render_sources: list[dict[str, str]] = []
    for source in fingerprint["source_files"]:
        if source["path"] in source_paths:
            raise SeriesMemoryError(f"Duplicate fingerprint source path: {source['path']}")
        source_paths.add(source["path"])
        if source["role"] == "render_manifest":
            render_sources.append(source)
        if verify_files:
            source_path = _path_from_stored(source["path"])
            if file_sha256(source_path) != source["sha256"]:
                raise SeriesMemoryError(f"Fingerprint source hash mismatch: {source['path']}")

    if len(render_sources) > 1:
        raise SeriesMemoryError("Fingerprint may reference only one render manifest")
    if render_sources:
        render_source = render_sources[0]
        if technical_qa["evidence_path"] != render_source["path"]:
            raise SeriesMemoryError("Technical QA evidence path is not the render manifest source")
        if technical_qa["evidence_sha256"] != render_source["sha256"]:
            raise SeriesMemoryError("Technical QA evidence hash disagrees with the render source")
        if verify_files:
            render_path = _path_from_stored(render_source["path"])
            render_manifest = load_json(render_path)
            if technical_qa["status"] == "pass" and (
                render_manifest.get("video_id") != fingerprint["video_id"]
            ):
                raise SeriesMemoryError(
                    "Passing technical QA render manifest belongs to another video"
                )
            recomputed_qa = _technical_qa_evidence(render_manifest, render_path)
            if canonical_json(technical_qa) != canonical_json(recomputed_qa):
                raise SeriesMemoryError("Technical QA evidence does not match its render manifest")
    elif canonical_json(technical_qa) != canonical_json(_technical_qa_evidence({}, None)):
        raise SeriesMemoryError("Technical QA evidence requires a render manifest source")

    if approval["status"] != "unreviewed" and verify_files:
        receipt_path = _path_from_stored(approval["approval_receipt_path"])
        if file_sha256(receipt_path) != approval["approval_receipt_sha256"]:
            raise SeriesMemoryError("Approval receipt hash does not match the fingerprint")
        receipt, report, _ = _receipt_evidence(
            receipt_path,
            expected_series_id=fingerprint["series_id"],
            expected_video_id=fingerprint["video_id"],
            expected_status=approval["status"],
        )
        if receipt.get("receipt_id") != approval["approval_ref"]:
            raise SeriesMemoryError("Approval receipt id does not match approval_ref")
        if approval["status"] == "approved" and (
            report["actual_artifact_sha256"] != approval["approved_artifact_sha256"]
        ):
            raise SeriesMemoryError("Approved artifact hash does not match its receipt")


def _fingerprint_input_paths(fingerprint: dict[str, Any]) -> tuple[Path, ...]:
    paths = [_path_from_stored(source["path"]) for source in fingerprint["source_files"]]
    approval = fingerprint["approval"]
    if approval["approval_receipt_path"] is not None:
        receipt_path = _path_from_stored(approval["approval_receipt_path"])
        _, _, artifact_path = _receipt_evidence(
            receipt_path,
            expected_series_id=fingerprint["series_id"],
            expected_video_id=fingerprint["video_id"],
            expected_status=approval["status"],
        )
        paths.extend([receipt_path, artifact_path])
    return tuple(dict.fromkeys(paths))


def _ledger_input_paths(ledger: dict[str, Any]) -> tuple[Path, ...]:
    paths: list[Path] = []
    for entry in ledger["entries"]:
        fingerprint_path = _path_from_stored(entry["fingerprint_path"])
        paths.append(fingerprint_path)
        paths.extend(_fingerprint_input_paths(load_json(fingerprint_path)))
    return tuple(dict.fromkeys(paths))


def validate_contract(contract: dict[str, Any]) -> None:
    _validate_schema(contract, CONTRACT_SCHEMA, "Series contract")
    dimensions = contract["dimensions"]
    dimension_ids = [item["dimension_id"] for item in dimensions]
    if len(dimension_ids) != len(set(dimension_ids)):
        raise SeriesMemoryError("Series contract contains duplicate dimension ids")

    families = contract["template_families"]
    family_ids = [item["family_id"] for item in families]
    if len(family_ids) != len(set(family_ids)):
        raise SeriesMemoryError("Series contract contains duplicate family ids")
    family_id_set = set(family_ids)
    dimension_id_set = set(dimension_ids)
    archetype_ids = [item["archetype_id"] for item in families]
    if len(archetype_ids) != len(set(archetype_ids)):
        raise SeriesMemoryError("Series contract contains duplicate family archetype ids")

    if contract["status"] == "active":
        active_count = sum(item["status"] != "retired" for item in families)
        target = contract["family_policy"]["minimum_active_families_target"]
        if active_count < target:
            raise SeriesMemoryError(
                f"Active contract needs at least {target} non-retired template families; found {active_count}"
            )

    expected_comparisons = {
        "locked": {"exact", "allowed_set"},
        "bounded": {"numeric_range", "allowed_set"},
        "rotating": {"rotation"},
        "free": {"none"},
    }
    for item in dimensions:
        dimension_id = item["dimension_id"]
        classification = item["classification"]
        comparison = item["comparison"]
        if comparison not in expected_comparisons[classification]:
            raise SeriesMemoryError(
                f"{dimension_id}: {classification} cannot use comparison {comparison}"
            )
        if item["scope"] == "series" and item["family_ids"]:
            raise SeriesMemoryError(f"{dimension_id}: series-scoped dimension must not list families")
        if item["scope"] == "family" and not item["family_ids"]:
            raise SeriesMemoryError(f"{dimension_id}: family-scoped dimension needs family_ids")
        unknown_families = set(item["family_ids"]) - family_id_set
        if unknown_families:
            raise SeriesMemoryError(f"{dimension_id}: unknown families {sorted(unknown_families)}")
        if item["state"] == "seed" and item["enforcement"] != "observe":
            raise SeriesMemoryError(f"{dimension_id}: a seed may only observe; seed is not law")
        if item["state"] in {"seed", "candidate"} and item["enforcement"] == "block":
            raise SeriesMemoryError(f"{dimension_id}: unpromoted evidence cannot block")
        if classification in {"rotating", "free"} and item["enforcement"] == "block":
            raise SeriesMemoryError(
                f"{dimension_id}: creative variety signals may warn but never block delivery"
            )

        expected = item["expected"]
        if comparison == "exact" and not expected["exact_values"]:
            raise SeriesMemoryError(f"{dimension_id}: exact comparison needs exact_values")
        if comparison == "allowed_set" and not expected["allowed_values"]:
            raise SeriesMemoryError(f"{dimension_id}: allowed_set needs allowed_values")
        if comparison == "numeric_range":
            lower, upper = expected["minimum"], expected["maximum"]
            if lower is None or upper is None or lower > upper:
                raise SeriesMemoryError(f"{dimension_id}: numeric_range needs minimum <= maximum")
        if comparison == "rotation" and expected["rotation"] is None:
            raise SeriesMemoryError(f"{dimension_id}: rotation comparison needs a rotation policy")
        if comparison == "rotation":
            rotation = expected["rotation"]
            if rotation["max_consecutive"] > rotation["window"]:
                raise SeriesMemoryError(f"{dimension_id}: max_consecutive exceeds rotation window")
            if rotation["max_occurrences_in_window"] > rotation["window"]:
                raise SeriesMemoryError(
                    f"{dimension_id}: max_occurrences_in_window exceeds rotation window"
                )
            if rotation["minimum_unique_in_window"] > rotation["window"]:
                raise SeriesMemoryError(
                    f"{dimension_id}: minimum_unique_in_window exceeds rotation window"
                )
        if comparison == "none" and any(
            [expected["exact_values"], expected["allowed_values"], expected["minimum"] is not None,
             expected["maximum"] is not None, expected["rotation"] is not None]
        ):
            raise SeriesMemoryError(f"{dimension_id}: free dimension may not carry hidden constraints")

        if item["state"] == "default":
            approved_evidence = [
                evidence
                for evidence in item["evidence"]
                if evidence["video_id"]
                and evidence["fingerprint_id"]
                and evidence["approval_ref"]
                and evidence["instruction_ref"] is None
            ]
            evidence_videos = {evidence["video_id"] for evidence in approved_evidence}
            if len(approved_evidence) != len(item["evidence"]):
                raise SeriesMemoryError(
                    f"{dimension_id}: default evidence must identify approved fingerprints"
                )
            minimum = contract["promotion_policy"]["default_minimum_approved_videos"]
            if len(evidence_videos) < minimum:
                raise SeriesMemoryError(
                    f"{dimension_id}: default needs {minimum} distinct approved-video evidence records"
                )
            if item["classification"] in {"rotating", "free"}:
                raise SeriesMemoryError(
                    f"{dimension_id}: creative rotating/free dimensions cannot become a single default"
                )
            if item["source"] != "approved_pattern":
                raise SeriesMemoryError(f"{dimension_id}: default state requires approved_pattern source")
        if item["state"] == "explicit" and not any(
            evidence["instruction_ref"] for evidence in item["evidence"]
        ):
            raise SeriesMemoryError(f"{dimension_id}: explicit state requires an instruction reference")
        if item["state"] == "explicit" and item["source"] != "explicit_instruction":
            raise SeriesMemoryError(f"{dimension_id}: explicit state requires explicit_instruction source")
        if item["state"] == "seed" and item["source"] != "seed_observation":
            raise SeriesMemoryError(f"{dimension_id}: seed state requires seed_observation source")

    for family in families:
        lineage_parent = family["lineage"]["parent_family_id"]
        if lineage_parent is not None and lineage_parent not in family_id_set:
            raise SeriesMemoryError(f"{family['family_id']}: unknown parent family {lineage_parent}")
        if lineage_parent == family["family_id"]:
            raise SeriesMemoryError(f"{family['family_id']}: family cannot be its own parent")
        preserved = set(family["preserved_dimensions"])
        controlled = set(family["controlled_dimensions"])
        unknown_dimensions = (preserved | controlled) - dimension_id_set
        if unknown_dimensions:
            raise SeriesMemoryError(
                f"{family['family_id']}: unknown dimensions {sorted(unknown_dimensions)}"
            )
        if preserved & controlled:
            raise SeriesMemoryError(
                f"{family['family_id']}: dimensions cannot be both preserved and controlled"
            )
        budget = family["novelty_budget"]
        if budget["target_similarity_minimum"] > budget["target_similarity_maximum"]:
            raise SeriesMemoryError(f"{family['family_id']}: invalid similarity target range")

    parents = {family["family_id"]: family["lineage"]["parent_family_id"] for family in families}
    for family_id in family_ids:
        seen: set[str] = set()
        current: str | None = family_id
        while current is not None:
            if current in seen:
                raise SeriesMemoryError(f"Template family lineage contains a cycle at {current}")
            seen.add(current)
            current = parents[current]


def _approved_date_from_fingerprint(fingerprint: dict[str, Any]) -> str | None:
    if fingerprint["approval"]["status"] != "approved":
        return None
    receipt_path = _path_from_stored(fingerprint["approval"]["approval_receipt_path"])
    receipt = load_json(receipt_path)
    decided_at = _nested(receipt, "decision", "decided_at")
    if not isinstance(decided_at, str) or "T" not in decided_at:
        raise SeriesMemoryError("Approved receipt lacks a decision timestamp")
    return decided_at.split("T", 1)[0]


def _load_verified_ledger_entry(
    entry: dict[str, Any], ledger_series_id: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    fingerprint_path = _path_from_stored(entry["fingerprint_path"])
    actual_sha = file_sha256(fingerprint_path)
    if actual_sha != entry["fingerprint_sha256"]:
        raise SeriesMemoryError(
            f"{entry['fingerprint_id']}: fingerprint file hash does not match the ledger"
        )
    fingerprint = load_json(fingerprint_path)
    validate_fingerprint(fingerprint)
    if fingerprint["series_id"] != ledger_series_id:
        raise SeriesMemoryError(
            f"{entry['fingerprint_id']}: fingerprint belongs to another series"
        )
    family = fingerprint.get("family") or {}
    canonical = {
        "video_id": fingerprint["video_id"],
        "fingerprint_id": fingerprint["fingerprint_id"],
        "fingerprint_path": entry["fingerprint_path"],
        "fingerprint_sha256": actual_sha,
        "family_id": family.get("family_id"),
        "archetype_id": family.get("archetype_id"),
        "approval_status": fingerprint["approval"]["status"],
        "approval_ref": fingerprint["approval"]["approval_ref"],
        "approved_artifact_sha256": fingerprint["approval"]["approved_artifact_sha256"],
        "approved_at": _approved_date_from_fingerprint(fingerprint),
        "technical_qa": copy.deepcopy(fingerprint["technical_qa"]),
        "recorded_at": fingerprint["recorded_at"],
        "fields": copy.deepcopy(fingerprint["fields"]),
        "traits": copy.deepcopy(fingerprint["traits"]),
    }
    for key, canonical_value in canonical.items():
        if key in {"fingerprint_path", "fingerprint_sha256"}:
            continue
        if canonical_json(entry.get(key)) != canonical_json(canonical_value):
            raise SeriesMemoryError(
                f"{entry['fingerprint_id']}: duplicated ledger field {key!r} disagrees with its fingerprint"
            )
    return canonical, fingerprint


def _verified_ledger_entries(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        _load_verified_ledger_entry(entry, ledger["series_id"])[0]
        for entry in ledger["entries"]
    ]


def validate_ledger(ledger: dict[str, Any]) -> None:
    _validate_schema(ledger, LEDGER_SCHEMA, "Variety ledger")
    policy = ledger["policy"]
    if policy["notice_similarity"] > policy["warning_similarity"]:
        raise SeriesMemoryError("Ledger notice_similarity cannot exceed warning_similarity")
    fingerprint_ids: set[str] = set()
    fingerprints: dict[str, dict[str, Any]] = {}
    for entry in ledger["entries"]:
        fingerprint_id = entry["fingerprint_id"]
        if fingerprint_id in fingerprint_ids:
            raise SeriesMemoryError(f"Duplicate ledger fingerprint: {fingerprint_id}")
        fingerprint_ids.add(fingerprint_id)
        if entry["approval_status"] == "approved":
            if not entry["approval_ref"] or not entry["approved_at"]:
                raise SeriesMemoryError(
                    f"{fingerprint_id}: approved ledger entry needs approval_ref and approved_at"
                )
        elif entry["approved_at"] is not None:
            raise SeriesMemoryError(f"{fingerprint_id}: only approved entries may carry approved_at")
        if entry["approval_status"] == "unreviewed" and entry["approval_ref"] is not None:
            raise SeriesMemoryError(f"{fingerprint_id}: unreviewed entry cannot carry approval_ref")
        _, fingerprint = _load_verified_ledger_entry(entry, ledger["series_id"])
        fingerprints[fingerprint_id] = fingerprint
    for fingerprint_id, fingerprint in fingerprints.items():
        family = fingerprint.get("family") or {}
        parent_id = family.get("parent_fingerprint_id")
        if parent_id is not None and parent_id not in fingerprints:
            raise SeriesMemoryError(
                f"{fingerprint_id}: unknown parent fingerprint {parent_id} in ledger lineage"
            )


def ledger_entry_from_fingerprint(
    fingerprint: dict[str, Any], fingerprint_path: Path | str, approved_at: str | None = None
) -> dict[str, Any]:
    fingerprint_path = _confined_path(fingerprint_path, must_exist=True, expect="file")
    stored_fingerprint = load_json(fingerprint_path)
    if canonical_json(stored_fingerprint) != canonical_json(fingerprint):
        raise SeriesMemoryError("Fingerprint object does not match fingerprint_path contents")
    validate_fingerprint(fingerprint)
    approval = fingerprint["approval"]
    receipt_date = _approved_date_from_fingerprint(fingerprint)
    if approval["status"] == "approved" and approved_at not in {None, receipt_date}:
        raise SeriesMemoryError("approved_at must match the verified approval receipt")
    if approval["status"] != "approved" and approved_at is not None:
        raise SeriesMemoryError("approved_at is only valid for an approved fingerprint")
    family = fingerprint.get("family") or {}
    return {
        "video_id": fingerprint["video_id"],
        "fingerprint_id": fingerprint["fingerprint_id"],
        "fingerprint_path": _portable_path(fingerprint_path),
        "fingerprint_sha256": file_sha256(fingerprint_path),
        "family_id": family.get("family_id"),
        "archetype_id": family.get("archetype_id"),
        "approval_status": approval["status"],
        "approval_ref": approval["approval_ref"],
        "approved_artifact_sha256": approval["approved_artifact_sha256"],
        "approved_at": receipt_date,
        "technical_qa": copy.deepcopy(fingerprint["technical_qa"]),
        "recorded_at": fingerprint["recorded_at"],
        "fields": copy.deepcopy(fingerprint["fields"]),
        "traits": copy.deepcopy(fingerprint["traits"]),
    }


def add_fingerprint_to_ledger(
    ledger: dict[str, Any],
    fingerprint: dict[str, Any],
    fingerprint_path: Path | str,
    *,
    approved_at: str | None = None,
) -> dict[str, Any]:
    validate_ledger(ledger)
    validate_fingerprint(fingerprint)
    if fingerprint["series_id"] != ledger["series_id"]:
        raise SeriesMemoryError("Fingerprint and ledger belong to different series")
    if any(
        entry["fingerprint_id"] == fingerprint["fingerprint_id"] for entry in ledger["entries"]
    ):
        raise SeriesMemoryError(f"Fingerprint already exists: {fingerprint['fingerprint_id']}")
    result = copy.deepcopy(ledger)
    result["entries"].append(
        ledger_entry_from_fingerprint(fingerprint, fingerprint_path, approved_at=approved_at)
    )
    validate_ledger(result)
    return result


def _entry_family_id(value: dict[str, Any]) -> str | None:
    if "family_id" in value:
        return value.get("family_id")
    family = value.get("family")
    return family.get("family_id") if isinstance(family, dict) else None


def _dimension_applies(dimension: dict[str, Any], value: dict[str, Any]) -> bool:
    if dimension["scope"] == "series":
        return True
    return _entry_family_id(value) in set(dimension["family_ids"])


def dimension_value(value: dict[str, Any], dimension: dict[str, Any]) -> Any:
    source = value.get(dimension["value_source"], {})
    return source.get(dimension["selector"]) if isinstance(source, dict) else None


def _value_key(value: Any) -> str:
    if isinstance(value, list):
        return canonical_json(sorted(value, key=lambda item: canonical_json(item)))
    return canonical_json(value)


def _value_similarity(left: Any, right: Any) -> float:
    if left is None or right is None:
        return 0.0
    if isinstance(left, list) and isinstance(right, list):
        left_set = {_value_key(item) for item in left}
        right_set = {_value_key(item) for item in right}
        if not left_set and not right_set:
            return 0.0
        union = left_set | right_set
        return len(left_set & right_set) / len(union) if union else 1.0
    return 1.0 if _value_key(left) == _value_key(right) else 0.0


def _comparison_passes(dimension: dict[str, Any], observed: Any) -> bool:
    comparison = dimension["comparison"]
    expected = dimension["expected"]
    if observed is None or observed == []:
        return False
    if comparison == "exact":
        return any(_value_key(observed) == _value_key(item) for item in expected["exact_values"])
    if comparison == "allowed_set":
        allowed = {_value_key(item) for item in expected["allowed_values"]}
        if isinstance(observed, list):
            return all(_value_key(item) in allowed for item in observed)
        return _value_key(observed) in allowed
    if comparison == "numeric_range":
        return (
            isinstance(observed, (int, float))
            and not isinstance(observed, bool)
            and expected["minimum"] <= observed <= expected["maximum"]
        )
    return True


def _issue_severity(dimension: dict[str, Any]) -> str:
    if dimension["state"] == "seed":
        return "observe"
    if dimension["classification"] in {"rotating", "free"}:
        return "warn" if dimension["enforcement"] != "observe" else "observe"
    return dimension["enforcement"]


def _approved_entries(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        entry
        for entry in _verified_ledger_entries(ledger)
        if entry["approval_status"] == "approved"
    ]


def _latest_distinct_approved(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    indexed = list(enumerate(entries))
    indexed.sort(
        key=lambda pair: (
            pair[1].get("approved_at") or "",
            pair[1].get("recorded_at") or "",
            pair[0],
        )
    )
    for _, entry in indexed:
        video_id = entry["video_id"]
        latest[video_id] = entry
    return sorted(
        latest.values(),
        key=lambda entry: (
            entry.get("approved_at") or "",
            entry.get("recorded_at") or "",
            entry["fingerprint_id"],
        ),
    )


def _rotation_issues(
    dimension: dict[str, Any],
    candidate: dict[str, Any],
    approved: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    observed = dimension_value(candidate, dimension)
    if observed is None:
        return []
    policy = dimension["expected"]["rotation"]
    applicable = [entry for entry in approved if _dimension_applies(dimension, entry)]
    history = applicable[-max(0, policy["window"] - 1):]
    values = [dimension_value(entry, dimension) for entry in history] + [observed]
    values = [value for value in values if value is not None]
    if len(values) < 2:
        return []

    keys = [_value_key(value) for value in values]
    current = keys[-1]
    consecutive = 0
    for key in reversed(keys):
        if key != current:
            break
        consecutive += 1
    occurrences = sum(key == current for key in keys)
    unique_count = len(set(keys))
    issues = []
    severity = _issue_severity(dimension)
    if consecutive > policy["max_consecutive"]:
        issues.append(
            {
                "code": "ROTATION_CONSECUTIVE_LIMIT",
                "dimension_id": dimension["dimension_id"],
                "severity": severity,
                "observed": observed,
                "message": f"Same value appears {consecutive} consecutive times; limit is {policy['max_consecutive']}.",
            }
        )
    if occurrences > policy["max_occurrences_in_window"]:
        issues.append(
            {
                "code": "ROTATION_WINDOW_LIMIT",
                "dimension_id": dimension["dimension_id"],
                "severity": severity,
                "observed": observed,
                "message": f"Value appears {occurrences} times in the comparison window; limit is {policy['max_occurrences_in_window']}.",
            }
        )
    if len(keys) >= policy["window"] and unique_count < policy["minimum_unique_in_window"]:
        issues.append(
            {
                "code": "ROTATION_UNDERVARIETY",
                "dimension_id": dimension["dimension_id"],
                "severity": severity,
                "observed": observed,
                "message": f"Window contains {unique_count} unique values; target is {policy['minimum_unique_in_window']}.",
            }
        )
    return issues


def fingerprint_similarity(
    left: dict[str, Any], right: dict[str, Any], dimensions: list[dict[str, Any]]
) -> tuple[float | None, list[dict[str, Any]]]:
    """Compare creative descriptors only; return no opinion about quality."""
    components = []
    for dimension in dimensions:
        if dimension["classification"] not in {"rotating", "free"}:
            continue
        if not _dimension_applies(dimension, left) or not _dimension_applies(dimension, right):
            continue
        left_value = dimension_value(left, dimension)
        right_value = dimension_value(right, dimension)
        if left_value is None or right_value is None or left_value == [] or right_value == []:
            continue
        score = _value_similarity(left_value, right_value)
        components.append(
            {
                "dimension_id": dimension["dimension_id"],
                "similarity": round(score, 6),
            }
        )
    if not components:
        return None, []
    score = sum(item["similarity"] for item in components) / len(components)
    return round(score, 6), components


def _family_for(contract: dict[str, Any], family_id: str | None) -> dict[str, Any] | None:
    return next(
        (family for family in contract["template_families"] if family["family_id"] == family_id),
        None,
    )


def _entry_archetype_id(value: dict[str, Any]) -> str | None:
    if "archetype_id" in value:
        return value.get("archetype_id")
    family = value.get("family")
    return family.get("archetype_id") if isinstance(family, dict) else None


def _validate_family_assignment(contract: dict[str, Any], value: dict[str, Any], label: str) -> None:
    family_id = _entry_family_id(value)
    archetype_id = _entry_archetype_id(value)
    if family_id is None and archetype_id is None:
        return
    if family_id is None or archetype_id is None:
        raise SeriesMemoryError(f"{label}: family_id and archetype_id must be paired")
    family = _family_for(contract, family_id)
    if family is None:
        raise SeriesMemoryError(f"{label}: unknown template family {family_id}")
    if family["archetype_id"] != archetype_id:
        raise SeriesMemoryError(
            f"{label}: archetype {archetype_id} does not belong to {family_id}"
        )


def _validate_candidate_lineage(
    contract: dict[str, Any],
    fingerprint: dict[str, Any],
    verified_entries: list[dict[str, Any]],
) -> None:
    _validate_family_assignment(contract, fingerprint, fingerprint["fingerprint_id"])
    family = fingerprint.get("family") or {}
    parent_id = family.get("parent_fingerprint_id")
    if parent_id is None:
        return
    parent = next(
        (entry for entry in verified_entries if entry["fingerprint_id"] == parent_id),
        None,
    )
    if parent is None:
        raise SeriesMemoryError(f"{fingerprint['fingerprint_id']}: unknown parent fingerprint {parent_id}")
    child_family = _family_for(contract, family.get("family_id"))
    parent_family_id = parent.get("family_id")
    if child_family is not None and parent_family_id not in {
        child_family["family_id"], child_family["lineage"]["parent_family_id"]
    }:
        raise SeriesMemoryError(
            f"{fingerprint['fingerprint_id']}: parent fingerprint is outside its family lineage"
        )


def _validate_ledger_lineage_against_contract(
    contract: dict[str, Any],
    ledger: dict[str, Any],
    verified_entries: list[dict[str, Any]],
) -> None:
    entries_by_id = {entry["fingerprint_id"]: entry for entry in verified_entries}
    for raw_entry in ledger["entries"]:
        _, fingerprint = _load_verified_ledger_entry(raw_entry, ledger["series_id"])
        family = fingerprint.get("family") or {}
        parent_id = family.get("parent_fingerprint_id")
        if parent_id is None:
            continue
        parent = entries_by_id[parent_id]
        child_family = _family_for(contract, family.get("family_id"))
        if child_family is not None and parent.get("family_id") not in {
            child_family["family_id"], child_family["lineage"]["parent_family_id"]
        }:
            raise SeriesMemoryError(
                f"{fingerprint['fingerprint_id']}: ledger parent is outside its family lineage"
            )


def _novelty_budget(
    contract: dict[str, Any],
    candidate: dict[str, Any],
    approved: list[dict[str, Any]],
) -> dict[str, Any]:
    family_id = _entry_family_id(candidate)
    family = _family_for(contract, family_id)
    if family is None:
        return {
            "status": "not_applicable",
            "family_id": family_id,
            "changed_rotating_dimensions": [],
            "changed_locked_dimensions": [],
            "same_family_similarity": None,
            "message": "Candidate is not assigned to a known template family.",
        }
    same_family = [entry for entry in approved if entry.get("family_id") == family_id]
    if not same_family:
        return {
            "status": "insufficient_history",
            "family_id": family_id,
            "changed_rotating_dimensions": [],
            "changed_locked_dimensions": [],
            "same_family_similarity": None,
            "message": "No approved predecessor exists in this family.",
        }
    budget = family["novelty_budget"]
    comparison_entries = same_family[-budget["comparison_window"] :]
    predecessor = comparison_entries[-1]
    dimensions_by_id = {item["dimension_id"]: item for item in contract["dimensions"]}
    changed_rotating = []
    changed_locked = []
    for dimension_id in family["controlled_dimensions"]:
        dimension = dimensions_by_id[dimension_id]
        if dimension["classification"] == "rotating":
            if _value_similarity(
                dimension_value(candidate, dimension), dimension_value(predecessor, dimension)
            ) < 1:
                changed_rotating.append(dimension_id)
    for dimension_id in family["preserved_dimensions"]:
        dimension = dimensions_by_id[dimension_id]
        if dimension["classification"] == "locked" and _value_similarity(
            dimension_value(candidate, dimension), dimension_value(predecessor, dimension)
        ) < 1:
            changed_locked.append(dimension_id)

    similarity_rows = []
    for prior in comparison_entries:
        score, _ = fingerprint_similarity(candidate, prior, contract["dimensions"])
        similarity_rows.append((score, prior))
    numeric_rows = [row for row in similarity_rows if row[0] is not None]
    if numeric_rows:
        similarity, most_similar = max(numeric_rows, key=lambda row: row[0])
    else:
        similarity, most_similar = None, predecessor
    status = "within_budget"
    reasons = []
    over_budget = len(changed_locked) > budget["maximum_changed_locked_dimensions"]
    under_budget = len(changed_rotating) < budget["minimum_changed_rotating_dimensions"]
    if over_budget:
        reasons.append("locked family identity changed")
    if under_budget:
        reasons.append("too few controlled creative dimensions changed")
    if similarity is not None and similarity > budget["target_similarity_maximum"]:
        under_budget = True
        reasons.append("similarity is above the family's novelty target")
    elif similarity is not None and similarity < budget["target_similarity_minimum"]:
        over_budget = True
        reasons.append("similarity is below the family's continuity target")
    if over_budget:
        status = "over_budget"
    elif under_budget:
        status = "under_budget"
    return {
        "status": status,
        "family_id": family_id,
        "predecessor_video_id": most_similar["video_id"],
        "compared_video_ids": [entry["video_id"] for entry in comparison_entries],
        "changed_rotating_dimensions": changed_rotating,
        "changed_locked_dimensions": changed_locked,
        "same_family_similarity": similarity,
        "message": "; ".join(reasons) if reasons else "Novelty remains within the declared family budget.",
    }


def check_fingerprint(
    contract: dict[str, Any], fingerprint: dict[str, Any], ledger: dict[str, Any]
) -> dict[str, Any]:
    validate_contract(contract)
    validate_fingerprint(fingerprint)
    validate_ledger(ledger)
    if len({contract["series_id"], ledger["series_id"], fingerprint["series_id"]}) != 1:
        raise SeriesMemoryError("Contract, ledger, and fingerprint belong to different series")

    verified_entries = _verified_ledger_entries(ledger)
    for entry in verified_entries:
        _validate_family_assignment(contract, entry, entry["fingerprint_id"])
    _validate_ledger_lineage_against_contract(contract, ledger, verified_entries)
    _validate_candidate_lineage(contract, fingerprint, verified_entries)
    approved = _latest_distinct_approved(
        [
            entry
            for entry in verified_entries
            if entry["approval_status"] == "approved"
            and entry["fingerprint_id"] != fingerprint["fingerprint_id"]
        ]
    )
    issues: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []
    for dimension in contract["dimensions"]:
        if not _dimension_applies(dimension, fingerprint):
            continue
        observed = dimension_value(fingerprint, dimension)
        if dimension["comparison"] == "rotation":
            rotation_issues = _rotation_issues(dimension, fingerprint, approved)
            issues.extend(rotation_issues)
            checks.append(
                {
                    "dimension_id": dimension["dimension_id"],
                    "classification": dimension["classification"],
                    "state": dimension["state"],
                    "observed": observed,
                    "status": "notice" if rotation_issues else "pass",
                }
            )
            continue
        if dimension["comparison"] == "none":
            checks.append(
                {
                    "dimension_id": dimension["dimension_id"],
                    "classification": "free",
                    "state": dimension["state"],
                    "observed": observed,
                    "status": "recorded",
                }
            )
            continue
        passed = _comparison_passes(dimension, observed)
        checks.append(
            {
                "dimension_id": dimension["dimension_id"],
                "classification": dimension["classification"],
                "state": dimension["state"],
                "observed": observed,
                "status": "pass" if passed else "mismatch",
            }
        )
        if not passed:
            issues.append(
                {
                    "code": "DIMENSION_MISSING" if observed is None else "DIMENSION_MISMATCH",
                    "dimension_id": dimension["dimension_id"],
                    "severity": _issue_severity(dimension),
                    "observed": observed,
                    "message": (
                        "Fingerprint has no value for the declared selector."
                        if observed is None
                        else "Observed value is outside the declared contract."
                    ),
                }
            )

    comparisons = []
    window = ledger["policy"]["comparison_window"]
    for prior in approved[-window:]:
        score, components = fingerprint_similarity(fingerprint, prior, contract["dimensions"])
        comparisons.append(
            {
                "video_id": prior["video_id"],
                "family_id": prior.get("family_id"),
                "relationship": (
                    "same_family"
                    if prior.get("family_id") is not None
                    and prior.get("family_id") == _entry_family_id(fingerprint)
                    else "cross_family"
                ),
                "similarity": score,
                "components": components,
            }
        )
    numeric_scores = [item["similarity"] for item in comparisons if item["similarity"] is not None]
    maximum_similarity = max(numeric_scores) if numeric_scores else None
    if maximum_similarity is None:
        similarity_signal = "insufficient_history"
    elif maximum_similarity >= ledger["policy"]["warning_similarity"]:
        similarity_signal = "warning"
    elif maximum_similarity >= ledger["policy"]["notice_similarity"]:
        similarity_signal = "notice"
    else:
        similarity_signal = "distinct"

    novelty = _novelty_budget(contract, fingerprint, approved)
    blocking_issues = [issue for issue in issues if issue["severity"] == "block"]
    warning_issues = [issue for issue in issues if issue["severity"] == "warn"]
    status = "fail" if blocking_issues else "pass_with_notices" if warning_issues or issues else "pass"
    return {
        "schema_version": "1.0.0",
        "series_id": contract["series_id"],
        "video_id": fingerprint["video_id"],
        "fingerprint_id": fingerprint["fingerprint_id"],
        "status": status,
        "blocking": bool(blocking_issues),
        "dimension_checks": checks,
        "issues": issues,
        "variety": {
            "maximum_similarity": maximum_similarity,
            "similarity_signal": similarity_signal,
            "comparisons": comparisons,
            "novelty_budget": novelty,
            "blocking": False,
        },
        "quality": {
            "conclusion": "not_assessed",
            "reason": "Similarity and novelty measure repetition/continuity, not editorial or technical quality.",
            "requires": ["human_creative_review", "technical_qa"],
        },
    }


def _supporting_entries(
    dimension: dict[str, Any], approved: list[dict[str, Any]], *, require_technical_qa: bool
) -> list[dict[str, Any]]:
    support = []
    for entry in approved:
        if not _dimension_applies(dimension, entry):
            continue
        if require_technical_qa and dimension["classification"] in {"locked", "bounded"}:
            qa = entry.get("technical_qa") or {}
            if not (
                qa.get("status") == "pass"
                and qa.get("artifact_sha256")
                and qa.get("artifact_sha256") == entry.get("approved_artifact_sha256")
            ):
                continue
        value = dimension_value(entry, dimension)
        if _comparison_passes(dimension, value):
            support.append(entry)
    support = _latest_distinct_approved(support)
    if dimension["classification"] == "locked" and support:
        # A locked default means the same invariant survived multiple approvals,
        # not merely that each video matched one of several allowed candidates.
        groups: dict[str, list[dict[str, Any]]] = {}
        for entry in support:
            key = _value_key(dimension_value(entry, dimension))
            groups.setdefault(key, []).append(entry)
        support = max(groups.values(), key=lambda items: (len(items), _value_key(dimension_value(items[0], dimension))))
    return support


def build_learning_plan(
    contract: dict[str, Any],
    ledger: dict[str, Any],
    *,
    explicit_dimension_id: str | None = None,
    instruction_ref: str | None = None,
) -> dict[str, Any]:
    validate_contract(contract)
    validate_ledger(ledger)
    if contract["series_id"] != ledger["series_id"]:
        raise SeriesMemoryError("Contract and ledger belong to different series")
    if bool(explicit_dimension_id) != bool(instruction_ref):
        raise SeriesMemoryError(
            "explicit_dimension_id and instruction_ref must be provided together"
        )
    dimensions_by_id = {item["dimension_id"]: item for item in contract["dimensions"]}
    if explicit_dimension_id and explicit_dimension_id not in dimensions_by_id:
        raise SeriesMemoryError(f"Unknown dimension: {explicit_dimension_id}")

    verified_entries = _verified_ledger_entries(ledger)
    for entry in verified_entries:
        _validate_family_assignment(contract, entry, entry["fingerprint_id"])
    _validate_ledger_lineage_against_contract(contract, ledger, verified_entries)
    approved = _latest_distinct_approved(
        [entry for entry in verified_entries if entry["approval_status"] == "approved"]
    )
    minimum = contract["promotion_policy"]["default_minimum_approved_videos"]
    recommendations = []
    for dimension in contract["dimensions"]:
        if explicit_dimension_id == dimension["dimension_id"]:
            recommendations.append(
                {
                    "dimension_id": dimension["dimension_id"],
                    "action": "promote_to_explicit",
                    "eligible": True,
                    "evidence_video_ids": [],
                    "instruction_ref": instruction_ref,
                    "reason": "Explicit instruction is authoritative but does not change the dimension's creative class.",
                }
            )
            continue
        if dimension["state"] in {"default", "explicit"}:
            recommendations.append(
                {
                    "dimension_id": dimension["dimension_id"],
                    "action": "keep_current_state",
                    "eligible": False,
                    "evidence_video_ids": [],
                    "instruction_ref": None,
                    "reason": "Dimension is already promoted.",
                }
            )
            continue
        if dimension["classification"] in {"rotating", "free"}:
            recommendations.append(
                {
                    "dimension_id": dimension["dimension_id"],
                    "action": (
                        "keep_rotating_collect_family_evidence"
                        if dimension["classification"] == "rotating"
                        else "keep_free"
                    ),
                    "eligible": False,
                    "evidence_video_ids": [],
                    "instruction_ref": None,
                    "reason": "Creative evidence must not collapse into a single global value.",
                }
            )
            continue
        require_technical_qa = contract["quality_policy"]["technical_qa_required"]
        support = _supporting_entries(
            dimension, approved, require_technical_qa=require_technical_qa
        )
        matching_without_qa = _supporting_entries(
            dimension, approved, require_technical_qa=False
        )
        eligible = len(support) >= minimum
        qa_excluded_video_ids = sorted(
            {entry["video_id"] for entry in matching_without_qa}
            - {entry["video_id"] for entry in support}
        )
        recommendations.append(
            {
                "dimension_id": dimension["dimension_id"],
                "action": (
                    "promote_to_default"
                    if eligible
                    else "collect_more_approved_qa_evidence"
                    if require_technical_qa and qa_excluded_video_ids
                    else "collect_more_approved_evidence"
                ),
                "eligible": eligible,
                "evidence_video_ids": [entry["video_id"] for entry in support],
                "qa_excluded_video_ids": qa_excluded_video_ids,
                "instruction_ref": None,
                "reason": (
                    f"{len(support)} distinct approved videos with artifact-bound passing technical QA "
                    f"support the declared expectation; {minimum} required."
                    if require_technical_qa
                    else f"{len(support)} distinct approved videos support the declared expectation; {minimum} required."
                ),
            }
        )

    approved_count = len(approved)
    recalibration = contract["recalibration_policy"]
    minimum_recalibration = recalibration["minimum_approved_videos"]
    last_recalibrated = recalibration["last_recalibrated_approved_count"]
    if last_recalibrated > approved_count:
        raise SeriesMemoryError(
            "last_recalibrated_approved_count exceeds the verified approved-video count"
        )
    since_last = approved_count - last_recalibrated
    first_review_due = approved_count >= minimum_recalibration and last_recalibrated < minimum_recalibration
    due = first_review_due or (
        last_recalibrated >= minimum_recalibration
        and since_last >= recalibration["interval_approved_videos"]
    )
    family_evidence = []
    for family in contract["template_families"]:
        entries = [entry for entry in approved if entry.get("family_id") == family["family_id"]]
        family_evidence.append(
            {
                "family_id": family["family_id"],
                "approved_video_count": len(entries),
                "approved_video_ids": [entry["video_id"] for entry in entries],
                "global_rank": None,
            }
        )
    return {
        "schema_version": "1.0.0",
        "series_id": contract["series_id"],
        "approved_distinct_video_count": approved_count,
        "promotion_recommendations": recommendations,
        "recalibration": {
            "due": due,
            "minimum_approved_videos": minimum_recalibration,
            "approved_since_last_recalibration": since_last,
            "mode": "review_before_apply",
            "reason": (
                "Re-estimate bounds and family coverage with human review; do not silently rewrite the contract."
                if due
                else "More approved evidence is needed before the next recalibration review."
            ),
        },
        "template_family_evidence": family_evidence,
        "selection_policy": {
            "single_global_winner": False,
            "basis": "content_audience_platform_fit",
            "instruction": "Preserve useful families and compare within and across lineage; do not crown one universal template.",
        },
        "quality": {
            "conclusion": "not_assessed",
            "reason": "Approval frequency and similarity are evidence about preference/consistency, not proof of quality.",
        },
    }


def promote_dimension(
    contract: dict[str, Any],
    ledger: dict[str, Any],
    dimension_id: str,
    *,
    instruction_ref: str | None = None,
) -> dict[str, Any]:
    """Return a promoted copy; the caller must save it as a reviewed revision."""
    plan = build_learning_plan(
        contract,
        ledger,
        explicit_dimension_id=dimension_id if instruction_ref else None,
        instruction_ref=instruction_ref,
    )
    recommendation = next(
        item for item in plan["promotion_recommendations"] if item["dimension_id"] == dimension_id
    )
    if not recommendation["eligible"]:
        raise SeriesMemoryError(
            f"{dimension_id} is not eligible for promotion: {recommendation['reason']}"
        )
    result = copy.deepcopy(contract)
    dimension = next(item for item in result["dimensions"] if item["dimension_id"] == dimension_id)
    if instruction_ref:
        dimension["state"] = "explicit"
        dimension["source"] = "explicit_instruction"
        dimension["evidence"].append(
            {
                "video_id": None,
                "fingerprint_id": None,
                "approval_ref": None,
                "instruction_ref": instruction_ref,
            }
        )
    else:
        if dimension["classification"] not in {"locked", "bounded"}:
            raise SeriesMemoryError("Only locked/bounded dimensions can become evidence defaults")
        approved_by_video = {
            entry["video_id"]: entry
            for entry in _approved_entries(ledger)
            if entry["video_id"] in set(recommendation["evidence_video_ids"])
        }
        if contract["quality_policy"]["technical_qa_required"]:
            invalid_qa = [
                entry["video_id"]
                for entry in approved_by_video.values()
                if not (
                    entry.get("technical_qa", {}).get("status") == "pass"
                    and entry.get("technical_qa", {}).get("artifact_sha256")
                    == entry.get("approved_artifact_sha256")
                )
            ]
            if invalid_qa:
                raise SeriesMemoryError(
                    "Promotion evidence lacks artifact-bound passing technical QA: "
                    + ", ".join(sorted(invalid_qa))
                )
        dimension["state"] = "default"
        dimension["source"] = "approved_pattern"
        dimension["evidence"] = [
            {
                "video_id": entry["video_id"],
                "fingerprint_id": entry["fingerprint_id"],
                "approval_ref": entry["approval_ref"],
                "instruction_ref": None,
            }
            for entry in approved_by_video.values()
        ]
        if dimension["enforcement"] == "observe":
            dimension["enforcement"] = "warn"
    validate_contract(result)
    return result


def _emit(
    value: dict[str, Any],
    output: Path | None,
    *,
    protected_paths: tuple[Path | str, ...] = (),
) -> None:
    if output is None:
        print(json.dumps(value, indent=2, ensure_ascii=False))
    else:
        _write_json(output, value, protected_paths=protected_paths)
        print(f"OK: wrote {output}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    fingerprint = subparsers.add_parser("fingerprint", help="Extract evidence from a video manifest/editable")
    fingerprint.add_argument("--editable", type=Path, required=True)
    fingerprint.add_argument("--project-manifest", type=Path)
    fingerprint.add_argument("--render-manifest", type=Path)
    fingerprint.add_argument("--series-id")
    fingerprint.add_argument("--video-id")
    fingerprint.add_argument("--recorded-at")
    fingerprint.add_argument("--approval-status", choices=["unreviewed", "approved", "rejected"], default="unreviewed")
    fingerprint.add_argument("--approval-ref")
    fingerprint.add_argument("--approval-receipt", type=Path)
    fingerprint.add_argument("--family-id")
    fingerprint.add_argument("--archetype-id")
    fingerprint.add_argument("--parent-fingerprint-id")
    fingerprint.add_argument("--out", type=Path)

    check = subparsers.add_parser("check", help="Check invariants and non-blocking variety signals")
    check.add_argument("--contract", type=Path, required=True)
    check.add_argument("--fingerprint", type=Path, required=True)
    check.add_argument("--ledger", type=Path, required=True)
    check.add_argument("--out", type=Path)

    learn = subparsers.add_parser("learn", help="Recommend promotions and a three-approval recalibration review")
    learn.add_argument("--contract", type=Path, required=True)
    learn.add_argument("--ledger", type=Path, required=True)
    learn.add_argument("--explicit-dimension-id")
    learn.add_argument("--instruction-ref")
    learn.add_argument("--out", type=Path)

    promote = subparsers.add_parser("promote", help="Create a reviewed contract revision with one promoted dimension")
    promote.add_argument("--contract", type=Path, required=True)
    promote.add_argument("--ledger", type=Path, required=True)
    promote.add_argument("--dimension-id", required=True)
    promote.add_argument("--instruction-ref")
    promote.add_argument("--out", type=Path, required=True)

    ledger_add = subparsers.add_parser("ledger-add", help="Add an immutable fingerprint snapshot to a ledger copy")
    ledger_add.add_argument("--ledger", type=Path, required=True)
    ledger_add.add_argument("--fingerprint", type=Path, required=True)
    ledger_add.add_argument("--approved-at")
    ledger_add.add_argument("--out", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "fingerprint":
            value = extract_fingerprint(
                args.editable,
                project_manifest=args.project_manifest,
                render_manifest=args.render_manifest,
                series_id=args.series_id,
                video_id=args.video_id,
                recorded_at=args.recorded_at,
                approval_status=args.approval_status,
                approval_ref=args.approval_ref,
                approval_receipt=args.approval_receipt,
                family_id=args.family_id,
                archetype_id=args.archetype_id,
                parent_fingerprint_id=args.parent_fingerprint_id,
            )
            fingerprint_inputs = _fingerprint_input_paths(value)
            _emit(value, args.out, protected_paths=fingerprint_inputs)
            return 0
        if args.command == "check":
            contract = load_json(args.contract)
            fingerprint = load_json(args.fingerprint)
            ledger = load_json(args.ledger)
            value = check_fingerprint(contract, fingerprint, ledger)
            _emit(
                value,
                args.out,
                protected_paths=(
                    args.contract,
                    args.fingerprint,
                    args.ledger,
                    *_fingerprint_input_paths(fingerprint),
                    *_ledger_input_paths(ledger),
                ),
            )
            return 2 if value["blocking"] else 0
        if args.command == "learn":
            contract = load_json(args.contract)
            ledger = load_json(args.ledger)
            value = build_learning_plan(
                contract,
                ledger,
                explicit_dimension_id=args.explicit_dimension_id,
                instruction_ref=args.instruction_ref,
            )
            _emit(
                value,
                args.out,
                protected_paths=(args.contract, args.ledger, *_ledger_input_paths(ledger)),
            )
            return 0
        if args.command == "promote":
            contract = load_json(args.contract)
            ledger = load_json(args.ledger)
            value = promote_dimension(
                contract,
                ledger,
                args.dimension_id,
                instruction_ref=args.instruction_ref,
            )
            _emit(
                value,
                args.out,
                protected_paths=(args.contract, args.ledger, *_ledger_input_paths(ledger)),
            )
            return 0
        if args.command == "ledger-add":
            ledger = load_json(args.ledger)
            fingerprint = load_json(args.fingerprint)
            value = add_fingerprint_to_ledger(
                ledger, fingerprint, args.fingerprint, approved_at=args.approved_at
            )
            _emit(
                value,
                args.out,
                protected_paths=(
                    args.ledger,
                    args.fingerprint,
                    *_fingerprint_input_paths(fingerprint),
                    *_ledger_input_paths(ledger),
                ),
            )
            return 0
    except (OSError, json.JSONDecodeError, SeriesMemoryError) as error:
        print(f"SERIES MEMORY ERROR: {error}", file=sys.stderr)
        return 2
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
